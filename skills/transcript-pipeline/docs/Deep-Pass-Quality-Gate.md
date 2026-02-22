# Deep Pass Quality Gate

Strict tutorial-quality gate for `final_notes.md` in `run_chat_pipeline.py`.

## Enable

- Run mode: `python3 scripts/run_chat_pipeline.py run "<path>" --deep-pass`
- Validate mode: `python3 scripts/run_chat_pipeline.py validate "<session_dir>" --deep-pass`

## Checks (Hard Fail)

1. Prerequisite rescue section present.
2. Intuition depth threshold met.
3. At least one Mermaid diagram block.
4. HOTS section with sufficient actionable items.
5. FAQ section with multiple Q/A entries.
6. Practice plan/roadmap section with sufficient items.

## Artifacts

- `.pipeline/deep_pass_report.md`
- `.pipeline/deep_pass_exceptions.json`

## Exit Behavior

- PASS: pipeline proceeds to deterministic validation.
- FAIL: pipeline exits non-zero with deep-pass failure status.
