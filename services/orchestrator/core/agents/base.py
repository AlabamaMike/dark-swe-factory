from __future__ import annotations
from typing import Optional
from ..models import Task

class BaseAgent:
    name: str = "base"

    async def run(self, task: Task) -> str:
        raise NotImplementedError
