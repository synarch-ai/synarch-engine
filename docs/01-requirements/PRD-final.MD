# Synarch Engine Product Requirements Document v1.2

**Status:** Canonical Baseline  
**Date:** 2026-02-21  
**Authors:** Claude (Cline) + Codex + Antigravity  
**Owner:** Praxlannister  
**Supersedes:** `docs/01-requirements/poc-prd.md`, `docs/01-requirements/prd-1.0-claude.md`, `docs/01-requirements/prd-1.0-codex.md`, `docs/01-requirements/prd-1.0-final.md`

---

## Table of Contents

1. Executive Summary
2. Product Vision and Principles
3. Personas and Primary Journeys
4. Scope and Non-Scope
5. Objectives and Success Metrics
6. System Architecture
7. Agent Organization
8. Mission Lifecycle and State Model
9. Persistence and Memory Model
10. Orchestration Requirements
11. Eventing and Streaming Requirements
12. Model, Tool, and Cost Routing
13. API and Idempotency Contracts
14. Mission Control Requirements
15. HITL and Autonomy Requirements
16. Security and Governance Requirements
17. Evaluation, Testing, and Quality Gates
18. Observability, Replay, and SLOs
19. Integrations and Protocol Strategy
20. Infrastructure and Deployment Requirements
21. Non-Functional Requirements Index
22. Functional Requirements Index (FR-1 to FR-86)
23. Canonical Roadmap (A -> B -> C)
24. Risk Register
25. Definition of Done
26. Open Questions
27. Source and Traceability
28. Approval and Revision History

---

## 1. Executive Summary

Synarch is an autonomous multi-agent operating system with strict governance. The product objective is to let a human operator (“God”) define mission goals while a hierarchy of agents decomposes, executes, validates, and delivers results with full observability, safety controls, and recovery guarantees.

The v1.2 baseline priorities are:
1. Close runtime gaps (durability, real orchestration execution, event streaming, approval persistence).
2. Enforce production safety (idempotency, auth modes, audit attribution, secure execution boundaries).
3. Establish measurable quality (evaluation framework, regression gates, cost and latency telemetry).
4. Build interoperability and extensibility (MCP, protocol contracts, configurable agent definitions).

Synarch’s strategic direction is staged:
- **A: Hardening-first** (trustworthy runtime)
- **B: Protocol-first** (ecosystem interoperability)
- **C: Visionary-first** (2027 differentiators)

---

## 2. Product Vision and Principles

### 2.1 Vision

Build the most trusted open-source control plane for autonomous agent teams, capable of startup velocity and enterprise governance.

### 2.2 Principles

1. Governance over raw autonomy.
2. Durable state over in-memory convenience.
3. Typed contracts over implicit behavior.
4. Measured quality over subjective output acceptance.
5. Secure-by-default execution and integration boundaries.
6. Protocol interoperability over proprietary lock-in.

---

## 3. Personas and Primary Journeys

### 3.1 Personas

1. **Solo Builder (Primary):** wants autonomous execution with clear visibility and low ops burden.
2. **Startup Operator (Primary):** wants cost-aware throughput and rapid mission iteration.
3. **Platform Engineer (Secondary):** wants stable contracts, replayability, and operability.
4. **Enterprise Architect (Secondary):** wants policy, audit, tenancy, and compliance controls.

### 3.2 Primary Journeys

1. Submit mission -> monitor live -> receive deliverables with provenance.
2. Review/approve sensitive operations without losing mission flow.
3. Recover mission after restart without manual repair.
4. Audit mission timeline and decisions after completion.
5. Adjust agent behavior by configuration, not hardcoded rewrites.

---

## 4. Scope and Non-Scope

### 4.1 In Scope (v1.2 Baseline)

1. Six core agents (Synarch, Zeus, Thoth, Hermes, Hephaestus, Janus) plus God.
2. LangGraph orchestration with PostgreSQL durability.
3. NATS event bus and SSE Mission Control stream.
4. litellm model routing with cost telemetry hooks.
5. HITL approvals with deterministic pause/resume behavior.
6. Security baseline (auth mode configuration, idempotency, audit attribution, secrets discipline).
7. Evaluation baseline (contract, integration, and regression tests).

### 4.2 Planned (phased)

1. MCP/A2A protocol surfaces.
2. Config-driven agents and AgentTool composition.
3. Memory compaction and anti-context-rot policies.
4. Sandbox-first untrusted code execution.
5. Replay/time-travel debugging and advanced SLO alerting.

