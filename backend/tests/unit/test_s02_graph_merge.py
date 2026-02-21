"""Graph merge semantics tests for parallel branch fan-out/fan-in."""

from __future__ import annotations

import pytest

from domain.orchestrator.graph import build_graph


async def _synarch_node(state):
    return {
        "plan": ["Implement backend service", "Research competitor approaches"],
        "plan_rationale": "mixed-plan",
        "messages": [],
    }


async def _zeus_node(state):
    return {
        "tasks": [{"task_id": "eng-1", "agent": "hephaestus", "description": "Implement", "status": "pending", "result": None}],
        "messages": [],
    }


async def _thoth_node(state):
    return {
        "tasks": [{"task_id": "res-1", "agent": "hermes", "description": "Research", "status": "pending", "result": None}],
        "messages": [],
    }


async def _hephaestus_node(state):
    return {"deliverables": [{"agent": "hephaestus", "type": "code"}], "messages": []}


async def _hermes_node(state):
    return {"deliverables": [{"agent": "hermes", "type": "research"}], "messages": []}


async def _janus_node(state):
    return {"review_verdict": "PASS", "review_feedback": "ok", "revision_count": 0, "messages": []}


async def _synthesize_node(state):
    return {"final_output": "done", "messages": []}


async def _fail_node(state):
    return {"error": "failed", "messages": []}


@pytest.mark.asyncio
async def test_parallel_branches_merge_tasks_and_deliverables_without_clobbering() -> None:
    graph = build_graph(
        {
            "synarch": _synarch_node,
            "zeus": _zeus_node,
            "thoth": _thoth_node,
            "hephaestus": _hephaestus_node,
            "hermes": _hermes_node,
            "janus": _janus_node,
            "synthesize": _synthesize_node,
            "fail": _fail_node,
        }
    ).compile()

    initial_state = {
        "mission_id": "m-1",
        "goal": "mixed mission",
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

    final_state = await graph.ainvoke(initial_state)
    assert len(final_state["tasks"]) == 2
    assert len(final_state["deliverables"]) == 2
    assert {d["agent"] for d in final_state["deliverables"]} == {"hephaestus", "hermes"}

