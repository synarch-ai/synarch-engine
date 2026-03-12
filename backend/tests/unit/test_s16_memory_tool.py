import pytest
from uuid import uuid4
from domain.agents.tools.memory_tool import WriteMemoryTool
from domain.models.memory import MemoryType
from ports.persistence import MemoryRepository

class DummyMemoryRepo(MemoryRepository):
    async def create(self, memory):
        self.saved = memory
        return memory
    async def search(self, agent, embedding, limit=5, threshold=0.7):
        return []

@pytest.mark.asyncio
async def test_write_memory_tool():
    dummy_repo = DummyMemoryRepo()
    # Need to pass pydantic model config to allow arbitrary types if using custom objects
    # But BaseTool configs often have arbitary_types_allowed=True.
    # Since DummyMemoryRepo inherits from MemoryRepository, it will pass `isinstance(val, MemoryRepository)`
    tool = WriteMemoryTool(memory_repo=dummy_repo)

    result = await tool._arun(
        content="The server address is 10.0.0.1",
        memory_type=MemoryType.SEMANTIC,
        mission_id=str(uuid4()),
        agent_name="hephaestus"
    )

    assert "Successfully saved" in result
    assert dummy_repo.saved.content == "The server address is 10.0.0.1"
    assert dummy_repo.saved.agent == "hephaestus"
