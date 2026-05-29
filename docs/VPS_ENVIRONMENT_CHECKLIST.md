# VPS Environment Checklist

## Purpose

This checklist defines the required VPS staging environment values for this project without recording real secrets.

It supports #159 and must be completed before the first private VPS staging deployment. It is not a production-readiness claim and does not approve real-money trading, broker integration, automatic execution, or public SaaS operation.

## Safety Rules

- Create the real `.env` file only on the VPS.
- Do not commit `.env` or `.env.*` files.
- Do not paste secrets, tokens, passwords, database URLs, cookies, private keys, or full `.env` contents into issues, PRs, docs, screenshots, logs, or chat.
- Use placeholders in documentation only.
- Rotate any secret that was copied into an unsafe channel.
- Prefer unique secrets per environment.

## Environment Location

Planned repository checkout on the VPS:

```text
/root/repos/cilly-trading-signal
```

Planned environment file location:

```text
/root/repos/cilly-trading-signal/.env
```

The `.env` file is intentionally local to the VPS checkout and ignored by git. It must not be copied to the repository, issues, PRs, or documentation.

## Required Values

Use this table as a completion checklist. Record only status, not actual values.

| Variable | Required Staging Value | Status | Notes |
| --- | --- | --- | --- |
| `APP_DOMAIN` | Dedicated app domain, for example `trading.<domain>` | TBD | Must match DNS and Caddy route. |
| `ENVIRONMENT` | `staging` | TBD | Enables non-local config guards. |
| `DATABASE_URL` | PostgreSQL URL using non-default app DB user and password | TBD | Must match `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB`. Do not paste the value. |
| `SECRET_KEY` | Strong random secret, at least 32 random characters | TBD | Session signing secret. Rotate if leaked. |
| `ADMIN_EMAIL` | Real admin email, not `admin@example.com` | TBD | Single-user admin login. |
| `ADMIN_INITIAL_PASSWORD` | Strong random password | TBD | Store in password manager. Rotate if shared unsafely. |
| `AUTH_COOKIE_NAME` | `cilly_session` or an app-specific cookie name | TBD | Default is acceptable unless a conflict exists. |
| `AUTH_COOKIE_SECURE` | `true` | TBD | Required for HTTPS staging. |
| `AUTH_SESSION_TTL_SECONDS` | `43200` or a deliberately chosen shorter TTL | TBD | Default is 12 hours. |
| `TRADINGVIEW_WEBHOOK_SECRET` | Strong random secret, at least 32 random characters | TBD | Required by non-local config guard. |
| `CORS_ORIGINS` | Exact HTTPS origin list, for example `["https://<app-domain>"]` | TBD | No wildcard origins. |
| `NEXT_PUBLIC_API_BASE_URL` | `/api` | TBD | Same-origin Caddy routing. |
| `POSTGRES_USER` | Non-default app-specific DB user | TBD | Do not use `postgres`. |
| `POSTGRES_PASSWORD` | Strong random DB password | TBD | Must match `DATABASE_URL`. |
| `POSTGRES_DB` | App-specific database name | TBD | Recommended: `cilly_trading_signal`. |

## Optional Values

| Variable | When Needed | Status | Notes |
| --- | --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Explicit Telegram test delivery and future alert routing | TBD | Optional until alert routing is approved. |
| `TELEGRAM_CHAT_ID` | Explicit Telegram test delivery and future alert routing | TBD | Optional until alert routing is approved. |
| `TELEGRAM_ALERT_ROUTING_ENABLED` | Automatic Telegram alert routing | TBD | Keep `false` until the v1.3 routing implementation and smoke test are ready. If set to `true`, token and chat ID must be safe real values. |
| `MARKET_DATA_PROVIDER_SYNC_ENABLED` | Future market data provider sync | TBD | Keep `false` unless provider sync is deliberately enabled for the environment. |
| `MARKET_DATA_PROVIDER` | Future market data provider sync | TBD | Required only when provider sync is enabled. Supported placeholders are `alpha_vantage`, `twelve_data`, `polygon`, and `tiingo`. |
| `MARKET_DATA_API_KEY` | Future market data provider sync | TBD | Required only when provider sync is enabled. Never paste the real key into docs, issues, PRs, logs, screenshots, or chat. |

## Disallowed Values Outside Local Development

Do not use these values in VPS staging:

