from .base import BaseAgent
from ..models import Task
import asyncio

class CodeWriterAgent(BaseAgent):
    name = "code-writer"

    async def run(self, task: Task) -> str:
        await asyncio.sleep(0.05)
        return f"# Generated code for: {task.title}\nprint('Hello from code agent')\n"
