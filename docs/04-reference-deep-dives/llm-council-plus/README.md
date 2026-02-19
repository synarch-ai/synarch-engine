# LLM Council Plus Deep Dive

## Why It Matters For Synarch

This reference provides a concrete staged deliberation UX pattern that maps directly to Synarch decision workflows.

## Primary Entrypoints

- `references/llm-council-plus/backend/main.py`
- `references/llm-council-plus/backend/council.py`
- `references/llm-council-plus/backend/storage.py`
- `references/llm-council-plus/frontend/src/App.jsx`

## Deliberation Model

1. Stage 1: gather model responses.
2. Stage 2: peer ranking across responses.
3. Stage 3: synthesis/chair result.
4. Optional execution modes (`chat_only`, `chat_ranking`, `full`) let operator choose depth.

## Streaming/Event Model

- SSE stream emits structured stage lifecycle events:
  - `stage1_start`, `stage1_progress`, `stage1_complete`
  - `stage2_start`, `stage2_progress`, `stage2_complete`
  - `stage3_start`, `stage3_complete`
- Search and title generation are emitted as additional event phases.
- Progressive UI updates consume these events incrementally.

## Persistence Model

- Simple JSON conversation storage with index rebuild fallback.
- Message metadata captures execution mode and ranking artifacts.

## What Synarch Should Adopt

1. Staged deliberation event contract in Mission Control.
2. Mode-based execution depth for operator control.
3. Progressive UI updates with explicit stage timers/progress.

## What Synarch Should Avoid

1. Flat file persistence for mission-critical state.
2. Conflating all debate outputs into one undifferentiated response payload.

## Suggested Synarch Integration Targets

- `backend/src/events/stages.py`: stage event schemas.
- `backend/src/orchestrator/modes.py`: execution mode policy.
- `apps/web/src/features/mission-control/stage-stream.ts`: SSE stage mapper.
- `apps/web/src/features/mission-control/components/*`: stage timeline and progress UI.

## Acceptance Checks

1. Mission Control visibly transitions across stages with live progress counts.
2. Operator can pick execution mode before launch.
3. Stage artifacts are persisted and retrievable post-run.
4. UI remains responsive under partial stage completion/failure.
