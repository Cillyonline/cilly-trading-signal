# Operational Incident Runbook

## Purpose

This runbook gives the owner/operator a conservative response path for common local or private-staging incidents. It is for controlled single-operator review workflows only.

It is not an on-call system, production-readiness claim, security certification, trading advice process, broker-readiness claim, or automated remediation plan.

## Incident Principles

- Stop relying on affected signals, alerts, imports, provider data, or portfolio views until the incident is understood and resolved.
- Do not trade from stale, failed, partial, unknown, or recently restored data.
- Prefer `No Trade` and manual review over acting on uncertain context.
- Do not run automated repair commands unless this runbook or the deployment runbook explicitly says to do so.
- Keep broker integration and automatic order execution out of scope.
- Preserve evidence, but sanitize secrets, `.env` values, database URLs, cookies, raw logs with private data, trade notes, journal notes, screenshots, and restored row contents.

## Severity Levels

| Severity | Examples | Immediate response |
| --- | --- | --- |
| High | DB unavailable, migration failure, repeated startup crash, restore uncertainty | Stop app reliance, freeze data-changing operations, preserve logs, prepare rollback or restore decision |
| Medium | Provider sync failure, Telegram delivery failure, repeated import failure | Stop relying on affected workflow, use manual fallback, create follow-up issue if repeatable |
| Low | Stale-data confusion, one-off operator mistake caught before use | Mark data as untrusted, document correction, improve checklist if needed |

## First Response Checklist

1. Stop using the affected workflow for trading review.
2. Confirm the safety boundary: no broker action, no automatic execution, no buy/sell instruction.
3. Capture sanitized time, environment, commit, branch, and the exact workflow affected.
4. Check current health without exposing secrets.

```bash
curl -fsS https://<app-domain>/api/health
curl -fsS https://<app-domain>/api/health/details
docker compose -f infra/docker-compose.yml ps
```

5. Check logs only as needed and redact before sharing.

```bash
docker compose -f infra/docker-compose.yml logs --tail=120 api
docker compose -f infra/docker-compose.yml logs --tail=120 web
docker compose -f infra/docker-compose.yml logs --tail=120 postgres
```

6. Decide whether to continue, rollback, restore into a disposable target for diagnosis, or escalate.

## Evidence Template

```markdown
## Incident Evidence

- Date/time:
- Operator:
- Environment: local / private staging / disposable test
- Severity: high / medium / low
- Affected workflow:
- Current commit:
- Health status: pass/fail/not checked
- Data-changing operations stopped: yes/no
- Trading-review reliance stopped: yes/no
- Rollback considered: yes/no
- Restore considered: yes/no
- Secrets/private data/raw logs included: no
- Follow-up issue:
- Resolution summary:
```

## Data Import Failure

Symptoms:

- CSV upload fails validation.
- Imported candle counts, timeframe, or symbol look wrong.
- Screener import creates unexpected validation errors.

Stop:

- Do not run analysis from the failed import.
- Do not convert suspect screener rows to Watchlist candidates.
- Treat any generated signal from suspect imported data as untrusted.

Triage:

1. Confirm the source file is the intended symbol, timeframe, and export date.
2. Check UI validation messages before checking logs.
3. Confirm whether the failure is repeatable with a sanitized sample file.
4. Check API logs for validation errors, without sharing private rows or notes.
5. If a bad import was saved, mark the symbol/review context as untrusted and avoid new analysis until corrected.

Rollback or recovery:

- Prefer re-importing a corrected file through the normal UI workflow.
- Do not manually edit database rows unless a separate repair plan is written and reviewed.
- If saved data is materially wrong and cannot be corrected through the UI, create a follow-up issue with sanitized metadata only.

Escalate when:

- The same valid file fails repeatedly.
- Bad data was persisted and used for analysis or trade review.
- The import failure could affect more than one symbol or workflow.

## Provider Sync Failure

Symptoms:

- Manual provider sync is skipped, fails, or returns stale/partial data.
- Provider source/freshness metadata does not match operator expectations.

