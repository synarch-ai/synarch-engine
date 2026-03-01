import json
from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID

import asyncpg
from asyncpg import Pool, Record

from domain.models.mission import Mission, MissionStatus, AuthorityMode
from domain.models.task import Task, TaskStatus
from domain.models.deliverable import Deliverable, DeliverableType, ReviewStatus
from domain.models.approval import Approval, ApprovalStatus, RiskLevel
from domain.events.envelope import EventEnvelope, EventTelemetry
from ports.persistence import (
    MissionRepository,
    TaskRepository,
    DeliverableRepository,
    ApprovalRepository,
    EventRepository,
)


async def create_postgres_pool(dsn: str) -> Pool:
    return await asyncpg.create_pool(dsn)


class PostgresMissionRepository(MissionRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, mission: Mission) -> Mission:
        # Transaction to insert into missions and mission_payloads
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 1. Insert Mission
                await conn.execute(
                    """
                    INSERT INTO missions (
                        id, goal, status, authority_mode, version, thread_id,
                        created_at, updated_at
                    ) VALUES ($1::uuid, $2, $3::mission_status, $4::authority_mode, $5, $6, $7, $8)
                    """,
                    mission.id,
                    mission.goal,
                    mission.status.value,
                    mission.authority_mode.value,
                    mission.version,
                    mission.thread_id,
                    mission.created_at,
                    mission.updated_at,
                )

                # 2. Insert Payload (Plan, Error Context)
                # Schema: mission_payloads(mission_id, constraints, budget_policy, plan, error_context)
                await conn.execute(
                    """
                    INSERT INTO mission_payloads (mission_id, plan, error_context)
                    VALUES ($1::uuid, $2::jsonb, $3::jsonb)
                    """,
                    mission.id,
                    json.dumps(mission.plan) if mission.plan else None,
                    json.dumps(mission.error_context) if mission.error_context else None,
                )

                # 3. Create and Persist 'mission.created' Event + Outbox (Atomic)
                # We duplicate the EventRepo logic here to ensure atomicity within the same transaction connection
                event = EventEnvelope.create(
                    event_type="mission.created",
                    mission_id=str(mission.id),
                    payload={
                        "goal": mission.goal,
                        "authority_mode": mission.authority_mode.value
                    },
                    agent="god",  # Created by user/god
                    stage="created"
                )

                # 3a. Allocate Sequence
                seq_val = await conn.fetchval("SELECT next_mission_sequence($1::uuid)", str(mission.id))
                event.sequence = seq_val

                # 3b. Insert Event
                await conn.execute(
                    """
                    INSERT INTO mission_events (
                        event_id, mission_id, sequence, event_type, subject,
                        stage, agent, schema_version, correlation_id, causation_id,
                        idempotency_key, payload, cost_usd, token_count, latency_ms, created_at
                    ) VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8, $9::uuid, $10::uuid, $11, $12::jsonb, $13, $14, $15, $16)
                    """,
                    event.id,
                    event.mission_id,
                    event.sequence,
                    event.type,
                    event.subject,
                    event.stage,
                    event.agent,
                    event.schema_version,
                    event.correlation_id,
                    event.causation_id,
                    event.idempotency_key,
                    json.dumps(event.payload),
                    event.telemetry.cost_usd,
                    event.telemetry.tokens,
                    event.telemetry.latency_ms,
                    event.timestamp,
                )

                # 3c. Insert Outbox
                await conn.execute(
                    """
                    INSERT INTO mission_event_outbox (
                        event_id, mission_id, subject, payload, created_at
                    ) VALUES ($1::uuid, $2::uuid, $3, $4::jsonb, $5)
                    """,
                    event.id,
                    event.mission_id,
                    event.subject,
                    json.dumps(event.payload),
                    event.timestamp,
                )

        return mission

    async def get(self, mission_id: UUID) -> Optional[Mission]:
        query = """
            SELECT
                m.id, m.goal, m.status, m.authority_mode, m.version, m.thread_id,
                m.created_at, m.updated_at, m.completed_at,
                mp.plan, mp.error_context
            FROM missions m
            LEFT JOIN mission_payloads mp ON m.id = mp.mission_id
            WHERE m.id = $1::uuid AND m.deleted_at IS NULL
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, mission_id)
            if not row:
                return None

            return Mission(
                id=row["id"],
                goal=row["goal"],
                status=MissionStatus(row["status"]),
                authority_mode=AuthorityMode(row["authority_mode"]),
                version=row["version"],
                thread_id=row["thread_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                completed_at=row["completed_at"],
                plan=json.loads(row["plan"]) if row["plan"] else None,
                error_context=json.loads(row["error_context"]) if row["error_context"] else None,
            )

    async def update_status(self, mission_id: UUID, status: str, **kwargs) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE missions
                SET status = $1::mission_status, updated_at = NOW()
                WHERE id = $2::uuid
                """,
                status,
                mission_id,
            )

    async def list(self, status: str | None = None, limit: int = 50, offset: int = 0) -> List[Mission]:
        # Simple list does not join payloads for performance usually, but domain model needs fields.
        # For now, we fetch base fields.
        where_clause = "WHERE deleted_at IS NULL"
        args = []
        if status:
            where_clause += " AND status = $1::mission_status"
            args.append(status)

        # Add limit/offset args
        args.append(limit)
        args.append(offset)

        limit_idx = len(args) - 1
        offset_idx = len(args)

        query = f"""
            SELECT
                id, goal, status, authority_mode, version, thread_id,
                created_at, updated_at, completed_at
            FROM missions
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ${limit_idx} OFFSET ${offset_idx}
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [
                Mission(
                    id=row["id"],
                    goal=row["goal"],
                    status=MissionStatus(row["status"]),
                    authority_mode=AuthorityMode(row["authority_mode"]),
                    version=row["version"],
                    thread_id=row["thread_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    completed_at=row["completed_at"],
                    # Plan/Error context omitted in list view for now or need separate fetch
                )
                for row in rows
            ]

    async def patch_payload(
        self,
        mission_id: UUID,
        *,
        plan: List[str] | None = None,
        error_context: dict | None = None,
    ) -> None:
        # Upsert into mission_payloads
        async with self.pool.acquire() as conn:
            # We use ON CONFLICT DO UPDATE
            # But standard SQL insert on conflict requires constraint name or unique index.
            # mission_payloads PK is mission_id.

            updates = []
            values = [mission_id]
            idx = 2

            if plan is not None:
                updates.append(f"plan = ${idx}")
                values.append(json.dumps(plan))
                idx += 1

            if error_context is not None:
                updates.append(f"error_context = ${idx}")
                values.append(json.dumps(error_context))
                idx += 1

            if not updates:
                return

            # This assumes row exists (created at mission creation).
            # If not, we should Insert.
            # Safe bet: INSERT ... ON CONFLICT (mission_id) DO UPDATE SET ...

            # Construct dynamic query is safer
            update_clause = ", ".join(updates)

            query = f"""
                INSERT INTO mission_payloads (mission_id, plan, error_context)
                VALUES ($1::uuid,
                    {'$2::jsonb' if plan is not None else 'NULL'},
                    {f'${3 if plan is not None else 2}::jsonb' if error_context is not None else 'NULL'}
                )
                ON CONFLICT (mission_id) DO UPDATE SET
                {update_clause}
            """
            # Note: The VALUES params logic in dynamic query construction is tricky.
            # Simplified approach: Just UPDATE. We created payload row in create().

            # For update clause with jsonb casting
            upd_clause_cast = update_clause.replace("$2", "$2::jsonb").replace("$3", "$3::jsonb")

            await conn.execute(
                f"UPDATE mission_payloads SET {upd_clause_cast} WHERE mission_id = $1::uuid",
                *values
            )

            # Also touch mission updated_at
            await conn.execute("UPDATE missions SET updated_at = NOW() WHERE id = $1::uuid", mission_id)


class PostgresTaskRepository(TaskRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, task: Task) -> Task:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 1. Insert Task
                await conn.execute(
                    """
                    INSERT INTO tasks (
                        id, mission_id, parent_task_id, assigned_agent, description,
                        status, priority, created_at
                    ) VALUES ($1::uuid, $2::uuid, $3::uuid, $4, $5, $6::task_status, $7, $8)
                    """,
                    task.id,
                    task.mission_id,
                    task.parent_task_id,
                    task.assigned_agent,
                    task.description,
                    task.status.value,
                    task.priority,
                    task.created_at,
                )

                # 2. Insert Payload (inputs, result)
                if task.inputs or task.result:
                    await conn.execute(
                        """
                        INSERT INTO task_payloads (task_id, inputs, result)
                        VALUES ($1::uuid, $2::jsonb, $3::jsonb)
                        """,
                        task.id,
                        json.dumps(task.inputs) if task.inputs else None,
                        json.dumps(task.result) if task.result else None,
                    )
        return task

    async def get(self, task_id: UUID) -> Optional[Task]:
        query = """
            SELECT
                t.id, t.mission_id, t.parent_task_id, t.assigned_agent, t.description,
                t.status, t.priority, t.created_at, t.completed_at,
                tp.inputs, tp.result
            FROM tasks t
            LEFT JOIN task_payloads tp ON t.id = tp.task_id
            WHERE t.id = $1::uuid
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, task_id)
            if not row:
                return None
            return Task(
                id=row["id"],
                mission_id=row["mission_id"],
                parent_task_id=row["parent_task_id"],
                assigned_agent=row["assigned_agent"],
                description=row["description"],
                status=TaskStatus(row["status"]),
                priority=row["priority"],
                created_at=row["created_at"],
                completed_at=row["completed_at"],
                inputs=json.loads(row["inputs"]) if row["inputs"] else None,
                result=json.loads(row["result"]) if row["result"] else None,
            )

    async def list_by_mission(self, mission_id: UUID) -> List[Task]:
        query = """
            SELECT
                t.id, t.mission_id, t.parent_task_id, t.assigned_agent, t.description,
                t.status, t.priority, t.created_at, t.completed_at,
                tp.inputs, tp.result
            FROM tasks t
            LEFT JOIN task_payloads tp ON t.id = tp.task_id
            WHERE t.mission_id = $1::uuid
            ORDER BY t.created_at ASC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, mission_id)
            return [
                Task(
                    id=row["id"],
                    mission_id=row["mission_id"],
                    parent_task_id=row["parent_task_id"],
                    assigned_agent=row["assigned_agent"],
                    description=row["description"],
                    status=TaskStatus(row["status"]),
                    priority=row["priority"],
                    created_at=row["created_at"],
                    completed_at=row["completed_at"],
                    inputs=json.loads(row["inputs"]) if row["inputs"] else None,
                    result=json.loads(row["result"]) if row["result"] else None,
                )
                for row in rows
            ]

    async def update_status(self, task_id: UUID, status: str, result: dict | None = None) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Update status
                await conn.execute(
                    "UPDATE tasks SET status = $1::task_status, updated_at = NOW() WHERE id = $2::uuid",
                    status, task_id
                )
                if status == TaskStatus.COMPLETED.value:
                    await conn.execute(
                        "UPDATE tasks SET completed_at = NOW() WHERE id = $1::uuid", task_id
                    )

                # Update result if provided
                if result:
                    await conn.execute(
                        """
                        INSERT INTO task_payloads (task_id, result)
                        VALUES ($1::uuid, $2::jsonb)
                        ON CONFLICT (task_id) DO UPDATE SET result = $2::jsonb
                        """,
                        task_id, json.dumps(result)
                    )


class PostgresDeliverableRepository(DeliverableRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, deliverable: Deliverable) -> Deliverable:
        query = """
            INSERT INTO deliverables (
                id, mission_id, task_id, agent, type, content,
                review_status, provenance_refs, created_at
            ) VALUES ($1::uuid, $2::uuid, $3::uuid, $4, $5, $6::jsonb, $7::deliverable_review_status, $8::jsonb, $9)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                deliverable.id,
                deliverable.mission_id,
                deliverable.task_id,
                deliverable.agent,
                deliverable.type.value,
                json.dumps(deliverable.content),
                deliverable.review_status.value,
                json.dumps(deliverable.provenance_refs),
                deliverable.created_at,
            )
        return deliverable

    async def list_by_mission(self, mission_id: UUID) -> List[Deliverable]:
        query = """
            SELECT
                id, mission_id, task_id, agent, type, content,
                review_status, provenance_refs, created_at
            FROM deliverables
            WHERE mission_id = $1::uuid
            ORDER BY created_at DESC
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, mission_id)
            return [
                Deliverable(
                    id=row["id"],
                    mission_id=row["mission_id"],
                    task_id=row["task_id"],
                    agent=row["agent"],
                    type=DeliverableType(row["type"]),
                    content=json.loads(row["content"]),
                    review_status=ReviewStatus(row["review_status"]),
                    provenance_refs=json.loads(row["provenance_refs"]),
                    created_at=row["created_at"],
                )
                for row in rows
            ]


class PostgresApprovalRepository(ApprovalRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, approval: Approval) -> Approval:
        query = """
            INSERT INTO approvals (
                id, mission_id, action_type, requested_by, description,
                risk_level, status, timeout_seconds, requested_at
            ) VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7::approval_status, $8, $9)
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                approval.id,
                approval.mission_id,
                approval.action_type,
                approval.requested_by,
                approval.description,
                approval.risk_level.value,
                approval.status.value,
                approval.timeout_seconds,
                approval.requested_at,
            )
        return approval

    async def get(self, approval_id: UUID) -> Optional[Approval]:
        query = """
            SELECT
                id, mission_id, action_type, requested_by, description,
                risk_level, status, timeout_seconds, requested_at,
                decided_by, decision_reason, decided_at
            FROM approvals
            WHERE id = $1::uuid
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, approval_id)
            if not row:
                return None
            return Approval(
                id=row["id"],
                mission_id=row["mission_id"],
                action_type=row["action_type"],
                requested_by=row["requested_by"],
                description=row["description"],
                risk_level=RiskLevel(row["risk_level"]),
                status=ApprovalStatus(row["status"]),
                timeout_seconds=row["timeout_seconds"],
                requested_at=row["requested_at"],
                decided_by=row["decided_by"],
                decision_reason=row["decision_reason"],
                decided_at=row["decided_at"],
            )

    async def list(self, mission_id: UUID, limit: int = 50, cursor: str | None = None) -> List[Approval]:
        # Keyset pagination using requested_at
        # Cursor is expected to be an ISO timestamp string
        where_clause = "WHERE mission_id = $1::uuid"
        args = [mission_id]

        if cursor:
            where_clause += " AND requested_at < $2"
            args.append(datetime.fromisoformat(cursor))

        args.append(limit)
        limit_idx = len(args)

        query = f"""
            SELECT
                id, mission_id, action_type, requested_by, description,
                risk_level, status, timeout_seconds, requested_at,
                decided_by, decision_reason, decided_at
            FROM approvals
            {where_clause}
            ORDER BY requested_at DESC
            LIMIT ${limit_idx}
        """

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [
                Approval(
                    id=row["id"],
                    mission_id=row["mission_id"],
                    action_type=row["action_type"],
                    requested_by=row["requested_by"],
                    description=row["description"],
                    risk_level=RiskLevel(row["risk_level"]),
                    status=ApprovalStatus(row["status"]),
                    timeout_seconds=row["timeout_seconds"],
                    requested_at=row["requested_at"],
                    decided_by=row["decided_by"],
                    decision_reason=row["decision_reason"],
                    decided_at=row["decided_at"],
                )
                for row in rows
            ]

    async def get_pending(self, mission_id: UUID) -> Optional[Approval]:
        query = """
            SELECT
                id, mission_id, action_type, requested_by, description,
                risk_level, status, timeout_seconds, requested_at,
                decided_by, decision_reason, decided_at
            FROM approvals
            WHERE mission_id = $1::uuid AND status = 'pending'::approval_status
            ORDER BY requested_at DESC
            LIMIT 1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, mission_id)
            if not row:
                return None
            return Approval(
                id=row["id"],
                mission_id=row["mission_id"],
                action_type=row["action_type"],
                requested_by=row["requested_by"],
                description=row["description"],
                risk_level=RiskLevel(row["risk_level"]),
                status=ApprovalStatus(row["status"]),
                timeout_seconds=row["timeout_seconds"],
                requested_at=row["requested_at"],
            )

    async def decide(self, approval_id: UUID, decision: str, decided_by: str, reason: str | None = None) -> Approval:
        query = """
            UPDATE approvals
            SET status = $1::approval_status, decided_by = $2, decision_reason = $3, decided_at = NOW(), updated_at = NOW()
            WHERE id = $4::uuid
            RETURNING id, mission_id, action_type, requested_by, description,
                      risk_level, status, timeout_seconds, requested_at,
                      decided_by, decision_reason, decided_at
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, decision, decided_by, reason, approval_id)
            if not row:
                raise ValueError(f"Approval {approval_id} not found")
            return Approval(
                id=row["id"],
                mission_id=row["mission_id"],
                action_type=row["action_type"],
                requested_by=row["requested_by"],
                description=row["description"],
                risk_level=RiskLevel(row["risk_level"]),
                status=ApprovalStatus(row["status"]),
                timeout_seconds=row["timeout_seconds"],
                requested_at=row["requested_at"],
                decided_by=row["decided_by"],
                decision_reason=row["decision_reason"],
                decided_at=row["decided_at"],
            )


class PostgresEventRepository(EventRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, event: EventEnvelope) -> EventEnvelope:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 1. Allocate sequence
                seq_val = await conn.fetchval("SELECT next_mission_sequence($1::uuid)", event.mission_id)
                event.sequence = seq_val

                # 2. Insert event (History)
                query = """
                    INSERT INTO mission_events (
                        event_id, mission_id, sequence, event_type, subject,
                        stage, agent, schema_version, correlation_id, causation_id,
                        idempotency_key, payload, cost_usd, token_count, latency_ms, created_at
                    ) VALUES ($1::uuid, $2::uuid, $3, $4, $5, $6, $7, $8, $9::uuid, $10::uuid, $11, $12::jsonb, $13, $14, $15, $16)
                """
                await conn.execute(
                    query,
                    event.id,
                    event.mission_id,
                    event.sequence,
                    event.type,
                    event.subject,
                    event.stage,
                    event.agent,
                    event.schema_version,
                    event.correlation_id,
                    event.causation_id,
                    event.idempotency_key,
                    json.dumps(event.payload),
                    event.telemetry.cost_usd,
                    event.telemetry.tokens,
                    event.telemetry.latency_ms,
                    event.timestamp,
                )

                # 3. Insert Outbox (Reliable Publishing)
                outbox_query = """
                    INSERT INTO mission_event_outbox (
                        event_id, mission_id, subject, payload, created_at
                    ) VALUES ($1::uuid, $2::uuid, $3, $4::jsonb, $5)
                """
                await conn.execute(
                    outbox_query,
                    event.id,
                    event.mission_id,
                    event.subject,
                    json.dumps(event.payload),
                    event.timestamp,
                )
        return event

    async def list_by_mission(self, mission_id: UUID, limit: int = 100, offset: int = 0) -> List[EventEnvelope]:
        query = """
            SELECT
                event_id, mission_id, sequence, event_type, subject,
                stage, agent, schema_version, correlation_id, causation_id,
                idempotency_key, payload, cost_usd, token_count, latency_ms, created_at
            FROM mission_events
            WHERE mission_id = $1::uuid
            ORDER BY sequence ASC
            LIMIT $2 OFFSET $3
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, str(mission_id), limit, offset)
            return [
                EventEnvelope(
                    id=str(row["event_id"]),
                    type=row["event_type"],
                    subject=row["subject"],
                    mission_id=str(row["mission_id"]),
                    agent=row["agent"],
                    stage=row["stage"],
                    timestamp=row["created_at"],
                    sequence=row["sequence"],
                    schema_version=row["schema_version"],
                    idempotency_key=row["idempotency_key"],
                    correlation_id=str(row["correlation_id"]) if row["correlation_id"] else None,
                    causation_id=str(row["causation_id"]) if row["causation_id"] else None,
                    telemetry=EventTelemetry(
                        cost_usd=float(row["cost_usd"]) if row["cost_usd"] is not None else None,
                        tokens=row["token_count"],
                        latency_ms=row["latency_ms"]
                    ),
                    payload=json.loads(row["payload"]),
                )
                for row in rows
            ]
