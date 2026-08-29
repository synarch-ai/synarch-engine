# Plan 001: Refresh memory-bank progress tracker from codebase truth

> **Executor instructions**: Follow this plan step by step. Run every verification command and confirm the expected result before moving to the next step. If anything in the "STOP conditions" section occurs, stop and report — do not improvise.

## Status

- **Priority**: P1
- **Effort**: S
- **Risk**: LOW
- **Depends on**: none
- **Category**: docs
- **Planned at**: commit `8bb4058`, 2026-08-29

## Why this matters

`memory-bank/progress.md` still shows M0.5 as in progress with unchecked items that are already implemented (Postgres persistence, LangGraph runtime, litellm, Mission Control dashboard). Agents and humans reading this file get a false picture of project state and may duplicate work or skip real gaps.

## Current state

- `memory-bank/progress.md` — milestone tracker; lines 18–31 show unchecked M0.5 items.
- `docs/plans/2026-03-06-principal-engineer-audit-report.md` — authoritative audit showing persistence, runtime, and UI are shipped.
- `backend/domain/orchestrator/runtime.py` — LangGraph mission execution exists.
- `apps/web/` — Next.js Mission Control exists.
- `backend/adapters/postgres/` — durable persistence exists.

Excerpt from stale tracker:

```markdown
### 🔲 M0.5: Gap Closure Program (2026-02-19) — IN PROGRESS
- [ ] Replace in-memory mission state with durable persistence
- [ ] Introduce non-linear graph routing + HITL approval path
```

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Tests | `cd backend && source .venv/bin/activate && python -m pytest -q` | 18 passed |
| Health | `curl -fsS http://localhost:8000/api/v1/health` | `"status":"ok"` |

## In scope

- `memory-bank/progress.md`

## Out of scope

- Rewriting `docs/plans/*` audit reports
- Changing milestone numbering in PRDs
- Any source code under `backend/` or `apps/web/`

## Steps

1. Read `docs/plans/2026-03-06-principal-engineer-audit-report.md` and `AGENTS.md` for current capabilities.
2. Mark M0.5 complete with checkboxes reflecting shipped work (persistence, LangGraph, litellm, Mission Control skeleton).
3. Add a short "Current focus" section naming real open gaps: Hermes tools, credential plane, health probes, NATS worker decoupling (from audit).
4. Update M1–M6 sections to reflect what is done vs. remaining — do not delete history; strike through or annotate superseded PoC roadmap items.
5. Verify markdown renders sensibly (no broken headings).

## Done criteria

- [ ] M0.5 marked complete with accurate checkboxes
- [ ] At least one "known open gap" listed with file references
- [ ] `git diff memory-bank/progress.md` shows only documentation changes
- [ ] Backend tests still pass (command above)

## STOP conditions

- Principal audit contradicts your reading of shipped features — stop and report which file is authoritative.
- You find yourself editing files outside `memory-bank/progress.md`.

## Maintenance note

Re-run `/improve` quarterly or after major milestone PRs merge; link new `plans/README.md` from progress.md "References" if helpful.
