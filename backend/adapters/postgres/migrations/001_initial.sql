-- Synarch Engine: Initial schema (from PRD §9.2)
-- Run: psql $DATABASE_URL -f 001_initial.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Missions
CREATE TABLE IF NOT EXISTS missions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    goal            TEXT NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'CREATED',
    authority_mode  VARCHAR(20) NOT NULL DEFAULT 'supervised',
    plan            JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_context   JSONB,
    thread_id       VARCHAR(64),
    CONSTRAINT valid_status CHECK (status IN (
        'CREATED','PLANNING','EXECUTING','AWAITING_APPROVAL',
        'REVIEWING','REVISING','SYNTHESIZING',
        'COMPLETED','PAUSED','CANCELLED','FAILED'
    ))
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    parent_task_id  UUID REFERENCES tasks(id),
    assigned_agent  VARCHAR(30) NOT NULL,
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority        INTEGER DEFAULT 0,
    inputs          JSONB,
    result          JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    CONSTRAINT valid_task_status CHECK (status IN (
        'PENDING','IN_PROGRESS','COMPLETED','FAILED','REVISION_NEEDED'
    ))
);

-- Deliverables
CREATE TABLE IF NOT EXISTS deliverables (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    task_id         UUID REFERENCES tasks(id),
    agent           VARCHAR(30) NOT NULL,
    type            VARCHAR(30) NOT NULL,
    content         JSONB NOT NULL,
    review_status   VARCHAR(20) DEFAULT 'PENDING_REVIEW',
    provenance_refs JSONB DEFAULT '[]',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Approvals (FR-21 to FR-25)
CREATE TABLE IF NOT EXISTS approvals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mission_id      UUID NOT NULL REFERENCES missions(id),
    action_type     VARCHAR(30) NOT NULL,
    requested_by    VARCHAR(30) NOT NULL,
    description     TEXT NOT NULL,
    risk_level      VARCHAR(10) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    decided_by      VARCHAR(30),
    decision_reason TEXT,
    timeout_seconds INTEGER DEFAULT 300,
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at      TIMESTAMPTZ
);

-- Mission Events (audit trail + outbox)
CREATE TABLE IF NOT EXISTS mission_events (
    id              BIGSERIAL PRIMARY KEY,
    mission_id      UUID NOT NULL REFERENCES missions(id),
    event_type      VARCHAR(60) NOT NULL,
    agent           VARCHAR(30),
    payload         JSONB NOT NULL,
    idempotency_key VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_tasks_mission ON tasks(mission_id);
CREATE INDEX IF NOT EXISTS idx_deliverables_mission ON deliverables(mission_id);
CREATE INDEX IF NOT EXISTS idx_approvals_mission ON approvals(mission_id);
CREATE INDEX IF NOT EXISTS idx_events_mission ON mission_events(mission_id);
CREATE INDEX IF NOT EXISTS idx_events_idempotency ON mission_events(idempotency_key) WHERE idempotency_key IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_events_created ON mission_events(created_at);
