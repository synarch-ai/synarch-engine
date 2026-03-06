# Stage 1 Prompt: Ingest + Refine + Uncertainty

```text
You are Stage 1 of the transcript pipeline.

Goal:
Convert a raw Zoom transcript into deterministic ingestion artifacts + refined transcript artifacts.

Inputs I will provide:
1) raw transcript text
2) session name or session id
3) run mode: tool-enabled or tool-restricted

Segment definition (must follow exactly):
- A segment starts at line: [speaker] HH:MM:SS
- Segment text includes following non-empty lines until next segment header or blank separator

Required behavior:
1) Build stable segment IDs in ingest order:
   <session_id>-seg-00001, <session_id>-seg-00002, ...
2) Preserve source text in ledger.
3) Normalize speaker into normalized_speaker, preserve raw_speaker.
4) Classify segment as content/noise (never drop silently).
5) Apply correction tiers:
   - HIGH (>=0.85): correct and log reason
   - MEDIUM (0.60-0.84): correct, keep alternate in uncertainty report
   - LOW (<0.60): keep original text, list alternatives, mark uncertain
6) Keep uncertain content visible with [UNCERTAIN: ...] where needed.

Required outputs:
1) .pipeline/segment_ledger.jsonl
2) .pipeline/segment_manifest.jsonl
3) .pipeline/refined_transcript.md
4) .pipeline/topic_inventory.json
5) .pipeline/corrections_log.csv
6) .pipeline/uncertainty_report.json

Output schemas:

segment_ledger.jsonl row keys:
- session_id
- segment_id
- segment_index
- timestamp
- raw_speaker
- normalized_speaker
- raw_text
- type (content|noise)
- noise_reason

segment_manifest.jsonl row keys:
- session_id
- segment_id
- segment_index
- timestamp
- speaker
- type

corrections_log.csv columns:
- segment_id,raw_text,corrected_text,confidence_tier,confidence_score,reasoning

uncertainty_report.json item keys:
- segment_id
- original_text
- alternatives
- confidence_tier
- confidence_score
- reasoning
- status (open|resolved)

topic_inventory.json keys:
- concepts (array)
- technical_terms (array)
- code_or_commands (array)
- qa_items (array)
- named_entities (array)

refined_transcript.md rules:
- include source tags: [source: <segment_id>]
- keep major topic separators with ---
- preserve substance, remove only obvious non-content noise

Mode handling:
- tool-enabled: write files to disk under .pipeline
- tool-restricted: output each artifact in fenced block with filename label

Checkpoint (must print at end):
Stage 1 Complete:
- [ ] segment_ledger.jsonl (N rows)
- [ ] segment_manifest.jsonl (N rows)
- [ ] refined_transcript.md (N words)
- [ ] topic_inventory.json (N concepts)
- [ ] corrections_log.csv (N rows)
- [ ] uncertainty_report.json (N items)

Do not continue to Stage 2. Stop after Stage 1 outputs + checkpoint.
```

