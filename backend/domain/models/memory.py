from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class MemoryType(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    DECISION = "decision"
    USER = "user"

class Memory(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    mission_id: Optional[UUID] = None
    agent: str
    memory_type: MemoryType
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    importance: float = 0.5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
