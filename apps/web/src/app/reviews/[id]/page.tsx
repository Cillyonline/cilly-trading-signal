"use client";

import { useEffect, useMemo, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { fetchReviewBatch, redirectToLoginOnAuthError } from "@/lib/api";
import type { ManualReviewLabel, ReviewBatch, ReviewEntry } from "@/types/reviews";

const labelTone: Record<ManualReviewLabel, string> = {
  useful: "border-emerald-300/40 bg-emerald-300/10 text-emerald-100",
  too_permissive: "border-red-300/40 bg-red-300/10 text-red-100",
  too_strict: "border-orange-300/40 bg-orange-300/10 text-orange-100",
  unclear: "border-yellow-300/40 bg-yellow-300/10 text-yellow-100",
};

export default function ReviewBatchDetailPage({ params }: { params: { id: string } }) {
  const authStatus = useProtectedRoute();
  const [batch, setBatch] = useState<ReviewBatch | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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

  const entriesByLabel = useMemo(() => groupEntriesByLabel(batch?.entries ?? []), [batch]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
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
              <PatternPanel title="Repeated Follow-ups" items={[...batch.summary.repeated_attention_labels.map(formatLabel), ...batch.summary.repeated_blocker_patterns.map((pattern) => `blocker: ${formatLabel(pattern)}`)]} />
            </section>

            <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold">Review Entries</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Eine Zeile pro Signal oder Kandidat. Labels markieren Review-Qualitaet, nicht Profit.
                  </p>
                </div>
                <span className="text-sm text-slate-400">{batch.entries.length} Eintraege</span>
              </div>
              <div className="mt-5 overflow-hidden rounded-2xl border border-white/10">
                {batch.entries.length === 0 ? (
                  <p className="p-5 text-sm text-slate-500">Noch keine Eintraege.</p>
                ) : (
                  <div className="divide-y divide-white/10">
                    {batch.entries.map((entry) => <EntryRow key={entry.id} entry={entry} />)}
                  </div>
                )}
              </div>
            </section>

            {Object.entries(entriesByLabel).length > 0 ? (
              <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
                <h2 className="text-xl font-semibold">Entries nach Label</h2>
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

function EntryRow({ entry }: { entry: ReviewEntry }) {
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
      <span className={`w-fit rounded-full border px-3 py-1 text-xs ${labelTone[entry.manual_review_label]}`}>
        {formatLabel(entry.manual_review_label)}
      </span>
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

function Notice({ text }: { text: string }) {
  return <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">{text}</div>;
}

function groupEntriesByLabel(entries: ReviewEntry[]) {
  return entries.reduce<Record<string, ReviewEntry[]>>((groups, entry) => {
    groups[entry.manual_review_label] = [...(groups[entry.manual_review_label] ?? []), entry];
    return groups;
  }, {});
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
