# Synarch Engine Implementation Master Plan

## Document Control
- Document: `moveforward_final.md`
- Version: `1.0`
- Status: `Proposed for approval`
- Date: `2026-02-20`
- Owner: `PraxLannister (God)`
- Technical author: `Codex`
- Audience: product owner, architecture reviewers, implementation contributors

## Purpose
This document is the execution source of truth for moving Synarch Engine from current skeleton state to production grade PoC implementation.

It merges:
- Execution speed discipline: deliver running vertical slices from Week 1.
- Architecture discipline: no uncontrolled coding without explicit contracts and verification gates.

This plan defines, phase by phase:
- Why the phase exists.
- Which documents are required.
- Which code must be implemented.
- Which tests must pass.
- Which exit criteria must be true.

---

## 1) Source of Truth Hierarchy
When documents disagree, follow this precedence order:

1. `docs/01-requirements/prd-1.0-final.md`
2. `docs/02-architecture/adr-005-modular-monolith-hexagonal-architecture.md`
3. `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md`
4. `docs/02-architecture/reference-adoption-matrix.md`
5. `moveforward_final.md` (this execution plan)
6. Phase specific HLD/LLD/ARD docs produced under this plan

Reason:
- Prevents local optimization and plan drift.
- Keeps implementation anchored to approved requirements and architecture decisions.

---

## 2) Current Baseline
From current repository state:
- PRD exists and covers `FR-1` through `FR-44`.
- ADR set exists through `ADR-005`.
- Hexagonal folder structure exists under `backend/`.
- Core runtime behavior is still incomplete for mission critical flows.
- UI is not yet at operational Mission Control level.
- Dedicated BRD/ARD/HLD/LLD/Data/Diagram folders are not yet scaffolded.

Implication:
- We should not spend multiple weeks in pure documentation.
- We should also not start implementation without minimal design contract pack.
- We execute in short phases with mandatory documentation at the beginning of each phase.

---

## 3) Delivery Strategy

## 3.1 Strategy Name
Guided Vertical Slices with Contract Gates.

## 3.2 Operating Rule
For each phase:
1. Produce minimal required design docs first.
2. Build the scoped code slice.
3. Run mandatory tests.
4. Pass gate and update memory-bank.
5. Move to next phase.

Reason:
- Produces visible progress quickly.
- Limits rework by freezing only the contracts needed for that slice.

## 3.3 Phase Cadence
- Week 1: Infrastructure + persistence + checkpoint recovery foundation.
- Week 2: Runtime graph + HITL + core eventing.
- Week 3: SSE + Mission Control functional UI + tokenized styling.
- Week 4: Hardening, security, quality gates, DoD validation.
- Week 5 (optional stretch): P2 reference adoption items `FR-37..FR-40`.

---

## 4) System Design Principles (Mandatory)

1. Control plane is LangGraph state.
Reason: deterministic orchestration and checkpoint resume.

2. Observation plane is NATS events.
Reason: decoupled telemetry and UI feed without driving core decisions.

3. Persistence plane is PostgreSQL.
Reason: mission durability, audit history, approval traceability.

4. Hexagonal boundaries are strict.
Reason: domain remains testable and infrastructure swappable.

5. Contract first APIs and events.
Reason: frontend and backend can evolve with explicit version compatibility.

6. Idempotency for side effects.
Reason: retries and duplicate requests must not create duplicate writes/actions.

7. Fail safe governance.
Reason: unsafe operations require explicit approval and timeout behavior.

8. Recovery by design.
Reason: crash and restart are expected operational realities.

9. Observability is mandatory, not optional.
Reason: debugging multi-agent behavior without traceability is not viable.

10. Security by default.
Reason: event streams and logs must never expose secrets.

---

## 5) UI/UX Design Principles (Mandatory)

1. Mission Control is an operational cockpit, not a marketing dashboard.
Reason: primary user task is control and supervision.

2. Event first UI updates.
Reason: state should reflect real execution timeline and prevent stale polling behavior.

3. Explainable progression.
Reason: user must always understand current phase, branch, pending approvals, and blockers.

4. Action safety clarity.
Reason: approval prompts must include risk context and decision consequence.

5. Brand token enforcement.
Reason: V3 design identity must be consistently expressed, not partially applied.

6. Responsive operations.
Reason: essential mission control actions must remain usable on mobile layout.

7. Minimal ambiguity in interactions.
Reason: command input, approval controls, and stream filters must be deterministic.

