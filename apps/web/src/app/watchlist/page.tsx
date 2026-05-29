"use client";

import { FormEvent, useEffect, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import {
  API_BASE_URL,
  assertAuthenticatedResponse,
  redirectToLoginOnAuthError,
} from "@/lib/api";
import type {
  AssetClass,
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
      setItems(await response.json());
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
        <header className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5 p-8 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Watchlist</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight">Symbole verwalten</h1>
            <p className="mt-3 max-w-2xl text-slate-300">
              Pflege Aktien und Krypto-Symbole als Grundlage fuer CSV-Import, Setup-Bewertungen
              und manuelles Trade Logging. Source/Freshness zeigt Datenkontext, keine Live-Preise
              und keine Trade-Anweisung.
            </p>
          </div>
          <a className="text-sm text-emerald-300 hover:text-emerald-200" href="/">
            Zurueck zum Dashboard
          </a>
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

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
            <div className="mt-5 overflow-hidden rounded-2xl border border-white/10">
              {isLoading ? (
                <p className="p-5 text-sm text-slate-400">Watchlist wird geladen...</p>
              ) : items.length === 0 ? (
                <p className="p-5 text-sm text-slate-400">Noch keine Symbole erfasst.</p>
              ) : (
                <div className="divide-y divide-white/10">
                  {items.map((item) => (
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
                </div>
              )}
            </div>
          </section>
        </section>
      </section>
    </main>
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
