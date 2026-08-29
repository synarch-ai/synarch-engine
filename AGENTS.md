# AGENTS.md

Operating guidance for AI agents working in the Synarch Engine repository.
See `README.md` for product context and architecture.

## Layout

- `backend/` — FastAPI + LangGraph orchestration engine (Python 3.12). Hexagonal
  layout: `api/` (routes, middleware, schemas), `domain/` (agents, orchestrator,
  models, events), `adapters/` (postgres, nats, litellm, langgraph, qdrant),
  `ports/` (interfaces), `tests/`.
- `apps/web/` — Next.js 14 Mission Control dashboard (App Router, Tailwind).
- `infra/docker-compose.yml` — canonical service topology (Postgres+pgvector,
  Redis, NATS, Qdrant, Ollama).
- `scripts/cloud-agent/` — idempotent environment provisioning (see below).

## Local development

The fastest path is the Cloud Agent provisioning scripts, which work on any
Ubuntu host with `sudo`:

```bash
bash scripts/cloud-agent/install.sh   # deps, venv, web deps, DB + migrations (idempotent)
bash scripts/cloud-agent/start.sh     # start Postgres/Redis/NATS + backend:8000 + web:3000
```

Services and ports: PostgreSQL `5432` (native; note `infra/docker-compose.yml`
maps it to `5433`), Redis `6379`, NATS `4222` (+ `8222` monitoring), backend
`8000`, web `3000`.

Local env overrides live in `backend/.env.local` and `apps/web/.env.local`
(gitignored). The backend reads `.env.local` then `.env`.

### Backend

```bash
cd backend && source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000   # or: python main.py (adds --reload)
```

Boot requires PostgreSQL, Redis, and (gracefully degrading) NATS. Side-effecting
API endpoints require an `Idempotency-Key` header.

### Web

```bash
cd apps/web && npm run dev
```

## Testing

```bash
cd backend && source .venv/bin/activate
TEST_DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch \
DATABASE_URL=postgresql://synarch:synarch_local@localhost:5432/synarch \
python -m pytest -q
```

Integration tests require a running PostgreSQL with the migrations applied
(`scripts/cloud-agent/db-bootstrap.sh` handles role/db/migrations idempotently).

## Cursor Cloud specific instructions

- The environment is provisioned by `scripts/cloud-agent/install.sh` (install
  phase) and `scripts/cloud-agent/start.sh` (start phase). `start.sh` self-heals
  dependencies (`backend/.venv`, `apps/web/node_modules`, `.env.local` files) if
  a fresh checkout removed them, then launches all services and both dev servers.
- To verify a change end-to-end after `start.sh`:
  - `curl -fsS http://localhost:8000/api/v1/health` (expect `status: ok`)
  - `curl -fsS http://localhost:8000/api/v1/metrics/daily` (JSON `metrics` array)
  - Create a mission (exercises DB + event sourcing):
    `curl -fsS -X POST http://localhost:8000/api/v1/mission/start -H 'Content-Type: application/json' -H "Idempotency-Key: $(python3 -c 'import uuid;print(uuid.uuid4())')" -d '{"goal":"smoke test","authority_mode":"supervised"}'`
  - Web: `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/dashboard` (expect `200`).
- For UI changes to `apps/web`, do manual GUI testing of the affected page and
  capture a screenshot/recording.
