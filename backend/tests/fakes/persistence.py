from typing import List, Optional, Dict
from uuid import UUID, uuid4
from datetime import datetime

from domain.models.mission import Mission, MissionStatus
from domain.models.task import Task
from domain.models.approval import Approval, ApprovalStatus
from domain.models.deliverable import Deliverable
from domain.events.envelope import EventEnvelope
from ports.persistence import (
    MissionRepository,
    TaskRepository,
    ApprovalRepository,
    DeliverableRepository,
    EventRepository
)

class FakeMissionRepository(MissionRepository):
    def __init__(self):
        self.missions: Dict[UUID, Mission] = {}

    async def create(self, mission: Mission) -> Mission:
        self.missions[mission.id] = mission
        return mission

    async def get(self, mission_id: UUID) -> Optional[Mission]:
        return self.missions.get(mission_id)

    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None:
        if mission_id in self.missions:
            self.missions[mission_id].status = MissionStatus(status)
            self.missions[mission_id].updated_at = datetime.utcnow()

    async def list(self, status: str | None = None, limit: int = 50, offset: int = 0) -> List[Mission]:
        filtered = [
            m for m in self.missions.values()
            if status is None or m.status.value == status
        ]
        return filtered[offset : offset + limit]

    async def patch_payload(self, mission_id: UUID, *, plan: List[str] | None = None, error_context: Dict | None = None) -> None:
        if mission_id in self.missions:
            if plan:
                self.missions[mission_id].plan = plan
            if error_context:
                self.missions[mission_id].error_context = error_context

class FakeTaskRepository(TaskRepository):
    def __init__(self):
        self.tasks: Dict[UUID, Task] = {}

    async def create(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    async def get(self, task_id: UUID) -> Optional[Task]:
        return self.tasks.get(task_id)

    async def list_by_mission(self, mission_id: UUID) -> List[Task]:
        return [t for t in self.tasks.values() if t.mission_id == mission_id]

    async def update_status(self, task_id: UUID, status: str, result: Dict | None = None) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if result:
                self.tasks[task_id].result = result

class FakeApprovalRepository(ApprovalRepository):
    def __init__(self):
        self.approvals: Dict[UUID, Approval] = {}

    async def create(self, approval: Approval) -> Approval:
        self.approvals[approval.id] = approval
        return approval

    async def get(self, approval_id: UUID) -> Optional[Approval]:
        return self.approvals.get(approval_id)

    async def get_pending(self, mission_id: UUID) -> Optional[Approval]:
        for a in self.approvals.values():
            if a.mission_id == mission_id and a.status == ApprovalStatus.PENDING:
                return a
        return None

    async def list(self, mission_id: UUID, limit: int = 50, cursor: str | None = None) -> List[Approval]:
        filtered = [a for a in self.approvals.values() if a.mission_id == mission_id]
        if cursor:
            dt = datetime.fromisoformat(cursor)
            filtered = [a for a in filtered if a.requested_at < dt]
        filtered.sort(key=lambda x: x.requested_at, reverse=True)
        return filtered[:limit]

    async def decide(self, approval_id: UUID, decision: str, decided_by: str, reason: str | None = None) -> Approval:
        if approval_id in self.approvals:
            approval = self.approvals[approval_id]
            approval.status = ApprovalStatus(decision.lower())
            approval.decided_by = decided_by
            approval.decision_reason = reason
            approval.decided_at = datetime.utcnow()
            return approval
        raise ValueError("Approval not found")

class FakeEventRepository(EventRepository):
    def __init__(self):
        self.events: List[EventEnvelope] = []
        self._sequences: Dict[str, int] = {}

    async def create(self, event: EventEnvelope) -> EventEnvelope:
        # Simulate sequence allocation
        seq = self._sequences.get(event.mission_id, 0) + 1
        self._sequences[event.mission_id] = seq
        event.sequence = seq
        self.events.append(event)
        return event

    async def list_by_mission(self, mission_id: UUID, limit: int = 100, offset: int = 0) -> List[EventEnvelope]:
        filtered = [e for e in self.events if e.mission_id == str(mission_id)]
        return filtered[offset : offset + limit]

class FakeDeliverableRepository(DeliverableRepository):
    def __init__(self):
        self.deliverables: Dict[UUID, Deliverable] = {}

    async def create(self, deliverable: Deliverable) -> Deliverable:
        self.deliverables[deliverable.id] = deliverable
        return deliverable

    async def list_by_mission(self, mission_id: UUID) -> List[Deliverable]:
        return [d for d in self.deliverables.values() if d.mission_id == mission_id]
