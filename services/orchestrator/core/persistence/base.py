from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from ..models import Feature, Task


class Persistence(ABC):
    @abstractmethod
    def init(self) -> None: ...

    @abstractmethod
    def save_feature_with_tasks(self, feature: Feature, tasks: List[Task]) -> None: ...

    @abstractmethod
    def get_feature(self, feature_id: str) -> Optional[Feature]: ...

    @abstractmethod
    def list_tasks(self, feature_id: str) -> List[Task]: ...

    @abstractmethod
    def get_task_dependencies(self, task_id: str) -> List[str]: ...

    @abstractmethod
    def update_task(self, task: Task) -> None: ...

    # PR metadata
    @abstractmethod
    def record_task_pr(self, task_id: str, branch: str, pr_number: int) -> None: ...

    @abstractmethod
    def get_task_pr(self, task_id: str) -> Optional[Tuple[str, int]]: ...
