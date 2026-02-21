# Synarch Engine — Master High-Level Design (HLD)

**Version:** 1.1 | **Author:** Cline (Backend-PE) | **Date:** 2026-02-21
**Input:** PRD-final.MD v1.2 (FR-1–FR-86), cline-future-vision-2027.md, all ADRs, 5 book summaries
**Canonical PRD:** `docs/01-requirements/PRD-final.MD`

---

## 1. System Overview

Synarch Engine is an autonomous multi-agent orchestration platform. A human ("God") issues a mission goal. The system decomposes it into sub-tasks, delegates to specialized AI agents, executes with quality gates, and delivers a synthesized result — all observable in real-time via Mission Control.

```
┌──────────────────────────────────────────────────────────────────┐
│                        GOD (Human User)                         │
│                    Mission Control Dashboard                     │
│                   (Next.js + SSE + WebSocket)                   │
└───────────────────────────┬──────────────────────────────────────┘
                            │ REST API + SSE
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                     GATEWAY (FastAPI)                            │
│  Auth │ Rate Limit │ Idempotency │ CORS │ Request Validation    │
└───────────────────────────┬──────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
┌──────────────────┐ ┌──────────┐ ┌──────────────┐
│  CONTROL PLANE   │ │ OBSERVE  │ │  PERSISTENCE │
│   (LangGraph)    │ │  PLANE   │ │    PLANE     │
│                  │ │  (NATS)  │ │ (PostgreSQL) │
│ StateGraph with  │ │          │ │  + Qdrant    │
│ conditional edges│ │ Pub/Sub  │ │  + Redis     │
│ + checkpointing  │ │ Events   │ │              │
└──────────────────┘ └──────────┘ └──────────────┘
```

---

## 2. Three-Plane Architecture (ADR-005)

| Plane | Responsibility | Technology | Protocol |
|---|---|---|---|
| **Control** | Agent orchestration, task routing, state machines | LangGraph StateGraph | Python async |
| **Observation** | Event streaming, real-time telemetry, audit trail | NATS JetStream | Pub/Sub |
| **Persistence** | Durable state, checkpoints, memory, vectors | PostgreSQL + Qdrant + Redis | SQL + gRPC |

**Rule:** NATS is observation-only. NEVER use NATS for control flow decisions. Control flow lives exclusively in LangGraph conditional edges.

---

## 3. Agent Hierarchy

```
                    ┌─────────┐
                    │   GOD   │  (Human)
                    │ Mission │
                    │ Creator │
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ SYNARCH │  CEO Agent
                    │ Strategy│  (Phase 2)
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │  ZEUS   │  COO / Orchestrator
                    │ Planner │  Decomposes → routes → aggregates
                    │ Router  │
                    └────┬────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
       ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
       │  THOTH  │ │HEPHAEST│ │ HERMES  │
       │Research │ │ Code   │ │ Comms   │
       │Analysis │ │ Build  │ │ Search  │
       └─────────┘ └────────┘ └─────────┘
                         │
                    ┌────▼────┐
                    │  JANUS  │  QA / Review
                    │ Validate│  (Reviews all outputs)
                    └─────────┘
```

### Agent Definitions

| Agent | Role | soul.md | Tools | Model Tier |
|---|---|---|---|---|
| **Zeus** | COO — decomposes missions, routes to specialists, aggregates results | `docs/agents/zeus/soul.md` | AgentTool (invoke other agents) | Opus/GPT-4o |
| **Thoth** | Research — web search, RAG, document analysis, citation | `docs/agents/thoth/soul.md` | web_search, rag_query, document_reader | Sonnet |
| **Hephaestus** | Engineering — code generation, file manipulation, testing | `docs/agents/hephaestus/soul.md` | code_write, file_edit, test_run | Opus/GPT-4o |
| **Hermes** | Communications — API calls, notifications, external integrations | `docs/agents/hermes/soul.md` | api_call, notification_send | Sonnet |
| **Janus** | QA — review outputs, validate quality, suggest improvements | `docs/agents/janus/soul.md` | code_review, fact_check | Sonnet |
| **Synarch** | CEO — strategic oversight, conflict resolution (Phase 2) | `docs/agents/synarch/soul.md` | escalation, strategy | Opus |

---

## 4. Mission Lifecycle (State Machine)

```
CREATED → PLANNING → EXECUTING → REVIEWING → SYNTHESIZING → COMPLETED
                ↑         │            │
                │         ▼            ▼
                │   AWAITING_APPROVAL  REVISING
                │         │            │
                │         ▼            │
                └─────────────────────←┘
                
            Any state → PAUSED (manual)
            Any state → FAILED (error)
            Any state → CANCELLED (manual)
```

### State Transitions