---

## 6) Design Patterns to Follow

## 6.1 Backend Patterns
- State machine orchestration pattern (LangGraph).
- Repository pattern for persistence ports.
- Outbox pattern for reliable event publication semantics.
- Idempotency key pattern for side-effecting API endpoints.
- Retry with exponential backoff and jitter for external model/tool calls.
- Structured event envelope with `schema_version`.
- Dependency injection composition root in `container.py`.
- Compensating action policy for partial failures.

## 6.2 Frontend Patterns
- Event driven store updates from SSE.
- Render by typed event categories and mission state.
- Feature level components with strict prop contracts.
- Token based styling through CSS variables.
- Explicit loading/error/empty states for each panel.

## 6.3 Documentation Patterns
- One artifact, one owner, one status.
- Every artifact references upstream IDs (`FR`, `CAP`, `ARD`, `LLD`).
- Every phase has DoR (Definition of Ready) and DoD (Definition of Done).

---

## 7) Anti Patterns to Reject

1. Direct adapter imports in domain layer.
2. UI logic dependent on untyped arbitrary payloads.
3. In-memory mission state as source of truth.
4. Fire and forget side effects without idempotency.
5. Secret values in logs, SSE payloads, or event metadata.
6. Large coding phases without phase scoped design contract.
7. Untracked reference adoption without implementation evidence.

---

## 8) Capability Map and FR Coverage

| CAP | Capability | Primary FR | Phase |
|---|---|---|---|
| CAP-01 | Mission lifecycle and durability | FR-1,2,3,4,5,10 | Phase 1 |
| CAP-02 | Graph routing and governance | FR-6,7,8,9,21,22,23,24,25,43 | Phase 2 |
| CAP-03 | Agent runtime and model routing | FR-11,12,13,15 | Phase 2 |
| CAP-04 | Event nervous system | FR-16,17,18,19,20 | Phase 2 and 3 |
| CAP-05 | Mission Control core UX | FR-26,27,28,29,30,31,32 | Phase 3 |
| CAP-06 | Brand system implementation | FR-33,34,35,36 | Phase 3 and 4 |
| CAP-07 | Security and audit posture | FR-41,42,44 | Phase 4 |
| CAP-08 | Reference driven extensions | FR-37,38,39,40 | Phase 5 optional |

Reason:
- This table is the planning bridge between PRD requirements and implementation sprints.

---

## 9) Required Documentation Set by Phase

This is the minimum required set. Do not exceed unless a risk demands it.

## Phase 0 docs
- `docs/00-program/traceability-matrix-1.0.md`

## Phase 1 docs
- `docs/02-architecture/ard/ard-006-mission-state-store.md`
- `docs/02-architecture/lld/lld-05-persistence.md`
- `docs/05-data/db-schema-1.0.md`
- `docs/06-diagrams/sequence-crash-recovery.mmd`

## Phase 2 docs
- `docs/02-architecture/ard/ard-007-hitl-interrupt-contract.md`
- `docs/02-architecture/ard/ard-008-event-envelope-versioning.md`
- `docs/02-architecture/ard/ard-009-idempotency-and-outbox.md`
- `docs/02-architecture/lld/lld-02-orchestrator-graph.md`
- `docs/02-architecture/lld/lld-03-agent-runtime.md`
- `docs/06-diagrams/sequence-hitl-approval.mmd`
- `docs/06-diagrams/state-mission-lifecycle.mmd`

## Phase 3 docs
- `docs/02-architecture/hld/hld-1.0-system-blueprint.md`
- `docs/02-architecture/lld/lld-01-api-layer.md`
- `docs/02-architecture/lld/lld-04-event-bus.md`
- `docs/02-architecture/lld/lld-06-frontend-mission-control.md`
- `docs/03-product/ui-spec/ui-spec-01-information-architecture.md`
- `docs/03-product/ui-spec/ui-spec-02-component-spec.md`
- `docs/03-product/ui-spec/ui-spec-03-interaction-and-hitl.md`
- `docs/06-diagrams/flow-ui-mission-control.mmd`
- `design/pen/mission-control/mission-control-v1.pen`
- `design/pen/mission-control/mission-control-mobile-v1.pen`

