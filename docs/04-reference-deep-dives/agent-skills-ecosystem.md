# Agent Skills & Plugin Ecosystem

Curated map of credible skill/plugin systems for pro developer workflows in
Cursor, Claude Code, Codex, and other agents. Synarch installs the **Installed
in this repo** set via `scripts/cloud-agent/install-pro-skills.sh`.

## Installed in this repo

| Source | Install path | Primary commands |
|--------|--------------|------------------|
| [shadcn/improve](https://github.com/shadcn/improve) | `.agents/skills/improve` | `/improve` — read-only audit → `plans/` |
| [garrytan/gstack](https://github.com/garrytan/gstack) | `.agents/skills/gstack-*` + `~/.cursor/skills` | `/gstack-review`, `/gstack-qa`, `/gstack-investigate` |
| [mattpocock/skills](https://github.com/mattpocock/skills) | `.agents/skills/mp-*` | `/mp-triage`, `/mp-implement`, `/mp-tdd` |
| [cursor/plugins pstack](https://github.com/cursor/plugins/tree/main/pstack) | `.agents/skills/pstack-*` | `/pstack-poteto-mode`, `/pstack-setup-pstack` |
| [obra/superpowers](https://github.com/obra/superpowers) | `.agents/skills/*` (namespaced on collision) | TDD, planning, subagent-driven development |

Pinned SHAs: `vendor/skills-sources/manifest.json`.

**Marketplace plugins** (optional; add hooks + auto-invocation in Cursor UI):

- `/add-plugin pstack`
- `/add-plugin superpowers`

## Universal distribution (install anything)

| System | URL | Notes |
|--------|-----|-------|
| **skills.sh** | https://skills.sh | Vercel-maintained registry + `npx skills add owner/repo`. Supports 50+ agents. The npm for agent skills. |
| **Agent Skills open standard** | https://agentskills.io | Vendor-neutral `SKILL.md` format (YAML frontmatter + instructions). |
| **Anthropic skills** | https://github.com/anthropics/skills | Official examples: frontend-design, docx, pdf, mcp-builder, etc. |
| **Vercel skills** | https://github.com/vercel-labs/agent-skills | React/Next.js performance, composition patterns, deploy. |
| **Microsoft azure-skills** | https://github.com/microsoft/azure-skills | Azure AI, infra, and enterprise patterns. |
| **Cursor plugins** | https://github.com/cursor/plugins | Official plugin monorepo (pstack, superpowers, CodeRabbit, etc.). |

```bash
# Install any public skill repo into detected agents
npx skills@latest add anthropics/skills --skill frontend-design
npx skills@latest add vercel-labs/agent-skills
npx skills@latest add mattpocock/skills
```

## Methodology & workflow systems

| System | URL | Best for |
|--------|-----|----------|
| **Superpowers** (obra) | https://github.com/obra/superpowers | Spec → plan → TDD → subagent execution pipeline |
| **pstack** (poteto) | https://github.com/cursor/plugins/tree/main/pstack | Rigorous engineering playbooks, multi-model parallelism |
| **gstack** (Garry Tan) | https://github.com/garrytan/gstack | Browser QA, design review, ship/land workflows |
| **improve** (shadcn) | https://github.com/shadcn/improve | Advisor audits; executor-friendly implementation plans |
| **mattpocock/skills** | https://github.com/mattpocock/skills | Composable engineering skills (triage, TDD, grill-me) |
| **GSD / BMAD / Spec-Kit** | Various | Full process ownership (heavier than composable skills) |

## MCP & tool ecosystems (complementary)

Skills teach *how* agents work; MCP servers give *tools*. High-value pairs:

| MCP / tool plane | Examples |
|------------------|----------|
| **Runlayer / managed MCP** | Org-governed MCP (audit, access control) |
| **Playwright MCP** | Browser automation for QA skills |
| **Composio** | 500+ SaaS integrations as tools |
| **Sourcegraph** | Cross-repo code intelligence |
| **Context.dev** | Live web search, scraping, extraction |

## Synarch-specific recommendations

1. **Audit before big refactors:** `/improve quick` → review `plans/README.md`.
2. **Feature work:** superpowers brainstorming → writing-plans → TDD, or `/pstack-poteto-mode`.
3. **UI changes:** `/gstack-qa` + manual recording per `AGENTS.md`.
4. **Credential plane gap:** improve + principal audit both flag litellm-only keys — track as P0.
5. **Avoid duplicate installs:** pick skills.sh *or* symlink installer for mattpocock; not both.

## Updating pro skills

```bash
bash scripts/cloud-agent/install-pro-skills.sh
```

Re-clones/pulls upstream and refreshes symlinks. Set `INSTALL_PRO_SKILLS=0` to
skip during `install.sh` if you need a faster backend-only bootstrap.
