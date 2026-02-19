# Product Requirements Document: Synarch Engine v1.0 (Codex)

**File:** `prd-1.0-codex`  
**Developer:** PraxLannister  
**Version:** 1.0  
**Status:** Draft for execution  
**Date:** 2026-02-19

---

## 1. Executive Summary

Synarch Engine is a hierarchical multi-agent execution platform where a human operator (God) issues a mission, Synarch (CEO agent) decomposes and governs execution, and specialist agents deliver artifacts through a durable, observable, and controllable runtime.

The v1.0 product goal is to convert the current architecture skeleton into a reliable operational system with:
1. Durable mission state and recovery.
2. Non-linear orchestration with HITL approvals.
3. Production-grade agent runtime (`litellm` + NATS events).
4. Real Mission Control cockpit (not static page).
5. Strict V3 brand-system implementation.

This PRD defines product behavior, requirements, acceptance criteria, and rollout for shipping v1.0.

---

## 2. Problem Statement

Current state has strong architecture direction but high-impact execution gaps:
1. Mission state is in-memory mock only.
2. Orchestration is linear and lacks interruptible governance paths.
3. Agent runtime is placeholder and does not emit production event contracts.
4. Mission Control UI is static and not operational.
5. Brand identity exists in docs but is not implemented in the UI system.

Without closing these gaps, Synarch cannot provide mission reliability, operator trust, or production-grade control.

---

## 3. Product Vision

Deliver an agent operating cockpit where:
1. Every mission is observable in real time.
2. Every sensitive action can be gated by operator approval.
3. Every result is traceable to nodes, tools, and events.
4. Every mission can survive failure and resume deterministically.
5. The UI expresses a clear Synarch identity rather than generic dashboard aesthetics.

---

## 4. Objectives

### 4.1 Primary Objectives (v1.0)

1. Durable orchestration: no mission-critical state lost on restart.
2. Governance-first runtime: conditional routing + HITL interrupt/resume.
3. Event-native operation: all runtime activity emitted as structured events.
4. Operational UI: Mission Control supports start/monitor/approve/review loops.
5. Brand fidelity: V3 tokens/components implemented and enforced.

### 4.2 Non-Goals (v1.0)

1. Full autonomous self-improving agent loops.
2. Runtime migration away from LangGraph.
3. Generic plugin marketplace.
4. Broad cloud-native multi-region deployment.
5. Replacing all reference patterns with third-party frameworks.

---

## 5. Users and Personas

### 5.1 God (Primary Operator)

Responsibilities:
1. Submit mission goals.
2. Set execution mode and constraints.
3. Review approvals and intervene when needed.
4. Inspect progress, evidence, and deliverables.

Needs:
1. Fast situational awareness.
2. Deterministic control over sensitive actions.
3. Clear provenance and recoverability.

### 5.2 Platform Developer (Secondary)

Responsibilities:
1. Implement and evolve orchestration/runtime.
2. Add tools/integrations safely.
3. Validate performance and reliability.

Needs:
1. Typed event contracts.
2. Clear runtime boundaries.
3. Strong observability and traceability.

---

## 6. Success Metrics

### 6.1 Product Metrics

1. Mission recovery success rate after restart: >= 95%.
2. Approval-loop completion rate (request -> decision -> resume): >= 99%.
3. Mission event stream render fidelity (backend vs UI): >= 99.5% event parity.
4. Deliverable provenance coverage: 100% of final outputs linked to source events/tasks.
5. Brand token compliance in Mission Control components: 100%.

### 6.2 Engineering Metrics

1. Mission start-to-first-event latency: <= 1.5s p95.
2. Event propagation backend-to-UI latency: <= 300ms p95.
3. Unhandled runtime errors per mission: < 1% of runs.
4. Idempotent side-effect replays blocked when key duplicates: 100%.

---

## 7. Scope

### 7.1 In Scope

