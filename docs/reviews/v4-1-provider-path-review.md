# v4.1 Provider Path Review

Date: 2026-06-04

Scope: Review the v4.1 provider-path decision, provider capability matrix, web
operator workflow, secret/VPS operation boundaries, and follow-up planning.

## Summary

v4.1 keeps the market-data provider path intentionally narrow. Alpha Vantage remains
the first practical guarded Daily/EOD smoke path because the adapter already exists
and is enough to validate provider plumbing, freshness states, sanitized failures,
and operator workflow. TradingView CSV remains the baseline and fallback for full
`1W`, `1D`, and `4H` multi-timeframe analysis.

The milestone is conservative and reviewable. It does not select a paid provider,
does not enable provider sync by default, does not add scheduler behavior, does not
change VPS secrets, and does not claim live/realtime market data. The main remaining
gap is operational evidence: a real provider-key smoke or broader provider decision
still requires explicit owner/operator approval, sanitized evidence, and licensing
review.

## Evidence

- #575 / PR #609 documented the provider decision in
  `docs/MARKET_DATA_PROVIDER_DECISION.md`: Alpha Vantage is the first practical
  Daily/EOD smoke path, while paid/provider reliance remains deferred.
- #575 preserved TradingView CSV as the required fallback for complete `1W`, `1D`,
  and `4H` workflows.
- #576 / PR #610 added backend provider timeframe capabilities to sync responses.
  Current Alpha Vantage capabilities are explicit: `1D` supported, `1W` and `4H`
  unsupported with CSV fallback guidance.
- #576 catches unsupported timeframes before provider calls and returns sanitized
  `unsupported_timeframe` failure context instead of raw provider details.
- #577 / PR #611 changed the web operator action to `Daten aktualisieren`, added
  capability hints, and kept manual-only/no-live-signal language visible.
- #578 / PR #612 documented provider-key handling, explicit VPS restart approval,
  sanitized smoke evidence, and rollback boundaries.

## Review Findings

No release-blocking defects were found in the merged v4.1 scope.

Important non-blocking gaps:

- There is no approved VPS/provider-key smoke evidence for a configured real
  provider key. This is intentional until the owner/operator explicitly approves
  setting or rotating a key and restarting the target environment.
- The current provider path does not solve `4H`/intraday data. That gap is visible
  and safely routed to TradingView CSV fallback.
- Broader provider reliance still needs watchlist size, symbol coverage, pricing,
  rate-limit, storage-rights, and licensing review before selecting a paid provider.
- The provider capability matrix is currently static for the implemented first path.
  That is acceptable while only Alpha Vantage Daily/EOD is implemented, but future
  providers should keep capability output provider-specific and tested.

## Safety Boundaries Checked

- No automatic order execution was added.
- No broker integration was added.
- No scheduler or background provider sync was added.
- No automatic analysis, signal generation, alert creation, or trade creation was
  added from provider sync.
- No provider secret, `.env` value, account ID, subscription detail, raw provider
  payload, or VPS setting was added to the repository.
- No live/realtime data, public production readiness, broker readiness, strategy
  validation, or profitability claim was added.
- Stale, failed, partial, unknown, and unsupported-timeframe states remain visible
  and conservative.

## Follow-Up Issues

Created from this review:

- #613 `docs: define paid provider evaluation checklist` - priority p2.
- #614 `review: provider daily EOD smoke after explicit key approval` - priority p2.

Recommended order:

1. Complete #613 before choosing or paying for a broader provider path.
2. Complete #614 only after explicit owner/operator approval to configure or test a
   provider key in the target environment.
3. Keep #605 separate for Trigger Radar VPS smoke after the next approved deployment.

## Verification

- `git diff --check -- docs/reviews/v4-1-provider-path-review.md docs/DELIVERY_ROADMAP.md`

Skipped:

- Frontend and backend builds were not run for this review-only documentation
  change. The implementation PRs documented their relevant checks and passed CI.
- VPS/provider-key smoke was not run because #579 explicitly excludes VPS deployment
  and real provider keys.

## Decision

v4.1 is conservative enough to proceed to v4.2 final audit work. The current provider
path may be used only as guarded stored-data Decision Support for manual Daily/EOD
updates, with CSV fallback for unsupported timeframes. Broader provider reliance,
real-key VPS smoke, intraday support, or production-like use require separate
approval and follow-up evidence.
