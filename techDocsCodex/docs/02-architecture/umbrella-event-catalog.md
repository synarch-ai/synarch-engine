# Synarch Umbrella Event Catalog (NATS + SSE)

Status: Authoritative Level-1 Master Doc (Create Once)
Source baseline: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD (v1.2)
Last updated: 2026-02-21

## 1. Scope

Defines canonical event envelope, NATS subject taxonomy, payload contracts, and SSE mapping.
No new event type or subject may be introduced without updating this document.

## 2. Canonical Event Envelope

All emitted events must satisfy:

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
  "payload": {}
}
```

Required rules:
1. `id` unique globally.
2. `sequence` monotonic per mission.
3. `schema_version` required for forward compatibility.
4. payloads must be secret-safe/redacted.
5. event records are immutable after publish.

## 3. Subject Taxonomy

Root namespace:
- `synarch.mission.{mission_id}.*`

Domains:
- mission
- agent
- task
- deliverable
- approval
- system

## 4. Mission Lifecycle Subjects

1. `synarch.mission.{mission_id}.created`
- payload: `{ "goal": "string", "authority_mode": "string" }`

2. `synarch.mission.{mission_id}.planned`
- payload: `{ "plan": [], "plan_rationale": "string" }`

3. `synarch.mission.{mission_id}.state_changed`
- payload: `{ "from": "string", "to": "string", "reason": "string|null" }`

4. `synarch.mission.{mission_id}.completed`
- payload: `{ "summary": "string", "deliverable_ids": [] }`

5. `synarch.mission.{mission_id}.failed`
- payload: `{ "error_code": "string", "message": "string", "recoverable": false }`

6. `synarch.mission.{mission_id}.cancelled`
- payload: `{ "actor": "string", "reason": "string|null" }`

## 5. Agent Subjects

Pattern:
- `synarch.mission.{mission_id}.agent.{agent_name}.{verb}`

Verbs and payload contracts:
1. `activated`
- `{ "task_id": "uuid|null" }`
2. `thinking`
- `{ "thought": "string" }`
3. `delegated`
- `{ "to": "agent_name", "task_id": "uuid", "intent": "string" }`
4. `tool_call`
- `{ "tool": "string", "arguments": {}, "risk": "low|medium|high|critical" }`
5. `tool_result`
- `{ "tool": "string", "ok": true, "summary": "string" }`
6. `result`
- `{ "task_id": "uuid|null", "result_ref": "string|uuid" }`
7. `error`
- `{ "code": "string", "message": "string", "recoverable": true }`
8. `deactivated`
- `{ "duration_ms": 1234 }`

## 6. Task Subjects

Pattern:
- `synarch.mission.{mission_id}.task.{task_id}.{verb}`

Verbs:
1. `created`
- `{ "description": "string", "assigned_agent": "string", "priority": 0 }`
2. `started`
- `{ "assigned_agent": "string" }`
3. `completed`
- `{ "result_summary": "string" }`
4. `revision_needed`
- `{ "requested_by": "janus", "feedback": "string" }`

## 7. Deliverable Subjects

Pattern:
- `synarch.mission.{mission_id}.deliverable.{deliverable_id}.{verb}`

Verbs:
1. `created`
- `{ "task_id": "uuid|null", "type": "string", "agent": "string" }`
2. `reviewed`
- `{ "review_status": "pass|revise|fail", "reviewer": "janus" }`
3. `accepted`
- `{ "accepted_by": "synarch|god", "provenance_refs": [] }`

## 8. Approval Subjects

Pattern:
- `synarch.mission.{mission_id}.approval.{approval_id}.{verb}`

Verbs:
1. `requested`
- `{ "action_type": "string", "risk_level": "high", "requested_by": "agent" }`
2. `approved`
- `{ "actor": {"id":"string","session":"string","device":"string"}, "reason": "string|null" }`
3. `rejected`
- `{ "actor": {"id":"string","session":"string","device":"string"}, "reason": "string|null" }`
4. `timeout`
- `{ "timeout_seconds": 300 }`

## 9. System Subjects

1. `synarch.mission.{mission_id}.system.retry`
- `{ "component": "string", "attempt": 2, "max_attempts": 3 }`

2. `synarch.mission.{mission_id}.system.guardrail_blocked`
- `{ "policy": "string", "tool": "string", "reason": "string" }`

3. `synarch.mission.{mission_id}.system.replay_started`
- `{ "from_sequence": 100 }`

4. `synarch.mission.{mission_id}.system.replay_completed`
- `{ "to_sequence": 220, "status": "ok|failed" }`

## 10. SSE Mapping Rules

1. Gateway subscribes to `synarch.mission.{mission_id}.>`.
2. Each NATS event is forwarded as SSE `event: mission_event` with canonical envelope as `data`.
3. SSE `id` must be set to event `id`.
4. reconnect with `Last-Event-ID` must attempt resume via event store.

## 11. Versioning Policy

1. New optional fields: allowed with schema version unchanged.
2. Field rename/removal/type change: breaking; bump schema version.
3. Subject rename: breaking; provide transition period and dual-publish policy.

## 12. Ralph Delta Protocol

Each issue mini-spec must declare:
- new/changed event types
- new/changed subjects
- payload delta
- version bump decision
- back-compat strategy
- stream/replay test updates
