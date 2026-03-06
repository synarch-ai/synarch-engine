# Resource Enrichment (Authenticated Flow)

This pipeline extends resource handling beyond plain link injection by producing session-local artifacts under each class folder.

## Scope

Input source:
- `<session>/.pipeline/resource_manifest.json`

Output artifacts:
- `<session>/.resources/resource_enrichment_report.json`
- provider snapshots (`.html`, `.pdf`, `.png`)
- Notion deep extraction outputs (`*.notion.md`, `*.notion.raw.json`) when auth is configured

## Supported Providers

1. Notion (`notion.so`)
- Public fallback: HTML snapshot + title extraction
- Auth mode: Notion v3 `loadCachedPageChunk` extraction
- Auth requirements:
  - `NOTION_TOKEN_V2`
  - `NOTION_ACTIVE_USER`

2. Canva (`canva.com`)
- Public fallback: HTML snapshot (often 403 on private designs)
- Auth mode: Playwright browser capture using authenticated storage state
- Auth requirement:
  - `RESOURCE_PLAYWRIGHT_STORAGE_STATE=/absolute/path/storage_state.json`

3. Google Drive
- HTML snapshot + title extraction
- PDF direct-download attempt via `uc?export=download&id=<file_id>`

4. Generic links
- HTML snapshot + title extraction

## Commands

All sessions:

```bash
cd /Users/praxlannister/Documents/Zoom/transcript-pipeline-kit
python3 scripts/resource_enrichment.py --all-sessions
```

Single session:

```bash
python3 scripts/resource_enrichment.py \
  --session-dir "/Users/praxlannister/Documents/Zoom/<SESSION_DIR>"
```

Dry run:

```bash
python3 scripts/resource_enrichment.py --all-sessions --dry-run
```

Notion auth run:

```bash
export NOTION_TOKEN_V2="..."
export NOTION_ACTIVE_USER="..."
python3 scripts/resource_enrichment.py --all-sessions
```

Canva auth run:

```bash
export RESOURCE_PLAYWRIGHT_STORAGE_STATE="/absolute/path/to/storage_state.json"
python3 scripts/resource_enrichment.py --all-sessions
```

## Notes and Limits

- Notion API v3 endpoint used here is unofficial and may change.
- Canva export controls are dynamic UI flows; script captures authenticated page content and screenshots, not guaranteed design-export PDFs.
- For locked/private resources without valid auth, report will record fallback behavior and failure notes.

## Report Schema (per session)

`resource_enrichment_report.json` includes:
- timestamp
- session path
- auth flags used
- per-resource status, method, provider, output files, and errors

This keeps resource extraction accountable and auditable in the same style as the transcript pipeline.
