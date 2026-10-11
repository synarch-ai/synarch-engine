# synarch-engine - Mac setup (verified 2026-10-05)

Repo: (GitHub synarch-ai/synarch-engine, HEAD d12286c). Python FastAPI backend (`backend/`) + Next.js 14 "Mission Control" (`apps/web/`). Submodules under `references/` are NOT needed for build/test (left uninitialised, all show `-`).

## Requirements
- Python 3.12+ (tested 3.13.16 via uv), uv, Node 24 / npm 12, Docker (colima running).
- Env vars (backend, read from `backend/.env.local` or `.env`, or the shell): DATABASE_URL, NATS_URL, REDIS_URL (not in .env.example, default redis://localhost:6379/0), QDRANT_URL, OLLAMA_API_BASE, AWS_REGION_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN (real LLM missions need Bedrock creds; or override MODEL_* to ollama/...). None are needed for tests or the smoke below.
- Web: apps/web/.env.local with NEXT_PUBLIC_API_BASE_URL / NEXT_PUBLIC_SSE_BASE_URL (dashboard actually hardcodes http://localhost:8000, see finding).

## Backend install + tests
```bash
cd backend
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -r requirements.txt
```
Tests: 16 pass without infra; 2 postgres integration tests need a Postgres with role `synarch`. Port 5433 on this Mac is already taken by a different host Postgres (no `synarch` role), so run the repo's DB on another port, bound to loopback:
```bash
# from the repo root
docker run -d --name synarch-audit-pg -p 127.0.0.1:55433:5432 \
  -e POSTGRES_USER=synarch -e POSTGRES_PASSWORD=synarch_local -e POSTGRES_DB=synarch \
  -v $PWD/backend/adapters/postgres/migrations/001_initial.sql:/docker-entrypoint-initdb.d/001_initial.sql:ro \
  pgvector/pgvector:pg16
cd backend
TEST_DATABASE_URL=postgresql://synarch:synarch_local@127.0.0.1:55433/synarch .venv/bin/python -m pytest -q -p no:cacheprovider tests
```
Result: **18 passed, 0 failed** with the DB (without it: 16 passed, 2 failed with `role "synarch" does not exist`; environment, not code).

## Run backend (full smoke, all on 127.0.0.1)
```bash
docker run -d --name synarch-audit-nats  -p 127.0.0.1:54222:4222 nats:2.10 -js
docker run -d --name synarch-audit-redis -p 127.0.0.1:56379:6379 redis:7.2-alpine
# apply the metrics migration (compose only mounts 001, see finding)
docker exec -i synarch-audit-pg psql -U synarch -d synarch < backend/adapters/postgres/migrations/002_metrics_views.sql
cd backend
export DATABASE_URL=postgresql://synarch:synarch_local@127.0.0.1:55433/synarch \
       NATS_URL=nats://127.0.0.1:54222 REDIS_URL=redis://127.0.0.1:56379/0
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```
Do not use `python main.py`: it binds 0.0.0.0 with reload. (On base d12286c only. On branch fix/audit-2026-10, `python main.py` binds 127.0.0.1 without reload; without `API_KEY` the API serves loopback clients only, and `uvicorn main:app --host 0.0.0.0` refuses to start. Never use `--host 0.0.0.0` without `API_KEY`.) Routes are under `/api/v1` (README does not say so).
Verified: GET /api/v1/health 200, /agents 200, /missions 200, /metrics/daily 200 (after 002), POST /api/v1/mission/start 201 (then mission goes `failed`: "Unable to locate credentials" for Bedrock, expected without AWS creds).

Repo's own flow (`docker compose -f infra/docker-compose.yml up -d`) was not used: it publishes ports on 0.0.0.0 and 5433 clashes with the host Postgres. It also pulls ollama and qdrant.

## Web
```bash
cd apps/web
npm ci
node_modules/.bin/tsc --noEmit        # passes
NEXT_TELEMETRY_DISABLED=1 node_modules/.bin/next build   # passes; routes /, /dashboard (static), 404
NEXT_TELEMETRY_DISABLED=1 node_modules/.bin/next start -H 127.0.0.1 -p 3000
```
Verified: / 200, /dashboard 200 (contain "Mission Control"), /nope 404. `npm run lint` does NOT work non-interactively (no ESLint config; `next lint` prompts). `npm ls` prints `next@ invalid` under npm 12 although 14.1.0 is installed (cosmetic). `tsc` leaves untracked `apps/web/tsconfig.tsbuildinfo` (added to .git/info/exclude).

## Known issues / workarounds
1. `GET /api/v1/metrics/daily` returns 500 on a fresh compose DB: 002_metrics_views.sql is not mounted by infra/docker-compose.yml. Apply it manually (above).
2. `GET /api/v1/agents/{name}/soul` returns "Soul file not found" when started from `backend/` because the path is the cwd-relative `docs/agents` (api/routes/agents.py:27); souls live in ../docs/agents. Workaround: symlink or run with cwd at repo root with PYTHONPATH=backend.
3. /health reports every dependency as "pending" (hardcoded, api/routes/health.py).
4. Missions need Bedrock creds (or MODEL_* overrides to Ollama).

## Cleanup done
Containers synarch-audit-pg/nats/redis removed, uvicorn and next stopped, no listeners left. Repo working tree clean (ignored: backend/.venv, apps/web/node_modules, .next).
