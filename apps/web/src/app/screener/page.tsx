"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import {
  ApiError,
  addScreenerResultToWatchlist,
  fetchScreenerImports,
  fetchScreenerResults,
  importScreenerCsv,
  redirectToLoginOnAuthError,
} from "@/lib/api";
import type { AssetClass } from "@/types/signals";
import type {
  ScreenerImport,
  ScreenerImportError,
  ScreenerResult,
  ScreenerResultFilters,
  ScreenerResultSortBy,
  ScreenerResultSortDirection,
  ScreenerResultStatus,
} from "@/types/screener";

type ScreenerPageError = {
  summary: string;
  details: ScreenerImportError[];
};

type ScreenerFiltersState = {
  asset_class: "" | AssetClass;
  status: "" | ScreenerResultStatus;
  exchange: string;
  screener_import_id: "" | number;
  min_volume: string;
  min_relative_volume: string;
  min_rsi14: string;
  max_rsi14: string;
  sort_by: ScreenerResultSortBy;
  sort_direction: ScreenerResultSortDirection;
};

const emptyResultFilters: ScreenerFiltersState = {
  asset_class: "",
  status: "",
  exchange: "",
  screener_import_id: "",
  min_volume: "",
  min_relative_volume: "",
  min_rsi14: "",
  max_rsi14: "",
  sort_by: "created_at",
  sort_direction: "desc",
};

const statusTone: Record<string, string> = {
  candidate: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  watchlist_added: "border-sky-300/30 bg-sky-300/10 text-sky-100",
  duplicate: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
  rejected: "border-red-300/30 bg-red-300/10 text-red-100",
  ignored: "border-slate-400/30 bg-slate-400/10 text-slate-200",
  imported: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  partial: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
  failed: "border-red-300/30 bg-red-300/10 text-red-100",
  pending: "border-slate-400/30 bg-slate-400/10 text-slate-200",
  validated: "border-sky-300/30 bg-sky-300/10 text-sky-100",
};

