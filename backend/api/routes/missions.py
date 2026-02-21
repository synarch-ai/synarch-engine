"""Mission API routes (FR-1, FR-3, FR-4, FR-18, FR-22)."""
import logging
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks
from sse_starlette.sse import EventSourceResponse

from api.schemas.requests import MissionStartRequest, ApprovalDecisionRequest
from api.schemas.responses import MissionStartResponse, MissionStateResponse, MissionListResponse, MissionSummary
from api.middleware.errors import MissionNotFoundError
from domain.models.mission import MissionStatus

logger = logging.getLogger(__name__)
router = APIRouter()

# Temporary in-memory store (replaced by PostgreSQL in Milestone A)
_MISSIONS: dict = {}


@router.post("/mission/start", response_model=MissionStartResponse)
async def start_mission(req: MissionStartRequest, background_tasks: BackgroundTasks):
    """Create and start a new mission (FR-1)."""
    mission_id = str(uuid4())
    _MISSIONS[mission_id] = {
        "mission_id": mission_id,
        "goal": req.goal,
        "status": MissionStatus.CREATED,
        "authority_mode": req.authority_mode,
        "plan": None,
        "tasks": [],
        "deliverables": [],
    }
    # TODO: Wire LangGraph execution in background_tasks (Milestone A)
    return MissionStartResponse(
        mission_id=mission_id,
        status="created",
        stream_url=f"/mission/{mission_id}/stream",
    )


@router.get("/mission/{mission_id}/state", response_model=MissionStateResponse)
async def get_mission_state(mission_id: str):
    """Get current mission state (FR-4)."""
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise MissionNotFoundError(mission_id)
    from datetime import datetime
    return MissionStateResponse(
        mission_id=mission["mission_id"],
        goal=mission["goal"],
        status=mission["status"],
        authority_mode=mission["authority_mode"],
        plan=mission.get("plan"),
        tasks=mission.get("tasks", []),
        deliverables=mission.get("deliverables", []),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.get("/mission/{mission_id}/stream")
async def stream_mission_events(mission_id: str):
    """SSE stream of mission events (FR-18). Placeholder until NATS wired."""
    async def _placeholder_generator():
        import asyncio, json
        yield f"event: mission.state_changed\ndata: {json.dumps({'mission_id': mission_id, 'status': 'created'})}\n\n"
        await asyncio.sleep(30)
        yield ": keepalive\n\n"
    
    return EventSourceResponse(_placeholder_generator())


@router.post("/mission/{mission_id}/cancel")
async def cancel_mission(mission_id: str):
    """Cancel a running mission (FR-3)."""
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise MissionNotFoundError(mission_id)
    mission["status"] = MissionStatus.CANCELLED
    return {"mission_id": mission_id, "status": "cancelled"}


@router.post("/mission/{mission_id}/pause")
async def pause_mission(mission_id: str):
    """Pause a running mission (FR-3)."""
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise MissionNotFoundError(mission_id)
    mission["status"] = MissionStatus.PAUSED
    return {"mission_id": mission_id, "status": "paused"}


@router.post("/mission/{mission_id}/resume")
async def resume_mission(mission_id: str):
    """Resume a paused mission (FR-3)."""
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise MissionNotFoundError(mission_id)
    mission["status"] = MissionStatus.EXECUTING
    return {"mission_id": mission_id, "status": "executing"}


@router.get("/missions", response_model=MissionListResponse)
async def list_missions():
    """List all missions (FR-4)."""
    from datetime import datetime
    summaries = [
        MissionSummary(
            mission_id=m["mission_id"],
            goal=m["goal"],
            status=m["status"],
            created_at=datetime.utcnow(),
        )
        for m in _MISSIONS.values()
    ]
    return MissionListResponse(missions=summaries, total=len(summaries))
