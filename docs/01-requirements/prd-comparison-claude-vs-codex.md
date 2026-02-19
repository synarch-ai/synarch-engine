# PRD Comparison: Claude v1.0 vs Codex v1.0

**Date:** 2026-02-20  
**Purpose:** Honest comparison to determine merge strategy

---

## Overview

| Dimension | Claude PRD | Codex PRD |
|---|---|---|
| **File** | `prd-1.0-claude.md` | `prd-1.0-codex.md` |
| **Length** | 1,645 lines | 501 lines |
| **Sections** | 24 | 21 |
| **Style** | Encyclopedic specification (blueprints, schemas, code) | Execution-focused requirements (FR-IDs, acceptance criteria) |

---

## Honest Strengths & Weaknesses

### Claude PRD — Strengths ✅

1. **Implementation-ready detail** — SQL schemas, Python code samples, Pydantic models, NATS subject trees, SSE wire format. A developer could start coding from this without asking questions.
2. **Visual architecture** — ASCII topology diagrams, state machine diagrams, cockpit wireframes, graph topology.
3. **Complete API spec** — 11 endpoints with full request/response Pydantic schemas and error code catalog.
4. **User stories with acceptance criteria** — 18 stories across 5 epics with testable criteria.
5. **Personas** — Named, specific personas (Arjun, Maya, Dmitri) with context/pain/goal/metric.
6. **Cost estimation** — Per-model and per-mission cost analysis.
7. **Glossary** — 14 defined terms for team alignment.

### Claude PRD — Weaknesses ❌

