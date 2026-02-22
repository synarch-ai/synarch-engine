# Stage 2 Guide: Structured Synthesis

## Inputs

1. `.pipeline/refined_transcript.md`
2. `.pipeline/topic_inventory.json`
3. `.pipeline/segment_manifest.jsonl` (or ledger)

## Outputs

1. `.pipeline/structured_notes.md`
2. `.pipeline/coverage_matrix.json`

## Core Rules

1. Every major section must include source references.
2. Every concept from topic inventory must appear in notes.
3. Do not add pedagogical expansions yet (Stage 3 handles that).
4. Preserve uncertain items; do not drop unresolved ambiguity.

## Suggested Notes Skeleton

- Session summary
- Topic hierarchy
- Detailed topic breakdown
- Code/command references
- Q&A extracted from transcript
- Open uncertainty notes

All sections should include `[source: <segment_id>]` tags.

## Coverage Matrix Requirements

Preferred schema:

```json
{
  "<segment_id>": {
    "sections": ["2.1", "3.4"],
    "status": "covered|noise"
  }
}
```

Alternative schema is acceptable if segment IDs are machine-extractable.

## Fail Conditions

Stage 2 is incomplete when:

1. Any inventory item has no representation in notes.
2. Any major section has no source mapping.
3. Coverage matrix omits content segments.

## Stage 2 Exit Checklist

- Structured notes are complete and source-traceable.
- Coverage matrix exists and maps segment IDs.
- Unmapped content segment count is explicitly reported.