### 4.3 Out of Scope (immediate release)

1. Fully autonomous self-modifying production runtime without governance gates.
2. Multi-region distributed scheduler and global quota balancing.
3. On-by-default crypto settlement for compute auctions.

---

## 5. Objectives and Success Metrics

### 5.1 Product Objectives

1. Mission durability across process restarts.
2. Sub-second mission event visibility in Mission Control.
3. Deterministic HITL flow for sensitive actions.
4. Measurable cost/quality/safety per mission.
5. Production-safe integration and execution boundaries.

### 5.2 Success Metrics

| Metric | Target | Notes |
|---|---:|---|
| Mission recovery success rate | >= 95% | Recovery from restart at last checkpoint |
| Event latency backend->UI (p95) | <= 300 ms | NATS to SSE to UI |
| Approval lifecycle completion | >= 99% | No dangling approval state |
| Duplicate side-effect prevention | 100% | Idempotency key enforcement |
| Mission cost telemetry coverage | 100% | token + latency + cost events |
| Critical-path test pass rate | 100% | Required for merge |

---

## 6. System Architecture

### 6.1 Core Components

1. **Gateway:** FastAPI routes, validation, idempotency, auth policy entry.
2. **Orchestrator:** LangGraph StateGraph with conditional routing and interrupts.
3. **Event Plane:** NATS/JetStream for typed mission and runtime events.
4. **Persistence Plane:** PostgreSQL for mission metadata, approvals, events, checkpoints.
5. **Model Plane:** litellm abstraction over local and managed models.
6. **Mission Control:** Next.js UI for live mission operations and approvals.

### 6.2 Architectural Constraints

1. Control-plane state and observation-plane events must remain separable.
2. No mission-critical logic may depend on transient process memory.
3. Every side effect must have traceable identity and idempotency semantics.

---

## 7. Agent Organization

### 7.1 Hierarchy

- Tier 0: God (human authority)
- Tier 1: Synarch (orchestrator)
- Tier 2: Zeus (engineering), Thoth (research)
- Tier 3: Hephaestus (builder), Hermes (research execution), Janus (review)

### 7.2 Governance Rules

1. No skip-level communication in default flow.
2. All user intent enters via Synarch path.
3. Sensitive tools require approval or sandbox policy checks.
4. Agent identity and role contracts are loaded from soul/config definitions.

---

## 8. Mission Lifecycle and State Model

### 8.1 Mission States

`created -> planning -> executing -> awaiting_approval -> reviewing -> revising -> synthesizing -> completed`  
Alternative terminal paths: `failed`, `cancelled`, `paused`.

### 8.2 Lifecycle Guarantees

1. State transitions are explicit and event-emitting.
2. Approvals create durable records before pause.
3. Resume path is deterministic from persisted state and checkpoint.

---

## 9. Persistence and Memory Model

### 9.1 Storage Layers

1. **PostgreSQL:** missions, tasks, approvals, deliverables, mission events, replay metadata.
2. **LangGraph checkpoint tables:** thread-based graph recovery.
3. **Vector memory (phase-controlled):** semantic recall and long-horizon context support.

### 9.2 Memory Policies

1. Fact extraction writes only validated memory entries.
2. Memory lifecycle supports create/update/TTL/archive/delete.
3. Memory compaction reduces stale context pressure.
4. Read-only policy blocks exist for invariant system memory.

### 9.3 Required Durability Rules

1. No `_in_memory` mission source of truth in production path.
2. Approval and mission state must survive restart.
3. Replay metadata must be preserved for debugging.

---

## 10. Orchestration Requirements

### 10.1 Graph Capabilities

1. StateGraph as orchestration core.
2. Conditional branch routing by mission state.
3. Interrupt/resume support for HITL actions.
4. Validation/policy nodes before side effects.
5. Review loop with revision bounds.

### 10.2 AgentTool and Dynamic Selection

1. Agent can expose callable capability as a tool abstraction.
2. Tool selection is contextual and budget-aware.
3. Routing chooses execution strategy by task class and mission constraints.

---

## 11. Eventing and Streaming Requirements

### 11.1 Event Contract

All runtime messages conform to typed envelope with:
- event id
- event type
- mission id
- actor/agent
- timestamp
- schema version
- sequence
- optional idempotency key
- payload

### 11.2 Subject Taxonomy

