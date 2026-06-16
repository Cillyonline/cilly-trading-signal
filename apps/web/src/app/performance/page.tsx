"use client";

import { useEffect, useState } from "react";

import { AuthenticatedHeaderActions } from "@/components/authenticated-header-actions";
import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { exportPerformanceCsv, fetchPerformanceSummary, redirectToLoginOnAuthError } from "@/lib/api";
import type {
  AssetConcentration,
  ConcentrationGroup,
  CorrelationProxy,
  CorrelationProxySummary,
  JournalAnalytics,
  JournalStrategySummary,
  OpenPortfolioRisk,
  OpenRiskGroup,
  PerformanceByAssetClass,
  PerformanceByStrategy,
  PerformanceSummary,
} from "@/types/performance";

export default function PerformancePage() {
  const authStatus = useProtectedRoute();
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSummary() {
      try {
        setSummary(await fetchPerformanceSummary());
      } catch (loadError) {
        if (redirectToLoginOnAuthError(loadError)) {
          return;
        }
        setError(loadError instanceof Error ? loadError.message : "Performance Summary konnte nicht geladen werden.");
      }
    }

    if (authStatus === "authenticated") {
      void loadSummary();
    }
  }, [authStatus]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function handleExport() {
    setExportError(null);
    try {
      await exportPerformanceCsv();
    } catch (err) {
      if (redirectToLoginOnAuthError(err)) {
        return;
      }
      setExportError(err instanceof Error ? err.message : "Export fehlgeschlagen.");
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#14532d,transparent_34%),rgba(255,255,255,0.05)] p-5 sm:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">Performance</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Dokumentierte Closed Trades in R</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Kompakte Auswertung manuell dokumentierter Paper-Trade-Abschluesse. Die Werte
                beschreiben historische R-Multiples als Lern- und Prozessnotizen, nicht als
                Profitabilitaetsnachweis, Strategievalidierung oder Prognose fuer zukuenftige Ergebnisse.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <button
                className="rounded-xl bg-emerald-400 px-4 py-2 font-semibold text-slate-950 hover:bg-emerald-300"
                onClick={() => void handleExport()}
                type="button"
              >
                Paper CSV exportieren
              </button>
              <AuthenticatedHeaderActions links={[{ href: "/trades", label: "Trades" }]} />
            </div>
          </div>
        </header>

        {exportError ? <ErrorState message={exportError} /> : null}
        {error ? <ErrorState message={error} /> : null}
        {!summary && !error ? <LoadingState /> : null}
        <PaperPerformanceBoundary />
        {summary ? <OpenPortfolioRiskOverview risk={summary.open_portfolio_risk} /> : null}
        {summary?.closed_trade_count === 0 ? <EmptyState /> : null}
        {summary && summary.closed_trade_count > 0 ? (
          <>
            <SummaryGrid summary={summary} />
            <JournalAnalyticsPanel analytics={summary.journal_analytics} />
            <StrategyBreakdown items={summary.by_strategy} />
            <AssetClassBreakdown items={summary.by_asset_class} />
          </>
        ) : null}
      </section>
    </main>
  );
}

function PaperPerformanceBoundary() {
  return (
    <section className="rounded-3xl border border-amber-300/25 bg-amber-300/[0.06] p-5 sm:p-6">
      <p className="text-sm uppercase tracking-[0.24em] text-amber-200">Paper Evidence Boundary</p>
      <h2 className="mt-2 text-2xl font-semibold text-amber-50">Performance ist Dokumentation, kein Nachweis</h2>
      <p className="mt-3 max-w-4xl text-sm text-amber-50/85">
        Diese Ansicht hilft, manuelle Paper-Ergebnisse in R-Multiples und Journal-Qualitaet zu reviewen.
        Geteilte Evidence darf nur sample-, synthetic- oder paper-only Daten enthalten und keine privaten
        Performance-Records, Broker-/Accountdaten, Roh-Exports oder Profitabilitaetsclaims zeigen.
      </p>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <BoundaryPill label="Erlaubt" text="Sanitisierte Counts, R-Felder als present/redacted, Route und Checkstatus" />
        <BoundaryPill label="Nicht erlaubt" text="Private R-Sequenzen, Accountwerte, Brokerdaten, Screenshots mit privaten Trades" />
        <BoundaryPill label="Interpretation" text="Historische Paper-Dokumentation, keine Strategie- oder Real-Money-Freigabe" />
      </div>
    </section>
  );
}

