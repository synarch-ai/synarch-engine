# Swarms Deep Dive

## Why It Matters For Synarch

Swarms is broad and idea-rich, but should remain architecture-catalog reference only per ADR policy.

## Primary Entrypoints

- `references/swarms/swarms/structs/swarm_router.py`
- `references/swarms/swarms/structs/agent.py`
- `references/swarms/swarms/telemetry/main.py`
- `references/swarms/README.md`

## Architecture Surface

1. `SwarmRouter` supports many swarm types with dynamic routing and execution modes.
2. `Agent` class is highly feature-dense with tool calling, memory options, loop control, and broad config surface.
3. Runtime includes pluggable workflows (sequential, concurrent, voting, council, etc.).

## Risk/Tradeoff Notes

- Surface area is large and opinionated; direct adoption can introduce heavy coupling.
- Telemetry module can send rich system metadata externally if enabled.
- Broad feature set increases governance complexity for enterprise-grade control planes.

## What Synarch Should Adopt

1. Conceptual architecture catalog: workflow varieties, deliberation structures, and agent composition motifs.
2. Selective inspiration for evaluation experiments only.

## What Synarch Should Avoid

1. Runtime migration to Swarms core.
2. Direct dependency on Swarms telemetry or expansive runtime abstractions.
3. Importing high-entropy configuration surface into Synarch core.

## Suggested Synarch Usage

- Keep this reference for architecture ideation in ADRs and design reviews.
- If any single pattern is adopted, re-document it explicitly in Synarch-native terms before implementation.

## Acceptance Checks

1. No Swarms runtime dependency is introduced into production paths.
2. Any adopted pattern is re-specified in Synarch docs and tests before implementation.
