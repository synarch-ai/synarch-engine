# Synarch Engine — Product Requirements Document v1.0 (Final)

**Authors:** Claude (Opus 4) + Codex (GPT-5.2) for PraxLannister  
**Version:** 1.0-final | **Status:** Draft for Approval | **Date:** 2026-02-20  
**Scope:** PoC — exhaustive specification  
**Supersedes:** `poc-prd.md`, `prd-1.0-claude.md`, `prd-1.0-codex.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision & Principles](#2-product-vision--principles)
3. [Problem Statement & Value Proposition](#3-problem-statement--value-proposition)
4. [Target Users & Personas](#4-target-users--personas)
5. [User Stories](#5-user-stories)
6. [The Hierarchy — Agent Specifications](#6-the-hierarchy--agent-specifications)
7. [System Architecture](#7-system-architecture)
8. [Mission Lifecycle State Machine](#8-mission-lifecycle-state-machine)
9. [Persistence Architecture](#9-persistence-architecture)
10. [Orchestration Engine — LangGraph](#10-orchestration-engine--langgraph)
11. [Nervous System — NATS Event Contract](#11-nervous-system--nats-event-contract)
12. [Model Routing — litellm](#12-model-routing--litellm)
13. [API Specification](#13-api-specification)
14. [Mission Control UI](#14-mission-control-ui)
15. [Human-in-the-Loop (HITL)](#15-human-in-the-loop-hitl)
16. [Security & Governance](#16-security--governance)
17. [Testing & Validation](#17-testing--validation)
18. [Observability & Telemetry](#18-observability--telemetry)
19. [Infrastructure & Deployment](#19-infrastructure--deployment)
20. [Non-Functional Requirements](#20-non-functional-requirements)
21. [Functional Requirements Index](#21-functional-requirements-index)
22. [Reference Adoption Requirements](#22-reference-adoption-requirements)
23. [Implementation Phases](#23-implementation-phases)
24. [Risk Register](#24-risk-register)
25. [Definition of Done](#25-definition-of-done)
26. [Open Questions](#26-open-questions)
27. [Out of Scope — Phase 2+ Roadmap](#27-out-of-scope--phase-2-roadmap)
28. [Glossary](#28-glossary)
29. [Source Index](#29-source-index)
30. [Approval](#30-approval)

---

## 1. Executive Summary

**Synarch** (syn=together + arch=govern) is an open-source, production-grade **Autonomous Multi-Agent Orchestration Engine** — the "Linux of autonomous agent teams."

Six mythologically-named AI agents — organized in a strict hierarchy from God (human user) through a CEO agent down to specialists — collaborate in real-time to execute complex missions spanning research, engineering, and review. Every agent has a **soul** (identity, SOP, constraints), communicates through an **event-driven nervous system** (NATS), and is orchestrated by a **durable state machine** (LangGraph with PostgreSQL checkpointing).

**Core Value Proposition:** *"God speaks a wish. The Synarch makes it real."*

### What Makes Synarch Different

| Existing Solutions | Synarch's Answer |
|---|---|
| Single agents (ChatGPT, Claude) | Autonomous agent **teams** with enforced hierarchy |
| Agent frameworks (CrewAI, AutoGen, LangGraph) | Production-grade **product** with Mission Control dashboard |
| Bhanu's SiteGPT system (closed, marketing-only) | Open-source, secure, general-purpose, self-hostable |
| Polling-based agent communication | Event-driven **nervous system** (NATS, 60ns latency) |
| No observability into agent reasoning | Real-time **Mission Control** — see gods think, argue, and deliver |
| Fragile in-memory state | **Durable** — crash recovery via PostgreSQL checkpointing |

### PoC Demo Scenario

God (human user) types into Mission Control:

> *"Research the best event bus for Synarch's nervous system and implement a working NATS integration prototype with tests."*

The system: decomposes → delegates → researches → codes → reviews → synthesizes → delivers. All visible in real-time.

---

## 2. Product Vision & Principles

### 2.1 Vision

Deliver an **agent operating cockpit** where:
1. Every mission is observable in real time.
2. Every sensitive action can be gated by operator approval.
3. Every result is traceable to nodes, tools, and events.
4. Every mission can survive failure and resume deterministically.
5. The UI expresses a clear Synarch identity rather than generic dashboard aesthetics.

### 2.2 Product Principles

These principles guide all ambiguous decisions:

1. **Governed autonomy over unrestricted autonomy** — Agents are powerful but never unchecked.
2. **Durable by default over fast-but-ephemeral** — No in-memory-only mission-critical state.
3. **Explicit contracts over implicit coupling** — Typed events, typed state, typed APIs.
4. **Traceability over black-box convenience** — Every output links to its source events.
5. **Identity-first interface over generic UI templates** — V3 Design System is the product's soul.

### 2.3 Primary Objectives (v1.0)

| ID | Objective |
|---|---|
| OBJ-1 | Durable orchestration: no mission-critical state lost on restart |
| OBJ-2 | Governance-first runtime: conditional routing + HITL interrupt/resume |
| OBJ-3 | Event-native operation: all runtime activity emitted as structured events |
| OBJ-4 | Operational UI: Mission Control supports start/monitor/approve/review loops |
| OBJ-5 | Brand fidelity: V3 tokens/components implemented and enforced |

---

## 3. Problem Statement & Value Proposition

### The Problem

AI agent frameworks today are **libraries, not products**. Developers using CrewAI, AutoGen, or LangGraph must build everything from scratch: orchestration logic, UI, memory management, security boundaries, monitoring, and deployment. The result is fragile, ad-hoc systems that break under production load and offer zero observability.

Bhanu Teja Padavala proved at SiteGPT that autonomous agent teams can work — his 14-agent marketing squad operates 24/7. But his system is:
- **Closed-source** — nobody can use it
- **Insecure** — agents have unfettered access to everything
- **Unobservable** — uses 15-minute polling, no real-time visibility
- **Marketing-only** — domain-locked, not general-purpose

### The Solution

Synarch is the **missing operating system layer** for autonomous agent teams:

1. **Hierarchy-first orchestration** — Agents have ranks, permissions, and delegation chains. No agent acts alone.
2. **Event-driven nervous system** — NATS pub/sub replaces polling. Every agent action is an event. Real-time.
3. **Soul system** — Each agent has identity, personality, SOPs, and constraints. Not just a system prompt.
4. **Durable execution** — PostgreSQL-checkpointed state machines. Crash, restart, resume.
5. **Mission Control dashboard** — See everything: agent thoughts, task flow, deliverables.
6. **Open-source, self-hostable** — `docker compose up` and you're running.

### Value Proposition by User Type

| User | Value |
|---|---|
| **Solo developer** | An AI team that works on your project 24/7 while you sleep |
| **Startup founder** | Scale operations without hiring — agents handle research, code, review |
| **Open-source contributor** | The self-hostable alternative to closed SaaS agent platforms |
| **Enterprise architect** | A production-grade reference for hierarchical agent orchestration |

---

## 4. Target Users & Personas

### Persona 1: The Solo Builder (God — Primary Operator)

- **Name:** Arjun, 28, full-stack developer
- **Context:** Building a SaaS product solo. Needs help with research, code review, and boilerplate.
- **Pain:** Can't afford to hire. ChatGPT is one-shot — no persistent multi-step execution.
- **Goal:** Give a mission, go to sleep, wake up to a researched analysis with working code.
- **Needs:** Fast situational awareness. Deterministic control over sensitive actions. Clear provenance and recoverability.
- **Success metric:** Mission completes autonomously with source-cited research and tested code.

### Persona 2: The Startup Operator (God — Primary Operator)

- **Name:** Maya, 33, CEO of a 3-person startup
- **Context:** Needs marketing research, competitor analysis, and engineering prototypes done fast.
- **Pain:** Existing agent tools are too technical to set up. No visibility into what agents are doing.
- **Goal:** One dashboard to see all agent activity. Non-technical enough to understand the flow.
- **Success metric:** Mission Control shows real-time progress without needing to read logs.

### Persona 3: The Open-Source Power User (God — Primary Operator)

- **Name:** Dmitri, 40, DevOps engineer and OSS contributor
- **Context:** Evaluates agent frameworks for self-hosting. Security and observability are non-negotiable.
- **Pain:** Every agent framework is a black box with no persistence and no permission model.
- **Goal:** Fork, customize, deploy on own infrastructure with full control.
- **Success metric:** System is self-hostable, extensible, and transparent in its decision-making.

### Persona 4: The Platform Developer (Secondary)

- **Name:** Kai, 32, backend engineer extending Synarch
- **Context:** Implements and evolves orchestration/runtime. Adds tools/integrations safely.
- **Pain:** Unclear runtime boundaries, untyped event contracts, no observability hooks.
- **Goal:** Typed event contracts, clear runtime boundaries, strong observability and traceability.
- **Needs:** Validated performance and reliability. Safe integration patterns.
- **Success metric:** New agent or tool can be added with clear contracts and no runtime regressions.

---

## 5. User Stories

### Epic 1: Mission Execution (FR-1 to FR-5)

| ID | As a... | I want to... | So that... | Priority | FR | Acceptance Criteria |
|---|---|---|---|---|---|---|
| US-1.1 | God | Submit a natural language goal via Mission Control | The Synarch decomposes and executes it | P0 | FR-1 | Goal accepted, plan visible in <5s |
| US-1.2 | God | See real-time agent thoughts and actions | I understand what's happening without reading logs | P0 | FR-18 | SSE stream updates Mission Control in <1s |
| US-1.3 | God | See the final deliverable(s) | I can use the output directly | P0 | FR-30 | Deliverables panel shows research report + code |
| US-1.4 | God | Kill or pause a running mission | I can stop runaway agents | P0 | FR-3 | Mission transitions to CANCELLED/PAUSED state |
| US-1.5 | God | Query mission state at any time | I know current status without streaming | P0 | FR-4 | GET `/mission/{id}/state` returns full state |

### Epic 2: Agent Hierarchy & Delegation (FR-6 to FR-15)

| ID | As a... | I want to... | So that... | Priority | FR | Acceptance Criteria |
|---|---|---|---|---|---|---|
| US-2.1 | Synarch (CEO) | Decompose a goal into sub-missions | Each C-Suite agent gets a clear objective | P0 | FR-7 | Plan has ≥2 sub-tasks with assigned agents |
| US-2.2 | Zeus (CTO) | Delegate engineering tasks to Hephaestus | Code is written by the specialist | P0 | FR-13 | Task assignment visible in NATS events |
| US-2.3 | Thoth (CRO) | Delegate research tasks to Hermes | Information is gathered by the specialist | P0 | FR-13 | Research results include source citations |
| US-2.4 | Janus (Reviewer) | Review deliverables from any agent | Quality is verified before delivery to God | P0 | FR-9 | Review verdict (PASS/FAIL/REVISE) is emitted |

### Epic 3: Durability & Recovery (FR-2, FR-5, FR-10)

| ID | As a... | I want to... | So that... | Priority | FR | Acceptance Criteria |
|---|---|---|---|---|---|---|
| US-3.1 | God | Restart the backend without losing state | Crashes don't destroy progress | P0 | FR-5 | Mission resumes from last checkpoint after restart |
| US-3.2 | God | See mission history after completion | Past missions are auditable | P1 | FR-4 | GET `/mission/{id}/state` returns completed mission |

### Epic 4: Human-in-the-Loop (FR-21 to FR-25)

| ID | As a... | I want to... | So that... | Priority | FR | Acceptance Criteria |
|---|---|---|---|---|---|---|
| US-4.1 | God | Approve or reject agent actions requiring permission | Dangerous operations don't execute without my consent | P0 | FR-21 | Pending approval pauses graph; approve/reject resumes |
| US-4.2 | God | See why an agent is asking for approval | I can make an informed decision | P1 | FR-22 | Request includes action description and risk reason |
| US-4.3 | God | Set approval timeout with fallback behavior | System doesn't hang indefinitely | P1 | FR-25 | Configurable timeout, default auto-reject after 5min |

### Epic 5: Observability (FR-16 to FR-20, FR-26 to FR-32)

| ID | As a... | I want to... | So that... | Priority | FR | Acceptance Criteria |
|---|---|---|---|---|---|---|
| US-5.1 | God | See which agents are active and their state | I know the system health | P0 | FR-26 | Agent topology shows active/idle/waiting states |
| US-5.2 | God | See a timeline of agent events | I can trace decision flow | P1 | FR-27 | Thought stream is chronological with timestamps |
| US-5.3 | God | See task progression (kanban) | I know what's in progress vs done | P1 | FR-30 | Task board reflects real-time state changes |
| US-5.4 | Platform Dev | Trace deliverable provenance to source events | I can audit output origins | P1 | FR-20 | Every deliverable has `provenance_refs[]` |

---

## 6. The Hierarchy — Agent Specifications

### 6.1 Tier Structure

```
Tier 0: 🌟 GOD (Human User) — source of all authority, Rule of Two enforcer
         │
