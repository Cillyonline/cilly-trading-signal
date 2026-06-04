# v3.9 Low-Friction CSV Workflow Review

Date: 2026-06-04

Scope: Review the v3.9 CSV import workflow from real TradingView-style files through
bulk import, readiness, explicit batch analysis, docs, and follow-up planning.

## Summary

v3.9 materially reduces the 12-file workflow friction. The operator no longer has
to manually prepare VPS-compatible CSV headers for common TradingView exports,
can select multiple files in one import session, can inspect detected filename
metadata, can see grouped readiness by symbol, and can explicitly analyze complete
symbols in one batch action.

The workflow remains decision-support only. There is still no automatic analysis
after upload, no broker integration, no order execution, no alerts from this path,
and no profitability or live/realtime claim.

## Evidence

- #564 / PR #590 accepted TradingView header and timestamp variants:
  case-insensitive headers, `Volume`, Unix epoch seconds, and Unix epoch milliseconds.
- #565 / PR #591 added multi-file CSV selection and per-file success/error results.
- #566 / PR #592 added filename detection for common TradingView names, including
  exchange-prefixed names and `240 = 4H`.
- #567 / PR #593 added grouped Import Readiness for `1W`, `1D`, and `4H`, using
  saved usable imports plus the current filename preview.
- #568 / PR #594 added an explicit Analyze-All action for complete imported symbols,
  skipped incomplete symbols with visible reasons, and showed per-symbol Ampel/radar
  decisions.
- #569 / PR #595 documented bulk CSV steps, filename rules, preview-vs-saved-data
  boundaries, error cases, CSV-as-fallback language, and private-data exclusions.

## Workflow Assessment

12-file import flow:

- Before v3.9, the operator had to normalize files manually, import each file one
  by one, mentally track symbol/timeframe coverage, and run analysis symbol by
  symbol.
- After v3.9, the operator can select files together, inspect filename detection,
  import sequentially through the existing safe endpoint, see per-file failures,
  check symbol readiness, and run one explicit batch analysis for complete symbols.
- Remaining manual checks are intentional: symbol/timeframe assignment is still
  manually selected for import, and filename preview is a guardrail rather than
  automatic routing.

Operator independence:

- Docs now explain supported filenames, `240 = 4H`, bulk steps, readiness semantics,
  skipped reasons, and private-data boundaries.
- The operator should be able to run the import workflow without technical help
  when files use documented TradingView-style names.
- Ambiguous filenames, wrong symbol/timeframe selection, failed imports, and missing
  timeframes are visible blockers instead of silent success.

Mobile and density:

- The import page uses responsive cards and stacked controls, so the flow remains
  usable on smaller screens.
- A 12-file batch still produces many result cards. This is acceptable for v3.9,
  but denser grouping/filtering would improve repeated use.

## Boundaries Checked

- No automatic order execution was added.
- No broker integration was added.
- No automatic analysis after upload was added; Analyze-All requires an explicit click.
- No private broker/account data is requested by docs or UI.
- CSV and provider data remain explicit stored-data inputs, not live/realtime claims.
- Conservative outcomes, skipped symbols, `Kein Trade`, and `Datenproblem` remain
  first-class outcomes.

## Known Gaps

- Filename preview does not automatically route each file to its detected symbol and
  timeframe. This prevents accidental automation, but still requires careful manual
  import grouping.
- Import Readiness combines saved usable imports with the current filename preview,
  so operators must not treat preview-only readiness as proven data before submit.
- Analyze-All currently starts from complete saved symbols and does not display a
  compact batch progress summary beyond per-symbol cards.
- The UI does not yet provide a single 12-file drag-and-drop mapping table with
  editable symbol/timeframe assignments.
- Backend verification is CI-based locally because `uv` is not installed on this
  machine.

## Follow-Up Issues

Created from this review:

- #596 `web: add CSV file mapping table before bulk import` - priority p1.
- #597 `web: add compact batch analysis summary and filters` - priority p2.
- #598 `docs: add 12-file CSV operator walkthrough with examples` - priority p2.

## Verification

- `git diff --check -- docs/reviews/v3-9-low-friction-csv-workflow-review.md docs/DELIVERY_ROADMAP.md`

Skipped:

- Frontend build and backend tests were not run for this review-only documentation
  change. Prior v3.9 implementation PRs ran CI and the relevant local frontend or
  diff checks documented in their PRs.

## Decision

v3.9 meets its goal for a materially easier low-friction CSV workflow while staying
inside manual decision-support boundaries. It is ready to close after the follow-up
issues above are filed and linked.
