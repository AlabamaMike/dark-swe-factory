import uuid
from typing import List
from ..models.schemas import Subtask, TaskCreate

def manual_or_simple_decompose(task: TaskCreate) -> List[Subtask]:
    """
    For MVP: if manual_decomposition is False, produce a simple 3-subtask decomposition
    mapping to code, test, review. This is a placeholder for future intelligent decomposition.
    """
    base_id = uuid.uuid4().hex[:8]
    return [
        Subtask(
            id=f"{base_id}-code",
            type="code",
            title=f"Implement: {task.title}",
            description=task.description or "Implement core logic.",
        ),
        Subtask(
            id=f"{base_id}-test",
            type="test",
            title=f"Test: {task.title}",
            description="Create unit/integration tests.",
        ),
        Subtask(
            id=f"{base_id}-review",
            type="review",
            title=f"Review: {task.title}",
            description="Perform code review and quality checks.",
        ),
    ]
