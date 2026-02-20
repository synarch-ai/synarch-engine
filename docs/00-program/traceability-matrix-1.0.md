# Traceability Matrix v1.0

**Version:** 1.0 | **Date:** 2026-02-20 | **Owner:** PraxLannister

Maps every PRD Functional Requirement to Capability, Phase, Implementation Target, and Test ID.

| FR | Description | CAP | Phase | Priority | Implementation Target | Test ID |
|---|---|---|---|---|---|---|
| FR-1 | Create mission with goal, mode, constraints | CAP-01 | 1 | P0 | `api/routes/missions.py`, `adapters/postgres/repositories.py` | T-1.1 |
| FR-2 | Durable mission record with unique ID and thread context | CAP-01 | 1 | P0 | `adapters/postgres/repositories.py` | T-1.2 |
| FR-3 | Mission states (11 states) | CAP-01 | 1 | P0 | `domain/models/mission.py` | T-1.3 |
| FR-4 | Mission state queryable at any time via API | CAP-01 | 1 | P0 | `api/routes/missions.py` | T-1.4 |
| FR-5 | Mission resumes from persisted state after restart | CAP-01 | 1 | P0 | `adapters/langgraph/checkpointer.py` | T-1.5 |
| FR-6 | LangGraph StateGraph as orchestration core | CAP-02 | 2 | P0 | `domain/orchestrator/graph.py` | T-2.1 |
| FR-7 | Graph supports conditional branches | CAP-02 | 2 | P0 | `domain/orchestrator/routing.py` | T-2.2 |
| FR-8 | Graph supports interrupt/resume for approvals | CAP-02 | 2 | P0 | `domain/orchestrator/graph.py` | T-2.3 |
| FR-9 | Graph includes validation nodes | CAP-02 | 2 | P0 | `domain/orchestrator/graph.py` | T-2.4 |
| FR-10 | Graph checkpoints persist to PostgreSQL | CAP-01 | 1 | P0 | `adapters/langgraph/checkpointer.py` | T-1.6 |
| FR-11 | All model calls route through litellm | CAP-03 | 2 | P0 | `adapters/litellm/provider.py` | T-2.5 |
| FR-12 | Agent system prompts load from soul.md | CAP-03 | 2 | P0 | `domain/agents/base.py` | T-2.6 |
| FR-13 | Agent runtime emits structured lifecycle events | CAP-03 | 2 | P0 | `domain/agents/base.py` | T-2.7 |
| FR-14 | Side-effecting tool calls support idempotency keys | CAP-04 | 2 | P0 | `api/middleware/idempotency.py` | T-2.8 |
| FR-15 | Runtime records retry metadata | CAP-03 | 2 | P1 | `domain/agents/base.py` | T-2.9 |
| FR-16 | NATS required for runtime event publication | CAP-04 | 2 | P0 | `adapters/nats/client.py` | T-2.10 |
| FR-17 | Event subjects include all domains | CAP-04 | 2 | P0 | `domain/events/types.py` | T-2.11 |
| FR-18 | SSE endpoint streams events in near real time | CAP-04 | 3 | P0 | `adapters/nats/sse_bridge.py` | T-3.1 |
| FR-19 | Event payloads typed and versioned | CAP-04 | 2 | P0 | `domain/events/envelope.py` | T-2.12 |
| FR-20 | Events include provenance | CAP-04 | 2 | P0 | `domain/events/envelope.py` | T-2.13 |
| FR-21 | Sensitive operations create approval requests | CAP-02 | 2 | P0 | `domain/orchestrator/graph.py` | T-2.14 |
| FR-22 | Operator can approve/reject with reason | CAP-02 | 2 | P0 | `api/routes/missions.py` | T-2.15 |
| FR-23 | Runtime pauses, resumes deterministically | CAP-02 | 2 | P0 | `domain/orchestrator/graph.py` | T-2.16 |
| FR-24 | Approval outcomes persisted and visible | CAP-02 | 2 | P0 | `adapters/postgres/repositories.py` | T-2.17 |
| FR-25 | Approval timeout configurable | CAP-02 | 2 | P1 | `config.py` | T-2.18 |
| FR-26 | Mission Control displays live phase/status | CAP-05 | 3 | P0 | `apps/web/components/` | T-3.2 |
| FR-27 | UI renders typed event stream with filters | CAP-05 | 3 | P0 | `apps/web/components/thought-stream.tsx` | T-3.3 |
| FR-28 | UI provides approval queue actions | CAP-05 | 3 | P0 | `apps/web/components/approval-modal.tsx` | T-3.4 |
| FR-29 | UI displays deliberation timeline | CAP-05 | 3 | P1 | `apps/web/components/` | T-3.5 |
| FR-30 | UI displays tasks, blockers, deliverables | CAP-05 | 3 | P0 | `apps/web/components/task-board.tsx` | T-3.6 |
| FR-31 | UI supports mission start and inspect | CAP-05 | 3 | P0 | `apps/web/components/command-input.tsx` | T-3.7 |
| FR-32 | UI shows execution mode and graph branch | CAP-05 | 3 | P1 | `apps/web/components/` | T-3.8 |
| FR-33 | V3 design tokens as CSS custom properties | CAP-06 | 3 | P0 | `apps/web/app/globals.css` | T-3.9 |
| FR-34 | Components use V3 primitives | CAP-06 | 3 | P0 | `apps/web/components/` | T-3.10 |
| FR-35 | Sharp-radius and border-first rules | CAP-06 | 3 | P0 | `apps/web/app/globals.css` | T-3.11 |
| FR-36 | Brand compliance checklist gates PRs | CAP-06 | 4 | P1 | CI/review process | T-4.1 |
| FR-37 | Browser tools follow Playwright-MCP pattern | CAP-08 | 5 | P2 | Phase 2+ | T-5.1 |
| FR-38 | Integration execution scoped by actor/org | CAP-08 | 5 | P2 | Phase 2+ | T-5.2 |
| FR-39 | External triggers routeable into workflows | CAP-08 | 5 | P2 | Phase 2+ | T-5.3 |
| FR-40 | MCP tool dev loop supports inspect/debug | CAP-08 | 5 | P2 | Phase 2+ | T-5.4 |
| FR-41 | Gateway auth supports mode configuration | CAP-07 | 4 | P1 | `api/middleware/` | T-4.2 |
| FR-42 | Control-plane actions audit-attributed | CAP-07 | 4 | P0 | `domain/events/envelope.py` | T-4.3 |
| FR-43 | Unsafe operations blocked without approval | CAP-02 | 2 | P0 | `domain/orchestrator/graph.py` | T-2.19 |
| FR-44 | Secrets never in events/logs | CAP-07 | 4 | P0 | All adapters | T-4.4 |
