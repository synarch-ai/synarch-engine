"""Janus — Reviewer Agent (Tier 3): Quality gate."""
import re

from domain.agents.base import AgentNode
from domain.orchestrator.state import MissionState
from domain.events.types import EventTypes


_VERDICT_LINE = re.compile(r"^[\s>*#_`\-]*verdict[\s*_`]*[:=\-][\s*_`]*(PASS|REVISE|FAIL)\b", re.I | re.M)
# Fallback: a bare verdict token, only on the first non-empty line, and only when it is
# the whole statement ("PASS", "FAIL: ...", "REVISE - ..."), never a word such as
# "Pass rate ..." or "Fail-safe ..." (review m2).
_LEADING_TOKEN = re.compile(r"^[\s>*#_`\-]*(PASS|REVISE|FAIL)[*_`]*(?:\s*[:.!]|\s+[-\u2013\u2014]\s|\s*$)", re.I)


def parse_verdict(response: str) -> str:
    """Anchored verdict extraction. Unparseable output -> REVISE (never a silent PASS)."""
    text = response or ""
    match = _VERDICT_LINE.search(text)
    if match is None:
        first_line = next((line for line in text.splitlines() if line.strip()), "")
        match = _LEADING_TOKEN.match(first_line)
    return match.group(1).upper() if match else "REVISE"


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
            f"Begin your reply with a line of exactly the form 'VERDICT: PASS', 'VERDICT: REVISE' or 'VERDICT: FAIL', "
            f"then provide specific feedback."
        )

        response = await self.invoke_llm(
            [{"role": "user", "content": prompt}],
            mission_id=mission_id,
        )

        verdict = parse_verdict(response)

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
