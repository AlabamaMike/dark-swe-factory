import asyncio
import json

import pytest


class FakeQueue:
    last_instance = None

    def __init__(self, *args, **kwargs):
        self._items: list[str] = []
        FakeQueue.last_instance = self

    def enqueue(self, payload: str) -> None:
        self._items.append(payload)

    def dequeue(self, block: bool = True, timeout: int = 5):
        if self._items:
            return self._items.pop(0)
        return None


async def consume_until_done(orch, feature_id: str, q: FakeQueue):
    # Drain queue messages and run tasks until feature is completed
    while True:
        item = q.dequeue(block=False)
        if item:
            data = json.loads(item)
            await orch._run_task(data["task_id"])  # internal method ok for test
        status = orch.feature_status(feature_id)
        if status.completed == status.total or status.failed > 0:
            break
        await asyncio.sleep(0.01)


@pytest.mark.asyncio
async def test_queue_execution_with_fake(monkeypatch, tmp_path):
    # Enable queue mode and isolate DB path
    monkeypatch.setenv("DSF_QUEUE", "redis")
    monkeypatch.chdir(tmp_path)

    # Replace RedisQueue with FakeQueue
    from services.orchestrator.core import orchestrator as orch_mod

    monkeypatch.setattr(orch_mod, "RedisQueue", FakeQueue, raising=True)

    orch = orch_mod.Orchestrator()
    feat = orch.submit_feature("Queued Feature", "test")

    consumer = asyncio.create_task(consume_until_done(orch, feat.id, FakeQueue.last_instance))
    await orch.run_feature(feat.id)
    await consumer

    status = orch.feature_status(feat.id)
    assert status.completed == status.total
    assert status.failed == 0
