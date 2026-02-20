# Synarch Engine Move-Forward Plan (Codex)

**Author:** Codex (Principal Engineer planning mode)  
**Date:** 2026-02-20  
**Scope:** Program-level execution plan from current PRD/ADR baseline to implementation-ready design package and build phases.

---

## 1) Executive Direction

You already have the right foundation:
- Product baseline: `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/prd-1.0-final.md`
- Core architecture baseline: `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/adr-005-modular-monolith-hexagonal-architecture.md`
- Reference adoption matrix and deep-dives are in place.

The main risk now is **execution diffusion**: too many artifacts without a strict dependency chain.

### Recommended execution model
Use one linear artifact ladder and do not skip gates:
1. `PRD/BRD` (what and why)
2. `ARD` (key architecture decisions per capability)
3. `HLD` (system blueprint across modules)
4. `LLD` (module-level contracts, APIs, flows)
5. `DB schema + migrations` (data contracts)
6. `UI/UX package` (`.pen`, flows, sequence, class/state diagrams)
7. `Implementation + tests`

If an upstream artifact changes, downstream artifacts must be version-bumped.

---

## 2) Proposed Artifact Structure (create this structure first)

```text
docs/
  00-program/
    roadmap-1.0.md
    release-plan-1.0.md
    risk-register-1.0.md
    traceability-matrix-1.0.md

  01-requirements/
    prd-1.0-final.md
    brd/
      brd-01-mission-lifecycle.md
      brd-02-orchestration-and-routing.md
      brd-03-agent-runtime.md
      brd-04-hitl-governance.md
      brd-05-event-nervous-system.md
      brd-06-persistence-and-recovery.md
      brd-07-mission-control-ui.md
      brd-08-security-and-audit.md

  02-architecture/
    adr-001-...md
    adr-005-...md
    ard/
      ard-006-mission-state-store.md
      ard-007-hitl-interrupt-contract.md
      ard-008-event-envelope-versioning.md
      ard-009-idempotency-and-outbox.md
      ard-010-sse-streaming-contract.md
      ard-011-model-routing-policy.md
    hld/
      hld-1.0-system-blueprint.md
    lld/
      lld-01-api-layer.md
      lld-02-orchestrator-graph.md
      lld-03-agent-runtime.md
      lld-04-event-bus.md
      lld-05-persistence.md
      lld-06-frontend-mission-control.md

  03-product/
    mission-control-ui-ux-and-functionality-strategy.md
    ui-spec/
      ui-spec-01-information-architecture.md
      ui-spec-02-component-spec.md
      ui-spec-03-interaction-and-hitl.md

  04-reference-deep-dives/
    ... (existing)

  05-data/
    db-schema-1.0.md
    data-dictionary-1.0.md
    retention-and-audit-policy-1.0.md

  06-diagrams/
    c4-context.mmd
    c4-container.mmd
    sequence-mission-happy-path.mmd
    sequence-hitl-approval.mmd
    state-mission-lifecycle.mmd
    class-domain-model.mmd

  07-validation/
    test-strategy-1.0.md
    nfr-validation-1.0.md

design/
  pen/
    mission-control/
      mission-control-v1.pen
      mission-control-mobile-v1.pen
      design-tokens-sync.md
```

---

## 3) Capability Breakdown (BRD and ARD units)

Define these as your canonical functional capabilities. Every capability gets one BRD and one ARD (minimum).

| Capability ID | Capability | BRD | ARD | HLD/LLD | DB impact | UI impact |
|---|---|---|---|---|---|---|
| CAP-01 | Mission lifecycle management | Required | Required | Required | Yes | Yes |
| CAP-02 | LangGraph orchestration and routing | Required | Required | Required | Indirect | Yes |
| CAP-03 | Agent runtime + litellm routing | Required | Required | Required | No | Yes |
| CAP-04 | HITL governance and approvals | Required | Required | Required | Yes | Yes |
| CAP-05 | NATS event nervous system | Required | Required | Required | Yes (outbox/audit) | Yes |
| CAP-06 | Durability and checkpoint recovery | Required | Required | Required | Yes | Moderate |
| CAP-07 | Mission Control cockpit UX | Required | Optional ADR | Required | No | Core |
| CAP-08 | Security, idempotency, auditability | Required | Required | Required | Yes | Moderate |

