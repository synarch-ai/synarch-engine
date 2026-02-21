"""S02 routing tests for conditional LangGraph branch selection (FR-7)."""

from domain.orchestrator.routing import route_after_planning, route_after_review


def test_route_after_planning_engineering_only() -> None:
    state = {"plan": ["Build backend service and implement API endpoint"]}
    assert route_after_planning(state) == ["zeus"]


def test_route_after_planning_research_only() -> None:
    state = {"plan": ["Research competitors and analyze market trends"]}
    assert route_after_planning(state) == ["thoth"]


def test_route_after_planning_mixed_returns_both() -> None:
    state = {"plan": ["Research options", "Implement final service"]}
    assert route_after_planning(state) == ["zeus", "thoth"]


def test_route_after_review_fail_routes_to_fail_terminal() -> None:
    assert route_after_review({"review_verdict": "FAIL", "revision_count": 0}) == "fail"
