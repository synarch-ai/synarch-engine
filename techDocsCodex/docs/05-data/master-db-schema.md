# Synarch Master Database Schema (Umbrella Constitution)

Status: Authoritative Level-1 Master Doc (Create Once)
Source baseline: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD (v1.2)
Last updated: 2026-02-21

## 1. Scope

Defines canonical PostgreSQL schema for:
- missions
- tasks
- deliverables
- approvals
- mission_events
- idempotency records
- replay metadata

LangGraph checkpoint tables are managed by AsyncPostgresSaver bootstrap and are part of the same DB durability boundary.

## 2. Global Rules

1. PostgreSQL 15+.
2. `TIMESTAMPTZ` for all timestamps.
3. UUID primary keys for control-plane entities.
4. Enumerated status constraints (no free-form states).
5. All foreign keys explicit; cascade behavior intentional.
6. Schema changes must be migration-based only.

## 3. Canonical DDL

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Mission lifecycle status
CREATE TYPE mission_status AS ENUM (
  'created',
  'planning',
  'executing',
  'awaiting_approval',
  'reviewing',
  'revising',
  'synthesizing',
  'paused',
  'failed',
  'completed',
  'cancelled'
);

-- Task status
CREATE TYPE task_status AS ENUM (
  'pending',
  'in_progress',
  'completed',
  'failed',
  'revision_needed'
);

-- Approval status
CREATE TYPE approval_status AS ENUM (
  'pending',
  'approved',
  'rejected',
  'timeout'
);

CREATE TABLE missions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  goal TEXT NOT NULL,
  authority_mode VARCHAR(20) NOT NULL DEFAULT 'supervised',
  status mission_status NOT NULL DEFAULT 'created',
  plan JSONB,
  current_branch VARCHAR(120),
  thread_id VARCHAR(96) NOT NULL,
  confidence_score NUMERIC(5,4),
  mission_cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
  token_usage_total BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  error_context JSONB,
  CONSTRAINT missions_authority_mode_chk CHECK (authority_mode IN ('guided', 'supervised', 'free_rein'))
);

CREATE UNIQUE INDEX ux_missions_thread_id ON missions(thread_id);
CREATE INDEX ix_missions_status ON missions(status);
CREATE INDEX ix_missions_created_at ON missions(created_at DESC);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  assigned_agent VARCHAR(40) NOT NULL,
  description TEXT NOT NULL,
  status task_status NOT NULL DEFAULT 'pending',
  priority INTEGER NOT NULL DEFAULT 0,
  inputs JSONB,
  result JSONB,
  retry_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX ix_tasks_mission_id ON tasks(mission_id);
CREATE INDEX ix_tasks_status ON tasks(status);
CREATE INDEX ix_tasks_assigned_agent ON tasks(assigned_agent);

CREATE TABLE deliverables (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  agent VARCHAR(40) NOT NULL,
  type VARCHAR(40) NOT NULL,
  content JSONB NOT NULL,
  review_status VARCHAR(24) NOT NULL DEFAULT 'pending_review',
  provenance_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_deliverables_mission_id ON deliverables(mission_id);
CREATE INDEX ix_deliverables_task_id ON deliverables(task_id);

CREATE TABLE approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  action_type VARCHAR(64) NOT NULL,
  requested_by VARCHAR(40) NOT NULL,
  description TEXT NOT NULL,
  risk_level VARCHAR(12) NOT NULL,
  status approval_status NOT NULL DEFAULT 'pending',
  timeout_seconds INTEGER NOT NULL DEFAULT 300,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  decided_at TIMESTAMPTZ,
  decided_by VARCHAR(120),
  decided_by_session VARCHAR(120),
  decided_by_device VARCHAR(200),
  decision_reason TEXT,
  CONSTRAINT approvals_risk_level_chk CHECK (risk_level IN ('low', 'medium', 'high', 'critical'))
);

CREATE INDEX ix_approvals_mission_id ON approvals(mission_id);
CREATE INDEX ix_approvals_status ON approvals(status);

CREATE TABLE mission_events (
  id BIGSERIAL PRIMARY KEY,
  event_id UUID NOT NULL,
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  sequence BIGINT NOT NULL,
  event_type VARCHAR(120) NOT NULL,
  subject VARCHAR(240) NOT NULL,
  stage VARCHAR(64),
  agent VARCHAR(40),
  schema_version VARCHAR(24) NOT NULL,
  correlation_id UUID,
  causation_id UUID,
  idempotency_key VARCHAR(96),
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX ux_mission_events_event_id ON mission_events(event_id);
CREATE UNIQUE INDEX ux_mission_events_mission_sequence ON mission_events(mission_id, sequence);
CREATE INDEX ix_mission_events_subject ON mission_events(subject);
CREATE INDEX ix_mission_events_created_at ON mission_events(created_at DESC);
CREATE INDEX ix_mission_events_idempotency_key ON mission_events(idempotency_key) WHERE idempotency_key IS NOT NULL;

CREATE TABLE idempotency_records (
  id BIGSERIAL PRIMARY KEY,
  scope VARCHAR(64) NOT NULL,
  idempotency_key VARCHAR(96) NOT NULL,
  request_hash VARCHAR(128) NOT NULL,
  response_status INTEGER NOT NULL,
  response_body JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,
  UNIQUE (scope, idempotency_key)
);

CREATE INDEX ix_idempotency_expires_at ON idempotency_records(expires_at);

CREATE TABLE mission_replay_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  replay_from_sequence BIGINT NOT NULL,
  replay_to_sequence BIGINT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  result JSONB
);

CREATE INDEX ix_replay_runs_mission_id ON mission_replay_runs(mission_id);
```

## 4. Checkpointer Contract

1. LangGraph checkpointer tables are initialized by runtime bootstrap.
2. `missions.thread_id` must map to LangGraph configurable thread id.
3. Runtime is invalid if mission row exists without checkpointer continuity.

## 5. Migration Governance (Delta-Only)

For each issue mini-spec:
1. create new numbered migration file
2. include backward-compatible step sequence
3. include rollback strategy
4. include data backfill when adding non-null columns
5. update this master schema document after migration merge

## 6. Query and Retention Rules

1. `mission_events` is append-only.
2. approval decisions are immutable after terminal decision state.
3. retention and archival policy must preserve replay fidelity for FR-85.

## 7. FR Mapping

- Runtime durability: FR-2, FR-5, FR-10, FR-75
- Approvals and governance: FR-21..FR-25, FR-77, FR-79
- Events and replay: FR-18..FR-20, FR-76, FR-85
- Idempotency and safety: FR-14, FR-42, FR-78
- Cost and telemetry persistence: FR-47, FR-58, FR-74, FR-86
