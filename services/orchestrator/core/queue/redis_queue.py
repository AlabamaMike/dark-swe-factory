from __future__ import annotations

import os
from typing import Optional

import redis

from .base import TaskQueue


class RedisQueue(TaskQueue):
    def __init__(self, name: str = "dsf:queue:tasks", url: Optional[str] = None):
        self._name = name
        self._url = url or os.getenv("DSF_REDIS_URL", "redis://localhost:6379/0")
        self._client = redis.Redis.from_url(self._url, decode_responses=True)

    def enqueue(self, payload: str) -> None:
        self._client.rpush(self._name, payload)

    def dequeue(self, block: bool = True, timeout: int = 5) -> Optional[str]:
        if block:
            item = self._client.blpop(self._name, timeout=timeout)
            if item is None:
                return None
            return item[1]
        data = self._client.lpop(self._name)
        return data
