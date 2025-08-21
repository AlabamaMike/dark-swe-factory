import json
from typing import Any, Dict
from redis.asyncio import Redis

TASKS_STREAM = "tasks"
EVENTS_STREAM = "events"


async def publish_task(r: Redis, payload: Dict[str, Any]) -> str:
    message_id = await r.xadd(TASKS_STREAM, {"data": json.dumps(payload)})
    return message_id

async def publish_event(r: Redis, payload: Dict[str, Any]) -> str:
    message_id = await r.xadd(EVENTS_STREAM, {"data": json.dumps(payload)})
    return message_id
