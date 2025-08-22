import asyncio

from ..models import Task
from .base import BaseAgent


class TestWriterAgent(BaseAgent):
    name = "test-writer"

    async def run(self, task: Task) -> str:
        await asyncio.sleep(0.05)
        return "def test_placeholder():\n    assert 1 + 1 == 2\n"