- `ENVIRONMENT=development`
- `SECRET_KEY=change-this-secret-key`
- `SECRET_KEY=change-me`
- `ADMIN_EMAIL=admin@example.com`
- `ADMIN_INITIAL_PASSWORD=change-this-password`
- `AUTH_COOKIE_SECURE=false`
- `TRADINGVIEW_WEBHOOK_SECRET=change-this-webhook-secret`
- `TRADINGVIEW_WEBHOOK_SECRET=change-me`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=postgres`
- `MARKET_DATA_API_KEY=change-this-market-data-api-key`
- `MARKET_DATA_API_KEY=market-data-api-key`
- `MARKET_DATA_API_KEY=provider-api-key`
- Empty passwords or empty secrets
- Wildcard CORS origins such as `*`

The API should fail fast in non-local environments when unsafe values are present.

## Secret Generation Guidance

Generate secrets on a trusted machine and store them in a password manager.

Examples of acceptable generation approaches:

```powershell
[Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Maximum 256 }))
```

```bash
openssl rand -base64 48
```

Do not paste generated secrets into this document.

## Sanitized Example

This example shows shape only. Do not use these placeholder values.

```dotenv
APP_DOMAIN=trading.<domain>
ENVIRONMENT=staging
DATABASE_URL=postgresql+psycopg://<app-db-user>:<strong-db-password>@postgres:5432/cilly_trading_signal
SECRET_KEY=<strong-random-session-secret>
ADMIN_EMAIL=<admin-email>
ADMIN_INITIAL_PASSWORD=<strong-random-admin-password>
AUTH_COOKIE_NAME=cilly_session
AUTH_COOKIE_SECURE=true
AUTH_SESSION_TTL_SECONDS=43200
TRADINGVIEW_WEBHOOK_SECRET=<strong-random-webhook-secret>
CORS_ORIGINS=["https://trading.<domain>"]
NEXT_PUBLIC_API_BASE_URL=/api
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_ALERT_ROUTING_ENABLED=false
MARKET_DATA_PROVIDER_SYNC_ENABLED=false
MARKET_DATA_PROVIDER=
MARKET_DATA_API_KEY=
POSTGRES_USER=<app-db-user>
POSTGRES_PASSWORD=<strong-db-password>
POSTGRES_DB=cilly_trading_signal
```

## Pre-Deployment Checks

Run these checks on the VPS from the repository checkout after creating `.env`. Do not paste full command output if it contains secrets.

Confirm `.env` exists and is not tracked:

```bash
test -f .env
git status --short -- .env .env.example
```

Expected result:

- `.env` exists.
- `git status --short -- .env .env.example` does not show `.env` as tracked or staged.

Confirm unsafe placeholders are not present without printing actual values:

```bash
grep -nE 'change-this|change-me|admin@example.com|postgres:postgres|AUTH_COOKIE_SECURE=false|CORS_ORIGINS=.*\*' .env && echo 'UNSAFE_PLACEHOLDER_FOUND' || echo 'No known unsafe placeholders found'
```

Expected result:

- `No known unsafe placeholders found`

Confirm required variable names are present without printing values:

```bash
for key in APP_DOMAIN ENVIRONMENT DATABASE_URL SECRET_KEY ADMIN_EMAIL ADMIN_INITIAL_PASSWORD AUTH_COOKIE_SECURE TRADINGVIEW_WEBHOOK_SECRET CORS_ORIGINS NEXT_PUBLIC_API_BASE_URL POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB; do grep -q "^${key}=" .env && echo "${key}=present" || echo "${key}=missing"; done
```

Expected result:

- Every required key prints `present`.

## App Startup Guard Check

The API configuration guard validates unsafe non-local settings at startup. The first staging deployment should confirm that the API starts successfully only after safe values are set.

If startup fails with an unsafe configuration error, stop and fix `.env` on the VPS. Do not weaken the guard to make staging start.

## Rotation Expectations

- Rotate `ADMIN_INITIAL_PASSWORD` if it was shared outside a password manager.
- Rotate `SECRET_KEY` if it leaked; existing sessions may become invalid.
- Rotate `POSTGRES_PASSWORD` together in both `POSTGRES_PASSWORD` and `DATABASE_URL`.
- Rotate `TRADINGVIEW_WEBHOOK_SECRET` if webhook URLs, payload examples, screenshots, or logs may have exposed it.
- Restart the stack after secret rotation and verify login plus `/api/health`.

## Completion Criteria

This checklist is complete when:

- Every required variable has a safe staging value on the VPS.
- `.env` exists only on the VPS and is not tracked by git.
- Known unsafe placeholders are absent.
- `AUTH_COOKIE_SECURE=true` is set.
- `CORS_ORIGINS` uses exact HTTPS origin(s).
- Strong secrets are stored in a password manager.
- No real secret values are committed or documented.

## Follow-Ups

- #158 defines the deployment plan.
- #161 defines minimum monitoring checks.
- #162 verifies backup and restore mechanics.
- #163 runs the first private VPS smoke test after deployment approval.