function BoundaryPill({ label, text }: { label: string; text: string }) {
  return (
    <div className="rounded-2xl border border-amber-200/20 bg-slate-950/40 p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-200">{label}</p>
      <p className="mt-2 text-sm text-amber-50/85">{text}</p>
    </div>
  );
}

function LoadingState() {
  return <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-8 text-sm text-slate-400">Performance Summary wird geladen...</section>;
}

function ErrorState({ message }: { message: string }) {
  return <section className="rounded-3xl border border-red-400/30 bg-red-950/40 p-6 text-sm text-red-100">{message}</section>;
}

function EmptyState() {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-8">
      <h2 className="text-2xl font-semibold">Noch keine geschlossenen Trades</h2>
      <p className="mt-3 max-w-2xl text-slate-400">
        Die Summary wird sichtbar, sobald manuell dokumentierte Trades geschlossen wurden. Offene
        Trades bleiben aus diesen Metriken ausgeschlossen.
      </p>
      <a
        className="mt-6 inline-flex rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950"
        href="/trades"
      >
        Zu Trades
      </a>
    </section>
  );
}

function SummaryGrid({ summary }: { summary: PerformanceSummary }) {
  return (
    <section className="grid gap-4 md:grid-cols-3">
      <Metric label="Closed Trades" value={String(summary.closed_trade_count)} />
      <Metric label="Documented Total R" value={formatR(summary.total_r)} />
      <Metric label="Documented Average R" value={formatR(summary.average_r)} />
      <Metric label="Win Rate" value={formatPercent(summary.win_rate)} />
      <Metric label="Best R" value={formatR(summary.best_r)} />
      <Metric label="Worst R" value={formatR(summary.worst_r)} />
    </section>
  );
}

function JournalAnalyticsPanel({ analytics }: { analytics: JournalAnalytics }) {
  return (
    <section className="rounded-3xl border border-violet-300/20 bg-violet-300/[0.05] p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-violet-200">Journal Quality</p>
          <h2 className="mt-2 text-2xl font-semibold">Process Review Analytics</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">{analytics.small_sample_notice}</p>
        </div>
        <span className="rounded-full border border-violet-200/30 px-4 py-2 text-sm text-violet-100">
          {analytics.reviewed_trade_count} reviewed / {analytics.missing_review_count} missing
        </span>
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Metric label="Closed Trades" value={String(analytics.closed_trade_count)} />
        <Metric label="Reviewed" value={String(analytics.reviewed_trade_count)} />
        <Metric label="Missing Reviews" value={String(analytics.missing_review_count)} />
        <Metric label="Rule Followed" value={String(analytics.setup_rule_followed_count)} />
      </div>
      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <CompactScore label="Entry Quality" value={analytics.average_entry_quality_score} />
        <CompactScore label="Stop Quality" value={analytics.average_stop_quality_score} />
        <CompactScore label="Exit Quality" value={analytics.average_exit_quality_score} />
        <CompactScore label="Discipline" value={analytics.average_discipline_score} />
      </div>
      <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/50 p-5">
        <h3 className="font-semibold text-slate-100">By Strategy</h3>
        <p className="mt-2 text-sm text-slate-400">
          Strategy breakdown appears from {analytics.min_strategy_sample_size} reviewed journal records.
        </p>
        {analytics.by_strategy.length > 0 ? (
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            {analytics.by_strategy.map((item) => (
              <JournalStrategyCard key={item.strategy_type} item={item} />
            ))}
          </div>
        ) : (
          <p className="mt-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-400">
            Noch keine Strategie mit ausreichender Journal-Stichprobe.
          </p>
        )}
      </div>
    </section>
  );
}

