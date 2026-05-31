"use client";

import { useEffect, useMemo, useState } from "react";

import { AuthenticatedHeaderActions } from "@/components/authenticated-header-actions";
import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { createReviewBatch, createReviewEntry, fetchReviewBatches, redirectToLoginOnAuthError } from "@/lib/api";
import type {
  ManualReviewLabel,
  ReviewBatch,
  ReviewBatchCreatePayload,
  ReviewBatchType,
  ReviewEntryCreatePayload,
} from "@/types/reviews";
import type { AssetClass, ScoreClass, SignalStatus, StrategyType } from "@/types/signals";

type BatchFormState = {
  name: string;
  review_type: ReviewBatchType;
  asset_class: "" | AssetClass;
  strategy_type: "" | StrategyType;
  review_window_start: string;
  review_window_end: string;
  data_source: string;
  context_notes: string;
};

type EntryFormState = {
  batch_id: string;
  signal_id: string;
  symbol: string;
  asset_class: AssetClass;
  strategy_type: StrategyType;
  signal_status: SignalStatus;
  score_class: "" | ScoreClass;
  benchmark_context: string;
  manual_review_label: ManualReviewLabel;
  quality_blockers: string;
  outcome_r: string;
  outcome_measurement_rule: string;
  follow_up_issue_url: string;
  notes: string;
};

const emptyBatchForm: BatchFormState = {
  name: "",
  review_type: "historical",
  asset_class: "",
  strategy_type: "",
  review_window_start: "",
  review_window_end: "",
  data_source: "",
  context_notes: "",
};

const emptyEntryForm: EntryFormState = {
  batch_id: "",
  signal_id: "",
  symbol: "",
  asset_class: "stock",
  strategy_type: "trend_pullback_long",
  signal_status: "watchlist",
  score_class: "",
  benchmark_context: "present",
  manual_review_label: "useful",
  quality_blockers: "",
  outcome_r: "",
  outcome_measurement_rule: "",
  follow_up_issue_url: "",
  notes: "",
};

const labelTone: Record<ManualReviewLabel, string> = {
  useful: "border-emerald-300/40 bg-emerald-300/10 text-emerald-100",
  too_permissive: "border-red-300/40 bg-red-300/10 text-red-100",
  too_strict: "border-orange-300/40 bg-orange-300/10 text-orange-100",
  unclear: "border-yellow-300/40 bg-yellow-300/10 text-yellow-100",
};

