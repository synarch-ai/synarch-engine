# Tech Context: Pantheon AI

## Tech Stack (Decided)

| Layer | Technology | Why |
|---|---|---|
| Orchestration | LangGraph (Python) | State machines, checkpointing, human-in-the-loop |
| Backend API | FastAPI | Async, SSE, OpenAPI auto-docs |
| Event Bus | NATS + JetStream | Subject hierarchy, persistence, 60ns latency |
| Vector DB | Qdrant | Rust-based, hybrid search, multi-tenancy |
| Relational DB | PostgreSQL 16 | LangGraph checkpointing, structured state |
| Frontend | Next.js 14 + shadcn/ui | App Router, streaming, accessible components |
| Local LLM | Ollama (Llama 3.1 8B) | Cost optimization for simple tasks |
| Frontier LLM | **litellm** (wraps Bedrock, Ollama, OpenAI, 100+) | Provider-agnostic: Opus 4, Sonnet 4, Haiku 3.5 via any provider |
| Research | notebooklm-kit 2.2.0 | Full NotebookLM SDK (notes, sources, artifacts) |
| Embedding | nomic-embed-text via Ollama | Local, no API cost |

## Model Routing (Bedrock)

| Complexity | Model | Agent |
|---|---|---|
| STRATEGIC | Claude Opus 4 | Pantheon |
| CREATIVE | Claude Sonnet 4 | Zeus, Thoth, Hephaestus |
| STRUCTURED | Claude Haiku 3.5 | Janus |
| RETRIEVAL | Ollama Llama 3.1 8B | Hermes |

## Infrastructure (Docker)
- NATS: `nats:latest` with JetStream
- Qdrant: `qdrant/qdrant:latest`
- PostgreSQL: `postgres:16-alpine`
- Ollama: `ollama/ollama:latest`
- Backend: runs on host (for MCP access)
- Frontend: runs on host (Next.js dev server)

## Reference Repos (in references/, gitignored)
- `openclaw/` — Agent identity, memory (MEMORY.md), system prompt builder
- `crewAI/` — Role-based crews, task delegation model
- `langgraph/` — Multi-agent examples, checkpointing patterns
- `letta/` — Best-in-class long-term memory management
- `llm-council-plus/` — Multi-agent council/voting concept

## Key Dependencies
- `notebooklm-kit` + `playwright` + `tsx` — NotebookLM SDK (already installed)
- `.auth-profile/` — Persistent Playwright browser session for NotebookLM auth
- AWS credentials in `.env` for Bedrock access

## Development Environment
- macOS Tahoe
- Node.js v22.21.1
- Python 3.12+
- Docker Desktop
- IDE: Antigravity (Cline + Gemini)