Tier 1: 🏛️ SYNARCH (CEO Agent) — supreme orchestrator, mission decomposer
         │
Tier 2: ⚡ Zeus (CTO)        📜 Thoth (CRO)
         │ Engineering cmd     │ Knowledge keeper
         │                     │
Tier 3: 🔨 Hephaestus        🪶 Hermes        🎭 Janus
         │  (Engineer)          (Researcher)      (Reviewer)
```

**Hierarchy Rules (FR-43):**
- Agents can ONLY communicate with their direct superior and direct reports
- Tier 3 agents cannot contact Tier 1 directly — must go through Tier 2
- God speaks ONLY to Synarch — never directly to specialists
- Synarch is the ONLY agent that can address God

### 6.2 Agent Specification Table

| Agent | Tier | Role | Model (litellm) | Soul File | Inputs | Outputs | Tools (PoC) |
|---|---|---|---|---|---|---|---|
| **God** | 0 | Human User | N/A | `docs/agents/god/soul.md` | N/A | Mission goals, approvals, feedback | Mission Control UI |
| **Synarch** | 1 | CEO / Supreme Orchestrator | `bedrock/anthropic.claude-opus-4-20250514-v1:0` | `docs/agents/synarch/soul.md` | God's goal | Mission plan, delegation orders, final synthesis | Plan decomposition, agent delegation |
| **Zeus** | 2 | CTO / Engineering Commander | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | `docs/agents/zeus/soul.md` | Engineering objectives from Synarch | Technical plans, task assignments | Task creation, code review delegation |
| **Thoth** | 2 | CRO / Knowledge Keeper | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | `docs/agents/thoth/soul.md` | Research objectives from Synarch | Research plans, knowledge synthesis | Research task creation, source evaluation |
| **Hermes** | 3 | Researcher / Info Gatherer | `ollama/llama3.1:8b` | `docs/agents/hermes/soul.md` | Research tasks from Thoth | Source-cited research findings | Web search, document retrieval |
| **Hephaestus** | 3 | Engineer / Code Builder | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | `docs/agents/hephaestus/soul.md` | Engineering tasks from Zeus | Working code with tests | Code generation, file write |
| **Janus** | 3 | Reviewer / Quality Gate | `bedrock/anthropic.claude-3-5-haiku-20241022-v1:0` | `docs/agents/janus/soul.md` | Deliverables from any agent | Structured review verdicts | Review checklist evaluation |

### 6.3 Agent Soul System (FR-12)

Every agent loads its `soul.md` file as the foundation of its system prompt. A soul defines:

1. **Identity** — Name, title, mythology, personality traits
2. **Hierarchy position** — Tier, who they report to, who reports to them
3. **Core directives** — What the agent MUST do
4. **Constraints** — What the agent MUST NOT do
5. **Communication protocol** — How to format messages, when to escalate
6. **Standard Operating Procedures** — Step-by-step workflows for common tasks

**Implementation:** `AgentNode.load_soul()` reads the markdown file and prepends it to every LLM call as system prompt context.

### 6.4 Future Agents (Phase 2+)

| Agent | Tier | Role | Mythology |
|---|---|---|---|
| Athena | 2 | CPO (Product) | Greek goddess of wisdom and strategy |
| Odin | 2 | CISO (Security) | Norse all-father, seeker of knowledge |
| Midas | 2 | CFO (Finance) | Greek king with the golden touch |
| Apollo | 2 | CMO (Marketing) | Greek god of communication and art |
| Vishwakarma | 3 | Infrastructure Engineer | Hindu divine architect |
| Saraswati | 3 | Documentation Writer | Hindu goddess of knowledge |

---

## 7. System Architecture

### 7.1 System Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     GOD (Human User)                         │
│                     Mission Control UI                       │
│                     Next.js 14 + shadcn/ui                  │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST + SSE (Server-Sent Events)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     GATEWAY (FastAPI)                         │
│  POST /mission/start         GET /mission/{id}/stream       │
│  GET  /mission/{id}/state    POST /mission/{id}/approvals/{approval_id}/decision │
│  POST /mission/{id}/cancel   GET /agents                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  LangGraph   │ │  NATS    │ │  PostgreSQL  │
│  Orchestrator│◄┤  Nervous │ │  Mission     │
│  (StateGraph)│ │  System  │ │  Metadata    │
│              │─┤          │ │  + LangGraph │
│  Agent Nodes │ │  Events  │ │  Checkpoints │
└──────────────┘ └──────────┘ └──────────────┘
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
      ┌──────────┐ ┌────────┐ ┌────────┐
      │ Qdrant   │ │ Ollama │ │Bedrock │
      │ Vector   │ │ Local  │ │Frontier│
      │ Memory   │ │ LLMs   │ │ LLMs   │
      └──────────┘ └────────┘ └────────┘
```