export default function ScreenerPage() {
  const authStatus = useProtectedRoute();
  const [imports, setImports] = useState<ScreenerImport[]>([]);
  const [results, setResults] = useState<ScreenerResult[]>([]);
  const [assetClass, setAssetClass] = useState<AssetClass>("stock");
  const [filters, setFilters] = useState<ScreenerFiltersState>(emptyResultFilters);
  const [preset, setPreset] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [convertingResultId, setConvertingResultId] = useState<number | null>(null);
  const [error, setError] = useState<ScreenerPageError | null>(null);
  const [createdImport, setCreatedImport] = useState<ScreenerImport | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function loadData(resultFilters: ScreenerFiltersState = filters) {
    setIsLoading(true);
    setError(null);
    try {
      const [loadedImports, loadedResults] = await Promise.all([
        fetchScreenerImports(),
        fetchScreenerResults(toApiFilters(resultFilters)),
      ]);
      setImports(loadedImports);
      setResults(loadedResults);
    } catch (loadError) {
      if (redirectToLoginOnAuthError(loadError)) {
        return;
      }
      setError(toSimpleError(loadError, "Screener-Daten konnten nicht geladen werden."));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (authStatus === "authenticated") {
      void loadData();
    }
  }, [authStatus]);

  const summary = useMemo(() => buildSummary(results), [results]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function submitImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setCreatedImport(null);

    if (!file) {
      setError(toSimpleError("Waehle eine TradingView Screener CSV-Datei aus."));
      return;
    }

    const formData = new FormData();
    formData.append("asset_class", assetClass);
    formData.append("file", file);
    if (preset.trim()) {
      formData.append("screener_preset", preset.trim());
    }

    setIsImporting(true);
    try {
      const imported = await importScreenerCsv(formData);
      setCreatedImport(imported);
      setNotice(null);
      setFile(null);
      await loadData(filters);
    } catch (importError) {
      if (redirectToLoginOnAuthError(importError)) {
        return;
      }
      setError(toImportError(importError));
    } finally {
      setIsImporting(false);
    }
  }

  async function addToWatchlist(result: ScreenerResult) {
    const message = result.watchlist_item_id
      ? `${result.symbol} ist bereits mit einem Watchlist-Eintrag verknuepft. Status aktualisieren?`
      : `${result.symbol} bewusst zur Watchlist hinzufuegen? Es werden keine Analyse, Signale, Trades oder Alerts erstellt.`;
    if (!window.confirm(message)) {
      return;
    }

    setError(null);
    setNotice(null);
    setConvertingResultId(result.id);
    try {
      const converted = await addScreenerResultToWatchlist(result.id);
      setResults((currentResults) =>
        currentResults.map((currentResult) => (currentResult.id === converted.id ? converted : currentResult)),
      );
      setNotice(
        converted.status === "duplicate"
          ? `${converted.symbol} ist bereits in der Watchlist und wurde als Duplikat verknuepft.`
          : `${converted.symbol} wurde zur Watchlist hinzugefuegt.`,
      );
    } catch (conversionError) {
      if (redirectToLoginOnAuthError(conversionError)) {
        return;
      }
      setError(toSimpleError(conversionError, "Kandidat konnte nicht zur Watchlist hinzugefuegt werden."));
    } finally {
      setConvertingResultId(null);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#7c3aed,transparent_34%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Screener</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Screener CSV pruefen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Importiere TradingView Screener Exporte als manuelle Review-Kandidaten. Es werden
                keine Watchlist-Eintraege, Signale, Trades oder Orders automatisch erstellt.
              </p>
            </div>
            <div className="flex flex-wrap gap-4 text-sm">
              <a className="text-emerald-300 hover:text-emerald-200" href="/watchlist">
                Watchlist
              </a>
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {error ? <ErrorMessage message={error} /> : null}
        {notice ? <NoticeMessage message={notice} /> : null}

        <section className="grid gap-4 md:grid-cols-4">
          <SummaryCard label="Kandidaten" value={summary.candidate.toString()} tone="border-emerald-300/40" />
          <SummaryCard label="Duplikate" value={summary.duplicate.toString()} tone="border-yellow-300/40" />
          <SummaryCard label="Watchlist" value={summary.watchlist.toString()} tone="border-sky-300/40" />
          <SummaryCard label="Importe" value={imports.length.toString()} />
        </section>

        <section className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <form onSubmit={submitImport} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-xl font-semibold">Screener CSV hochladen</h2>
                <p className="mt-2 text-sm text-slate-400">
                  Pflicht: Symbol/Ticker. Optionale Felder wie Exchange, Price, Volume, RSI oder EMAs
                  werden als Kontext gespeichert.
                </p>
              </div>
              <button
                type="button"
                onClick={() => void loadData()}
                className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
              >
                Aktualisieren
              </button>
            </div>

            <div className="mt-6 grid gap-4">
              <label className="grid gap-2 text-sm text-slate-300">
                Asset Class
                <select
                  value={assetClass}
                  onChange={(event) => setAssetClass(event.target.value as AssetClass)}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                >
                  <option value="stock">Stock</option>
                  <option value="crypto">Crypto</option>
                </select>
              </label>

              <label className="grid gap-2 text-sm text-slate-300">
                Preset optional
                <input
                  value={preset}
                  onChange={(event) => setPreset(event.target.value)}
                  className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
                  placeholder="US Growth Pullback"
                />
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

              <p className="rounded-2xl border border-yellow-300/20 bg-yellow-300/10 p-4 text-sm text-yellow-50">
                Screener-Zeilen sind nur Kandidaten. Pruefe Datenkontext und erstelle Watchlist-Eintraege
                spaeter bewusst manuell.
              </p>

              <button
                disabled={isImporting || isLoading}
                type="submit"
                className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
              >
                {isImporting ? "Importiere..." : "Screener CSV importieren"}
              </button>
            </div>
          </form>

          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Letzter Import</h2>
            <p className="mt-2 text-sm text-slate-400">
              Validierung, Duplikate und rejected Rows bleiben sichtbar. Partial bedeutet Review noetig,
              nicht dass Kandidaten direkt handelbar sind.
            </p>
            <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
              {createdImport ? <ScreenerImportCard item={createdImport} /> : <ImportEmptyState />}
            </div>
          </section>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Screener Kandidaten</h2>
              <p className="mt-2 text-sm text-slate-400">
                Review-Liste aus gespeicherten Screener-Snapshots. Keine Live-Daten, keine Empfehlung,
                keine automatische Analyse.
              </p>
            </div>
            <span className="text-sm text-slate-400">{results.length} Rows</span>
          </div>

          <ScreenerFiltersPanel
            filters={filters}
            imports={imports}
            resultCount={results.length}
            onChange={setFilters}
            onApply={(nextFilters) => void loadData(nextFilters)}
            onReset={() => {
              setFilters(emptyResultFilters);
              void loadData(emptyResultFilters);
            }}
          />

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Screener-Kandidaten werden geladen...</p>
            ) : results.length > 0 ? (
              <div className="divide-y divide-white/10">
                {results.map((result) => (
                  <ScreenerResultCard
                    key={result.id}
                    result={result}
                    isConverting={convertingResultId === result.id}
                    onAddToWatchlist={addToWatchlist}
                  />
                ))}
              </div>
            ) : (
              <ResultsEmptyState />
            )}
          </div>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Screener Import-Historie</h2>
              <p className="mt-2 text-sm text-slate-400">
                Import-Snapshots inklusive accepted, duplicate und rejected Counts.
              </p>
            </div>
            <span className="text-sm text-slate-400">{imports.length} Importe</span>
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Screener-Importe werden geladen...</p>
            ) : imports.length > 0 ? (
              <div className="divide-y divide-white/10">
                {imports.map((item) => (
                  <ScreenerImportCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <ImportEmptyState />
            )}
          </div>
        </section>
      </section>
    </main>
  );
}