1. Mission lifecycle APIs and runtime wiring.
2. LangGraph orchestration with conditional routing.
3. PostgreSQL checkpointing and mission persistence.
4. NATS structured event publishing.
5. HITL approvals with pause/resume.
6. Mission Control cockpit UI with live streaming.
7. V3 brand token/component system implementation.

### 7.2 Out of Scope

1. Full long-term memory productization beyond foundational model.
2. Extensive external marketplace integrations.
3. Multi-tenant enterprise admin suite.
4. Mobile-native client app.
5. Cross-region failover architecture.

---

## 8. Product Principles

1. Governed autonomy over unrestricted autonomy.
2. Durable by default over fast-but-ephemeral execution.
3. Explicit contracts over implicit coupling.
4. Traceability over black-box convenience.
5. Identity-first interface over generic UI templates.

---

## 9. Functional Requirements

## 9.1 Mission Intake and Lifecycle

FR-1: Operator can create a mission with goal, mode, and optional constraints.  
FR-2: Mission receives unique ID and durable thread/checkpoint context.  
FR-3: Mission status states include at minimum: `created`, `running`, `awaiting_approval`, `paused`, `failed`, `completed`, `cancelled`.  
FR-4: Mission state can be queried at any time via API.  
FR-5: Mission can be resumed from persisted state after service restart.

### 9.2 Orchestration (LangGraph)

FR-6: Runtime must use LangGraph StateGraph as orchestration core.  
FR-7: Graph must support conditional branches based on mission state.  
FR-8: Graph must support interrupt/resume semantics for approvals.  
FR-9: Graph must include validation nodes for pre-execution policy checks.  
FR-10: Graph execution checkpoints must persist to PostgreSQL.

### 9.3 Agent Runtime

FR-11: All model calls must route through `litellm`.  
FR-12: Agent system prompts must load from `docs/agents/*/soul.md`.  
FR-13: Agent runtime must emit structured lifecycle events (`start`, `progress`, `result`, `error`).  
FR-14: Side-effecting tool calls must support idempotency keys.  
FR-15: Runtime must record retry metadata for retried operations.

### 9.4 Event Bus and Streaming

FR-16: NATS is required for runtime event publication.  
FR-17: Event subjects must include mission/agent/task/deliverable domains.  
FR-18: FastAPI SSE endpoint must stream events to Mission Control in near real time.  
FR-19: Event payloads must be typed and versioned.  
FR-20: Events must include mission ID, timestamp, stage, and source actor/node.

### 9.5 HITL and Approval Controls

FR-21: Sensitive operations must create explicit approval requests.  
FR-22: Operator can approve/reject with reason.  
FR-23: Runtime must pause awaiting decision and resume deterministically on decision.  
FR-24: Approval outcomes must be persisted and visible in mission history.  
FR-25: Approval timeout policy must be configurable.

### 9.6 Mission Control UI

FR-26: Mission Control must display live mission phase and status.  
FR-27: UI must render typed event stream with category filters.  
FR-28: UI must provide approval queue actions.  
FR-29: UI must display deliberation timeline (draft/challenge/synthesis style progression).  
FR-30: UI must display tasks, blockers, and deliverables.  
FR-31: UI must support mission start and mission inspect flows.  
FR-32: UI must show execution mode and current graph branch.

### 9.7 Brand System Enforcement

FR-33: V3 design tokens must exist as source-of-truth CSS/custom properties.  
FR-34: Mission Control components must use V3 primitives (void/plate/border/amber language).  
FR-35: Sharp-radius and border-first rules must be enforced in component styles.  
FR-36: Brand compliance checklist must gate PR acceptance for UI changes.

### 9.8 Integrations and Tooling Boundaries

FR-37: Browser specialist tools must follow deterministic Playwright-MCP pattern.  
FR-38: Integration execution must be scoped by actor/user/org context.  
FR-39: Trigger-style external events must be routeable into mission workflows.  
FR-40: MCP tool development loop must support inspect/debug workflow.

### 9.9 Security and Governance

