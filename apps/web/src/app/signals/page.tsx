"use client";

import { useEffect, useMemo, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { fetchSignals, redirectToLoginOnAuthError } from "@/lib/api";
import type { ScoreClass, Signal, SignalStatus, StrategyType } from "@/types/signals";

type SignalFilters = {
  symbol: string;
  status: "all" | SignalStatus;
  strategy: "all" | StrategyType;
  scoreClass: "all" | ScoreClass;
  freshness: "all" | "fresh" | "stale";
  context: "all" | "risk_flags" | "no_trade_reasons";
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
  const [filters, setFilters] = useState<SignalFilters>(emptyFilters);
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
  const filteredSignals = useMemo(() => filterSignals(signals, filters), [signals, filters]);

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

          <SignalFiltersPanel
            filters={filters}
            resultCount={filteredSignals.length}
            totalCount={signals.length}
            onChange={setFilters}
            onReset={() => setFilters(emptyFilters)}
          />

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Signale werden geladen...</p>
            ) : signals.length === 0 ? (
              <EmptyState />
            ) : filteredSignals.length === 0 ? (
              <FilteredEmptyState />
            ) : (
              <div className="divide-y divide-white/10">
                {filteredSignals.map((signal) => (
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
            ["triggered", "Triggered"],
            ["armed", "Armed"],
            ["watchlist", "Watchlist"],
            ["no_setup", "No Setup"],
            ["invalidated", "Invalidated"],
            ["missed", "Missed"],
            ["expired", "Expired"],
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
            ["all", "Alle Score Classes"],
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

function SummaryCard({ label, value, tone = "border-white/10" }: { label: string; value: string; tone?: string }) {
  return (
    <article className={`rounded-2xl border ${tone} bg-slate-950/70 p-5`}>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-semibold">{value}</p>
    </article>
  );
}

function SignalCard({ signal }: { signal: Signal }) {
  const reasoning = toTextList(signal.reasoning);
  const riskFlags = toTextList(signal.risk_flags);
  const noTradeReasons = toTextList(signal.no_trade_reasons);

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

function buildSummary(signals: Signal[]) {
  return {
    armed: signals.filter((signal) => signal.status === "armed").length,
    watchlist: signals.filter((signal) => signal.status === "watchlist").length,
    stale: signals.filter((signal) => signal.is_stale).length,
  };
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
