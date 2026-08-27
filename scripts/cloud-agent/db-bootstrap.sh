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

# Apply pending migrations individually (tracked in schema_migrations).
export PGPASSWORD="${DB_PASS}"

psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
  filename TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SQL

migration_already_applied() {
  local filename="$1"
  case "$filename" in
    001_initial.sql)
      psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -tAc \
        "SELECT to_regclass('public.missions')" | grep -q missions
      ;;
    002_metrics_views.sql)
      psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -tAc \
        "SELECT to_regclass('public.daily_mission_metrics')" | grep -q daily_mission_metrics
      ;;
    *)
      return 1
      ;;
  esac
}

log "Applying pending migrations"
for f in "${MIGRATIONS}"/*.sql; do
  filename="$(basename "$f")"
  if psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -tAc \
      "SELECT 1 FROM schema_migrations WHERE filename = '${filename}'" | grep -q 1; then
    log "  skip ${filename} (recorded)"
    continue
  fi
  if migration_already_applied "${filename}"; then
    log "  backfill ${filename} (objects already present)"
    psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 \
      -c "INSERT INTO schema_migrations (filename) VALUES ('${filename}')"
    continue
  fi
  log "  -> ${filename}"
  psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 -f "$f"
  psql -h localhost -U "${DB_USER}" -d "${DB_NAME}" -v ON_ERROR_STOP=1 \
    -c "INSERT INTO schema_migrations (filename) VALUES ('${filename}')"
done

log "Database ready."
