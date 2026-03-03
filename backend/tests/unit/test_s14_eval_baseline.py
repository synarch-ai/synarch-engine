import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from domain.evals.judge import EvalRunner, EvaluationResult
from domain.models.mission import Mission
from domain.models.deliverable import Deliverable, DeliverableType, ReviewStatus
from ports.model_provider import ModelProviderPort
from ports.persistence import DeliverableRepository


@pytest.fixture
def mock_model_provider():
    provider = AsyncMock(spec=ModelProviderPort)
    return provider


@pytest.fixture
def mock_deliverable_repo():
    repo = AsyncMock(spec=DeliverableRepository)
    return repo


@pytest.mark.asyncio
async def test_eval_runner_no_deliverables(mock_model_provider, mock_deliverable_repo):
    """Test EvalRunner gracefully handles missions with zero deliverables."""
    mission = Mission(id=uuid4(), goal="Write a hello world script.")

    mock_deliverable_repo.list_by_mission.return_value = []

    runner = EvalRunner(mock_model_provider, mock_deliverable_repo)
    result = await runner.evaluate_mission(mission)

    assert result.score == 0.0
    assert result.dimension_scores["completeness"] == 0.0
    assert "no deliverables" in result.reasoning.lower()
    mock_model_provider.invoke.assert_not_called()


@pytest.mark.asyncio
async def test_eval_runner_successful_evaluation(mock_model_provider, mock_deliverable_repo):
    """Test EvalRunner parses standard LLM JSON output."""
    mission = Mission(id=uuid4(), goal="Write a hello world script in Python.", plan=["Step 1"])

    # Fake deliverable
    d = Deliverable(
        mission_id=mission.id,
        agent="Hermes",
        type=DeliverableType.CODE,
        content={"code": "print('Hello, World!')"},
        review_status=ReviewStatus.APPROVED,
        provenance_refs=[]
    )
    mock_deliverable_repo.list_by_mission.return_value = [d]

    # Fake model response
    fake_json_response = '''
    ```json
    {
      "score": 0.95,
      "reasoning": "The script correctly prints Hello World.",
      "dimension_scores": {
        "completeness": 1.0,
        "accuracy": 1.0,
        "quality": 0.85
      }
    }
    ```
    '''
    mock_model_provider.invoke.return_value = fake_json_response

    runner = EvalRunner(mock_model_provider, mock_deliverable_repo)
    result = await runner.evaluate_mission(mission)

    assert result.score == 0.95
    assert "correctly prints" in result.reasoning
    assert result.dimension_scores["completeness"] == 1.0
    assert result.dimension_scores["accuracy"] == 1.0
    assert result.dimension_scores["quality"] == 0.85

    # Verify model invocation
    mock_model_provider.invoke.assert_called_once()
    call_kwargs = mock_model_provider.invoke.call_args.kwargs
    assert "messages" in call_kwargs
    assert "Write a hello world script" in call_kwargs["messages"][1]["content"]


@pytest.mark.asyncio
async def test_eval_runner_handles_malformed_json(mock_model_provider, mock_deliverable_repo):
    """Test EvalRunner catches json decode errors and degrades gracefully."""
    mission = Mission(id=uuid4(), goal="Do something")
    mock_deliverable_repo.list_by_mission.return_value = [
        Deliverable(
            mission_id=mission.id,
            agent="Hermes",
            type=DeliverableType.TEXT,
            content={"text": "stuff"},
            review_status=ReviewStatus.APPROVED,
            provenance_refs=[]
        )
    ]

    mock_model_provider.invoke.return_value = "I am not a JSON object, sorry!"

    runner = EvalRunner(mock_model_provider, mock_deliverable_repo)
    result = await runner.evaluate_mission(mission)

    assert result.score == 0.0
    assert "unparseable judge output" in result.reasoning.lower()
