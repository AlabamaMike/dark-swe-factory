import networkx as nx
from typing import List, Tuple
from .models import Task, AgentType


def basic_decompose(title: str, description: str) -> Tuple[List[Task], nx.DiGraph]:
    """
    MVP decomposition into: plan/implement/test/review with simple dependencies.
    - implement depends on plan
    - test depends on implement
    - review depends on test
    """
    g = nx.DiGraph()
    plan = Task(title=f"Plan: {title}", description=description, agent_type=AgentType.CODE)
    implement = Task(title=f"Implement: {title}", description=description, agent_type=AgentType.CODE, depends_on=[plan.id])
    test = Task(title=f"Test: {title}", description=description, agent_type=AgentType.TEST, depends_on=[implement.id])
    review = Task(title=f"Review: {title}", description=description, agent_type=AgentType.REVIEW, depends_on=[test.id])
    tasks = [plan, implement, test, review]
    for t in tasks:
        g.add_node(t.id, task=t)
    for t in tasks:
        for dep in t.depends_on:
            g.add_edge(dep, t.id)
    return tasks, g
