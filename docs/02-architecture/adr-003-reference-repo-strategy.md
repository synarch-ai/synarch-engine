# ADR-003: Reference Repository Strategy

**Developer:** PraxLannister  
*Architecture Decision Record | 2026-02-19 | Status: ACCEPTED*

---

## Context
Synarch Engine depends on rapid learning from upstream agent ecosystems while keeping a focused in-house architecture (LangGraph + NATS + FastAPI + Next.js + soul-based hierarchy).  
Unstructured dependency sprawl increases maintenance cost and creates architectural drift.

## Decision
Use a **curated reference strategy**:

1. Track selected upstream projects as `git submodule`s under `references/`.
2. Treat these repositories as **pattern sources**, not direct runtime dependencies.
3. Keep Sync Policy: update submodules regularly; adopt ideas selectively through ADRs and implementation notes.
4. Default mode is **keep-as-reference**, not fork.

## Reference Set (Current)

### Core Orchestration and Agent Patterns
- `references/langgraph`
- `references/openclaw`
- `references/crewAI`
- `references/autogen`
- `references/swarms`
- `references/letta`
- `references/llm-council-plus`

### Tooling, MCP, and HITL UX Patterns
- `references/playwright-mcp`
- `references/mcp-use`
- `references/smolagents`
- `references/magentic-ui`
- `references/composio`

## Fork Policy
Fork only when at least one condition is true:

1. A blocking defect impacts Synarch and cannot be addressed upstream in required timeline.
2. A strategic capability requires long-lived custom patches.
3. License/compliance requirements demand controlled distribution.

If none apply, keep upstream as submodule and avoid maintenance burden.

## Evaluation Rubric for New References
Every candidate repo must score positively on:

1. Architectural fit with Synarch goals (hierarchy, event-driven runtime, observability, security).
2. Maintenance health (recent commits, issue responsiveness, release cadence).
3. License compatibility and commercial safety.
4. Practical extraction value (copyable patterns, not just marketing claims).

## Update and Operations

### Standard Update Command
```bash
git submodule update --init --recursive --remote -- references
```

### Cadence
- Before major milestone planning.
- Before architecture ADR changes.
- At least once per active sprint.

### Documentation Requirement
When a reference materially affects implementation direction:

1. Capture decision in an ADR.
2. Add implementation notes in docs/memory-bank.
3. Keep naming and namespace conventions aligned with ADR-002.

## Consequences

### Positive
- Faster architecture learning without codebase lock-in.
- Repeatable update process for reference intelligence.
- Lower long-term maintenance than premature forking.

### Negative
- Requires discipline to avoid importing conflicting patterns.
- Submodule refreshes can create noisy pointer diffs.

---

*"Reference broadly, implement deliberately."*
