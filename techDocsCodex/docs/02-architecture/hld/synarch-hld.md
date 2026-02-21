# Synarch Master HLD (Umbrella Constitution)

Status: Authoritative Level-1 Master Doc (Create Once)
Source baseline: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD (v1.2, FR-1..FR-86)
Last updated: 2026-02-21

## 1. Purpose

This document defines non-negotiable system architecture constraints for Synarch.
All issue work (S01+) must comply with this architecture.

Governance model:
- Level 1: Umbrella constitution docs (this HLD + DB schema + API + event catalog)
- Level 2: Per-issue mini-specs (delta only)

## 2. Architecture Invariants (MUST)

1. Mission-critical state must be durable; no in-memory source of truth for mission lifecycle (FR-75).
2. Control flow is decided only by LangGraph state and policy nodes, never by UI-only state or ad-hoc event consumers (FR-6..FR-10).
3. Runtime events must flow through typed NATS envelope and be streamable to UI via SSE with reconnect semantics (FR-16..FR-20, FR-76).
4. Sensitive actions must follow deterministic HITL pause/resume lifecycle with durable approval records (FR-21..FR-25, FR-77).
5. Side effects must be idempotent and auditable (FR-14, FR-42, FR-78, FR-79).
6. Secrets must never leak into event payloads or UI logs (FR-44).

## 3. Planes and Boundaries

### 3.1 Control Plane

Scope:
- FastAPI gateway
- LangGraph orchestrator
- policy and approval lifecycle

Responsibilities:
- mission create/pause/resume/cancel
- state transitions
- approval gating
- deterministic recovery entrypoint

### 3.2 Event Plane

Scope:
- NATS/JetStream subjects
- typed event envelope
- SSE bridge

Responsibilities:
- publish immutable runtime events
- expose UI stream with Last-Event-ID compatibility
- event parity with persistence plane

### 3.3 Persistence Plane

Scope:
- PostgreSQL mission metadata
- approval records
- event journal
- LangGraph checkpointer tables

Responsibilities:
- durable source of truth for mission state
- queryability for APIs
- replay support

## 4. Core Runtime Components

1. Gateway (FastAPI)
- validates requests
- enforces idempotency and auth mode checks
- exposes mission + approval APIs and SSE stream

2. Orchestrator (LangGraph)
- StateGraph with conditional routing
- policy validation nodes before risky actions
- interrupt/resume for HITL

3. Event Bus (NATS)
- mission/agent/task/deliverable/approval event domains
- strict envelope validation before publish

4. Storage (PostgreSQL)
- missions/tasks/deliverables/approvals/mission_events/idempotency records
- checkpointer-backed thread continuity

5. Mission Control (Next.js)
- live phase/status
- timeline + filters
- approval actions
- task/deliverable visibility

## 5. LangGraph and NATS Interaction Contract

Required sequence (high level):
1. create mission row in PostgreSQL
2. compile/load graph with persistent checkpointer
3. execute graph step
4. persist state transition
5. publish typed event to NATS
6. bridge event to SSE stream
7. checkpoint graph thread

Rule:
- No graph transition is considered complete unless persistence + event publication are both accounted for.

## 6. Rule of Two Enforcement

For risky operations:
1. pre-tool policy check triggers approval request
2. approval record written before graph pause
3. graph enters awaiting_approval deterministically
4. operator decision API writes decision with actor/session/device attribution
5. graph resumes with explicit decision context
6. timeout path is deterministic and auditable

## 7. Target State Model

Required mission states:
- created
- planning
- executing
- awaiting_approval
- reviewing
- revising
- synthesizing
- paused
- failed
- completed
- cancelled

State changes must emit events and write persistence updates.

## 8. Security and Governance Envelope

1. Auth mode must be explicit and enforceable at gateway.
2. Per-agent least-privilege tool/data policies must exist.
3. Guardrail wrappers must protect dangerous tools.
4. Prompt-injection mitigation path must be deterministic.
5. Forensic correlation IDs must connect API call, mission transition, and event trail.
6. Untrusted code execution must route through sandbox contract when enabled.

## 9. Quality and Operability Requirements

1. Contract and orchestrator tests are mandatory merge gates (FR-81).
2. Mission Control build/lint/type checks are mandatory merge gates (FR-82).
3. Replay and SLO capabilities are required for enterprise hardening (FR-85, FR-86).

## 10. Ralph Delta Protocol (Level 2)

Every issue mini-spec must include:
1. FRs addressed
2. files to change (exact paths)
3. SQL migration(s) to run (exact filenames)
4. API contract delta (if any)
5. event catalog delta (if any)
6. rollback plan
7. verification plan

Forbidden:
- hidden schema changes
- undocumented event type additions
- endpoint behavior changes without contract update

## 11. FR Traceability Summary

This HLD governs FR groups:
- Runtime core: FR-1..FR-44
- Expanded capabilities: FR-45..FR-74 (architecture impact)
- Runtime closure + enterprise baseline: FR-75..FR-86
