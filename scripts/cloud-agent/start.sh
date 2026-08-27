#!/usr/bin/env bash
#
# Synarch Engine — Cloud Agent start phase (per-boot, idempotent).
#
# Brings up the infrastructure daemons required by the backend:
#   - PostgreSQL 16 (cluster)
#   - Redis
#   - NATS JetStream
#
# Application dev servers (FastAPI, Next.js) run as visible `terminals`, not here.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PG_VERSION=16

log() { printf '\033[1;33m[start]\033[0m %s\n' "$*"; }

# --- PostgreSQL -----------------------------------------------------------
if ! sudo pg_lsclusters -h 2>/dev/null | awk '{print $4}' | grep -q online; then
  log "Starting PostgreSQL ${PG_VERSION}"
  sudo pg_ctlcluster "${PG_VERSION}" main start || true
else
  log "PostgreSQL already running."
fi

# --- Redis ----------------------------------------------------------------
if ! redis-cli ping >/dev/null 2>&1; then
  log "Starting Redis"
  sudo redis-server /etc/redis/redis.conf --daemonize yes
else
  log "Redis already running."
fi

# --- NATS -----------------------------------------------------------------
if ! curl -fsS http://localhost:8222/varz >/dev/null 2>&1; then
  log "Starting NATS JetStream"
  nohup nats-server -js -m 8222 > /tmp/nats-server.log 2>&1 &
else
  log "NATS already running."
fi

# --- Readiness ------------------------------------------------------------
for _ in $(seq 1 30); do
  if pg_isready -h localhost -p 5432 -U synarch >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

log "Infrastructure ready (PostgreSQL:5432, Redis:6379, NATS:4222/8222)."
