# Product Requirements Document: Pantheon PoC
**Version:** 1.0 | **Status:** Final Draft | **Date:** 2026-02-13  
**Authors:** Cline (Claude Opus 4) + Antigravity (Gemini 3 Pro) — synthesized

---

## 1. Executive Summary

**Pantheon** is a local, open-source, production-grade **Autonomous Multi-Agent Operating System**. This Proof of Concept demonstrates 5–6 mythologically-named agents collaborating in real-time on a Dev + Research task, orchestrated through an event-driven nervous system, with full observability via a Mission Control dashboard.

**Core Value Prop:** *"The Oracle speaks a wish. The Pantheon makes it real."*

**What Makes This Different From Every Other Agent Framework:**
- Agents have **hierarchy** (CEO → C-Suite → Specialists), not flat peer-to-peer
- Communication is **event-driven** (NATS), not polling or sequential
- Every agent has a **soul** (persona, SOP, constraints), not just a system prompt
- Full **observability** — you SEE the gods think, argue, and deliver

---

## 2. Goals & Success Criteria

### The Demo Scenario

The Oracle (you) types into Mission Control:

> *"Research the best event bus for Pantheon's nervous system and implement a working NATS integration prototype with tests."*

### Success Looks Like

| Criteria | What Happens | Verification |
|---|---|---|
| **Pantheon decomposes** | Splits goal into research (→ Thoth) and engineering (→ Zeus) objectives | Dashboard shows task tree |
| **Thoth delegates to Hermes** | Hermes queries NotebookLM + web for event bus comparisons | Source-cited research report generated |
| **Zeus delegates to Hephaestus** | Hephaestus writes NATS client code with tests | Working code in `/output/` directory |
| **Janus reviews** | Reviews both research and code deliverables | Structured review with verdict |
| **Pantheon synthesizes** | Combines deliverables into final report to The Oracle | Dashboard shows MISSION COMPLETE |
| **Real-time visibility** | Dashboard shows agent messages, task flow, status in real-time | WebSocket-driven live updates |
| **Local deployment** | Everything runs via `docker compose up` + one start script | No cloud dependencies |

---

## 3. Architecture

### 3.1 System Topology

```
┌──────────────────────────────────────────────────────────────────┐
│                    THE ORACLE (Human)                              │
│                    Mission Control UI                              │
│                    (Next.js + shadcn/ui)                          │
└──────────────────────┬───────────────────────────────────────────┘
                       │ REST + SSE (Server-Sent Events)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    GATEWAY (FastAPI)                               │
│                    POST /mission/start                             │
│                    GET  /mission/{id}/stream                       │
│                    GET  /mission/{id}/state                        │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH ORCHESTRATOR                          │
│                                                                    │
│  ┌──────────┐    ┌────────┐    ┌────────┐                        │
│  │ PANTHEON  │───▶│  ZEUS  │───▶│HEPHAEST│                        │
│  │  (CEO)    │    │  (CTO) │    │  US    │                        │
│  └─────┬────┘    └────────┘    └────────┘                        │
│        │                                                          │
│        │         ┌────────┐    ┌────────┐    ┌────────┐          │
│        └────────▶│  THOTH │───▶│ HERMES │    │ JANUS  │          │
│                  │  (CRO) │    │(Researc│    │(Review)│          │
│                  └────────┘    └────────┘    └────────┘          │
│                                                                    │
│  State: LangGraph StateGraph + PostgreSQL checkpointing           │
└──────────────────────┬───────────────────────────────────────────┘
                       │ All events published to NATS
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    NERVOUS SYSTEM (NATS)                           │
│                                                                    │
│  Subjects:                                                        │
│    pantheon.mission.>     — mission lifecycle events               │
│    pantheon.agent.>       — agent status/message events            │
│    pantheon.task.>        — task assignment/completion events       │
│    pantheon.deliverable.> — deliverable creation events             │
└──────────────────────────────────────────────────────────────────┘
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
      ┌──────────┐ ┌────────┐ ┌────────┐
      │PostgreSQL│ │ Qdrant │ │ Ollama │
      │  State   │ │ Memory │ │ Local  │
      │  + Logs  │ │ Vector │ │ Models │
      └──────────┘ └────────┘ └────────┘
```

