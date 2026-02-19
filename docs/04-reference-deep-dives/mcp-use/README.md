# MCP-Use Deep Dive

## Why It Matters For Synarch

MCP-Use provides the strongest practical model for inspector-first MCP development, distributed session management, and auth-capable server surfaces.

## Primary Entrypoints

- `references/mcp-use/libraries/typescript/packages/mcp-use/src/server/mcp-server.ts`
- `references/mcp-use/libraries/typescript/packages/mcp-use/src/server/sessions/ARCHITECTURE.md`
- `references/mcp-use/libraries/typescript/packages/mcp-use/src/server/sessions/session-manager.ts`
- `references/mcp-use/libraries/typescript/packages/mcp-use/src/client.ts`
- `references/mcp-use/libraries/python/mcp_use/server/server.py`
- `references/mcp-use/libraries/python/mcp_use/client/client.py`

## Session Architecture Pattern

1. Split serializable session metadata from non-serializable transport/runtime objects.
2. Separate session store concerns from stream manager concerns.
3. Use message bus/pub-sub for cross-instance notification delivery.
4. Enable idle cleanup and resource subscription cleanup per session.

## Developer Loop Pattern

- Built-in inspector/docs/openmcp endpoints in debug mode.
- Middleware stack for telemetry/logging/auth.
- Router inclusion pattern for modular MCP tool surfaces.

## What Synarch Should Adopt

1. Session metadata vs runtime transport split.
2. Inspector-first workflow for internal MCP tool development.
3. Auth-capable MCP boundary and middleware model.
4. Structured session cleanup and subscription lifecycle management.

## What Synarch Should Avoid

1. Single-process assumptions for all MCP workloads.
2. Embedding transport/socket objects into persistent mission state.

## Suggested Synarch Integration Targets

- `backend/src/mcp/session_store.py`: serializable session metadata.
- `backend/src/mcp/stream_manager.py`: connection fanout + notification bridge.
- `backend/src/mcp/server.py`: middleware and auth hooks.
- `backend/src/mcp/inspector/*`: internal tool inspection endpoints.

## Acceptance Checks

1. Sessions survive API-node handoff in distributed deployment.
2. Notifications reach connected clients regardless of handling node.
3. MCP tool development includes inspector workflow and schema validation.
4. Session cleanup removes stale subscriptions and transports.
