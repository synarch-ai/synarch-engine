# Letta Deep Dive

## Why It Matters For Synarch

Letta is a strong reference for explicit memory-block modeling and run lifecycle/callback semantics.

## Primary Entrypoints

- `references/letta/letta/schemas/block.py`
- `references/letta/letta/schemas/memory.py`
- `references/letta/letta/schemas/run.py`
- `references/letta/letta/server/rest_api/routers/v1/runs.py`
- `references/letta/letta/server/rest_api/routers/v1/agents.py`

## Memory Model

1. Memory is modeled as typed blocks with labels, limits, metadata, and read-only flags.
2. Character limits are enforced at schema layer to prevent context overflow drift.
3. Separate `file_blocks` and directory-style render paths support attached-file context management.
4. Block labels and block metadata make memory introspection explicit, not implicit prompt text.

## Run Lifecycle Model

- Run has explicit status and timing fields.
- Callback fields (`callback_url`, `callback_sent_at`, `callback_status_code`, `callback_error`) make completion notification auditable.
- Run/step/message endpoints provide traceable operational history.

## What Synarch Should Adopt

1. Block-oriented memory state with explicit labels and limits.
2. Read-only memory sections for policy-locked context.
3. Step-complete webhook/event pattern after durable commits.
4. Run status model with explicit stop reasons.

## What Synarch Should Avoid

1. Importing full Letta runtime/state APIs as dependencies.
2. Overloading orchestration state with long free-form memory text blobs.

## Suggested Synarch Integration Targets

- `backend/src/memory/blocks.py`: block schemas and validators.
- `backend/src/memory/render.py`: deterministic render format for prompts.
- `backend/src/runs/model.py`: run status + callback metadata.
- `backend/src/runs/events.py`: step-complete event emission only after commit.

## Acceptance Checks

1. Memory write beyond limit is rejected with explicit error.
2. Read-only blocks cannot be mutated by agent tool actions.
3. Mission step completion emits callback/event after durable persistence.
4. Run history API can return run status + step timeline for audits.
