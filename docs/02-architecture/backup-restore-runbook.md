# Synarch Backup and Restore Runbook

Version: 1.0
Date: 2026-02-21
Scope: PostgreSQL mission runtime data + checkpoint consistency

## 1. Backup Policy

1. Daily full backup of PostgreSQL with 30-day retention.
2. 15-minute WAL archival for point-in-time recovery.
3. Weekly restore drill into isolated environment.
4. Backup encryption at rest and in transit.

## 2. Backup Procedure

1. Verify DB health (`ok` or `degraded`, never `down`).
2. Run `pg_dump` for logical full snapshot.
3. Archive WAL segments for PITR window.
4. Record backup manifest with:
- timestamp
- schema migration version
- git SHA
- WAL range

## 3. Restore Procedure

1. Restore latest full snapshot to recovery instance.
2. Replay WAL to target timestamp/LSN.
3. Run consistency checks:
- mission count parity
- approval pending count parity
- outbox unpublished rows parity
- checkpoint continuity checks (`thread_id` mapping)
4. Promote recovery instance only after checks pass.

## 4. Post-Restore Verification

1. Run mission state API smoke checks.
2. Run approval timeout sweeper dry-run.
3. Validate SSE replay from recent `Last-Event-ID`.
4. Run a replay job from checkpoint to confirm FR-85 behavior.

## 5. Failure Handling

1. If checkpoint continuity fails, keep service read-only and perform checkpoint reconciliation.
2. If outbox parity fails, replay unpublished outbox rows before opening write traffic.
3. If mission/version mismatch is detected, block state transitions until reconciled.