| From | To | Trigger |
|---|---|---|
| CREATED | PLANNING | Mission submitted |
| PLANNING | EXECUTING | Zeus produces plan |
| EXECUTING | AWAITING_APPROVAL | Approval gate triggered (Supervised mode) |
| AWAITING_APPROVAL | EXECUTING | Human approves |
| EXECUTING | REVIEWING | All sub-tasks complete |
| REVIEWING | REVISING | Janus requests changes |
| REVIEWING | SYNTHESIZING | Janus approves |
| REVISING | EXECUTING | Re-execute with corrections |
| SYNTHESIZING | COMPLETED | Final output delivered |
| Any | PAUSED | Human pauses |
| Any | FAILED | Unrecoverable error |
| Any | CANCELLED | Human cancels |

---

## 5. LangGraph Control Plane Design

### StateGraph Definition

```python
class MissionState(TypedDict):
    mission_id: str
    goal: str
    mode: Literal["autopilot", "supervised", "manual"]
    phase: MissionPhase
    plan: list[SubTask]
    results: dict[str, AgentResult]
    messages: Annotated[Sequence[BaseMessage], operator.add]
    retry_count: int
    cost_usd: float
    confidence: float
```

### Graph Nodes

| Node | Function | Agent |
|---|---|---|
| `plan` | Decompose mission into sub-tasks | Zeus |
| `route` | Select agent for next sub-task | Zeus |
| `execute` | Run agent on sub-task | Thoth/Hephaestus/Hermes |
| `review` | Validate output quality | Janus |
| `approve` | Human approval gate (if supervised) | Human |
| `synthesize` | Combine all results into final output | Zeus |
| `error_handler` | Handle failures, retry logic | System |

### Conditional Edges

```
plan → route (always)
route → execute (selected agent)
execute → review (always)
review → synthesize (if approved)
review → route (if revision needed, re-route to agent)
approve → execute (if human approves)
approve → cancelled (if human rejects)
```

---

## 6. Data Flow

### Mission Execution Flow

```
1. GOD → POST /api/v1/missions → Gateway validates → Creates mission record (PostgreSQL)
2. Gateway → Compiles LangGraph → Starts execution
3. LangGraph plan node → Zeus decomposes goal → Produces sub-tasks
4. LangGraph route node → Zeus selects agent → Routes to specialist
5. Agent executes → Calls litellm → Uses tools → Produces result
6. Each step → NATS publish (synarch.mission.{id}.agent.{name}.{event})
7. NATS → SSE bridge → Mission Control dashboard updates
8. LangGraph review node → Janus validates output
9. If supervised → LangGraph interrupt → Human approval via API
10. LangGraph synthesize → Zeus combines results → Final output
11. Mission state → COMPLETED → PostgreSQL updated
```

---

## 7. Component Architecture

### Backend (Python/FastAPI)

```
backend/
├── api/                    # Gateway layer
│   ├── app.py             # FastAPI application
│   ├── middleware/         # Auth, CORS, idempotency, rate limiting
│   ├── routes/            # REST endpoints
│   │   ├── missions.py    # CRUD + start/pause/cancel
│   │   ├── agents.py      # Agent status/config
│   │   ├── events.py      # SSE streaming endpoint
│   │   └── health.py      # Health checks
│   └── schemas/           # Pydantic request/response models
├── domain/                 # Business logic (hexagonal core)
│   ├── agents/            # Agent definitions, soul.md loading
│   ├── events/            # Event types, envelope
│   ├── models/            # Domain models (Mission, SubTask, AgentResult)
│   └── orchestrator/      # LangGraph graph definition
├── ports/                  # Interface contracts (abstract)
│   ├── checkpointer.py   # LangGraph checkpoint storage
│   ├── event_bus.py       # Event publishing
│   ├── model_provider.py  # LLM calls (litellm)
│   ├── persistence.py     # Mission/agent CRUD
│   └── vector_store.py    # RAG/memory
├── adapters/               # Implementations (hexagonal outer)
│   ├── langgraph/         # LangGraph StateGraph + checkpointer
│   ├── litellm/           # litellm model provider
│   ├── nats/              # NATS JetStream adapter
│   ├── postgres/          # SQLAlchemy/asyncpg repositories
│   └── qdrant/            # Qdrant vector store
├── config.py              # Pydantic Settings
├── container.py           # Dependency injection
└── main.py                # Uvicorn entrypoint
```

### Frontend (Next.js)

```
apps/web/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Dashboard home
│   ├── missions/
│   │   ├── page.tsx        # Mission list
│   │   └── [id]/page.tsx   # Mission detail + live stream
│   └── agents/
│       └── page.tsx        # Agent status
├── components/
│   ├── MissionCard.tsx
│   ├── AgentStream.tsx
│   ├── ApprovalGate.tsx
│   └── EventTimeline.tsx
└── lib/
    ├── api.ts              # REST client
    └── sse.ts              # SSE connection manager
```

