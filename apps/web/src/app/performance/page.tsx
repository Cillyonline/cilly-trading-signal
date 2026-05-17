"use client";

import { useEffect, useState } from "react";

import { fetchPerformanceSummary } from "@/lib/api";
import type { PerformanceSummary } from "@/types/performance";

export default function PerformancePage() {
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSummary() {
      try {
        setSummary(await fetchPerformanceSummary());
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Performance Summary konnte nicht geladen werden.");
      }
    }

    void loadSummary();
  }, []);

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
            <div className="flex gap-4 text-sm">
              <a className="text-emerald-300 hover:text-emerald-200" href="/trades">
                Trades
              </a>
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {error ? <ErrorState message={error} /> : null}
        {!summary && !error ? <LoadingState /> : null}
        {summary?.closed_trade_count === 0 ? <EmptyState /> : null}
        {summary && summary.closed_trade_count > 0 ? <SummaryGrid summary={summary} /> : null}
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

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight">{value}</p>
    </article>
  );
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
