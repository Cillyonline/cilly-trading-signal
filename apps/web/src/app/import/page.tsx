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
import {
  buildSignalDecision,
  signalDecisionDotClass,
  signalDecisionExplanation,
  signalDecisionToneClass,
} from "@/lib/signal-decision";
import type {
  CsvImportError,
  CsvImportResult,
  ImportHistoryItem,
  MarketDataFreshnessStatus,
  MarketDataSource,
  MarketDataSyncStatus,
  MarketDataAnalysisResult,
  MarketDataSyncResult,
  ProviderTimeframeCapability,
  Timeframe,
} from "@/types/imports";
import type { WatchlistItem } from "@/types/watchlist";

const timeframes: Timeframe[] = ["1D", "4H", "1W"];

type ImportPageError = {
  summary: string;
  details: CsvImportError[];
  guidance: string[];
};

type BulkImportItem = {
  fileName: string;
  targetSymbol: string | null;
  targetTimeframe: Timeframe | null;
  status: "success" | "failed";
  result: CsvImportResult | null;
  error: ImportPageError | null;
};

type DetectedCsvFile = {
  fileName: string;
  symbol: string | null;
  exchange: string | null;
  timeframe: Timeframe | null;
  warning: string | null;
};

type CsvFileMapping = {
  fileName: string;
  detectedSymbol: string | null;
  detectedExchange: string | null;
  detectedTimeframe: Timeframe | null;
  warning: string | null;
  watchlistItemId: string;
  timeframe: Timeframe | "";
};

type ImportReadinessGroup = {
  symbol: string;
  present: Timeframe[];
  missing: Timeframe[];
  complete: boolean;
};

type TimeframeReadiness = {
  timeframe: Timeframe;
  status: "ready" | "missing" | "stale" | "failed" | "partial" | "unknown" | "insufficient";
  candleCount: number | null;
  freshnessStatus: MarketDataFreshnessStatus | null;
  source: MarketDataSource | null;
  providerName: string | null;
  latestCandle: string | null;
};

type SymbolDataReadiness = {
  symbol: string;
  isActive: boolean;
  timeframes: TimeframeReadiness[];
  ready: boolean;
  nextAction: string;
};

type CsvWorkflowGuidanceItem = {
  title: string;
  timeframe: Timeframe;
  scope: string;
  count: number;
  symbols: string[];
  guidance: string;
  className: string;
};

type BatchAnalysisPlanItem = {
  symbol: string;
  seriesId: number | null;
  missing: Timeframe[];
  skipReason: string | null;
};

type BatchAnalysisResultItem = {
  symbol: string;
  status: "pending" | "success" | "failed" | "skipped";
  seriesId: number | null;
  reason: string | null;
  result: MarketDataAnalysisResult | null;
};

type AnalysisDiagnosis = {
  riskFlags: string[];
  noTradeReasons: string[];
  qualityIssues: MarketDataAnalysisResult["signal"]["quality_report"];
};

type BatchAnalysisFilter =
  | "all"
  | "paper"
  | "watch"
  | "no_trade"
  | "data_problem"
  | "pending"
  | "skipped"
  | "failed";