Stop:

- Do not treat provider-backed data as current until freshness is confirmed.
- Do not claim live, realtime, or automatic market-data coverage.
- Use CSV import as the manual fallback when appropriate.

Triage:

1. Confirm `MARKET_DATA_PROVIDER_SYNC_ENABLED` is intentionally enabled for the environment.
2. Confirm provider name and API key are configured only in local/server environment files.
3. Check `/api/health/details` for sanitized configuration booleans.
4. Check API logs for provider errors, rate limits, unsupported symbol/timeframe, or failed persistence.
5. Confirm source and freshness metadata in the UI before using the symbol for review.

Rollback or recovery:

- Disable provider sync if configuration or provider behavior is uncertain.
- Fall back to a known-good CSV import path.
- Re-run sync only after confirming the environment and provider constraints.

Escalate when:

- Provider errors repeat after config is confirmed.
- Freshness metadata is misleading or absent.
- Provider data could have replaced or confused a known-good review dataset.

## Migration Failure

Symptoms:

- Deployment fails during Alembic migration.
- API starts with schema errors.
- `/api/health/details` reports migration mismatch or DB errors.

Stop:

- Stop the deployment rollout.
- Do not continue data-changing UI work.
- Do not run repeated migration commands blindly.

Triage:

1. Record current commit and expected migration revision.
2. Capture sanitized API and migration logs.
3. Confirm the target database and Compose project are the intended environment.
4. Check whether the previous app version still runs against the current schema.
5. Confirm a recent backup exists before considering destructive repair.

Rollback or recovery:

- If the migration did not alter the database, roll back the app to the previous known-good commit using `docs/DEPLOYMENT_RUNBOOK.md#basic-rollback`.
- If the migration partially applied, stop and create a repair plan before touching the database.
- Test any restore or repair first on a disposable target using `docs/DEPLOYMENT_RUNBOOK.md#backup-restore-drill`.

Escalate when:

- The schema state is unclear.
- Data may have been partially migrated.
- A backup is missing, stale, or unverified.

## Telegram Failure

Symptoms:

- Operator test message fails.
- Policy-allowed alert delivery fails, is deduplicated, or is rate-limited unexpectedly.
- Telegram config guard prevents startup when routing is enabled.

Stop:

- Do not rely on Telegram for timely review prompts.
- Review alert events in the app manually.
- Do not loosen message policy to force delivery.

Triage:

1. Confirm `TELEGRAM_ALERT_ROUTING_ENABLED` is intentionally enabled.
2. Confirm token and chat ID are present only in local/server environment files, never in issues or logs.
3. Check alert event review state in the UI.
4. Check API logs for failed, skipped, deduplicated, or rate-limited delivery states.
5. Send only sanitized test evidence; never paste tokens or chat IDs.

Rollback or recovery:

- Disable Telegram routing if config or delivery behavior is uncertain.
- Continue with manual alert review in the app.
- Re-enable only after a sanitized operator test passes.

Escalate when:

- Delivery failures repeat after config is confirmed.
- Alerts appear to route outside the allowed event policy.
- Message wording risks buy/sell instruction or trading advice.

## Database Unavailable

Symptoms:

- API health fails because the database cannot be reached.
- PostgreSQL container is unhealthy or stopped.
- Login, imports, analysis, trades, journal, or performance pages fail broadly.

Stop:

- Stop all data-changing operations.
- Do not trust partially loaded pages or cached browser state.
- Do not restart repeatedly without checking disk and container state.

Triage:

1. Check containers and PostgreSQL health.
2. Check disk space and memory pressure.
3. Check recent deployment, backup, restore, or host maintenance activity.
4. Confirm `.env` and `DATABASE_URL` were not changed or exposed.
5. Check PostgreSQL logs for startup, authentication, disk, or corruption errors.

Rollback or recovery:

- If caused by app deployment and the DB is healthy, roll back the app to the previous known-good commit.
- If caused by database state, stop and verify backups before repair.
- Restore only after confirming the target can be replaced; test first on a disposable target when possible.

