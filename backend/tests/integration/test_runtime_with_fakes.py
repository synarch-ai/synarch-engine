import os

# Add backend to path
import sys
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../backend"))

from api.routes.approvals import decide_approval
from api.schemas.approvals import DecideApprovalRequest
from container import Container
from domain.models.approval import RiskLevel
from domain.models.mission import AuthorityMode, Mission
from tests.fakes.persistence import (
    FakeApprovalRepository,
    FakeDeliverableRepository,
    FakeEventRepository,
    FakeMissionRepository,
    FakeTaskRepository,
)


@pytest.mark.asyncio
async def test_full_mission_lifecycle_with_fakes():
    # 1. Setup Container with Fakes
    mission_repo = FakeMissionRepository()
    task_repo = FakeTaskRepository()
    approval_repo = FakeApprovalRepository()
    event_repo = FakeEventRepository()
    deliverable_repo = FakeDeliverableRepository()

    event_bus = AsyncMock() # Mock NATS for now
    model_provider = AsyncMock()
    checkpointer = MagicMock() # Mock checkpointer

    # Mock Runtime (since we don't have full graph execution in fakes yet)
    # But we want to test the *API* interaction with the runtime
    runtime = AsyncMock()

    from tests.fakes.idempotency import FakeIdempotencyRepository
    idempotency_repo = FakeIdempotencyRepository()

    container = Container(
        event_bus=event_bus,
        model_provider=model_provider,
        checkpointer=checkpointer,
        db_pool=None, # Not needed for fakes
        mission_repo=mission_repo,
        task_repo=task_repo,
        approval_repo=approval_repo,
        deliverable_repo=deliverable_repo,
        event_repo=event_repo,
        idempotency_repo=idempotency_repo,
        mission_runtime=runtime
    )

    # 2. Start Mission (Simulate API call logic)
    mission_id = uuid4()
    mission = Mission(id=mission_id, goal="Deploy Prod", authority_mode=AuthorityMode.SUPERVISED)
    await mission_repo.create(mission)

    # 3. Simulate Runtime hitting Interrupt
    # Runtime would create an approval request
    from domain.models.approval import Approval
    approval_id = uuid4()
    approval = Approval(
        id=approval_id,
        mission_id=mission_id,
        action_type="tool_call",
        requested_by="agent_x",
        description="Deploy to prod",
        risk_level=RiskLevel.HIGH
    )
    await approval_repo.create(approval)

    # Verify Pending State
    pending = await approval_repo.get_pending(mission_id)
    assert pending is not None
    assert pending.id == approval_id

    # 4. API Decision
    decision_req = DecideApprovalRequest(decision="approved", reason="LGTM")
    await decide_approval(approval_id, decision_req, container)

    # 5. Verify Outcome
    # DB State
    stored_approval = await approval_repo.get(approval_id)
    assert stored_approval.status == "approved"
    assert stored_approval.decided_by == "operator"

    # Event Log
    events = await event_repo.list_by_mission(mission_id)
    assert len(events) == 1
    assert events[0].type == "approval.approved"
    assert events[0].sequence == 1

    # Runtime Resume
    runtime.resume_mission.assert_called_once()
    args = runtime.resume_mission.call_args
    assert args[0][0] == str(mission_id)
    assert args[0][1] == {"approved": True, "modifier": {"reason": "LGTM"}}

    print("Full lifecycle (Start -> Interrupt -> Approve -> Resume) verified with Fakes.")