function ScreenerFiltersPanel({
  filters,
  imports,
  resultCount,
  onChange,
  onApply,
  onReset,
}: {
  filters: ScreenerFiltersState;
  imports: ScreenerImport[];
  resultCount: number;
  onChange: (filters: ScreenerFiltersState) => void;
  onApply: (filters: ScreenerFiltersState) => void;
  onReset: () => void;
}) {
  return (
    <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-200">Filter und Sortierung</p>
          <p className="mt-1 text-xs text-slate-400">
            Filter veraendern keine Kandidaten und erzeugen keine Analyse, Signale oder Trades.
          </p>
        </div>
        <span className="text-sm text-slate-400">{resultCount} sichtbar</span>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <FilterSelect
          label="Asset"
          value={filters.asset_class}
          onChange={(asset_class) => onChange({ ...filters, asset_class: asset_class as ScreenerFiltersState["asset_class"] })}
          options={[["", "Alle"], ["stock", "Stock"], ["crypto", "Crypto"]]}
        />
        <FilterSelect
          label="Status"
          value={filters.status}
          onChange={(status) => onChange({ ...filters, status: status as ScreenerFiltersState["status"] })}
          options={[["", "Alle"], ["candidate", "Candidate"], ["watchlist_added", "Watchlist"], ["duplicate", "Duplicate"], ["rejected", "Rejected"], ["ignored", "Ignored"]]}
        />
        <FilterSelect
          label="Import"
          value={String(filters.screener_import_id)}
          onChange={(screener_import_id) => onChange({ ...filters, screener_import_id: screener_import_id ? Number(screener_import_id) : "" })}
          options={[["", "Alle Importe"], ...imports.map((item) => [String(item.id), item.screener_preset ?? item.file_name ?? `Import #${item.id}`] as [string, string])]}
        />
        <label className="grid gap-2 text-sm text-slate-300">
          Exchange
          <input
            value={filters.exchange}
            onChange={(event) => onChange({ ...filters, exchange: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            placeholder="NASDAQ, BINANCE"
          />
        </label>
        <NumberFilter label="Min Volume" value={filters.min_volume} onChange={(min_volume) => onChange({ ...filters, min_volume })} />
        <NumberFilter label="Min Rel Volume" value={filters.min_relative_volume} onChange={(min_relative_volume) => onChange({ ...filters, min_relative_volume })} />
        <NumberFilter label="Min RSI14" value={filters.min_rsi14} onChange={(min_rsi14) => onChange({ ...filters, min_rsi14 })} />
        <NumberFilter label="Max RSI14" value={filters.max_rsi14} onChange={(max_rsi14) => onChange({ ...filters, max_rsi14 })} />
        <FilterSelect
          label="Sortieren nach"
          value={filters.sort_by}
          onChange={(sort_by) => onChange({ ...filters, sort_by: sort_by as ScreenerResultSortBy })}
          options={[["created_at", "Importiert"], ["symbol", "Symbol"], ["status", "Status"], ["volume", "Volume"], ["relative_volume", "Rel Volume"], ["rsi14", "RSI14"], ["price", "Price"], ["rank", "Rank"]]}
        />
        <FilterSelect
          label="Richtung"
          value={filters.sort_direction}
          onChange={(sort_direction) => onChange({ ...filters, sort_direction: sort_direction as ScreenerResultSortDirection })}
          options={[["desc", "Absteigend"], ["asc", "Aufsteigend"]]}
        />
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <button type="button" onClick={() => onApply(filters)} className="rounded-xl bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-950">
          Anwenden
        </button>
        <button type="button" onClick={onReset} className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50">
          Zuruecksetzen
        </button>
      </div>
    </div>
  );
}

function FilterSelect({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: [string, string][] }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)} className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300">
        {options.map(([optionValue, labelText]) => <option key={optionValue} value={optionValue}>{labelText}</option>)}
      </select>
    </label>
  );
}

