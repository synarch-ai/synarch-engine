#!/usr/bin/env bash
#
# Synarch Engine — Pro developer skills installer (idempotent).
#
# Clones upstream skill/plugin sources, symlinks into .agents/skills/,
# and runs host-specific setup (gstack browse binary + Cursor skills).
#
# Sources:
#   - shadcn/improve          (codebase audit → plans/)
#   - garrytan/gstack         (review, QA, browser automation)
#   - mattpocock/skills       (engineering + productivity workflows)
#   - cursor/plugins pstack   (poteto-mode rigorous engineering)
#   - obra/superpowers        (TDD, planning, subagent development)
#
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

VENDOR_DIR="${REPO_ROOT}/vendor/skills-sources"
SKILLS_DIR="${REPO_ROOT}/.agents/skills"
MANIFEST="${REPO_ROOT}/vendor/skills-sources/manifest.json"
QUIET=0

log() {
  if [ "$QUIET" -eq 0 ]; then
    printf '\033[1;36m[pro-skills]\033[0m %s\n' "$*"
  fi
}

usage() {
  cat <<'EOF'
Usage: bash scripts/cloud-agent/install-pro-skills.sh [options]

Options:
  -q, --quiet   Suppress progress output
  -h, --help    Show this help

Installs pro developer skills into .agents/skills/ and ~/.cursor/skills (gstack).
Safe to run repeatedly.
EOF
}

for arg in "$@"; do
  case "$arg" in
    -q|--quiet) QUIET=1 ;;
    -h|--help) usage; exit 0 ;;
  esac
done

mkdir -p "$VENDOR_DIR" "$SKILLS_DIR"

clone_or_update() {
  local url="$1"
  local dir="$2"
  local branch="${3:-main}"

  if [ -d "$dir/.git" ]; then
    log "Updating $(basename "$dir")..."
    git -C "$dir" fetch --depth 1 origin "$branch" 2>/dev/null || git -C "$dir" fetch origin "$branch"
    git -C "$dir" checkout -q "$branch" 2>/dev/null || true
    git -C "$dir" pull --ff-only origin "$branch" 2>/dev/null || git -C "$dir" reset --hard "origin/$branch"
  else
    log "Cloning $(basename "$dir")..."
    git clone --depth 1 --branch "$branch" "$url" "$dir"
  fi
}

link_skill() {
  local src="$1"
  local dest_name="$2"
  local dest="${SKILLS_DIR}/${dest_name}"

  if [ ! -f "${src}/SKILL.md" ]; then
    log "  skip (no SKILL.md): ${dest_name}"
    return 0
  fi

  if [ -L "$dest" ] || [ -d "$dest" ]; then
    rm -rf "$dest"
  fi
  ln -sfn "$src" "$dest"
}

skill_exists() {
  local name="$1"
  [ -e "${SKILLS_DIR}/${name}" ]
}

# --- 1. Clone upstream sources -----------------------------------------------
clone_or_update "https://github.com/shadcn/improve.git" "${VENDOR_DIR}/shadcn-improve"
clone_or_update "https://github.com/garrytan/gstack.git" "${VENDOR_DIR}/garrytan-gstack"
clone_or_update "https://github.com/mattpocock/skills.git" "${VENDOR_DIR}/mattpocock-skills"
clone_or_update "https://github.com/obra/superpowers.git" "${VENDOR_DIR}/obra-superpowers"

# pstack: sparse checkout from cursor/plugins monorepo
PSTACK_DIR="${VENDOR_DIR}/cursor-plugins"
if [ ! -d "${PSTACK_DIR}/.git" ]; then
  log "Cloning cursor/plugins (sparse: pstack)..."
  git clone --depth 1 --filter=blob:none --sparse https://github.com/cursor/plugins.git "$PSTACK_DIR"
  git -C "$PSTACK_DIR" sparse-checkout set pstack
else
  log "Updating cursor/plugins (pstack)..."
  git -C "$PSTACK_DIR" pull --ff-only origin main 2>/dev/null || true
fi

# --- 2. shadcn/improve -------------------------------------------------------
log "Linking shadcn/improve..."
link_skill "${VENDOR_DIR}/shadcn-improve/skills/improve" "improve"