Mission, agent, task, deliverable, and approval domains are required.

### 11.3 SSE Bridge Behavior

1. Mission stream is generated from durable event flow, not placeholders.
2. Reconnect semantics include `Last-Event-ID` compatibility.
3. Keepalive behavior must not hide upstream event failures.

---

## 12. Model, Tool, and Cost Routing

### 12.1 Routing Model

1. Static base mapping by agent role.
2. Dynamic override by mission complexity, latency target, and cost budget.
3. Degradation policy when budget threshold is reached.

### 12.2 Cost Tracking

1. Token usage per model call.
2. Latency and error rate by agent and model.
3. Mission-level aggregate cost with threshold alerts.

---

## 13. API and Idempotency Contracts

### 13.1 Required Endpoints

1. Mission start, state, list, stream, pause/resume/cancel.
2. Approval decision endpoints.
3. Agent list and soul/config inspection endpoints.
4. Health endpoint with dependency surface.

### 13.2 Idempotency Rules

1. All side-effecting POST endpoints require idempotency handling.
2. Same key + same payload -> replay prior result.
3. Same key + different payload -> conflict error.
4. TTL and storage rules for idempotency records are mandatory.

---

## 14. Mission Control Requirements

### 14.1 Functional UI Requirements

1. Live mission phase/status.
2. Typed event timeline with filtering.
3. Approval inbox and decision actions.
4. Task board and deliverable panel with provenance.
5. Execution mode and branch visibility.

### 14.2 Build and Quality Gates

1. Root layout and production build validity.
2. Lint and type-check pass required.
3. Basic UI smoke tests for mission start and stream render.

### 14.3 Design System

1. Design tokens are source of truth.
2. Border-first and sharp-radius rules enforced.
3. PR gate requires brand compliance evidence.

---

## 15. HITL and Autonomy Requirements

### 15.1 Approval Lifecycle

1. Request emitted and persisted before runtime pause.
2. Decision updates state with actor, reason, and timestamp.
3. Runtime resumes deterministically with decision context.
4. Timeout policy is configurable and deterministic.

### 15.2 Autonomy Gradient

1. Modes: guided, supervised, free_rein.
2. Confidence score per decision and action class.
3. Progressive trust metrics can increase autonomy thresholds.
4. Graceful handoff bundles full context when escalating to human.

---

## 16. Security and Governance Requirements

### 16.1 Control Matrix

| Area | Requirement | Acceptance Signal |
|---|---|---|
| Auth mode enforcement | Explicit auth modes and policy checks at gateway | Unauthorized paths rejected with typed errors |
| Least privilege | Per-agent permission profile for tools/data | Forbidden tool invocation blocked and logged |
| Tool guardrails | Input/output validators wrap risky tools | Guardrail reject path covered by tests |
| Prompt injection defense | Canary markers + untrusted input scanning path | Injection test corpus yields deterministic mitigation |
| Forensic audit | Correlation IDs across mission + API + events | End-to-end trace reconstruction possible |
| Supply chain | Integration dependency and provenance checks | Third-party connector policy report exists |
| Secure execution | Sandbox contract for untrusted generated code | Host escape tests fail-safe |
| Secrets discipline | Redaction in logs/events/UI | Secret scanner passes on artifacts |

### 16.2 Security Policy Rules

1. Unsafe actions must be approval-gated or sandbox-constrained.
2. No secret may be emitted to event stream payloads.
3. All privileged actions require actor attribution.

---

## 17. Evaluation, Testing, and Quality Gates

### 17.1 Evaluation Framework

1. Unit, integration, and end-to-end mission evals.
2. LLM-as-judge scoring for output quality dimensions.
3. Golden dataset + production sample set management.
4. Regression suite enforced in CI for prompt/runtime changes.

### 17.2 Test Gate Policy

1. Contract tests for API shape and idempotency behavior.
2. Orchestrator tests for branching and resume semantics.
3. Approval state machine tests.
4. Mission recovery tests from checkpoints.
5. Merge blocked unless critical-path tests pass.

---

## 18. Observability, Replay, and SLOs

### 18.1 Telemetry Requirements

1. Structured logs with mission correlation fields.
2. Metric dimensions: quality, cost, latency, safety.
3. Event parity checks between backend and Mission Control view.

### 18.2 Replay and Time-Travel

