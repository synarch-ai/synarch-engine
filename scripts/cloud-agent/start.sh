#!/usr/bin/env bash
#
# Synarch Engine — Cloud Agent start phase (per-boot, idempotent).
#
# Brings up everything an agent needs on each container start:
#   - Infrastructure daemons: PostgreSQL 16, Redis, NATS JetStream
#   - Application dev servers: FastAPI backend (:8000), Next.js Mission Control (:3000)
#
# All processes are launched in the background and logged under /tmp so the
# command returns promptly. Safe to run repeatedly (guards on running services).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PG_VERSION=16

log() { printf '\033[1;33m[start]\033[0m %s\n' "$*"; }

cd "$REPO_ROOT"

# --- Restore install artifacts if a fresh checkout wiped them --------------
# Cloud Agent boots re-checkout the repo, removing untracked files such as
# backend/.venv, apps/web/node_modules, and the .env.local files. Recreate
# them idempotently before launching anything.
if [ ! -d backend/.venv ] || [ ! -d apps/web/node_modules ] \
   || [ ! -f backend/.env.local ] || [ ! -f apps/web/.env.local ]; then
  log "Install artifacts missing (fresh checkout) — running install.sh"
  bash "$REPO_ROOT/scripts/cloud-agent/install.sh"
fi

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

# --- Wait for PostgreSQL readiness ----------------------------------------
for _ in $(seq 1 30); do
  pg_isready -h localhost -p 5432 -U synarch >/dev/null 2>&1 && break
  sleep 1
done

# --- Backend API (FastAPI / uvicorn, :8000) -------------------------------
if ! curl -fsS http://localhost:8000/api/v1/health >/dev/null 2>&1; then
  log "Starting Synarch backend on :8000"
  nohup bash -c "cd '${REPO_ROOT}/backend' && source .venv/bin/activate && exec uvicorn main:app --host 0.0.0.0 --port 8000" \
    > /tmp/synarch-backend.log 2>&1 &
else
  log "Backend already running."
fi

# --- Web Mission Control (Next.js, :3000) ---------------------------------
if ! curl -fsS http://localhost:3000 >/dev/null 2>&1; then
  log "Starting Mission Control web on :3000"
  nohup bash -c "cd '${REPO_ROOT}/apps/web' && exec npm run dev" \
    > /tmp/synarch-web.log 2>&1 &
else
  log "Web already running."
fi

log "Startup dispatched (PostgreSQL:5432, Redis:6379, NATS:4222/8222, API:8000, Web:3000)."
