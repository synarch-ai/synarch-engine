# synarch-engine: Understanding (comprehension lead, 2026-10-05)

GitHub: synarch-ai/synarch-engine (PUBLIC)  |  HEAD d12286c (main)
Activity: 123 commits (89 Prax Lannister, 22 google-labs-jules[bot], 9 Cursor Agent, 3 cursor[bot]); 83 in 2026-02, 23 in 2026-03, 17 in 2026-08; nothing since 2026-08-29.

## 1. What it is
"Synarch Engine": a hierarchical multi-agent orchestration engine. Human ("God") -> Synarch (CEO) -> Zeus (CTO) / Thoth (CRO) -> Hephaestus (engineer) / Hermes (researcher) -> Janus (QA gate). FastAPI + LangGraph backend, Postgres persistence, NATS event bus, litellm model routing (Bedrock/Ollama), Next.js "Mission Control" dashboard. Most of the 1302 tracked files are NOT product code: 1017 are `.agents/skills/**` (119 vendored skill dirs), plus ~150 research/design docs (docs/, techDocsCline/, techDocsCodex/, notebook-lm-research/, moveforward_*.md). Product code is ~4.8k lines Python (backend) + ~450 lines TSX (apps/web).

## 2. Document authority
Authoritative (current-ish): AGENTS.md (dev/test/cloud-agent instructions; matches scripts/cloud-agent), docs/01-requirements/PRD-final.MD (FR-1..FR-44 and later FR-48/49), docs/00-program/traceability-matrix-1.0.md (FR -> file targets, many targets never built), ADR-005 (hexagonal modular monolith), plans/README.md (2026-08-29 /improve audit, 5 TODO plans).
Stale/historical: README.md roadmap (all of M1-M6 unchecked, says "early development"), memory-bank/* (progress.md says M1 not started; activeContext says "ready to start"; both say repo is "private"), moveforward_Cline/Codex/final.md (planning journals; final has 1074 lines), techDocsCline/*, notebook-lm-research/*, docs/04-reference-deep-dives (study notes for 12 reference submodules).
No LICENSE file although README badge claims MIT and package.json says MIT.

## 3. Module map
| Path | Role |
|---|---|
| backend/main.py | uvicorn entry; lifespan builds DI container; `host=0.0.0.0, reload=True` in `__main__` |
| backend/config.py | pydantic-settings; reads .env.local then .env; DB default port 5433 (AGENTS.md says native 5432) |
| backend/container.py | wires NATS, litellm, LangGraph PG checkpointer, Redis (required: `ping()` has no try/except), asyncpg pool, MissionOrchestratorRuntime; ONLY mission_repo is wired (task/approval/deliverable repos are None) |
| backend/api/ | app factory, routes (missions, agents, health, metrics), middleware (request_id, idempotency, cors, errors), schemas |
| backend/domain/orchestrator/ | runtime.py (asyncio-task mission runner + Redis budget guard), graph.py (StateGraph), routing.py (keyword routing), state.py |
| backend/domain/agents/ | AgentNode base (soul.md load, litellm call, event emit) + synarch/zeus/thoth/hermes/hephaestus/janus; tools/memory_tool.py (unwired) |
| backend/domain/evals/judge.py | LLM-as-judge EvalRunner (used only by tests) |
| backend/domain/models, events | pydantic models; EventEnvelope + event types |
| backend/ports/ | ABCs: persistence (Mission/Task/Deliverable/Approval/Memory repos), event_bus, model_provider, checkpointer, vector_store |
| backend/adapters/ | postgres (repositories.py 506 LOC = only PostgresMissionRepository; memory_repo.py; migrations 001, 002), nats (client, sse_bridge), litellm, langgraph (checkpointer), qdrant (empty package) |
| backend/src/ | LEGACY PoC (in-memory MISSIONS dict, old graph); imported by nothing; dead code |
| backend/scripts/ | metrics_worker.py (refreshes daily_mission_metrics every 5 min; not started by start.sh), run_live_evals.py (stub: loads dataset and logs only) |
| backend/tests/ | 18 tests: unit (graph merge, routing, runtime, memory tool), integration (missions API w/ fakes, PG repo, S15 metrics, S15 "regression") |
| apps/web | Next.js 14.1 App Router: `/` static stub ("Mission Log" with hardcoded lines), `/dashboard` (Recharts metrics, fetches hardcoded http://localhost:8000), components/ui/{GlassCard,NeonBadge} |
| infra/docker-compose.yml | nats, pgvector/pg16 (host 5433), redis, qdrant:latest, ollama:latest; no backend/web services |
| scripts/cloud-agent/ | Ubuntu-only provisioning (sudo, pg_lsclusters): install.sh, start.sh, db-bootstrap.sh, install-pro-skills.sh (clones many upstream skill repos) |
| scripts/*.ts, scripts/ralph/ | NotebookLM downloaders (notebooklm-kit via root package.json); "ralph" issue-loop scripts |
| vendor/skills-sources/manifest.json | pinned skill sources; .agents/skills committed copies |
| references/ | 12 git submodules (autogen, crewAI, langgraph, letta, ...), uninitialised here and not needed for build/test |

## 4. Main flow (as implemented)
1. `POST /api/v1/mission/start` (needs `Idempotency-Key`, stored in `idempotency_records`) -> creates Mission row (+ payload, events, outbox row) -> `MissionOrchestratorRuntime.launch_mission` spawns an in-process `asyncio.Task`.
2. run_mission: CREATED->PLANNING->EXECUTING, `graph.ainvoke` (checkpointed to Postgres thread_id=mission id). Graph: synarch -> (zeus|thoth by keyword match on plan text, default zeus) -> hephaestus|hermes -> janus -> {synthesize | revise->zeus | fail}.
3. Each agent loads docs/agents/<name>/soul.md as system prompt, calls litellm (Redis INCR budget cap 24 calls/mission), emits NATS event (dropped with a warning if NATS is down).
4. Final: COMPLETED or FAILED with error_context; budget exceeded -> PAUSED_AWAITING_RESOURCES. Startup `resume_inflight_missions` relaunches created/planning/executing missions.
5. Read APIs: GET state (tasks and deliverables always `[]`), list (cursor=offset), SSE stream (placeholder: one state event then sleep 30s), metrics/daily (reads materialized view).
6. Pause/resume/cancel endpoints only flip DB status; they do not signal the running task.

## 5. Data and state
Postgres schema (migrations/001_initial.sql, 354 lines): missions, mission_payloads, tasks, task_payloads, deliverables, approvals, mission_events (+ per-mission sequence counters), mission_event_outbox, idempotency_records, cost_logs, agent_configs, memories (pgvector 1536 + hnsw), replay_metadata; 002 adds materialized view daily_mission_metrics. Optimistic locking via `missions.version`; transition table in repositories.update_status. Redis: budget counters. NATS JetStream: subjects synarch.*.<mission>.*. Checkpoints: langgraph-checkpoint-postgres. Written by code today: missions, payloads, events, outbox, idempotency. Never written: tasks, deliverables, approvals, cost_logs, memories, agent_configs, replay_metadata. Outbox is written but nothing publishes/drains it.

## 6. External services / env
Postgres 16 + pgvector, Redis (hard requirement), NATS (soft), Qdrant (config only), Ollama (Hermes default model), AWS Bedrock (needs AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_REGION_NAME; .env.example also lists AWS_SESSION_TOKEN, which Settings does not declare). Without creds a mission ends `failed` (documented as expected). NotebookLM scripts need cookies (playwright profile).

## 7. Build / run / test (verified this run)
- Backend: `cd backend && python -m venv .venv && pip install -r requirements.txt` (unpinned `>=`). Python 3.13.15 works. Tests: with a Postgres at TEST_DATABASE_URL: **18 passed** (private temp PG18 on 127.0.0.1:55432, migration 001 applied with the pgvector lines stripped because pgvector is only installed for PG17 here; `memories` embedding path therefore untested). Without DB: 16 passed, 2 PG-repo tests fail with `role "synarch" does not exist` (default test URL points at localhost:5433, which on this laptop is an unrelated Postgres).
- Web: `npm ci` ok; `npx tsc --noEmit` ok; `npm run build` ok (/dashboard 196 kB first load). `npm run lint` does NOT lint: no ESLint config is committed, so `next lint` opens an interactive "How would you like to configure ESLint?" prompt (exit 0 under CI=1 here but nothing is checked).
- Not run: full stack (needs Redis + NATS + Postgres w/ pgvector; redis-server/nats-server not installed; docker/colima not started on purpose). Submodules: not initialised, not needed.

## 8. CI / GitHub
- `.github/workflows/` does not exist at HEAD. Only pull_request_template.md. The only workflow ("Synarch CI": poetry + ruff + mypy + pytest + eslint/tsc/build) was deleted by bot commit 26e6664 (2026-03-06) together with backend/pyproject.toml and poetry.lock. Last 3 recorded runs (2026-03-03) all FAILED (logs expired, HTTP 410). Likely cause: `poetry install` needed pyproject (present then) but `.eslintrc` / ruff configs absent; unknowable without logs. Net: zero CI today, no ruff/mypy config at all.
- PRs: 25 merged shown (#45-#69), 0 open. Open issues: 42 (S14-S43 spec slices; #15-#28 labelled `ralph-blocked`, #29-#44 unlabelled). Issue #15 "S14 Eval baseline" is still open even though PR #56 "implement S14" merged.
- Remote branches: bolt/usememo-metrics..., palette/add-loading-skeletons..., phase-1-persistence-implementation... all have 0 commits ahead of origin/main (stale, merged).
- Dependencies: backend/requirements.txt is unpinned; apps/web uses next 14.1.0. Dependency and secret-scan results are kept privately by the owner.

## 9. Roadmap vs reality (spot checks, 14 claims)
| Claim | Source | Reality |
|---|---|---|
| M1/M2/M3/M4/M5 "not started" | README.md:~190, memory-bank/progress.md | Docker compose, FastAPI, LangGraph graph, 6 agents, NATS client, dashboard all exist. Docs stale (plan 001 TODO). |
| "Real-time dashboard with agent topology" | README | /dashboard shows daily metrics charts only; `/` is static fake log. No topology, no SSE client. |
| FR-18 SSE streams events | traceability matrix | missions.py `stream_mission_events` is a placeholder; sse_bridge.py never imported. |
| FR-8/21-23/43 HITL interrupt/approval | matrix; PRs #50 (S07) | No approvals route, no ApprovalRepository impl, `should_request_approval` unused, graph has no interrupt. approvals.py/ApprovalInbox deleted by 26e6664. |
| FR-30 tasks/deliverables board (PR #51 S08) | matrix | state endpoint returns `tasks=[]`, `deliverables=[]`; no Task/Deliverable repo impl; TaskBoard.tsx deleted by 26e6664. |
| FR-41/42 (S10), FR-44 (S11) | matrix, PR | Code deleted by 26e6664. PR #70 adds API-key auth; the rest is an owner decision (details kept privately). |
| FR-36 CI gates (S13) | matrix, commit ed63064 | workflow, pyproject, poetry.lock deleted. |
| FR-14 idempotency | matrix | Implemented (middleware + table), tests deleted; check-then-insert race, no lock. |
| FR-5 resume after restart | matrix | `resume_inflight_missions` relaunches from scratch with initial_state; whether LangGraph resumes from checkpoint depends on re-invoking with initial_state (it re-feeds input, not `None`), so likely restarts from the entry node. Untested. |
| FR-12 soul.md loading | matrix | Works only when cwd lets `docs/agents` resolve (see GRAPH/findings). |
| FR-48 regression evals (S15) | PR | test mocks the judge to return the expected score then asserts >= expected: tautology. run_live_evals.py is a stub. |
| FR-49 dashboard cost/token metrics | PR | view reads cost_logs, which nothing writes -> cost/tokens always 0. |
| Health endpoint probes (FR/PRD) | health.py | hardcoded "pending" (plan 004). |
| Repo is private | memory-bank, AGENTS | gh reports PUBLIC. |

## 10. Risk areas (where bugs likely live)
1. domain/orchestrator/runtime.py: cancel/pause don't stop work; terminal-state overwrite attempts; relaunch on restart; unbounded in-process tasks; shared compiled graph.
2. adapters/postgres/repositories.py: transition table, optimistic locking, `list` input validation (unvalidated status/limit -> 500), outbox drain missing.
3. api/middleware/idempotency.py: race, caches 5xx, buffers whole body/response (breaks SSE if ever POST), body read in BaseHTTPMiddleware.
4. SSE/NATS path: dropped events, unwired bridge.
5. Agents: keyword routing on plan text, revise loop only to zeus, REVISE after 3 rounds silently synthesizes.
6. Security: see PR #70 for the API-key and loopback-bind changes; other security notes are kept privately by the owner.
7. Frontend: hardcoded API URL, no error/loading states beyond dashboard, no lint.
8. Process: no CI, no pins, huge committed vendored skills.

## 11. Cleanup performed by this run
Created backend/.venv and apps/web/node_modules (ignored). Added `apps/web/tsconfig.tsbuildinfo` to .git/info/exclude. Temp Postgres in audit dir (pgdata/) on 127.0.0.1:55432, stopped at the end. No tracked file modified.
