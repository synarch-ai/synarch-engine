# Synarch Master API Contract (Canonical)

Version: 2.0
Date: 2026-02-21
Source of truth: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD

## 1. Scope

Defines canonical FastAPI route contracts, middleware expectations, SSE structure, and idempotency semantics.

Base path:
- REST Control Plane: `/api/v1`
- SSE Forwarding Proxy: `http://{proxy_host}:{proxy_port}/api/v1/mission/{mission_id}/stream`

## 2. Cross-Cutting Rules

1. `X-Request-Id` must be present on all responses.
2. Side-effecting endpoints require `Idempotency-Key`.
3. Typed error envelope is mandatory.
4. Auth mode enforcement occurs before business execution.
5. Approval decisions require actor/session/device attribution.
6. approval timeout sweeper must auto-transition stale pending approvals to `timeout`.
7. budget policy checks must run before each model invocation and enforce deterministic mission degradation/stop behavior.

## 3. Auth and Middleware Contract

### 3.1 Supported auth modes
- `local_none` (dev only)
- `token`
- `proxy`

### 3.2 Required middleware order
1. request-id
2. auth policy
3. idempotency guard (for all side-effecting endpoints, including POST/PUT)
4. validation/error wrapper
5. structured response logging

### 3.3 CORS policy
1. development default allowlist: `http://localhost:3000`
2. production allowlist must be explicit config (no wildcard)
3. allowed headers include `Authorization`, `Content-Type`, `Idempotency-Key`, `Last-Event-ID`, `X-Request-Id`

### 3.4 Rate limiting policy
1. `POST /mission/start`: 10 requests/minute per actor
2. mission control CRUD endpoints: 100 requests/minute per actor
3. SSE streams: max 10 concurrent connections per mission, max 2 per actor/mission

### 3.5 Request timeout policy
1. CRUD endpoints: 30s gateway timeout
2. mission start endpoint: 120s timeout
3. SSE endpoints: no request timeout, heartbeat required every <= 25s

## 4. Error Envelope

```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human-readable message",
    "details": {},
    "request_id": "uuid"
  }
}
```

Status classes:
- 400 invalid input
- 401/403 auth violations
- 404 not found
- 409 conflict/state/idempotency mismatch
- 410 replay/stream history expired
- 422 schema validation
- 500 internal error
- 503 dependency unavailable

## 5. Endpoint Catalog

### 5.1 POST /api/v1/mission/start

Headers:
- `Idempotency-Key` required

Request:
```json
{
  "goal": "string",
  "authority_mode": "guided|supervised|free_rein",
  "cost_budget": 100.0,
  "constraints": {},
  "metadata": {}
}
```

Response 201:
```json
{
  "mission_id": "uuid",
  "status": "created",
  "stream_url": "/api/v1/mission/{mission_id}/stream",
  "request_id": "uuid"
}
```

### 5.2 GET /api/v1/mission/{mission_id}/state

Response 200:
```json
{
  "mission_id": "uuid",
  "goal": "string",
  "status": "created|planning|executing|awaiting_approval|reviewing|revising|synthesizing|paused|paused_awaiting_resources|failed|completed|cancelled",
  "authority_mode": "guided|supervised|free_rein",
  "current_branch": "string|null",
  "plan": [],
  "tasks": [],
  "deliverables": [],
  "error_context": null,
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "completed_at": null,
  "request_id": "uuid"
}
```

### 5.3 GET /api/v1/missions

Query params:
- `status` optional
- `limit` optional (default 50)
- `cursor` optional
- `sort` fixed to `created_at_desc` (stable keyset)

Pagination contract:
1. ordering is `created_at DESC, mission_id DESC`
2. cursor encodes `(created_at, mission_id)` from last item
3. cursor must be treated as opaque by clients
4. offset pagination is forbidden for this endpoint

Response 200:
```json
{
  "items": [
    {
      "mission_id": "uuid",
      "goal": "string",
      "status": "executing",
      "created_at": "timestamp"
    }
  ],
  "next_cursor": null,
  "request_id": "uuid"
}
```

### 5.4 POST /api/v1/mission/{mission_id}/pause
### 5.5 POST /api/v1/mission/{mission_id}/resume
### 5.6 POST /api/v1/mission/{mission_id}/cancel

Headers:
- `Idempotency-Key` required

Response 200:
```json
{
  "mission_id": "uuid",
  "status": "paused|executing|cancelled",
  "request_id": "uuid"
}
```

### 5.7 GET /api/v1/mission/{mission_id}/approvals

Query params:
- `status` optional (default `pending`)
- `limit` optional (default 50)
- `cursor` optional

