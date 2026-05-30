import type { Signal, SignalReviewNoteUpdatePayload, SignalStatusUpdatePayload } from "@/types/signals";
import type { AlertEvent, TelegramTestMessageResult } from "@/types/alerts";
import type { AuthUser, LoginPayload } from "@/types/auth";
import type {
  CsvImportResult,
  ImportHistoryItem,
  MarketDataAnalysisResult,
  MarketDataSyncRequest,
  MarketDataSyncResult,
} from "@/types/imports";
import type { PerformanceSummary } from "@/types/performance";
import type { ReviewBatch, ReviewBatchCreatePayload, ReviewEntry, ReviewEntryCreatePayload } from "@/types/reviews";
import type {
  ScreenerImport,
  ScreenerResult,
  ScreenerResultBulkStatusPayload,
  ScreenerResultBulkStatusResult,
  ScreenerResultFilters,
  ScreenerResultPage,
} from "@/types/screener";
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
  TradeFilters,
} from "@/types/trades";
import type { BenchmarkContextStatus, WatchlistItem } from "@/types/watchlist";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

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

export class AuthenticationRequiredError extends Error {
  constructor(message = "Login erforderlich.") {
    super(message);
    this.name = "AuthenticationRequiredError";
  }
}

export function isAuthenticationRequiredError(error: unknown): error is AuthenticationRequiredError {
  return error instanceof AuthenticationRequiredError;
}

export function isUnauthorizedStatus(status: number): boolean {
  return status === 401 || status === 403;
}

export function assertAuthenticatedResponse(response: Response): void {
  if (isUnauthorizedStatus(response.status)) {
    throw new AuthenticationRequiredError();
  }
}

export function redirectToLoginOnAuthError(error: unknown): boolean {
  if (!isAuthenticationRequiredError(error)) {
    return false;
  }

  window.location.replace("/login");
  return true;
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
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Nicht angemeldet.");
  }
  return response.json();
}

export async function fetchWatchlist(): Promise<WatchlistItem[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/watchlist`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Watchlist konnte nicht geladen werden.");
  }
  return response.json();
}

export async function fetchBenchmarkContextStatus(): Promise<BenchmarkContextStatus[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/watchlist/benchmark-context`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Benchmark-Kontext konnte nicht geladen werden.");
  }
  return response.json();
}

export async function fetchSignals(): Promise<Signal[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/signals`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Signale konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchAlerts(): Promise<AlertEvent[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/alerts`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
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
  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

export async function fetchImportHistory(): Promise<ImportHistoryItem[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/imports`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Import-Historie konnte nicht geladen werden.");
  }
  return response.json();
}

export async function analyzeImport(seriesId: number): Promise<MarketDataAnalysisResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/imports/${seriesId}/analyze`, {
    method: "POST",
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Analyse konnte nicht gestartet werden."));
  }

  return response.json();
}

export async function syncMarketData(payload: MarketDataSyncRequest): Promise<MarketDataSyncResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/imports/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Provider-Sync konnte nicht gestartet werden."));
  }

  return response.json();
}

