# MVP Smoke Test

## Purpose

This document records the MVP smoke-test workflow and the latest validation result for the manual trading cockpit. The smoke test uses local/sample data only and does not make a production-readiness, profitability, or execution claim.

For the private VPS staging smoke-test procedure and evidence template, see `docs/VPS_STAGING_SMOKE_TEST.md`.
For the guarded manual provider sync checklist, see `docs/PROVIDER_SYNC_SMOKE_TEST.md`.
For the intended end-to-end manual cockpit review sequence, see `docs/COCKPIT_REVIEW_WORKFLOW.md`.
For repeatable visual browser clickthrough evidence, see `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md`.

## Safety Scope

- Signals are review prompts, not buy/sell instructions.
- The app must not create broker orders or connect to a broker.
- Trades in this smoke test are manual documentation records only.
- Performance views show documented historical/paper results, not forecasts.
- Provider sync smoke evidence, if run separately, validates only guarded stored-data
  sync behavior and is not live/realtime or production-readiness evidence.
- Screener CSV smoke evidence validates stored candidate review and explicit Watchlist
  conversion only. It must not imply automatic analysis, signal creation, trade
  creation, alert creation, broker action, or order execution.

## Runner

The `scripts/smoke_test.ps1` runner automates preflight, stack startup, local
database migrations, and the API health check. It does not replace the browser
portion of the smoke test — it only reduces manual setup ambiguity.

```powershell
# Bring the stack up and wait for /api/health
.\scripts\smoke_test.ps1

# Bring the stack down (volumes preserved)
.\scripts\smoke_test.ps1 -Cleanup

# Bring the stack down and wipe the Postgres volume
.\scripts\smoke_test.ps1 -Cleanup -PurgeVolumes
```

The runner fails fast with a clear `[FAIL]` message when the Docker engine pipe
is unreachable or when `alembic upgrade head` fails in the local API container.
Browser steps (login, watchlist, CSV import, analysis, trade log, journal,
performance) continue manually using the fixtures under `test-data/csv/`.

The migration step prevents stale preserved Docker volumes from producing
confusing workflow failures during local smoke testing. It is not a production
migration policy, does not reset volumes, and does not remove the need for a
separate production-like deployment gate.

Use `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md` to record the visual browser
workflow after the runner succeeds.

This script is release-validation tooling, not a production deployment claim.

Optional sanitized evidence formatting:

```powershell
.\scripts\format_smoke_evidence.ps1 `
  -CommitSha <branch-or-sha> `
  -SmokeRunnerStatus pass `
  -ApiHealth pass `
  -WebLoad pass `
  -BrowserChecklist 'not run'
```

The formatter only uses explicit command-line inputs and prints Markdown. It does
not read `.env`, cookies, browser sessions, local storage, logs, databases,
provider payloads, screenshots, or private trading data.

## Target Workflow

1. Start the local stack with Docker Compose.
2. Verify API health.
3. Open the web app and log in with the local admin credentials.
4. Create or verify a watchlist item for sample/paper data.
5. Import TradingView-compatible CSV data for `1W`, `1D`, and `4H`.
6. Run analysis and review generated signal cards.
7. Review signal detail, stale wording, manual status actions, review notes, and review history.
8. Create a manual trade log from paper/sample values only.
9. Add trade events, close the trade, and add a journal review.
10. Verify dashboard, performance, settings, alerts, and safety wording remain decision-support only.

## Screener-To-Watchlist Smoke Checklist

Use sample-only screener rows. Do not use private watchlists, personal trading notes,
provider credentials, cookies, screenshots with secrets, or production data.

Suggested sample CSV:

```csv
Symbol,Name,Exchange,Sector,Price,Change %,Volume,Relative Volume,Market Cap,RSI (14)
SMOKE-SCR-001,Smoke Screener One,SAMPLE,Technology,100.00,1.25%,100K,1.10,1M,55.2
SMOKE-SCR-002,Smoke Screener Two,SAMPLE,Healthcare,50.00,-0.50%,80K,0.95,500K,60.1
```

Checklist:

1. Start the local stack and log in with local admin credentials.
2. Open `/screener`.
3. Upload the sample CSV with asset class `stock` and a clearly fake preset label.
4. Confirm the import summary shows accepted candidate rows and no private data.
5. Confirm the results appear as review candidates, not recommendations.
6. Select one candidate and use the explicit `Zur Watchlist hinzufuegen` action.
7. Confirm the browser confirmation copy states that no analysis, signal, trade, or alert is created.
8. Confirm the result changes to `watchlist_added` and shows a linked Watchlist item id.
9. Confirm the Watchlist page contains the added fake symbol.
10. Upload or convert a duplicate symbol path and confirm the result is visibly linked as a duplicate instead of creating another Watchlist symbol.
11. Confirm no automatic analysis, signal, trade, alert, broker action, order, live/realtime claim, profitability claim, or trading advice appears in the workflow.

API-level optional checks after the UI path:

```powershell
Invoke-RestMethod http://localhost:8000/api/health
```

If deeper API inspection is needed, use authenticated browser/API tooling only with
local sample data. Do not paste cookies or session tokens into issues, docs, or PRs.

## v3.1 Owner Cockpit Local Validation Evidence

Date: 2026-06-02

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Branch/commit context: `main` at `d7fc8af`
- Deployment shape: local Docker Compose stack with PostgreSQL, API, and web.
- Data scope: local/sample validation only; no private watchlists, broker data,
  account data, fills, provider credentials, cookies, screenshots, database dumps,
  raw logs, private notes, or production data were recorded.
- Browser/UI scope: web HTTP load was checked, then the local Caddy proxy was
  used for same-origin browser validation at `https://localhost` because direct
  `http://localhost:3000` loads the web app but does not route `/api/*`.

