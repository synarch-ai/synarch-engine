# Mission Control UI/UX and Functionality Strategy

**Developer:** PraxLannister  
*Product + Experience Strategy | 2026-02-19 | Status: ACTIVE*

---

## Problem Statement

Mission Control is currently a static starter page. It does not yet support live orchestration, deliberation visibility, operator intervention, or delivery review.

If Synarch is intended to be a real mission cockpit, the UI must be treated as an operational surface, not a demo.

---

## Design Goals

1. **Operational clarity:** operator can always answer "what stage are we in and why?"
2. **Control authority:** operator can approve/reject/override sensitive actions.
3. **Trust through traceability:** every output links to the agents, events, and tools that produced it.
4. **Low-latency cognition:** dense information display without visual noise.
5. **Brand fidelity:** strict adherence to V3 design system (`branding/brand-identity.md`).

---

## Reference-to-Feature Mapping

| Reference | Pattern to Adopt | UI/Functional Change in Synarch |
|---|---|---|
| `references/llm-council-plus` | 3-stage deliberation display | Add `Deliberation Timeline` panel (`draft -> challenge -> synthesis`) |
| `references/magentic-ui` | Co-planning/co-tasking + guardrails | Add `Action Guard Queue` with approve/reject + reason capture |
| `references/crewAI` | Event taxonomy + listeners | Add filterable `Event Stream` with typed categories |
| `references/openclaw` | control-plane reliability mindset | Add execution metadata strip (idempotency key, retry count, auth scope) |
| `references/letta` | stateful memory blocks | Add `Memory Blocks` panel linked to mission phases |
| `references/playwright-mcp` | deterministic browser tooling | Add specialist action cards for Hermes/Janus browser tasks |
| `references/composio` | user/org isolation + routing | Add `Integration Scope` panel (workspace/user/toolkit context) |

---

## Cockpit Information Architecture

### Desktop ("Cockpit")

- Left rail: mission list, phase, mode, health
- Center: deliberation timeline + thought stream + current task
- Right rail: approval queue, integrations, deliverables
- Bottom strip: transport controls (pause/resume/stop), event rate, error status

### Mobile ("Datapad")

- Single-column priority stack:
  1. phase + approvals
  2. current task + blockers
  3. deliverables
  4. recent events

---

## Functional Upgrades by Priority

### P0 (must ship first)

1. Live mission start/state/stream integration
2. Mission phase and execution mode visibility
3. Approval workflow UI (awaiting_approval -> approve/reject -> resume)
4. Deliverables panel with final output and artifacts

### P1 (next)

1. Deliberation timeline with stage transitions
2. Typed event filters (mission/agent/task/deliverable/system)
3. Memory block viewer aligned to mission steps

### P2 (after stability)

1. Parallel mission sessions
2. Integration routing dashboard
3. Specialist tool cards (browser/code/research execution traces)

---

## V3 Brand Implementation Rules (Non-Negotiable)

1. Use core tokens: `--bg-void`, `--bg-plate`, `--border-primary`, `--signal-amber`.
2. Everything bordered; no soft card aesthetic.
3. Sharp radius default (`0px`), micro-radius only for inputs/actions.
4. Log-entry format must be agent-signature coded.
5. Input must use console pattern (`>_`, bottom-border emphasis).

---

## Success Metrics

1. **Operator intervention latency:** time from approval request to operator decision.
2. **Mission transparency score:** percentage of outputs with visible provenance trail.
3. **Recovery confidence:** successful resume rate after pause/restart.
4. **UI event fidelity:** mismatch rate between backend event stream and rendered timeline.
5. **Brand compliance:** zero violations in V3 token usage audit for cockpit components.

---

## Record-Keeping Requirements

For every shipped UI/functional change:

1. Update `docs/02-architecture/reference-adoption-matrix.md`
2. Update `memory-bank/progress.md`
3. Capture proof in PR notes:
   - changed files
   - acceptance check results
   - before/after UI screenshots (desktop and mobile)
