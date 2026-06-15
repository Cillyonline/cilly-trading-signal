# v5.8 Private Staging Secret Rotation

Date: 2026-06-14

## Scope

This file records the private-staging secret rotation procedure and sanitized
evidence for issue #754.

This is a private-staging operations artifact only. It is not production-readiness
evidence, public SaaS readiness, broker-readiness evidence, profitability
evidence, strategy-validation evidence, trading advice, real-money readiness, or
approval for automatic execution.

## Safety Rules

- Rotate secrets only through an owner/operator-controlled channel and password
  manager.
- Do not paste, print, commit, screenshot, or record `.env` values, generated
  secrets, database URLs, provider keys, cookies, tokens, backup credentials, or
  password-manager contents.
- Keep the unrelated VPS Compose project `staging` untouched.
- Restart only the `cilly-trading-signal` Compose project when needed.
- Stop and rotate again if any secret appears in terminal output, chat, docs,
  issues, PRs, screenshots, or logs.

## Rotation Checklist

Record only `pass`, `blocked`, `deferred`, or `not applicable`; never record the
secret value.

| Secret category | Expected action | Status | Sanitized notes |
| --- | --- | --- | --- |
| `ADMIN_INITIAL_PASSWORD` | Rotate and store in password manager. | pass | Rotated by owner/operator and verified through login. |
| `SECRET_KEY` | Rotate if previously exposed; expect old sessions to become invalid. | pass | Rotated by owner/operator. |
| `TRADINGVIEW_WEBHOOK_SECRET` | Rotate if webhook examples, URLs, screenshots, or logs may have exposed it. | pass | Rotated by owner/operator. |
| `POSTGRES_PASSWORD` and `DATABASE_URL` | Rotate together only with a controlled database password change. | deferred | Deferred intentionally to avoid database-password risk during stage-1 rotation. |
| Optional provider credentials | Rotate only if enabled or exposed. | not applicable | Provider smoke is out of scope for this issue. |
| Optional Telegram credentials | Rotate only if enabled or exposed. | not applicable | Telegram routing is out of scope for this issue. |

## Operator Procedure

Run on the VPS only after the owner/operator has generated replacement secrets and
stored them in a password manager.

1. SSH to the VPS and enter the repository checkout.
2. Confirm `.env` exists without printing it.
3. Create a timestamped backup copy of `.env` outside Git-tracked evidence.
4. Edit `.env` on the VPS with the password-manager values.
5. If the database password is rotated, update the PostgreSQL role password and
   keep `POSTGRES_PASSWORD` and `DATABASE_URL` in sync.
6. Rebuild/restart only the `cilly-trading-signal` Compose project.
7. Run migrations.
8. Verify internal API health, HTTPS API health, HTTPS web health, login, logout,
   and protected-route behavior.
9. Record only the sanitized evidence below.

## Sanitized Evidence

- Date/time UTC: 2026-06-15
- Operator or role: owner/operator
- Environment class: private staging
- Target domain: `trading.cillyonline.de`
- Branch or commit SHA: `e696cbe` or later `main` on VPS after fast-forward
- `.env` exists and remains untracked: pass
- Unsafe placeholder check: pass; no known unsafe placeholders found
- Required variable presence check: pass for `ADMIN_INITIAL_PASSWORD`, `SECRET_KEY`, and `TRADINGVIEW_WEBHOOK_SECRET`
- Secret categories rotated: `ADMIN_INITIAL_PASSWORD`, `SECRET_KEY`, `TRADINGVIEW_WEBHOOK_SECRET`
- Secret categories explicitly deferred: `POSTGRES_PASSWORD` and `DATABASE_URL`
- `cilly-trading-signal` Compose project restarted: pass
- Existing unrelated `staging` project unaffected: pass; still listed as separate `running(1)` Compose project
- Alembic migration status: pass
- Internal API health: pass
- HTTPS API health: pass
- HTTPS web health: pass
- Manual login after rotation: pass
- Logout/protected-route behavior after rotation: pass
- Failed or blocked steps: none for stage-1 rotation
- Follow-up issues or PRs: database password rotation remains deferred until explicitly needed
- Secrets, `.env` values, database URLs, provider keys, request URLs, raw logs,
  cookies, local storage, backup credentials, private symbols, broker data,
  screenshots with sensitive data, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, or
  automatic-execution claim made: no

## Current Status

Status: pass for stage-1 private-staging secret rotation.

The owner/operator rotated `ADMIN_INITIAL_PASSWORD`, `SECRET_KEY`, and
`TRADINGVIEW_WEBHOOK_SECRET` on the VPS using private secret values stored outside
GitHub, docs, and chat.

`POSTGRES_PASSWORD` and `DATABASE_URL` remain intentionally deferred because
database-password rotation requires a separate controlled database role update and
is higher risk than stage-1 app secret rotation.
