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
| `ADMIN_INITIAL_PASSWORD` | Rotate and store in password manager. | pending | Required before stronger private-staging reliance. |
| `SECRET_KEY` | Rotate if previously exposed; expect old sessions to become invalid. | pending | Required if session secret exposure is possible. |
| `TRADINGVIEW_WEBHOOK_SECRET` | Rotate if webhook examples, URLs, screenshots, or logs may have exposed it. | pending | Required before relying on webhook path. |
| `POSTGRES_PASSWORD` and `DATABASE_URL` | Rotate together only with a controlled database password change. | pending | Requires careful operator execution; do not print DB URL. |
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

- Date/time UTC: pending
- Operator or role: owner/operator
- Environment class: private staging
- Target domain: `trading.cillyonline.de`
- Branch or commit SHA: pending
- `.env` exists and remains untracked: pending
- Unsafe placeholder check: pending
- Required variable presence check: pending
- Secret categories rotated: pending
- Secret categories explicitly deferred: pending
- `cilly-trading-signal` Compose project restarted: pending
- Existing unrelated `staging` project unaffected: pending
- Alembic migration status: pending
- Internal API health: pending
- HTTPS API health: pending
- HTTPS web health: pending
- Manual login after rotation: pending
- Logout/protected-route behavior after rotation: pending
- Failed or blocked steps: pending
- Follow-up issues or PRs: pending
- Secrets, `.env` values, database URLs, provider keys, request URLs, raw logs,
  cookies, local storage, backup credentials, private symbols, broker data,
  screenshots with sensitive data, or private trading records included: no
- Production-readiness, live/realtime, broker-readiness, profitability,
  strategy-validation, trading-advice, real-money-readiness, or
  automatic-execution claim made: no

## Current Status

Status: pending operator rotation.

The repository now contains the safe procedure and evidence structure. The actual
secret rotation must be performed by the owner/operator on the VPS using secret
values from a password manager or another approved private channel.

Do not close issue #754 as passed until the sanitized evidence fields above are
updated from `pending` to concrete pass/deferred values after the rotation.
