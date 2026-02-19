# Reference Adoption Matrix

**Owner:** Synarch Architecture  
**Last Updated:** 2026-02-19  
**Source of Truth:** ADR-003 + ADR-004

---

## Purpose

Track exactly which patterns from `references/*` are being adopted, where they map in Synarch, and how adoption is verified.

This document is mandatory to update when architecture/runtime/UI behavior is implemented from a reference repository.

---

## Status Legend

- `planned`: Decision exists, implementation not started.
- `in_progress`: Work started but not fully verified.
- `adopted`: Implemented and verified by acceptance signal.
- `deferred`: Intentionally delayed to later milestone.
- `reference_only`: Studied for patterns, no direct implementation target.

---

## Matrix

| Reference | Decision | Pattern(s) to Extract | Target Synarch Component(s) | Status | Acceptance Signal |
|---|---|---|---|---|---|
| `references/langgraph` | adopt | Postgres checkpointer, interrupts, validation nodes, conditional graph routing | `backend/src/orchestrator/*`, mission state persistence | planned | mission resume after restart + HITL pause/resume path tested |
| `references/openclaw` | adopt_patterns | control-plane protocol, idempotency discipline, pairing/auth model, security audit mindset | API contract, gateway/auth middleware, safety docs | planned | repeated side-effect requests deduped; auth model documented and enforced |
| `references/crewAI` | adopt_patterns | event taxonomy, listener model, guardrail concepts | event schema layer + guardrail hooks | planned | typed event categories used end-to-end; guardrail checks trigger expected decisions |
| `references/autogen` | reference_only | MCP workbench patterns, multi-agent tooling style | MCP integration design notes only | reference_only | documented as pattern source only |
| `references/letta` | adopt_patterns | stateful memory block model, step-complete webhook style | memory model + mission step completion callbacks/webhooks | planned | step completion notification emitted after durable commit |
| `references/llm-council-plus` | adopt_patterns | 3-stage deliberation UX, execution modes, live stage progress | Mission Control decision/review UX | planned | UI shows stage transitions and mode-specific behavior |
| `references/playwright-mcp` | adopt | deterministic browser automation via accessibility snapshots | Hermes/Janus browser specialist tooling | planned | deterministic browser tasks executed without vision-model dependence |
| `references/mcp-use` | adopt_patterns | inspector workflow, session management, auth-ready MCP interfaces | internal MCP dev loop + tool server contracts | planned | tool server inspect/debug loop documented and used in development |
| `references/smolagents` | adopt_patterns | secure execution options (Docker/E2B/WASM), telemetry patterns | code execution sandbox strategy + observability | planned | untrusted code path runs in sandbox mode with telemetry traces |
| `references/magentic-ui` | adopt_patterns | co-planning, co-tasking, action guards, parallel task UX | Mission Control HITL interaction model | planned | operator can intervene, approve/reject actions, run parallel sessions |
| `references/composio` | adopt_patterns | user/org isolation model, triggers, toolkit routing | external integration boundary and account scoping | planned | user/org scoped tool execution documented and enforced |
| `references/swarms` | reference_only | architecture catalog only; no runtime dependency | architecture ideation only | reference_only | no runtime import/dependency introduced |

---

## Review Cadence

1. Update before each milestone planning cycle.
2. Update in each architecture-significant PR.
3. Reconcile with `memory-bank/progress.md` at least once per active sprint.

---

## Non-Compliance Rule

If a pattern is implemented from `references/*` but not recorded here, the implementation is considered incomplete from an architecture governance standpoint.
