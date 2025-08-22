from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from typing import List, Optional

from ..models import AgentType, Feature, Task, TaskStatus


class SQLitePersistence:
    def __init__(self, path: str = "artifacts/dsf.db"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._path = path
        self._conn = sqlite3.connect(self._path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def init(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS features (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                feature_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                agent_type TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                FOREIGN KEY(feature_id) REFERENCES features(id)
            );
            CREATE TABLE IF NOT EXISTS task_deps (
                task_id TEXT NOT NULL,
                depends_on_id TEXT NOT NULL,
                PRIMARY KEY(task_id, depends_on_id),
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(depends_on_id) REFERENCES tasks(id)
            );
            CREATE TABLE IF NOT EXISTS task_prs (
                task_id TEXT PRIMARY KEY,
                branch TEXT NOT NULL,
                pr_number INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            );
            """
        )
        self._conn.commit()

    def save_feature_with_tasks(self, feature: Feature, tasks: List[Task]) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO features(id,title,description,created_at) VALUES (?,?,?,?)",
            (feature.id, feature.title, feature.description, feature.created_at.isoformat()),
        )
        for t in tasks:
            cur.execute(
                """
                INSERT OR REPLACE INTO tasks
                (id, feature_id, title, description, agent_type, status, result)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    t.id,
                    feature.id,
                    t.title,
                    t.description,
                    t.agent_type.value,
                    t.status.value,
                    t.result,
                ),
            )
            for dep in t.depends_on:
                cur.execute(
                    "INSERT OR IGNORE INTO task_deps(task_id, depends_on_id) VALUES (?,?)",
                    (t.id, dep),
                )
        self._conn.commit()

    def get_feature(self, feature_id: str) -> Optional[Feature]:
        cur = self._conn.cursor()
        row = cur.execute(
            "SELECT id,title,description,created_at FROM features WHERE id=?",
            (feature_id,),
        ).fetchone()
        if not row:
            return None
        feat = Feature(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            task_ids=[],
        )
        task_rows = cur.execute(
            "SELECT id FROM tasks WHERE feature_id=? ORDER BY rowid ASC",
            (feature_id,),
        ).fetchall()
        feat.task_ids = [r[0] for r in task_rows]
        return feat

    def list_tasks(self, feature_id: str) -> List[Task]:
        cur = self._conn.cursor()
        rows = cur.execute(
            """
            SELECT id, title, description, agent_type, status, result FROM tasks
            WHERE feature_id=? ORDER BY rowid ASC
            """,
            (feature_id,),
        ).fetchall()
        tasks: List[Task] = []
        for r in rows:
            tid = r["id"]
            deps = [
                d[0]
                for d in cur.execute(
                    "SELECT depends_on_id FROM task_deps WHERE task_id=?",
                    (tid,),
                ).fetchall()
            ]
            tasks.append(
                Task(
                    id=tid,
                    title=r["title"],
                    description=r["description"],
                    agent_type=AgentType(r["agent_type"]),
                    status=TaskStatus(r["status"]),
                    result=r["result"],
                    depends_on=deps,
                )
            )
        return tasks

    def get_task_dependencies(self, task_id: str) -> List[str]:
        cur = self._conn.cursor()
        return [
            r[0]
            for r in cur.execute(
                "SELECT depends_on_id FROM task_deps WHERE task_id=?",
                (task_id,),
            ).fetchall()
        ]

    def update_task(self, task: Task) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE tasks SET status=?, result=? WHERE id=?",
            (task.status.value, task.result, task.id),
        )
        self._conn.commit()

    def record_task_pr(self, task_id: str, branch: str, pr_number: int) -> None:
        cur = self._conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO task_prs(task_id, branch, pr_number, created_at) VALUES (?,?,?,?)",
            (task_id, branch, pr_number, datetime.utcnow().isoformat()),
        )
        self._conn.commit()

    def get_task_pr(self, task_id: str):
        cur = self._conn.cursor()
        row = cur.execute(
            "SELECT branch, pr_number FROM task_prs WHERE task_id=?",
            (task_id,),
        ).fetchone()
        if not row:
            return None
        return (row["branch"], int(row["pr_number"]))
