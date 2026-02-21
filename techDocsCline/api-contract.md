# Synarch Engine — Master API Contract

**Version:** 1.0 | **Author:** Cline (Backend-PE) | **Date:** 2026-02-21
**Framework:** FastAPI | **Base URL:** `http://localhost:8000/api/v1`

---

## Authentication

Phase 0-1: API key via `X-API-Key` header (FR-41, FR-79).
Phase 2+: OAuth2 / JWT with session attribution.

```
X-API-Key: synarch-dev-key-{env}
```

---

## Endpoints

### 1. Missions

#### `POST /api/v1/missions` — Create Mission (FR-1, FR-2)

```json
// Request
{
  "goal": "Research best practices for Python async patterns and generate a summary report",
  "mode": "supervised",          // "autopilot" | "supervised" | "manual"
  "constraints": {               // Optional
    "max_cost_usd": 0.10,
    "max_duration_seconds": 180,
    "allowed_agents": ["thoth", "janus"]
  }
}

// Response 201 Created
{
  "id": "uuid",
  "goal": "...",
  "mode": "supervised",
  "state": "created",
  "thread_id": "uuid",
  "created_at": "2026-02-21T17:30:00Z"
}
```

#### `GET /api/v1/missions` — List Missions (FR-4)

```
GET /api/v1/missions?state=executing&limit=20&offset=0

// Response 200
{
  "items": [ { Mission } ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

#### `GET /api/v1/missions/{id}` — Get Mission Detail (FR-4)

```json
// Response 200
{
  "id": "uuid",
  "goal": "...",
  "mode": "supervised",
  "state": "executing",
  "plan": [ { SubTask } ],
  "results": { "thoth": { AgentResult } },
  "cost_usd": 0.045,
  "token_count": 12500,
  "created_at": "...",
  "updated_at": "..."
}
```

#### `POST /api/v1/missions/{id}/start` — Start Execution (FR-6, FR-75)

```json
// Request: empty body
// Response 202 Accepted
{
  "id": "uuid",
  "state": "planning",
  "message": "Mission execution started"
}
```

#### `POST /api/v1/missions/{id}/pause` — Pause Mission

```json
// Response 200
{ "id": "uuid", "state": "paused" }
```

#### `POST /api/v1/missions/{id}/resume` — Resume Mission (FR-5, FR-8)

```json
// Response 200
{ "id": "uuid", "state": "executing" }
```

#### `POST /api/v1/missions/{id}/cancel` — Cancel Mission

```json
// Response 200
{ "id": "uuid", "state": "cancelled" }
```

---

### 2. Approvals (FR-8, FR-15, FR-77)

#### `GET /api/v1/missions/{id}/approvals` — List Pending Approvals

```json
// Response 200
{
  "items": [
    {
      "id": "uuid",
      "mission_id": "uuid",
      "sub_task_id": "uuid",
      "status": "pending",
      "context": {
        "agent": "hephaestus",
        "action": "code_write",
        "description": "Write auth middleware",
        "proposed_output": "..."
      },
      "requested_at": "..."
    }
  ]
}
```

#### `POST /api/v1/approvals/{id}/approve` — Approve Action

```json
// Request
{ "reason": "Looks good, proceed" }  // Optional

// Response 200
{ "id": "uuid", "status": "approved", "resolved_at": "..." }
```

#### `POST /api/v1/approvals/{id}/deny` — Deny Action

```json
// Request
{ "reason": "Needs error handling for edge case X" }

// Response 200
{ "id": "uuid", "status": "denied", "resolved_at": "..." }
```

---

### 3. Events / Streaming (FR-18, FR-76)

#### `GET /api/v1/missions/{id}/events/stream` — SSE Stream

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

// Event format
event: agent.progress
data: {"event_id":"uuid","event_type":"agent.progress","mission_id":"uuid","agent_name":"thoth","timestamp":"...","payload":{"message":"Searching for Python async patterns...","progress":0.3}}

event: agent.completed
data: {"event_id":"uuid","event_type":"agent.completed","mission_id":"uuid","agent_name":"thoth","timestamp":"...","payload":{"summary":"Found 12 relevant sources"}}

event: approval.requested
data: {"event_id":"uuid","event_type":"approval.requested","mission_id":"uuid","agent_name":"hephaestus","timestamp":"...","payload":{"approval_id":"uuid","context":{...}}}
```

#### `GET /api/v1/missions/{id}/events` — Event History (paginated)

```
GET /api/v1/missions/{id}/events?limit=50&after=2026-02-21T17:00:00Z

// Response 200
{
  "items": [ { AgentEvent } ],
  "total": 150,
  "limit": 50
}
```

---

### 4. Agents (FR-12)

#### `GET /api/v1/agents` — List Agent Configs

```json
// Response 200
{
  "items": [
    {
      "name": "zeus",
      "display_name": "Zeus",
      "role": "COO — decomposes missions, routes to specialists",
      "model_default": "claude-sonnet-4-20250514",
      "enabled": true,
      "tools": ["agent_tool_thoth", "agent_tool_hephaestus", "agent_tool_hermes"]
    }
  ]
}
```

#### `GET /api/v1/agents/{name}` — Agent Detail

```json
// Response 200
{
  "name": "thoth",
  "display_name": "Thoth",
  "role": "Research specialist",
  "model_default": "claude-sonnet-4-20250514",
  "temperature": 0.0,
  "max_iterations": 10,
  "tools": ["web_search", "rag_query", "document_reader"],
  "permissions": {
    "code_exec": false,
    "file_write": false,
    "web_access": true,
    "db_access": "read_only"
  }
}
```

---

### 5. Health & Metrics

#### `GET /api/v1/health` — Health Check

```json
// Response 200
{
  "status": "healthy",
  "version": "0.1.0",
  "services": {
    "postgres": "connected",
    "nats": "connected",
    "qdrant": "connected",
    "redis": "connected"
  },
  "uptime_seconds": 3600
}
```

#### `GET /api/v1/metrics` — Cost & Usage Metrics (FR-47, FR-49)

```json
// Response 200
{
  "total_missions": 42,
  "active_missions": 3,
  "total_cost_usd": 2.45,
  "total_tokens": 450000,
  "avg_mission_cost_usd": 0.058,
  "avg_mission_duration_seconds": 95
}
```

---

## Error Format (Consistent)

```json
// 4xx / 5xx Response
{
  "error": {
    "code": "MISSION_NOT_FOUND",
    "message": "Mission with ID abc-123 not found",
    "details": {},
    "correlation_id": "uuid"
  }
}
```

### Error Codes

| Code | HTTP | Description |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Invalid request body |
| `MISSION_NOT_FOUND` | 404 | Mission ID doesn't exist |
| `MISSION_INVALID_STATE` | 409 | Action not valid for current state |
| `APPROVAL_NOT_FOUND` | 404 | Approval ID doesn't exist |
| `APPROVAL_ALREADY_RESOLVED` | 409 | Approval already approved/denied |
| `RATE_LIMITED` | 429 | Too many requests |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Idempotency (FR-14, FR-78)

All state-changing endpoints accept `Idempotency-Key` header:

```
POST /api/v1/missions
Idempotency-Key: client-generated-uuid
```

Server stores key → response mapping for 24 hours. Duplicate requests return cached response.

---

*This API contract is the single source of truth for all REST endpoints. Per-issue work references specific endpoints.*
