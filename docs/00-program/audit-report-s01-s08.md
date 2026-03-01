# Technical Debt & Architecture Audit Report (S01-S08)

**Date:** 2026-02-22
**Auditor Persona:** Backend Principal Engineer Python ML Pro Max
**Scope:** `backend/` and `apps/web/` across S01 to S08 implementations.

## 1. Architectural Boundary Review (Hexagonal Architecture)
**Status: PASS**
- `backend/domain/` is perfectly pure. No imports from `adapters/` or `api/`.
- `backend/ports/` uses abstract classes to define strong boundaries.
- **Rigor Check:** High. The dependency inversion principle is maintained via `container.py`.

## 2. Persistence & SQL Safety (S01, S05)
**Status: PASS with minor warnings**
- `Postgres*Repository` classes correctly use `asyncpg` parameterized queries (`$1`, `$2`), preventing SQL injection.
- Transaction boundaries (`async with conn.transaction():`) are correctly used for multi-statement atomic operations (e.g., Mission creation + Outbox event).
- **Debt Note:** The use of `json.dumps()` in repositories for payload serialization is safe for current dictionary structures but will fail if `datetime` or UUID objects are introduced directly into payload dictionaries without prior Pydantic serialization. *Mitigation:* Ensure models use `model_dump(mode='json')` before passing to repository, which is currently handled by `EventEnvelope` but should be monitored for `Mission.plan` and `Task.result`.

## 3. Event System & Streaming (S03, S04)
**Status: PASS** (Remediated during audit)
- **Previous Debt:** `SSEBridge` naively yielded all history on reconnect, causing client-side duplication.
- **Remediation Applied:** Added cursor tracking in `stream_mission_events`. The bridge now scans history and skips events up to `last_event_id`, correctly resuming the stream.
- Event subjects correctly use `synarch.mission_events.{mission_id}.*` for targeted routing.
- Resource leaks (unclosed NATS subscriptions) were previously addressed.

## 4. Orchestration & HITL Governance (S02, S06)
**Status: NEEDS ATTENTION (Functional Stub)**
- The API layer (`DecideApproval`) correctly resumes the LangGraph runtime using `Command(resume=...)`.
- **Debt Note:** In `backend/domain/orchestrator/graph.py`, the `check_approval` node is currently a stub containing only comments. While the infrastructure for HITL exists and is tested at the API level, the actual trigger point *within the graph* is not physically wired into the `StateGraph` definition.
- **Action Required:** In a future slice (likely S18/AgentTool composition), the tool execution logic must explicitly call `interrupt()` or route to `check_approval` when `PolicyEvaluator` returns `RiskLevel.HIGH`.

## 5. API Contracts & Typing
**Status: PASS**
- Pydantic v2 is used effectively (`model_config = {"from_attributes": True}`).
- Endpoints return strongly typed objects (`TaskResponse`, `DeliverableResponse`).

## Summary Conclusion
The codebase is in excellent shape structurally. The Hexagonal boundaries are solid, enabling the "Fake" testing strategy used when Docker failed. The primary technical debt is the missing internal graph wiring for the HITL interrupt, which should be addressed when concrete tools are added to the agents.