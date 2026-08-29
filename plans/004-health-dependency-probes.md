# Plan 004: Implement real health dependency probes

> **Executor instructions**: Follow this plan step by step. Run every verification command and confirm the expected result before moving to the next step.

## Status

- **Priority**: P2
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: dx
- **Planned at**: commit `8bb4058`, 2026-08-29

## Why this matters

`GET /api/v1/health` always returns `dependencies.*.status: "pending"` even when Postgres, Redis, and NATS are running. Mission Control and ops tooling cannot distinguish healthy from degraded deployments.

## Current state

```python
# backend/api/routes/health.py
"dependencies": {
    "postgresql": {"status": "pending"},
    "nats": {"status": "pending"},
    ...
}
```

Container holds live adapter instances (`app.state.container`) initialized in `main.py` lifespan.

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Health | `curl -fsS http://localhost:8000/api/v1/health \| jq .dependencies.postgresql.status` | `"ok"` or `"degraded"` when DB up |
| Tests | `python -m pytest -q tests/ -k health` | new tests pass |

## In scope

- `backend/api/routes/health.py`
- `backend/api/dependencies.py` — inject container if needed
- `backend/tests/unit/test_health.py` (new)

## Out of scope

- Kubernetes liveness/readiness split
- Qdrant/Ollama deep health (ping only if adapter exists)

## Steps

1. Add optional `Request` dependency to access `app.state.container`.
2. Probe Postgres with `SELECT 1` via existing pool/repository (2s timeout).
3. Probe Redis with `PING` via container redis client.
4. Probe NATS: if event_bus connected, status `ok`; else `degraded` (not fatal — graceful degradation per AGENTS.md).
5. Return `status: degraded` at top level if any critical dependency (postgres, redis) fails.
6. Unit test with mocked container returning success/failure.

## Done criteria

- [ ] Health JSON shows `ok`/`error` per dependency when services running
- [ ] Top-level `status` reflects critical failures
- [ ] Tests cover at least postgres ok and postgres fail paths
- [ ] Full pytest suite passes

## STOP conditions

- Health check adds >500ms latency in local dev — add caching or async gather with timeout.