## Phase 4 docs
- `docs/05-data/data-dictionary-1.0.md`
- `docs/05-data/retention-and-audit-policy-1.0.md`
- `docs/07-validation/test-strategy-1.0.md`
- `docs/07-validation/nfr-validation-1.0.md`
- `docs/03-product/brand-compliance-checklist.md`
- `docs/06-diagrams/c4-context.mmd`
- `docs/06-diagrams/c4-container.mmd`

## Phase 5 docs (optional extension)
- `docs/02-architecture/ard/ard-010-sse-streaming-contract.md`
- `docs/02-architecture/ard/ard-011-model-routing-policy.md`
- `docs/02-architecture/ard/ard-012-reference-adoption-p2.md`

---

## 10) Directory Scaffold to Create First

Create once at start:

```text
docs/00-program/
docs/01-requirements/brd/
docs/02-architecture/ard/
docs/02-architecture/hld/
docs/02-architecture/lld/
docs/03-product/ui-spec/
docs/05-data/
docs/06-diagrams/
docs/07-validation/
design/pen/mission-control/
```

Reason:
- Stable document placement avoids path churn and broken references.

---

## 11) Phase by Phase Execution Plan

## Phase 0: Program Bootstrap and Environment Proof (Day 1 to Day 2)

### Why this phase exists
Without environment proof and requirement traceability, implementation starts blind and rework probability increases.

### Definition of Ready
- Current `main` is clean and pull complete.
- Local `.env` values available for model providers and infrastructure.

### Documents required
1. `traceability-matrix-1.0.md`
- Why: maps `FR-1..FR-44` to `CAP`, phase, and test IDs.

### Code and setup required
1. Create `.env` from `.env.example` with real credentials.
- Why: all services need configured environment to start.
2. Bring up infra services via Docker Compose.
- Why: validates runtime dependency availability.
3. Pull Ollama model: `docker exec ollama ollama pull llama3.1:8b`
- Why: Hermes agent needs local LLM available.
4. Install backend and frontend dependencies.
- Why: baseline reproducibility for all subsequent phases.
5. Verify health endpoints and service connectivity.
- Why: prevents late debugging from simple misconfiguration.
6. Add startup check for required env vars.
- Why: fail fast on invalid setup.

### Bedrock fallback note
If AWS Bedrock credentials are unavailable during Phase 0-1 testing, ALL agents can temporarily use `ollama/llama3.1:8b` via litellm config override. This allows full graph testing without cloud API costs. Switch to Bedrock models once credentials are confirmed.

### Tests required
1. Infrastructure smoke script:
- PostgreSQL reachable.
- NATS reachable.
- Qdrant reachable.
- Ollama reachable.
2. Backend starts and `/health` reports dependency status.
3. Frontend starts and can reach backend base URL.

### Exit criteria
- All infra services healthy.
- Backend and frontend startup reproducible from clean shell.
- Traceability matrix created with complete FR coverage.

### Deliverables
- Document scaffold exists.
- Phase 0 evidence recorded in `memory-bank/progress.md`.

---

## Phase 1: Durable Mission State and Recovery Foundation (Week 1)

### Why this phase exists
Durability is the highest value risk reducer. Without persisted mission state, all orchestration and UI value is fragile.

### Definition of Ready
- Phase 0 passed.
- DB schema migration file validated syntactically.

### Documents required
1. `ard-006-mission-state-store.md`
- Why: locks mission persistence strategy and failure behavior.
2. `lld-05-persistence.md`
- Why: defines repository contracts and transaction boundaries.
3. `db-schema-1.0.md`
- Why: explicit dictionary beyond raw SQL for developers and reviewers.
4. `sequence-crash-recovery.mmd`
- Why: clarifies resume semantics and expected event/state transitions.

### Code required
Backend:
1. Implement concrete PostgreSQL repositories for mission, task, deliverable, approval.
2. Replace in-memory mission map usage in routes.
3. Wire repository instances through DI container.
4. Wire LangGraph checkpointer to PostgreSQL saver.
5. Persist mission lifecycle transitions.
6. Ensure mission retrieval endpoint serves persisted canonical state.

Infra:
1. Apply initial migration on clean database.
2. Add migration runbook command.

### Tests required
Unit:
1. Repository CRUD behaviors with fixtures.
2. Domain to persistence mapping tests.

Integration:
1. Create mission and query mission state.
2. Update state across multiple lifecycle transitions.
3. Crash restart resume test with checkpoint continuity.

Regression:
1. Existing API contract still valid for mission start and query.

### Exit criteria
- Mission survives backend restart.
- Checkpoint resume demonstrated in integration test.
- No in-memory mission store remains as source of truth.

