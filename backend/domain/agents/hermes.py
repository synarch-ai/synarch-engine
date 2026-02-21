"""Hermes — Researcher Agent (Tier 3): Information gathering."""
from domain.agents.base import AgentNode
from domain.orchestrator.state import MissionState
from domain.events.types import EventTypes


class HermesAgent(AgentNode):
    """Information gatherer. Retrieves and synthesizes research findings."""

    async def process(self, state: MissionState) -> dict:
        mission_id = state["mission_id"]
        tasks = [t for t in state.get("tasks", []) if t.get("agent") == "hermes"]

        task_descriptions = "\n".join(f"- {t['description']}" for t in tasks) if tasks else state["goal"]

        prompt = (
            f"You are Hermes, researcher in the Synarch hierarchy.\n\n"
            f"RESEARCH TASKS:\n{task_descriptions}\n\n"
            f"Provide thorough research findings with source citations where possible."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        await self.emit_event(
            EventTypes.AGENT_RESULT,
            mission_id,
            {"type": "research", "content_preview": response[:200]},
        )

        deliverable = {"agent": "hermes", "type": "research_report", "content": response}

        return {
            "current_agent": "hermes",
            "deliverables": [deliverable],
            "messages": [{"agent": "hermes", "role": "result", "content": response, "timestamp": "", "metadata": {}}],
        }
