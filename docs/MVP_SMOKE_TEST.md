# MVP Smoke Test

## Purpose

This document records the MVP smoke-test workflow and the latest validation result for the manual trading cockpit. The smoke test uses local/sample data only and does not make a production-readiness, profitability, or execution claim.

For the private VPS staging smoke-test procedure and evidence template, see `docs/VPS_STAGING_SMOKE_TEST.md`.
For the guarded manual provider sync checklist, see `docs/PROVIDER_SYNC_SMOKE_TEST.md`.

## Safety Scope

- Signals are review prompts, not buy/sell instructions.
- The app must not create broker orders or connect to a broker.
- Trades in this smoke test are manual documentation records only.
- Performance views show documented historical/paper results, not forecasts.
- Provider sync smoke evidence, if run separately, validates only guarded stored-data
  sync behavior and is not live/realtime or production-readiness evidence.

## Runner

The `scripts/smoke_test.ps1` runner automates preflight, stack startup, and
the API health check. It does not replace the browser portion of the smoke
test — it only reduces manual setup ambiguity.

```powershell
# Bring the stack up and wait for /api/health
.\scripts\smoke_test.ps1

# Bring the stack down (volumes preserved)
.\scripts\smoke_test.ps1 -Cleanup

# Bring the stack down and wipe the Postgres volume
.\scripts\smoke_test.ps1 -Cleanup -PurgeVolumes
```

The runner fails fast with a clear `[FAIL]` message when the Docker engine
pipe is unreachable. Browser steps (login, watchlist, CSV import, analysis,
trade log, journal, performance) continue manually using the fixtures under
`test-data/csv/`.

This script is release-validation tooling, not a production deployment claim.

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
