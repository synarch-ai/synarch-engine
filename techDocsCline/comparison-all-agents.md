# Tech Docs Comparison — Cline vs Codex vs Antigravity

**Date:** 2026-02-21 | **Purpose:** Identify best-of-breed from each agent's architecture docs for merging into canonical set

---

## Summary Verdict

| Doc | Winner | Why |
|---|---|---|
| **HLD** | **Cline** for detail, **Antigravity** for governance | Cline has ASCII diagrams, StateGraph code, component trees. Antigravity adds Rule-of-Two, cost-degradation, WASM sandboxing |
| **DB Schema** | **Cline** for completeness | 8 tables vs Antigravity's 6. Cline adds cost_logs, agent_configs, memories, checkpoints |
| **API Contract** | **Cline** for spec detail | Full JSON request/response, SSE streaming, idempotency, error codes |
| **Event Catalog** | **Cline** for breadth | 30+ events, 8 categories, consumer groups, SSE bridge mapping |

---

## 1. HLD Comparison

### Cline's synarch-hld.md (v1.1, 383 lines)

**Strengths:**
- Full ASCII system architecture diagram
- Agent hierarchy tree with tool assignments and model tiers
- Mission state machine with ASCII diagram + transition table
- LangGraph `MissionState` TypedDict definition (actual Python code)
- Graph nodes table with agent assignment
- 11-step data flow narrative
- Complete component architecture (backend/ file tree)
- Docker Compose service table with ports
- Agent Permission Matrix (security)
- NATS subject hierarchy
- Non-functional requirements with targets

**Missing:**
- Rule-of-Two governance pattern
- Cost-degradation to Ollama
- WASM/Container sandboxing detail
- A2A/MCP interoperability section
- Config-driven agent identity loading

### Antigravity's synarch-hld.md (v1.2, from earlier extraction)

**Strengths:**
- "Rule of Two" governance (HITL approval with auto-reject timeout)
- Cost-degradation logic (auto-downgrade to local Ollama models)
- WASM/Container sandboxing (FR-80)
- Prompt injection scanning before graph execution (FR-54)
- A2A/MCP interoperability readiness (FR-61–63)
- Config-driven agent identity from YAML/JSON (FR-65/67)
- Higher version (v1.2 based on PRD-final.MD v1.2)

**Missing:**
- Less detailed component architecture
- No ASCII diagrams
- No LangGraph code definitions

### Codex's synarch-hld.md

**Strengths:**
- Explicit numbered architecture invariants (6 MUST rules)
- Interaction contracts between planes

**Missing:**
- No agent hierarchy, no diagrams, no code, no file trees

### 🎯 MERGE RECOMMENDATION for HLD:
Take Cline's as base (diagrams, code, detail), add Antigravity's Rule-of-Two, cost-degradation, WASM, A2A/MCP, and config-driven sections.

---

## 2. DB Schema Comparison

### Cline (8 tables)

| Table | Purpose |
|---|---|
| `missions` | Central entity, all states, cost tracking, thread_id |
| `sub_tasks` | Individual work items per mission |
| `agent_events` | Immutable audit log (every agent action) |
| `approvals` | HITL approval records with LangGraph interrupt metadata |
| `checkpoints` | LangGraph checkpoint storage (2 tables) |
| `cost_logs` | Per-LLM-call cost tracking (model, tokens, $) |
| `agent_configs` | Agent configuration from YAML (tools, permissions) |
| `memories` | Long-term agent memory with TTL |

### Antigravity (6 tables)

| Table | Purpose |
|---|---|
| `missions` | Central entity |
| `tasks` | Work items (named "tasks" not "sub_tasks") |
| `approvals` | HITL records |
| `mission_events` | Audit log (named differently) |
| `replay_metadata` | Mission replay/time-travel (FR-85) |
| `deliverables` | Mission output artifacts |

### Codex
- Single `master-db-schema.md` in `docs/05-data/`
- Content not fully extracted in comparison

### Key Differences

| Aspect | Cline | Antigravity |
|---|---|---|
| Table count | 8 | 6 |
| Cost tracking | Separate `cost_logs` table | Cost columns on missions |
| Agent config storage | `agent_configs` table | Not in schema |
| Memory storage | `memories` table with TTL | Not in schema |
| LangGraph checkpoints | Dedicated `checkpoints` tables | Not in schema |
| Replay/time-travel | Not in schema | `replay_metadata` table |
| Deliverables | Result stored as JSONB on missions | Separate `deliverables` table |
| Naming convention | `sub_tasks`, `agent_events` | `tasks`, `mission_events` |

