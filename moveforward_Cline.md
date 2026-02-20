# Synarch Engine — Move Forward Plan

**Author:** Claude (Principal Engineer mode)  
**Date:** 2026-02-20  
**Context:** PRD v1.0-final approved, ADR-005 accepted, hexagonal skeleton deployed. Zero runtime functionality yet.

---

## Current State

| Asset | Status |
|---|---|
| PRD v1.0-final (30 sections, FR-1→FR-44) | ✅ Complete |
| ADR-001→005 (5 architecture decisions) | ✅ Complete |
| 12 reference deep-dives | ✅ Complete |
| Hexagonal skeleton (domain/ports/adapters/api) | ✅ Scaffolded (61 files) |
| Agent soul files (7 agents) | ✅ Complete |
| V3 Design System spec | ✅ Locked |
| **Working runtime** | ❌ None — in-memory stubs only |
| **Working UI** | ❌ Placeholder page only |
| **Database** | ❌ Migration written but not applied |
| **NATS wired** | ❌ Adapter exists but not tested |
| **litellm wired** | ❌ Adapter exists but not tested |

---

## Engineering Philosophy

**We do NOT do more docs before building.** We have enough specification. What we need now is:

1. **Vertical slices** — each milestone delivers working, testable functionality
2. **Design docs per workstream** — HLD/LLD only when complexity justifies it
3. **Diagrams alongside code** — Mermaid in markdown, not separate tools
4. **Test before next milestone** — each slice has acceptance criteria

---

## Phase 0: Infrastructure Smoke Test (Day 1)

**Goal:** Verify all 6 processes start and can talk to each other.

### Tasks
- [ ] `docker compose -f infra/docker-compose.yml up -d` — verify all 4 containers healthy
- [ ] Run SQL migration: `psql $DATABASE_URL -f backend/adapters/postgres/migrations/001_initial.sql`
- [ ] `cd backend && pip install -r requirements.txt && python main.py` — verify FastAPI starts at :8000
- [ ] `cd apps/web && npm install && npm run dev` — verify Next.js starts at :3000
- [ ] `curl http://localhost:8000/health` — verify response
- [ ] `curl http://localhost:4222` — verify NATS responds

### Artifacts
- [ ] `.env` file created from `.env.example` with real credentials

### Exit Criteria
All 6 processes running. Health check returns OK with all dependencies connected.

---

## Phase 1: Durable Persistence (Milestone A, Week 1)

**Goal:** Replace in-memory `_MISSIONS` dict with PostgreSQL. Missions survive restart.

### Design Artifacts Needed

| Artifact | Location | Why |
|---|---|---|
| DB Schema (already done) | `backend/adapters/postgres/migrations/001_initial.sql` | ✅ Exists |
| Repository LLD | `docs/05-implementation/lld-persistence.md` | Maps domain models to SQL, connection pooling, transaction boundaries |
| Sequence Diagram | In the LLD | Mission create → PG insert → checkpoint setup → graph invoke |

### Implementation Tasks
- [ ] Implement `PostgresMissionRepository` in `backend/adapters/postgres/repositories.py`
- [ ] Implement `PostgresApprovalRepository`
- [ ] Implement `PostgresTaskRepository`  
- [ ] Implement `PostgresDeliverableRepository`
- [ ] Implement `backend/adapters/postgres/connection.py` (asyncpg pool)
- [ ] Wire repositories into `container.py`
- [ ] Replace `_MISSIONS` in `api/routes/missions.py` with injected `MissionRepository`
- [ ] Wire LangGraph checkpointer to PostgreSQL (already scaffolded)
- [ ] Wire graph execution into mission start background task

### Tests
- [ ] Unit: Repository CRUD operations (mocked DB)
- [ ] Integration: Mission create → query → update status (real PG)
- [ ] Integration: Graph checkpoint → kill process → restart → resume

### Exit Criteria
`POST /mission/start` → creates PG record. Kill backend. Restart. Mission state still exists.

---

## Phase 2: Agent Runtime + NATS Events (Milestone A continued, Week 1-2)

**Goal:** Agents call real LLMs and emit real events. The graph executes end-to-end.

### Design Artifacts Needed

| Artifact | Location | Why |
|---|---|---|
| Agent Interaction Sequence Diagram | `docs/05-implementation/sequence-mission-execution.md` | Shows full flow: Synarch→Zeus→Hephaestus→Janus→Synthesize |
| NATS Event Flow Diagram | Same file | Shows which events fire at each step |

