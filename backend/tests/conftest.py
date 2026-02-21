"""Shared test fixtures for Synarch Engine."""
import sys
import pytest

# Ensure backend/ is on Python path
sys.path.insert(0, ".")


@pytest.fixture
def sample_mission_state():
    """Minimal MissionState for unit tests."""
    return {
        "mission_id": "test-mission-001",
        "goal": "Test goal",
        "authority_mode": "supervised",
        "plan": [],
        "plan_rationale": "",
        "phase": "planning",
        "tasks": [],
        "current_agent": "",
        "messages": [],
        "review_verdict": None,
        "review_feedback": None,
        "revision_count": 0,
        "deliverables": [],
        "final_output": None,
        "needs_approval": False,
        "approval_request": None,
        "error": None,
    }
