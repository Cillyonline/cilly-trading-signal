# Mobile Layout Audit

## Purpose

This audit reviews mobile usability risks for the owner/operator review cockpit. It is a planning document for v2.7 follow-up fixes, not a production-readiness statement, PWA-readiness claim, trading advice, broker-readiness claim, or approval for automatic execution.

## Scope

Covered workflows:

- Dashboard.
- Watchlist.
- Screener.
- Signals and signal detail.
- Reviews and review batch detail.
- Trades and trade detail.

Method:

- Source-level responsive review of the current Next.js/Tailwind pages.
- The repository does not currently include a browser viewport audit harness, and no app code changes are allowed in this issue.
- Follow-up implementation issues should verify fixes with a real mobile viewport around 360-390 px wide and a tablet viewport around 768 px wide.

## Overall Assessment

The app uses mobile-first stacking in most core layouts: page shells are single-column by default, multi-column sections usually start at `sm`, `md`, `lg`, or `xl`, and primary cards avoid desktop-only table layouts. This is a reasonable baseline for controlled owner/operator use.

The main mobile risks are density and review friction rather than catastrophic layout failure. Several screens put large headers, dense filters, long cards, and multi-step forms into one continuous vertical flow. On phones this can hide the next safe action, make stale-data warnings easier to miss, and make manual review notes harder to complete without context switching.

## Priority Fixes

| Priority | Area | Finding | Suggested follow-up |
| --- | --- | --- | --- |
| P1 | Signals | Signal list/detail cards contain important stale, No-Trade, risk, and action context, but mobile scanning requires reading long stacked cards. | Improve mobile signal cards with a compact top summary, always-visible status/stale/risk badges, and clearer next-action hierarchy. |
| P1 | Reviews | Review batch entry is a long form with many fields and no mobile task grouping. | Improve mobile review batch entry with section grouping, clearer required fields, and reduced scroll friction. |
| P2 | Screener | Screener result review combines upload, filters, bulk actions, result cards, details modal, and error lists; mobile cognitive load is high. | Split mobile screener review into clearer upload/filter/results blocks and make bulk actions easier to reach. |
| P2 | Trades | Trade creation/detail forms are long and mix source selection, risk inputs, events, close, and journal review. | Group mobile trade workflows by task and make destructive/final actions visually separated. |
| P2 | Global headers | Many pages use `p-8`, `text-4xl`, and very wide uppercase letter spacing on mobile. | Reduce mobile header density while preserving desktop styling through responsive classes. |
| P3 | PWA baseline | No mobile installability affordance is documented in this audit. | Handle through the planned PWA manifest baseline issue. |

## Screen Notes

### Dashboard

Strengths:

- Main dashboard sections stack by default and only introduce grids at larger breakpoints.
- Summary cards and review priority cards are link-based and reachable on mobile.
- Safety wording remains explicit: manual review, no automatic execution.

Issues:

- The hero header uses large mobile typography and spacing, including `text-4xl`, `md:text-6xl`, `p-8`, and wide uppercase tracking. This can consume most of the first mobile viewport before review priorities appear.
- Dashboard cards are numerous. Mobile users may need to scroll through overview cards before seeing the highest-priority review tasks.
- Some cards use dense mixed English/German status detail text, which is harder to scan on small screens.

Suggested fixes:

- Make the mobile dashboard prioritize the first actionable review block above less urgent summaries.
- Reduce mobile header padding/type scale, keeping the current larger style from tablet/desktop upward.
- Keep No-Trade and stale-data warnings visible before any signal or trade action link.

### Watchlist

Strengths:

- Form and list use a single column on mobile before switching to the two-column desktop layout.
- Inputs are full-width and have reasonable touch targets.
- Source/freshness and benchmark context are present in the workflow.

Issues:

- The add/edit form appears before the list on mobile, so a user checking data freshness may need to scroll past the form first.
- Header density has the same `p-8`, `text-4xl`, and wide tracking pattern as other pages.
- Watchlist item cards can become verbose when freshness, sync, benchmark context, notes, and actions are all present.

Suggested fixes:

- Consider a mobile order or jump link that surfaces existing watchlist freshness before the add/edit form.
- Keep symbol, asset class, freshness, and benchmark status as the first visible row in each mobile item card.
- De-emphasize optional notes unless expanded.