---

## Phase 2: Graph Runtime, HITL Governance, and Event Contract (Week 2)

### Why this phase exists
Phase 2 turns scaffolding into actual orchestration behavior and enforces governance and observability contracts early.

### Definition of Ready
- Phase 1 exit criteria passed.
- Persistence and recovery behavior stable.

### Documents required
1. `ard-007-hitl-interrupt-contract.md`
- Why: deterministic interrupt and resume behavior.
2. `ard-008-event-envelope-versioning.md`
- Why: event schema stability for backend and UI.
3. `ard-009-idempotency-and-outbox.md`
- Why: reconcile delivery semantics and retries safely.
4. `lld-02-orchestrator-graph.md`
- Why: route logic and validation nodes specification.
5. `lld-03-agent-runtime.md`
- Why: agent invocation, retries, and lifecycle events.
6. `state-mission-lifecycle.mmd`
- Why: lifecycle transitions used by runtime and UI.
7. `sequence-hitl-approval.mmd`
- Why: approval request, pause, decision, resume flow.

### Code required
Backend runtime:
1. Implement graph conditional routing functions.
2. Add policy/validation nodes and revise loop limits.
3. Integrate LangGraph `interrupt()` for approval points.
4. Persist approval requests and decisions.
5. Implement approval decision endpoint.
6. Add approval timeout behavior with deterministic fallback.

Agent runtime:
1. Load `soul.md` prompts for each agent.
2. Invoke models through `litellm` provider abstraction only.
3. Emit structured lifecycle events for start, progress, result, error.
4. Record retry metadata.

Eventing:
1. Define canonical event envelope model with `schema_version`.
2. Publish mission, agent, task, deliverable, approval events to NATS subjects.
3. Implement outbox relay semantics or explicit publish reliability strategy.

Idempotency:
1. Add idempotency middleware for side effect endpoints.
2. Persist idempotency key and response replay metadata.

### Tests required
Unit:
1. Routing decision tests across input plan variants.
2. Event envelope schema validation tests.
3. Idempotency middleware decision path tests.

Integration:
1. Full mission execution with routing and validation nodes.
2. HITL pause resume flow with approval decision API.
3. Approval timeout fallback behavior.
4. Duplicate request with same idempotency key returns safe replay.

Contract:
1. Event payload schema contract snapshots.
2. API response contract snapshots for mission and approval endpoints.

### Exit criteria
- Mission executes through real graph branches.
- HITL pause and resume works deterministically.
- Event stream published for all critical domains.
- Side effect dedupe is verified.

---

## Phase 3: Mission Control Functional Cockpit and Tokenized UI (Week 3)

### Why this phase exists
Without operational UI, governance and observability are inaccessible to the user.

### Definition of Ready
- Phase 2 runtime and event contracts stable.
- Event schemas version locked for UI consumption.

### Documents required
1. `hld-1.0-system-blueprint.md`
- Why: end to end backend to frontend integration topology.
2. `lld-01-api-layer.md`
- Why: endpoint behaviors and error envelopes used by UI.
3. `lld-04-event-bus.md`
- Why: SSE bridge and event fanout behavior.
4. `lld-06-frontend-mission-control.md`
- Why: component boundaries, state model, data flow.
5. `ui-spec-01-information-architecture.md`
- Why: panel model and operator workflows.
6. `ui-spec-02-component-spec.md`
- Why: reusable components and states.
7. `ui-spec-03-interaction-and-hitl.md`
- Why: approval and command interactions.
8. `flow-ui-mission-control.mmd`
- Why: operator interaction flow and branching.
9. `.pen` mocks for desktop and mobile.
- Why: implementation alignment and visual signoff.

### Code required
Backend:
1. SSE endpoint with reconnect and heartbeat behavior.
2. Stream filtering by mission and event category.
3. Error envelope consistency across API routes.

Frontend:
1. Mission start command panel.
2. Live thought/event stream panel with typed categories and filters.
3. Agent topology panel with active/idle/waiting states.
4. Task and deliverable panel with phase aware rendering.
5. Approval queue and decision controls.
6. Mission status and branch indicator.
7. Execution mode indicator.
8. V3 token based styling and typography integration.

Design system implementation:
1. CSS custom property tokens as source of truth.
2. Core primitives for void, plate, border, amber states.
3. Sharp radius and border first rule enforcement.

