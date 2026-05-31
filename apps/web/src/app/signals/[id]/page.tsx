"use client";

import { useEffect, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import {
  fetchSignal,
  redirectToLoginOnAuthError,
  updateSignalReviewNote,
  updateSignalStatus,
} from "@/lib/api";
import type { Signal, SignalReviewEvent, SignalStatus } from "@/types/signals";

const statusTone: Record<SignalStatus, string> = {
  watchlist: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
  armed: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  triggered: "border-green-300/30 bg-green-300/10 text-green-100",
  invalidated: "border-red-300/30 bg-red-300/10 text-red-100",
  no_setup: "border-slate-400/30 bg-slate-400/10 text-slate-200",
  missed: "border-orange-300/30 bg-orange-300/10 text-orange-100",
  expired: "border-slate-500/30 bg-slate-500/10 text-slate-300",
};

const statusLabel: Record<SignalStatus, string> = {
  watchlist: "Watchlist",
  armed: "Armed",
  triggered: "Triggered",
  invalidated: "Invalidated",
  no_setup: "No Setup",
  missed: "Missed",
  expired: "Expired",
};

export default function SignalDetailPage({ params }: { params: { id: string } }) {
  const authStatus = useProtectedRoute();
  const [signal, setSignal] = useState<Signal | null>(null);
  const [reviewNote, setReviewNote] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isSavingReviewNote, setIsSavingReviewNote] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [reviewNoteMessage, setReviewNoteMessage] = useState<string | null>(null);
  const [reviewNoteError, setReviewNoteError] = useState<string | null>(null);

  async function loadSignal() {
    const signalId = Number(params.id);
    if (!Number.isInteger(signalId) || signalId <= 0) {
      setError("Ungueltige Signal-ID.");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const loaded = await fetchSignal(signalId);
      setSignal(loaded);
      setReviewNote(loaded.review_note ?? "");
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
      void loadSignal();
    }
  }, [authStatus, params.id]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  async function submitStatus(targetStatus: SignalStatus) {
    if (!signal) {
      return;
    }
    setStatusError(null);
    setStatusMessage(null);
    setIsUpdatingStatus(true);
    try {
      const updated = await updateSignalStatus(signal.id, { status: targetStatus });
      setSignal(updated);
      setStatusMessage(`Status manuell auf ${statusLabel[targetStatus]} gesetzt.`);
    } catch (updateError) {
      if (redirectToLoginOnAuthError(updateError)) {
        return;
      }
      setStatusError(updateError instanceof Error ? updateError.message : "Unbekannter Fehler.");
    } finally {
      setIsUpdatingStatus(false);
    }
  }

  async function submitReviewNote() {
    if (!signal) {
      return;
    }
    setReviewNoteError(null);
    setReviewNoteMessage(null);
    setIsSavingReviewNote(true);
    try {
      const updated = await updateSignalReviewNote(signal.id, {
        review_note: reviewNote.trim() || null,
      });
      setSignal(updated);
      setReviewNote(updated.review_note ?? "");
      setReviewNoteMessage("Review Note gespeichert. Strategie-Score und Setup-Bewertung bleiben unveraendert.");
    } catch (saveError) {
      if (redirectToLoginOnAuthError(saveError)) {
        return;
      }
      setReviewNoteError(saveError instanceof Error ? saveError.message : "Unbekannter Fehler.");
    } finally {
      setIsSavingReviewNote(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#064e3b,transparent_36%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">Signal Detail</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Signal vollstaendig pruefen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Diese Ansicht zeigt die gespeicherte Setup-Bewertung als Entscheidungshilfe fuer
                deine manuelle Pruefung. Sie ist keine Kauf- oder Verkaufsanweisung und nutzt keine
                Live-Marktdaten.
              </p>
            </div>
            <div className="flex flex-wrap gap-4 text-sm">
              <a className="text-emerald-300 hover:text-emerald-200" href="/signals">
                Zurueck zu Signalen
              </a>
              <a className="text-emerald-300 hover:text-emerald-200" href="/">
                Dashboard
              </a>
            </div>
          </div>
        </header>

        {error ? <ErrorMessage message={error} onRetry={() => void loadSignal()} /> : null}
        {statusError ? <Notice message={statusError} tone="error" /> : null}
        {statusMessage ? <Notice message={statusMessage} tone="success" /> : null}
        {reviewNoteError ? <Notice message={reviewNoteError} tone="error" /> : null}
        {reviewNoteMessage ? <Notice message={reviewNoteMessage} tone="success" /> : null}

        {isLoading ? (
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <p className="text-sm text-slate-400">Signal wird geladen...</p>
          </section>
        ) : signal ? (
          <SignalDetail
            signal={signal}
            isUpdatingStatus={isUpdatingStatus}
            isSavingReviewNote={isSavingReviewNote}
            reviewNote={reviewNote}
            onReviewNoteChange={setReviewNote}
            onReviewNoteSave={() => void submitReviewNote()}
            onStatusChange={(targetStatus) => void submitStatus(targetStatus)}
          />
        ) : error ? null : (
          <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-8 text-center">
            <p className="text-lg font-semibold text-slate-200">Signal nicht gefunden.</p>
            <p className="mt-2 text-sm text-slate-400">Pruefe die URL oder kehre zur Signalliste zurueck.</p>
          </section>
        )}
      </section>
    </main>
  );
}

function SignalDetail({
  isUpdatingStatus,
  isSavingReviewNote,
  onStatusChange,
  onReviewNoteChange,
  onReviewNoteSave,
  reviewNote,
  signal,
}: {
  isSavingReviewNote: boolean;
  isUpdatingStatus: boolean;
  onReviewNoteChange: (value: string) => void;
  onReviewNoteSave: () => void;
  onStatusChange: (targetStatus: SignalStatus) => void;
  reviewNote: string;
  signal: Signal;
}) {
  const reasoning = toTextList(signal.reasoning);
  const riskFlags = toTextList(signal.risk_flags);
  const noTradeReasons = toTextList(signal.no_trade_reasons);

  return (
    <section className="grid gap-6">
      <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[signal.status]}`}>
                {statusLabel[signal.status]}
              </span>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
                {signal.bias}
              </span>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                Signal #{signal.id}
              </span>
            </div>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight">{signal.symbol}</h2>
            <p className="mt-2 text-sm text-slate-400">
              {formatStrategy(signal.strategy_type)} · {signal.asset_class}
              {signal.exchange ? ` · ${signal.exchange}` : ""} · Watchlist Item #{signal.watchlist_item_id}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:min-w-96">
            <Metric label="Score" value={formatScore(signal)} />
            <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
          </div>
        </div>
      </article>

      {signal.is_stale ? <StaleSignalBanner signal={signal} /> : null}

      <SignalMobileSummary noTradeReasons={noTradeReasons} riskFlags={riskFlags} signal={signal} />

      <section className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <article className="rounded-3xl border border-emerald-400/20 bg-emerald-950/20 p-6">
          <div>
            <p className="text-xs uppercase tracking-[0.3em] text-emerald-300">Manual Review</p>
            <h3 className="mt-2 text-xl font-semibold text-emerald-100">Review Workbench</h3>
            <p className="mt-2 max-w-2xl text-sm text-emerald-50/70">
              Aendere nur den Review-Zustand und dokumentiere deine Entscheidung. Diese Aktionen
              erstellen keine Trades, platzieren keine Orders und sind keine Ausfuehrungsanweisung.
            </p>
          </div>

          <div className="mt-5 rounded-2xl border border-emerald-300/20 bg-slate-950/50 p-4">
            <p className="text-sm font-medium text-emerald-100">Status manuell setzen</p>
            <div className="mt-3 grid gap-2 sm:grid-cols-3">
              {manualStatusTargets(signal.status).map((targetStatus) => (
                <button
                  key={targetStatus}
                  type="button"
                  disabled={isUpdatingStatus}
                  onClick={() => onStatusChange(targetStatus)}
                  className="rounded-xl border border-emerald-300/40 px-4 py-3 text-sm font-semibold text-emerald-100 hover:bg-emerald-300/10 disabled:opacity-60"
                >
                  {statusActionLabel[targetStatus]}
                </button>
              ))}
              {manualStatusTargets(signal.status).length === 0 ? (
                <span className="rounded-xl border border-white/10 px-4 py-3 text-sm text-slate-400">
                  Keine manuelle Transition verfuegbar
                </span>
              ) : null}
            </div>
          </div>

          <div className="mt-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-medium text-slate-100">Review Note</p>
                <p className="mt-1 text-xs text-slate-400">
                  Manuelle Review-Notiz, kein Trade-Journal und kein Einfluss auf Score oder Strategie.
                </p>
              </div>
              <button
                type="button"
                disabled={isSavingReviewNote}
                onClick={onReviewNoteSave}
                className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
              >
                {isSavingReviewNote ? "Speichere..." : "Review Note speichern"}
              </button>
            </div>
            <textarea
              value={reviewNote}
              maxLength={5000}
              onChange={(event) => onReviewNoteChange(event.target.value)}
              placeholder="Warum wurde das Setup bewaffnet, ignoriert, invalidiert oder spaeter erneut geprueft?"
              className="mt-4 min-h-36 w-full rounded-2xl border border-white/10 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none focus:border-emerald-300"
            />
            <p className="mt-2 text-xs text-slate-500">{reviewNote.length}/5000 Zeichen</p>
          </div>
        </article>

        <ReviewContextPanel noTradeReasons={noTradeReasons} riskFlags={riskFlags} signal={signal} />
      </section>

      <ReviewHistory events={signal.review_events} />

      <section className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-xl font-semibold">Setup Bewertungsdaten</h3>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <Metric label="Entry Low" value={formatMoney(signal.entry_low)} />
            <Metric label="Entry High" value={formatMoney(signal.entry_high)} />
            <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
            <Metric label="Stop" value={formatMoney(signal.stop_loss)} />
            <Metric label="Target 1" value={formatMoney(signal.target_1)} />
            <Metric label="Target 2" value={formatMoney(signal.target_2)} />
          </div>
          <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
            <p className="text-sm font-medium text-slate-200">Invalidierung</p>
            <p className="mt-2 text-sm text-slate-300">
              {signal.invalidation_reason || "Keine Invalidierung gespeichert."}
            </p>
          </div>
        </article>

        <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <h3 className="text-xl font-semibold">Timeframes</h3>
          <div className="mt-5 grid gap-3">
            <Metric label="Kontext" value={signal.timeframe_context ?? "-"} />
            <Metric label="Setup" value={signal.timeframe_setup ?? "-"} />
            <Metric label="Trigger" value={signal.timeframe_trigger ?? "-"} />
          </div>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <Metric label="Erstellt" value={formatDateTime(signal.created_at)} />
            <Metric label="Aktualisiert" value={formatDateTime(signal.updated_at)} />
            <Metric label="Triggered At" value={formatDateTime(signal.triggered_at)} />
          </div>
        </article>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
        <TextList title="Vollstaendige Begruendung" empty="Keine Begruendung gespeichert." items={reasoning} />
        <div className="grid gap-6">
          <QualityReportCard checks={signal.quality_report} />
          <BadgeList title="No-Trade Gruende" empty="Keine harten No-Trade Gruende" items={noTradeReasons} tone="red" />
          <BadgeList title="Risk Flags" empty="Keine Risk Flags" items={riskFlags} tone="orange" />
        </div>
      </section>

      <article className="rounded-3xl border border-slate-400/20 bg-slate-900/60 p-6">
        <h3 className="text-xl font-semibold">Naechste manuelle Aktion</h3>
        <p className="mt-3 text-sm text-slate-300">
          {signal.next_action || "Keine naechste Aktion gespeichert. Weiter manuell pruefen."}
        </p>
        <p className="mt-3 text-xs text-slate-500">
          Diese Aktion ist ein Pruefhinweis fuer deine manuelle Entscheidung, keine Order-Anweisung.
        </p>
      </article>
    </section>
  );
}

function QualityReportCard({ checks }: { checks: Signal["quality_report"] }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h3 className="text-xl font-semibold">Analyse-Qualitaet</h3>
      {checks.length > 0 ? (
        <div className="mt-5 grid gap-3">
          {checks.map((check) => (
            <div key={check.key} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              <div className="flex items-start justify-between gap-3">
                <p className="text-sm font-semibold text-slate-100">{check.label}</p>
                <span className={`rounded-full px-2 py-1 text-xs ${qualityTone(check.status)}`}>
                  {check.status}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-400">{check.detail}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-5 text-sm text-slate-500">Kein Qualitaetsbericht gespeichert.</p>
      )}
    </article>
  );
}

function SignalMobileSummary({
  noTradeReasons,
  riskFlags,
  signal,
}: {
  noTradeReasons: string[];
  riskFlags: string[];
  signal: Signal;
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-slate-900/70 p-4 sm:hidden">
      <div className="flex flex-wrap gap-2">
        <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[signal.status]}`}>
          {statusLabel[signal.status]}
        </span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
          {formatStrategy(signal.strategy_type)}
        </span>
        {signal.is_stale ? (
          <span className="rounded-full border border-orange-300/30 bg-orange-300/10 px-3 py-1 text-xs text-orange-100">
            Stale
          </span>
        ) : null}
        {noTradeReasons.length > 0 ? (
          <span className="rounded-full border border-red-300/30 bg-red-300/10 px-3 py-1 text-xs text-red-100">
            No-Trade Context
          </span>
        ) : null}
        {riskFlags.length > 0 ? (
          <span className="rounded-full border border-orange-300/30 bg-orange-300/10 px-3 py-1 text-xs text-orange-100">
            {riskFlags.length} Risk Flags
          </span>
        ) : null}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <Metric label="Score" value={formatScore(signal)} />
        <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
        <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
        <Metric label="Freshness" value={signal.is_stale ? "Stale" : "Current enough"} />
      </div>
      <div className="mt-4 rounded-2xl border border-emerald-300/20 bg-emerald-950/20 p-4">
        <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Naechste manuelle Aktion</p>
        <p className="mt-2 text-sm text-emerald-50/90">{signal.next_action || "Manuell weiter pruefen."}</p>
        <p className="mt-2 text-xs text-emerald-50/60">Pruefhinweis, keine Order-Anweisung.</p>
      </div>
    </section>
  );
}