### 3.2 The Brain — LangGraph Orchestrator

- **Framework:** LangGraph (Python) with `StateGraph`
- **Pattern:** Plan-and-Execute with hierarchical delegation
- **State:** Global state graph tracks mission, tasks, deliverables, agent status
- **Checkpointing:** PostgreSQL-backed for crash recovery and replay
- **Agent Nodes:** Each agent is a LangGraph node with its soul.md as system prompt

### 3.3 The Nervous System — NATS

- **Why NATS over Redis Pub/Sub:** NATS has built-in subjects hierarchy (`pantheon.agent.zeus.task`), JetStream for persistence, and 60ns latency. Aligns with SAMAS research notes.
- **Docker:** `nats:latest` container
- **Event Schema:**
```json
{
  "event_type": "agent.message",
  "agent": "Thoth.Hermes",
  "mission_id": "m-001",
  "timestamp": "2026-02-13T17:30:00Z",
  "payload": {
    "type": "research_finding",
    "content": "NATS benchmarks show 1.2M msg/sec...",
    "source": "NotebookLM: SAMAS Notes"
  }
}
```

### 3.4 The Memory — Qdrant + PostgreSQL

- **Qdrant (Docker):** Vector memory for semantic search across agent knowledge
- **PostgreSQL (Docker):** Structured state — missions, tasks, deliverables, agent logs, checkpoints
- **Embedding Model:** `nomic-embed-text` via Ollama (local, no API cost)

### 3.5 The Interface — Mission Control

- **Framework:** Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
- **Real-time:** SSE from FastAPI gateway → React state
- **Panels:**
  1. **Chat Input** — The Oracle speaks here
  2. **Agent Topology** — Visual graph showing who's active, who's talking to whom
  3. **Thought Stream** — Real-time log of all agent messages (color-coded by agent)
  4. **Task Board** — Kanban: To Do → In Progress → Review → Done
  5. **Deliverables** — Final outputs from completed missions

### 3.6 The Models — AWS Bedrock + Ollama (Cost-Optimized from Day 1)

**Why Bedrock:** One API key, multiple models, pay-per-use, no rate limits. The user already has Bedrock access (used for this Cline session). This gives us the full Claude model family + Llama + Mistral under one roof.

| Agent | Model (Bedrock) | Bedrock Model ID | Reasoning |
|---|---|---|---|
| **Pantheon** | Claude Opus 4 | `us.anthropic.claude-opus-4-20250514-v1:0` | Strategic decomposition — needs the strongest reasoning |
| **Zeus** | Claude Sonnet 4 | `us.anthropic.claude-sonnet-4-20250514-v1:0` | Technical planning — strong reasoning, good cost balance |
| **Thoth** | Claude Sonnet 4 | `us.anthropic.claude-sonnet-4-20250514-v1:0` | Research synthesis — needs quality, not maximum power |
| **Hermes** | Llama 3.1 8B (Ollama) | Local — `ollama/llama3.1:8b` | Information retrieval is structured — save money here |
| **Hephaestus** | Claude Sonnet 4 | `us.anthropic.claude-sonnet-4-20250514-v1:0` | Code generation — frontier quality for correct code |
| **Janus** | Claude Haiku 3.5 | `us.anthropic.claude-3-5-haiku-20241022-v1:0` | Review is checklist-based — fast + cheap is ideal |

**Model Routing Strategy:**
```
Complexity → Model Selection:
  STRATEGIC (decomposition, arbitration)  → Opus 4    ($$$$)
  CREATIVE  (code, research synthesis)    → Sonnet 4  ($$$)
  STRUCTURED (review, formatting)         → Haiku 3.5 ($$)
  RETRIEVAL  (search, simple queries)     → Ollama    (free)
```

**Cost per mission (estimated):** ~$0.03–0.10 (Bedrock pay-per-token + free local)

