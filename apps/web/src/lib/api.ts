import type { Signal } from "@/types/signals";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function fetchSignals(): Promise<Signal[]> {
  const response = await fetch(`${API_BASE_URL}/signals`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Signale konnten nicht geladen werden.");
  }
  return response.json();
}