### Tests required
Unit:
1. Component rendering for loading/error/empty/data states.
2. Hook tests for SSE connection lifecycle and reconnection.

Integration:
1. Start mission from UI and observe live stream updates.
2. Complete approval flow from UI.
3. Deliverable rendering against typed event payloads.

E2E:
1. Happy path mission from command input to completion.
2. Mission with approval pause and resume.

### Exit criteria
- User can fully operate mission lifecycle from browser.
- UI reflects backend event/state accurately in near real time.
- V3 core token rules applied consistently.

---

## Phase 4: Security, Compliance, and Reliability Hardening (Week 4)

### Why this phase exists
Feature completeness without hardening produces unreliable demos and security regressions.

### Definition of Ready
- Phase 3 exit criteria passed.
- Core mission loop stable.

### Documents required
1. `data-dictionary-1.0.md`
- Why: clear field level semantics for audit, analytics, and debugging.
2. `retention-and-audit-policy-1.0.md`
- Why: data lifecycle and compliance behavior.
3. `test-strategy-1.0.md`
- Why: final quality bars and test ownership.
4. `nfr-validation-1.0.md`
- Why: measurable non functional quality validation.
5. `brand-compliance-checklist.md`
- Why: enforce brand consistency gate.
6. `c4-context.mmd` and `c4-container.mmd`
- Why: final architecture communication and operation runbook support.

### Code required
Security:
1. Secret redaction in logs and event payloads.
2. Approval and control plane actor attribution metadata.
3. Auth mode configuration hardening per ADR direction.

Reliability:
1. Timeout policies for external providers.
2. Retry policies with capped attempts and jitter.
3. Circuit break style safety around unstable dependencies.
4. Backpressure handling for stream bursts.

Quality:
1. Standardized structured logging fields.
2. Metrics hooks for mission latency, approval delay, error rates.

UI hardening:
1. Brand compliance fixes and polish.
2. Accessibility and keyboard workflow pass.

### Tests required
Security tests:
1. Secrets not present in stream payloads or logs.
2. Unauthorized or invalid approval actions rejected.

Reliability tests:
1. Provider failure retry and fallback behavior.
2. Stream stability under burst event load.
3. Recovery test repeated with random interruption points.

E2E acceptance set:
1. Happy path.
2. HITL pause/resume.
3. Cancellation.
4. Crash recovery.
5. Idempotent duplicate request behavior.

### Exit criteria
- PRD DoD criteria satisfied.
- Security and NFR validation reports pass.
- Demo ready with predictable behavior.

---

## Phase 5: Reference Adoption Extensions (Optional Week 5)

### Why this phase exists
This phase addresses lower priority but strategically important FRs derived from reference adoption strategy.

### Definition of Ready
- Phase 4 passed.
- PoC core declared stable.

### Documents required
1. `ard-012-reference-adoption-p2.md`
- Why: explicit decision boundaries for P2 capabilities.
2. Update `reference-adoption-matrix.md` with implemented evidence.

### Code required
1. Deterministic browser specialist tooling pattern alignment (`FR-37`).
2. Actor or org scoped integration context (`FR-38`).
3. Trigger routing into workflows (`FR-39`).
4. MCP inspect debug loop tooling support (`FR-40`).

### Tests required
1. Contract tests for scoped integration context.
2. Trigger driven mission path tests.
3. Tooling debug workflow tests.

### Exit criteria
- Optional P2 FRs implemented or explicitly deferred with rationale.

---

## 12) Detailed Test Strategy by Layer

## Unit Tests
- Domain models and invariants.
- Routing functions.
- Envelope builders and validation.
- Idempotency middleware.
- UI components and hooks.

Why:
- Fast feedback for logic correctness.

## Integration Tests
- API to repository to database.
- Graph to checkpointer to database.
- Runtime to event bus publication.
- SSE stream to event relay.

Why:
- Validates behavior at subsystem boundaries where most regressions occur.

## Contract Tests
- API request and response schema snapshots.
- Event schema and subject taxonomy snapshots.

Why:
- Prevents silent breaking changes between backend and frontend.

## E2E Tests
- Full mission flow scenarios with real dependencies in controlled environment.

Why:
- Confirms user visible outcomes and system interactions under realistic runtime.

## NFR Validation
- Latency targets.
- Recovery behavior.
- Error budget style reliability checks.

Why:
- Prevents functionally correct but operationally unacceptable behavior.

---

## 13) Global Quality Gates

