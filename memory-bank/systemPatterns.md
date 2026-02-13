# System Patterns: Synarch Engine

## Agent Hierarchy (Tier System)
```
Tier 0: God (Human) — source of all authority
Tier 1: Pantheon (CEO) — supreme orchestrator
Tier 2: C-Suite — Zeus(CTO), Thoth(CRO), Athena(CPO), Odin(CISO), Midas(CFO), Apollo(CMO)
Tier 3: Specialists — Hephaestus, Hermes, Vishwakarma, Janus, etc.
```

## Communication: Event-Driven Nervous System
- NATS subjects: `pantheon.mission.>`, `pantheon.agent.>`, `pantheon.task.>`, `pantheon.deliverable.>`
- All agent actions emit events → SSE stream → Mission Control dashboard
- Replaces SiteGPT's 15-minute polling with real-time pub/sub

## State Management: LangGraph StateGraph
- Global mission state tracked in StateGraph
- PostgreSQL-backed checkpointing for crash recovery
- Each agent is a node in the graph with soul.md as system prompt

## Memory Architecture
- **Qdrant** — vector search for semantic memory (per-agent + shared namespaces)
- **PostgreSQL** — structured state (missions, tasks, deliverables, logs)
- **MEMORY.md pattern** (from OpenClaw) — file-first memory with vector indexing
- Future: GraphRAG with Neo4j for relationship-aware retrieval

## Security: Rule of Two (Meta Research 2025)
- Agent cannot hold 2+ of: private data, untrusted content, external communication
- Violation → mandatory escalation through Pantheon to God
- Per-agent tool allowlists (future: WASM sandboxing)

## Soul System (Identity Enforcement)
- Each agent has `docs/agents/{name}/soul.md`
- soul.md defines: identity, purpose, personality, behaviors, tools, system prompt
- Compiled into runtime system prompt by prompt builder (OpenClaw pattern)
- Self-awareness: agents know their role boundaries and redirect out-of-scope requests

## Key Design Decisions
1. **LangGraph over CrewAI** — state machines > role chains, checkpointing required
2. **NATS over Redis** — subject hierarchy, JetStream persistence
3. **Qdrant over ChromaDB** — production-grade, multi-tenancy
4. **PostgreSQL now, not later** — checkpointing needs it from day 1
5. **Bedrock over direct API** — one key, multi-model, cost-optimized
6. **Hierarchy over flat** — CEO→CTO→Engineer, not peer-to-peer
