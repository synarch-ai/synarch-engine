# ARD-009: Idempotency and Retry Metadata

**Status:** PROPOSED
**Date:** 2026-02-22
**Author:** Codex (Principal Engineer)

## Context
Synarch API clients (especially UI and automated systems) need safe retry semantics for side-effecting operations (e.g., `POST /missions`, `POST /approvals/{id}/decision`). Network failures or timeout thresholds may cause a client to retry a request that was successfully processed by the server but the response was dropped.

## Decision
We will enforce idempotency via the `Idempotency-Key` HTTP header for all `POST`, `PUT`, `PATCH`, and `DELETE` requests under `/api/v1/`.

### Mechanics
1.  **Middleware Intercept:** `IdempotencyMiddleware` intercepts requests and hashes the request body.
2.  **Lookup:** It checks the `IdempotencyRepository` for a record matching `(scope, idempotency_key)`. Scope is defined as `{method}:{path}`.
3.  **Conflict Resolution:**
    *   If a record exists and the `request_hash` matches, it returns the cached response (with a `X-Idempotent-Replay: true` header).
    *   If a record exists and the `request_hash` differs, it returns a `409 Conflict` (FR-14: "Same key + different payload -> conflict error").
4.  **Execution & Caching:** If no record exists, the request proceeds. The response is intercepted, serialized, and stored in the repository with a TTL (e.g., 24 hours).

### Architecture Alignment
The current implementation of `IdempotencyMiddleware` accesses the `asyncpg.Pool` directly. To align with our Hexagonal Architecture (ARD-005), we must introduce an `IdempotencyRepository` port in `domain` or `ports` and implement it in `adapters/postgres`.

## Consequences
- Requires storage for response bodies. We use the `idempotency_records` table defined in `docs/05-data/master-db-schema.md`.
- Middleware buffers the response body in memory. This is acceptable for our JSON APIs but would need modification if we start handling large file uploads/downloads (which are currently out of scope for the control plane).
