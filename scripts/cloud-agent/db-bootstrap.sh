#!/usr/bin/env bash
#
# Synarch Engine — PostgreSQL bootstrap (idempotent).
#
# Ensures the local PostgreSQL cluster is running, the `synarch` role and
# database exist, and the schema migrations have been applied exactly once.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PG_VERSION=16
DB_NAME=synarch
DB_USER=synarch
DB_PASS=synarch_local
MIGRATIONS="$REPO_ROOT/backend/adapters/postgres/migrations"

log() { printf '\033[1;33m[db-bootstrap]\033[0m %s\n' "$*"; }

# Ensure the cluster is online (needed to run psql).
if ! sudo pg_lsclusters -h 2>/dev/null | awk '{print $4}' | grep -q online; then
  log "Starting PostgreSQL ${PG_VERSION} cluster"
  sudo pg_ctlcluster "${PG_VERSION}" main start || true
  sleep 2
fi

# Create role (superuser for local dev parity with docker-compose image).
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN SUPERUSER PASSWORD '${DB_PASS}';
  END IF;
END \$\$;
SQL

# Create database if missing.
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
  log "Creating database ${DB_NAME}"
  sudo -u postgres createdb -O "${DB_USER}" "${DB_NAME}"
fi

# Apply migrations once (guard on presence of the core 'missions' table).
export PGPASSWORD="${DB_PASS}"
if psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -tAc \
    "SELECT to_regclass('public.missions')" | grep -q missions; then
  log "Schema already present; skipping migrations."
else
  log "Applying migrations"
  for f in "${MIGRATIONS}"/*.sql; do
    log "  -> $(basename "$f")"
    psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 -f "$f"
  done
fi

log "Database ready."
