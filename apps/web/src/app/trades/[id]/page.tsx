"use client";

import { FormEvent, useEffect, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import {
  closeTrade,
  createJournalEntry,
  createTradeEvent,
  fetchTrade,
  redirectToLoginOnAuthError,
} from "@/lib/api";
import type { StrategyType } from "@/types/signals";
import type {
  ExitReason,
  JournalEntry,
  JournalEntryCreatePayload,
  TradeClosePayload,
  TradeDetail,
  TradeEventCreatePayload,
  TradeEventType,
} from "@/types/trades";

type EventForm = {
  event_type: TradeEventType;
  event_time: string;
  price: string;
  reason: "" | "target_1" | "target_2";
  notes: string;
};

type CloseForm = {
  exit_price: string;
  exit_reason: ExitReason;
  closed_at: string;
  notes: string;
};

type JournalForm = {
  setup_rule_followed: "" | "true" | "false";
  entry_quality_score: string;
  stop_quality_score: string;
  exit_quality_score: string;
  discipline_score: string;
  market_context: string;
  emotional_notes: string;
  what_went_well: string;
  what_went_wrong: string;
  lesson_learned: string;
  reviewed_at: string;
};

const emptyForm: EventForm = {
  event_type: "note",
  event_time: "",
  price: "",
  reason: "",
  notes: "",
};

const emptyCloseForm: CloseForm = {
  exit_price: "",
  exit_reason: "manual_exit",
  closed_at: "",
  notes: "",
};

const emptyJournalForm: JournalForm = {
  setup_rule_followed: "",
  entry_quality_score: "",
  stop_quality_score: "",
  exit_quality_score: "",
  discipline_score: "",
  market_context: "",
  emotional_notes: "",
  what_went_well: "",
  what_went_wrong: "",
  lesson_learned: "",
  reviewed_at: "",
};

export default function TradeDetailPage({ params }: { params: { id: string } }) {
  const authStatus = useProtectedRoute();
  const [trade, setTrade] = useState<TradeDetail | null>(null);
  const [form, setForm] = useState<EventForm>(emptyForm);
  const [closeForm, setCloseForm] = useState<CloseForm>(emptyCloseForm);
  const [journalForm, setJournalForm] = useState<JournalForm>(emptyJournalForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [isReviewing, setIsReviewing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadTrade() {
    const tradeId = Number(params.id);
    if (!Number.isInteger(tradeId) || tradeId <= 0) {
      setError("Ungueltige Trade-ID.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      setTrade(await fetchTrade(tradeId));
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
      void loadTrade();
    }
  }, [authStatus, params.id]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function submitEvent(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!trade) {
      return;
    }

    const payload = buildEventPayload(form);
    if (!payload) {
      setError("Fuellen die Pflichtfelder fuer das Management-Event aus.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      await createTradeEvent(trade.id, payload);
      setForm({ ...emptyForm, event_time: form.event_time });
      await loadTrade();
    } catch (saveError) {
      if (redirectToLoginOnAuthError(saveError)) {
        return;
      }
      setError(saveError instanceof Error ? saveError.message : "Unbekannter Fehler.");
    } finally {
      setIsSaving(false);
    }
  }

  async function submitClose(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!trade) {
      return;
    }

    const payload = buildClosePayload(closeForm);
    if (!payload) {
      setError("Fuellen die Pflichtfelder fuer den manuellen Close aus.");
      return;
    }

    setIsClosing(true);
    setError(null);
    try {
      setTrade(await closeTrade(trade.id, payload));
      setCloseForm(emptyCloseForm);
    } catch (closeError) {
      if (redirectToLoginOnAuthError(closeError)) {
        return;
      }
      setError(closeError instanceof Error ? closeError.message : "Unbekannter Fehler.");
    } finally {
      setIsClosing(false);
    }
  }

  async function submitJournal(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!trade) {
      return;
    }

    const payload = buildJournalPayload(journalForm);
    if (!payload) {
      setError("Fuellen das Review-Datum aus.");
      return;
    }

    setIsReviewing(true);
    setError(null);
    try {
      await createJournalEntry(trade.id, payload);
      setJournalForm(emptyJournalForm);
      await loadTrade();
    } catch (reviewError) {
      if (redirectToLoginOnAuthError(reviewError)) {
        return;
      }
      setError(reviewError instanceof Error ? reviewError.message : "Unbekannter Fehler.");
    } finally {
      setIsReviewing(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-5 text-slate-100 sm:px-6 sm:py-8">
      <section className="mx-auto flex max-w-6xl flex-col gap-5 sm:gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#1d4ed8,transparent_34%),rgba(255,255,255,0.05)] p-5 sm:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">Trade Detail</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Trade manuell verwalten</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Management Events sind reine Dokumentation. Stop- und Target-Updates spiegeln deine
                manuelle Verwaltung ausserhalb der App wider und fuehren keine Orders aus.
              </p>
            </div>
            <div className="flex gap-4 text-sm">
              <a className="text-emerald-300 hover:text-emerald-200" href="/trades">
                Zurueck zu Trades
              </a>
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {error ? <ErrorMessage message={error} /> : null}

        {isLoading ? (
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-slate-400">Trade wird geladen...</p>
          </section>
        ) : trade ? (
          <section className="grid gap-5 sm:gap-6 lg:grid-cols-[1fr_0.9fr]">
            <div className="grid gap-6">
              <TradeSummary trade={trade} />
              <EventTimeline trade={trade} />
            </div>
            <div className="grid gap-6">
              <ManagementBoundaryCard trade={trade} />
              <EventFormCard form={form} isSaving={isSaving} onChange={setForm} onSubmit={submitEvent} />
              <CloseTradeCard
                form={closeForm}
                isClosing={isClosing}
                onChange={setCloseForm}
                onSubmit={submitClose}
                trade={trade}
              />
              <JournalReviewCard
                form={journalForm}
                isReviewing={isReviewing}
                onChange={setJournalForm}
                onSubmit={submitJournal}
                trade={trade}
              />
            </div>
          </section>
        ) : null}
      </section>
    </main>
  );
}

function buildEventPayload(form: EventForm): TradeEventCreatePayload | null {
  if (!form.event_time) {
    return null;
  }

  const payload: TradeEventCreatePayload = {
    event_type: form.event_type,
    event_time: new Date(form.event_time).toISOString(),
    notes: form.notes || null,
  };

  if (form.event_type === "stop_updated") {
    if (!form.price) {
      return null;
    }
    payload.price = form.price;
  }

  if (form.event_type === "target_updated") {
    if (!form.price || !form.reason) {
      return null;
    }
    payload.price = form.price;
    payload.reason = form.reason;
  }

  if (form.event_type === "note" && !form.notes) {
    return null;
  }

  return payload;
}

function buildClosePayload(form: CloseForm): TradeClosePayload | null {
  if (!form.exit_price || !form.closed_at) {
    return null;
  }
  return {
    exit_price: form.exit_price,
    exit_reason: form.exit_reason,
    closed_at: new Date(form.closed_at).toISOString(),
    notes: form.notes || null,
  };
}

function buildJournalPayload(form: JournalForm): JournalEntryCreatePayload | null {
  if (!form.reviewed_at) {
    return null;
  }

  return {
    setup_rule_followed: form.setup_rule_followed === "" ? null : form.setup_rule_followed === "true",
    entry_quality_score: optionalScore(form.entry_quality_score),
    stop_quality_score: optionalScore(form.stop_quality_score),
    exit_quality_score: optionalScore(form.exit_quality_score),
    discipline_score: optionalScore(form.discipline_score),
    market_context: form.market_context || null,
    emotional_notes: form.emotional_notes || null,
    what_went_well: form.what_went_well || null,
    what_went_wrong: form.what_went_wrong || null,
    lesson_learned: form.lesson_learned || null,
    reviewed_at: new Date(form.reviewed_at).toISOString(),
  };
}

function optionalScore(value: string) {
  return value ? Number(value) : null;
}

function TradeSummary({ trade }: { trade: TradeDetail }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-2xl font-semibold">{trade.symbol}</h2>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{trade.status}</span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{trade.asset_class}</span>
        <ReviewStatusBadge trade={trade} />
        <span className="text-sm text-slate-400">{formatStrategy(trade.strategy_type)}</span>
      </div>

      <div className="mt-5 grid grid-cols-2 gap-2 sm:gap-3 lg:grid-cols-4">
        <Metric label="Entry" value={formatMoney(trade.entry_price)} />
        <Metric label="Stop" value={formatMoney(trade.stop_loss)} />
        <Metric label="Target 1" value={formatMoney(trade.target_1)} />
        <Metric label="Target 2" value={formatMoney(trade.target_2)} />
        <Metric label="Position" value={formatNumber(trade.position_size)} />
        <Metric label="Risk" value={formatMoney(trade.initial_risk_amount)} />
        <Metric label="R:R" value={formatR(trade.initial_risk_reward)} />
        <Metric label="Opened" value={formatDateTime(trade.opened_at)} />
        <Metric label="Exit" value={formatMoney(trade.exit_price)} />
        <Metric label="Result" value={formatMoney(trade.result_amount)} />
        <Metric label="Result R" value={formatR(trade.result_r)} />
        <Metric label="Closed" value={formatDateTime(trade.closed_at)} />
      </div>

      {trade.notes ? <p className="mt-5 text-sm text-slate-300">{trade.notes}</p> : null}
    </article>
  );
}

function ManagementBoundaryCard({ trade }: { trade: TradeDetail }) {
  return (
    <section className="rounded-3xl border border-sky-300/20 bg-sky-300/[0.06] p-5 sm:p-6">
      <h2 className="text-xl font-semibold text-sky-50">Manual Management Boundary</h2>
      <p className="mt-2 text-sm text-sky-100/80">
        Status {trade.status}; Risiko {formatMoney(trade.initial_risk_amount)}; Result R {formatR(trade.result_r)}.
        Alle Aktionen unten dokumentieren externe manuelle Entscheidungen. Keine Broker-Verbindung, keine Orderausfuehrung.
      </p>
      <div className="mt-4 grid gap-2 text-xs text-sky-50 sm:grid-cols-3">
        <WorkflowPill label="1 Manage" text="Events und Anpassungen loggen" />
        <WorkflowPill label="2 Close" text="Externen Exit dokumentieren" />
        <WorkflowPill label="3 Journal" text="Nach Close Prozess reviewen" />
      </div>
    </section>
  );
}

function WorkflowPill({ label, text }: { label: string; text: string }) {
  return (
    <div className="rounded-2xl border border-sky-200/20 bg-slate-950/40 p-3">
      <p className="font-semibold uppercase tracking-wide text-sky-100">{label}</p>
      <p className="mt-1 text-sky-100/70">{text}</p>
    </div>
  );
}

function ReviewStatusBadge({ trade }: { trade: TradeDetail }) {
  if (trade.review_status === "reviewed") {
    return <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-xs text-emerald-100">Review komplett</span>;
  }
  if (trade.review_status === "needs_review") {
    return <span className="rounded-full bg-yellow-300/10 px-3 py-1 text-xs text-yellow-100">Review offen</span>;
  }
  return <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-400">Review nach Close</span>;
}

function JournalReviewCard({
  form,
  isReviewing,
  onChange,
  onSubmit,
  trade,
}: {
  form: JournalForm;
  isReviewing: boolean;
  onChange: (form: JournalForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  trade: TradeDetail;
}) {
  if (trade.journal_entry) {
    return <JournalReviewSummary journalEntry={trade.journal_entry} />;
  }

  if (trade.status !== "closed") {
    return (
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
        <StepHeading step="3 Journal" title="Journal Review" />
        <p className="mt-2 text-sm text-slate-400">
          Review ist erst nach einem geschlossenen Trade moeglich. Fokus: Prozessqualitaet, Disziplin und Lernen.
        </p>
      </section>
    );
  }

  return (
    <form onSubmit={onSubmit} className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
      <StepHeading step="3 Journal" title="Journal Review erfassen" />
      <p className="mt-2 text-sm text-slate-400">
        Reflektiert Prozess, Disziplin und Lernpunkte im R-Kontext. Keine Trade-Empfehlung.
      </p>

      <div className="mt-6 grid gap-4">
        <label className="grid gap-2 text-sm text-slate-300">
          Review Datum
          <input
            required
            type="datetime-local"
            value={form.reviewed_at}
            onChange={(event) => onChange({ ...form, reviewed_at: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          />
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Setup-Regeln eingehalten?
          <select
            value={form.setup_rule_followed}
            onChange={(event) =>
              onChange({
                ...form,
                setup_rule_followed: event.target.value as JournalForm["setup_rule_followed"],
              })
            }
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="">Nicht bewertet</option>
            <option value="true">Ja</option>
            <option value="false">Nein</option>
          </select>
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          <ScoreField
            label="Entry Qualitaet"
            value={form.entry_quality_score}
            onChange={(value) => onChange({ ...form, entry_quality_score: value })}
          />
          <ScoreField
            label="Stop Qualitaet"
            value={form.stop_quality_score}
            onChange={(value) => onChange({ ...form, stop_quality_score: value })}
          />
          <ScoreField
            label="Exit Qualitaet"
            value={form.exit_quality_score}
            onChange={(value) => onChange({ ...form, exit_quality_score: value })}
          />
          <ScoreField
            label="Disziplin"
            value={form.discipline_score}
            onChange={(value) => onChange({ ...form, discipline_score: value })}
          />
        </div>

        <JournalTextArea
          label="Marktkontext"
          value={form.market_context}
          onChange={(value) => onChange({ ...form, market_context: value })}
        />
        <JournalTextArea
          label="Emotionale Notizen"
          value={form.emotional_notes}
          onChange={(value) => onChange({ ...form, emotional_notes: value })}
        />
        <JournalTextArea
          label="Was lief gut?"
          value={form.what_went_well}
          onChange={(value) => onChange({ ...form, what_went_well: value })}
        />
        <JournalTextArea
          label="Was lief falsch?"
          value={form.what_went_wrong}
          onChange={(value) => onChange({ ...form, what_went_wrong: value })}
        />
        <JournalTextArea
          label="Gelernt"
          value={form.lesson_learned}
          onChange={(value) => onChange({ ...form, lesson_learned: value })}
        />

        <button
          disabled={isReviewing}
          type="submit"
          className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
        >
          {isReviewing ? "Speichere..." : "Review speichern"}
        </button>
      </div>
    </form>
  );
}

function JournalReviewSummary({ journalEntry }: { journalEntry: JournalEntry }) {
  return (
    <section className="rounded-3xl border border-emerald-300/20 bg-emerald-300/5 p-5 sm:p-6">
      <StepHeading step="3 Journal" title="Journal Review" />
      <p className="mt-2 text-sm text-slate-400">Erfasst am {formatDateTime(journalEntry.reviewed_at)}</p>

      <div className="mt-5 grid grid-cols-2 gap-2 sm:gap-3">
        <Metric label="Setup Rules" value={formatBoolean(journalEntry.setup_rule_followed)} />
        <Metric label="Entry" value={formatScore(journalEntry.entry_quality_score)} />
        <Metric label="Stop" value={formatScore(journalEntry.stop_quality_score)} />
        <Metric label="Exit" value={formatScore(journalEntry.exit_quality_score)} />
        <Metric label="Disziplin" value={formatScore(journalEntry.discipline_score)} />
      </div>

      <div className="mt-5 grid gap-4 text-sm text-slate-300">
        <JournalText label="Marktkontext" value={journalEntry.market_context} />
        <JournalText label="Emotionale Notizen" value={journalEntry.emotional_notes} />
        <JournalText label="Was lief gut?" value={journalEntry.what_went_well} />
        <JournalText label="Was lief falsch?" value={journalEntry.what_went_wrong} />
        <JournalText label="Gelernt" value={journalEntry.lesson_learned} />
      </div>
    </section>
  );
}

function ScoreField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <input
        type="number"
        min="1"
        max="5"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
        placeholder="1-5"
      />
    </label>
  );
}

function JournalTextArea({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-24 rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
        placeholder="Prozessbezogene Beobachtung festhalten"
      />
    </label>
  );
}

function JournalText({ label, value }: { label: string; value: string | null }) {
  if (!value) {
    return null;
  }
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 whitespace-pre-line">{value}</p>
    </div>
  );
}

function CloseTradeCard({
  form,
  isClosing,
  onChange,
  onSubmit,
  trade,
}: {
  form: CloseForm;
  isClosing: boolean;
  onChange: (form: CloseForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  trade: TradeDetail;
}) {
  if (trade.status === "closed") {
    return (
      <section className="rounded-3xl border border-emerald-300/20 bg-emerald-300/5 p-5 sm:p-6">
        <StepHeading step="2 Close" title="Trade geschlossen" />
        <p className="mt-2 text-sm text-slate-300">
          Ergebnis: {formatMoney(trade.result_amount)} / {formatR(trade.result_r)}. Dieser Close ist
          eine manuelle Dokumentation, keine Broker-Aktion.
        </p>
      </section>
    );
  }

  return (
    <form onSubmit={onSubmit} className="rounded-3xl border border-red-300/30 bg-red-300/[0.05] p-5 sm:p-6">
      <StepHeading step="2 Close" title="Trade manuell schliessen" />
      <p className="mt-2 text-sm text-red-100/80">
        Finaler Close-Log fuer eine bereits extern ausgefuehrte Entscheidung. Keine Orderausfuehrung.
      </p>

      <div className="mt-6 grid gap-4">
        <label className="grid gap-2 text-sm text-slate-300">
          Exit Price
          <input
            required
            type="number"
            min="0"
            step="0.00000001"
            value={form.exit_price}
            onChange={(event) => onChange({ ...form, exit_price: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          />
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Exit Reason
          <select
            value={form.exit_reason}
            onChange={(event) => onChange({ ...form, exit_reason: event.target.value as ExitReason })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="stop_loss">Stop Loss</option>
            <option value="target_1">Target 1</option>
            <option value="target_2">Target 2</option>
            <option value="manual_exit">Manual Exit</option>
            <option value="structure_break">Structure Break</option>
            <option value="time_stop">Time Stop</option>
            <option value="failed_breakout">Failed Breakout</option>
            <option value="other">Other</option>
          </select>
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Closed At
          <input
            required
            type="datetime-local"
            value={form.closed_at}
            onChange={(event) => onChange({ ...form, closed_at: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          />
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Notes optional
          <textarea
            value={form.notes}
            onChange={(event) => onChange({ ...form, notes: event.target.value })}
            className="min-h-24 rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            placeholder="Warum wurde der Trade manuell geschlossen?"
          />
        </label>

        <button
          disabled={isClosing}
          type="submit"
          className="rounded-xl bg-red-300 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
        >
          {isClosing ? "Schliesse..." : "Trade Close loggen"}
        </button>
      </div>
    </form>
  );
}

function EventTimeline({ trade }: { trade: TradeDetail }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-xl font-semibold">Management Events</h2>
        <span className="text-sm text-slate-400">{trade.events.length} Events</span>
      </div>

      {trade.events.length === 0 ? (
        <p className="mt-5 rounded-2xl border border-white/10 bg-slate-950/60 p-5 text-sm text-slate-400">
          Noch keine Management Events geloggt.
        </p>
      ) : (
        <div className="mt-5 divide-y divide-white/10 overflow-hidden rounded-2xl border border-white/10">
          {trade.events.map((event) => (
            <article key={event.id} className="grid gap-3 p-5">
              <div className="flex flex-wrap items-center gap-3">
                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
                  {event.event_type.replaceAll("_", " ")}
                </span>
                <span className="text-sm text-slate-400">{formatDateTime(event.event_time)}</span>
              </div>
              {event.old_value || event.new_value ? (
                <p className="text-sm text-slate-300">
                  {event.old_value ?? "-"} zu {event.new_value ?? "-"}
                </p>
              ) : null}
              {event.reason ? <p className="text-sm text-slate-400">Reason: {event.reason}</p> : null}
              {event.notes ? <p className="text-sm text-slate-300">{event.notes}</p> : null}
            </article>
          ))}
        </div>
      )}
    </article>
  );
}

function EventFormCard({
  form,
  isSaving,
  onChange,
  onSubmit,
}: {
  form: EventForm;
  isSaving: boolean;
  onChange: (form: EventForm) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form onSubmit={onSubmit} className="rounded-3xl border border-emerald-300/20 bg-emerald-300/[0.04] p-5 sm:p-6">
      <StepHeading step="1 Manage" title="Management Event loggen" />
      <p className="mt-2 text-sm text-emerald-100/80">
        Routine-Dokumentation fuer Notes, Stop- oder Target-Updates. Keine Broker-Aktion.
      </p>

      <div className="mt-6 grid gap-4">
        <label className="grid gap-2 text-sm text-slate-300">
          Event Type
          <select
            value={form.event_type}
            onChange={(event) => onChange({ ...form, event_type: event.target.value as TradeEventType })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          >
            <option value="note">Note</option>
            <option value="stop_updated">Stop Update</option>
            <option value="target_updated">Target Update</option>
          </select>
        </label>

        <label className="grid gap-2 text-sm text-slate-300">
          Event Time
          <input
            required
            type="datetime-local"
            value={form.event_time}
            onChange={(event) => onChange({ ...form, event_time: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
          />
        </label>

        {form.event_type !== "note" ? (
          <label className="grid gap-2 text-sm text-slate-300">
            Neuer Preis
            <input
              required
              type="number"
              min="0"
              step="0.00000001"
              value={form.price}
              onChange={(event) => onChange({ ...form, price: event.target.value })}
              className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            />
          </label>
        ) : null}

        {form.event_type === "target_updated" ? (
          <label className="grid gap-2 text-sm text-slate-300">
            Target
            <select
              required
              value={form.reason}
              onChange={(event) => onChange({ ...form, reason: event.target.value as EventForm["reason"] })}
              className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            >
              <option value="">Target waehlen</option>
              <option value="target_1">Target 1</option>
              <option value="target_2">Target 2</option>
            </select>
          </label>
        ) : null}

        <label className="grid gap-2 text-sm text-slate-300">
          Notes
          <textarea
            required={form.event_type === "note"}
            value={form.notes}
            onChange={(event) => onChange({ ...form, notes: event.target.value })}
            className="min-h-28 rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            placeholder="Was wurde manuell dokumentiert?"
          />
        </label>

        <button
          disabled={isSaving}
          type="submit"
          className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
        >
          {isSaving ? "Speichere..." : "Event loggen"}
        </button>
      </div>
    </form>
  );
}

function StepHeading({ step, title }: { step: string; title: string }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="rounded-full border border-white/10 bg-slate-950/60 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
        {step}
      </span>
      <h2 className="text-xl font-semibold">{title}</h2>
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

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
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

function formatScore(value: number | null) {
  return value ? `${value}/5` : "-";
}

function formatBoolean(value: boolean | null) {
  if (value === null) {
    return "-";
  }
  return value ? "Ja" : "Nein";
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