### Implementation Tasks
- [ ] Verify litellm adapter works with Bedrock (Synarch + Opus 4)
- [ ] Verify litellm adapter works with Ollama (Hermes + Llama 3.1)
- [ ] Wire `model_provider` and `event_bus` into all agent constructors via container
- [ ] Test Synarch agent: submit goal → get plan from Opus 4
- [ ] Test Zeus + Hephaestus: delegation → code generation
- [ ] Test Thoth + Hermes: delegation → research
- [ ] Test Janus: review deliverables → verdict
- [ ] Wire full graph: START→Synarch→Zeus/Thoth→Specialists→Janus→Synthesize→END
- [ ] Verify NATS events appear on correct subjects
- [ ] Wire SSE bridge: NATS events → `/mission/{id}/stream` SSE endpoint

### Tests
- [ ] Unit: Each agent `process()` with mocked LLM (returns canned response)
- [ ] Integration: Full graph execution with real NATS
- [ ] Integration: SSE endpoint receives events in correct order

### Exit Criteria
Submit goal via API → all 6 agents execute → events stream to SSE → mission COMPLETED.

---

## Phase 3: Governed Orchestration + HITL (Milestone B, Week 2-3)

**Goal:** Conditional routing works. HITL pauses and resumes. Idempotency deduplicates.

### Design Artifacts Needed

| Artifact | Location | Why |
|---|---|---|
| HITL State Machine Diagram | `docs/05-implementation/lld-hitl-approval.md` | Approval lifecycle: request→pending→decided→resumed |
| Idempotency Handler LLD | Same file | Key storage, TTL, conflict detection |
| Graph Routing Decision Tree | `docs/05-implementation/hld-orchestration-routing.md` | When to route to Zeus, Thoth, or both |

### Implementation Tasks
- [ ] Conditional routing: Synarch plan analysis → Zeus, Thoth, or both
- [ ] Janus review gate: PASS → synthesize, REVISE → loop back (max 3)
- [ ] LangGraph `interrupt()` for HITL approval requests
- [ ] Approval creation in PG when interrupt fires
- [ ] NATS event: `synarch.approval.{id}.requested`
- [ ] API: `POST /mission/{id}/approvals/{approval_id}/decision`
- [ ] Graph resume after approval decision
- [ ] Approval timeout: auto-reject after configurable seconds (FR-25)
- [ ] Idempotency middleware: `Idempotency-Key` header → PG lookup → replay or execute
- [ ] Authority modes: `guided`/`supervised`/`free_rein` behavior differences

### Tests
- [ ] Unit: Routing functions with varied plan inputs
- [ ] Integration: Mission with HITL → pause → approve → resume → complete
- [ ] Integration: Duplicate idempotency key → same response, no re-execution
- [ ] Integration: Approval timeout → auto-reject → mission continues

### Exit Criteria
Research+code mission routes correctly. HITL approval works. Duplicate requests are deduped.

---

## Phase 4: Mission Control UI (Milestone C, Week 3-4)

**Goal:** Operational cockpit. God can start, monitor, approve, and review missions from browser.

### Design Artifacts Needed

| Artifact | Location | Why |
|---|---|---|
| UI Component Tree | `docs/05-implementation/hld-mission-control-ui.md` | Component hierarchy, props, state management |
| Wireframe (Pencil .pen) | `apps/web/designs/cockpit.pen` | Visual layout of 5-panel cockpit |
| SSE Integration Diagram | In HLD | EventSource → React state → component renders |
| V3 Token Map | In HLD | CSS custom properties → Tailwind config mapping |

### Implementation Tasks
- [ ] Set up Tailwind with V3 design tokens (CSS custom properties)
- [ ] Set up fonts: Space Grotesk, Geist Sans, Geist Mono
- [ ] Create V3 base components: DataPlate, LogEntry, InputConsole
- [ ] Implement `useMissionStream` hook (SSE EventSource)
- [ ] Implement layout: 5-panel cockpit grid
- [ ] Panel 1: Agent Topology (SVG hierarchy with pulse states)
- [ ] Panel 2: Thought Stream (chronological events, color-coded by agent)
- [ ] Panel 3: Task Board (kanban columns: Pending→Active→Review→Done)
- [ ] Panel 4: Deliverables (tabbed: Research|Code|Reviews|Synthesis)
- [ ] Panel 5: Command Input (goal text, authority mode selector, send button)
- [ ] Approval Modal (amber border, approve/reject, countdown timer)
- [ ] Mobile priority stack layout
- [ ] Wire to backend API: start mission, stream events, approve/reject

### Tests
- [ ] Component tests: each panel renders correctly with mock data
- [ ] Integration: start mission from UI → see events stream → approve → see completion

### Exit Criteria
God can run a full mission from Mission Control start to finish.

---

## Phase 5: Brand Enforcement + Hardening (Milestone D, Week 4-5)

**Goal:** V3 design system fully applied. Security hardened. All acceptance tests pass.

### Design Artifacts Needed

| Artifact | Location | Why |
|---|---|---|
| Brand Compliance Checklist | `docs/05-implementation/brand-compliance-checklist.md` | Every component verified against V3 spec |
| Security Audit Checklist | `docs/05-implementation/security-checklist.md` | FR-41→44 verified |