FR-41: Gateway auth model must support explicit mode configuration and proxy-safe behavior.  
FR-42: Control-plane actions must be audit-attributed (actor/device/session).  
FR-43: Unsafe/irreversible operations must be blocked without explicit approval.  
FR-44: Secrets must never be emitted in event streams or UI logs.

---

## 10. Non-Functional Requirements

NFR-1 Reliability: Mission durability across restart with no in-memory-only source of truth.  
NFR-2 Performance: SSE and event rendering latency targets as defined in Section 6.  
NFR-3 Observability: Structured logs, traces, and event IDs for all mission-critical actions.  
NFR-4 Maintainability: Runtime boundaries (orchestrator, runtime, event bus, UI) must stay decoupled.  
NFR-5 Security: Auth, approval, and idempotency controls must be test-covered.

---

## 11. Information Architecture (Mission Control)

### 11.1 Desktop Layout

1. Left rail: missions list, current phase, mode, health.
2. Center: deliberation timeline + thought stream + active task context.
3. Right rail: approvals queue, integration scope, deliverables summary.
4. Bottom strip: transport controls and runtime diagnostics.

### 11.2 Mobile Layout

Priority stack:
1. Phase and approvals.
2. Current task and blockers.
3. Deliverables.
4. Recent events.

---

## 12. Data and Event Contract Requirements

## 12.1 Core Entities

1. Mission
- id
- status
- mode
- created_at
- updated_at
- current_phase
- checkpoint_thread_id

2. Task
- id
- mission_id
- parent_task_id
- assigned_agent
- status
- priority
- inputs
- outputs

3. Deliverable
- id
- mission_id
- producer_agent
- type
- content_ref
- provenance_refs[]

4. Approval
- id
- mission_id
- action_type
- requested_by
- status
- decided_by
- decision_reason
- decided_at

5. Event
- event_id
- mission_id
- domain (`mission|agent|task|deliverable|approval|system`)
- type
- source
- timestamp
- payload
- schema_version

### 12.2 Event Semantics

1. Events are append-only.
2. Events are immutable once published.
3. Event IDs are unique and traceable across backend and UI.
4. Event payloads must be redaction-safe for UI display.

---

## 13. API Requirements (v1.0)

### 13.1 Required Endpoints

1. `POST /mission` create mission.
2. `GET /mission/{id}` retrieve mission state.
3. `GET /mission/{id}/stream` SSE event stream.
4. `POST /mission/{id}/approval/{approval_id}/approve`.
5. `POST /mission/{id}/approval/{approval_id}/reject`.
6. `POST /mission/{id}/pause` and `POST /mission/{id}/resume`.

### 13.2 API Contract Rules

1. All responses include stable error shapes.
2. Side-effecting endpoints support idempotency key headers.
3. Approval endpoints are auditable and authenticated.
4. Mission stream supports reconnect semantics from last event ID.

---

## 14. Reference Adoption Requirements (Governed)

The following are mandatory adoption targets for v1.0 behavior:

1. LangGraph: Postgres checkpointer, interrupts, conditional routing.
2. OpenClaw patterns: control-plane idempotency, auth rigor, approval lifecycle discipline.
3. CrewAI patterns: event taxonomy/listener style.
4. Letta patterns: memory block and run-step completion semantics.
5. LLM Council Plus patterns: staged deliberation UX and mode visibility.
6. Playwright-MCP: deterministic browser specialist tooling.
7. MCP-Use patterns: session management and inspector development loop.
8. Smolagents patterns: secure code execution policy + telemetry shape.
9. Magentic-UI patterns: co-planning and guarded action UX.
10. Composio patterns: user/org scoped integration routing.

References and deep dives:
- `docs/04-reference-deep-dives/README.md`
- `docs/02-architecture/reference-adoption-matrix.md`

---

## 15. Rollout Plan

### Milestone A: Runtime Foundation

Scope:
1. Durable mission state.
2. LangGraph checkpoint integration.
3. Base event schema and NATS publishing.

Exit criteria:
1. Restart-resume test passes.
2. Mission emits typed events end to end.

