# Stage 4 Guide: Deterministic Validation + Recovery

## Inputs

1. `.pipeline/segment_ledger.jsonl`
2. `.pipeline/coverage_matrix.json` (if available)
3. `final_notes.md`
4. `.pipeline/uncertainty_report.json` (if available)
5. `.pipeline/human_review_queue.md` (optional)

## Deterministic Command

Preferred invocation:

```bash
python scripts/validate_coverage.py --pipeline-dir .pipeline
```

Equivalent explicit invocation:

```bash
python scripts/validate_coverage.py \
  --ledger .pipeline/segment_ledger.jsonl \
  --final-notes final_notes.md \
  --coverage-matrix .pipeline/coverage_matrix.json \
  --uncertainty-report .pipeline/uncertainty_report.json \
  --human-review-queue .pipeline/human_review_queue.md \
  --report-out .pipeline/validation_report.md \
  --exceptions-out .pipeline/exceptions.json
```

## Hard Gates (PASS/FAIL)

1. Segment accountability:
- Every content segment must be mapped/referenced.
- Noise segments must include explicit noise reason.
2. Uncertainty retention:
- Unresolved uncertainty must remain in notes or review queue.
3. Orphan claims:
- Referenced source IDs must exist in ledger.

Note:
- `final_notes.md` can be sanitized and may not contain inline `[source: ...]` tags.
- Hard accountability remains deterministic through `.pipeline/coverage_matrix.json` + ledger checks.

## Recovery Loop

If FAIL:

1. Read `.pipeline/exceptions.json`.
2. Identify earliest failing stage.
3. Patch only missing gaps.
4. Re-run validation.
5. Max retries: 3, then escalate unresolved issues.

## Stage 4 Exit Checklist

- `validation_report.md` exists.
- `exceptions.json` exists.
- Hard-gate status is explicit.
- Retry count is tracked.
