# MVP Smoke Test

## Purpose

This document records the MVP smoke-test workflow and the latest validation result for the manual trading cockpit. The smoke test uses local/sample data only and does not make a production-readiness, profitability, or execution claim.

## Safety Scope

- Signals are review prompts, not buy/sell instructions.
- The app must not create broker orders or connect to a broker.
- Trades in this smoke test are manual documentation records only.
- Performance views show documented historical/paper results, not forecasts.

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
| Docker CLI availability | PASS | Docker CLI returned `Docker version 29.1.3, build f52814d`. |
| Docker Compose CLI availability | PASS | Compose returned `Docker Compose version v2.40.3-desktop.1`. |
| Docker engine reachability | PASS | Initially unavailable, then reachable after Docker Desktop was started. |
| Compose stack startup | BLOCKED | Web image build failed because `/app/public` was not found during Dockerfile runner-stage copy. |
| API health | NOT RUN | Requires running stack. |
| Web login | NOT RUN | Requires running stack. |
| Watchlist workflow | NOT RUN | Requires running stack. |
| CSV import 1W fixture | NOT RUN | Requires running stack. Fixture exists at `test-data/csv/sample_paper_1w.csv`. |
| CSV import 1D fixture | NOT RUN | Requires running stack. Fixture exists at `test-data/csv/sample_paper_1d.csv`. |
| CSV import 4H fixture | NOT RUN | Requires running stack. Fixture exists at `test-data/csv/sample_paper_4h.csv`. |
| Analysis and signal review | NOT RUN | Requires running stack and imported sample data. |
| Signal detail review | NOT RUN | Requires generated or persisted signals. |
| Manual paper trade logging | NOT RUN | Requires running stack and sample signal/trade data. |
| Trade close flow | NOT RUN | Requires manual paper trade record. |
| Journal review | NOT RUN | Requires closed manual paper trade record. |
| Performance review | NOT RUN | Requires trade records. |
| Alerts review | NOT RUN | Requires running stack. |
| Settings review | NOT RUN | Requires running stack. |
| Dashboard review | NOT RUN | Requires running stack. |
| Safety wording review | NOT RUN | Full browser review requires running stack. Existing smoke document keeps decision-support and no-execution boundaries explicit. |

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

- `#132` Fix defects found during MVP smoke test. Current reproduced blocker: web Docker build fails because `apps/web/Dockerfile` copies `/app/public`, but no `public` directory exists in the web build context.
- `#133` Add release candidate checklist status update.

## Next Smoke-Test Requirements

Before marking the MVP smoke flow as passed, rerun this document with:

- Docker Desktop Linux engine running and reachable.
- Docker Compose stack startup passing successfully.
- API health endpoint reachable.
- Deterministic sample/paper CSV files for `1W`, `1D`, and `4H` committed under `test-data/csv/`.
- A browser pass through the complete manual workflow.
- Follow-up issues opened for any material product defects discovered.

## Cleanup Notes

The temporary local `.env` created during this run remains local and must not be committed. If future smoke runs create local data, logs, screenshots, or exports, review them for secrets or personal trading data before sharing.
