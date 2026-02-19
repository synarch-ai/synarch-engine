# CrewAI Deep Dive

## Why It Matters For Synarch

CrewAI is a pattern source for event taxonomy, listener orchestration, and guarded flow logic. It is not a runtime replacement target.

## Primary Entrypoints

- `references/crewAI/lib/crewai/src/crewai/events/event_bus.py`
- `references/crewAI/lib/crewai/src/crewai/flow/flow.py`

## Runtime/Data Model

1. Singleton event bus handles sync and async handlers with execution planning.
2. Handler dependencies (`depends_on`) support ordered, deterministic listener chains.
3. Flow decorators (`@start`, `@listen`, `@router`) express event-driven control paths.
4. Flow state is typed and instrumentable, with pause/resume-like semantics around method execution events.

## Event Semantics

- Explicit event classes and scoped parent/child event context.
- Separation of sync and async handler pools.
- Built-in tracing/listener hooks make observability first-class.

## Routing/HITL Patterns

- Router decorators model branch decisions by returned constants.
- Flow can express complex trigger conditions (AND/OR conditions).
- Human feedback hooks exist in broader flow stack and should inspire Synarch HITL interfaces.

## What Synarch Should Adopt

1. Typed event taxonomy and structured event families.
2. Listener-style extension points for observability/guardrails.
3. Router-style explicit branch declarations for orchestration clarity.

## What Synarch Should Avoid

1. Replacing LangGraph orchestration with Crew runtime.
2. Mixing role-play abstractions into Synarch hierarchy core.

## Suggested Synarch Integration Targets

- `backend/src/events/schema.py`: canonical event classes and fields.
- `backend/src/events/bus.py`: listener registration with ordering constraints.
- `backend/src/orchestrator/routing.py`: routing constants and branch reasons.

## Acceptance Checks

1. Mission events are categorized in typed families (mission, agent, task, deliverable).
2. Listener modules can subscribe without changing orchestrator core.
3. Routing decisions emit machine-readable reason and selected branch.