Commands and checks recorded:

```powershell
.\scripts\smoke_test.ps1 -TimeoutSeconds 180
curl.exe -fsS -I http://localhost:3000
.\scripts\format_smoke_evidence.ps1 -CommitSha main-0390c35 -SmokeRunnerStatus pass -ApiHealth pass -WebLoad pass -BrowserChecklist 'not run'
docker compose -f infra/docker-compose.yml --profile proxy up -d caddy
curl.exe -k -fsS https://localhost/api/health
```

Sanitized formatter output:

```markdown
## Local Smoke Evidence

- Date/time UTC: 2026-06-02T19:20:49Z
- Environment class: local
- Workflow: local smoke
- Commit SHA: main-0390c35
- Check or command: scripts/smoke_test.ps1 / browser checklist summary
- Smoke runner status: pass
- API health: pass
- Web load: pass
- Browser checklist: not run
- Sanitized details: none
- Follow-up issue: none
- Secrets/private data/raw logs/screenshots with sensitive data included: no
- Cookies/tokens/browser storage/provider keys/.env values read or included: no
- Production-readiness, broker-readiness, real-money, profitability, live/realtime, trading-advice, or automatic-execution claim made: no
```

Stack and service results:

- Docker CLI: PASS, `Docker version 29.5.2, build 79eb04c`.
- Docker Compose CLI: PASS, `Docker Compose version v5.1.3`.
- Docker engine reachability: PASS.
- Docker Compose build and stack startup: PASS.
- PostgreSQL container health: PASS.
- Database migrations: PASS, `alembic upgrade head` completed in the local API
  container.
- API health: PASS, `/api/health` returned healthy status.
- Web build inside Docker: PASS; Next.js built 16 routes including
  `/reviews/[id]`, `/screener`, and `/trades/[id]`.
- Web HTTP load: PASS, `curl.exe -fsS -I http://localhost:3000` returned
  `HTTP/1.1 200 OK`.
- Local Caddy proxy startup: PASS, `caddy` started with the existing proxy
  profile and routed `/api/*` to the API container.
- Proxied API health: PASS, `curl.exe -k -fsS https://localhost/api/health`
  returned healthy status. `-k` was used only for the local self-signed Caddy
  certificate.
- Proxied login/session path: PASS. Local placeholder admin login succeeded
  through `https://localhost/api/auth/login`, and `/api/auth/me` returned `200`
  with the same session. Cookie values were not recorded.

Cockpit route checklist:

| Route | Desktop | Mobile | Evidence Notes |
| --- | --- | --- | --- |
| `/reviews/[id]` | pass | pass | Operator browser check confirmed Review Entries, `Suggested disposition: deferred`, evidence-only copy, Draft, and Edit are visible. Mobile emulation passed. |
| `/screener` | pass | pass | Operator mobile validation passed; no remaining mobile candidate-review friction reported. |
| `/trades/[id]` | pass | pass | Operator mobile validation passed; no remaining Manage/Close/Journal grouping friction reported. |

Known gaps from this run:

- Direct `http://localhost:3000` is suitable for web-load checks but not for
  authenticated browser validation, because the browser API base path is `/api`
  and requires same-origin proxy routing. Use `https://localhost` for local
  browser validation with the Caddy profile.
- No blocking desktop or mobile cockpit friction was reported by the operator
  validation. Issue `#515` can be closed without follow-up UI work unless later
  evidence contradicts this pass.
- The local stack was left running after validation so an operator can continue
  browser review at `https://localhost`. Tear down with
  `./scripts/smoke_test.ps1 -Cleanup` when finished.

Interpretation:

The v3.1 owner cockpit local validation passed for local Docker Compose build,
stack startup, current database migrations, API health, Docker web build, web
HTTP load, Caddy-routed same-origin browser access, proxied login/session, and
operator desktop/mobile cockpit review. This supports controlled internal
owner/operator review only. It is not a production-readiness statement,
broker-readiness statement, strategy validation, backtest, profitability claim,
real-money readiness claim, live/realtime data claim, trading advice, or
permission for automatic order execution.

