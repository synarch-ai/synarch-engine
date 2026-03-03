"""Integration tests for PostgresMissionRepository behavior."""

from __future__ import annotations

import json
import os
from uuid import UUID

import pytest

from adapters.postgres.repositories import PostgresMissionRepository, create_postgres_pool
from api.middleware.errors import SynarchError
from domain.models.mission import AuthorityMode, Mission, MissionStatus

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://synarch:synarch_local@localhost:5433/synarch",
)


def _json_obj(value):
    if isinstance(value, str):
        return json.loads(value)
    return value


@pytest.mark.asyncio
async def test_update_status_writes_state_change_event_and_outbox() -> None:
    pool = await create_postgres_pool(TEST_DATABASE_URL)
    repo = PostgresMissionRepository(pool)
    mission_id: UUID | None = None
    try:
        mission = Mission(
            goal="repo integration status event test",
            authority_mode=AuthorityMode.SUPERVISED,
            status=MissionStatus.CREATED,
        )
        mission.thread_id = str(mission.id)
        persisted = await repo.create(mission)
        mission_id = persisted.id

        await repo.update_status(
            persisted.id,
            MissionStatus.PAUSED.value,
            expected_version=persisted.version,
        )

        async with pool.acquire() as conn:
            mission_row = await conn.fetchrow(
                "SELECT status, version FROM missions WHERE id = $1::uuid",
                mission_id,
            )
            assert mission_row is not None
            assert mission_row["status"] == "paused"
            assert mission_row["version"] == 2

            event_row = await conn.fetchrow(
                """
                SELECT event_type, subject, payload
                FROM mission_events
                WHERE mission_id = $1::uuid
                  AND event_type = 'mission.state_changed'
                ORDER BY sequence DESC
                LIMIT 1
                """,
                mission_id,
            )
            assert event_row is not None
            assert event_row["subject"] == "synarch.mission_events.mission.state_changed"
            event_payload = _json_obj(event_row["payload"])
            assert event_payload["from_status"] == "created"
            assert event_payload["to_status"] == "paused"

            outbox_row = await conn.fetchrow(
                """
                SELECT subject, payload
                FROM mission_event_outbox
                WHERE mission_id = $1::uuid
                ORDER BY id DESC
                LIMIT 1
                """,
                mission_id,
            )
            assert outbox_row is not None
            assert outbox_row["subject"] == "synarch.mission_events.mission.state_changed"
            outbox_payload = _json_obj(outbox_row["payload"])
            assert outbox_payload["to_status"] == "paused"
    finally:
        if mission_id is not None:
            async with pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM mission_event_outbox WHERE mission_id = $1::uuid",
                    mission_id,
                )
                await conn.execute(
                    "DELETE FROM mission_events WHERE mission_id = $1::uuid",
                    mission_id,
                )
                await conn.execute(
                    "DELETE FROM mission_payloads WHERE mission_id = $1::uuid",
                    mission_id,
                )
                await conn.execute("DELETE FROM missions WHERE id = $1::uuid", mission_id)
        await pool.close()


@pytest.mark.asyncio
async def test_update_status_enforces_optimistic_lock() -> None:
    pool = await create_postgres_pool(TEST_DATABASE_URL)
    repo = PostgresMissionRepository(pool)
    mission_id: UUID | None = None
    try:
        mission = Mission(
            goal="repo integration optimistic lock test",
            authority_mode=AuthorityMode.SUPERVISED,
            status=MissionStatus.CREATED,
        )
        mission.thread_id = str(mission.id)
        persisted = await repo.create(mission)
        mission_id = persisted.id

        await repo.update_status(
            persisted.id,
            MissionStatus.PAUSED.value,
            expected_version=persisted.version,
        )

        with pytest.raises(SynarchError) as exc_info:
            await repo.update_status(
                persisted.id,
                MissionStatus.CANCELLED.value,
                expected_version=persisted.version,
            )

        err = exc_info.value
        assert err.code == "MISSION_CONFLICT"
        assert err.status_code == 409
        assert err.details.get("expected_version") == persisted.version
        assert err.details.get("current_version") == persisted.version + 1
    finally:
        if mission_id is not None:
            async with pool.acquire() as conn:
                await conn.execute(
                    "DELETE FROM mission_event_outbox WHERE mission_id = $1::uuid",
                    mission_id,
                )
                await conn.execute(
                    "DELETE FROM mission_events WHERE mission_id = $1::uuid",
                    mission_id,
                )
                await conn.execute(
                    "DELETE FROM mission_payloads WHERE mission_id = $1::uuid",
                    mission_id,
                )
                await conn.execute("DELETE FROM missions WHERE id = $1::uuid", mission_id)
        await pool.close()
