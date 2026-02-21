# Synarch Umbrella Event Catalog (Canonical)

Version: 2.0
Date: 2026-02-21
Source of truth: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD

## 1. Scope

Defines canonical event envelope, NATS subject dictionary, payload contracts, consumer roles, and SSE mapping.
No event type/subject/schema change is allowed without updating this catalog.

## 2. Canonical Envelope

```json
{
  "id": "uuid",
  "type": "string",
  "subject": "string",
  "mission_id": "uuid",
  "agent": "string|null",
  "stage": "string|null",
  "timestamp": "ISO-8601 UTC",
  "sequence": 1,
  "schema_version": "1.0",
  "correlation_id": "uuid|null",
  "causation_id": "uuid|null",
  "idempotency_key": "string|null",
  "telemetry": {
    "cost_usd": "number|null",
    "latency_ms": "number|null",
    "tokens": "number|null"
  },
  "payload": {}
}
```

Required:
1. unique `id`
2. monotonic `sequence` per mission
3. immutable event after publish
4. redaction-safe payload content
5. schema version compatibility policy
6. `X-Mission-Id` header must be present for broker-side mission filtering

## 3. Subject Naming Convention

Base routing pattern (bounded cardinality for JetStream):
- `synarch.mission_events.{domain}.{verb}`

*CRITICAL:* Do not place unbounded IDs (`mission_id`, `task_id`, `approval_id`) in the NATS routing subject. IDs are carried in event envelope fields and NATS headers (`X-Mission-Id`, optional `X-Task-Id`, optional `X-Approval-Id`).

Domains:
- mission
- plan
- task
- agent
- tool
- review
- approval
- cost
- eval
- security
- system

## 4. Event Dictionary

### 4.1 Mission Events

1. `synarch.mission_events.mission.created`
- type: `mission.created`
- payload: `{ "goal": "string", "authority_mode": "guided|supervised|free_rein" }`

2. `synarch.mission_events.mission.planned`
- type: `mission.planned`
- payload: `{ "plan": [], "plan_rationale": "string" }`

3. `synarch.mission_events.mission.state_changed`
- type: `mission.state_changed`
- payload: `{ "from": "string", "to": "string", "reason": "string|null" }`

4. `synarch.mission_events.mission.completed`
- type: `mission.completed`
- payload: `{ "summary": "string", "deliverable_ids": [] }`

5. `synarch.mission_events.mission.failed`
- type: `mission.failed`
- payload: `{ "error_code": "string", "message": "string", "recoverable": false }`

6. `synarch.mission_events.mission.cancelled`
- type: `mission.cancelled`
- payload: `{ "actor": "string", "reason": "string|null" }`

### 4.2 Plan Events

1. `synarch.mission_events.plan.created`
- type: `plan.created`
- payload: `{ "tasks": [{"task_id":"uuid","assigned_agent":"string"}] }`

2. `synarch.mission_events.plan.revised`
- type: `plan.revised`
- payload: `{ "revision_count": 1, "changes": [] }`

### 4.3 Task Events

1. `synarch.mission_events.task.created`
- type: `task.created`
- payload: `{ "description": "string", "assigned_agent": "string", "priority": 0 }`

2. `synarch.mission_events.task.started`
- type: `task.started`
- payload: `{ "assigned_agent": "string" }`

3. `synarch.mission_events.task.completed`
- type: `task.completed`
- payload: `{ "result_summary": "string" }`

4. `synarch.mission_events.task.revision_needed`
- type: `task.revision_needed`
- payload: `{ "requested_by": "janus", "feedback": "string" }`

### 4.4 Agent Lifecycle Events

1. `synarch.mission_events.agent.activated`
- type: `agent.activated`
- payload: `{ "task_id": "uuid|null" }`

2. `synarch.mission_events.agent.thinking`
- type: `agent.thinking`
- payload: `{ "thought_summary": "string", "redaction_level": "none|partial|strict" }`

3. `synarch.mission_events.agent.delegated`
- type: `agent.delegated`
- payload: `{ "to": "string", "task_id": "uuid", "intent": "string" }`

4. `synarch.mission_events.agent.result`
- type: `agent.result`
- payload: `{ "task_id": "uuid|null", "result_ref": "string|uuid" }`

5. `synarch.mission_events.agent.error`
- type: `agent.error`
- payload: `{ "code": "string", "message": "string", "recoverable": true }`

6. `synarch.mission_events.agent.deactivated`
- type: `agent.deactivated`
- payload: `{ "duration_ms": 0 }`

### 4.5 Tool Events

1. `synarch.mission_events.tool.call`
- type: `tool.call`
- payload: `{ "tool": "string", "arguments": {}, "risk": "low|medium|high|critical" }`

