"use client";

import { useEffect, useMemo, useState } from "react";

import { AuthenticatedHeaderActions } from "@/components/authenticated-header-actions";
import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { fetchSignals, fetchWatchlist, redirectToLoginOnAuthError } from "@/lib/api";
import {
  buildSignalDecision,
  signalDecisionDotClass,
  signalDecisionExplanation,
  signalDecisionToneClass,
} from "@/lib/signal-decision";
import type { ScoreClass, Signal, SignalStatus, StrategyType, TriggerProximityState } from "@/types/signals";
import type { WatchlistItem } from "@/types/watchlist";

type SignalFilters = {
  symbol: string;
  status: "all" | SignalStatus;
  strategy: "all" | StrategyType;
  scoreClass: "all" | ScoreClass;
  freshness: "all" | "fresh" | "stale";
  context: "all" | "risk_flags" | "no_trade_reasons";
};

type TriggerRadarState = Exclude<TriggerProximityState, "not_available">;

type TriggerRadarItem = {
  signal: Signal;
  state: TriggerRadarState;
  label: string;
  action: string;
};

type ActiveReviewItem = {
  signal: Signal;
  label: string;
  reason: string;
  action: string;
  priority: number;
  tone: "green" | "yellow" | "orange" | "gray";
};

const emptyFilters: SignalFilters = {
  symbol: "",
  status: "all",
  strategy: "all",
  scoreClass: "all",
  freshness: "all",
  context: "all",
};

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
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [filters, setFilters] = useState<SignalFilters>(emptyFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadSignals() {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedSignals, loadedWatchlist] = await Promise.all([fetchSignals(), fetchWatchlist()]);
      setSignals(loadedSignals);
      setWatchlist(loadedWatchlist);
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

  const activeSignals = useMemo(() => filterActiveWatchlistSignals(signals, watchlist), [signals, watchlist]);
  const inactiveSignalCount = signals.length - activeSignals.length;
  const summary = useMemo(() => buildSummary(activeSignals), [activeSignals]);
  const activeReviewItems = useMemo(() => buildActiveReviewItems(activeSignals), [activeSignals]);
  const triggerRadarItems = useMemo(() => buildTriggerRadarItems(activeSignals), [activeSignals]);
  const filteredSignals = useMemo(() => filterSignals(activeSignals, filters), [activeSignals, filters]);
  const rankedSignals = useMemo(() => rankSignals(filteredSignals), [filteredSignals]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#064e3b,transparent_36%),rgba(255,255,255,0.05)] p-5 sm:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">Signal Radar</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Heute relevante Setups sehen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Das Radar sortiert gespeicherte Setup-Bewertungen nach manueller Relevanz. Gruen und
                Gelb heissen pruefen oder beobachten, Rot heisst Kein Trade. Keine Karte ist eine
                Kauf- oder Verkaufsanweisung.
              </p>
            </div>
            <AuthenticatedHeaderActions />
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          <SummaryCard label="Paper-Kandidaten" value={summary.paperCandidates.toString()} tone="green" />
          <SummaryCard label="Beobachten" value={summary.observe.toString()} tone="yellow" />
          <SummaryCard label="Kein Trade" value={summary.noTrade.toString()} tone="red" />
          <SummaryCard label="Datenproblem" value={summary.dataProblem.toString()} tone="gray" />
        </section>

        <SignalStateGuide />

        {inactiveSignalCount > 0 ? <InactiveSignalsNotice count={inactiveSignalCount} /> : null}

        <ActiveReviewShortlistSection items={activeReviewItems} isLoading={isLoading} />

        <TriggerRadarSection items={triggerRadarItems} isLoading={isLoading} />

        {error ? (
          <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <details className="group rounded-3xl border border-white/10 bg-white/[0.03] [&>summary:focus]:outline-none">
          <summary className="flex cursor-pointer list-none items-center justify-between p-6">
            <div>
              <h2 className="text-xl font-semibold">Radar-Rangliste (alle Signale)</h2>
              <p className="mt-1 text-sm text-slate-400">
                Vollstaendige Liste aller Signale. Relevante Kandidaten stehen oben. Nutze Active
                Review und Trigger Radar fuer die taegliche Arbeit.
              </p>
            </div>
            <span className="rounded-full border border-white/10 bg-slate-800 px-3 py-1 text-xs text-slate-300">
              Zweite Prioritaet
            </span>
          </summary>
          <div className="p-6 pt-0">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-slate-400">
                  Relevante Kandidaten stehen oben. No-Trade und Datenprobleme bleiben sichtbar, aber
                  werden konservativ nachrangig sortiert.
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

            <SignalFiltersPanel
              filters={filters}
              resultCount={filteredSignals.length}
              totalCount={activeSignals.length}
              onChange={setFilters}
              onReset={() => setFilters(emptyFilters)}
            />

            <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
              {isLoading ? (
                <p className="p-5 text-sm text-slate-400">Signale werden geladen...</p>
              ) : activeSignals.length === 0 ? (
                <EmptyState />
              ) : filteredSignals.length === 0 ? (
                <FilteredEmptyState />
              ) : (
                <div className="divide-y divide-white/10">
                  {rankedSignals.map((signal) => (
                    <SignalCard key={signal.id} signal={signal} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </details>
      </section>
    </main>
  );
}

function ActiveReviewShortlistSection({ isLoading, items }: { isLoading: boolean; items: ActiveReviewItem[] }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(16,185,129,0.14),transparent_34%),rgba(255,255,255,0.03)] p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-300">Active Review</p>
          <h2 className="mt-2 text-xl font-semibold">Heutige Shortlist</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Kompakte Arbeitsliste aus Paper-Kandidat, Beobachten, Trigger-Naehe und Datenproblemen.
            Sie ersetzt nicht die Detailpruefung und erzeugt keine Analyse, Alerts, Trades oder Orders.
          </p>
        </div>
        <span className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1 text-sm text-emerald-100">
          {items.length} Fokuskarte(n)
        </span>
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-4">
        {isLoading ? (
          <p className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-400">
            Shortlist wird geladen...
          </p>
        ) : items.length === 0 ? (
          <p className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-400 lg:col-span-4">
            Keine aktiven Review-Kandidaten. Importiere aktuelle CSV-Daten oder pruefe die Radar-Rangliste.
          </p>
        ) : (
          items.slice(0, 8).map((item) => <ActiveReviewCard key={item.signal.id} item={item} />)
        )}
      </div>
    </section>
  );
}

function ActiveReviewCard({ item }: { item: ActiveReviewItem }) {
  const toneClass = {
    green: "border-emerald-300/40 bg-emerald-300/10 text-emerald-100",
    yellow: "border-yellow-300/40 bg-yellow-300/10 text-yellow-100",
    orange: "border-orange-300/40 bg-orange-300/10 text-orange-100",
    gray: "border-slate-400/40 bg-slate-400/10 text-slate-100",
  }[item.tone];

  return (
    <article className={`rounded-2xl border p-4 ${toneClass}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-50">{item.signal.symbol}</h3>
          <p className="mt-1 text-xs uppercase tracking-[0.18em] opacity-80">{item.label}</p>
        </div>
        <span className="rounded-full border border-current/20 px-3 py-1 text-xs">
          {statusLabel[item.signal.status]}
        </span>
      </div>
      <p className="mt-3 text-sm font-medium text-slate-50">{item.reason}</p>
      <p className="mt-2 text-sm">{item.action}</p>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <Metric label="Score" value={formatScore(item.signal)} compact />
        <Metric label="Trigger" value={formatMoney(item.signal.trigger_level)} compact />
      </div>
      <a className="mt-4 inline-flex text-sm font-semibold text-current hover:text-slate-50" href={`/signals/${item.signal.id}`}>
        Detail pruefen
      </a>
    </article>
  );
}

function TriggerRadarSection({ isLoading, items }: { isLoading: boolean; items: TriggerRadarItem[] }) {
  const atTriggerCount = items.filter((item) => item.state === "at_trigger").length;
  const nearTriggerCount = items.filter((item) => item.state === "near_trigger").length;
  const farCount = items.filter((item) => item.state === "far_from_trigger").length;
  const visibleItems = items.slice(0, 6);

  return (
    <section className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(20,184,166,0.16),transparent_34%),rgba(255,255,255,0.03)] p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-300">Trigger Radar</p>
          <h2 className="mt-2 text-xl font-semibold">Manuelle Trigger-Review priorisieren</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Tagesarbeitsliste fuer gespeicherte Signale mit Trigger-Level. Nutze sie fuer gezielte
            `4H` CSV-Updates und Detailpruefung. Kein Live-Preis, keine Order, kein Alert.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm sm:min-w-72">
          <Metric label="Am Trigger" value={atTriggerCount.toString()} compact />
          <Metric label="Nah dran" value={nearTriggerCount.toString()} compact />
          <Metric label="Weiter weg" value={farCount.toString()} compact />
        </div>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-3">
        <TriggerWorkflowStep
          title="1. 4H gezielt aktualisieren"
          text="Nur Trigger-Shortlist per TradingView CSV aktualisieren, nicht das ganze Universum."
        />
        <TriggerWorkflowStep
          title="2. Detail pruefen"
          text="Trigger-Level, Freshness, Risk Flags, Invalidation und No-Trade Gruende lesen."
        />
        <TriggerWorkflowStep
          title="3. Extern entscheiden"
          text="Jede Ausfuehrung bleibt manuell ausserhalb der App. Keine Buy/Sell-Anweisung."
        />
      </div>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        {isLoading ? (
          <p className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-400">
            Trigger Radar wird geladen...
          </p>
        ) : items.length === 0 ? (
          <p className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-400 lg:col-span-3">
            Keine reviewbaren Trigger-Kandidaten. No-Trade, stale Daten und fehlende Trigger-Level
            bleiben bewusst draussen.
          </p>
        ) : (
          visibleItems.map((item) => <TriggerRadarCard key={item.signal.id} item={item} />)
        )}
      </div>

      {!isLoading && items.length > visibleItems.length ? (
        <p className="mt-4 rounded-2xl border border-white/10 bg-slate-950/60 p-3 text-sm text-slate-400">
          {visibleItems.length} von {items.length} Trigger-Kandidaten sichtbar. Nutze die Radar-Rangliste fuer weitere
          Symbole, aber halte die aktive Trigger-Liste klein.
        </p>
      ) : null}
    </section>
  );
}

function TriggerWorkflowStep({ text, title }: { text: string; title: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-300">
      <p className="font-semibold text-slate-100">{title}</p>
      <p className="mt-2 text-xs text-slate-400">{text}</p>
    </div>
  );
}

function TriggerRadarCard({ item }: { item: TriggerRadarItem }) {
  const toneClass = {
    at_trigger: "border-emerald-300/40 bg-emerald-300/10 text-emerald-100",
    near_trigger: "border-yellow-300/40 bg-yellow-300/10 text-yellow-100",
    far_from_trigger: "border-sky-300/30 bg-sky-300/10 text-sky-100",
  }[item.state];

  return (
    <article className={`rounded-2xl border p-4 ${toneClass}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-50">{item.signal.symbol}</h3>
          <p className="mt-1 text-xs uppercase tracking-[0.18em] opacity-80">{item.label}</p>
        </div>
        <span className="rounded-full border border-current/20 px-3 py-1 text-xs">
          {statusLabel[item.signal.status]}
        </span>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-2">
        <Metric label="Trigger" value={formatMoney(item.signal.trigger_level)} compact />
        <Metric label="Score" value={formatScore(item.signal)} compact />
      </div>
      <p className="mt-3 text-sm">{item.action}</p>
      <a
        className="mt-4 inline-flex text-sm font-semibold text-current hover:text-slate-50"
        href={`/signals/${item.signal.id}`}
      >
        Detail pruefen
      </a>
    </article>
  );
}

function SignalFiltersPanel({
  filters,
  resultCount,
  totalCount,
  onChange,
  onReset,
}: {
  filters: SignalFilters;
  resultCount: number;
  totalCount: number;
  onChange: (filters: SignalFilters) => void;
  onReset: () => void;
}) {
  return (
    <div className="mt-6 grid gap-4 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-200">Review-Filter</p>
          <p className="mt-1 text-xs text-slate-400">
            Filter veraendern keine Signale. No Setup und No Trade bleiben sichtbar und pruefbar.
          </p>
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-400">
          <span>
            {resultCount} / {totalCount} sichtbar
          </span>
          <button
            className="rounded-xl border border-white/10 px-3 py-2 text-slate-200 hover:border-emerald-300/50"
            onClick={onReset}
            type="button"
          >
            Zuruecksetzen
          </button>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <label className="grid gap-2 text-sm text-slate-300">
          Symbol
          <input
            value={filters.symbol}
            onChange={(event) => onChange({ ...filters, symbol: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            placeholder="AAPL, BTC..."
          />
        </label>

        <FilterSelect
          label="Status"
          value={filters.status}
          onChange={(value) => onChange({ ...filters, status: value as SignalFilters["status"] })}
          options={[
            ["all", "Alle Status"],
            ["triggered", "Trigger erreicht"],
            ["armed", "Pruefbereit"],
            ["watchlist", "Watchlist"],
            ["no_setup", "Kein Setup"],
            ["invalidated", "Ungueltig"],
            ["missed", "Verpasst"],
            ["expired", "Abgelaufen"],
          ]}
        />

        <FilterSelect
          label="Strategie"
          value={filters.strategy}
          onChange={(value) => onChange({ ...filters, strategy: value as SignalFilters["strategy"] })}
          options={[
            ["all", "Alle Strategien"],
            ["trend_pullback_long", "Trend Pullback Long"],
            ["base_breakout_long", "Base Breakout Long"],
          ]}
        />

        <FilterSelect
          label="Score Class"
          value={filters.scoreClass}
          onChange={(value) => onChange({ ...filters, scoreClass: value as SignalFilters["scoreClass"] })}
          options={[
            ["all", "Alle Qualitaeten"],
            ["a_setup", "A Setup"],
            ["b_setup", "B Setup"],
            ["watchlist", "Watchlist"],
            ["no_trade", "No Trade"],
          ]}
        />

        <FilterSelect
          label="Freshness"
          value={filters.freshness}
          onChange={(value) => onChange({ ...filters, freshness: value as SignalFilters["freshness"] })}
          options={[
            ["all", "Alle Datenstaende"],
            ["fresh", "Nicht stale"],
            ["stale", "Stale"],
          ]}
        />

        <FilterSelect
          label="Kontext"
          value={filters.context}
          onChange={(value) => onChange({ ...filters, context: value as SignalFilters["context"] })}
          options={[
            ["all", "Alle Kontexte"],
            ["risk_flags", "Mit Risk Flags"],
            ["no_trade_reasons", "Mit No-Trade Gruenden"],
          ]}
        />
      </div>
    </div>
  );
}

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: [string, string][];
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
      >
        {options.map(([optionValue, optionLabel]) => (
          <option key={optionValue} value={optionValue}>
            {optionLabel}
          </option>
        ))}
      </select>
    </label>
  );
}

function SummaryCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string;
  tone?: "green" | "yellow" | "red" | "gray" | "default";
}) {
  const toneClass = {
    default: "border-white/10 bg-slate-950/70 text-slate-100",
    green: "border-emerald-300/40 bg-emerald-300/10 text-emerald-100",
    yellow: "border-yellow-300/40 bg-yellow-300/10 text-yellow-100",
    red: "border-red-300/40 bg-red-300/10 text-red-100",
    gray: "border-slate-400/40 bg-slate-400/10 text-slate-100",
  }[tone];

  return (
    <article className={`rounded-2xl border p-5 ${toneClass}`}>
      <p className="text-sm opacity-80">{label}</p>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
    </article>
  );
}

function SignalStateGuide() {
  const states = [
    { kind: "paper_candidate", label: "Paper-Kandidat", tone: "green" },
    { kind: "observe", label: "Beobachten", tone: "yellow" },
    { kind: "no_trade", label: "Kein Trade", tone: "red" },
    { kind: "data_problem", label: "Datenproblem", tone: "gray" },
  ] as const;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-300">Status verstehen</p>
      <h2 className="mt-2 text-xl font-semibold">Was die Radar-Farben bedeuten</h2>
      <p className="mt-2 max-w-3xl text-sm text-slate-400">
        Die Labels priorisieren manuelle Review-Arbeit. Sie sind keine Kauf-/Verkaufsanweisung,
        keine Order und kein automatischer Trade.
      </p>
      <div className="mt-5 grid gap-3 lg:grid-cols-4">
        {states.map((state) => {
          const explanation = signalDecisionExplanation(state.kind);
          return (
            <article key={state.kind} className={`rounded-2xl border p-4 ${stateGuideTone(state.tone)}`}>
              <p className="font-semibold text-slate-50">{state.label}</p>
              <p className="mt-3 text-xs font-semibold uppercase tracking-[0.16em] opacity-75">Was bedeutet das?</p>
              <p className="mt-1 text-sm opacity-90">{explanation.whatItMeans}</p>
              <p className="mt-3 text-xs font-semibold uppercase tracking-[0.16em] opacity-75">Was jetzt?</p>
              <p className="mt-1 text-sm opacity-90">{explanation.whatNow}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}

function InactiveSignalsNotice({ count }: { count: number }) {
  return (
    <section className="rounded-2xl border border-slate-400/20 bg-slate-800/60 p-4 text-sm text-slate-300">
      {count} Signal(e) gehoeren zu inaktiven Watchlist-Symbolen und werden nicht als aktive Review-Arbeit
      angezeigt. Historische Signale bleiben im Backend erhalten; Reaktivierung erfolgt bewusst ueber die Watchlist.
    </section>
  );
}

function stateGuideTone(tone: "green" | "yellow" | "red" | "gray") {
  if (tone === "green") {
    return "border-emerald-300/30 bg-emerald-300/10 text-emerald-100";
  }
  if (tone === "yellow") {
    return "border-yellow-300/30 bg-yellow-300/10 text-yellow-100";
  }
  if (tone === "red") {
    return "border-red-300/30 bg-red-300/10 text-red-100";
  }
  return "border-slate-400/30 bg-slate-400/10 text-slate-100";
}

function SignalCard({ signal }: { signal: Signal }) {
  const reasoning = toTextList(signal.reasoning);
  const riskFlags = toTextList(signal.risk_flags);
  const noTradeReasons = toTextList(signal.no_trade_reasons);
  const decision = buildSignalDecision(signal);
  const explanation = signalDecisionExplanation(decision.kind);

  return (
    <article className="grid gap-4 p-4 sm:p-5 lg:grid-cols-[1fr_0.82fr]">
      <div className="min-w-0">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{formatStrategy(signal.strategy_type)}</p>
            <h3 className="mt-1 break-words text-2xl font-semibold tracking-tight text-slate-50">{signal.symbol}</h3>
          </div>
          <a
            className="inline-flex w-full justify-center rounded-xl border border-emerald-300/30 px-4 py-3 text-sm font-semibold text-emerald-200 hover:border-emerald-300/60 hover:text-emerald-100 sm:w-auto"
            href={`/signals/${signal.id}`}
          >
            Detail pruefen
          </a>
        </div>

        <div className={`mt-4 rounded-2xl border p-4 ${signalDecisionToneClass(decision.tone)}`}>
          <div className="flex flex-wrap items-center gap-3">
            <span className={`h-3 w-3 rounded-full ${signalDecisionDotClass(decision.tone)}`} />
            <p className="text-sm font-semibold uppercase tracking-[0.18em]">{decision.label}</p>
            <span className="rounded-full border border-current/20 px-3 py-1 text-xs">
              Qualitaet: {decision.quality}
            </span>
          </div>
          <p className="mt-3 text-lg font-semibold text-slate-50">{decision.headline}</p>
          <p className="mt-2 text-sm">{decision.action}</p>
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            <DecisionExplanationBox title="Was bedeutet das?" text={explanation.whatItMeans} />
            <DecisionExplanationBox title="Was jetzt?" text={explanation.whatNow} />
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-2">
          <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[signal.status]}`}>
            {statusLabel[signal.status]}
          </span>
          {signal.is_stale ? (
            <span className="rounded-full border border-orange-300/30 bg-orange-300/10 px-3 py-1 text-xs text-orange-100">
              Stale CSV Review
            </span>
          ) : null}
          {noTradeReasons.length > 0 ? (
            <span className="rounded-full border border-red-300/30 bg-red-300/10 px-3 py-1 text-xs text-red-100">
              No-Trade Context
            </span>
          ) : null}
          {riskFlags.length > 0 ? (
            <span className="rounded-full border border-orange-300/30 bg-orange-300/10 px-3 py-1 text-xs text-orange-100">
              {riskFlags.length} Risk Flags
            </span>
          ) : null}
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

        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
          <Metric label="Score" value={formatScore(signal)} />
          <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
          <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
        </div>

        {signal.is_stale ? <StaleNotice signal={signal} compact /> : null}

        <div className="mt-4 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Naechste manuelle Aktion</p>
          <p className="mt-2 text-sm font-medium text-slate-200">
            {signal.next_action || "Manuell weiter pruefen."}
          </p>
          <p className="mt-2 text-xs text-slate-500">Pruefhinweis, keine Order-Anweisung.</p>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Metric label="Entry Low" value={formatMoney(signal.entry_low)} compact />
          <Metric label="Entry High" value={formatMoney(signal.entry_high)} compact />
          <Metric label="Stop" value={formatMoney(signal.stop_loss)} compact />
          <Metric label="Target 1" value={formatMoney(signal.target_1)} compact />
        </div>
      </div>

      <div className="grid content-start gap-3 rounded-2xl border border-white/10 bg-slate-950/60 p-3 sm:p-4">
        <SignalContextDisclosure title="Begruendung" items={reasoning} empty="Keine Begruendung gespeichert." defaultOpen />
        <SignalContextDisclosure title="No-Trade Gruende" items={noTradeReasons} empty="Keine harten No-Trade Gruende gespeichert." tone="red" />
        <SignalContextDisclosure title="Risk Flags" items={riskFlags} empty="Keine Risk Flags gespeichert." tone="orange" />
      </div>
    </article>
  );
}

function DecisionExplanationBox({ text, title }: { text: string; title: string }) {
  return (
    <div className="rounded-xl border border-current/15 bg-slate-950/30 p-3 text-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] opacity-75">{title}</p>
      <p className="mt-2 opacity-90">{text}</p>
    </div>
  );
}

function SignalContextDisclosure({
  defaultOpen = false,
  empty,
  items,
  title,
  tone = "slate",
}: {
  defaultOpen?: boolean;
  empty: string;
  items: string[];
  title: string;
  tone?: "orange" | "red" | "slate";
}) {
  const itemClass =
    tone === "red"
      ? "border-red-300/20 bg-red-950/20 text-red-100"
      : tone === "orange"
        ? "border-orange-300/20 bg-orange-950/20 text-orange-100"
        : "border-white/10 bg-white/[0.03] text-slate-300";

  return (
    <details open={defaultOpen} className="rounded-xl border border-white/10 bg-slate-900/70 p-3">
      <summary className="cursor-pointer list-none text-sm font-semibold text-slate-100">
        {title} <span className="text-xs font-normal text-slate-500">({items.length})</span>
      </summary>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm">
          {items.map((item) => (
            <li key={item} className={`rounded-xl border p-3 ${itemClass}`}>
              {item.replaceAll("_", " ")}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-500">{empty}</p>
      )}
    </details>
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

function FilteredEmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Keine Signale fuer diese Filter.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Setze Filter zurueck oder pruefe bewusst auch No Setup, No Trade und stale Kandidaten.
      </p>
    </div>
  );
}

function filterActiveWatchlistSignals(signals: Signal[], watchlist: WatchlistItem[]) {
  if (watchlist.length === 0) {
    return signals;
  }

  const activeIds = new Set(watchlist.filter((item) => item.is_active).map((item) => item.id));
  return signals.filter((signal) => activeIds.has(signal.watchlist_item_id));
}

function buildSummary(signals: Signal[]) {
  const decisions = signals.map((signal) => buildSignalDecision(signal));
  return {
    paperCandidates: decisions.filter((decision) => decision.kind === "paper_candidate").length,
    observe: decisions.filter((decision) => decision.kind === "observe").length,
    noTrade: decisions.filter((decision) => decision.kind === "no_trade").length,
    dataProblem: decisions.filter((decision) => decision.kind === "data_problem").length,
  };
}

function buildActiveReviewItems(signals: Signal[]): ActiveReviewItem[] {
  return signals
    .map(toActiveReviewItem)
    .filter((item): item is ActiveReviewItem => item !== null)
    .sort(
      (left, right) =>
        left.priority - right.priority ||
        (right.signal.score ?? 0) - (left.signal.score ?? 0) ||
        left.signal.symbol.localeCompare(right.signal.symbol),
    );
}

function toActiveReviewItem(signal: Signal): ActiveReviewItem | null {
  const decision = buildSignalDecision(signal);

  if (decision.kind === "paper_candidate") {
    return {
      signal,
      label: "Paper-Kandidat",
      reason: "Starker manueller Review-Kandidat.",
      action: "Chart, 4H-Kontext, Risiko und Invalidation manuell pruefen.",
      priority: 0,
      tone: "green",
    };
  }

  if (signal.trigger_proximity_state === "at_trigger" && !signal.is_stale) {
    return {
      signal,
      label: "Am Trigger",
      reason: "Gespeicherter Trigger-Kontext ist nah genug fuer fokussierte Review.",
      action: "4H-Daten, Setup-Qualitaet und Risikoplan pruefen. Keine Order aus der App.",
      priority: 1,
      tone: "orange",
    };
  }

  if (signal.trigger_proximity_state === "near_trigger" && !signal.is_stale) {
    return {
      signal,
      label: "Nah dran",
      reason: "Trigger-Naehe macht das Symbol relevant fuer die kleine Trigger-Liste.",
      action: "4H-CSV gezielt aktualisieren und Detailkarte pruefen.",
      priority: 2,
      tone: "orange",
    };
  }

  if (decision.kind === "observe") {
    return {
      signal,
      label: "Beobachten",
      reason: "Interessant, aber noch kein klarer Trigger oder Paper-Kandidat.",
      action: "Auf der aktiven Review-Liste lassen. `trigger: missing` ist normal; nach neuer 1D/4H-CSV erneut pruefen.",
      priority: 3,
      tone: "yellow",
    };
  }

  if (decision.kind === "data_problem" || signal.is_stale) {
    return {
      signal,
      label: "Datenproblem",
      reason: signal.is_stale ? "Datenstand ist stale." : "Daten oder Freshness blockieren die Review.",
      action: "CSV-Arbeitsplan auf /import nutzen und fehlende oder stale Timeframes gezielt aktualisieren.",
      priority: 4,
      tone: "gray",
    };
  }

  return null;
}

function buildTriggerRadarItems(signals: Signal[]): TriggerRadarItem[] {
  return signals
    .map(toTriggerRadarItem)
    .filter((item): item is TriggerRadarItem => item !== null)
    .sort(
      (left, right) =>
        triggerRadarPriority(left.state) - triggerRadarPriority(right.state) ||
        (right.signal.score ?? 0) - (left.signal.score ?? 0),
    );
}

function toTriggerRadarItem(signal: Signal): TriggerRadarItem | null {
  const decision = buildSignalDecision(signal);
  const noTradeReasons = toTextList(signal.no_trade_reasons);
  if (
    decision.kind === "no_trade" ||
    decision.kind === "data_problem" ||
    noTradeReasons.length > 0 ||
    signal.is_stale ||
    !signal.trigger_level ||
    signal.trigger_proximity_state === "not_available"
  ) {
    return null;
  }

  if (signal.trigger_proximity_state === "at_trigger") {
    return {
      signal,
      state: "at_trigger",
      label: "Am Trigger",
      action: "Jetzt 4H-Freshness, Detailkarte und Risikoplan manuell pruefen. Keine automatische Order.",
    };
  }
  if (signal.trigger_proximity_state === "near_trigger") {
    return {
      signal,
      state: "near_trigger",
      label: "Nah dran",
      action: "Auf der kleinen Trigger-Liste halten und 4H-CSV gezielt aktualisieren.",
    };
  }
  return {
    signal,
    state: "far_from_trigger",
    label: "Weiter weg",
    action: "Trigger bleibt nur Beobachtung. Nicht als aktuellen Einstieg interpretieren.",
  };
}

function triggerRadarPriority(state: TriggerRadarState) {
  return {
    at_trigger: 0,
    near_trigger: 1,
    far_from_trigger: 2,
  }[state];
}

function rankSignals(signals: Signal[]) {
  return [...signals].sort((left, right) => {
    const leftDecision = buildSignalDecision(left);
    const rightDecision = buildSignalDecision(right);
    if (leftDecision.priority !== rightDecision.priority) {
      return leftDecision.priority - rightDecision.priority;
    }
    return (right.score ?? 0) - (left.score ?? 0);
  });
}

function filterSignals(signals: Signal[], filters: SignalFilters) {
  const symbol = filters.symbol.trim().toLowerCase();

  return signals.filter((signal) => {
    if (symbol && !signal.symbol.toLowerCase().includes(symbol)) {
      return false;
    }
    if (filters.status !== "all" && signal.status !== filters.status) {
      return false;
    }
    if (filters.strategy !== "all" && signal.strategy_type !== filters.strategy) {
      return false;
    }
    if (filters.scoreClass !== "all" && signal.score_class !== filters.scoreClass) {
      return false;
    }
    if (filters.freshness === "stale" && !signal.is_stale) {
      return false;
    }
    if (filters.freshness === "fresh" && signal.is_stale) {
      return false;
    }
    if (filters.context === "risk_flags" && toTextList(signal.risk_flags).length === 0) {
      return false;
    }
    if (filters.context === "no_trade_reasons" && toTextList(signal.no_trade_reasons).length === 0) {
      return false;
    }
    return true;
  });
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

function toTextList(value: unknown) {
  if (Array.isArray(value)) {
    return value.map(String);
  }
  if (value && typeof value === "object") {
    return Object.values(value).map(String);
  }
  return [];
}
