"use client";

import { useEffect, useMemo, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { fetchSignals, redirectToLoginOnAuthError } from "@/lib/api";
import type { Signal, SignalStatus } from "@/types/signals";

const statusTone: Record<SignalStatus, string> = {
  watchlist: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
  armed: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  triggered: "border-green-300/30 bg-green-300/10 text-green-100",
  invalidated: "border-red-300/30 bg-red-300/10 text-red-100",
  no_setup: "border-slate-400/30 bg-slate-400/10 text-slate-200",
  missed: "border-orange-300/30 bg-orange-300/10 text-orange-100",
  expired: "border-slate-500/30 bg-slate-500/10 text-slate-300",
};

const statusLabel: Record<SignalStatus, string> = {
  watchlist: "Watchlist",
  armed: "Armed",
  triggered: "Triggered",
  invalidated: "Invalidated",
  no_setup: "No Setup",
  missed: "Missed",
  expired: "Expired",
};

export default function SignalsPage() {
  const authStatus = useProtectedRoute();
  const [signals, setSignals] = useState<Signal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadSignals() {
    setIsLoading(true);
    setError(null);
    try {
      setSignals(await fetchSignals());
    } catch (loadError) {
      if (redirectToLoginOnAuthError(loadError)) {
        return;
      }
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (authStatus === "authenticated") {
      void loadSignals();
    }
  }, [authStatus]);

  const summary = useMemo(() => buildSummary(signals), [signals]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#064e3b,transparent_36%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Signals</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Signal-Karten pruefen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Persistierte Setup-Bewertungen aus dem Backend. Die Karten unterstuetzen deine
                manuelle Pruefung und sind keine Kauf- oder Verkaufsanweisung. Stale Hinweise bedeuten,
                dass keine Live-Freshness vorliegt und neue CSV-Daten sinnvoll sind.
              </p>
            </div>
            <a className="text-sm text-emerald-300 hover:text-emerald-200" href="/">
              Zurueck zum Dashboard
            </a>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          <SummaryCard label="Alle Signale" value={signals.length.toString()} />
          <SummaryCard label="Armed" value={summary.armed.toString()} tone="border-emerald-300/40" />
          <SummaryCard label="Watchlist" value={summary.watchlist.toString()} tone="border-yellow-300/40" />
          <SummaryCard label="Stale" value={summary.stale.toString()} tone="border-orange-300/40" />
        </section>

        {error ? (
          <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Persistierte Signale</h2>
              <p className="mt-1 text-sm text-slate-400">
                Sortierung kommt vom Backend. Detailseiten zeigen die gespeicherte Begruendung,
                damit du den Kontext selbst pruefen kannst.
              </p>
            </div>
            <button
              type="button"
              onClick={() => void loadSignals()}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
            >
              Aktualisieren
            </button>
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Signale werden geladen...</p>
            ) : signals.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="divide-y divide-white/10">
                {signals.map((signal) => (
                  <SignalCard key={signal.id} signal={signal} />
                ))}
              </div>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}

function SummaryCard({ label, value, tone = "border-white/10" }: { label: string; value: string; tone?: string }) {
  return (
    <article className={`rounded-2xl border ${tone} bg-slate-950/70 p-5`}>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
    </article>
  );
}

function SignalCard({ signal }: { signal: Signal }) {
  const reasoning = toTextList(signal.reasoning).slice(0, 2);
  const riskFlags = toTextList(signal.risk_flags).slice(0, 4);

  return (
    <article className="grid gap-5 p-5 lg:grid-cols-[1fr_0.8fr]">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[signal.status]}`}>
            {statusLabel[signal.status]}
          </span>
          {signal.is_stale ? (
            <span className="rounded-full border border-orange-300/30 bg-orange-300/10 px-3 py-1 text-xs text-orange-100">
              Stale CSV Review
            </span>
          ) : null}
          <h3 className="text-lg font-semibold">{signal.symbol}</h3>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
            {signal.asset_class}
          </span>
          {signal.exchange ? (
            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
              {signal.exchange}
            </span>
          ) : null}
          <span className="text-sm text-slate-400">{formatStrategy(signal.strategy_type)}</span>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
            {signal.bias}
          </span>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <Metric label="Score" value={formatScore(signal)} />
          <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
          <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
        </div>
        {signal.is_stale ? <StaleNotice signal={signal} compact /> : null}
        <div className="mt-4 grid gap-3 sm:grid-cols-4">
          <Metric label="Entry Low" value={formatMoney(signal.entry_low)} compact />
          <Metric label="Entry High" value={formatMoney(signal.entry_high)} compact />
          <Metric label="Stop" value={formatMoney(signal.stop_loss)} compact />
          <Metric label="Target 1" value={formatMoney(signal.target_1)} compact />
        </div>
        <a
          className="mt-4 inline-flex rounded-xl border border-white/10 px-4 py-2 text-sm text-emerald-300 hover:border-emerald-300/50 hover:text-emerald-200"
          href={`/signals/${signal.id}`}
        >
          Signal im Detail pruefen
        </a>
      </div>

      <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
        <p className="text-sm font-medium text-slate-200">Begruendung zur manuellen Pruefung</p>
        {reasoning.length > 0 ? (
          <ul className="mt-3 space-y-2 text-sm text-slate-300">
            {reasoning.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-slate-500">Keine Begruendung gespeichert.</p>
        )}
        <div className="mt-4 flex flex-wrap gap-2">
          {riskFlags.length > 0 ? (
            riskFlags.map((flag) => (
              <span key={flag} className="rounded-full bg-orange-300/10 px-3 py-1 text-xs text-orange-100">
                {flag.replaceAll("_", " ")}
              </span>
            ))
          ) : (
            <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">
              Keine Risk Flags
            </span>
          )}
        </div>
      </div>
    </article>
  );
}

function Metric({ label, value, compact = false }: { label: string; value: string; compact?: boolean }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`${compact ? "text-sm" : "text-base"} mt-1 font-semibold text-slate-100`}>{value}</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch keine Signale gespeichert.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Importiere CSV-Daten und starte die Analyse, damit das Backend Indikatoren berechnet und
        erklaerbare Setup-Bewertungen speichert.
      </p>
    </div>
  );
}

function buildSummary(signals: Signal[]) {
  return {
    armed: signals.filter((signal) => signal.status === "armed").length,
    watchlist: signals.filter((signal) => signal.status === "watchlist").length,
    stale: signals.filter((signal) => signal.is_stale).length,
  };
}

function StaleNotice({ compact, signal }: { compact?: boolean; signal: Signal }) {
  return (
    <div className={`${compact ? "mt-4" : "mt-5"} rounded-2xl border border-orange-300/30 bg-orange-950/30 p-4`}>
      <p className="text-sm font-semibold text-orange-100">Stale Review Candidate</p>
      <p className="mt-1 text-sm text-orange-100/80">
        {signal.stale_reason ?? `Dieses Signal ist aelter als ${signal.stale_after_days} Tage.`}
      </p>
      <p className="mt-2 text-xs text-orange-100/60">
        Kein Live-Datenstatus. Vor weiterer Review neue CSV-Daten importieren oder manuell als expired markieren.
      </p>
    </div>
  );
}

function formatStrategy(strategy: Signal["strategy_type"]) {
  return strategy === "trend_pullback_long" ? "Trend Pullback Long" : "Base Breakout Long";
}

function formatScore(signal: Signal) {
  const score = signal.score ?? "-";
  return signal.score_class ? `${score} / ${signal.score_class.replaceAll("_", " ")}` : `${score}`;
}

function formatMoney(value: string | null) {
  return value ? formatNumber(value) : "-";
}

function formatNumber(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(2) : value;
}

function toTextList(value: Signal["reasoning"] | Signal["risk_flags"]) {
  if (Array.isArray(value)) {
    return value.map(String);
  }
  if (value && typeof value === "object") {
    return Object.values(value).map(String);
  }
  return [];
}
