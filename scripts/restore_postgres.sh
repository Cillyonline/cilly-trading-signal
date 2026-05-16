#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <backup-file.dump>" >&2
  exit 1
fi

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
POSTGRES_DB="${POSTGRES_DB:-cilly_trading_signal}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
BACKUP_FILE="$1"
CONTAINER_FILE="/tmp/restore_${POSTGRES_DB}.dump"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "Backup file not found: ${BACKUP_FILE}" >&2
  exit 1
fi

echo "This will replace database '${POSTGRES_DB}' using '${BACKUP_FILE}'."
echo "Press Ctrl+C to abort, or wait 5 seconds to continue."
sleep 5

docker compose -f "${COMPOSE_FILE}" stop api web

docker compose -f "${COMPOSE_FILE}" cp "${BACKUP_FILE}" "postgres:${CONTAINER_FILE}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres dropdb \
  --username "${POSTGRES_USER}" \
  --if-exists \
  "${POSTGRES_DB}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres createdb \
  --username "${POSTGRES_USER}" \
  "${POSTGRES_DB}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres pg_restore \
  --username "${POSTGRES_USER}" \
  --dbname "${POSTGRES_DB}" \
  --clean \
  --if-exists \
  "${CONTAINER_FILE}"

docker compose -f "${COMPOSE_FILE}" exec -T postgres rm "${CONTAINER_FILE}"

docker compose -f "${COMPOSE_FILE}" start api web

echo "Restored PostgreSQL database '${POSTGRES_DB}' from '${BACKUP_FILE}'."
