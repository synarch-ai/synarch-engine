#!/usr/bin/env python3
"""
Install skills from this repo into agent global or workspace skill folders.

Usage examples:
  python skills/install_skills.py --list
  python skills/install_skills.py --skill backend-pe --skill frontend-pe
  python skills/install_skills.py --all --targets claude,codex,gemini
  python skills/install_skills.py --skill backend-pe --targets antigravity --mode symlink --force
  python skills/install_skills.py --skill frontend-pe --workspace /path/to/project
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set


IGNORE_DIRS = {"legacy", "notes", "packaged", "__pycache__"}


def repo_skills(base_dir: Path) -> List[str]:
    skills: List[str] = []
    for entry in base_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name in IGNORE_DIRS or entry.name.startswith("."):
            continue
        if (entry / "SKILL.md").is_file():
            skills.append(entry.name)
    return sorted(skills)


def parse_selection(input_str: str, options: List[str]) -> List[str]:
    s = input_str.strip().lower()
    if s in {"all", "*"}:
        return options

    selected: Set[str] = set()
    parts = [p.strip() for p in s.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError:
                continue
            for idx in range(start, end + 1):
                if 1 <= idx <= len(options):
                    selected.add(options[idx - 1])
        else:
            try:
                idx = int(part)
            except ValueError:
                continue
            if 1 <= idx <= len(options):
                selected.add(options[idx - 1])
    return [s for s in options if s in selected]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_skill(src: Path, dest: Path, force: bool) -> str:
    if dest.exists():
        if not force:
            return "skipped (exists)"
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    return "copied"


def symlink_skill(src: Path, dest: Path, force: bool) -> str:
    if dest.exists() or dest.is_symlink():
        if not force:
            return "skipped (exists)"
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    dest.symlink_to(src, target_is_directory=True)
    return "linked"


def resolve_targets(targets_arg: str, workspace: str | None) -> Dict[str, Path]:
    home = Path.home()
    targets: Dict[str, Path] = {
        "claude": home / ".claude" / "skills",
        "codex": home / ".codex" / "skills",
        "gemini": home / ".gemini" / "skills",
        "cline": home / ".cline" / "skills",
        "kilocode": home / ".kilocode" / "skills",
        "copilot": home / ".copilot" / "skills",
        "antigravity": home / ".gemini" / "antigravity" / "global_skills",
    }

    if workspace:
        targets["workspace"] = Path(workspace) / ".agent" / "skills"

    if targets_arg.strip().lower() == "all":
        return targets

    wanted = {t.strip().lower() for t in targets_arg.split(",") if t.strip()}
    resolved = {k: v for k, v in targets.items() if k in wanted}
    if not resolved:
        raise SystemExit(f"No valid targets found for: {targets_arg}")
    return resolved


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    available = repo_skills(base_dir)
    if not available:
        print("No skills found in this directory.")
        return 1

    parser = argparse.ArgumentParser(description="Install skills to agent directories.")
    parser.add_argument("--list", action="store_true", help="List available skills and exit.")
    parser.add_argument("--skill", action="append", help="Skill name to install (can repeat).")
    parser.add_argument("--all", action="store_true", help="Install all skills.")
    parser.add_argument(
        "--targets",
        default="all",
        help="Comma-separated targets (claude,codex,gemini,cline,kilocode,copilot,antigravity,workspace) or 'all'.",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        help="Workspace path to install into <workspace>/.agent/skills (adds 'workspace' target).",
    )
    parser.add_argument(
        "--mode",
        choices=["copy", "symlink"],
        default="copy",
        help="Install mode: copy (default) or symlink.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing skill folders.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen.")

    args = parser.parse_args()

    if args.list:
        print("Available skills:")
        for s in available:
            print(f"- {s}")
        return 0

    if args.all and args.skill:
        print("Use either --all or --skill, not both.")
        return 1

    if args.all:
        selected = available
    elif args.skill:
        selected = []
        missing = []
        for s in args.skill:
            if s in available:
                selected.append(s)
            else:
                missing.append(s)
        if missing:
            print(f"Unknown skills: {', '.join(missing)}")
            return 1
    else:
        print("Select skills to install:")
        for i, s in enumerate(available, start=1):
            print(f"{i:>2}. {s}")
        choice = input("Enter numbers (e.g., 1,3-5) or 'all': ").strip()
        selected = parse_selection(choice, available)
        if not selected:
            print("No skills selected.")
            return 1

    targets = resolve_targets(args.targets, args.workspace)

    install_fn = copy_skill if args.mode == "copy" else symlink_skill

    print(f"Mode: {args.mode}")
    print(f"Skills: {', '.join(selected)}")
    print(f"Targets: {', '.join(targets.keys())}")

    for target_name, target_path in targets.items():
        if args.dry_run:
            print(f"[dry-run] {target_name} -> {target_path}")
            continue
        ensure_dir(target_path)
        for s in selected:
            src = base_dir / s
            dest = target_path / s
            result = install_fn(src, dest, args.force)
            print(f"{target_name}: {s} -> {dest} [{result}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
