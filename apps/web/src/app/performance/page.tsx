"use client";

import { useEffect, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { exportPerformanceCsv, fetchPerformanceSummary, redirectToLoginOnAuthError } from "@/lib/api";
import type {
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
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#14532d,transparent_34%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Performance</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Dokumentierte Closed Trades in R</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Kompakte Auswertung manuell dokumentierter Trade-Abschluesse. Die Werte beschreiben
                historische R-Multiples und sind keine Prognose fuer zukuenftige Ergebnisse.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <button
                className="rounded-xl bg-emerald-400 px-4 py-2 font-semibold text-slate-950 hover:bg-emerald-300"
                onClick={() => void handleExport()}
                type="button"
              >
                CSV exportieren
              </button>
              <a className="text-emerald-300 hover:text-emerald-200" href="/trades">
                Trades
              </a>
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {exportError ? <ErrorState message={exportError} /> : null}
        {error ? <ErrorState message={error} /> : null}
        {!summary && !error ? <LoadingState /> : null}
        {summary ? <OpenPortfolioRiskOverview risk={summary.open_portfolio_risk} /> : null}
        {summary?.closed_trade_count === 0 ? <EmptyState /> : null}
        {summary && summary.closed_trade_count > 0 ? (
          <>
            <SummaryGrid summary={summary} />
            <StrategyBreakdown items={summary.by_strategy} />
            <AssetClassBreakdown items={summary.by_asset_class} />
          </>
        ) : null}
      </section>
    </main>
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

function OpenPortfolioRiskOverview({ risk }: { risk: OpenPortfolioRisk }) {
  return (
    <section className="rounded-3xl border border-amber-300/20 bg-amber-300/[0.06] p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-amber-200">Open Risk Review</p>
          <h2 className="mt-2 text-2xl font-semibold">Dokumentiertes Risiko offener Trades</h2>
          <p className="mt-2 max-w-3xl text-sm text-amber-50/75">
            {risk.review_only_notice} Fehlende Risikoangaben werden separat gezaehlt und nicht
            stillschweigend in Summen eingerechnet.
          </p>
        </div>
        <span className="rounded-full border border-amber-200/30 px-4 py-2 text-sm text-amber-100">
          {risk.open_trade_count} offene Trades
        </span>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Metric label="Open Trades" value={String(risk.open_trade_count)} />
        <Metric label="Complete Risk Records" value={String(risk.complete_risk_count)} />
        <Metric label="Incomplete Risk Records" value={String(risk.incomplete_risk_count)} />
        <Metric label="Documented Initial Risk" value={formatMoney(risk.documented_initial_risk_amount)} />
        <Metric label="Documented Risk %" value={formatPercent(risk.documented_initial_risk_percent)} />
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <OpenRiskGroupList title="Nach Strategie" items={risk.by_strategy} formatter={formatStrategy} />
        <OpenRiskGroupList title="Nach Asset Class" items={risk.by_asset_class} formatter={formatAssetClass} />
      </div>
    </section>
  );
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
                <p className="text-sm text-slate-400">{item.open_trade_count} offen</p>
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
          Keine offenen Trades vorhanden.
        </p>
      )}
    </div>
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
