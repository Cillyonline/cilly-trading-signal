"use client";

import { useEffect, useState } from "react";

import { fetchSignal } from "@/lib/api";
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

export default function SignalDetailPage({ params }: { params: { id: string } }) {
  const [signal, setSignal] = useState<Signal | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadSignal() {
    const signalId = Number(params.id);
    if (!Number.isInteger(signalId) || signalId <= 0) {
      setError("Ungueltige Signal-ID.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      setSignal(await fetchSignal(signalId));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadSignal();
  }, [params.id]);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#064e3b,transparent_36%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Signal Detail</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Signal vollstaendig pruefen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Diese Ansicht zeigt die gespeicherte Setup-Bewertung als Entscheidungshilfe fuer
                deine manuelle Pruefung. Sie ist keine Kauf- oder Verkaufsanweisung.
              </p>
            </div>
            <div className="flex gap-4 text-sm">
              <a className="text-emerald-300 hover:text-emerald-200" href="/signals">
                Zurueck zu Signalen
              </a>
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {error ? <ErrorMessage message={error} onRetry={() => void loadSignal()} /> : null}

        {isLoading ? (
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-slate-400">Signal wird geladen...</p>
          </section>
        ) : signal ? (
          <SignalDetail signal={signal} />
        ) : error ? null : (
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-8 text-center">
            <p className="text-lg font-semibold text-slate-200">Signal nicht gefunden.</p>
            <p className="mt-2 text-sm text-slate-400">Pruefe die URL oder kehre zur Signalliste zurueck.</p>
          </section>
        )}
      </section>
    </main>
  );
}

function SignalDetail({ signal }: { signal: Signal }) {
  const reasoning = toTextList(signal.reasoning);
  const riskFlags = toTextList(signal.risk_flags);
  const noTradeReasons = toTextList(signal.no_trade_reasons);

  return (
    <section className="grid gap-6">
      <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[signal.status]}`}>
                {statusLabel[signal.status]}
              </span>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
                {signal.bias}
              </span>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                Signal #{signal.id}
              </span>
            </div>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight">{signal.symbol}</h2>
            <p className="mt-2 text-sm text-slate-400">
              {formatStrategy(signal.strategy_type)} · {signal.asset_class}
              {signal.exchange ? ` · ${signal.exchange}` : ""} · Watchlist Item #{signal.watchlist_item_id}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:min-w-96">
            <Metric label="Score" value={formatScore(signal)} />
            <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
          </div>
        </div>
      </article>

      <section className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-xl font-semibold">Setup Bewertungsdaten</h3>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <Metric label="Entry Low" value={formatMoney(signal.entry_low)} />
            <Metric label="Entry High" value={formatMoney(signal.entry_high)} />
            <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
            <Metric label="Stop" value={formatMoney(signal.stop_loss)} />
            <Metric label="Target 1" value={formatMoney(signal.target_1)} />
            <Metric label="Target 2" value={formatMoney(signal.target_2)} />
          </div>
          <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
            <p className="text-sm font-medium text-slate-200">Invalidierung</p>
            <p className="mt-2 text-sm text-slate-300">
              {signal.invalidation_reason || "Keine Invalidierung gespeichert."}
            </p>
          </div>
        </article>

        <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-xl font-semibold">Timeframes</h3>
          <div className="mt-5 grid gap-3">
            <Metric label="Kontext" value={signal.timeframe_context ?? "-"} />
            <Metric label="Setup" value={signal.timeframe_setup ?? "-"} />
            <Metric label="Trigger" value={signal.timeframe_trigger ?? "-"} />
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <Metric label="Erstellt" value={formatDateTime(signal.created_at)} />
            <Metric label="Aktualisiert" value={formatDateTime(signal.updated_at)} />
            <Metric label="Triggered At" value={formatDateTime(signal.triggered_at)} />
          </div>
        </article>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
        <TextList title="Vollstaendige Begruendung" empty="Keine Begruendung gespeichert." items={reasoning} />
        <div className="grid gap-6">
          <BadgeList title="No-Trade Gruende" empty="Keine harten No-Trade Gruende" items={noTradeReasons} tone="red" />
          <BadgeList title="Risk Flags" empty="Keine Risk Flags" items={riskFlags} tone="orange" />
        </div>
      </section>

      <article className="rounded-3xl border border-slate-400/20 bg-slate-900/60 p-6">
        <h3 className="text-xl font-semibold">Naechste manuelle Aktion</h3>
        <p className="mt-3 text-sm text-slate-300">
          {signal.next_action || "Keine naechste Aktion gespeichert. Weiter manuell pruefen."}
        </p>
        <p className="mt-3 text-xs text-slate-500">
          Diese Aktion ist ein Pruefhinweis fuer deine manuelle Entscheidung, keine Order-Anweisung.
        </p>
      </article>
    </section>
  );
}

function ErrorMessage({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100 sm:flex-row sm:items-center sm:justify-between">
      <span>{message}</span>
      <button
        className="rounded-xl border border-red-200/20 px-4 py-2 text-red-50 hover:border-red-100/50"
        onClick={onRetry}
        type="button"
      >
        Erneut laden
      </button>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function TextList({ title, empty, items }: { title: string; empty: string; items: string[] }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h3 className="text-xl font-semibold">{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-5 space-y-3 text-sm text-slate-300">
          {items.map((item) => (
            <li key={item} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-5 text-sm text-slate-500">{empty}</p>
      )}
    </article>
  );
}

function BadgeList({
  empty,
  items,
  title,
  tone,
}: {
  empty: string;
  items: string[];
  title: string;
  tone: "orange" | "red";
}) {
  const badgeClass = tone === "red" ? "bg-red-300/10 text-red-100" : "bg-orange-300/10 text-orange-100";
  const emptyClass = "bg-emerald-300/10 text-emerald-100";
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h3 className="text-xl font-semibold">{title}</h3>
      <div className="mt-5 flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <span key={item} className={`rounded-full px-3 py-1 text-xs ${badgeClass}`}>
              {item.replaceAll("_", " ")}
            </span>
          ))
        ) : (
          <span className={`rounded-full px-3 py-1 text-xs ${emptyClass}`}>{empty}</span>
        )}
      </div>
    </article>
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

function formatDateTime(value: string | null) {
  if (!value) {
    return "-";
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString("de-DE");
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
