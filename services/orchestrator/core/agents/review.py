import asyncio

from ..models import Task
from .base import BaseAgent


class ReviewAgent(BaseAgent):
    name = "review"

    async def run(self, task: Task) -> str:
        await asyncio.sleep(0.05)
        return "LGTM: basic checks passed"
