# S01 Code Review — Durable Mission Bootstrap

**Reviewer:** Cline (Backend-PE) | **Date:** 2026-02-21
**Commit:** `3085655` | **Files:** 6 | **Lines Added:** ~558

---

## Overall Grade: B+ (Merge with 2 P1 fixes)

---

## File 1: `repositories.py` (277 lines) — Grade: B+

### ✅ Excellent
- **Zero SQL injection risk** — ALL queries use `$N` parameterized placeholders
- **Atomic create()** — single transaction wraps: mission INSERT → payload INSERT → sequence counter → event INSERT → outbox INSERT. If any fails, all roll back
- **Correct outbox pattern** — event and outbox share same `event_id`, written in same transaction
- **Proper pool management** — `async with self.pool.acquire()` ensures connection release
- **Soft-delete aware** — `WHERE deleted_at IS NULL` on reads

### 🔴 Issues

| # | Severity | Issue | Fix |
|---|---|---|---|
| 1 | **P1** | `update_status()` does bare UPDATE with NO outbox write. Status changes (pause/resume/cancel) won't publish events. SSE bridge won't see state transitions. | Add event+outbox write inside same transaction as status UPDATE |
| 2 | **P1** | `update_status()` has no optimistic locking. No `WHERE version = $expected AND status = $current_status`. Two concurrent requests can both succeed. | Add `version` check: `UPDATE missions SET status=$1, version=version+1 WHERE id=$2 AND version=$3 RETURNING version` |
| 3 | **P2** | No connection timeout configured on pool creation. If Postgres is slow, acquire() hangs forever. | Add `timeout=10` to `asyncpg.create_pool()` |
| 4 | **P2** | `list_missions()` has no pagination. Returns ALL missions with `LIMIT 100`. | Add cursor-based pagination per API contract |
| 5 | **P2** | `get()` returns `None` for not found — no distinction between "not found" and "deleted". | Return typed result (e.g., `MissionNotFound` vs `MissionDeleted`) |
| 6 | **P3** | No retry logic on pool creation failure at startup. | Add exponential backoff on `create_pool()` |

---

## File 2: `dependencies.py` (32 lines) — Grade: A-

### ✅ Excellent
- Clean FastAPI dependency injection
- Repository created per-request from shared pool

### 🔴 Issues

| # | Severity | Issue |
|---|---|---|
| 1 | **P3** | No error handling if pool is None (e.g., before startup completes) |

---

## File 3: `missions.py` (API routes) — Grade: B

### ✅ Good
- Working CRUD endpoints
- Proper async handlers
- Returns JSON responses with mission data

### 🔴 Issues

| # | Severity | Issue | Fix |
|---|---|---|---|
| 1 | **P1** | API paths are `/missions/*` not `/api/v1/mission/*` per contract v2.0 | Change router prefix to match canonical contract |
| 2 | **P1** | No `Idempotency-Key` header handling on POST endpoints | Add idempotency middleware per FR-14/FR-78 |
| 3 | **P1** | No `X-Request-Id` response header | Required by API contract §2 |
| 4 | **P2** | No Pydantic request validation models — accepts raw dict | Create `MissionCreateRequest` schema |
| 5 | **P2** | Error responses are plain strings, not canonical error envelope | Implement `{"error": {"code": "...", "message": "...", "request_id": "..."}}` |
| 6 | **P2** | No `authority_mode` validation — accepts any string | Validate against `guided|supervised|free_rein` |
| 7 | **P3** | Missing `/start` endpoint — create + start are merged | Separate per contract (POST create, then POST start) |

---

## File 4: `container.py` — Grade: A-

### ✅ Excellent
- Proper startup/shutdown lifecycle
- Pool created on startup, closed on shutdown
- Settings loaded from config

### 🔴 Issues

| # | Severity | Issue |
|---|---|---|
| 1 | **P3** | No graceful shutdown timeout — if pool.close() hangs, app hangs |

---

## File 5: `main.py` — Grade: A

### ✅ Excellent
- Clean lifespan context manager
- Container startup/shutdown wired correctly
- No issues found

---

## File 6: `test_missions_api.py` (111 lines) — Grade: B-

### ✅ Good
- 3 tests passing against real PostgreSQL
- Tests create → get → list → status update flow
- Uses TestClient correctly

### 🔴 Issues

| # | Severity | Issue |
|---|---|---|
| 1 | **P1** | No test for concurrent status updates (race condition) |
| 2 | **P1** | No test that outbox event was written on create |
| 3 | **P2** | No test for invalid mission ID (should return 404) |
| 4 | **P2** | No test for invalid status transition (e.g., completed → planning) |
| 5 | **P2** | No test for DB connection failure behavior |
| 6 | **P2** | No test for list pagination |
| 7 | **P3** | No test cleanup — created missions accumulate across runs |

---

## Summary of All Issues

| Severity | Count | Key Items |
|---|---|---|
| **P1** (Critical) | 6 | Missing outbox on status update, no optimistic locking, wrong API paths, no idempotency, no request-id, missing race condition test |
| **P2** (High) | 9 | No pagination, no input validation, no error envelope, no authority_mode check, no connection timeout, missing test cases |
| **P3** (Low) | 4 | No pool error handling, no retry on startup, no graceful shutdown timeout, no test cleanup |

---

## What Must Be Fixed Before Merge

1. **Add outbox write to `update_status()`** (P1) — without this, SSE is broken for state changes
2. **Add optimistic locking** (P1) — without this, concurrent requests corrupt state

## What Can Be Deferred to S02+

- API path alignment (can be done when building S02 routing)
- Idempotency middleware (S09)
- Input validation schemas (S02)
- Pagination (S02)
- Additional tests (ongoing)

---

*This review evaluates S01 against the canonical architecture docs (HLD v2.0, API Contract v2.0, DB Schema v2.0, LLD v1.0). Grade: B+ with clear path to A after the 2 P1 fixes.*
