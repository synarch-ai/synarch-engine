# Agent Skills & Plugin Ecosystem

Curated map of credible skill/plugin systems for pro developer workflows in
Cursor, Claude Code, Codex, and other agents. Synarch installs the **Installed
in this repo** set via `scripts/cloud-agent/install-pro-skills.sh`.

## Layered pipeline

Use one layer at a time per task — do not stack competing methodologies
(superpowers + pstack + compound-engineering on the same feature causes context
rot and conflicting instructions).

```mermaid
flowchart LR
  D[discover] --> I[interrogate / spec]
  I --> P[plan]
  P --> M[implement]
  M --> R[review]
  R --> S[security]
  S --> B[browser QA]
  B --> H[ship]
  H --> L[learn]
```

| Stage | Installed skills | When |
|-------|------------------|------|
| **discover** | `find-skills` | User needs a capability; search skills.sh before inventing workflows |
| **interrogate / spec** | `brainstorming`, `ce-brainstorm`, `gh-copilot-breakdown-feature-prd` | Clarify requirements, write specs |
| **plan** | `writing-plans`, `ce-plan`, `mp-triage`, `pstack-poteto-mode`, `improve` | Produce implementation plans |
| **implement** | `test-driven-development`, `mp-implement`, `mp-tdd`, `ce-work` | Write code with TDD or structured execution |
| **review** | `review`, `ce-code-review`, `pstack-*`, CodeRabbit | Code review before merge |
| **security** | `tob-*` (Trail of Bits, on-demand) | Security audit, static analysis, fuzzing — invoke explicitly |
| **browser QA** | `agent-browser`, `qa`, `ce-test-browser` | Manual/automated UI verification |
| **ship** | `ship`, `ce-commit-push-pr`, `vercel-deploy-to-vercel` | Land PRs, deploy |
| **learn** | `ce-compound`, `ce-compound-refresh` | Capture learnings for next iteration |

## Core 10

High-signal skills every Synarch agent should know about (all installed):

