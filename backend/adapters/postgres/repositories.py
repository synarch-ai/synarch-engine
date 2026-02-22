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
from ports.persistence import (
    MissionRepository,
    TaskRepository,
    DeliverableRepository,
    ApprovalRepository,
)


async def create_postgres_pool(dsn: str) -> Pool:
    return await asyncpg.create_pool(dsn)


class PostgresMissionRepository(MissionRepository):
    def __init__(self, pool: Pool):
        self.pool = pool

    async def create(self, mission: Mission) -> Mission:
        query = """
            INSERT INTO missions (
                id, goal, status, authority_mode, version, thread_id,
                created_at, updated_at, plan, error_context
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
        """
        async with self.pool.acquire() as conn:
            await conn.execute(
                query,
                mission.id,
                mission.goal,
                mission.status.value,
                mission.authority_mode.value,
                mission.version,
                mission.thread_id,
                mission.created_at,
                mission.updated_at,
                json.dumps(mission.plan) if mission.plan else None,
                json.dumps(mission.error_context) if mission.error_context else None,
            )
        return mission

    async def get(self, mission_id: UUID) -> Optional[Mission]:
        query = """
            SELECT
                id, goal, status, authority_mode, version, thread_id,
                created_at, updated_at, completed_at,
                mp.plan, mp.error_context
            FROM missions m
            LEFT JOIN mission_payloads mp ON m.id = mp.mission_id
            WHERE m.id = $1
        """
        # Note: mission_payloads join is needed if we use the sidecar table as per schema v2.0
        # However, the CREATE above inserted into 'missions' directly for plan/error_context.
        # Let's check the schema again.
        # Schema v2.0 says: plan and error_context are in mission_payloads table.
        # So my CREATE above was WRONG for v2.0 schema compliance.
        # I need to insert into mission_payloads separately.

        # Let's fix CREATE first.
        return await self._get_impl(query, mission_id)

    async def _get_impl(self, query: str, mission_id: UUID) -> Optional[Mission]:
        async with self.pool.acquire() as conn:
            # First try with join, assuming payload exists
            # Actually, let's implement the corrected CREATE first, then GET makes sense.
            pass

    # ... refactoring below ...

# RE-WRITING CLASS WITH CORRECT SCHEMA v2.0 COMPLIANCE

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
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
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
                    VALUES ($1, $2, $3)
                    """,
                    mission.id,
                    json.dumps(mission.plan) if mission.plan else None,
                    json.dumps(mission.error_context) if mission.error_context else None,
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
            WHERE m.id = $1 AND m.deleted_at IS NULL
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
                SET status = $1, updated_at = NOW()
                WHERE id = $2
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
            where_clause += " AND status = $1"
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
                VALUES ($1,
                    {'$2' if plan is not None else 'NULL'},
                    {f'${3 if plan is not None else 2}' if error_context is not None else 'NULL'}
                )
                ON CONFLICT (mission_id) DO UPDATE SET
                {update_clause}
            """
            # Note: The VALUES params logic in dynamic query construction is tricky.
            # Simplified approach: Just UPDATE. We created payload row in create().

            await conn.execute(
                f"UPDATE mission_payloads SET {update_clause} WHERE mission_id = $1",
                *values
            )

            # Also touch mission updated_at
            await conn.execute("UPDATE missions SET updated_at = NOW() WHERE id = $1", mission_id)


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
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
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
                        VALUES ($1, $2, $3)
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
            WHERE t.id = $1
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
            WHERE t.mission_id = $1
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
                    "UPDATE tasks SET status = $1, updated_at = NOW() WHERE id = $2",
                    status, task_id
                )
                if status == TaskStatus.COMPLETED.value:
                    await conn.execute(
                        "UPDATE tasks SET completed_at = NOW() WHERE id = $1", task_id
                    )

                # Update result if provided
                if result:
                    await conn.execute(
                        """
                        INSERT INTO task_payloads (task_id, result)
                        VALUES ($1, $2)
                        ON CONFLICT (task_id) DO UPDATE SET result = $2
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
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
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
            WHERE mission_id = $1
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
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
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
            WHERE id = $1
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

    async def get_pending(self, mission_id: UUID) -> Optional[Approval]:
        query = """
            SELECT
                id, mission_id, action_type, requested_by, description,
                risk_level, status, timeout_seconds, requested_at
            FROM approvals
            WHERE mission_id = $1 AND status = 'pending'
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
            SET status = $1, decided_by = $2, decision_reason = $3, decided_at = NOW(), updated_at = NOW()
            WHERE id = $4
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