2. `synarch.mission_events.tool.result`
- type: `tool.result`
- payload: `{ "tool": "string", "ok": true, "summary": "string" }`

3. `synarch.mission_events.tool.error`
- type: `tool.error`
- payload: `{ "tool": "string", "error": "string" }`

### 4.6 Review Events

1. `synarch.mission_events.review.started`
- type: `review.started`
- payload: `{ "reviewer": "janus", "target": "task|deliverable" }`

2. `synarch.mission_events.review.approved`
- type: `review.approved`
- payload: `{ "quality_score": 0.0, "notes": "string" }`

3. `synarch.mission_events.review.rejected`
- type: `review.rejected`
- payload: `{ "issues": [], "revision_instructions": "string" }`

### 4.7 Approval Events

1. `synarch.mission_events.approval.requested`
- type: `approval.requested`
- payload: `{ "action_type": "string", "risk_level": "high", "requested_by": "agent" }`

2. `synarch.mission_events.approval.approved`
- type: `approval.approved`
- payload: `{ "actor": {"id":"string","session":"string","device":"string"}, "reason": "string|null" }`

3. `synarch.mission_events.approval.rejected`
- type: `approval.rejected`
- payload: `{ "actor": {"id":"string","session":"string","device":"string"}, "reason": "string|null" }`

4. `synarch.mission_events.approval.timeout`
- type: `approval.timeout`
- payload: `{ "timeout_seconds": 300 }`

### 4.8 Cost Events

1. `synarch.mission_events.cost.logged`
- type: `cost.logged`
- payload: `{ "model": "string", "provider": "string", "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0, "latency_ms": 0 }`

2. `synarch.mission_events.cost.budget_warning`
- type: `cost.budget_warning`
- payload: `{ "current_cost": 0, "budget_limit": 0, "percentage": 80 }`

3. `synarch.mission_events.cost.budget_exceeded`
- type: `cost.budget_exceeded`
- payload: `{ "current_cost": 0, "budget_limit": 0 }`

### 4.9 System Events

1. `synarch.mission_events.system.retry`
- type: `system.retry`
- payload: `{ "component": "string", "attempt": 1, "max_attempts": 3 }`

2. `synarch.mission_events.system.guardrail_blocked`
- type: `system.guardrail_blocked`
- payload: `{ "policy": "string", "tool": "string", "reason": "string" }`

3. `synarch.mission_events.system.replay_started`
- type: `system.replay_started`
- payload: `{ "from_sequence": 0 }`

4. `synarch.mission_events.system.replay_completed`
- type: `system.replay_completed`
- payload: `{ "to_sequence": 0, "status": "ok|failed" }`

### 4.10 Eval and Security Events

1. `synarch.mission_events.eval.score_recorded`
- type: `eval.score_recorded`
- payload: `{ "dimension": "quality|safety|correctness|cost_efficiency", "score": 0.0, "judge_model": "string" }`

2. `synarch.mission_events.security.violation`
- type: `security.violation`
- payload: `{ "policy": "string", "severity": "low|medium|high|critical", "action": "blocked|sandboxed|escalated" }`

3. `synarch.mission_events.security.injection_detected`
- type: `security.injection_detected`
- payload: `{ "source": "prompt|tool_input|integration", "mitigation": "redact|reject|isolate" }`

## 5. SSE Mapping

SSE endpoint:
- `GET /api/v1/mission/{mission_id}/stream`

Mapping rules:
1. REST/SSE bridge proxy connects to NATS, filters on `X-Mission-Id` header.
2. forward each event as:
```text
id: <event.id>
event: mission_event
data: {<canonical envelope JSON>}

```
3. support `Last-Event-ID` resume path
4. if `Last-Event-ID` cannot be replayed from retained history, return `409 REPLAY_GAP`
5. if mission history retention has expired, return `410 STREAM_HISTORY_EXPIRED`

## 6. Consumer Roles

1. `sse-bridge`: mission stream fanout
2. `audit-writer`: persist event journal to PostgreSQL
3. `cost-aggregator`: mission cost rollups
4. `metrics-collector`: SLO and platform metrics
5. `eval-pipeline`: judge scoring and regression artifacts
6. `security-monitor`: policy violations and incident correlation

## 7. Versioning and Compatibility

1. additive optional fields: non-breaking
2. rename/remove/type changes: breaking and requires schema version bump
3. subject rename: breaking and requires migration/dual-publish window

## 8. Governance

Any event-plane change must include:
1. subject diff
2. payload diff
3. version decision
4. replay/SSE compatibility tests

## 9. FR Linkage

Primary FR coverage:
- FR-13, FR-16, FR-17, FR-18, FR-19, FR-20
- FR-45, FR-46, FR-47, FR-49
- FR-54, FR-55, FR-76, FR-86
