from __future__ import annotations

import asyncio
import json
import os

from services.orchestrator.core.orchestrator import Orchestrator
from services.orchestrator.core.queue.redis_queue import RedisQueue


async def handle_task(orch: Orchestrator, task_id: str) -> None:
    await orch._run_task(task_id)


def main() -> int:
    if os.getenv("DSF_QUEUE", "").lower() != "redis":
        print("DSF_QUEUE!=redis; worker is idle.")
        return 0
    queue = RedisQueue()
    orch = Orchestrator()
    print("DSF worker started (redis)")
    while True:
        msg = queue.dequeue(block=True, timeout=5)
        if not msg:
            continue
        try:
            data = json.loads(msg)
            task_id = data["task_id"]
            asyncio.run(handle_task(orch, task_id))
        except Exception as e:
            print(f"worker error: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
