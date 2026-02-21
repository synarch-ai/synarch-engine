# Synarch Engine — Umbrella Event Catalog

**Version:** 1.0 | **Author:** Cline (Backend-PE) | **Date:** 2026-02-21
**Transport:** NATS JetStream | **Format:** JSON | **Envelope:** FR-19

---

## NATS Subject Convention

```
synarch.{domain}.{entity_id}.{event_category}.{event_name}
```

**Stream:** `SYNARCH` (JetStream durable stream)
**Retention:** WorkQueue for SSE bridge, Limits for audit (7 days)

---

## Canonical Event Envelope

Every event published to NATS uses this envelope:

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "mission.state_changed",
  "version": "1.0",
  "timestamp": "2026-02-21T17:30:00.123Z",
  "mission_id": "550e8400-e29b-41d4-a716-446655440001",
  "agent_name": "zeus",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440002",
  "payload": { ... },
  "metadata": {
    "cost_usd": 0.003,
    "token_count": 850,
    "model": "claude-sonnet-4-20250514",
    "latency_ms": 1200
  }
}
```

---

## Event Dictionary

### 1. Mission Events

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.created` | `mission.created` | POST /missions | `{ goal, mode, constraints }` |
| `synarch.mission.{id}.started` | `mission.started` | POST /missions/{id}/start | `{ thread_id }` |
| `synarch.mission.{id}.state_changed` | `mission.state_changed` | Any state transition | `{ from_state, to_state, reason }` |
| `synarch.mission.{id}.paused` | `mission.paused` | POST /missions/{id}/pause | `{ paused_at_node }` |
| `synarch.mission.{id}.resumed` | `mission.resumed` | POST /missions/{id}/resume | `{ resumed_from_node }` |
| `synarch.mission.{id}.completed` | `mission.completed` | Synthesize node finishes | `{ result_summary, total_cost, duration_ms }` |
| `synarch.mission.{id}.failed` | `mission.failed` | Unrecoverable error | `{ error, failed_at_node, retry_count }` |
| `synarch.mission.{id}.cancelled` | `mission.cancelled` | POST /missions/{id}/cancel | `{ cancelled_by, reason }` |

### 2. Planning Events

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.plan.created` | `plan.created` | Zeus produces plan | `{ sub_tasks: [{ title, agent, sequence }] }` |
| `synarch.mission.{id}.plan.revised` | `plan.revised` | Re-planning after review | `{ changes, revision_count }` |

### 3. Agent Lifecycle Events

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.agent.{name}.assigned` | `agent.assigned` | Route node selects agent | `{ sub_task_id, sub_task_title }` |
| `synarch.mission.{id}.agent.{name}.started` | `agent.started` | Agent begins execution | `{ sub_task_id, model, iteration: 1 }` |
| `synarch.mission.{id}.agent.{name}.progress` | `agent.progress` | Periodic during execution | `{ message, progress: 0.0-1.0, iteration }` |
| `synarch.mission.{id}.agent.{name}.thinking` | `agent.thinking` | LLM reasoning step | `{ thought_summary }` |
| `synarch.mission.{id}.agent.{name}.completed` | `agent.completed` | Agent finishes sub-task | `{ output_summary, cost_usd, tokens }` |
| `synarch.mission.{id}.agent.{name}.error` | `agent.error` | Agent encounters error | `{ error, retryable, retry_count }` |

### 4. Tool Events

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.agent.{name}.tool.called` | `tool.called` | Agent invokes a tool | `{ tool_name, arguments }` |
| `synarch.mission.{id}.agent.{name}.tool.result` | `tool.result` | Tool returns result | `{ tool_name, result_summary, duration_ms }` |
| `synarch.mission.{id}.agent.{name}.tool.error` | `tool.error` | Tool execution fails | `{ tool_name, error }` |

### 5. Approval Events (FR-15, FR-77)

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.approval.requested` | `approval.requested` | Graph hits interrupt node | `{ approval_id, agent, action, context }` |
| `synarch.mission.{id}.approval.granted` | `approval.granted` | Human approves | `{ approval_id, decided_by, reason }` |
| `synarch.mission.{id}.approval.denied` | `approval.denied` | Human denies | `{ approval_id, decided_by, reason }` |
| `synarch.mission.{id}.approval.expired` | `approval.expired` | TTL exceeded | `{ approval_id, ttl_seconds }` |

### 6. Review Events

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.review.started` | `review.started` | Janus begins review | `{ sub_task_id, reviewing_agent }` |
| `synarch.mission.{id}.review.approved` | `review.approved` | Janus approves output | `{ sub_task_id, quality_score }` |
| `synarch.mission.{id}.review.rejected` | `review.rejected` | Janus requests revision | `{ sub_task_id, issues, revision_instructions }` |

### 7. Cost Events (FR-47)

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.mission.{id}.cost.logged` | `cost.logged` | After each LLM call | `{ model, provider, prompt_tokens, completion_tokens, cost_usd, latency_ms }` |
| `synarch.mission.{id}.cost.budget_warning` | `cost.budget_warning` | Cost > 80% of budget | `{ current_cost, budget_limit, percentage }` |
| `synarch.mission.{id}.cost.budget_exceeded` | `cost.budget_exceeded` | Cost exceeds budget | `{ current_cost, budget_limit }` |

### 8. System Events

| Subject | Event Type | Trigger | Payload |
|---|---|---|---|
| `synarch.system.health` | `system.health` | Periodic (30s) | `{ services: { postgres, nats, qdrant, redis }, uptime_s }` |
| `synarch.system.error` | `system.error` | Unhandled exception | `{ error, stack_trace, component }` |
| `synarch.system.startup` | `system.startup` | Backend starts | `{ version, config_hash }` |
| `synarch.system.shutdown` | `system.shutdown` | Backend stops | `{ reason, uptime_s }` |

---

## SSE Bridge Mapping

The NATS-to-SSE bridge (FR-76) subscribes to mission-specific subjects and forwards to the SSE endpoint:

```
NATS Subject: synarch.mission.{id}.*
     ↓
SSE Endpoint: GET /api/v1/missions/{id}/events/stream
     ↓
SSE Event Format:
  event: {event_type}
  data: {full_envelope_json}
  id: {event_id}
  retry: 5000
```

### Reconnect Safety

- SSE client sends `Last-Event-ID` header on reconnect
- Bridge replays missed events from NATS JetStream consumer position
- Events are delivered exactly-once per SSE connection

---

## Consumer Groups

| Consumer | Subjects | Purpose | Delivery |
|---|---|---|---|
| `sse-bridge` | `synarch.mission.>` | Real-time dashboard | Push, ack |
| `audit-writer` | `synarch.>` | PostgreSQL audit log | Queue group, ack |
| `cost-aggregator` | `synarch.mission.*.cost.>` | Cost rollup to missions table | Queue group, ack |
| `metrics-collector` | `synarch.>` | Prometheus/metrics | Sampling, no ack |

---

*This event catalog is the single source of truth for all NATS subjects and event payloads. Per-issue work references specific events.*