1. **No formal requirement IDs** — User stories have IDs (US-1.1) but functional requirements aren't enumerable. Makes traceability harder.
2. **No idempotency contract** — Codex explicitly requires idempotency keys for side-effecting operations (FR-14). Claude mentions it nowhere.
3. **No event versioning** — Codex requires `schema_version` field in events (FR-19). Claude's EventEnvelope has no version field.
4. **No approval timeout policy** — Codex explicitly calls this out (FR-25, Open Question #2). Claude doesn't address what happens if God never responds.
5. **No provenance tracking** — Codex requires deliverables to link back to source events/tasks (FR-44 pattern, entity `provenance_refs[]`). Claude's deliverable schema lacks this.
6. **No mobile layout** — Codex includes mobile priority stack (Section 11.2). Claude only specifies desktop.
7. **No explicit "Definition of Done"** — Codex has a crisp 8-point DoD (Section 19). Claude has phases but no single "v1.0 is DONE when..." statement.
8. **No platform developer persona** — Claude only addresses operator (God). Codex adds the developer building/extending the system.
9. **No reference adoption traceability** — Codex explicitly lists 10 reference adoption targets with source links (Section 14). Claude doesn't connect PRD requirements to reference deep-dives.
10. **Verbose** — At 3.3x the length, some sections could be tighter. The SQL schema and Python code, while useful, belong in implementation docs not a PRD.

### Codex PRD — Strengths ✅

1. **Formal requirement IDs** — FR-1 through FR-44. Every requirement is enumerable, testable, traceable.
2. **Idempotency-first** — FR-14 and FR-15 mandate idempotency keys and retry metadata. Production-critical.
3. **Event versioning** — Requires `schema_version` in event payloads. Forward-compatible.
4. **Explicit success metrics** — Quantified: "95% recovery rate", "≤300ms p95 event latency", "100% brand compliance".
5. **Definition of Done** — Clear 8-point checklist for v1.0 ship readiness.
6. **Open Questions** — 5 explicit unresolved decisions (timeout policy, retention, sensitive action baseline). Honest about gaps.
7. **Reference adoption as requirements** — Section 14 traces PRD back to deep-dive patterns. Maintains governance contract.
8. **Product principles** — "Governed autonomy over unrestricted autonomy" etc. Guides ambiguous decisions.
9. **Approval entity model** — Explicit `Approval` entity with `decision_reason`, `decided_at`. Claude's HITL is workflow-focused but doesn't model the approval as a first-class entity.
10. **Concise** — 501 lines says everything that matters without implementation detail bloat.

### Codex PRD — Weaknesses ❌

1. **No implementation detail** — No SQL schemas, no Python code, no Pydantic models. A developer needs to translate FR-IDs into code patterns.
2. **No architecture diagrams** — No topology, no state machine diagram, no data flow visualization.
3. **No API schemas** — Lists endpoints but no request/response types, no error code catalog.
4. **No persona depth** — "God" and "Platform Developer" described in 3-4 lines vs. Claude's named personas with scenarios.
5. **No cost analysis** — No model pricing, no per-mission cost estimate.
6. **No user stories** — Requirements are functional (FR-*), not user-centric. Harder to prioritize from user value perspective.
7. **No NATS subject hierarchy** — Mentions NATS requirements but doesn't specify the subject tree.
8. **No UI wireframe** — Mentions layout zones but no visual representation.
9. **No model routing table** — Mentions litellm requirement but doesn't specify which model per agent.
10. **No glossary** — Assumes reader knows Synarch terminology.

---

## Side-by-Side Gap Analysis

| Requirement Area | Claude | Codex | Winner |
|---|---|---|---|
| Mission lifecycle states | 11 states with diagram | 7 states listed | Claude |
| Formal requirement IDs (FR-*) | ❌ No | ✅ FR-1 to FR-44 | **Codex** |
| Idempotency contract | ❌ Missing | ✅ FR-14, FR-15 | **Codex** |
| Event versioning | ❌ Missing | ✅ FR-19 | **Codex** |
| Approval timeout policy | ❌ Missing | ✅ FR-25 | **Codex** |
| Deliverable provenance | ❌ Missing | ✅ provenance_refs[] | **Codex** |
| SQL schema | ✅ Full DDL | ❌ Entity list only | Claude |
| Python code samples | ✅ AgentNode, routing, events | ❌ None | Claude |
| API request/response schemas | ✅ Typed Pydantic | ❌ Endpoint list only | Claude |
| Architecture diagrams | ✅ 5+ ASCII diagrams | ❌ None | Claude |
| NATS subject taxonomy | ✅ Full tree | ❌ Mentioned only | Claude |
| UI wireframe | ✅ Cockpit layout | ❌ Zone descriptions | Claude |
| Success metrics (quantified) | ❌ NFRs are targets, not metrics | ✅ Precise p95/percentages | **Codex** |
| Definition of Done | ❌ No single checklist | ✅ 8-point DoD | **Codex** |
| Product principles | ❌ Not stated | ✅ 5 principles | **Codex** |
| Reference adoption traceability | ❌ Not connected | ✅ 10 adoptions traced | **Codex** |
| User stories | ✅ 18 stories, 5 epics | ❌ No stories | Claude |
| Personas (depth) | ✅ Named, detailed | ⚠️ Functional roles | Claude |
| Cost analysis | ✅ Per-model pricing | ❌ None | Claude |
| Glossary | ✅ 14 terms | ❌ None | Claude |
| Open questions (honest gaps) | ❌ Not listed | ✅ 5 explicit questions | **Codex** |
| Mobile layout | ❌ Desktop only | ✅ Priority stack | **Codex** |

---

## Verdict

**Neither PRD is complete alone. Together they're excellent.**

- **Claude PRD** is the **implementation bible** — read it to understand *how* to build every component.
- **Codex PRD** is the **execution contract** — read it to understand *what's required* and *how to verify it*.

### Recommended Strategy: Merge Into One

Create `prd-1.0-final.md` by:

1. **Use Codex structure** as backbone (FR-IDs, product principles, DoD, open questions, success metrics)
2. **Inject Claude detail** into each FR section (schemas, diagrams, code samples, API specs)
3. **Add Codex-only requirements** to Claude: idempotency (FR-14/15), event versioning (FR-19), approval timeout (FR-25), provenance (deliverable entity), mobile layout
4. **Add Claude-only content** to Codex: SQL DDL, state machine diagram, NATS subject tree, UI wireframe, cost analysis, glossary, personas
5. **Reconcile conflicts** (mission states: 11 vs 7 → use 11; endpoint names: `/mission/start` vs `/mission` → use `/mission/start` per existing code)

### Quick Wins (Apply Now)

Even without a full merge, these Codex gaps should be backported into Claude PRD immediately:

1. Add `schema_version` field to `EventEnvelope`
2. Add `idempotency_key` to side-effecting API requests
3. Add `Approval` as first-class entity in persistence schema
4. Add `provenance_refs` to deliverables table
5. Add "Definition of Done" section
6. Add "Open Questions" section
7. Add FR-* IDs to existing requirements

---

*Both documents reflect strong engineering thinking. The difference is perspective: Claude thinks like an architect showing blueprints; Codex thinks like a PM writing acceptance criteria. The product needs both.*
