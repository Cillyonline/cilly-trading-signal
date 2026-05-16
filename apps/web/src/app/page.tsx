"use client";

import { useEffect, useState } from "react";

import { fetchPerformanceSummary, fetchSignals, fetchTrades, fetchWatchlist, logout } from "@/lib/api";
import type { PerformanceSummary } from "@/types/performance";
import type { Signal } from "@/types/signals";
import type { Trade } from "@/types/trades";
import type { WatchlistItem } from "@/types/watchlist";

const workflowAreas = [
  { label: "Watchlist", href: "/watchlist", description: "Symbole und Asset-Klassen pflegen." },
  { label: "CSV Import", href: "/import", description: "OHLCV-Daten importieren und analysieren." },
  { label: "Signals", href: "/signals", description: "Setup-Bewertungen und No-Trade Gruende pruefen." },
  { label: "Alerts", href: "/alerts", description: "Webhook- und Notification-Events auditieren." },
  { label: "Trades", href: "/trades", description: "Extern ausgefuehrte Trades manuell dokumentieren." },
  { label: "Performance", href: "/performance", description: "Dokumentierte Ergebnisse in R auswerten." },
];

export default function Home() {
  const [dashboard, setDashboard] = useState<DashboardResult | null>(null);

  useEffect(() => {
    void loadDashboardData().then(setDashboard);
  }, []);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#172554,transparent_32%),#050816] px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/30 backdrop-blur">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Cilly Trading Signal</p>
              <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
                Trading-Cockpit fuer Long-only Swingtrading.
              </h1>
              <p className="mt-5 max-w-2xl text-lg text-slate-300">
                Kontext, Setup, Trigger und Risiko werden getrennt bewertet. Keine automatische
                Orderausfuehrung, sondern erklaerbare Signal-Karten, manuelles Trade Logging und
                dokumentierte Ergebnisse in R-Multiples.
              </p>
            </div>
            <LogoutButton />
          </div>
        </header>

        {dashboard ? (
          dashboard.ok ? <DashboardContent data={dashboard.data} /> : <DashboardError message={dashboard.error} />
        ) : (
          <DashboardLoading />
        )}
      </section>
    </main>
  );
}

type DashboardResult = { ok: true; data: DashboardData } | { ok: false; error: string };

async function loadDashboardData(): Promise<DashboardResult> {
  try {
    const [watchlist, signals, trades, performance] = await Promise.all([
      fetchWatchlist(),
      fetchSignals(),
      fetchTrades(),
      fetchPerformanceSummary(),
    ]);

    return {
      ok: true,
      data: buildDashboardData(watchlist, signals, trades, performance),
    };
  } catch (error) {
    return {
      ok: false,
      error: error instanceof Error ? error.message : "Dashboard-Daten konnten nicht geladen werden.",
    };
  }
}

type DashboardData = {
  cards: DashboardCard[];
  hasAnyData: boolean;
  recentSignals: Signal[];
  openTrades: Trade[];
};

type DashboardCard = {
  label: string;
  value: string;
  detail: string;
  href: string;
  tone: string;
};

function buildDashboardData(
  watchlist: WatchlistItem[],
  signals: Signal[],
  trades: Trade[],
  performance: PerformanceSummary,
): DashboardData {
  const openTrades = trades.filter((trade) => trade.status !== "closed" && trade.status !== "reviewed");
  const reviewSignals = signals.filter((signal) => signal.status === "armed" || signal.status === "triggered");
  const triggeredSignals = signals.filter((signal) => signal.status === "triggered");

  return {
    cards: [
      {
        label: "Watchlist Items",
        value: String(watchlist.length),
        detail: watchlist.length === 0 ? "Noch keine Symbole" : "Aktive Analyse-Basis",
        href: "/watchlist",
        tone: "border-blue-400/40",
      },
      {
        label: "Signals To Review",
        value: String(reviewSignals.length),
        detail: `${triggeredSignals.length} triggered for manual review`,
        href: "/signals",
        tone: "border-yellow-400/40",
      },
      {
        label: "Open Trades",
        value: String(openTrades.length),
        detail: "Manuell dokumentierte Trades",
        href: "/trades",
        tone: "border-green-400/40",
      },
      {
        label: "Total R",
        value: formatR(performance.total_r),
        detail: `${performance.closed_trade_count} documented closes`,
        href: "/performance",
        tone: "border-slate-400/40",
      },
    ],
    hasAnyData: watchlist.length > 0 || signals.length > 0 || trades.length > 0,
    recentSignals: signals.slice(0, 3),
    openTrades: openTrades.slice(0, 3),
  };
}

