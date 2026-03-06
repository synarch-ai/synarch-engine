# Chat-Provider Orchestration Guide

> Version: `v1.1`  
> Purpose: practical, provider-agnostic execution of the transcript pipeline through chat interfaces without requiring user API keys.

## 1. Reality Check (Important)

Single-conversation full-pipeline execution is not reliable for large transcripts because:

1. Context window pressure grows across stages.
2. Output token limits can block multi-artifact delivery.
3. LLM self-validation is weaker than deterministic script checks.

Therefore, the recommended pattern is:

1. **Stage-isolated conversations** (new conversation per stage).
2. **Chunk only when needed**.
3. **Deterministic local validator script** whenever possible.

## 2. Supported Modes

### Mode A: Tool-Enabled Chat (recommended)

Provider can read/write files and run local scripts.

Result:

1. Full artifact generation to disk.
2. Deterministic hard-gate validation is possible.

### Mode B: Tool-Restricted Chat

Provider cannot run local scripts or write files.

Result:

1. Must run stage-by-stage manually.
2. Artifacts emitted as text blocks.
3. Hard-gate validation becomes best-effort unless user runs local script.

## 3. Canonical Stage Execution Pattern

Run in separate conversations:

1. Stage 1: ingest + refine
2. Stage 2: structured synthesis
3. Stage 3: enhancement + packaging
4. Stage 4: validation + recovery

Prompt files:

1. `docs/prompts/stages/stage1-refine.md`
2. `docs/prompts/stages/stage2-synthesize.md`
3. `docs/prompts/stages/stage3-enhance.md`
4. `docs/prompts/stages/stage4-validate.md`

## 4. Chunking Policy

Chunk only if either threshold is exceeded:

1. Refined transcript > 20,000 words
2. Segment count > 2,500

Chunking rules:

1. Prefer split near midpoint on timestamp gaps >= 120 seconds.
2. Keep segment ID continuity.
3. Process each chunk through Stage 1.
4. Merge Stage 1 outputs before Stage 2.

Current dataset sizing (words):

1. 6 transcripts fit single-pass comfortably.
2. 3 Web3 transcripts are likely chunk candidates.

## 5. Deterministic Validation Strategy

Best option (recommended, no API required):

1. Run local script `scripts/validate_coverage.py`.

Why:

1. Preserves deterministic hard-gate guarantee.
2. Avoids LLM self-policing failure mode.

Fallback option (degraded):

1. Tool-restricted LLM validation only.
2. Must be marked as non-deterministic in report.

## 6. Minimal User Interface

User provides:

1. Input path (file or session folder).
2. Mode (`tool-enabled` or `tool-restricted`).

Everything else is handled by stage prompts and artifacts.

## 7. Output Contract

Learner-tier:

1. `final_notes.md`
2. `bootcamp_index.md`

Pipeline-tier:

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

Run-control:

1. `.pipeline/run_manifest.json`
2. `.pipeline/events.jsonl`

## 8. Recommended Start Commands (Tool-Enabled)

Stage 1 deterministic ingestion:

```bash
python scripts/ingest_zoom_captions.py "<input_file_or_session_dir>"
```

Stage 4 deterministic validation:

```bash
python scripts/validate_coverage.py \
  --ledger ".pipeline/segment_ledger.jsonl" \
  --final-notes "final_notes.md" \
  --coverage-matrix ".pipeline/coverage_matrix.json" \
  --uncertainty-report ".pipeline/uncertainty_report.json" \
  --report-out ".pipeline/validation_report.md" \
  --exceptions-out ".pipeline/exceptions.json"
```

## 9. No-Loop Rule

Do not start another design-review cycle before:

1. Running one pilot transcript end-to-end.
2. Collecting real failure evidence.
3. Applying only blocker-level design edits.

