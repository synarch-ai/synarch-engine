# ARD-006: Mission State Store Strategy

**Status:** PROPOSED
**Date:** 2026-02-21
**Author:** Codex (Implementation Mode)
**Deciders:** PraxLannister (God)

## Context

The Synarch Engine requires a durable persistence layer for mission execution state. The PRD v1.2 (FR-75) mandates "End-to-end durable runtime wiring (no in-memory mission SOT)".
This means if the backend process crashes or restarts, the mission state must be recoverable exactly where it left off.

**Constraints:**
1.  **LangGraph Checkpointing:** The orchestration engine (LangGraph) relies on a checkpointer to save graph state (thread execution history).
2.  **Mission Metadata:** We need queryable metadata (mission ID, goal, status, created_at) separate from the opaque graph state blob.
3.  **Relational Integrity:** Tasks, Deliverables, and Approvals have relationships that must be enforced.
4.  **Single Source of Truth:** We want to avoid split-brain scenarios where metadata says "running" but graph state says "completed".

## Decision

**Use PostgreSQL as the unified persistence store for both Mission Metadata and LangGraph Checkpoints.**

We will implement two distinct but related persistence mechanisms within the same PostgreSQL database:
1.  **Mission Metadata Tables:** `missions`, `tasks`, `deliverables`, `approvals`, `mission_events`. These store structured, queryable data for the API and UI.
2.  **LangGraph Checkpoint Tables:** `checkpoints`, `writes`. These store the serialized graph state required by LangGraph to resume execution.

**Key Invariant:**
A Mission ID in the metadata tables corresponds 1:1 to a Thread ID in the checkpoint tables.
`missions.thread_id` will store the LangGraph thread identifier.

## Alternatives Considered

### A) Redis for Checkpoints, Postgres for Metadata
- **Pros:** Fast checkpoint writes.
- **Cons:** Two systems of record. Distributed transaction complexity (writing to Postgres and Redis atomically is hard). Durability configuration in Redis (AOF/RDB) can be tricky.

### B) SQLite for Everything
- **Pros:** Simple, single file.
- **Cons:** Concurrency limits with async Python writers. Not suitable for production scale (Phase 2+).

### C) In-Memory Checkpoints (Current State)
- **Pros:** Fast, simple.
- **Cons:** Violates FR-75. Data loss on restart. unacceptable for production.

## Consequences

1.  **Transactional Integrity:** We must ensure that when a mission state changes (e.g., to "completed"), the corresponding graph checkpoint is also saved. LangGraph handles its own checkpointing, so we must coordinate metadata updates around graph steps.
2.  **Performance:** PostgreSQL writes are slower than memory. We accept this latency for durability.
3.  **Migration:** We need to apply the `001_initial.sql` schema (defined in DB Schema v2.0) to set up the tables.
4.  **Adapter Pattern:** We will implement `AsyncPostgresSaver` from `langgraph.checkpoint.postgres` (or similar adapter) and wire it into the `StateGraph` compilation.

## Verification

- **Test:** Create a mission, run a few steps, kill the process, restart. Verify `missions` table has correct status AND `checkpoints` table has the thread state.
- **Test:** Verify `missions.thread_id` links correctly to the checkpoint.