## v3.1 VPS Update And Browser Smoke Evidence

Date: 2026-06-02

Environment:

- Host: `trading.cillyonline.de`
- Repo path: `/root/repos/cilly-trading-signal`
- Compose project: `cilly-trading-signal`
- Branch/commit after update: `main` at `b553f86`
- Deployment shape: VPS Docker Compose proxy stack with PostgreSQL, API, web,
  and Caddy.
- Operator model: VPS commands were executed manually by the operator and
  sanitized output was reviewed. No `.env`, cookies, tokens, provider keys,
  database URLs, private trading data, raw sensitive logs, or screenshots with
  private data were recorded.

Preflight summary:

- Git branch before update: `main`.
- Git status before update: clean, tracking `origin/main`.
- Commit before update: `e1d3e4c`.
- Disk space: PASS, root filesystem had substantial free space.
- Docker CLI: PASS, `Docker version 29.3.1`.
- Docker Compose CLI: PASS, `Docker Compose version v5.1.1`.
- Existing services before update: API, web, Caddy, and PostgreSQL were running;
  PostgreSQL was healthy.

Update commands recorded:

```bash
git fetch origin
git pull --ff-only origin main
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml --profile proxy up --build -d
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml exec -T api alembic upgrade head
docker compose --env-file .env -p cilly-trading-signal -f infra/docker-compose.yml exec -T api alembic current
```

Update results:

- Git update: PASS, fast-forwarded from `e1d3e4c` to `b553f86`.
- API image build: PASS.
- Web image build: PASS.
- Stack restart: PASS.
- PostgreSQL health after restart: PASS.
- Alembic upgrade: PASS.
- Alembic current: PASS, `20260531_0010 (head)`.
- Services after restart: PASS, API, web, Caddy, and PostgreSQL were running.

Smoke checks:

- Local VPS API health: PASS, `http://127.0.0.1:8000/api/health` returned
  healthy staging status according to operator-provided output.
- Public API health: PASS, `https://trading.cillyonline.de/api/health` returned
  healthy staging status from operator-provided output and from local follow-up
  verification.
- Public web load: PASS, `https://trading.cillyonline.de/` returned `HTTP 200`.
- Browser smoke: PASS, operator confirmed login and browser route smoke passed
  after the update.

Local follow-up verification from Windows:

```powershell
curl.exe --ssl-no-revoke -fsS https://trading.cillyonline.de/api/health
curl.exe --ssl-no-revoke -fsSI https://trading.cillyonline.de/
```

The `--ssl-no-revoke` flag was needed only because Windows Schannel could not
complete certificate revocation checking from this local environment. It was not
used to bypass a reported VPS application failure. The public API returned
healthy staging status and the public web endpoint returned `HTTP/1.1 200 OK`.

Known gaps and boundaries:

- This was a staging/VPS smoke for the current private operator deployment, not
  a production-readiness, broker-readiness, real-money, live/realtime,
  profitability, strategy-validation, trading-advice, or automatic-execution
  claim.
- No private account data, private trade data, provider credentials, cookies,
  tokens, database URLs, backup credentials, or raw sensitive logs were recorded.
- The separate `staging` Compose project on the host was observed as running and
  was not modified.

## v3.5 Existing VPS Public Route Partial Evidence

Date: 2026-06-03

Scope:

- Target: existing VPS at `trading.cillyonline.de`.
- Exposure: controlled private owner/operator staging only.
- Data class: sample, synthetic, and paper data only.
- Approved action class: non-destructive public route smoke only.

Checks run from the local Windows workspace:

```powershell
Invoke-RestMethod -Uri "https://trading.cillyonline.de/api/health" -Method GET
curl.exe --ssl-no-revoke -fsS https://trading.cillyonline.de/api/health
curl.exe --ssl-no-revoke -fsSI https://trading.cillyonline.de/
curl.exe -fsSI https://trading.cillyonline.de/
curl.exe -fsS https://trading.cillyonline.de/api/health
curl.exe -fsS https://trading.cillyonline.de/api/health/details
```

Results:

- Public API health via `Invoke-RestMethod`: PASS, returned healthy staging
  status with service `Cilly Trading Signal API`, version `0.1.0`, and
  environment `staging`.
- Public API health via `curl.exe --ssl-no-revoke`: PASS, returned healthy
  staging status.
- Public web route via `curl.exe --ssl-no-revoke`: PASS, returned `HTTP/1.1 200
  OK` through Caddy with Next.js response headers.
- Public web route via `Invoke-WebRequest -Method Head`: NOT CONCLUSIVE from this
  non-interactive PowerShell environment because `Invoke-WebRequest` attempted an
  interactive behavior that is unavailable in non-interactive mode.