### 7.2 Component Responsibilities

| Component | Responsibility | Technology | FR |
|---|---|---|---|
| **Gateway** | HTTP API, SSE streaming, request validation, CORS | FastAPI | FR-1,4,18 |
| **Orchestrator** | Agent execution graph, state management, routing | LangGraph StateGraph | FR-6,7,8,9,10 |
| **Nervous System** | Event pub/sub, subject hierarchy, real-time propagation | NATS + JetStream | FR-16,17 |
| **Mission Store** | Mission metadata, API query support, status tracking | PostgreSQL | FR-2,3,4 |
| **Checkpoint Store** | Graph execution state, crash recovery, resume | PostgreSQL (checkpointer) | FR-5,10 |
| **Vector Memory** | Semantic search, per-agent knowledge, shared namespaces | Qdrant | Phase 2 |
| **Model Router** | Provider-agnostic LLM calls, cost-optimized routing | litellm | FR-11 |
| **Mission Control** | Real-time dashboard, agent viz, HITL approvals | Next.js + shadcn/ui | FR-26-32 |

### 7.3 Data Flow — Mission Execution

```
1. God submits goal via Mission Control UI
2. POST /mission/start → Gateway creates mission record in PostgreSQL
3. Gateway invokes LangGraph graph.astream() with initial state
4. Synarch node activates → reads soul.md → calls litellm (Opus 4)
5. Synarch decomposes goal → emits plan to NATS (synarch.mission.{id}.planned)
6. Graph conditionally routes to Zeus and/or Thoth based on plan
7. Zeus/Thoth activate → delegate to specialists → emit events to NATS
8. Specialists (Hermes, Hephaestus) execute → emit results to NATS
9. Janus reviews deliverables → emits verdict to NATS
10. Synarch synthesizes → emits final output to NATS
11. NATS events → SSE subscriber → Mission Control UI updates in real-time
12. Graph checkpoints to PostgreSQL after every node completion
13. Mission metadata updated to COMPLETED
```

---

## 8. Mission Lifecycle State Machine

### 8.1 Mission States (FR-3)

```
                    ┌──────────┐
                    │ CREATED  │
                    └────┬─────┘
                         │ Graph invoked
                         ▼
                    ┌──────────┐
              ┌────►│ PLANNING │
              │     └────┬─────┘
              │          │ Synarch produces plan
              │          ▼
              │     ┌──────────┐
              │     │EXECUTING │◄────────────┐
              │     └────┬─────┘             │
              │          │                   │ Janus says REVISE
              │          ▼                   │
              │     ┌──────────┐        ┌────┴─────┐
              │     │REVIEWING │───────►│ REVISING │
              │     └────┬─────┘        └──────────┘
              │          │ Janus says PASS
              │          ▼
              │     ┌──────────────┐
              │     │ SYNTHESIZING │
              │     └────┬─────────┘
              │          │ Synarch produces final output
              │          ▼
              │     ┌──────────┐
              │     │COMPLETED │
              │     └──────────┘
              │
              │     ┌──────────────────┐
              └─────│AWAITING_APPROVAL │ (HITL interrupt)
                    └──────────────────┘
              
              At any point:
              ┌──────────┐    ┌──────────┐
              │ PAUSED   │    │CANCELLED │
              └──────────┘    └──────────┘
              ┌──────────┐
              │ FAILED   │
              └──────────┘
```

### 8.2 State Definitions

