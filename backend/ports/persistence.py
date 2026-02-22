"""Abstract persistence ports — repository interfaces (FR-2, FR-4)."""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from uuid import UUID

from domain.models.mission import Mission
from domain.models.task import Task
from domain.models.deliverable import Deliverable
from domain.models.approval import Approval
from domain.events.envelope import EventEnvelope


class EventRepository(ABC):
    @abstractmethod
    async def create(self, event: EventEnvelope) -> EventEnvelope: ...

    @abstractmethod
    async def list_by_mission(self, mission_id: UUID, limit: int = 100, offset: int = 0) -> List[EventEnvelope]: ...


class MissionRepository(ABC):
    @abstractmethod
    async def create(self, mission: Mission) -> Mission: ...

    @abstractmethod
    async def get(self, mission_id: UUID) -> Optional[Mission]: ...

    @abstractmethod
    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None: ...

    @abstractmethod
    async def list(self, status: str | None = None, limit: int = 50, offset: int = 0) -> List[Mission]: ...

    @abstractmethod
    async def patch_payload(
        self,
        mission_id: UUID,
        *,
        plan: List[str] | None = None,
        error_context: Dict | None = None,
    ) -> None: ...


class TaskRepository(ABC):
    @abstractmethod
    async def create(self, task: Task) -> Task: ...

    @abstractmethod
    async def get(self, task_id: UUID) -> Optional[Task]: ...

    @abstractmethod
    async def list_by_mission(self, mission_id: UUID) -> List[Task]: ...

    @abstractmethod
    async def update_status(self, task_id: UUID, status: str, result: Dict | None = None) -> None: ...


class DeliverableRepository(ABC):
    @abstractmethod
    async def create(self, deliverable: Deliverable) -> Deliverable: ...

    @abstractmethod
    async def list_by_mission(self, mission_id: UUID) -> List[Deliverable]: ...


class ApprovalRepository(ABC):
    @abstractmethod
    async def create(self, approval: Approval) -> Approval: ...

    @abstractmethod
    async def get(self, approval_id: UUID) -> Optional[Approval]: ...

    @abstractmethod
    async def get_pending(self, mission_id: UUID) -> Optional[Approval]: ...

    @abstractmethod
    async def list(self, mission_id: UUID, limit: int = 50, cursor: str | None = None) -> List[Approval]: ...

    @abstractmethod
    async def decide(self, approval_id: UUID, decision: str, decided_by: str, reason: str | None = None) -> Approval: ...
