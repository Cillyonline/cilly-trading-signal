"use client";

import { FormEvent, useEffect, useState } from "react";

import { createTradeEvent, fetchTrade } from "@/lib/api";
import type { StrategyType } from "@/types/signals";
import type { TradeDetail, TradeEventCreatePayload, TradeEventType } from "@/types/trades";

type EventForm = {
  event_type: TradeEventType;
  event_time: string;
  price: string;
  reason: "" | "target_1" | "target_2";
  notes: string;
};

const emptyForm: EventForm = {
  event_type: "note",
  event_time: "",
  price: "",
  reason: "",
  notes: "",
};

export default function TradeDetailPage({ params }: { params: { id: string } }) {
  const [trade, setTrade] = useState<TradeDetail | null>(null);
  const [form, setForm] = useState<EventForm>(emptyForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
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
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadTrade();
  }, [params.id]);

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
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Trade Detail</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Trade manuell verwalten</h1>
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
          <section className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
            <div className="grid gap-6">
              <TradeSummary trade={trade} />
              <EventTimeline trade={trade} />
            </div>
            <EventFormCard form={form} isSaving={isSaving} onChange={setForm} onSubmit={submitEvent} />
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

function TradeSummary({ trade }: { trade: TradeDetail }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="flex flex-wrap items-center gap-3">
        <h2 className="text-2xl font-semibold">{trade.symbol}</h2>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{trade.status}</span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">{trade.asset_class}</span>
        <span className="text-sm text-slate-400">{formatStrategy(trade.strategy_type)}</span>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Entry" value={formatMoney(trade.entry_price)} />
        <Metric label="Stop" value={formatMoney(trade.stop_loss)} />
        <Metric label="Target 1" value={formatMoney(trade.target_1)} />
        <Metric label="Target 2" value={formatMoney(trade.target_2)} />
        <Metric label="Position" value={formatNumber(trade.position_size)} />
        <Metric label="Risk" value={formatMoney(trade.initial_risk_amount)} />
        <Metric label="R:R" value={formatR(trade.initial_risk_reward)} />
        <Metric label="Opened" value={formatDateTime(trade.opened_at)} />
      </div>

      {trade.notes ? <p className="mt-5 text-sm text-slate-300">{trade.notes}</p> : null}
    </article>
  );
}

function EventTimeline({ trade }: { trade: TradeDetail }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
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
    <form onSubmit={onSubmit} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h2 className="text-xl font-semibold">Management Event loggen</h2>
      <p className="mt-2 text-sm text-slate-400">Nur manuelle Dokumentation. Keine Broker-Aktion.</p>

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
