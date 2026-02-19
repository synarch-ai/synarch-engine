# Synarch Engine — Full Context Handoff Prompt
*Updated: 2026-02-19 | Copy everything below the line into a new Cline chat*

---

#synarch-engine

## 🧠 YOU ARE RESUMING WORK ON SYNARCH ENGINE

**Synarch** (syn=together + arch=govern) is an open-source, production-grade **Autonomous Multi-Agent Orchestration Engine**. Think: the "Linux of autonomous agent teams." Specialized AI agents with mythology-based identities collaborate in a hierarchical council to execute complex missions.

**Repo:** https://github.com/synarch-ai/synarch-engine (private)
**Local:** `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine`

---

## STEP 1: Read Memory Bank (MANDATORY — do this first, in order)

1. `memory-bank/projectbrief.md` — mission, scope, acceptance criteria
2. `memory-bank/productContext.md` — problem statement, target users, differentiation
3. `memory-bank/techContext.md` — full tech stack: LangGraph, NATS, litellm, Qdrant, PostgreSQL, Next.js
4. `memory-bank/systemPatterns.md` — hierarchy, nervous system, soul system, Rule of Two security
5. `memory-bank/activeContext.md` — latest decisions, what was done, next steps
6. `memory-bank/progress.md` — milestone tracker (M0 done, M1 in progress)

## STEP 2: Read Architecture Docs

7. `docs/01-requirements/poc-prd.md` — comprehensive PoC PRD (tech stack, API, Docker, phases)
8. `docs/02-architecture/adr-001-swarms-vs-langgraph.md` — why LangGraph (not Swarms)
9. `docs/02-architecture/adr-002-branding-synarch-ai-to-synarch.md` — naming decision
10. `docs/02-architecture/adr-003-reference-repo-strategy.md` — how we use reference repos
11. `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md` — what to adopt from each
12. `docs/02-architecture/reference-adoption-matrix.md` — pattern-by-pattern adoption map
13. `docs/02-architecture/agent-naming-convention.md` — mythology hierarchy (20+ names)
14. `docs/plans/2026-02-19-gap-closure-and-reference-adoption.md` — latest implementation plan

## STEP 3: Read Agent Souls (know who you're building)

15. `docs/agents/god/soul.md` — Tier 0: The Human (Rule of Two permissions)
16. `docs/agents/synarch/soul.md` — Tier 1: CEO Agent (supreme orchestrator)
17. `docs/agents/zeus/soul.md` — Tier 2: CTO (engineering commander)
18. `docs/agents/thoth/soul.md` — Tier 2: CRO (knowledge keeper)
19. `docs/agents/hermes/soul.md` — Tier 3: Researcher (information gatherer)
20. `docs/agents/hephaestus/soul.md` — Tier 3: Engineer (code builder)
21. `docs/agents/janus/soul.md` — Tier 3: Reviewer (quality gate)

## STEP 4: Read Current Code

22. `backend/main.py` — FastAPI entry point
23. `backend/src/orchestrator/state.py` — mission state schema
24. `backend/src/orchestrator/graph.py` — LangGraph StateGraph definition
25. `backend/src/agents/agent_node.py` — base AgentNode class
26. `backend/src/agents/synarch.py` — Synarch CEO agent implementation
27. `backend/src/agents/zeus.py` — Zeus CTO implementation
28. `backend/src/agents/thoth.py` — Thoth CRO implementation
29. `backend/src/api/server.py` — API routes
30. `apps/web/app/page.tsx` — Next.js Mission Control
31. `infra/docker-compose.yml` — NATS + Qdrant + PostgreSQL + Ollama

## STEP 5: Read Branding

32. `docs/modules/branding/brand-identity.md` — V3 Design System (LOCKED): Cyber-Sovereign Industrialism
33. `README.md` — project README with logos and architecture

## STEP 6: Study Reference Repos (patterns, not code)

12 reference repos in `references/` (all gitmodules):

