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

### Reviewed-Example Golden Case Template

Use this template when converting a historical/paper review finding into a
deterministic golden case. Fill it out before changing strategy implementation.

```markdown
## Golden Case: <short_descriptive_name>

### Source Review Evidence

- Review batch: <batch name or id>
- Review entry ids: <ids or local references>
- Manual review label: useful / too_permissive / too_strict / unclear
- Repeated blocker or finding: <blocker code, label, or none>
- Repeated false-positive pattern: <pattern code or none>
- Follow-up disposition: created / accepted limitation / deferred / not applicable
- Linked follow-up issue: <issue url or none>
- Sanitized observation: <short description with no private account data>

### Safety Boundary

- This case is deterministic review evidence only.
- It is not a backtest, profitability claim, trading advice, live-data claim,
  broker-readiness claim, or execution workflow.
- No private broker/account/fill data is included.

### Fixture Inputs

- Strategy: trend_pullback_long / base_breakout_long / no_strategy
- Asset class: stock / crypto
- Symbol: synthetic or public ticker only
- Timeframes: 1W / 1D / 4H present or explicitly missing
- Benchmark context: present / missing / stale / failed / partial / unknown
- Asset-specific overlay: stock earnings/liquidity or crypto ATR/liquidity/wick risk
- OHLCV fixture source: synthetic / anonymized public / minimal object

### Expected State Coverage

- Pass state: <what should pass, if any>
- Warning state: <risk flag, missing context, stale context, or caution>
- Blocked state: <No Trade reason or blocker, if applicable>

### Expected Output

- Expected status: watchlist / armed / triggered / no_setup / invalidated / missed / expired
- Expected score class: a_setup / b_setup / watchlist / no_trade
- Expected no-trade reasons: <codes or none>
- Expected risk flags: <codes or none>
- Expected quality report states: passed / warning / missing / blocked
- Expected next action: <manual review wording, no buy/sell instruction>
- Expected risk plan: entry / stop / target / R:R or explicit reason unavailable

### Regression Intent

- What future regression should this case catch?
- Would a failure mean rules are too permissive, too strict, or unclear?
- Does the case preserve `No Trade` or `Watchlist` as an acceptable conservative
  outcome when context, confirmation, or risk planning is incomplete?
```

Pass, warning, and blocked coverage expectations:

- A pass state should prove only that the documented setup requirement is present;
  it must not imply a trade instruction.
- A warning state should keep the candidate reviewable only when the playbook allows
  it and the risk/context limitation is visible.
- A blocked state should preserve `No Trade` as a successful conservative outcome.
- Missing, stale, failed, partial, or unknown data should be tested explicitly when
  that context caused the review finding.

Anonymized OHLCV and benchmark fixture guidance:

- Prefer synthetic OHLCV series that isolate one behavior, such as pullback depth,
  breakout close, volume confirmation, or stale benchmark context.
- If using a public example, transform prices and volumes while preserving shape,
  order, gaps, wick structure, and relative volume relationships needed by the rule.
- Never include brokerage fills, account size, realized P/L, screenshots, API keys,
  or private notes.
- Keep benchmark fixtures explicit: include enough `SPY`/`QQQ` or `BTC`/`ETH`
  context to prove present/missing/stale/failed/partial/unknown behavior.

Test naming convention:

- Unit-style golden cases: `test_calibration_<strategy>_<expected_state>_<reason>`.
- End-to-end stored fixture cases:
  `test_calibration_e2e_<asset_class>_<strategy>_<finding>`.
- Use reason codes in names where practical, for example
  `test_calibration_trend_pullback_no_trade_stale_benchmark_context`.
- Keep one behavioral assertion focus per test. If one reviewed example reveals
  multiple unrelated findings, split it into separate golden cases.

## Evidence Sample Before Rule Changes

Before changing strategy behavior from review observations, collect the first
structured historical/paper review sample described in
`docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md`.

The first 80-example paper calibration batch is recorded in
`docs/reviews/first-50-paper-calibration-batch.md`.

Minimum evidence gate:

- At least 50 examples are reviewed, with a preferred first pass of 80 examples.
- Stocks and crypto are both represented, or the shortfall is explicitly recorded.
- Trend Pullback Long, Base Breakout Long, Watchlist, No Trade, and missing/stale
  context cases are all represented.
- `too_permissive`, `too_strict`, and repeated `unclear` labels become follow-up
  issues or are explicitly accepted as limitations.
- No rule change is made only because a small sample has attractive or unattractive
  paper outcomes.

Interpretation rules:

- `too_permissive` evidence usually supports tightening, clearer blockers, or
  stronger No Trade wording.
- `too_strict` evidence requires a golden case before any loosening is considered.
- Repeated `unclear` evidence usually supports explanation, next-action, or quality
  report improvements before score changes.
- Missing/stale context evidence should preserve conservative behavior and visible
  No Trade gates.

This gate does not validate profitability or live readiness. It only determines
whether deterministic rule work has enough structured review evidence to proceed.

The current backend golden-case suite can be run with:

```powershell
cd apps/api
uv run --no-project --with pytest --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" pytest tests/test_calibration_golden_cases.py
```

When `uv` is unavailable locally, run the same test file with the active API test
environment's Python interpreter.

End-to-end stored OHLCV and benchmark-context calibration fixtures can be run with:

```powershell
cd apps/api
uv run --no-project --with pytest --with "fastapi[standard]" --with pydantic-settings --with sqlalchemy --with "psycopg[binary]" pytest tests/test_calibration_e2e_fixtures.py
```

These fixtures exercise stored watchlist items, `1W`/`1D`/`4H` series, benchmark
context, signal orchestration, and analysis quality report states. They are still
deterministic review fixtures, not backtests or profitability evidence.

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

## Too-Strict Review Decision Gate

Repeated `too_strict` findings should be reviewed conservatively. They do not
automatically justify lower thresholds or more A/B setups.

Current v2.4 decision:

- Missing trigger confirmation remains `Watchlist`, not `No Trade`, when the setup
  has a coherent risk plan and no hard blocker.
- The golden case
  `review_finding_too_strict_watchlist_missing_trigger_not_blocked` protects this
  behavior.
- No loosening is currently justified for missing/stale context, incoherent risk
  plans, bearish regime, nearby strong resistance, uncontrolled pullbacks, wide
  bases, unclear base highs, or extended breakouts.
- A future loosening must cite a specific golden case and must not turn weak or
  incomplete setups into `A-Setup` or `B-Setup` without coherent stop, target,
  invalidation, and minimum R:R.

Preferred outcomes for repeated `too_strict` findings:

- Improve wording or `next_action` when the blocker is correct but confusing.
- Add a golden case when the playbook clearly says the case should remain
  reviewable.
- Keep conservative No Trade behavior when data quality, market regime, trigger,
  structure, or risk plan is incomplete.

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

The historical/paper review protocol is documented in
`docs/HISTORICAL_PAPER_REVIEW_PROTOCOL.md`.
