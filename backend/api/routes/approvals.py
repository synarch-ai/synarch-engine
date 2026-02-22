"""Approval API routes (FR-21 to FR-25)."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from container import Container
from api.dependencies import get_container
from api.schemas.approvals import CreateApprovalRequest, DecideApprovalRequest
from domain.models.approval import Approval, ApprovalStatus
from domain.events.envelope import EventEnvelope

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=List[Approval])
async def list_approvals(
    mission_id: UUID,
    container: Container = Depends(get_container),
):
    """List approvals for a mission."""
    # Note: ApprovalRepo interface might need 'list_by_mission' method update if not present.
    # Currently it has get_pending which returns one.
    # We will assume a list method exists or stick to pending for now if strict.
    # Checking LLD-05: get_pending(mission_id) returns Optional[Approval].
    # But usually we want all pending.
    # Let's use get_pending for now as per repo interface.
    # If we need list, we must update Repo.
    # For S06, the key is the decision flow.

    # Actually, let's implement get_pending as a list for robust UI?
    # Repo currently says: get_pending -> Optional[Approval].
    # We'll just return that one if it exists.

    approval = await container.approval_repo.get_pending(mission_id)
    return [approval] if approval else []


@router.post("/{approval_id}/decision", response_model=Approval)
async def decide_approval(
    approval_id: UUID,
    request: DecideApprovalRequest,
    container: Container = Depends(get_container),
):
    """Decide an approval (Approve/Reject) and resume execution."""
    approval = await container.approval_repo.get(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=409, detail="Approval already decided")

    # 1. Persist Decision
    updated_approval = await container.approval_repo.decide(
        approval_id,
        decision=request.decision,
        decided_by=request.decided_by,
        reason=request.reason,
    )

    # 2. Emit Event
    event_type = f"approval.{request.decision.lower()}"  # approved/rejected
    event = EventEnvelope.create(
        event_type=event_type,
        mission_id=str(approval.mission_id),
        payload={
            "approval_id": str(approval.id),
            "actor": request.decided_by,
            "reason": request.reason
        },
        agent="god" # Operator
    )
    await container.event_repo.create(event)
    await container.event_bus.publish(event)

    # 3. Resume Runtime
    if container.mission_runtime:
        decision_payload = {
            "approved": request.decision.lower() == "approved",
            "modifier": {"reason": request.reason}
        }
        await container.mission_runtime.resume_mission(
            str(approval.mission_id),
            decision_payload
        )

    return updated_approval