- Public web/API checks via `curl.exe` without `--ssl-no-revoke`: NOT CONCLUSIVE
  from this Windows environment because Schannel certificate revocation checking
  failed with `CRYPT_E_NO_REVOCATION_CHECK`. This matches the known local Windows
  revocation-check limitation recorded in the v3.1 evidence; it is not evidence
  of a VPS application failure.

Not run in this partial check:

- SSH/VPS command checks.
- `git pull`, deployment, restart, migration, or rollback command.
- Compose status, container health, local VPS API route, or Alembic current.
- Browser login smoke.
- Restore drill, backup check, secret rotation, firewall, DNS, or private-data
  workflow.

Conclusion:

- This partial evidence supports that the public API health route was reachable
  and healthy, and that the public web route returned `HTTP 200`, from the local
  environment when using the same Windows Schannel revocation workaround recorded
  in v3.1.
- It does not satisfy the full v3.5 target deployment smoke and rollback
  readiness issue. Full completion still requires operator-guided VPS evidence
  for commit, service state, migration version, browser/login smoke, and rollback
  readiness.
- Production-like exposure and routine private trading data remain No Go.

## v3.5 Existing VPS Operator Smoke And Rollback Readiness Evidence

Date: 2026-06-03

Environment:

- Host: `trading.cillyonline.de`.
- Repo path: `/root/repos/cilly-trading-signal`.
- Compose project: `cilly-trading-signal`.
- Branch/commit: `main` at `b553f86`.
- Deployment shape: existing VPS Docker Compose proxy stack with PostgreSQL, API,
  web, and Caddy.
- Operator model: VPS commands and browser checks were run manually by the
  owner/operator. Sanitized pass/fail evidence was recorded only.

Scope:

- Controlled private owner/operator staging only.
- Sample, synthetic, and paper data only.
- Non-destructive smoke and rollback-readiness review only.
- No deployment, restart, migration, restore, backup, secret rotation, firewall,
  DNS, private-data, broker, or automatic-execution action was performed.

VPS status evidence:

- Git branch: PASS, `main`.
- Git commit: PASS, `b553f86`.
- Git status: PASS, clean and tracking `origin/main`.
- Compose project status: PASS, `cilly-trading-signal` running with four
  services.
- Services: PASS, API, web, Caddy, and PostgreSQL were running.
- PostgreSQL health: PASS, PostgreSQL container reported healthy.
- API direct port exposure: PASS for private operator check, API bound to
  `127.0.0.1:8000`.
- Web direct port exposure: PASS for private operator check, web bound to
  `127.0.0.1:3000`.
- Public Caddy route: PASS, Caddy exposed ports `80` and `443`.
- Alembic current: PASS, `20260531_0010 (head)`.
- Local VPS API health: PASS, `http://127.0.0.1:8000/api/health` returned
  healthy staging status.
- Public web route: PASS, `https://trading.cillyonline.de/` returned `HTTP 200`
  through Caddy.
- Compose isolation: PASS, unrelated `staging` Compose project was visible as a
  separate running project and was not modified.

Browser smoke evidence:

| Route or workflow | Result |
| --- | --- |
| Login page loads | PASS |
| Login succeeds | PASS |
| Dashboard loads | PASS |
| Watchlist page loads | PASS |
| Screener page loads | PASS |
| Import page loads | PASS |
| Signals page loads | PASS |
| Reviews page loads | PASS |
| Trades page loads | PASS |
| Performance page loads | PASS |
| Alerts page loads | PASS |
| Settings page loads | PASS |
| Logout succeeds | PASS |
| Protected page requires login after logout | PASS |

Rollback readiness review:

- Previous known-good process: documented in `docs/DEPLOYMENT_RUNBOOK.md#basic-rollback`.
- Rollback/migration decision matrix: documented in
  `docs/ROLLBACK_MIGRATION_SAFETY_CHECKLIST.md`.
- Current migration version known: PASS, `20260531_0010 (head)`.
- Migration state for this smoke: no migration was run; schema state was checked
  only.
- App-only rollback assumption: would require confirming previous app/schema
  compatibility before use.
- Restore decision point: any unclear schema state, partial migration, or data
  corruption concern must stop rollout and use disposable restore diagnosis
  before live repair.
- Backup freshness: not checked in this issue; handled separately by `#544`.
- Data-changing workflows: not performed as part of this smoke.

Known gaps and boundaries:

- This evidence satisfies the v3.5 target deployment smoke and rollback-readiness
  review for controlled private owner/operator staging only.
- This does not satisfy full monitoring escalation evidence; that remains tracked
  by `#543`.
- This does not satisfy offsite encrypted backup or restore-drill evidence; that
  remains tracked by `#544`.
- This is not production-like approval, private-data approval, broker-readiness,
  live/realtime readiness, profitability validation, strategy validation, trading
  advice, or approval for automatic execution.
- No `.env`, secrets, cookies, tokens, database URLs, raw logs, backup contents,
  private trading records, private screenshots, or restored rows were recorded.

## v2.9 Current-Main Local Validation Evidence

