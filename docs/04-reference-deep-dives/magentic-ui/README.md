# Magentic-UI Deep Dive

## Why It Matters For Synarch

Magentic-UI is a practical reference for co-planning UX, guarded action execution, and session/team orchestration.

## Primary Entrypoints

- `references/magentic-ui/src/magentic_ui/backend/web/app.py`
- `references/magentic-ui/src/magentic_ui/backend/teammanager/teammanager.py`
- `references/magentic-ui/src/magentic_ui/approval_guard.py`
- `references/magentic-ui/src/magentic_ui/guarded_action.py`
- `references/magentic-ui/README.md`

## Interaction Model

1. Team manager orchestrates run contexts, workspace paths, and config source precedence.
2. Approval guard evaluates action reversibility and can require user confirmation.
3. Guarded action wrapper unifies `prepare -> approval -> invoke -> cleanup` behavior.
4. Async event handling supports progressive UI updates and streamed events.

## HITL/Guardrail Model

- Baseline policy levels: `always`, `maybe`, `never`.
- Optional LLM-based risk guess can upgrade `maybe` to approval-required.
- Approval denial throws explicit error to halt unsafe execution.

## What Synarch Should Adopt

1. Guarded action wrapper pattern for all sensitive tools.
2. Co-planning and co-tasking UI interactions with explicit approvals.
3. Parallel session framing for independent mission branches.

## What Synarch Should Avoid

1. Directly copying full agent suite/runtime assumptions.
2. Delegating all risk decisions to model-only classification.

## Suggested Synarch Integration Targets

- `backend/src/guards/approval.py`: policy + approval service.
- `backend/src/runtime/guarded_action.py`: execution wrapper.
- `apps/web/src/features/mission-control/approvals/*`: approval inbox and decision UI.
- `apps/web/src/features/mission-control/sessions/*`: parallel mission session views.

## Acceptance Checks

1. Sensitive tool call pauses for approval when policy requires it.
2. Approval decision is logged and replayable in mission history.
3. Rejected action never executes side effects.
4. Operator can manage multiple active sessions in Mission Control.
