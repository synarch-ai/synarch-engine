"""Mission API routes (FR-1, FR-4, FR-18)."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from container import Container
from api.dependencies import get_container
from api.schemas.requests import CreateMissionRequest
from api.schemas.responses import MissionResponse
from domain.models.mission import Mission, MissionStatus, AuthorityMode
from adapters.nats.sse_bridge import SSEBridge

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=MissionResponse, status_code=201)
async def create_mission(
    request: CreateMissionRequest,
    container: Container = Depends(get_container),
):
    """Create a new mission."""
    mission = Mission(
        goal=request.goal,
        authority_mode=AuthorityMode(request.authority_mode),
    )
    saved_mission = await container.mission_repo.create(mission)

    # Also trigger orchestration start (Phase 2)
    # await container.mission_runtime.start_mission(saved_mission.id)

    return MissionResponse.model_validate(saved_mission)


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: UUID,
    container: Container = Depends(get_container),
):
    """Get mission state."""
    mission = await container.mission_repo.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return MissionResponse.model_validate(mission)


@router.get("/{mission_id}/stream")
async def stream_mission(
    mission_id: UUID,
    request: Request,
    container: Container = Depends(get_container),
):
    """Stream mission events via SSE (FR-18)."""
    mission = await container.mission_repo.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    last_event_id = request.headers.get("last-event-id")

    # Create Bridge on demand (or inject singleton if stateless)
    # SSEBridge needs repo + bus.
    bridge = SSEBridge(container.event_bus, container.event_repo)

    return EventSourceResponse(
        bridge.stream_mission_events(mission_id, last_event_id)
    )
