"""Integration tests for mission API durable path."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi.testclient import TestClient

from api.app import create_app
from api.middleware.errors import SynarchError
from domain.models.mission import Mission
from ports.persistence import MissionRepository


class InMemoryMissionRepository(MissionRepository):
    """Async in-memory repository for route integration tests."""

    def __init__(self) -> None:
        self._missions: dict[UUID, Mission] = {}

    @staticmethod
    def _enum_value(value: object) -> str:
        if hasattr(value, "value"):
            return str(value.value)
        return str(value)

    async def create(self, mission: Mission) -> Mission:
        now = datetime.utcnow()
        mission.created_at = now
        mission.updated_at = now
        mission.version = 1
        self._missions[mission.id] = mission
        return mission

    async def get(self, mission_id: UUID | str) -> Optional[Mission]:
        # Return none if mission_id comes as a string representation
        if isinstance(mission_id, str):
            mission_id = UUID(mission_id)
        return self._missions.get(mission_id)

    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None:
        if isinstance(mission_id, str):
            mission_id = UUID(mission_id)
        mission = self._missions.get(mission_id)
        if mission is None:
            return
        expected_version = kwargs.get("expected_version")
        if expected_version is not None and mission.version != int(expected_version):
            raise SynarchError(
                "MISSION_CONFLICT",
                f"Mission '{mission_id}' was modified concurrently.",
                status_code=409,
                details={"expected_version": int(expected_version), "current_version": mission.version},
            )
        from_status = self._enum_value(mission.status)
        allowed_transitions = {
            "created": {"planning", "executing", "paused", "cancelled", "failed"},
            "planning": {"executing", "cancelled", "failed"},
            "executing": {"awaiting_approval", "reviewing", "synthesizing", "paused", "paused_awaiting_resources", "completed", "cancelled", "failed"},
            "awaiting_approval": {"executing", "paused", "cancelled", "failed"},
            "reviewing": {"revising", "synthesizing", "failed"},
            "revising": {"executing", "reviewing", "failed"},
            "synthesizing": {"completed", "failed"},
            "paused": {"executing", "cancelled", "failed"},
            "paused_awaiting_resources": {"executing", "cancelled", "failed"},
            "completed": set(),
            "cancelled": set(),
            "failed": set(),
        }
        status_value = self._enum_value(status)
        if from_status != status_value and status_value not in allowed_transitions.get(from_status, set()):
            raise SynarchError(
                "MISSION_INVALID_TRANSITION",
                f"Invalid mission transition: {from_status} -> {status_value}",
                status_code=409,
            )
        mission.status = status_value
        mission.version += 1
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

    async def patch_payload(
        self,
        mission_id: UUID,
        *,
        plan: list[str] | None = None,
        error_context: dict | None = None,
    ) -> None:
        if isinstance(mission_id, str):
            mission_id = UUID(mission_id)
        mission = self._missions.get(mission_id)
        if mission is None:
            return
        if plan is not None:
            mission.plan = plan
        if error_context is not None:
            mission.error_context = error_context


class NoopMissionRuntime:
    async def launch_mission(self, mission_id: UUID) -> None:
        return None

    async def start_mission(self, mission_id: UUID) -> None:
        return None


@dataclass
class _TestContainer:
    mission_repo: MissionRepository
    mission_runtime: NoopMissionRuntime


def _build_client() -> TestClient:
    app = create_app(enable_idempotency=False)

    test_container = _TestContainer(
        mission_repo=InMemoryMissionRepository(),
        mission_runtime=NoopMissionRuntime(),
    )

    async def get_test_container() -> _TestContainer:
        return test_container

    # Note: we need to override the real container.
    # In api.app we might not have a direct way to override unless we monkeypatch or use dependency overrides.
    # We will override the dependency.
    from api.dependencies import get_container

    app.dependency_overrides[get_container] = get_test_container

    return TestClient(app)


def test_start_mission_and_fetch_state() -> None:
    with _build_client() as client:
        start_resp = client.post(
            "/api/v1/missions",
            json={"goal": "Implement S01 durable mission flow", "authority_mode": "supervised"},
        )
        assert start_resp.status_code == 201
        assert "x-request-id" in start_resp.headers
        start_body = start_resp.json()
        assert start_body["status"] == "created"
        assert "id" in start_body

        mission_id = start_body["id"]

        state_resp = client.get(f"/api/v1/missions/{mission_id}")
        assert state_resp.status_code == 200
        state_body = state_resp.json()
        assert state_body["id"] == mission_id
        assert state_body["status"] == "created"
        assert state_body["goal"] == "Implement S01 durable mission flow"
        assert state_body["authority_mode"] == "supervised"

def test_mission_not_found_returns_404() -> None:
    with _build_client() as client:
        resp = client.get("/api/v1/missions/8d5dcabb-b9a6-42a5-8568-a902fba5f99d")
        assert resp.status_code == 404
        body = resp.json()
        assert body["detail"] == "Mission not found"

