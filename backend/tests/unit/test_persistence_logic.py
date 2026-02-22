import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

# Adjust path for imports if needed
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from domain.models.mission import Mission, MissionStatus
from domain.models.task import Task
from adapters.postgres.repositories import PostgresMissionRepository, PostgresTaskRepository

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

    repo = PostgresMissionRepository(pool)
    mission = Mission(goal="Test Goal")

    saved_mission = await repo.create(mission)

    assert saved_mission == mission
    # Verify transaction used
    assert conn.transaction.called
    # Verify execute called twice (1 for mission, 1 for payload)
    assert conn.execute.call_count == 2

    # Check first call (Mission insert)
    args, _ = conn.execute.call_args_list[0]
    assert "INSERT INTO missions" in args[0]
    assert args[1] == mission.id
    assert args[2] == "Test Goal"

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