| # | Source | Symlink prefix | Primary use |
|---|--------|----------------|-------------|
| 1 | [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack) | `pstack-*` | Rigorous engineering playbooks |
| 2 | [obra/superpowers](https://github.com/obra/superpowers) | (root or `superpowers-*`) | TDD, planning, subagent development |
| 3 | [mattpocock/skills](https://github.com/mattpocock/skills) | `mp-*` | Composable engineering workflows |
| 4 | [garrytan/gstack](https://github.com/garrytan/gstack) | short names (`review`, `plan-ceo-review`; `gstack-*` on collision) | Review, QA, browser automation |
| 5 | [shadcn/improve](https://github.com/shadcn/improve) | `improve` | Read-only audit → `plans/` |
| 6 | [trailofbits/skills](https://github.com/trailofbits/skills) | `tob-*` | Security analysis (on-demand) |
| 7 | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | `agent-browser` | CLI + skill for browser QA |
| 8 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | `vercel-*` | React/Next.js performance, deploy |
| 9 | [vercel-labs/skills](https://github.com/vercel-labs/skills) | `find-skills` | Discover skills from the ecosystem |
| 10 | [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | `ce-*` | Spec → plan → implement → compound learnings |

Pinned SHAs and per-tier counts: `vendor/skills-sources/manifest.json`.

## Installed in this repo (by tier)

### Tier 0 — Discovery

| Source | Symlink | Command |
|--------|---------|---------|
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | `find-skills` | Search/install via `npx skills find` |

### Core (original installer)

| Source | Symlink prefix | Primary commands |
|--------|----------------|------------------|
| [shadcn/improve](https://github.com/shadcn/improve) | `improve` | `/improve` — read-only audit → `plans/` |
| [garrytan/gstack](https://github.com/garrytan/gstack) | short names + `~/.cursor/skills` | `/review`, `/qa`, `/plan-ceo-review`, `/ship` |
| [mattpocock/skills](https://github.com/mattpocock/skills) | `mp-*` | `/mp-triage`, `/mp-implement`, `/mp-tdd` |
| [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack) | `pstack-*` | `/pstack-poteto-mode`, `/pstack-setup-pstack` |
| [obra/superpowers](https://github.com/obra/superpowers) | root / `superpowers-*` | TDD, planning, subagent-driven development |

### Tier S+ — Security

| Source | Symlink prefix | Notes |
|--------|----------------|-------|
| [trailofbits/skills](https://github.com/trailofbits/skills) | `tob-*` | ~80 skills; **on-demand only** — do not load all into context |

### Tier S+ — Browser QA

| Source | Install | Notes |
|--------|---------|-------|
| `agent-browser` CLI | `npm install -g agent-browser && agent-browser install` | Installed by installer; falls back to `npx` |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | `agent-browser` | Skill for browser automation workflows |

### Tier S — Web & reference

| Source | Symlink prefix | Notes |
|--------|----------------|-------|
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | `vercel-*` | React best practices, composition patterns, deploy |
| [anthropics/skills](https://github.com/anthropics/skills) | `anthropic-*` | Dev subset only: mcp-builder, frontend-design, webapp-testing, web-artifacts-builder, skill-creator, claude-api |

### Tier A+ — Toolbox (curated)

| Source | Symlink prefix | Notes |
|--------|----------------|-------|
| [github/awesome-copilot](https://github.com/github/awesome-copilot) | `gh-copilot-*` | ~15 high-signal engineering skills (not full 100+ dump) |

Curated subset: codebase knowledge, feature breakdown, implementation plans,
Playwright exploration, bug reproduction, GitHub issue/PR workflows, agentic
workflows.

### Stack-specific (Synarch)

| Source | Symlink prefix | Notes |
|--------|----------------|-------|
| [supabase/agent-skills](https://github.com/supabase/agent-skills) | `supabase-*` | Postgres best practices, database design |

### Compound Engineering

| Source | Symlink prefix | Notes |
|--------|----------------|-------|
| [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | `ce-*` | Full spec→ship→learn pipeline |

**Cursor native install (optional):** `/add-plugin compound-engineering`

## Documented only (not installed wholesale)

These are referenced for optional manual install — installing entire repos causes
context rot.

| Source | Why documented-only | How to add |
|--------|---------------------|------------|
| [microsoft/skills](https://github.com/microsoft/skills) | 100+ skills; too broad for always-on context | `npx skills add microsoft/skills --skill <name>` |
| [aws/agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) | AWS-specific; Synarch uses Bedrock via litellm | Install when AWS agent tooling is needed |
| [cloudflare/skills](https://github.com/cloudflare/skills) | Edge/workers-specific | `npx skills add cloudflare/skills` |
| [github/spec-kit](https://github.com/github/spec-kit) | `specify init` mutates repo heavily | See Spec Kit section below |

## Cursor marketplace (native plugins)

Optional; adds hooks + auto-invocation in Cursor UI beyond symlinked skills:

| Plugin | Install |
|--------|---------|
| pstack | `/add-plugin pstack` |
| superpowers | `/add-plugin superpowers` |
| compound-engineering | `/add-plugin compound-engineering` |

### gstack Cursor caveat

We symlink gstack skills into `.agents/skills/` with gstack's default short names
(`/plan-ceo-review`, `/review`) and run `./setup --host cursor --no-prefix` for
`~/.cursor/skills`. On name collisions with other packs, the installer keeps the
`gstack-*` variant. The native Cursor plugin path has known issues
([gstack#2361](https://github.com/garrytan/gstack/issues/2361)) — prefer
symlinked skills for Cloud Agents; use `/add-plugin gstack` only if you need
native hooks and accept potential breakage.

## Spec Kit

Do **not** run `specify init` in the Synarch repo — it rewrites project
structure. For greenfield projects:

```bash
# Outside this repo only
uv tool install specify-cli
specify init my-project --ai claude
```

## Universal distribution

| System | URL | Notes |
|--------|-----|-------|
| **skills.sh** | https://skills.sh | Vercel-maintained registry + `npx skills add owner/repo` |
| **Agent Skills open standard** | https://agentskills.io | Vendor-neutral `SKILL.md` format |
| **Cursor plugins** | https://github.com/cursor/plugins | Official plugin monorepo |

```bash
npx skills@latest find "postgres"
npx skills@latest add anthropics/skills --skill frontend-design
npx skills@latest add vercel-labs/agent-skills
```

## MCP & tool ecosystems (complementary)

Skills teach *how* agents work; MCP servers give *tools*.

| MCP / tool plane | Examples |
|------------------|----------|
| **Runlayer / managed MCP** | Org-governed MCP (audit, access control) |
| **Playwright MCP** | Browser automation for QA skills |
| **Composio** | 500+ SaaS integrations as tools |
| **Sourcegraph** | Cross-repo code intelligence |
| **Context.dev** | Live web search, scraping, extraction |

## Synarch-specific recommendations

1. **Start with discovery:** `find-skills` or `npx skills find` before adding skills.
2. **Audit before big refactors:** `/improve quick` → review `plans/README.md`.
3. **Feature work:** pick *one* methodology — superpowers *or* pstack *or* compound-engineering.
4. **UI changes:** `agent-browser` or `/gstack-qa` + manual recording per `AGENTS.md`.
5. **Security review:** invoke specific `tob-*` skills (semgrep, codeql, sharp-edges) on demand.
6. **Postgres/RLS:** `supabase-postgres-best-practices` for query and schema work.
7. **Avoid duplicate installs:** pick skills.sh *or* symlink installer for the same source.

## Updating pro skills

```bash
bash scripts/cloud-agent/install-pro-skills.sh
# Inspect counts
cat vendor/skills-sources/manifest.json | python3 -m json.tool
ls .agents/skills | wc -l
```

Re-clones/pulls upstream and refreshes symlinks. Set `INSTALL_PRO_SKILLS=0` to
skip during `install.sh` if you need a faster backend-only bootstrap.
