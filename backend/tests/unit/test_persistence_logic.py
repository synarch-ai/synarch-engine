import os

# Adjust path for imports if needed
import sys
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from adapters.postgres.repositories import PostgresMissionRepository, PostgresTaskRepository
from domain.models.mission import Mission
from domain.models.task import Task


@pytest.mark.asyncio
async def test_mission_repo_create():
    pool = MagicMock()
    conn = AsyncMock()
    # Mock context manager for pool.acquire()
    # pool.acquire() returns an object that has __aenter__
    pool.acquire.return_value.__aenter__.return_value = conn

    # Mock context manager for conn.transaction()
    conn.transaction = MagicMock()
    conn.transaction.return_value.__aenter__.return_value = AsyncMock()

    # Mock next_mission_sequence for event creation
    conn.fetchval.return_value = 1

    repo = PostgresMissionRepository(pool)
    mission = Mission(goal="Test Goal")

    saved_mission = await repo.create(mission)

    assert saved_mission == mission
    # Verify transaction used
    assert conn.transaction.called

    # Verify execute called:
    # 1. Mission Insert
    # 2. Payload Insert
    # 3. Event Insert (History)
    # 4. Outbox Insert
    assert conn.execute.call_count == 4

    # Check first call (Mission insert)
    args0, _ = conn.execute.call_args_list[0]
    assert "INSERT INTO missions" in args0[0]

    # Check last call (Outbox insert)
    args3, _ = conn.execute.call_args_list[3]
    assert "INSERT INTO mission_event_outbox" in args3[0]

@pytest.mark.asyncio
async def test_task_repo_create():
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    conn.transaction = MagicMock()
    conn.transaction.return_value.__aenter__.return_value = AsyncMock()

    repo = PostgresTaskRepository(pool)
    task = Task(
        mission_id=uuid4(),
        assigned_agent="TestAgent",
        description="Do something"
    )

    saved_task = await repo.create(task)

    assert saved_task == task
    assert conn.transaction.called
    # execute called once because no payload
    assert conn.execute.call_count == 1

    args, _ = conn.execute.call_args_list[0]
    assert "INSERT INTO tasks" in args[0]
    assert args[5] == "Do something"

@pytest.mark.asyncio
async def test_task_repo_create_with_payload():
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn
    conn.transaction = MagicMock()
    conn.transaction.return_value.__aenter__.return_value = AsyncMock()

    repo = PostgresTaskRepository(pool)
    task = Task(
        mission_id=uuid4(),
        assigned_agent="TestAgent",
        description="Do something",
        inputs={"key": "val"}
    )

    await repo.create(task)

    # execute called twice (task + payload)
    assert conn.execute.call_count == 2

    args2, _ = conn.execute.call_args_list[1]
    assert "INSERT INTO task_payloads" in args2[0]
