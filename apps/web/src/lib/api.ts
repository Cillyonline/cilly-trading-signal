import type { Signal } from "@/types/signals";
import type { CsvImportResult, MarketDataAnalysisResult } from "@/types/imports";
import type {
  JournalEntry,
  JournalEntryCreatePayload,
  Trade,
  TradeClosePayload,
  TradeCreatePayload,
  TradeDetail,
  TradeEvent,
  TradeEventCreatePayload,
} from "@/types/trades";
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

export async function fetchSignal(signalId: number): Promise<Signal> {
  const response = await fetch(`${API_BASE_URL}/signals/${signalId}`, { cache: "no-store" });
  if (response.status === 404) {
    throw new Error("Signal wurde nicht gefunden.");
  }
  if (!response.ok) {
    throw new Error("Signal konnte nicht geladen werden.");
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

export async function analyzeImport(seriesId: number): Promise<MarketDataAnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/imports/${seriesId}/analyze`, {
    method: "POST",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Analyse konnte nicht gestartet werden."));
  }

  return response.json();
}

export async function fetchTrades(): Promise<Trade[]> {
  const response = await fetch(`${API_BASE_URL}/trades`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Trades konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchTrade(tradeId: number): Promise<TradeDetail> {
  const response = await fetch(`${API_BASE_URL}/trades/${tradeId}`, { cache: "no-store" });
  if (response.status === 404) {
    throw new Error("Trade wurde nicht gefunden.");
  }
  if (!response.ok) {
    throw new Error("Trade konnte nicht geladen werden.");
  }
  return response.json();
}

export async function createTrade(payload: TradeCreatePayload): Promise<Trade> {
  const response = await fetch(`${API_BASE_URL}/trades`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Trade konnte nicht gespeichert werden."));
  }

  return response.json();
}

export async function createTradeEvent(tradeId: number, payload: TradeEventCreatePayload): Promise<TradeEvent> {
  const response = await fetch(`${API_BASE_URL}/trades/${tradeId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Trade Event konnte nicht gespeichert werden."));
  }

  return response.json();
}

export async function closeTrade(tradeId: number, payload: TradeClosePayload): Promise<TradeDetail> {
  const response = await fetch(`${API_BASE_URL}/trades/${tradeId}/close`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Trade konnte nicht geschlossen werden."));
  }

  return response.json();
}

export async function createJournalEntry(tradeId: number, payload: JournalEntryCreatePayload): Promise<JournalEntry> {
  const response = await fetch(`${API_BASE_URL}/trades/${tradeId}/journal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Journal Review konnte nicht gespeichert werden."));
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
        const error = item as {
          loc?: unknown[];
          msg?: string;
          row?: number | null;
          field?: string | null;
          message?: string;
        };
        const location = [
          error.row ? `Zeile ${error.row}` : null,
          error.field,
          Array.isArray(error.loc) ? error.loc.filter((part) => part !== "body").join(" / ") : null,
        ]
          .filter(Boolean)
          .join(" / ");
        return [location, error.message ?? error.msg].filter(Boolean).join(": ");
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join("\n");
    }
  }

  return fallback;
}
