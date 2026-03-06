#!/usr/bin/env python3
"""Guided runner for transcript-pipeline-kit.

This script automates deterministic stages (ingestion + validation) and guides
chat-driven stages (Stage 1/2/3) with file checks and run logs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class StageSpec:
    name: str
    prompt_relpath: str
    required_outputs: list[str]


@dataclass
class DeepPassCheck:
    id: str
    title: str
    passed: bool
    details: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def kit_root() -> Path:
    return script_dir().parent


def resolve_input(path: Path) -> Path:
    if path.is_file():
        return path
    if path.is_dir():
        exact = path / "meeting_saved_closed_caption.txt"
        if exact.exists():
            return exact
        txts = sorted(path.glob("*.txt"))
        if len(txts) == 1:
            return txts[0]
        raise FileNotFoundError(f"Could not resolve unique transcript .txt in directory: {path}")
    raise FileNotFoundError(f"Input path not found: {path}")


def append_event(pipeline_dir: Path, event: str, data: dict) -> None:
    row = {
        "ts": now_iso(),
        "event": event,
        "data": data,
    }
    path = pipeline_dir / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=True) + "\n")


def load_manifest(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def run_cmd(cmd: list[str], cwd: Path | None = None) -> int:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
    return proc.returncode


def _find_section(text: str, keywords: list[str]) -> str:
    flags = re.IGNORECASE | re.MULTILINE
    # Treat level-2 headings as section boundaries so level-3 FAQ/HOTS entries remain inside section content.
    heading_pattern = re.compile(r"^##\s+.*$", flags)
    matches = list(heading_pattern.finditer(text))
    if not matches:
        return ""

    kw_pattern = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
    for idx, m in enumerate(matches):
        heading = m.group(0)
        if not kw_pattern.search(heading):
            continue
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        return text[start:end]
    return ""


def _count_list_items(section: str) -> int:
    count = 0
    for line in section.splitlines():
        if re.match(r"^\s*[-*]\s+\S+", line):
            count += 1
        elif re.match(r"^\s*\d+\.\s+\S+", line):
            count += 1
    return count


def _run_deep_pass_checks(final_notes_text: str) -> list[DeepPassCheck]:
    text = final_notes_text
    lower = text.lower()

    prereq_section = _find_section(text, ["prereq", "prerequisite"])
    hots_section = _find_section(text, ["hots", "high-order", "high order"])
    faq_section = _find_section(text, ["faq"])
    practice_section = _find_section(text, ["practice roadmap", "practice plan", "practice"])

    intuition_hits = len(re.findall(r"\bintuition\b", lower))
    mermaid_hits = len(re.findall(r"```mermaid", lower))
    hots_items = _count_list_items(hots_section)
    faq_q_hits = len(
        re.findall(
            r"(?im)^\s*(?:###\s+)?q(?:\d+)?(?:\s*[:\-.]|\b)",
            faq_section,
        )
    )
    practice_items = _count_list_items(practice_section)

    checks = [
        DeepPassCheck(
            id="prereq_rescue",
            title="Prerequisite rescue section",
            passed=bool(prereq_section.strip()),
            details="Requires a dedicated prerequisites/prereq section.",
        ),
        DeepPassCheck(
            id="intuition_depth",
            title="Intuition-first depth",
            passed=intuition_hits >= 3,
            details=f"Found 'intuition' mentions: {intuition_hits} (min: 3).",
        ),
        DeepPassCheck(
            id="mermaid_diagrams",
            title="Mermaid diagrams present",
            passed=mermaid_hits >= 1,
            details=f"Found mermaid blocks: {mermaid_hits} (min: 1).",
        ),
        DeepPassCheck(
            id="hots_section",
            title="HOTS section with actionable questions",
            passed=bool(hots_section.strip()) and hots_items >= 2,
            details=f"HOTS list items: {hots_items} (min: 2).",
        ),
        DeepPassCheck(
            id="faq_section",
            title="FAQ section with multiple Q/A entries",
            passed=bool(faq_section.strip()) and faq_q_hits >= 2,
            details=f"FAQ question markers: {faq_q_hits} (min: 2).",
        ),
        DeepPassCheck(
            id="practice_plan",
            title="Practice plan/roadmap section",
            passed=bool(practice_section.strip()) and practice_items >= 2,
            details=f"Practice items: {practice_items} (min: 2).",
        ),
    ]
    return checks


def run_deep_pass(session_dir: Path) -> int:
    pipeline_dir = session_dir / ".pipeline"
    pipeline_dir.mkdir(parents=True, exist_ok=True)
    final_notes_path = session_dir / "final_notes.md"
    report_path = pipeline_dir / "deep_pass_report.md"
    exceptions_path = pipeline_dir / "deep_pass_exceptions.json"

    if not final_notes_path.exists():
        report_path.write_text(
            "# Deep Pass Report\n\n- **status:** FAIL\n- **reason:** final_notes.md missing\n",
            encoding="utf-8",
        )
        exceptions_path.write_text(
            json.dumps(
                {
                    "status": "FAIL",
                    "reason": "missing_final_notes",
                    "missing": ["final_notes.md"],
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return 1

    text = final_notes_path.read_text(encoding="utf-8")
    checks = _run_deep_pass_checks(text)
    failed = [c for c in checks if not c.passed]
    passed = not failed

    lines = ["# Deep Pass Report", "", f"- **status:** {'PASS' if passed else 'FAIL'}", ""]
    lines.append("## Checks")
    for c in checks:
        mark = "PASS" if c.passed else "FAIL"
        lines.append(f"- **{c.title}:** {mark} - {c.details}")
    lines.append("")
    if failed:
        lines.append("## Missing Requirements")
        for c in failed:
            lines.append(f"- `{c.id}`: {c.title}")
        lines.append("")

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    exceptions_path.write_text(
        json.dumps(
            {
                "status": "PASS" if passed else "FAIL",
                "checks": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "passed": c.passed,
                        "details": c.details,
                    }
                    for c in checks
                ],
                "failed_ids": [c.id for c in failed],
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0 if passed else 1


def check_outputs(session_dir: Path, output_paths: list[str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for rel in output_paths:
        p = session_dir / rel
        if not p.exists():
            missing.append(rel)
    return (len(missing) == 0, missing)


def write_handoff_file(session_dir: Path, stage: StageSpec) -> Path:
    pipeline_dir = session_dir / ".pipeline"
    handoff = pipeline_dir / f"{stage.name}_chat_handoff.md"
    prompt_path = kit_root() / stage.prompt_relpath
    lines = [
        f"# {stage.name.upper()} Chat Handoff",
        "",
        f"Prompt file: `{prompt_path}`",
        f"Session dir: `{session_dir}`",
        "",
        "## Required outputs",
    ]
    for rel in stage.required_outputs:
        lines.append(f"- `{session_dir / rel}`")
    lines.append("")
    lines.append("After generating outputs in chat, save files and return to this runner.")
    handoff.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return handoff


def default_stages() -> list[StageSpec]:
    return [
        StageSpec(
            name="stage1",
            prompt_relpath="docs/prompts/stages/stage1-refine.md",
            required_outputs=[
                ".pipeline/refined_transcript.md",
                ".pipeline/topic_inventory.json",
                ".pipeline/corrections_log.csv",
                ".pipeline/uncertainty_report.json",
            ],
        ),
        StageSpec(
            name="stage2",
            prompt_relpath="docs/prompts/stages/stage2-synthesize.md",
            required_outputs=[
                ".pipeline/structured_notes.md",
                ".pipeline/coverage_matrix.json",
            ],
        ),
        StageSpec(
            name="stage3",
            prompt_relpath="docs/prompts/stages/stage3-enhance.md",
            required_outputs=[
                ".pipeline/enhanced_notes.md",
                "final_notes.md",
                "bootcamp_index.md",
            ],
        ),
    ]


def ensure_ingestion(input_file: Path, session_dir: Path, skip_ingest: bool) -> None:
    pipeline_dir = session_dir / ".pipeline"
    ledger = pipeline_dir / "segment_ledger.jsonl"
    manifest = pipeline_dir / "segment_manifest.jsonl"

    if skip_ingest and ledger.exists() and manifest.exists():
        return

    cmd = [
        sys.executable,
        str(script_dir() / "ingest_zoom_captions.py"),
        str(input_file),
    ]
    rc = run_cmd(cmd)
    if rc != 0:
        raise RuntimeError("Ingestion failed.")


def run_validation(session_dir: Path) -> int:
    pipeline_dir = session_dir / ".pipeline"
    cmd = [
        sys.executable,
        str(script_dir() / "validate_coverage.py"),
        "--ledger",
        str(pipeline_dir / "segment_ledger.jsonl"),
        "--final-notes",
        str(session_dir / "final_notes.md"),
        "--coverage-matrix",
        str(pipeline_dir / "coverage_matrix.json"),
        "--uncertainty-report",
        str(pipeline_dir / "uncertainty_report.json"),
        "--human-review-queue",
        str(pipeline_dir / "human_review_queue.md"),
        "--report-out",
        str(pipeline_dir / "validation_report.md"),
        "--exceptions-out",
        str(pipeline_dir / "exceptions.json"),
    ]
    return run_cmd(cmd)


def publish_tutorial(session_dir: Path) -> int:
    cmd = [
        sys.executable,
        str(script_dir() / "publish_tutorial_notes.py"),
        "--session-dir",
        str(session_dir),
        "--root",
        str(session_dir.parent),
    ]
    return run_cmd(cmd)


def run_pipeline(args: argparse.Namespace) -> int:
    input_file = resolve_input(Path(args.input_path).expanduser().resolve())
    session_dir = input_file.parent
    pipeline_dir = session_dir / ".pipeline"
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = pipeline_dir / "run_manifest.json"
    manifest = load_manifest(manifest_path)
    if not manifest:
        manifest = {
            "schema_version": "1.0",
            "run_id": datetime.now().strftime("run-%Y%m%d-%H%M%S"),
            "created_at": now_iso(),
            "input_path": str(input_file),
            "session_dir": str(session_dir),
            "mode": args.mode,
            "deep_pass": bool(args.deep_pass),
            "status": "running",
            "stages": {
                "ingest": "pending",
                "stage1": "pending",
                "stage2": "pending",
                "stage3": "pending",
                "deep_pass": "pending" if args.deep_pass else "skipped",
                "stage4": "pending",
            },
        }
        save_manifest(manifest_path, manifest)
    else:
        manifest.setdefault("stages", {})
        for stage_key in ("ingest", "stage1", "stage2", "stage3", "stage4"):
            manifest["stages"].setdefault(stage_key, "pending")
        if args.deep_pass:
            manifest["stages"].setdefault("deep_pass", "pending")
        else:
            manifest["stages"].setdefault("deep_pass", "skipped")
        manifest["deep_pass"] = bool(args.deep_pass)
        save_manifest(manifest_path, manifest)

    append_event(
        pipeline_dir,
        "run_started",
        {"input_path": str(input_file), "mode": args.mode, "deep_pass": bool(args.deep_pass)},
    )

    try:
        ensure_ingestion(input_file, session_dir, args.skip_ingest)
        manifest["stages"]["ingest"] = "completed"
        save_manifest(manifest_path, manifest)
        append_event(pipeline_dir, "ingest_completed", {})

        for stage in default_stages():
            ok, missing = check_outputs(session_dir, stage.required_outputs)
            if ok:
                manifest["stages"][stage.name] = "completed"
                save_manifest(manifest_path, manifest)
                append_event(pipeline_dir, f"{stage.name}_already_complete", {})
                continue

            handoff = write_handoff_file(session_dir, stage)
            append_event(
                pipeline_dir,
                f"{stage.name}_handoff_created",
                {"handoff": str(handoff), "missing": missing},
            )

            print(f"\n{stage.name.upper()} is pending.")
            print(f"Prompt: {kit_root() / stage.prompt_relpath}")
            print(f"Handoff: {handoff}")
            print("Missing outputs:")
            for rel in missing:
                print(f"- {session_dir / rel}")

            if args.non_interactive:
                manifest["status"] = "waiting_for_chat_stage"
                save_manifest(manifest_path, manifest)
                return 3

            input("\nRun this stage in chat, save outputs, then press Enter to continue...")

            ok_after, missing_after = check_outputs(session_dir, stage.required_outputs)
            if not ok_after:
                append_event(pipeline_dir, f"{stage.name}_outputs_missing", {"missing": missing_after})
                manifest["status"] = "failed_missing_stage_outputs"
                save_manifest(manifest_path, manifest)
                print("\nStill missing outputs:")
                for rel in missing_after:
                    print(f"- {session_dir / rel}")
                return 4

            manifest["stages"][stage.name] = "completed"
            save_manifest(manifest_path, manifest)
            append_event(pipeline_dir, f"{stage.name}_completed", {})

        if args.deep_pass:
            rc_deep = run_deep_pass(session_dir)
            manifest["stages"]["deep_pass"] = "completed" if rc_deep == 0 else "failed"
            save_manifest(manifest_path, manifest)
            append_event(pipeline_dir, "deep_pass_completed", {"exit_code": rc_deep})
            if rc_deep != 0:
                manifest["status"] = "fail_deep_pass"
                manifest["completed_at"] = now_iso()
                save_manifest(manifest_path, manifest)
                print("\nPipeline complete: FAIL (deep pass)")
                print(f"Deep pass report: {pipeline_dir / 'deep_pass_report.md'}")
                print(f"Deep pass exceptions: {pipeline_dir / 'deep_pass_exceptions.json'}")
                return 1

        rc_val = run_validation(session_dir)
        manifest["stages"]["stage4"] = "completed" if rc_val == 0 else "failed"
        manifest["status"] = "pass" if rc_val == 0 else "fail"
        manifest["completed_at"] = now_iso()
        save_manifest(manifest_path, manifest)
        append_event(pipeline_dir, "validation_completed", {"exit_code": rc_val})

        if rc_val == 0:
            rc_pub = publish_tutorial(session_dir)
            append_event(pipeline_dir, "publish_tutorial_completed", {"exit_code": rc_pub})
            if rc_pub != 0:
                manifest["status"] = "pass_with_publish_warning"
                save_manifest(manifest_path, manifest)
                print("\nPipeline complete: PASS (publish warning)")
                print("Tutorial publish step failed; final_notes.md is still available.")
                print(f"Final notes: {session_dir / 'final_notes.md'}")
                print(f"Validation report: {pipeline_dir / 'validation_report.md'}")
                return 0

            print("\nPipeline complete: PASS")
            print(f"Final notes: {session_dir / 'final_notes.md'}")
            print("Published tutorial file: see bootcamp_index.md in session folder")
            print(f"Validation report: {pipeline_dir / 'validation_report.md'}")
            return 0

        print("\nPipeline complete: FAIL")
        print(f"Exceptions: {pipeline_dir / 'exceptions.json'}")
        return 1

    except Exception as exc:
        append_event(pipeline_dir, "run_error", {"error": str(exc)})
        manifest["status"] = "error"
        manifest["error"] = str(exc)
        save_manifest(manifest_path, manifest)
        print(f"ERROR: {exc}")
        return 2


def run_status(args: argparse.Namespace) -> int:
    session_dir = Path(args.session_dir).expanduser().resolve()
    pipeline_dir = session_dir / ".pipeline"
    manifest_path = pipeline_dir / "run_manifest.json"

    if not manifest_path.exists():
        print(f"No run manifest found: {manifest_path}")
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(json.dumps(manifest, ensure_ascii=True, indent=2))
    return 0


def run_validate_only(args: argparse.Namespace) -> int:
    session_dir = Path(args.session_dir).expanduser().resolve()
    if not session_dir.exists():
        print(f"Session directory not found: {session_dir}")
        return 2
    rc_val = run_validation(session_dir)
    if rc_val != 0:
        return rc_val
    if args.deep_pass:
        rc_deep = run_deep_pass(session_dir)
        if rc_deep != 0:
            print(f"Deep pass failed: {session_dir / '.pipeline' / 'deep_pass_report.md'}")
            return 1
        print(f"Deep pass passed: {session_dir / '.pipeline' / 'deep_pass_report.md'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guided runner for transcript-pipeline-kit.")
    sub = parser.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run", help="Run guided pipeline")
    p_run.add_argument("input_path", help="Transcript file or session directory")
    p_run.add_argument("--mode", default="tool-restricted", choices=["tool-enabled", "tool-restricted"])
    p_run.add_argument("--skip-ingest", action="store_true", help="Skip ingestion if ledger/manifest already exist")
    p_run.add_argument("--non-interactive", action="store_true", help="Stop at pending chat stage instead of waiting for input")
    p_run.add_argument(
        "--deep-pass",
        action="store_true",
        help="Enable strict tutorial depth gate (prereq, intuition, mermaid, HOTS, FAQ, practice).",
    )

    p_status = sub.add_parser("status", help="Show run status from run_manifest.json")
    p_status.add_argument("session_dir", help="Session directory containing .pipeline")

    p_val = sub.add_parser("validate", help="Run validation only")
    p_val.add_argument("session_dir", help="Session directory containing .pipeline and final_notes.md")
    p_val.add_argument(
        "--deep-pass",
        action="store_true",
        help="Also run strict deep-pass quality checks on final_notes.md.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.cmd == "run":
        return run_pipeline(args)
    if args.cmd == "status":
        return run_status(args)
    if args.cmd == "validate":
        return run_validate_only(args)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
