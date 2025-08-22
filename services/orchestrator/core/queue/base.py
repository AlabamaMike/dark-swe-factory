from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class TaskQueue(ABC):
    @abstractmethod
    def enqueue(self, payload: str) -> None: ...

    @abstractmethod
    def dequeue(self, block: bool = True, timeout: int = 5) -> Optional[str]: ...
