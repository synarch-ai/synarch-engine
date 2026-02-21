"""PostgreSQL repository adapters for persistence ports."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from uuid import UUID, uuid4

import asyncpg

from api.middleware.errors import SynarchError
from domain.models.mission import Mission
from ports.persistence import MissionRepository


def _enum_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


class PostgresMissionRepository(MissionRepository):
    """PostgreSQL-backed mission repository."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def create(self, mission: Mission) -> Mission:
        authority_mode = _enum_value(mission.authority_mode)
        status = _enum_value(mission.status)
        thread_id = mission.thread_id or str(mission.id)
        plan_json = json.dumps(mission.plan) if mission.plan is not None else None
        error_context_json = (
            json.dumps(mission.error_context) if mission.error_context is not None else None
        )

        event_id = uuid4()
        event_type = "mission.created"
        subject = "synarch.mission_events.mission.created"
        event_payload = json.dumps(
            {
                "mission_id": str(mission.id),
                "goal": mission.goal,
                "authority_mode": authority_mode,
                "status": status,
            }
        )
        outbox_headers = json.dumps(
            {
                "X-Mission-Id": str(mission.id),
                "X-Event-Type": event_type,
            }
        )

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    """
                    INSERT INTO missions (id, goal, authority_mode, status, thread_id)
                    VALUES ($1::uuid, $2, $3, $4::mission_status, $5)
                    RETURNING id, goal, status, authority_mode, version, created_at, updated_at, completed_at, thread_id
                    """,
                    mission.id,
                    mission.goal,
                    authority_mode,
                    status,
                    thread_id,
                )

                await conn.execute(
                    """
                    INSERT INTO mission_payloads (mission_id, plan, error_context)
                    VALUES ($1::uuid, $2::jsonb, $3::jsonb)
                    ON CONFLICT (mission_id) DO UPDATE
                      SET plan = EXCLUDED.plan,
                          error_context = EXCLUDED.error_context
                    """,
                    mission.id,
                    plan_json,
                    error_context_json,
                )

                sequence = await conn.fetchval(
                    "SELECT next_mission_sequence($1::uuid)",
                    mission.id,
                )

                await conn.execute(
                    """
                    INSERT INTO mission_events (
                        event_id,
                        mission_id,
                        sequence,
                        event_type,
                        subject,
                        schema_version,
                        payload
                    )
                    VALUES (
                        $1::uuid,
                        $2::uuid,
                        $3::bigint,
                        $4,
                        $5,
                        $6,
                        $7::jsonb
                    )
                    """,
                    event_id,
                    mission.id,
                    sequence,
                    event_type,
                    subject,
                    "1.0",
                    event_payload,
                )

                await conn.execute(
                    """
                    INSERT INTO mission_event_outbox (
                        event_id,
                        mission_id,
                        subject,
                        payload,
                        headers
                    )
                    VALUES (
                        $1::uuid,
                        $2::uuid,
                        $3,
                        $4::jsonb,
                        $5::jsonb
                    )
                    """,
                    event_id,
                    mission.id,
                    subject,
                    event_payload,
                    outbox_headers,
                )

        return Mission(
            id=row["id"],
            goal=row["goal"],
            status=row["status"],
            authority_mode=row["authority_mode"],
            version=row["version"],
            plan=mission.plan,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
            error_context=mission.error_context,
            thread_id=row["thread_id"],
        )

    async def get(self, mission_id: UUID) -> Mission | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    m.id,
                    m.goal,
                    m.status,
                    m.authority_mode,
                    m.version,
                    m.created_at,
                    m.updated_at,
                    m.completed_at,
                    m.thread_id,
                    mp.plan,
                    mp.error_context
                FROM missions m
                LEFT JOIN mission_payloads mp ON mp.mission_id = m.id
                WHERE m.id = $1::uuid
                  AND m.deleted_at IS NULL
                """,
                mission_id,
            )
            if row is None:
                return None
            return Mission(
                id=row["id"],
                goal=row["goal"],
                status=row["status"],
                authority_mode=row["authority_mode"],
                version=row["version"],
                plan=row["plan"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"],
                error_context=row["error_context"],
                thread_id=row["thread_id"],
            )

    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None:
        status_value = _enum_value(status)
        completed_at = kwargs.get("completed_at")
        expected_version = kwargs.get("expected_version")
        if not isinstance(completed_at, datetime):
            completed_at = None

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                current = await conn.fetchrow(
                    """
                    SELECT id, status, version
                    FROM missions
                    WHERE id = $1::uuid
                      AND deleted_at IS NULL
                    """,
                    mission_id,
                )
                if current is None:
                    raise SynarchError(
                        "MISSION_NOT_FOUND",
                        f"Mission '{mission_id}' not found.",
                        status_code=404,
                    )

                if expected_version is None:
                    expected_version = int(current["version"])

                from_status = str(current["status"])
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
                if from_status != status_value and status_value not in allowed_transitions.get(from_status, set()):
                    raise SynarchError(
                        "MISSION_INVALID_TRANSITION",
                        f"Invalid mission transition: {from_status} -> {status_value}",
                        status_code=409,
                        details={
                            "mission_id": str(mission_id),
                            "from_status": from_status,
                            "to_status": status_value,
                        },
                    )

                updated = await conn.fetchrow(
                    """
                    UPDATE missions
                    SET
                        status = $2::mission_status,
                        version = version + 1,
                        updated_at = NOW(),
                        completed_at = CASE
                            WHEN $3::timestamptz IS NOT NULL THEN $3::timestamptz
                            WHEN $2::mission_status = 'completed' THEN NOW()
                            ELSE completed_at
                        END
                    WHERE id = $1::uuid
                      AND deleted_at IS NULL
                      AND version = $4::integer
                    RETURNING id, status, version
                    """,
                    mission_id,
                    status_value,
                    completed_at,
                    int(expected_version),
                )

                if updated is None:
                    latest_version = await conn.fetchval(
                        "SELECT version FROM missions WHERE id = $1::uuid",
                        mission_id,
                    )
                    raise SynarchError(
                        "MISSION_CONFLICT",
                        f"Mission '{mission_id}' was modified concurrently.",
                        status_code=409,
                        details={
                            "mission_id": str(mission_id),
                            "expected_version": int(expected_version),
                            "current_version": int(latest_version) if latest_version is not None else None,
                        },
                    )

                event_id = uuid4()
                event_type = "mission.state_changed"
                subject = "synarch.mission_events.mission.state_changed"
                event_payload = json.dumps(
                    {
                        "mission_id": str(mission_id),
                        "from_status": str(current["status"]),
                        "to_status": status_value,
                        "version": int(updated["version"]),
                    }
                )
                outbox_headers = json.dumps(
                    {
                        "X-Mission-Id": str(mission_id),
                        "X-Event-Type": event_type,
                    }
                )

                sequence = await conn.fetchval(
                    "SELECT next_mission_sequence($1::uuid)",
                    mission_id,
                )

                await conn.execute(
                    """
                    INSERT INTO mission_events (
                        event_id,
                        mission_id,
                        sequence,
                        event_type,
                        subject,
                        schema_version,
                        payload
                    )
                    VALUES (
                        $1::uuid,
                        $2::uuid,
                        $3::bigint,
                        $4,
                        $5,
                        $6,
                        $7::jsonb
                    )
                    """,
                    event_id,
                    mission_id,
                    sequence,
                    event_type,
                    subject,
                    "1.0",
                    event_payload,
                )

                await conn.execute(
                    """
                    INSERT INTO mission_event_outbox (
                        event_id,
                        mission_id,
                        subject,
                        payload,
                        headers
                    )
                    VALUES (
                        $1::uuid,
                        $2::uuid,
                        $3,
                        $4::jsonb,
                        $5::jsonb
                    )
                    """,
                    event_id,
                    mission_id,
                    subject,
                    event_payload,
                    outbox_headers,
                )

    async def list(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Mission]:
        params: list[object] = []
        where = ["m.deleted_at IS NULL"]
        if status is not None:
            where.append(f"m.status = ${len(params) + 1}::mission_status")
            params.append(_enum_value(status))

        params.extend([limit, offset])
        sql = f"""
            SELECT
                m.id,
                m.goal,
                m.status,
                m.authority_mode,
                m.version,
                m.created_at,
                m.updated_at,
                m.completed_at,
                m.thread_id,
                mp.plan,
                mp.error_context
            FROM missions m
            LEFT JOIN mission_payloads mp ON mp.mission_id = m.id
            WHERE {' AND '.join(where)}
            ORDER BY m.created_at DESC
            LIMIT ${len(params) - 1}
            OFFSET ${len(params)}
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)
            return [
                Mission(
                    id=row["id"],
                    goal=row["goal"],
                    status=row["status"],
                    authority_mode=row["authority_mode"],
                    version=row["version"],
                    plan=row["plan"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    completed_at=row["completed_at"],
                    error_context=row["error_context"],
                    thread_id=row["thread_id"],
                )
                for row in rows
            ]

    async def patch_payload(
        self,
        mission_id: UUID,
        *,
        plan: list[str] | None = None,
        error_context: dict | None = None,
    ) -> None:
        plan_json = json.dumps(plan) if plan is not None else None
        error_context_json = json.dumps(error_context) if error_context is not None else None
        if plan_json is None and error_context_json is None:
            return

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO mission_payloads (mission_id, plan, error_context)
                    VALUES ($1::uuid, $2::jsonb, $3::jsonb)
                    ON CONFLICT (mission_id) DO UPDATE
                    SET
                        plan = COALESCE(EXCLUDED.plan, mission_payloads.plan),
                        error_context = COALESCE(EXCLUDED.error_context, mission_payloads.error_context)
                    """,
                    mission_id,
                    plan_json,
                    error_context_json,
                )
                await conn.execute(
                    """
                    UPDATE missions
                    SET updated_at = NOW()
                    WHERE id = $1::uuid
                      AND deleted_at IS NULL
                    """,
                    mission_id,
                )


async def create_postgres_pool(database_url: str) -> asyncpg.Pool:
    """Create a shared asyncpg pool for repository adapters."""
    attempts = 0
    max_attempts = 5
    while True:
        try:
            return await asyncpg.create_pool(
                dsn=database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                timeout=10,
            )
        except Exception:
            attempts += 1
            if attempts >= max_attempts:
                raise
            await asyncio.sleep(min(2**attempts, 10))