## Gate G0: Setup Gate
- Environment and scaffold ready.

## Gate G1: Durability Gate
- Mission persistence and recovery proven.

## Gate G2: Runtime Governance Gate
- Routing, HITL, event contracts, idempotency proven.

## Gate G3: Operational UI Gate
- Mission Control functional and contract aligned.

## Gate G4: Hardening Gate
- Security, reliability, and NFR reports passed.

## Gate G5: Release Readiness Gate
- Traceability and acceptance evidence complete.

Rule:
- No phase advancement without gate signoff and evidence links.

---

## 14) Definition of Ready and Definition of Done

## Definition of Ready (phase level)
A phase is ready when:
1. Prior phase gate is passed.
2. Required docs for this phase exist in draft complete form.
3. Test plan for this phase is defined.
4. Required dependencies are available.

## Definition of Done (phase level)
A phase is done when:
1. All scoped code tasks implemented.
2. All scoped tests pass.
3. Exit criteria validated with evidence.
4. Memory bank updated.
5. Traceability matrix updated.

---

## 15) Change Control and Scope Management

1. Any new requirement must reference `FR-*` or create explicit change request.
2. Any architecture impacting change must either fit existing ADRs or add new ADR.
3. Any schema change requires migration and rollback notes.
4. Any event contract change requires `schema_version` compatibility note.
5. Any UI contract change requires update to UI specs and component contracts.

Why:
- Maintains stable velocity without hidden rework.

---

## 16) RACI Model

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| PRD compliance | Current AI session | PraxLannister | Other AI | Team |
| ARD and LLD drafting | Current AI session | PraxLannister | Other AI | Team |
| Implementation | Current AI session | PraxLannister | Other AI | Team |
| Test evidence | Current AI session | PraxLannister | Other AI | Team |
| Final phase gate signoff | PraxLannister | PraxLannister | All AI sessions | Team |

Note: "Current AI session" = whichever AI (Claude/Cline, Codex, Antigravity) God is working with at that moment. God decides per-session.

---

## 17) Immediate Action Plan (Next 48 Hours)

1. Create directory scaffold from Section 10.
- Why: unblock deterministic artifact placement.

2. Create `traceability-matrix-1.0.md` with all `FR-1..FR-44` rows.
- Why: foundation for coverage and gate checks.

3. Produce Phase 1 required docs (`ard-006`, `lld-05`, `db-schema-1.0`, crash sequence diagram).
- Why: minimum contract for persistence slice.

4. Implement repository layer and replace in-memory mission path.
- Why: highest risk reduction and first hard technical proof.

5. Run Phase 1 tests and generate evidence summary.
- Why: qualify progression to Phase 2.

---

## 18) Commands Checklist by Phase

## Phase 0 command checklist
```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine

docker compose --env-file .env.local -f infra/docker-compose.yml up -d

cd backend
pip install -r requirements.txt
python main.py

cd ../apps/web
npm install
npm run dev
```

## Phase 1 command checklist
```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine

# run migration using your configured DATABASE_URL
psql "$DATABASE_URL" -f backend/adapters/postgres/migrations/001_initial.sql

# run backend tests
cd backend
pytest -q
```

## Phase 2 to 4 command checklist
```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/backend
pytest -q

cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/apps/web
npm test
```

Note:
- Adjust test commands to match final project scripts once standardized.

---

## 19) Evidence Template (Use for Every Gate)

For each gate, record:
1. Date and owner.
2. Commits included.
3. Docs updated.
4. Tests executed with pass/fail summary.
5. Open issues and mitigation owner.
6. Decision: pass, conditional pass, fail.

Recommended storage:
- `docs/00-program/gate-reviews/gate-gX-YYYY-MM-DD.md`

---

## 20) Final Guidance

This plan is intentionally strict on contracts and strict on testing, while still optimized for fast implementation.

If a conflict appears between speed and correctness:
- Prefer the smallest additional design artifact that resolves ambiguity.
- Then resume implementation in the same phase.

Do not return to broad pre implementation documentation mode.
Do not code new scope without FR and CAP linkage.

The correct path is disciplined execution with visible working slices each week.

---

## 21) Environment, Keys, and Secrets Guide (env.local)

This section defines exactly which keys are needed, at which phase and step, and how to generate or obtain them safely.

## 21.1 Secret Management Rules (Mandatory)

