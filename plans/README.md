# Synarch Engine — Improve Audit Index

**Audit level:** `quick` (read-only recon + hotspot review)  
**Date:** 2026-08-29  
**Auditor:** Cloud Agent using [shadcn/improve](https://github.com/shadcn/improve) methodology  
**Scope:** Repo root, `backend/`, `apps/web/`, `docs/`, `scripts/cloud-agent/`. Not audited: full `vendor/`, every reference deep-dive, production infra.

## Verification commands (for plan executors)

```bash
# Backend
cd backend && source .venv/bin/activate
TEST_DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch \
DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch \
python -m pytest -q

# Services (after install + start)
curl -fsS http://localhost:8000/api/v1/health
curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/dashboard
```

**Current baseline:** 18 tests passed; health `ok`; dashboard HTTP 200.

## Findings (top 6 by leverage)

| # | Finding | Category | Impact | Effort | Risk | Evidence |
|---|---------|----------|--------|--------|------|----------|
| 1 | **Stale progress tracker** — `memory-bank/progress.md` shows M0.5 in progress with unchecked items already implemented (Postgres persistence, LangGraph, litellm, Mission Control). Misleads agents and humans. | Docs / DX | High | S | Low | `memory-bank/progress.md` vs `docs/plans/2026-03-06-principal-engineer-audit-report.md` |
| 2 | **Hermes is LLM-only** — no real research tools (web, NotebookLM, MCP). Research deliverables are hallucination-prone. | Correctness | High | M | Med | `backend/domain/agents/hermes.py` — `invoke_llm` only |
| 3 | **Credential plane gap** — only Bedrock + Ollama env vars in settings; no vault, multi-provider routing UI, or subscription/ACP bridge. | Security / Architecture | High | L | Med | `backend/config.py` lines 22–25, 36–42 |
| 4 | **Default DB port mismatch** — `Settings.database_url` defaults to `5433` but cloud-agent uses native Postgres on `5432`. Fresh env without `.env.local` can fail silently or connect wrong. | Correctness | Med | S | Low | `backend/config.py:11` vs `scripts/cloud-agent/install.sh` |
| 5 | **Health endpoint reports dependencies `pending`** even when Postgres/Redis/NATS are running — observability gap for Mission Control and ops. | DX / Observability | Med | S | Low | `curl localhost:8000/api/v1/health` during smoke test |
| 6 | **`datetime.utcnow()` deprecation** — 75 pytest warnings; will break on future Python. | Tech debt | Low | S | Low | `backend/tests/unit/test_s02_runtime.py` |

## Considered and rejected

- **"No Docker Compose in daily dev"** — by design; `scripts/cloud-agent/` is the canonical path per `AGENTS.md`.
- **"Monorepo missing /frontend"** — `apps/web/` is the frontend; progress.md naming is stale, not a structural bug.

## Direction (product, not defects)

1. **Credential Plane + AgentTool registry** — unify API keys, litellm profiles, and optional ACP/Goose providers behind one port (aligns with competitor research on Buzz/Goose).
2. **Hermes tool wiring** — NotebookLM adapter, Exa/Context MCP, or `parallel-deep-research` as pluggable tools behind `ports/`.
3. **Operational Mission Control** — approval queue, live NATS thought stream, credential status panel (per UI strategy doc).

## Plans to generate (default top 3–5)

Select findings to turn into executor-ready plans:

- [ ] Plan 01: Refresh `memory-bank/progress.md` from principal audit + codebase truth
- [ ] Plan 02: Hermes AgentTool port + first research adapter
- [ ] Plan 03: Align `database_url` default with cloud-agent Postgres port
- [ ] Plan 04: Health check — probe Postgres, Redis, NATS, Qdrant, Ollama with real status
- [ ] Plan 05: Replace `datetime.utcnow()` with timezone-aware UTC in tests/runtime

Run `/improve` (standard or deep) to expand any finding into a full implementation plan under `plans/`.
