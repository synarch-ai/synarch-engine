# Synarch Master HLD (Canonical)

Version: 2.0
Date: 2026-02-21
Source of truth: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD
Scope: Level-1 umbrella architecture constitution for FR-1..FR-86

## 1. Purpose

This HLD defines non-negotiable architecture constraints and interaction boundaries.
All implementation issues (S01+) must conform to this document and its companion contracts.

Companion contracts:
1. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/05-data/master-db-schema.md
2. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/api-contract.md
3. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/umbrella-event-catalog.md
4. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/lld/synarch-lld.md

## 2. System Topology

```text
God (Operator)
   |
Mission Control (Next.js)
   | REST                            | SSE
Gateway (FastAPI)              SSE Stream Bridge (Go/Rust/Envoy)
   |-- Control Plane: LangGraph      |-- Event Plane: NATS/JetStream
   |-- Persistence Plane: PostgreSQL (+ LangGraph checkpointer)
   |-- Model Plane: litellm
   |-- Integration Plane: MCP/A2A adapters + external trigger ingress
   |-- Safety Plane: sandbox executor + policy engine + secret redaction
   |-- Optional memory plane: pgvector stores + episodic compaction
```

## 3. Planes and Boundaries

### 3.1 Control Plane

Components:
- FastAPI route handlers
- orchestration application service
- LangGraph graph + policy nodes + interrupt/resume lifecycle

Rules:
1. only graph state drives branching
2. risky side effects must pass policy gate
3. graph pause/resume must be deterministic and audit-attributed

### 3.2 Event Plane

Components:
- NATS publisher/subscriber adapters
- event schema validation
- SSE bridge (Decoupled reverse-proxy to prevent FastAPI connection pool exhaustion)

Rules:
1. all runtime events use canonical envelope
2. event emission is append-only and immutable
3. JetStream routes must maintain bounded cardinality
4. SSE is a projection of event stream, never a source of truth
5. event publication must use transactional outbox coupling with persistence plane

### 3.3 Persistence Plane

Components:
- missions/tasks/deliverables/approvals/event journal tables
- idempotency record store
- replay metadata
- LangGraph checkpointer tables

Rules:
1. no mission-critical state in process memory
2. mission state and approval state survive restart
3. replayability requires retained event/checkpoint continuity
4. mission and approval state transitions use optimistic locking (`version` counters)
5. soft delete is default for missions; hard delete requires explicit admin path

## 4. Architecture Invariants (MUST)

1. Durable runtime only; in-memory mission store is forbidden in production path.
2. Typed contracts only; API and event payloads must be schema-validated.
3. Idempotent side effects only; conflict semantics are required.
4. Rule-of-Two for sensitive operations: approval record first, pause second, resume after decision.
5. Redaction-by-default for events/logs/UI payloads.
6. Correlation/causation fields required for forensic traceability.
7. Quality gates must block merge on failed critical-path checks.
8. Budget-aware model routing must support deterministic degradation paths.
9. Protocol contracts (MCP/A2A) must be additive-versioned and traceable.
10. mission event sequencing must use DB-backed monotonic allocator.
11. no unbounded runtime loops: budget and timeout guards are mandatory control-plane checks.

## 5. Orchestration Model (LangGraph)

Required capabilities:
1. conditional branch routing by state and policy
2. interrupt/resume for HITL approvals
3. review loop with bounded revisions
4. checkpoint persistence at node boundaries
5. deterministic mission completion/failure semantics

High-level flow:
1. create mission record
2. start graph thread with persisted checkpointer
3. execute planning/delegation/specialist nodes
4. emit and persist lifecycle events
5. run review and synthesis
6. handle model-provider limits (429/503) via graceful `infrastructure_pause` edge rather than fatal logic errors
7. enforce budget-policy gate before every model call
8. complete mission with deliverables + provenance

## 6. Rule-of-Two and Autonomy

### 6.1 Approval Lifecycle

1. policy node identifies high-risk action
2. approval request persisted in DB
3. mission state transitions to `awaiting_approval`
4. approval event published and visible in Mission Control
5. operator decision API captures actor/session/device attribution
6. graph resumes deterministically with decision context
7. timeout policy resolves deterministic fallback path
8. timeout sweeper is a required background control-loop, not optional best effort

### 6.2 Autonomy Gradient

Supported modes:
- `guided`
- `supervised`
- `free_rein`

Future extensions:
- confidence scoring
- progressive trust thresholds
- graceful handoff packet to operator
- policy-bound autonomy escalation with downgrade-safe fallback

## 7. Agent Hierarchy and Communication Policy

Hierarchy:
- Tier 0: God
- Tier 1: Synarch
- Tier 2: Zeus, Thoth
- Tier 3: Hephaestus, Hermes, Janus

Communication policy:
1. no skip-level communication in default flow
2. all user intent enters through Synarch path
3. no direct specialist-to-God pathway
4. review gate is mandatory before synthesis completion

## 8. Security Envelope

1. explicit auth mode and policy enforcement at gateway
2. per-agent least privilege for tools and data
3. guardrail wrappers for dangerous tools
4. prompt-injection mitigation path (canary/scanning)
5. secure execution boundary for untrusted code (sandbox class)
6. integration supply-chain checks for external connectors
7. enforcement that approval-gated or sandbox-gated paths are never bypassed

## 9. Observability and Operability

1. structured logs + mission correlation IDs
2. metric families: quality, latency, cost, safety
3. stream parity checks between backend events and UI rendering
4. checkpoint + event replay for incident analysis
5. SLO alerting surfaces and error-budget policy
6. backup + restore runbook must be versioned with migration procedures
7. baseline capacity profile for Phase 0-1: max 5 concurrent missions, DB pool size 20
8. control-plane APIs must remain stateless to allow horizontal scaling behind a load balancer

Runbook reference:
- `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/backup-restore-runbook.md`

## 10. Implementation Conventions

Codebase shape:
- `backend/api`: routes, middleware, schemas
- `backend/domain`: models, events, orchestrator logic
- `backend/ports`: interfaces
- `backend/adapters`: infra-specific implementations
- `apps/web`: Mission Control UI

All architecture changes require:
1. updated contract docs
2. migration plan (if data impact)
3. tests proving backward compatibility or approved breaking change path

## 11. FR Coverage Summary

This HLD governs all FR bands:
- Core runtime: FR-1..FR-44
- Expanded capabilities: FR-45..FR-74
- Runtime closure + enterprise baseline: FR-75..FR-86

## 12. Ralph Delta Protocol

Every issue mini-spec MUST provide:
1. FRs addressed
2. exact files touched
3. exact migration file names
4. API contract deltas
5. event catalog deltas
6. tests and verification matrix
7. rollback strategy

Forbidden:
- undocumented endpoint behavior changes
- undocumented event additions/renames
- undocumented schema changes
