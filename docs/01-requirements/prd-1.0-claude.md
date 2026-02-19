# Synarch Engine — Product Requirements Document v1.0

**Author:** Claude (Opus 4) for PraxLannister  
**Version:** 1.0 | **Status:** Draft | **Date:** 2026-02-20  
**Scope:** PoC (Proof of Concept) — exhaustive specification  
**Supersedes:** `poc-prd.md` (2026-02-13, incomplete draft)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement & Value Proposition](#2-problem-statement--value-proposition)
3. [Target Users & Personas](#3-target-users--personas)
4. [User Stories](#4-user-stories)
5. [The Hierarchy — Agent Specifications](#5-the-hierarchy--agent-specifications)
6. [System Architecture](#6-system-architecture)
7. [Mission Lifecycle State Machine](#7-mission-lifecycle-state-machine)
8. [Persistence Architecture](#8-persistence-architecture)
9. [Orchestration Engine — LangGraph](#9-orchestration-engine--langgraph)
10. [Nervous System — NATS Event Contract](#10-nervous-system--nats-event-contract)
11. [Model Routing — litellm](#11-model-routing--litellm)
12. [API Specification](#12-api-specification)
13. [Mission Control UI](#13-mission-control-ui)
14. [Human-in-the-Loop (HITL)](#14-human-in-the-loop-hitl)
15. [Security Model](#15-security-model)
16. [Testing Strategy](#16-testing-strategy)
17. [Observability & Telemetry](#17-observability--telemetry)
18. [Infrastructure & Deployment](#18-infrastructure--deployment)
19. [Non-Functional Requirements](#19-non-functional-requirements)
20. [Implementation Phases](#20-implementation-phases)
21. [Risk Register](#21-risk-register)
22. [Out of Scope — Phase 2+ Roadmap](#22-out-of-scope--phase-2-roadmap)
23. [Glossary](#23-glossary)
24. [Approval](#24-approval)

---

## 1. Executive Summary

**Synarch** (syn=together + arch=govern) is an open-source, production-grade **Autonomous Multi-Agent Orchestration Engine**. Think: the "Linux of autonomous agent teams."

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

## 2. Problem Statement & Value Proposition

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
5. **Mission Control dashboard** — See everything: agent thoughts, task flow, deliverables. The UI IS the differentiator.
6. **Open-source, self-hostable** — `docker compose up` and you're running.

### Value Proposition by User Type

| User | Value |
|---|---|
| **Solo developer** | An AI team that works on your project 24/7 while you sleep |
| **Startup founder** | Scale operations without hiring — agents handle research, code, review |
| **Open-source contributor** | The self-hostable alternative to closed SaaS agent platforms |
| **Enterprise architect** | A production-grade reference for hierarchical agent orchestration |

---

## 3. Target Users & Personas

### Persona 1: The Solo Builder

- **Name:** Arjun, 28, full-stack developer
- **Context:** Building a SaaS product solo. Needs help with research, code review, and boilerplate.
- **Pain:** Can't afford to hire. ChatGPT is one-shot — no persistent multi-step execution.
- **Goal:** Give a mission, go to sleep, wake up to a researched analysis with working code.
- **Success metric:** Mission completes autonomously with source-cited research and tested code.

### Persona 2: The Startup Operator

- **Name:** Maya, 33, CEO of a 3-person startup
- **Context:** Needs marketing research, competitor analysis, and engineering prototypes done fast.
- **Pain:** Existing agent tools are too technical to set up. No visibility into what agents are doing.
- **Goal:** One dashboard to see all agent activity. Non-technical enough to understand the flow.
- **Success metric:** Mission Control shows real-time progress without needing to read logs.

### Persona 3: The Open-Source Power User

- **Name:** Dmitri, 40, DevOps engineer and OSS contributor
- **Context:** Evaluates agent frameworks for self-hosting. Security and observability are non-negotiable.
- **Pain:** Every agent framework is a black box with no persistence and no permission model.
- **Goal:** Fork, customize, deploy on own infrastructure with full control.
- **Success metric:** System is self-hostable, extensible, and transparent in its decision-making.

---

## 4. User Stories

### Epic 1: Mission Execution

| ID | As a... | I want to... | So that... | Priority | Acceptance Criteria |
|---|---|---|---|---|---|
| US-1.1 | God (user) | Submit a natural language goal via Mission Control | The Synarch decomposes and executes it | P0 | Goal accepted, plan visible in <5s |
| US-1.2 | God | See real-time agent thoughts and actions | I understand what's happening without reading logs | P0 | SSE stream updates Mission Control in <1s |
| US-1.3 | God | See the final deliverable(s) | I can use the output directly | P0 | Deliverables panel shows research report + code |
| US-1.4 | God | Kill or pause a running mission | I can stop runaway agents | P0 | Mission transitions to CANCELLED/PAUSED state |

### Epic 2: Agent Hierarchy & Delegation

| ID | As a... | I want to... | So that... | Priority | Acceptance Criteria |
|---|---|---|---|---|---|
| US-2.1 | Synarch (CEO) | Decompose a goal into sub-missions | Each C-Suite agent gets a clear objective | P0 | Plan has ≥2 sub-tasks with assigned agents |
| US-2.2 | Zeus (CTO) | Delegate engineering tasks to Hephaestus | Code is written by the specialist | P0 | Task assignment visible in NATS events |
| US-2.3 | Thoth (CRO) | Delegate research tasks to Hermes | Information is gathered by the specialist | P0 | Research results include source citations |
| US-2.4 | Janus (Reviewer) | Review deliverables from any agent | Quality is verified before delivery to God | P0 | Review verdict (PASS/FAIL/REVISE) is emitted |

### Epic 3: Durability & Recovery

| ID | As a... | I want to... | So that... | Priority | Acceptance Criteria |
|---|---|---|---|---|---|
| US-3.1 | God | Restart the backend without losing mission state | Crashes don't destroy progress | P0 | Mission resumes from last checkpoint after restart |
| US-3.2 | God | See mission history after completion | Past missions are auditable | P1 | GET `/mission/{id}/state` returns completed mission |

### Epic 4: Human-in-the-Loop

| ID | As a... | I want to... | So that... | Priority | Acceptance Criteria |
|---|---|---|---|---|---|
| US-4.1 | God | Approve or reject agent actions that require permission | Dangerous operations don't execute without my consent | P0 | Pending approval pauses graph; approve/reject resumes |
| US-4.2 | God | See why an agent is asking for approval | I can make an informed decision | P1 | Approval request includes action description and risk reason |

### Epic 5: Observability

| ID | As a... | I want to... | So that... | Priority | Acceptance Criteria |
|---|---|---|---|---|---|
| US-5.1 | God | See which agents are active and their current state | I know the system health | P0 | Agent topology shows active/idle/waiting states |
| US-5.2 | God | See a timeline of agent events | I can trace decision flow | P1 | Thought stream is chronologically ordered with timestamps |
| US-5.3 | God | See task progression (kanban) | I know what's in progress vs done | P1 | Task board reflects real-time state changes |

---

## 5. The Hierarchy — Agent Specifications

### 5.1 Tier Structure

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

**Hierarchy Rules:**
- Agents can ONLY communicate with their direct superior and direct reports
- Tier 3 agents cannot contact Tier 1 directly — must go through Tier 2
- God speaks ONLY to Synarch — never directly to specialists
- Synarch is the ONLY agent that can address God

### 5.2 Agent Specification Table

| Agent | Tier | Role | Model (litellm) | Soul File | Inputs | Outputs | Tools (PoC) |
|---|---|---|---|---|---|---|---|
| **God** | 0 | Human User | N/A | `docs/agents/god/soul.md` | N/A | Mission goals, approvals, feedback | Mission Control UI |
| **Synarch** | 1 | CEO / Supreme Orchestrator | `bedrock/anthropic.claude-opus-4-20250514-v1:0` | `docs/agents/synarch/soul.md` | God's goal | Mission plan, delegation orders, final synthesis | Plan decomposition, agent delegation |
| **Zeus** | 2 | CTO / Engineering Commander | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | `docs/agents/zeus/soul.md` | Engineering objectives from Synarch | Technical plans, task assignments | Task creation, code review delegation |
| **Thoth** | 2 | CRO / Knowledge Keeper | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | `docs/agents/thoth/soul.md` | Research objectives from Synarch | Research plans, knowledge synthesis | Research task creation, source evaluation |
| **Hermes** | 3 | Researcher / Information Gatherer | `ollama/llama3.1:8b` | `docs/agents/hermes/soul.md` | Research tasks from Thoth | Source-cited research findings | Web search, document retrieval |
| **Hephaestus** | 3 | Engineer / Code Builder | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | `docs/agents/hephaestus/soul.md` | Engineering tasks from Zeus | Working code with tests | Code generation, file write |
| **Janus** | 3 | Reviewer / Quality Gate | `bedrock/anthropic.claude-3-5-haiku-20241022-v1:0` | `docs/agents/janus/soul.md` | Deliverables from any agent | Structured review verdicts | Review checklist evaluation |

### 5.3 Agent Soul System

Every agent loads its `soul.md` file as the foundation of its system prompt. A soul defines:

1. **Identity** — Name, title, mythology, personality traits
2. **Hierarchy position** — Tier, who they report to, who reports to them
3. **Core directives** — What the agent MUST do
4. **Constraints** — What the agent MUST NOT do
5. **Communication protocol** — How to format messages, when to escalate
6. **Standard Operating Procedures** — Step-by-step workflows for common tasks

**Implementation:** `AgentNode.load_soul()` reads the markdown file and prepends it to every LLM call as system prompt context.

### 5.4 Future Agents (Phase 2+)

| Agent | Tier | Role | Mythology |
|---|---|---|---|
| Athena | 2 | CPO (Product) | Greek goddess of wisdom and strategy |
| Odin | 2 | CISO (Security) | Norse all-father, seeker of knowledge |
| Midas | 2 | CFO (Finance) | Greek king with the golden touch |
| Apollo | 2 | CMO (Marketing) | Greek god of communication and art |
| Vishwakarma | 3 | Infrastructure Engineer | Hindu divine architect |
| Saraswati | 3 | Documentation Writer | Hindu goddess of knowledge |

---

## 6. System Architecture

### 6.1 System Topology

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
│  GET  /mission/{id}/state    POST /mission/{id}/approve     │
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

### 6.2 Component Responsibilities

| Component | Responsibility | Technology |
|---|---|---|
| **Gateway** | HTTP API, SSE streaming, request validation, CORS | FastAPI |
| **Orchestrator** | Agent execution graph, state management, routing decisions | LangGraph StateGraph |
| **Nervous System** | Event pub/sub, subject hierarchy, real-time propagation | NATS + JetStream |
| **Mission Store** | Mission metadata, API query support, status tracking | PostgreSQL (thin table) |
| **Checkpoint Store** | Graph execution state, crash recovery, resume | PostgreSQL (LangGraph checkpointer) |
| **Vector Memory** | Semantic search, per-agent knowledge, shared namespaces | Qdrant |
| **Model Router** | Provider-agnostic LLM calls, cost-optimized routing | litellm |
| **Mission Control** | Real-time dashboard, agent visualization, HITL approvals | Next.js + shadcn/ui |

### 6.3 Data Flow — Mission Execution

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

## 7. Mission Lifecycle State Machine

### 7.1 Mission States

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

### 7.2 State Definitions

| State | Description | Triggers Entry | Triggers Exit |
|---|---|---|---|
| `CREATED` | Mission record exists, graph not yet invoked | POST `/mission/start` | Graph invocation begins |
| `PLANNING` | Synarch is decomposing the goal | Graph enters Synarch node | Plan produced with sub-tasks |
| `EXECUTING` | Agents are working on assigned tasks | Plan delegation begins | All tasks report completion |
| `AWAITING_APPROVAL` | HITL interrupt — God must approve/reject | Agent requests Rule of Two permission | God approves or rejects |
| `REVIEWING` | Janus is evaluating deliverables | All execution tasks complete | Janus emits verdict |
| `REVISING` | Agents are reworking based on review feedback | Janus verdict = REVISE | Revised deliverables submitted |
| `SYNTHESIZING` | Synarch is combining final deliverables | Review passed | Final output produced |
| `COMPLETED` | Mission finished successfully | Final output delivered to God | Terminal state |
| `PAUSED` | God paused the mission | POST `/mission/{id}/pause` | POST `/mission/{id}/resume` |
| `CANCELLED` | God cancelled the mission | POST `/mission/{id}/cancel` | Terminal state |
| `FAILED` | Unrecoverable error occurred | Exception in agent node | Terminal state (with error context) |

### 7.3 State Persistence

- Mission state is persisted as a `status` field in the `missions` PostgreSQL table
- State transitions emit NATS events: `synarch.mission.{id}.state_changed`
- Every state transition is logged with timestamp, previous state, and trigger reason
- LangGraph checkpoints independently track graph execution position

---

## 8. Persistence Architecture

### 8.1 Dual-Store Strategy

Synarch uses **two persistence layers** in PostgreSQL (same database, separate concerns):

| Store | Purpose | Schema Owner | Access Pattern |
|---|---|---|---|
| **Mission Metadata Store** | API queries, status tracking, mission listing | Synarch application | Fast reads by mission ID, status filtering, pagination |
| **LangGraph Checkpoint Store** | Graph execution state, crash recovery, resume | LangGraph checkpointer | Thread-scoped checkpoint reads/writes by graph runtime |

**Why two stores?** (Pattern from Letta deep-dive)
- The API layer should never deserialize graph checkpoints just to list missions
- Graph execution state is opaque to the API — only the orchestrator needs it
- Mission metadata is a thin, queryable projection of mission lifecycle

### 8.2 Mission Metadata Schema

```sql
CREATE TABLE missions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal            TEXT NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'CREATED',
    authority_mode  VARCHAR(20) NOT NULL DEFAULT 'supervised',
    plan            JSONB,                    -- Synarch's decomposed plan
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_context   JSONB,                    -- populated on FAILED
    thread_id       VARCHAR(64),              -- links to LangGraph checkpoint thread
    CONSTRAINT valid_status CHECK (status IN (
        'CREATED', 'PLANNING', 'EXECUTING', 'AWAITING_APPROVAL',
        'REVIEWING', 'REVISING', 'SYNTHESIZING',
        'COMPLETED', 'PAUSED', 'CANCELLED', 'FAILED'
    ))
);

CREATE TABLE tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    assigned_agent  VARCHAR(30) NOT NULL,
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    result          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    CONSTRAINT valid_task_status CHECK (status IN (
        'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'REVISION_NEEDED'
    ))
);

CREATE TABLE deliverables (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    task_id         UUID REFERENCES tasks(id),
    agent           VARCHAR(30) NOT NULL,
    type            VARCHAR(30) NOT NULL,      -- 'research_report', 'code', 'review_verdict', 'synthesis'
    content         JSONB NOT NULL,
    review_status   VARCHAR(20) DEFAULT 'PENDING_REVIEW',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE mission_events (
    id              BIGSERIAL PRIMARY KEY,
    mission_id      UUID NOT NULL REFERENCES missions(id),
    event_type      VARCHAR(60) NOT NULL,
    agent           VARCHAR(30),
    payload         JSONB NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_missions_status ON missions(status);
CREATE INDEX idx_tasks_mission ON tasks(mission_id);
CREATE INDEX idx_deliverables_mission ON deliverables(mission_id);
CREATE INDEX idx_events_mission ON mission_events(mission_id);
CREATE INDEX idx_events_created ON mission_events(created_at);
```

### 8.3 LangGraph Checkpoint Schema

Managed by `langgraph-checkpoint-postgres` package. Schema is bootstrapped automatically via `PostgresSaver.setup()`. Uses `thread_id` to scope checkpoints per mission.

### 8.4 Database Access Pattern

```python
# Application code uses asyncpg for mission metadata
# LangGraph uses its own PostgresSaver for checkpoints
# Both share the same PostgreSQL instance (database: synarch)

# Mission metadata: thin repository pattern
class MissionRepository:
    async def create(self, goal: str, authority: str) -> Mission
    async def get(self, mission_id: UUID) -> Mission
    async def update_status(self, mission_id: UUID, status: str) -> None
    async def list(self, status: str = None, limit: int = 50) -> List[Mission]

# LangGraph checkpointer: built-in
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)
```

---

## 9. Orchestration Engine — LangGraph

### 9.1 StateGraph Design

The orchestrator is a LangGraph `StateGraph` with typed state, conditional routing, and checkpoint-backed durability.

**Current state (skeleton):** Linear chain synarch→zeus→thoth→END  
**Target state (this PRD):** Conditional routing with HITL interrupts

### 9.2 Target Graph Topology

```
                        START
                          │
                          ▼
                    ┌──────────┐
                    │ SYNARCH  │ (Plan & Decompose)
                    └────┬─────┘
                         │
                    ┌────┴────┐ (Conditional: what does the plan require?)
                    ▼         ▼
              ┌──────────┐ ┌──────────┐
              │   ZEUS   │ │  THOTH   │ (Can run in parallel branches)
              └────┬─────┘ └────┬─────┘
                   │            │
              ┌────┴────┐ ┌────┴────┐
              ▼         ▼ ▼         ▼
        ┌───────────┐ ┌──────────┐
        │HEPHAESTUS │ │  HERMES  │
        └────┬──────┘ └────┬─────┘
             │             │
             └──────┬──────┘
                    ▼
              ┌──────────┐
              │  JANUS   │ (Review Gate)
              └────┬─────┘
                   │
              ┌────┴────┐ (Conditional: verdict?)
              ▼         ▼
        ┌──────────┐ ┌──────────┐
        │ SYNARCH  │ │ REVISE   │──► (back to EXECUTING agents)
        │(Synthesize)│ └──────────┘
        └────┬─────┘
             │
             ▼
            END
```

### 9.3 State Schema (Target)

```python
from typing import TypedDict, List, Optional, Annotated
from enum import Enum
import operator

class MissionPhase(str, Enum):
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    REVIEWING = "REVIEWING"
    REVISING = "REVISING"
    SYNTHESIZING = "SYNTHESIZING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"

class AgentMessage(TypedDict):
    agent: str
    role: str           # "thought", "delegation", "result", "review", "synthesis"
    content: str
    timestamp: str
    metadata: dict      # agent-specific data (sources, code paths, review scores)

class TaskAssignment(TypedDict):
    task_id: str
    agent: str
    description: str
    status: str         # PENDING, IN_PROGRESS, COMPLETED, REVISION_NEEDED
    result: Optional[str]

class MissionState(TypedDict):
    # Identity
    mission_id: str
    goal: str
    authority_mode: str     # "guided", "supervised", "free_rein"
    
    # Planning
    plan: List[str]
    plan_rationale: str
    
    # Execution
    phase: MissionPhase
    tasks: List[TaskAssignment]
    current_agent: str
    
    # Communication (append-only via reducer)
    messages: Annotated[List[AgentMessage], operator.add]
    
    # Review
    review_verdict: Optional[str]   # "PASS", "FAIL", "REVISE"
    review_feedback: Optional[str]
    revision_count: int
    
    # Output
    deliverables: List[dict]
    final_output: Optional[str]
    
    # Control
    needs_approval: bool
    approval_request: Optional[dict]
    error: Optional[str]
```

### 9.4 Conditional Routing Functions

```python
def route_after_planning(state: MissionState) -> list[str]:
    """Route to Zeus, Thoth, or both based on plan analysis."""
    plan = state.get("plan", [])
    needs_engineering = any("engineer" in t.lower() or "code" in t.lower() for t in plan)
    needs_research = any("research" in t.lower() or "investigate" in t.lower() for t in plan)
    
    routes = []
    if needs_engineering:
        routes.append("zeus")
    if needs_research:
        routes.append("thoth")
    if not routes:
        routes.append("zeus")  # default to engineering
    return routes

def route_after_review(state: MissionState) -> str:
    """Route based on Janus review verdict."""
    verdict = state.get("review_verdict", "PASS")
    if verdict == "REVISE" and state.get("revision_count", 0) < 3:
        return "revise"
    return "synthesize"

def should_request_approval(state: MissionState) -> str:
    """Check if HITL approval is needed before proceeding."""
    if state.get("needs_approval"):
        return "await_approval"
    return "continue"
```

### 9.5 Checkpointing Configuration

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def create_checkpointer():
    checkpointer = AsyncPostgresSaver.from_conn_string(
        "postgresql://synarch:synarch_local@localhost:5432/synarch"
    )
    await checkpointer.setup()  # creates checkpoint tables if not exist
    return checkpointer

# Graph compilation with checkpointer
graph = build_graph()
app = graph.compile(checkpointer=checkpointer)

# Invoke with thread_id for mission-scoped checkpoints
config = {"configurable": {"thread_id": mission_id}}
result = await app.ainvoke(initial_state, config=config)
```

---

## 10. Nervous System — NATS Event Contract

### 10.1 Subject Hierarchy

```
synarch.
├── mission.{mission_id}.
│   ├── created          # Mission created
│   ├── planned          # Synarch produced plan
│   ├── state_changed    # Status transition
│   ├── completed        # Mission finished
│   ├── failed           # Mission failed
│   └── cancelled        # Mission cancelled
│
├── agent.{agent_name}.
│   ├── activated        # Agent node started processing
│   ├── thinking         # Agent reasoning (intermediate thought)
│   ├── delegated        # Agent assigned task to subordinate
│   ├── result           # Agent produced output
│   ├── error            # Agent encountered error
│   └── deactivated      # Agent node finished
│
├── task.{task_id}.
│   ├── created          # Task assigned to agent
│   ├── started          # Agent began work
│   ├── completed        # Task finished
│   └── revision         # Task sent back for revision
│
├── deliverable.{deliverable_id}.
│   ├── created          # Deliverable produced
│   ├── reviewed         # Janus reviewed it
│   └── accepted         # Synarch accepted it
│
└── approval.{mission_id}.
    ├── requested        # HITL approval needed
    ├── approved         # God approved
    └── rejected         # God rejected
```

### 10.2 Canonical Event Envelope

Every NATS message follows this canonical envelope:

```json
{
  "id": "evt-uuid-v4",
  "type": "agent.thinking",
  "subject": "synarch.agent.zeus.thinking",
  "mission_id": "mission-uuid",
  "agent": "zeus",
  "timestamp": "2026-02-20T00:00:00.000Z",
  "sequence": 42,
  "payload": {
    "content": "Analyzing the goal... I need to delegate code generation to Hephaestus.",
    "metadata": {
      "phase": "EXECUTING",
      "task_id": "task-uuid",
      "model": "bedrock/anthropic.claude-sonnet-4-20250514-v1:0",
      "token_usage": { "input": 1200, "output": 350 }
    }
  }
}
```

### 10.3 Event Envelope Schema (Python)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from typing import Optional, Any

class EventEnvelope(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str                              # "agent.thinking", "mission.planned", etc.
    subject: str                           # Full NATS subject
    mission_id: str
    agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence: int = 0                      # Monotonic per-mission counter
    payload: dict[str, Any]

    def to_nats_subject(self) -> str:
        return self.subject

    def to_json_bytes(self) -> bytes:
        return self.model_dump_json().encode()
```

### 10.4 NATS Client Wrapper

```python
import nats

class NervousSystem:
    """Synarch nervous system — NATS pub/sub wrapper."""
    
    def __init__(self, url: str = "nats://localhost:4222"):
        self.url = url
        self.nc = None
        self._sequence = {}  # per-mission sequence counters
    
    async def connect(self):
        self.nc = await nats.connect(self.url)
    
    async def publish(self, event: EventEnvelope):
        """Publish typed event to NATS."""
        if not self.nc:
            await self.connect()
        await self.nc.publish(
            event.to_nats_subject(),
            event.to_json_bytes()
        )
    
    async def subscribe(self, subject: str, callback):
        """Subscribe to NATS subject pattern."""
        if not self.nc:
            await self.connect()
        return await self.nc.subscribe(subject, cb=callback)
    
    async def close(self):
        if self.nc:
            await self.nc.drain()
```

### 10.5 SSE Bridge Pattern

```
NATS subscription (synarch.mission.{id}.>) 
    → parse EventEnvelope 
    → yield as SSE event 
    → Mission Control UI EventSource
```

The SSE endpoint subscribes to all events for a mission via NATS wildcard, formats them as SSE, and streams to the frontend. This replaces the current mock-polling from in-memory dict.

---

## 11. Model Routing — litellm

### 11.1 Provider-Agnostic Model Calls

All LLM calls go through `litellm.acompletion()`. No raw Bedrock SDK, no raw OpenAI SDK. This is **non-negotiable** per ADR-001.

### 11.2 Model Assignment

| Agent | litellm Model String | Provider | Cost Tier | Reasoning |
|---|---|---|---|---|
| Synarch | `bedrock/anthropic.claude-opus-4-20250514-v1:0` | AWS Bedrock | $$$$ | Strategic decomposition needs strongest reasoning |
| Zeus | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | AWS Bedrock | $$$ | Technical planning — strong reasoning, good cost balance |
| Thoth | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | AWS Bedrock | $$$ | Research synthesis — quality over cost |
| Hermes | `ollama/llama3.1:8b` | Ollama (local) | Free | Information retrieval is structured — save money |
| Hephaestus | `bedrock/anthropic.claude-sonnet-4-20250514-v1:0` | AWS Bedrock | $$$ | Code generation needs frontier quality |
| Janus | `bedrock/anthropic.claude-3-5-haiku-20241022-v1:0` | AWS Bedrock | $$ | Review is checklist-based — fast + cheap |

### 11.3 Cost Estimation

| Complexity Tier | Model | Input $/1M tokens | Output $/1M tokens | Est. per mission |
|---|---|---|---|---|
| STRATEGIC | Opus 4 | $15.00 | $75.00 | ~$0.05 |
| CREATIVE | Sonnet 4 | $3.00 | $15.00 | ~$0.02 per agent |
| STRUCTURED | Haiku 3.5 | $0.80 | $4.00 | ~$0.005 |
| RETRIEVAL | Ollama | $0.00 | $0.00 | $0.00 |

**Total estimated cost per mission:** $0.03–$0.15 depending on complexity.

### 11.4 litellm Integration in AgentNode

```python
import litellm

class AgentNode:
    def __init__(self, name: str, model: str, soul_path: str):
        self.name = name
        self.model = model
        self.soul = self.load_soul(soul_path)
    
    async def invoke(self, messages: list[dict], **kwargs) -> str:
        """Call LLM via litellm with soul as system prompt."""
        full_messages = [
            {"role": "system", "content": self.soul},
            *messages
        ]
        response = await litellm.acompletion(
            model=self.model,
            messages=full_messages,
            **kwargs
        )
        return response.choices[0].message.content
```

### 11.5 Environment Configuration

```env
# AWS Bedrock (for Opus 4, Sonnet 4, Haiku 3.5)
AWS_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=<from-bedrock>
AWS_SECRET_ACCESS_KEY=<from-bedrock>

# Ollama (local, for Hermes)
OLLAMA_API_BASE=http://localhost:11434

# litellm configuration
LITELLM_LOG=DEBUG  # development only
```

---

## 12. API Specification

### 12.1 Endpoint Summary

| Method | Path | Description | Auth | Request Body | Response |
|---|---|---|---|---|---|
| POST | `/mission/start` | Start a new mission | — | `MissionStartRequest` | `MissionStartResponse` |
| GET | `/mission/{id}/stream` | SSE stream of mission events | — | — | SSE `EventEnvelope` stream |
| GET | `/mission/{id}/state` | Get current mission state | — | — | `MissionStateResponse` |
| POST | `/mission/{id}/approve` | Approve a pending HITL request | — | `ApprovalDecision` | `ApprovalResponse` |
| POST | `/mission/{id}/cancel` | Cancel a running mission | — | — | `MissionStatusResponse` |
| POST | `/mission/{id}/pause` | Pause a running mission | — | — | `MissionStatusResponse` |
| POST | `/mission/{id}/resume` | Resume a paused mission | — | — | `MissionStatusResponse` |
| GET | `/missions` | List missions with filtering | — | Query params | `MissionListResponse` |
| GET | `/agents` | List all agent definitions | — | — | `AgentListResponse` |
| GET | `/agents/{name}/soul` | Get agent's soul.md content | — | — | `AgentSoulResponse` |
| GET | `/health` | Health check | — | — | `HealthResponse` |

### 12.2 Request/Response Schemas

```python
# POST /mission/start
class MissionStartRequest(BaseModel):
    goal: str                                    # Natural language goal
    authority_mode: str = "supervised"           # "guided" | "supervised" | "free_rein"

class MissionStartResponse(BaseModel):
    mission_id: str
    status: str                                  # "CREATED"
    stream_url: str                              # "/mission/{id}/stream"

# GET /mission/{id}/state
class MissionStateResponse(BaseModel):
    mission_id: str
    goal: str
    status: str
    authority_mode: str
    plan: list[str] | None
    tasks: list[TaskSummary]
    deliverables: list[DeliverableSummary]
    created_at: datetime
    updated_at: datetime
    error_context: dict | None

class TaskSummary(BaseModel):
    task_id: str
    assigned_agent: str
    description: str
    status: str

class DeliverableSummary(BaseModel):
    deliverable_id: str
    agent: str
    type: str                                    # "research_report", "code", "review_verdict", "synthesis"
    review_status: str
    created_at: datetime

# POST /mission/{id}/approve
class ApprovalDecision(BaseModel):
    decision: str                                # "approve" | "reject"
    reason: str | None = None                    # Optional explanation

class ApprovalResponse(BaseModel):
    mission_id: str
    decision: str
    resumed: bool                                # Whether graph execution resumed

# GET /missions
class MissionListResponse(BaseModel):
    missions: list[MissionSummary]
    total: int
    page: int
    page_size: int

class MissionSummary(BaseModel):
    mission_id: str
    goal: str
    status: str
    created_at: datetime
    updated_at: datetime
```

### 12.3 Error Response Contract

All errors follow a consistent envelope (pattern from OpenClaw deep-dive):

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

**Error Codes:**

| Code | HTTP Status | Description |
|---|---|---|
| `MISSION_NOT_FOUND` | 404 | Mission ID doesn't exist |
| `MISSION_NOT_RUNNING` | 409 | Action requires running mission (e.g., pause on completed) |
| `MISSION_NOT_AWAITING_APPROVAL` | 409 | Approve/reject when no pending approval |
| `INVALID_AUTHORITY_MODE` | 400 | Unknown authority mode |
| `GOAL_EMPTY` | 400 | Empty goal string |
| `INTERNAL_ERROR` | 500 | Unhandled exception |
| `NATS_UNAVAILABLE` | 503 | Cannot connect to NATS |
| `DATABASE_UNAVAILABLE` | 503 | Cannot connect to PostgreSQL |

### 12.4 SSE Event Format

```
event: agent.thinking
data: {"id":"evt-123","type":"agent.thinking","agent":"zeus","mission_id":"m-1","timestamp":"...","payload":{"content":"Analyzing..."}}

event: mission.state_changed
data: {"id":"evt-124","type":"mission.state_changed","mission_id":"m-1","timestamp":"...","payload":{"from":"PLANNING","to":"EXECUTING"}}

event: approval.requested
data: {"id":"evt-125","type":"approval.requested","mission_id":"m-1","agent":"hephaestus","timestamp":"...","payload":{"action":"file_write","target":"/output/main.py","risk":"medium"}}
```

---

## 13. Mission Control UI

### 13.1 Design System

**V3 "Cyber-Sovereign Industrialism" is LOCKED.** All UI must follow:

| Token | Value | Usage |
|---|---|---|
| `--bg-void` | `#0A0A0B` | Main background (Layer 0) |
| `--bg-plate` | `#121214` | Component background (Layer 1) |
| `--bg-active` | `#18181B` | Hover state |
| `--signal-amber` | `#FFB900` | Primary signal, active states, CTAs |
| `--border-primary` | `#27272A` | Panel borders (Zinc-800) |
| `--border-active` | `#3F3F46` | Active borders (Zinc-700) |
| `--border-highlight` | `#FFB900` | Highlight borders (Amber) |
| Grid dot | `rgba(39,39,42,0.2)` | 40px crosshair grid pattern |
| `--font-display` | Space Grotesk | Headings, module titles (500, 700) |
| `--font-ui` | Geist Sans | UI text, body (400, 500) |
| `--font-mono` | Geist Mono / JetBrains Mono | Code, logs, technical output |
| `--radius` | `0px` global, `2px` inputs | Sharp corners — `>4px` forbidden |

**Agent Signature Colors:**

| Agent | Color | Hex |
|---|---|---|
| Synarch | Amber (gold) | `#FFB900` |
| Zeus | Electric Blue | `#3B82F6` |
| Thoth | Violet | `#8B5CF6` |
| Hermes | Cyan | `#06B6D4` |
| Hephaestus | Rose/Red | `#F43F5E` |
| Janus | Emerald | `#10B981` |

### 13.2 Five-Panel Cockpit Layout

```
┌──────────────────────────────────────────────────────────────┐
│  MISSION CONTROL — Synarch Engine              [Status Bar] │
├──────────────────────┬───────────────────────────────────────┤
│                      │                                       │
│  🗺️ AGENT TOPOLOGY   │  💬 THOUGHT STREAM                    │
│  (Graph viz showing  │  (Real-time event log, color-coded   │
│   active agents,     │   by agent, scrolling, filterable)   │
│   connections,       │                                       │
│   current state)     │                                       │
│                      │                                       │
├──────────────────────┼───────────────────────────────────────┤
│                      │                                       │
│  📋 TASK BOARD        │  📦 DELIVERABLES                      │
│  (Kanban columns:    │  (Research reports, code outputs,    │
│   Pending → Active   │   review verdicts, final synthesis)  │
│   → Review → Done)   │                                       │
│                      │                                       │
├──────────────────────┴───────────────────────────────────────┤
│  ⌨️ COMMAND INPUT                                             │
│  [Type your mission here...]                         [Send] │
└──────────────────────────────────────────────────────────────┘
```

### 13.3 Panel Specifications

**1. Agent Topology (Top-Left)**
- Visual graph showing hierarchy
- Nodes pulse with agent signature color when active
- Edges glow when delegation is happening
- States: IDLE (dim), ACTIVE (pulsing), WAITING (amber outline), ERROR (red)
- Technology: SVG or Canvas-based renderer

**2. Thought Stream (Top-Right)**
- Chronological event feed from SSE
- Each event shows: `[timestamp] [agent-icon] [agent-name]: message`
- Color-coded by agent signature color
- Filterable by agent, event type
- Auto-scroll with "pin to bottom" behavior

**3. Task Board (Bottom-Left)**
- Kanban columns: PENDING → IN_PROGRESS → REVIEW → COMPLETED
- Each card shows: task description, assigned agent, time elapsed
- Cards move between columns in real-time via SSE updates
- Click to expand for full task details

**4. Deliverables (Bottom-Right)**
- Tabbed view by type: Research | Code | Reviews | Synthesis
- Each deliverable shows agent, timestamp, content preview
- Expandable for full content
- Code deliverables with syntax highlighting

**5. Command Input (Bottom Bar)**
- Text input for God's mission goals
- Authority mode selector: Guided | Supervised | Free Rein
- Send button with loading state
- Mission status indicator (current phase)

### 13.4 Approval Inbox (Overlay)

When a HITL approval is requested:
- Amber-bordered modal appears over the cockpit
- Shows: requesting agent, action description, risk level, context
- Two buttons: APPROVE (amber) | REJECT (red)
- Optional text input for God's reasoning
- Countdown timer if configured (auto-reject on timeout)

### 13.5 Frontend Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Next.js | 14+ | App Router, Server Components |
| TypeScript | 5+ | Type safety |
| Tailwind CSS | 3+ | Utility-first styling |
| shadcn/ui | latest | Accessible component primitives |
| EventSource | native | SSE consumption |

---

## 14. Human-in-the-Loop (HITL)

### 14.1 The Rule of Two

The "Rule of Two" is Synarch's permission boundary model (from `docs/agents/god/soul.md`):

> When an agent needs to perform a **high-impact action** — one that is irreversible, costly, or affects external systems — the action must be approved by **two authorities**: the agent's direct superior AND God.

In the PoC, this simplifies to: **God approves all high-impact actions.** The agent's superior (Tier 2) escalates to Synarch, who escalates to God.

### 14.2 Actions Requiring Approval (PoC)

| Action | Agent | Risk Level | Why |
|---|---|---|---|
| Write files to disk | Hephaestus | Medium | Modifies filesystem |
| Execute generated code | Hephaestus | High | Arbitrary code execution |
| Send external API requests | Hermes | Medium | Network side effects |
| Final mission delivery | Synarch | Low | Commit to "done" state |

### 14.3 Approval Workflow

```
1. Agent determines action requires approval
2. Agent sets state.needs_approval = True with approval_request details
3. LangGraph graph hits interrupt (via `interrupt_before` on approval node)
4. Mission status → AWAITING_APPROVAL
5. NATS event: synarch.approval.{mission_id}.requested
6. SSE streams approval request to Mission Control
7. Mission Control shows approval modal to God
8. God clicks Approve or Reject
9. POST /mission/{id}/approve with decision
10. Graph resumes with approval decision injected into state
11. If approved → agent proceeds with action
12. If rejected → agent skips action and reports rejection to superior
```

### 14.4 LangGraph Interrupt Implementation

```python
from langgraph.types import interrupt

# In agent node:
async def hephaestus_node(state: MissionState) -> dict:
    # ... generate code ...
    
    if action_requires_approval(state):
        # This pauses the graph until resume
        approval = interrupt({
            "agent": "hephaestus",
            "action": "file_write",
            "target": "/output/main.py",
            "risk": "medium",
            "description": "Write generated Python file to output directory"
        })
        
        if approval["decision"] == "reject":
            return {"messages": [{"agent": "hephaestus", "content": "Action rejected by God."}]}
    
    # Proceed with file write
    ...
```

### 14.5 Authority Modes

| Mode | Description | Approval Behavior |
|---|---|---|
| `guided` | God approves every significant action | Most interrupts, highest control |
| `supervised` | God approves only high-risk actions | Default — balanced autonomy |
| `free_rein` | Agents act autonomously, God reviews at end | Minimal interrupts — fast execution |

---

## 15. Security Model

### 15.1 PoC Security Scope

The PoC runs **locally** with no external network exposure. Security in this phase focuses on:
- **Agent permission boundaries** — hierarchy enforcement
- **Secrets management** — no hardcoded credentials
- **Input validation** — structured request/response contracts
- **Execution sandboxing** — generated code runs in controlled environment

Full enterprise security (OAuth, RBAC, audit trails, WASM sandboxing) is Phase 2+.

### 15.2 Hierarchy Enforcement

| Rule | Implementation |
|---|---|
| Agents only communicate with direct superior/reports | Graph edges enforce adjacency; no skip-level edges |
| God speaks only to Synarch | API endpoint routes all user input through Synarch node |
| Tier 3 cannot contact Tier 1 | No graph edge from specialist to Synarch |
| Delegation follows chain of command | Zeus delegates to Hephaestus, not directly to Hermes |

### 15.3 Secrets Management

```env
# .env file (gitignored)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1
DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch
NATS_URL=nats://localhost:4222
```

- `.env` is in `.gitignore` — never committed
- `.env.example` provides template with placeholder values
- All infrastructure credentials use environment variables
- No secrets in soul.md files, state objects, or NATS events

### 15.4 Code Execution Safety (PoC)

For Hephaestus-generated code:
- Code is written to an `output/` directory (never to system paths)
- Execution requires God's approval via HITL (in `supervised` and `guided` modes)
- In `free_rein` mode, code is written but not auto-executed
- Full sandboxing (Docker/WASM) is Phase 2 (pattern from Smolagents deep-dive)

### 15.5 Input Validation

- All API inputs validated via Pydantic models (FastAPI auto-validation)
- NATS event payloads validated via `EventEnvelope` Pydantic schema
- Agent outputs are structured (not free-form strings passed to shell)
- Error responses use consistent envelope with machine-readable codes

---

## 16. Testing Strategy

### 16.1 Testing Pyramid

```
        ┌───────────────┐
        │   E2E Tests   │  ← Full mission execution (1-2 happy paths)
        │    (10%)      │
        ├───────────────┤
        │ Integration   │  ← Agent→NATS→SSE, Graph→PostgreSQL
        │   (30%)       │
        ├───────────────┤
        │  Unit Tests   │  ← Agent nodes, state reducers, routing
        │    (60%)      │     functions, event schemas, repository
        └───────────────┘
```

### 16.2 Unit Tests

| Component | Test Focus | Framework |
|---|---|---|
| `MissionState` | State schema validation, reducer behavior | pytest |
| `EventEnvelope` | Serialization, NATS subject generation | pytest |
| `AgentNode` | Soul loading, message formatting | pytest + unittest.mock |
| Routing functions | Conditional routing logic (plan→agents, review→verdict) | pytest |
| `MissionRepository` | CRUD operations, status transitions | pytest + asyncpg mock |

### 16.3 Integration Tests

| Scenario | Components | Verification |
|---|---|---|
| Graph checkpoint/resume | LangGraph + PostgreSQL | Kill mid-mission → restart → resumes |
| NATS event flow | Agent node → NervousSystem → NATS | Events arrive on correct subjects |
| SSE streaming | NATS → SSE endpoint → EventSource | Frontend receives events in order |
| Mission lifecycle | API → Graph → PostgreSQL | Status transitions match state machine |

### 16.4 End-to-End Tests

| Scenario | Description | Success Criteria |
|---|---|---|
| Happy path: Research + Code | Submit goal → Synarch plans → Zeus+Thoth execute → Janus reviews → Complete | Mission reaches COMPLETED with deliverables |
| HITL approval | Submit goal → Agent requests approval → Approve → Continues | Mission pauses and resumes correctly |
| Mission cancellation | Submit goal → Cancel mid-execution | Mission reaches CANCELLED, agents stop |

### 16.5 Test Infrastructure

- **Framework:** pytest + pytest-asyncio
- **Mocking:** LLM calls mocked via `litellm` mock responses (no real API calls in CI)
- **Database:** Test PostgreSQL instance (Docker) with schema migration
- **NATS:** Test NATS instance (Docker) for integration tests
- **Frontend:** Playwright for E2E browser tests (Phase 2)

---

## 17. Observability & Telemetry

### 17.1 Logging

All components emit structured JSON logs:

```json
{
  "timestamp": "2026-02-20T00:00:00.000Z",
  "level": "INFO",
  "component": "agent.zeus",
  "mission_id": "m-001",
  "message": "Delegating code generation to Hephaestus",
  "metadata": {
    "task_id": "t-003",
    "model": "bedrock/anthropic.claude-sonnet-4-20250514-v1:0"
  }
}
```

**Log Levels:**
- `DEBUG` — LLM prompt/response (development only, never in production)
- `INFO` — Agent activations, delegations, completions
- `WARNING` — Retry attempts, degraded performance
- `ERROR` — Agent failures, infrastructure connectivity issues
- `CRITICAL` — Unrecoverable mission failures

### 17.2 Metrics (PoC Scope)

Tracked per mission and exposed via `/health` endpoint:

| Metric | Description | Source |
|---|---|---|
| `mission_duration_seconds` | Total mission execution time | API layer |
| `agent_invocation_count` | Number of LLM calls per mission | AgentNode |
| `agent_token_usage` | Input/output tokens per agent per mission | litellm response |
| `mission_cost_usd` | Estimated cost per mission | litellm token counts × pricing |
| `nats_events_published` | Total events emitted | NervousSystem |
| `checkpoint_count` | Number of graph checkpoints | LangGraph |
| `approval_wait_seconds` | Time spent in AWAITING_APPROVAL | Mission state |

### 17.3 NATS as Telemetry Backbone

Every agent action is already an event on NATS. This means:
- **Real-time monitoring** comes free via NATS subscription
- **Audit trail** can be built by persisting NATS events to `mission_events` table
- **Debugging** — replay events from `mission_events` to understand what happened
- **Alerting** — subscribe to `synarch.agent.*.error` for failure detection

### 17.4 Health Check Endpoint

```json
GET /health

{
  "status": "ok",
  "service": "synarch-backend",
  "version": "0.1.0",
  "dependencies": {
    "postgresql": { "status": "connected", "latency_ms": 2 },
    "nats": { "status": "connected", "latency_ms": 1 },
    "qdrant": { "status": "connected", "latency_ms": 3 },
    "ollama": { "status": "connected", "models": ["llama3.1:8b"] },
    "bedrock": { "status": "configured", "region": "us-east-1" }
  },
  "active_missions": 1,
  "uptime_seconds": 3600
}
```

---

## 18. Infrastructure & Deployment

### 18.1 Deployment Topology (PoC)

```
HOST MACHINE (your laptop/workstation)
├── Python Backend (FastAPI + LangGraph)     ← runs natively
├── Next.js Frontend (Mission Control)       ← runs natively
│
└── Docker Compose (infra only)
    ├── NATS (nats:latest)                   ← port 4222, 8222
    ├── PostgreSQL 16 (postgres:16-alpine)   ← port 5432
    ├── Qdrant (qdrant/qdrant:latest)        ← port 6333
    └── Ollama (ollama/ollama:latest)        ← port 11434
```

**Why backend on host?** Simpler debugging, direct MCP access, no Docker networking overhead for PoC.

### 18.2 Docker Compose (Infrastructure)

```yaml
# infra/docker-compose.yml
services:
  nats:
    image: nats:latest
    ports: ["4222:4222", "8222:8222"]
    command: ["--jetstream"]
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: synarch
      POSTGRES_USER: synarch
      POSTGRES_PASSWORD: synarch_local
    volumes: ["pg_data:/var/lib/postgresql/data"]
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]
    restart: unless-stopped

volumes:
  pg_data:
  qdrant_data:
  ollama_data:
```

### 18.3 Startup Sequence

```bash
# 1. Start infrastructure
docker compose -f infra/docker-compose.yml up -d

# 2. Pull Ollama model (first time only)
docker exec -it $(docker ps -qf name=ollama) ollama pull llama3.1:8b

# 3. Start backend
cd backend && pip install -r requirements.txt && python main.py

# 4. Start frontend
cd apps/web && npm install && npm run dev

# 5. Open Mission Control
open http://localhost:3000
```

### 18.4 Environment Variables

```env
# backend/.env
DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch
NATS_URL=nats://localhost:4222
QDRANT_URL=http://localhost:6333
OLLAMA_API_BASE=http://localhost:11434

# AWS Bedrock
AWS_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
```

### 18.5 Project Structure (Target)

```
synarch-engine/
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── requirements.txt
│   ├── .env                       # gitignored
│   ├── .env.example
│   └── src/
│       ├── agents/                # Agent node implementations
│       │   ├── agent_node.py      # Base class (soul loading, litellm)
│       │   ├── synarch.py
│       │   ├── zeus.py
│       │   ├── thoth.py
│       │   ├── hermes.py
│       │   ├── hephaestus.py
│       │   └── janus.py
│       ├── orchestrator/          # LangGraph state machine
│       │   ├── graph.py           # StateGraph with conditional routing
│       │   ├── state.py           # MissionState TypedDict
│       │   ├── routing.py         # Routing functions
│       │   └── checkpoint.py      # PostgreSQL checkpointer setup
│       ├── nervous_system/        # NATS integration
│       │   ├── client.py          # NervousSystem wrapper
│       │   ├── events.py          # EventEnvelope schema
│       │   └── sse_bridge.py      # NATS→SSE bridge
│       ├── persistence/           # Database layer
│       │   ├── repository.py      # MissionRepository
│       │   ├── models.py          # SQLAlchemy/Pydantic models
│       │   └── migrations/        # Schema migrations
│       ├── api/                   # FastAPI routes
│       │   ├── server.py          # Route handlers
│       │   ├── schemas.py         # Request/response Pydantic models
│       │   └── errors.py          # Error envelope contract
│       └── config.py              # Environment/settings
├── apps/
│   └── web/                       # Next.js Mission Control
│       ├── app/
│       │   ├── page.tsx           # Main cockpit layout
│       │   └── layout.tsx         # Root layout with V3 theme
│       ├── components/
│       │   ├── agent-topology.tsx
│       │   ├── thought-stream.tsx
│       │   ├── task-board.tsx
│       │   ├── deliverables.tsx
│       │   ├── command-input.tsx
│       │   └── approval-modal.tsx
│       ├── hooks/
│       │   └── use-mission-stream.ts  # SSE EventSource hook
│       └── lib/
│           ├── api.ts             # Backend API client
│           └── types.ts           # Shared TypeScript types
├── infra/
│   └── docker-compose.yml
├── docs/                          # All documentation
├── branding/                      # V3 Design System
├── memory-bank/                   # Session memory
└── references/                    # 12 git submodule repos
```

---

## 19. Non-Functional Requirements

| Requirement | Target | Measurement |
|---|---|---|
| **Startup time** | All services ready in <2 minutes | `docker compose up` + `python main.py` + `npm run dev` |
| **First agent response** | Visible in dashboard <5 seconds after mission start | Time from POST to first SSE event |
| **End-to-end mission** | Simple research+code task <3 minutes | Time from goal submission to COMPLETED |
| **Cost per mission** | <$0.20 for frontier models, $0 for local-only | litellm token tracking |
| **Crash recovery** | Mission resumes from last checkpoint after restart | Kill backend → restart → mission continues |
| **Event latency** | Agent event → Mission Control update <1 second | NATS publish → SSE receive |
| **Concurrent missions** | At least 1 (PoC), designed for N (Phase 2) | Single mission at a time in PoC |
| **Data durability** | Zero mission data loss on backend crash | PostgreSQL persistence + checkpointing |
| **Code quality** | All Python typed, all TypeScript strict | mypy + tsc --strict |

---

## 20. Implementation Phases

Aligned with `docs/plans/2026-02-19-gap-closure-and-reference-adoption.md`:

### Phase 1: Durable Foundation (Task 1)
- [ ] PostgreSQL schema migration (missions, tasks, deliverables, events)
- [ ] `MissionRepository` with asyncpg
- [ ] LangGraph `AsyncPostgresSaver` checkpointer setup
- [ ] Replace in-memory `MISSIONS` dict in server.py
- [ ] Verify crash recovery: kill → restart → resume
- **Acceptance:** Mission survives backend restart

### Phase 2: Non-Linear Graph + HITL (Task 2)
- [ ] Conditional routing after Synarch planning (Zeus, Thoth, or both)
- [ ] Janus review gate with REVISE/PASS routing
- [ ] LangGraph `interrupt()` for HITL approval
- [ ] `/mission/{id}/approve` endpoint
- [ ] Mission phase tracking in state
- **Acceptance:** Graph routes conditionally; HITL pauses and resumes

### Phase 3: Agent Runtime + NATS (Task 3)
- [ ] litellm integration in `AgentNode.invoke()`
- [ ] `EventEnvelope` Pydantic schema
- [ ] `NervousSystem` NATS client wrapper
- [ ] All agent nodes publish events to NATS
- [ ] SSE bridge: NATS subscription → SSE stream
- [ ] Replace mock SSE polling with real NATS-backed stream
- **Acceptance:** Agent thoughts appear in real-time via NATS→SSE

### Phase 4: Mission Control UI (Task 4)
- [ ] Five-panel cockpit layout
- [ ] SSE EventSource hook
- [ ] Thought Stream component (color-coded, filterable)
- [ ] Task Board component (kanban, real-time updates)
- [ ] Agent Topology component (hierarchy visualization)
- [ ] Deliverables component (tabbed view)
- [ ] Command Input with authority mode selector
- [ ] Approval Modal overlay
- **Acceptance:** Full mission visible and controllable from browser

### Phase 5: Brand Enforcement (Task 5)
- [ ] V3 CSS variables and grid background
- [ ] Space Grotesk / Geist Sans / Geist Mono fonts
- [ ] Agent signature colors throughout UI
- [ ] 0px radius enforcement
- [ ] Plate/void/overlay depth system
- **Acceptance:** UI matches V3 Design System specification exactly

### Phase 6: Integration & Polish (Task 6)
- [ ] End-to-end flow: goal → decompose → research → code → review → synthesize → deliver
- [ ] Error handling and graceful degradation
- [ ] Reference adoption matrix updated
- [ ] Memory bank updated
- [ ] README with one-liner start command
- **Acceptance:** Demo scenario completes successfully

---

## 21. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Bedrock API latency** causes slow mission execution | Medium | Medium | litellm fallback to Ollama for non-critical agents; timeout with retry |
| **LangGraph checkpointing** schema breaks on upgrade | Low | High | Pin langgraph version; test migrations in CI |
| **NATS message loss** during high throughput | Low | Medium | JetStream persistence; event sequence numbers for gap detection |
| **Ollama model quality** insufficient for Hermes tasks | Medium | Low | Upgrade to larger model or fall back to Haiku 3.5 |
| **PostgreSQL connection exhaustion** under load | Low | High | Connection pooling via asyncpg pool; connection limits in Docker |
| **SSE connection drops** in browser | Medium | Low | EventSource auto-reconnect with `lastEventId` |
| **Agent hallucination** produces incorrect code | High | Medium | Janus review gate catches errors; HITL for code execution |
| **Context window overflow** for complex missions | Medium | High | Token tracking per agent; summarize context when approaching limits |
| **Scope creep** — adding Phase 2 features too early | High | Medium | Strict adherence to this PRD scope; YAGNI enforcement |

---

## 22. Out of Scope — Phase 2+ Roadmap

The following features are explicitly **NOT in the PoC** but are documented for future reference:

| Feature | Phase | Description |
|---|---|---|
| **Cloud deployment** | 2 | Kubernetes, Terraform, multi-region |
| **Self-evolution** | 2 | Agents optimize their own prompts and SOPs |
| **Consensus voting (AAD)** | 2 | Confidence-weighted multi-agent debate |
| **WASM sandboxing** | 2 | Isolated code execution for Hephaestus |
| **Multi-user support** | 2 | Multiple Gods, team workspaces, RBAC |
| **Full audit trail** | 2 | Compliance-grade logging, event replay |
| **Agent spawning** | 3 | Dynamically create new agents without coding |
| **GraphRAG** | 3 | Neo4j-backed relationship-aware memory |
| **MCP tool marketplace** | 3 | Agents discover and consume external MCP tools |
| **Consensus-based C-Suite** | 3 | C-Suite agents debate and vote on strategy |
| **Plugin system** | 3 | Third-party agent and tool plugins |
| **NotebookLM RAG** | 2 | Deep research via NotebookLM SDK integration |

---

## 23. Glossary

| Term | Definition |
|---|---|
| **God** | The human user — source of all authority in the Synarch hierarchy |
| **Synarch** | The CEO agent (Tier 1) — supreme orchestrator that decomposes God's goals |
| **Soul** | A markdown file defining an agent's identity, directives, constraints, and SOPs |
| **Mission** | A goal submitted by God, decomposed and executed by the agent hierarchy |
| **Nervous System** | The NATS event bus — all agent communication flows through it |
| **Mission Control** | The Next.js dashboard — God's window into the agent hierarchy |
| **Rule of Two** | Permission model — high-impact actions require approval from superior AND God |
| **HITL** | Human-in-the-Loop — mechanism for God to approve/reject agent actions |
| **EventEnvelope** | The canonical NATS message format — typed, sequenced, mission-scoped |
| **Checkpoint** | LangGraph state snapshot in PostgreSQL — enables crash recovery |
| **litellm** | Provider-agnostic LLM abstraction layer — all model calls go through it |
| **Tier** | Agent hierarchy level: 0 (God) → 1 (CEO) → 2 (C-Suite) → 3 (Specialist) |
| **Authority Mode** | How much autonomy agents have: guided, supervised, or free_rein |
| **Deliverable** | An output produced by an agent: research report, code, review verdict, synthesis |

---

## 24. Approval

| Role | Name | Date | Status |
|---|---|---|---|
| God (Project Owner) | PraxLannister | 2026-02-20 | ⏳ Pending Review |
| Architect (Claude) | Claude Opus 4 | 2026-02-20 | ✅ Drafted |

**Version History:**

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-02-13 | Cline + Antigravity | Initial `poc-prd.md` draft |
| 1.0 | 2026-02-20 | Claude Opus 4 | Complete rewrite: 24 sections, exhaustive specification |

---

*"In the Synarch, every god has a throne. Every throne has a purpose. No god acts alone."*
