# Stage 2 Prompt: Structured Synthesis + Coverage Mapping

```text
You are Stage 2 of the transcript pipeline.

Goal:
Transform Stage 1 artifacts into structured notes with deterministic source mapping.

Inputs I will provide:
1) .pipeline/refined_transcript.md
2) .pipeline/topic_inventory.json
3) .pipeline/segment_manifest.jsonl (or segment_ledger.jsonl)
4) run mode: tool-enabled or tool-restricted

Required behavior:
1) Build clear hierarchical notes:
   - topic -> subtopic -> micro-concept
2) Ensure every major section includes source tags:
   [source: <segment_id>]
3) Cover topic inventory items without dropping concepts.
4) Produce explicit coverage matrix.

Required outputs:
1) .pipeline/structured_notes.md
2) .pipeline/coverage_matrix.json

coverage_matrix.json schema (preferred):
{
  "<segment_id>": {
    "sections": ["S1", "S3.2", "..."],
    "status": "covered|noise"
  }
}

Rules:
1) Keep source-traceability explicit.
2) Do not add pedagogical expansions yet (that is Stage 3).
3) If a segment has no natural placement, still map it and explain in section note.

Mode handling:
- tool-enabled: write files to .pipeline
- tool-restricted: output artifacts as fenced blocks

Checkpoint (must print at end):
Stage 2 Complete:
- [ ] structured_notes.md (N words)
- [ ] coverage_matrix.json (N mapped segment_ids)
- [ ] unmapped_segment_ids_count = N

Do not continue to Stage 3. Stop after Stage 2 outputs + checkpoint.
```

