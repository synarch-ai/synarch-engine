# Stage 1 Guide: Ingest + Refine + Uncertainty

## Inputs

1. Raw transcript file (`meeting_saved_closed_caption.txt` or equivalent)
2. Session path

## Deterministic First

Always run deterministic ingestion script before any language transformation:

```bash
python scripts/ingest_captions.py "<input_path>"
```

This creates:

- `.pipeline/segment_ledger.jsonl`
- `.pipeline/segment_manifest.jsonl`

## Required Stage 1 Outputs

1. `.pipeline/segment_ledger.jsonl` (script-generated)
2. `.pipeline/segment_manifest.jsonl` (script-generated)
3. `.pipeline/refined_transcript.md`
4. `.pipeline/topic_inventory.json`
5. `.pipeline/corrections_log.csv`
6. `.pipeline/uncertainty_report.json`

## Refinement Rules

1. Preserve all substantive content.
2. Remove only non-substantive noise segments.
3. Keep source mapping in refined transcript:
- `[source: <segment_id>]`
4. Apply tiered correction policy from `domain-corrections.md`.
5. For LOW confidence items, preserve original wording and list alternatives.

## `refined_transcript.md` Pattern

- Keep natural paragraph flow.
- Include source tags for each paragraph or bullet.
- Keep `---` topic breaks.
- Optionally embed unresolved marker inline:
- `[UNCERTAIN: original -> {alt1 | alt2}]`

## `topic_inventory.json` Minimal Schema

```json
{
  "concepts": [],
  "technical_terms": [],
  "code_or_commands": [],
  "qa_items": [],
  "named_entities": []
}
```

## `corrections_log.csv` Columns

- `segment_id,raw_text,corrected_text,confidence_tier,confidence_score,reasoning`

## `uncertainty_report.json` Item Schema

```json
{
  "segment_id": "...",
  "original_text": "...",
  "alternatives": ["..."],
  "confidence_tier": "LOW",
  "confidence_score": 0.42,
  "reasoning": "...",
  "status": "open"
}
```

## Stage 1 Exit Checklist

- Ledger and manifest exist.
- Refined transcript includes source tags.
- Corrections are logged with confidence + reasoning.
- Uncertainties are explicitly recorded.
- Topic inventory exists and is non-empty for real lectures.
