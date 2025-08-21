from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class Subtask(BaseModel):
    id: str
    type: Literal["code", "test", "review"] = "code"
    title: str
    description: str


class TaskCreate(BaseModel):
    title: str = Field(..., description="High-level feature request")
    description: Optional[str] = None
    manual_decomposition: bool = False


class Task(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = None
    subtasks: List[Subtask] = []
