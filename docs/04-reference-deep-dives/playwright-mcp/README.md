# Playwright-MCP Deep Dive

## Why It Matters For Synarch

Playwright-MCP is the primary reference for deterministic browser automation through structured accessibility data instead of screenshot-driven heuristics.

## Primary Entrypoints

- `references/playwright-mcp/README.md`
- `references/playwright-mcp/packages/playwright-mcp/index.js`
- `references/playwright-mcp/packages/playwright-mcp/config.d.ts`
- `references/playwright-mcp/packages/playwright-mcp/tests/capabilities.spec.ts`

## Tooling Model

1. MCP server exposes a deterministic browser action API.
2. Accessibility snapshots are first-class context input for model decisions.
3. Capability flags gate tool families (`core`, `pdf`, `vision`, `devtools`, etc.).
4. Config surface supports persistence, origin restrictions, output capture, and session tracing.

## Key Observation

The package surface is intentionally thin (`index.js` delegates to Playwright internals), so behavior contracts should be validated via official docs and integration tests rather than deep local source patching.

## What Synarch Should Adopt

1. Accessibility-snapshot-first browser specialist strategy.
2. Capability-gated tool exposure per agent role.
3. Strict origin/network controls for browser tasks.
4. Reproducible session outputs (trace/video/logs) for audits.

## What Synarch Should Avoid

1. Vision-model dependency for routine browser tasks.
2. Unbounded tool exposure to non-browser-specialist agents.

## Suggested Synarch Integration Targets

- `backend/src/agents/hermes/browser_tools.py`
- `backend/src/agents/janus/browser_validation.py`
- `backend/src/browser/playwright_config.py`
- `backend/src/security/browser_network_policy.py`

## Acceptance Checks

1. Hermes/Janus complete deterministic browser workflow using snapshot tools only.
2. Tool capability restrictions prevent unauthorized browser operations.
3. Browser task runs emit traceable artifacts for replay/review.
