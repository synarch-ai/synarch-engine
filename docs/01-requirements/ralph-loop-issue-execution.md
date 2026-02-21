# Ralph Loop Issue Execution

This workflow runs implementation issues through Ralphy while preserving PR traceability.

## Why this workflow exists

Running autonomous loops blindly across all open issues is risky and noisy.  
This process scopes execution to labeled implementation issues and audits issue-to-PR linkage.

## Required labels

- `ralph-ready`: issue is approved for autonomous execution
- `ralph-blocked`: issue has dependency or environment blocker
- `ralph-done`: issue delivered and verified

Create labels once:

```bash
gh label create ralph-ready --repo synarch-ai/synarch-engine --color 1f6feb --description "Ready for Ralph loop execution" 2>/dev/null || true
gh label create ralph-blocked --repo synarch-ai/synarch-engine --color d73a4a --description "Blocked issue" 2>/dev/null || true
gh label create ralph-done --repo synarch-ai/synarch-engine --color 2da44e --description "Completed by Ralph loop and validated" 2>/dev/null || true
```

## Run all ready issues through Ralph

From repo root:

```bash
chmod +x scripts/ralph/run_issues_via_ralph.sh scripts/ralph/audit_issue_pr_coverage.sh scripts/ralph/label_open_issues.sh
scripts/ralph/label_open_issues.sh --repo synarch-ai/synarch-engine --exclude 1
scripts/ralph/run_issues_via_ralph.sh \
  --repo synarch-ai/synarch-engine \
  --label ralph-ready \
  --engine codex \
  --parallel 2 \
  --base-branch main \
  --max-retries 2 \
  --max-iterations 0
```

### Safe first run (dry run)

```bash
scripts/ralph/run_issues_via_ralph.sh \
  --repo synarch-ai/synarch-engine \
  --label ralph-ready \
  --engine codex \
  --parallel 2 \
  --dry-run
```

## Audit that no issue is left without PR linkage

```bash
scripts/ralph/audit_issue_pr_coverage.sh \
  --repo synarch-ai/synarch-engine \
  --label ralph-ready \
  --state all
```

The audit exits non-zero if any scoped issue has no linked PR.

## Guardrails

1. Do not include parent/meta issues (like PRD umbrella issues) in `ralph-ready`.
2. Keep CI required checks enabled so bad PRs cannot merge.
3. Use draft PRs first for broad issue batches.
4. Promote to `ralph-done` only after manual verification + green checks.
