"use client";

import { FormEvent, useEffect, useState } from "react";

import { AuthenticatedHeaderActions } from "@/components/authenticated-header-actions";
import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import {
  API_BASE_URL,
  assertAuthenticatedResponse,
  fetchBenchmarkContextStatus,
  redirectToLoginOnAuthError,
} from "@/lib/api";
import type {
  AssetClass,
  BenchmarkContextStatus,
  MarketDataFreshnessStatus,
  MarketDataSource,
  MarketDataSyncStatus,
  WatchlistItem,
} from "@/types/watchlist";

type WatchlistForm = {
  symbol: string;
  name: string;
  asset_class: AssetClass;
  exchange: string;
  currency: string;
  notes: string;
};

const emptyForm: WatchlistForm = {
  symbol: "",
  name: "",
  asset_class: "stock",
  exchange: "",
  currency: "",
  notes: "",
};

export default function WatchlistPage() {
  const authStatus = useProtectedRoute();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [benchmarkContexts, setBenchmarkContexts] = useState<BenchmarkContextStatus[]>([]);
  const [form, setForm] = useState<WatchlistForm>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadItems() {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/watchlist`, { cache: "no-store", credentials: "include" });
      assertAuthenticatedResponse(response);
      if (!response.ok) {
        throw new Error("Watchlist konnte nicht geladen werden.");
      }
      const [loadedItems, loadedBenchmarkContexts] = await Promise.all([
        response.json(),
        fetchBenchmarkContextStatus(),
      ]);
      setItems(loadedItems);
      setBenchmarkContexts(loadedBenchmarkContexts);
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
      void loadItems();
    }
  }, [authStatus]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }

  function editItem(item: WatchlistItem) {
    setEditingId(item.id);
    setForm({
      symbol: item.symbol,
      name: item.name ?? "",
      asset_class: item.asset_class,
      exchange: item.exchange ?? "",
      currency: item.currency ?? "",
      notes: item.notes ?? "",
    });
  }

  async function saveItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);

    const payload = {
      ...form,
      name: form.name || null,
      exchange: form.exchange || null,
      currency: form.currency || null,
      notes: form.notes || null,
    };

    try {
      const response = await fetch(
        editingId ? `${API_BASE_URL}/watchlist/${editingId}` : `${API_BASE_URL}/watchlist`,
        {
          method: editingId ? "PATCH" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          credentials: "include",
        },
      );

      assertAuthenticatedResponse(response);
      if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail ?? "Watchlist-Eintrag konnte nicht gespeichert werden.");
      }

      resetForm();
      await loadItems();
    } catch (saveError) {
      if (redirectToLoginOnAuthError(saveError)) {
        return;
      }
      setError(saveError instanceof Error ? saveError.message : "Unbekannter Fehler.");
    } finally {
      setIsSaving(false);
    }
  }

  async function deactivateItem(item: WatchlistItem) {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/watchlist/${item.id}`, {
        method: "DELETE",
        credentials: "include",
      });
      assertAuthenticatedResponse(response);
      if (!response.ok) {
        throw new Error("Watchlist-Eintrag konnte nicht deaktiviert werden.");
      }
      await loadItems();
    } catch (deleteError) {
      if (redirectToLoginOnAuthError(deleteError)) {
        return;
      }
      setError(deleteError instanceof Error ? deleteError.message : "Unbekannter Fehler.");
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 sm:p-8 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">Watchlist</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Symbole verwalten</h1>
            <p className="mt-3 max-w-2xl text-slate-300">
              Pflege Aktien und Krypto-Symbole als Grundlage fuer CSV-Import, Setup-Bewertungen
              und manuelles Trade Logging. Source/Freshness zeigt Datenkontext, keine Live-Preise
              und keine Trade-Anweisung.
            </p>
          </div>
          <AuthenticatedHeaderActions />
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <WatchlistBeginnerGuide />

        <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <form onSubmit={saveItem} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">{editingId ? "Eintrag bearbeiten" : "Neues Symbol"}</h2>
            <div className="mt-5 grid gap-4">
              <label className="grid gap-2 text-sm text-slate-300">
                Symbol
                <input
                  required
                  maxLength={32}
                  value={form.symbol}
                  onChange={(event) => setForm({ ...form, symbol: event.target.value })}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                  placeholder="AAPL oder BTCUSDT"
                />
              </label>
              <label className="grid gap-2 text-sm text-slate-300">
                Name optional
                <input
                  value={form.name}
                  onChange={(event) => setForm({ ...form, name: event.target.value })}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                  placeholder="Apple Inc."
                />
              </label>
              <label className="grid gap-2 text-sm text-slate-300">
                Asset Class
                <select
                  value={form.asset_class}
                  onChange={(event) =>
                    setForm({ ...form, asset_class: event.target.value as AssetClass })
                  }
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                >
                  <option value="stock">Stock</option>
                  <option value="crypto">Crypto</option>
                </select>
              </label>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="grid gap-2 text-sm text-slate-300">
                  Exchange
                  <input
                    value={form.exchange}
                    onChange={(event) => setForm({ ...form, exchange: event.target.value })}
                    className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                    placeholder="NASDAQ"
                  />
                </label>
                <label className="grid gap-2 text-sm text-slate-300">
                  Currency
                  <input
                    value={form.currency}
                    onChange={(event) => setForm({ ...form, currency: event.target.value })}
                    className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                    placeholder="USD"
                  />
                </label>
              </div>
              <label className="grid gap-2 text-sm text-slate-300">
                Notes
                <textarea
                  value={form.notes}
                  onChange={(event) => setForm({ ...form, notes: event.target.value })}
                  className="min-h-24 rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                  placeholder="Warum ist das Symbol relevant?"
                />
              </label>
              <div className="flex gap-3">
                <button
                  disabled={isSaving}
                  className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
                  type="submit"
                >
                  {isSaving ? "Speichern..." : editingId ? "Aktualisieren" : "Hinzufuegen"}
                </button>
                {editingId ? (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="rounded-xl border border-white/10 px-5 py-3 text-slate-200"
                  >
                    Abbrechen
                  </button>
                ) : null}
              </div>
            </div>
          </form>

          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-semibold">Aktive Liste</h2>
              <span className="text-sm text-slate-400">{items.length} Symbole</span>
            </div>
            <p className="mt-2 text-sm text-slate-400">
              Aktive Symbole sind Teil des Import- und Analyse-Workflows. Inaktive Symbole bleiben als
              Historie erhalten und werden unten separat angezeigt.
            </p>
            <div className="mt-5 overflow-hidden rounded-2xl border border-white/10">
              {isLoading ? (
                <p className="p-5 text-sm text-slate-400">Watchlist wird geladen...</p>
              ) : items.length === 0 ? (
                <p className="p-5 text-sm text-slate-400">Noch keine Symbole erfasst.</p>
              ) : (
                <div className="divide-y divide-white/10">
                  {items.filter((item) => item.is_active).map((item) => (
                    <article
                      key={item.id}
                      className="grid gap-4 p-5 md:grid-cols-[1fr_auto] md:items-center"
                    >
                      <div>
                        <div className="flex flex-wrap items-center gap-3">
                          <h3 className="text-lg font-semibold">{item.symbol}</h3>
                          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
                            {item.asset_class}
                          </span>
                          <span
                            className={`rounded-full px-3 py-1 text-xs ${
                              item.is_active
                                ? "bg-emerald-400/10 text-emerald-200"
                                : "bg-slate-700 text-slate-300"
                            }`}
                          >
                            {item.is_active ? "Active" : "Inactive"}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-slate-400">
                          {[item.name, item.exchange, item.currency].filter(Boolean).join(" / ") ||
                            "Keine Zusatzdaten"}
                        </p>
                        {item.notes ? <p className="mt-3 text-sm text-slate-300">{item.notes}</p> : null}
                        <MarketDataSummary item={item} />
                      </div>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => editItem(item)}
                          className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200"
                        >
                          Bearbeiten
                        </button>
                        {item.is_active ? (
                          <button
                            type="button"
                            onClick={() => deactivateItem(item)}
                            className="rounded-xl border border-red-400/30 px-4 py-2 text-sm text-red-100"
                          >
                            Deaktivieren
                          </button>
                        ) : null}
                      </div>
                    </article>
                  ))}
                  {items.some((item) => !item.is_active) ? (
                    <InactiveWatchlistSection items={items.filter((item) => !item.is_active)} onEdit={editItem} />
                  ) : null}
                </div>
              )}
            </div>
          </section>
        </section>

        <BenchmarkContextPanel contexts={benchmarkContexts} />
      </section>
    </main>
  );
}

