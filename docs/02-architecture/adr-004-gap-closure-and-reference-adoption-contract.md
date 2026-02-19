# ADR-004: Gap Closure and Reference Adoption Contract

**Developer:** PraxLannister  
*Architecture Decision Record | 2026-02-19 | Status: ACCEPTED*

---

## Context

Synarch Engine currently has five high-impact implementation gaps between target architecture and runtime reality:

1. Mission state is in-memory only (no durable recovery).
2. Orchestration is linear, without conditional routing or human-in-the-loop (HITL) interrupts.
3. Agent runtime is placeholder logic (no production `litellm` path, no NATS event publishing contract).
4. Mission Control UI is a static starter page, not an operational cockpit.
5. Brand system is defined but not enforced in UI implementation.

At the same time, `references/*` now contains 12 upstream projects. Without explicit adoption policy, reference usage can drift and become inconsistent.

---

## Decision

Synarch adopts a **Gap Closure Program** with mandatory implementation gates and an explicit **Reference Adoption Contract**.

### A. Gap Closure Workstreams (Mandatory)

#### W1. Durable Mission State

Implement persistent mission state and crash recovery via PostgreSQL-backed state/checkpointing.

**Acceptance Criteria**

1. Mission state survives backend restart.
2. Mission stream can resume from persisted mission ID/thread ID.
3. No core mission state is kept exclusively in process memory.

#### W2. Non-Linear Orchestration + HITL

Replace fixed linear graph with conditional edges, explicit phase/state transitions, and interrupt/approval paths.

**Acceptance Criteria**

1. Graph routing supports branch decisions based on state.
2. HITL approval path exists for sensitive operations and strategic disputes.
3. Mission can pause, await approval, and resume deterministically.

#### W3. Production Agent Runtime

Replace placeholder agent execution with `litellm`-driven runtime, structured tool invocation, and NATS event publishing.

**Acceptance Criteria**

1. Each agent emits structured lifecycle/task events.
2. Model routing is explicit and testable.
3. Retry/idempotency behavior is defined for side-effecting operations.

#### W4. Mission Control Cockpit

Implement production Mission Control surface with live mission state, topology, thought stream, task board, and deliverables.

**Acceptance Criteria**

1. UI reflects live mission events, not static mocks.
2. Operator can start mission, inspect state, approve/reject gated actions.
3. Execution modes and mission phases are visible and actionable.

#### W5. Brand System Enforcement

Translate the locked design system into implementation tokens/components and enforce usage in Mission Control.

**Acceptance Criteria**

1. Core tokens are implemented (`--bg-void`, `--bg-plate`, `--border-primary`, `--signal-amber`, agent signature colors).
2. Mission Control uses defined plate/log/input-console patterns.
3. UI adheres to sharp-radius, border-first, cockpit/datapad directives.

---

## Reference Adoption Contract

The following decisions are now canonical:

| Reference | Decision | Synarch Use |
|---|---|---|
| `langgraph` | **Adopt** | Core orchestration runtime, Postgres checkpointer, interrupts, validation patterns |
| `openclaw` | **Adopt Patterns** | Gateway control-plane patterns: WS contract, idempotency, pairing/auth, security audit mindset |
| `crewAI` | **Adopt Patterns** | Event taxonomy, listener model, guardrail patterns (no runtime switch) |
| `autogen` | **Reference Only** | MCP workbench and multi-agent tooling patterns |
| `letta` | **Adopt Patterns** | Stateful memory blocks and step-complete webhook pattern |
| `llm-council-plus` | **Adopt Patterns** | 3-stage deliberation UX, execution modes, progress display |
| `playwright-mcp` | **Adopt** | Deterministic browser specialist tooling for Hermes/Janus workflows |
| `mcp-use` | **Adopt Patterns** | Inspector-style tool dev loop, session management, auth-ready MCP interfaces |
| `smolagents` | **Adopt Patterns** | Secure code execution model (Docker/E2B/WASM options) + telemetry patterns |
| `magentic-ui` | **Adopt Patterns** | Co-planning, co-tasking, action guards, parallel session UX |
| `composio` | **Adopt Patterns** | User/org isolation, trigger subscriptions, toolkit routing |
| `swarms` | **Reference Only** | Architecture catalog/pattern source; no runtime migration or fork decision |

---

## Governance and Enforcement

To prevent adoption drift:

1. **Architecture-changing PRs** (orchestrator/runtime/control-plane/UI architecture) must update:
   - `docs/02-architecture/reference-adoption-matrix.md`
   - `memory-bank/progress.md`
   - PR checklist in `.github/pull_request_template.md`
2. **New reference-derived behavior** must include:
   - source reference link/path
   - target Synarch component
   - acceptance signal (test, contract check, or live behavior proof)
3. **No implicit adoption:** if a pattern is used from `references/*` and not recorded, it is considered undocumented and incomplete.
4. **Operational enforcement playbook** is mandatory:
   - `docs/02-architecture/adoption-enforcement-playbook.md`
5. **Product/UI strategy alignment** is mandatory for Mission Control:
   - `docs/03-product/mission-control-ui-ux-and-functionality-strategy.md`

---

## Consequences

### Positive

1. Gaps are converted into explicit, testable workstreams.
2. Reference repos become governed inputs, not informal inspiration.
3. Architecture evolution remains auditable through ADR + matrix + progress updates.

### Negative

1. Extra documentation updates are required in implementation PRs.
2. Initial velocity may be slower while contracts and gates are established.

---

*"No pattern is adopted until it is implemented, verified, and recorded."*
