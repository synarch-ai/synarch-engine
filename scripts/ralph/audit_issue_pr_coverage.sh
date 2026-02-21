#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Audit issue -> PR linkage so no implementation issue is left without PR traceability.

Usage:
  scripts/ralph/audit_issue_pr_coverage.sh --repo owner/repo [options]

Options:
  --repo <owner/repo>       GitHub repository (required)
  --label <name>            Scope issues to label (default: ralph-ready)
  --state <open|closed|all> Issue state filter (default: all)
  -h, --help                Show this help
EOF
}

REPO=""
LABEL="ralph-ready"
STATE="all"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --state) STATE="${2:-}"; shift 2 ;;
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

tmp_issues="$(mktemp)"
gh issue list \
  --repo "$REPO" \
  --state "$STATE" \
  --label "$LABEL" \
  --limit 500 \
  --json number,title,state,url \
  > "$tmp_issues"

count="$(jq 'length' "$tmp_issues")"
if [[ "$count" == "0" ]]; then
  echo "No issues found for repo='$REPO' label='$LABEL' state='$STATE'."
  rm -f "$tmp_issues"
  exit 0
fi

echo "| Issue | State | Linked PRs | Status |"
echo "|---|---|---:|---|"

missing=0
for issue in $(jq -r '.[].number' "$tmp_issues"); do
  state="$(jq -r ".[] | select(.number==$issue) | .state" "$tmp_issues")"
  # Heuristic linkage: PR body/title/metadata referencing #<issue>
  pr_count="$(gh pr list --repo "$REPO" --state all --search "#$issue" --json number | jq 'length')"
  if [[ "$pr_count" -eq 0 ]]; then
    status="MISSING_PR_LINK"
    missing=$((missing + 1))
  else
    status="OK"
  fi
  echo "| #$issue | $state | $pr_count | $status |"
done

rm -f "$tmp_issues"

if [[ "$missing" -gt 0 ]]; then
  echo
  echo "Audit failed: $missing issue(s) without PR linkage."
  exit 3
fi

echo
echo "Audit passed: all scoped issues have at least one linked PR."

