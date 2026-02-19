# Active Context: Synarch Engine

## Current Focus
**PoC Phase 1 — Foundation** (ready to start implementation)

## PRD v1.0-final (2026-02-20)
- **File:** `docs/01-requirements/prd-1.0-final.md` (1,240 lines, 30 sections)
- **Scope:** Exhaustive PoC specification — merged from Claude + Codex PRDs
- **Supersedes:** `poc-prd.md`, `prd-1.0-claude.md`, `prd-1.0-codex.md`
- **Key features:**
  - FR-1 to FR-44 requirement IDs cross-referenced throughout
  - Product principles, Definition of Done (8-point gate), 5 open questions
  - Idempotency contract (FR-14), event versioning (FR-19), approval timeout (FR-25)
  - Approvals as first-class DB entity, provenance tracking (FR-20)
  - SQL DDL, architecture diagrams, state machine, NATS subject tree, API specs
  - Mobile layout, reference adoption traceability (12 targets in §22)
  - Brand-correct: #121214 plate, Geist Sans/Mono, aligned with ADR-004 W1-W5

## Repository
- **URL:** https://github.com/synarch-ai/synarch-engine (private)
- **Local:** `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine`
- **Org:** github.com/synarch-ai

## What Was Done (2026-02-13)
1. NotebookLM SDK connected — 43 notebooks, full archive (50 notes, 12 guides, quiz, flashcards)
2. 7 agent soul files: God, Synarch (CEO), Zeus, Thoth, Hermes, Hephaestus, Janus
3. PoC PRD with litellm model routing (provider-agnostic)
4. Agent naming convention (mythology hierarchy, 20+ names)
5. 12 reference repos tracked in `references/` for architecture patterns and implementation study
6. Dual vision analysis: Cline + Antigravity
7. ADR-001: Swarms vs LangGraph — REFERENCE NOT FORK
8. ADR-002: Branding pivot — Synarch AI → Synarch
9. V3 Design System LOCKED: "Cyber-Sovereign Industrialism" (branding/brand-identity.md)
10. Logo generation prompts created (branding/logo-prompts.md)
11. Repo renamed + transferred: PrakharMNNIT/synarch-ai → synarch-ai/synarch-engine
12. Local dir renamed: synarch-ai → synarch-engine

## Key Decisions
- **Company:** Synarch (syn=together + arch=govern)
- **Product:** Synarch Engine
- **CEO Agent:** Synarch
- **Gods:** Zeus, Thoth, Hermes, Hephaestus, Janus — unchanged
- **User:** God — unchanged
- **Models:** litellm (wraps Bedrock, Ollama, OpenAI, 100+)
- **Event Bus:** NATS (not Redis)
- **Orchestration:** LangGraph (not CrewAI, not Swarms)
- **NotebookLM:** DROPPED from PoC (Phase 2 RAG)
- **Design System:** V3 "Cyber-Sovereign Industrialism" — amber #FFB900 on void #0A0A0B

## Reference Intelligence (2026-02-19)
- **Index:** `docs/04-reference-deep-dives/README.md`
- **Autogen:** `docs/04-reference-deep-dives/autogen/README.md`
- **LangGraph:** `docs/04-reference-deep-dives/langgraph/README.md`
- **OpenClaw:** `docs/04-reference-deep-dives/openclaw/README.md`
- **CrewAI:** `docs/04-reference-deep-dives/crewAI/README.md`
- **Letta:** `docs/04-reference-deep-dives/letta/README.md`
- **LLM Council Plus:** `docs/04-reference-deep-dives/llm-council-plus/README.md`
- **Magentic-UI:** `docs/04-reference-deep-dives/magentic-ui/README.md`
- **MCP-Use:** `docs/04-reference-deep-dives/mcp-use/README.md`
- **Playwright-MCP:** `docs/04-reference-deep-dives/playwright-mcp/README.md`
- **Smolagents:** `docs/04-reference-deep-dives/smolagents/README.md`
- **Composio:** `docs/04-reference-deep-dives/composio/README.md`
- **Swarms:** `docs/04-reference-deep-dives/swarms/README.md`

## Architecture Decision (2026-02-20)
- **ADR-005:** Modular Monolith with Hexagonal Architecture
- **File:** `docs/02-architecture/adr-005-modular-monolith-hexagonal-architecture.md`
- **Pattern:** domain/ (pure) → ports/ (abstract) → adapters/ (infra) → api/ (thin)
- **Three planes:** Control (LangGraph state), Observation (NATS), Persistence (PostgreSQL)
- **NOT microservices** — LangGraph requires in-process execution

## Immediate Next Steps (M1: Foundation)
1. Restructure backend to match hexagonal architecture (domain/ports/adapters/api)
2. `docker compose up` — verify NATS, Qdrant, PostgreSQL, Ollama
3. Implement Milestone A: PostgreSQL schema, repositories, checkpointer
4. Implement Milestone B: Conditional routing, HITL, idempotency
5. Implement Milestone C: Mission Control cockpit with V3 design system

## Open Questions
- AgentNode base class design (from Antigravity's "Wrapper Strategy")
- soul.md parsing: rich markdown vs OpenClaw key:value
- Logo generation (user action — Midjourney/DALL-E)

## Blockers
None — all dependencies resolved, all decisions made, ready to build.