function WatchlistBeginnerGuide() {
  return (
    <section className="rounded-3xl border border-emerald-300/20 bg-emerald-300/[0.04] p-6">
      <p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-300">Erster Schritt</p>
      <h2 className="mt-2 text-xl font-semibold">Symbole sauber anlegen</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        <HelpCard title="Stocks" text="Nutze einfache Ticker wie AAPL, MSFT, NVDA oder GOOG. Beispiele sind nur Formathilfe, keine Trade-Ideen." />
        <HelpCard title="Crypto" text="Crypto-Symbole sind provider-abhaengig. Pruefe das Format vor Import oder Provider-Sync, z.B. ob BTCUSDT erwartet wird." />
        <HelpCard title="Exchange & Currency" text="Exchange beschreibt den Handelsplatz wie NASDAQ. Currency ist die Kurswaehrung wie USD oder EUR." />
        <HelpCard title="Doppelte & Inaktive" text="Doppelte Symbole werden vom Backend abgelehnt. Deaktivieren entfernt ein Symbol nur aus dem aktiven Workflow, nicht aus der Historie." />
      </div>
      <p className="mt-4 rounded-2xl border border-yellow-300/20 bg-yellow-300/10 p-3 text-sm text-yellow-50">
        Hinzufuegen speichert nur das Watchlist-Symbol. Es ruft keine Marktdaten ab, startet keine Analyse
        und erzeugt keine Signale, Trades oder Orders.
      </p>
    </section>
  );
}

