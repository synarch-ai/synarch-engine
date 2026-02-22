# Skills Format Research and Cross-Agent Compatibility

Last verified: January 27, 2026

This note consolidates current public docs for major agents (Claude Code, Gemini CLI, Codex, Cline, Kilo Code) and the Agent Skills open specification. It focuses on whether skill syntax is unified, what differs by tool, and what constraints matter if you want one canonical skills repo.

## Executive summary

- The skill file format is unified across these agents: a skill is a folder containing a `SKILL.md` with YAML frontmatter (`name`, `description`) followed by Markdown instructions.
- Optional supporting directories (such as `scripts/`, `references/`, `assets/`) are widely accepted.
- Differences are mostly about skill locations (where folders live), extra optional fields (like `allowed-tools`), and stricter naming/length rules in some tools.
- Conclusion: You can keep a single canonical skills repo and then install or symlink it into each agent's expected folder. You do not need separate skill formats.

## Universal baseline (Agent Skills open spec)

The Agent Skills spec defines the core format shared by tools:

- Skill = directory with a `SKILL.md` file.
- `SKILL.md` must begin with YAML frontmatter containing:
  - `name`: 1-64 characters, lowercase letters/numbers/hyphens only, no leading/trailing hyphen, no consecutive `--`, must match the directory name.
  - `description`: 1-1024 characters, non-empty, should describe both what the skill does and when to use it.
- Optional frontmatter keys (examples): `license`, `compatibility`, `metadata`, `allowed-tools` (experimental).
- Optional directories: `scripts/`, `references/`, `assets/`.

## Platform-by-platform notes

### Claude Code (Anthropic)

- Skills live in:
  - Personal: `~/.claude/skills/`
  - Project: `.claude/skills/`
- `SKILL.md` uses YAML frontmatter with `name` and `description`.
- Claude Code supports an optional `allowed-tools` field in frontmatter to restrict tool access.
- Anthropic authoring guidance imposes naming constraints (lowercase, numbers, hyphens only) and max length for `name` (64) and `description` (1024).

### Gemini CLI (Google)

- Skills live in:
  - Workspace: `.gemini/skills/`
  - User: `~/.gemini/skills/`
  - Extension skills are also discovered.
- Gemini CLI follows the Agent Skills open standard and uses the same `SKILL.md` frontmatter (`name`, `description`) with an instruction body.
- Standard optional directories are recognized (`scripts/`, `references/`, `assets/`).

### Codex (OpenAI)

- Skills live in:
  - User: `~/.codex/skills/<skill-name>/SKILL.md`
  - Repo: `.codex/skills/<skill-name>/SKILL.md`
- `SKILL.md` uses YAML frontmatter with `name` and `description` and a Markdown body.
- Codex docs specify length limits: `name` <= 100 characters, `description` <= 500 characters. Extra keys are ignored.

### Cline

- Skills live in:
  - Global: `~/.cline/skills/`
  - Project: `.cline/skills/`
  - Also recognized: `.clinerules/skills/` and `.claude/skills/` for compatibility.
- `SKILL.md` uses YAML frontmatter with `name` and `description`.
- Cline requires `name` to exactly match the directory name.
- `description` max length: 1024 characters (per Cline docs).

### Kilo Code

- Skills live in:
  - Global: `~/.kilocode/skills/` (generic, all modes)
  - Project: `.kilocode/skills/` (generic)
- Kilo Code supports mode-specific skills:
  - `~/.kilocode/skills-code/`, `~/.kilocode/skills-architect/` (and similar project paths)
- `SKILL.md` uses YAML frontmatter with `name` and `description`, and Markdown body instructions.

### Antigravity

- No official vendor documentation was found that defines a unique skill syntax.
- In practice, community tooling and the Agent Skills standard indicate it follows the same `SKILL.md` format and uses `.agent/skills/` (project) and `~/.gemini/antigravity/skills/` (user). Verify in official Antigravity docs if they publish any.

## Practical conclusion: one canonical skills repo is enough

You can keep a single skills repo with standard `SKILL.md` files and then install/symlink into each agent's expected directory. The format is shared; the differences are mostly in locations and optional fields.

## Safest universal template (lowest common denominator)

Use this format if you want maximum cross-agent compatibility:

```
---
name: example-skill
description: Use when you need to [specific situation]. Provides [brief summary of what it does].
---

# Example Skill

## Instructions
1. Step one
2. Step two
3. Step three
```

Recommended constraints to avoid breaking any platform:

- `name`: lowercase, numbers, hyphens only; 1-64 chars; match folder name.
- `description`: keep <= 500 chars to satisfy Codex limits; be explicit about when to use the skill.
- Avoid reserved words (Anthropic guidance: do not use "anthropic" or "claude" in name).

## Differences that matter in practice

- `allowed-tools` is supported by Claude Code only. Other tools typically ignore it.
- Cline and the Agent Skills spec require `name` to match the directory name.
- Kilo Code supports mode-specific skill directories (e.g., `skills-code`, `skills-architect`).
- Codex has stricter length limits on `name` and `description` than the open spec.

## Suggested repo strategy

- Keep one canonical skills repo with strict naming and description length constraints.
- Add small per-agent overlays only when needed (for example, add `allowed-tools` to Claude-specific skills).
- Use symlinks or an installer (like `vercel-skills`) to populate each agent directory.

## Sources (public docs)

- Agent Skills Specification: https://agentskills.io/specification
- Agent Skills Overview: https://agentskills.io/what-are-skills
- Claude Code Skills: https://docs.claude.com/en/docs/claude-code/skills
- Anthropic authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Gemini CLI Skills: https://geminicli.com/docs/cli/skills/
- OpenAI Codex Skills (Create Skill): https://developers.openai.com/codex/skills/create-skill
- OpenAI Codex Skills (Overview): https://developers.openai.com/codex/skills
- Cline Skills: https://docs.cline.bot/features/skills
- Kilo Code Skills: https://kilo.ai/docs/agent-behavior/skills
