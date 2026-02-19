# Project Brief: Synarch Engine

## Mission
Build an open-source, production-grade **Autonomous Multi-Agent Operating System** — the "Linux of agent teams." Inspired by Bhanu Teja P's 14-agent SiteGPT marketing squad, but engineered to be self-evolving, secure, general-purpose, and event-driven.

## Core Value Proposition
*"God speaks a wish. The Synarch makes it real."*

## Acceptance Criteria (PoC)
1. 6 agents (Synarch, Zeus, Thoth, Hermes, Hephaestus, Janus) collaborate on a Dev+Research task
2. Real-time Mission Control dashboard shows agent thoughts, task flow, deliverables
3. Everything runs locally via `docker compose up` + one start script
4. AWS Bedrock for frontier models + Ollama for local cost optimization
5. Agent hierarchy enforced: God → Synarch → C-Suite → Specialists

## Scope
- **In:** PoC with 6 agents, NATS event bus, LangGraph orchestration, Next.js dashboard, Search/RAG integration
- **Out:** Cloud deployment, self-evolution, consensus voting, WASM sandboxing (Phase 2+)

## Success Metrics
- Synarch decomposes goals into multi-agent workflows
- Hermes queries Search/RAG and returns source-cited research
- Hephaestus writes tested code
- Dashboard shows real-time agent activity
- End-to-end mission completes in <3 minutes

## Non-Functional Requirements
- Startup < 2 minutes
- Cost per mission < $0.10
- Crash recovery via PostgreSQL checkpointing
