# Transcript Pipeline Kit

A provider-agnostic, deterministic transcript-to-tutorial system for Zoom class captions.

[![Quick Start](https://img.shields.io/badge/Quick_Start-Run_Pipeline-0A66C2?style=for-the-badge&logo=gnubash&logoColor=white)](./USAGEGUIDE.md#quick-start)
[![Deep Pass](https://img.shields.io/badge/Quality_Gate---deep--pass-111827?style=for-the-badge&logo=checkmarx&logoColor=white)](./USAGEGUIDE.md#strict-quality-gate-deep-pass)
[![Deterministic](https://img.shields.io/badge/Deterministic-Ledger_%2B_Validation-0F766E?style=for-the-badge&logo=shield&logoColor=white)](./USAGEGUIDE.md#deterministic-contract)

## Why This Exists

LLM transformations are probabilistic. This kit guarantees accountability by splitting responsibilities:

- Scripts for deterministic stages (`ingest`, `validate`, publish).
- Chat providers for language-heavy stages (refine, synthesize, enhance).
- Traceability artifacts in `.pipeline/` for every session.

## System Architecture

```mermaid
flowchart TD
  A[Raw Zoom Captions] --> B[Stage 0: ingest_zoom_captions.py]
  B --> C[.pipeline/segment_ledger.jsonl]
  C --> D[Stage 1 Chat: refine]
  D --> E[Stage 2 Chat: synthesize]
  E --> F[Stage 3 Chat: enhance]
  F --> G[final_notes.md]
  G --> H[Deep Pass Gate (--deep-pass)]
  H --> I[Stage 4: validate_coverage.py]
  I --> J[publish_tutorial_notes.py]
  J --> K[Published tutorial file]
```

## What You Get

- End-to-end run orchestration: `scripts/run_chat_pipeline.py`
- Deterministic ingestion: `scripts/ingest_zoom_captions.py`
- Deterministic validation: `scripts/validate_coverage.py`
- Standardized publishing: `scripts/publish_tutorial_notes.py`
- Chunk merge utility: `scripts/merge_chunks.py`
- Dedicated Colab explainer pipeline: `scripts/run_colab_notebook_pipeline.py`
- Authenticated resource enrichment (Notion/Canva): `scripts/resource_enrichment.py`

## Strict Quality Gate (`--deep-pass`)

Enable deep tutorial quality enforcement in the runner.

It hard-fails if `final_notes.md` misses any of these:

- Prerequisite rescue section
- Intuition depth (minimum threshold)
- Mermaid diagram block
- HOTS section (minimum actionable items)
- FAQ section (minimum Q/A entries)
- Practice plan/roadmap section

Reports:

- `.pipeline/deep_pass_report.md`
- `.pipeline/deep_pass_exceptions.json`

## Quick Start

```bash
cd /Users/praxlannister/Documents/Zoom/transcript-pipeline-kit
python3 scripts/run_chat_pipeline.py run "<transcript_or_session_path>" --deep-pass
```

## Colab Code Pipeline (AI/ML)

```bash
cd /Users/praxlannister/Documents/Zoom/transcript-pipeline-kit
python3 scripts/run_colab_notebook_pipeline.py
```

This augments AI/ML notes with official resource links, full notebook code appendices, import/function deep explanations, and line-by-line learning commentary.

## Authenticated Resource Enrichment

```bash
cd /Users/praxlannister/Documents/Zoom/transcript-pipeline-kit
python3 scripts/resource_enrichment.py --all-sessions
```

Optional auth for deeper extraction:

- `NOTION_TOKEN_V2` + `NOTION_ACTIVE_USER` for Notion block extraction.
- `RESOURCE_PLAYWRIGHT_STORAGE_STATE` for authenticated Canva capture.

See: [docs/Resource-Enrichment-Authenticated-Flow.md](./docs/Resource-Enrichment-Authenticated-Flow.md)

## Canonical Docs

- Full usage: [USAGEGUIDE.md](./USAGEGUIDE.md)
- Colab pipeline spec: [docs/Colab-Notebook-Explainer-Pipeline.md](./docs/Colab-Notebook-Explainer-Pipeline.md)
- Resource enrichment spec: [docs/Resource-Enrichment-Authenticated-Flow.md](./docs/Resource-Enrichment-Authenticated-Flow.md)
- Prompts: [docs/prompts](./docs/prompts)
- Blueprint: [docs/Transcript-Intelligence-Master-Blueprint.md](./docs/Transcript-Intelligence-Master-Blueprint.md)
- SOP: [docs/Multi-Agent-Contribution-SOP.md](./docs/Multi-Agent-Contribution-SOP.md)

## Repo Layout

```text
transcript-pipeline-kit/
├── README.md
├── USAGEGUIDE.md
├── docs/
│   ├── prompts/
│   ├── Transcript-Intelligence-Master-Blueprint.md
│   └── Multi-Agent-Contribution-SOP.md
└── scripts/
    ├── run_chat_pipeline.py
    ├── run_colab_notebook_pipeline.py
    ├── resource_enrichment.py
    ├── ingest_zoom_captions.py
    ├── validate_coverage.py
    ├── publish_tutorial_notes.py
    └── merge_chunks.py
```
