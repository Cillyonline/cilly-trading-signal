"use client";

import { useEffect, useState } from "react";

import { fetchCurrentUser, redirectToLoginOnAuthError } from "@/lib/api";

type AuthStatus = "checking" | "authenticated";

export function useProtectedRoute(): AuthStatus {
  const [status, setStatus] = useState<AuthStatus>("checking");

  useEffect(() => {
    let isMounted = true;

    async function verifySession() {
      try {
        await fetchCurrentUser();
        if (isMounted) {
          setStatus("authenticated");
        }
      } catch (error) {
        if (!redirectToLoginOnAuthError(error)) {
          window.location.replace("/login");
        }
      }
    }

    void verifySession();

    return () => {
      isMounted = false;
    };
  }, []);

  return status;
}

export function ProtectedRouteLoading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-8 text-slate-100">
      <p className="text-sm text-slate-400">Session wird geprueft...</p>
    </main>
  );
}
