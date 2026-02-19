# Autogen Deep Dive

## Why It Matters For Synarch

Autogen is a strong reference for message-oriented multi-agent runtime discipline and MCP workbench integration patterns. It should remain a reference source, not a runtime replacement.

## Primary Entrypoints

- `references/autogen/python/packages/autogen-core/src/autogen_core/_single_threaded_agent_runtime.py`
- `references/autogen/python/packages/autogen-core/src/autogen_core/_intervention.py`
- `references/autogen/python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py`
- `references/autogen/python/packages/autogen-ext/src/autogen_ext/tools/mcp/_workbench.py`

## Runtime/Data Model

1. Runtime centers on envelopes (`SendMessageEnvelope`, `PublishMessageEnvelope`, `ResponseMessageEnvelope`) queued and processed asynchronously.
2. The runtime exposes both directed (`send_message`) and topic-style (`publish_message`) semantics.
3. Intervention hooks allow pre-processing, mutation, or dropping messages before dispatch.
4. Group chat/team logic is layered on top of base runtime primitives, not baked into core transport.

## Event and Control-Plane Semantics

- Message flow is explicit and typed via envelopes.
- Runtime tracing and telemetry hooks are present in core.
- Intervention API (`on_send`, `on_publish`, `on_response`) creates a clean interception point for policy and governance.

## MCP Patterns To Reuse

- `McpWorkbench` (`_workbench.py`) pattern for tool discovery/call orchestration.
- Context-managed lifecycle for MCP server sessions.
- Tool override mapping for controlled exposure of tool names/descriptions.

## What Synarch Should Adopt

1. Message envelope discipline for internal agent runtime events.
2. Interception pipeline concept for guardrails before execution.
3. MCP workbench abstraction style for specialist agents consuming MCP servers.

## What Synarch Should Avoid

1. Full runtime migration away from LangGraph.
2. Tight coupling to Autogen team abstractions where LangGraph state machine is stronger for mission durability.

## Suggested Synarch Integration Targets

- `backend/src/runtime/agent_runtime.py`: envelope types and dispatch semantics.
- `backend/src/runtime/interventions.py`: policy hooks before/after model/tool calls.
- `backend/src/tools/mcp_workbench.py`: normalized MCP session wrapper for Hermes/Janus specialists.

## Acceptance Checks

1. Every agent action emits a typed runtime envelope (not free-form dicts).
2. Guardrail/intervention hook can block or rewrite a tool call deterministically.
3. MCP-backed specialist can list/call tools through a shared workbench adapter.
