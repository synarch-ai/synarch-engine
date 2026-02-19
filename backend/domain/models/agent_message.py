"""Domain model: Agent messages and mission phases."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MissionPhase(str, Enum):
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REVIEWING = "REVIEWING"
    REVISING = "REVISING"
    SYNTHESIZING = "SYNTHESIZING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"


class MessageRole(str, Enum):
    THOUGHT = "thought"
    DELEGATION = "delegation"
    RESULT = "result"
    REVIEW = "review"
    SYNTHESIS = "synthesis"
    ERROR = "error"


class AgentMessage(BaseModel):
    agent: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)
