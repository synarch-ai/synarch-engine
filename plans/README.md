# Synarch Engine — Improve Audit Index

**Audit level:** `standard` (hotspot-weighted, all nine categories)  
**Date:** 2026-08-29  
**Planned at:** commit `8bb4058`  
**Auditor:** Cloud Agent using shadcn/improve methodology  
**Scope:** `backend/`, `apps/web/`, `docs/`, `scripts/cloud-agent/`. Not audited: full `vendor/` tree, production infra, every UI route.

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

**Baseline (2026-08-29):** 18 tests passed; health `ok`; dashboard HTTP 200.

## Findings (vetted, ordered by leverage)

| # | Finding | Category | Impact | Effort | Risk | Confidence | Plan |
|---|---------|----------|--------|--------|------|------------|------|
| 1 | Stale `memory-bank/progress.md` — M0.5 unchecked items already shipped (Postgres, LangGraph, litellm, Mission Control) | Docs / DX | High | S | Low | HIGH | [001](001-refresh-progress-tracker.md) |
| 2 | Hermes is LLM-only — no research tools behind a port; deliverables are hallucination-prone | Correctness | High | M | Med | HIGH | [002](002-hermes-research-tool-port.md) |
| 3 | `database_url` defaults to port `5433` while cloud-agent uses native Postgres on `5432` | Correctness | Med | S | Low | HIGH | [003](003-align-database-port-default.md) |
| 4 | Health endpoint hardcodes `dependencies.*.status: pending` — no real probes | DX / Observability | Med | S | Low | HIGH | [004](004-health-dependency-probes.md) |
| 5 | `datetime.utcnow()` in models/tests — 75 deprecation warnings | Tech debt | Low | S | Low | HIGH | [005](005-timezone-aware-datetimes.md) |
| 6 | Credential plane limited to Bedrock/Ollama env vars — no vault or multi-provider routing | Security / Architecture | High | L | Med | MED | — |
| 7 | Mission runtime uses in-process `asyncio.Task` — HTTP workers coupled to orchestration | Architecture | Med | L | Med | HIGH | — |

## Considered and rejected

- **"No Docker Compose in daily dev"** — by design; `scripts/cloud-agent/` is canonical per `AGENTS.md`.
- **"Monorepo missing /frontend"** — `apps/web/` is the frontend; progress.md naming is stale.
- **"Vendored skills deleted from git"** — intentional; `install-pro-skills.sh` restores symlinks idempotently (PR #64/#65).

## Direction (product options)

1. **Credential Plane + AgentTool registry** — unify API keys, litellm profiles, optional ACP/Goose behind one port (aligns with competitor research).
2. **Hermes tool wiring** — NotebookLM, Exa/Context MCP, or parallel-deep-research as pluggable adapters behind `ports/`.
3. **Operational Mission Control** — approval queue, live NATS thought stream, credential status panel.

## Execution order

| Plan | Title | Priority | Depends on | Status |
|------|-------|----------|------------|--------|
| 001 | Refresh progress tracker | P1 | none | TODO |
| 003 | Align database port default | P1 | none | TODO |
| 004 | Health dependency probes | P2 | none | TODO |
| 005 | Timezone-aware datetimes | P2 | none | TODO |
| 002 | Hermes research tool port | P1 | none | TODO |

Plans 001 and 003 are safe quick wins. Plan 002 is highest product leverage but larger scope.
