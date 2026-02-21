# Synarch Master DB Schema (Canonical)

Version: 2.0
Date: 2026-02-21
Source of truth: /Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/01-requirements/PRD-final.MD

## 1. Scope

Canonical PostgreSQL schema for mission runtime, approvals, events, cost/eval telemetry, config, and memory lifecycle.

## 2. Design Decisions

1. Keep PRD/backend naming (`tasks`, `mission_events`, `authority_mode`, `status`).
2. Keep Cline-level completeness (cost logs, agent config, memory tables).
3. Add replay and eval structures for FR-45..FR-86.
4. Keep LangGraph checkpoint tables managed by checkpointer bootstrap.

## 3. Canonical DDL

```sql
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

CREATE TYPE mission_status AS ENUM (
  'created','planning','executing','awaiting_approval','reviewing','revising','synthesizing','paused','paused_awaiting_resources','failed','completed','cancelled'
);

CREATE TYPE task_status AS ENUM (
  'pending','in_progress','completed','failed','revision_needed'
);

CREATE TYPE approval_status AS ENUM (
  'pending','approved','rejected','timeout'
);

CREATE TYPE deliverable_review_status AS ENUM (
  'pending_review','approved','rejected','revision_required'
);

CREATE TYPE replay_status AS ENUM (
  'started','running','completed','failed','cancelled'
);

CREATE TYPE memory_type AS ENUM (
  'episodic','semantic','procedural','decision','user'
);

CREATE TABLE missions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  goal TEXT NOT NULL,
  authority_mode VARCHAR(20) NOT NULL DEFAULT 'supervised',
  status mission_status NOT NULL DEFAULT 'created',
  version INTEGER NOT NULL DEFAULT 1,
  current_branch VARCHAR(120),
  thread_id VARCHAR(96),
  confidence_score NUMERIC(5,4),
  cost_budget_usd NUMERIC(12,6),
  mission_cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
  token_usage_total BIGINT NOT NULL DEFAULT 0,
  created_by VARCHAR(255) DEFAULT 'god',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  CONSTRAINT missions_authority_mode_chk CHECK (authority_mode IN ('guided','supervised','free_rein'))
);

CREATE UNIQUE INDEX ux_missions_thread_id ON missions(thread_id) WHERE thread_id IS NOT NULL;
CREATE INDEX ix_missions_status ON missions(status);
CREATE INDEX ix_missions_created_at ON missions(created_at DESC);
CREATE INDEX ix_missions_active_created_at ON missions(created_at DESC) WHERE deleted_at IS NULL;

-- Sidecar table for large JSON payloads to prevent TOAST bloat
CREATE TABLE mission_payloads (
  mission_id UUID PRIMARY KEY REFERENCES missions(id) ON DELETE CASCADE,
  constraints JSONB NOT NULL DEFAULT '{}'::jsonb,
  budget_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
  plan JSONB,
  error_context JSONB
);

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  parent_task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  sequence INTEGER,
  assigned_agent VARCHAR(40) NOT NULL,
  description TEXT NOT NULL,
  status task_status NOT NULL DEFAULT 'pending',
  priority INTEGER NOT NULL DEFAULT 0,
  retry_count INTEGER NOT NULL DEFAULT 0,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (mission_id, sequence)
);

CREATE INDEX ix_tasks_mission_id ON tasks(mission_id);
CREATE INDEX ix_tasks_status ON tasks(status);
CREATE INDEX ix_tasks_assigned_agent ON tasks(assigned_agent);
CREATE INDEX ix_tasks_created_at ON tasks(created_at DESC);

-- Sidecar table for large task payloads
CREATE TABLE task_payloads (
  task_id UUID PRIMARY KEY REFERENCES tasks(id) ON DELETE CASCADE,
  inputs JSONB,
  result JSONB
);

CREATE TABLE deliverables (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  agent VARCHAR(40) NOT NULL,
  type VARCHAR(40) NOT NULL,
  content JSONB NOT NULL,
  review_status deliverable_review_status NOT NULL DEFAULT 'pending_review',
  eval_score NUMERIC(5,4),
  eval_metadata JSONB,
  provenance_refs JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_deliverables_mission_id ON deliverables(mission_id);
CREATE INDEX ix_deliverables_task_id ON deliverables(task_id);
CREATE INDEX ix_deliverables_eval_score ON deliverables(eval_score) WHERE eval_score IS NOT NULL;

CREATE TABLE approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  action_type VARCHAR(64) NOT NULL,
  requested_by VARCHAR(40) NOT NULL,
  description TEXT NOT NULL,
  risk_level VARCHAR(12) NOT NULL,
  status approval_status NOT NULL DEFAULT 'pending',
  version INTEGER NOT NULL DEFAULT 1,
  timeout_seconds INTEGER NOT NULL DEFAULT 300,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  decided_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  decided_by VARCHAR(120),
  decided_by_session VARCHAR(120),
  decided_by_device VARCHAR(200),
  decision_reason TEXT,
  checkpoint_id TEXT,
  interrupt_node VARCHAR(120),
  CONSTRAINT approvals_risk_level_chk CHECK (risk_level IN ('low','medium','high','critical'))
);

CREATE INDEX ix_approvals_mission_id ON approvals(mission_id);
CREATE INDEX ix_approvals_status ON approvals(status);
CREATE INDEX ix_approvals_pending_requested_at ON approvals(requested_at) WHERE status = 'pending';

CREATE TABLE mission_events (
  id BIGSERIAL PRIMARY KEY,
  event_id UUID NOT NULL,
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
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
  cost_usd NUMERIC(12,6),
  token_count BIGINT,
  latency_ms INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX ux_mission_events_event_id ON mission_events(event_id);
CREATE UNIQUE INDEX ux_mission_events_mission_sequence ON mission_events(mission_id, sequence);
CREATE INDEX ix_mission_events_subject ON mission_events(subject);
CREATE INDEX ix_mission_events_created_at ON mission_events(created_at DESC);
CREATE INDEX ix_mission_events_idempotency_key ON mission_events(idempotency_key) WHERE idempotency_key IS NOT NULL;

CREATE TABLE mission_sequence_counters (
  mission_id UUID PRIMARY KEY REFERENCES missions(id) ON DELETE CASCADE,
  next_sequence BIGINT NOT NULL DEFAULT 1,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION next_mission_sequence(p_mission_id UUID) RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
  v_next BIGINT;
BEGIN
  INSERT INTO mission_sequence_counters (mission_id, next_sequence)
  VALUES (p_mission_id, 2)
  ON CONFLICT (mission_id) DO UPDATE
    SET next_sequence = mission_sequence_counters.next_sequence + 1,
        updated_at = NOW()
  RETURNING next_sequence - 1 INTO v_next;
  RETURN v_next;
END;
$$;

CREATE TABLE mission_event_outbox (
  id BIGSERIAL PRIMARY KEY,
  event_id UUID NOT NULL UNIQUE,
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  subject VARCHAR(240) NOT NULL,
  payload JSONB NOT NULL,
  headers JSONB NOT NULL DEFAULT '{}'::jsonb,
  publish_attempts INTEGER NOT NULL DEFAULT 0,
  available_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  published_at TIMESTAMPTZ,
  dead_lettered_at TIMESTAMPTZ,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_outbox_ready ON mission_event_outbox(available_at) WHERE published_at IS NULL AND dead_lettered_at IS NULL;
CREATE INDEX ix_outbox_mission_id ON mission_event_outbox(mission_id);

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

CREATE TABLE cost_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
  agent VARCHAR(40) NOT NULL,
  model VARCHAR(120) NOT NULL,
  provider VARCHAR(60) NOT NULL,
  prompt_tokens INTEGER NOT NULL DEFAULT 0,
  completion_tokens INTEGER NOT NULL DEFAULT 0,
  total_tokens INTEGER NOT NULL DEFAULT 0,
  cost_usd NUMERIC(12,6) NOT NULL DEFAULT 0,
  latency_ms INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_cost_logs_mission_id ON cost_logs(mission_id);
CREATE INDEX ix_cost_logs_created_at ON cost_logs(created_at DESC);

CREATE TABLE agent_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(50) NOT NULL UNIQUE,
  display_name VARCHAR(100) NOT NULL,
  tier INTEGER NOT NULL,
  role TEXT NOT NULL,
  source_type VARCHAR(24) NOT NULL DEFAULT 'soul',
  source_path TEXT,
  model_default VARCHAR(120) NOT NULL,
  model_fallback VARCHAR(120),
  temperature NUMERIC(3,2) DEFAULT 0.0,
  max_iterations INTEGER DEFAULT 10,
  tools JSONB NOT NULL DEFAULT '[]'::jsonb,
  permissions JSONB NOT NULL DEFAULT '{}'::jsonb,
  enabled BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID REFERENCES missions(id) ON DELETE SET NULL,
  agent VARCHAR(40) NOT NULL,
  memory_type memory_type NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  importance NUMERIC(4,3) DEFAULT 0.5,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  archived_at TIMESTAMPTZ,
  CONSTRAINT memories_content_size_chk CHECK (length(content) <= 32000)
);

CREATE INDEX ix_memories_agent_type ON memories(agent, memory_type);
CREATE INDEX ix_memories_expires_at ON memories(expires_at);
-- Create the vector index for fast semantic search similarity queries
CREATE INDEX ix_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops);

CREATE TABLE replay_metadata (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  mission_id UUID NOT NULL REFERENCES missions(id) ON DELETE CASCADE,
  replay_from_sequence BIGINT NOT NULL,
  replay_to_sequence BIGINT,
  checkpoint_ref TEXT,
  status replay_status NOT NULL DEFAULT 'started',
  result JSONB,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

CREATE INDEX ix_replay_metadata_mission_id ON replay_metadata(mission_id);
CREATE INDEX ix_replay_metadata_status ON replay_metadata(status);

-- JSONB query acceleration for common filter paths
CREATE INDEX ix_mission_payloads_constraints_gin ON mission_payloads USING gin (constraints);
CREATE INDEX ix_mission_payloads_budget_policy_gin ON mission_payloads USING gin (budget_policy);
CREATE INDEX ix_mission_payloads_plan_gin ON mission_payloads USING gin (plan);
CREATE INDEX ix_task_payloads_inputs_gin ON task_payloads USING gin (inputs);
CREATE INDEX ix_task_payloads_result_gin ON task_payloads USING gin (result);
CREATE INDEX ix_deliverables_content_gin ON deliverables USING gin (content);
CREATE INDEX ix_deliverables_eval_metadata_gin ON deliverables USING gin (eval_metadata);
CREATE INDEX ix_mission_events_payload_gin ON mission_events USING gin (payload);

-- Referential integrity for agent identity-bearing columns
ALTER TABLE tasks
  ADD CONSTRAINT fk_tasks_assigned_agent
  FOREIGN KEY (assigned_agent) REFERENCES agent_configs(name)
  ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE deliverables
  ADD CONSTRAINT fk_deliverables_agent
  FOREIGN KEY (agent) REFERENCES agent_configs(name)
  ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE cost_logs
  ADD CONSTRAINT fk_cost_logs_agent
  FOREIGN KEY (agent) REFERENCES agent_configs(name)
  ON UPDATE CASCADE ON DELETE RESTRICT;

ALTER TABLE mission_events
  ADD CONSTRAINT fk_mission_events_agent
  FOREIGN KEY (agent) REFERENCES agent_configs(name)
  ON UPDATE CASCADE ON DELETE SET NULL;

ALTER TABLE memories
  ADD CONSTRAINT fk_memories_agent
  FOREIGN KEY (agent) REFERENCES agent_configs(name)
  ON UPDATE CASCADE ON DELETE RESTRICT;

-- Automatic updated_at maintenance
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

CREATE TRIGGER trg_missions_updated_at
BEFORE UPDATE ON missions
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_deliverables_updated_at
BEFORE UPDATE ON deliverables
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_approvals_updated_at
BEFORE UPDATE ON approvals
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_agent_configs_updated_at
BEFORE UPDATE ON agent_configs
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

## 4. LangGraph Checkpointer Contract

1. checkpointer tables are bootstrapped by runtime (`setup`).
2. `missions.thread_id` maps to graph thread id and must be assigned before first graph checkpoint write.
3. restart recovery is invalid if checkpoint continuity is broken.
4. checkpoint orphan reconciliation job must remove checkpoint rows for hard-deleted missions.

## 5. Migration Governance

Per schema change PR:
1. add numbered migration under backend migrations path
2. include rollback notes
3. include backfill strategy for non-null additions
4. evaluate monthly partitions for `mission_events` in a dedicated migration plan
5. update this master schema doc
6. update integration tests for affected repositories
7. optimistic-lock update patterns must be documented for tables with `version` columns.
8. validate restore procedure against `/Users/praxlannister/Documents/workspace/synarch-ai/synarch-engine/docs/02-architecture/backup-restore-runbook.md`

## 6. Retention and Safety Rules

1. `mission_events` append-only.
2. terminal approval decisions immutable.
3. replay retention must satisfy FR-85 debugging requirements.
4. idempotency records must expire by policy but remain auditable within TTL window.
5. outbox rows are immutable after `published_at` except dead-letter metadata.
6. outbox workers must implement exponential backoff + terminal dead-letter policy.
7. missions use soft delete by default (`deleted_at`); hard delete requires explicit admin workflow.
8. memory lifecycle job enforces per-agent caps and archives low-importance stale rows.

## 7. Mission Events Partition Rollout Strategy

1. retain current non-partitioned table for Phase 0-1.
2. at first sustained-write threshold, migrate to range partitions by `created_at` (monthly).
3. move unique guarantees to partition-compatible model:
- global uniqueness by `event_id` (application-level UUID + partition-local unique index)
- mission-local ordering by `(mission_id, sequence)` with allocator enforcement.
4. enforce retention with rolling archive/drop policy per closed partition.

## 8. FR Mapping

- durability and runtime closure: FR-2, FR-5, FR-10, FR-75
- approvals and governance: FR-21..FR-25, FR-77, FR-79
- event/replay: FR-18..FR-20, FR-76, FR-85
- idempotency/audit: FR-14, FR-42, FR-78
- cost/eval/slo: FR-45..FR-49, FR-58, FR-74, FR-86
- config/memory/protocol readiness support: FR-57, FR-59..FR-67, FR-84