Escalate when:

- PostgreSQL reports corruption, missing files, or repeated crash loops.
- Recent backups are missing or unverified.
- Any private data exposure is suspected.

## Stale Data Confusion

Symptoms:

- Operator cannot tell whether data is current enough for review.
- Source/freshness metadata is stale, unknown, partial, or inconsistent.
- Saved signals do not reflect expected current market context.

Stop:

- Do not trade from stale or unclear data.
- Treat stale signals as review history, not current prompts.
- Prefer `No Trade` until context is refreshed and reviewed.

Triage:

1. Check source and freshness metadata in Watchlist, signal detail, and related review screens.
2. Confirm whether the symbol uses CSV data or provider-backed Daily/EOD data.
3. Confirm required benchmark context is present where applicable.
4. Re-import or sync only through documented manual workflows.
5. Re-run analysis only after data freshness is understood.

Rollback or recovery:

- Use a known-good CSV import if provider freshness is uncertain.
- Add a journal/review note that older signals are stale and should not be used for current decisions.
- Create a follow-up issue if the UI fails to make stale/unknown context obvious.

Escalate when:

- Stale or unknown data looks equivalent to fresh data.
- A signal or alert could be misread as current when it is not.
- Benchmark or relative-strength context is missing but not clearly visible.

## Provider Sync Failure

Symptoms:

- Manual provider sync returns `skipped`, `failed`, or `partial`.
- `sync_error_code` is present or freshness remains `stale`, `failed`, `partial`, or `unknown`.
- Required `1W`, `1D`, or `4H` context is missing after a sync attempt.

Stop:

- Do not treat provider-backed output as current while sync status or freshness is unclear.
- Do not paste API keys, request URLs, provider payloads, account details, database URLs, or raw logs into issues, PRs, screenshots, or chat.
- Do not rotate secrets, restart VPS services, or edit server `.env` files without explicit operator approval.

Triage:

1. Identify the visible state: `skipped`, `failed`, `partial`, `stale`, `unknown`, or `fresh`.
2. Record only the sanitized `sync_error_code`, affected timeframe, and public/fake symbol.
3. Check whether provider sync is intentionally disabled before treating `skipped` as a defect.
4. Confirm whether the issue is config/auth, rate limit/transport, invalid payload, partial coverage, or stale existing data.
5. Use TradingView CSV/manual import as the fallback when current review context is needed.

Recovery:

- Config/auth: fix environment values outside git, then rerun manual sync.
- Rate limit/transport: wait, reduce scope, or retry later; do not loop requests aggressively.
- Invalid/empty payload: verify provider symbol/timeframe mapping and fallback to CSV.
- Partial coverage: fill missing required timeframes before analysis.
- Stale existing data: keep prior signals as historical review only until data is refreshed.

Escalate when:

- Repeated sync failures affect multiple symbols or required benchmark context.
- UI wording does not make failed/partial/stale/unknown state obvious.
- Recovery requires service restarts, secret rotation, database edits, migrations, or backup restore.

## Escalation Guidance

Create a follow-up GitHub issue when:

- The incident repeats.
- Data may be wrong, lost, partially migrated, or restored from the wrong source.
- A safety boundary is unclear.
- The response requires code changes, schema repair, manual database edits, or new operational policy.
- Evidence cannot be shared without exposing private data.

Issue text must include sanitized facts only: environment class, approximate time, affected workflow, current commit, pass/fail health, operator-visible symptoms, and redacted logs if needed.

## Final Recovery Checklist

Before returning to normal review:

1. Health checks pass.
2. The affected workflow has a known-good data source and timestamp.
3. Any stale, failed, partial, or restored data is clearly understood.
4. Backup or rollback status is known if the incident touched persistence.
5. No secrets or private trading data were exposed in evidence.
6. Follow-up issues exist for unresolved root causes.
7. The operator explicitly confirms no trading decision was made from failed or stale data.
