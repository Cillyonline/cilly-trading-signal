"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { AuthenticatedHeaderActions } from "@/components/authenticated-header-actions";
import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import {
  ApiError,
  analyzeImport,
  fetchImportHistory,
  fetchWatchlist,
  importCsv,
  redirectToLoginOnAuthError,
  syncMarketData,
} from "@/lib/api";
import { buildSignalDecision, signalDecisionDotClass, signalDecisionToneClass } from "@/lib/signal-decision";
import type {
  CsvImportError,
  CsvImportResult,
  ImportHistoryItem,
  MarketDataFreshnessStatus,
  MarketDataSource,
  MarketDataSyncStatus,
  MarketDataAnalysisResult,
  MarketDataSyncResult,
  Timeframe,
} from "@/types/imports";
import type { WatchlistItem } from "@/types/watchlist";

const timeframes: Timeframe[] = ["1D", "4H", "1W"];

type ImportPageError = {
  summary: string;
  details: CsvImportError[];
  guidance: string[];
};

export default function ImportPage() {
  const authStatus = useProtectedRoute();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [watchlistItemId, setWatchlistItemId] = useState("");
  const [timeframe, setTimeframe] = useState<Timeframe>("1D");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<CsvImportResult | null>(null);
  const [syncResult, setSyncResult] = useState<MarketDataSyncResult | null>(null);
  const [history, setHistory] = useState<ImportHistoryItem[]>([]);
  const [analysisResult, setAnalysisResult] = useState<MarketDataAnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [analyzingSeriesId, setAnalyzingSeriesId] = useState<number | null>(null);
  const [error, setError] = useState<ImportPageError | null>(null);

  async function loadPageData() {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedItems, loadedHistory] = await Promise.all([fetchWatchlist(), fetchImportHistory()]);
      setItems(loadedItems);
      setHistory(loadedHistory);
      setWatchlistItemId((current) => current || loadedItems[0]?.id.toString() || "");
    } catch (loadError) {
      if (redirectToLoginOnAuthError(loadError)) {
        return;
      }
      setError(toSimpleError(loadError, "Import-Seite konnte nicht geladen werden."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (authStatus === "authenticated") {
      void loadPageData();
    }
  }, [authStatus]);

  const selectedItem = useMemo(
    () => items.find((item) => item.id.toString() === watchlistItemId) ?? null,
    [items, watchlistItemId],
  );

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function submitImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setSyncResult(null);
    setAnalysisResult(null);

    if (!watchlistItemId || !file) {
      setError(toSimpleError("Waehle ein Symbol und eine CSV-Datei aus."));
      return;
    }

    const formData = new FormData();
    formData.append("watchlist_item_id", watchlistItemId);
    formData.append("timeframe", timeframe);
    formData.append("file", file);

    setIsImporting(true);
    try {
      const imported = await importCsv(formData);
      setResult(imported);
      setHistory(await fetchImportHistory());
    } catch (importError) {
      if (redirectToLoginOnAuthError(importError)) {
        return;
      }
      setError(toImportError(importError));
    } finally {
      setIsImporting(false);
    }
  }

  async function runAnalysis() {
    if (!result?.series_id) {
      setError(toSimpleError("Importiere zuerst eine valide CSV-Serie."));
      return;
    }

    await runAnalysisForSeries(result.series_id);
  }

  async function runAnalysisForSeries(seriesId: number) {
    setError(null);
    setAnalysisResult(null);
    setAnalyzingSeriesId(seriesId);
    try {
      setAnalysisResult(await analyzeImport(seriesId));
      setHistory(await fetchImportHistory());
    } catch (analysisError) {
      if (redirectToLoginOnAuthError(analysisError)) {
        return;
      }
      setError(toSimpleError(analysisError, "Analyse konnte nicht gestartet werden."));
    } finally {
      setAnalyzingSeriesId(null);
    }
  }

  async function runProviderSync() {
    setError(null);
    setResult(null);
    setSyncResult(null);
    setAnalysisResult(null);

    if (!watchlistItemId) {
      setError(toSimpleError("Waehle ein Symbol fuer den Provider-Sync aus."));
      return;
    }

    setIsSyncing(true);
    try {
      const synced = await syncMarketData({ watchlist_item_id: Number(watchlistItemId), timeframe });
      setSyncResult(synced);
      setHistory(await fetchImportHistory());
    } catch (syncError) {
      if (redirectToLoginOnAuthError(syncError)) {
        return;
      }
      setError(toSimpleError(syncError, "Provider-Sync konnte nicht gestartet werden."));
    } finally {
      setIsSyncing(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#0f766e,transparent_34%),rgba(255,255,255,0.05)] p-5 sm:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">CSV Import</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Marktdaten importieren</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Lade TradingView CSV-Daten fuer ein Watchlist-Symbol hoch. Der Import validiert die
                Kerzen und speichert sie als Grundlage fuer eine erklaerbare Setup-Bewertung.
              </p>
            </div>
            <AuthenticatedHeaderActions />
          </div>
        </header>

        {error ? <ErrorMessage message={error} /> : null}

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <form onSubmit={submitImport} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-semibold">Neue CSV hochladen</h2>
                <p className="mt-2 text-sm text-slate-400">
                  Erwartete Spalten: time, open, high, low, close, volume.
                </p>
              </div>
              <button
                type="button"
                onClick={() => void loadPageData()}
                className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
              >
                Watchlist laden
              </button>
            </div>

            <div className="mt-6 grid gap-4">
              <label className="grid gap-2 text-sm text-slate-300">
                Symbol
                <select
                  required
                  disabled={isLoading || items.length === 0}
                  value={watchlistItemId}
                  onChange={(event) => setWatchlistItemId(event.target.value)}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300 disabled:opacity-60"
                >
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.symbol} {item.name ? `- ${item.name}` : ""}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid gap-2 text-sm text-slate-300">
                Timeframe
                <select
                  value={timeframe}
                  onChange={(event) => setTimeframe(event.target.value as Timeframe)}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                >
                  {timeframes.map((value) => (
                    <option key={value} value={value}>
                      {value}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid gap-2 text-sm text-slate-300">
                CSV-Datei
                <input
                  required
                  type="file"
                  accept=".csv,text/csv"
                  onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 file:mr-4 file:rounded-lg file:border-0 file:bg-emerald-400 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-slate-950 focus:border-emerald-300"
                />
              </label>

              {selectedItem ? (
                <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
                  <p className="font-medium text-slate-100">{selectedItem.symbol}</p>
                  <p className="mt-1">
                    {selectedItem.asset_class} {selectedItem.exchange ? `auf ${selectedItem.exchange}` : ""}
                  </p>
                </div>
              ) : null}

              {items.length === 0 && !isLoading ? (
                <div className="rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-4 text-sm text-yellow-100">
                  Noch keine Watchlist-Symbole vorhanden. Lege zuerst ein Symbol in der Watchlist an.
                </div>
              ) : null}

              <button
                disabled={isImporting || isLoading || items.length === 0}
                type="submit"
                className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
              >
                {isImporting ? "Importiere..." : "CSV importieren"}
              </button>
            </div>
          </form>

          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Import-Ergebnis</h2>
            <p className="mt-2 text-sm text-slate-400">
              Nach einem erfolgreichen Import kannst du die Analyse im naechsten Workflow-Schritt
              starten. Source/Freshness sind Entscheidungs-Kontext, keine Live-Daten und keine
              Trade-Anweisung.
            </p>

            <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
              {isLoading ? (
                <p className="p-5 text-sm text-slate-400">Importdaten werden geladen...</p>
              ) : result ? (
                <ImportResultCard
                  analysisResult={analysisResult}
                  isAnalyzing={analyzingSeriesId === result.series_id}
                  onAnalyze={() => void runAnalysis()}
                  result={result}
                  symbol={selectedItem?.symbol ?? "Symbol"}
                />
              ) : (
                <EmptyState />
              )}
            </div>
          </section>
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Provider manuell synchronisieren</h2>
            <p className="mt-2 text-sm text-slate-400">
              Fordert einen einmaligen, serverseitig geschuetzten Provider-Sync fuer das ausgewaehlte
              Symbol und den Timeframe an. Das ist kein Live-Preis, kein Signal und keine
              Trade-Anweisung.
            </p>
            <div className="mt-5 grid gap-4 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
              <div className="grid gap-3 sm:grid-cols-2">
                <Metric label="Symbol" value={selectedItem?.symbol ?? "-"} />
                <Metric label="Timeframe" value={timeframe} />
              </div>
              <p className="rounded-2xl border border-yellow-300/20 bg-yellow-300/10 p-3 text-yellow-50">
                Wenn Provider-Sync im Backend deaktiviert oder nicht konfiguriert ist, wird der
                Request sicher als skipped oder failed markiert. Es wird keine Analyse und kein
                Trade automatisch erstellt.
              </p>
              <button
                disabled={isSyncing || isLoading || items.length === 0}
                onClick={() => void runProviderSync()}
                type="button"
                className="rounded-xl border border-emerald-300/40 px-5 py-3 font-semibold text-emerald-200 hover:bg-emerald-300/10 disabled:opacity-60"
              >
                {isSyncing ? "Synchronisiere..." : "Provider-Sync anfragen"}
              </button>
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Provider-Sync Ergebnis</h2>
            <p className="mt-2 text-sm text-slate-400">
              Pruefe Status, Freshness und Provider-Kontext, bevor du Daten fuer Analyse-Workflows
              nutzt.
            </p>
            <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
              {syncResult ? <ProviderSyncResultCard result={syncResult} /> : <ProviderSyncEmptyState />}
            </div>
          </section>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Import-Historie</h2>
              <p className="mt-2 text-sm text-slate-400">
                Read-only Uebersicht deiner gespeicherten Marktdaten. Stale oder unbekannte Daten
                sind konservativ markiert und nicht als Live-Signal zu verstehen.
              </p>
            </div>
            <span className="text-sm text-slate-400">{history.length} Importe</span>
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Import-Historie wird geladen...</p>
            ) : history.length > 0 ? (
              <div className="divide-y divide-white/10">
                {history.map((item) => (
                  <ImportHistoryCard
                    key={item.series_id}
                    isAnalyzing={analyzingSeriesId === item.series_id}
                    item={item}
                    onAnalyze={() => {
                      setResult(toImportResult(item));
                      void runAnalysisForSeries(item.series_id);
                    }}
                  />
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <p className="text-lg font-semibold text-slate-200">Noch keine CSV-Importe.</p>
                <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
                  Lade zuerst TradingView CSV-Daten hoch. Erfolgreiche Importe erscheinen danach hier.
                </p>
              </div>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}

function ErrorMessage({ message }: { message: ImportPageError }) {
  return (
    <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
      <p className="font-semibold">{message.summary}</p>
      {message.details.length > 0 ? (
        <div className="mt-4 overflow-hidden rounded-xl border border-red-300/20">
          <div className="grid grid-cols-[4.5rem_6rem_minmax(0,1fr)] gap-3 bg-red-300/10 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-red-100">
            <span>Zeile</span>
            <span>Feld</span>
            <span>Problem</span>
          </div>
          <div className="divide-y divide-red-300/10">
            {message.details.map((detail, index) => (
              <div
                key={`${detail.row ?? "global"}-${detail.field ?? "csv"}-${index}`}
                className="grid grid-cols-[4.5rem_6rem_minmax(0,1fr)] gap-3 px-3 py-2"
              >
                <span>{detail.row ?? "CSV"}</span>
                <span>{detail.field ?? "-"}</span>
                <span className="min-w-0 break-words">{detail.message}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {message.guidance.length > 0 ? (
        <div className="mt-4 rounded-xl border border-yellow-300/20 bg-yellow-300/10 p-3 text-yellow-50">
          <p className="font-medium">Naechster Check</p>
          <ul className="mt-2 list-disc space-y-1 pl-5">
            {message.guidance.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

function toSimpleError(error: unknown, fallback = "Unbekannter Fehler."): ImportPageError {
  return {
    summary: typeof error === "string" ? error : error instanceof Error ? error.message : fallback,
    details: [],
    guidance: [],
  };
}

function toImportError(error: unknown): ImportPageError {
  if (error instanceof ApiError && Array.isArray(error.detail)) {
    const details = error.detail.filter(isCsvImportError);
    if (details.length > 0) {
      return {
        summary: "CSV konnte nicht importiert werden.",
        details,
        guidance: buildImportGuidance(details),
      };
    }
  }

  return toSimpleError(error, "CSV-Import konnte nicht gespeichert werden.");
}

function isCsvImportError(value: unknown): value is CsvImportError {
  if (!value || typeof value !== "object") {
    return false;
  }

  const error = value as CsvImportError;
  return (
    (error.row === null || error.row === undefined || typeof error.row === "number") &&
    (error.field === null || error.field === undefined || typeof error.field === "string") &&
    typeof error.message === "string"
  );
}

function buildImportGuidance(details: CsvImportError[]) {
  const messages = details.map((detail) => detail.message.toLowerCase());
  const fields = new Set(details.map((detail) => detail.field).filter(Boolean));
  const guidance: string[] = [];

  if (messages.some((message) => message.includes("selected timeframe") || message.includes("timeframe"))) {
    guidance.push("Pruefe, ob der ausgewaehlte Timeframe zur TradingView-CSV passt, zum Beispiel 1D, 4H oder 1W.");
  }

  if (messages.some((message) => message.includes("at most") || message.includes("bytes"))) {
    guidance.push("Reduziere den Export-Zeitraum oder lade eine kleinere CSV-Datei hoch.");
  }

  if (fields.size > 0) {
    guidance.push("Vergleiche die betroffenen Felder mit den erwarteten Spalten: time, open, high, low, close, volume.");
  }

  return guidance.length > 0 ? guidance : ["Korrigiere die CSV und starte den Import danach erneut."];
}

function toImportResult(item: ImportHistoryItem): CsvImportResult {
  return {
    series_id: item.series_id,
    watchlist_item_id: item.watchlist_item_id,
    timeframe: item.timeframe,
    status: item.status,
    candle_count: item.candle_count,
    start_time: item.start_time,
    end_time: item.end_time,
    source: item.source,
    freshness_status: item.freshness_status,
    sync_status: item.sync_status,
    last_synced_at: item.last_synced_at,
    errors: [],
  };
}

function ImportResultCard({
  analysisResult,
  isAnalyzing,
  onAnalyze,
  result,
  symbol,
}: {
  analysisResult: MarketDataAnalysisResult | null;
  isAnalyzing: boolean;
  onAnalyze: () => void;
  result: CsvImportResult;
  symbol: string;
}) {
  return (
    <article className="grid gap-5 p-5">
      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">
          {result.status}
        </span>
        <h3 className="text-lg font-semibold">{symbol}</h3>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
          {result.timeframe}
        </span>
        <MarketDataStateBadges
          freshnessStatus={result.freshness_status}
          source={result.source}
          syncStatus={result.sync_status}
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Series ID" value={result.series_id?.toString() ?? "-"} />
        <Metric label="Kerzen" value={result.candle_count.toString()} />
        <Metric label="Start" value={formatDateTime(result.start_time)} />
        <Metric label="Ende" value={formatDateTime(result.end_time)} />
      </div>

      <MarketDataFreshnessNotice freshnessStatus={result.freshness_status} syncStatus={result.sync_status} />

      <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300 sm:flex-row sm:items-center sm:justify-between">
        <p>
          Marktdaten gespeichert. Starte die Analyse nur nach manueller Pruefung von Source und
          Freshness.
        </p>
        <button
          disabled={isAnalyzing || !result.series_id}
          onClick={onAnalyze}
          type="button"
          className="rounded-xl bg-emerald-400 px-4 py-2 font-semibold text-slate-950 disabled:opacity-60"
        >
          {isAnalyzing ? "Analysiere..." : "Analyse starten"}
        </button>
      </div>

      {analysisResult ? <AnalysisResultCard result={analysisResult} /> : null}
    </article>
  );
}

function ImportHistoryCard({
  isAnalyzing,
  item,
  onAnalyze,
}: {
  isAnalyzing: boolean;
  item: ImportHistoryItem;
  onAnalyze: () => void;
}) {
  return (
    <article className="grid gap-5 p-5 lg:grid-cols-[1fr_auto] lg:items-center">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="text-lg font-semibold">{item.symbol}</h3>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
            {item.timeframe}
          </span>
          <span className="rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">
            {item.status}
          </span>
          <MarketDataStateBadges
            freshnessStatus={item.freshness_status}
            source={item.source}
            syncStatus={item.sync_status}
          />
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Metric label="Kerzen" value={item.candle_count.toString()} />
          <Metric label="Start" value={formatDateTime(item.start_time)} />
          <Metric label="Ende" value={formatDateTime(item.end_time)} />
          <Metric label="Importiert" value={formatDateTime(item.imported_at)} />
          <Metric label="Sync" value={formatSyncDetail(item)} />
        </div>
        <div className="mt-4">
          <MarketDataFreshnessNotice freshnessStatus={item.freshness_status} syncStatus={item.sync_status} />
        </div>
      </div>
      <button
        className="inline-flex rounded-xl border border-white/10 px-4 py-2 text-sm text-emerald-300 hover:border-emerald-300/50 hover:text-emerald-200 disabled:opacity-60"
        disabled={isAnalyzing}
        onClick={onAnalyze}
        type="button"
      >
        {isAnalyzing ? "Analysiere..." : "Analyse starten"}
      </button>
    </article>
  );
}

function ProviderSyncResultCard({ result }: { result: MarketDataSyncResult }) {
  const state = providerSyncState(result);

  return (
    <article className="grid gap-5 p-5">
      <div className={`rounded-2xl border p-4 ${state.className}`}>
        <p className="text-sm font-semibold">{state.title}</p>
        <p className="mt-2 text-sm">{state.message}</p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <span className="rounded-full border border-sky-300/20 bg-sky-300/10 px-3 py-1 text-xs text-sky-100">
          Provider: {result.provider_name ?? "-"}
        </span>
        <MarketDataStateBadges
          freshnessStatus={result.freshness_status}
          source={result.source}
          syncStatus={result.sync_status}
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Series ID" value={result.series_id.toString()} />
        <Metric label="Provider Symbol" value={result.provider_symbol ?? "-"} />
        <Metric label="Provider Timeframe" value={result.provider_timeframe ?? result.timeframe} />
        <Metric label="Letzte Kerze" value={formatDateTime(result.end_time)} />
        <Metric label="Letzter Sync" value={formatDateTime(result.last_synced_at)} />
        <Metric label="Exchange" value={result.provider_exchange ?? "-"} />
        <Metric label="Fehler-Code" value={result.sync_error_code ?? "-"} />
        <Metric label="Status" value={formatLabel(result.sync_status)} />
      </div>

      <MarketDataFreshnessNotice freshnessStatus={result.freshness_status} syncStatus={result.sync_status} />

      {result.sync_error_message ? (
        <p className="rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-3 text-sm text-yellow-100 break-words">
          {result.sync_error_message}
        </p>
      ) : null}
    </article>
  );
}

function ProviderSyncEmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch kein Provider-Sync angefragt.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Starte den Sync manuell. Das Ergebnis erscheint hier und in der Import-Historie.
      </p>
    </div>
  );
}

function providerSyncState(result: MarketDataSyncResult) {
  if (result.sync_status === "success") {
    return result.freshness_status === "fresh"
      ? {
          title: "Sync gespeichert",
          message:
            "Provider-Daten wurden gespeichert und als fresh markiert. Das ist weiterhin kein Live-Preis und startet keine Analyse automatisch.",
          className: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
        }
      : {
          title: "Sync gespeichert, aber Freshness pruefen",
          message:
            "Provider-Daten wurden gespeichert, sind aber nicht fresh. Nutze sie nur als Kontext und pruefe den Datenstand vor einer Analyse.",
          className: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
        };
  }

  if (result.sync_status === "skipped") {
    return {
      title: "Provider-Sync uebersprungen",
      message:
        result.sync_error_code === "sync_disabled"
          ? "Provider-Sync ist im Backend deaktiviert. Das ist der sichere Default und es wurden keine Provider-Daten abgerufen."
          : "Der Sync wurde sicher uebersprungen. Pruefe die Backend-Konfiguration, falls du Provider-Daten erwartest.",
      className: "border-slate-500/30 bg-slate-800/70 text-slate-200",
    };
  }

  if (result.sync_status === "partial") {
    return {
      title: "Provider-Sync teilweise nutzbar",
      message:
        "Der Sync hat nur einen Teilzustand geliefert. Fehlende Kerzen oder Timeframes koennen Analyse-Ergebnisse konservativ blockieren.",
      className: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
    };
  }

  return {
    title: "Provider-Sync fehlgeschlagen",
    message:
      "Der Sync wurde nicht als nutzbarer Datenstand gespeichert. Pruefe den Fehler-Code und behandle den Datenstand konservativ.",
    className: "border-red-300/30 bg-red-300/10 text-red-100",
  };
}

function AnalysisResultCard({ result }: { result: MarketDataAnalysisResult }) {
  const signal = result.signal;
  const decision = buildSignalDecision(signal);
  const reasons = decision.reasons;
  const technicalReasons = signal.reasoning.slice(0, 3);
  const flags = signal.risk_flags.slice(0, 4);
  const noTradeReasons = signal.no_trade_reasons.slice(0, 4);

  return (
    <section className="grid gap-5 rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-medium text-emerald-100">Analyse abgeschlossen</p>
          <h4 className="mt-1 text-lg font-semibold">{formatStrategy(signal.strategy_type)}</h4>
        </div>
        <a className="text-sm text-emerald-300 hover:text-emerald-200" href="/signals">
          Zu den Signalen
        </a>
      </div>

      <div className={`rounded-2xl border p-5 ${signalDecisionToneClass(decision.tone)}`}>
        <div className="flex flex-wrap items-center gap-3">
          <span className={`h-4 w-4 rounded-full ${signalDecisionDotClass(decision.tone)}`} />
          <p className="text-sm font-semibold uppercase tracking-[0.2em]">{decision.label}</p>
          <span className="rounded-full border border-current/20 px-3 py-1 text-xs">
            Qualitaet: {decision.quality}
          </span>
        </div>
        <p className="mt-4 text-2xl font-semibold text-slate-50">{decision.headline}</p>
        <p className="mt-2 max-w-2xl text-sm">{decision.action}</p>

        <div className="mt-4 grid gap-3 lg:grid-cols-[1fr_0.9fr]">
          <div className="rounded-xl border border-current/15 bg-slate-950/30 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">Warum?</p>
            <ul className="mt-3 space-y-2 text-sm">
              {reasons.map((reason) => (
                <li key={reason}>- {reason}</li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-current/15 bg-slate-950/30 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">Was jetzt?</p>
            <p className="mt-3 text-sm">{decision.action}</p>
            <p className="mt-2 text-xs opacity-75">Keine automatische Order. Echte Ausfuehrung bleibt manuell.</p>
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Backend Status" value={signal.status.replaceAll("_", " ")} />
        <Metric label="Score" value={`${signal.score} / ${signal.score_class.replaceAll("_", " ")}`} />
        <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
        <Metric label="Snapshots" value={result.indicator_snapshot_count.toString()} />
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
        <Metric label="Stop" value={formatMoney(signal.stop_loss)} />
        <Metric label="Target 1" value={formatMoney(signal.target_1)} />
      </div>

      <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
        <p className="text-sm font-medium text-slate-200">Backend-Naechste Aktion</p>
        <p className="mt-2 text-sm text-slate-300">{signal.next_action}</p>
      </div>

      <TextList title="Technische Begruendung" empty="Keine Begruendung gespeichert." items={technicalReasons} />
      <QualityReport checks={signal.quality_report} />
      <BadgeList title="Risk Flags" empty="Keine Risk Flags" items={flags} tone="orange" />
      <BadgeList title="No-Trade Gruende" empty="Keine No-Trade Gruende" items={noTradeReasons} tone="slate" />
    </section>
  );
}

function QualityReport({ checks }: { checks: MarketDataAnalysisResult["signal"]["quality_report"] }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <p className="text-sm font-medium text-slate-200">Analyse-Qualitaet</p>
      {checks.length > 0 ? (
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {checks.slice(0, 8).map((check) => (
            <div key={check.key} className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">
                {check.label} · {check.status}
              </p>
              <p className="mt-1 text-sm text-slate-300">{check.detail}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-slate-500">Kein Qualitaetsbericht gespeichert.</p>
      )}
    </div>
  );
}

function TextList({ title, empty, items }: { title: string; empty: string; items: string[] }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <p className="text-sm font-medium text-slate-200">{title}</p>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm text-slate-300">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm text-slate-500">{empty}</p>
      )}
    </div>
  );
}

function BadgeList({
  title,
  empty,
  items,
  tone,
}: {
  title: string;
  empty: string;
  items: string[];
  tone: "orange" | "slate";
}) {
  const badgeClass =
    tone === "orange" ? "bg-orange-300/10 text-orange-100" : "bg-slate-700/70 text-slate-200";

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <p className="text-sm font-medium text-slate-200">{title}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <span key={item} className={`rounded-full px-3 py-1 text-xs ${badgeClass}`}>
              {item.replaceAll("_", " ")}
            </span>
          ))
        ) : (
          <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">{empty}</span>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch kein Import ausgefuehrt.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Waehle ein Symbol, Timeframe und CSV-Datei aus. Der Backend-Import prueft die Daten, bevor
        sie fuer die Analyse genutzt werden.
      </p>
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

function MarketDataStateBadges({
  freshnessStatus,
  source,
  syncStatus,
}: {
  freshnessStatus: MarketDataFreshnessStatus;
  source: MarketDataSource;
  syncStatus: MarketDataSyncStatus;
}) {
  return (
    <>
      <span className="rounded-full border border-sky-300/20 bg-sky-300/10 px-3 py-1 text-xs text-sky-100">
        Source: {formatMarketDataSource(source)}
      </span>
      <span className={`rounded-full border px-3 py-1 text-xs ${freshnessBadgeClass(freshnessStatus)}`}>
        Freshness: {formatLabel(freshnessStatus)}
      </span>
      <span className="rounded-full border border-white/10 bg-slate-800 px-3 py-1 text-xs text-slate-300">
        Sync: {formatLabel(syncStatus)}
      </span>
    </>
  );
}

function MarketDataFreshnessNotice({
  freshnessStatus,
  syncStatus,
}: {
  freshnessStatus: MarketDataFreshnessStatus;
  syncStatus: MarketDataSyncStatus;
}) {
  if (freshnessStatus === "fresh") {
    return (
      <p className="rounded-2xl border border-emerald-300/20 bg-emerald-300/5 p-3 text-sm text-emerald-100">
        Daten sind als fresh markiert, aber nicht live oder realtime. Ausfuehrung bleibt manuell.
      </p>
    );
  }

  const message =
    freshnessStatus === "stale"
      ? "Daten sind stale. Nicht als aktuelles Setup oder Trigger interpretieren."
      : freshnessStatus === "failed" || syncStatus === "failed"
        ? "Letzter Sync/Import-Status ist failed. Analyse nur als Fehlerkontext verwenden."
        : freshnessStatus === "partial" || syncStatus === "partial"
          ? "Daten sind partial. Fehlende Kerzen oder Timeframes koennen die Analyse blockieren."
          : "Freshness ist unknown. Behandle diese Daten konservativ und nicht als actionable.";

  return (
    <p className="rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-3 text-sm text-yellow-100">
      {message}
    </p>
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

function formatMarketDataSource(source: MarketDataSource) {
  if (source === "tradingview_csv") {
    return "TradingView CSV";
  }
  if (source === "provider") {
    return "Provider";
  }
  return formatLabel(source);
}

function formatSyncDetail(item: ImportHistoryItem) {
  if (item.source === "provider") {
    return item.provider_name
      ? `${item.provider_name} / ${formatDateTime(item.last_synced_at)}`
      : formatDateTime(item.last_synced_at);
  }
  return item.file_name ?? "CSV";
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

function formatStrategy(value: MarketDataAnalysisResult["signal"]["strategy_type"]) {
  return value === "trend_pullback_long" ? "Trend Pullback Long" : "Base Breakout Long";
}

function formatMoney(value: string | null) {
  return value ? formatNumber(value) : "-";
}

function formatNumber(value: string) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(2) : value;
}