Date: 2026-06-02

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Branch/commit context: `main` at `9ddf365`
- Deployment shape: local Docker Compose stack with PostgreSQL, API, and web.
- Data scope: local/sample validation only; no private watchlists, broker data,
  account data, fills, provider credentials, cookies, screenshots, database dumps,
  raw logs, private notes, or production data were recorded.
- Browser/UI scope: web HTTP load was checked. The visual browser checklist was
  not run and remains operator-run evidence.

Commands and checks recorded:

```powershell
.\scripts\smoke_test.ps1 -TimeoutSeconds 180
curl.exe -fsS -I http://localhost:3000
.\scripts\smoke_test.ps1 -Cleanup
.\scripts\format_smoke_evidence.ps1 -CommitSha main-9ddf365 -SmokeRunnerStatus pass -ApiHealth pass -WebLoad pass -BrowserChecklist 'not run'
```

Sanitized formatter output:

```markdown
## Local Smoke Evidence

- Date/time UTC: 2026-06-02T18:07:35Z
- Environment class: local
- Workflow: local smoke
- Commit SHA: main-9ddf365
- Check or command: scripts/smoke_test.ps1 / browser checklist summary
- Smoke runner status: pass
- API health: pass
- Web load: pass
- Browser checklist: not run
- Sanitized details: Docker CLI and Compose available; local stack built and started; migrations applied; API health passed; web HTTP load passed; cleanup preserved volumes.
- Follow-up issue: none
- Secrets/private data/raw logs/screenshots with sensitive data included: no
- Cookies/tokens/browser storage/provider keys/.env values read or included: no
- Production-readiness, broker-readiness, real-money, profitability, live/realtime, trading-advice, or automatic-execution claim made: no
```

Stack and service results:

- Docker CLI: PASS, `Docker version 29.5.2, build 79eb04c`.
- Docker Compose CLI: PASS, `Docker Compose version v5.1.3`.
- Docker engine reachability: PASS.
- Docker Compose build and stack startup: PASS.
- PostgreSQL container health: PASS.
- Database migrations: PASS; migrations advanced the preserved local volume from
  `20260530_0008` through `20260531_0010`.
- API health: PASS, `/api/health` returned healthy status.
- Web HTTP load: PASS, `curl.exe -fsS -I http://localhost:3000` returned
  `HTTP/1.1 200 OK`.
- Cleanup: PASS, `./scripts/smoke_test.ps1 -Cleanup` stopped the stack with
  volumes preserved.

Known gaps from this run:

- The visual browser checklist was not run. Use
  `docs/FINAL_BROWSER_CLICKTHROUGH_CHECKLIST.md` for operator-run desktop/mobile
  browser evidence with sample, synthetic, or paper data only.
- No authenticated workflow data was created in this validation pass; the evidence
  covers local stack build/startup, migrations, API health, web load, formatter
  output, and cleanup.

Interpretation:

The v2.9 current-main local validation passed for local Docker Compose build,
stack startup, current database migrations, API health, web HTTP load, sanitized
evidence formatting, and cleanup. This supports controlled internal
owner/operator review only. It is not a production-readiness statement,
broker-readiness statement, strategy validation, backtest, profitability claim,
real-money readiness claim, live/realtime data claim, trading advice, or
permission for automatic order execution.

## v2.8 Final Internal Workflow Smoke

Date: 2026-05-31

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Branch used for attempt: `issue-340-final-internal-smoke-test`
- Deployment shape: local Docker Compose stack with PostgreSQL, API, and web.
- Data scope: local sample/synthetic data only; no real account data, private watchlists, provider credentials, cookies, session tokens, screenshots, logs with secrets, or production data were recorded.
- Browser/UI scope: web app HTTP load was checked; the end-to-end workflow was API-assisted because no browser automation or visual clickthrough harness is available in this environment.

Commands and checks recorded:

```powershell
.\scripts\smoke_test.ps1 -TimeoutSeconds 180
curl.exe --fail-with-body ... # authenticated sample-only API workflow; cookies and payload temp files not recorded
curl.exe -fsS -I http://localhost:3000
.\scripts\smoke_test.ps1 -Cleanup
```

Stack and service results:

- Docker CLI: PASS, `Docker version 29.5.2, build 79eb04c`.
- Docker Compose CLI: PASS, `Docker Compose version v5.1.3`.
- Docker engine reachability: PASS.
- Docker Compose build and stack startup: PASS.
- PostgreSQL container health: PASS.
- API health: PASS, `/api/health` returned `{"status":"ok","service":"Cilly Trading Signal API","version":"0.1.0","environment":"development"}`.
- Database migrations: PASS after running `alembic upgrade head` in the API container. The preserved local Docker volume had been behind current `main`, and migrations advanced it through market-data metadata, screener import, and review batch revisions.
- Web HTTP load: PASS, `curl.exe -fsS -I http://localhost:3000` returned `HTTP/1.1 200 OK`.
- Cleanup: PASS, `./scripts/smoke_test.ps1 -Cleanup` stopped the stack with volumes preserved.

