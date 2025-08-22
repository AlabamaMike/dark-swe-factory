from __future__ import annotations

import asyncio
import os
from typing import Dict, List, Optional

import networkx as nx

from .agents.code_writer import CodeWriterAgent
from .agents.review import ReviewAgent
from .agents.test_writer import TestWriterAgent
from .dag import basic_decompose
from .models import AgentType, Feature, Task, TaskStatus
from .persistence.base import Persistence
from .persistence.sqlite import SQLitePersistence


class Orchestrator:
    def __init__(self):
        self._features: Dict[str, Feature] = {}
        self._tasks: Dict[str, Task] = {}
        self._graphs: Dict[str, nx.DiGraph] = {}
        self._agents = {
            AgentType.CODE: CodeWriterAgent(),
            AgentType.TEST: TestWriterAgent(),
            AgentType.REVIEW: ReviewAgent(),
        }
        # Optional persistence
        self._persistence: Optional[Persistence] = None
        if os.getenv("DSF_DB", "sqlite").lower() == "sqlite":
            self._persistence = SQLitePersistence()
            self._persistence.init()

    def submit_feature(self, title: str, description: str) -> Feature:
        feature = Feature(title=title, description=description)
        tasks, g = basic_decompose(title, description)
        self._features[feature.id] = feature
        self._graphs[feature.id] = g
        for t in tasks:
            self._tasks[t.id] = t
            feature.task_ids.append(t.id)
        if self._persistence:
            self._persistence.save_feature_with_tasks(feature, tasks)
        return feature

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        if self._persistence:
            feat = self._persistence.get_feature(feature_id)
            if feat:
                # Ensure in-memory graph exists if loaded later (rebuild minimal graph)
                if feature_id not in self._graphs:
                    g = nx.DiGraph()
                    for t in self._persistence.list_tasks(feature_id):
                        g.add_node(t.id, task=t)
                        for dep in t.depends_on:
                            g.add_edge(dep, t.id)
                    self._graphs[feature_id] = g
                    self._tasks.update(
                        {
                            n: self._graphs[feature_id].nodes[n]["task"]
                            for n in self._graphs[feature_id].nodes
                        }
                    )
                self._features[feature_id] = feat
                return feat
        return self._features.get(feature_id)

    def list_tasks(self, feature_id: str) -> List[Task]:
        feat = self.get_feature(feature_id)
        if not feat:
            return []
        if self._persistence:
            tasks = self._persistence.list_tasks(feature_id)
            for t in tasks:
                self._tasks[t.id] = t
            return tasks
        return [self._tasks[tid] for tid in feat.task_ids]

    async def run_feature(self, feature_id: str):
        g = self._graphs[feature_id]
        # Run tasks respecting dependencies
        pending = set(g.nodes())
        while pending:
            runnable = [
                n
                for n in list(pending)
                if all(self._tasks[d].status == TaskStatus.DONE for d in g.predecessors(n))
            ]
            if not runnable:
                # Detect deadlock if any task failed
                failures = [n for n in pending if self._tasks[n].status == TaskStatus.FAILED]
                if failures:
                    break
                # Otherwise wait a bit for running tasks
                await asyncio.sleep(0.05)
                continue

            # Run all runnable tasks concurrently
            await asyncio.gather(*(self._run_task(n) for n in runnable))
            for n in runnable:
                pending.discard(n)

    async def _run_task(self, task_id: str):
        task = self._tasks[task_id]
        if task.status in (TaskStatus.DONE, TaskStatus.RUNNING):
            return
        task.status = TaskStatus.RUNNING
        try:
            agent = self._agents[task.agent_type]
            result = await agent.run(task)
            task.result = result
            task.status = TaskStatus.DONE
            if self._persistence:
                self._persistence.update_task(task)
        except Exception as e:
            task.result = f"error: {e}"
            task.status = TaskStatus.FAILED
            if self._persistence:
                self._persistence.update_task(task)

    def feature_status(self, feature_id: str):
        from services.orchestrator.app.schemas import FeatureStatusOut, TaskOut

        feat = self._features[feature_id]
        tasks = [self._tasks[tid] for tid in feat.task_ids]
        total = len(tasks)
        completed = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        running = sum(1 for t in tasks if t.status == TaskStatus.RUNNING)
        failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
        pending = total - completed - running - failed
        return FeatureStatusOut(
            id=feature_id,
            status=(
                "done"
                if completed == total
                else "running" if completed > 0 or running > 0 else "pending"
            ),
            completed=completed,
            total=total,
            running=running,
            pending=pending,
            failed=failed,
            tasks=[TaskOut.model_validate(t.model_dump()) for t in tasks],
        )
