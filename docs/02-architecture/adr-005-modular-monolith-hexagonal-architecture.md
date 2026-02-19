# ADR-005: Modular Monolith with Hexagonal Architecture

**Status:** ACCEPTED  
**Date:** 2026-02-20  
**Accepted:** 2026-02-20 by PraxLannister (God)  
**Author:** Claude (BackendPE / Distinguished Principal Engineer mode)  
**Deciders:** PraxLannister (God)

---

## Context

The PRD v1.0-final specifies a multi-agent orchestration engine with 6 agents, real-time event streaming, durable checkpointing, and a Mission Control UI. We need to decide the service architecture before writing production code.

**Constraints from PRD and existing decisions:**
- LangGraph `StateGraph` requires in-process execution for checkpointing to work
- NATS is the observation plane (events/telemetry), NOT the control plane
- LangGraph state is the control plane (agent communication and routing)
- PostgreSQL is the persistence plane (metadata + checkpoints)
- 1 developer + AI assistants (cannot maintain microservice fleet)
- PoC scope: 1 concurrent mission, local deployment

---

## Decision

**Architecture: Modular Monolith with Hexagonal (Ports & Adapters) pattern.**

Two processes:
1. **Python backend** — FastAPI + LangGraph + all agents (single process)
2. **Next.js frontend** — Mission Control (separate process)

Infrastructure in Docker: NATS, PostgreSQL, Qdrant, Ollama.

---

## Alternatives Considered

### A) Microservices (Agent-per-Service)

Each agent runs as its own service, communicating via NATS messages.

**Rejected because:**
- LangGraph's StateGraph is an **in-process** state machine. Agents are graph nodes, not services. Splitting them breaks checkpointing, conditional routing, and interrupt/resume.
- 6+ services for 1 developer = operational overhead without benefit
- Network latency between agents kills mission throughput (each agent call adds ~5ms RTT)
- NATS is explicitly the observation plane, not the control plane — agents don't message each other through NATS

### B) Traditional MVC

Simple Controller → Service → Repository layers.

**Rejected because:**
- No separation between domain logic and infrastructure
- Swapping NATS for Kafka or litellm for direct SDK requires touching business logic
- Violates PRD principle: "Explicit contracts over implicit coupling"

### C) Clean Architecture (Uncle Bob)

Entities → Use Cases → Interface Adapters → Frameworks.

**Rejected because:**
- 4 concentric layers is overkill for PoC
- Use Cases layer adds ceremony without clear benefit at current scale
- Hexagonal achieves the same decoupling with fewer layers

### D) Vertical Slice Architecture

Organize by feature (mission/, agents/, approvals/) with each slice owning its own persistence and routing.

**Rejected because:**
- Cross-cutting concerns (events, checkpoints, HITL) span all features
- Orchestration logic inherently coordinates across slices
- Better suited for CRUD-heavy apps, not stateful orchestration engines

---

## Architecture

### Three Separation Planes

```
┌─────────────────────────────────────────────────────┐
│                    CONTROL PLANE                      │
│             LangGraph StateGraph (in-process)        │
│     Agent communication via state, NOT messages      │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                  OBSERVATION PLANE                     │
│              NATS Events (side-channel)               │
│    Every action emits event, but events don't        │
│    drive agent decisions — state does                 │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                  PERSISTENCE PLANE                     │
│     PostgreSQL (metadata + LangGraph checkpoints)    │
│            Crash recovery, audit trail               │
└─────────────────────────────────────────────────────┘
```

**Critical rule:** These three planes must NEVER be conflated. Agents communicate through the LangGraph state (control), emit events to NATS (observation), and persist results to PostgreSQL (durability). Removing NATS should not break mission execution — only observability.

### Hexagonal Layers

```
┌─────────────────────────────────────────────────────┐
│                    API LAYER                          │
│  FastAPI routes, middleware, schemas, DI wiring      │
│  (Thin controller — delegates to domain via ports)   │
└──────────────────────┬──────────────────────────────┘
                       │ depends on ports (not adapters)
                       ▼
┌─────────────────────────────────────────────────────┐
│                   PORTS LAYER                         │
│  Abstract interfaces (Python Protocol/ABC classes)   │
│  MissionRepo, EventBus, ModelProvider, Checkpointer  │
│  (Contracts between domain and infrastructure)       │
└──────────────────────┬──────────────────────────────┘
           ┌───────────┼───────────┐
           ▼           ▼           ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ DOMAIN CORE  │ │ ADAPTERS │ │  ADAPTERS    │
│ (Pure logic) │ │ (Infra)  │ │  (Infra)     │
│              │ │          │ │              │
│ Orchestrator │ │ Postgres │ │ NATS         │
│ Agents       │ │ litellm  │ │ Qdrant       │
│ Events       │ │ LangGraph│ │ SSE Bridge   │
│ Models       │ │ checkpoint│ │              │
└──────────────┘ └──────────┘ └──────────────┘
```

### Dependency Rule

