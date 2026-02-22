#!/usr/bin/env python3
"""Merge chunked Stage-1 artifacts into a unified .pipeline set.

Deterministic local utility. No API usage.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")


def merge_ledgers(chunk_dirs: list[Path]) -> tuple[list[dict], list[dict]]:
    merged_ledger: list[dict] = []
    merged_manifest: list[dict] = []

    seen_ledger: dict[str, dict] = {}
    seen_manifest: dict[str, dict] = {}

    for chunk_dir in chunk_dirs:
        ledger_path = chunk_dir / "segment_ledger.jsonl"
        manifest_path = chunk_dir / "segment_manifest.jsonl"
        if not ledger_path.exists() or not manifest_path.exists():
            raise FileNotFoundError(f"Missing ledger/manifest in chunk dir: {chunk_dir}")

        for row in read_jsonl(ledger_path):
            seg_id = row.get("segment_id")
            if not isinstance(seg_id, str):
                raise ValueError(f"Invalid segment_id in {ledger_path}: {row}")

            prior = seen_ledger.get(seg_id)
            if prior is None:
                seen_ledger[seg_id] = row
                merged_ledger.append(row)
            else:
                if prior.get("raw_text") != row.get("raw_text") or prior.get("timestamp") != row.get("timestamp"):
                    raise ValueError(
                        f"Conflicting duplicate segment_id '{seg_id}' across chunks. "
                        "Re-run chunking preserving globally unique segment IDs."
                    )

        for row in read_jsonl(manifest_path):
            seg_id = row.get("segment_id")
            if not isinstance(seg_id, str):
                raise ValueError(f"Invalid segment_id in {manifest_path}: {row}")
            if seg_id not in seen_manifest:
                seen_manifest[seg_id] = row
                merged_manifest.append(row)

    return merged_ledger, merged_manifest


def merge_refined_transcripts(chunk_dirs: list[Path]) -> str:
    parts: list[str] = []
    for idx, chunk_dir in enumerate(chunk_dirs, start=1):
        path = chunk_dir / "refined_transcript.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        parts.append(f"<!-- chunk:{idx} path:{chunk_dir} -->\n{text}")
    return "\n\n---\n\n".join(parts).strip() + "\n" if parts else ""


def merge_topic_inventory(chunk_dirs: list[Path]) -> dict:
    merged: dict[str, list] = {
        "concepts": [],
        "technical_terms": [],
        "code_or_commands": [],
        "qa_items": [],
        "named_entities": [],
    }

    for chunk_dir in chunk_dirs:
        path = chunk_dir / "topic_inventory.json"
        if not path.exists():
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            continue
        for key in merged.keys():
            values = obj.get(key, [])
            if isinstance(values, list):
                merged[key].extend(values)

    for key, values in merged.items():
        seen = set()
        deduped = []
        for value in values:
            sig = json.dumps(value, sort_keys=True, ensure_ascii=True)
            if sig in seen:
                continue
            seen.add(sig)
            deduped.append(value)
        merged[key] = deduped

    return merged


def merge_csv(chunk_dirs: list[Path], file_name: str, key_fields: tuple[str, ...]) -> tuple[list[str], list[dict]]:
    header: list[str] = []
    rows: list[dict] = []
    seen_keys: set[tuple[str, ...]] = set()

    for chunk_dir in chunk_dirs:
        path = chunk_dir / file_name
        if not path.exists():
            continue

        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not header:
                header = reader.fieldnames or []
            for row in reader:
                key = tuple(str(row.get(field, "")) for field in key_fields)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                rows.append(row)

    return header, rows


def merge_uncertainty(chunk_dirs: list[Path]) -> list[dict]:
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for chunk_dir in chunk_dirs:
        path = chunk_dir / "uncertainty_report.json"
        if not path.exists():
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        items = obj if isinstance(obj, list) else obj.get("items", []) if isinstance(obj, dict) else []
        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue
            seg_id = str(item.get("segment_id", ""))
            original = str(item.get("original_text", ""))
            sig = (seg_id, original)
            if sig in seen:
                continue
            seen.add(sig)
            rows.append(item)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge chunked Stage-1 artifacts into unified .pipeline artifacts.")
    parser.add_argument("--chunk-dirs", nargs="+", required=True, help="Chunk .pipeline directories in temporal order")
    parser.add_argument("--output-dir", required=True, help="Target .pipeline directory for merged artifacts")
    args = parser.parse_args()

    chunk_dirs = [Path(p).expanduser().resolve() for p in args.chunk_dirs]
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    merged_ledger, merged_manifest = merge_ledgers(chunk_dirs)
    write_jsonl(output_dir / "segment_ledger.jsonl", merged_ledger)
    write_jsonl(output_dir / "segment_manifest.jsonl", merged_manifest)

    refined = merge_refined_transcripts(chunk_dirs)
    if refined:
        (output_dir / "refined_transcript.md").write_text(refined, encoding="utf-8")

    topic_inventory = merge_topic_inventory(chunk_dirs)
    (output_dir / "topic_inventory.json").write_text(
        json.dumps(topic_inventory, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )

    corrections_header, corrections_rows = merge_csv(
        chunk_dirs,
        "corrections_log.csv",
        ("segment_id", "raw_text", "corrected_text"),
    )
    if corrections_header:
        with (output_dir / "corrections_log.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=corrections_header)
            writer.writeheader()
            for row in corrections_rows:
                writer.writerow(row)

    uncertainty_rows = merge_uncertainty(chunk_dirs)
    if uncertainty_rows:
        (output_dir / "uncertainty_report.json").write_text(
            json.dumps(uncertainty_rows, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"chunks: {len(chunk_dirs)}")
    print(f"merged_segments: {len(merged_ledger)}")
    print(f"wrote: {output_dir / 'segment_ledger.jsonl'}")
    print(f"wrote: {output_dir / 'segment_manifest.jsonl'}")
    if refined:
        print(f"wrote: {output_dir / 'refined_transcript.md'}")
    print(f"wrote: {output_dir / 'topic_inventory.json'}")
    if corrections_header:
        print(f"wrote: {output_dir / 'corrections_log.csv'}")
    if uncertainty_rows:
        print(f"wrote: {output_dir / 'uncertainty_report.json'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
