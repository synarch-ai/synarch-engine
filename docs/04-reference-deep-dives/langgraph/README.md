# LangGraph Deep Dive

## Why It Matters For Synarch

LangGraph is the chosen orchestration engine and is the highest priority reference for core runtime behavior.

## Primary Entrypoints

- `references/langgraph/libs/langgraph/langgraph/graph/state.py`
- `references/langgraph/libs/langgraph/langgraph/types.py`
- `references/langgraph/libs/checkpoint-postgres/README.md`
- `references/langgraph/README.md`

## Runtime/Data Model

1. `StateGraph` builds node graph over shared state (`State -> Partial<State>` updates).
2. Nodes compile into executable graph that supports invoke/stream semantics.
3. State reducers enable deterministic merges when multiple branches update same key.
4. Checkpointer abstraction supports durability modes (`sync`, `async`, `exit`).

## Interrupt/Resume Model

- `Interrupt` type and resume IDs provide deterministic HITL pause/resume control.
- Stream modes expose runtime observability (`values`, `updates`, `checkpoints`, `tasks`, `messages`, `debug`).
- Checkpointer is first-class (not an add-on), making recovery a design-time concern.

## Postgres Persistence Patterns

- Postgres saver requires setup and schema bootstrap.
- Thread-scoped state (`thread_id`) supports resumable multi-turn mission execution.
- Designed for crash recovery and long-running workflows.

## What Synarch Should Adopt

1. Postgres checkpointer for mission durability immediately.
2. Conditional routing and explicit validation nodes.
3. Interrupt/resume paths for human approvals and policy gates.
4. Stream modes for Mission Control telemetry feed.

## What Synarch Should Avoid

1. In-memory-only saver for production mission state.
2. Linear chain orchestration where conditional edges are required.

## Suggested Synarch Integration Targets

- `backend/src/orchestrator/graph.py`: conditional branches + validation gates.
- `backend/src/orchestrator/checkpoint.py`: Postgres checkpointer bootstrap.
- `backend/src/orchestrator/state.py`: typed state with reducer strategy.
- `backend/src/api/sse.py`: map stream events into Mission Control feeds.

## Acceptance Checks

1. Mission survives backend restart and resumes from persisted checkpoint.
2. HITL approval pauses graph and resumes to correct next node.
3. At least one branch decision routes to different specialist paths based on state.
4. Mission Control receives node/task/checkpoint stage updates in real time.
