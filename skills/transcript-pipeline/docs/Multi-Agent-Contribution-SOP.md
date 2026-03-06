# Multi-Agent Contribution SOP

> Document ID: `SOP-MULTI-AGENT-TRANSCRIPT-PIPELINE`  
> Version: `v1.3`  
> Updated: `12 Feb 2026`  
> Scope: contribution protocol for Codex, KiloCode, OpenCode, and future agents.

## 1. Purpose

This SOP defines how agents contribute without breaking:

1. Transcript fidelity.
2. Provenance and traceability.
3. Deterministic validation.
4. Final note quality.

## 2. Canonical Read Order

Every agent must read these first:

1. `docs/Transcript-Intelligence-Master-Blueprint.md`
2. `docs/Design-Review-Record-KiloCode-OpenCode.md`
3. `docs/Multi-Agent-Contribution-SOP.md`

Conflict resolution:

1. Blueprint is canonical for pipeline definitions.
2. SOP defines execution behavior and handoff rules.
3. Design Review is audit and decision history.

## 3. Scope and Non-Goals

In scope:

1. Text-only transcript pipeline.
2. Uncertainty-aware correction.
3. Structured synthesis and pedagogical enhancement.
4. Deterministic hard-gate validation.
5. Cross-lecture linking.

Out of scope (unless explicitly re-enabled):

1. Audio re-transcription.

## 4. Roles and Ownership

Required roles:

1. `Architect`
- Owns architecture decisions, stage boundaries, and contradictions.

2. `Transcript Fidelity Auditor`
- Owns correction safety, uncertainty policy, and source preservation.

3. `Pedagogy Designer`
- Owns explanation quality, examples, and enhancement markers.

4. `Validator Engineer`
- Owns deterministic checks, validation scripts, and pass/fail gates.

Optional roles:

1. `Integration Agent`
- Owns file contracts, automation glue, and merge flow.

2. `Skill Maintainer`
- Owns skill creation/updates when recurring patterns require standardization.

## 4.1 Decision Authority and Parallel Ranking

This project uses explicit decision authority to avoid review loops:

1. `P0 Authority`: Codex Driver
- Final architectural and execution go/no-go decisions.
- Owns acceptance/rejection of external agent proposals.

2. `P1 Authority`: OpenCode Principal Engineer
- Counter-adjudication and technical challenge role.
- Blocks only when deterministic integrity or major correctness risk is found.

3. `P2 Authority`: Kilo Design Auditor
- Edge-case discovery, failure mode surfacing, and risk amplification.
- Advisory unless escalated by P0/P1.

Parallel assignment model:

1. Codex lane (core build): ingestion script, artifact contracts, pilot orchestration.
2. OpenCode lane (quality gate build): deterministic validator script and validation tests.
3. Kilo lane (audit lane): edge-case tests, uncertainty stress-cases, hallucination-risk checks.

## 5. Mandatory Trace Tag

Use this in every recorded decision thread:

```text
[<agent-id>-reply | role:<Role> | date:<DD Mon YYYY> | time:<HH:MM AM/PM IST> | doc:<version> | thread:<ID>]
```

Each thread entry must include:

1. Source
2. Item
3. Decision (`Accepted`, `Accepted with modification`, `Deferred`, `Rejected`)
4. Risk
5. Impact (`Low`, `Medium`, `High`)
6. Mitigation
7. Owner

## 6. Skill Routing Matrix

| Work Type | Primary Skill(s) | Secondary Skill(s) | Output |
|---|---|---|---|
| Design tradeoff analysis | `brainstorming` | `sequential-thinking` | Decision-ready options |
| Multi-step execution planning | `writing-plans` | `sequential-thinking` | Implementable plan |
| Transcript cleanup and reconstruction | `transcribe-refiner` | `sequential-thinking` | Refined transcript + uncertainty artifacts |
| Structured note synthesis | `lecture-alchemist` | `markdown-note-formatter` | Source-mapped structured notes |
| Diagram generation | `concept-cartographer`, `mermaid-diagrams` | `markdown-note-formatter` | Mermaid-first diagrams |
| Final note polishing | `obsidian-markdown`, `markdown-note-formatter` | `concept-cartographer` | Learner-facing note quality |
| Script bug diagnosis | `systematic-debugging` | `sequential-thinking` | Root cause and fix path |
| Script/code checks | `lint-and-validate` | `systematic-debugging` | Check report |
| New skill development | `skill-creator` | `brainstorming` | Skill package |

Rules:

1. Skills are for language transformation and pedagogy.
2. Scripts are for deterministic validation and provenance.

