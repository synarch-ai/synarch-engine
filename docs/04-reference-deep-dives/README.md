# Reference Deep-Dive Index

**Developer:** PraxLannister  
**Scope:** Source-level technical briefs for every repository under `references/`.

## Purpose

This directory is the implementation-facing companion to:
- `docs/02-architecture/adr-003-reference-repo-strategy.md`
- `docs/02-architecture/adr-004-gap-closure-and-reference-adoption-contract.md`
- `docs/02-architecture/reference-adoption-matrix.md`

Each brief is grounded in real source files and answers five questions:
1. Where does execution start?
2. How does data/state move?
3. What event model and control-plane semantics exist?
4. Which patterns should Synarch adopt vs avoid?
5. What acceptance checks prove adoption is complete?

## Deep-Dive Briefs

| Reference | Brief |
|---|---|
| autogen | `docs/04-reference-deep-dives/autogen/README.md` |
| langgraph | `docs/04-reference-deep-dives/langgraph/README.md` |
| openclaw | `docs/04-reference-deep-dives/openclaw/README.md` |
| crewAI | `docs/04-reference-deep-dives/crewAI/README.md` |
| letta | `docs/04-reference-deep-dives/letta/README.md` |
| llm-council-plus | `docs/04-reference-deep-dives/llm-council-plus/README.md` |
| magentic-ui | `docs/04-reference-deep-dives/magentic-ui/README.md` |
| mcp-use | `docs/04-reference-deep-dives/mcp-use/README.md` |
| playwright-mcp | `docs/04-reference-deep-dives/playwright-mcp/README.md` |
| smolagents | `docs/04-reference-deep-dives/smolagents/README.md` |
| composio | `docs/04-reference-deep-dives/composio/README.md` |
| swarms | `docs/04-reference-deep-dives/swarms/README.md` |

## Usage Rules

1. Before adopting any new pattern from `references/*`, update that reference brief first.
2. Record exact Synarch target files and acceptance checks in the brief.
3. After implementation, update `docs/02-architecture/reference-adoption-matrix.md` and `memory-bank/progress.md` in the same PR.
4. Keep references as pattern sources unless an ADR explicitly authorizes runtime migration/fork.

## Review Cadence

- Refresh every sprint planning cycle.
- Refresh immediately when submodules are updated.
- Refresh before closing any gap-closure workstream in ADR-004.
