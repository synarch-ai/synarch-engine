import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from config import Settings
from container import Container
from ports.persistence import MissionRepository
from domain.models.mission import Mission
from typing import Optional, List, Dict
from uuid import UUID

class FakeMissionRepository(MissionRepository):
    async def create(self, mission: Mission) -> Mission: return mission
    async def get(self, mission_id: UUID) -> Optional[Mission]: return None
    async def list(self, status: str | None = None, limit: int = 50, offset: int = 0) -> List[Mission]: return []
    async def get_daily_metrics(self) -> List[Dict]: return []
    async def refresh_daily_metrics(self) -> None: pass
    async def patch_payload(self, mission_id: UUID, *, plan: List[str] | None = None, error_context: Dict | None = None) -> None: pass
    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None: pass

@pytest.fixture
def fake_container():
    settings = Settings(database_url="sqlite+aiosqlite:///:memory:")
    container = Container(
        event_bus=None,
        model_provider=None,
        checkpointer=None,
        db_pool=None,
        mission_repo=FakeMissionRepository(),
        task_repo=None,
        approval_repo=None,
        deliverable_repo=None,
    )
    return container

@pytest.fixture
def client(fake_container):
    app = create_app()
    app.state.container = fake_container
    return TestClient(app)

def test_get_daily_metrics_empty(client):
    response = client.get("/api/v1/metrics/daily")
    assert response.status_code == 200
    assert response.json()["metrics"] == []

def test_get_daily_metrics_with_data(client, fake_container):
    async def mock_get_daily_metrics():
        return [
            {
                "metrics_date": "2026-02-23T00:00:00Z",
                "authority_mode": "supervised",
                "total_missions": 10,
                "daily_cost_usd": 1.50,
                "daily_tokens": 15000,
                "avg_confidence_score": 0.92
            }
        ]
    fake_container.mission_repo.get_daily_metrics = mock_get_daily_metrics

    response = client.get("/api/v1/metrics/daily")
    assert response.status_code == 200
    data = response.json()
    assert len(data["metrics"]) == 1
    m = data["metrics"][0]
    assert m["total_missions"] == 10
    assert m["daily_cost_usd"] == 1.50
    assert m["daily_tokens"] == 15000