### 🎯 MERGE RECOMMENDATION for DB Schema:
Take Cline's 8 tables as base. Add Antigravity's `replay_metadata` (FR-85) and `deliverables` tables → **10 tables total**.

---

## 3. API Contract Comparison

### Cline (14 endpoints)

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/missions` | POST | Create mission |
| `/api/v1/missions` | GET | List missions (paginated) |
| `/api/v1/missions/{id}` | GET | Mission detail |
| `/api/v1/missions/{id}/start` | POST | Start execution |
| `/api/v1/missions/{id}/pause` | POST | Pause |
| `/api/v1/missions/{id}/resume` | POST | Resume |
| `/api/v1/missions/{id}/cancel` | POST | Cancel |
| `/api/v1/missions/{id}/approvals` | GET | List pending approvals |
| `/api/v1/approvals/{id}/approve` | POST | Approve action |
| `/api/v1/approvals/{id}/deny` | POST | Deny action |
| `/api/v1/missions/{id}/events/stream` | GET | SSE stream |
| `/api/v1/missions/{id}/events` | GET | Event history |
| `/api/v1/agents` | GET | List agents |
| `/api/v1/agents/{name}` | GET | Agent detail |
| `/api/v1/health` | GET | Health check |
| `/api/v1/metrics` | GET | Cost/usage metrics |

**Extras:** Full JSON request/response bodies, SSE format spec, error codes table, idempotency spec

### Antigravity
- Has stricter auth model with actor attribution
- Different endpoint naming conventions

### Codex
- Has API contract in `docs/02-architecture/api-contract.md`
- Content not fully extracted

### 🎯 MERGE RECOMMENDATION for API:
Cline's is most complete with full JSON specs. Add Antigravity's auth/attribution patterns.

---

## 4. Event Catalog Comparison

### Cline (30+ events, 8 categories)

| Category | Events |
|---|---|
| Mission | 8 (created, started, state_changed, paused, resumed, completed, failed, cancelled) |
| Planning | 2 (plan.created, plan.revised) |
| Agent Lifecycle | 6 (assigned, started, progress, thinking, completed, error) |
| Tool | 3 (called, result, error) |
| Approval | 4 (requested, granted, denied, expired) |
| Review | 3 (started, approved, rejected) |
| Cost | 3 (logged, budget_warning, budget_exceeded) |
| System | 4 (health, error, startup, shutdown) |

**Extras:** SSE bridge mapping, reconnect safety, 4 consumer groups

### Antigravity
- More concise event set
- Focus on critical path events

### Codex
- Has event catalog in `docs/02-architecture/umbrella-event-catalog.md`
- Content not fully extracted

### 🎯 MERGE RECOMMENDATION for Events:
Cline's is most comprehensive with 33 events and consumer groups. Use as base.

---

## 5. Contradictions & Conflicts

| Issue | Cline | Antigravity | Resolution |
|---|---|---|---|
| Table naming | `sub_tasks`, `agent_events` | `tasks`, `mission_events` | Use Cline's (more descriptive) |
| Observation plane name | "Observation" | "Event" | Use "Observation" (matches PRD) |
| HLD version | v1.1 | v1.2 | Merge to v2.0 |
| PRD reference | PRD-final.MD v1.2 | PRD-final.MD v1.2 | Aligned ✅ |
| Deliverables storage | JSONB on missions table | Separate `deliverables` table | Add separate table (cleaner) |

---

## 6. Final Merge Plan

### Recommended Canonical Set (v2.0)

1. **HLD:** Cline base + Antigravity's Rule-of-Two, cost-degradation, WASM, A2A/MCP
2. **DB Schema:** Cline's 8 tables + Antigravity's replay_metadata + deliverables = **10 tables**
3. **API Contract:** Cline's 14+ endpoints + Antigravity's auth patterns
4. **Event Catalog:** Cline's 33 events (superset of all)

### Location
```
docs/02-architecture/hld/synarch-hld.md      ← merged canonical
docs/05-data/master-db-schema.md              ← merged canonical
docs/02-architecture/api-contract.md          ← merged canonical
docs/02-architecture/umbrella-event-catalog.md ← merged canonical
```

Agent-specific versions preserved in `techDocs{Agent}/` for reference.
