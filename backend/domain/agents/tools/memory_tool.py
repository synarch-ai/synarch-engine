from uuid import UUID
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from domain.models.memory import Memory, MemoryType
from ports.persistence import MemoryRepository

class WriteMemoryInput(BaseModel):
    content: str = Field(description="The actual fact, procedure, or decision to remember.")
    memory_type: MemoryType = Field(description="Must be 'fact', 'procedure', or 'decision'.")
    mission_id: str = Field(description="The UUID of the current mission.")
    agent_name: str = Field(description="Your agent name.")

class WriteMemoryTool(BaseTool):
    name: str = "write_memory"
    description: str = "Use this tool to durably store important facts, procedures, or decisions you learn during a mission so you don't forget them."
    args_schema: type[BaseModel] = WriteMemoryInput
    memory_repo: MemoryRepository

    model_config = {"arbitrary_types_allowed": True}

    def _run(self, content: str, memory_type: MemoryType, mission_id: str, agent_name: str) -> str:
        raise NotImplementedError("This tool is async only.")

    async def _arun(self, content: str, memory_type: MemoryType, mission_id: str, agent_name: str) -> str:
        memory = Memory(
            mission_id=UUID(mission_id) if mission_id else None,
            agent=agent_name,
            memory_type=memory_type,
            content=content
        )
        await self.memory_repo.create(memory)
        return f"Successfully saved {memory_type.value} to long-term memory."
