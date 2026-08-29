# Plan 002: Add AgentTool port and first Hermes research adapter

> **Executor instructions**: Follow this plan step by step. Run every verification command and confirm the expected result before moving to the next step. If anything in the "STOP conditions" section occurs, stop and report — do not improvise.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `8bb4058`, 2026-08-29

## Why this matters

Hermes is the research specialist but only calls `invoke_llm` with no external data sources (`backend/domain/agents/hermes.py`). Research deliverables are therefore LLM-hallucinated rather than grounded. A port-based tool registry matches the hexagonal layout (`ports/`, `adapters/`) and enables NotebookLM, web search, or MCP adapters without bloating the agent class.

## Current state

- `backend/domain/agents/hermes.py` — `execute()` builds messages and calls `self.invoke_llm(...)` only.
- `backend/domain/agents/base.py` — `invoke_llm` wraps `ModelProviderPort`; no tool abstraction.
- `backend/domain/agents/tools/memory_tool.py` — existing tool pattern to study (if present).
- `backend/ports/model_provider.py` — reference for port style (ABC with async methods).
- `docs/agents/hermes/soul.md` — agent identity; update only if tool behavior changes user-facing promises.

Excerpt (`backend/domain/agents/hermes.py`):

```python
response = await self.invoke_llm(
    messages=[{"role": "user", "content": prompt}],
    mission_id=state.get("mission_id"),
)
```

## Commands you will need

| Purpose | Command | Expected on success |
|---------|---------|---------------------|
| Tests | `cd backend && source .venv/bin/activate && TEST_DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch python -m pytest -q` | all pass |
| Unit filter | `python -m pytest -q tests/unit/ -k hermes` | new tests pass |

## In scope

- `backend/ports/research_tool.py` (new) — `ResearchToolPort` ABC
- `backend/adapters/research/` (new) — at least one adapter (e.g. `noop_research.py` or `exa_research.py` stub with env-gated real calls)
- `backend/domain/agents/hermes.py` — inject and call tool before/alongside LLM synthesis
- `backend/container.py` — wire adapter into DI
- `backend/tests/unit/test_hermes_research.py` (new)

## Out of scope

- NotebookLM full integration (follow-up adapter)
- UI changes in Mission Control
- Changing other agents (Thoth, Hephaestus) unless required for DI signature

## Steps

1. Define `ResearchToolPort` with `async def search(self, query: str, *, mission_id: str) -> list[dict]` returning structured snippets (title, url, excerpt).
2. Implement `NoopResearchAdapter` returning empty list (always safe in CI).
3. Optionally implement `EnvGatedExaAdapter` that calls external API only when `EXA_API_KEY` is set; otherwise delegates to noop.
4. Inject `research_tool` into `HermesAgent.__init__`; in `execute`, call `search` and include results in the user prompt before `invoke_llm`.
5. Register adapter in `container.py` following `ModelProviderPort` wiring pattern.
6. Write unit tests: Hermes with noop returns LLM-only behavior; with fake adapter asserting prompt contains snippet text.
7. Run full pytest suite.

## Done criteria

- [ ] `ResearchToolPort` exists under `backend/ports/`
- [ ] Hermes `execute` calls research tool when injected
- [ ] Container wires default noop adapter without breaking boot
- [ ] At least 2 new unit tests pass
- [ ] Full suite: 18+ tests pass

## STOP conditions

- Container bootstrap fails after wiring — revert DI change and report import error.
- Existing mission runtime tests fail — do not patch tests without understanding regression.

## Maintenance note

Future adapters (NotebookLM, Context MCP) implement the same port. Document env vars in `AGENTS.md` when adding real adapters.
