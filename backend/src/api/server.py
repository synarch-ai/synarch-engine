from fastapi import APIRouter, BackgroundTasks, HTTPException
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from ..orchestrator.graph import app_graph
from ..orchestrator.state import MissionState

router = APIRouter()

# Mock Persistence for PoC (Since Postgres/Redis unavailable in this env)
MISSIONS = {}

@router.post("/mission/start")
async def start_mission(goal: str, background_tasks: BackgroundTasks):
    mission_id = f"mission-{len(MISSIONS) + 1}"

    # Initialize State
    initial_state = MissionState(
        mission_id=mission_id,
        goal=goal,
        plan=[],
        current_step=0,
        logs=[],
        final_output=""
    )
    MISSIONS[mission_id] = initial_state

    # Run Graph in Background
    background_tasks.add_task(run_mission_background, mission_id, initial_state)

    return {"mission_id": mission_id, "status": "started"}

async def run_mission_background(mission_id: str, state: MissionState):
    """
    Executes the LangGraph workflow.
    """
    print(f"Starting mission {mission_id}...")
    async for output in app_graph.astream(state):
        for key, value in output.items():
            print(f"Node {key} finished: {value}")
            # Update local state store (Mock)
            if "logs" in value:
                MISSIONS[mission_id]["logs"].extend(value["logs"])
            if "plan" in value:
                MISSIONS[mission_id]["plan"] = value["plan"]

@router.get("/mission/{mission_id}/stream")
async def stream_mission(mission_id: str):
    if mission_id not in MISSIONS:
        raise HTTPException(status_code=404, detail="Mission not found")

    async def event_generator():
        # Stream existing logs first
        for log in MISSIONS[mission_id]["logs"]:
            yield {"event": "log", "data": json.dumps(log)}

        # Poll for new logs (Mock Realtime)
        last_idx = len(MISSIONS[mission_id]["logs"])
        while True:
            await asyncio.sleep(1)
            current_logs = MISSIONS[mission_id]["logs"]
            if len(current_logs) > last_idx:
                for log in current_logs[last_idx:]:
                    yield {"event": "log", "data": json.dumps(log)}
                last_idx = len(current_logs)

    return EventSourceResponse(event_generator())
