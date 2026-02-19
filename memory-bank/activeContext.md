# Active Context: Synarch Engine

## Current Focus
**PoC Phase 1 — Foundation** (ready to start implementation)

## Repository
- **URL:** https://github.com/synarch-ai/synarch-engine (private)
- **Local:** `/Users/praxlannister/Documents/workspace/synarch-engine`
- **Org:** github.com/synarch-ai

## What Was Done (2026-02-13)
1. NotebookLM SDK connected — 43 notebooks, full archive (50 notes, 12 guides, quiz, flashcards)
2. 7 agent soul files: God, Synarch (CEO), Zeus, Thoth, Hermes, Hephaestus, Janus
3. PoC PRD with litellm model routing (provider-agnostic)
4. Agent naming convention (mythology hierarchy, 20+ names)
5. 7 reference repos: OpenClaw, CrewAI, LangGraph, Letta, LLM-Council-Plus, Swarms, AutoGen
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
- **CEO Agent:** Synarch (renamed from Synarch)
- **Gods:** Zeus, Thoth, Hermes, Hephaestus, Janus — unchanged
- **User:** God — unchanged
- **Models:** litellm (wraps Bedrock, Ollama, OpenAI, 100+)
- **Event Bus:** NATS (not Redis)
- **Orchestration:** LangGraph (not CrewAI, not Swarms)
- **NotebookLM:** DROPPED from PoC (Phase 2 RAG)
- **Design System:** V3 "Cyber-Sovereign Industrialism" — amber #FFB900 on void #0A0A0B

## Immediate Next Steps (M1: Foundation)
1. Operation Rename: synarch → synarch in code (agent files, NATS subjects, classes)
2. `docker compose up` — NATS, Qdrant, PostgreSQL, Ollama
3. FastAPI skeleton with litellm integration
4. LangGraph StateGraph with Synarch as entry node
5. Next.js Mission Control with V3 design system

## Open Questions
- AgentNode base class design (from Antigravity's "Wrapper Strategy")
- soul.md parsing: rich markdown vs OpenClaw key:value
- Logo generation (user action — Midjourney/DALL-E)

## Blockers
None — all dependencies resolved, all decisions made, ready to build.
