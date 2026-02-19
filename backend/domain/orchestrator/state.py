"""LangGraph mission state schema (FR-6)."""
from typing import TypedDict, List, Optional, Annotated
import operator

from domain.models.agent_message import MissionPhase, AgentMessage


class TaskAssignment(TypedDict):
    task_id: str
    agent: str
    description: str
    status: str
    result: Optional[str]


class MissionState(TypedDict):
    """Global state flowing through the LangGraph StateGraph."""

    # Identity
    mission_id: str
    goal: str
    authority_mode: str  # "guided", "supervised", "free_rein"

    # Planning
    plan: List[str]
    plan_rationale: str

    # Execution
    phase: str  # MissionPhase value
    tasks: List[TaskAssignment]
    current_agent: str

    # Communication (append-only via reducer)
    messages: Annotated[List[dict], operator.add]

    # Review
    review_verdict: Optional[str]  # "PASS", "FAIL", "REVISE"
    review_feedback: Optional[str]
    revision_count: int

    # Output
    deliverables: List[dict]
    final_output: Optional[str]

    # Control
    needs_approval: bool
    approval_request: Optional[dict]
    error: Optional[str]
