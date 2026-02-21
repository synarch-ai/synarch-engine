# Master Docs Comparison Findings and Merge Decisions

Date: 2026-02-21
Canonical PRD: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD (v1.2, FR-1..FR-86)
Compared sets:
- /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/techDocsCline
- /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/techDocsCodex
- /Users/praxlannister/Documents/workspace/synarch-ai/techDocsAntigravity

## 1. Executive Findings

1. `techDocsCline` is strongest on implementation detail (payload examples, tables, event breadth, component trees).
2. `techDocsCodex` is strongest on invariants/governance (must/shall rules, delta protocol, anti-drift controls).
3. `techDocsAntigravity` is strongest on future-readiness (Rule-of-Two rigor, replay/time-travel hooks, budget degradation, protocol surfaces).
4. There are hard conflicts that must be resolved before issue execution:
- endpoint naming and paths
- authority mode vocabulary
- event envelope shape
- schema naming and table model

## 2. Conflicts and Resolution

### 2.1 API Path Conflict

Conflict:
- Cline uses `/api/v1/missions/*` style with separate approval endpoints (`/api/v1/approvals/{id}/approve`).
- Codex and live backend use `/api/v1/mission/*` plus `/api/v1/missions` list.

Resolution:
- Canonicalize to PRD + current backend path family:
  - `POST /api/v1/mission/start`
  - `GET /api/v1/mission/{mission_id}/state`
  - `GET /api/v1/mission/{mission_id}/stream`
  - `POST /api/v1/mission/{mission_id}/approvals/{approval_id}/decision`
  - `POST /api/v1/mission/{mission_id}/pause|resume|cancel`
  - `GET /api/v1/missions`

### 2.2 Authority Mode Conflict

Conflict:
- Cline: `autopilot|supervised|manual`
- PRD/backend/Codex: `guided|supervised|free_rein`

Resolution:
- Canonicalize to PRD values: `guided|supervised|free_rein`.

### 2.3 Event Envelope Conflict

Conflict:
- Cline envelope (`event_id`, `event_type`, `version`, `agent_name`).
- Codex/backend envelope (`id`, `type`, `subject`, `agent`, `schema_version`, `idempotency_key`).

Resolution:
- Canonicalize to backend-compatible envelope and keep additive optional fields (`correlation_id`, `causation_id`, `stage`) for enterprise traceability.

### 2.4 DB Schema Conflict

Conflict:
- Cline names: `sub_tasks`, `agent_events`, `mode/state`.
- PRD/backend names: `tasks`, `mission_events`, `authority_mode/status`.

Resolution:
- Canonicalize to PRD/backend names (`tasks`, `mission_events`, `authority_mode/status`) and absorb Cline strengths as additional columns/tables.

## 3. Best-of-Breed Merge Decisions

### HLD
- Base: Codex invariants + PRD v1.2 structure.
- Added from Cline: runtime topology, component boundaries, dataflow and implementation checkpoints.
- Added from Antigravity evaluation: Rule-of-Two rigor, cost degradation policy, sandbox and protocol readiness.

### LLD
- Added explicitly as missing Level-1 artifact.
- Covers module boundaries, orchestrator node contracts, policy gates, replay, and test matrix.

### API Contract
- Base: PRD/backend-compatible route names and semantics.
- Added from Cline: concrete payload examples, SSE framing, operational health/metrics shape.
- Added from Codex: middleware order, idempotency conflict semantics, contract-change governance.
- Added from Antigravity source: replay endpoint, agent config hot-reload contract, and budget-aware request fields.

### Event Catalog
- Base: backend/Codex envelope shape and subject taxonomy.
- Added from Cline: broad event dictionary and consumer-group mapping.
- Added from Antigravity source: telemetry envelope extension and explicit security/eval event subjects for FR-45..FR-56 and FR-86.

### DB Schema
- Base: PRD/backend table naming and state model.
- Added from Cline: richer cost/config/memory structures.
- Added from Antigravity source: replay metadata + eval hooks + budget-related fields.

## 4. Canonical Files Produced

1. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/hld/synarch-hld.md
2. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/lld/synarch-lld.md
3. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/api-contract.md
4. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/umbrella-event-catalog.md
5. /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/05-data/master-db-schema.md

## 5. Ralph Execution Rule (effective immediately)

Per issue mini-spec MUST include:
1. FR coverage
2. exact files touched
3. migration filenames (if schema changes)
4. API delta
5. event delta
6. tests to add/update
7. rollback plan

No undocumented schema/API/event changes are allowed.

## 6. Principal-Engineer Re-Review Fixes Applied (2026-02-21)

1. Added transactional outbox contract for event publication consistency.
2. Added DB-backed mission sequence allocator (`next_mission_sequence`) to avoid parallel writer collisions.
3. Standardized event subject grammar to bounded-cardinality routing subjects.
4. Added keyset pagination contract for `GET /api/v1/missions`.
5. Constrained `deliverables.review_status` and `replay_metadata.status` via enums.
6. Changed `missions.thread_id` to nullable + partial unique index for async runtime assignment.
7. Added explicit SSE replay-gap semantics (`409 REPLAY_GAP`, `410 STREAM_HISTORY_EXPIRED`).
8. Replaced raw thought payload contract with redaction-safe `thought_summary` + `redaction_level`.
9. Added migration governance note for event-table partition planning at scale.
10. Added optimistic-locking schema fields for mission and approval state transitions.
11. Added soft-delete mission model (`deleted_at`) and active-query indexing guidance.
12. Added updated_at trigger contract for mutation safety across tables.
13. Added approval timeout control-loop requirement and race-safe decision semantics.
14. Added keyset pagination contract for approvals list endpoint.
15. Added agent referential-integrity constraints across task/event/cost/memory data.
16. Added missing operational indexes (`tasks.created_at`, `deliverables.eval_score`, `replay_metadata.status`) and JSONB GIN indexes.
17. Added health degradation criteria, CORS policy, rate-limit policy, and request-timeout policy.
18. Added backup/restore runbook requirement and baseline capacity profile for Phase 0-1.
