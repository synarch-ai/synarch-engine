"""API response schemas."""
from datetime import datetime
from pydantic import BaseModel


class MissionStartResponse(BaseModel):
    mission_id: str
    status: str
    stream_url: str


class MissionStateResponse(BaseModel):
    mission_id: str
    goal: str
    status: str
    authority_mode: str
    plan: list[str] | None = None
    tasks: list[dict] = []
    deliverables: list[dict] = []
    created_at: datetime
    updated_at: datetime
    error_context: dict | None = None


class MissionSummary(BaseModel):
    mission_id: str
    goal: str
    status: str
    created_at: datetime


class MissionListResponse(BaseModel):
    missions: list[MissionSummary]
    total: int


class ApprovalResponse(BaseModel):
    mission_id: str
    approval_id: str
    decision: str
    resumed: bool


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    dependencies: dict


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}
    request_id: str = ""


class ErrorResponse(BaseModel):
    error: ErrorDetail