1. Never commit real secrets to git.
2. Keep only example files in git (`*.example`).
3. Use `.env.local` for local development secrets.
4. Keep backend and frontend env files separate.
5. Rotate credentials if they are accidentally exposed.

Why:
- Prevents secret leakage and environment drift.

## 21.2 Env File Locations

Use these files:
1. Repository root: `.env.local`
- Purpose: docker compose variable injection (PostgreSQL credentials and any infra-level vars).

2. Backend: `backend/.env.local`
- Purpose: runtime settings consumed by `backend/config.py`.
- Note: backend now loads `.env.local` first, then `.env`.

3. Frontend: `apps/web/.env.local`
- Purpose: Next.js client-facing config (`NEXT_PUBLIC_*`).

Why separate files:
- Least privilege and clearer ownership of keys.

## 21.3 Key Matrix by Phase and Step

Legend:
- Required: must exist for that phase to pass.
- Optional: needed only if that provider or feature is used.

| Key | Used by | First required at phase/step | Required | How to obtain/generate |
|---|---|---|---|---|
| `POSTGRES_USER` | docker compose postgres service | Phase 0, infra startup step | Yes | Choose value, e.g. `synarch` |
| `POSTGRES_PASSWORD` | docker compose postgres service | Phase 0, infra startup step | Yes | Generate with `openssl rand -base64 24` |
| `POSTGRES_DB` | docker compose postgres service | Phase 0, infra startup step | Yes | Choose value, e.g. `synarch` |
| `DATABASE_URL` | backend checkpointer + repos | Phase 0, backend startup step | Yes | Compose from postgres vars |
| `NATS_URL` | backend NATS adapter | Phase 0, backend startup step | Yes | `nats://localhost:4222` for local |
| `QDRANT_URL` | backend vector store (future phases) | Phase 0 setup baseline | Recommended | `http://localhost:6333` |
| `OLLAMA_API_BASE` | litellm local model path | Phase 2, runtime step | Optional/Recommended | `http://localhost:11434` |
| `AWS_REGION_NAME` | Bedrock model invocation | Phase 2, runtime step | Required for Bedrock | AWS region, e.g. `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Bedrock model invocation | Phase 2, runtime step | Required for Bedrock | IAM user or STS temporary creds |
| `AWS_SECRET_ACCESS_KEY` | Bedrock model invocation | Phase 2, runtime step | Required for Bedrock | IAM user or STS temporary creds |
| `AWS_SESSION_TOKEN` | Bedrock with temporary creds | Phase 2, runtime step | Optional | STS / SSO temporary session token |
| `MODEL_SYNARCH` | agent model override | Phase 2, model routing step | Optional | Set explicit model string |
| `MODEL_ZEUS` | agent model override | Phase 2, model routing step | Optional | Set explicit model string |
| `MODEL_THOTH` | agent model override | Phase 2, model routing step | Optional | Set explicit model string |
| `MODEL_HERMES` | agent model override | Phase 2, model routing step | Optional | Set explicit model string |
| `MODEL_HEPHAESTUS` | agent model override | Phase 2, model routing step | Optional | Set explicit model string |
| `MODEL_JANUS` | agent model override | Phase 2, model routing step | Optional | Set explicit model string |
| `APPROVAL_TIMEOUT_SECONDS` | HITL timeout behavior | Phase 2, HITL step | Yes | Integer seconds (default `300`) |
| `DEFAULT_AUTHORITY_MODE` | mission governance mode | Phase 2, HITL step | Yes | `guided`, `supervised`, or `free_rein` |
| `DEBUG` | backend runtime logging/detail | Phase 0 startup | Recommended | `true` local, `false` production |
| `CORS_ORIGINS` | backend API CORS | Phase 3, UI integration step | Yes | JSON array, e.g. `["http://localhost:3000"]` |
| `NEXT_PUBLIC_API_BASE_URL` | frontend REST client | Phase 3, UI wiring step | Yes | `http://localhost:8000` |
| `NEXT_PUBLIC_SSE_BASE_URL` | frontend SSE client | Phase 3, UI wiring step | Yes | `http://localhost:8000` |
| `NEXT_PUBLIC_ENABLE_MISSION_STREAM` | frontend feature flag | Phase 3, UI stream step | Optional | `true` or `false` |

## 21.4 Important Consistency Rule

`DATABASE_URL` must match `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`.

Why:
- If these drift, backend checkpointer and repositories fail at startup or runtime.

Validation check:
```bash
psql "$DATABASE_URL" -c 'select 1;'
```

