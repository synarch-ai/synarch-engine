"""Integration tests for mission API durable path."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi.testclient import TestClient

from api.app import create_app
from domain.models.mission import Mission
from ports.persistence import MissionRepository


class InMemoryMissionRepository(MissionRepository):
    """Async in-memory repository for route integration tests."""

    def __init__(self) -> None:
        self._missions: dict[UUID, Mission] = {}

    async def create(self, mission: Mission) -> Mission:
        now = datetime.utcnow()
        mission.created_at = now
        mission.updated_at = now
        self._missions[mission.id] = mission
        return mission

    async def get(self, mission_id: UUID) -> Optional[Mission]:
        return self._missions.get(mission_id)

    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None:
        mission = self._missions.get(mission_id)
        if mission is None:
            return
        mission.status = status
        mission.updated_at = datetime.utcnow()
        if status == "completed":
            mission.completed_at = mission.updated_at

    async def list(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Mission]:
        missions = list(self._missions.values())
        if status is not None:
            missions = [m for m in missions if str(m.status) == status or getattr(m.status, "value", None) == status]
        return missions[offset : offset + limit]


@dataclass
class _TestContainer:
    mission_repo: MissionRepository


def _build_client() -> TestClient:
    app = create_app()
    app.state.container = _TestContainer(mission_repo=InMemoryMissionRepository())
    return TestClient(app)


def test_start_mission_and_fetch_state() -> None:
    with _build_client() as client:
        start_resp = client.post(
            "/mission/start",
            json={"goal": "Implement S01 durable mission flow", "authority_mode": "supervised"},
        )
        assert start_resp.status_code == 200
        start_body = start_resp.json()
        assert start_body["status"] == "created"
        mission_id = start_body["mission_id"]

        state_resp = client.get(f"/mission/{mission_id}/state")
        assert state_resp.status_code == 200
        state_body = state_resp.json()
        assert state_body["mission_id"] == mission_id
        assert state_body["goal"] == "Implement S01 durable mission flow"
        assert state_body["status"] == "created"
        assert state_body["authority_mode"] == "supervised"


def test_mission_lifecycle_pause_resume_cancel() -> None:
    with _build_client() as client:
        start_resp = client.post(
            "/mission/start",
            json={"goal": "Lifecycle transitions", "authority_mode": "guided"},
        )
        mission_id = start_resp.json()["mission_id"]

        pause_resp = client.post(f"/mission/{mission_id}/pause")
        assert pause_resp.status_code == 200
        assert pause_resp.json()["status"] == "paused"

        resume_resp = client.post(f"/mission/{mission_id}/resume")
        assert resume_resp.status_code == 200
        assert resume_resp.json()["status"] == "executing"

        cancel_resp = client.post(f"/mission/{mission_id}/cancel")
        assert cancel_resp.status_code == 200
        assert cancel_resp.json()["status"] == "cancelled"


def test_mission_not_found_returns_404() -> None:
    with _build_client() as client:
        resp = client.get("/mission/8d5dcabb-b9a6-42a5-8568-a902fba5f99d/state")
        assert resp.status_code == 404
        body = resp.json()
        assert body["error"]["code"] == "MISSION_NOT_FOUND"
