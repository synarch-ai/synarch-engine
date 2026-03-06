"""Hephaestus — Engineer Agent (Tier 3): Code generation."""
from domain.agents.base import AgentNode
from domain.orchestrator.state import MissionState
from domain.events.types import EventTypes


class HephaestusAgent(AgentNode):
    """Code builder. Generates working code with tests."""

    async def process(self, state: MissionState) -> dict:
        mission_id = state["mission_id"]
        tasks = [t for t in state.get("tasks", []) if t.get("agent") == "hephaestus"]

        task_descriptions = "\n".join(f"- {t['description']}" for t in tasks) if tasks else state["goal"]

        prompt = (
            f"You are Hephaestus, engineer in the Synarch hierarchy.\n\n"
            f"ENGINEERING TASKS:\n{task_descriptions}\n\n"
            f"Generate working, production-quality code with tests. Include file paths."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        await self.emit_event(
            EventTypes.AGENT_RESULT,
            mission_id,
            {"type": "code", "content_preview": response[:200]},
        )

        deliverable = {"agent": "hephaestus", "type": "code", "content": response}

        return {
            "current_agent": "hephaestus",
            "deliverables": [deliverable],
            "messages": [{"agent": "hephaestus", "role": "result", "content": response, "timestamp": "", "metadata": {}}],
        }