1. Replay mission from persisted checkpoint + event timeline.
2. Inspect branch decisions and approval gates post-mortem.
3. Use replay artifacts in regression and incident analysis.

### 18.3 SLO Requirements

1. Defined p95 latency and reliability targets.
2. Alert thresholds and error-budget policy.
3. Incident classification and recovery objectives.

---

## 19. Integrations and Protocol Strategy

### 19.1 MCP Requirements

1. Synarch-exposed MCP server interfaces.
2. Synarch MCP client to consume external tool servers.
3. Inspector-friendly MCP development workflow.

### 19.2 A2A Readiness

1. Agent discovery card support.
2. Task delegation contracts for external agents.
3. Signed trust and capability metadata for cross-agent calls.

### 19.3 Configuration-Driven Agents

1. YAML/JSON schema-backed agent definitions.
2. Schema validation at startup.
3. Controlled hot-reload for non-breaking config changes.

---

## 20. Infrastructure and Deployment Requirements

### 20.1 Runtime Topology

1. Backend and web app deployment profiles (local and hosted modes).
2. Managed infra: PostgreSQL, NATS/JetStream, vector store, model providers.
3. Health surface includes all critical dependencies.

### 20.2 Operational Controls

1. Environment profile management.
2. Startup/shutdown consistency procedures.
3. Backup/restore processes for persistent state.

---

## 21. Non-Functional Requirements Index

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Reliability | no in-memory-only mission critical state |
| NFR-2 | Streaming latency | <= 300ms p95 |
| NFR-3 | Observability | all critical actions traceable |
| NFR-4 | Maintainability | modular boundaries enforced |
| NFR-5 | Security | auth + approval + idempotency test-covered |
| NFR-6 | Startup | full stack < 2 minutes (local baseline) |
| NFR-7 | Cost | mission cost telemetry and budget enforcement |
| NFR-8 | Quality | strict lint/type/test gates |
| NFR-9 | Replayability | checkpoint + event replay for mission debugging |
| NFR-10 | Extensibility | MCP protocol-compatible tool boundary |

---

## 22. Functional Requirements Index (FR-1 to FR-86)

### 22.1 Core Runtime FR-1 to FR-44

| FR | Description | Priority | Section |
|---|---|---|---|
| FR-1 | Create mission with goal, mode, constraints | P0 | §13 |
| FR-2 | Durable mission record with unique thread context | P0 | §9 |
| FR-3 | Mission state model includes execution and terminal states | P0 | §8 |
| FR-4 | Mission state query endpoint | P0 | §13 |
| FR-5 | Resume from persisted state after restart | P0 | §9 |
| FR-6 | LangGraph StateGraph as orchestration core | P0 | §10 |
| FR-7 | Conditional branch routing on state | P0 | §10 |
| FR-8 | Interrupt/resume support for approvals | P0 | §10 |
| FR-9 | Validation nodes before risky transitions | P0 | §10 |
| FR-10 | Graph checkpoints persisted to PostgreSQL | P0 | §9 |
| FR-11 | All model calls route through litellm | P0 | §12 |
| FR-12 | Agent prompts load from soul/config source | P0 | §7 |
| FR-13 | Structured lifecycle event emission | P0 | §11 |
| FR-14 | Side-effecting tools support idempotency key semantics | P0 | §13 |
| FR-15 | Retry metadata captured for retried operations | P1 | §12 |
| FR-16 | NATS required for runtime event publication | P0 | §11 |
| FR-17 | Event subject taxonomy covers mission/agent/task/deliverable/approval | P0 | §11 |
| FR-18 | SSE streams runtime events in near-real time | P0 | §11 |
| FR-19 | Event schema typed and versioned | P0 | §11 |
| FR-20 | Event envelope includes mission/time/stage/source/provenance fields | P0 | §11 |
| FR-21 | Sensitive operations generate approval requests | P0 | §15 |
| FR-22 | Operator approves/rejects with reason | P0 | §15 |
| FR-23 | Runtime pauses and resumes deterministically on decisions | P0 | §15 |
| FR-24 | Approval outcomes persisted and queryable | P0 | §9 |
| FR-25 | Approval timeout policy configurable | P1 | §15 |
| FR-26 | Mission Control shows live mission phase and status | P0 | §14 |
| FR-27 | UI renders typed stream with filters | P0 | §14 |
| FR-28 | UI approval queue actions | P0 | §14 |
| FR-29 | UI deliberation timeline | P1 | §14 |
| FR-30 | UI tasks/blockers/deliverables | P0 | §14 |
| FR-31 | UI mission start and inspect flows | P0 | §14 |
| FR-32 | UI execution mode + branch visibility | P1 | §14 |
| FR-33 | Design tokens as source of truth | P0 | §14 |
| FR-34 | Components use defined visual primitives | P0 | §14 |
| FR-35 | Border/shape rules enforced | P0 | §14 |
| FR-36 | Brand compliance gate in PR path | P1 | §14 |
| FR-37 | Browser tooling follows deterministic Playwright-MCP approach | P2 | §19 |
| FR-38 | Integration execution scoped by actor/user/org context | P2 | §19 |
| FR-39 | External triggers route into mission workflows | P2 | §19 |
| FR-40 | MCP tool dev loop supports inspect/debug workflows | P2 | §19 |
| FR-41 | Gateway auth supports explicit mode configuration | P1 | §16 |
| FR-42 | Control-plane actions audit-attributed | P0 | §16 |
| FR-43 | Unsafe operations blocked without approval/policy | P0 | §16 |
| FR-44 | Secrets never emitted in event/UI logs | P0 | §16 |

