# Pantheon AI — Next Session Prompt

Copy everything below this line into a new Cline chat:

---

#pantheon-ai

## Context
You are resuming work on **Pantheon AI** — an open-source autonomous multi-agent operating system. M0 (Research & Architecture) is complete. You are starting **M1: Foundation**.

## Instructions

1. **Read the memory bank first:**
   - `memory-bank/projectbrief.md` — mission, scope, acceptance criteria
   - `memory-bank/techContext.md` — full tech stack (LangGraph, NATS, litellm, Qdrant, PostgreSQL, Next.js)
   - `memory-bank/systemPatterns.md` — hierarchy, nervous system, soul system, Rule of Two
   - `memory-bank/activeContext.md` — latest decisions, next steps
   - `memory-bank/progress.md` — milestone tracker

2. **Read the PRD:**
   - `docs/01-requirements/poc-prd.md` — comprehensive PoC requirements

3. **Read the ADR:**
   - `docs/02-architecture/adr-001-swarms-vs-langgraph.md` — why LangGraph, what to steal from Swarms

4. **Read the agent souls (know who you're building):**
   - `docs/agents/pantheon/soul.md` through `docs/agents/janus/soul.md`

5. **Study reference patterns (don't copy code, learn patterns):**
   - `references/langgraph/` — study multi-agent supervisor examples
   - `references/swarms/swarms/structs/hiearchical_swarm.py` — Director→Worker planning prompts
   - `references/swarms/swarms/structs/model_router.py` — complexity-based model routing
   - `references/openclaw/src/agents/system-prompt.ts` — system prompt compilation

## Build M1: Foundation

Execute these in order:

### Step 1: Docker Compose
Create `docker-compose.yml` with: NATS (JetStream), Qdrant, PostgreSQL 16, Ollama. Test with `docker compose up`.

### Step 2: Python Backend
Create `backend/` with:
- `requirements.txt` — langgraph, litellm, fastapi, uvicorn, nats-py, qdrant-client, psycopg
- `main.py` — FastAPI app with health check, `/mission/start`, `/mission/{id}/stream` (SSE)
- `orchestrator/state.py` — TypedDict for mission state
- `orchestrator/graph.py` — LangGraph StateGraph with Pantheon as entry node

### Step 3: AgentNode Base Class
Create the standardized agent wrapper (from Antigravity's analysis):
```python
class AgentNode:
    def __init__(self, soul_path: str, model: str, tools: list):
        self.soul = load_soul(soul_path)  # Parse soul.md
        self.model = model  # litellm model string
        self.tools = tools
    async def run(self, state: MissionState) -> dict:
        # Build system prompt from soul.md
        # Call litellm.completion()
        # Publish event to NATS
        # Return updated state
```

### Step 4: Pantheon Node
Implement Pantheon (CEO) — receives goal, decomposes into tasks, delegates to Zeus + Thoth.

### Step 5: Next.js Skeleton
Create `frontend/` with Next.js 14 + shadcn/ui. Minimal: chat input + thought stream (SSE consumer).

## Critical Rules
- **Use litellm** for ALL model calls (not raw Bedrock/OpenAI SDK)
- **Use NATS** for all agent events (not in-memory)
- **Use PostgreSQL** for checkpointing (not JSON files)
- **NotebookLM is NOT in PoC** — RAG is Phase 2
- **Backend runs on host**, infra in Docker
- **Every agent reads its soul.md** as system prompt foundation
- **All agent events publish to NATS** subjects: `pantheon.agent.{name}.{event}`
- **God = Human user**, Pantheon = CEO, hierarchy is non-negotiable

## Model Routing (litellm)
```
Pantheon: bedrock/anthropic.claude-opus-4-20250514-v1:0
Zeus:     bedrock/anthropic.claude-sonnet-4-20250514-v1:0
Thoth:    bedrock/anthropic.claude-sonnet-4-20250514-v1:0
Hermes:   ollama/llama3.1:8b
Hephaestus: bedrock/anthropic.claude-sonnet-4-20250514-v1:0
Janus:    bedrock/anthropic.claude-3-5-haiku-20241022-v1:0
```

## Start building. Show me gods that think.