export async function importScreenerCsv(formData: FormData): Promise<ScreenerImport> {
  const response = await credentialedFetch(`${API_BASE_URL}/screener/imports`, {
    method: "POST",
    body: formData,
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new ApiError(
      formatApiError(body?.detail, "Screener CSV konnte nicht gespeichert werden."),
      body?.detail,
      response.status,
    );
  }

  return response.json();
}

export async function fetchScreenerImports(): Promise<ScreenerImport[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/screener/imports`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Screener-Importe konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchScreenerResults(filters: ScreenerResultFilters = {}): Promise<ScreenerResult[]> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  }
  const query = params.toString();
  const response = await credentialedFetch(`${API_BASE_URL}/screener/results${query ? `?${query}` : ""}`, {
    cache: "no-store",
  });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Screener-Kandidaten konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchScreenerResultPage(filters: ScreenerResultFilters = {}): Promise<ScreenerResultPage> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  }
  const query = params.toString();
  const response = await credentialedFetch(`${API_BASE_URL}/screener/results/page${query ? `?${query}` : ""}`, {
    cache: "no-store",
  });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Screener-Kandidaten konnten nicht geladen werden.");
  }
  return response.json();
}

export async function updateScreenerResultStatuses(
  payload: ScreenerResultBulkStatusPayload,
): Promise<ScreenerResultBulkStatusResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/screener/results/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Screener-Status konnte nicht aktualisiert werden."));
  }

  return response.json();
}

export async function addScreenerResultToWatchlist(resultId: number): Promise<ScreenerResult> {
  const response = await credentialedFetch(`${API_BASE_URL}/screener/results/${resultId}/watchlist`, {
    method: "POST",
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Kandidat konnte nicht zur Watchlist hinzugefuegt werden."));
  }

  return response.json();
}

export async function fetchTrades(filters: TradeFilters = {}): Promise<Trade[]> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  }
  const query = params.toString();
  const response = await credentialedFetch(`${API_BASE_URL}/trades${query ? `?${query}` : ""}`, {
    cache: "no-store",
  });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Trades konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchPerformanceSummary(): Promise<PerformanceSummary> {
  const response = await credentialedFetch(`${API_BASE_URL}/performance/summary`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Performance Summary konnte nicht geladen werden.");
  }
  return response.json();
}

export async function fetchReviewBatches(): Promise<ReviewBatch[]> {
  const response = await credentialedFetch(`${API_BASE_URL}/reviews/batches`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Review-Batches konnten nicht geladen werden.");
  }
  return response.json();
}

export async function fetchReviewBatch(batchId: number): Promise<ReviewBatch> {
  const response = await credentialedFetch(`${API_BASE_URL}/reviews/batches/${batchId}`, { cache: "no-store" });
  if (response.status === 404) {
    throw new Error("Review-Batch wurde nicht gefunden.");
  }
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Review-Batch konnte nicht geladen werden.");
  }
  return response.json();
}

export async function exportReviewBatchCsv(batchId: number): Promise<void> {
  const response = await credentialedFetch(`${API_BASE_URL}/reviews/batches/${batchId}/export`, { cache: "no-store" });
  if (response.status === 404) {
    throw new Error("Review-Batch wurde nicht gefunden.");
  }
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Review-Batch Export konnte nicht geladen werden.");
  }
  const blob = await response.blob();
  _triggerDownload(blob, `review-batch-${batchId}.csv`);
}

export async function createReviewBatch(payload: ReviewBatchCreatePayload): Promise<ReviewBatch> {
  const response = await credentialedFetch(`${API_BASE_URL}/reviews/batches`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Review-Batch konnte nicht gespeichert werden."));
  }

  return response.json();
}

export async function createReviewEntry(batchId: number, payload: ReviewEntryCreatePayload): Promise<ReviewEntry> {
  const response = await credentialedFetch(`${API_BASE_URL}/reviews/batches/${batchId}/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Review-Eintrag konnte nicht gespeichert werden."));
  }

  return response.json();
}

export async function fetchRiskSettings(): Promise<RiskSettings> {
  const response = await credentialedFetch(`${API_BASE_URL}/settings`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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
  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
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

  assertAuthenticatedResponse(response);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatApiError(body?.detail, "Journal Review konnte nicht gespeichert werden."));
  }

  return response.json();
}

export async function exportTradesCsv(): Promise<void> {
  const response = await credentialedFetch(`${API_BASE_URL}/export/trades`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Trade-Export konnte nicht geladen werden.");
  }
  const blob = await response.blob();
  _triggerDownload(blob, "trades.csv");
}

export async function exportPerformanceCsv(): Promise<void> {
  const response = await credentialedFetch(`${API_BASE_URL}/export/performance`, { cache: "no-store" });
  assertAuthenticatedResponse(response);
  if (!response.ok) {
    throw new Error("Performance-Export konnte nicht geladen werden.");
  }
  const blob = await response.blob();
  _triggerDownload(blob, "performance.csv");
}

function _triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
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