```
domain/  →  imports NOTHING from adapters/ or api/
ports/   →  imports ONLY from domain/ and typing
adapters/→  imports from ports/ (implements) and domain/ (types)
api/     →  imports from ports/ (via DI), never adapters/ directly
```

This rule ensures:
- Domain logic is testable without any infrastructure
- Adapters are swappable without touching business logic
- API layer is a thin orchestration shell

### Directory Structure

```
backend/
├── main.py                          # Bootstrap, uvicorn
├── config.py                        # pydantic-settings from .env
├── container.py                     # DI: wire ports → adapters
│
├── domain/                          # PURE DOMAIN (zero infra imports)
│   ├── models/                      # Pydantic domain entities
│   │   ├── mission.py               # Mission, MissionStatus
│   │   ├── task.py                  # Task, TaskStatus
│   │   ├── deliverable.py           # Deliverable (with provenance_refs)
│   │   ├── approval.py              # Approval entity
│   │   └── agent_message.py         # AgentMessage, MissionPhase
│   ├── events/                      # Event schemas
│   │   ├── envelope.py              # EventEnvelope (schema_version, idempotency_key)
│   │   └── types.py                 # Event type taxonomy constants
│   ├── agents/                      # Agent domain logic
│   │   ├── base.py                  # AgentNode ABC (soul loading, process contract)
│   │   ├── synarch.py               # CEO: planning + synthesis
│   │   ├── zeus.py                  # CTO: engineering delegation
│   │   ├── thoth.py                 # CRO: research planning
│   │   ├── hermes.py                # Researcher: retrieval
│   │   ├── hephaestus.py            # Engineer: code generation
│   │   └── janus.py                 # Reviewer: quality gate
│   └── orchestrator/                # Graph logic
│       ├── state.py                 # MissionState TypedDict
│       ├── graph.py                 # StateGraph definition
│       └── routing.py               # Conditional routing functions
│
├── ports/                           # ABSTRACT INTERFACES
│   ├── persistence.py               # Repository ABCs
│   ├── event_bus.py                 # EventBusPort ABC
│   ├── model_provider.py            # ModelProviderPort ABC
│   ├── checkpointer.py              # CheckpointerPort ABC
│   └── vector_store.py              # VectorStorePort ABC
│
├── adapters/                        # INFRASTRUCTURE IMPLEMENTATIONS
│   ├── postgres/
│   │   ├── connection.py            # asyncpg pool
│   │   ├── repositories.py          # Concrete repos
│   │   └── migrations/
│   │       └── 001_initial.sql      # Schema from PRD §9.2
│   ├── nats/
│   │   ├── client.py                # NervousSystem
│   │   └── sse_bridge.py            # NATS→SSE
│   ├── litellm/
│   │   └── provider.py              # litellm ModelProvider
│   ├── langgraph/
│   │   └── checkpointer.py          # AsyncPostgresSaver wrapper
│   └── qdrant/
│       └── store.py                 # Phase 2
│
├── api/                             # HTTP INTERFACE
│   ├── app.py                       # FastAPI factory
│   ├── dependencies.py              # Depends() injection
│   ├── middleware/
│   │   ├── errors.py                # Error envelope
│   │   ├── idempotency.py           # Idempotency-Key
│   │   └── cors.py
│   ├── routes/
│   │   ├── missions.py              # /mission/* 
│   │   ├── agents.py                # /agents/*
│   │   └── health.py                # /health
│   └── schemas/
│       ├── requests.py              # API request models
│       └── responses.py             # API response models
│
└── tests/
    ├── unit/                        # Mock ports, test domain
    ├── integration/                 # Real adapters, Docker services
    └── conftest.py

apps/web/                            # SEPARATE PROCESS
├── app/                             # Next.js App Router
├── components/                      # V3 Design System
├── hooks/                           # useMissionStream (SSE)
└── lib/                             # API client, shared types
```

---

## Key Design Decisions Within This Architecture

### 1. Agents are Domain Logic, NOT Infrastructure

Agent process() functions live in `domain/agents/`. They receive state and return state updates. They call the ModelProviderPort (abstract) for LLM invocation. They don't import litellm, NATS, or PostgreSQL.

### 2. Events are Side-Effects, NOT Control Flow

When an agent emits an event, it calls `EventBusPort.publish()`. If NATS is down, the mission continues — events are lost but execution isn't. LangGraph state is the source of truth for what agents should do next.

### 3. Dependency Injection via Container

`container.py` wires everything at startup:
```python
# container.py (pseudocode)
async def create_container(settings: Settings) -> Container:
    pg_pool = await create_pool(settings.database_url)
    nats_client = await connect_nats(settings.nats_url)
    checkpointer = await create_checkpointer(settings.database_url)
    
    return Container(
        mission_repo=PostgresMissionRepository(pg_pool),
        approval_repo=PostgresApprovalRepository(pg_pool),
        event_bus=NATSEventBus(nats_client),
        model_provider=LiteLLMProvider(),
        checkpointer=checkpointer,
    )
```

FastAPI routes receive ports via `Depends()`, never concrete adapters.

### 4. Frontend is Fully Decoupled