# --- 3. obra/superpowers (skip name collisions) ------------------------------
log "Linking obra/superpowers..."
for skill_dir in "${VENDOR_DIR}/obra-superpowers/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  base="$(basename "$skill_dir")"
  if skill_exists "$base"; then
    link_skill "$skill_dir" "superpowers-${base}"
  else
    link_skill "$skill_dir" "$base"
  fi
done

# --- 4. cursor/plugins pstack (namespaced) -----------------------------------
log "Linking cursor/plugins pstack..."
for skill_dir in "${PSTACK_DIR}/pstack/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  base="$(basename "$skill_dir")"
  dest="pstack-${base}"
  link_skill "$skill_dir" "$dest"
done

# --- 5. mattpocock/skills (engineering + productivity + misc) ---------------
log "Linking mattpocock/skills..."
for category in engineering productivity misc; do
  cat_dir="${VENDOR_DIR}/mattpocock-skills/skills/${category}"
  [ -d "$cat_dir" ] || continue
  for skill_dir in "${cat_dir}"/*/; do
    [ -d "$skill_dir" ] || continue
    base="$(basename "$skill_dir")"
    dest="mp-${base}"
    if skill_exists "$dest" || skill_exists "$base"; then
      dest="mp-${category}-${base}"
    fi
    link_skill "$skill_dir" "$dest"
  done
done

# --- 6. garrytan/gstack (requires bun) ---------------------------------------
ensure_bun() {
  if command -v bun >/dev/null 2>&1; then
    return 0
  fi
  log "Installing bun (required by gstack)..."
  curl -fsSL https://bun.sh/install | bash
  export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
  export PATH="$BUN_INSTALL/bin:$PATH"
}

ensure_bun
export PATH="${BUN_INSTALL:-$HOME/.bun}/bin:$PATH"

log "Running gstack setup (cursor, prefixed)..."
GSTACK_QUIET=()
[ "$QUIET" -eq 1 ] && GSTACK_QUIET=(--quiet)
(
  cd "${VENDOR_DIR}/garrytan-gstack"
  ./setup --host cursor --prefix "${GSTACK_QUIET[@]}"
)

# Also expose gstack skills in project .agents/skills for cloud agents
if [ -d "${VENDOR_DIR}/garrytan-gstack/.agents/skills" ]; then
  mkdir -p "${SKILLS_DIR}/gstack"
  for skill_dir in "${VENDOR_DIR}/garrytan-gstack/.agents/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    base="$(basename "$skill_dir")"
    link_skill "$skill_dir" "gstack-${base#gstack-}"
  done
fi

# --- 7. Write manifest -------------------------------------------------------
log "Writing manifest..."
python3 - "$REPO_ROOT" <<'PY'
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(sys.argv[1])
vendor = repo_root / "vendor" / "skills-sources"
manifest_path = vendor / "manifest.json"

repos = {
    "shadcn-improve": vendor / "shadcn-improve",
    "garrytan-gstack": vendor / "garrytan-gstack",
    "mattpocock-skills": vendor / "mattpocock-skills",
    "obra-superpowers": vendor / "obra-superpowers",
    "cursor-plugins-pstack": vendor / "cursor-plugins",
}

def git_sha(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        return subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return None

skills_dir = repo_root / ".agents" / "skills"
linked = sorted(
    p.name for p in skills_dir.iterdir()
    if p.is_symlink() and any(
        str(p.resolve()).startswith(str(vendor / name))
        for name in repos
    )
)

data = {
    "installed_at": datetime.now(timezone.utc).isoformat(),
    "repos": {name: {"path": str(path.relative_to(repo_root)), "sha": git_sha(path)} for name, path in repos.items()},
    "linked_skill_count": len(linked),
    "linked_skills_sample": linked[:30],
    "cursor_plugins_recommended": [
        {"name": "pstack", "install": "/add-plugin pstack"},
        {"name": "superpowers", "install": "/add-plugin superpowers"},
    ],
}

manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(data, indent=2) + "\n")
print(f"manifest: {manifest_path} ({len(linked)} pro skills linked)")
PY

log "Pro skills install complete."
log "Optional Cursor marketplace plugins: /add-plugin pstack, /add-plugin superpowers"
log "Run once per repo: /setup-pstack, /setup-matt-pocock-skills (via mp-setup-matt-pocock-skills)"
