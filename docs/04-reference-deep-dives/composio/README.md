# Composio Deep Dive

## Why It Matters For Synarch

Composio is the reference for external integration boundary design: user/org isolation, connected accounts, trigger subscriptions, and toolkit routing.

## Primary Entrypoints

- `references/composio/ts/packages/core/src/composio.ts`
- `references/composio/ts/packages/core/src/models/ToolRouter.ts`
- `references/composio/ts/packages/core/src/models/ConnectedAccounts.ts`
- `references/composio/ts/packages/core/src/models/Triggers.ts`
- `references/composio/ts/packages/core/src/models/MCP.ts`
- `references/composio/ts/packages/core/src/types/toolRouter.types.ts`
- `references/composio/ts/packages/core/src/models/Tools.ts`

## Account and Session Model

1. SDK root object composes tools, toolkits, triggers, connected accounts, MCP, and tool-router sessions.
2. Connected account flows are scoped by user IDs and auth config IDs.
3. Tool-router sessions isolate toolkit/tool/tag policies per user context.
4. Session create/use model supports reusable, policy-bounded integration context.

## Trigger/Webhook Model

- Trigger creation/upsert binds trigger to user-connected account and toolkit.
- Webhook payload verification and version handling are explicit.
- Trigger lifecycle includes list/update/delete and active-state management.

## Routing/Policy Model

- Tool router config supports enable/disable semantics for toolkits, tools, and behavior tags.
- Manage-connections mode allows strict connection orchestration.
- Workbench/auto-offload options hint at scaled tool execution pathways.

## What Synarch Should Adopt

1. Strong user/org/account isolation at integration layer.
2. Toolkit-routing session abstraction with allow/deny controls.
3. Trigger subscription model for external event ingestion.
4. Consistent connected-account lifecycle model.

## What Synarch Should Avoid

1. Vendor lock-in via direct SDK assumptions inside orchestration core.
2. Mixing account-linking UX concerns into agent runtime code paths.

## Suggested Synarch Integration Targets

- `backend/src/integrations/accounts.py`
- `backend/src/integrations/tool_router.py`
- `backend/src/integrations/triggers.py`
- `backend/src/integrations/mcp_bridge.py`

## Acceptance Checks

1. Tool execution is scoped by mission actor/user/org context.
2. Unauthorized toolkit/tool use is blocked by router policy.
3. Trigger events can be subscribed, verified, and routed into mission workflow.
4. Connected account state transitions are auditable.
