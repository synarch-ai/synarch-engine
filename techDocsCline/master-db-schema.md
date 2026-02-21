# Synarch Engine — Master Database Schema

**Version:** 1.0 | **Author:** Cline (Backend-PE) | **Date:** 2026-02-21
**Database:** PostgreSQL 16 | **ORM:** SQLAlchemy 2.0 (async) + Alembic migrations

---

## Schema Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  missions   │────<│  sub_tasks   │     │  agent_events   │
│             │     │              │     │  (audit log)    │
└──────┬──────┘     └──────────────┘     └─────────────────┘
       │
       │ 1:N
       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  approvals  │     │ checkpoints  │     │  agent_configs  │
│             │     │ (LangGraph)  │     │  (soul.md meta) │
└─────────────┘     └──────────────┘     └─────────────────┘
       
┌─────────────┐     ┌──────────────┐
│  cost_logs  │     │  memories    │
│ (per-call)  │     │ (long-term)  │
└─────────────┘     └──────────────┘
```

---

## Table: `missions`

The central entity. Every mission gets a durable record.

```sql
CREATE TABLE missions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal            TEXT NOT NULL,
    mode            VARCHAR(20) NOT NULL DEFAULT 'supervised'
                    CHECK (mode IN ('autopilot', 'supervised', 'manual')),
    state           VARCHAR(30) NOT NULL DEFAULT 'created'
                    CHECK (state IN (
                        'created', 'planning', 'executing',
                        'awaiting_approval', 'reviewing', 'revising',
                        'synthesizing', 'paused', 'failed',
                        'completed', 'cancelled'
                    )),
    constraints     JSONB DEFAULT '{}',
    plan            JSONB DEFAULT '[]',        -- Array of sub-task definitions
    result          JSONB,                      -- Final synthesized output
    error           TEXT,                       -- Error message if failed
    cost_usd        NUMERIC(10, 6) DEFAULT 0,  -- Cumulative cost
    token_count     INTEGER DEFAULT 0,          -- Cumulative tokens
    created_by      VARCHAR(255) DEFAULT 'god', -- Actor attribution
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    
    -- Thread context for LangGraph
    thread_id       UUID UNIQUE DEFAULT gen_random_uuid()
);

CREATE INDEX idx_missions_state ON missions(state);
CREATE INDEX idx_missions_created_at ON missions(created_at DESC);
CREATE INDEX idx_missions_thread_id ON missions(thread_id);
```

---

## Table: `sub_tasks`

Individual work items within a mission, assigned to agents.

```sql
CREATE TABLE sub_tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    sequence        INTEGER NOT NULL,           -- Execution order
    title           TEXT NOT NULL,
    description     TEXT,
    assigned_agent  VARCHAR(50) NOT NULL
                    CHECK (assigned_agent IN ('zeus', 'thoth', 'hephaestus', 'hermes', 'janus', 'synarch')),
    state           VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (state IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    input           JSONB DEFAULT '{}',         -- Input context for agent
    output          JSONB,                      -- Agent's result
    error           TEXT,
    cost_usd        NUMERIC(10, 6) DEFAULT 0,
    token_count     INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(mission_id, sequence)
);

CREATE INDEX idx_sub_tasks_mission ON sub_tasks(mission_id);
CREATE INDEX idx_sub_tasks_state ON sub_tasks(state);
```

---

## Table: `agent_events`

Immutable audit log of every agent action. Published to NATS, persisted here.

```sql
CREATE TABLE agent_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      VARCHAR(100) NOT NULL,      -- e.g. 'agent.started', 'tool.called'
    mission_id      UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    sub_task_id     UUID REFERENCES sub_tasks(id),
    agent_name      VARCHAR(50) NOT NULL,
    correlation_id  UUID NOT NULL,              -- Links related events
    payload         JSONB NOT NULL DEFAULT '{}',
    cost_usd        NUMERIC(10, 6) DEFAULT 0,
    token_count     INTEGER DEFAULT 0,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version         VARCHAR(10) NOT NULL DEFAULT '1.0'
);

CREATE INDEX idx_events_mission ON agent_events(mission_id);
CREATE INDEX idx_events_correlation ON agent_events(correlation_id);
CREATE INDEX idx_events_type ON agent_events(event_type);
CREATE INDEX idx_events_timestamp ON agent_events(timestamp DESC);
-- For time-range queries on audit log
CREATE INDEX idx_events_mission_time ON agent_events(mission_id, timestamp DESC);
```

---

## Table: `approvals`

Human-in-the-loop approval records (FR-8, FR-15, FR-77).

```sql
CREATE TABLE approvals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    sub_task_id     UUID REFERENCES sub_tasks(id),
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'approved', 'denied', 'expired')),
    context         JSONB NOT NULL DEFAULT '{}', -- What's being approved
    decision_by     VARCHAR(255),                -- Who approved/denied
    reason          TEXT,                        -- Optional explanation
    
    -- LangGraph interrupt metadata
    checkpoint_id   TEXT,                        -- LangGraph checkpoint to resume from
    interrupt_node  VARCHAR(100)                 -- Which graph node was interrupted
);

