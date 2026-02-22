# Synarch Engine Implementation Master Plan (v2.2)

**Document Control:**
- **Status:** Canonical Execution Baseline
- **Version:** 2.2
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

| Slice | Issue | Description | Status | Dependencies |
|---|---|---|---|---|
| **S01** | #2 | Durable mission bootstrap + persisted state API | **DONE** | - |
| **S02** | #3 | LangGraph core routing + prompt/model baseline | **DONE** | S01 |
| **S03** | #4 | Typed event contract + NATS publication | **OPEN** | S02 |
| **S04** | #5 | Reconnect-safe NATS->SSE + live mission inspect UI | **OPEN** | S03 |
| **S05** | #6 | Checkpoint persistence + crash recovery | **BUILD COMPLETE** | S01 |
| **S06** | #7 | HITL interrupt/resume + approval persistence | **OPEN** | S01, S05 |
| **S07** | #8 | Approval inbox + deliberation timeline + mode visibility | **OPEN** | S06 |
| **S08** | #9 | Tasks/blockers/deliverables board projection | **OPEN** | S04 |
| **S09** | #10 | Idempotency middleware + retry metadata | **OPEN** | S01 |
| **S10** | #11 | Auth modes + attribution + secrets discipline | **OPEN** | S01 |
| **S11** | #12 | Least privilege + guardrails + injection defense | **OPEN** | S10 |
| **S12** | #13 | Mission Control design-system + brand compliance | **OPEN** | - |
| **S13** | #14 | Build/lint/type + critical path CI gates | **OPEN** | - |
| **S14** | #15 | Eval baseline + cost telemetry + reference adoption | **OPEN** | S02 |
| **S15** | #16 | LLM-as-judge + regression suite + quality dashboards | **OPEN** | S14 |
| **S16** | #17 | Context assembly + token budgets + memory write patterns | **OPEN** | S14 |
| **S17** | #18 | Memory lifecycle + compaction/anti-context-rot | **OPEN** | S16 |
| **S18** | #19 | AgentTool composition + dynamic tool selection | **OPEN** | S02 |
| **S19** | #20 | Dynamic model routing + budget degradation strategy | **OPEN** | S14 |
| **S20** | #21 | Confidence scoring + progressive trust + graceful handoff | **OPEN** | S06 |
| **S21** | #22 | Config-driven agents + schema validation + hot reload | **OPEN** | S02 |
| **S22** | #23 | MCP server/client + inspect loop + tooling | **OPEN** | S18 |
| **S23** | #24 | A2A readiness + discovery cards | **OPEN** | S22 |
| **S24** | #25 | Scoped integrations + external trigger routing | **OPEN** | S22 |
| **S25** | #26 | Integration supply-chain security checks | **OPEN** | S24 |
| **S26** | #27 | Sandboxed execution for untrusted code | **OPEN** | S11 |
| **S27** | #28 | Replay/time-travel debugging + SLO instrumentation | **OPEN** | S05, S03 |

---

## 3. Immediate Execution Plan

### Step 1: Event Nervous System (S03 - Issue #4)
*   **Context:** `NATSEventBus` exists but needs hardening. `EventEnvelope` needs validation against `umbrella-event-catalog.md`.
*   **Invariant:** "Event writes follow transactional outbox + mission-sequence allocator."
*   **Task:**
    1.  Implement `PostgresEventRepository` using DB sequence function.
    2.  Harden `EventEnvelope` with schema versioning.
    3.  Implement "Dual Write" logic (DB first, then NATS) or Outbox logic in the EventBus adapter.
*   **DoD:** Integration test where event is persisted to DB with correct sequence AND published to NATS mock.

### Step 2: Mission Control Streaming (S04 - Issue #5)
*   **Task:** Implement `SSEBridge` in `adapters/nats/sse_bridge.py`.
*   **DoD:** Frontend receives live updates via `/api/missions/{id}/stream`.

### Step 3: Verify Persistence (S05 - Issue #6)
*   **Status:** Build Complete (PR #45). Pending verification on live env.
*   **Task:** Verify integration with live PostgreSQL.

---

## 4. Documentation Strategy

For each slice, produce/update:
1.  **Mini-Spec:** Issue description (GitHub).
2.  **Contracts:** `docs/02-architecture/api-contract.md`, `umbrella-event-catalog.md`.
3.  **ADR:** Only if a major decision is made (e.g., Auth provider).
4.  **Verification:** PR description with logs/screenshots.
