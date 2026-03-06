"""Domain model: Task entity."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REVISION_NEEDED = "revision_needed"


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    mission_id: UUID
    parent_task_id: UUID | None = None
    assigned_agent: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    inputs: dict | None = None
    result: dict | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
