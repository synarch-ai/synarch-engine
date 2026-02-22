# Synarch Engine Implementation Master Plan (v2.1)

**Document Control:**
- **Status:** Canonical Execution Baseline
- **Version:** 2.1
- **Date:** 2026-02-22
- **Source of Truth:**
    - **PRD v1.2** (`docs/01-requirements/PRD-final.MD`)
    - **HLD v2.0** (`docs/02-architecture/hld/synarch-hld.md`)
    - **DB Schema v2.0** (`docs/05-data/master-db-schema.md`)
    - **GitHub Issues:** S01..S43

---

## 1. Execution Strategy: Guided Vertical Slices (S-Slices)

This plan executes the roadmap through independently verifiable slices (S01-S43).
Each slice executes the "Ralph Loop":
1.  **Contract:** Define ARD/LLD/Schema.
2.  **Code:** Implement backend/frontend/infra.
3.  **Verify:** Run tests and validation checks.

---

## 2. Slice Status Tracker

| Slice | Description | FR Mapping | Status | Dependencies |
|---|---|---|---|---|
| **S01** | Durable mission bootstrap + persisted state API | FR-1, FR-2, FR-75 | **DONE** | - |
| **S02** | LangGraph core routing + prompt/model baseline | FR-6, FR-7, FR-11 | **DONE** | S01 |
| **S03** | Typed event contract + NATS publication | FR-13, FR-16..20 | **OPEN** | S02 |
| **S04** | Reconnect-safe NATS->SSE + live mission inspect UI | FR-18, FR-26, FR-76 | **OPEN** | S03 |
| **S05** | Checkpoint persistence + crash recovery | FR-5, FR-10 | **OPEN** | S01 |
| **S06** | HITL interrupt/resume + approval persistence | FR-8, FR-21..25, FR-77 | **OPEN** | S01, S05 |
| **S07** | Approval inbox + deliberation timeline + mode visibility | FR-28, FR-29, FR-32 | **OPEN** | S06 |
| **S08** | Tasks/blockers/deliverables board projection | FR-30 | **OPEN** | S04 |
| **S09** | Idempotency middleware + retry metadata | FR-14, FR-15, FR-78 | **OPEN** | S01 |
| **S10** | Auth modes + attribution + secrets discipline | FR-41, FR-42, FR-79 | **OPEN** | S01 |
| **S11** | Least privilege + guardrails + injection defense | FR-43, FR-51..55 | **OPEN** | S10 |
| **S12** | Mission Control design-system + brand compliance | FR-33..36 | **OPEN** | - |
| **S13** | Build/lint/type + critical path CI gates | FR-81, FR-82 | **OPEN** | - |
| **S14** | Eval baseline + cost telemetry + reference adoption | FR-45, FR-47, FR-83 | **OPEN** | S02 |
| **S15** | LLM-as-judge + regression suite + quality dashboards | FR-46, FR-48..50 | **OPEN** | S14 |
| **S16** | Context assembly + token budgets + memory write patterns | FR-57..59 | **OPEN** | S14 |
| **S17** | Memory lifecycle + compaction/anti-context-rot | FR-60, FR-84 | **OPEN** | S16 |
| **S18** | AgentTool composition + dynamic tool selection | FR-68, FR-73 | **OPEN** | S02 |
| **S19** | Dynamic model routing + budget degradation strategy | FR-72, FR-74 | **OPEN** | S14 |
| **S20** | Confidence scoring + progressive trust + graceful handoff | FR-69..71 | **OPEN** | S06 |
| **S21** | Config-driven agents + schema validation + hot reload | FR-65..67 | **OPEN** | S02 |
| **S22** | MCP server/client + inspect loop + tooling | FR-37, FR-40, FR-61/62 | **OPEN** | S18 |
| **S23** | A2A readiness + discovery cards | FR-63, FR-64 | **OPEN** | S22 |
| **S24** | Scoped integrations + external trigger routing | FR-38, FR-39 | **OPEN** | S22 |
| **S25** | Integration supply-chain security checks | FR-56 | **OPEN** | S24 |
| **S26** | Sandboxed execution for untrusted code | FR-80 | **OPEN** | S11 |
| **S27** | Replay/time-travel debugging + SLO instrumentation | FR-85, FR-86 | **OPEN** | S05, S03 |
| ... | S28-S43 (Advanced/Enterprise) | - | **PENDING** | - |

---

## 3. Immediate Execution Plan

### Step 1: Verify & Finalize Persistence (S05)
*   **Context:** `PostgresMissionRepository` and `LangGraphCheckpointer` are implemented (Phase 1 PR).
*   **Task:** Verify integration with live PostgreSQL (via `scripts/migrate.py` and integration tests). Ensure `missions.thread_id` and checkpoints are 1:1.
*   **DoD:** Mission resumes from DB checkpoint after process restart.

### Step 2: Event Nervous System (S03)
*   **Task:** Implement `NATSEventBus` with Typed Event Contracts (CloudEvents envelope).
*   **Docs:** Update `umbrella-event-catalog.md`.
*   **DoD:** Runtime events published to NATS subjects `synarch.mission.{id}.{type}`.

### Step 3: Mission Control Streaming (S04)
*   **Task:** Implement `SSEBridge` in `adapters/nats/sse_bridge.py`.
*   **DoD:** Frontend receives live updates via `/api/missions/{id}/stream`.

### Step 4: Governance & HITL (S06)
*   **Task:** Implement `ApprovalRepository`, `interrupt` logic in graph, and Decision API.
*   **DoD:** Mission pauses on `awaiting_approval`, resumes after API decision.

---

## 4. Documentation Strategy

For each slice, produce/update:
1.  **Mini-Spec:** Issue description (GitHub).
2.  **Contracts:** `docs/02-architecture/api-contract.md`, `umbrella-event-catalog.md`.
3.  **ADR:** Only if a major decision is made (e.g., Auth provider).
4.  **Verification:** PR description with logs/screenshots.
