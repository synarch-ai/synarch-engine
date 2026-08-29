#!/usr/bin/env bash
#
# Synarch Engine — Cloud Agent install phase (idempotent).
#
# Prepares the repository for local development:
#   - System services: PostgreSQL 16 + pgvector, Redis, NATS (installed if missing)
#   - Backend: Python venv + pip dependencies
#   - Web: npm dependencies
#   - Local env files (.env.local) if absent
#   - Database role/db + schema migrations (applied once)
#
# Safe to run repeatedly. Designed to run after checkout; per-boot service
# startup lives in scripts/cloud-agent/start.sh.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

PG_VERSION=16
PG_PORT=5432
NATS_VERSION=2.10.22

log() { printf '\033[1;33m[install]\033[0m %s\n' "$*"; }

# --- 1. System packages (only if missing) ---------------------------------
NEED_APT=()
command -v pg_ctlcluster >/dev/null 2>&1 || NEED_APT+=("postgresql-${PG_VERSION}")
dpkg -s "postgresql-${PG_VERSION}-pgvector" >/dev/null 2>&1 || NEED_APT+=("postgresql-${PG_VERSION}-pgvector")
command -v redis-server >/dev/null 2>&1 || NEED_APT+=("redis-server")
command -v python3 >/dev/null 2>&1 || NEED_APT+=("python3")
python3 -m venv --help >/dev/null 2>&1 || NEED_APT+=("python3-venv")

if [ "${#NEED_APT[@]}" -gt 0 ]; then
  log "Installing system packages: ${NEED_APT[*]}"
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "${NEED_APT[@]}"
else
  log "System packages already present."
fi

# --- 2. NATS server binary (only if missing) ------------------------------
if ! command -v nats-server >/dev/null 2>&1; then
  log "Installing nats-server v${NATS_VERSION}"
  tmp="$(mktemp -d)"
  curl -fsSL -o "${tmp}/nats.tar.gz" \
    "https://github.com/nats-io/nats-server/releases/download/v${NATS_VERSION}/nats-server-v${NATS_VERSION}-linux-amd64.tar.gz"
  tar -xzf "${tmp}/nats.tar.gz" -C "${tmp}"
  sudo cp "${tmp}/nats-server-v${NATS_VERSION}-linux-amd64/nats-server" /usr/local/bin/
  rm -rf "${tmp}"
else
  log "nats-server already present."
fi

# --- 3. Local env files (only if absent) ----------------------------------
if [ ! -f backend/.env.local ]; then
  log "Writing backend/.env.local"
  cat > backend/.env.local <<ENV
DATABASE_URL=postgresql://synarch:synarch_local@localhost:${PG_PORT}/synarch
NATS_URL=nats://localhost:4222
QDRANT_URL=http://localhost:6333
OLLAMA_API_BASE=http://localhost:11434
REDIS_URL=redis://localhost:6379/0
AWS_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
APPROVAL_TIMEOUT_SECONDS=300
DEFAULT_AUTHORITY_MODE=supervised
ENV
fi

if [ ! -f apps/web/.env.local ]; then
  log "Writing apps/web/.env.local"
  cat > apps/web/.env.local <<ENV
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SSE_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_MISSION_STREAM=true
ENV
fi

# --- 4. Backend Python dependencies ---------------------------------------
log "Setting up backend virtualenv + dependencies"
if [ ! -d backend/.venv ]; then
  python3 -m venv backend/.venv
fi
# shellcheck disable=SC1091
source backend/.venv/bin/activate
pip install --upgrade pip -q
pip install -q -r backend/requirements.txt
deactivate

# --- 5. Web dependencies --------------------------------------------------
log "Installing web dependencies"
( cd apps/web && npm install --no-audit --no-fund )

# --- 6. Database bootstrap (role/db + migrations, applied once) ------------
log "Bootstrapping PostgreSQL database"
"$REPO_ROOT/scripts/cloud-agent/db-bootstrap.sh"

# --- 7. Pro developer skills (idempotent; skip with INSTALL_PRO_SKILLS=0) ---
if [ "${INSTALL_PRO_SKILLS:-1}" != "0" ]; then
  log "Installing pro developer skills"
  bash "$REPO_ROOT/scripts/cloud-agent/install-pro-skills.sh" -q
fi

log "Install complete."
