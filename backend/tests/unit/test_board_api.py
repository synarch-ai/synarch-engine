import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

# Adjust path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from api.routes.missions import list_mission_tasks, list_mission_deliverables
from domain.models.task import Task, TaskStatus
from domain.models.deliverable import Deliverable, DeliverableType, ReviewStatus

@pytest.mark.asyncio
async def test_board_api_contracts():
    mission_id = uuid4()
    task_id = uuid4()

    # 1. Mock Container & Repos
    container = MagicMock()

    mock_task = Task(
        id=task_id,
        mission_id=mission_id,
        assigned_agent="hephaestus",
        description="Write code",
        status=TaskStatus.IN_PROGRESS
    )
    container.task_repo.list_by_mission = AsyncMock(return_value=[mock_task])

    mock_deliv = Deliverable(
        id=uuid4(),
        mission_id=mission_id,
        task_id=task_id,
        agent="hephaestus",
        type=DeliverableType.CODE,
        content={"file": "main.py"},
        review_status=ReviewStatus.APPROVED
    )
    container.deliverable_repo.list_by_mission = AsyncMock(return_value=[mock_deliv])

    # 2. Test Task List
    tasks_response = await list_mission_tasks(mission_id, container)
    assert len(tasks_response) == 1
    assert tasks_response[0].id == task_id
    assert tasks_response[0].status == TaskStatus.IN_PROGRESS

    # 3. Test Deliverable List
    deliv_response = await list_mission_deliverables(mission_id, container)
    assert len(deliv_response) == 1
    assert deliv_response[0].type == DeliverableType.CODE
    assert deliv_response[0].content["file"] == "main.py"

    print("S08 API Contracts Verified")