Workflow results:

- Login/session: PASS with local development credentials from `.env.example`; no cookie or token value was recorded.
- Watchlist: PASS, created synthetic sample symbol `SMK34031132423` with `SAMPLE` exchange metadata.
- Screener CSV import: PASS, imported one synthetic candidate row from a temporary CSV outside the repository.
- Screener-to-Watchlist conversion: PASS, explicit conversion returned `watchlist_added` and did not create analysis, signal, trade, alert, broker action, order, buy/sell instruction, or trading advice automatically.
- Guarded provider sync: PASS for disabled-by-default behavior; manual provider sync returned `skipped` with `unknown` freshness because provider sync is not enabled locally.
- TradingView OHLCV CSV import: PASS for synthetic `1W`, `1D`, and `4H` fixtures under `test-data/csv/`, creating series ids `7`, `8`, and `9`.
- Analysis: PASS, analysis on series `9` generated signal id `2` with `no_setup` / `no_trade`, preserving conservative No Trade behavior for the sample data.
- Signal review note: PASS, an operator review note was added without any trade instruction.
- Review batch and entry: PASS, created paper review batch id `1` and entry id `1` with label `unclear`; this remains process evidence only, not backtesting or profitability validation.
- Manual trade record: PASS, created manual sample trade id `1`; no broker/account/order integration was involved.
- Trade management and close flow: PASS, added management note event id `1`, closed the sample trade as `closed`, and recorded sample `result_r` of `1.2000` as documentation evidence only.
- Journal review: PASS, created journal entry id `1` with sample-only process notes.
- Performance/risk review: PASS, performance summary showed `closed_trade_count=1`, open risk warning status `ok`, and `journal_analytics.reviewed_trade_count=1`.
- Alerts list: PASS, authenticated alert list returned zero alerts; no Telegram or external notification delivery was triggered.
- Logout: PASS, logout returned HTTP `204`.

Known gaps from this run:

- A visual browser clickthrough was not separately recorded because the environment has no browser automation or screenshot harness. Web container build and HTTP load passed, and the authenticated data workflow passed through API calls.
- The preserved local Docker volume required an explicit `alembic upgrade head` before current screener/review workflow tables existed. A fresh disposable stack or a migrated persistent stack should not treat missing tables as product smoke evidence.

Interpretation:

The v2.8 final internal workflow smoke passed for local Docker Compose startup, API health, current database migrations, web HTTP load, authenticated sample-only workflow coverage from Watchlist through Screener, CSV import, disabled provider-sync behavior, analysis, signal review, paper review batch entry, manual trade logging, management event, close flow, journal, performance/risk summary, alerts list, logout, and stack cleanup.

This evidence supports controlled internal owner/operator review only. It is not a production-readiness statement, broker-readiness statement, strategy validation, backtest, profitability claim, real-money readiness claim, live/realtime data claim, trading advice, or permission for automatic order execution.

## Previous Current Main Smoke Attempt

Date: 2026-05-30

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Branch used for attempt: `issue-264-269-v2-rebaseline`
- Scope: current-main Docker Compose smoke runner after v1.9 screener workflow completion.
- Data scope: no app data was loaded because the stack did not start.

Command:

```powershell
.\scripts\smoke_test.ps1 -TimeoutSeconds 180
```

Results:

- Docker CLI: PASS, `Docker version 29.1.3, build f52814d`.
- Docker Compose CLI: PASS, `Docker Compose version v2.40.3-desktop.1`.
- Docker engine reachability: BLOCKED. The runner could not connect to `npipe:////./pipe/dockerDesktopLinuxEngine` because the pipe was not found.
- Docker Compose stack startup: NOT RUN because Docker engine reachability failed.
- API health: NOT RUN because the stack did not start.
- Browser workflow: NOT RUN because the stack did not start.
- Screener-to-Watchlist browser smoke: NOT RUN because the stack did not start.

Observed blocker:

```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine;
check if the path is correct and if the daemon is running:
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

Interpretation:

The current-main smoke attempt did not validate the running application because Docker
Desktop's Linux engine was not reachable in the local environment. This is an
environment blocker, not a product pass. Rerun the same command after starting Docker
Desktop and confirming the Linux engine is available.

This blocked attempt does not claim production readiness, broker readiness,
profitability, strategy validation, live/realtime data, trading advice, or automatic
execution capability.

## Latest Run

Date: 2026-05-26

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Branch used for rerun: `issue-134-verify-staging-deployment-path-rerun`
- Deployment shape: Docker Compose proxy stack with PostgreSQL, API, web, and Caddy.
- Scope: staging/VPS-like local rerun after `#139` was merged.
- Data scope: local/sample smoke-test data only.

Commands and checks recorded:

