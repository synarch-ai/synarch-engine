import json
import pytest
from pathlib import Path
from uuid import uuid4
from unittest.mock import AsyncMock

from domain.evals.judge import EvalRunner, EvaluationResult
from domain.models.mission import Mission
from domain.models.deliverable import Deliverable, DeliverableType, ReviewStatus
from ports.model_provider import ModelProviderPort
from ports.persistence import DeliverableRepository

@pytest.fixture
def golden_dataset():
    dataset_path = Path(__file__).parent.parent / "datasets" / "golden_evals.json"
    with open(dataset_path) as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_golden_dataset_regression(golden_dataset):
    mock_model_provider = AsyncMock(spec=ModelProviderPort)
    mock_deliverable_repo = AsyncMock(spec=DeliverableRepository)
    runner = EvalRunner(mock_model_provider, mock_deliverable_repo)

    for case in golden_dataset:
        mission_id = uuid4()
        mission = Mission(id=mission_id, goal=case["goal"], plan=case["plan"])

        mock_deliverables = []
        for d in case["deliverables"]:
            mock_deliverables.append(Deliverable(
                mission_id=mission_id,
                agent=d["agent"],
                type=DeliverableType(d["type"]),
                content=d["content"],
                review_status=ReviewStatus.APPROVED,
                provenance_refs=[]
            ))
        mock_deliverable_repo.list_by_mission.return_value = mock_deliverables

        expected_score = case.get("expected_min_score", case.get("expected_max_score", 0.5))
        mock_model_provider.invoke.return_value = f'''
        {{
            "score": {expected_score},
            "reasoning": "Mocked reasoning for deterministic test.",
            "dimension_scores": {{"completeness": {expected_score}, "accuracy": {expected_score}, "quality": {expected_score}}}
        }}
        '''

        result = await runner.evaluate_mission(mission)

        if "expected_min_score" in case:
            assert result.score >= case["expected_min_score"]
        if "expected_max_score" in case:
            assert result.score <= case["expected_max_score"]
