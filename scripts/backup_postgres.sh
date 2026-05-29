#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-}"
POSTGRES_DB="${POSTGRES_DB:-cilly_trading_signal}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-}"
RETENTION_MIN_KEEP="${RETENTION_MIN_KEEP:-7}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"

docker_compose() {
  local cmd=(docker compose)

  if [[ -n "${COMPOSE_ENV_FILE}" ]]; then
    cmd+=(--env-file "${COMPOSE_ENV_FILE}")
  fi

  cmd+=(-f "${COMPOSE_FILE}")
  "${cmd[@]}" "$@"
}

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

docker_compose exec -T postgres pg_dump \
  --username "${POSTGRES_USER}" \
  --dbname "${POSTGRES_DB}" \
  --format custom \
  --file "/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump"

docker_compose cp \
  "postgres:/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump" \
  "${BACKUP_FILE}"

docker_compose exec -T postgres rm \
  "/tmp/${POSTGRES_DB}_${TIMESTAMP}.dump"

echo "Created PostgreSQL backup: ${BACKUP_FILE}"

if [[ -n "${RETENTION_DAYS}" ]]; then
  if [[ ! "${RETENTION_DAYS}" =~ ^[0-9]+$ ]] || [[ "${RETENTION_DAYS}" -lt 1 ]]; then
    echo "RETENTION_DAYS must be a positive integer when set." >&2
    exit 1
  fi

  if [[ ! "${RETENTION_MIN_KEEP}" =~ ^[0-9]+$ ]]; then
    echo "RETENTION_MIN_KEEP must be a non-negative integer." >&2
    exit 1
  fi

  mapfile -t backup_files < <(
    find "${BACKUP_DIR}" -maxdepth 1 -type f -name "${POSTGRES_DB}_*.dump" -printf '%T@ %p\n' \
      | sort -n \
      | cut -d' ' -f2-
  )

  delete_budget=$((${#backup_files[@]} - RETENTION_MIN_KEEP))

  if [[ "${delete_budget}" -gt 0 ]]; then
    deleted_count=0
    for backup_file in "${backup_files[@]}"; do
      if [[ "${deleted_count}" -ge "${delete_budget}" ]]; then
        break
      fi

      if find "${backup_file}" -maxdepth 0 -type f -mtime +"${RETENTION_DAYS}" | grep -q .; then
        rm -f -- "${backup_file}"
        deleted_count=$((deleted_count + 1))
      fi
    done

    echo "Retention cleanup removed ${deleted_count} old PostgreSQL backup(s)."
  else
    echo "Retention cleanup skipped; backup count is within RETENTION_MIN_KEEP."
  fi
fi
