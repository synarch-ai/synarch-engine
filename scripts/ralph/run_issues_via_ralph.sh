#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Run GitHub issues through Ralphy with strict defaults.

Usage:
  scripts/ralph/run_issues_via_ralph.sh --repo owner/repo [options]

Options:
  --repo <owner/repo>       GitHub repository (required)
  --label <name>            Only process issues with this label (default: ralph-ready)
  --engine <name>           Engine: claude|codex|cursor|opencode|qwen|droid|copilot|gemini (default: codex)
  --base-branch <name>      Base branch for PRs (default: main)
  --parallel <n>            Max parallel workers; 1 disables parallel mode (default: 2)
  --max-retries <n>         Task retries per issue (default: 2)
  --retry-delay <sec>       Delay between retries in seconds (default: 5)
  --max-iterations <n>      Max tasks per run; 0 means unlimited (default: 0)
  --no-draft                Create normal PRs instead of draft PRs
  --dry-run                 Print command and exit without executing
  -h, --help                Show this help

Notes:
  - This script requires a clean git working tree.
  - Use labels so only implementation issues are processed (exclude parent/meta issues).
EOF
}

REPO=""
LABEL="ralph-ready"
ENGINE="codex"
BASE_BRANCH="main"
PARALLEL="2"
MAX_RETRIES="2"
RETRY_DELAY="5"
MAX_ITERATIONS="0"
DRAFT_PR="1"
DRY_RUN="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --label) LABEL="${2:-}"; shift 2 ;;
    --engine) ENGINE="${2:-}"; shift 2 ;;
    --base-branch) BASE_BRANCH="${2:-}"; shift 2 ;;
    --parallel) PARALLEL="${2:-}"; shift 2 ;;
    --max-retries) MAX_RETRIES="${2:-}"; shift 2 ;;
    --retry-delay) RETRY_DELAY="${2:-}"; shift 2 ;;
    --max-iterations) MAX_ITERATIONS="${2:-}"; shift 2 ;;
    --no-draft) DRAFT_PR="0"; shift ;;
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

# Ensure downstream tools (ralphy/octokit) can access private repos.
if [[ -z "${GITHUB_TOKEN:-}" ]] && [[ -z "${GH_TOKEN:-}" ]]; then
  token="$(gh auth token 2>/dev/null || true)"
  if [[ -n "$token" ]]; then
    export GITHUB_TOKEN="$token"
    export GH_TOKEN="$token"
  fi
fi

if [[ "$DRY_RUN" != "1" ]] && [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: git working tree is dirty. Commit/stash first." >&2
  exit 1
fi

ISSUE_COUNT="$(gh issue list --repo "$REPO" --state open --label "$LABEL" --limit 500 --json number | jq 'length')"
if [[ "$ISSUE_COUNT" == "0" ]]; then
  echo "No open issues found with label '$LABEL' in '$REPO'."
  exit 0
fi

ENGINE_FLAG="--$ENGINE"
case "$ENGINE" in
  claude|codex|cursor|opencode|qwen|droid|copilot|gemini) ;;
  *)
    echo "Error: unsupported engine '$ENGINE'." >&2
    exit 2
    ;;
esac

CMD=(
  npx -y ralphy-cli
  "$ENGINE_FLAG"
  --github "$REPO"
  --github-label "$LABEL"
  --branch-per-task
  --create-pr
  --base-branch "$BASE_BRANCH"
  --max-retries "$MAX_RETRIES"
  --retry-delay "$RETRY_DELAY"
  --max-iterations "$MAX_ITERATIONS"
)

if [[ "$DRAFT_PR" == "1" ]]; then
  CMD+=(--draft-pr)
fi

if [[ "$PARALLEL" =~ ^[0-9]+$ ]] && [[ "$PARALLEL" -gt 1 ]]; then
  CMD+=(--parallel --max-parallel "$PARALLEL")
fi

if [[ "$DRY_RUN" == "1" ]]; then
  CMD+=(--dry-run)
fi

echo "Repository: $REPO"
echo "Label: $LABEL"
echo "Engine: $ENGINE"
echo "Open labeled issues: $ISSUE_COUNT"
echo "Command:"
printf '  %q' "${CMD[@]}"
echo

if [[ "$DRY_RUN" == "1" ]]; then
  echo "Dry run complete."
  exit 0
fi

"${CMD[@]}"
