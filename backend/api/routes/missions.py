"""Mission API routes (FR-1, FR-3, FR-4, FR-18, FR-22)."""
import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sse_starlette.sse import EventSourceResponse

from api.dependencies import get_mission_repository
from api.middleware.errors import MissionNotFoundError, SynarchError
from api.schemas.requests import MissionStartRequest
from api.schemas.responses import MissionStartResponse, MissionStateResponse, MissionListResponse, MissionSummary
from domain.models.mission import Mission, MissionStatus, AuthorityMode
from ports.persistence import MissionRepository

logger = logging.getLogger(__name__)
router = APIRouter()


def _parse_mission_id(mission_id: str) -> UUID:
    try:
        return UUID(mission_id)
    except ValueError as exc:
        raise MissionNotFoundError(mission_id) from exc


def _parse_authority_mode(authority_mode: str) -> AuthorityMode:
    try:
        return AuthorityMode(authority_mode)
    except ValueError as exc:
        raise SynarchError(
            "INVALID_AUTHORITY_MODE",
            "authority_mode must be one of: guided, supervised, free_rein.",
            status_code=422,
            details={"authority_mode": authority_mode},
        ) from exc


def _value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


@router.post("/mission/start", response_model=MissionStartResponse)
async def start_mission(
    req: MissionStartRequest,
    background_tasks: BackgroundTasks,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Create and start a new mission (FR-1)."""
    mission = Mission(
        goal=req.goal,
        authority_mode=_parse_authority_mode(req.authority_mode),
        status=MissionStatus.CREATED,
    )
    mission.thread_id = str(mission.id)
    persisted = await mission_repo.create(mission)

    # TODO: Wire LangGraph execution in background_tasks (Milestone A)
    return MissionStartResponse(
        mission_id=str(persisted.id),
        status=_value(persisted.status),
        stream_url=f"/mission/{persisted.id}/stream",
    )


@router.get("/mission/{mission_id}/state", response_model=MissionStateResponse)
async def get_mission_state(
    mission_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Get current mission state (FR-4)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)

    return MissionStateResponse(
        mission_id=str(mission.id),
        goal=mission.goal,
        status=_value(mission.status),
        authority_mode=_value(mission.authority_mode),
        plan=mission.plan,
        tasks=[],
        deliverables=[],
        created_at=mission.created_at,
        updated_at=mission.updated_at,
        error_context=mission.error_context,
    )


@router.get("/mission/{mission_id}/stream")
async def stream_mission_events(
    mission_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """SSE stream of mission events (FR-18). Placeholder until NATS wired."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)

    async def _placeholder_generator():
        import asyncio, json
        yield f"event: mission.state_changed\ndata: {json.dumps({'mission_id': mission_id, 'status': _value(mission.status)})}\n\n"
        await asyncio.sleep(30)
        yield ": keepalive\n\n"

    return EventSourceResponse(_placeholder_generator())


@router.post("/mission/{mission_id}/cancel")
async def cancel_mission(
    mission_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Cancel a running mission (FR-3)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)
    await mission_repo.update_status(mission_uuid, MissionStatus.CANCELLED.value)
    return {"mission_id": mission_id, "status": MissionStatus.CANCELLED.value}


@router.post("/mission/{mission_id}/pause")
async def pause_mission(
    mission_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Pause a running mission (FR-3)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)
    await mission_repo.update_status(mission_uuid, MissionStatus.PAUSED.value)
    return {"mission_id": mission_id, "status": MissionStatus.PAUSED.value}


@router.post("/mission/{mission_id}/resume")
async def resume_mission(
    mission_id: str,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Resume a paused mission (FR-3)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)
    await mission_repo.update_status(mission_uuid, MissionStatus.EXECUTING.value)
    return {"mission_id": mission_id, "status": MissionStatus.EXECUTING.value}


@router.get("/missions", response_model=MissionListResponse)
async def list_missions(
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """List all missions (FR-4)."""
    missions = await mission_repo.list(status=status, limit=limit, offset=offset)
    summaries = [
        MissionSummary(
            mission_id=str(m.id),
            goal=m.goal,
            status=_value(m.status),
            created_at=m.created_at,
        )
        for m in missions
    ]
    return MissionListResponse(missions=summaries, total=len(summaries))