function HelpCard({ text, title }: { text: string; title: string }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-300">
      <p className="font-semibold text-slate-100">{title}</p>
      <p className="mt-2 text-slate-400">{text}</p>
    </article>
  );
}

function InactiveWatchlistSection({
  items,
  onEdit,
}: {
  items: WatchlistItem[];
  onEdit: (item: WatchlistItem) => void;
}) {
  return (
    <details className="bg-slate-950/40">
      <summary className="cursor-pointer list-none p-5 text-sm font-semibold text-slate-300">
        Inaktive Symbole anzeigen ({items.length})
      </summary>
      <div className="divide-y divide-white/10 border-t border-white/10">
        {items.map((item) => (
          <article key={item.id} className="grid gap-4 p-5 opacity-80 md:grid-cols-[1fr_auto] md:items-center">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h3 className="text-lg font-semibold">{item.symbol}</h3>
                <span className="rounded-full bg-slate-700 px-3 py-1 text-xs text-slate-300">Inactive</span>
              </div>
              <p className="mt-1 text-sm text-slate-400">
                Historie bleibt erhalten. Das Symbol ist nicht Teil der aktiven Import- und Analysearbeit.
              </p>
            </div>
            <button
              type="button"
              onClick={() => onEdit(item)}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200"
            >
              Bearbeiten
            </button>
          </article>
        ))}
      </div>
    </details>
  );
}