function NumberFilter({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <input type="number" min="0" step="any" value={value} onChange={(event) => onChange(event.target.value)} className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300" />
    </label>
  );
}

function ScreenerResultCard({
  result,
  isConverting,
  onAddToWatchlist,
}: {
  result: ScreenerResult;
  isConverting: boolean;
  onAddToWatchlist: (result: ScreenerResult) => void;
}) {
  const canAddToWatchlist = result.status === "candidate" || result.status === "duplicate";
  return (
    <article className="grid gap-5 p-5 lg:grid-cols-[1fr_0.9fr]">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[result.status]}`}>
            {formatLabel(result.status)}
          </span>
          <h3 className="text-lg font-semibold">{result.symbol}</h3>
          {result.exchange ? (
            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
              {result.exchange}
            </span>
          ) : null}
          <span className="text-sm text-slate-400">{result.asset_class}</span>
        </div>
        <p className="mt-3 text-sm text-slate-300">{result.name ?? "Kein Name im Screener-Export."}</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Price" value={formatNumber(result.price)} />
          <Metric label="Change %" value={formatPercent(result.change_percent)} />
          <Metric label="Volume" value={formatCompact(result.volume)} />
          <Metric label="Rel Volume" value={formatNumber(result.relative_volume)} />
        </div>
        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            type="button"
            disabled={!canAddToWatchlist || isConverting}
            onClick={() => onAddToWatchlist(result)}
            className="rounded-xl bg-sky-300 px-4 py-2 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isConverting ? "Fuege hinzu..." : "Zur Watchlist hinzufuegen"}
          </button>
          <span className="text-xs text-slate-500">
            Manuell: keine Analyse, kein Signal, kein Trade, kein Alert.
          </span>
        </div>
      </div>
      <aside className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
        <p className="text-sm font-medium text-slate-200">Review Kontext</p>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <Metric label="Sector" value={result.sector ?? "-"} />
          <Metric label="Industry" value={result.industry ?? "-"} />
          <Metric label="RSI14" value={formatNumber(result.rsi14)} />
          <Metric label="Market Cap" value={formatCompact(result.market_cap)} />
          <Metric label="EMA20" value={formatNumber(result.ema20)} />
          <Metric label="EMA50" value={formatNumber(result.ema50)} />
        </div>
        {asErrors(result.validation_errors).length > 0 ? (
          <InlineErrors errors={asErrors(result.validation_errors)} />
        ) : null}
        {result.watchlist_item_id ? (
          <p className="mt-4 rounded-xl border border-sky-300/20 bg-sky-300/10 p-3 text-sm text-sky-100">
            Verknuepfter Watchlist-Eintrag #{result.watchlist_item_id}
          </p>
        ) : null}
      </aside>
    </article>
  );
}

function ScreenerImportCard({ item }: { item: ScreenerImport }) {
  return (
    <article className="grid gap-4 p-5 lg:grid-cols-[1fr_auto] lg:items-center">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[item.status]}`}>
            {formatLabel(item.status)}
          </span>
          <h3 className="text-lg font-semibold">{item.screener_preset ?? item.file_name ?? `Import #${item.id}`}</h3>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
            {item.asset_class}
          </span>
        </div>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          <Metric label="Accepted" value={item.accepted_count.toString()} />
          <Metric label="Rejected" value={item.rejected_count.toString()} />
          <Metric label="Duplicate" value={item.duplicate_count.toString()} />
          <Metric label="Rows" value={item.row_count.toString()} />
          <Metric label="Importiert" value={formatDateTime(item.created_at)} />
        </div>
        {asErrors(item.validation_errors).length > 0 ? <InlineErrors errors={asErrors(item.validation_errors)} /> : null}
      </div>
      <p className="text-sm text-slate-500">#{item.id}</p>
    </article>
  );
}

