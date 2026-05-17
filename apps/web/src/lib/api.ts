import type { Signal, SignalReviewNoteUpdatePayload, SignalStatusUpdatePayload } from "@/types/signals";
import type { AlertEvent, TelegramTestMessageResult } from "@/types/alerts";
import type { AuthUser, LoginPayload } from "@/types/auth";
import type { CsvImportResult, MarketDataAnalysisResult } from "@/types/imports";
import type { PerformanceSummary } from "@/types/performance";
import type { RiskSettings, RiskSettingsUpdatePayload } from "@/types/settings";
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

const credentialedFetch: typeof fetch = (input, init) => fetch(input, { ...init, credentials: "include" });

export class ApiError extends Error {
  detail: unknown;
  status: number;

  constructor(message: string, detail: unknown, status: number) {
    super(message);
    this.name = "ApiError";
    this.detail = detail;
    this.status = status;
  }
}

export async function login(payload: LoginPayload): Promise<AuthUser> {
  const response = await credentialedFetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Login fehlgeschlagen."));
  }

  return response.json();
}

export async function logout(): Promise<void> {
  await credentialedFetch(`${API_BASE_URL}/auth/logout`, { method: "POST" });
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const response = await credentialedFetch(`${API_BASE_URL}/auth/me`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Nicht angemeldet.");
  }
  return response.json();
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/watchlist`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Watchlist konnte nicht geladen werden.");
  }
  return response.json();
}

export async function fetchSignals(): Promise<Signal[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/signals`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Signale konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchAlerts(): Promise<AlertEvent[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/alerts`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Alert Events konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchSignal(signalId: number): Promise<Signal> {
  const response = await credentialedFetch(`${API_BASE_URL}/signals/${signalId}`, { cache: "no-store" });
  if (response.status === 404) {
    throw new Error("Signal wurde nicht gefunden.");
  }
  if (!response.ok) {
    throw new Error("Signal konnte nicht geladen werden.");
  }
  return response.json();
}

export async function updateSignalStatus(
  signalId: number,
  payload: SignalStatusUpdatePayload,
): Promise<Signal> {
  const response = await credentialedFetch(`${API_BASE_URL}/signals/${signalId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Signal Status konnte nicht geaendert werden."));
  }

  return response.json();
}

export async function updateSignalReviewNote(
  signalId: number,
  payload: SignalReviewNoteUpdatePayload,
): Promise<Signal> {
  const response = await credentialedFetch(`${API_BASE_URL}/signals/${signalId}/review-note`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Review Note konnte nicht gespeichert werden."));
  }

  return response.json();
}

export async function importCsv(formData: FormData): Promise<CsvImportResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/imports/csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      formatApiError(body?.detail, "CSV-Import konnte nicht gespeichert werden."),
      body?.detail,
      response.status,
    );
  }

  return response.json();
}

export async function analyzeImport(seriesId: number): Promise<MarketDataAnalysisResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/imports/${seriesId}/analyze`, {
    method: "POST",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Analyse konnte nicht gestartet werden."));
  }

  return response.json();
}

export async function fetchTrades(): Promise<Trade[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/trades`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Trades konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchPerformanceSummary(): Promise<PerformanceSummary> {
  const response = await credentialedFetch(`${API_BASE_URL}/performance/summary`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Performance Summary konnte nicht geladen werden.");
  }
  return response.json();
}

export async function fetchRiskSettings(): Promise<RiskSettings> {
  const response = await credentialedFetch(`${API_BASE_URL}/settings`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Risk Settings konnten nicht geladen werden.");
  }
  return response.json();
}

export async function updateRiskSettings(payload: RiskSettingsUpdatePayload): Promise<RiskSettings> {
  const response = await credentialedFetch(`${API_BASE_URL}/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Risk Settings konnten nicht gespeichert werden."));
  }

  return response.json();
}

export async function sendTelegramTestMessage(): Promise<TelegramTestMessageResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/alerts/test-telegram`, {
    method: "POST",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Telegram Test konnte nicht gesendet werden."));
  }

  return response.json();
}

export async function fetchTrade(tradeId: number): Promise<TradeDetail> {
  const response = await credentialedFetch(`${API_BASE_URL}/trades/${tradeId}`, { cache: "no-store" });
  if (response.status === 404) {
    throw new Error("Trade wurde nicht gefunden.");
  }
  if (!response.ok) {
    throw new Error("Trade konnte nicht geladen werden.");
  }
  return response.json();
}

export async function createTrade(payload: TradeCreatePayload): Promise<Trade> {
  const response = await credentialedFetch(`${API_BASE_URL}/trades`, {
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
  const response = await credentialedFetch(`${API_BASE_URL}/trades/${tradeId}/events`, {
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
  const response = await credentialedFetch(`${API_BASE_URL}/trades/${tradeId}/close`, {
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
  const response = await credentialedFetch(`${API_BASE_URL}/trades/${tradeId}/journal`, {
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
