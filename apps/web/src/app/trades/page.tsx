"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { createTrade, exportTradesCsv, fetchSignals, fetchTrades, fetchWatchlist } from "@/lib/api";
import type { Signal, StrategyType } from "@/types/signals";
import type { Trade, TradeCreatePayload, TradeFilters } from "@/types/trades";
import type { WatchlistItem } from "@/types/watchlist";

type TradeForm = {
  mode: "watchlist" | "signal";
  watchlist_item_id: string;
  signal_id: string;
  strategy_type: StrategyType;
  entry_price: string;
  stop_loss: string;
  target_1: string;
  target_2: string;
  position_size: string;
  fees: string;
  opened_at: string;
  notes: string;
};

type FilterForm = {
  opened_from: string;
  opened_to: string;
  strategy_type: "" | StrategyType;
  asset_class: "" | "stock" | "crypto";
  reviewed: "" | "true" | "false";
  setup_rule_followed: "" | "true" | "false";
};

const emptyForm: TradeForm = {
  mode: "watchlist",
  watchlist_item_id: "",
  signal_id: "",
  strategy_type: "trend_pullback_long",
  entry_price: "",
  stop_loss: "",
  target_1: "",
  target_2: "",
  position_size: "",
  fees: "",
  opened_at: "",
  notes: "",
};

const emptyFilters: FilterForm = {
  opened_from: "",
  opened_to: "",
  strategy_type: "",
  asset_class: "",
  reviewed: "",
  setup_rule_followed: "",
};

