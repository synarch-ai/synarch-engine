"""Janus — Reviewer Agent (Tier 3): Quality gate."""
from domain.agents.base import AgentNode
from domain.events.types import EventTypes
from domain.orchestrator.state import MissionState


class JanusAgent(AgentNode):
    """Quality gate. Reviews deliverables and issues PASS/FAIL/REVISE verdicts."""

    async def process(self, state: MissionState) -> dict:
        mission_id = state["mission_id"]
        deliverables = state.get("deliverables", [])
        revision_count = state.get("revision_count", 0)

        prompt = (
            f"You are Janus, quality reviewer in the Synarch hierarchy.\n\n"
            f"DELIVERABLES TO REVIEW:\n{deliverables}\n\n"
            f"REVISION COUNT: {revision_count}/3\n\n"
            f"Review each deliverable for quality, completeness, and correctness.\n"
            f"Issue a verdict: PASS (ready for synthesis), REVISE (needs improvement), or FAIL (unsalvageable).\n"
            f"Provide specific feedback."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        # Extract verdict (simplified — will use structured output)
        verdict = "PASS"
        if "REVISE" in response.upper():
            verdict = "REVISE"
        elif "FAIL" in response.upper():
            verdict = "FAIL"

        await self.emit_event(
            EventTypes.DELIVERABLE_REVIEWED,
            mission_id,
            {"verdict": verdict, "feedback_preview": response[:200]},
        )

        return {
            "current_agent": "janus",
            "review_verdict": verdict,
            "review_feedback": response,
            "revision_count": revision_count + (1 if verdict == "REVISE" else 0),
            "phase": "reviewing",
            "messages": [{"agent": "janus", "role": "review", "content": response, "timestamp": "", "metadata": {"verdict": verdict}}],
        }
