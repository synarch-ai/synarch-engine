#!/usr/bin/env bash
#
# Synarch Engine — Pro developer skills installer (idempotent).
#
# Clones upstream skill/plugin sources, symlinks into .agents/skills/,
# and runs host-specific setup (gstack browse binary + Cursor skills).
#
# Layered pipeline: discover → interrogate/spec → plan → implement → review →
# security → browser QA → ship → learn
#
# Sources (see docs/04-reference-deep-dives/agent-skills-ecosystem.md):
#   Tier 0:  vercel-labs/skills (find-skills)
#   Core:    shadcn/improve, garrytan/gstack, mattpocock/skills, pstack, superpowers
#   Tier S+: trailofbits/skills, vercel-labs/agent-browser
#   Tier S:  vercel-labs/agent-skills, anthropics/skills (dev subset)
#   Tier A+: github/awesome-copilot (curated subset)
#   Stack:   supabase/agent-skills
#   CE:      EveryInc/compound-engineering-plugin
#   PraxStack 2026 (curated):
#     Discovery: last30days, deep-research
#     UI:        hallmark, impeccable
#     NVIDIA:    rag-blueprint, cudaq-guide, nemo-retriever (nvidia- prefix)
#     wshobson:  5 specialist skills (wsh- prefix; full repo documented-only)
#     Personas:  praxstack/skills-and-personas (new-skills portfolio + extras)
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