---

## 8. Infrastructure

### Docker Compose (Development)

| Service | Image | Port | Purpose |
|---|---|---|---|
| `backend` | Custom (Dockerfile) | 8000 | FastAPI + LangGraph |
| `web` | Custom (Dockerfile) | 3000 | Next.js dashboard |
| `postgres` | postgres:16 | 5432 | Missions, checkpoints, audit |
| `nats` | nats:latest | 4222, 8222 | Event streaming |
| `qdrant` | qdrant/qdrant | 6333 | Vector memory |
| `redis` | redis:7 | 6379 | Cache, sessions |

### Startup Sequence

```
1. postgres → ready (healthcheck)
2. nats → ready (healthcheck)
3. qdrant → ready (healthcheck)
4. redis → ready (healthcheck)
5. backend → connects to all services → ready
6. web → connects to backend → ready
```

---

## 9. Security Model (FR-51–FR-56)

### Defense-in-Depth Layers

```
Layer 1: Input Sanitization (all user inputs cleaned before reaching agents)
Layer 2: Prompt Hardening (system prompts resistant to injection)
Layer 3: Tool Guardrails (validation wrappers on every tool)
Layer 4: Per-Agent Permissions (least privilege, capability matrix)
Layer 5: Output Monitoring (scan for sensitive data, policy violations)
Layer 6: Audit Logging (every action logged with correlation ID)
```

### Agent Permission Matrix

| Agent | Code Exec | File Write | Web Access | DB Access | API Calls |
|---|---|---|---|---|---|
| Zeus | ❌ | ❌ | ❌ | Read-only | ❌ |
| Thoth | ❌ | ❌ | ✅ (read) | Read-only | ❌ |
| Hephaestus | ✅ (sandboxed) | ✅ (scoped) | ❌ | ❌ | ❌ |
| Hermes | ❌ | ❌ | ✅ | ❌ | ✅ |
| Janus | ❌ | ❌ | ❌ | Read-only | ❌ |

---

## 10. Observability (FR-27–FR-33)

### Event Flow

```
Agent action → Domain event → NATS publish → SSE bridge → Dashboard
                                    ↓
                              PostgreSQL (audit log)
```

### NATS Subject Hierarchy

```
synarch.mission.{mission_id}.created
synarch.mission.{mission_id}.state.{new_state}
synarch.mission.{mission_id}.agent.{agent_name}.started
synarch.mission.{mission_id}.agent.{agent_name}.progress
synarch.mission.{mission_id}.agent.{agent_name}.tool.{tool_name}
synarch.mission.{mission_id}.agent.{agent_name}.completed
synarch.mission.{mission_id}.agent.{agent_name}.error
synarch.mission.{mission_id}.approval.requested
synarch.mission.{mission_id}.approval.granted
synarch.mission.{mission_id}.approval.denied
synarch.mission.{mission_id}.completed
synarch.mission.{mission_id}.failed
```

### Canonical Event Envelope (FR-19)

```json
{
  "event_id": "uuid-v4",
  "event_type": "agent.progress",
  "mission_id": "uuid-v4",
  "agent_name": "thoth",
  "timestamp": "2026-02-21T17:30:00Z",
  "version": "1.0",
  "payload": { ... },
  "correlation_id": "uuid-v4",
  "cost_usd": 0.003
}
```

---

## 11. Key Architectural Decisions Summary

| # | Decision | Rationale |
|---|---|---|
| ADR-001 | LangGraph over Swarms | Graph-based state machines, native PostgreSQL checkpointing, stream_events() |
| ADR-002 | Naming: Synarch (company) = Synarch (CEO agent) | Simplified naming, clear hierarchy |
| ADR-003 | Reference, don't fork | 12 submodules as pattern sources, not dependencies |
| ADR-004 | Gap closure contract | Systematic reference adoption with evidence |
| ADR-005 | Hexagonal / Modular Monolith | Ports & adapters, domain isolation, testability |
| NEW | litellm for all model calls | Provider-agnostic, cost tracking, model routing |
| NEW | NATS = observation only | Never control plane. Prevents distributed state bugs |
| NEW | AgentTool pattern (FR-68) | Agents wrapped as tools for composable orchestration |

---

## 12. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Mission E2E latency | < 3 minutes |
| Mission cost | < $0.10 for standard missions |
| Startup time | < 2 minutes (docker compose up) |
| Availability | 99.9% for local deployment |
| Checkpoint recovery | Resume within 30s after crash |
| SSE latency | < 500ms from event to dashboard |
| API response time | < 200ms for CRUD operations |

---

*This HLD is the constitutional document for Synarch Engine. All implementation must conform to these architectural boundaries. Per-issue work references specific sections.*
