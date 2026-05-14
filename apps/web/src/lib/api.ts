import type { Signal } from "@/types/signals";
import type { CsvImportResult } from "@/types/imports";
import type { WatchlistItem } from "@/types/watchlist";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const response = await fetch(`${API_BASE_URL}/watchlist`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Watchlist konnte nicht geladen werden.");
  }
  return response.json();
}

export async function fetchSignals(): Promise<Signal[]> {
  const response = await fetch(`${API_BASE_URL}/signals`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Signale konnten nicht geladen werden.");
  }
  return response.json();
}

export async function importCsv(formData: FormData): Promise<CsvImportResult> {
  const response = await fetch(`${API_BASE_URL}/imports/csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "CSV-Import konnte nicht gespeichert werden."));
  }

  return response.json();
}

function formatApiError(detail: unknown, fallback: string) {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (!item || typeof item !== "object") {
          return null;
        }
        const error = item as { row?: number | null; field?: string | null; message?: string };
        const location = [error.row ? `Zeile ${error.row}` : null, error.field].filter(Boolean).join(" / ");
        return [location, error.message].filter(Boolean).join(": ");
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join("\n");
    }
  }

  return fallback;
}
