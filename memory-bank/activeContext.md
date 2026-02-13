# Active Context: Pantheon AI

## Current Focus
**PoC Phase 1 — Foundation** (ready to start implementation)

## What Was Done (2026-02-13)
1. NotebookLM SDK (`notebooklm-kit`) connected — 43 notebooks, full archive downloaded
2. Downloaded: 50 notes (169KB), 12 source guides (65KB), quiz (39KB), flashcards (29KB), audio (81MB)
3. 7 agent soul files created: God, Pantheon, Zeus, Thoth, Hermes, Hephaestus, Janus
4. Comprehensive PoC PRD with AWS Bedrock model routing
5. Agent naming convention (mythology-based, 3-tier hierarchy)
6. OpenClaw studied: identity.ts, system-prompt.ts, identity-file.ts
7. 5 reference repos cloned: OpenClaw, CrewAI, LangGraph, Letta, LLM-Council-Plus
8. Dual vision analysis: Cline (Claude Opus 4) + Antigravity (Gemini 3 Pro)

## Key Decisions Made
- **Name:** Pantheon AI (God → Pantheon → C-Suite → Specialists)
- **Models:** AWS Bedrock (Opus 4/Sonnet 4/Haiku 3.5) + Ollama (Llama 3.1 8B)
- **Event Bus:** NATS (not Redis) — subject hierarchy, JetStream persistence
- **Orchestration:** LangGraph (not CrewAI) — state machines, checkpointing
- **User = God** — Rule of Two permission escalation from Meta Research

## Immediate Next Steps
1. `docker compose up` — spin up NATS, Qdrant, PostgreSQL, Ollama
2. FastAPI skeleton with `/mission/start`, `/mission/{id}/stream` endpoints
3. LangGraph StateGraph with Pantheon as entry node
4. Soul.md → runtime system prompt compiler
5. Next.js Mission Control skeleton with shadcn/ui

## Key Decision (Late Session)
**DROP NotebookLM from PoC.** Antigravity's "NotebookLM Latency Trap" analysis is correct. RAG should be a pluggable capability, not hardwired. Hermes uses web search + Qdrant for PoC. NotebookLM integration becomes Phase 2 optional RAG provider.

## Open Questions
- Should soul.md format follow OpenClaw's identity-file.ts parsing (key:value) or stay as rich markdown?
- How to handle Bedrock region failover?
- Future: agents vote on model selection for new agents — design needed
- AgentNode base class design (from Antigravity's "Wrapper Strategy")

## Blockers
None — all dependencies resolved, all decisions made, ready to build.