---

## 4) Document Standards (what each artifact must contain)

### 4.1 BRD standard (per capability)
Each BRD must include:
1. Problem statement and business value
2. Actors/personas and user journeys
3. Scope and non-scope
4. Functional requirements with IDs (`FR-*`) mapped to PRD
5. Non-functional requirements (`NFR-*`) with measurable thresholds
6. Acceptance criteria and demo scenarios
7. Dependencies on other capabilities
8. Risks and rollback expectations

### 4.2 ARD standard (per capability)
Each ARD must include:
1. Decision statement
2. Context and constraints
3. Options considered + trade-off table
4. Final decision and implications
5. Runtime boundaries (control/observation/persistence plane impact)
6. Failure modes and mitigations
7. Migration strategy and compatibility notes
8. Verification criteria

### 4.3 HLD standard
The HLD must include:
1. C4 context + container view
2. End-to-end data and control flow
3. Top-level service/module decomposition
4. Trust boundaries and external dependencies
5. Primary runtime and deployment topology
6. Interface catalog (API, events, storage)

### 4.4 LLD standard (per module)
Each LLD must include:
1. Module responsibilities and invariants
2. Public interfaces (input/output schemas)
3. Sequence diagrams for normal and failure paths
4. Error handling and retries/timeouts
5. Test design (unit/integration/e2e)
6. Observability points (logs/metrics/traces/events)

### 4.5 DB schema package standard
`db-schema-1.0.md` + migrations must include:
1. ER model
2. Table definitions and strict constraints
3. Index strategy and expected query patterns
4. Lifecycle data policy (retention, audit, archival)
5. Migration playbook: forward + rollback + compatibility window

### 4.6 UI/UX and `.pen` package standard
Each screen/package must include:
1. `.pen` source file + exported screenshots
2. User flow diagram and interaction states
3. State mapping to backend events and API calls
4. Desktop and mobile layout behavior
5. Design token usage (must match brand system)

---

## 5) Sequence of Work (Program Plan)

## Phase 0: Program Setup and Traceability (2 days)
**Goal:** Make artifact production deterministic before new design work.

Deliverables:
- `docs/00-program/traceability-matrix-1.0.md`
- `docs/00-program/roadmap-1.0.md`
- Directory scaffold in Section 2
- Naming/versioning convention (`v1.0`, `v1.1`, etc.)

Exit criteria:
- Every PRD FR maps to at least one capability (`CAP-*`)
- Every capability has an owner and target sprint

## Phase 1: BRD Pack (5-7 days)
**Goal:** Freeze functional scope by capability.

Deliverables:
- 8 BRDs (`brd-01` to `brd-08`)

Exit criteria:
- All BRDs contain acceptance criteria and NFR targets
- Open questions reduced to explicit decision backlog

## Phase 2: ARD Pack (4-6 days)
**Goal:** Close architecture decisions for each capability before detailed design.

Deliverables:
- 6 core ARDs (`ard-006` to `ard-011`) minimum

Exit criteria:
- No unresolved P0 architecture questions
- Each ARD has verification criteria and migration notes

## Phase 3: HLD + LLD Pack (7-10 days)
**Goal:** Make implementation unambiguous.

Deliverables:
- `hld-1.0-system-blueprint.md`
- 6 LLDs (API, graph, agents, event bus, persistence, frontend)
- Diagram pack under `docs/06-diagrams/`

Exit criteria:
- Every module interface typed and versioned
- Happy-path and failure-path sequence diagrams complete

## Phase 4: DB and Contract Freeze (3-4 days)
**Goal:** Lock data contracts and migrations before heavy implementation.

Deliverables:
- `docs/05-data/db-schema-1.0.md`
- `docs/05-data/data-dictionary-1.0.md`
- SQL migrations in `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/backend/adapters/postgres/migrations/`

Exit criteria:
- Migration applied successfully on clean DB
- Backward compatibility and rollback path documented

## Phase 5: UI/UX System Pack (.pen + flows) (5-8 days)
**Goal:** Finalize operational cockpit behavior before front-end build.

Deliverables:
- `.pen` files in `design/pen/mission-control/`
- `ui-spec-01/02/03`
- Flow, state, sequence, class diagrams aligned to UI states

Exit criteria:
- Every UI state maps to backend state/event contract
- HITL approval journey fully designed and validated

