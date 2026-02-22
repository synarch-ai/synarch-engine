import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from api.routes.approvals import decide_approval
from api.schemas.approvals import DecideApprovalRequest
from domain.models.approval import Approval, ApprovalStatus, RiskLevel

@pytest.mark.asyncio
async def test_decide_approval_flow():
    # Setup
    mission_id = uuid4()
    approval_id = uuid4()

    mock_approval = Approval(
        id=approval_id,
        mission_id=mission_id,
        action_type="tool_call",
        requested_by="agent_x",
        description="Run dangerous command",
        risk_level=RiskLevel.HIGH,
        status=ApprovalStatus.PENDING
    )

    container = MagicMock()
    container.approval_repo.get = AsyncMock(return_value=mock_approval)
    container.approval_repo.decide = AsyncMock(return_value=mock_approval) # Simplified return
    container.event_repo.create = AsyncMock()
    container.event_bus.publish = AsyncMock()
    container.mission_runtime.resume_mission = AsyncMock()

    # Request
    req = DecideApprovalRequest(decision="approved", reason="Looks safe")

    # Act
    await decide_approval(approval_id, req, container)

    # Assert
    # 1. Decision Persisted
    container.approval_repo.decide.assert_called_once_with(
        approval_id,
        decision="approved",
        decided_by="operator",
        reason="Looks safe"
    )

    # 2. Event Emitted
    container.event_repo.create.assert_called_once()
    event = container.event_repo.create.call_args[0][0]
    assert event.type == "approval.approved"
    assert event.mission_id == str(mission_id)

    # 3. Runtime Resumed
    container.mission_runtime.resume_mission.assert_called_once()
    args = container.mission_runtime.resume_mission.call_args
    assert args[0][0] == str(mission_id)
    assert args[0][1] == {"approved": True, "modifier": {"reason": "Looks safe"}}
