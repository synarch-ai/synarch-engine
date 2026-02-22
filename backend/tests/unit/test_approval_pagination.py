import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

# Adjust path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from adapters.postgres.repositories import PostgresApprovalRepository
from domain.models.approval import Approval, ApprovalStatus, RiskLevel

@pytest.mark.asyncio
async def test_approval_pagination_logic():
    # Mock Pool/Connection
    pool = MagicMock()
    conn = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = conn

    repo = PostgresApprovalRepository(pool)
    mission_id = uuid4()

    # 1. Test Initial Fetch (No Cursor)
    # limit=2
    await repo.list(mission_id, limit=2)

    args, _ = conn.fetch.call_args
    query = args[0]
    params = args[1:]

    assert "WHERE mission_id = $1" in query
    assert "ORDER BY requested_at DESC" in query
    assert "LIMIT $2" in query
    assert params[0] == mission_id
    assert params[1] == 2

    # 2. Test Next Page (With Cursor)
    cursor_str = datetime.utcnow().isoformat()
    await repo.list(mission_id, limit=2, cursor=cursor_str)

    args, _ = conn.fetch.call_args
    query = args[0]
    params = args[1:]

    assert "requested_at < $2" in query
    assert "LIMIT $3" in query # limit is now 3rd param
    assert params[1].isoformat() == datetime.fromisoformat(cursor_str).isoformat()