Response 200:
```json
{
  "items": [
    {
      "approval_id": "uuid",
      "status": "pending",
      "requested_by": "hephaestus",
      "action_type": "execute_generated_code",
      "risk_level": "high",
      "requested_at": "timestamp",
      "timeout_seconds": 300
    }
  ],
  "next_cursor": null,
  "request_id": "uuid"
}
```

### 5.8 POST /api/v1/mission/{mission_id}/approvals/{approval_id}/decision

Headers:
- `Idempotency-Key` required

Request:
```json
{
  "decision": "approved|rejected",
  "reason": "string|null",
  "actor": {
    "id": "string",
    "session": "string",
    "device": "string"
  }
}
```

Response 200:
```json
{
  "mission_id": "uuid",
  "approval_id": "uuid",
  "status": "approved|rejected|timeout",
  "resumed": true,
  "request_id": "uuid"
}
```

Health status criteria:
1. `ok`: all dependencies reachable and p95 dependency latency <= 500ms
2. `degraded`: dependencies reachable but any p95 dependency latency > 500ms
3. `down`: any critical dependency unreachable

### 5.9 GET /api/v1/agents

Response 200:
```json
{
  "items": [
    {
      "name": "zeus",
      "tier": 2,
      "role": "engineering_commander",
      "enabled": true
    }
  ],
  "request_id": "uuid"
}
```

### 5.10 GET /api/v1/agents/{name}/soul

Response 200:
```json
{
  "name": "zeus",
  "source": "soul|config",
  "content": "string",
  "request_id": "uuid"
}
```

### 5.11 GET /api/v1/health

Response 200:
```json
{
  "status": "ok|degraded|down",
  "version": "string",
  "dependencies": {
    "postgres": "ok",
    "nats": "ok",
    "checkpointer": "ok"
  },
  "auth_mode": "token|proxy|local_none",
  "request_id": "uuid"
}
```

### 5.12 GET /api/v1/metrics (recommended)

Response 200:
```json
{
  "mission_cost_usd": 0.0,
  "token_usage_total": 0,
  "latency_p95_ms": 0,
  "stream_lag_ms": 0,
  "request_id": "uuid"
}
```

### 5.13 POST /api/v1/mission/{mission_id}/replay (P2)

Headers:
- `Idempotency-Key` required

Request:
```json
{
  "checkpoint_ref": "string",
  "from_sequence": 0
}
```

Response 202:
```json
{
  "mission_id": "uuid",
  "replay_id": "uuid",
  "status": "started",
  "request_id": "uuid"
}
```

### 5.14 PUT /api/v1/agents/{name}/config (P2)

Headers:
- `Idempotency-Key` required

Request:
```json
{
  "model_default": "string",
  "model_fallback": "string|null",
  "temperature": 0.0,
  "max_iterations": 10,
  "tools": [],
  "permissions": {},
  "enabled": true
}
```

Response 200:
```json
{
  "name": "zeus",
  "status": "updated",
  "hot_reload": "accepted|rejected",
  "request_id": "uuid"
}
```

## 6. Idempotency Semantics

1. same key + same request hash -> replay previous response.
2. same key + different request hash -> 409 `IDEMPOTENCY_CONFLICT`.
3. idempotency records must include TTL.
4. idempotency scope is endpoint + actor context.
5. unique-constraint collisions on idempotency storage must be mapped to 409 response, never raw 500.

## 7. SSE Contract (Proxy Decoupled)

Endpoint:
- `GET http://{proxy_host}:{proxy_port}/api/v1/mission/{mission_id}/stream`

Headers:
- `Last-Event-ID` optional for reconnect.

Frame format:
```text
id: <event-id>
event: mission_event
data: {<canonical-event-envelope>}

```

Rules:
1. payload is canonical event envelope only.
2. keepalive heartbeats must not hide upstream failure.
3. reconnect should resume from event store when possible.
4. stale or evicted `Last-Event-ID` must return `409 REPLAY_GAP`.
5. unknown mission stream must return `404 MISSION_NOT_FOUND`.
6. retention-expired replay windows may return `410 STREAM_HISTORY_EXPIRED`.

## 8. Change Management

Any API change requires:
1. contract diff in PR
2. compatibility statement
3. updated tests (contract + integration)
4. version bump for breaking changes

## 9. Implementation Drift Note

Current backend implementation may temporarily expose routes without `/api/v1` prefix.
The canonical contract in this document is the target public interface and must be reached by runtime-closure issues before production readiness.

## 10. FR Linkage

Primary FR coverage:
- FR-1, FR-4, FR-13, FR-14
- FR-18, FR-21, FR-22, FR-24, FR-25
- FR-41, FR-42, FR-76, FR-78, FR-79
- FR-85 (replay endpoint), FR-65/FR-66 (agent config endpoint)