function qualityTone(status: string) {
  if (status === "passed") {
    return "bg-emerald-300/10 text-emerald-100";
  }
  if (status === "warning" || status === "missing") {
    return "bg-orange-300/10 text-orange-100";
  }
  return "bg-red-300/10 text-red-100";
}

function ReviewHistory({ events }: { events: SignalReviewEvent[] }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-slate-900/60 p-6">
      <h3 className="text-xl font-semibold">Review History</h3>
      <p className="mt-2 text-sm text-slate-400">
        Read-only Historie manueller Review-Aktionen. Diese Eintraege sind Audit-Kontext und keine
        Order- oder Trade-Aktionen.
      </p>
      {events.length === 0 ? (
        <p className="mt-5 text-sm text-slate-500">Noch keine manuellen Review Events gespeichert.</p>
      ) : (
        <div className="mt-5 divide-y divide-white/10 overflow-hidden rounded-2xl border border-white/10">
          {events.map((event) => (
            <div key={event.id} className="grid gap-3 bg-slate-950/60 p-4 md:grid-cols-[0.9fr_1fr]">
              <div>
                <p className="text-sm font-semibold text-slate-100">{formatEventType(event.event_type)}</p>
                <p className="mt-1 text-xs text-slate-500">{formatDateTime(event.created_at)}</p>
              </div>
              <div className="text-sm text-slate-300">
                {event.event_type === "status_change" ? (
                  <p>
                    {formatOptionalStatus(event.previous_status)} {"->"} {formatOptionalStatus(event.new_status)}
                  </p>
                ) : (
                  <p>{event.note || "Review Note geleert."}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

function ReviewContextPanel({
  noTradeReasons,
  riskFlags,
  signal,
}: {
  noTradeReasons: string[];
  riskFlags: string[];
  signal: Signal;
}) {
  return (
    <aside className="rounded-3xl border border-orange-300/20 bg-orange-950/10 p-6">
      <p className="text-xs uppercase tracking-[0.3em] text-orange-200">Risk Context</p>
      <h3 className="mt-2 text-xl font-semibold">Vor jeder Review-Aktion pruefen</h3>
      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
        <Metric label="Aktueller Status" value={statusLabel[signal.status]} />
        <Metric label="Freshness" value={signal.is_stale ? "Stale" : "Current enough"} />
        <Metric label="Next Action" value={signal.next_action || "Manuell weiter pruefen"} />
        <Metric label="R:R" value={signal.risk_reward ? `${formatNumber(signal.risk_reward)}R` : "-"} />
        <Metric label="Trigger" value={formatMoney(signal.trigger_level)} />
      </div>
      <div className="mt-5 rounded-2xl border border-red-300/20 bg-red-950/20 p-4">
        <p className="text-sm font-medium text-red-100">No-Trade Gruende</p>
        <CompactTextItems items={noTradeReasons} empty="Keine harten No-Trade Gruende gespeichert." tone="red" />
      </div>
      <div className="mt-4 rounded-2xl border border-orange-300/20 bg-orange-950/20 p-4">
        <p className="text-sm font-medium text-orange-100">Risk Flags</p>
        <CompactTextItems items={riskFlags} empty="Keine Risk Flags gespeichert." tone="orange" />
      </div>
    </aside>
  );
}

function CompactTextItems({ empty, items, tone }: { empty: string; items: string[]; tone: "orange" | "red" }) {
  const itemClass = tone === "red" ? "bg-red-300/10 text-red-100" : "bg-orange-300/10 text-orange-100";
  return items.length > 0 ? (
    <ul className="mt-3 flex flex-wrap gap-2">
      {items.slice(0, 5).map((item) => (
        <li key={item} className={`rounded-full px-3 py-1 text-xs ${itemClass}`}>
          {item.replaceAll("_", " ")}
        </li>
      ))}
    </ul>
  ) : (
    <p className="mt-3 text-sm text-slate-500">{empty}</p>
  );
}

function StaleSignalBanner({ signal }: { signal: Signal }) {
  return (
    <article className="rounded-3xl border border-orange-300/30 bg-orange-950/30 p-6">
      <p className="text-xs uppercase tracking-[0.3em] text-orange-200">Stale Signal</p>
      <h3 className="mt-2 text-xl font-semibold text-orange-100">Nicht als aktuellen Review-Kandidaten behandeln</h3>
      <p className="mt-3 max-w-3xl text-sm text-orange-100/80">
        {signal.stale_reason ?? `Dieses Signal ist aelter als ${signal.stale_after_days} Tage.`}
      </p>
      <p className="mt-3 text-xs text-orange-100/60">
        Die App hat keine Live-Daten. Importiere aktuelle CSV-Daten oder markiere das Signal manuell als expired,
        wenn es nicht mehr relevant ist.
      </p>
    </article>
  );
}

const manualStatusTransitions: Partial<Record<SignalStatus, SignalStatus[]>> = {
  watchlist: ["armed", "invalidated", "expired"],
  armed: ["invalidated", "missed", "expired"],
  triggered: ["invalidated", "missed", "expired"],
};

const statusActionLabel: Record<SignalStatus, string> = {
  watchlist: "Auf Watchlist setzen",
  armed: "Als Armed markieren",
  triggered: "Als Triggered markieren",
  invalidated: "Invalidieren",
  no_setup: "Als No Setup markieren",
  missed: "Als Missed markieren",
  expired: "Als Expired markieren",
};

function manualStatusTargets(currentStatus: SignalStatus) {
  return manualStatusTransitions[currentStatus] ?? [];
}

function formatEventType(eventType: string) {
  return eventType === "status_change" ? "Status Change" : "Review Note";
}

function formatOptionalStatus(status: SignalStatus | null) {
  return status ? statusLabel[status] : "-";
}

function Notice({ message, tone }: { message: string; tone: "error" | "success" }) {
  const classes =
    tone === "error"
      ? "border-red-400/30 bg-red-950/40 text-red-100"
      : "border-emerald-300/30 bg-emerald-300/10 text-emerald-50";
  return <div className={`whitespace-pre-line rounded-2xl border p-4 text-sm ${classes}`}>{message}</div>;
}

function ErrorMessage({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100 sm:flex-row sm:items-center sm:justify-between">
      <span>{message}</span>
      <button
        className="rounded-xl border border-red-200/20 px-4 py-2 text-red-50 hover:border-red-100/50"
        onClick={onRetry}
        type="button"
      >
        Erneut laden
      </button>
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

function TextList({ title, empty, items }: { title: string; empty: string; items: string[] }) {
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h3 className="text-xl font-semibold">{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-5 space-y-3 text-sm text-slate-300">
          {items.map((item) => (
            <li key={item} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
              {item}
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-5 text-sm text-slate-500">{empty}</p>
      )}
    </article>
  );
}

function BadgeList({
  empty,
  items,
  title,
  tone,
}: {
  empty: string;
  items: string[];
  title: string;
  tone: "orange" | "red";
}) {
  const badgeClass = tone === "red" ? "bg-red-300/10 text-red-100" : "bg-orange-300/10 text-orange-100";
  const emptyClass = "bg-emerald-300/10 text-emerald-100";
  return (
    <article className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h3 className="text-xl font-semibold">{title}</h3>
      <div className="mt-5 flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <span key={item} className={`rounded-full px-3 py-1 text-xs ${badgeClass}`}>
              {item.replaceAll("_", " ")}
            </span>
          ))
        ) : (
          <span className={`rounded-full px-3 py-1 text-xs ${emptyClass}`}>{empty}</span>
        )}
      </div>
    </article>
  );
}

function formatStrategy(strategy: Signal["strategy_type"]) {
  return strategy === "trend_pullback_long" ? "Trend Pullback Long" : "Base Breakout Long";
}

function formatScore(signal: Signal) {
  const score = signal.score ?? "-";
  return signal.score_class ? `${score} / ${signal.score_class.replaceAll("_", " ")}` : `${score}`;
}

function formatMoney(value: string | null) {
  return value ? formatNumber(value) : "-";
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

function toTextList(value: Signal["reasoning"] | Signal["risk_flags"]) {
  if (Array.isArray(value)) {
    return value.map(String);
  }
  if (value && typeof value === "object") {
    return Object.values(value).map(String);
  }
  return [];
}
