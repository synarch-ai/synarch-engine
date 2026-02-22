# Transcript Intelligence Master Blueprint

> Version: `v1.2`  
> Updated: `12 Feb 2026`  
> Scope: text-only pipeline (no audio stage in current scope)

## 1. Objective

Produce high-quality class notes from Zoom transcripts while preserving full informational fidelity from the source transcript.

## 2. Canonical Definitions

1. `segment`
- One header line matching `[speaker] HH:MM:SS`, plus all following non-empty text lines until the next header or blank separator.

2. `segment_id`
- Stable identifier for each segment in ingestion order.

3. `noise segment`
- Segment that carries no substantive class content (for example: greeting checks, pure filler acknowledgments). Noise is never silently dropped; it must be tagged and reasoned.

4. `chunk`
- A bounded subset of a session used when transcript size exceeds processing threshold.

5. `confidence tiers`
- `HIGH`: >= 0.85
- `MEDIUM`: 0.60 to 0.84
- `LOW`: < 0.60

## 3. Non-Negotiable Constraints

1. No context loss from source transcript.
2. No topic loss from source transcript.
3. No structural loss from source transcript.
4. No silent low-confidence replacement.
5. Every major note claim must be source-traceable.

## 4. Canonical 4-Stage Pipeline

### Stage 1: Ingestion and Uncertainty-Aware Refinement

Inputs:

1. Raw `meeting_saved_closed_caption.txt`

Outputs:

1. `.pipeline/segment_ledger.jsonl`
2. `.pipeline/segment_manifest.jsonl`
3. `.pipeline/refined_transcript.md`
4. `.pipeline/topic_inventory.json`
5. `.pipeline/corrections_log.csv`
6. `.pipeline/uncertainty_report.json`

Rules:

1. Preserve raw text in ledger.
2. Tag each segment as `content` or `noise` with explicit reason.
3. Apply tiered correction policy:
- `HIGH`: correct in refined output and log reasoning.
- `MEDIUM`: correct with explicit reasoning and preserve alternate interpretation in uncertainty report.
- `LOW`: keep original text and log alternatives; do not silently normalize.
4. Normalize speaker names into `normalized_speaker` while preserving `raw_speaker`.

### Stage 2: Structured Synthesis with Source Mapping

Inputs:

1. Stage 1 artifacts

Outputs:

1. `.pipeline/structured_notes.md`
2. `.pipeline/coverage_matrix.json`

Rules:

1. Every major section maps to one or more `segment_id` values.
2. Topic inventory items must be represented in notes.

### Stage 3: Enhancement and Packaging

Inputs:

1. Stage 2 artifacts

Outputs:

1. `.pipeline/enhanced_notes.md`
2. `final_notes.md`
3. `bootcamp_index.md`

Rules:

1. Added pedagogical content must be marked with `[ENHANCED]`.
2. Original lecture content must not be overwritten.
3. Mermaid diagrams are primary.
4. ASCII diagrams are optional fallback for contexts where Mermaid is unsuitable.
5. Keep `structured_notes.md` as rollback artifact.
6. Preserve timestamp anchors for major topic transitions using `<!-- T:HH:MM:SS -->`.

### Stage 4: Deterministic Validation and Recovery

Inputs:

1. Stage 1 through Stage 3 outputs

Outputs:

1. `.pipeline/validation_report.md`
2. `.pipeline/exceptions.json` (if fail)
3. `.pipeline/human_review_queue.md` (if unresolved uncertainty)

Hard-gate checks (PASS/FAIL):

1. 100% `segment_id` accountability (covered or explicitly tagged noise with reason).
2. Uncertainty retention (no dropped unresolved uncertainty items).
3. No orphan claims without source mapping.

Soft-gate checks (advisory):

1. Semantic coverage quality.
2. Pedagogical completeness quality.
3. Potential hallucination risk in `[ENHANCED]` content.

Soft-gate mechanism:

1. Extract `[ENHANCED]` claims from enhanced/final notes.
2. For each claim, require at least one related source concept from `topic_inventory.json`.
3. Flag claims with no related source concept for human review.

Recovery protocol on hard-gate fail:

1. Generate gap list.
2. Return to earliest affected stage (usually Stage 2 or Stage 3).
3. Reprocess only failing gaps.
4. Re-run validation.
5. After 3 failed retries, escalate to human review queue.

## 5. Output Contract (Per Session)

Learner-tier outputs:

1. `final_notes.md`
2. `bootcamp_index.md`

Pipeline-tier outputs:

1. `.pipeline/segment_ledger.jsonl`
2. `.pipeline/segment_manifest.jsonl`
3. `.pipeline/refined_transcript.md`
4. `.pipeline/topic_inventory.json`
5. `.pipeline/corrections_log.csv`
6. `.pipeline/uncertainty_report.json`
7. `.pipeline/structured_notes.md`
8. `.pipeline/coverage_matrix.json`
9. `.pipeline/enhanced_notes.md`
10. `.pipeline/validation_report.md`
11. `.pipeline/exceptions.json` (conditional)
12. `.pipeline/human_review_queue.md` (conditional)

## 6. Chunking and Merge Protocol

Trigger chunking when any condition is true:

1. Refined transcript exceeds 20,000 words.
2. Segment count exceeds 2,500.

Chunking rules:

1. Prefer split on timestamp gaps >= 120 seconds.
2. If no clean gap exists, split at nearest topic transition marker.
3. Preserve segment IDs and chunk IDs.

Merge rules:

1. Merge chunk outputs in original temporal order.
2. Deduplicate repeated content conservatively.
3. Rebuild unified coverage matrix.
4. Re-run Stage 4 validation on merged result.

## 7. Conventions

1. Uncertain transcript text marker: `[UNCERTAIN: ...]` (optional inline view, mandatory in structured uncertainty artifact).
2. Enhanced pedagogical content marker: `[ENHANCED: ...]`.
3. Source mapping token format: `[source: <segment_id>]`.

## 8. Definition of Done

A session is complete only when:

1. Stage 4 hard-gate validation passes.
2. No unresolved critical uncertainty remains.
3. Learner-tier outputs are generated.
4. Pipeline-tier outputs are generated and traceable.
