"""Synarch — CEO Agent (Tier 1): Mission planning and synthesis."""
from domain.agents.base import AgentNode
from domain.events.types import EventTypes
from domain.models.agent_message import MissionPhase
from domain.orchestrator.state import MissionState


class SynarchAgent(AgentNode):
    """Supreme orchestrator. Decomposes God's goal into a plan."""

    async def process(self, state: MissionState) -> dict:
        state["mission_id"]
        state["goal"]
        phase = state.get("phase", MissionPhase.PLANNING)

        if phase == MissionPhase.SYNTHESIZING or state.get("review_verdict") == "PASS":
            return await self._synthesize(state)

        return await self._plan(state)

    async def _plan(self, state: MissionState) -> dict:
        """Decompose goal into actionable plan."""
        mission_id = state["mission_id"]
        goal = state["goal"]

        prompt = (
            f"You are the Synarch, supreme orchestrator of an AI agent hierarchy.\n\n"
            f"MISSION GOAL: {goal}\n\n"
            f"Decompose this goal into a clear plan. For each step, indicate whether it "
            f"requires RESEARCH (assign to Thoth/Hermes) or ENGINEERING (assign to Zeus/Hephaestus).\n\n"
            f"Return a JSON array of step descriptions."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        await self.emit_event(
            EventTypes.MISSION_PLANNED,
            mission_id,
            {"plan": response, "goal": goal},
        )

        # Parse plan (simplified — will be enhanced with structured output)
        plan_steps = [line.strip() for line in response.split("\n") if line.strip()]

        return {
            "plan": plan_steps,
            "plan_rationale": response,
            "phase": MissionPhase.EXECUTING,
            "messages": [{"agent": "synarch", "role": "delegation", "content": response, "timestamp": "", "metadata": {}}],
        }

    async def _synthesize(self, state: MissionState) -> dict:
        """Combine deliverables into final output."""
        mission_id = state["mission_id"]
        deliverables = state.get("deliverables", [])

        prompt = (
            f"You are the Synarch. The mission is complete.\n\n"
            f"ORIGINAL GOAL: {state['goal']}\n\n"
            f"DELIVERABLES:\n{deliverables}\n\n"
            f"Synthesize a final report for God (the human user)."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        await self.emit_event(
            EventTypes.MISSION_COMPLETED,
            mission_id,
            {"synthesis": response},
        )

        return {
            "final_output": response,
            "phase": MissionPhase.SYNTHESIZING,
            "messages": [{"agent": "synarch", "role": "synthesis", "content": response, "timestamp": "", "metadata": {}}],
        }
