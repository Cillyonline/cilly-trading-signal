# v5.3 Twelve Data Provider Smoke Evidence

Date: 2026-06-11 UTC

Issue: #695

Environment class: local Docker Compose

Provider identifier: `twelve_data`

Sample symbol scope: public provider-recognized sample symbol

## Summary

The configured Twelve Data provider smoke was run locally after explicit
owner/operator approval and local key setup outside git. Evidence is sanitized and
contains only status fields, timeframe, provider identifier, candle counts, and
boolean checks.

This smoke proves only guarded manual stored-data sync behavior in the tested
local environment. It is not production-readiness evidence, broker-readiness
evidence, live/realtime market-data evidence, strategy-validation evidence,
profitability evidence, trading advice, or approval for automatic execution.

## Setup Boundary

- `.env` was present locally and ignored by git.
- No `.env` values, provider key, request URL, raw provider payload, cookies,
  browser storage, screenshots, private symbols, broker/account data, or private
  trading records are included.
- Docker Desktop was restarted by the operator after the Docker engine initially
  failed to respond.
- Local Docker Compose stack was built and started.
- Alembic migrations were run inside the API container.
- API health returned `status=ok`.

## Provider Sync Evidence

Manual authenticated API sync was run for `1W`, `1D`, and `4H` against a public
provider-recognized sample symbol.

| Timeframe | HTTP | sync_status | freshness_status | Provider | Provider timeframe | Candle count | Latest timestamp visible | Import history updated | Error code |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |
| `1W` | pass | success | fresh | twelve_data | `1W` | 2376 | true | true | none |
| `1D` | pass | success | fresh | twelve_data | `1D` | 5000 | true | true | none |
| `4H` | pass | success | fresh | twelve_data | `4H` | 3639 | true | true | none |

## Downstream Safety Check

A follow-up manual `1D` sync was run while comparing downstream counts before and
after the sync.

| Check | Before | After | Result |
| --- | ---: | ---: | --- |
| Signals | 2 | 2 | pass |
| Trades | 1 | 1 | pass |
| Alerts | 0 | 0 | pass |

No automatic analysis, signal, trade, order, broker action, or alert was created
by the provider sync path in this check.

## Verification Commands

Sanitized verification performed:

```powershell
docker info --format '{{.ServerVersion}}'
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec -T api uv run --with alembic --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" alembic upgrade head
Invoke-RestMethod -Uri 'http://localhost:8000/api/health' -TimeoutSec 15
```

The provider sync and downstream-count checks were run through authenticated local
API calls. Cookies were held only in the local PowerShell web request session and
were not printed or recorded.

## Security And Privacy Review

Secrets/redaction reviewed: pass.

No secrets, `.env` values, provider keys, request URLs, raw provider payloads,
cookies, browser storage, screenshots, private symbols, broker/account data,
private trading records, raw logs, or database dumps are included in this
evidence.

## Decision

The v5.3 operator-run configured Twelve Data provider smoke is complete for local
guarded manual stored-data sync of `1W`, `1D`, and `4H`.

Broader provider reliance still requires separate licensing, entitlement,
rate-limit, asset-scope, and production-like environment review. TradingView CSV
remains the fallback.
