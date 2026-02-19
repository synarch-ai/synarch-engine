# OpenClaw Deep Dive

## Why It Matters For Synarch

OpenClaw is the strongest reference for gateway control-plane rigor: protocol validation, idempotency, auth, device pairing, and approval workflows.

## Primary Entrypoints

- `references/openclaw/src/gateway/server.impl.ts`
- `references/openclaw/src/gateway/server/ws-connection/message-handler.ts`
- `references/openclaw/src/gateway/protocol/index.ts`
- `references/openclaw/src/gateway/server-methods/chat.ts`
- `references/openclaw/src/gateway/auth.ts`
- `references/openclaw/src/gateway/server-methods/exec-approval.ts`
- `references/openclaw/src/gateway/server-methods/devices.ts`
- `references/openclaw/src/gateway/control-plane-audit.ts`

## Runtime/Data Model

1. Request handling enforces frame validation before execution.
2. Chat pipeline includes message sanitation, transcript persistence discipline, and dedupe caching.
3. Session/transcript model preserves parent chains for recovery and context consistency.
4. Gateway startup path performs config validation and controlled initialization.

## Idempotency and Reliability Patterns

- Transcript-level idempotency key checks prevent duplicate side effects.
- In-memory dedupe cache for repeated client run keys.
- Two-phase exec approval support: immediate acceptance + later decision.

## Auth/Security Model

- Multiple auth modes: `token`, `password`, `trusted-proxy`, `none`.
- Trusted proxy/IP handling and local-vs-remote checks prevent header spoofing assumptions.
- Rate limiting hooks on authentication paths.
- Device pairing and token rotation/revocation endpoints reduce control-plane drift.

## Approval/HITL Patterns

- Explicit `exec.approval.request`, `waitDecision`, `resolve` lifecycle.
- Broadcast events for approval state transitions.
- Timeout and unknown/expired ID handling with explicit error contracts.

## What Synarch Should Adopt

1. Typed protocol validation and explicit error shapes.
2. Idempotency keys for side-effecting mission actions.
3. Explicit approval state machine for sensitive tool calls.
4. Auth mode hardening model and proxy-aware client IP resolution.
5. Audit-friendly actor attribution in control-plane logs.

## What Synarch Should Avoid

1. Copying full gateway implementation wholesale.
2. Mixing transcript persistence concerns into orchestration nodes.

## Suggested Synarch Integration Targets

- `backend/src/api/protocol.py`: request validation/error envelope contract.
- `backend/src/api/idempotency.py`: key extraction, dedupe, and TTL policy.
- `backend/src/approvals/service.py`: approval lifecycle APIs.
- `backend/src/security/auth.py`: mode resolution + proxy-aware IP checks.
- `backend/src/security/audit.py`: actor/device/session attribution.

## Acceptance Checks

1. Repeated side-effect request with same idempotency key executes once.
2. Approval request enters pending state and resolves deterministically.
3. Unauthorized requests fail with structured reason codes.
4. Audit logs include actor/device/connection metadata for privileged actions.
