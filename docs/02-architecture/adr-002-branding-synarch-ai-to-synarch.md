# ADR-002: Branding Consolidation — Synarch AI → Synarch

**Developer:** PraxLannister  
*Architecture Decision Record | 2026-02-13 | Status: DECIDED*

---

## Context
The repository and documentation used multiple naming variants for the same initiative:

- Synarch AI
- Synarch
- Synarch Engine

This created ambiguity in docs, package metadata, and implementation language (especially around company vs product vs agent names).

## Decision
Adopt a single naming model:

1. **Company/Brand:** `Synarch`
2. **Product:** `Synarch Engine`
3. **CEO Agent Name:** `Synarch`
4. **GitHub Organization:** `synarch-ai` (kept as-is)
5. **Runtime namespace prefix:** `synarch.*` for subjects/events

## Rationale

- Removes naming drift across docs and code.
- Keeps a clean distinction between legal/brand identity and product identity.
- Preserves existing mythology hierarchy without renaming deity agents.
- Simplifies onboarding and external communication.

## Scope

### Updated
- Documentation references to use `Synarch` and `Synarch Engine` consistently.
- Agent root path and class naming to `synarch`.
- NATS/event examples to `synarch.*`.
- Package identifiers aligned with `synarch-*` naming pattern.

### Unchanged
- Architecture decisions (LangGraph, NATS, litellm, Qdrant, PostgreSQL).
- Hierarchy model: `God → Synarch → C-Suite → Specialists`.
- Mythology-based C-Suite and specialist names (Zeus, Thoth, Hermes, Hephaestus, Janus, etc.).

## Naming Contract

| Layer | Canonical Name | Example |
|---|---|---|
| Company/Brand | Synarch | "Built by Synarch" |
| Product | Synarch Engine | "Synarch Engine PoC" |
| CEO Agent | Synarch | `SynarchAgent` |
| Event Namespace | synarch | `synarch.agent.zeus.task` |

## Consequences

### Positive
- Lower cognitive load for contributors.
- Cleaner branding in public-facing materials.
- More reliable search/replace and automation workflows.

### Negative
- Requires periodic doc audits to avoid regressions in naming consistency.

## Follow-up

- Maintain naming checks during docs updates.
- Keep ADR-003 (references strategy) aligned with this naming model.

---

*"Synarch: Where agents rule together."*