export default function ReviewsPage() {
  const authStatus = useProtectedRoute();
  const [batches, setBatches] = useState<ReviewBatch[]>([]);
  const [batchForm, setBatchForm] = useState<BatchFormState>(emptyBatchForm);
  const [entryForm, setEntryForm] = useState<EntryFormState>(emptyEntryForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function loadBatches() {
    setIsLoading(true);
    setError(null);
    try {
      const loaded = await fetchReviewBatches();
      setBatches(loaded);
      setEntryForm((current) => ({ ...current, batch_id: current.batch_id || String(loaded[0]?.id ?? "") }));
    } catch (loadError) {
      if (redirectToLoginOnAuthError(loadError)) {
        return;
      }
      setError(loadError instanceof Error ? loadError.message : "Review-Batches konnten nicht geladen werden.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (authStatus === "authenticated") {
      void loadBatches();
    }
  }, [authStatus]);

  const summary = useMemo(() => buildPageSummary(batches), [batches]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function handleCreateBatch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    setMessage(null);
    try {
      const payload: ReviewBatchCreatePayload = {
        name: batchForm.name.trim(),
        review_type: batchForm.review_type,
        asset_class: batchForm.asset_class || null,
        strategy_type: batchForm.strategy_type || null,
        review_window_start: batchForm.review_window_start || null,
        review_window_end: batchForm.review_window_end || null,
        data_source: batchForm.data_source.trim() || null,
        context_notes: batchForm.context_notes.trim() || null,
      };
      const created = await createReviewBatch(payload);
      setBatchForm(emptyBatchForm);
      setEntryForm((current) => ({ ...current, batch_id: String(created.id) }));
      await loadBatches();
      setMessage("Review-Batch gespeichert. Evidence-only: keine Backtest- oder Profitabilitaetsaussage.");
    } catch (saveError) {
      if (redirectToLoginOnAuthError(saveError)) {
        return;
      }
      setError(saveError instanceof Error ? saveError.message : "Review-Batch konnte nicht gespeichert werden.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleCreateEntry(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!entryForm.batch_id) {
      setError("Bitte zuerst einen Review-Batch auswaehlen oder anlegen.");
      return;
    }
    setIsSaving(true);
    setError(null);
    setMessage(null);
    try {
      const payload: ReviewEntryCreatePayload = {
        signal_id: entryForm.signal_id ? Number(entryForm.signal_id) : null,
        symbol: entryForm.symbol.trim(),
        asset_class: entryForm.asset_class,
        strategy_type: entryForm.strategy_type,
        signal_status: entryForm.signal_status,
        score_class: entryForm.score_class || null,
        benchmark_context: entryForm.benchmark_context.trim() || null,
        manual_review_label: entryForm.manual_review_label,
        quality_blockers: splitList(entryForm.quality_blockers),
        outcome_r: entryForm.outcome_r || null,
        outcome_measurement_rule: entryForm.outcome_measurement_rule.trim() || null,
        follow_up_needed: entryForm.manual_review_label !== "useful" || Boolean(entryForm.follow_up_issue_url),
        follow_up_issue_url: entryForm.follow_up_issue_url.trim() || null,
        notes: entryForm.notes.trim() || null,
      };
      await createReviewEntry(Number(entryForm.batch_id), payload);
      setEntryForm({ ...emptyEntryForm, batch_id: entryForm.batch_id });
      await loadBatches();
      setMessage("Review-Eintrag gespeichert. Wiederholte Labels werden im Batch sichtbar gemacht.");
    } catch (saveError) {
      if (redirectToLoginOnAuthError(saveError)) {
        return;
      }
      setError(saveError instanceof Error ? saveError.message : "Review-Eintrag konnte nicht gespeichert werden.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#312e81,transparent_34%),#020617] px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-white/[0.05] p-5 sm:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-violet-300 sm:tracking-[0.35em]">Historical / Paper Review</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Review-Batches erfassen</h1>
              <p className="mt-3 max-w-3xl text-slate-300">
                Strukturierte Evidence fuer Kalibrierung: Label, Blocker, optionale R-Notiz und Follow-up Issue.
                Kein Backtest, keine Profitabilitaetsvalidierung, keine Trading Advice und keine Ausfuehrung.
              </p>
            </div>
            <AuthenticatedHeaderActions tone="violet" />
          </div>
        </header>

        <section className="rounded-3xl border border-violet-300/20 bg-violet-300/10 p-4 text-sm text-violet-50 sm:hidden">
          <p className="font-semibold">Mobile Review Flow</p>
          <p className="mt-2 text-violet-100/80">
            1. Batch waehlen, 2. Signal identifizieren, 3. Review Label und Blocker erfassen,
            4. optional Outcome/Folgeissue dokumentieren. Evidence only, keine Regel- oder Trade-Aktion.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-4">
          <SummaryCard label="Batches" value={String(batches.length)} />
          <SummaryCard label="Reviewed" value={String(summary.reviewedCount)} tone="border-violet-300/40" />
          <SummaryCard label="Follow-ups" value={String(summary.followUps)} tone="border-orange-300/40" />
          <SummaryCard label="Repeated Patterns" value={String(summary.repeatedPatterns)} tone="border-yellow-300/40" />
        </section>

        {error ? <Notice tone="red" text={error} /> : null}
        {message ? <Notice tone="emerald" text={message} /> : null}

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <form onSubmit={handleCreateBatch} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Batch anlegen</h2>
            <p className="mt-1 text-sm text-slate-400">Fixiere Review-Fenster und Datenkontext vor der Auswertung.</p>
            <div className="mt-5 grid gap-4">
              <FormSection
                eyebrow="1"
                title="Batch Identity"
                description="Pflicht: Name und Review-Typ. Lege den Kontext fest, bevor einzelne Signale bewertet werden."
              >
                <TextInput label="Name" value={batchForm.name} onChange={(name) => setBatchForm({ ...batchForm, name })} required />
                <SelectInput
                  label="Typ"
                  value={batchForm.review_type}
                  onChange={(review_type) => setBatchForm({ ...batchForm, review_type: review_type as ReviewBatchType })}
                  options={[["historical", "Historical"], ["paper", "Paper"]]}
                />
              </FormSection>
              <FormSection
                eyebrow="2"
                title="Review Scope"
                description="Optionaler Filterkontext fuer spaetere Auswertung. Keine automatische Strategieaenderung."
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <SelectInput
                    label="Asset Class"
                    value={batchForm.asset_class}
                    onChange={(asset_class) => setBatchForm({ ...batchForm, asset_class: asset_class as BatchFormState["asset_class"] })}
                    options={[["", "Alle"], ["stock", "Stock"], ["crypto", "Crypto"]]}
                  />
                  <SelectInput
                    label="Strategie"
                    value={batchForm.strategy_type}
                    onChange={(strategy_type) => setBatchForm({ ...batchForm, strategy_type: strategy_type as BatchFormState["strategy_type"] })}
                    options={[["", "Alle"], ["trend_pullback_long", "Trend Pullback"], ["base_breakout_long", "Base Breakout"]]}
                  />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <TextInput label="Fenster Start" type="date" value={batchForm.review_window_start} onChange={(review_window_start) => setBatchForm({ ...batchForm, review_window_start })} />
                  <TextInput label="Fenster Ende" type="date" value={batchForm.review_window_end} onChange={(review_window_end) => setBatchForm({ ...batchForm, review_window_end })} />
                </div>
                <TextInput label="Datenquelle" value={batchForm.data_source} onChange={(data_source) => setBatchForm({ ...batchForm, data_source })} placeholder="stored csv, provider-sync..." />
                <TextArea label="Kontextnotizen" value={batchForm.context_notes} onChange={(context_notes) => setBatchForm({ ...batchForm, context_notes })} />
              </FormSection>
            </div>
            <button disabled={isSaving} className="mt-5 rounded-xl bg-violet-300 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60" type="submit">
              Batch speichern
            </button>
          </form>

          <form onSubmit={handleCreateEntry} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <h2 className="text-xl font-semibold">Review-Eintrag</h2>
            <p className="mt-1 text-sm text-slate-400">Eine Zeile pro Signal oder Kandidat. Freitext nur sanitisiert erfassen.</p>
            <p className="mt-3 rounded-2xl border border-yellow-300/20 bg-yellow-300/10 p-3 text-xs text-yellow-50">
              Pflichtfelder: Batch, Symbol, Asset, Strategie, Signal Status und Review Label. Outcome-R ist optional und bleibt Prozess-Evidence, keine Profitabilitaetsaussage.
            </p>
            <div className="mt-5 grid gap-4">
              <FormSection eyebrow="1" title="Signal Identity" description="Pflicht: Batch und Symbol. Signal ID ist optional, wenn der Review-Kandidat nicht aus einer gespeicherten Signal-ID stammt.">
                <SelectInput
                  label="Batch"
                  value={entryForm.batch_id}
                  onChange={(batch_id) => setEntryForm({ ...entryForm, batch_id })}
                  options={[["", "Batch auswaehlen"], ...batches.map((batch) => [String(batch.id), batch.name] as [string, string])]}
                />
                <div className="grid gap-4 sm:grid-cols-2">
                  <TextInput label="Symbol" value={entryForm.symbol} onChange={(symbol) => setEntryForm({ ...entryForm, symbol })} required />
                  <TextInput label="Signal ID optional" type="number" value={entryForm.signal_id} onChange={(signal_id) => setEntryForm({ ...entryForm, signal_id })} />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <SelectInput label="Asset" value={entryForm.asset_class} onChange={(asset_class) => setEntryForm({ ...entryForm, asset_class: asset_class as AssetClass })} options={[["stock", "Stock"], ["crypto", "Crypto"]]} />
                  <SelectInput label="Strategie" value={entryForm.strategy_type} onChange={(strategy_type) => setEntryForm({ ...entryForm, strategy_type: strategy_type as StrategyType })} options={[["trend_pullback_long", "Trend Pullback"], ["base_breakout_long", "Base Breakout"]]} />
                </div>
              </FormSection>
              <FormSection eyebrow="2" title="Review Decision" description="Pflicht: Status und Label. No Setup / No Trade bleiben gueltige Review-Ergebnisse.">
                <div className="grid gap-4 sm:grid-cols-3">
                  <SelectInput label="Signal Status" value={entryForm.signal_status} onChange={(signal_status) => setEntryForm({ ...entryForm, signal_status: signal_status as SignalStatus })} options={[["armed", "Armed"], ["watchlist", "Watchlist"], ["no_setup", "No Setup"], ["invalidated", "Invalidated"], ["missed", "Missed"], ["expired", "Expired"], ["triggered", "Triggered"]]} />
                  <SelectInput label="Score Class" value={entryForm.score_class} onChange={(score_class) => setEntryForm({ ...entryForm, score_class: score_class as EntryFormState["score_class"] })} options={[["", "Keine"], ["a_setup", "A Setup"], ["b_setup", "B Setup"], ["watchlist", "Watchlist"], ["no_trade", "No Trade"]]} />
                  <SelectInput label="Review Label" value={entryForm.manual_review_label} onChange={(manual_review_label) => setEntryForm({ ...entryForm, manual_review_label: manual_review_label as ManualReviewLabel })} options={[["useful", "Useful"], ["too_permissive", "Too permissive"], ["too_strict", "Too strict"], ["unclear", "Unclear"]]} />
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  <TextInput label="Benchmark Context" value={entryForm.benchmark_context} onChange={(benchmark_context) => setEntryForm({ ...entryForm, benchmark_context })} placeholder="present, missing, stale, mixed, bearish" />
                  <TextInput label="Quality Blockers" value={entryForm.quality_blockers} onChange={(quality_blockers) => setEntryForm({ ...entryForm, quality_blockers })} placeholder="market_regime, risk_plan..." />
                </div>
              </FormSection>
              <FormSection eyebrow="3" title="Evidence And Follow-up" description="Optional. Sanitized notes only; no private trading journal text or profitability claim.">
                <div className="grid gap-4 sm:grid-cols-2">
                  <TextInput label="Outcome R optional" value={entryForm.outcome_r} onChange={(outcome_r) => setEntryForm({ ...entryForm, outcome_r })} placeholder="1.25" />
                  <TextInput label="Follow-up Issue URL" value={entryForm.follow_up_issue_url} onChange={(follow_up_issue_url) => setEntryForm({ ...entryForm, follow_up_issue_url })} />
                </div>
                <TextArea label="Outcome Measurement Rule" value={entryForm.outcome_measurement_rule} onChange={(outcome_measurement_rule) => setEntryForm({ ...entryForm, outcome_measurement_rule })} />
                <TextArea label="Sanitized Notes" value={entryForm.notes} onChange={(notes) => setEntryForm({ ...entryForm, notes })} />
              </FormSection>
            </div>
            <button disabled={isSaving || batches.length === 0} className="mt-5 rounded-xl bg-violet-300 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60" type="submit">
              Eintrag speichern
            </button>
          </form>
        </section>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Gespeicherte Batches</h2>
              <p className="mt-1 text-sm text-slate-400">Repeated Labels und Blocker markieren Kalibrierungs-Follow-ups.</p>
            </div>
            <button type="button" onClick={() => void loadBatches()} className="rounded-xl border border-white/10 px-4 py-2 text-sm hover:border-violet-300/60">
              Aktualisieren
            </button>
          </div>
          {isLoading ? (
            <p className="mt-5 text-sm text-slate-400">Review-Batches werden geladen...</p>
          ) : batches.length === 0 ? (
            <p className="mt-5 rounded-2xl border border-white/10 p-5 text-sm text-slate-400">Noch keine Batches. Lege zuerst ein fixes Review-Fenster an.</p>
          ) : (
            <div className="mt-5 grid gap-4">
              {batches.map((batch) => <BatchCard key={batch.id} batch={batch} />)}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function BatchCard({ batch }: { batch: ReviewBatch }) {
  return (
    <article className="rounded-2xl border border-white/10 bg-slate-950/70 p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-violet-300">{batch.review_type}</p>
          <h3 className="mt-2 text-lg font-semibold">{batch.name}</h3>
          <p className="mt-1 text-sm text-slate-400">{batch.summary.evidence_only_notice}</p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-sm">
          <MiniStat label="Reviewed" value={String(batch.summary.reviewed_count)} />
          <MiniStat label="Follow-ups" value={String(batch.summary.follow_up_needed_count)} />
          <MiniStat label="Repeated" value={String(batch.summary.repeated_attention_labels.length)} />
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {Object.entries(batch.summary.label_counts).map(([label, count]) => (
          <span key={label} className={`rounded-full border px-3 py-1 text-xs ${labelTone[label as ManualReviewLabel] ?? "border-slate-400/30 bg-slate-400/10"}`}>
            {label.replaceAll("_", " ")}: {count}
          </span>
        ))}
        {batch.summary.repeated_blocker_patterns.map((pattern) => (
          <span key={pattern} className="rounded-full border border-yellow-300/40 bg-yellow-300/10 px-3 py-1 text-xs text-yellow-100">
            repeated blocker &gt;=2: {pattern}
          </span>
        ))}
      </div>
      {(batch.summary.repeated_attention_labels.length > 0 || batch.summary.repeated_blocker_patterns.length > 0) ? (
        <div className="mt-4 rounded-2xl border border-yellow-300/30 bg-yellow-300/10 p-4 text-sm text-yellow-50">
          <p className="font-semibold">Repeated Finding Summary</p>
          <p className="mt-1 text-yellow-100/80">
            Schwelle: mindestens 2 gleiche Attention-Labels oder Blocker. Follow-up Evidence only; keine automatische Regelanpassung.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {batch.summary.repeated_attention_labels.map((label) => (
              <span key={label} className="rounded-full border border-yellow-200/30 px-3 py-1 text-xs">
                repeated label &gt;=2: {label.replaceAll("_", " ")}
              </span>
            ))}
            {batch.summary.repeated_blocker_patterns.map((pattern) => (
              <span key={pattern} className="rounded-full border border-yellow-200/30 px-3 py-1 text-xs">
                repeated blocker &gt;=2: {pattern}
              </span>
            ))}
          </div>
        </div>
      ) : null}
      <div className="mt-4 divide-y divide-white/10 rounded-xl border border-white/10">
        {batch.entries.slice(0, 5).map((entry) => (
          <div key={entry.id} className="grid gap-2 p-3 text-sm md:grid-cols-[1fr_auto_auto] md:items-center">
            <span className="font-medium text-slate-100">{entry.symbol} / {entry.strategy_type.replaceAll("_", " ")}</span>
            <span className="text-slate-400">{entry.signal_status} / {entry.score_class ?? "no score"}</span>
            <span className={`w-fit rounded-full border px-3 py-1 text-xs ${labelTone[entry.manual_review_label]}`}>{entry.manual_review_label.replaceAll("_", " ")}</span>
          </div>
        ))}
        {batch.entries.length === 0 ? <p className="p-3 text-sm text-slate-500">Noch keine Eintraege.</p> : null}
      </div>
      <a
        href={`/reviews/${batch.id}`}
        className="mt-4 inline-flex rounded-xl border border-white/10 px-4 py-2 text-sm text-violet-100 hover:border-violet-300/60"
      >
        Batch Details oeffnen
      </a>
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

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="font-semibold">{value}</p>
    </div>
  );
}

function Notice({ tone, text }: { tone: "red" | "emerald"; text: string }) {
  const classes = tone === "red" ? "border-red-400/30 bg-red-950/40 text-red-100" : "border-emerald-400/30 bg-emerald-950/40 text-emerald-100";
  return <div className={`rounded-2xl border p-4 text-sm ${classes}`}>{text}</div>;
}

function FormSection({
  children,
  description,
  eyebrow,
  title,
}: {
  children: React.ReactNode;
  description: string;
  eyebrow: string;
  title: string;
}) {
  return (
    <fieldset className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
      <legend className="px-2 text-xs uppercase tracking-[0.2em] text-violet-300">Step {eyebrow}</legend>
      <h3 className="text-base font-semibold text-slate-100">{title}</h3>
      <p className="mt-1 text-xs text-slate-400">{description}</p>
      <div className="mt-4 grid gap-4">{children}</div>
    </fieldset>
  );
}

function TextInput({ label, value, onChange, type = "text", required = false, placeholder }: { label: string; value: string; onChange: (value: string) => void; type?: string; required?: boolean; placeholder?: string }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      <span>
        {label}
        {required ? <span className="ml-1 text-violet-200">required</span> : null}
      </span>
      <input required={required} type={type} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} className="rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-violet-300" />
    </label>
  );
}

function TextArea({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <textarea value={value} onChange={(event) => onChange(event.target.value)} rows={3} className="rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-violet-300" />
    </label>
  );
}

function SelectInput({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: [string, string][] }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)} className="rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-violet-300">
        {options.map(([optionValue, labelText]) => <option key={optionValue} value={optionValue}>{labelText}</option>)}
      </select>
    </label>
  );
}

function splitList(value: string): string[] {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function buildPageSummary(batches: ReviewBatch[]) {
  return batches.reduce(
    (summary, batch) => ({
      reviewedCount: summary.reviewedCount + batch.summary.reviewed_count,
      followUps: summary.followUps + batch.summary.follow_up_needed_count,
      repeatedPatterns: summary.repeatedPatterns + batch.summary.repeated_attention_labels.length + batch.summary.repeated_blocker_patterns.length,
    }),
    { reviewedCount: 0, followUps: 0, repeatedPatterns: 0 },
  );
}
