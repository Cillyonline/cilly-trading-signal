"use client";

import { useEffect } from "react";

import { ProtectedRouteLoading, useProtectedRoute } from "@/lib/auth-guard";

export default function ImportsRedirectPage() {
  const authStatus = useProtectedRoute();

  useEffect(() => {
    if (authStatus === "authenticated") {
      window.location.replace("/import");
    }
  }, [authStatus]);

  return <ProtectedRouteLoading />;
}