| State | Description | Triggers Entry | Triggers Exit |
|---|---|---|---|
| `CREATED` | Mission record exists, graph not yet invoked | POST `/mission/start` | Graph invocation begins |
| `PLANNING` | Synarch is decomposing the goal | Graph enters Synarch node | Plan produced with sub-tasks |
| `EXECUTING` | Agents are working on assigned tasks | Plan delegation begins | All tasks report completion |
| `AWAITING_APPROVAL` | HITL interrupt — God must approve/reject | Agent requests Rule of Two permission | God approves/rejects or timeout |
| `REVIEWING` | Janus is evaluating deliverables | All execution tasks complete | Janus emits verdict |
| `REVISING` | Agents are reworking based on review feedback | Janus verdict = REVISE | Revised deliverables submitted |
| `SYNTHESIZING` | Synarch is combining final deliverables | Review passed | Final output produced |
| `COMPLETED` | Mission finished successfully | Final output delivered to God | Terminal state |
| `PAUSED` | God paused the mission | POST `/mission/{id}/pause` | POST `/mission/{id}/resume` |
| `CANCELLED` | God cancelled the mission | POST `/mission/{id}/cancel` | Terminal state |
| `FAILED` | Unrecoverable error occurred | Exception in agent node | Terminal state (with error context) |

### 8.3 State Persistence

- Mission state is persisted as a `status` field in the `missions` PostgreSQL table
- State transitions emit NATS events: `synarch.mission.{id}.state_changed`
- Every state transition is logged with timestamp, previous state, and trigger reason
- LangGraph checkpoints independently track graph execution position
- Checkpoint-at-phase-boundary policy + state reconciliation test (FR-5)

---

## 9. Persistence Architecture

### 9.1 Dual-Store Strategy (FR-2, FR-5, FR-10)

| Store | Purpose | Schema Owner | Access Pattern |
|---|---|---|---|
| **Mission Metadata Store** | API queries, status tracking, mission listing | Synarch application | Fast reads by ID, status filtering |
| **LangGraph Checkpoint Store** | Graph execution state, crash recovery, resume | LangGraph checkpointer | Thread-scoped checkpoint read/write |

### 9.2 Mission Metadata Schema

```sql
CREATE TABLE missions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal            TEXT NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'CREATED',
    authority_mode  VARCHAR(20) NOT NULL DEFAULT 'supervised',
    plan            JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_context   JSONB,
    thread_id       VARCHAR(64),
    CONSTRAINT valid_status CHECK (status IN (
        'CREATED','PLANNING','EXECUTING','AWAITING_APPROVAL',
        'REVIEWING','REVISING','SYNTHESIZING',
        'COMPLETED','PAUSED','CANCELLED','FAILED'
    ))
);

CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    parent_task_id  UUID REFERENCES tasks(id),
    assigned_agent  VARCHAR(30) NOT NULL,
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority        INTEGER DEFAULT 0,
    inputs          JSONB,
    result          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    CONSTRAINT valid_task_status CHECK (status IN (
        'PENDING','IN_PROGRESS','COMPLETED','FAILED','REVISION_NEEDED'
    ))
);

CREATE TABLE deliverables (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    task_id         UUID REFERENCES tasks(id),
    agent           VARCHAR(30) NOT NULL,
    type            VARCHAR(30) NOT NULL,
    content         JSONB NOT NULL,
    review_status   VARCHAR(20) DEFAULT 'PENDING_REVIEW',
    provenance_refs JSONB DEFAULT '[]',       -- [FR-20] links to source event/task IDs
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE approvals (                       -- [FR-21-25] first-class entity
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    action_type     VARCHAR(30) NOT NULL,
    requested_by    VARCHAR(30) NOT NULL,
    description     TEXT NOT NULL,
    risk_level      VARCHAR(10) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    decided_by      VARCHAR(30),
    decision_reason TEXT,
    timeout_seconds INTEGER DEFAULT 300,       -- [FR-25] configurable timeout
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at      TIMESTAMPTZ
);

CREATE TABLE mission_events (
    id              BIGSERIAL PRIMARY KEY,
    mission_id      UUID NOT NULL REFERENCES missions(id),
    event_type      VARCHAR(60) NOT NULL,
    agent           VARCHAR(30),
    payload         JSONB NOT NULL,
    idempotency_key VARCHAR(64),               -- [FR-14] dedup side effects
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_missions_status ON missions(status);
CREATE INDEX idx_tasks_mission ON tasks(mission_id);
CREATE INDEX idx_deliverables_mission ON deliverables(mission_id);
CREATE INDEX idx_approvals_mission ON approvals(mission_id);
CREATE INDEX idx_events_mission ON mission_events(mission_id);
CREATE INDEX idx_events_idempotency ON mission_events(idempotency_key) WHERE idempotency_key IS NOT NULL;
```

### 9.3 LangGraph Checkpoint Schema

Managed by `langgraph-checkpoint-postgres`. Bootstrapped via `PostgresSaver.setup()`. Uses `thread_id` per mission.

### 9.4 Database Access Pattern

```python
class MissionRepository:
    async def create(self, goal: str, authority: str) -> Mission
    async def get(self, mission_id: UUID) -> Mission
    async def update_status(self, mission_id: UUID, status: str) -> None
    async def list(self, status: str = None, limit: int = 50) -> List[Mission]

class ApprovalRepository:
    async def create(self, mission_id: UUID, action: str, agent: str, risk: str) -> Approval
    async def decide(self, approval_id: UUID, decision: str, reason: str) -> Approval
    async def get_pending(self, mission_id: UUID) -> Optional[Approval]
```

---

## 10. Orchestration Engine — LangGraph (FR-6 to FR-10)

### 10.1 Target Graph Topology

```
                        START
                          │
                          ▼
                    ┌──────────┐
                    │ SYNARCH  │ (Plan & Decompose)
                    └────┬─────┘
                         │
                    ┌────┴────┐ (Conditional: FR-7)
                    ▼         ▼
              ┌──────────┐ ┌──────────┐
              │   ZEUS   │ │  THOTH   │
              └────┬─────┘ └────┬─────┘
                   │            │
              ┌────┴────┐ ┌────┴────┐
              ▼         ▼ ▼         ▼
        ┌───────────┐ ┌──────────┐
        │HEPHAESTUS │ │  HERMES  │
        └────┬──────┘ └────┬─────┘
             └──────┬──────┘
                    ▼
              ┌──────────┐
              │  JANUS   │ (Review Gate: FR-9)
              └────┬─────┘
              ┌────┴────┐
              ▼         ▼
        ┌──────────┐ ┌──────────┐
        │SYNTHESIZE│ │ REVISE   │──► back to agents
        └────┬─────┘ └──────────┘
             ▼
            END
```

### 10.2 State Schema

```python
class MissionState(TypedDict):
    mission_id: str
    goal: str
    authority_mode: str
    plan: List[str]
    plan_rationale: str
    phase: MissionPhase
    tasks: List[TaskAssignment]
    current_agent: str
    messages: Annotated[List[AgentMessage], operator.add]
    review_verdict: Optional[str]
    review_feedback: Optional[str]
    revision_count: int
    deliverables: List[dict]
    final_output: Optional[str]
    needs_approval: bool
    approval_request: Optional[dict]
    error: Optional[str]
```

