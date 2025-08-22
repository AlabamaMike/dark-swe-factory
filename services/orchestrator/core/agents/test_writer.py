from .base import BaseAgent
from ..models import Task
import asyncio

class TestWriterAgent(BaseAgent):
    name = "test-writer"

    async def run(self, task: Task) -> str:
        await asyncio.sleep(0.05)
        return f"def test_placeholder():\n    assert 1 + 1 == 2\n"
