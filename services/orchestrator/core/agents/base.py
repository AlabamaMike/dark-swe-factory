from __future__ import annotations

from ..models import Task


class BaseAgent:
    name: str = "base"

    async def run(self, task: Task) -> str:
        raise NotImplementedError
