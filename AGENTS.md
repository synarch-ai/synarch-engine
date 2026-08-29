# AGENTS.md

Operating guidance for AI agents working in the Synarch Engine repository.
See `README.md` for product context and architecture.

## Layout

- `backend/` — FastAPI + LangGraph orchestration engine (Python 3.12). Hexagonal
  layout: `api/` (routes, middleware, schemas), `domain/` (agents, orchestrator,
  models, events), `adapters/` (postgres, nats, litellm, langgraph, qdrant),
  `ports/` (interfaces), `tests/`.
- `apps/web/` — Next.js 14 Mission Control dashboard (App Router, Tailwind).
- `infra/docker-compose.yml` — canonical service topology (Postgres+pgvector,
  Redis, NATS, Qdrant, Ollama).
- `scripts/cloud-agent/` — idempotent environment provisioning (see below).

## Local development

The fastest path is the Cloud Agent provisioning scripts, which work on any
Ubuntu host with `sudo`:

```bash
bash scripts/cloud-agent/install.sh   # deps, venv, web deps, DB + migrations (idempotent)
bash scripts/cloud-agent/start.sh     # start Postgres/Redis/NATS + backend:8000 + web:3000
```

Services and ports: PostgreSQL `5432` (native; note `infra/docker-compose.yml`
maps it to `5433`), Redis `6379`, NATS `4222` (+ `8222` monitoring), backend
`8000`, web `3000`.

Local env overrides live in `backend/.env.local` and `apps/web/.env.local`
(gitignored). The backend reads `.env.local` then `.env`.

### Backend

```bash
cd backend && source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000   # or: python main.py (adds --reload)
```

Boot requires PostgreSQL, Redis, and (gracefully degrading) NATS. Side-effecting
API endpoints require an `Idempotency-Key` header.

### Web

```bash
cd apps/web && npm run dev
```

## Testing

```bash
cd backend && source .venv/bin/activate
TEST_DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch \
DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch \
python -m pytest -q
```

Integration tests require a running PostgreSQL with the migrations applied
(`scripts/cloud-agent/db-bootstrap.sh` handles role/db/migrations idempotently).

## Cursor Cloud specific instructions

- The environment is provisioned by `scripts/cloud-agent/install.sh` (install
  phase) and `scripts/cloud-agent/start.sh` (start phase). `start.sh` self-heals
  dependencies (`backend/.venv`, `apps/web/node_modules`, `.env.local` files) if
  a fresh checkout removed them, then launches all services and both dev servers.
- To verify a change end-to-end after `start.sh`:
  - `curl -fsS http://localhost:8000/api/v1/health` (expect `status: ok`)
  - `curl -fsS http://localhost:8000/api/v1/metrics/daily` (JSON `metrics` array)
  - Create a mission (exercises DB + event sourcing):
    `curl -fsS -X POST http://localhost:8000/api/v1/mission/start -H 'Content-Type: application/json' -H "Idempotency-Key: $(python3 -c 'import uuid;print(uuid.uuid4())')" -d '{"goal":"smoke test","authority_mode":"supervised"}'`
  - Web: `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/dashboard` (expect `200`).
- For UI changes to `apps/web`, do manual GUI testing of the affected page and
  capture a screenshot/recording.
- Live autonomous mission execution calls AWS Bedrock via litellm. Without
  `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (or a local Ollama model), a
  mission transitions to `failed` with a structured `error_context` — expected,
  not an environment defect. Persistence, API, and UI paths do not need
  credentials.

## Pro developer skills

Installed idempotently by `scripts/cloud-agent/install-pro-skills.sh` (also runs
at the end of `install.sh` unless `INSTALL_PRO_SKILLS=0`). Skills symlink into
`.agents/skills/` from pinned upstream repos under `vendor/skills-sources/`
(gitignored except `manifest.json`).

| Skill / command | When to use |
|-----------------|-------------|
| `/improve` | Read-only codebase audit → prioritized plans in `plans/` |
| `/pstack-poteto-mode` | Rigorous engineering playbooks (bug fix, perf, ship, etc.) |
| `/mp-triage`, `/mp-implement`, `/mp-tdd` | Matt Pocock engineering workflows |
| `/gstack-review`, `/gstack-qa`, `/gstack-investigate` | Garry Tan gstack review + browser QA |
| `brainstorming`, `test-driven-development`, `writing-plans` | Obra superpowers methodology |

**One-time setup per repo:** run `/pstack-setup-pstack` and
`/mp-setup-matt-pocock-skills` after install.

**Optional Cursor marketplace plugins** (hooks + auto-invocation):
`/add-plugin pstack`, `/add-plugin superpowers`.

See `docs/04-reference-deep-dives/agent-skills-ecosystem.md` for the full
ecosystem map and additional credible sources.
