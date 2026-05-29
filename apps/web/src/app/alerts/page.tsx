"use client";

import { useEffect, useMemo, useState } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { fetchAlerts, redirectToLoginOnAuthError } from "@/lib/api";
import type { AlertDeliveryStatus, AlertEvent, AlertStatus } from "@/types/alerts";

const statusTone: Record<AlertStatus, string> = {
  active: "border-blue-300/30 bg-blue-300/10 text-blue-100",
  triggered: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  resolved: "border-slate-300/30 bg-slate-300/10 text-slate-100",
  cancelled: "border-orange-300/30 bg-orange-300/10 text-orange-100",
  expired: "border-slate-500/30 bg-slate-500/10 text-slate-300",
};

const deliveryTone: Record<AlertDeliveryStatus, string> = {
  pending: "border-yellow-300/30 bg-yellow-300/10 text-yellow-100",
  sent: "border-emerald-300/30 bg-emerald-300/10 text-emerald-100",
  failed: "border-red-300/30 bg-red-300/10 text-red-100",
  skipped: "border-slate-400/30 bg-slate-400/10 text-slate-200",
};

export default function AlertsPage() {
  const authStatus = useProtectedRoute();
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAlerts() {
    setIsLoading(true);
    setError(null);
    try {
      setAlerts(await fetchAlerts());
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
      void loadAlerts();
    }
  }, [authStatus]);

  const summary = useMemo(() => buildSummary(alerts), [alerts]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#0f766e,transparent_34%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Alerts</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Alert Events pruefen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Audit-Liste fuer empfangene Webhooks und Notification-Status. Alerts sind
                Review-Prompts, keine Kauf-/Verkaufsanweisungen und keine Orderausfuehrung.
              </p>
            </div>
            <a className="text-sm text-emerald-300 hover:text-emerald-200" href="/">
              Zurueck zum Dashboard
            </a>
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          <SummaryCard label="Alle Events" value={alerts.length.toString()} />
          <SummaryCard label="Sent" value={summary.sent.toString()} tone="border-emerald-300/40" />
          <SummaryCard label="Failed" value={summary.failed.toString()} tone="border-red-300/40" />
          <SummaryCard label="Skipped" value={summary.skipped.toString()} tone="border-slate-300/30" />
        </section>

        {error ? (
          <div className="rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">
            {error}
          </div>
        ) : null}

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold">Recent Alert Events</h2>
              <p className="mt-1 text-sm text-slate-400">
                Read-only Ansicht der letzten Events. Es gibt hier keine Trade- oder Order-Aktion.
              </p>
            </div>
            <button
              type="button"
              onClick={() => void loadAlerts()}
              className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
            >
              Aktualisieren
            </button>
          </div>

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Alert Events werden geladen...</p>
            ) : alerts.length === 0 ? (
              <EmptyState />
            ) : (
              <div className="divide-y divide-white/10">
                {alerts.map((alert) => (
                  <AlertCard key={alert.id} alert={alert} />
                ))}
              </div>
            )}
          </div>
        </section>
      </section>
    </main>
  );
}

