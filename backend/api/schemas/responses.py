"""API response schemas."""
from datetime import datetime
from pydantic import BaseModel, Field


class MissionStartResponse(BaseModel):
    mission_id: str
    status: str
    stream_url: str
    request_id: str


class MissionStateResponse(BaseModel):
    mission_id: str
    goal: str
    status: str
    authority_mode: str
    plan: list[str] | None = None
    tasks: list[dict] = Field(default_factory=list)
    deliverables: list[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    error_context: dict | None = None
    request_id: str


class MissionSummary(BaseModel):
    mission_id: str
    goal: str
    status: str
    created_at: datetime


class MissionListResponse(BaseModel):
    items: list[MissionSummary]
    next_cursor: str | None = None
    request_id: str


class ApprovalResponse(BaseModel):
    mission_id: str
    approval_id: str
    decision: str
    resumed: bool
    request_id: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dependencies: dict


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)
    request_id: str = ""


class ErrorResponse(BaseModel):
    error: ErrorDetail