## 7. Execution Stages (Aligned to Blueprint v1.1)

### Stage 1: Ingestion and Refinement

Expected artifacts:

1. `.pipeline/segment_ledger.jsonl`
2. `.pipeline/segment_manifest.jsonl`
3. `.pipeline/refined_transcript.md`
4. `.pipeline/topic_inventory.json`
5. `.pipeline/corrections_log.csv`
6. `.pipeline/uncertainty_report.json`

Stage rule:

1. Low-confidence text is never silently normalized.

### Stage 2: Structured Synthesis

Expected artifacts:

1. `.pipeline/structured_notes.md`
2. `.pipeline/coverage_matrix.json`

Stage rule:

1. Every major section must map to segment IDs.

### Stage 3: Enhancement and Packaging

Expected artifacts:

1. `.pipeline/enhanced_notes.md`
2. `final_notes.md`
3. `bootcamp_index.md`

Stage rules:

1. Added content must use `[ENHANCED: ...]`.
2. Mermaid is primary; ASCII is optional fallback.
3. Keep `.pipeline/structured_notes.md` for rollback comparison.

### Stage 4: Deterministic Validation and Recovery

Expected artifacts:

1. `.pipeline/validation_report.md`
2. `.pipeline/exceptions.json` (if fail)
3. `.pipeline/human_review_queue.md` (if unresolved uncertainty)

Hard gates:

1. 100% segment accountability.
2. Uncertainty retention.
3. No orphan claims without source mapping.

Soft gates:

1. Semantic coverage quality.
2. Pedagogical quality.
3. Hallucination-risk review in enhanced content.

Recovery protocol:

1. On hard-gate fail, generate gap list.
2. Return to earliest affected stage.
3. Reprocess only failing gaps.
4. Re-run validation.
5. Escalate after 3 failed retries.

## 8. Chunking Protocol

When triggered by Blueprint thresholds:

1. Split by timestamp gaps first.
2. Preserve chunk IDs and segment ID continuity.
3. Merge in temporal order.
4. Deduplicate conservatively.
5. Re-run Stage 4 on merged output.

## 9. Contribution Workflow

### Step 1: Join Handshake

Declare:

1. Role
2. Scope
3. Skills
4. Expected artifacts

### Step 2: Change Proposal

Before edits, state:

1. Target files
2. Risks
3. Validation approach

### Step 3: Execute

Perform stage-bounded work only.

### Step 4: Validate

Run relevant checks/scripts.

### Step 5: Record Thread

Log trace entry with required fields.

### Step 6: Handoff

Provide:

1. What changed
2. What passed
3. What failed
4. Open risks
5. Next owner

## 10. Mandatory Edge Cases Log

For each touched stage, record risk/impact/mitigation/owner for:

1. Ambiguous terminology.
2. Speaker alias drift.
3. Chunk boundary concept splitting.
4. Merge duplication artifacts.
5. Uncertainty overload.
6. Mapping mismatch.
7. Unsupported enhanced claims.

## 11. Devil's Advocate Rule

For each major architecture decision accepted, at least one agent must document the strongest counter-position before final lock.

## 12. Definition of Done

A contribution is complete only when:

1. It follows Blueprint and this SOP.
2. Required artifacts for touched stages are present.
3. Hard-gate validations pass (or fail with explicit escalation artifact).
4. Decision trace is recorded.
5. Handoff is complete.

## 13. Quick Start for New Agents

1. Read canonical docs.
2. Pick role.
3. Pick stage.
4. Select skills from Section 6.
5. Execute stage output contract.
6. Run checks.
7. Record trace thread.
8. Hand off.

## 14. Chat-Provider Execution Mode

For users without API keys, this project supports chat-orchestrated execution:

1. Controller guide: `docs/Chat-Provider-Orchestration-Guide.md`
2. Copy-paste prompt: `docs/prompts/Chat-Pipeline-Controller-Prompt.md`
3. Stage prompts:
- `docs/prompts/stages/stage1-refine.md`
- `docs/prompts/stages/stage2-synthesize.md`
- `docs/prompts/stages/stage3-enhance.md`
- `docs/prompts/stages/stage4-validate.md`

Rules in chat-provider mode:

1. User provides only input path and run mode.
2. Provider executes stage-isolated conversations (one stage at a time).
3. Provider must emit required stage artifacts and logs before proceeding.
4. Deterministic hard-gate requires local validator script; otherwise validation is marked non-deterministic.
5. Provider must enforce hard-gate recovery policy.
