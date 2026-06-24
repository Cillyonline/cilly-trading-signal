# Paper Performance Evidence Format

## Purpose

This format defines how to record sanitized evidence for `/performance` reviews.
It supports sample/paper-only workflow validation without exposing private trading
records or implying profitability, strategy validation, predictive value,
broker-readiness, real-money readiness, or automatic execution.

## Scope

Use this format for:

- Browser or operator checks of the Performance page.
- R-multiple summary visibility checks for sample, synthetic, fake, or paper data.
- Journal-quality summary checks using non-private records.
- Performance export boundary checks.

Do not use this format for:

- Backtests, benchmark comparisons, profitability claims, strategy-validation claims, or live/realtime claims.
- Private trade histories, private performance exports, broker statements, account values, order IDs, fill records, or private journal text.
- Approval for real-money use, broker integration, automatic execution, or production readiness.

## Allowed Evidence

Allowed evidence may include only sanitized facts:

| Field | Allowed values |
| --- | --- |
| Date/time UTC | Timestamp or date, rounded if needed. |
| Environment class | `local`, `private staging`, `sample-only browser smoke`, or `paper-only review`. |
| Commit SHA | Full or short SHA. |
| Route | `/performance`. |
| Data class | `sample`, `synthetic`, `fake`, or `paper`. |
| Closed trade count | `0`, a sample count, or `present/redacted` for private contexts. |
| R-multiple fields | `visible`, `not visible`, `present/redacted`; do not paste private sequences. |
| Journal analytics | `visible`, `not visible`, `present/redacted`; do not paste private notes. |
| Interpretation guidance | `present`, `missing`, or `needs follow-up`; must frame results as historical paper/process documentation only. |
| Export check | `not run`, `pass`, `fail`, or `skipped with reason`; do not attach private CSV output. |
| Boundary copy | `present`, `missing`, or `needs follow-up`. |
| Result | `pass`, `fail`, or `skipped`. |

## Forbidden Evidence

Never include:

- Private symbols, watchlists, trade rows, R sequences, win/loss counts, result amounts, strategy grouping, concentration, active exposure, notes, lessons, mistakes, screenshots, or exports unless they are sample/synthetic/fake/paper-only and contain no private context.
- Broker statements, account balances, order IDs, fill records, account dashboards, billing/subscription details, cookies, tokens, local storage, devtools, raw logs, raw database rows, or `.env` values.
- Wording that frames R-multiple summaries as profitability proof, strategy validation, predictive evidence, real-money readiness, broker readiness, live/realtime readiness, or production readiness.

## Evidence Template

```markdown
- Date/time UTC:
- Environment class: local / private staging / sample-only browser smoke / paper-only review
- Commit SHA:
- Route checked: /performance
- Data class: sample / synthetic / fake / paper
- Closed trade count evidence: 0 / sample count / present-redacted
- R-multiple summary evidence: visible / not visible / present-redacted
- Journal analytics evidence: visible / not visible / present-redacted
- Interpretation guidance present: yes / no
- Export check: not run / pass / fail / skipped with reason
- Boundary copy present: yes / no
- Result: pass / fail / skipped
- Follow-up issue:
- Private performance records, account data, raw exports, screenshots with sensitive data, profitability claims, or strategy-validation claims included: no
```

## Interpretation Boundary

Paper-performance evidence is historical documentation only. It may show that the
app can display or export sanitized paper-review summaries, but it does not prove
that the strategy works, that future trades are likely to be profitable, or that
the app is ready for real-money trading.
