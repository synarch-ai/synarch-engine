# Plan 003: Align database_url default port with cloud-agent Postgres

> **Executor instructions**: Follow this plan step by step. Run every verification command and confirm the expected result before moving to the next step.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: bug
- **Planned at**: commit `8bb4058`, 2026-08-29

## Why this matters

`Settings.database_url` defaults to port `5433` (`backend/config.py:11`) while `scripts/cloud-agent/install.sh` provisions native Postgres on `5432`. Fresh environments without `backend/.env.local` may fail to connect or connect to the wrong instance.

## Current state

```python
# backend/config.py:11
database_url: str = "postgresql://synarch:synarch_local@localhost:5433/synarch"
```

`scripts/cloud-agent/db-bootstrap.sh` and `AGENTS.md` document port `5432`.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Tests | `cd backend && source .venv/bin/activate && TEST_DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch python -m pytest -q` | all pass |

## In scope

- `backend/config.py` — change default port to `5432`
- `backend/.env.example` if it exists — align port
- Any test fixtures hardcoding `5433` — search and update

## Out of scope

- Changing `infra/docker-compose.yml` port mapping (5433 is intentional for Docker-only path)
- Migrating production deployments

## Steps

1. `rg '5433' backend/` — list all references.
2. Change default `database_url` to port `5432`.
3. Add comment in `config.py`: Docker Compose maps host 5433 → use `.env.local` override for docker-only dev.
4. Update any unit tests that assert the old default string.
5. Run pytest.

## Done criteria

- [ ] Default `database_url` uses port `5432`
- [ ] Comment documents Docker override path
- [ ] `python -m pytest -q` passes
- [ ] `curl -fsS http://localhost:8000/api/v1/health` still works when services running

## STOP conditions

- More than 5 files need changing for unrelated reasons — stop and report scope creep.