### 22.2 Expanded Capability FR-45 to FR-74

| FR | Description | Priority | Section |
|---|---|---|---|
| FR-45 | Evaluation framework (unit + integration + E2E mission evals) | P0 | §17 |
| FR-46 | LLM-as-judge quality scoring | P1 | §17 |
| FR-47 | Cost tracking (tokens, latency, mission cost) | P0 | §12, §18 |
| FR-48 | Regression eval suite in CI | P1 | §17 |
| FR-49 | Multi-dimensional quality/latency/cost/safety dashboards | P1 | §18 |
| FR-50 | Eval dataset management (golden + sampled production) | P2 | §17 |
| FR-51 | Defense-in-depth security model | P0 | §16 |
| FR-52 | Per-agent least-privilege permission model | P0 | §16 |
| FR-53 | Tool guardrail wrappers for dangerous operations | P0 | §16 |
| FR-54 | Prompt injection detection and mitigation path (canary + scanning) | P1 | §16 |
| FR-55 | Forensic audit trail with correlation IDs | P1 | §16 |
| FR-56 | External integration supply-chain security checks | P2 | §16 |
| FR-57 | Context assembly pipeline per agent | P1 | §9 |
| FR-58 | Token budget tracking across context classes | P1 | §12, §18 |
| FR-59 | Memory write patterns (facts, procedures, decisions) | P1 | §9 |
| FR-60 | Memory lifecycle management (TTL, archive, delete) | P2 | §9 |
| FR-61 | MCP server interface for Synarch tools | P1 | §19 |
| FR-62 | MCP client integration for external tool servers | P1 | §19 |
| FR-63 | A2A protocol readiness | P2 | §19 |
| FR-64 | Agent discovery card support | P2 | §19 |
| FR-65 | YAML/JSON agent configuration model | P1 | §19 |
| FR-66 | Safe configuration hot-reloading | P2 | §19 |
| FR-67 | Schema validation for agent configuration at startup | P1 | §19 |
| FR-68 | AgentTool composition pattern | P1 | §10 |
| FR-69 | Confidence scoring per decision/action | P2 | §15 |
| FR-70 | Progressive trust metrics for autonomy expansion | P2 | §15 |
| FR-71 | Graceful handoff to human with full context package | P1 | §15 |
| FR-72 | Dynamic model routing by complexity/cost/quality constraints | P2 | §12 |
| FR-73 | Dynamic tool selection by context and task type | P2 | §10 |
| FR-74 | Mission cost budgets with degradation strategy | P2 | §12 |

### 22.3 Runtime Closure and Enterprise Baseline FR-75 to FR-86

| FR | Description | Priority | Section |
|---|---|---|---|
| FR-75 | End-to-end durable runtime wiring (no in-memory mission SOT) | P0 | §9 |
| FR-76 | NATS-to-SSE bridge with reconnect-safe semantics | P0 | §11 |
| FR-77 | Approval persistence + deterministic interrupt/resume validation | P0 | §15 |
| FR-78 | Gateway idempotency middleware for side effects | P0 | §13 |
| FR-79 | Auth mode enforcement + actor/session/device attribution | P0 | §16 |
| FR-80 | Sandboxed code execution (container or WASM class) | P1 | §16 |
| FR-81 | Backend contract/orchestrator tests required for merge | P1 | §17 |
| FR-82 | Mission Control build-quality gate | P1 | §14 |
| FR-83 | Mandatory reference-adoption evidence in implementation PRs | P1 | §19 |
| FR-84 | Memory compaction and anti-context-rot policy | P2 | §9 |
| FR-85 | Mission replay/time-travel debugging from checkpoints | P2 | §18 |
| FR-86 | SLO instrumentation and alert thresholds | P2 | §18 |