function ErrorMessage({ message }: { message: ScreenerPageError }) {
  return (
    <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
      <p className="font-semibold">{message.summary}</p>
      {message.details.length > 0 ? <InlineErrors errors={message.details} /> : null}
    </div>
  );
}

function NoticeMessage({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-sky-300/30 bg-sky-950/40 p-4 text-sm text-sky-100">
      {message}
    </div>
  );
}

function InlineErrors({ errors }: { errors: ScreenerImportError[] }) {
  return (
    <div className="mt-4 overflow-hidden rounded-xl border border-yellow-300/20 text-sm text-yellow-50">
      <div className="grid grid-cols-[4.5rem_7rem_minmax(0,1fr)] gap-3 bg-yellow-300/10 px-3 py-2 text-xs font-semibold uppercase tracking-wide">
        <span>Zeile</span>
        <span>Feld</span>
        <span>Hinweis</span>
      </div>
      <div className="divide-y divide-yellow-300/10">
        {errors.map((error, index) => (
          <div key={`${error.row ?? "csv"}-${error.field ?? "field"}-${index}`} className="grid grid-cols-[4.5rem_7rem_minmax(0,1fr)] gap-3 px-3 py-2">
            <span>{error.row ?? "CSV"}</span>
            <span>{error.field ?? "-"}</span>
            <span className="min-w-0 break-words">{error.message}</span>
          </div>
        ))}
      </div>
    </div>
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

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function ResultsEmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch keine Screener-Kandidaten.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Lade einen TradingView Screener CSV-Snapshot hoch. Ergebnisse erscheinen hier als Review-Liste.
      </p>
    </div>
  );
}

function ImportEmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch kein Screener-Import ausgewaehlt.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Importiere eine CSV oder lade die Historie neu. Diese Ansicht bleibt read-only.
      </p>
    </div>
  );
}

function buildSummary(results: ScreenerResult[]) {
  return {
    candidate: results.filter((result) => result.status === "candidate").length,
    duplicate: results.filter((result) => result.status === "duplicate").length,
    watchlist: results.filter((result) => result.status === "watchlist_added").length,
  };
}

function toApiFilters(filters: ScreenerFiltersState): ScreenerResultFilters {
  return {
    asset_class: filters.asset_class,
    status: filters.status,
    exchange: filters.exchange.trim(),
    screener_import_id: filters.screener_import_id,
    min_volume: filters.min_volume,
    min_relative_volume: filters.min_relative_volume,
    min_rsi14: filters.min_rsi14,
    max_rsi14: filters.max_rsi14,
    sort_by: filters.sort_by,
    sort_direction: filters.sort_direction,
  };
}

function toSimpleError(error: unknown, fallback = "Unbekannter Fehler."): ScreenerPageError {
  return {
    summary: typeof error === "string" ? error : error instanceof Error ? error.message : fallback,
    details: [],
  };
}

function toImportError(error: unknown): ScreenerPageError {
  if (error instanceof ApiError && Array.isArray(error.detail)) {
    const details = error.detail.filter(isScreenerError);
    if (details.length > 0) {
      return { summary: "Screener CSV konnte nicht importiert werden.", details };
    }
  }
  return toSimpleError(error, "Screener CSV konnte nicht gespeichert werden.");
}

function asErrors(value: ScreenerImport["validation_errors"] | ScreenerResult["validation_errors"]) {
  return Array.isArray(value) ? value.filter(isScreenerError) : [];
}

function isScreenerError(value: unknown): value is ScreenerImportError {
  if (!value || typeof value !== "object") {
    return false;
  }
  const error = value as ScreenerImportError;
  return (
    (error.row === null || error.row === undefined || typeof error.row === "number") &&
    (error.field === null || error.field === undefined || typeof error.field === "string") &&
    typeof error.message === "string"
  );
}

function formatNumber(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(2) : value;
}

function formatPercent(value: string | null) {
  return value ? `${formatNumber(value)}%` : "-";
}

function formatCompact(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed)
    ? new Intl.NumberFormat("de-DE", { maximumFractionDigits: 2, notation: "compact" }).format(parsed)
    : value;
}

function formatDateTime(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString("de-DE");
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}
