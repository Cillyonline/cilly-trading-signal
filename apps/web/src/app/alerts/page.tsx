"use client";

import { useEffect, useMemo, useState } from "react";

import { AuthenticatedHeaderActions } from "@/components/authenticated-header-actions";
import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";
import { fetchAlerts, redirectToLoginOnAuthError } from "@/lib/api";
import type { AlertDeliveryStatus, AlertEvent, AlertStatus, AlertType } from "@/types/alerts";

type AlertFilters = {
  delivery: "all" | AlertDeliveryStatus;
  status: "all" | AlertStatus;
  type: "all" | AlertType;
  priority: "all" | "p1" | "p2" | "p3";
  symbol: string;
};

const emptyFilters: AlertFilters = {
  delivery: "all",
  status: "all",
  type: "all",
  priority: "all",
  symbol: "",
};

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
  const [filters, setFilters] = useState<AlertFilters>(emptyFilters);
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
  const filteredAlerts = useMemo(() => filterAlerts(alerts, filters), [alerts, filters]);

  if (authStatus !== "authenticated") {
    return <ProtectedRouteLoading />;
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#0f766e,transparent_34%),rgba(255,255,255,0.05)] p-5 sm:p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-emerald-300 sm:tracking-[0.35em]">Alerts</p>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Alert Events pruefen</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Audit-Liste fuer empfangene Webhooks und Notification-Status. Alerts sind
                Review-Prompts, keine Kauf-/Verkaufsanweisungen und keine Orderausfuehrung.
              </p>
            </div>
            <AuthenticatedHeaderActions />
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-5">
          <SummaryCard label="Alle Events" value={alerts.length.toString()} />
          <SummaryCard label="Pending" value={summary.pending.toString()} tone="border-yellow-300/40" />
          <SummaryCard label="Sent" value={summary.sent.toString()} tone="border-emerald-300/40" />
          <SummaryCard label="Failed" value={summary.failed.toString()} tone="border-red-300/40" />
          <SummaryCard label="Skipped" value={summary.skipped.toString()} tone="border-slate-300/30" />
        </section>

        <AlertTriageNotice summary={summary} />

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

          <AlertFiltersPanel
            filters={filters}
            resultCount={filteredAlerts.length}
            totalCount={alerts.length}
            onChange={setFilters}
            onReset={() => setFilters(emptyFilters)}
          />

          <div className="mt-6 overflow-hidden rounded-2xl border border-white/10">
            {isLoading ? (
              <p className="p-5 text-sm text-slate-400">Alert Events werden geladen...</p>
            ) : alerts.length === 0 ? (
              <EmptyState />
            ) : filteredAlerts.length === 0 ? (
              <FilteredEmptyState />
            ) : (
              <div className="divide-y divide-white/10">
                {filteredAlerts.map((alert) => (
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

function AlertTriageNotice({ summary }: { summary: ReturnType<typeof buildSummary> }) {
  if (summary.failed > 0 || summary.pending > 0) {
    return (
      <section className="rounded-3xl border border-red-300/30 bg-red-300/10 p-5 text-red-100">
        <p className="font-semibold">Alert Delivery manuell pruefen</p>
        <p className="mt-2 text-sm">
          {summary.failed} failed und {summary.pending} pending Events brauchen Review. Das ist keine
          automatische Trade-Aktion und keine Ausfuehrung.
        </p>
      </section>
    );
  }

  if (summary.skipped > 0) {
    return (
      <section className="rounded-3xl border border-slate-400/30 bg-slate-800/60 p-5 text-slate-200">
        <p className="font-semibold">Skipped Events sichtbar</p>
        <p className="mt-2 text-sm">
          Skipped kann durch Policy, deaktiviertes Routing, Dedup oder Rate Limit entstehen. Events bleiben
          fuer die manuelle Pruefung sichtbar.
        </p>
      </section>
    );
  }

  return null;
}

function AlertFiltersPanel({
  filters,
  resultCount,
  totalCount,
  onChange,
  onReset,
}: {
  filters: AlertFilters;
  resultCount: number;
  totalCount: number;
  onChange: (filters: AlertFilters) => void;
  onReset: () => void;
}) {
  return (
    <div className="mt-6 grid gap-4 rounded-2xl border border-white/10 bg-slate-950/70 p-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-200">Alert Review Filter</p>
          <p className="mt-1 text-xs text-slate-400">
            Filter helfen beim Audit. Sie loesen keine Zustellung, keinen Trade und keine Order aus.
          </p>
        </div>
        <div className="flex items-center gap-3 text-sm text-slate-400">
          <span>
            {resultCount} / {totalCount} sichtbar
          </span>
          <button
            className="rounded-xl border border-white/10 px-3 py-2 text-slate-200 hover:border-emerald-300/50"
            onClick={onReset}
            type="button"
          >
            Zuruecksetzen
          </button>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <FilterSelect
          label="Delivery"
          value={filters.delivery}
          onChange={(value) => onChange({ ...filters, delivery: value as AlertFilters["delivery"] })}
          options={[
            ["all", "Alle Delivery States"],
            ["failed", "Failed"],
            ["pending", "Pending"],
            ["skipped", "Skipped"],
            ["sent", "Sent"],
          ]}
        />
        <FilterSelect
          label="Status"
          value={filters.status}
          onChange={(value) => onChange({ ...filters, status: value as AlertFilters["status"] })}
          options={[
            ["all", "Alle Status"],
            ["triggered", "Triggered"],
            ["active", "Active"],
            ["resolved", "Resolved"],
            ["cancelled", "Cancelled"],
            ["expired", "Expired"],
          ]}
        />
        <FilterSelect
          label="Typ"
          value={filters.type}
          onChange={(value) => onChange({ ...filters, type: value as AlertFilters["type"] })}
          options={[
            ["all", "Alle Typen"],
            ["near_trigger", "Near Trigger"],
            ["entry_trigger", "Entry Trigger"],
            ["invalidation", "Invalidation"],
            ["exit_warning", "Exit Warning"],
            ["info", "Info"],
            ["watchlist", "Watchlist"],
            ["armed", "Armed"],
            ["management", "Management"],
            ["exit_signal", "Exit Signal"],
          ]}
        />
        <FilterSelect
          label="Prioritaet"
          value={filters.priority}
          onChange={(value) => onChange({ ...filters, priority: value as AlertFilters["priority"] })}
          options={[
            ["all", "Alle Prioritaeten"],
            ["p1", "P1"],
            ["p2", "P2"],
            ["p3", "P3"],
          ]}
        />
        <label className="grid gap-2 text-sm text-slate-300 xl:col-span-2">
          Symbol
          <input
            value={filters.symbol}
            onChange={(event) => onChange({ ...filters, symbol: event.target.value })}
            className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            placeholder="AAPL, BTC..."
          />
        </label>
      </div>
    </div>
  );
}

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: [string, string][];
  onChange: (value: string) => void;
}) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
      >
        {options.map(([optionValue, optionLabel]) => (
          <option key={optionValue} value={optionValue}>
            {optionLabel}
          </option>
        ))}
      </select>
    </label>
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
          <span className={`rounded-full border px-3 py-1 text-xs ${deliveryTone[alert.delivery_status]}`}>
            {getDeliveryTitle(alert.delivery_status)}
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

function FilteredEmptyState() {
  return (
    <div className="p-8 text-center">
      <p className="text-lg font-semibold text-slate-200">Keine Alert Events fuer diese Filter.</p>
      <p className="mx-auto mt-2 max-w-xl text-sm text-slate-400">
        Setze Filter zurueck oder pruefe failed, skipped und pending Events bewusst separat.
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

function filterAlerts(alerts: AlertEvent[], filters: AlertFilters) {
  const symbol = filters.symbol.trim().toLowerCase();

  return alerts.filter((alert) => {
    if (filters.delivery !== "all" && alert.delivery_status !== filters.delivery) {
      return false;
    }
    if (filters.status !== "all" && alert.status !== filters.status) {
      return false;
    }
    if (filters.type !== "all" && alert.alert_type !== filters.type) {
      return false;
    }
    if (filters.priority !== "all" && alert.priority.toLowerCase() !== filters.priority) {
      return false;
    }
    if (symbol) {
      const payloadSymbol = getPayloadText(alert.source_payload, "symbol")?.toLowerCase() ?? "";
      if (!payloadSymbol.includes(symbol)) {
        return false;
      }
    }
    return true;
  });
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
