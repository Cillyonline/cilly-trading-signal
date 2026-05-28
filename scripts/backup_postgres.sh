#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
POSTGRES_DB="${POSTGRES_DB:-cilly_trading_signal}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"

resolve_path() {
  local target="$1"
  local path
  local ancestor
  local suffix=""

  if [[ "${target}" = /* ]]; then
    path="${target}"
  else
    path="${PWD}/${target}"
  fi

  ancestor="${path}"
  while [[ ! -e "${ancestor}" && "${ancestor}" != "/" ]]; do
    suffix="/$(basename "${ancestor}")${suffix}"
    ancestor="$(dirname "${ancestor}")"
  done

  printf '%s%s\n' "$(cd "${ancestor}" && pwd -P)" "${suffix}"
}

if [[ -z "${BACKUP_DIR:-}" ]]; then
  BACKUP_DIR="${REPO_ROOT}/../cilly-postgres-backups/postgres"
  echo "BACKUP_DIR is not set; using repository-external backup directory: ${BACKUP_DIR}" >&2
  echo "Set BACKUP_DIR explicitly for staging or production-like backups." >&2
fi

REPO_ROOT="$(resolve_path "${REPO_ROOT}")"
BACKUP_DIR="$(resolve_path "${BACKUP_DIR}")"

case "${BACKUP_DIR}/" in
  "${REPO_ROOT}/"*)
    if [[ "${ALLOW_REPO_BACKUP_DIR:-}" != "true" ]]; then
      echo "Refusing to write PostgreSQL backup inside the repository working tree:" >&2
      echo "  ${BACKUP_DIR}" >&2
      echo "Set BACKUP_DIR to a path outside the repository." >&2
      echo "For disposable local-only tests, set ALLOW_REPO_BACKUP_DIR=true explicitly." >&2
      exit 1
    fi
    echo "WARNING: writing backup inside the repository because ALLOW_REPO_BACKUP_DIR=true." >&2
    ;;
esac

BACKUP_FILE="${BACKUP_DIR}/${POSTGRES_DB}_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres pg_dump \
  --username "${POSTGRES_USER}" \
  --dbname "${POSTGRES_DB}" \
  --format custom \
  --file "/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump"

docker compose -f "${COMPOSE_FILE}" cp \
  "postgres:/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump" \
  "${BACKUP_FILE}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres rm \
  "/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump"

echo "Created PostgreSQL backup: ${BACKUP_FILE}"
