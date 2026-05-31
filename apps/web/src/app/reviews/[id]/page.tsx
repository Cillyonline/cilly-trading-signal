"use client";

import { useEffect, useMemo, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { exportReviewBatchCsv, fetchReviewBatch, redirectToLoginOnAuthError } from "@/lib/api";
import type { ManualReviewLabel, ReviewBatch, ReviewEntry } from "@/types/reviews";
import type { AssetClass, StrategyType } from "@/types/signals";

type EntryFilterState = {
  label: "" | ManualReviewLabel;
  assetClass: "" | AssetClass;
  strategyType: "" | StrategyType;
  symbol: string;
  blocker: string;
  followUp: "" | "yes" | "no";
};

const emptyFilters: EntryFilterState = {
  label: "",
  assetClass: "",
  strategyType: "",
  symbol: "",
  blocker: "",
  followUp: "",
};

const labelTone: Record<ManualReviewLabel, string> = {
  useful: "border-emerald-300/40 bg-emerald-300/10 text-emerald-100",
  too_permissive: "border-red-300/40 bg-red-300/10 text-red-100",
  too_strict: "border-orange-300/40 bg-orange-300/10 text-orange-100",
  unclear: "border-yellow-300/40 bg-yellow-300/10 text-yellow-100",
};

export default function ReviewBatchDetailPage({ params }: { params: { id: string } }) {
  const authStatus = useProtectedRoute();
  const [batch, setBatch] = useState<ReviewBatch | null>(null);
  const [filters, setFilters] = useState<EntryFilterState>(emptyFilters);
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [draftText, setDraftText] = useState<string | null>(null);
  const [copyMessage, setCopyMessage] = useState<string | null>(null);
  const batchId = Number(params.id);

  async function loadBatch() {
    if (!Number.isInteger(batchId) || batchId <= 0) {
      setError("Ungueltige Review-Batch ID.");
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      setBatch(await fetchReviewBatch(batchId));
    } catch (loadError) {
      if (redirectToLoginOnAuthError(loadError)) {
        return;
      }
      setError(loadError instanceof Error ? loadError.message : "Review-Batch konnte nicht geladen werden.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (authStatus === "authenticated") {
      void loadBatch();
    }
  }, [authStatus, batchId]);

  const filteredEntries = useMemo(() => filterEntries(batch?.entries ?? [], filters), [batch, filters]);
  const entriesByLabel = useMemo(() => groupEntriesByLabel(filteredEntries), [filteredEntries]);
  const hasActiveFilters = Object.values(filters).some(Boolean);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function handleExport() {
    setIsExporting(true);
    setError(null);
    try {
      await exportReviewBatchCsv(batchId);
    } catch (exportError) {
      if (redirectToLoginOnAuthError(exportError)) {
        return;
      }
      setError(exportError instanceof Error ? exportError.message : "Review-Batch Export fehlgeschlagen.");
    } finally {
      setIsExporting(false);
    }
  }

  async function handleCopyDraft() {
    if (!draftText) {
      return;
    }
    try {
      await navigator.clipboard.writeText(draftText);
      setCopyMessage("Draft wurde in die Zwischenablage kopiert.");
    } catch {
      setCopyMessage("Kopieren nicht moeglich. Draft kann manuell markiert werden.");
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#312e81,transparent_34%),#020617] px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-white/[0.05] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-violet-300">Review Batch</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">
                {batch?.name ?? `Batch #${params.id}`}
              </h1>
              <p className="mt-3 max-w-3xl text-slate-300">
                Batch-Details sind Prozess-Evidence fuer Kalibrierung. Kein Backtest, keine
                Profitabilitaetsvalidierung, keine Trading Advice und keine Ausfuehrung.
              </p>
            </div>
            <div className="flex flex-wrap gap-4 text-sm">
              <button
                className="rounded-xl bg-violet-300 px-4 py-2 font-semibold text-slate-950 hover:bg-violet-200 disabled:opacity-60"
                disabled={!batch || isExporting}
                onClick={() => void handleExport()}
                type="button"
              >
                {isExporting ? "Export laeuft..." : "CSV exportieren"}
              </button>
              <a className="text-violet-300 hover:text-violet-200" href="/reviews">
                Review Batches
              </a>
              <a className="text-violet-300 hover:text-violet-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {error ? <Notice text={error} /> : null}
        {isLoading ? <p className="text-sm text-slate-400">Review-Batch wird geladen...</p> : null}

        {batch ? (
          <>
            <section className="grid gap-4 md:grid-cols-4">
              <SummaryCard label="Reviewed" value={String(batch.summary.reviewed_count)} />
              <SummaryCard label="Follow-ups" value={String(batch.summary.follow_up_needed_count)} tone="border-orange-300/40" />
              <SummaryCard label="Repeated Labels" value={String(batch.summary.repeated_attention_labels.length)} tone="border-yellow-300/40" />
              <SummaryCard label="Repeated Blockers" value={String(batch.summary.repeated_blocker_patterns.length)} tone="border-red-300/40" />
            </section>

            <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
              <h2 className="text-xl font-semibold">Batch Kontext</h2>
              <p className="mt-2 rounded-2xl border border-yellow-300/20 bg-yellow-300/10 p-4 text-sm text-yellow-50">
                {batch.summary.evidence_only_notice}
              </p>
              <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                <InfoCard label="Typ" value={batch.review_type} />
                <InfoCard label="Asset" value={batch.asset_class ?? "mixed"} />
                <InfoCard label="Strategie" value={formatLabel(batch.strategy_type ?? "mixed")} />
                <InfoCard label="Datenquelle" value={batch.data_source ?? "nicht erfasst"} />
                <InfoCard label="Fenster Start" value={batch.review_window_start ?? "-"} />
                <InfoCard label="Fenster Ende" value={batch.review_window_end ?? "-"} />
                <InfoCard label="Erstellt" value={formatDateTime(batch.created_at)} />
                <InfoCard label="Aktualisiert" value={formatDateTime(batch.updated_at)} />
              </div>
              {batch.context_notes ? <p className="mt-4 text-sm text-slate-300">{batch.context_notes}</p> : null}
            </section>

            <section className="grid gap-4 md:grid-cols-2">
              <PatternPanel title="Label Counts" items={Object.entries(batch.summary.label_counts).map(([label, count]) => `${formatLabel(label)}: ${count}`)} />
              <RepeatedFindingPanel batch={batch} />
            </section>

            <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold">Review Entries</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Eine Zeile pro Signal oder Kandidat. Labels markieren Review-Qualitaet, nicht Profit.
                  </p>
                </div>
                <span className="text-sm text-slate-400">
                  {filteredEntries.length} sichtbar / {batch.entries.length} gesamt
                </span>
              </div>
              <EntryFilters filters={filters} onChange={setFilters} onReset={() => setFilters(emptyFilters)} />
              <div className="mt-5 overflow-hidden rounded-2xl border border-white/10">
                {batch.entries.length === 0 ? (
                  <p className="p-5 text-sm text-slate-500">Noch keine Eintraege.</p>
                ) : filteredEntries.length === 0 ? (
                  <p className="p-5 text-sm text-slate-500">
                    Keine Eintraege passen zu den aktiven Filtern. Repeated Blockers bleiben oben als Batch-Kontext sichtbar.
                  </p>
                ) : (
                  <div className="divide-y divide-white/10">
                    {filteredEntries.map((entry) => (
                      <EntryRow
                        key={entry.id}
                        batch={batch}
                        entry={entry}
                        onDraft={() => {
                          setDraftText(buildFollowUpDraft(batch, entry));
                          setCopyMessage(null);
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>
            </section>

            {draftText ? (
              <section className="rounded-3xl border border-violet-300/30 bg-violet-300/10 p-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-violet-50">Calibration Follow-up Draft</h2>
                    <p className="mt-2 text-sm text-violet-100/80">
                      Lokaler Markdown-Draft fuer ein manuelles Issue. Pruefe private Notizen vor dem Einfuegen;
                      es wird nichts automatisch hochgeladen oder an Regeln geaendert.
                    </p>
                  </div>
                  <button className="w-fit rounded-xl bg-violet-200 px-4 py-2 text-sm font-semibold text-slate-950" type="button" onClick={() => void handleCopyDraft()}>
                    Draft kopieren
                  </button>
                </div>
                {copyMessage ? <p className="mt-3 text-sm text-violet-100">{copyMessage}</p> : null}
                <textarea className="mt-4 h-96 w-full rounded-2xl border border-white/10 bg-slate-950 p-4 font-mono text-xs text-slate-100" readOnly value={draftText} />
              </section>
            ) : null}

            {Object.entries(entriesByLabel).length > 0 ? (
              <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                <h2 className="text-xl font-semibold">Entries nach Label{hasActiveFilters ? " (gefiltert)" : ""}</h2>
                <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  {Object.entries(entriesByLabel).map(([label, entries]) => (
                    <SummaryCard key={label} label={formatLabel(label)} value={String(entries.length)} tone={labelTone[label as ManualReviewLabel] ?? "border-white/10"} />
                  ))}
                </div>
              </section>
            ) : null}
          </>
        ) : null}
      </section>
    </main>
  );
}

function EntryFilters({
  filters,
  onChange,
  onReset,
}: {
  filters: EntryFilterState;
  onChange: (filters: EntryFilterState) => void;
  onReset: () => void;
}) {
  return (
    <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/50 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="font-semibold">Entry Filter</h3>
          <p className="mt-1 text-xs text-slate-500">Filter dienen nur der Review-Suche, nicht der Signalbewertung.</p>
        </div>
        <button className="w-fit rounded-xl border border-white/10 px-3 py-2 text-xs text-slate-300 hover:border-violet-300/60" type="button" onClick={onReset}>
          Filter zuruecksetzen
        </button>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-6">
        <SelectInput label="Label" value={filters.label} onChange={(label) => onChange({ ...filters, label: label as EntryFilterState["label"] })} options={[["", "Alle"], ["useful", "Useful"], ["too_permissive", "Too permissive"], ["too_strict", "Too strict"], ["unclear", "Unclear"]]} />
        <SelectInput label="Asset" value={filters.assetClass} onChange={(assetClass) => onChange({ ...filters, assetClass: assetClass as EntryFilterState["assetClass"] })} options={[["", "Alle"], ["stock", "Stock"], ["crypto", "Crypto"]]} />
        <SelectInput label="Strategie" value={filters.strategyType} onChange={(strategyType) => onChange({ ...filters, strategyType: strategyType as EntryFilterState["strategyType"] })} options={[["", "Alle"], ["trend_pullback_long", "Trend Pullback"], ["base_breakout_long", "Base Breakout"]]} />
        <TextInput label="Symbol" value={filters.symbol} onChange={(symbol) => onChange({ ...filters, symbol })} placeholder="AAPL" />
        <TextInput label="Blocker" value={filters.blocker} onChange={(blocker) => onChange({ ...filters, blocker })} placeholder="market_regime" />
        <SelectInput label="Follow-up" value={filters.followUp} onChange={(followUp) => onChange({ ...filters, followUp: followUp as EntryFilterState["followUp"] })} options={[["", "Alle"], ["yes", "Ja"], ["no", "Nein"]]} />
      </div>
    </div>
  );
}

function EntryRow({ batch, entry, onDraft }: { batch: ReviewBatch; entry: ReviewEntry; onDraft: () => void }) {
  const isAttentionFinding = entry.manual_review_label !== "useful" || entry.follow_up_needed;
  return (
    <article className="grid gap-3 p-4 text-sm lg:grid-cols-[1fr_auto_auto] lg:items-center">
      <div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-semibold text-slate-100">{entry.symbol}</span>
          <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{entry.asset_class}</span>
          <span className="text-slate-400">{formatLabel(entry.strategy_type)}</span>
        </div>
        <p className="mt-2 text-slate-500">{entry.notes ?? "Keine Notes."}</p>
      </div>
      <span className="text-slate-400">{formatLabel(entry.signal_status)} / {formatLabel(entry.score_class ?? "no score")}</span>
      <div className="flex flex-wrap items-center gap-2">
        <span className={`w-fit rounded-full border px-3 py-1 text-xs ${labelTone[entry.manual_review_label]}`}>
          {formatLabel(entry.manual_review_label)}
        </span>
        <button
          className="rounded-full border border-violet-300/30 px-3 py-1 text-xs text-violet-100 hover:border-violet-200 disabled:cursor-not-allowed disabled:opacity-40"
          disabled={!isAttentionFinding}
          onClick={onDraft}
          title={isAttentionFinding ? "Markdown-Draft fuer Follow-up erzeugen" : "Nur fuer Attention-Findings noetig"}
          type="button"
        >
          Draft
        </button>
      </div>
    </article>
  );
}

function SummaryCard({ label, value, tone = "border-white/10" }: { label: string; value: string; tone?: string }) {
  return (
    <article className={`rounded-2xl border ${tone} bg-white/[0.04] p-5`}>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </article>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-2 text-sm font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function PatternPanel({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h2 className="text-xl font-semibold">{title}</h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">Keine wiederholten Muster.</p>
      ) : (
        <div className="mt-4 flex flex-wrap gap-2">
          {items.map((item) => (
            <span key={item} className="rounded-full border border-white/10 px-3 py-1 text-xs text-slate-300">
              {item}
            </span>
          ))}
        </div>
      )}
    </section>
  );
}

function RepeatedFindingPanel({ batch }: { batch: ReviewBatch }) {
  const items = [
    ...batch.summary.repeated_attention_labels.map((label) => `label >=2: ${formatLabel(label)}`),
    ...batch.summary.repeated_blocker_patterns.map((pattern) => `blocker >=2: ${formatLabel(pattern)}`),
  ];
  return (
    <section className="rounded-3xl border border-yellow-300/30 bg-yellow-300/10 p-6">
      <h2 className="text-xl font-semibold text-yellow-50">Repeated Finding Summary</h2>
      <p className="mt-2 text-sm text-yellow-100/80">
        Schwelle: mindestens 2 gleiche Attention-Labels oder Blocker. Das ist Follow-up Evidence only,
        keine automatische Regelanpassung und keine Performance-Aussage.
      </p>
      {items.length === 0 ? (
        <p className="mt-4 text-sm text-yellow-100/70">Noch keine wiederholten Findings ueber der Schwelle.</p>
      ) : (
        <div className="mt-4 flex flex-wrap gap-2">
          {items.map((item) => (
            <span key={item} className="rounded-full border border-yellow-200/30 px-3 py-1 text-xs text-yellow-50">
              {item}
            </span>
          ))}
        </div>
      )}
    </section>
  );
}

function SelectInput({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: [string, string][];
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <select className="rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-slate-100" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map(([optionValue, optionLabel]) => <option key={optionValue} value={optionValue}>{optionLabel}</option>)}
      </select>
    </label>
  );
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <input className="rounded-xl border border-white/10 bg-slate-950 px-3 py-2 text-slate-100" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />
    </label>
  );
}

function Notice({ text }: { text: string }) {
  return <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">{text}</div>;
}

function groupEntriesByLabel(entries: ReviewEntry[]) {
  return entries.reduce<Record<string, ReviewEntry[]>>((groups, entry) => {
    groups[entry.manual_review_label] = [...(groups[entry.manual_review_label] ?? []), entry];
    return groups;
  }, {});
}

function filterEntries(entries: ReviewEntry[], filters: EntryFilterState) {
  const symbol = filters.symbol.trim().toUpperCase();
  const blocker = filters.blocker.trim().toLowerCase();
  return entries.filter((entry) => {
    if (filters.label && entry.manual_review_label !== filters.label) {
      return false;
    }
    if (filters.assetClass && entry.asset_class !== filters.assetClass) {
      return false;
    }
    if (filters.strategyType && entry.strategy_type !== filters.strategyType) {
      return false;
    }
    if (symbol && !entry.symbol.toUpperCase().includes(symbol)) {
      return false;
    }
    if (filters.followUp === "yes" && !entry.follow_up_needed) {
      return false;
    }
    if (filters.followUp === "no" && entry.follow_up_needed) {
      return false;
    }
    if (blocker && !extractTextValues(entry.quality_blockers).some((value) => value.toLowerCase().includes(blocker))) {
      return false;
    }
    return true;
  });
}

function extractTextValues(value: unknown): string[] {
  if (!value) {
    return [];
  }
  if (Array.isArray(value)) {
    return value.flatMap(extractTextValues);
  }
  if (typeof value === "object") {
    return Object.values(value).flatMap((item) => (typeof item === "string" ? [item] : []));
  }
  return [];
}

function buildFollowUpDraft(batch: ReviewBatch, entry: ReviewEntry) {
  const blockers = extractTextValues(entry.quality_blockers);
  return [
    `## Calibration Follow-up: ${entry.symbol} ${formatLabel(entry.manual_review_label)}`,
    "",
    "## Source Evidence",
    `- Review batch: ${batch.name} (#${batch.id}, ${batch.review_type})`,
    `- Entry: #${entry.id}`,
    `- Symbol: ${entry.symbol}`,
    `- Asset class: ${entry.asset_class}`,
    `- Strategy: ${formatLabel(entry.strategy_type)}`,
    `- Signal status: ${formatLabel(entry.signal_status)}`,
    `- Score class: ${formatLabel(entry.score_class ?? "no score")}`,
    `- Manual review label: ${formatLabel(entry.manual_review_label)}`,
    `- Follow-up needed: ${entry.follow_up_needed ? "yes" : "no"}`,
    `- Quality blockers: ${blockers.length > 0 ? blockers.join(", ") : "none recorded"}`,
    "",
    "## Expected Behavior",
    "Describe the conservative, explainable behavior expected from the strategy or review workflow.",
    "",
    "## Actual Output / Observed Issue",
    entry.notes ? sanitizeDraftText(entry.notes) : "Describe the observed output using sanitized notes only.",
    "",
    "## Evidence Boundary Check",
    "- This draft is process evidence only, not a backtest or profitability validation.",
    "- No automatic strategy or rule change is requested by this draft alone.",
    "- No trading advice, broker action, or order execution is implied.",
    "- Notes have been reviewed for private account data before filing.",
    "",
    "## Suggested Follow-up",
    "Manual review required: decide whether documentation, fixture coverage, or calibration discussion is needed.",
  ].join("\n");
}

function sanitizeDraftText(value: string) {
  return value.replace(/[\r\n]+/g, " ").trim();
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