---

## 22) Step-by-Step Setup Guide to Generate env.local Files

## Step A: Generate root `.env.local` for Docker Compose

From repository root:

```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine
cp .env.local.example .env.local
```

Generate secure password:

```bash
openssl rand -base64 24
```

Then replace `replace_with_secure_password` in `.env.local`.

Why:
- Compose reads these values and initializes PostgreSQL consistently.

## Step B: Generate `backend/.env.local`

```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/backend
cp .env.example .env.local
```

Then edit `backend/.env.local` and set at minimum:

```env
DATABASE_URL=postgresql://synarch:<same_password_as_root_env_local>@localhost:5432/synarch
NATS_URL=nats://localhost:4222
QDRANT_URL=http://localhost:6333
OLLAMA_API_BASE=http://localhost:11434
AWS_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
APPROVAL_TIMEOUT_SECONDS=300
DEFAULT_AUTHORITY_MODE=supervised
```

Why:
- Backend config is loaded from this file and powers all runtime adapters.

## Step C: Generate `apps/web/.env.local`

```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/apps/web
cp .env.local.example .env.local
```

Edit and keep:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SSE_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_MISSION_STREAM=true
```

Why:
- Frontend must know where to call backend and stream events.

## Step D: Start stack with root `.env.local`

```bash
cd /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine
docker compose --env-file .env.local -f infra/docker-compose.yml up -d
```

Then start backend and frontend in separate shells.

---

## 23) How to Obtain Cloud API Credentials (Bedrock)

## Option 1: IAM access key pair (simple local PoC)

1. Create IAM user with Bedrock invoke permission.
2. Generate access key pair.
3. Put values in `backend/.env.local` as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
4. Set `AWS_REGION_NAME` to the enabled Bedrock region.

## Option 2: AWS SSO / STS temporary credentials (recommended)

1. Authenticate with AWS SSO in terminal.
2. Export temporary credentials to environment.
3. Copy values to `backend/.env.local` including `AWS_SESSION_TOKEN`.
4. Reissue when token expires.

Why option 2 is preferred:
- Reduces risk of long-lived credential leakage.

---

## 24) Phase-by-Phase Secret Checklist

## Phase 0 checklist
- [ ] root `.env.local` created.
- [ ] postgres variables set.
- [ ] `backend/.env.local` created.
- [ ] `DATABASE_URL` connects successfully.
- [ ] `NATS_URL` reachable.

## Phase 1 checklist
- [ ] migration runs with `DATABASE_URL`.
- [ ] checkpointer setup succeeds.

## Phase 2 checklist
- [ ] Bedrock or Ollama credentials configured for selected models.
- [ ] `APPROVAL_TIMEOUT_SECONDS` and `DEFAULT_AUTHORITY_MODE` set.
- [ ] model override keys set if non-default routing needed.

## Phase 3 checklist
- [ ] `apps/web/.env.local` created.
- [ ] frontend base URLs match backend host/port.
- [ ] CORS origins include frontend URL.

## Phase 4 checklist
- [ ] secret redaction tests passing.
- [ ] no secrets in event stream payload snapshots.
- [ ] no secrets in frontend logs.

## Phase 5 checklist (if executed)
- [ ] external integration keys scoped by actor or organization context.
- [ ] rotation and revocation procedure documented for each integration.

---

## 25) Quick Troubleshooting for Env Setup

1. Backend cannot connect to PostgreSQL.
- Check `DATABASE_URL` matches root `.env.local` postgres values.
- Re-run `docker compose --env-file .env.local ... up -d`.

2. NATS events are dropped.
- Check `NATS_URL` in `backend/.env.local`.
- Verify NATS container is healthy and reachable on `4222`.

3. Bedrock calls fail with auth errors.
- Validate region and credentials.
- If using temporary creds, verify session token not expired.

4. Frontend cannot call backend.
- Validate `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_SSE_BASE_URL`.
- Validate backend CORS includes frontend origin.

5. Compose values not applied.
- Ensure command includes `--env-file .env.local`.
- Confirm `.env.local` is in repo root.

---

## 26) Final Rule for Secrets During Implementation

For every PR that introduces a new provider or integration:
1. Add key names to this section.
2. Add `.example` entries, never real values.
3. Add runtime validation for missing required keys.
4. Add tests covering missing-key failure behavior.

Reason:
- Keeps environment management deterministic and secure as scope grows.
