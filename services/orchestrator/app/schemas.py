from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FeatureIn(BaseModel):
    title: str
    description: str

class FeatureOut(BaseModel):
    id: str
    title: str
    description: str
    created_at: datetime

class TaskOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    agent_type: str
    status: str
    result: Optional[str] = None

class FeatureStatusOut(BaseModel):
    id: str
    status: str
    completed: int
    total: int
    running: int
    pending: int
    failed: int
    tasks: List[TaskOut] = Field(default_factory=list)