### Milestone B: Governed Orchestration

Scope:
1. Conditional routing.
2. HITL interrupt/resume.
3. Idempotency contract for side effects.

Exit criteria:
1. Approval flow fully functional with persistence.
2. Duplicate side-effect requests deduped.

### Milestone C: Mission Control Cockpit

Scope:
1. Live event stream UI.
2. Approval queue.
3. Deliberation timeline.
4. Task and deliverable surfaces.

Exit criteria:
1. Operator can run mission from UI start to completion.
2. Stage transitions and provenance visible.

### Milestone D: Brand and Hardening

Scope:
1. V3 token/component enforcement.
2. Security and observability hardening.
3. Final acceptance and doc updates.

Exit criteria:
1. Brand compliance checklist passes.
2. Governance docs/memory-bank synced.

---

## 16. Testing and Validation Strategy

### 16.1 Test Layers

1. Unit tests:
- state transitions
- approval state machine
- event schema serialization
- idempotency handler

2. Integration tests:
- mission create -> run -> approval -> resume -> complete
- backend restart during active mission and successful resume
- SSE event ordering and reconnect behavior

3. UI tests:
- live event rendering
- approval action workflows
- mission phase transitions

4. Contract tests:
- API error envelope shape
- event schema version compatibility

### 16.2 Acceptance Test Scenarios

1. Happy path mission completes with visible provenance.
2. Sensitive action path pauses and resumes after operator decision.
3. Duplicate idempotency key does not duplicate side effect.
4. Crash/restart recovery preserves mission continuity.

---

## 17. Risks and Mitigations

1. Risk: State drift between graph and persistence.
- Mitigation: checkpoint-at-phase-boundary policy + state reconciliation test.

2. Risk: Event flood causes UI lag.
- Mitigation: event batching/throttled rendering + severity filters.

3. Risk: Approval UX bottlenecks operator throughput.
- Mitigation: priority queueing and SLA visibility in approval panel.

4. Risk: Brand drift over time.
- Mitigation: token lint/checklist in PR process and design review gates.

5. Risk: Reference adoption drift.
- Mitigation: mandatory matrix/deep-dive/progress updates in architecture PRs.

---

## 18. Dependencies

1. Core services: PostgreSQL, NATS, Qdrant, Ollama (as configured).
2. Runtime libraries: LangGraph, FastAPI, `litellm`.
3. Frontend stack: Next.js app shell and Mission Control components.
4. Governance docs:
- `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md`
- `docs/02-architecture/reference-adoption-matrix.md`
- `docs/03-product/mission-control-ui-ux-and-functionality-strategy.md`

---

## 19. Definition of Done (v1.0)

v1.0 is complete only when all are true:

1. W1-W5 workstreams from ADR-004 are implemented and verified.
2. Mission recovery after restart is proven by automated test.
3. HITL approval interrupt/resume is live and audited.
4. Agent runtime uses `litellm` and publishes structured NATS events.
5. Mission Control is operational and real-time.
6. V3 brand tokens/components are fully integrated in Mission Control.
7. Reference adoption matrix reflects implemented patterns with evidence.
8. Memory-bank progress and active context are updated.

---

## 20. Open Questions (To Resolve Before Final Freeze)

1. Which execution modes are mandatory at launch (`guided`, `supervised`, `free_rein`) versus deferred?
2. What is the default approval timeout and fallback behavior on timeout?
3. What mission retention period is required for persisted checkpoints/events?
4. Which actions are classified as "sensitive" in v1.0 policy baseline?
5. What minimum provenance depth is required in deliverables for compliance?

---

## 21. Source Index

1. `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md`
2. `docs/02-architecture/reference-adoption-matrix.md`
3. `docs/03-product/mission-control-ui-ux-and-functionality-strategy.md`
4. `docs/04-reference-deep-dives/README.md`
5. `docs/04-reference-deep-dives/openclaw/README.md`
6. `docs/04-reference-deep-dives/langgraph/README.md`

