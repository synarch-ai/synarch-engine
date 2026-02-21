# Synarch Master LLD (Canonical)

Version: 2.0
Date: 2026-02-21
Source baseline: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD

## 1. Purpose

Defines module-level contracts, sequencing, and integration behavior required to implement HLD and contracts without ambiguity.

## 2. Module Map

### 2.1 Backend

1. `backend/api`
- validates HTTP payloads
- invokes orchestration services
- returns typed responses
- enforces configured request/rate/time budget limits

2. `backend/domain`
- mission state model
- event envelope/type definitions
- orchestration node logic and routing rules

3. `backend/ports`
- persistence, event_bus, model_provider, checkpointer interfaces

4. `backend/adapters`
- postgres repositories
- nats client and SSE bridge
- litellm provider
- langgraph checkpointer integration
- mcp/a2a protocol adapters
- sandbox execution adapters
- database pool baseline: 20 connections for Phase 0-1

### 2.2 Web

1. `apps/web/app`
- mission start + inspect pages

2. `apps/web/components`
- timeline
- approval inbox
- task/deliverable views

3. `apps/web/lib`
- API client (REST Gateway)
- SSE client with reconnect handling (Dedicated Stream Bridge)

## 3. Core Domain Types

### 3.1 MissionState

Required fields:
- mission_id
- goal
- authority_mode
- phase/state
- plan
- tasks
- deliverables
- approval_request (optional)
- review verdict and revision count
- cost/latency summaries

### 3.2 ApprovalDecision

Required fields:
- decision (`approved|rejected|timeout`)
- reason
- actor id/session/device
- decided_at

### 3.3 EventEnvelope

Canonical event shape as defined in:
- /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/umbrella-event-catalog.md

## 4. Orchestrator Node Contract

Required nodes:
1. `plan`
2. `route`
3. `execute`
4. `policy_gate`
5. `approve_interrupt`
6. `review`
7. `synthesize`
8. `error_handler`

Node contract shape:
- inputs: immutable snapshot + prior messages
- output: explicit state patch
- side effects: emitted event(s) + persistence updates
- routing edges: must include graceful fallback (e.g., `infrastructure_pause`) for upstream 429/503 limits to prevent cascading graph failure
- failure: typed terminal error + retry policy metadata

## 5. Transactional Sequencing Rules

For side-effecting node completion:
1. persist state mutation intent
2. perform side effect (guarded)
3. allocate mission-scoped sequence via DB allocator
4. persist outcome and metadata
5. write canonical event to outbox in same DB transaction
6. checkpoint thread
7. async outbox worker publishes to NATS and marks `published_at`

For approval interruption:
1. persist approval request
2. emit approval.requested event
3. transition mission state to awaiting_approval
4. interrupt graph

For approval decision:
1. validate pending status and expected `version`
2. persist decision + attribution with optimistic-lock update (`WHERE status='pending' AND version=:expected_version`)
3. emit decision event
4. resume graph with decision context

For mission state transition commands:
1. read current mission row (`status`, `version`)
2. validate allowed transition
3. update with optimistic-lock guard (`WHERE id=:id AND version=:expected_version`)
4. increment `version` on success
5. emit state-changed event through outbox path

## 6. API-Layer Behavior

1. route handlers must not contain business rules
2. all state transitions delegated to application/orchestrator service
3. idempotency guard executes before invoking orchestration service
4. standardized error envelope for all failures
5. mission approval list endpoint must support keyset pagination (`limit` + opaque `cursor`)

## 7. Event-Layer Behavior

1. event publisher validates envelope before publish
2. sequence assignment is mission-scoped monotonic
3. sequence assignment uses DB allocator (`next_mission_sequence`) to avoid race conflicts
4. subscriber processing is idempotent
5. SSE proxy adapter connects to NATS, filters on `X-Mission-Id` headers, and forwards canonical envelope unchanged (except framing)
6. Last-Event-ID replay path required for reconnect

## 8. Persistence-Layer Behavior

1. repository methods are async and transaction-aware
2. mission state update and related writes occur atomically where required
3. event journal is append-only
4. approval rows become immutable after terminal status
5. idempotency records enforce key+hash semantics
6. outbox write is transactionally coupled to mission state changes
7. outbox publisher retries with backoff and dead-letters terminal failures
8. updated_at timestamps are trigger-maintained, not manually set by handlers
9. agent-bearing columns enforce referential integrity to `agent_configs`

## 9. Runtime Control Loops

1. approval timeout sweeper scans pending approvals on fixed cadence and applies deterministic timeout decisions
2. budget guard runs before each model invocation and halts/degrades mission when thresholds are exceeded
3. checkpoint orphan reconciler removes orphan runtime checkpoint rows after hard delete events

## 10. Test Matrix (Minimum)

### 10.1 Unit
- state transition guards
- policy gate decisions
- envelope validation
- idempotency hash conflict behavior

### 10.2 Integration
- API -> orchestrator -> DB happy path
- NATS publish -> SSE stream parity
- approval interrupt/resume lifecycle
- restart recovery from checkpoints
- concurrent approval decision race (single winner)
- concurrent mission transition race (single winner)
- timeout sweeper auto-resolution path
- budget exceed transition path

### 10.3 Contract
- request/response schema conformance
- event payload conformance
- migration compatibility checks

## 11. Merge Gate Checklist

Every PR touching runtime must include:
1. FR mapping
2. changed module list
3. API contract delta (if any)
4. event contract delta (if any)
5. migration + rollback notes (if data change)
6. test evidence (unit/integration/contract)

## 12. Non-Goals in LLD

1. visual design details (owned by Mission Control design docs)
2. model prompt content details (owned by soul/config docs)
3. deployment-runbook specifics (owned by infra docs)

## 13. FR Linkage

Primary FR coverage:
- FR-2, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10
- FR-14, FR-18, FR-19, FR-20
- FR-21, FR-22, FR-23, FR-24, FR-25
- FR-75, FR-76, FR-77, FR-78, FR-81