### Implementation Tasks
- [ ] V3 grid background (40px crosshair pattern)
- [ ] Plate/void/overlay depth system verified in every component
- [ ] Agent signature colors applied throughout
- [ ] 0px radius enforcement (2px inputs only, >4px forbidden)
- [ ] Lucide icons (1.5px stroke, sparse usage)
- [ ] Animation: 150ms snap-to-finish, scan/blink/glitch keyframes
- [ ] Secrets audit: verify no secrets in events, logs, or UI
- [ ] Error envelope audit: all errors match contract
- [ ] Event redaction audit: payloads are UI-safe
- [ ] Health check: verify all dependency statuses
- [ ] Structured logging: all components emit JSON logs
- [ ] Write E2E acceptance tests (5 scenarios from PRD §17.3)

### Tests
- [ ] E2E: Happy path mission completes with provenance
- [ ] E2E: HITL pause → approve → resume
- [ ] E2E: Crash recovery (kill → restart → resume)
- [ ] E2E: Mission cancellation
- [ ] E2E: Duplicate idempotency key

### Exit Criteria
All 8 DoD items from PRD §25 pass. Brand compliance checklist 100%.

---

## Documents to Create (in execution order)

These documents are written **during** the phase they belong to, not before.

| # | Document | Phase | Type | Location |
|---|---|---|---|---|
| 1 | LLD: Persistence Layer | Phase 1 | Low-Level Design | `docs/05-implementation/lld-persistence.md` |
| 2 | Sequence: Mission Execution | Phase 2 | Flow Diagram (Mermaid) | `docs/05-implementation/sequence-mission-execution.md` |
| 3 | HLD: Orchestration Routing | Phase 3 | High-Level Design | `docs/05-implementation/hld-orchestration-routing.md` |
| 4 | LLD: HITL Approval + Idempotency | Phase 3 | Low-Level Design | `docs/05-implementation/lld-hitl-approval.md` |
| 5 | HLD: Mission Control UI | Phase 4 | High-Level Design | `docs/05-implementation/hld-mission-control-ui.md` |
| 6 | Wireframe: Cockpit Layout | Phase 4 | .pen / Pencil Design | `apps/web/designs/cockpit.pen` |
| 7 | Brand Compliance Checklist | Phase 5 | Checklist | `docs/05-implementation/brand-compliance-checklist.md` |
| 8 | Security Checklist | Phase 5 | Checklist | `docs/05-implementation/security-checklist.md` |

### What We DON'T Need More Of
- ❌ More ADRs (architecture is decided)
- ❌ More PRD sections (requirements are complete)
- ❌ Class diagrams for every file (Pydantic models ARE the schema)
- ❌ Separate DB schema doc (SQL migration IS the schema)
- ❌ Full Figma mockups (Pencil .pen in-repo + V3 spec is enough)

---

## Diagram Strategy

| Diagram Type | When | Tool | Where |
|---|---|---|---|
| Sequence diagrams | Phase 2, 3 | Mermaid in markdown | `docs/05-implementation/` |
| State machine | Already done | ASCII in PRD §8 | ✅ Exists |
| Component tree | Phase 4 | Mermaid in markdown | UI HLD |
| ER diagram | Not needed — SQL migration IS the schema | N/A | ✅ `001_initial.sql` |
| System topology | Already done | ASCII in PRD §7 | ✅ Exists |
| NATS subject tree | Already done | Tree in PRD §11 | ✅ Exists |
| Flow diagram | Phase 2 | Mermaid in sequence doc | `docs/05-implementation/` |

---

## Week-by-Week Schedule

| Week | Phase | Deliverable |
|---|---|---|
| **Week 1** | Phase 0 + Phase 1 | Infra running. Persistence wired. Missions durable. |
| **Week 2** | Phase 2 | Agent runtime live. NATS events streaming. Full graph executes. |
| **Week 3** | Phase 3 | HITL works. Conditional routing. Idempotency. |
| **Week 4** | Phase 4 | Mission Control UI operational. God can use it. |
| **Week 5** | Phase 5 | Brand enforced. Tests passing. DoD met. |

---

## Execution Rules

1. **Write the LLD/HLD at the START of each phase** — not before, not after
2. **Build a vertical slice first** — get one happy path working, then harden
3. **Test at phase boundary** — don't start Phase N+1 until Phase N exits
4. **Update memory-bank after every phase** — `activeContext.md` + `progress.md`
5. **Commit with conventional messages** — `✨ feat`, `🐛 fix`, `📝 docs`, `✅ test`
6. **Ask God before starting each phase** — confirm priorities haven't changed

---

## What to Do RIGHT NOW

**Start Phase 0.** Run `docker compose up`, install deps, verify the backend starts.

Then immediately into Phase 1: implement PostgreSQL repositories and wire the graph.

*"Stop planning. Start building."*
