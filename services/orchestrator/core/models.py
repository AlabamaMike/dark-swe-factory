from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class AgentType(str, Enum):
    CODE = "code"
    TEST = "test"
    REVIEW = "review"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    agent_type: AgentType
    depends_on: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None

class Feature(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    task_ids: List[str] = Field(default_factory=list)
