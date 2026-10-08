"""Review m4: checkpointed state stores MissionPhase as a plain string, not an enum object."""
import pytest
from langgraph.checkpoint.memory import MemorySaver

from config import Settings
from domain.orchestrator.runtime import MissionOrchestratorRuntime
from tests.unit.test_s02_runtime import FakeEventBus, FakeModelProvider, FakeRedis, InMemoryMissionRepository
from tests.unit.test_syn039_resume_and_lease import SaverPort, _mission


@pytest.mark.asyncio
async def test_every_checkpoint_phase_is_a_plain_string():
    repo, saver = InMemoryMissionRepository(), MemorySaver()
    runtime = MissionOrchestratorRuntime(
        mission_repo=repo, model_provider=FakeModelProvider(), event_bus=FakeEventBus(),
        checkpointer=SaverPort(saver), redis_client=FakeRedis(),
        settings=Settings(model_call_budget_cap=40, require_durable_checkpointer=True),
    )
    m = await _mission(repo)
    await runtime.run_mission(m.id)
    assert (await repo.get(m.id)).status == "completed"

    config = {"configurable": {"thread_id": m.thread_id}}
    phases = [snap.values.get("phase") async for snap in runtime._compiled_graph.aget_state_history(config)]
    phases = [p for p in phases if p is not None]
    assert "executing" in phases and "synthesizing" in phases
    assert all(type(p) is str for p in phases), [type(p) for p in phases]
