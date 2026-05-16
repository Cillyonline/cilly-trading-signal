#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
BACKUP_DIR="${BACKUP_DIR:-backups/postgres}"
POSTGRES_DB="${POSTGRES_DB:-cilly_trading_signal}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
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
