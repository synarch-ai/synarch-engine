#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Apply a label to open issues in bulk (useful before Ralph execution).

Usage:
  scripts/ralph/label_open_issues.sh --repo owner/repo [options]

Options:
  --repo <owner/repo>       GitHub repository (required)
  --label <name>            Label to apply (default: ralph-ready)
  --exclude <num[,num...]>  Comma-separated issue numbers to skip (default: 1)
  --dry-run                 Print target issues without labeling
  -h, --help                Show this help
EOF
}

REPO=""
LABEL="ralph-ready"
EXCLUDE_CSV="1"
DRY_RUN="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --exclude) EXCLUDE_CSV="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN="1"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "Error: --repo is required." >&2
  usage
  exit 2
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh CLI is required." >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq is required." >&2
  exit 1
fi

gh auth status >/dev/null

tmp="$(mktemp)"
gh issue list --repo "$REPO" --state open --limit 500 --json number,title,url > "$tmp"

IFS=',' read -r -a EXCLUDES <<< "$EXCLUDE_CSV"
exclude_match() {
  local n="$1"
  for e in "${EXCLUDES[@]}"; do
    if [[ "$n" == "$e" ]]; then
      return 0
    fi
  done
  return 1
}

targets=()
while IFS= read -r n; do
  if ! exclude_match "$n"; then
    targets+=("$n")
  fi
done < <(jq -r '.[].number' "$tmp")

if [[ "${#targets[@]}" -eq 0 ]]; then
  echo "No target issues to label."
  rm -f "$tmp"
  exit 0
fi

echo "Repo: $REPO"
echo "Label: $LABEL"
echo "Exclude: $EXCLUDE_CSV"
echo "Target issue count: ${#targets[@]}"
printf 'Targets: '
printf '#%s ' "${targets[@]}"
echo

if [[ "$DRY_RUN" == "1" ]]; then
  echo "Dry run complete."
  rm -f "$tmp"
  exit 0
fi

for issue in "${targets[@]}"; do
  gh issue edit "$issue" --repo "$REPO" --add-label "$LABEL" >/dev/null
done

echo "Labeling complete."
rm -f "$tmp"

