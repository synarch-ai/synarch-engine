# Principal Engineer Audit — Canonical Architecture Docs

**Auditor:** Cline (Backend-PE, Distinguished Principal) | **Date:** 2026-02-21
**Scope:** Schema, API, HLD, Events — production readiness, scaling, edge cases

---

## Overall Verdict: 🟡 SOLID v1 DRAFT — NOT PRODUCTION-READY YET

The canonical docs are an excellent architectural foundation but have **12 critical issues** and **18 medium issues** that must be addressed before production deployment. Most are solvable with targeted fixes, not redesigns.

---

## CRITICAL ISSUES (Must Fix Before Phase 1 Completion)

### C1: No Approval Race Condition Protection
**Risk:** Two operators approve/reject the same approval simultaneously.
**Schema gap:** `approvals` table has no optimistic locking (no `version` column).
**Fix:** Add `version INTEGER NOT NULL DEFAULT 1` + `WHERE status = 'pending' AND version = :expected_version` in UPDATE.

### C2: No Mission State Transition Guard
**Risk:** Concurrent requests move mission to conflicting states (e.g., pause + cancel simultaneously).
**Fix:** Add `version INTEGER` to `missions` table + optimistic locking on state transitions. OR use `SELECT ... FOR UPDATE SKIP LOCKED` pattern.

### C3: mission_events Table Will Grow Unbounded
**Risk:** No partitioning strategy for the highest-write table. At 100 events/mission × 1000 missions = 100K rows fast.
**Fix:** Partition by `created_at` (monthly range partitions). Add retention policy (archive after 90 days).

### C4: Agent Name References Have No Referential Integrity
**Risk:** `tasks.assigned_agent`, `cost_logs.agent`, `mission_events.agent`, `memories.agent` are all VARCHAR with NO FK to `agent_configs.name`.
**Fix:** Add FK constraints or CHECK constraints against a fixed enum. Agent rename becomes a coordinated migration.

### C5: Missing updated_at Triggers
**Risk:** `updated_at` columns exist but no auto-update trigger. Application code must remember to set it — guaranteed to be forgotten.
**Fix:** Add `CREATE TRIGGER` for auto-updating `updated_at` on all tables with that column.

### C6: Approval Timeout Not Enforced
**Risk:** Approval has `timeout_seconds` column but no mechanism to enforce it. Missions can be stuck in `awaiting_approval` forever.
**Fix:** Background job/scheduler that checks `requested_at + timeout_seconds < NOW()` and auto-resolves with `timeout` status.

### C7: SSE Connection Scaling Not Addressed
**Risk:** Each SSE connection holds an open HTTP connection. 100 concurrent dashboards = 100 persistent connections. No max limit defined.
**Fix:** Define max SSE connections per mission (e.g., 10). Use connection pooling. Consider WebSocket for future.

### C8: NATS Down = Silent Event Loss
**Risk:** If NATS is temporarily unavailable, events published by agents are silently lost. No retry/buffer mechanism specified.
**Fix:** Local event buffer (in-memory queue) with retry. Or use NATS JetStream's built-in persistence with publisher acknowledgment.

### C9: No Cost Budget Enforcement Mechanism
**Risk:** `cost.budget_warning` and `cost.budget_exceeded` events are defined, but no mechanism to actually STOP a mission when budget is exceeded.
**Fix:** Add budget check in the orchestration loop before each LLM call. If exceeded, transition to `paused` or `failed` with budget reason.

### C10: Idempotency Key Collision Under High Throughput
**Risk:** Client-generated idempotency keys could collide if poorly generated. `UNIQUE(scope, idempotency_key)` will throw 500 instead of proper 409.
**Fix:** Catch unique constraint violation and return 409 `IDEMPOTENCY_CONFLICT` with the original response.

### C11: No Soft Delete Support
**Risk:** `ON DELETE CASCADE` means deleting a mission permanently destroys all sub-tasks, events, approvals, costs. No recovery possible.
**Fix:** Add `deleted_at TIMESTAMPTZ` column to `missions`. Change queries to filter `WHERE deleted_at IS NULL`. CASCADE only on hard delete.

### C12: Docker Compose Data Loss on Restart
**Risk:** If PostgreSQL data volume is not explicitly mounted, `docker compose down -v` destroys all data.
**Fix:** Ensure `docker-compose.yml` has named volumes for PostgreSQL data. Document backup/restore procedure.

---