CREATE INDEX idx_approvals_mission ON approvals(mission_id);
CREATE INDEX idx_approvals_status ON approvals(status);
```

---

## Table: `checkpoints`

LangGraph checkpoint storage (FR-10). Uses LangGraph's PostgreSQL checkpointer format.

```sql
-- This table is managed by langgraph-checkpoint-postgres
-- Schema follows LangGraph's checkpoint protocol
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id       UUID NOT NULL,
    checkpoint_ns   TEXT NOT NULL DEFAULT '',
    checkpoint_id   TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type            TEXT,
    checkpoint      JSONB NOT NULL,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id       UUID NOT NULL,
    checkpoint_ns   TEXT NOT NULL DEFAULT '',
    checkpoint_id   TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    idx             INTEGER NOT NULL,
    channel         TEXT NOT NULL,
    type            TEXT,
    value           JSONB,
    
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);
```

---

## Table: `cost_logs`

Per-LLM-call cost tracking (FR-47).

```sql
CREATE TABLE cost_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
    sub_task_id     UUID REFERENCES sub_tasks(id),
    agent_name      VARCHAR(50) NOT NULL,
    model           VARCHAR(100) NOT NULL,       -- e.g. 'claude-sonnet-4-20250514'
    provider        VARCHAR(50) NOT NULL,        -- e.g. 'anthropic', 'openai'
    prompt_tokens   INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens    INTEGER NOT NULL DEFAULT 0,
    cost_usd        NUMERIC(10, 6) NOT NULL DEFAULT 0,
    latency_ms      INTEGER,                     -- Response time
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_costs_mission ON cost_logs(mission_id);
CREATE INDEX idx_costs_agent ON cost_logs(agent_name);
CREATE INDEX idx_costs_model ON cost_logs(model);
CREATE INDEX idx_costs_timestamp ON cost_logs(timestamp DESC);
```

---

## Table: `agent_configs`

Agent configuration metadata (FR-65). Stores YAML-derived config.

```sql
CREATE TABLE agent_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(50) NOT NULL UNIQUE,  -- e.g. 'zeus', 'thoth'
    display_name    VARCHAR(100) NOT NULL,
    role            TEXT NOT NULL,
    soul_md_path    TEXT NOT NULL,                 -- Path to soul.md file
    model_default   VARCHAR(100) NOT NULL,         -- Default model
    model_fallback  VARCHAR(100),                  -- Fallback model
    temperature     NUMERIC(3, 2) DEFAULT 0.0,
    max_iterations  INTEGER DEFAULT 10,
    tools           JSONB DEFAULT '[]',            -- Enabled tool names
    permissions     JSONB DEFAULT '{}',            -- Permission matrix
    enabled         BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Table: `memories`

Agent long-term memory storage (FR-59, FR-60).

```sql
CREATE TABLE memories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name      VARCHAR(50) NOT NULL,
    memory_type     VARCHAR(30) NOT NULL
                    CHECK (memory_type IN ('episodic', 'semantic', 'procedural', 'user')),
    content         TEXT NOT NULL,
    metadata        JSONB DEFAULT '{}',
    importance      NUMERIC(3, 2) DEFAULT 0.5,   -- 0.0 to 1.0
    expires_at      TIMESTAMPTZ,                  -- TTL (FR-60)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_memories_agent ON memories(agent_name);
CREATE INDEX idx_memories_type ON memories(memory_type);
CREATE INDEX idx_memories_importance ON memories(importance DESC);
CREATE INDEX idx_memories_expires ON memories(expires_at) WHERE expires_at IS NOT NULL;
```

---

## Migration Strategy

```
migrations/
├── 001_create_missions.sql
├── 002_create_sub_tasks.sql
├── 003_create_agent_events.sql
├── 004_create_approvals.sql
├── 005_create_checkpoints.sql    (LangGraph managed)
├── 006_create_cost_logs.sql
├── 007_create_agent_configs.sql
├── 008_create_memories.sql
└── 009_seed_agent_configs.sql    (Insert default agent definitions)
```

All migrations are **idempotent** (IF NOT EXISTS), **reversible** (with DOWN scripts), and run via Alembic.

---

*This schema is the single source of truth for all PostgreSQL tables. Per-issue migrations reference specific tables and add columns/indexes as needed.*