function BenchmarkContextPanel({ contexts }: { contexts: BenchmarkContextStatus[] }) {
  return (
    <section className="rounded-3xl border border-sky-300/20 bg-sky-300/5 p-6">
      <p className="text-xs uppercase tracking-[0.3em] text-sky-200">Benchmark Context</p>
      <h2 className="mt-2 text-xl font-semibold">Regime-Kontext fuer Strategie-Kalibrierung</h2>
      <p className="mt-2 max-w-3xl text-sm text-slate-300">
        Diese Checkliste zeigt, welche gespeicherten Daily-Benchmarkdaten fuer Aktien und Krypto
        vorhanden sind. Sie startet keine Analyse, ruft keine Live-Daten ab und erstellt keine
        Trades, Alerts oder Orders.
      </p>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        {contexts.map((context) => (
          <article key={context.asset_class} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold uppercase text-slate-100">{context.asset_class}</h3>
                <p className="mt-1 text-sm text-slate-400">{context.guidance}</p>
              </div>
              <span className={`rounded-full px-3 py-1 text-xs ${contextReadyClass(context)}`}>
                {context.requirements.every((requirement) => requirement.status === "ready") ? "ready" : "review"}
              </span>
            </div>
            <div className="mt-4 grid gap-3">
              {context.requirements.map((requirement) => (
                <div key={requirement.key} className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium text-slate-100">{requirement.key}</span>
                    <span className={`rounded-full px-2 py-1 text-xs ${benchmarkRequirementClass(requirement.status)}`}>
                      {formatLabel(requirement.status)}
                    </span>
                    {requirement.present_symbol ? (
                      <span className="rounded-full bg-slate-800 px-2 py-1 text-xs text-slate-300">
                        {requirement.present_symbol}
                      </span>
                    ) : null}
                  </div>
                  <p className="mt-2 text-sm text-slate-400">{requirement.message}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Akzeptiert: {requirement.accepted_symbols.join(", ")}
                  </p>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function MarketDataSummary({ item }: { item: WatchlistItem }) {
  const summary = item.latest_market_data;
  if (!summary) {
    return (
      <div className="mt-4 rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-3 text-sm text-yellow-100">
        Keine Marktdaten gespeichert. Importiere zuerst CSV-Daten; ohne Daten gibt es kein aktuelles
        Setup-Signal.
      </div>
    );
  }

  return (
    <div className="mt-4 grid gap-3 rounded-2xl border border-white/10 bg-slate-950/70 p-3 text-sm text-slate-300">
      <div className="flex flex-wrap gap-2">
        <span className="rounded-full border border-sky-300/20 bg-sky-300/10 px-3 py-1 text-xs text-sky-100">
          Source: {formatMarketDataSource(summary.source)}
        </span>
        <span className={`rounded-full border px-3 py-1 text-xs ${freshnessBadgeClass(summary.freshness_status)}`}>
          Freshness: {formatLabel(summary.freshness_status)}
        </span>
        <span className="rounded-full border border-white/10 bg-slate-800 px-3 py-1 text-xs text-slate-300">
          Sync: {formatLabel(summary.sync_status)}
        </span>
      </div>
      <div className="grid gap-2 sm:grid-cols-3">
        <Metric label="Timeframe" value={summary.timeframe} />
        <Metric label="Letzte Kerze" value={formatDateTime(summary.end_time)} />
        <Metric label="Provider" value={summary.provider_name ?? "-"} />
      </div>
      <p className={`text-xs ${summary.freshness_status === "fresh" ? "text-slate-400" : "text-yellow-100"}`}>
        {freshnessMessage(summary.freshness_status, summary.sync_status)}
      </p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function freshnessBadgeClass(status: MarketDataFreshnessStatus) {
  if (status === "fresh") {
    return "border-emerald-300/30 bg-emerald-300/10 text-emerald-100";
  }
  if (status === "stale" || status === "unknown") {
    return "border-yellow-300/30 bg-yellow-300/10 text-yellow-100";
  }
  return "border-red-300/30 bg-red-300/10 text-red-100";
}

function contextReadyClass(context: BenchmarkContextStatus) {
  return context.requirements.every((requirement) => requirement.status === "ready")
    ? "bg-emerald-300/10 text-emerald-100"
    : "bg-orange-300/10 text-orange-100";
}

function benchmarkRequirementClass(status: string) {
  if (status === "ready") {
    return "bg-emerald-300/10 text-emerald-100";
  }
  if (status === "missing_symbol" || status === "missing_daily_data") {
    return "bg-yellow-300/10 text-yellow-100";
  }
  return "bg-orange-300/10 text-orange-100";
}

function freshnessMessage(status: MarketDataFreshnessStatus, syncStatus: MarketDataSyncStatus) {
  if (status === "fresh") {
    return "Fresh markiert, aber nicht live oder realtime. Manuelle Pruefung bleibt erforderlich.";
  }
  if (status === "stale") {
    return "Stale Daten: nicht wie ein aktuelles Setup oder Trigger behandeln.";
  }
  if (status === "failed" || syncStatus === "failed") {
    return "Fehlerhafter Datenstand: erst korrigieren, dann analysieren.";
  }
  if (status === "partial" || syncStatus === "partial") {
    return "Teilweiser Datenstand: fehlende Kerzen oder Timeframes konservativ behandeln.";
  }
  return "Unbekannte Freshness: konservativ behandeln und vor Analyse aktualisieren.";
}

function formatMarketDataSource(source: MarketDataSource) {
  if (source === "tradingview_csv") {
    return "TradingView CSV";
  }
  if (source === "provider") {
    return "Provider";
  }
  return formatLabel(source);
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}

function formatDateTime(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString("de-DE");
}