```powershell
docker compose -f .\infra\docker-compose.yml --profile proxy up --build -d
docker compose -f .\infra\docker-compose.yml --profile proxy ps
curl.exe -fsS http://localhost:8000/api/health
curl.exe -k -fsS https://localhost/api/health
curl.exe -k -I https://localhost
```

Additional frontend bundle check:

```powershell
docker compose -f .\infra\docker-compose.yml --profile proxy exec web sh -lc "grep -R 'http://localhost:8000/api' -n .next server.js 2>/dev/null | head -20 || true"
```

Result: returned no output.

Results:

- Docker Compose proxy stack rebuild: PASS.
- PostgreSQL container health: PASS, Postgres reported healthy.
- API service: PASS, running.
- Web service: PASS, running.
- Caddy service: PASS, running.
- Direct API health: PASS with `curl.exe -fsS http://localhost:8000/api/health`.
- Caddy API health: PASS with `curl.exe -k -fsS https://localhost/api/health`.
- Caddy web load: PASS, `curl.exe -k -I https://localhost` returned `HTTP/1.1 200 OK` through Caddy.
- Frontend API base URL bundle check: PASS, grep for `http://localhost:8000/api` returned no output.

Browser workflow results:

- Login/session: PASS. Login succeeded and authenticated browser workflow continued.
- Dashboard: PASS. Dashboard loaded successfully after login.
- Watchlist: PASS. Watchlist page loaded while authenticated.
- CSV import: PASS. CSV import page loaded and sample CSV import worked.
- Analysis: PASS. Analysis completed and produced a conservative `No Setup` / `No Trade` result under the strategy and risk rules. This is an expected conservative outcome, not a failed workflow.
- Signals: PASS. Signals page loaded and showed the persisted AAPL `No Setup` signal.
- Signal detail: PASS. Detail view loaded and showed reasoning, no-trade reasons, risk flags, and safety wording.
- Trades page: PASS. Trades page loaded and showed manual trade logging only.
- Logout: PASS. Logout completed.
- Protected data after logout: PASS for data protection. After logout, protected API data was not accessible.

Known gap from rerun:

- After logout, opening `/watchlist` still renders the page shell and shows `Watchlist konnte nicht geladen werden` instead of redirecting cleanly to login. This is a UX/auth-guard follow-up gap. It was not observed to expose protected data.

Interpretation:

The staging/VPS-like Docker Compose proxy path passed this rerun for stack rebuild, service health, Caddy-routed API and web access, same-origin frontend API configuration, authenticated browser workflow, conservative analysis output, signal review, manual trade logging page access, logout, and protected API data behavior after logout.

This evidence closes the previously documented release-validation blocker path for `#132` and the Caddy HTTPS frontend API base URL blocker fixed by `#139`. It does not claim production readiness, profitability, strategy validation, trading advice, broker integration, or automatic trading.

## Previous Run

Date: 2026-05-17

Environment:

- Windows workspace: `C:\repos\cilly-trading-signal`
- Branch: `issue-131-browser-mvp-smoke-test`
- Docker CLI: `Docker version 29.1.3, build f52814d`
- Docker Compose CLI: `Docker Compose version v2.40.3-desktop.1`
- Docker Desktop Linux engine: reachable after starting Docker Desktop
- Docker Server: `29.1.3`
- Docker OS: Docker Desktop / Linux / WSL2
- Sample CSV fixtures: available under `test-data/csv/`

Commands attempted:

```powershell
.\scripts\smoke_test.ps1
docker compose -f .\infra\docker-compose.yml ps
Test-Path .\public
Test-Path .\apps\web\public
Get-Content .\infra\docker-compose.yml
Get-Content .\apps\web\Dockerfile
```

Results:

- `docker CLI`: PASS
- `docker compose`: PASS
- Docker engine reachability: PASS after Docker Desktop was started
- Compose file presence: PASS
- `.env` presence: PASS, created from `.env.example` by the smoke runner
- Docker Compose stack startup: BLOCKED
- API health check: NOT RUN because stack startup was blocked
- Browser login: NOT RUN because stack startup was blocked
- Full browser workflow: NOT RUN because the web image build failed before the app became available

Observed blocker:

```text
Dockerfile:15

COPY --from=builder /app/public ./public

target web: failed to solve: failed to compute cache key:
failed to calculate checksum of ref ...:
"/app/public": not found
```

Additional evidence:

```powershell
docker compose -f .\infra\docker-compose.yml ps
```

Result:

```text
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
```

No services were running after the failed startup attempt.

```powershell
Test-Path .\public
Test-Path .\apps\web\public
```

Result:

```text
False
False
```

Interpretation:

The local Docker engine is now reachable, but the release-validation stack cannot start because the web Docker build expects `/app/public` in the Next.js builder stage while no `public` directory exists in the current repository checkout. This blocks the browser-based MVP smoke test before login, CSV import, analysis, signal review, manual paper trade, close, journal, and performance steps can be attempted.

