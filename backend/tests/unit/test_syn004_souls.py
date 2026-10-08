"""SYN-004: soul files resolve independent of cwd and fail loudly when missing."""
import os

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from config import Settings
from domain.agents.zeus import ZeusAgent


def test_default_souls_dir_is_absolute_and_exists():
    from pathlib import Path
    p = Path(Settings().souls_dir)
    assert p.is_absolute() and (p / "zeus" / "soul.md").is_file()


def test_soul_loads_from_other_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    agent = ZeusAgent(name="zeus", model="m", soul_path=Settings().souls_dir)
    assert "generic" not in agent.soul.lower()
    assert agent.soul != "You are zeus, an AI agent in the Synarch hierarchy."


def test_missing_soul_raises(tmp_path):
    agent = ZeusAgent(name="zeus", model="m", soul_path=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        agent.load_soul()


def test_soul_endpoint_from_other_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = TestClient(create_app(enable_idempotency=False))
    r = c.get("/api/v1/agents/zeus/soul")
    assert r.status_code == 200 and r.json()["soul"].strip()
    assert "not found" not in r.json()["soul"].lower()
    assert c.get("/api/v1/agents/nobody/soul").status_code == 404
