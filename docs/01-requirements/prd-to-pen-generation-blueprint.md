# PRD -> Pencil (.pen) Generation Blueprint

Date: 2026-02-21  
Scope: Synarch Mission Control from `docs/01-requirements/prd-1.0-final.md`

## 1) Readiness Check (Local)

- Codex MCP registry includes Pencil: `codex mcp list` shows `pencil` as enabled.
- Pencil MCP responds: `get_editor_state` works after opening a document.
- Smoke test passed end-to-end:
  - Created nodes via `pencil/batch_design`
  - Read nodes back via `pencil/batch_get`
  - Rendered screenshot via `pencil/get_screenshot`
- Note: current MCP session is editing an active document named `pencil-new.pen` (not yet persisted under repo path by MCP in this run).

## 2) PRD-to-Design Mapping (What to Generate in .pen)

Primary UI scope comes from:
- Section 14 (Mission Control UI, FR-26..FR-36)
- Section 15 (Approval overlay, FR-21..FR-25)
- Section 11 (typed event stream semantics, FR-18..FR-20)
- Section 8 (mission lifecycle states, FR-3)

Minimum first artifact (`mission-control-shell.pen`):
- Header/status bar
- Left top: Agent topology
- Left bottom: Task board (kanban)
- Right top: Thought stream
- Right bottom: Deliverables
- Bottom: Command input + mode selector
- Overlay: Approval modal with timeout indicator

## 3) Three Ways to Use Pencil from PRD

1. Manual-first (fastest to start)
- Read PRD layout and build frames/components by hand in Pencil.
- Pros: immediate, low setup risk.
- Cons: traceability to FRs can drift.

2. Prompt-assisted (recommended now)
- Keep a "PRD -> panel brief" markdown.
- Use MCP operations to scaffold frame hierarchy, then refine visually.
- Pros: fast iteration plus reproducible structure.
- Cons: still requires disciplined FR tagging.

3. Fully generated pipeline (best long term)
- Parse PRD headings/FRs into intermediate JSON spec, then generate .pen.
- Pros: strongest repeatability and auditability.
- Cons: higher engineering cost up front.

Recommendation: adopt Option 2 now, evolve to Option 3 after Milestone C.

## 4) Operational Workflow (Recommended)

1. Freeze UI requirements slice (FR-21..32, 33..36) for one milestone.
2. Create a `panel-spec.md` per panel with:
- panel goal
- FR coverage
- required states
- data bindings
- acceptance screenshot checklist
3. Generate initial panel frames via MCP (`batch_design`), one panel at a time.
4. Validate visually (`get_screenshot`) and structurally (`batch_get`).
5. Attach FR tags in node names (example: `Thought Stream [FR-27,18]`).
6. Export/save `.pen` into `design/pen/mission-control/`.
7. Implement code from design and verify against PRD acceptance criteria.

## 5) Definition of Done for PRD->.pen

- Every PRD UI requirement maps to at least one named node in `.pen`.
- All five cockpit panels + approval overlay exist and are screenshot-verified.
- Token usage follows brand spec (`docs/modules/branding/brand-identity.md`).
- Traceability table exists: `FR -> panel -> node_id -> code component`.