- Live autonomous mission execution calls AWS Bedrock via litellm. Without
  `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (or a local Ollama model), a
  mission transitions to `failed` with a structured `error_context` — expected,
  not an environment defect. Persistence, API, and UI paths do not need
  credentials.

## Pro developer skills

Installed idempotently by `scripts/cloud-agent/install-pro-skills.sh` (also runs
at the end of `install.sh` unless `INSTALL_PRO_SKILLS=0`). Skills symlink into
`.agents/skills/` from pinned upstream repos under `vendor/skills-sources/`
(gitignored except `manifest.json`).

See `docs/04-reference-deep-dives/agent-skills-ecosystem.md` for the full
**PraxStack 2026** architecture diagram, curated tiers, and optional repo
intelligence tools (OpenSpec, Graphify, Serena MCP, Context7 MCP).

### Layered workflow

Use **one methodology per task** — do not combine gstack + superpowers + pstack +
compound-engineering on the same feature (context rot).

```
discover → interrogate/spec → plan → implement → review → security → browser QA → ship → learn
```

| Stage | Skills | When to use |
|-------|--------|-------------|
| discover | `find-skills`, `last30days`, `npx skills find` | Need a capability; search before inventing |
| spec | `brainstorming`, `ce-brainstorm`, `hallmark audit` | Clarify requirements |
| plan | `writing-plans`, `ce-plan`, `improve`, `/pstack-poteto-mode` | Implementation plans |
| implement | `test-driven-development`, `/mp-implement`, `ce-work` | Write code |
| review | `/review`, `ce-code-review`, `impeccable`, CodeRabbit | Pre-merge review |
| security | `tob-*` (on-demand) | Security audit — invoke specific skill only |
| browser QA | `agent-browser`, `/qa` | UI verification |
| ship | `ce-commit-push-pr`, `/ship`, `vercel-deploy-to-vercel` | Land and deploy |
| learn | `ce-compound` | Capture learnings |
| research | `last30days`, `research-deep-research` | Trend scan, deep research |

### Core commands

| Skill / command | When to use |
|-----------------|-------------|
| `find-skills` | Discover/install skills from the open ecosystem |
| `last30days` | 30-day social/web trend research |
| `research-deep-research` | Async Gemini deep research |
| `hallmark` | Anti-slop UI design (audit/redesign/study) |
| `impeccable` | Design QA and polish |
| `/improve` | Read-only codebase audit → prioritized plans in `plans/` |
| `/pstack-poteto-mode` | Rigorous engineering playbooks (bug fix, perf, ship) |
| `/mp-triage`, `/mp-implement`, `/mp-tdd` | Matt Pocock engineering workflows |
| `/review`, `/qa`, `/investigate`, `/plan-ceo-review` | Garry Tan gstack review + planning |
| `agent-browser` | Vercel browser automation CLI + skill |
| `tob-semgrep`, `tob-codeql`, `tob-sharp-edges` | Trail of Bits security (examples) |
| `vercel-react-best-practices` | Next.js/React performance patterns |
| `supabase-postgres-best-practices` | Postgres query/schema optimization |
| `ce-plan`, `ce-work`, `ce-compound` | Compound engineering pipeline |
| `nvidia-rag-blueprint`, `nvidia-cudaq-guide` | NVIDIA RAG/CUDA (on-demand) |
| `wshobson-api-design-principles` | API design patterns (on-demand) |
| `kingmode`, `prax-kingmode`, `super-mode-core` | Deep reasoning orchestrators (praxstack) |
| `constellation-team` / `prax-constellation-team` | Cross-functional star-team workflow |
| `prax-principal-engineer`, `prax-product-manager`, `prax-qa-security-engineer` | Role personas (praxstack) |
| `teach-pro-max` | Adaptive evidence-oriented tutoring |
| `transcript-pipeline`, `blueprint-creator`, `spec-creator` | Document production (praxstack) |

**One-time setup per repo:** `/pstack-setup-pstack`, `/mp-setup-matt-pocock-skills`.

### PraxStack personas, goals, and workflow prompts

The [praxstack/skills-and-personas](https://github.com/praxstack/skills-and-personas)
portfolio installs via `install-pro-skills.sh`. After install, read workflow
prompts from the vendor clone (not copied into the repo):

| Path (under vendor clone) | Purpose |
|---------------------------|---------|
| `prompts/high-end-operator/CATALOG.md` | Full paste-prompt inventory |
| `prompts/high-end-operator/00-router/CLAUDE-ROUTING.md` | Short always-on routing block for AGENTS.md |
| `prompts/project-alignment/ALIGN-INSTALL-QA.md` | Reconstruct project + install packs + report-only QA |
| `prompts/project-alignment/INSTALL-SKILLS.md` | Install named packs only |

**Steady loop** (one prompt per turn — do not load every skill every session):

`/spec` → writing-plans → TDD slice → `/review` → `/ship` → `/retro`

| Stage | Invoke | When |
|-------|--------|------|
| Think | `/office-hours`, `brainstorming`, project-alignment prompts | New idea, lost thread |
| Plan | `/spec`, `writing-plans`, `openspec-propose` | Spec and implementation plan |
| Build | `test-driven-development`, `executing-plans` | One failing test per slice |
| Review | `/review`, `/design-review`, `/cso`, `/plan-eng-review` | Pre-landing review |
| Test | `/qa-only`, `/qa`, `/health` | Report-only or fix-and-verify QA |
| Ship | `/ship`, `/land-and-deploy` | PR and deploy |
| Reflect | `/retro`, `/learn` | End-of-week retrospective |
| Research | `last30days`, `research-deep-research` | Trends and deep research |

**Constellation team:** use `constellation-team` (committed Synarch variant) or
`prax-constellation-team` (canonical praxstack audited skill). Role skills:
`prax-principal-engineer`, `prax-product-manager`, `prax-frontend-uiux-designer`,
`prax-backend-system-design-expert`, `prax-qa-security-engineer`,
`prax-devops-sre-engineer`.

**Optional repo-specific tools** (not run by installer — see ecosystem doc):

```bash
# OpenSpec (greenfield only — do NOT run openspec init in this repo)
npm install -g @fission-ai/openspec@latest

# Graphify codebase graph + MCP
uv tool install graphifyy && graphify cursor install --project

# Context7 live library docs MCP
npx ctx7 setup --cursor

# Serena semantic code retrieval
uv tool install -p 3.13 serena-agent@latest --prerelease=allow && serena init

# Impeccable hooks (skill symlinked by installer; hooks optional)
npx impeccable skills install --providers=cursor --no-hooks
```

**Optional Cursor marketplace plugins** (hooks + auto-invocation):
`/add-plugin pstack`, `/add-plugin superpowers`, `/add-plugin compound-engineering`.

**gstack note:** installed with short slash-command names (`/plan-ceo-review`,
`/review`, `/ship`). Symlinked skills are preferred for Cloud Agents; native
`/add-plugin gstack` has known issues (gstack#2361). On name collisions with
other packs, the installer keeps the `gstack-*` variant.

**Spec Kit:** do not run `specify init` in this repo — see ecosystem doc.

```bash
bash scripts/cloud-agent/install-pro-skills.sh   # refresh all tiers
INSTALL_PRO_SKILLS=1 bash scripts/cloud-agent/install.sh  # full cloud bootstrap
INSTALL_PRO_SKILLS=0 bash scripts/cloud-agent/install.sh  # skip skills (faster)
cat vendor/skills-sources/manifest.json          # pinned SHAs + tier counts
```

See `docs/04-reference-deep-dives/agent-skills-ecosystem.md` for the full
ecosystem map, documented-only sources, and Spec Kit install steps.
