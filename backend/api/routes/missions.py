"""Mission API routes (FR-1, FR-4, FR-18)."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from adapters.nats.sse_bridge import SSEBridge
from api.dependencies import get_container
from api.schemas.requests import MissionStartRequest as CreateMissionRequest
from api.schemas.responses import DeliverableResponse, EvalResponse, MissionResponse, TaskResponse
from container import Container
from domain.evals.judge import EvalRunner
from domain.models.mission import AuthorityMode, Mission

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

    if container.mission_runtime:
        # Fire and forget start
        # In a real app, we might want to ensure this is scheduled reliably.
        # But for now, we invoke it.
        # Note: start_mission should be async.
        # We assume start_mission handles background execution.
        await container.mission_runtime.start_mission(saved_mission.id)

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


@router.get("/{mission_id}/tasks", response_model=List[TaskResponse])
async def list_mission_tasks(
    mission_id: UUID,
    container: Container = Depends(get_container),
):
    """List tasks for a mission."""
    tasks = await container.task_repo.list_by_mission(mission_id)
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{mission_id}/deliverables", response_model=List[DeliverableResponse])
async def list_mission_deliverables(
    mission_id: UUID,
    container: Container = Depends(get_container),
):
    """List deliverables for a mission."""
    deliverables = await container.deliverable_repo.list_by_mission(mission_id)
    return [DeliverableResponse.model_validate(d) for d in deliverables]


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

@router.post("/{mission_id}/eval", response_model=EvalResponse)
async def evaluate_mission(
    mission_id: UUID,
    container: Container = Depends(get_container),
):
    """Run an evaluation on a completed mission using LLM-as-a-judge (FR-45)."""
    mission = await container.mission_repo.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    runner = EvalRunner(
        model_provider=container.model_provider,
        deliverable_repo=container.deliverable_repo,
    )

    result = await runner.evaluate_mission(mission)
    return EvalResponse.model_validate(result)