## MEDIUM ISSUES (Fix Before Phase 2)

### M1: ENUM Types Will Cause Migration Pain
PostgreSQL ENUMs can't have values removed (only added). `mission_status`, `task_status`, `approval_status`, `memory_type` will need `ALTER TYPE ... ADD VALUE` for every new state.
**Alternative:** Use `VARCHAR` with `CHECK` constraint instead — easier to migrate.

### M2: JSONB Fields Need GIN Indexes
`missions.plan`, `tasks.inputs`, `tasks.result`, `deliverables.content` are all JSONB with no GIN indexes. Querying inside these fields will be full table scans.
**Fix:** Add `CREATE INDEX USING gin()` on frequently queried JSONB fields.

### M3: No Request Timeout Policy Specified
API contract doesn't specify max request timeout. Long-running mission starts could block connections.
**Fix:** Define: 30s for CRUD, 120s for mission start, ∞ for SSE (with keepalive).

### M4: Missing CORS Specification
No CORS configuration defined. Mission Control (port 3000) calling backend (port 8000) will be blocked without proper CORS headers.
**Fix:** Add CORS section to API contract. Allow `localhost:3000` in dev, configurable origins in production.

### M5: No Rate Limiting Details
API contract mentions rate limiting in middleware order but doesn't define limits.
**Fix:** Define: 100 req/min for CRUD, 10 mission starts/min, 1 SSE connection per mission per client.

### M6: Memories Table Has No Size Limit
Agent memories grow unbounded. No max row count, no max content size, no compaction policy.
**Fix:** Add `max_memories_per_agent` config. Implement LRU eviction based on `importance` score.

### M7: Missing Approvals Pagination
`GET /api/v1/mission/{id}/approvals` has no pagination. Long-running missions in guided mode could accumulate hundreds.
**Fix:** Add `limit`/`cursor` params.

### M8: API Response Shape Drift
Contract defines `{"items": [...], "next_cursor": ...}` but current backend returns `{"missions": [...], "total": int}`.
**Fix:** Align implementation to contract OR update contract to match implementation.

### M9: Checkpoint-Mission FK Not Enforced
`missions.thread_id` maps to LangGraph checkpoint `thread_id` but no FK because checkpoints are managed by LangGraph runtime.
**Risk:** Orphaned checkpoints if mission is deleted.
**Mitigation:** Cleanup job that deletes checkpoints for deleted missions.

### M10: No Health Check Degradation Levels
Health endpoint returns `ok|degraded|down` but no definition of what triggers `degraded`.
**Fix:** Define: degraded = any dependency > 500ms response time. Down = any dependency unreachable.

### M11: Single Backend Instance Bottleneck
HLD assumes single backend. No horizontal scaling strategy.
**Future fix:** Stateless API + NATS-based job distribution. LangGraph execution in worker processes.

### M12: LangGraph In-Process Memory Pressure
Each active mission holds a LangGraph graph + conversation history in memory. 10 concurrent missions = significant memory.
**Fix:** Define max concurrent missions (e.g., 5 for PoC). Queue excess. Monitor memory.

### M13-M18: Additional Minor Issues
- M13: No connection pool sizing guidance (recommend: 20 connections for PoC)
- M14: No backup/restore documentation
- M15: No database migration rollback strategy
- M16: `replay_metadata` has no index on `status`
- M17: `deliverables.eval_score` has no index (needed for quality dashboards)
- M18: Missing `created_at` index on `tasks` table

---

## SCALING PROJECTIONS

| Scale | Missions | Events | DB Size | Concern |
|---|---|---|---|---|
| PoC (Phase 0-1) | ~100 | ~10K | < 100MB | No issues |
| Production (Phase 2) | ~10K | ~1M | ~5GB | Need partitioning for mission_events |
| Enterprise (Phase 4) | ~100K | ~100M | ~500GB | Need read replicas, archival, sharding strategy |

---

## RECOMMENDED IMMEDIATE ACTIONS (Phase 0-1)

1. Add `version` column to `missions` and `approvals` for optimistic locking (C1, C2)
2. Add `updated_at` triggers (C5)
3. Add approval timeout background job (C6)
4. Define CORS policy (M4)
5. Ensure Docker volumes are persistent (C12)
6. Add max concurrent missions config (M12)
7. Catch idempotency constraint violations properly (C10)

---

*This audit should be re-run after each phase completion. Production deployment requires all Critical items resolved.*
