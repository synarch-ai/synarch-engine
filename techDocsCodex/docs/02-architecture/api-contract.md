# Synarch Master API Contract (Umbrella Constitution)

Status: Authoritative Level-1 Master Doc (Create Once)
Source baseline: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD (v1.2)
Last updated: 2026-02-21

## 1. Contract Scope

Defines required REST and SSE contracts for control-plane operations.
Any behavior changes require both API delta and test delta.

Base path:
- REST: `/api/v1`
- SSE: `/api/v1/mission/{mission_id}/stream`

## 2. Cross-Cutting Requirements

1. Every response includes `X-Request-Id`.
2. Side-effecting endpoints must enforce idempotency semantics.
3. Typed error envelope is mandatory.
4. Auth mode policy checks execute before business logic.
5. Approval decision endpoints must enforce actor attribution fields.

## 3. Authentication and Middleware Expectations

### 3.1 Auth Modes

Supported modes:
- `local_none` (dev-only)
- `token`
- `proxy`

Mode selection is explicit via configuration and surfaced in health metadata.

### 3.2 Required middleware order

1. request_id
2. auth_mode policy
3. idempotency guard (for POST/PATCH/DELETE)
4. structured error wrapper
5. response logging and correlation

## 4. Canonical Error Envelope

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

HTTP behavior:
- 400 invalid request
- 401/403 auth violations
- 404 missing entity
- 409 conflict/idempotency/invalid state transition
- 422 schema validation
- 500 internal
- 503 dependency unavailable

## 5. Endpoint Contracts

### 5.1 POST /api/v1/mission/start

Headers:
- `Idempotency-Key` required

Request body:
```json
{
  "goal": "string, non-empty",
  "authority_mode": "guided|supervised|free_rein",
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
  "status": "created|planning|executing|awaiting_approval|reviewing|revising|synthesizing|paused|failed|completed|cancelled",
  "authority_mode": "guided|supervised|free_rein",
  "current_branch": "string|null",
  "plan": [],
  "tasks": [],
  "deliverables": [],
  "error_context": null,
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "completed_at": null
}
```

### 5.3 GET /api/v1/missions

Query params:
- `status` optional
- `limit` optional (default 50)
- `cursor` optional

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
  "request_id": "uuid"
}
```

### 5.8 POST /api/v1/mission/{mission_id}/approvals/{approval_id}/decision

Headers:
- `Idempotency-Key` required

Request body:
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

### 5.9 GET /api/v1/agents

Response 200:
```json
{
  "items": [
    {
      "name": "zeus",
      "tier": 2,
      "role": "engineering_commander"
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
  "auth_mode": "token",
  "request_id": "uuid"
}
```

## 6. Idempotency Semantics

1. Same key + same request hash => replay stored response.
2. Same key + different request hash => 409 conflict.
3. TTL expiration is explicit and documented.
4. Idempotency scope includes endpoint identity.

## 7. SSE Contract

Endpoint:
- `GET /api/v1/mission/{mission_id}/stream`

Headers:
- `Last-Event-ID` optional for replay continuation.

SSE frame:
```text
id: <event-id>
event: mission_event
data: {<canonical-event-envelope>}

```

Rules:
1. Stream emits only typed canonical envelopes.
2. Heartbeats must not mask upstream disconnects.
3. On reconnect, server must resume from last known event id when available.

## 8. Versioning and Breaking Change Rules

1. Breaking response/request changes require API version bump.
2. Non-breaking additive fields require schema update and tests.
3. Every API delta must cite impacted FR(s) and issue id.

## 9. Ralph Delta Protocol

Per issue mini-spec must include:
- endpoint(s) touched
- request/response delta
- middleware impact
- idempotency impact
- tests added/updated
- backward compatibility statement
