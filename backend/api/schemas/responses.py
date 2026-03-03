"""API response schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from domain.models.deliverable import DeliverableType, ReviewStatus
from domain.models.mission import AuthorityMode, MissionStatus
from domain.models.task import TaskStatus


class TaskResponse(BaseModel):
    id: UUID
    mission_id: UUID
    parent_task_id: Optional[UUID]
    assigned_agent: str
    description: str
    status: TaskStatus
    priority: int
    inputs: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DeliverableResponse(BaseModel):
    id: UUID
    mission_id: UUID
    task_id: Optional[UUID]
    agent: str
    type: DeliverableType
    content: Dict[str, Any]
    review_status: ReviewStatus
    provenance_refs: List[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MissionResponse(BaseModel):
    id: UUID
    goal: str
    status: MissionStatus
    authority_mode: AuthorityMode
    plan: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_context: Optional[Dict[str, Any]] = None
    cost_usd: Optional[float] = None
    total_tokens: Optional[int] = None
    # Lightweight response, tasks/deliverables fetched separately or via expansion if needed

    model_config = {"from_attributes": True}


class EvalResponse(BaseModel):
    score: float
    reasoning: str
    dimension_scores: Dict[str, float]

    model_config = {"from_attributes": True}


# Retain existing schemas for compatibility if needed, or alias them
MissionStartResponse = MissionResponse
# Note: Cleaning up duplicative schemas from previous implementation if any