### 10.3 Checkpointing (FR-5, FR-10)

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)
await checkpointer.setup()
app = graph.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": mission_id}}
```

---

## 11. Nervous System — NATS Event Contract (FR-16 to FR-20)

### 11.1 Subject Hierarchy (FR-17)

```
synarch.
├── mission.{mission_id}.
│   ├── created / planned / state_changed / completed / failed / cancelled
├── agent.{agent_name}.
│   ├── activated / thinking / delegated / result / error / deactivated
├── task.{task_id}.
│   ├── created / started / completed / revision
├── deliverable.{deliverable_id}.
│   ├── created / reviewed / accepted
└── approval.{mission_id}.
    ├── requested / approved / rejected
```

### 11.2 Canonical Event Envelope (FR-19, FR-20)

```python
class EventEnvelope(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    subject: str
    mission_id: str
    agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence: int = 0
    schema_version: str = "1.0"              # [FR-19] typed and versioned
    idempotency_key: Optional[str] = None    # [FR-14] for side-effecting events
    payload: dict[str, Any]
```

### 11.3 Event Semantics

1. Events are append-only and immutable once published.
2. Event IDs are unique and traceable across backend and UI.
3. Event payloads must be redaction-safe for UI display (FR-44: no secrets).
4. `schema_version` enables forward-compatible evolution.

### 11.4 NATS Client Wrapper

```python
class NervousSystem:
    async def connect(self) -> None
    async def publish(self, event: EventEnvelope) -> None
    async def subscribe(self, subject: str, callback) -> Subscription
    async def close(self) -> None
```

### 11.5 SSE Bridge

NATS → `EventEnvelope` parse → SSE yield → Mission Control `EventSource`. Supports reconnect via `lastEventId`.

---

## 12. Model Routing — litellm (FR-11)

### 12.1 Model Assignment

| Agent | litellm Model String | Provider | Cost |
|---|---|---|---|
| Synarch | `bedrock/anthropic.claude-opus-4-20250514-v1:0` | Bedrock | $$$$ |
| Zeus | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | Bedrock | $$$ |
| Thoth | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | Bedrock | $$$ |
| Hermes | `ollama/llama3.1:8b` | Ollama | Free |
| Hephaestus | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | Bedrock | $$$ |
| Janus | `bedrock/anthropic.claude-3-5-haiku-20241022-v1:0` | Bedrock | $$ |

**Cost per mission:** $0.03–$0.15 depending on complexity.

### 12.2 Integration

```python
class AgentNode:
    async def invoke(self, messages: list[dict], **kwargs) -> str:
        response = await litellm.acompletion(
            model=self.model,
            messages=[{"role": "system", "content": self.soul}, *messages],
            **kwargs
        )
        return response.choices[0].message.content
```

### 12.3 Runtime Requirements (FR-13, FR-14, FR-15)

- **FR-13:** Agent runtime must emit structured lifecycle events (`start`, `progress`, `result`, `error`)
- **FR-14:** Side-effecting tool calls must support idempotency keys
- **FR-15:** Runtime must record retry metadata for retried operations

---

## 13. API Specification

### 13.1 Endpoints

| Method | Path | Description | Idempotency | FR |
|---|---|---|---|---|
| POST | `/mission/start` | Create + start mission | `Idempotency-Key` header | FR-1 |
| GET | `/mission/{id}/state` | Current mission state | — | FR-4 |
| GET | `/mission/{id}/stream` | SSE event stream | Reconnect via `lastEventId` | FR-18 |
| POST | `/mission/{id}/approvals/{approval_id}/decision` | Approve/reject HITL request by approval ID | `Idempotency-Key` header | FR-22 |
| POST | `/mission/{id}/cancel` | Cancel mission | `Idempotency-Key` header | FR-3 |
| POST | `/mission/{id}/pause` | Pause mission | `Idempotency-Key` header | FR-3 |
| POST | `/mission/{id}/resume` | Resume paused mission | `Idempotency-Key` header | FR-3 |
| GET | `/missions` | List with filtering | — | FR-4 |
| GET | `/agents` | List agent definitions | — | — |
| GET | `/agents/{name}/soul` | Agent soul.md content | — | FR-12 |
| GET | `/health` | Dependency health check | — | — |

### 13.2 Idempotency Contract (FR-14)

All side-effecting endpoints (`POST`) accept an `Idempotency-Key` header. If the key has been seen within the TTL window (default 24h), the response is replayed without re-executing the action.

### 13.3 Error Response Contract

```json
{
  "error": {
    "code": "MISSION_NOT_FOUND",
    "message": "Mission with ID 'xyz' does not exist.",
    "details": {},
    "request_id": "req-uuid"
  }
}
```

| Code | HTTP | Description |
|---|---|---|
| `MISSION_NOT_FOUND` | 404 | Mission ID doesn't exist |
| `APPROVAL_NOT_FOUND` | 404 | Approval ID doesn't exist for mission |
| `APPROVAL_ALREADY_DECIDED` | 409 | Approval request already resolved |
| `MISSION_NOT_RUNNING` | 409 | Action requires running mission |
| `MISSION_NOT_AWAITING_APPROVAL` | 409 | No pending approval |
| `IDEMPOTENCY_CONFLICT` | 409 | Key reused with different payload |
| `INVALID_AUTHORITY_MODE` | 400 | Unknown authority mode |
| `GOAL_EMPTY` | 400 | Empty goal string |
| `INTERNAL_ERROR` | 500 | Unhandled exception |
| `NATS_UNAVAILABLE` | 503 | Cannot connect to NATS |
| `DATABASE_UNAVAILABLE` | 503 | Cannot connect to PostgreSQL |

---

## 14. Mission Control UI (FR-26 to FR-36)

### 14.1 Design System (FR-33 to FR-36)

**V3 "Cyber-Sovereign Industrialism" is LOCKED.** Source of truth: `branding/brand-identity.md`

| Token | Value | Usage |
|---|---|---|
| `--bg-void` | `#0A0A0B` | Main background (Layer 0) |
| `--bg-plate` | `#121214` | Component background (Layer 1) |
| `--bg-active` | `#18181B` | Hover state |
| `--signal-amber` | `#FFB900` | Primary signal, active states, CTAs |
| `--border-primary` | `#27272A` | Panel borders (Zinc-800) |
| `--border-active` | `#3F3F46` | Active borders (Zinc-700) |
| `--border-highlight` | `#FFB900` | Highlight borders (Amber) |
| Grid | `rgba(39,39,42,0.2)` | 40px crosshair grid pattern |
| `--font-display` | Space Grotesk | Headings, module titles (500, 700) |
| `--font-ui` | Geist Sans | UI text, body (400, 500) |
| `--font-mono` | Geist Mono / JetBrains Mono | Code, logs |
| `--radius` | `0px` global, `2px` inputs | `>4px` forbidden |

**Agent Signature Colors:**

| Agent | Hex |
|---|---|
| Synarch | `#FFB900` |
| Zeus | `#3B82F6` |
| Thoth | `#8B5CF6` |
| Hermes | `#06B6D4` |
| Hephaestus | `#F43F5E` |
| Janus | `#10B981` |

### 14.2 Desktop Layout — Five-Panel Cockpit (FR-26 to FR-32)

```
┌──────────────────────────────────────────────────────────────┐
│  MISSION CONTROL — Synarch Engine              [Status Bar] │
├──────────────────────┬───────────────────────────────────────┤
│  🗺️ AGENT TOPOLOGY   │  💬 THOUGHT STREAM                    │
│  (Active agents,     │  (Real-time event log, color-coded,  │
│   connections, state)│   filterable by agent/event type)    │
├──────────────────────┼───────────────────────────────────────┤
│  📋 TASK BOARD        │  📦 DELIVERABLES                      │
│  (Kanban: Pending →  │  (Tabbed: Research|Code|Reviews|     │
│   Active → Review →  │   Synthesis, with provenance links)  │
│   Done)              │                                       │
├──────────────────────┴───────────────────────────────────────┤
│  ⌨️ COMMAND INPUT  [mode: supervised ▾]              [Send] │
└──────────────────────────────────────────────────────────────┘
```

### 14.3 Mobile Layout — Priority Stack

1. Mission phase + approval queue
2. Current task and blockers
3. Deliverables summary
4. Recent events (collapsed)

### 14.4 Approval Inbox (Overlay)

- Amber-bordered modal over cockpit
- Shows: requesting agent, action, risk level, context
- Buttons: APPROVE (amber) | REJECT (red)
- Optional reason text input
- Countdown timer (FR-25 timeout policy)

---

## 15. Human-in-the-Loop (FR-21 to FR-25)

### 15.1 The Rule of Two

High-impact actions require approval from the agent's superior AND God. In PoC: **God approves all high-impact actions** (simplified chain).

### 15.2 Actions Requiring Approval

| Action | Agent | Risk | FR |
|---|---|---|---|
| Write files to disk | Hephaestus | Medium | FR-43 |
| Execute generated code | Hephaestus | High | FR-43 |
| External API requests | Hermes | Medium | FR-43 |
| Final mission delivery | Synarch | Low | FR-43 |

### 15.3 Approval Lifecycle (FR-21 to FR-25)

```
1. Agent sets state.needs_approval = True
2. Graph interrupt (LangGraph interrupt())
3. Approval record created in approvals table (FR-24)
4. Mission → AWAITING_APPROVAL
5. NATS: synarch.approval.{id}.requested
6. SSE → Mission Control approval modal
7. God: APPROVE or REJECT (with optional reason)
8. POST /mission/{id}/approvals/{approval_id}/decision
9. Approval record updated (decided_by, decided_at, reason)
10. Graph resumes with decision
11. If timeout (FR-25): auto-reject after configurable period (default 300s)
```

### 15.4 Authority Modes

| Mode | Behavior |
|---|---|
| `guided` | God approves every significant action |
| `supervised` | God approves only high-risk actions (default) |
| `free_rein` | Agents act autonomously, God reviews at end |

---

## 16. Security & Governance (FR-41 to FR-44)

### 16.1 Hierarchy Enforcement (FR-43)

| Rule | Implementation |
|---|---|
| Adjacent communication only | Graph edges enforce hierarchy |
| God → Synarch only | API routes all input through Synarch |
| No skip-level access | No graph edge from Tier 3 to Tier 1 |
| Chain of command delegation | Zeus→Hephaestus, not Zeus→Hermes |

### 16.2 Gateway Auth Model (FR-41)

- PoC: No auth (local only)
- Gateway supports explicit mode configuration for future auth
- Proxy-safe IP resolution (pattern from OpenClaw deep-dive)

### 16.3 Audit Attribution (FR-42)

- Control-plane actions include actor/device/session metadata
- Approval decisions are persisted with `decided_by`, `decided_at`
- All events include `agent` field for attribution

### 16.4 Secrets Protection (FR-44)

- `.env` gitignored, `.env.example` committed
- No secrets in soul.md, state objects, NATS events, or UI logs
- Event payloads are redaction-safe by contract

### 16.5 Code Execution Safety

- Generated code written to `output/` only (never system paths)
- Execution requires HITL approval in `supervised`/`guided` modes
- Full sandboxing (Docker/WASM) deferred to Phase 2

---

## 17. Testing & Validation

### 17.1 Testing Pyramid

| Layer | Coverage | Focus |
|---|---|---|
| Unit (60%) | State transitions, event schemas, routing logic, repositories | pytest |
| Integration (30%) | Graph→PG checkpoint, Agent→NATS→SSE, mission lifecycle | pytest-asyncio + Docker services |
| E2E (10%) | Full mission happy path, HITL flow, cancellation | pytest + httpx |

### 17.2 Contract Tests (from Codex)

| Contract | Verification |
|---|---|
| API error envelope shape | All errors match `{"error":{"code","message","details","request_id"}}` |
| Event schema version compat | EventEnvelope v1.0 payloads parse correctly |
| Idempotency handler | Duplicate key returns cached response, not re-execution |
| Approval state machine | PENDING→APPROVED/REJECTED transitions are deterministic |

### 17.3 Acceptance Test Scenarios

1. Happy path: mission completes with visible provenance
2. Sensitive action pauses and resumes after operator decision
3. Duplicate idempotency key does not duplicate side effect
4. Crash/restart recovery preserves mission continuity
5. Mission cancellation stops all agents cleanly

---

## 18. Observability & Telemetry

### 18.1 Structured Logging

All components emit JSON logs with: `timestamp`, `level`, `component`, `mission_id`, `message`, `metadata`.

### 18.2 Metrics

| Metric | Target | Source |
|---|---|---|
| Mission start-to-first-event | ≤1.5s p95 | API layer |
| Event backend-to-UI latency | ≤300ms p95 | NATS→SSE |
| Mission recovery success rate | ≥95% | Integration tests |
| Approval loop completion rate | ≥99% | Approval service |
| Event parity (backend vs UI) | ≥99.5% | SSE verification |
| Brand token compliance | 100% | UI audit |

### 18.3 NATS as Telemetry Backbone

- Real-time monitoring via NATS subscription
- Audit trail by persisting events to `mission_events` table
- Debugging via event replay
- Alerting via `synarch.agent.*.error` subscription

### 18.4 Health Check

```json
GET /health → { "status": "ok", "dependencies": { "postgresql", "nats", "qdrant", "ollama", "bedrock" } }
```

---

## 19. Infrastructure & Deployment

### 19.1 Topology (PoC)

- Backend (FastAPI + LangGraph): **runs on host**
- Frontend (Next.js): **runs on host**
- Infrastructure (NATS, PostgreSQL, Qdrant, Ollama): **Docker Compose**

### 19.2 Startup

```bash
docker compose -f infra/docker-compose.yml up -d
cd backend && python main.py
cd apps/web && npm run dev
open http://localhost:3000
```

### 19.3 Environment

```env
DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch
NATS_URL=nats://localhost:4222
QDRANT_URL=http://localhost:6333
OLLAMA_API_BASE=http://localhost:11434
AWS_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
```

---

## 20. Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Reliability: mission durability across restart | No in-memory-only state |
| NFR-2 | Performance: SSE/event latency | ≤300ms p95 |
| NFR-3 | Observability: structured logs + event tracing | All mission-critical actions |
| NFR-4 | Maintainability: runtime boundaries decoupled | Orchestrator/Runtime/EventBus/UI independent |
| NFR-5 | Security: auth + approval + idempotency | Test-covered |
| NFR-6 | Startup time | <2 minutes all services |
| NFR-7 | Cost per mission | <$0.20 frontier, $0 local |
| NFR-8 | Code quality | mypy + tsc --strict, zero warnings |

---

## 21. Functional Requirements Index

| FR | Description | Section | Priority |
|---|---|---|---|
| FR-1 | Create mission with goal, mode, constraints | §9, §13 | P0 |
| FR-2 | Durable mission record with unique ID and thread context | §9 | P0 |
| FR-3 | Mission states: created, planning, executing, awaiting_approval, reviewing, revising, synthesizing, paused, failed, completed, cancelled | §8 | P0 |
| FR-4 | Mission state queryable at any time via API | §13 | P0 |
| FR-5 | Mission resumes from persisted state after restart | §9, §10 | P0 |
| FR-6 | LangGraph StateGraph as orchestration core | §10 | P0 |
| FR-7 | Graph supports conditional branches based on state | §10 | P0 |
| FR-8 | Graph supports interrupt/resume for approvals | §10, §15 | P0 |
| FR-9 | Graph includes validation nodes for policy checks | §10 | P0 |
| FR-10 | Graph checkpoints persist to PostgreSQL | §10 | P0 |
| FR-11 | All model calls route through litellm | §12 | P0 |
| FR-12 | Agent system prompts load from soul.md | §6 | P0 |
| FR-13 | Agent runtime emits structured lifecycle events | §11, §12 | P0 |
| FR-14 | Side-effecting tool calls support idempotency keys | §11, §13 | P0 |
| FR-15 | Runtime records retry metadata for retried operations | §12 | P1 |
| FR-16 | NATS required for runtime event publication | §11 | P0 |
| FR-17 | Event subjects include mission/agent/task/deliverable/approval domains | §11 | P0 |
| FR-18 | SSE endpoint streams events to Mission Control in near real time | §11, §13 | P0 |
| FR-19 | Event payloads typed and versioned (schema_version) | §11 | P0 |
| FR-20 | Events include mission ID, timestamp, stage, source actor, provenance | §11 | P0 |
| FR-21 | Sensitive operations create explicit approval requests | §15 | P0 |
| FR-22 | Operator can approve/reject with reason | §15 | P0 |
| FR-23 | Runtime pauses awaiting decision, resumes deterministically | §15 | P0 |
| FR-24 | Approval outcomes persisted and visible in history | §9, §15 | P0 |
| FR-25 | Approval timeout policy configurable (default 300s) | §15 | P1 |
| FR-26 | Mission Control displays live mission phase and status | §14 | P0 |
| FR-27 | UI renders typed event stream with category filters | §14 | P0 |
| FR-28 | UI provides approval queue actions | §14 | P0 |
| FR-29 | UI displays deliberation timeline (stage progression) | §14 | P1 |
| FR-30 | UI displays tasks, blockers, and deliverables | §14 | P0 |
| FR-31 | UI supports mission start and inspect flows | §14 | P0 |
| FR-32 | UI shows execution mode and current graph branch | §14 | P1 |
| FR-33 | V3 design tokens as source-of-truth CSS custom properties | §14 | P0 |
| FR-34 | Components use V3 primitives (void/plate/border/amber) | §14 | P0 |
| FR-35 | Sharp-radius and border-first rules enforced | §14 | P0 |
| FR-36 | Brand compliance checklist gates PR acceptance for UI | §14 | P1 |
| FR-37 | Browser tools follow Playwright-MCP deterministic pattern | §22 | P2 |
| FR-38 | Integration execution scoped by actor/user/org context | §22 | P2 |
| FR-39 | External trigger events routeable into mission workflows | §22 | P2 |
| FR-40 | MCP tool dev loop supports inspect/debug workflow | §22 | P2 |
| FR-41 | Gateway auth supports explicit mode configuration | §16 | P1 |
| FR-42 | Control-plane actions audit-attributed (actor/device/session) | §16 | P0 |
| FR-43 | Unsafe/irreversible operations blocked without approval | §15, §16 | P0 |
| FR-44 | Secrets never emitted in event streams or UI logs | §16 | P0 |

---

## 22. Reference Adoption Strategy

Adoption strategy traced to deep-dives and aligned with ADR-004 decisions:

| # | Reference | Decision | Pattern | Deep-Dive | Delivery Phase |
|---|---|---|---|---|---|
| 1 | LangGraph | Adopt | Postgres checkpointer, interrupts, conditional routing | `docs/04-reference-deep-dives/langgraph/` | Milestones A-B |
| 2 | OpenClaw | Adopt Patterns | Control-plane idempotency, auth rigor, approval lifecycle | `docs/04-reference-deep-dives/openclaw/` | Milestones B-D |
| 3 | CrewAI | Adopt Patterns | Event taxonomy, listener-style extension points | `docs/04-reference-deep-dives/crewAI/` | Milestone B |
| 4 | Autogen | Reference Only | MCP workbench and multi-agent tooling patterns | `docs/04-reference-deep-dives/autogen/` | Reference only |
| 5 | Letta | Adopt Patterns | Memory block model, run-step completion semantics | `docs/04-reference-deep-dives/letta/` | Milestone C+ |
| 6 | LLM Council+ | Adopt Patterns | Staged deliberation UX, mode visibility | `docs/04-reference-deep-dives/llm-council-plus/` | Milestone C |
| 7 | Playwright-MCP | Adopt | Deterministic browser specialist tooling | `docs/04-reference-deep-dives/playwright-mcp/` | Phase 2 |
| 8 | MCP-Use | Adopt Patterns | Session management, inspector dev loop | `docs/04-reference-deep-dives/mcp-use/` | Phase 2 |
| 9 | Smolagents | Adopt Patterns | Secure code execution policy, telemetry shape | `docs/04-reference-deep-dives/smolagents/` | Milestone D / Phase 2 |
| 10 | Magentic-UI | Adopt Patterns | Co-planning, guarded action UX | `docs/04-reference-deep-dives/magentic-ui/` | Milestone C |
| 11 | Composio | Adopt Patterns | User/org scoped integration routing | `docs/04-reference-deep-dives/composio/` | Phase 2 |
| 12 | Swarms | Reference Only | Architecture catalog/pattern source; no runtime migration or fork | `docs/04-reference-deep-dives/swarms/` | Reference only |

Governance: `docs/02-architecture/reference-adoption-matrix.md` and `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md`

---

## 23. Implementation Phases

Aligned with ADR-004 W1-W5 workstreams:

### Milestone A: Runtime Foundation (W1)
- [ ] PostgreSQL schema (missions, tasks, deliverables, approvals, events)
- [ ] MissionRepository + ApprovalRepository
- [ ] LangGraph AsyncPostgresSaver checkpointer
- [ ] Replace in-memory MISSIONS dict
- **Exit:** Restart-resume test passes. Mission emits typed events end-to-end.

### Milestone B: Governed Orchestration (W2)
- [ ] Conditional routing after planning
- [ ] Janus review gate with REVISE/PASS
- [ ] LangGraph interrupt() for HITL
- [ ] Idempotency contract for side effects
- **Exit:** Approval flow functional. Duplicate side-effects deduped.

### Milestone C: Mission Control Cockpit (W3-W4)
- [ ] Live event stream UI
- [ ] Approval queue
- [ ] Deliberation timeline
- [ ] Task board + deliverables
- [ ] Command input with mode selector
- **Exit:** Operator can run mission from UI start to completion.

### Milestone D: Brand & Hardening (W5)
- [ ] V3 token/component enforcement
- [ ] Security and observability hardening
- [ ] Acceptance tests passing
- [ ] Docs/memory-bank synced
- **Exit:** Brand compliance checklist passes. Governance docs updated.

---

## 24. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| State drift between graph and persistence | Medium | High | Checkpoint-at-phase-boundary + reconciliation test |
| Bedrock API latency | Medium | Medium | litellm fallback to Ollama; timeout + retry |
| Event flood causes UI lag | Medium | Medium | Event batching + severity filters |
| Approval UX bottlenecks operator | Low | Medium | Priority queueing + SLA visibility |
| LangGraph checkpoint schema breaks on upgrade | Low | High | Pin version; test migrations in CI |
| NATS message loss | Low | Medium | JetStream persistence; sequence gap detection |
| Agent hallucination produces wrong code | High | Medium | Janus review gate + HITL for execution |
| Context window overflow | Medium | High | Token tracking + summarization |
| Brand drift over time | Medium | Low | Token lint in PR process + design review gates |
| Reference adoption drift | Medium | Medium | Mandatory matrix/deep-dive updates in architecture PRs |
| Scope creep | High | Medium | Strict PRD scope; YAGNI enforcement |

---

## 25. Definition of Done

v1.0 is complete **only when ALL are true:**

1. ✅ W1-W5 workstreams from ADR-004 are implemented and verified
2. ✅ Mission recovery after restart proven by automated test
3. ✅ HITL approval interrupt/resume is live and audited
4. ✅ Agent runtime uses litellm and publishes structured NATS events
5. ✅ Mission Control is operational and real-time
6. ✅ V3 brand tokens/components fully integrated in Mission Control
7. ✅ Reference adoption matrix reflects implemented patterns with evidence
8. ✅ Memory-bank `progress.md` and `activeContext.md` are updated

---

## 26. Open Questions

| # | Question | Impact | Decision Needed By |
|---|---|---|---|
| 1 | Which execution modes mandatory at launch? (`guided`, `supervised`, `free_rein`) or subset? | Scope | Milestone A |
| 2 | Default approval timeout and fallback behavior on timeout? (auto-reject vs auto-approve) | HITL | Milestone B |
| 3 | Mission retention period for persisted checkpoints/events? | Storage | Milestone D |
| 4 | Which actions are classified as "sensitive" in v1.0 policy baseline? | Security | Milestone B |
| 5 | Minimum provenance depth required in deliverables for compliance? | Traceability | Milestone C |

---

## 27. Out of Scope — Phase 2+ Roadmap

| Feature | Phase |
|---|---|
| Cloud deployment (Kubernetes, Terraform) | 2 |
| Self-evolution (prompt optimization) | 2 |
| Consensus voting (AAD) | 2 |
| WASM sandboxing | 2 |
| Multi-user support (RBAC) | 2 |
| Full audit trail | 2 |
| NotebookLM RAG | 2 |
| Agent spawning | 3 |
| GraphRAG (Neo4j) | 3 |
| MCP tool marketplace | 3 |
| Plugin system | 3 |

---

## 28. Glossary

| Term | Definition |
|---|---|
| **God** | The human user — source of all authority |
| **Synarch** | The CEO agent (Tier 1) — supreme orchestrator |
| **Soul** | Markdown file defining agent identity, directives, constraints, SOPs |
| **Mission** | Goal submitted by God, decomposed and executed by hierarchy |
| **Nervous System** | NATS event bus — all agent communication |
| **Mission Control** | Next.js dashboard — God's window into the hierarchy |
| **Rule of Two** | High-impact actions require approval from superior AND God |
| **HITL** | Human-in-the-Loop — God approves/rejects agent actions |
| **EventEnvelope** | Canonical NATS message format — typed, versioned, mission-scoped |
| **Checkpoint** | LangGraph state snapshot in PostgreSQL — crash recovery |
| **litellm** | Provider-agnostic LLM abstraction — all model calls go through it |
| **Tier** | Hierarchy level: 0 (God) → 1 (CEO) → 2 (C-Suite) → 3 (Specialist) |
| **Authority Mode** | Agent autonomy level: guided, supervised, free_rein |
| **Deliverable** | Output: research report, code, review verdict, synthesis |
| **Idempotency Key** | Header preventing duplicate execution of side-effecting operations |
| **Provenance** | Links from deliverables back to their source events/tasks |

---

## 29. Source Index

| # | Document | Path |
|---|---|---|
| 1 | ADR-004: Gap Closure Contract | `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md` |
| 2 | Reference Adoption Matrix | `docs/02-architecture/reference-adoption-matrix.md` |
| 3 | Mission Control UX Strategy | `docs/03-product/mission-control-ui-ux-and-functionality-strategy.md` |
| 4 | Reference Deep-Dives Index | `docs/04-reference-deep-dives/README.md` |
| 5 | Gap Closure Implementation Plan | `docs/plans/2026-02-19-gap-closure-and-reference-adoption.md` |
| 6 | V3 Design System | `branding/brand-identity.md` |
| 7 | Agent Souls | `docs/agents/*/soul.md` |
| 8 | Claude PRD (superseded) | `docs/01-requirements/prd-1.0-claude.md` |
| 9 | Codex PRD (superseded) | `docs/01-requirements/prd-1.0-codex.md` |
| 10 | Comparison Analysis | `docs/01-requirements/prd-comparison-claude-vs-codex.md` |

---

## 30. Approval

| Role | Name | Date | Status |
|---|---|---|---|
| God (Project Owner) | PraxLannister | 2026-02-20 | ⏳ Pending Review |
| Architect (Claude) | Claude Opus 4 | 2026-02-20 | ✅ Drafted |
| Architect (Codex) | GPT-5.2 | 2026-02-20 | ✅ Contributed |

**Version History:**

| Version | Date | Authors | Changes |
|---|---|---|---|
| 0.1 | 2026-02-13 | Cline + Antigravity | Initial `poc-prd.md` draft |
| 1.0-claude | 2026-02-20 | Claude | 1,645-line exhaustive spec |
| 1.0-codex | 2026-02-19 | Codex | 501-line execution-focused spec (FR-1 to FR-44) |
| **1.0-final** | **2026-02-20** | **Claude + Codex** | **Merged: 30 sections, all gaps closed** |

---

*"In the Synarch, every god has a throne. Every throne has a purpose. No god acts alone."*