export default function TradesPage() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [signals, setSignals] = useState<Signal[]>([]);
  const [form, setForm] = useState<TradeForm>(emptyForm);
  const [filters, setFilters] = useState<FilterForm>(emptyFilters);
  const [createdTrade, setCreatedTrade] = useState<Trade | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedTrades, loadedWatchlist, loadedSignals] = await Promise.all([
        fetchTrades(toTradeFilters(filters)),
        fetchWatchlist(),
        fetchSignals(),
      ]);
      setTrades(loadedTrades);
      setWatchlist(loadedWatchlist);
      setSignals(loadedSignals);
      setForm((current) => ({
        ...current,
        watchlist_item_id: current.watchlist_item_id || loadedWatchlist[0]?.id.toString() || "",
        signal_id: current.signal_id || loadedSignals[0]?.id.toString() || "",
      }));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function submitFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadData();
  }

  async function resetFilters() {
    setFilters(emptyFilters);
    setIsLoading(true);
    setError(null);
    try {
      setTrades(await fetchTrades());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler.");
    } finally {
      setIsLoading(false);
    }
  }

  const selectedSignal = useMemo(
    () => signals.find((signal) => signal.id.toString() === form.signal_id) ?? null,
    [form.signal_id, signals],
  );
  const selectedWatchlistItem = useMemo(
    () => watchlist.find((item) => item.id.toString() === form.watchlist_item_id) ?? null,
    [form.watchlist_item_id, watchlist],
  );

  async function handleExport() {
    setExportError(null);
    try {
      await exportTradesCsv();
    } catch (err) {
      setExportError(err instanceof Error ? err.message : "Export fehlgeschlagen.");
    }
  }

  async function submitTrade(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setCreatedTrade(null);

    const payload = buildPayload(form);
    if (!payload) {
      setError("Waehle ein Signal oder Watchlist-Symbol und fuelle die Pflichtfelder aus.");
      return;
    }

    setIsSaving(true);
    try {
      const trade = await createTrade(payload);
      setCreatedTrade(trade);
      setForm({
        ...emptyForm,
        watchlist_item_id: form.watchlist_item_id,
        signal_id: form.signal_id,
        opened_at: form.opened_at,
      });
      await loadData();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unbekannter Fehler.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#1d4ed8,transparent_34%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Trades</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Manuelle Trades loggen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Erfasse Trades, die du ausserhalb der App manuell ausgefuehrt hast. Die App
                dokumentiert Risiko und R-Werte, fuehrt aber keine Orders aus.
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
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Zurueck zum Dashboard
              </a>
            </div>
          </div>
        </header>

        {exportError ? <ErrorMessage message={exportError} /> : null}
        {error ? <ErrorMessage message={error} /> : null}

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <form onSubmit={submitTrade} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold">Trade erfassen</h2>
                <p className="mt-2 text-sm text-slate-400">
                  Long-only MVP: Entry muss ueber Stop liegen. Risiko wird zur Dokumentation vom Backend berechnet.
                </p>
              </div>
              <button
                type="button"
                onClick={() => void loadData()}
                className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
              >
                Daten laden
              </button>
            </div>

            <div className="mt-6 grid gap-4">
              <label className="grid gap-2 text-sm text-slate-300">
                Quelle
                <select
                  value={form.mode}
                  onChange={(event) => setForm({ ...form, mode: event.target.value as TradeForm["mode"] })}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                >
                  <option value="watchlist">Direkt von Watchlist</option>
                  <option value="signal">Aus Signal-Bewertung</option>
                </select>
              </label>

              {form.mode === "signal" ? (
                <label className="grid gap-2 text-sm text-slate-300">
                  Signal
                  <select
                    required
                    disabled={signals.length === 0}
                    value={form.signal_id}
                    onChange={(event) => setForm({ ...form, signal_id: event.target.value })}
                    className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300 disabled:opacity-60"
                  >
                    {signals.map((signal) => (
                      <option key={signal.id} value={signal.id}>
                        {signal.symbol} - {formatStrategy(signal.strategy_type)} - {signal.status}
                      </option>
                    ))}
                  </select>
                </label>
              ) : (
                <>
                  <label className="grid gap-2 text-sm text-slate-300">
                    Symbol
                    <select
                      required
                      disabled={watchlist.length === 0}
                      value={form.watchlist_item_id}
                      onChange={(event) => setForm({ ...form, watchlist_item_id: event.target.value })}
                      className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300 disabled:opacity-60"
                    >
                      {watchlist.map((item) => (
                        <option key={item.id} value={item.id}>
                          {item.symbol} {item.name ? `- ${item.name}` : ""}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label className="grid gap-2 text-sm text-slate-300">
                    Strategie
                    <select
                      value={form.strategy_type}
                      onChange={(event) => setForm({ ...form, strategy_type: event.target.value as StrategyType })}
                      className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                    >
                      <option value="trend_pullback_long">Trend Pullback Long</option>
                      <option value="base_breakout_long">Base Breakout Long</option>
                    </select>
                  </label>
                </>
              )}

              <ContextCard signal={selectedSignal} watchlistItem={selectedWatchlistItem} mode={form.mode} />

              <div className="grid gap-4 sm:grid-cols-2">
                <NumberField label="Entry Price" value={form.entry_price} onChange={(value) => setForm({ ...form, entry_price: value })} />
                <NumberField label="Stop Loss" value={form.stop_loss} onChange={(value) => setForm({ ...form, stop_loss: value })} />
                <NumberField label="Target 1 optional" value={form.target_1} onChange={(value) => setForm({ ...form, target_1: value })} />
                <NumberField label="Target 2 optional" value={form.target_2} onChange={(value) => setForm({ ...form, target_2: value })} />
                <NumberField label="Position Size" value={form.position_size} onChange={(value) => setForm({ ...form, position_size: value })} />
                <NumberField label="Fees optional" value={form.fees} onChange={(value) => setForm({ ...form, fees: value })} />
              </div>

              <label className="grid gap-2 text-sm text-slate-300">
                Opened At
                <input
                  required
                  type="datetime-local"
                  value={form.opened_at}
                  onChange={(event) => setForm({ ...form, opened_at: event.target.value })}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                />
              </label>

              <label className="grid gap-2 text-sm text-slate-300">
                Notes
                <textarea
                  value={form.notes}
                  onChange={(event) => setForm({ ...form, notes: event.target.value })}
                  className="min-h-24 rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                  placeholder="Warum hast du den Trade ausserhalb der App manuell ausgefuehrt?"
                />
              </label>

              <button
                disabled={isSaving || isLoading}
                type="submit"
                className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
              >
                {isSaving ? "Speichere..." : "Trade manuell loggen"}
              </button>
            </div>
          </form>

          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold">Offene und geloggte Trades</h2>
                <p className="mt-1 text-sm text-slate-400">Manuelle Dokumentation, keine Orderausfuehrung.</p>
              </div>
              <span className="text-sm text-slate-400">{trades.length} Trades</span>
            </div>

            {createdTrade ? <CreatedTradeCard trade={createdTrade} /> : null}

            <TradeFilterForm
              filters={filters}
              isLoading={isLoading}
              onChange={setFilters}
              onReset={() => void resetFilters()}
              onSubmit={submitFilters}
            />

            <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
              {isLoading ? (
                <p className="p-5 text-sm text-slate-400">Trades werden geladen...</p>
              ) : trades.length === 0 ? (
                <EmptyState />
              ) : (
                <div className="divide-y divide-white/10">
                  {trades.map((trade) => (
                    <TradeCard key={trade.id} trade={trade} />
                  ))}
                </div>
              )}
            </div>
          </section>
        </section>
      </section>
    </main>
  );
}

function buildPayload(form: TradeForm): TradeCreatePayload | null {
  if (!form.entry_price || !form.stop_loss || !form.position_size || !form.opened_at) {
    return null;
  }

  const payload: TradeCreatePayload = {
    entry_price: form.entry_price,
    stop_loss: form.stop_loss,
    target_1: form.target_1 || null,
    target_2: form.target_2 || null,
    position_size: form.position_size,
    fees: form.fees || null,
    opened_at: new Date(form.opened_at).toISOString(),
    notes: form.notes || null,
  };

  if (form.mode === "signal") {
    if (!form.signal_id) {
      return null;
    }
    payload.signal_id = Number(form.signal_id);
    return payload;
  }

  if (!form.watchlist_item_id) {
    return null;
  }
  payload.watchlist_item_id = Number(form.watchlist_item_id);
  payload.strategy_type = form.strategy_type;
  return payload;
}

function toTradeFilters(filters: FilterForm): TradeFilters {
  return {
    opened_from: filters.opened_from ? new Date(filters.opened_from).toISOString() : undefined,
    opened_to: filters.opened_to ? new Date(filters.opened_to).toISOString() : undefined,
    strategy_type: filters.strategy_type || undefined,
    asset_class: filters.asset_class || undefined,
    reviewed: filters.reviewed === "" ? undefined : filters.reviewed === "true",
    setup_rule_followed:
      filters.setup_rule_followed === "" ? undefined : filters.setup_rule_followed === "true",
  };
}

function TradeFilterForm({
  filters,
  isLoading,
  onChange,
  onReset,
  onSubmit,
}: {
  filters: FilterForm;
  isLoading: boolean;
  onChange: (filters: FilterForm) => void;
  onReset: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form onSubmit={onSubmit} className="mt-5 rounded-2xl border border-white/10 bg-slate-950/60 p-4">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <label className="grid gap-2 text-sm text-slate-300">
          Opened from
          <input
            type="datetime-local"
            value={filters.opened_from}
            onChange={(event) => onChange({ ...filters, opened_from: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
          />
        </label>
        <label className="grid gap-2 text-sm text-slate-300">
          Opened to
          <input
            type="datetime-local"
            value={filters.opened_to}
            onChange={(event) => onChange({ ...filters, opened_to: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
          />
        </label>
        <label className="grid gap-2 text-sm text-slate-300">
          Strategie
          <select
            value={filters.strategy_type}
            onChange={(event) => onChange({ ...filters, strategy_type: event.target.value as FilterForm["strategy_type"] })}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="">Alle</option>
            <option value="trend_pullback_long">Trend Pullback Long</option>
            <option value="base_breakout_long">Base Breakout Long</option>
          </select>
        </label>
        <label className="grid gap-2 text-sm text-slate-300">
          Asset Class
          <select
            value={filters.asset_class}
            onChange={(event) => onChange({ ...filters, asset_class: event.target.value as FilterForm["asset_class"] })}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="">Alle</option>
            <option value="stock">Stock</option>
            <option value="crypto">Crypto</option>
          </select>
        </label>
        <label className="grid gap-2 text-sm text-slate-300">
          Review
          <select
            value={filters.reviewed}
            onChange={(event) => onChange({ ...filters, reviewed: event.target.value as FilterForm["reviewed"] })}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="">Alle</option>
            <option value="true">Review vorhanden</option>
            <option value="false">Noch nicht reviewed</option>
          </select>
        </label>
        <label className="grid gap-2 text-sm text-slate-300">
          Setup-Regel
          <select
            value={filters.setup_rule_followed}
            onChange={(event) => onChange({ ...filters, setup_rule_followed: event.target.value as FilterForm["setup_rule_followed"] })}
            className="rounded-xl border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="">Alle</option>
            <option value="true">Regel befolgt</option>
            <option value="false">Regel nicht befolgt</option>
          </select>
        </label>
      </div>
      <div className="mt-4 flex flex-col gap-3 sm:flex-row">
        <button
          disabled={isLoading}
          type="submit"
          className="rounded-xl bg-emerald-400 px-4 py-2 font-semibold text-slate-950 disabled:opacity-60"
        >
          Filter anwenden
        </button>
        <button
          disabled={isLoading}
          type="button"
          onClick={onReset}
          className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50 disabled:opacity-60"
        >
          Filter zuruecksetzen
        </button>
      </div>
    </form>
  );
}

function ContextCard({
  mode,
  signal,
  watchlistItem,
}: {
  mode: TradeForm["mode"];
  signal: Signal | null;
  watchlistItem: WatchlistItem | null;
}) {
  const title = mode === "signal" ? signal?.symbol : watchlistItem?.symbol;
  const meta = mode === "signal" ? signal ? `${formatStrategy(signal.strategy_type)} / ${signal.status}` : null : watchlistItem?.asset_class;

  return title ? (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
      <p className="font-medium text-slate-100">{title}</p>
      <p className="mt-1">{meta}</p>
    </div>
  ) : null;
}

function NumberField({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <input
        required={!label.includes("optional")}
        type="number"
        min="0"
        step="0.00000001"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
      />
    </label>
  );
}

function CreatedTradeCard({ trade }: { trade: Trade }) {
  return (
    <div className="mt-5 rounded-2xl border border-emerald-300/30 bg-emerald-300/10 p-4 text-sm text-emerald-50">
      <p className="font-semibold">Trade #{trade.id} gespeichert.</p>
      <p className="mt-1">
        Initial Risk: {formatMoney(trade.initial_risk_amount)} / R:R {formatR(trade.initial_risk_reward)}
      </p>
    </div>
  );
}

function TradeCard({ trade }: { trade: Trade }) {
  return (
    <article className="grid gap-5 p-5 lg:grid-cols-[1fr_0.9fr]">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="text-lg font-semibold">{trade.symbol}</h3>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{trade.status}</span>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{trade.asset_class}</span>
          <ReviewStatusBadge trade={trade} />
          <span className="text-sm text-slate-400">{formatStrategy(trade.strategy_type)}</span>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-4">
          <Metric label="Entry" value={formatMoney(trade.entry_price)} />
          <Metric label="Stop" value={formatMoney(trade.stop_loss)} />
          <Metric label="Risk" value={formatMoney(trade.initial_risk_amount)} />
          <Metric label="R:R" value={formatR(trade.initial_risk_reward)} />
        </div>
        <a
          className="mt-4 inline-flex rounded-xl border border-white/10 px-4 py-2 text-sm text-emerald-300 hover:border-emerald-300/50 hover:text-emerald-200"
          href={`/trades/${trade.id}`}
        >
          Trade im Detail dokumentieren
        </a>
      </div>
      <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <Metric label="Position" value={formatNumber(trade.position_size)} />
          <Metric label="Opened" value={formatDateTime(trade.opened_at)} />
          <Metric label="Target 1" value={formatMoney(trade.target_1)} />
          <Metric label="Target 2" value={formatMoney(trade.target_2)} />
        </div>
        {trade.notes ? <p className="mt-4 text-sm text-slate-300">{trade.notes}</p> : null}
      </div>
    </article>
  );
}

function ReviewStatusBadge({ trade }: { trade: Trade }) {
  if (trade.review_status === "reviewed") {
    return <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">Review komplett</span>;
  }
  if (trade.review_status === "needs_review") {
    return <span className="rounded-full bg-yellow-300/10 px-3 py-1 text-xs text-yellow-100">Review offen</span>;
  }
  return <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">Review nach Close</span>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch keine Trades geloggt.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Logge nur Trades, die du manuell ausserhalb der App ausgefuehrt hast. Keine Orders werden automatisch platziert.
      </p>
    </div>
  );
}

function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="whitespace-pre-line rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
      {message}
    </div>
  );
}

function formatStrategy(strategy: StrategyType) {
  return strategy === "trend_pullback_long" ? "Trend Pullback Long" : "Base Breakout Long";
}

function formatMoney(value: string | null) {
  return value ? formatNumber(value) : "-";
}

function formatR(value: string | null) {
  return value ? `${formatNumber(value)}R` : "-";
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
