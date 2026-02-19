# Synarch Gap Closure and Reference Adoption Implementation Plan

**Goal:** Close the five high-impact architecture/runtime/UI gaps and operationalize reference adoption decisions into implemented, testable Synarch behavior.

**Architecture:** Move from mock linear demo to durable event-driven runtime: PostgreSQL-backed mission state, non-linear LangGraph with HITL checkpoints, NATS event backbone, and cockpit-grade Mission Control UI aligned to the V3 brand system.

**Tech Stack:** FastAPI, LangGraph, PostgreSQL, NATS/JetStream, litellm, Next.js, Tailwind/shadcn, Ollama.

---

## Task 1: Durable Mission State Baseline

**Files:**
- Modify: `backend/src/api/server.py`
- Modify: `backend/src/orchestrator/state.py`
- Create: `backend/src/state/repository.py`
- Create: `backend/src/state/models.py`
- Test: `backend/tests/test_mission_state_persistence.py`

**Steps:**
1. Replace in-memory `MISSIONS` map with repository abstraction.
2. Define persisted mission model (mission metadata, plan, logs, status, timestamps).
3. Wire startup path to initialize storage dependencies.
4. Add read/write methods used by `/mission/start`, `/mission/{id}/state`, `/mission/{id}/stream`.
5. Add tests that validate mission data survives process restart boundary (simulated with repository re-instantiation).

**Verification:**
- `pytest backend/tests/test_mission_state_persistence.py -v`
- Manual: start mission, restart backend, fetch state by mission ID.

---

## Task 2: Non-Linear Graph and HITL Interrupt Path

**Files:**
- Modify: `backend/src/orchestrator/graph.py`
- Modify: `backend/src/orchestrator/state.py`
- Create: `backend/src/orchestrator/routing.py`
- Create: `backend/src/orchestrator/hitl.py`
- Modify: `backend/src/api/server.py` (approval endpoint)
- Test: `backend/tests/test_graph_routing_and_hitl.py`

**Steps:**
1. Add explicit mission phase fields to state (`planning`, `execution`, `review`, `awaiting_approval`, `completed`, `failed`).
2. Replace fixed edges with conditional routing logic.
3. Introduce HITL checkpoint node for sensitive actions and arbitration points.
4. Implement `/mission/{id}/approve` endpoint to resume mission with decision payload.
5. Add tests for: branch routing, pause for approval, resume after approval, reject path behavior.

**Verification:**
- `pytest backend/tests/test_graph_routing_and_hitl.py -v`
- Manual: mission pauses in `awaiting_approval`, resumes only after approval call.

---

## Task 3: Production Agent Runtime and NATS Event Contract

**Files:**
- Modify: `backend/src/agents/agent_node.py`
- Modify: `backend/src/agents/synarch.py`
- Modify: `backend/src/agents/zeus.py`
- Modify: `backend/src/agents/thoth.py`
- Create: `backend/src/nervous_system/publisher.py`
- Create: `backend/src/events/schema.py`
- Test: `backend/tests/test_agent_runtime_and_events.py`

**Steps:**
1. Replace placeholder run logic with `litellm` invocation path and explicit model routing config.
2. Define canonical event envelope (`event_type`, `mission_id`, `agent`, `phase`, `payload`, `timestamp`, `event_id`).
3. Publish agent lifecycle/task events to NATS subjects (`synarch.mission.*`, `synarch.agent.*`, `synarch.task.*`, `synarch.deliverable.*`).
4. Add idempotency key handling for side-effecting mission operations.
5. Add tests validating event schema shape and subject routing.

**Verification:**
- `pytest backend/tests/test_agent_runtime_and_events.py -v`
- Manual: inspect NATS traffic and confirm structured event emission.

---

## Task 4: Mission Control Cockpit (Functional UI)

**Files:**
- Modify: `apps/web/app/page.tsx`
- Create: `apps/web/app/globals.css`
- Create: `apps/web/components/chat-input.tsx`
- Create: `apps/web/components/thought-stream.tsx`
- Create: `apps/web/components/agent-topology.tsx`
- Create: `apps/web/components/task-board.tsx`
- Create: `apps/web/components/deliverables.tsx`
- Create: `apps/web/lib/api.ts`
- Create: `apps/web/lib/events.ts`
- Test: `apps/web` UI tests (if introduced) + manual e2e smoke

**Steps:**
1. Replace static starter UI with 5-panel cockpit layout.
2. Connect to mission start + stream + state endpoints.
3. Render live thought stream from event feed.
4. Render topology/task/deliverables from mission state.
5. Add operator controls for approval actions.

**Verification:**
- Manual smoke: start mission from UI, observe live updates, approve gated action, view final deliverable.

---

## Task 5: Brand System Enforcement in Mission Control

**Files:**
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/app/page.tsx`
- Modify: component files under `apps/web/components/*`
- Reference: `branding/brand-identity.md`

**Steps:**
1. Implement core CSS variables from V3 design system.
2. Apply grid background, plate surfaces, border-first style, sharp radii.
3. Implement log-entry styling with per-agent signature colors.
4. Implement input console pattern (`>_`, terminal behavior cues).
5. Validate desktop cockpit + mobile datapad behavior.

**Verification:**
- Visual check against V3 directives in `branding/brand-identity.md`.
- No generic starter styles remain in Mission Control.

---

## Task 6: Reference Adoption Governance Integration

**Files:**
- Modify: `docs/02-architecture/reference-adoption-matrix.md`
- Modify: `docs/02-architecture/adoption-enforcement-playbook.md`
- Modify: `memory-bank/progress.md`
- Modify: `README.md`
- Modify: `.github/pull_request_template.md`
- Add/Update ADRs as needed in `docs/02-architecture/*`
- Align UI work with `docs/03-product/mission-control-ui-ux-and-functionality-strategy.md`

**Steps:**
1. Update matrix statuses (`planned -> in_progress -> adopted`) as each pattern lands.
2. Update progress milestones to reflect gap closure status.
3. Keep README documentation links aligned with active governance docs.
4. For every reference-derived implementation, include source-path trace in PR notes.
5. Keep PR template checks aligned to governance requirements.

**Verification:**
- Architecture-significant PRs include matrix/progress updates.
- No reference-derived implementation is merged undocumented.

---

## Delivery Order

1. Task 1 (durable state)
2. Task 2 (graph + HITL)
3. Task 3 (runtime + NATS events)
4. Task 4 (functional cockpit)
5. Task 5 (brand enforcement)
6. Task 6 (governance hygiene, continuous)

---

## Exit Criteria

1. Backend restart does not lose mission state.
2. At least one mission flow exercises HITL pause/resume.
3. Agent events flow through NATS and render in UI.
4. Mission Control is operational and brand-consistent.
5. Reference adoption is tracked with at least one `adopted` row backed by implementation evidence.
