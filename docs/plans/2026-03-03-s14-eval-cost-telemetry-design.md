# Implementation Plan: S14 - Eval baseline + cost telemetry (Issue #15)

## Objective
Implement evaluation framework baseline (FR-45), LLM-as-judge scoring (FR-46), and track token/latency/mission cost telemetry (FR-47).

## Context
As the first step in Phase 2 (Production Readiness), the system needs to move beyond simple execution to structured measurement of cost, quality, and performance. We already have a `telemetry` field on our `EventEnvelope`, but it is currently not being populated by actual runtime metrics.

## Approach

### 1. Cost & Telemetry Tracking (FR-47)
*   **Mechanism:** Implement a custom `LangChain` CallbackHandler (`TelemetryCallbackHandler`) that intercepts `on_llm_end` and `on_llm_start` events.
*   **Data Extraction:** Extract `token_usage` and calculate `cost` (using LiteLLM cost utilities or static fallback mappings). Calculate `latency` via start/end timestamp diffs.
*   **Emission:** Attach the `TelemetryCallbackHandler` to the agents in `MissionOrchestratorRuntime`. Accumulate metrics into the `MissionState` or emit real-time telemetry events via `EventBus` so they stream to the UI.
*   **State Updates:** Add an aggregate `cost_usd`, `total_tokens` to `MissionState` and persist it to `MissionRepository`.

### 2. Eval Baseline (FR-45, FR-46)
*   **Mechanism:** Create an `evals` package (`backend/domain/evals/`).
*   **LLM-as-Judge:** Build an `EvalRunner` that takes a completed `Mission` (and its `Deliverables`), invokes an LLM (e.g., `gpt-4o`) with a strict grading prompt (e.g., scoring quality, completeness, and adherence to constraints 1-5), and outputs a structured Pydantic `EvaluationResult`.
*   **API/Trigger:** Add an endpoint `POST /api/v1/missions/{mission_id}/eval` to manually trigger an evaluation of a completed mission.
*   **Persistence:** (Optional for this slice, but good practice) Store the evaluation result in the database (new table `mission_evaluations` or append to `Mission` model).

## Plan
1. Implement `TelemetryCallbackHandler` to track tokens, cost, and latency during LLM calls.
2. Inject callback into the LangGraph execution in `MissionOrchestratorRuntime`.
3. Update `MissionState` and `Mission` DB schema to store aggregated telemetry (cost, tokens).
4. Implement the `EvalRunner` service with an LLM-as-judge prompt template.
5. Create `EvaluationResult` models and an API route to trigger it.
6. Write unit tests for the callback handler and eval runner.
