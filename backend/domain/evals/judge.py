import json
import logging
from typing import Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field

from domain.models.mission import Mission
from ports.model_provider import ModelProviderPort
from ports.persistence import DeliverableRepository

logger = logging.getLogger(__name__)

class EvaluationResult(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Overall score between 0.0 and 1.0")
    reasoning: str = Field(description="Explanation of the score")
    dimension_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Scores for specific dimensions like completeness, accuracy, etc."
    )

class EvalRunner:
    """Uses LLM-as-a-judge to evaluate mission outcomes and deliverables (FR-45, FR-46)."""

    def __init__(
        self,
        model_provider: ModelProviderPort,
        deliverable_repo: DeliverableRepository,
        eval_model: str = "gpt-4o",  # Default strong model for evals
    ):
        self.model_provider = model_provider
        self.deliverable_repo = deliverable_repo
        self.eval_model = eval_model

        self.system_prompt = """You are an expert technical evaluator.
Your task is to review an autonomous AI agent's mission deliverables and determine how well they fulfill the original mission goal.

You will be provided with:
1. The original mission goal.
2. The final plan executed.
3. The content of the deliverables produced.

You must evaluate the outcome on the following dimensions:
- Completeness: Did the agent address all parts of the goal?
- Accuracy: Is the generated content correct and free of hallucinations or logical errors?
- Quality: Is the deliverable well-structured, clear, and professional?

Provide a JSON response strictly matching this schema:
{
  "score": <float between 0.0 and 1.0 representing the overall assessment>,
  "reasoning": "<detailed explanation of your evaluation>",
  "dimension_scores": {
    "completeness": <float 0.0-1.0>,
    "accuracy": <float 0.0-1.0>,
    "quality": <float 0.0-1.0>
  }
}
"""

    async def evaluate_mission(self, mission: Mission) -> EvaluationResult:
        """Run an evaluation on a completed mission."""
        logger.info("Starting evaluation for mission %s", mission.id)

        deliverables = await self.deliverable_repo.list_by_mission(mission_id=mission.id)

        if not deliverables:
            logger.warning("Mission %s has no deliverables to evaluate.", mission.id)
            return EvaluationResult(
                score=0.0,
                reasoning="No deliverables were produced for this mission.",
                dimension_scores={"completeness": 0.0, "accuracy": 0.0, "quality": 0.0}
            )

        deliverables_text = ""
        for i, d in enumerate(deliverables):
            deliverables_text += f"\n--- Deliverable {i+1} [{d.type}] (Agent: {d.agent}) ---\n"
            if isinstance(d.content, dict):
                deliverables_text += json.dumps(d.content, indent=2)
            else:
                deliverables_text += str(d.content)
            deliverables_text += "\n"

        plan_text = "\n".join(mission.plan) if mission.plan else "No plan recorded."
        user_prompt = f"""
MISSION GOAL:
{mission.goal}

EXECUTED PLAN:
{plan_text}

PRODUCED DELIVERABLES:
{deliverables_text}

Evaluate the success of this mission based on the provided deliverables.
"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_text = await self.model_provider.invoke(
                model=self.eval_model,
                messages=messages,
                temperature=0.1,
            )

            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            result_dict = json.loads(clean_text)

            return EvaluationResult(
                score=float(result_dict.get("score", 0.0)),
                reasoning=str(result_dict.get("reasoning", "No reasoning provided.")),
                dimension_scores=result_dict.get("dimension_scores", {})
            )

        except json.JSONDecodeError as e:
            logger.error("Failed to parse evaluation result for mission %s: %s\nResponse was: %s", mission.id, e, response_text)
            return EvaluationResult(
                score=0.0,
                reasoning=f"Evaluation failed due to unparseable judge output: {str(e)}",
                dimension_scores={}
            )
        except Exception as e:
            logger.error("Evaluation failed for mission %s: %s", mission.id, e)
            raise
