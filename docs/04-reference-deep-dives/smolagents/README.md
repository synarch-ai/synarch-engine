# Smolagents Deep Dive

## Why It Matters For Synarch

Smolagents is a high-value reference for compact code-agent loops, secure local execution constraints, and lightweight telemetry/monitoring structures.

## Primary Entrypoints

- `references/smolagents/src/smolagents/agents.py`
- `references/smolagents/src/smolagents/local_python_executor.py`
- `references/smolagents/src/smolagents/monitoring.py`
- `references/smolagents/README.md`

## Execution Model

1. Multi-step ReAct-style loop with explicit step memory.
2. Tool calls and final answer handling are explicit typed operations.
3. Monitoring captures timing and token usage per step/run.

## Secure Execution Model

- Local executor restricts dangerous imports/functions.
- Safety checks block dunder abuse and unsafe module/function access.
- Execution time and operation limits constrain runaway code.
- Remote executors (Docker/E2B/WASM paths) are supported in broader stack.

## What Synarch Should Adopt

1. Hardened execution sandbox contract for code-writing specialists.
2. Explicit per-step telemetry for timing and token usage.
3. Clear separation between planning/action/final answer steps.

## What Synarch Should Avoid

1. Running generated code in unrestricted host process.
2. Overcomplicated runtime adoption when focused execution guardrails suffice.

## Suggested Synarch Integration Targets

- `backend/src/execution/sandbox.py`
- `backend/src/execution/policies.py`
- `backend/src/telemetry/run_metrics.py`
- `backend/src/agents/hephaestus/code_runner.py`

## Acceptance Checks

1. Unsafe imports/system calls are blocked by execution policy.
2. Code execution path has timeout + operation caps.
3. Telemetry captures step duration and token usage for each run.
