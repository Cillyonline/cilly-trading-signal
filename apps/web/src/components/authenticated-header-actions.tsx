"use client";

import { logout } from "@/lib/api";

type HeaderLink = {
  href: string;
  label: string;
};

type AuthenticatedHeaderActionsProps = {
  links?: HeaderLink[];
  showDashboard?: boolean;
  tone?: "emerald" | "violet";
};

export function AuthenticatedHeaderActions({
  links = [],
  showDashboard = true,
  tone = "emerald",
}: AuthenticatedHeaderActionsProps) {
  async function submitLogout() {
    await logout();
    window.location.href = "/login";
  }

  const linkClass = tone === "violet" ? "text-violet-300 hover:text-violet-200" : "text-emerald-300 hover:text-emerald-200";

  return (
    <div className="flex flex-wrap items-center gap-3 text-sm">
      {links.map((link) => (
        <a key={link.href} className={linkClass} href={link.href}>
          {link.label}
        </a>
      ))}
      {showDashboard ? (
        <a className={linkClass} href="/">
          Dashboard
        </a>
      ) : null}
      <button
        className="rounded-xl border border-white/10 px-4 py-2 text-sm text-slate-200 hover:border-emerald-300/50"
        onClick={() => void submitLogout()}
        type="button"
      >
        Logout
      </button>
    </div>
  );
}