---

## 23. Canonical Roadmap (A -> B -> C)

### Phase 0-1: Runtime Closure (Now)

1. Implement FR-75..79 and FR-82/81 baseline.
2. Remove placeholder execution/stream paths.
3. Validate durability, approvals, and build stability.

### Phase 2: Production Readiness

1. Implement FR-45..60, FR-68.
2. Enforce quality/security measurement loops.
3. Move from hardcoded behaviors to controlled configurable patterns.

### Phase 3: Protocol Ecosystem

1. Implement FR-61..67 and FR-83.
2. Deliver MCP and A2A interoperability primitives.
3. Add integration governance controls for enterprise rollout.

### Phase 4: Enterprise Hardening

1. Implement FR-80, FR-85, FR-86 fully.
2. Expand tenancy/compliance and incident operations.
3. Enforce secure execution as default path.

### Phase 5: 2027 Visionary Track

1. Agentic Forge (self-building toolchain under strict guardrails).
2. Holographic paged memory behavior.
3. Adversarial validation swarms.
4. Living Constellation Mission Control GenUX.
5. Optional compute auction model (policy-gated).

---

## 24. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| State loss due to incomplete durability wiring | Medium | High | FR-75 gate before release |
| Approval deadlocks in runtime | Medium | High | deterministic timeout + resume tests |
| Prompt injection via external content | High | High | FR-54 controls + guardrails |
| Cost explosion in long missions | Medium | High | FR-47 + FR-74 budgets |
| Tool misuse and privilege creep | Medium | High | FR-52 + FR-53 enforcement |
| Debugging blind spots post-incident | Medium | Medium | FR-85 replay requirement |
| UI drift from runtime truth | Medium | Medium | FR-82 + event parity checks |

---

## 25. Definition of Done

v1.2 baseline is done only when all are true:

1. FR-1..44 are implemented and tested on real runtime path.
2. FR-75..79 runtime closure requirements are live.
3. FR-81 and FR-82 quality gates block failing merges/builds.
4. FR-45/47 baseline eval + cost telemetry exist.
5. FR-51..55 baseline security controls are implemented.
6. Mission recovery + approval resume tests pass in CI.
7. Mission Control operates on real event stream, not placeholders.
8. Reference adoption evidence is updated for implemented patterns.

---

## 26. Open Questions

1. Which auth mode is required for first hosted beta (token vs proxy)?
2. Which actions are mandatory approval-gated vs sandbox-only?
3. Which cost degradation policy is acceptable for user-facing quality?
4. What minimum replay retention period balances debug value and storage cost?
5. What is the acceptable confidence threshold for autonomy escalation?

---

## 27. Source and Traceability

Primary synthesis sources:
- `docs/01-requirements/future-vision-prd-analysis.md`
- `docs/01-requirements/enterprise-readiness-and-future-forward-roadmap.md`
- `docs/01-requirements/antigravity-future-vision-2027.md`
- `docs/01-requirements/codex-future-vision-2027.md`
- `docs/04-reference-deep-dives/*`
- `memory-bank/knowledge-synthesis-2026-02-21.md`
- `memory-bank/prd-v1-gap-matrix-2026-02-21.md`

Canonical cross-check rule:
- A requirement is considered valid only when represented in this PRD and linked to acceptance signals in implementation/testing artifacts.

---

## 28. Approval and Revision History

| Version | Date | Author(s) | Summary |
|---|---|---|---|
| 0.1 | 2026-02-13 | Cline + Antigravity | Initial PoC PRD |
| 1.0 | 2026-02-20 | Claude + Codex | Unified FR-1..44 baseline |
| 1.1 | 2026-02-21 | Claude + Codex + Antigravity | FR-45..86 expansion + hybrid roadmap |
| 1.2 | 2026-02-21 | Claude + Codex + Antigravity (canonical rewrite) | Full PRD rebuilt from scratch with explicit traceability and renamed canonical file |