## Phase 6: Implementation Sprints (2-4 weeks)
**Goal:** Build to frozen design contracts.

Sprint structure:
1. Sprint A: Persistence + graph execution + recovery
2. Sprint B: Event bus + SSE + idempotency + outbox
3. Sprint C: Mission Control cockpit + HITL UX + token enforcement
4. Sprint D: Hardening (tests, NFR validation, runbooks)

Exit criteria:
- PRD FR-1..FR-44 all mapped to implemented tests or explicit deferments

---

## 6) Diagram Plan (must-have set)

Create these diagrams in `docs/06-diagrams/`:
1. `c4-context.mmd`
2. `c4-container.mmd`
3. `state-mission-lifecycle.mmd`
4. `sequence-mission-happy-path.mmd`
5. `sequence-hitl-approval.mmd`
6. `sequence-crash-recovery.mmd`
7. `class-domain-model.mmd`
8. `flow-ui-mission-control.mmd`

Minimum quality bar:
- Every diagram has title, date, and source refs to PRD/ARD/LLD IDs.
- If behavior changes, diagram update is mandatory in same PR.

---

## 7) Governance and Review Cadence

## Weekly cadence
1. Monday: artifact planning + dependency review
2. Midweek: architecture/contract review
3. Friday: gate review + risk register update

## Gate model
1. `G1 Requirements Freeze` -> BRDs approved
2. `G2 Architecture Freeze` -> ARDs approved
3. `G3 Design Freeze` -> HLD/LLD + diagrams approved
4. `G4 Data Freeze` -> schema + migration plan approved
5. `G5 Build Freeze` -> implementation starts only after G1-G4

No implementation of CAP-x before its BRD+ARD exist and are approved.

---

## 8) Definition of Done for Artifacts

An artifact is complete only if:
1. It has version, owner, status, and date.
2. It links upstream and downstream dependencies.
3. It includes explicit acceptance criteria.
4. It includes risks and unresolved items.
5. It is referenced from `traceability-matrix-1.0.md`.
6. It has at least one review sign-off note.

---

## 9) Immediate Next 10 Actions (starting now)

1. Create `docs/00-program/traceability-matrix-1.0.md` seeded from FR-1..FR-44.
2. Create BRD skeleton files for `CAP-01` to `CAP-08`.
3. Draft `brd-01-mission-lifecycle.md` first (highest coupling capability).
4. Draft `ard-006-mission-state-store.md` and `ard-007-hitl-interrupt-contract.md`.
5. Draft `hld-1.0-system-blueprint.md` with C4 context/container.
6. Create `docs/05-data/db-schema-1.0.md` from current PRD schema sections.
7. Create initial `docs/06-diagrams/state-mission-lifecycle.mmd`.
8. Create initial `docs/06-diagrams/sequence-hitl-approval.mmd`.
9. Set up `design/pen/mission-control/` and define screen inventory.
10. Update memory-bank to reference this plan as active execution baseline.

---

## 10) Risk Controls (Principal Engineer view)

Top execution risks and controls:
1. **Spec drift** between PRD and implementation.
Control: traceability matrix + PR checklist requiring FR and CAP references.
2. **Architecture bypass** (coding before ARD/LLD).
Control: gate policy G1-G5 enforced in review.
3. **UI/backend contract mismatch**.
Control: UI spec must bind each component state to event/API schemas.
4. **Data model churn late in build**.
Control: DB freeze gate before Sprint B.
5. **Over-documentation without shipping**.
Control: timebox each artifact phase and move to implementation after G4.

---

## 11) Recommended Ownership Model (for 1 human + AI team)

- **God (PraxLannister):** final approver for BRD/ARD gates
- **Codex:** HLD/LLD/schema/diagram drafting, implementation scaffolds
- **Claude/Cline (optional):** alternative proposals, red-team review on ARD/LLD

Decision rule:
- One owner per artifact, one approver, one review window. No multi-owner ambiguity.

---

## 12) Bottom Line

Do not jump straight to coding across all areas.

First produce a **bounded design package** in this order:
`BRD pack -> ARD pack -> HLD/LLD pack -> DB freeze -> UI .pen + diagrams -> implementation sprints`.

This plan turns your current high-context docs into a controlled build program that can scale without chaos.
