# Stage 4 Prompt: Deterministic Validation + Recovery

```text
You are Stage 4 of the transcript pipeline.

Goal:
Run hard-gate validation deterministically and produce recovery artifacts on failure.

Inputs I will provide:
1) .pipeline/segment_ledger.jsonl
2) .pipeline/coverage_matrix.json
3) final_notes.md
4) .pipeline/uncertainty_report.json (if present)
5) .pipeline/human_review_queue.md (optional)
6) run mode: tool-enabled or tool-restricted

Primary validation command (tool-enabled):
python scripts/validate_coverage.py \
  --ledger .pipeline/segment_ledger.jsonl \
  --final-notes final_notes.md \
  --coverage-matrix .pipeline/coverage_matrix.json \
  --uncertainty-report .pipeline/uncertainty_report.json \
  --human-review-queue .pipeline/human_review_queue.md \
  --report-out .pipeline/validation_report.md \
  --exceptions-out .pipeline/exceptions.json

Hard-gate checks:
1) 100% content segment accountability
2) uncertainty retention
3) no orphan source ids

Note:
- `final_notes.md` may be sanitized with no inline `[source: ...]` tags.
- Coverage accountability can be satisfied via `.pipeline/coverage_matrix.json`.

Soft-gate checks (advisory):
1) semantic coverage quality
2) pedagogical completeness quality
3) hallucination-risk in [ENHANCED] content

Required outputs:
1) .pipeline/validation_report.md
2) .pipeline/exceptions.json
3) .pipeline/human_review_queue.md (if unresolved uncertainty/failure)

If hard-gate FAIL:
1) Generate gap list
2) Identify earliest affected stage
3) Request targeted re-run for only failing gaps
4) Retry up to 3 times
5) Escalate after retry limit

Mode handling:
- tool-enabled: run script and save files
- tool-restricted: perform best-effort checks and clearly label as non-deterministic

Checkpoint (must print at end):
Stage 4 Complete:
- [ ] validation_report.md
- [ ] exceptions.json
- [ ] status = PASS|FAIL
- [ ] retry_count = N

Stop after Stage 4.
```