| Repo | Study For | Key Files |
|---|---|---|
| `openclaw/` | Agent identity, soul system, memory (MEMORY.md) | `src/agents/identity.ts`, `src/agents/system-prompt.ts` |
| `swarms/` | Hierarchical orchestration, model routing, prompts | `swarms/structs/hiearchical_swarm.py`, `swarms/structs/model_router.py` |
| `langgraph/` | Multi-agent supervisor, checkpointing | `examples/multi_agent/` |
| `crewAI/` | Role/crew/task model | `lib/crewai/` |
| `letta/` | Long-term memory management | `letta/memory/`, `letta/agent/` |
| `autogen/` | GroupChat manager pattern | `python/packages/autogen-agentchat/` |
| `composio/` | Tool integration platform, MCP patterns | `python/`, `ts/` |
| `smolagents/` | Lightweight agent framework | Root source |
| `mcp-use/` | MCP client from Python | Root source |
| `magentic-ui/` | Agent UI patterns | Root source |
| `playwright-mcp/` | Browser automation MCP | Root source |
| `llm-council-plus/` | Multi-agent voting/debate UI | `backend/`, `frontend/` |

---

## THE HIERARCHY

```
Tier 0: 🌟 GOD (Human User) — source of all authority
         │
Tier 1: 🏛️ SYNARCH (CEO Agent) — supreme orchestrator
         │
Tier 2: ⚡Zeus(CTO)  📜Thoth(CRO)  [+Athena, Odin, Midas, Apollo future]
         │              │
Tier 3: 🔨Hephaestus  🪶Hermes  🎭Janus
         (Engineer)     (Research) (Review)
```

## KEY DECISIONS (NON-NEGOTIABLE)

- **litellm** for ALL model calls (not raw Bedrock/OpenAI SDK)
- **NATS** for all agent events (not in-memory, not Redis)
- **PostgreSQL** for checkpointing (not JSON files)
- **NotebookLM is NOT in PoC** — RAG is Phase 2
- **Backend runs on host**, infra (NATS/Qdrant/PG/Ollama) in Docker
- **Every agent reads its soul.md** as system prompt foundation
- **All agent events publish to NATS** subjects: `synarch.agent.{name}.{event}`
- **God = Human user**, Synarch = CEO, hierarchy is enforced
- **V3 Design System** is LOCKED — amber #FFB900, void #0A0A0B, Space Grotesk, no pills, 0px radius

## MODEL ROUTING (litellm)

```
Synarch:     bedrock/anthropic.claude-opus-4-20250514-v1:0     (strategic)
Zeus:        bedrock/anthropic.claude-sonnet-4-20250514-v1:0    (technical)
Thoth:       bedrock/anthropic.claude-sonnet-4-20250514-v1:0    (research)
Hermes:      ollama/llama3.1:8b                                  (retrieval, free)
Hephaestus:  bedrock/anthropic.claude-sonnet-4-20250514-v1:0    (code gen)
Janus:       bedrock/anthropic.claude-3-5-haiku-20241022-v1:0   (review, cheap)
```

## WHAT TO BUILD NEXT

**M1: Foundation** is in progress. Backend skeleton exists. Continue by:

1. Verify `docker compose -f infra/docker-compose.yml up -d` works
2. Verify `python backend/main.py` starts FastAPI
3. Verify `cd apps/web && npm run dev` starts Next.js
4. Then implement: Synarch→Zeus/Thoth delegation flow in LangGraph
5. Then implement: NATS event publishing from agent nodes
6. Then implement: SSE streaming from FastAPI to Next.js dashboard

## RULES OF ENGAGEMENT

- **Read everything before writing code.** Context = quality.
- **Use ULTRATHINK** for architectural decisions.
- **Ask God (the user) before committing** major design changes.
- **Study reference repos** for patterns before building from scratch.
- **Update memory-bank/** after every significant change.
- **Commit with conventional messages** (🎉 feat, 🐛 fix, 📝 docs, 🔧 chore).

## START

After reading all of the above, present a brief status summary of what you understand and what you plan to do first. Then await God's orders.

*"Synarch: Where agents rule together."*