Next.js communicates ONLY via HTTP REST + SSE. No shared code, no shared imports. Could be replaced with any SSE-consuming client.

---

## Event Delivery Semantics (Resolves FR-16 vs ADR Conflict)

**The conflict:** FR-16 says "NATS required for runtime event publication." ADR-005 says "removing NATS should not break mission execution."

**Resolution:** Both are correct at different levels:

- **FR-16 is a DEPLOYMENT requirement:** NATS must be running in production. The system is designed to use it. Startup health checks verify NATS connectivity.
- **ADR-005 is an ARCHITECTURE constraint:** The domain/orchestrator must not have a hard dependency on NATS. If `EventBusPort.publish()` fails, the mission graph continues — the event is lost (degraded observability) but the agent's work is not rolled back.

**Concrete policy:**

| Scenario | Behavior |
|---|---|
| NATS healthy | Events published normally, SSE streams to UI |
| NATS temporarily unreachable | `EventBusPort.publish()` logs warning, does NOT throw. Mission continues. Events written to `mission_events` table as fallback (outbox pattern). |
| NATS down at startup | Health check fails, backend logs error. Mission start is allowed but warns operator that observability is degraded. |
| NATS recovers | Outbox events can be replayed from `mission_events` table to NATS for catch-up. |

**Implementation:** The NATS adapter wraps publish in try/except. On failure, it writes to the `mission_events` PostgreSQL table (which exists regardless). The SSE bridge can fall back to polling `mission_events` if NATS subscription fails.

This ensures:
- **Control plane (LangGraph)** never depends on observation plane (NATS)
- **Observation plane** degrades gracefully, never blocks
- **Persistence plane** serves as durable outbox for event replay

---

## Migration Path: Legacy → Hexagonal

**Current layout** (`backend/src/*`) → **Target layout** (`backend/domain/`, `backend/ports/`, etc.)

| Current Path | Target Path | Notes |
|---|---|---|
| `backend/src/agents/agent_node.py` | `backend/domain/agents/base.py` | Rename + add ABC |
| `backend/src/agents/synarch.py` | `backend/domain/agents/synarch.py` | Move, remove infra imports |
| `backend/src/agents/zeus.py` | `backend/domain/agents/zeus.py` | Move |
| `backend/src/agents/thoth.py` | `backend/domain/agents/thoth.py` | Move |
| `backend/src/orchestrator/state.py` | `backend/domain/orchestrator/state.py` | Move |
| `backend/src/orchestrator/graph.py` | `backend/domain/orchestrator/graph.py` | Move, extract routing to routing.py |
| `backend/src/api/server.py` | `backend/api/routes/missions.py` | Split into route modules |
| `backend/main.py` | `backend/main.py` | Keep, add container bootstrap |
| (new) | `backend/ports/*.py` | Create abstract interfaces |
| (new) | `backend/adapters/postgres/` | Extract from in-memory MISSIONS |
| (new) | `backend/adapters/nats/` | New: NervousSystem client |
| (new) | `backend/adapters/litellm/` | New: ModelProvider adapter |
| (new) | `backend/config.py` | New: pydantic-settings |
| (new) | `backend/container.py` | New: DI wiring |

**Migration strategy:** Incremental, not big-bang. Move one module at a time, verify tests pass after each move. Start with `domain/models/` and `ports/` (zero-risk), then migrate agents, then wire adapters.

---

## Consequences

### Positive
- Domain logic is 100% testable without infrastructure
- Any adapter can be swapped by implementing the port interface
- Single process simplifies deployment, debugging, and LangGraph checkpointing
- Clear boundaries prevent spaghetti coupling
- NATS failure doesn't break missions (graceful degradation)

### Negative
- Port abstractions add indirection (justified by testability and swappability)
- Single process means single point of failure (mitigated by PostgreSQL checkpoints — restart resumes)
- Cannot scale individual agents independently (not needed for PoC; Phase 2 can extract if required)

### Risks
- Dependency rule violations if developers import adapters in domain code → mitigate with CI lint rule
- Over-engineering port abstractions for adapters that will never be swapped → YAGNI: only create ports for adapters that the PRD explicitly lists as swappable

---

## Verification

This architecture satisfies all PRD objectives:
- **OBJ-1 (Durability):** PostgreSQL checkpointer in adapter, graph runs in-process
- **OBJ-2 (Governance):** Routing logic in domain/orchestrator, HITL via LangGraph interrupt
- **OBJ-3 (Events):** EventBusPort published from domain, NATS adapter implements
- **OBJ-4 (UI):** SSE bridge adapter streams to decoupled Next.js frontend
- **OBJ-5 (Brand):** Frontend is independent process with its own V3 component library

---

## References

- PRD v1.0-final: `docs/01-requirements/prd-1.0-final.md`
- ADR-001: LangGraph over Swarms (in-process orchestration)
- ADR-004: Gap Closure (W1-W5 workstream alignment)
- LangGraph deep-dive: `docs/04-reference-deep-dives/langgraph/`
- OpenClaw deep-dive: `docs/04-reference-deep-dives/openclaw/` (port/adapter patterns)