function DashboardContent({ data }: { data: DashboardData }) {
  return (
    <>
      <section className="grid gap-4 md:grid-cols-4">
        {data.cards.map((card) => (
          <a
            key={card.label}
            className={`rounded-2xl border ${card.tone} bg-slate-950/70 p-5 hover:bg-slate-900/80`}
            href={card.href}
          >
            <p className="text-sm text-slate-400">{card.label}</p>
            <p className="mt-3 text-3xl font-semibold">{card.value}</p>
            <p className="mt-2 text-xs text-slate-500">{card.detail}</p>
          </a>
        ))}
      </section>

      {!data.hasAnyData ? <DashboardEmptyState /> : null}

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <WorkflowCard />
        <CockpitSnapshot data={data} />
      </section>
    </>
  );
}

function DashboardError({ message }: { message: string }) {
  return (
    <section className="rounded-3xl border border-red-400/30 bg-red-950/40 p-6">
      <h2 className="text-xl font-semibold text-red-100">Dashboard konnte nicht geladen werden</h2>
      <p className="mt-2 whitespace-pre-line text-sm text-red-100/80">{message}</p>
      <p className="mt-4 text-sm text-red-100/70">
        Pruefe, ob die API laeuft. Die Workflow-Links bleiben im Code unveraendert verfuegbar.
      </p>
    </section>
  );
}

function LogoutButton() {
  async function submitLogout() {
    await logout();
    window.location.href = "/login";
  }

  return (
    <button
      className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
      onClick={() => void submitLogout()}
      type="button"
    >
      Logout
    </button>
  );
}

function DashboardLoading() {
  return (
    <section className="grid gap-4 md:grid-cols-4">
      {["Watchlist", "Signals", "Trades", "Performance"].map((label) => (
        <article key={label} className="rounded-2xl border border-white/10 bg-slate-950/70 p-5">
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-semibold text-slate-600">...</p>
          <p className="mt-2 text-xs text-slate-600">Dashboard-Daten werden geladen</p>
        </article>
      ))}
    </section>
  );
}

function DashboardEmptyState() {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <h2 className="text-xl font-semibold">Noch keine Cockpit-Daten</h2>
      <p className="mt-2 max-w-2xl text-sm text-slate-400">
        Starte mit der Watchlist, importiere CSV-Daten und analysiere Setups. Das Dashboard zeigt
        danach gespeicherte Signal-Bewertungen, manuell geloggte Trades und dokumentierte R-Ergebnisse.
      </p>
      <a
        className="mt-5 inline-flex rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950"
        href="/watchlist"
      >
        Watchlist oeffnen
      </a>
    </section>
  );
}

function WorkflowCard() {
  return (
    <article className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
      <h2 className="text-xl font-semibold">MVP Workflows</h2>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {workflowAreas.map((area) => (
          <a
            key={area.label}
            className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 hover:border-emerald-300/50"
            href={area.href}
          >
            <p className="font-medium text-emerald-300">{area.label}</p>
            <p className="mt-1 text-sm text-slate-400">{area.description}</p>
          </a>
        ))}
      </div>
    </article>
  );
}

function CockpitSnapshot({ data }: { data: DashboardData }) {
  return (
    <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-950/20 p-6">
      <h2 className="text-xl font-semibold text-emerald-200">Cockpit Snapshot</h2>
      <SnapshotList
        title="Recent Signals"
        emptyText="Noch keine Signale."
        items={data.recentSignals.map(formatSignal)}
      />
      <SnapshotList
        title="Open Trades"
        emptyText="Keine offenen Trades."
        items={data.openTrades.map(formatTrade)}
      />
    </aside>
  );
}

function SnapshotList({
  title,
  emptyText,
  items,
}: {
  title: string;
  emptyText: string;
  items: string[];
}) {
  return (
    <div className="mt-5">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-emerald-100/80">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-emerald-50/60">{emptyText}</p>
      ) : (
        <ul className="mt-3 space-y-2 text-sm text-emerald-50/90">
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function formatSignal(signal: Signal) {
  return `${signal.symbol} / ${signal.status.replaceAll("_", " ")}`;
}

function formatTrade(trade: Trade) {
  return `${trade.symbol} / ${formatR(trade.result_r ?? trade.initial_risk_reward)}`;
}

function formatR(value: string | null) {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${parsed.toFixed(2)}R` : `${value}R`;
}
