# ARD-007: HITL Interrupt Contract (The Rule of Two)

**Status:** PROPOSED
**Date:** 2026-02-22
**Author:** Codex (Principal Engineer)
**Context:** S06 HITL Governance

## Context

Synarch Engine must enforce the "Rule of Two": An agent session cannot simultaneously possess critical risk properties without human approval.
We need a deterministic mechanism to:
1.  Pause execution when a risky tool call is planned.
2.  Persist an `ApprovalRequest` record.
3.  Wait for human decision (Approve/Reject) via API.
4.  Resume execution with the decision context.

## Decision

**Use LangGraph `interrupt()` for Human-in-the-Loop (HITL) flow.**

The orchestration graph will include a `check_permission` node (or similar logic within agent nodes) that:
1.  Evaluates `RiskPolicy`.
2.  If risk > threshold:
    a. Persists `Approval` record to Postgres.
    b. Emits `approval.requested` event.
    c. Calls `langgraph.types.interrupt(payload)`.

**Resume Semantics:**
The API `POST /approvals/{id}/decision` will:
1.  Update the `Approval` record.
2.  Locate the LangGraph thread.
3.  Call `Command(resume=decision_payload)` to resume the graph.

**Data Contract:**
- **Interrupt Value:** The value passed to `interrupt()` is the `ApprovalRequest` details (tool, args, reason).
- **Resume Value:** The value passed back to the graph is `{"approved": bool, "modifier": dict}`.

## Consequences

1.  **State Durability:** Interrupts require checkpoints. Our `PostgresCheckpointer` (S05) is critical here.
2.  **UX Latency:** The graph is effectively frozen. Mission Control must visualize this "Paused" state.
3.  **Timeout:** We need a background sweeper (out of scope for S06, but planned) to auto-reject stale approvals.

## Alternatives Considered

- **Async Callbacks:** Graph sends event and waits for a callback webhook. Complex to manage state.
- **Polling:** Agent polls DB loop. Wasteful of tokens and compute.

`interrupt()` is the native LangGraph pattern for this use case.
