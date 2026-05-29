#!/usr/bin/env bash
set -euo pipefail

APP_DOMAIN="${APP_DOMAIN:-trading.cillyonline.de}"
COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-.env}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-cilly-trading-signal}"
BACKUP_DIR="${BACKUP_DIR:-/srv/backups/cilly-trading-signal/postgres}"
BACKUP_MAX_AGE_HOURS="${BACKUP_MAX_AGE_HOURS:-30}"
DISK_PATH="${DISK_PATH:-/}"
DISK_MAX_USED_PERCENT="${DISK_MAX_USED_PERCENT:-85}"

failures=0

require_non_negative_integer() {
  local name="$1"
  local value="$2"

  if [[ ! "${value}" =~ ^[0-9]+$ ]]; then
    printf 'FAIL invalid_%s\n' "${name}"
    exit 1
  fi
}

check_pass() {
  printf 'PASS %s\n' "$1"
}

check_fail() {
  printf 'FAIL %s\n' "$1"
  failures=$((failures + 1))
}

docker_compose() {
  docker compose --env-file "${COMPOSE_ENV_FILE}" -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" "$@"
}

check_api_health() {
  if curl -fsS --max-time 15 "https://${APP_DOMAIN}/api/health" >/dev/null; then
    check_pass "api_health"
  else
    check_fail "api_health"
  fi
}

check_https_route() {
  if curl -fsSI --max-time 15 "https://${APP_DOMAIN}/" >/dev/null; then
    check_pass "https_route"
  else
    check_fail "https_route"
  fi
}

check_compose_services() {
  local services=(postgres api web caddy)
  local service
  local status

  for service in "${services[@]}"; do
    status="$(docker_compose ps --status running --services "${service}" 2>/dev/null || true)"
    if [[ "${status}" == "${service}" ]]; then
      check_pass "compose_${service}_running"
    else
      check_fail "compose_${service}_running"
    fi
  done
}

check_disk() {
  local used_percent

  used_percent="$(df -P "${DISK_PATH}" | awk 'NR == 2 { gsub(/%/, "", $5); print $5 }')"
  if [[ -n "${used_percent}" && "${used_percent}" =~ ^[0-9]+$ && "${used_percent}" -le "${DISK_MAX_USED_PERCENT}" ]]; then
    check_pass "disk_usage_percent=${used_percent}"
  else
    check_fail "disk_usage_percent=${used_percent:-unknown}"
  fi
}

check_backup_freshness() {
  local newest
  local now
  local age_hours

  newest="$(find "${BACKUP_DIR}" -maxdepth 1 -type f -name 'cilly_trading_signal_*.dump' -printf '%T@\n' 2>/dev/null | sort -nr | head -n 1 || true)"
  if [[ -z "${newest}" ]]; then
    check_fail "backup_freshness_hours=missing"
    return
  fi

  now="$(date +%s)"
  age_hours="$(awk -v now="${now}" -v newest="${newest}" 'BEGIN { printf "%d", (now - newest) / 3600 }')"

  if [[ "${age_hours}" -le "${BACKUP_MAX_AGE_HOURS}" ]]; then
    check_pass "backup_freshness_hours=${age_hours}"
  else
    check_fail "backup_freshness_hours=${age_hours}"
  fi
}

require_non_negative_integer "backup_max_age_hours" "${BACKUP_MAX_AGE_HOURS}"
require_non_negative_integer "disk_max_used_percent" "${DISK_MAX_USED_PERCENT}"
check_api_health
check_https_route
check_compose_services
check_disk
check_backup_freshness

if [[ "${failures}" -gt 0 ]]; then
  printf 'SUMMARY failed_checks=%s\n' "${failures}"
  exit 1
fi

printf 'SUMMARY failed_checks=0\n'