function AlertCard({ alert }: { alert: AlertEvent }) {
  const symbol = getPayloadText(alert.source_payload, "symbol") ?? "Unbekanntes Symbol";
  const exchange = getPayloadText(alert.source_payload, "exchange");

  return (
    <article className="grid gap-5 p-5 lg:grid-cols-[1fr_0.75fr]">
      <div>
        <div className="flex flex-wrap items-center gap-3">
          <span className={`rounded-full border px-3 py-1 text-xs ${statusTone[alert.status]}`}>
            {formatLabel(alert.status)}
          </span>
          <h3 className="text-lg font-semibold">{symbol}</h3>
          {exchange ? (
            <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase text-slate-300">
              {exchange}
            </span>
          ) : null}
          {alert.timeframe ? <span className="text-sm text-slate-400">{alert.timeframe}</span> : null}
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <Metric label="Type" value={formatLabel(alert.alert_type)} />
          <Metric label="Source" value={formatLabel(alert.source)} />
          <Metric label="Delivery" value={getDeliveryTitle(alert.delivery_status)} />
        </div>

        <p className="mt-4 text-sm text-slate-300">{alert.message ?? "Keine Event-Nachricht gespeichert."}</p>
        {alert.signal_id ? (
          <a
            className="mt-4 inline-flex rounded-xl border border-white/10 px-4 py-2 text-sm text-emerald-300 hover:border-emerald-300/50 hover:text-emerald-200"
            href={`/signals/${alert.signal_id}`}
          >
            Verknuepftes Signal pruefen
          </a>
        ) : null}
      </div>

      <aside className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
        <p className="text-sm font-medium text-slate-200">Event Details</p>
        <div className="mt-3 grid gap-3">
          <Metric label="Created" value={formatDate(alert.created_at)} compact />
          <Metric label="Triggered" value={formatDate(alert.last_triggered_at)} compact />
          <div className={`rounded-xl border p-3 text-sm ${deliveryTone[alert.delivery_status]}`}>
            <p className="font-semibold">{getDeliveryTitle(alert.delivery_status)}</p>
            <p className="mt-1 text-xs opacity-80">{getDeliveryDescription(alert.delivery_status)}</p>
          </div>
          {alert.delivery_error ? (
            <p className="rounded-xl border border-red-300/30 bg-red-300/10 p-3 text-sm text-red-100">
              {formatDeliveryError(alert.delivery_error)}
            </p>
          ) : null}
        </div>
      </aside>
    </article>
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

function Metric({ label, value, compact = false }: { label: string; value: string; compact?: boolean }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`${compact ? "text-sm" : "text-base"} mt-1 font-semibold text-slate-100`}>{value}</p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Noch keine Alert Events gespeichert.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        TradingView Webhooks und spaetere Notification-Versuche erscheinen hier zur manuellen Pruefung.
      </p>
    </div>
  );
}

function buildSummary(alerts: AlertEvent[]) {
  return {
    triggered: alerts.filter((alert) => alert.status === "triggered").length,
    pending: alerts.filter((alert) => alert.delivery_status === "pending").length,
    sent: alerts.filter((alert) => alert.delivery_status === "sent").length,
    failed: alerts.filter((alert) => alert.delivery_status === "failed").length,
    skipped: alerts.filter((alert) => alert.delivery_status === "skipped").length,
  };
}

function getPayloadText(payload: AlertEvent["source_payload"], key: string) {
  if (!payload || Array.isArray(payload)) {
    return null;
  }
  const value = payload[key];
  return typeof value === "string" && value.trim() ? value : null;
}

function formatLabel(value: string) {
  return value.replaceAll("_", " ");
}

function getDeliveryTitle(status: AlertDeliveryStatus) {
  const labels: Record<AlertDeliveryStatus, string> = {
    pending: "Pending",
    sent: "Telegram sent",
    failed: "Delivery failed",
    skipped: "Delivery skipped",
  };
  return labels[status];
}

function getDeliveryDescription(status: AlertDeliveryStatus) {
  const descriptions: Record<AlertDeliveryStatus, string> = {
    pending: "Zustellung ist vorgemerkt oder noch nicht abgeschlossen.",
    sent: "Telegram-Zustellung wurde dokumentiert. Weiterhin manuell pruefen.",
    failed: "Zustellung ist fehlgeschlagen. Alert bleibt zur manuellen Pruefung sichtbar.",
    skipped: "Nicht gesendet, z.B. wegen Policy, deaktiviertem Routing, Dedup oder Rate Limit.",
  };
  return descriptions[status];
}

function formatDeliveryError(error: string) {
  const safeMessages: Record<string, string> = {
    "Telegram alert routing is disabled.": "Routing deaktiviert: Telegram wurde nicht automatisch gesendet.",
    "Alert type is manual-review only.": "Policy: Dieser Alert-Typ bleibt manual-only.",
    "Telegram alert deduplicated within 30 minutes.": "Dedup: In den letzten 30 Minuten wurde dieser Alert-Key bereits gesendet.",
    "Telegram alert rate limit reached.": "Rate Limit: Zu viele Telegram-Zustellungen in kurzer Zeit.",
    TelegramConfigurationError: "Telegram-Konfiguration fehlt oder ist unvollstaendig.",
    TelegramDeliveryError: "Telegram-Provider konnte die Nachricht nicht zustellen.",
  };
  return safeMessages[error] ?? "Delivery-Hinweis: Bitte Alert und Konfiguration manuell pruefen.";
}

function formatDate(value: string | null) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
