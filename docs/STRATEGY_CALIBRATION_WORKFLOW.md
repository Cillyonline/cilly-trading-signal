# Strategy Calibration Workflow

## Purpose

This workflow defines how strategy rules should be changed, tested, and reviewed.
The goal is professional signal quality: fewer weak signals, clearer No Trade
filters, better risk plans, and more explainable manual review output.

This is not strategy validation, trading advice, a profitability claim,
broker-readiness evidence, a live/realtime data claim, or permission for automatic
order execution. It is an engineering and review workflow for deterministic signal
rules.

## Calibration Loop

Use this loop for every strategy behavior change:

1. Define the playbook rule: write the intended trader-facing rule before changing
   code. Reference `docs/PROFESSIONAL_STRATEGY_PLAYBOOK.md` and
   `docs/ASSET_SPECIFIC_SIGNAL_FILTERS.md`.
2. Create deterministic fixtures: add synthetic or anonymized test cases that cover
   the intended pass, warning, missing, and blocked states.
3. Assign expected labels: decide whether each case should produce `A-Setup`,
   `B-Setup`, `Watchlist`, or `No Trade` before adjusting implementation.
4. Run the audit: compare actual score, status, no-trade reasons, next action, and
   analysis quality report against expected labels.
5. Adjust rules conservatively: prefer tightening weak signals, improving gates, or
   clarifying risk plans over loosening rules to produce more signals.
6. Rerun tests: backend strategy tests, API tests, and UI build must pass for the
   changed surface.
7. Review outcomes: verify wording is trader-readable and does not imply a trade,
   automatic execution, live data, or expected profit.
8. Document residual gaps: if a known limitation remains, create a follow-up issue
   instead of hiding it in the implementation.

## Golden Cases

Golden cases are deterministic fixtures that represent expected professional
review outcomes. They should be small, explicit, and safe to share in the repo.

Allowed sources:

- Synthetic OHLCV series built for a specific setup or blocker.
- Publicly describable examples converted into anonymized values.
- Minimal strategy input objects that isolate one rule.
- Stored CSV snippets only if they contain no private account, broker, or personal
  data.

Disallowed sources:

- Private brokerage data, account data, fills, statements, or screenshots.
- Claims that a fixture proves profitability.
- Fixtures that require a live provider, realtime feed, broker API, or automatic
  trading path.

Each golden case should state:

- Setup type: Trend Pullback Long, Base Breakout Long, or fallback/no strategy.
- Asset context: stock or crypto and any benchmark context used.
- Expected quality class and status.
- Expected no-trade reasons or risk flags.
- Expected next manual review action.
- Risk-plan expectation: entry, stop, target, and minimum R:R where applicable.

The current backend golden-case suite can be run with:

```powershell
cd apps/api
uv run --no-project --with pytest --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" pytest tests/test_calibration_golden_cases.py
```

When `uv` is unavailable locally, run the same test file with the active API test
environment's Python interpreter.

## Interpreting Outputs

`A-Setup` should be rare. It means the stored context, setup, trigger plan, and
risk plan are aligned and no hard blocker is active. It is still review support,
not an instruction.

`B-Setup` means the setup is valid enough for manual review but has visible
limitations. Risk flags or missing context should be read before any external
manual decision.

`Watchlist` means the candidate is developing but not ready for trigger review.
The next action should state what must happen before the setup can be reviewed
again.

`No Trade` means the system intentionally blocked the setup. This is a successful
risk-control outcome when context, structure, trigger, data quality, or risk plan
is not acceptable.

## Required Checks Before Rule Loosening

Do not loosen a rule only because the engine produces too few signals. Before any
loosening:

- Add at least one golden case that proves the currently blocked setup should be
  reviewable under the professional playbook.
- Confirm the setup has a coherent stop, target, invalidation, and minimum R:R.
- Confirm benchmark/regime and asset-specific missing-context behavior remains
  visible.
- Confirm No Trade remains available for weak or incomplete setups.
- Run relevant backend tests and, for UI output changes, `npm run build`.

If the tests need to be weakened to pass, the rule change is probably not ready.

## Review Checklist

For each calibration PR, reviewers should check:

- Does the change improve signal quality rather than just signal quantity?
- Are No Trade blockers explicit and trader-readable?
- Does `next_action` tell the user what to wait for or verify manually?
- Does the analysis quality report show passed, warning, missing, and blocked
  states consistently?
- Are stocks and crypto handled through their appropriate overlays?
- Are safety boundaries preserved: no broker action, automatic order, live/realtime
  claim, profitability claim, or trading advice?

## Residual Risk

Passing calibration tests does not prove positive expectancy, profitability, or
production readiness. It only proves that deterministic rules match the documented
playbook and fixtures. Separate historical or paper review with enough examples is
required before making any stronger statement about strategy performance.
