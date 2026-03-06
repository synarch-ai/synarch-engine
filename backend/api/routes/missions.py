"""Mission API routes (FR-1, FR-3, FR-4, FR-18, FR-22)."""
import base64
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sse_starlette.sse import EventSourceResponse

from api.dependencies import get_mission_repository, get_mission_runtime
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


def _decode_cursor(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
        data = json.loads(raw)
        value = int(data.get("offset", 0))
        return max(value, 0)
    except Exception:
        raise SynarchError(
            "INVALID_CURSOR",
            "Invalid pagination cursor.",
            status_code=422,
        )


def _encode_cursor(offset: int) -> str:
    payload = json.dumps({"offset": offset}, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("utf-8")


@router.post("/mission/start", response_model=MissionStartResponse, status_code=status.HTTP_201_CREATED)
async def start_mission(
    req: MissionStartRequest,
    request: Request,
    mission_repo: MissionRepository = Depends(get_mission_repository),
    mission_runtime=Depends(get_mission_runtime),
):
    """Create and start a new mission (FR-1)."""
    mission = Mission(
        goal=req.goal,
        authority_mode=_parse_authority_mode(req.authority_mode),
        status=MissionStatus.CREATED,
    )
    mission.thread_id = str(mission.id)
    persisted = await mission_repo.create(mission)

    await mission_runtime.launch_mission(persisted.id)
    return MissionStartResponse(
        mission_id=str(persisted.id),
        status=_value(persisted.status),
        stream_url=f"/api/v1/mission/{persisted.id}/stream",
        request_id=request.state.request_id,
    )


@router.get("/mission/{mission_id}/state", response_model=MissionStateResponse)
async def get_mission_state(
    mission_id: str,
    request: Request,
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
        completed_at=mission.completed_at,
        error_context=mission.error_context,
        request_id=request.state.request_id,
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
    request: Request,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Cancel a running mission (FR-3)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)
    await mission_repo.update_status(
        mission_uuid,
        MissionStatus.CANCELLED.value,
        expected_version=mission.version,
    )
    return {
        "mission_id": mission_id,
        "status": MissionStatus.CANCELLED.value,
        "request_id": request.state.request_id,
    }


@router.post("/mission/{mission_id}/pause")
async def pause_mission(
    mission_id: str,
    request: Request,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Pause a running mission (FR-3)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)
    await mission_repo.update_status(
        mission_uuid,
        MissionStatus.PAUSED.value,
        expected_version=mission.version,
    )
    return {
        "mission_id": mission_id,
        "status": MissionStatus.PAUSED.value,
        "request_id": request.state.request_id,
    }


@router.post("/mission/{mission_id}/resume")
async def resume_mission(
    mission_id: str,
    request: Request,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """Resume a paused mission (FR-3)."""
    mission_uuid = _parse_mission_id(mission_id)
    mission = await mission_repo.get(mission_uuid)
    if not mission:
        raise MissionNotFoundError(mission_id)
    await mission_repo.update_status(
        mission_uuid,
        MissionStatus.EXECUTING.value,
        expected_version=mission.version,
    )
    return {
        "mission_id": mission_id,
        "status": MissionStatus.EXECUTING.value,
        "request_id": request.state.request_id,
    }


@router.get("/missions", response_model=MissionListResponse)
async def list_missions(
    request: Request,
    status: str | None = None,
    limit: int = 50,
    cursor: str | None = None,
    mission_repo: MissionRepository = Depends(get_mission_repository),
):
    """List all missions (FR-4)."""
    offset = _decode_cursor(cursor)
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
    next_cursor = _encode_cursor(offset + limit) if len(summaries) == limit else None
    return MissionListResponse(items=summaries, next_cursor=next_cursor, request_id=request.state.request_id)