**Bedrock Configuration (.env):**
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<from-bedrock>
AWS_SECRET_ACCESS_KEY=<from-bedrock>
# No per-model API keys needed — Bedrock handles routing
```

---

## 4. Technical Specifications

### 4.1 Tech Stack

| Layer | Technology | Version | Justification |
|---|---|---|---|
| Orchestration | LangGraph | 0.3+ | State machines with checkpointing, human-in-the-loop |
| Backend API | FastAPI | 0.115+ | Async, SSE support, OpenAPI auto-docs |
| Event Bus | NATS | 2.10+ | Subject hierarchy, JetStream persistence, 60ns latency |
| Vector DB | Qdrant | 1.12+ | Rust-based, hybrid search, multi-tenancy |
| Relational DB | PostgreSQL | 16+ | LangGraph checkpointing, structured state |
| Frontend | Next.js | 14+ | App Router, Server Components, streaming |
| UI Library | shadcn/ui | latest | Accessible, customizable, Tailwind-based |
| Local LLM | Ollama | 0.5+ | Llama 3.1 8B for cost optimization |
| Model Abstraction | **litellm** | latest | Provider-agnostic: Bedrock, Ollama, OpenAI, Groq, 100+ |
| Research | notebooklm-kit | 2.2.0 | Full NotebookLM SDK (Phase 2 RAG) |
| Language | Python 3.12+ | — | LangGraph ecosystem |
| Language | TypeScript 5+ | — | Frontend + NotebookLM scripts |

### 4.2 Project Structure

```
pantheon-ai/
├── backend/                    # Python
│   ├── main.py                # FastAPI gateway
│   ├── orchestrator/          # LangGraph state machine
│   │   ├── graph.py           # Main StateGraph definition
│   │   ├── state.py           # State schema (TypedDict)
│   │   └── nodes/             # Agent node implementations
│   │       ├── pantheon.py
│   │       ├── zeus.py
│   │       ├── thoth.py
│   │       ├── hermes.py
│   │       ├── hephaestus.py
│   │       └── janus.py
│   ├── nervous_system/        # NATS client
│   │   ├── publisher.py
│   │   └── subscriber.py
│   ├── memory/                # Qdrant + embeddings
│   │   └── vector_store.py
│   └── requirements.txt
├── frontend/                  # Next.js
│   ├── app/
│   │   ├── page.tsx           # Mission Control dashboard
│   │   └── api/               # API routes (proxy to backend)
│   ├── components/
│   │   ├── chat-input.tsx
│   │   ├── thought-stream.tsx
│   │   ├── agent-topology.tsx
│   │   ├── task-board.tsx
│   │   └── deliverables.tsx
│   └── package.json
├── docker-compose.yml         # NATS + Qdrant + PostgreSQL + Ollama
├── docs/                      # Already exists
│   ├── 01-requirements/
│   │   └── poc-prd.md         # This file
│   ├── 02-architecture/
│   │   ├── agent-naming-convention.md
│   │   ├── pantheon-vision-analysis-cline.md
│   │   └── pantheon-vision-analysis-antigravity.md
│   └── agents/
│       ├── pantheon/soul.md
│       ├── zeus/soul.md
│       ├── thoth/soul.md
│       ├── hermes/soul.md
│       ├── hephaestus/soul.md
│       └── janus/soul.md
└── scripts/                   # NotebookLM download scripts (already exists)
```

### 4.3 API Design

| Endpoint | Method | Description |
|---|---|---|
| `/mission/start` | POST | Start a new mission. Body: `{ "goal": "string", "authority": "guided\|supervised\|free_rein" }` |
| `/mission/{id}/stream` | GET | SSE stream of all agent events for this mission |
| `/mission/{id}/state` | GET | Current mission state (tasks, agents, deliverables) |
| `/mission/{id}/approve` | POST | The Oracle approves/rejects a pending decision |
| `/agents` | GET | List all active agents with status |
| `/agents/{name}/soul` | GET | Get an agent's soul.md |

### 4.4 Docker Compose

```yaml
services:
  nats:
    image: nats:latest
    ports: ["4222:4222", "8222:8222"]
    command: ["--jetstream"]
  
  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: ["qdrant_data:/qdrant/storage"]
  
  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: pantheon
      POSTGRES_USER: pantheon
      POSTGRES_PASSWORD: pantheon_local
    volumes: ["pg_data:/var/lib/postgresql/data"]
  
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]

volumes:
  qdrant_data:
  pg_data:
  ollama_data:
