"""Conditional routing functions for the LangGraph StateGraph (FR-7, FR-9)."""
from domain.orchestrator.state import MissionState


def route_after_planning(state: MissionState) -> list[str]:
    """Route to Zeus, Thoth, or both based on plan analysis (FR-7)."""
    plan = state.get("plan", [])
    needs_engineering = any(
        keyword in t.lower()
        for t in plan
        for keyword in ("engineer", "code", "implement", "build", "develop", "write")
    )
    needs_research = any(
        keyword in t.lower()
        for t in plan
        for keyword in ("research", "investigate", "analyze", "compare", "study", "find")
    )

    routes = []
    if needs_engineering:
        routes.append("zeus")
    if needs_research:
        routes.append("thoth")
    if not routes:
        routes.append("zeus")  # default to engineering path
    return routes


def route_after_review(state: MissionState) -> str:
    """Route based on Janus review verdict (FR-9)."""
    verdict = state.get("review_verdict", "PASS")
    revision_count = state.get("revision_count", 0)

    if verdict == "FAIL":
        return "fail"
    if verdict == "REVISE" and revision_count < 3:
        return "revise"
    return "synthesize"


def should_request_approval(state: MissionState) -> str:
    """Check if HITL approval is needed before proceeding (FR-8)."""
    if state.get("needs_approval"):
        return "await_approval"
    return "continue"