This is a reproduced smoke-test defect and should be handled under follow-up issue `#132`. No product feature changes, strategy/scoring changes, broker integration, automatic order execution, real trading data, secrets, or personal journal data were introduced or used.

## Coverage Matrix

| Area | Result | Notes |
| --- | --- | --- |
| Docker Compose proxy stack rebuild | PASS | Stack rebuilt successfully with the proxy profile. |
| PostgreSQL health | PASS | Postgres reported healthy. |
| API service | PASS | API was running and direct health passed. |
| Web service | PASS | Web was running and loaded through Caddy. |
| Caddy service | PASS | Caddy was running and routed API and web requests. |
| Direct API health | PASS | `curl.exe -fsS http://localhost:8000/api/health` passed. |
| Caddy API health | PASS | `curl.exe -k -fsS https://localhost/api/health` passed. |
| Caddy web load | PASS | `curl.exe -k -I https://localhost` returned `HTTP/1.1 200 OK`. |
| Frontend API base URL bundle check | PASS | Grep for `http://localhost:8000/api` returned no output. |
| Login/session | PASS | Authenticated browser workflow continued after login. |
| Dashboard review | PASS | Dashboard loaded successfully after login. |
| Watchlist workflow | PASS | Watchlist page loaded while authenticated. |
| CSV import | PASS | CSV import page loaded and sample CSV import worked. |
| Analysis and signal review | PASS | Analysis completed with conservative `No Setup` / `No Trade`, which is valid under risk rules. |
| Signals list | PASS | Signals page showed the persisted AAPL `No Setup` signal. |
| Signal detail review | PASS | Detail showed reasoning, no-trade reasons, risk flags, and safety wording. |
| Manual trade logging page | PASS | Trades page loaded and showed manual trade logging only. |
| Logout | PASS | Logout completed. |
| Protected API data after logout | PASS | Protected API data was not accessible after logout. |
| Protected route UX after logout | FOLLOW-UP | `/watchlist` renders a page shell with `Watchlist konnte nicht geladen werden` instead of cleanly redirecting to login. No protected data exposure was observed. |
| Safety wording review | PASS | Signal detail and workflow kept decision-support, No Trade, risk, and manual execution boundaries visible. |

## Sample Data

Deterministic paper/sample CSV fixtures live under `test-data/csv/` and are
the canonical input for the import + analysis portion of this smoke flow.
They are synthetic OHLCV curves — not market data — and exist only to make
this workflow reproducible without exposing personal trading data.

| File | Timeframe | Candles |
| --- | --- | --- |
| `test-data/csv/sample_paper_1w.csv` | 1W | 60 |
| `test-data/csv/sample_paper_1d.csv` | 1D | 250 |
| `test-data/csv/sample_paper_4h.csv` | 4H | 250 |

Suggested smoke workflow with these fixtures:

1. In the web app, add a watchlist item with a clearly fake symbol (for
   example `SMOKE-PAPER-001`, asset class `stock`, exchange `SAMPLE`).
2. Upload each CSV from the Import page, selecting the matching timeframe.
3. From the import history, run analysis to generate signals.
4. Continue through the manual trade/journal/performance steps using only
   sample values.

Regenerate the fixtures with `python scripts/generate_smoke_fixtures.py`
if they are ever removed; output is deterministic.

See `test-data/csv/README.md` for the full safety scope of these fixtures.

## Follow-Up Issues

- `#132` Fix defects found during MVP smoke test. Status: no longer an active smoke-test blocker in the latest documented rerun; the Docker Compose proxy stack rebuilt and started successfully.
- `#139` Fix Caddy HTTPS frontend API base URL. Status: no longer an active smoke-test blocker in the latest documented rerun; Caddy-routed API health passed and the frontend bundle check found no `http://localhost:8000/api` reference.
- `#133` Add release candidate checklist status update.
- UX/auth-guard follow-up: after logout, opening `/watchlist` renders the page shell with `Watchlist konnte nicht geladen werden` instead of redirecting cleanly to login. Protected API data was not accessible.

## Next Smoke-Test Requirements

For future reruns, preserve the following evidence:

- Docker Desktop Linux engine running and reachable.
- Docker Compose stack startup passing successfully.
- API health endpoint reachable.
- Deterministic sample/paper CSV files for `1W`, `1D`, and `4H` committed under `test-data/csv/`.
- A browser pass through the complete manual workflow.
- Follow-up issues opened for any material product defects discovered.

## Cleanup Notes

The temporary local `.env` created during this run remains local and must not be committed. If future smoke runs create local data, logs, screenshots, or exports, review them for secrets or personal trading data before sharing.

For disposable local demo data only, use the reset safety procedure in [Disposable Demo Data Reset](DEPLOYMENT_RUNBOOK.md#disposable-demo-data-reset). Do not delete staging, production-like, or real-data volumes as part of smoke-test cleanup.