```

---

## 5. Implementation Phases

### Phase 1: Foundation (Day 1-2)
- [ ] Set up monorepo (`/backend`, `/frontend`)
- [ ] Docker Compose with NATS, Qdrant, PostgreSQL, Ollama
- [ ] Pull Llama 3.1 8B model into Ollama
- [ ] FastAPI skeleton with health check
- [ ] Next.js skeleton with shadcn/ui

### Phase 2: The Brain (Day 3-4)
- [ ] LangGraph StateGraph with Pantheon as entry node
- [ ] State schema: mission, tasks, deliverables, agent_messages
- [ ] Pantheon node: decompose goal → delegate to Zeus + Thoth
- [ ] Zeus node: create engineering tasks → delegate to Hephaestus
- [ ] Thoth node: create research tasks → delegate to Hermes

### Phase 3: The Specialists (Day 5-6)
- [ ] Hermes node: NotebookLM integration via notebooklm-kit
- [ ] Hermes node: Web search fallback
- [ ] Hephaestus node: Code generation with file system write
- [ ] Janus node: Review framework implementation

### Phase 4: The Nervous System (Day 7)
- [ ] NATS client (publisher + subscriber)
- [ ] All agent nodes publish events to NATS
- [ ] SSE endpoint subscribes to NATS and streams to frontend

### Phase 5: Mission Control (Day 8-10)
- [ ] Chat input component
- [ ] Thought Stream (real-time agent log, color-coded)
- [ ] Task Board (Kanban from state)
- [ ] Agent Topology (visual graph)
- [ ] Deliverables panel

### Phase 6: Integration & Polish (Day 11-12)
- [ ] End-to-end flow: input → decompose → research → code → review → output
- [ ] PostgreSQL checkpointing
- [ ] Qdrant memory for agent context
- [ ] Error handling and recovery
- [ ] README with one-liner start command

---

## 6. Constraints & Decisions

| Decision | Choice | Rationale |
|---|---|---|
| **Orchestration** | LangGraph, not CrewAI | State machines > role chains. Checkpointing. Human-in-the-loop. |
| **Event Bus** | NATS, not Redis Pub/Sub | Subject hierarchy, JetStream persistence, aligned with SAMAS research |
| **Vector DB** | Qdrant, not ChromaDB | Production-grade, Rust performance, multi-tenancy for per-agent namespaces |
| **Database** | PostgreSQL, not "add later" | LangGraph checkpointing needs it. No shortcuts on state management. |
| **Local LLM** | Ollama, not API-only | Cost optimization from day 1. Hermes and Janus use local models. |
| **Frontend** | Next.js, not "terminal only" | The dashboard IS the product differentiator. No demo without it. |
| **Backend on host** | Not in Docker (PoC) | Simplifies MCP/NotebookLM integration. Backend runs on host, infra in Docker. |

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| **Startup time** | `docker compose up` + `python main.py` + `npm run dev` < 2 minutes |
| **Mission latency** | First agent response visible in dashboard < 5 seconds |
| **End-to-end mission** | Simple research+code task < 3 minutes |
| **Cost per mission** | < $0.20 for frontier models, $0 for local-only missions |
| **Recovery** | Kill backend → restart → mission resumes from last checkpoint |

---

## 8. Out of Scope (for PoC)

- Cloud deployment / Kubernetes
- Self-evolution / prompt optimization
- Consensus voting (AAD, confidence-weighted)
- Security model (Rule of Two, WASM sandboxing)
- Full audit trail / compliance
- Agent spawning without coding
- Multi-user support

These are Phase 2+ features documented in the vision analysis.

---

## 9. Open Questions (Resolved)

| Question | Decision |
|---|---|
| PostgreSQL now or later? | **Now.** LangGraph checkpointing requires it. No shortcuts. |
| Backend in Docker? | **No.** Run on host for PoC. Simpler MCP/NotebookLM access. |
| Which frontier model? | **Claude Sonnet 4** primary, GPT-4o fallback. User provides API key in `.env`. |
| How many agents in PoC? | **6:** Pantheon, Zeus, Thoth, Hermes, Hephaestus, Janus |

---

**Approved by:** The Oracle  
**Date:** 2026-02-13  

*"In the Pantheon, every god has a throne. Every throne has a purpose. No god acts alone."*