function JournalStrategyCard({ item }: { item: JournalStrategySummary }) {
  return (
    <article className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-center justify-between gap-3">
        <h4 className="font-semibold text-slate-100">{formatStrategy(item.strategy_type)}</h4>
        <span className="text-xs text-slate-400">{item.reviewed_trade_count} journals</span>
      </div>
      <p className="mt-2 text-sm text-slate-400">
        Rule: {item.setup_rule_followed_count} followed / {item.setup_rule_broken_count} broken / {item.setup_rule_unknown_count} unknown
      </p>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <CompactScore label="Entry" value={item.average_entry_quality_score} />
        <CompactScore label="Stop" value={item.average_stop_quality_score} />
        <CompactScore label="Exit" value={item.average_exit_quality_score} />
        <CompactScore label="Discipline" value={item.average_discipline_score} />
      </div>
    </article>
  );
}

function OpenPortfolioRiskOverview({ risk }: { risk: OpenPortfolioRisk }) {
  const warningTone = getOpenRiskWarningTone(risk.warning_status);
  return (
    <section className={`rounded-3xl border p-6 ${warningTone.container}`}>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className={`text-sm uppercase tracking-[0.3em] ${warningTone.eyebrow}`}>Active Risk Review</p>
          <h2 className="mt-2 text-2xl font-semibold">Dokumentiertes Risiko aktiver Trades</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">
            {risk.review_only_notice} Fehlende Risikoangaben werden separat gezaehlt und nicht
            stillschweigend in Summen eingerechnet.
          </p>
        </div>
        <span className={`rounded-full border px-4 py-2 text-sm ${warningTone.badge}`}>
          {formatOpenRiskStatus(risk.warning_status)}
        </span>
      </div>

      {risk.warnings.length > 0 ? (
        <div className={`mt-5 rounded-2xl border p-4 text-sm ${warningTone.notice}`}>
          <p className="font-semibold">Risk Review Warning</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {risk.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Metric label="Active Trades" value={String(risk.open_trade_count)} />
        <Metric label="Complete Risk Records" value={String(risk.complete_risk_count)} />
        <Metric label="Incomplete Risk Records" value={String(risk.incomplete_risk_count)} />
        <Metric label="Documented Initial Risk" value={formatMoney(risk.documented_initial_risk_amount)} />
        <Metric
          label="Documented Risk %"
          value={`${formatPercent(risk.documented_initial_risk_percent)} / max ${formatPercent(risk.max_risk_percent)}`}
        />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <OpenRiskGroupList title="Nach Strategie" items={risk.by_strategy} formatter={formatStrategy} />
        <OpenRiskGroupList title="Nach Asset Class" items={risk.by_asset_class} formatter={formatAssetClass} />
      </div>

      <AssetConcentrationPanel concentration={risk.asset_concentration} />
      <CorrelationProxyPanel proxies={risk.correlation_proxies} />
    </section>
  );
}

function getOpenRiskWarningTone(status: OpenPortfolioRisk["warning_status"]) {
  if (status === "warning") {
    return {
      container: "border-red-300/30 bg-red-950/25",
      eyebrow: "text-red-200",
      badge: "border-red-200/30 text-red-100",
      notice: "border-red-300/30 bg-red-950/40 text-red-100",
    };
  }
  if (status === "unknown") {
    return {
      container: "border-amber-300/20 bg-amber-300/[0.06]",
      eyebrow: "text-amber-200",
      badge: "border-amber-200/30 text-amber-100",
      notice: "border-amber-200/30 bg-amber-950/30 text-amber-100",
    };
  }
  return {
    container: "border-emerald-300/20 bg-emerald-300/[0.05]",
    eyebrow: "text-emerald-200",
    badge: "border-emerald-200/30 text-emerald-100",
    notice: "border-emerald-200/30 bg-emerald-950/30 text-emerald-100",
  };
}

function formatOpenRiskStatus(status: OpenPortfolioRisk["warning_status"]) {
  if (status === "warning") {
    return "Risk warning";
  }
  if (status === "unknown") {
    return "Risk unknown";
  }
  return "Risk ok";
}

function OpenRiskGroupList({
  title,
  items,
  formatter,
}: {
  title: string;
  items: OpenRiskGroup[];
  formatter: (value: string) => string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold text-slate-100">{title}</h3>
        <span className="text-xs text-slate-400">{items.length} Gruppen</span>
      </div>
      {items.length > 0 ? (
        <div className="mt-4 flex flex-col gap-3">
          {items.map((item) => (
            <article key={item.group} className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-medium text-slate-100">{formatter(item.group)}</p>
                <p className="text-sm text-slate-400">{item.open_trade_count} aktiv</p>
              </div>
              <div className="mt-3 grid gap-3 sm:grid-cols-3">
                <CompactMetric label="Risk" value={formatMoney(item.documented_initial_risk_amount)} />
                <CompactMetric label="Risk %" value={formatPercent(item.documented_initial_risk_percent)} />
                <CompactMetric label="Incomplete" value={String(item.incomplete_risk_count)} />
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="mt-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-400">
          Keine aktiven Trades vorhanden.
        </p>
      )}
    </div>
  );
}

function AssetConcentrationPanel({ concentration }: { concentration: AssetConcentration }) {
  const isWarning = concentration.warning_status === "warning";
  return (
    <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/50 p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="font-semibold text-slate-100">Asset Concentration Review</h3>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            {concentration.review_only_notice} Threshold: {formatPercent(concentration.warning_threshold_percent)}.
          </p>
        </div>
        <span
          className={`rounded-full border px-3 py-1 text-xs ${
            isWarning ? "border-red-200/30 text-red-100" : "border-emerald-200/30 text-emerald-100"
          }`}
        >
          {isWarning ? "Concentration warning" : "Concentration ok"}
        </span>
      </div>
      {concentration.warnings.length > 0 ? (
        <div className="mt-4 rounded-xl border border-red-300/30 bg-red-950/30 p-4 text-sm text-red-100">
          <p className="font-semibold">Review prompts</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {concentration.warnings.map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </div>
      ) : null}
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <ConcentrationGroupList title="Asset Class" items={concentration.by_asset_class} formatter={formatAssetClass} />
        <ConcentrationGroupList title="Symbol" items={concentration.by_symbol} />
        <ConcentrationGroupList title="Sector" items={concentration.by_sector} formatter={formatUnknownBucket} />
        <ConcentrationGroupList title="Industry" items={concentration.by_industry} formatter={formatUnknownBucket} />
      </div>
    </div>
  );
}

function ConcentrationGroupList({
  title,
  items,
  formatter = (value) => value,
}: {
  title: string;
  items: ConcentrationGroup[];
  formatter?: (value: string) => string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <h4 className="text-sm font-semibold uppercase tracking-wide text-slate-300">{title}</h4>
      {items.length > 0 ? (
        <div className="mt-3 flex flex-col gap-2">
          {items.map((item) => (
            <div key={item.group} className="flex items-center justify-between gap-3 text-sm">
              <span className={item.warning ? "text-red-100" : "text-slate-300"}>{formatter(item.group)}</span>
              <span className={item.warning ? "font-semibold text-red-100" : "text-slate-400"}>
                {item.open_trade_count} / {formatPercent(item.open_trade_percent)}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-slate-500">Keine aktiven Trades.</p>
      )}
    </div>
  );
}

function CorrelationProxyPanel({ proxies }: { proxies: CorrelationProxySummary }) {
  const isWarning = proxies.warning_status === "warning";
  const isUnknown = proxies.warning_status === "unknown";
  return (
    <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/50 p-5">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="font-semibold text-slate-100">Correlation Proxy Review</h3>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">{proxies.review_only_notice}</p>
        </div>
        <span
          className={`rounded-full border px-3 py-1 text-xs ${
            isWarning
              ? "border-red-200/30 text-red-100"
              : isUnknown
                ? "border-amber-200/30 text-amber-100"
                : "border-emerald-200/30 text-emerald-100"
          }`}
        >
          {isWarning ? "Proxy warning" : isUnknown ? "Proxy unknown" : "Proxy ok"}
        </span>
      </div>
      {proxies.warnings.length > 0 ? (
        <div className="mt-4 grid gap-3 lg:grid-cols-2">
          {proxies.warnings.map((proxy) => (
            <CorrelationProxyCard key={proxy.key} proxy={proxy} />
          ))}
        </div>
      ) : (
        <p className="mt-4 rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-400">
          Keine Proxy-Warnungen fuer aktive Exposures.
        </p>
      )}
    </div>
  );
}

function CorrelationProxyCard({ proxy }: { proxy: CorrelationProxy }) {
  const isWarning = proxy.status === "warning";
  return (
    <article className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-center justify-between gap-3">
        <h4 className="font-semibold text-slate-100">{proxy.label}</h4>
        <span className={isWarning ? "text-xs text-red-100" : "text-xs text-amber-100"}>{proxy.status}</span>
      </div>
      <p className="mt-2 text-sm text-slate-400">{proxy.message}</p>
      <p className="mt-3 text-sm text-slate-300">
        {proxy.open_trade_count} aktive Trades: {proxy.symbols.length > 0 ? proxy.symbols.join(", ") : "-"}
      </p>
    </article>
  );
}

function StrategyBreakdown({ items }: { items: PerformanceByStrategy[] }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Dokumentierte Performance nach Strategie</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Gruppiert nur manuell dokumentierte geschlossene Trades. Diese historischen R-Werte sind
            keine Prognose und keine Strategie-Validierung.
          </p>
        </div>
        <span className="text-sm text-slate-400">{items.length} Strategien</span>
      </div>

      {items.length > 0 ? (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          {items.map((item) => (
            <article key={item.strategy_type} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-lg font-semibold">{formatStrategy(item.strategy_type)}</h3>
                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                  {item.closed_trade_count} Closed Trades
                </span>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <Metric label="Documented Total R" value={formatR(item.total_r)} />
                <Metric label="Documented Average R" value={formatR(item.average_r)} />
                <Metric label="Win Rate" value={formatPercent(item.win_rate)} />
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="mt-6 rounded-2xl border border-white/10 bg-slate-950/60 p-5 text-sm text-slate-400">
          Noch keine geschlossenen Trades mit Strategy-Zuordnung vorhanden.
        </p>
      )}
    </section>
  );
}

function AssetClassBreakdown({ items }: { items: PerformanceByAssetClass[] }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Dokumentierte Performance nach Asset Class</h2>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Gruppiert nur manuell dokumentierte geschlossene Trades nach Stock und Crypto. Diese
            historischen R-Werte sind keine Portfolio- oder Allokationsempfehlung.
          </p>
        </div>
        <span className="text-sm text-slate-400">{items.length} Asset Classes</span>
      </div>

      {items.length > 0 ? (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          {items.map((item) => (
            <article key={item.asset_class} className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-lg font-semibold">{formatAssetClass(item.asset_class)}</h3>
                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                  {item.closed_trade_count} Closed Trades
                </span>
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                <Metric label="Documented Total R" value={formatR(item.total_r)} />
                <Metric label="Documented Average R" value={formatR(item.average_r)} />
                <Metric label="Win Rate" value={formatPercent(item.win_rate)} />
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="mt-6 rounded-2xl border border-white/10 bg-slate-950/60 p-5 text-sm text-slate-400">
          Noch keine geschlossenen Trades mit Asset-Class-Zuordnung vorhanden.
        </p>
      )}
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight">{value}</p>
    </article>
  );
}

function CompactMetric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function CompactScore({ label, value }: { label: string; value: string | null }) {
  return <CompactMetric label={label} value={value ? `${Number(value).toFixed(2)} / 5` : "-"} />;
}

function formatMoney(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(2) : value;
}

function formatR(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${parsed.toFixed(2)}R` : `${value}R`;
}

function formatPercent(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${parsed.toFixed(2)}%` : `${value}%`;
}

function formatStrategy(value: string) {
  if (value === "trend_pullback_long") {
    return "Trend Pullback Long";
  }
  if (value === "base_breakout_long") {
    return "Base Breakout Long";
  }
  return value.replaceAll("_", " ");
}

function formatAssetClass(value: string) {
  if (value === "stock") {
    return "Stock";
  }
  if (value === "crypto") {
    return "Crypto";
  }
  return value.replaceAll("_", " ");
}

function formatUnknownBucket(value: string) {
  if (value === "unknown_sector") {
    return "Unknown sector";
  }
  if (value === "unknown_industry") {
    return "Unknown industry";
  }
  return value.replaceAll("_", " ");
}