export default function ImportPage() {
  const authStatus = useProtectedRoute();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [watchlistItemId, setWatchlistItemId] = useState("");
  const [timeframe, setTimeframe] = useState<Timeframe>("1D");
  const [file, setFile] = useState<File | null>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [fileMappings, setFileMappings] = useState<CsvFileMapping[]>([]);
  const [result, setResult] = useState<CsvImportResult | null>(null);
  const [resultSymbol, setResultSymbol] = useState<string | null>(null);
  const [bulkResults, setBulkResults] = useState<BulkImportItem[]>([]);
  const [syncResult, setSyncResult] = useState<MarketDataSyncResult | null>(null);
  const [history, setHistory] = useState<ImportHistoryItem[]>([]);
  const [analysisResult, setAnalysisResult] = useState<MarketDataAnalysisResult | null>(null);
  const [batchAnalysisResults, setBatchAnalysisResults] = useState<BatchAnalysisResultItem[]>([]);
  const [batchAnalysisFilter, setBatchAnalysisFilter] = useState<BatchAnalysisFilter>("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isBatchAnalyzing, setIsBatchAnalyzing] = useState(false);
  const [analyzingSeriesId, setAnalyzingSeriesId] = useState<number | null>(null);
  const [error, setError] = useState<ImportPageError | null>(null);

  async function loadPageData() {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedItems, loadedHistory] = await Promise.all([fetchWatchlist(), fetchImportHistory()]);
      setItems(loadedItems);
      setHistory(loadedHistory);
      setWatchlistItemId((current) => {
        const activeItems = loadedItems.filter((item) => item.is_active);
        return activeItems.some((item) => item.id.toString() === current)
          ? current
          : activeItems[0]?.id.toString() || "";
      });
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
  const activeItems = useMemo(() => items.filter((item) => item.is_active), [items]);
  const detectedFiles = useMemo(() => files.map((selectedFile) => detectCsvFile(selectedFile.name)), [files]);
  const mappedFiles = useMemo(() => buildMappedDetectedFiles(fileMappings, activeItems), [fileMappings, activeItems]);
  const readinessGroups = useMemo(
    () => buildImportReadinessGroups(history, mappedFiles.length > 0 ? mappedFiles : detectedFiles),
    [history, mappedFiles, detectedFiles],
  );
  const dataReadiness = useMemo(() => buildSymbolDataReadiness(activeItems, history), [activeItems, history]);
  const mappingHasInvalidRows = useMemo(
    () => fileMappings.some((mapping) => !mapping.watchlistItemId || !mapping.timeframe),
    [fileMappings],
  );
  const batchAnalysisPlan = useMemo(() => buildBatchAnalysisPlan(history), [history]);
  const providerCapabilityHints = useMemo(() => buildProviderCapabilityHints(syncResult), [syncResult]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function submitImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setResult(null);
    setResultSymbol(null);
    setBulkResults([]);
    setSyncResult(null);
    setAnalysisResult(null);
    setBatchAnalysisResults([]);

    const selectedFiles = files.length > 0 ? files : file ? [file] : [];
    if (selectedFiles.length === 0) {
      setError(toSimpleError("Waehle mindestens eine CSV-Datei aus."));
      return;
    }

    if (fileMappings.length !== selectedFiles.length || mappingHasInvalidRows) {
      setError(
        toSimpleError(
          "Korrigiere zuerst die CSV-Zuordnung. Jede Datei braucht ein Watchlist-Symbol und einen Timeframe.",
        ),
      );
      return;
    }

    setIsImporting(true);
    const importedItems: BulkImportItem[] = [];
    try {
      for (let index = 0; index < selectedFiles.length; index += 1) {
        const selectedFile = selectedFiles[index];
        const mapping = fileMappings[index];
        const targetTimeframe = mapping.timeframe as Timeframe;
        const targetItem = items.find((item) => item.id.toString() === mapping.watchlistItemId) ?? null;
        const formData = new FormData();
        formData.append("watchlist_item_id", mapping.watchlistItemId);
        formData.append("timeframe", targetTimeframe);
        formData.append("file", selectedFile);

        try {
          const imported = await importCsv(formData);
          importedItems.push({
            fileName: selectedFile.name,
            targetSymbol: targetItem?.symbol ?? null,
            targetTimeframe,
            status: "success",
            result: imported,
            error: null,
          });
          setResult(imported);
          setResultSymbol(targetItem?.symbol ?? null);
        } catch (importError) {
          if (redirectToLoginOnAuthError(importError)) {
            return;
          }
          importedItems.push({
            fileName: selectedFile.name,
            targetSymbol: targetItem?.symbol ?? null,
            targetTimeframe,
            status: "failed",
            result: null,
            error: toImportError(importError),
          });
          if (selectedFiles.length === 1) {
            setError(toImportError(importError));
          }
        }
        setBulkResults([...importedItems]);
      }
      setHistory(await fetchImportHistory());
      if (importedItems.every((item) => item.status === "failed")) {
        setError(toSimpleError("Keine CSV-Datei konnte importiert werden. Pruefe die Fehlerliste."));
      }
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

  async function runAnalyzeCompleteSymbols() {
    setError(null);
    setResult(null);
    setAnalysisResult(null);
    setBatchAnalysisResults([]);

    const plan = buildBatchAnalysisPlan(history);
    if (plan.length === 0) {
      setError(toSimpleError("Keine importierten Symbole fuer eine Batch-Analyse gefunden."));
      return;
    }

    const initialResults: BatchAnalysisResultItem[] = plan.map((item) => ({
      symbol: item.symbol,
      status: item.seriesId ? "pending" : "skipped",
      seriesId: item.seriesId,
      reason: item.skipReason,
      result: null,
    }));
    setBatchAnalysisResults(initialResults);
    setIsBatchAnalyzing(true);

    try {
      for (const item of plan) {
        if (!item.seriesId) {
          continue;
        }

        setAnalyzingSeriesId(item.seriesId);
        try {
          const analyzed = await analyzeImport(item.seriesId);
          setBatchAnalysisResults((current) =>
            current.map((resultItem) =>
              resultItem.symbol === item.symbol
                ? { ...resultItem, status: "success", reason: null, result: analyzed }
                : resultItem,
            ),
          );
        } catch (analysisError) {
          if (redirectToLoginOnAuthError(analysisError)) {
            return;
          }
          setBatchAnalysisResults((current) =>
            current.map((resultItem) =>
              resultItem.symbol === item.symbol
                ? {
                    ...resultItem,
                    status: "failed",
                    reason: toSimpleError(analysisError, "Analyse konnte nicht gestartet werden.").summary,
                    result: null,
                  }
                : resultItem,
            ),
          );
        }
      }
      setHistory(await fetchImportHistory());
    } finally {
      setAnalyzingSeriesId(null);
      setIsBatchAnalyzing(false);
    }
  }

  async function runProviderSync() {
    setError(null);
    setResult(null);
    setSyncResult(null);
    setAnalysisResult(null);
    setBatchAnalysisResults([]);

    if (!watchlistItemId) {
      setError(toSimpleError("Waehle ein Symbol fuer die Datenaktualisierung aus."));
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
      setError(toSimpleError(syncError, "Datenaktualisierung konnte nicht gestartet werden."));
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

        <CsvWorkflowSection activeCount={activeItems.length} groups={readinessGroups} />
        <SymbolDataReadinessSection items={dataReadiness} isLoading={isLoading} />

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
                Standard-Symbol / Provider-Kontext
                <select
                  required
                  disabled={isLoading || items.length === 0}
                  value={watchlistItemId}
                  onChange={(event) => setWatchlistItemId(event.target.value)}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300 disabled:opacity-60"
                >
                  {activeItems.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.symbol} {item.name ? `- ${item.name}` : ""}
                    </option>
                  ))}
                </select>
              </label>

              <label className="grid gap-2 text-sm text-slate-300">
                Standard-Timeframe / Provider-Kontext
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
                  multiple
                  accept=".csv,text/csv"
                  onChange={(event) => {
                    const selectedFiles = Array.from(event.target.files ?? []);
                    setFiles(selectedFiles);
                    setFile(selectedFiles[0] ?? null);
                    setFileMappings(buildCsvFileMappings(selectedFiles, activeItems));
                    setResultSymbol(null);
                  }}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 file:mr-4 file:rounded-lg file:border-0 file:bg-emerald-400 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-slate-950 focus:border-emerald-300"
                />
              </label>

              {files.length > 0 ? (
                <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
                  <p className="font-medium text-slate-100">{files.length} Datei(en) ausgewaehlt</p>
                  <p className="mt-1 text-slate-400">
                    Pruefe die Zuordnung je Datei. Der Import startet erst nach explizitem Klick.
                  </p>
                </div>
              ) : null}

              {fileMappings.length > 0 ? (
                <CsvFileMappingTable items={activeItems} mappings={fileMappings} onChange={setFileMappings} />
              ) : null}

              {readinessGroups.length > 0 ? <ImportReadinessPanel groups={readinessGroups} /> : null}

              {selectedItem ? (
                <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
                  <p className="font-medium text-slate-100">{selectedItem.symbol}</p>
                  <p className="mt-1">
                    {selectedItem.asset_class} {selectedItem.exchange ? `auf ${selectedItem.exchange}` : ""}
                  </p>
                </div>
              ) : null}

              {activeItems.length === 0 && !isLoading ? (
                <div className="rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-4 text-sm text-yellow-100">
                  Keine aktiven Watchlist-Symbole vorhanden. Lege zuerst ein Symbol an oder reaktiviere es in der Watchlist.
                </div>
              ) : null}

              <button
                disabled={isImporting || isLoading || activeItems.length === 0 || mappingHasInvalidRows}
                type="submit"
                className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
              >
                {isImporting ? "Importiere..." : files.length > 1 ? "CSV-Dateien importieren" : "CSV importieren"}
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
              ) : bulkResults.length > 1 || (bulkResults.length === 1 && bulkResults[0]?.status === "failed") ? (
                <BulkImportResultList items={bulkResults} />
              ) : result ? (
                <ImportResultCard
                  analysisResult={analysisResult}
                  isAnalyzing={analyzingSeriesId === result.series_id}
                  onAnalyze={() => void runAnalysis()}
                  result={result}
                  symbol={resultSymbol ?? selectedItem?.symbol ?? "Symbol"}
                />
              ) : (
                <EmptyState />
              )}
            </div>
          </section>
        </section>

        <details className="group rounded-3xl border border-white/10 bg-white/[0.03] [&>summary:focus]:outline-none">
          <summary className="flex cursor-pointer list-none items-center justify-between p-6">
            <div>
              <h2 className="text-xl font-semibold">Provider-Sync (erweitert)</h2>
              <p className="mt-1 text-sm text-slate-400">
                Manuelle Provider-Datenaktualisierung. Nur nutzen, wenn CSV nicht ausreicht.
              </p>
            </div>
            <span className="rounded-full border border-white/10 bg-slate-800 px-3 py-1 text-xs text-slate-300">
              Erweitert
            </span>
          </summary>
          <div className="grid gap-6 p-6 pt-0 lg:grid-cols-[0.9fr_1.1fr]">
            <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
              <h2 className="text-xl font-semibold">Daten aktualisieren</h2>
              <p className="mt-2 text-sm text-slate-400">
                Fordert einmalig gespeicherte Provider-Marktdaten fuer das ausgewaehlte Symbol an.
                Das ist manuell, kein Live-Preis, kein Signal und keine Trade-Anweisung.
              </p>
              <ProviderSyncBeginnerGuide selectedSymbol={selectedItem?.symbol ?? null} selectedTimeframe={timeframe} />
              <div className="mt-5 grid gap-4 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
                <div className="grid gap-3 sm:grid-cols-2">
                  <Metric label="Symbol" value={selectedItem?.symbol ?? "-"} />
                  <Metric label="Timeframe" value={timeframe} />
                </div>
                <ProviderCapabilityHintPanel hints={providerCapabilityHints} selectedTimeframe={timeframe} />
                <p className="rounded-2xl border border-yellow-300/20 bg-yellow-300/10 p-3 text-yellow-50">
                  Wenn der Provider deaktiviert, nicht konfiguriert oder fuer den Timeframe ungeeignet
                  ist, wird die Anfrage sicher als skipped oder failed markiert. Es wird keine Analyse,
                  kein Alert und kein Trade automatisch erstellt.
                </p>
                <button
                  disabled={isSyncing || isLoading || activeItems.length === 0}
                  onClick={() => void runProviderSync()}
                  type="button"
                  className="rounded-xl border border-emerald-300/40 px-5 py-3 font-semibold text-emerald-200 hover:bg-emerald-300/10 disabled:opacity-60"
                >
                  {isSyncing ? "Aktualisiere Daten..." : "Daten aktualisieren"}
                </button>
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
              <h2 className="text-xl font-semibold">Aktualisierungs-Ergebnis</h2>
              <p className="mt-2 text-sm text-slate-400">
                Pruefe Status, Freshness, Provider-Kontext und Timeframe-Capability, bevor du Daten
                fuer Analyse-Workflows nutzt.
              </p>
              <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
                {syncResult ? <ProviderSyncResultCard result={syncResult} /> : <ProviderSyncEmptyState />}
              </div>
            </section>
          </div>
        </details>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Vollstaendige Symbole analysieren</h2>
              <p className="mt-2 max-w-3xl text-sm text-slate-400">
                Startet nur nach explizitem Klick eine Analyse fuer Symbole mit nutzbaren `1W`, `1D`
                und `4H` Daten. Unvollstaendige Symbole werden uebersprungen und bleiben No-Action.
              </p>
            </div>
            <button
              disabled={isBatchAnalyzing || isLoading || batchAnalysisPlan.length === 0}
              onClick={() => void runAnalyzeCompleteSymbols()}
              type="button"
              className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
            >
              {isBatchAnalyzing ? "Analysiere Symbole..." : "Vollstaendige Symbole analysieren"}
            </button>
          </div>

          <BatchAnalysisPanel
            filter={batchAnalysisFilter}
            isAnalyzing={isBatchAnalyzing}
            onFilterChange={setBatchAnalysisFilter}
            plan={batchAnalysisPlan}
            results={batchAnalysisResults}
          />
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
                      setResultSymbol(item.symbol);
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

function ProviderSyncBeginnerGuide({
  selectedSymbol,
  selectedTimeframe,
}: {
  selectedSymbol: string | null;
  selectedTimeframe: Timeframe;
}) {
  const steps = [
    `Waehle oben im Feld Standard-Symbol dein Symbol aus. Aktuell ausgewaehlt: ${selectedSymbol ?? "-"}.`,
    `Waehle oben im Feld Standard-Timeframe den ersten Timeframe aus. Aktuell ausgewaehlt: ${selectedTimeframe}.`,
    "Klicke auf Daten aktualisieren und warte auf das Aktualisierungs-Ergebnis rechts.",
    "Pruefe nach jedem Lauf Status, Freshness, letzte Kerze und Fehler-Code. Nur success/fresh ist fuer aktuelle Analyse geeignet.",
    "Wiederhole den Ablauf fuer 1W, 1D und 4H. Erst danach Vollstaendige Symbole analysieren starten.",
    "Wenn weniger als 200 Kerzen oder wichtige Indikatoren fehlen, bleibt die Analyse konservativ bei Datenproblem.",
  ];

  return (
    <div className="mt-5 rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-4 text-sm text-emerald-50">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <p className="font-semibold text-emerald-100">Schritt fuer Schritt fuer neue Nutzer</p>
        <span className="rounded-full border border-emerald-200/30 px-3 py-1 text-xs text-emerald-100">
          Twelve Data
        </span>
      </div>
      <ol className="mt-3 list-decimal space-y-2 pl-5 text-emerald-50/90">
        {steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
      <p className="mt-3 rounded-xl border border-white/10 bg-slate-950/40 p-3 text-xs text-emerald-50/80">
        Wichtig: Provider-Sync speichert nur Marktdaten. Er startet keine Analyse automatisch, erzeugt
        kein Signal, keinen Alert, keinen Trade und ist kein Live-Preis. Fuer eine saubere Analyse
        braucht jeder benoetigte Timeframe ausreichend Historie fuer Indikatoren wie EMA200.
      </p>
    </div>
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

function BulkImportResultList({ items }: { items: BulkImportItem[] }) {
  const successCount = items.filter((item) => item.status === "success").length;
  const failedCount = items.length - successCount;

  return (
    <article className="grid gap-4 p-5">
      <div>
        <p className="text-sm font-medium text-emerald-100">Bulk-Import abgeschlossen</p>
        <h3 className="mt-1 text-lg font-semibold">
          {successCount} erfolgreich, {failedCount} fehlgeschlagen
        </h3>
        <p className="mt-2 text-sm text-slate-400">
          Fehler in einzelnen Dateien blockieren die anderen Importe nicht. Pruefe jede Zuordnung,
          bevor du Analysen startest.
        </p>
      </div>

      <div className="grid gap-3">
        {items.map((item) => (
          <div
            key={item.fileName}
            className={`rounded-2xl border p-4 ${
              item.status === "success"
                ? "border-emerald-300/30 bg-emerald-300/10"
                : "border-red-300/30 bg-red-300/10"
            }`}
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="break-words text-sm font-semibold text-slate-100">{item.fileName}</p>
              <span className="rounded-full border border-current/20 px-3 py-1 text-xs text-slate-100">
                {item.status === "success" ? "Importiert" : "Fehler"}
              </span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="rounded-full bg-slate-900/70 px-3 py-1 text-slate-100">
                Ziel: {item.targetSymbol ?? "unklar"}
              </span>
              <span className="rounded-full bg-slate-900/70 px-3 py-1 text-slate-100">
                Timeframe: {item.targetTimeframe ?? "unklar"}
              </span>
            </div>
            {item.result ? (
              <div className="mt-3 grid gap-2 sm:grid-cols-3">
                <Metric label="Timeframe" value={item.result.timeframe} />
                <Metric label="Kerzen" value={item.result.candle_count.toString()} />
                <Metric label="Freshness" value={formatLabel(item.result.freshness_status)} />
              </div>
            ) : null}
            {item.error ? (
              <div className="mt-3 text-sm text-red-100">
                <p className="font-medium">{item.error.summary}</p>
                <ul className="mt-2 space-y-1">
                  {item.error.details.slice(0, 3).map((detail, index) => (
                    <li key={`${item.fileName}-${index}`}>
                      {detail.field ?? "CSV"}: {detail.message}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </article>
  );
}

function CsvWorkflowSection({ activeCount, groups }: { activeCount: number; groups: ImportReadinessGroup[] }) {
  return (
    <section className="rounded-3xl border border-emerald-300/20 bg-emerald-300/[0.03] p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-300">CSV-Arbeitsplan</p>
          <h2 className="mt-2 text-xl font-semibold">Update-Modus waehlen</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Waehle den passenden Update-Modus vor dem CSV-Import. Das hilft, das Universum,
            aktive Kandidaten und die Trigger-Liste getrennt zu halten.
            {activeCount === 0 ? " Starte zuerst in der Watchlist mit einem aktiven Symbol." : ""}
          </p>
        </div>
        <span className="rounded-full border border-emerald-200/30 bg-slate-950/40 px-3 py-1 text-xs text-emerald-50">
          CSV-first, kein Live-Feed
        </span>
      </div>
      <CsvWorkflowGuidancePanel groups={groups} />
    </section>
  );
}

function SymbolDataReadinessSection({
  isLoading,
  items,
}: {
  isLoading: boolean;
  items: SymbolDataReadiness[];
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-300">Data Hygiene</p>
          <h2 className="mt-2 text-xl font-semibold">Readiness je aktivem Symbol</h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Kompakte Read-only Sicht auf `1W`, `1D` und `4H`. Sie nutzt bestehende Import-/Sync-Historie,
            startet keine Analyse und erzeugt keine Trades, Alerts oder Orders.
          </p>
        </div>
        <span className="rounded-full border border-white/10 bg-slate-800 px-3 py-1 text-xs text-slate-300">
          {items.filter((item) => item.ready).length}/{items.length} analysebereit
        </span>
      </div>

      <div className="mt-5 grid gap-3">
        {isLoading ? (
          <p className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-400">
            Datenhygiene wird geladen...
          </p>
        ) : items.length === 0 ? (
          <p className="rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-4 text-sm text-yellow-100">
            Keine aktiven Symbole. Naechster Schritt: Watchlist oeffnen und ein Symbol aktiv anlegen.
          </p>
        ) : (
          items.map((item) => <SymbolDataReadinessCard key={item.symbol} item={item} />)
        )}
      </div>
    </section>
  );
}

function SymbolDataReadinessCard({ item }: { item: SymbolDataReadiness }) {
  return (
    <article className={`rounded-2xl border p-4 ${item.ready ? "border-emerald-300/30 bg-emerald-300/5" : "border-yellow-300/30 bg-yellow-300/10"}`}>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-50">{item.symbol}</h3>
          <p className="mt-1 text-sm text-slate-400">{item.nextAction}</p>
        </div>
        <span className={`rounded-full border px-3 py-1 text-xs ${item.ready ? "border-emerald-300/30 text-emerald-100" : "border-yellow-300/30 text-yellow-100"}`}>
          {item.ready ? "Analysebereit" : "Daten pruefen"}
        </span>
      </div>
      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        {item.timeframes.map((timeframe) => (
          <div key={`${item.symbol}-${timeframe.timeframe}`} className={`rounded-xl border p-3 text-sm ${readinessStatusClass(timeframe.status)}`}>
            <div className="flex items-center justify-between gap-2">
              <p className="font-semibold text-slate-50">{timeframe.timeframe}</p>
              <span className="rounded-full border border-current/20 px-2 py-0.5 text-xs">{formatLabel(timeframe.status)}</span>
            </div>
            <div className="mt-3 grid gap-2 text-xs opacity-90">
              <span>Kerzen: {timeframe.candleCount ?? "-"}</span>
              <span>Freshness: {timeframe.freshnessStatus ? formatLabel(timeframe.freshnessStatus) : "missing"}</span>
              <span>Source: {timeframe.source ? formatMarketDataSource(timeframe.source) : "-"}</span>
              <span>Provider: {timeframe.providerName ?? "-"}</span>
              <span>Letzte Kerze: {formatDateTime(timeframe.latestCandle)}</span>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function readinessStatusClass(status: TimeframeReadiness["status"]) {
  if (status === "ready") {
    return "border-emerald-300/20 bg-emerald-300/10 text-emerald-100";
  }
  if (status === "failed" || status === "insufficient") {
    return "border-red-300/30 bg-red-300/10 text-red-100";
  }
  return "border-yellow-300/30 bg-yellow-300/10 text-yellow-100";
}

function CsvFileMappingTable({
  items,
  mappings,
  onChange,
}: {
  items: WatchlistItem[];
  mappings: CsvFileMapping[];
  onChange: (items: CsvFileMapping[]) => void;
}) {
  const invalidCount = mappings.filter((mapping) => !mapping.watchlistItemId || !mapping.timeframe).length;

  function updateMapping(fileName: string, changes: Partial<CsvFileMapping>) {
    onChange(mappings.map((mapping) => (mapping.fileName === fileName ? { ...mapping, ...changes } : mapping)));
  }

  return (
    <div className="rounded-2xl border border-sky-300/20 bg-sky-300/10 p-4 text-sm text-sky-50">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-medium">CSV-Zuordnung vor Import</p>
          <p className="mt-1 text-sky-100/80">
            Pruefe Symbol und Timeframe je Datei. Unklare Zeilen muessen korrigiert werden, bevor
            der manuelle Import startet.
          </p>
        </div>
        {invalidCount > 0 ? (
          <span className="rounded-full border border-yellow-300/30 bg-yellow-300/10 px-3 py-1 text-xs text-yellow-50">
            {invalidCount} Zeile(n) blockiert
          </span>
        ) : (
          <span className="rounded-full border border-emerald-300/30 bg-emerald-300/10 px-3 py-1 text-xs text-emerald-50">
            Alle Zeilen bereit
          </span>
        )}
      </div>
      <p className="mt-3 rounded-xl border border-white/10 bg-slate-950/40 p-3 text-xs text-sky-100/80">
        Diese Tabelle speichert keine privaten Broker-, Depot- oder Orderdaten. Sie ordnet nur
        ausgewaehlte oeffentliche OHLCV-CSV-Dateien bestehenden Watchlist-Symbolen zu.
      </p>
      <div className="mt-3 overflow-x-auto rounded-xl border border-white/10">
        <table className="min-w-full divide-y divide-white/10 text-left text-xs">
          <thead className="bg-slate-950/70 text-sky-100/80">
            <tr>
              <th className="px-3 py-2 font-semibold">Datei</th>
              <th className="px-3 py-2 font-semibold">Erkannt</th>
              <th className="px-3 py-2 font-semibold">Ziel-Symbol</th>
              <th className="px-3 py-2 font-semibold">Timeframe</th>
              <th className="px-3 py-2 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 bg-slate-950/40">
            {mappings.map((mapping) => {
              const isBlocked = !mapping.watchlistItemId || !mapping.timeframe;
              return (
                <tr key={mapping.fileName} className={isBlocked ? "bg-yellow-300/5" : undefined}>
                  <td className="max-w-[13rem] px-3 py-3 align-top text-slate-100">
                    <p className="break-words font-semibold">{mapping.fileName}</p>
                    {mapping.detectedExchange ? (
                      <p className="mt-1 text-slate-400">Exchange: {mapping.detectedExchange}</p>
                    ) : null}
                  </td>
                  <td className="px-3 py-3 align-top text-slate-300">
                    <div className="grid gap-1">
                      <span>Symbol: {mapping.detectedSymbol ?? "unklar"}</span>
                      <span>Timeframe: {mapping.detectedTimeframe ?? "unklar"}</span>
                    </div>
                    {mapping.warning ? <p className="mt-2 text-yellow-100">{mapping.warning}</p> : null}
                  </td>
                  <td className="px-3 py-3 align-top">
                    <select
                      value={mapping.watchlistItemId}
                      onChange={(event) => updateMapping(mapping.fileName, { watchlistItemId: event.target.value })}
                      className="w-full min-w-40 rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
                    >
                      <option value="">Symbol waehlen</option>
                      {items.map((item) => (
                        <option key={`${mapping.fileName}-${item.id}`} value={item.id}>
                          {item.symbol} {item.name ? `- ${item.name}` : ""}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-3 py-3 align-top">
                    <select
                      value={mapping.timeframe}
                      onChange={(event) => updateMapping(mapping.fileName, { timeframe: event.target.value as Timeframe })}
                      className="w-full min-w-28 rounded-lg border border-white/10 bg-slate-900 px-3 py-2 text-slate-100 outline-none focus:border-emerald-300"
                    >
                      <option value="">Waehlen</option>
                      {timeframes.map((value) => (
                        <option key={`${mapping.fileName}-${value}`} value={value}>
                          {value}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-3 py-3 align-top">
                    <span
                      className={`inline-flex rounded-full border px-3 py-1 ${
                        isBlocked
                          ? "border-yellow-300/30 bg-yellow-300/10 text-yellow-50"
                          : "border-emerald-300/30 bg-emerald-300/10 text-emerald-50"
                      }`}
                    >
                      {isBlocked ? "Korrektur noetig" : "Bereit"}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-xs text-sky-100/80">
        Import bleibt manuell. Es wird keine Analyse, kein Alert, kein Trade und keine Broker-Aktion
        automatisch erstellt.
      </p>
    </div>
  );
}

function buildCsvFileMappings(files: File[], items: WatchlistItem[]): CsvFileMapping[] {
  return files.map((file) => {
    const detected = detectCsvFile(file.name);
    const matchedItem = detected.symbol ? findWatchlistItemBySymbol(items, detected.symbol) : null;
    return {
      fileName: file.name,
      detectedSymbol: detected.symbol,
      detectedExchange: detected.exchange,
      detectedTimeframe: detected.timeframe,
      warning: detected.warning,
      watchlistItemId: matchedItem?.id.toString() ?? "",
      timeframe: detected.timeframe ?? "",
    };
  });
}

function buildMappedDetectedFiles(mappings: CsvFileMapping[], items: WatchlistItem[]): DetectedCsvFile[] {
  return mappings.map((mapping) => {
    const item = items.find((watchlistItem) => watchlistItem.id.toString() === mapping.watchlistItemId) ?? null;
    return {
      fileName: mapping.fileName,
      symbol: item?.symbol.toUpperCase() ?? mapping.detectedSymbol,
      exchange: mapping.detectedExchange,
      timeframe: mapping.timeframe || mapping.detectedTimeframe,
      warning: mapping.warning,
    };
  });
}

function findWatchlistItemBySymbol(items: WatchlistItem[], symbol: string) {
  const normalizedSymbol = symbol.toUpperCase();
  return items.find((item) => item.symbol.toUpperCase() === normalizedSymbol) ?? null;
}

function ImportReadinessPanel({ groups }: { groups: ImportReadinessGroup[] }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
      <p className="font-medium text-slate-100">Import-Readiness nach Symbol</p>
      <p className="mt-1 text-slate-400">
        Fuer eine vollstaendige Analyse werden `1W`, `1D` und `4H` benoetigt. Diese Uebersicht nutzt
        gespeicherte Importe und die aktuelle Dateivorschau.
      </p>
      <div className="mt-3 grid gap-2">
        {groups.map((group) => (
          <div
            key={group.symbol}
            className={`rounded-xl border p-3 ${
              group.complete
                ? "border-emerald-300/30 bg-emerald-300/10"
                : "border-yellow-300/30 bg-yellow-300/10"
            }`}
          >
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="font-semibold text-slate-100">{group.symbol}</p>
              <span className="rounded-full border border-current/20 px-3 py-1 text-xs text-slate-100">
                {group.present.length}/3 Timeframes
              </span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2 text-xs">
              {timeframes.map((value) => (
                <span
                  key={`${group.symbol}-${value}`}
                  className={`rounded-full px-3 py-1 ${
                    group.present.includes(value)
                      ? "bg-emerald-300/20 text-emerald-100"
                      : "bg-slate-800 text-slate-300"
                  }`}
                >
                  {value}
                </span>
              ))}
            </div>
            {group.missing.length > 0 ? (
              <p className="mt-2 text-xs text-yellow-100">Fehlt: {group.missing.join(", ")}</p>
            ) : (
              <p className="mt-2 text-xs text-emerald-100">Vollstaendig fuer Analyse vorbereitet.</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function CsvWorkflowGuidancePanel({ groups }: { groups: ImportReadinessGroup[] }) {
  const guidanceItems = buildCsvWorkflowGuidance(groups);

  return (
    <div className="rounded-2xl border border-emerald-300/20 bg-emerald-300/10 p-4 text-sm text-emerald-50">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-medium">CSV-Arbeitsplan</p>
          <p className="mt-1 text-emerald-100/80">
            Nutze CSV gezielt: Wochenkontext fuer das Universum, Daily fuer aktive Kandidaten,
            `4H` nur fuer die Trigger-Liste.
          </p>
        </div>
        <span className="rounded-full border border-emerald-200/30 bg-slate-950/40 px-3 py-1 text-xs text-emerald-50">
          CSV-first, kein Live-Feed
        </span>
      </div>

      <div className="mt-3 grid gap-3 lg:grid-cols-3">
        {guidanceItems.map((item) => (
          <div key={item.title} className={`rounded-xl border p-3 ${item.className}`}>
            <div className="flex items-center justify-between gap-2">
              <p className="font-semibold text-slate-50">{item.title}</p>
              <span className="rounded-full border border-current/20 px-2 py-0.5 text-xs">{item.timeframe}</span>
            </div>
            <p className="mt-1 text-xs text-slate-200/80">{item.scope}</p>
            <p className="mt-3 text-2xl font-semibold text-slate-50">{item.count}</p>
            <p className="text-xs text-slate-200/80">Symbol(e) mit Bedarf</p>
            <p className="mt-3 text-xs text-slate-100">{item.guidance}</p>
            {item.symbols.length > 0 ? (
              <p className="mt-2 text-xs text-slate-200/80">Beispiele: {item.symbols.join(", ")}</p>
            ) : null}
          </div>
        ))}
      </div>

      <p className="mt-3 text-xs text-emerald-100/80">
        Diese Hinweise starten keine Analyse und erzeugen keine Alerts, Trades oder Orders. Sie helfen nur,
        den naechsten manuellen CSV-Import zu waehlen.
      </p>
    </div>
  );
}

function buildCsvWorkflowGuidance(groups: ImportReadinessGroup[]): CsvWorkflowGuidanceItem[] {
  const missingWeekly = groups.filter((group) => group.missing.includes("1W"));
  const missingDaily = groups.filter((group) => group.missing.includes("1D"));
  const missingFourHour = groups.filter((group) => group.missing.includes("4H"));
  const triggerCandidates = groups.filter(
    (group) => group.missing.includes("4H") && (group.present.includes("1W") || group.present.includes("1D")),
  );

  return [
    {
      title: "Wochen-Setup",
      timeframe: "1W",
      scope: "Universum vorbereiten",
      count: missingWeekly.length,
      symbols: missingWeekly.slice(0, 4).map((group) => group.symbol),
      guidance:
        missingWeekly.length > 0
          ? "Importiere 1W, wenn der grobe Kontext fehlt. Das ist eher Wochenend-/Vorbereitungsarbeit."
          : "1W ist fuer die sichtbaren Symbole vorhanden. Pruefe als Naechstes 1D oder 4H.",
      className: "border-sky-300/20 bg-sky-300/10",
    },
    {
      title: "Tagesreview",
      timeframe: "1D",
      scope: "Aktive Kandidaten aktualisieren",
      count: missingDaily.length,
      symbols: missingDaily.slice(0, 4).map((group) => group.symbol),
      guidance:
        missingDaily.length > 0
          ? "Importiere 1D fuer aktive Kandidaten nach Schluss oder vor der naechsten Review-Session."
          : "1D ist fuer die sichtbaren Symbole vorhanden. Nutze 4H nur fuer eine kleine Trigger-Liste.",
      className: "border-emerald-300/20 bg-emerald-300/10",
    },
    {
      title: "Trigger-Fokus",
      timeframe: "4H",
      scope: "Nur kleine Trigger-Liste",
      count: triggerCandidates.length || missingFourHour.length,
      symbols: (triggerCandidates.length > 0 ? triggerCandidates : missingFourHour).slice(0, 4).map((group) => group.symbol),
      guidance:
        triggerCandidates.length > 0
          ? "Importiere 4H gezielt fuer diese Symbole. Nicht das gesamte Universum intraday aktualisieren."
          : "4H ist nur sinnvoll fuer Symbole, die nach 1W/1D-Kontext wirklich nah an der Review sind.",
      className: "border-amber-300/20 bg-amber-300/10",
    },
  ];
}

function BatchAnalysisPanel({
  filter,
  isAnalyzing,
  onFilterChange,
  plan,
  results,
}: {
  filter: BatchAnalysisFilter;
  isAnalyzing: boolean;
  onFilterChange: (filter: BatchAnalysisFilter) => void;
  plan: BatchAnalysisPlanItem[];
  results: BatchAnalysisResultItem[];
}) {
  if (plan.length === 0) {
    return (
      <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-400">
        Noch keine importierten Symbole gefunden. Importiere zuerst Marktdaten fuer `1W`, `1D` und `4H`.
      </div>
    );
  }

  const completeCount = plan.filter((item) => item.seriesId).length;
  const skippedCount = plan.length - completeCount;
  const visibleItems = results.length > 0 ? results : plan.map(toPlannedBatchAnalysisResult);
  const summary = summarizeBatchAnalysisResults(visibleItems);
  const filteredItems = visibleItems.filter((item) => batchAnalysisFilterForItem(item) === filter || filter === "all");

  return (
    <div className="mt-5 grid gap-4">
      <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <Metric label="Symbole" value={plan.length.toString()} />
        <Metric label="Analysebereit" value={completeCount.toString()} />
        <Metric label="Geplant uebersprungen" value={skippedCount.toString()} />
        <Metric label="Paper-Kandidat" value={summary.paper.toString()} />
        <Metric label="Beobachten" value={summary.watch.toString()} />
        <Metric label="Kein Trade" value={(summary.noTrade + summary.dataProblem).toString()} />
      </div>

      <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-300">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="font-medium text-slate-100">Batch-Filter</p>
            <p className="mt-1 text-slate-400">
              Standard zeigt alle Ergebnisse, inklusive uebersprungener und fehlgeschlagener Symbole.
            </p>
          </div>
          <span className="rounded-full border border-white/10 bg-slate-800 px-3 py-1 text-xs text-slate-300">
            Sichtbar: {filteredItems.length}/{visibleItems.length}
          </span>
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {batchAnalysisFilterOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => onFilterChange(option.value)}
              className={`rounded-full border px-3 py-1 text-xs transition ${
                filter === option.value
                  ? "border-emerald-300/50 bg-emerald-300/15 text-emerald-100"
                  : "border-white/10 bg-slate-900 text-slate-300 hover:border-emerald-300/30"
              }`}
            >
              {option.label} ({summary[option.summaryKey]})
            </button>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-400">
          Filter aendern nur die Ansicht. Sie erzeugen keine Trades, Alerts oder Kauf-/Verkaufsanweisungen.
        </p>
      </div>

      <div className="grid gap-3">
        {filteredItems.map((item) => (
          <BatchAnalysisResultCard key={item.symbol} isAnalyzing={isAnalyzing} item={item} />
        ))}
        {filteredItems.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-sm text-slate-400">
            Keine Ergebnisse fuer diesen Filter. Wechsle zu "Alle", um Safety-Blocker wieder sichtbar zu machen.
          </div>
        ) : null}
      </div>
    </div>
  );
}

function BatchAnalysisResultCard({
  isAnalyzing,
  item,
}: {
  isAnalyzing: boolean;
  item: BatchAnalysisResultItem;
}) {
  if (item.status === "success" && item.result) {
    const decision = buildSignalDecision(item.result.signal);
    const explanation = signalDecisionExplanation(decision.kind);
    const diagnosis = buildAnalysisDiagnosis(item.result);
    return (
      <article className={`rounded-2xl border p-4 ${signalDecisionToneClass(decision.tone)}`}>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <span className={`h-4 w-4 rounded-full ${signalDecisionDotClass(decision.tone)}`} />
              <h3 className="text-lg font-semibold text-slate-50">{item.symbol}</h3>
              <span className="rounded-full border border-current/20 px-3 py-1 text-xs">{decision.label}</span>
            </div>
            <p className="mt-3 text-xl font-semibold text-slate-50">{decision.headline}</p>
            <p className="mt-2 text-sm">{decision.action}</p>
            <div className="mt-4 grid gap-3 lg:grid-cols-2">
              <PlainLanguageBox title="Was bedeutet das?" text={explanation.whatItMeans} />
              <PlainLanguageBox title="Was jetzt?" text={explanation.whatNow} />
            </div>
          </div>
          <span className="rounded-full border border-current/20 px-3 py-1 text-xs">
            Qualitaet: {decision.quality}
          </span>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Metric label="Score" value={`${item.result.signal.score} / ${item.result.signal.score_class.replaceAll("_", " ")}`} />
          <Metric label="Backend Status" value={item.result.signal.status.replaceAll("_", " ")} />
          <Metric label="R:R" value={item.result.signal.risk_reward ? `${formatNumber(item.result.signal.risk_reward)}R` : "-"} />
          <Metric label="Kerzen" value={item.result.candle_count.toString()} />
          <Metric label="Snapshots" value={item.result.indicator_snapshot_count.toString()} />
        </div>
        {decision.kind === "data_problem" ? <AnalysisDiagnosisPanel diagnosis={diagnosis} /> : null}
      </article>
    );
  }

  const toneClass =
    item.status === "failed"
      ? "border-red-300/30 bg-red-300/10 text-red-100"
      : item.status === "pending" && isAnalyzing
        ? "border-sky-300/30 bg-sky-300/10 text-sky-100"
        : "border-yellow-300/30 bg-yellow-300/10 text-yellow-100";
  const label =
    item.status === "failed"
      ? "Fehler"
      : item.status === "pending" && isAnalyzing
        ? "Wartet auf Analyse"
        : item.status === "pending"
          ? "Bereit"
        : "Uebersprungen";

  return (
    <article className={`rounded-2xl border p-4 ${toneClass}`}>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <h3 className="text-lg font-semibold">{item.symbol}</h3>
        <span className="rounded-full border border-current/20 px-3 py-1 text-xs">{label}</span>
      </div>
      <p className="mt-2 text-sm">{item.reason ?? "Analyse wurde noch nicht gestartet."}</p>
    </article>
  );
}

function PlainLanguageBox({ text, title }: { text: string; title: string }) {
  return (
    <div className="rounded-xl border border-current/15 bg-slate-950/30 p-3 text-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">{title}</p>
      <p className="mt-2 opacity-90">{text}</p>
    </div>
  );
}

function AnalysisDiagnosisPanel({ diagnosis }: { diagnosis: AnalysisDiagnosis }) {
  const hasDetails =
    diagnosis.riskFlags.length > 0 ||
    diagnosis.noTradeReasons.length > 0 ||
    diagnosis.qualityIssues.length > 0;

  return (
    <div className="mt-4 rounded-2xl border border-slate-300/20 bg-slate-950/50 p-4 text-sm text-slate-200">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-semibold text-slate-50">Datenproblem-Diagnose</p>
          <p className="mt-1 text-slate-400">
            Diese Werte kommen direkt aus der Analyse und erklaeren, warum kein Trade erzeugt wird.
          </p>
        </div>
        <span className="rounded-full border border-slate-300/20 px-3 py-1 text-xs text-slate-200">
          Safety-Blocker
        </span>
      </div>

      {hasDetails ? (
        <div className="mt-4 grid gap-3 lg:grid-cols-3">
          <DiagnosticBadgeList
            empty="Keine Risk Flags"
            items={diagnosis.riskFlags}
            title="Risk Flags"
          />
          <DiagnosticBadgeList
            empty="Keine No-Trade-Gruende"
            items={diagnosis.noTradeReasons}
            title="No-Trade-Gruende"
          />
          <QualityIssueList checks={diagnosis.qualityIssues} />
        </div>
      ) : (
        <p className="mt-3 rounded-xl border border-white/10 bg-white/[0.03] p-3 text-slate-400">
          Keine Detailursache in der Analyse-Antwort enthalten. Pruefe den Einzelimport oder starte
          die Analyse erneut.
        </p>
      )}

      <p className="mt-3 text-xs text-slate-500">
        Typische Ursache nach Provider-Sync: weniger als 200 Kerzen in einem Timeframe oder fehlende
        Indikatoren wie EMA200.
      </p>
    </div>
  );
}

function DiagnosticBadgeList({
  empty,
  items,
  title,
}: {
  empty: string;
  items: string[];
  title: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <span key={item} className="rounded-full bg-slate-700/80 px-3 py-1 text-xs text-slate-100">
              {formatDiagnosticToken(item)}
            </span>
          ))
        ) : (
          <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">
            {empty}
          </span>
        )}
      </div>
    </div>
  );
}

function QualityIssueList({ checks }: { checks: MarketDataAnalysisResult["signal"]["quality_report"] }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Quality Checks</p>
      {checks.length > 0 ? (
        <div className="mt-3 grid gap-2">
          {checks.map((check) => (
            <div key={check.key} className="rounded-lg border border-white/10 bg-slate-950/50 p-2">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium text-slate-100">{check.label}</span>
                <span className={`rounded-full px-2 py-0.5 text-xs ${qualityStatusClass(check.status)}`}>
                  {formatLabel(check.status)}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-400">{check.detail}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-3 text-sm text-slate-500">Keine blockierten oder warnenden Checks.</p>
      )}
    </div>
  );
}

function buildAnalysisDiagnosis(result: MarketDataAnalysisResult): AnalysisDiagnosis {
  return {
    riskFlags: result.signal.risk_flags,
    noTradeReasons: result.signal.no_trade_reasons,
    qualityIssues: result.signal.quality_report.filter((check) =>
      ["blocked", "warning", "missing"].includes(check.status),
    ),
  };
}

function toPlannedBatchAnalysisResult(item: BatchAnalysisPlanItem): BatchAnalysisResultItem {
  return {
    symbol: item.symbol,
    status: item.seriesId ? "pending" : "skipped",
    seriesId: item.seriesId,
    reason: item.skipReason,
    result: null,
  };
}

const batchAnalysisFilterOptions: {
  value: BatchAnalysisFilter;
  label: string;
  summaryKey: keyof BatchAnalysisSummary;
}[] = [
  { value: "all", label: "Alle", summaryKey: "all" },
  { value: "paper", label: "Paper-Kandidat", summaryKey: "paper" },
  { value: "watch", label: "Beobachten", summaryKey: "watch" },
  { value: "no_trade", label: "Kein Trade", summaryKey: "noTrade" },
  { value: "data_problem", label: "Datenproblem", summaryKey: "dataProblem" },
  { value: "pending", label: "Bereit/Wartet", summaryKey: "pending" },
  { value: "skipped", label: "Uebersprungen", summaryKey: "skipped" },
  { value: "failed", label: "Fehler", summaryKey: "failed" },
];

type BatchAnalysisSummary = {
  all: number;
  paper: number;
  watch: number;
  noTrade: number;
  dataProblem: number;
  pending: number;
  skipped: number;
  failed: number;
};

function summarizeBatchAnalysisResults(items: BatchAnalysisResultItem[]): BatchAnalysisSummary {
  const summary: BatchAnalysisSummary = {
    all: items.length,
    paper: 0,
    watch: 0,
    noTrade: 0,
    dataProblem: 0,
    pending: 0,
    skipped: 0,
    failed: 0,
  };

  for (const item of items) {
    const filter = batchAnalysisFilterForItem(item);
    if (filter === "paper") {
      summary.paper += 1;
    } else if (filter === "watch") {
      summary.watch += 1;
    } else if (filter === "no_trade") {
      summary.noTrade += 1;
    } else if (filter === "data_problem") {
      summary.dataProblem += 1;
    } else if (filter === "pending") {
      summary.pending += 1;
    } else if (filter === "skipped") {
      summary.skipped += 1;
    } else if (filter === "failed") {
      summary.failed += 1;
    }
  }

  return summary;
}

function batchAnalysisFilterForItem(item: BatchAnalysisResultItem): Exclude<BatchAnalysisFilter, "all"> {
  if (item.status === "failed") {
    return "failed";
  }
  if (item.status === "pending") {
    return "pending";
  }
  if (item.status === "skipped" || !item.result) {
    return "skipped";
  }

  const decision = buildSignalDecision(item.result.signal);
  if (decision.label === "Paper-Kandidat") {
    return "paper";
  }
  if (decision.label === "Beobachten") {
    return "watch";
  }
  if (decision.label === "Datenproblem") {
    return "data_problem";
  }
  return "no_trade";
}

function buildImportReadinessGroups(
  history: ImportHistoryItem[],
  detectedFiles: DetectedCsvFile[],
): ImportReadinessGroup[] {
  const grouped = new Map<string, Set<Timeframe>>();

  for (const item of history) {
    if (!isUsableImportHistoryItem(item)) {
      continue;
    }
    const symbol = item.symbol.toUpperCase();
    if (!grouped.has(symbol)) {
      grouped.set(symbol, new Set());
    }
    grouped.get(symbol)?.add(item.timeframe);
  }

  for (const item of detectedFiles) {
    if (!item.symbol || !item.timeframe) {
      continue;
    }
    if (!grouped.has(item.symbol)) {
      grouped.set(item.symbol, new Set());
    }
    grouped.get(item.symbol)?.add(item.timeframe);
  }

  return Array.from(grouped.entries())
    .map(([symbol, presentSet]) => {
      const present = timeframes.filter((value) => presentSet.has(value));
      const missing = timeframes.filter((value) => !presentSet.has(value));
      return {
        symbol,
        present,
        missing,
        complete: missing.length === 0,
      };
    })
    .sort((left, right) => Number(right.complete) - Number(left.complete) || left.symbol.localeCompare(right.symbol));
}

function buildSymbolDataReadiness(items: WatchlistItem[], history: ImportHistoryItem[]): SymbolDataReadiness[] {
  const latestBySymbolAndTimeframe = new Map<string, ImportHistoryItem>();

  for (const item of history) {
    const key = `${item.symbol.toUpperCase()}-${item.timeframe}`;
    const current = latestBySymbolAndTimeframe.get(key);
    if (!current || new Date(item.imported_at).getTime() > new Date(current.imported_at).getTime()) {
      latestBySymbolAndTimeframe.set(key, item);
    }
  }

  return items
    .map((item) => {
      const symbol = item.symbol.toUpperCase();
      const readiness = timeframes.map((timeframe) => {
        const latest = latestBySymbolAndTimeframe.get(`${symbol}-${timeframe}`) ?? null;
        return toTimeframeReadiness(timeframe, latest);
      });
      const ready = readiness.every((timeframe) => timeframe.status === "ready");
      return {
        symbol,
        isActive: item.is_active,
        timeframes: readiness,
        ready,
        nextAction: nextReadinessAction(readiness),
      };
    })
    .sort((left, right) => Number(right.ready) - Number(left.ready) || left.symbol.localeCompare(right.symbol));
}

function toTimeframeReadiness(timeframe: Timeframe, item: ImportHistoryItem | null): TimeframeReadiness {
  if (!item) {
    return {
      timeframe,
      status: "missing",
      candleCount: null,
      freshnessStatus: null,
      source: null,
      providerName: null,
      latestCandle: null,
    };
  }

  const status = timeframeReadinessStatus(item);
  return {
    timeframe,
    status,
    candleCount: item.candle_count,
    freshnessStatus: item.freshness_status,
    source: item.source,
    providerName: item.provider_name,
    latestCandle: item.end_time,
  };
}

function timeframeReadinessStatus(item: ImportHistoryItem): TimeframeReadiness["status"] {
  if (item.status === "failed" || item.sync_status === "failed" || item.sync_status === "skipped") {
    return "failed";
  }
  if (item.candle_count < 200) {
    return "insufficient";
  }
  if (item.freshness_status === "fresh") {
    return "ready";
  }
  return item.freshness_status;
}

function nextReadinessAction(timeframesReadiness: TimeframeReadiness[]) {
  const blocked = timeframesReadiness.find((item) => item.status !== "ready");
  if (!blocked) {
    return "1W, 1D und 4H sind vorhanden und fresh genug. Analyse kann bewusst manuell gestartet werden.";
  }
  if (blocked.status === "missing") {
    return `${blocked.timeframe} fehlt. Naechster Schritt: CSV importieren oder geeigneten Provider-Pfad manuell nutzen.`;
  }
  if (blocked.status === "insufficient") {
    return `${blocked.timeframe} hat zu wenig Kerzen. Mehr Historie importieren, bevor Analyse gestartet wird.`;
  }
  if (blocked.status === "failed") {
    return `${blocked.timeframe} ist failed/skipped. Fehler pruefen und Daten neu importieren.`;
  }
  return `${blocked.timeframe} ist ${formatLabel(blocked.status)}. Daten vor Analyse aktualisieren oder konservativ blockiert lassen.`;
}

function isUsableImportHistoryItem(item: ImportHistoryItem) {
  return (
    item.candle_count > 0 &&
    item.status !== "failed" &&
    item.sync_status !== "failed" &&
    item.sync_status !== "skipped"
  );
}

function buildBatchAnalysisPlan(history: ImportHistoryItem[]): BatchAnalysisPlanItem[] {
  const grouped = new Map<string, ImportHistoryItem[]>();

  for (const item of history) {
    if (!isUsableImportHistoryItem(item)) {
      continue;
    }
    const symbol = item.symbol.toUpperCase();
    grouped.set(symbol, [...(grouped.get(symbol) ?? []), item]);
  }

  return Array.from(grouped.entries())
    .map(([symbol, items]) => {
      const present = new Set(items.map((item) => item.timeframe));
      const missing = timeframes.filter((value) => !present.has(value));
      const anchor = latestSeriesForTimeframe(items, "1D");
      return {
        symbol,
        seriesId: missing.length === 0 ? anchor?.series_id ?? null : null,
        missing,
        skipReason:
          missing.length > 0
            ? `Fehlende Timeframes: ${missing.join(", ")}. Analyse wird nicht gestartet.`
            : anchor
              ? null
              : "Keine nutzbare 1D-Serie als Analyse-Anker gefunden.",
      };
    })
    .sort((left, right) => Number(Boolean(right.seriesId)) - Number(Boolean(left.seriesId)) || left.symbol.localeCompare(right.symbol));
}

function latestSeriesForTimeframe(items: ImportHistoryItem[], timeframe: Timeframe) {
  return items
    .filter((item) => item.timeframe === timeframe)
    .toSorted((left, right) => {
      const importedDiff = new Date(right.imported_at).getTime() - new Date(left.imported_at).getTime();
      return importedDiff || right.series_id - left.series_id;
    })[0];
}

function detectCsvFile(fileName: string): DetectedCsvFile {
  const baseName = fileName.replace(/\.csv$/i, "");
  const timeframeMatch = baseName.match(/(?:^|[,_\s-])(1D|1W|240|4H)(?:[,_\s-]|$)/i);
  const timeframe = normalizeDetectedTimeframe(timeframeMatch?.[1] ?? null);
  const prefixedMatch = baseName.match(
    /^([A-Z0-9]+)[_,\s-]+([A-Z0-9.:-]+?)(?:[_,\s-]+(?:1D|1W|240|4H)\b|$)/i,
  );
  const symbolOnlyMatch = baseName.match(/^([A-Z0-9.:-]+?)(?:[_,\s-]+(?:1D|1W|240|4H)\b|$)/i);
  const detectedExchange = prefixedMatch?.[1]?.toUpperCase() ?? null;
  const detectedSymbol = normalizeDetectedSymbol(prefixedMatch?.[2] ?? null);
  const exchange = detectedSymbol && detectedSymbol !== timeframe ? detectedExchange : null;
  const symbol = exchange ? detectedSymbol : normalizeDetectedSymbol(symbolOnlyMatch?.[1] ?? null);
  const warning =
    symbol && timeframe
      ? null
      : "Dateiname konnte nicht eindeutig erkannt werden. Bitte Symbol und Timeframe manuell pruefen.";

  return {
    fileName,
    symbol,
    exchange,
    timeframe,
    warning,
  };
}

function normalizeDetectedTimeframe(value: string | null): Timeframe | null {
  if (!value) {
    return null;
  }
  const normalized = value.toUpperCase();
  if (normalized === "240" || normalized === "4H") {
    return "4H";
  }
  if (normalized === "1D" || normalized === "1W") {
    return normalized;
  }
  return null;
}

function normalizeDetectedSymbol(value: string | null) {
  if (!value) {
    return null;
  }
  return value.replace(/^.*:/, "").toUpperCase();
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
        <Metric label="Kerzen" value={result.candle_count.toString()} />
        <Metric label="Letzter Sync" value={formatDateTime(result.last_synced_at)} />
        <Metric label="Exchange" value={result.provider_exchange ?? "-"} />
        <Metric label="Fehler-Code" value={result.sync_error_code ?? "-"} />
        <Metric label="Status" value={formatLabel(result.sync_status)} />
      </div>

      <MarketDataFreshnessNotice freshnessStatus={result.freshness_status} syncStatus={result.sync_status} />

      <ProviderCapabilityHintPanel hints={result.provider_capabilities} selectedTimeframe={result.timeframe} />

      {result.capability_note ? (
        <p className="rounded-2xl border border-sky-300/20 bg-sky-300/10 p-3 text-sm text-sky-100">
          {result.capability_note}
        </p>
      ) : null}

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
      <p className="text-lg font-semibold text-slate-200">Noch keine Datenaktualisierung angefragt.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Starte die Aktualisierung manuell. Das Ergebnis erscheint hier und in der Import-Historie.
      </p>
    </div>
  );
}

function ProviderCapabilityHintPanel({
  hints,
  selectedTimeframe,
}: {
  hints: ProviderTimeframeCapability[];
  selectedTimeframe: Timeframe;
}) {
  const selectedHint = hints.find((hint) => hint.timeframe === selectedTimeframe);

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-3 text-sm text-slate-300">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-medium text-slate-100">Provider-Capability</p>
          <p className="mt-1 text-slate-400">
            Aktueller Provider-Pfad ist gespeicherte Marktdaten-Aktualisierung, nicht Live- oder
            Intraday-Signalversorgung.
          </p>
        </div>
        {selectedHint ? (
          <span className={`rounded-full border px-3 py-1 text-xs ${capabilityBadgeClass(selectedHint.supported)}`}>
            {selectedTimeframe}: {selectedHint.supported ? "unterstuetzt" : "CSV-Fallback"}
          </span>
        ) : null}
      </div>
      <div className="mt-3 grid gap-2 sm:grid-cols-3">
        {hints.map((hint) => (
          <div
            key={hint.timeframe}
            className={`rounded-xl border p-3 ${
              hint.timeframe === selectedTimeframe ? "border-emerald-300/30 bg-emerald-300/5" : "border-white/10"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="font-semibold text-slate-100">{hint.timeframe}</span>
              <span className={`rounded-full border px-2 py-0.5 text-xs ${capabilityBadgeClass(hint.supported)}`}>
                {hint.supported ? "Provider" : "CSV"}
              </span>
            </div>
            <p className="mt-2 text-xs text-slate-400">{hint.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function buildProviderCapabilityHints(result: MarketDataSyncResult | null) {
  if (result?.provider_capabilities.length) {
    return result.provider_capabilities;
  }

  return defaultProviderCapabilities();
}

function defaultProviderCapabilities(): ProviderTimeframeCapability[] {
  return [
    {
      timeframe: "1W",
      supported: false,
      reason: "Weekly Provider-Aktualisierung ist im ersten Pfad nicht aktiv; nutze TradingView CSV.",
    },
    {
      timeframe: "1D",
      supported: true,
      reason: "Guarded Daily/EOD-Aktualisierung ist fuer konfigurierte Symbole vorgesehen.",
    },
    {
      timeframe: "4H",
      supported: false,
      reason: "4H/Intraday-Provider-Aktualisierung ist nicht aktiv; nutze TradingView CSV.",
    },
  ];
}

function capabilityBadgeClass(supported: boolean) {
  return supported
    ? "border-emerald-300/30 bg-emerald-300/10 text-emerald-100"
    : "border-yellow-300/30 bg-yellow-300/10 text-yellow-100";
}

function providerSyncState(result: MarketDataSyncResult) {
  if (result.sync_status === "success") {
    return result.freshness_status === "fresh"
      ? {
          title: "Datenaktualisierung gespeichert",
          message:
            "Provider-Daten wurden gespeichert und als fresh markiert. Das ist weiterhin kein Live-Preis und startet keine Analyse automatisch.",
          className: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
        }
      : {
          title: "Datenaktualisierung gespeichert, aber Freshness pruefen",
          message:
            "Provider-Daten wurden gespeichert, sind aber nicht fresh. Nutze sie nur als Kontext und pruefe den Datenstand vor einer Analyse.",
          className: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
        };
  }

  if (result.sync_status === "skipped") {
    return {
      title: "Datenaktualisierung uebersprungen",
      message:
        result.sync_error_code === "sync_disabled"
          ? "Provider-Aktualisierung ist im Backend deaktiviert. Das ist der sichere Default und es wurden keine Provider-Daten abgerufen."
          : "Die Aktualisierung wurde sicher uebersprungen. Pruefe die Backend-Konfiguration, falls du Provider-Daten erwartest.",
      className: "border-slate-500/30 bg-slate-800/70 text-slate-200",
    };
  }

  if (result.sync_status === "partial") {
    return {
      title: "Datenaktualisierung teilweise nutzbar",
      message:
        "Die Aktualisierung hat nur einen Teilzustand geliefert. Fehlende Kerzen oder Timeframes koennen Analyse-Ergebnisse konservativ blockieren.",
      className: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
    };
  }

  return {
    title: "Datenaktualisierung fehlgeschlagen",
    message:
      result.sync_error_code === "unsupported_timeframe"
        ? "Dieser Timeframe wird vom aktuellen Provider-Pfad nicht unterstuetzt. Nutze TradingView CSV als Fallback und behandle den Datenstand konservativ."
        : "Die Aktualisierung wurde nicht als nutzbarer Datenstand gespeichert. Pruefe den Fehler-Code und behandle den Datenstand konservativ.",
    className: "border-red-300/30 bg-red-300/10 text-red-100",
  };
}

function AnalysisResultCard({ result }: { result: MarketDataAnalysisResult }) {
  const signal = result.signal;
  const decision = buildSignalDecision(signal);
  const explanation = signalDecisionExplanation(decision.kind);
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
            <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">Was bedeutet das?</p>
            <p className="mt-3 text-sm">{explanation.whatItMeans}</p>
          </div>
          <div className="rounded-xl border border-current/15 bg-slate-950/30 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">Was jetzt?</p>
            <p className="mt-3 text-sm">{explanation.whatNow}</p>
            <p className="mt-2 text-xs opacity-75">Keine automatische Order. Echte Ausfuehrung bleibt manuell.</p>
          </div>
        </div>

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
            <p className="text-xs font-semibold uppercase tracking-[0.18em] opacity-80">Backend-Hinweis</p>
            <p className="mt-3 text-sm">{decision.action}</p>
            <p className="mt-2 text-xs opacity-75">Pruefhinweis, keine Buy/Sell-Anweisung.</p>
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

function formatDiagnosticToken(value: string) {
  return value.replaceAll("_", " ");
}

function qualityStatusClass(status: string) {
  if (status === "blocked" || status === "missing") {
    return "bg-red-300/10 text-red-100";
  }
  if (status === "warning") {
    return "bg-yellow-300/10 text-yellow-100";
  }
  return "bg-emerald-300/10 text-emerald-100";
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
