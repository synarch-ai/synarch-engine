"""Domain model: Mission entity."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class MissionStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    REVIEWING = "REVIEWING"
    REVISING = "REVISING"
    SYNTHESIZING = "SYNTHESIZING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class AuthorityMode(str, Enum):
    GUIDED = "guided"
    SUPERVISED = "supervised"
    FREE_REIN = "free_rein"


class Mission(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    goal: str
    status: MissionStatus = MissionStatus.CREATED
    authority_mode: AuthorityMode = AuthorityMode.SUPERVISED
    plan: list[str] | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_context: dict | None = None
    thread_id: str | None = None