warn() {
  if [ "$QUIET" -eq 0 ]; then
    printf '\033[1;33m[pro-skills]\033[0m %s\n' "$*" >&2
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

# Link all SKILL.md dirs under root with prefix; skip tests/fixtures.
link_skills_recursive() {
  local root="$1"
  local prefix="$2"
  local count=0

  while IFS= read -r skill_md; do
    local skill_dir base dest
    skill_dir="$(dirname "$skill_md")"
    base="$(basename "$skill_dir")"
    dest="${prefix}${base}"
    link_skill "$skill_dir" "$dest"
    count=$((count + 1))
  done < <(
    find "$root" -name 'SKILL.md' \
      ! -path '*/tests/*' \
      ! -path '*/test/*' \
      ! -path '*/fixtures/*' \
      2>/dev/null | sort
  )
  echo "$count"
}

link_skills_flat() {
  local root="$1"
  local prefix="$2"
  local replace="${3:-0}"
  local count=0

  for skill_dir in "${root}"/*/; do
    [ -d "$skill_dir" ] || continue
    local base dest
    base="$(basename "$skill_dir")"
    dest="${prefix}${base}"
    link_skill "$skill_dir" "$dest"
    count=$((count + 1))
  done
  echo "$count"
}

# Map upstream folder names to canonical skill names used in docs/rules.
link_vercel_agent_skills() {
  local root="${VENDOR_DIR}/vercel-agent-skills/skills"
  local count=0
  declare -A ALIASES=(
    [react-best-practices]=vercel-react-best-practices
    [composition-patterns]=vercel-composition-patterns
    [deploy-to-vercel]=vercel-deploy-to-vercel
  )

  for skill_dir in "${root}"/*/; do
    [ -d "$skill_dir" ] || continue
    local base dest
    base="$(basename "$skill_dir")"
    if [ -n "${ALIASES[$base]:-}" ]; then
      dest="${ALIASES[$base]}"
    elif [[ "$base" == vercel-* ]]; then
      dest="$base"
    else
      dest="vercel-${base}"
    fi
    link_skill "$skill_dir" "$dest"
    count=$((count + 1))
  done
  echo "$count"
}

link_supabase_agent_skills() {
  local root="${VENDOR_DIR}/supabase-agent-skills/skills"
  local count=0

  for skill_dir in "${root}"/*/; do
    [ -d "$skill_dir" ] || continue
    local base dest
    base="$(basename "$skill_dir")"
    if [[ "$base" == supabase-* ]]; then
      dest="$base"
    else
      dest="supabase-${base}"
    fi
    link_skill "$skill_dir" "$dest"
    count=$((count + 1))
  done
  echo "$count"
}

link_named_skills() {
  local root="$1"
  local prefix="$2"
  shift 2
  local count=0

  for name in "$@"; do
    local skill_dir dest
    skill_dir="${root}/${name}"
    dest="${prefix}${name}"
    if [ ! -d "$skill_dir" ]; then
      warn "  skip (missing): ${name}"
      continue
    fi
    link_skill "$skill_dir" "$dest"
    count=$((count + 1))
  done
  echo "$count"
}

# Link into .agents/skills and ~/.cursor/skills for global discovery/research skills.
link_global_skill() {
  local src="$1"
  local dest_name="$2"
  local cursor_skills="${HOME}/.cursor/skills"
  local dest

  link_skill "$src" "$dest_name"

  [ -d "$cursor_skills" ] || mkdir -p "$cursor_skills"
  dest="${cursor_skills}/${dest_name}"
  if [ -L "$dest" ] || [ -d "$dest" ]; then
    rm -rf "$dest"
  fi
  ln -sfn "$src" "$dest"
}

link_skill_path() {
  local skill_dir="$1"
  local dest_name="$2"
  if [ ! -f "${skill_dir}/SKILL.md" ]; then
    warn "  skip (no SKILL.md): ${dest_name}"
    return 0
  fi
  link_skill "$skill_dir" "$dest_name"
}

# gstack's Cursor host links gstack-* names; SKILL.md uses short names (/plan-ceo-review).
# Add alias symlinks in a skills directory so slash-command discovery matches gstack docs.
link_gstack_short_aliases() {
  local skills_root="$1"
  local label="${2:-gstack}"
  local count=0

  [ -d "$skills_root" ] || return 0

  for prefixed in "$skills_root"/gstack-*/; do
    [ -d "$prefixed" ] || continue
    local base short dest
    base="$(basename "$prefixed")"
    [ "$base" = "gstack" ] && continue
    short="${base#gstack-}"
    [ "$short" = "$base" ] && continue
    dest="${skills_root}/${short}"
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
      continue
    fi
    ln -sfn "$prefixed" "$dest"
    count=$((count + 1))
  done

  if [ "$count" -gt 0 ] && [ "$QUIET" -eq 0 ]; then
    log "  gstack ${label} aliases: ${count} short-name symlinks"
  fi
}

link_gstack_cursor_aliases() {
  link_gstack_short_aliases "${HOME}/.cursor/skills" "cursor"
}

link_gstack_agents_aliases() {
  link_gstack_short_aliases "$SKILLS_DIR" "agents"
}

# praxstack/skills-and-personas: short names when free; prax-<name> on collision.
link_praxstack_skill() {
  local skill_dir="$1"
  local name="$2"
  local dest="$name"

  if skill_exists "$name"; then
    dest="prax-${name}"
  fi
  link_skill "$skill_dir" "$dest"
}

install_agent_browser_cli() {
  if command -v agent-browser >/dev/null 2>&1; then
    log "agent-browser CLI already installed"
  else
    log "Installing agent-browser CLI globally..."
    if ! npm install -g agent-browser 2>/dev/null; then
      warn "Global npm install failed; will use npx fallback"
    fi
  fi

  if command -v agent-browser >/dev/null 2>&1; then
    log "Running agent-browser install..."
    agent-browser install 2>/dev/null || warn "agent-browser install step failed (non-fatal)"
  else
    log "Trying npx agent-browser install..."
    npx --yes agent-browser install 2>/dev/null || warn "agent-browser CLI unavailable (browser QA skill still linked)"
  fi
}

# --- Clone all upstream sources -----------------------------------------------
log "Cloning/updating skill sources..."
clone_or_update "https://github.com/vercel-labs/skills.git" "${VENDOR_DIR}/vercel-labs-skills"
clone_or_update "https://github.com/shadcn/improve.git" "${VENDOR_DIR}/shadcn-improve"
clone_or_update "https://github.com/garrytan/gstack.git" "${VENDOR_DIR}/garrytan-gstack"
clone_or_update "https://github.com/mattpocock/skills.git" "${VENDOR_DIR}/mattpocock-skills"
clone_or_update "https://github.com/obra/superpowers.git" "${VENDOR_DIR}/obra-superpowers"
clone_or_update "https://github.com/trailofbits/skills.git" "${VENDOR_DIR}/trailofbits-skills"
clone_or_update "https://github.com/vercel-labs/agent-browser.git" "${VENDOR_DIR}/vercel-agent-browser"
clone_or_update "https://github.com/vercel-labs/agent-skills.git" "${VENDOR_DIR}/vercel-agent-skills"
clone_or_update "https://github.com/anthropics/skills.git" "${VENDOR_DIR}/anthropics-skills"
clone_or_update "https://github.com/github/awesome-copilot.git" "${VENDOR_DIR}/awesome-copilot"
clone_or_update "https://github.com/supabase/agent-skills.git" "${VENDOR_DIR}/supabase-agent-skills"
clone_or_update "https://github.com/EveryInc/compound-engineering-plugin.git" "${VENDOR_DIR}/compound-engineering"
clone_or_update "https://github.com/mvanhorn/last30days-skill.git" "${VENDOR_DIR}/last30days-skill"
clone_or_update "https://github.com/24601/agent-deep-research.git" "${VENDOR_DIR}/agent-deep-research"
clone_or_update "https://github.com/nutlope/hallmark.git" "${VENDOR_DIR}/hallmark"
clone_or_update "https://github.com/pbakaus/impeccable.git" "${VENDOR_DIR}/impeccable"
clone_or_update "https://github.com/nvidia/skills.git" "${VENDOR_DIR}/nvidia-skills"
clone_or_update "https://github.com/wshobson/agents.git" "${VENDOR_DIR}/wshobson-agents"
clone_or_update "https://github.com/praxstack/skills-and-personas.git" "${VENDOR_DIR}/praxstack-skills-and-personas"

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

# --- Tier 0: Discovery (install FIRST) ----------------------------------------
log "Tier 0: find-skills (discovery)..."
link_named_skills "${VENDOR_DIR}/vercel-labs-skills/skills" "" find-skills >/dev/null

# --- Core: shadcn/improve -----------------------------------------------------
log "Core: shadcn/improve..."
link_skill "${VENDOR_DIR}/shadcn-improve/skills/improve" "improve"

# --- Core: obra/superpowers (skip name collisions) ---------------------------
log "Core: obra/superpowers..."
for skill_dir in "${VENDOR_DIR}/obra-superpowers/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  base="$(basename "$skill_dir")"
  if skill_exists "$base"; then
    link_skill "$skill_dir" "superpowers-${base}"
  else
    link_skill "$skill_dir" "$base"
  fi
done

# --- Core: cursor/plugins pstack (namespaced) --------------------------------
log "Core: cursor/plugins pstack..."
for skill_dir in "${PSTACK_DIR}/pstack/skills"/*/; do
  [ -d "$skill_dir" ] || continue
  base="$(basename "$skill_dir")"
  dest="pstack-${base}"
  link_skill "$skill_dir" "$dest"
done

# --- Core: mattpocock/skills -------------------------------------------------
log "Core: mattpocock/skills..."
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

# --- Core: garrytan/gstack (requires bun) ------------------------------------
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

log "Core: gstack setup (cursor, short slash-command names)..."
GSTACK_QUIET=()
[ "$QUIET" -eq 1 ] && GSTACK_QUIET=(--quiet)
(
  cd "${VENDOR_DIR}/garrytan-gstack"
  ./setup --host cursor --no-prefix "${GSTACK_QUIET[@]}"
)
link_gstack_cursor_aliases

# Link into .agents/skills/ with gstack's default short names (/plan-ceo-review).
# Fall back to gstack-* when another pack already owns the name.
if [ -d "${VENDOR_DIR}/garrytan-gstack/.agents/skills" ]; then
  for skill_dir in "${VENDOR_DIR}/garrytan-gstack/.agents/skills"/*/; do
    [ -d "$skill_dir" ] || continue
    base="$(basename "$skill_dir")"
    short="${base#gstack-}"
    if [ "$short" = "$base" ]; then
      short="$base"
    fi
    if skill_exists "$short"; then
      link_skill "$skill_dir" "gstack-${short}"
    else
      link_skill "$skill_dir" "$short"
    fi
  done
fi
link_gstack_agents_aliases

# --- Tier S+: Security (Trail of Bits) --------------------------------------
log "Tier S+: trailofbits/skills (tob- prefix, on-demand)..."
link_skills_recursive "${VENDOR_DIR}/trailofbits-skills/plugins" "tob-" >/dev/null

# --- Tier S+: Browser QA ------------------------------------------------------
log "Tier S+: agent-browser CLI + skill..."
install_agent_browser_cli
link_skill "${VENDOR_DIR}/vercel-agent-browser/skills/agent-browser" "agent-browser"

# --- Tier S: Vercel agent-skills ----------------------------------------------
log "Tier S: vercel-labs/agent-skills (canonical vercel-* names)..."
# Remove legacy double-prefix symlinks from older installer runs
rm -rf "${SKILLS_DIR}/vercel-vercel-optimize" \
  "${SKILLS_DIR}/vercel-vercel-cli-with-tokens" \
  "${SKILLS_DIR}/supabase-supabase-postgres-best-practices" \
  "${SKILLS_DIR}/vercel-deploy" 2>/dev/null || true
link_vercel_agent_skills >/dev/null

# --- Tier S: Anthropic reference (dev subset) ---------------------------------
log "Tier S: anthropics/skills (dev subset, anthropic- prefix)..."
ANTHROPIC_DEV_SKILLS=(
  mcp-builder
  frontend-design
  webapp-testing
  web-artifacts-builder
  skill-creator
  claude-api
  doc-coauthoring
  internal-comms
  docx
  pdf
  pptx
  xlsx
  theme-factory
)
link_named_skills "${VENDOR_DIR}/anthropics-skills/skills" "anthropic-" "${ANTHROPIC_DEV_SKILLS[@]}" >/dev/null

# --- Tier A+: awesome-copilot (curated engineering subset) --------------------
log "Tier A+: github/awesome-copilot (gh-copilot- prefix, curated)..."
GH_COPILOT_SKILLS=(
  acquire-codebase-knowledge
  breakdown-feature-implementation
  breakdown-feature-prd
  breakdown-plan
  breakdown-test
  create-implementation-plan
  structured-autonomy-implement
  playwright-explore-website
  bug-reproduction-brief
  create-github-action-workflow-specification
  create-github-issue-feature-from-specification
  codebase-memory-mcp
  finalize-agent-prompt
  copilot-pr-autopilot
)
for name in "${GH_COPILOT_SKILLS[@]}"; do
  skill_dir="${VENDOR_DIR}/awesome-copilot/skills/${name}"
  if [ ! -d "$skill_dir" ]; then
    skill_dir="${VENDOR_DIR}/awesome-copilot/.github/skills/${name}"
  fi
  dest="gh-copilot-${name}"
  if [ -d "$skill_dir" ]; then
    link_skill "$skill_dir" "$dest"
  fi
done
if [ -d "${VENDOR_DIR}/awesome-copilot/.github/skills/agentic-workflows" ]; then
  link_skill "${VENDOR_DIR}/awesome-copilot/.github/skills/agentic-workflows" "gh-copilot-agentic-workflows"
fi

# --- Stack: Supabase ----------------------------------------------------------
log "Stack: supabase/agent-skills (canonical supabase-* names)..."
link_supabase_agent_skills >/dev/null

# --- PraxStack 2026: Discovery / Research ------------------------------------
log "PraxStack: discovery/research (global .agents + ~/.cursor/skills)..."
rm -f "${SKILLS_DIR}/deep-research" "${SKILLS_DIR}/research-deep-research" \
  "${HOME}/.cursor/skills/deep-research" \
  "${HOME}/.cursor/skills/research-deep-research" 2>/dev/null || true
for stale in "${SKILLS_DIR}"/wshobson-* "${SKILLS_DIR}"/wsh-*; do
  [ -e "$stale" ] || continue
  rm -rf "$stale"
done
link_global_skill \
  "${VENDOR_DIR}/last30days-skill/skills/last30days" \
  "last30days"
link_global_skill \
  "${VENDOR_DIR}/agent-deep-research" \
  "research-deep-research"

# --- PraxStack 2026: UI -------------------------------------------------------
log "PraxStack: UI (hallmark, impeccable)..."
link_skill_path "${VENDOR_DIR}/hallmark/skills/hallmark" "hallmark"
IMPECCABLE_SKILL="${VENDOR_DIR}/impeccable/.agents/skills/impeccable"
if [ ! -d "$IMPECCABLE_SKILL" ]; then
  IMPECCABLE_SKILL="${VENDOR_DIR}/impeccable/plugin/skills/impeccable"
fi
if [ ! -d "$IMPECCABLE_SKILL" ]; then
  IMPECCABLE_SKILL="${VENDOR_DIR}/impeccable/.cursor/skills/impeccable"
fi
if [ -d "$IMPECCABLE_SKILL" ]; then
  link_skill "$IMPECCABLE_SKILL" "impeccable"
else
  warn "  impeccable skill dir missing; see ecosystem doc for npx fallback"
fi
if command -v npx >/dev/null 2>&1; then
  log "  optional: npx impeccable skills install --providers=cursor --no-hooks (for hooks)"
fi

# --- PraxStack 2026: NVIDIA (curated dev subset) ------------------------------
log "PraxStack: nvidia/skills (nvidia- prefix, curated subset)..."
for stale in "${SKILLS_DIR}"/nvidia-*; do
  [ -e "$stale" ] || continue
  rm -rf "$stale"
done
NVIDIA_SKILLS=(
  cudaq-guide
  rag-blueprint
  rag-eval
  rag-perf
  nemo-retriever
  nvidia-skill-finder
  aiq-research
)
for name in "${NVIDIA_SKILLS[@]}"; do
  skill_dir="${VENDOR_DIR}/nvidia-skills/skills/${name}"
  link_skill_path "$skill_dir" "nvidia-${name}"
done

# --- PraxStack 2026: wshobson/agents (3 specialist skills only) ---------------
log "PraxStack: wshobson/agents (3 specialist skills, wshobson- prefix)..."
WSHOBSON_SKILLS=(
  "plugins/backend-development/skills/api-design-principles"
  "plugins/backend-development/skills/architecture-patterns"
  "plugins/developer-essentials/skills/debugging-strategies"
)
for rel in "${WSHOBSON_SKILLS[@]}"; do
  skill_dir="${VENDOR_DIR}/wshobson-agents/${rel}"
  base="$(basename "$rel")"
  link_skill_path "$skill_dir" "wshobson-${base}"
done

# --- PraxStack: skills-and-personas (canonical new-skills portfolio) ----------
log "PraxStack: praxstack/skills-and-personas (new-skills portfolio)..."
PRAXSTACK_DIR="${VENDOR_DIR}/praxstack-skills-and-personas"
PRAX_NEW_SKILLS="${PRAXSTACK_DIR}/new-skills"
if [ -d "$PRAX_NEW_SKILLS" ]; then
  for skill_dir in "${PRAX_NEW_SKILLS}"/*/; do
    [ -d "$skill_dir" ] || continue
    base="$(basename "$skill_dir")"
    [ "$base" = "_audit" ] && continue
    [[ "$base" == .* ]] && continue
    link_praxstack_skill "$skill_dir" "$base"
  done
else
  warn "  praxstack new-skills/ missing; skip portfolio"
fi

# Public skills in skills/ not duplicated in new-skills/
PRAX_EXTRA_SKILLS=(
  teach-pro-max
  superimprove
  coding-agent-leadership-principles
  cross-agent-handoff
)
for name in "${PRAX_EXTRA_SKILLS[@]}"; do
  skill_dir="${PRAXSTACK_DIR}/skills/${name}"
  if [ -d "$skill_dir" ]; then
    link_praxstack_skill "$skill_dir" "$name"
  else
    warn "  skip (missing): praxstack skills/${name}"
  fi
done

# teach-pro-max is skills.sh-discoverable; mirror short name to ~/.cursor/skills
if [ -d "${PRAXSTACK_DIR}/skills/teach-pro-max" ] && [ -L "${SKILLS_DIR}/teach-pro-max" ]; then
  cursor_skills="${HOME}/.cursor/skills"
  [ -d "$cursor_skills" ] || mkdir -p "$cursor_skills"
  ln -sfn "${PRAXSTACK_DIR}/skills/teach-pro-max" "${cursor_skills}/teach-pro-max"
fi

# --- Compound Engineering -----------------------------------------------------
log "Compound: EveryInc/compound-engineering-plugin (ce- prefix)..."
for skills_root in "${VENDOR_DIR}/compound-engineering/skills" "${VENDOR_DIR}/compound-engineering/.agents/skills"; do
  [ -d "$skills_root" ] || continue
  for skill_dir in "${skills_root}"/*/; do
    [ -d "$skill_dir" ] || continue
    base="$(basename "$skill_dir")"
    if [[ "$base" == ce-* ]]; then
      dest="$base"
    else
      dest="ce-${base}"
    fi
    link_skill "$skill_dir" "$dest"
  done
done

# --- Write manifest -----------------------------------------------------------
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
    "vercel-labs-skills": vendor / "vercel-labs-skills",
    "shadcn-improve": vendor / "shadcn-improve",
    "garrytan-gstack": vendor / "garrytan-gstack",
    "mattpocock-skills": vendor / "mattpocock-skills",
    "obra-superpowers": vendor / "obra-superpowers",
    "cursor-plugins-pstack": vendor / "cursor-plugins",
    "trailofbits-skills": vendor / "trailofbits-skills",
    "vercel-agent-browser": vendor / "vercel-agent-browser",
    "vercel-agent-skills": vendor / "vercel-agent-skills",
    "anthropics-skills": vendor / "anthropics-skills",
    "awesome-copilot": vendor / "awesome-copilot",
    "supabase-agent-skills": vendor / "supabase-agent-skills",
    "compound-engineering": vendor / "compound-engineering",
    "last30days-skill": vendor / "last30days-skill",
    "agent-deep-research": vendor / "agent-deep-research",
    "hallmark": vendor / "hallmark",
    "impeccable": vendor / "impeccable",
    "nvidia-skills": vendor / "nvidia-skills",
    "wshobson-agents": vendor / "wshobson-agents",
    "praxstack-skills-and-personas": vendor / "praxstack-skills-and-personas",
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
vendor_prefix = str(vendor)

def is_pro_skill(p: Path) -> bool:
    if not p.is_symlink():
        return False
    try:
        resolved = str(p.resolve())
    except OSError:
        return False
    return resolved.startswith(vendor_prefix)

linked = sorted(p.name for p in skills_dir.iterdir() if is_pro_skill(p))

def count_vendor_prefix(repo_key: str, prefix: str = "") -> int:
    repo_path = str(repos[repo_key].resolve())
    n = 0
    for name in linked:
        target = skills_dir / name
        try:
            resolved = str(target.resolve())
        except OSError:
            continue
        if not resolved.startswith(repo_path):
            continue
        if prefix and not name.startswith(prefix):
            continue
        n += 1
    return n

tier_counts = {
    "tier0": sum(1 for n in linked if n == "find-skills"),
    "tier_s_plus_security": count_vendor_prefix("trailofbits-skills", "tob-"),
    "tier_s_plus_browser": sum(1 for n in linked if n == "agent-browser"),
    "tier_s_web": count_vendor_prefix("vercel-agent-skills", "vercel-"),
    "tier_s_reference": count_vendor_prefix("anthropics-skills", "anthropic-"),
    "tier_a_toolbox": sum(1 for n in linked if n.startswith("gh-copilot-")),
    "stack_supabase": count_vendor_prefix("supabase-agent-skills", "supabase-"),
    "compound_engineering": count_vendor_prefix("compound-engineering"),
    "praxstack_discovery": sum(
        1 for n in linked if n in ("last30days", "research-deep-research")
    ),
    "praxstack_ui": sum(
        1 for n in linked if n in ("hallmark", "impeccable")
    ),
    "praxstack_nvidia": count_vendor_prefix("nvidia-skills", "nvidia-"),
    "praxstack_wshobson": sum(1 for n in linked if n.startswith("wshobson-")),
    "praxstack_personas": sum(
        1 for n in linked
        if str((skills_dir / n).resolve()).startswith(
            str(repos["praxstack-skills-and-personas"].resolve())
        )
    ),
    "core": sum(
        1 for n in linked
        if any(
            str((skills_dir / n).resolve()).startswith(str(repos[k].resolve()))
            for k in (
                "shadcn-improve",
                "garrytan-gstack",
                "mattpocock-skills",
                "obra-superpowers",
                "cursor-plugins-pstack",
            )
        )
    ),
}

data = {
    "installed_at": datetime.now(timezone.utc).isoformat(),
    "pipeline": "discover → interrogate/spec → plan → implement → review → security → browser QA → ship → learn",
    "tier_counts": tier_counts,
    "repos": {
        name: {"path": str(path.relative_to(repo_root)), "sha": git_sha(path)}
        for name, path in repos.items()
    },
    "linked_skill_count": len(linked),
    "linked_skills_sample": linked[:40],
    "cursor_plugins_recommended": [
        {"name": "pstack", "install": "/add-plugin pstack"},
        {"name": "superpowers", "install": "/add-plugin superpowers"},
        {"name": "compound-engineering", "install": "/add-plugin compound-engineering"},
    ],
    "documented_only": [
        {"name": "microsoft/skills", "install": "npx skills add microsoft/skills --skill <name>", "note": "Context rot if installed wholesale"},
        {"name": "aws/agent-toolkit-for-aws", "note": "Install when AWS agent tooling is needed"},
        {"name": "cloudflare/skills", "note": "Edge/workers-specific; see ecosystem doc"},
        {"name": "github/spec-kit", "note": "Do not run specify init in-repo; see OpenSpec section"},
        {"name": "wshobson/agents (full)", "note": "94 plugins; only 5 wsh-* specialists installed"},
        {"name": "remotion-dev/skills", "note": "Video in React; install on demand"},
        {"name": "entireio/entire", "note": "Agent memory layer; evaluate separately"},
        {"name": "beads", "note": "Task beads for agents; optional"},
        {"name": "affaan-m/everything-claude-code", "note": "Claude Code config dump; not for Synarch"},
        {"name": "openai/plugins", "note": "OpenAI plugin format; not deprecated openai/skills"},
    ],
    "repo_specific_tools": [
        {"name": "OpenSpec", "install": "npm install -g @fission-ai/openspec", "init": "openspec init (greenfield only; do not run in synarch-engine)"},
        {"name": "Graphify", "install": "uv tool install graphifyy", "init": "graphify install --project (see ecosystem doc for MCP)"},
        {"name": "Serena", "note": "MCP semantic code retrieval; see ecosystem doc"},
        {"name": "Context7", "note": "Up-to-date library docs MCP; see ecosystem doc"},
    ],
}

manifest_path.parent.mkdir(parents=True, exist_ok=True)
manifest_path.write_text(json.dumps(data, indent=2) + "\n")
print(f"manifest: {manifest_path} ({len(linked)} pro skills linked)")
for tier, count in sorted(tier_counts.items()):
    print(f"  {tier}: {count}")
PY

log "Pro skills install complete."
log "Optional Cursor marketplace plugins: /add-plugin pstack, /add-plugin superpowers, /add-plugin compound-engineering"
log "Run once per repo: /pstack-setup-pstack, /mp-setup-matt-pocock-skills (via mp-setup-matt-pocock-skills)"
log "Discovery: use find-skills or npx skills find <query> before adding more skills"
