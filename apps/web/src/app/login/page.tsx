"use client";

import { FormEvent, useState } from "react";

import { login } from "@/lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      await login({ email, password });
      window.location.href = "/";
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : "Login fehlgeschlagen.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-8 text-slate-100">
      <form onSubmit={submitLogin} className="w-full max-w-md rounded-3xl border border-white/10 bg-white/[0.03] p-8">
        <p className="text-sm uppercase tracking-[0.35em] text-emerald-300">Login</p>
        <h1 className="mt-3 text-3xl font-semibold">Cilly Trading Signal</h1>
        <p className="mt-3 text-sm text-slate-400">
          Single-User MVP Login. Die Session wird als HttpOnly Cookie gespeichert, nicht im Browser Storage.
        </p>

        {error ? <p className="mt-5 rounded-2xl border border-red-400/30 bg-red-950/40 p-4 text-sm text-red-100">{error}</p> : null}

        <div className="mt-6 grid gap-4">
          <label className="grid gap-2 text-sm text-slate-300">
            E-Mail
            <input
              required
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            />
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Passwort
            <input
              required
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="rounded-xl border border-white/10 bg-slate-900 px-4 py-3 text-slate-100 outline-none focus:border-emerald-300"
            />
          </label>
          <button
            disabled={isLoading}
            type="submit"
            className="rounded-xl bg-emerald-400 px-5 py-3 font-semibold text-slate-950 disabled:opacity-60"
          >
            {isLoading ? "Melde an..." : "Anmelden"}
          </button>
        </div>
      </form>
    </main>
  );
}
