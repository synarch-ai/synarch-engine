# Synarch Engine Implementation Master Plan (v2.0)

**Document Control:**
- **Status:** Canonical Execution Baseline
- **Version:** 2.0 (Supersedes v1.0)
- **Date:** 2026-02-21
- **Source of Truth:**
    - **PRD v1.2** (`docs/01-requirements/PRD-final.MD`)
    - **HLD v2.0** (`docs/02-architecture/hld/synarch-hld.md`)
    - **LLD v2.0** (`docs/02-architecture/lld/synarch-lld.md`)
    - **DB Schema v2.0** (`docs/05-data/master-db-schema.md`)

---

## 1. Executive Direction

This plan executes the **"Runtime Closure (Phase 0-1)"** roadmap defined in PRD v1.2. The immediate goal is to establish **mission durability** (no in-memory state) and **checkpoint recovery** (FR-75..79).

We follow the **"Guided Vertical Slices"** strategy:
1.  **Define Contracts:** ARD/LLD/Schema (Minimal required docs first).
2.  **Implement Slice:** Code aligned to contracts.
3.  **Verify:** Integration tests and gate checks.

---

## 2. Phase 1: Persistence & Runtime Closure (Immediate Focus)

**Goal:** Ensure missions survive process restarts and state is persisted to PostgreSQL.

**Scope (FR Mapping):**
- **FR-75:** End-to-end durable runtime wiring (no in-memory mission SOT).
- **FR-2:** Durable mission record with unique thread context.
- **FR-5:** Resume from persisted state after restart.
- **FR-10:** Graph checkpoints persisted to PostgreSQL.
- **FR-77:** Approval persistence (pre-requisite for HITL).

**Deliverables:**

### 2.1 Documentation (Design Contracts)
- [ ] **ARD-006:** Mission State Store Strategy (Create/Update `docs/02-architecture/ard/ard-006-mission-state-store.md`).
- [ ] **LLD-05:** Persistence Layer Contract (Create/Update `docs/02-architecture/lld/lld-05-persistence.md`).
- [ ] **DB Schema:** Verify `docs/05-data/master-db-schema.md` (v2.0) is the single source of truth for DDL.

### 2.2 Implementation (Persistence Layer)
- [ ] **PostgreSQL Repositories:** Implement concrete repositories in `backend/adapters/postgres/repositories.py` for:
    - `MissionRepository`
    - `TaskRepository`
    - `ApprovalRepository`
    - `EventRepository`
- [ ] **LangGraph Checkpointer:** Implement `AsyncPostgresSaver` adapter in `backend/adapters/langgraph/checkpointer.py`.
- [ ] **Dependency Injection:** Wire repositories and checkpointer in `backend/container.py`.
- [ ] **Domain Models:** Ensure `backend/domain/` Pydantic models align 1:1 with DB schema v2.0.

### 2.3 Verification
- [ ] **DB Migrations:** Apply `backend/adapters/postgres/migrations/001_initial.sql`.
- [ ] **Integration Test:**
    1.  Create a mission via API.
    2.  Wait for initial state persistence.
    3.  Restart backend process.
    4.  Verify mission state is retrievable and matches pre-restart state.
    5.  Verify graph thread checkpoint exists.

---

## 3. Future Phases (Roadmap v1.2)

### Phase 2: Runtime Governance (Week 2)
- **Goal:** HITL Approvals, Event Streaming, Idempotency.
- **FRs:** FR-76, FR-78, FR-79, FR-21..25.
- **Key Docs:** `ard-007-hitl-interrupt-contract.md`, `lld-02-orchestrator-graph.md`.

### Phase 3: Mission Control UI (Week 3)
- **Goal:** Operational Cockpit, SSE Integration.
- **FRs:** FR-26..36.
- **Key Docs:** `ui-spec-01..03`, `lld-06-frontend-mission-control.md`.

---

## 4. Immediate Next Steps

1.  **Create Phase 1 Docs:** Draft `ard-006` and `lld-05` aligned with HLD v2.0.
2.  **Implement Repositories:** Code the PostgreSQL adapters.
3.  **Wire & Verify:** Connect to LangGraph and run integration test.
