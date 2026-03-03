"""Domain model: Mission entity."""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MissionStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    AWAITING_APPROVAL = "awaiting_approval"
    REVIEWING = "reviewing"
    REVISING = "revising"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    PAUSED = "paused"
    PAUSED_AWAITING_RESOURCES = "paused_awaiting_resources"
    CANCELLED = "cancelled"
    FAILED = "failed"


class AuthorityMode(str, Enum):
    GUIDED = "guided"
    SUPERVISED = "supervised"
    FREE_REIN = "free_rein"


class Mission(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    goal: str
    status: MissionStatus = MissionStatus.CREATED
    authority_mode: AuthorityMode = AuthorityMode.SUPERVISED
    version: int = 1
    plan: list[str] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_context: dict | None = None
    thread_id: str | None = None
