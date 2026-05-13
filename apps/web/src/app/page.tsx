const dashboardCards = [
  { label: "Open Trades", value: "0", tone: "border-blue-400/40" },
  { label: "Armed Setups", value: "0", tone: "border-yellow-400/40" },
  { label: "Triggered Today", value: "0", tone: "border-green-400/40" },
  { label: "Total R", value: "0.0R", tone: "border-slate-400/40" },
];

const plannedAreas = [
  "Watchlist",
  "CSV Import",
  "Signals",
  "Trades",
  "Journal",
  "Performance",
  "Settings",
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#172554,transparent_32%),#050816] px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-white/5 p-8 shadow-2xl shadow-black/30 backdrop-blur">
          <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Cilly Trading Signal</p>
          <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
            Trading-Cockpit fuer Long-only Swingtrading.
          </h1>
          <p className="mt-5 max-w-2xl text-lg text-slate-300">
            Kontext, Setup, Trigger und Risiko werden getrennt bewertet. Keine automatische
            Orderausfuehrung, sondern klare Signal-Karten, manuelles Trade Logging und Performance
            in R-Multiples.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-4">
          {dashboardCards.map((card) => (
            <article key={card.label} className={`rounded-2xl border ${card.tone} bg-slate-950/70 p-5`}>
              <p className="text-sm text-slate-400">{card.label}</p>
              <p className="mt-3 text-3xl font-semibold">{card.value}</p>
            </article>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <article className="rounded-3xl border border-white/10 bg-slate-950/70 p-6">
            <h2 className="text-xl font-semibold">MVP Fokus</h2>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {plannedAreas.map((area) => (
                <div key={area} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                  {area === "Watchlist" ? (
                    <a className="font-medium text-emerald-300 hover:text-emerald-200" href="/watchlist">
                      {area}
                    </a>
                  ) : (
                    <p className="font-medium">{area}</p>
                  )}
                  <p className="mt-1 text-sm text-slate-400">Geplant fuer den MVP-Aufbau.</p>
                </div>
              ))}
            </div>
          </article>

          <aside className="rounded-3xl border border-emerald-400/20 bg-emerald-950/20 p-6">
            <h2 className="text-xl font-semibold text-emerald-200">Strategie-Standard</h2>
            <ul className="mt-5 space-y-3 text-sm text-emerald-50/90">
              <li>1W Kontext</li>
              <li>1D Setup</li>
              <li>4H Trigger und Management</li>
              <li>Trend Pullback Long</li>
              <li>Base Breakout Long</li>
              <li>Minimum R:R 1:2</li>
            </ul>
          </aside>
        </section>
      </section>
    </main>
  );
}