### Screener

Strengths:

- Result cards are not implemented as a desktop-only table.
- Filters stack on mobile and bulk review wording preserves the no-auto-analysis/no-trade boundary.
- Details modal uses `overflow-y-auto`, which is appropriate for small screens.

Issues:

- Screener is the densest mobile workflow: upload, import history, filters, bulk actions, result list, details modal, and import errors all live on one page.
- Import error rows use fixed grid columns for row and field labels. This can be cramped on 360 px screens when field names or messages are long.
- Bulk selection and status changes may be far from the result cards after filtering and pagination controls.
- The details modal can become long, and closing/actions may be below the fold depending on content length.

Suggested fixes:

- Put mobile screener workflow into clearer blocks: upload, filters, active results, import history/errors.
- Make import error rows use a stacked mobile layout and reserve fixed columns for wider screens.
- Keep selected-count and bulk action controls close to visible results on mobile.
- Ensure modal close/action controls remain easy to reach after scrolling.

### Signals

Strengths:

- Signal list cards stack cleanly and avoid horizontal tables.
- Filters stack by default and preserve No Setup / No Trade visibility.
- Signal detail page has explicit manual-review and no-live-data wording.

Issues:

- Signal cards can become long because status, strategy, score, stale context, risk flags, reasoning, No-Trade reasons, and actions all compete vertically.
- Signal detail header links use a simple horizontal flex row. Long translated labels or small widths may crowd the row.
- The detail page places the review workbench and full context in large sections; mobile users may need to scroll heavily between decision context and review action.

Suggested fixes:

- Prioritize a compact mobile card header: symbol, status, stale marker, score class, and next action.
- Show No-Trade reasons and stale warnings before less urgent metadata.
- Use wrapped header actions consistently on detail pages.
- Keep manual review action controls close to the key decision context on mobile.

### Reviews

Strengths:

- Review pages are mobile-stacked and avoid desktop-only tables.
- Evidence-only and no-profitability wording is visible.
- Batch detail supports filtering and editable entries.

Issues:

- Creating review batches and entries is form-heavy. On phones, it is easy to lose context while scrolling through required and optional fields.
- Some compact summary grids use multiple equal columns on small breakpoints; the numbers are readable, but labels can feel compressed.
- Entry edit forms and generated draft text are long mobile tasks with limited progress cues.

Suggested fixes:

- Group review entry fields into mobile sections: identity, context, label/blockers, outcome/evidence, follow-up.
- Make required fields and safe optional fields more obvious.
- Consider a short mobile summary above the form that shows the selected batch and current evidence-only boundary.

### Trades

Strengths:

- Trade creation and detail pages are single-column by default and use large touch targets.
- Manual execution and no-order wording is explicit.
- Trade detail separates events, close, and journal sections.

Issues:

- Trade creation has many numeric inputs and source selectors in one long form. Mobile users may need stronger grouping to avoid entry mistakes.
- Trade detail combines management events, close flow, journal review, timeline, and existing journal entries. The page can become long quickly.
- Header action groups sometimes use non-wrapping horizontal flex rows.

Suggested fixes:

- Split mobile trade creation visually into source, risk plan, execution details, and notes.
- Separate close action styling from routine note/event actions to reduce accidental workflow confusion.
- Ensure trade detail top summary always shows status, risk, and no-execution boundary before management forms.

## Follow-Up Fix List

Planned milestone issues already map to the highest-priority areas:

- `#336` should focus on mobile signal cards and signal detail review hierarchy.
- `#337` should focus on mobile review batch entry and review batch detail editing.
- `#338` should handle baseline PWA manifest/installability without push trading, background sync, live data, or execution claims.

Recommended additional follow-ups after v2.7 if needed:

- Improve mobile screener review density and import error layout.
- Improve mobile trade creation/detail task grouping.
- Apply a global mobile header density pass across core pages.

## Verification Notes

- This issue did not change app code.
- Manual responsive implementation checks remain required for follow-up fixes.
- Follow-up PRs should verify mobile behavior at a narrow phone viewport and a tablet viewport.
- No trading logic, broker integration, automatic execution, live/realtime claim, profitability claim, or trading advice was introduced.
