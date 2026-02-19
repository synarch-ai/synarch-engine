# ADR-001: Swarms vs Custom LangGraph

**Developer:** PraxLannister
*Architecture Decision Record | 2026-02-13 | Status: DECIDED*

---

## The Question
Should Synarch AI fork and build upon `kyegomez/swarms`, or keep it as reference and build custom LangGraph?

## Analysis (Dual — Cline + Antigravity independently agreed)

### What Swarms Offers (v9.0.0)
- `HierarchicalSwarm`: Director→Worker pattern (nearly identical to Synarch→C-Suite→Specialist)
- `litellm`: Universal model provider interface (Bedrock, Ollama, OpenAI, 100+)
- MCP client tools: Native MCP server integration from Python
- `model_router.py`: Complexity-based routing (maps to our Opus/Sonnet/Haiku/Ollama tiers)
- `HierarchicalSwarmDashboard`: Rich terminal dashboard with real-time monitoring
- `auto_swarm_builder.py`: Auto-generate agents from prompts
- `board_of_directors_swarm.py`: Multi-agent debate/voting

### Why NOT Fork
1. **Too heavy** — Agent class is 6000+ lines, massive dependency chain
2. **Tightly coupled to terminal** — Rich console dashboard, not web-compatible
3. **Synchronous** — Standard Python while loop, no NATS/event-driven
4. **No LangGraph** — Built their own orchestration without state machine checkpointing
5. **JSON persistence** — Not PostgreSQL-grade, no crash recovery
6. **No SSE streaming** — Terminal output only, not structured events for Next.js
7. **To adapt it, we'd rewrite the core** — effectively defeating the purpose of forking

### Why LangGraph Instead
1. **Native PostgreSQL checkpointing** — built-in crash recovery
2. **Native `stream_events()`** — granular updates for Next.js frontend
3. **State machines** — conditional edges, human-in-the-loop nodes
4. **Full control** — we define the graph, we define the hierarchy

## Decision: **REFERENCE, NOT FORK**

Keep `swarms` in `references/` for pattern study. Build on LangGraph.

## What We Adopt (patterns, not code)

| From Swarms | Our Implementation |
|---|---|
| `HIEARCHICAL_SWARM_SYSTEM_PROMPT` | Adapt for Synarch's system prompt |
| `HierarchicalOrder` Pydantic model | Use for structured task delegation |
| `SwarmSpec` data structure | Use for mission specification |
| Director→Plan→Order→Feedback loop | Implement in LangGraph StateGraph |
| `litellm` library | **USE DIRECTLY** — replaces raw Bedrock SDK |
| MCP client integration pattern | Study `mcp_client_tools.py` for future MCP support |
| `model_router.py` logic | Adapt for our Opus/Sonnet/Haiku/Ollama routing |

## Key Change to PRD

**Replace raw AWS Bedrock SDK with `litellm`:**
- One interface for ALL providers (Bedrock, Ollama, OpenAI, Groq, etc.)
- Provider-agnostic model routing
- Users bring their own API keys for any provider
- Future: agents can vote on model selection from full litellm catalog

```python
# Before (raw Bedrock):
import boto3
client = boto3.client('bedrock-runtime')

# After (litellm):
from litellm import completion
response = completion(
    model="bedrock/anthropic.claude-sonnet-4-20250514-v1:0",
    messages=[{"role": "user", "content": "..."}]
)
# OR
response = completion(
    model="ollama/llama3.1:8b",
    messages=[{"role": "user", "content": "..."}]
)
```

## Consequences
- We own the orchestration layer fully (LangGraph)
- We use litellm for model abstraction (lighter than importing all of swarms)
- We study swarms for patterns but don't inherit their tech debt
- Users get provider flexibility from day 1

---

*Both Cline (Claude Opus 4) and Antigravity (Gemini 3 Pro) independently reached the same verdict. High confidence decision.*
