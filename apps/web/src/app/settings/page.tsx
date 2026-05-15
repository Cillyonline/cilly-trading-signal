"use client";

import { FormEvent, useEffect, useState } from "react";

import { fetchRiskSettings, updateRiskSettings } from "@/lib/api";
import type { RiskSettings, RiskSettingsUpdatePayload } from "@/types/settings";

type SettingsForm = {
  account_size: string;
  default_risk_percent: string;
  max_risk_percent: string;
  min_risk_reward: string;
  max_open_trades: string;
  base_currency: string;
};

const emptyForm: SettingsForm = {
  account_size: "",
  default_risk_percent: "1.00",
  max_risk_percent: "1.00",
  min_risk_reward: "2.00",
  max_open_trades: "5",
  base_currency: "EUR",
};

export default function SettingsPage() {
  const [form, setForm] = useState<SettingsForm>(emptyForm);
  const [settings, setSettings] = useState<RiskSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadSettings() {
    setIsLoading(true);
    setError(null);
    try {
      const loaded = await fetchRiskSettings();
      setSettings(loaded);
      setForm(formFromSettings(loaded));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unbekannter Fehler.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadSettings();
  }, []);

  async function submitSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSaving(true);
    try {
      const saved = await updateRiskSettings(payloadFromForm(form));
      setSettings(saved);
      setForm(formFromSettings(saved));
      setMessage("Risk Settings gespeichert. Sie gelten fuer neue manuell geloggte Trades.");
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unbekannter Fehler.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100">
      <section className="mx-auto flex max-w-5xl flex-col gap-8">
        <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,#047857,transparent_32%),rgba(255,255,255,0.05)] p-8">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Settings</p>
              <h1 className="mt-3 text-4xl font-semibold tracking-tight">Risk Settings</h1>
              <p className="mt-3 max-w-2xl text-slate-300">
                Lege dokumentarische Risikolimits fuer manuell erfasste Trades fest. Die App berechnet
                und validiert Risiken, platziert aber keine Orders und fuehrt keine Positionsgroessen aus.
              </p>
            </div>
            <a className="text-sm text-emerald-300 hover:text-emerald-200" href="/">
              Zurueck zum Dashboard
            </a>
          </div>
        </header>

        {error ? <Notice tone="error" message={error} /> : null}
        {message ? <Notice tone="success" message={message} /> : null}

        <section className="grid gap-6 lg:grid-cols-[1fr_0.85fr]">
          <form onSubmit={submitSettings} className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div>
              <h2 className="text-xl font-semibold">Limits bearbeiten</h2>
              <p className="mt-2 text-sm text-slate-400">
                Diese Werte pruefen neue Trade-Logs. Bestehende Trades werden nicht rueckwirkend geaendert.
              </p>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <NumberField
                label="Account Size optional"
                value={form.account_size}
                onChange={(value) => setForm({ ...form, account_size: value })}
              />
              <TextField
                label="Base Currency"
                value={form.base_currency}
                onChange={(value) => setForm({ ...form, base_currency: value.toUpperCase() })}
              />
              <NumberField
                label="Default Risk %"
                value={form.default_risk_percent}
                onChange={(value) => setForm({ ...form, default_risk_percent: value })}
              />
              <NumberField
                label="Max Risk %"
                value={form.max_risk_percent}
                onChange={(value) => setForm({ ...form, max_risk_percent: value })}
              />
              <NumberField
                label="Min R:R"
                value={form.min_risk_reward}
                onChange={(value) => setForm({ ...form, min_risk_reward: value })}
              />
              <NumberField
                label="Max Open Trades"
                value={form.max_open_trades}
                onChange={(value) => setForm({ ...form, max_open_trades: value })}
              />
            </div>

            <button
              disabled={isLoading || isSaving}
              type="submit"
              className="mt-6 rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
            >
              {isSaving ? "Speichere..." : "Risk Settings speichern"}
            </button>
          </form>

          <aside className="rounded-3xl border border-white/10 bg-slate-900/70 p-6">
            <h2 className="text-xl font-semibold">Aktuelle Wirkung</h2>
            <p className="mt-2 text-sm text-slate-400">
              Neue Trades werden abgelehnt, wenn Min R:R, Max Risk % oder Max Open Trades verletzt werden.
            </p>
            <div className="mt-6 grid gap-3">
              <Metric label="Account Size" value={formatOptionalMoney(settings?.account_size, settings?.base_currency)} />
              <Metric label="Default Risk" value={settings ? `${settings.default_risk_percent}%` : "-"} />
              <Metric label="Max Risk" value={settings ? `${settings.max_risk_percent}%` : "-"} />
              <Metric label="Min R:R" value={settings ? `${settings.min_risk_reward}R` : "-"} />
              <Metric label="Max Open Trades" value={settings ? settings.max_open_trades.toString() : "-"} />
            </div>
          </aside>
        </section>
      </section>
    </main>
  );
}

function formFromSettings(settings: RiskSettings): SettingsForm {
  return {
    account_size: settings.account_size ?? "",
    default_risk_percent: settings.default_risk_percent,
    max_risk_percent: settings.max_risk_percent,
    min_risk_reward: settings.min_risk_reward,
    max_open_trades: settings.max_open_trades.toString(),
    base_currency: settings.base_currency,
  };
}

function payloadFromForm(form: SettingsForm): RiskSettingsUpdatePayload {
  return {
    account_size: form.account_size || null,
    default_risk_percent: form.default_risk_percent,
    max_risk_percent: form.max_risk_percent,
    min_risk_reward: form.min_risk_reward,
    max_open_trades: Number(form.max_open_trades),
    base_currency: form.base_currency,
  };
}

function NumberField({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <input
        required={!label.includes("optional")}
        type="number"
        min="0"
        step="0.01"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
      />
    </label>
  );
}

function TextField({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label className="grid gap-2 text-sm text-slate-300">
      {label}
      <input
        required
        value={value}
        maxLength={3}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-xl border border-white/10 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
      />
    </label>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-semibold text-slate-100">{value}</p>
    </div>
  );
}

function Notice({ message, tone }: { message: string; tone: "error" | "success" }) {
  const classes = tone === "error" ? "border-red-400/30 bg-red-950/40 text-red-100" : "border-emerald-300/30 bg-emerald-300/10 text-emerald-50";
  return <div className={`whitespace-pre-line rounded-2xl border p-4 text-sm ${classes}`}>{message}</div>;
}

function formatOptionalMoney(value: string | null | undefined, currency: string | undefined) {
  if (!value) {
    return "Nicht gesetzt";
  }
  return `${Number(value).toLocaleString("de-DE", { maximumFractionDigits: 2 })} ${currency ?? ""}`.trim();
}
