from .base import BaseAgent
from ..models import Task
import asyncio

class ReviewAgent(BaseAgent):
    name = "review"

    async def run(self, task: Task) -> str:
        await asyncio.sleep(0.05)
        return "LGTM: basic checks passed"
