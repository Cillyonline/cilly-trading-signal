from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataSyncStatus,
    Timeframe,
)
from app.models.market_data import MarketDataCandle, MarketDataSeries

FRESHNESS_WINDOWS = {
    Timeframe.ONE_WEEK: timedelta(days=14),
    Timeframe.ONE_DAY: timedelta(days=3),
    Timeframe.FOUR_HOURS: timedelta(hours=24),
}
ALPHA_VANTAGE_DAILY_URL = "https://www.alphavantage.co/query"
TWELVE_DATA_TIME_SERIES_URL = "https://api.twelvedata.com/time_series"


@dataclass(frozen=True)
class MarketDataSyncPlan:
    symbol: str
    timeframe: Timeframe
    provider_name: str | None
    provider_symbol: str | None = None
    provider_exchange: str | None = None
    provider_timeframe: str | None = None
    enabled: bool = False


@dataclass(frozen=True)
class ProviderTimeframeCapability:
    timeframe: Timeframe
    supported: bool
    reason: str


@dataclass(frozen=True)
class MarketDataSyncResult:
    sync_status: MarketDataSyncStatus
    freshness_status: MarketDataFreshnessStatus
    provider_name: str | None = None
    provider_symbol: str | None = None
    provider_exchange: str | None = None
    provider_timeframe: str | None = None
    data_end_at: datetime | None = None
    candles: tuple["ProviderCandle", ...] = ()
    error_code: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class ProviderCandle:
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class MarketDataProvider(Protocol):
    def sync(self, plan: MarketDataSyncPlan) -> MarketDataSyncResult:
        pass


class NoopMarketDataProvider:
    def sync(self, plan: MarketDataSyncPlan) -> MarketDataSyncResult:
        return MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SKIPPED,
            freshness_status=MarketDataFreshnessStatus.UNKNOWN,
            provider_name=plan.provider_name,
            provider_symbol=plan.provider_symbol,
            provider_exchange=plan.provider_exchange,
            provider_timeframe=plan.provider_timeframe,
            error_code="provider_not_configured",
            error_message="Market data provider sync is not configured.",
        )


class AlphaVantageDailyProvider:
    def __init__(
        self,
        api_key: str,
        *,
        transport: "ProviderTransport | None" = None,
    ) -> None:
        self.api_key = api_key
        self.transport = transport or UrllibProviderTransport()

    def sync(self, plan: MarketDataSyncPlan) -> MarketDataSyncResult:
        unsupported_reason = unsupported_timeframe_reason(plan)
        if unsupported_reason is not None:
            return provider_failure(
                plan,
                "unsupported_timeframe",
                unsupported_reason,
            )

        try:
            payload = self.transport.get_json(build_alpha_vantage_daily_url(plan, self.api_key))
        except ProviderTransportError:
            return provider_failure(plan, "provider_transport_error")

        candles, error_code = parse_alpha_vantage_daily_response(payload)
        if error_code is not None:
            return provider_failure(plan, error_code)
        if not candles:
            return MarketDataSyncResult(
                sync_status=MarketDataSyncStatus.PARTIAL,
                freshness_status=MarketDataFreshnessStatus.PARTIAL,
                provider_name=plan.provider_name,
                provider_symbol=plan.provider_symbol,
                provider_exchange=plan.provider_exchange,
                provider_timeframe=plan.provider_timeframe,
                error_code="provider_empty_response",
                error_message=provider_failure_message("provider_empty_response"),
            )

        latest_timestamp = max(candle.timestamp for candle in candles)
        return MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SUCCESS,
            freshness_status=evaluate_timestamp_freshness(latest_timestamp, plan.timeframe),
            provider_name=plan.provider_name,
            provider_symbol=plan.provider_symbol,
            provider_exchange=plan.provider_exchange,
            provider_timeframe=plan.provider_timeframe,
            data_end_at=latest_timestamp,
            candles=tuple(candles),
        )


class TwelveDataProvider:
    def __init__(
        self,
        api_key: str,
        *,
        transport: "ProviderTransport | None" = None,
    ) -> None:
        self.api_key = api_key
        self.transport = transport or UrllibProviderTransport()

    def sync(self, plan: MarketDataSyncPlan) -> MarketDataSyncResult:
        unsupported_reason = unsupported_timeframe_reason(plan)
        if unsupported_reason is not None:
            return provider_failure(
                plan,
                "unsupported_timeframe",
                unsupported_reason,
            )

        try:
            payload = self.transport.get_json(build_twelve_data_url(plan, self.api_key))
        except ProviderTransportError:
            return provider_failure(plan, "provider_transport_error")

        candles, error_code = parse_twelve_data_response(payload)
        if error_code is not None:
            return provider_failure(plan, error_code)
        if not candles:
            return MarketDataSyncResult(
                sync_status=MarketDataSyncStatus.PARTIAL,
                freshness_status=MarketDataFreshnessStatus.PARTIAL,
                provider_name=plan.provider_name,
                provider_symbol=plan.provider_symbol,
                provider_exchange=plan.provider_exchange,
                provider_timeframe=plan.provider_timeframe,
                error_code="provider_empty_response",
                error_message=provider_failure_message("provider_empty_response"),
            )

        latest_timestamp = max(candle.timestamp for candle in candles)
        return MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SUCCESS,
            freshness_status=evaluate_timestamp_freshness(latest_timestamp, plan.timeframe),
            provider_name=plan.provider_name,
            provider_symbol=plan.provider_symbol,
            provider_exchange=plan.provider_exchange,
            provider_timeframe=plan.provider_timeframe,
            data_end_at=latest_timestamp,
            candles=tuple(candles),
        )


class ProviderTransport(Protocol):
    def get_json(self, url: str) -> object:
        pass


class ProviderTransportError(Exception):
    pass


class UrllibProviderTransport:
    def get_json(self, url: str) -> object:
        import json

        try:
            with urlopen(url, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            raise ProviderTransportError from error


def build_alpha_vantage_daily_url(plan: MarketDataSyncPlan, api_key: str) -> str:
    params = urlencode(
        {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": plan.provider_symbol or plan.symbol,
            "apikey": api_key,
            "outputsize": "compact",
        }
    )
    return f"{ALPHA_VANTAGE_DAILY_URL}?{params}"


def build_twelve_data_url(plan: MarketDataSyncPlan, api_key: str) -> str:
    params = urlencode(
        {
            "symbol": plan.provider_symbol or plan.symbol,
            "interval": _twelve_data_interval(plan.timeframe),
            "outputsize": "5000",
            "apikey": api_key,
        }
    )
    return f"{TWELVE_DATA_TIME_SERIES_URL}?{params}"


def _twelve_data_interval(timeframe: Timeframe) -> str:
    mapping = {
        Timeframe.ONE_WEEK: "1week",
        Timeframe.ONE_DAY: "1day",
        Timeframe.FOUR_HOURS: "4h",
    }
    return mapping[timeframe]


def parse_twelve_data_response(payload: object) -> tuple[list[ProviderCandle], str | None]:
    if not isinstance(payload, dict):
        return [], "provider_invalid_response"
    if payload.get("status") == "error":
        code = payload.get("code")
        if code == 429:
            return [], "provider_rate_limited"
        if code in {400, 404}:
            return [], "provider_symbol_or_entitlement"
        return [], "provider_error"

    raw_values = payload.get("values")
    if not isinstance(raw_values, list):
        return [], "provider_invalid_response"

    candles: list[ProviderCandle] = []
    for raw_candle in raw_values:
        if not isinstance(raw_candle, dict):
            return [], "provider_invalid_response"
        try:
            candles.append(
                ProviderCandle(
                    timestamp=datetime.fromisoformat(raw_candle["datetime"]).replace(tzinfo=UTC),
                    open=_decimal_field(raw_candle, "open"),
                    high=_decimal_field(raw_candle, "high"),
                    low=_decimal_field(raw_candle, "low"),
                    close=_decimal_field(raw_candle, "close"),
                    volume=_decimal_field(raw_candle, "volume"),
                )
            )
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return [], "provider_invalid_response"
    return candles, None


def parse_alpha_vantage_daily_response(payload: object) -> tuple[list[ProviderCandle], str | None]:
    if not isinstance(payload, dict):
        return [], "provider_invalid_response"
    if "Error Message" in payload:
        return [], "provider_error"
    if "Note" in payload or "Information" in payload:
        return [], "provider_rate_limited"

    raw_series = payload.get("Time Series (Daily)")
    if not isinstance(raw_series, dict):
        return [], "provider_invalid_response"

    candles: list[ProviderCandle] = []
    for date_text, raw_candle in raw_series.items():
        if not isinstance(date_text, str) or not isinstance(raw_candle, dict):
            return [], "provider_invalid_response"
        try:
            candles.append(
                ProviderCandle(
                    timestamp=datetime.fromisoformat(date_text).replace(tzinfo=UTC),
                    open=_decimal_field(raw_candle, "1. open"),
                    high=_decimal_field(raw_candle, "2. high"),
                    low=_decimal_field(raw_candle, "3. low"),
                    close=_decimal_field(raw_candle, "4. close"),
                    volume=_decimal_field(raw_candle, "6. volume"),
                )
            )
        except (InvalidOperation, KeyError, TypeError, ValueError):
            return [], "provider_invalid_response"
    return candles, None


def build_market_data_sync_plan(
    *,
    symbol: str,
    timeframe: Timeframe,
    provider_sync_enabled: bool,
    provider_name: str | None,
    provider_symbol: str | None = None,
    provider_exchange: str | None = None,
    provider_timeframe: str | None = None,
) -> MarketDataSyncPlan:
    return MarketDataSyncPlan(
        symbol=symbol.strip().upper(),
        timeframe=timeframe,
        provider_name=provider_name.strip().lower() if provider_name else None,
        provider_symbol=(provider_symbol or symbol).strip().upper(),
        provider_exchange=provider_exchange.strip().upper() if provider_exchange else None,
        provider_timeframe=provider_timeframe.strip() if provider_timeframe else timeframe.value,
        enabled=provider_sync_enabled,
    )


def provider_timeframe_capabilities(
    provider_name: str | None,
) -> tuple[ProviderTimeframeCapability, ...]:
    normalized = provider_name.strip().lower() if provider_name else None
    if normalized == "alpha_vantage":
        return (
            ProviderTimeframeCapability(
                timeframe=Timeframe.ONE_WEEK,
                supported=False,
                reason=(
                    "Alpha Vantage first path does not support weekly sync here; "
                    "use CSV fallback."
                ),
            ),
            ProviderTimeframeCapability(
                timeframe=Timeframe.ONE_DAY,
                supported=True,
                reason="Guarded Daily/EOD sync path is supported for configured symbols.",
            ),
            ProviderTimeframeCapability(
                timeframe=Timeframe.FOUR_HOURS,
                supported=False,
                reason=(
                    "4H/intraday provider sync is not selected; "
                    "use TradingView CSV fallback."
                ),
            ),
        )

    if normalized == "twelve_data":
        return (
            ProviderTimeframeCapability(
                timeframe=Timeframe.ONE_WEEK,
                supported=True,
                reason="Twelve Data supports weekly sync for configured symbols.",
            ),
            ProviderTimeframeCapability(
                timeframe=Timeframe.ONE_DAY,
                supported=True,
                reason="Twelve Data supports Daily/EOD sync for configured symbols.",
            ),
            ProviderTimeframeCapability(
                timeframe=Timeframe.FOUR_HOURS,
                supported=True,
                reason="Twelve Data supports 4H sync for configured symbols.",
            ),
        )

    return tuple(
        ProviderTimeframeCapability(
            timeframe=timeframe,
            supported=False,
            reason="No configured provider capability for this timeframe.",
        )
        for timeframe in (Timeframe.ONE_WEEK, Timeframe.ONE_DAY, Timeframe.FOUR_HOURS)
    )


def unsupported_timeframe_reason(plan: MarketDataSyncPlan) -> str | None:
    capabilities = provider_timeframe_capabilities(plan.provider_name)
    for capability in capabilities:
        if capability.timeframe == plan.timeframe:
            return None if capability.supported else capability.reason
    return "Provider capability for this timeframe is unknown."


def sync_market_data_series(
    series: MarketDataSeries,
    plan: MarketDataSyncPlan,
    provider: MarketDataProvider | None = None,
    *,
    now: datetime | None = None,
) -> MarketDataSyncResult:
    completed_at = now or datetime.now(UTC)
    if not plan.enabled:
        result = MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SKIPPED,
            freshness_status=evaluate_market_data_freshness(series, completed_at),
            provider_name=plan.provider_name,
            provider_symbol=plan.provider_symbol,
            provider_exchange=plan.provider_exchange,
            provider_timeframe=plan.provider_timeframe,
            data_end_at=series.end_time,
            error_code="sync_disabled",
            error_message="Market data provider sync is disabled.",
        )
        apply_market_data_sync_result(series, result, completed_at)
        return result

    unsupported_reason = unsupported_timeframe_reason(plan)
    if unsupported_reason is not None:
        result = provider_failure(plan, "unsupported_timeframe", unsupported_reason)
        apply_market_data_sync_result(series, result, completed_at)
        return result

    result = (provider or NoopMarketDataProvider()).sync(plan)
    apply_market_data_sync_result(series, result, completed_at)
    return result


def sync_and_persist_market_data_series(
    db: Session,
    series: MarketDataSeries,
    plan: MarketDataSyncPlan,
    provider: MarketDataProvider | None = None,
    *,
    now: datetime | None = None,
) -> MarketDataSyncResult:
    completed_at = now or datetime.now(UTC)
    if not plan.enabled:
        result = MarketDataSyncResult(
            sync_status=MarketDataSyncStatus.SKIPPED,
            freshness_status=evaluate_market_data_freshness(series, completed_at),
            provider_name=plan.provider_name,
            provider_symbol=plan.provider_symbol,
            provider_exchange=plan.provider_exchange,
            provider_timeframe=plan.provider_timeframe,
            data_end_at=series.end_time,
            error_code="sync_disabled",
            error_message="Market data provider sync is disabled.",
        )
        apply_market_data_sync_result(series, result, completed_at)
        return result

    unsupported_reason = unsupported_timeframe_reason(plan)
    if unsupported_reason is not None:
        result = provider_failure(plan, "unsupported_timeframe", unsupported_reason)
        apply_market_data_sync_result(series, result, completed_at)
        return result

    result = (provider or NoopMarketDataProvider()).sync(plan)
    persist_provider_sync_result(db, series, result, completed_at)
    return result


def persist_provider_sync_result(
    db: Session,
    series: MarketDataSeries,
    result: MarketDataSyncResult,
    completed_at: datetime,
) -> None:
    if series.source != MarketDataSource.PROVIDER:
        series.last_synced_at = completed_at
        series.sync_status = MarketDataSyncStatus.FAILED
        series.freshness_status = MarketDataFreshnessStatus.FAILED
        series.sync_error_code = "provider_series_required"
        series.sync_error_message = (
            "Provider candles can only be persisted to provider-backed series."
        )
        return

    if result.sync_status == MarketDataSyncStatus.SUCCESS:
        duplicate_count = len({candle.timestamp for candle in result.candles})
        if not result.candles:
            result = MarketDataSyncResult(
                sync_status=MarketDataSyncStatus.PARTIAL,
                freshness_status=MarketDataFreshnessStatus.PARTIAL,
                provider_name=result.provider_name,
                provider_symbol=result.provider_symbol,
                provider_exchange=result.provider_exchange,
                provider_timeframe=result.provider_timeframe,
                error_code="provider_empty_response",
                error_message=provider_failure_message("provider_empty_response"),
            )
        elif duplicate_count != len(result.candles):
            result = MarketDataSyncResult(
                sync_status=MarketDataSyncStatus.FAILED,
                freshness_status=MarketDataFreshnessStatus.FAILED,
                provider_name=result.provider_name,
                provider_symbol=result.provider_symbol,
                provider_exchange=result.provider_exchange,
                provider_timeframe=result.provider_timeframe,
                error_code="duplicate_provider_candles",
                error_message=provider_failure_message("duplicate_provider_candles"),
            )
        else:
            persist_provider_candles(db, series, result.candles)
            result = MarketDataSyncResult(
                sync_status=result.sync_status,
                freshness_status=result.freshness_status,
                provider_name=result.provider_name,
                provider_symbol=result.provider_symbol,
                provider_exchange=result.provider_exchange,
                provider_timeframe=result.provider_timeframe,
                data_end_at=max(candle.timestamp for candle in result.candles),
                candles=result.candles,
            )

    apply_market_data_sync_result(series, result, completed_at)


def persist_provider_candles(
    db: Session,
    series: MarketDataSeries,
    candles: tuple[ProviderCandle, ...],
) -> None:
    sorted_candles = sorted(candles, key=lambda candle: candle.timestamp)
    db.execute(delete(MarketDataCandle).where(MarketDataCandle.series_id == series.id))
    db.flush()
    db.add_all(
        MarketDataCandle(
            series_id=series.id,
            timestamp=candle.timestamp,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,
        )
        for candle in sorted_candles
    )
    series.start_time = sorted_candles[0].timestamp
    series.end_time = sorted_candles[-1].timestamp
    series.candle_count = len(sorted_candles)


def apply_market_data_sync_result(
    series: MarketDataSeries,
    result: MarketDataSyncResult,
    completed_at: datetime,
) -> None:
    series.source = MarketDataSource.PROVIDER
    series.provider_name = result.provider_name
    series.provider_symbol = result.provider_symbol
    series.provider_exchange = result.provider_exchange
    series.provider_timeframe = result.provider_timeframe
    series.last_synced_at = completed_at
    if result.data_end_at is not None:
        series.end_time = result.data_end_at
    series.sync_status = result.sync_status
    series.freshness_status = result.freshness_status
    series.sync_error_code = result.error_code
    series.sync_error_message = result.error_message


def evaluate_market_data_freshness(
    series: MarketDataSeries,
    now: datetime | None = None,
) -> MarketDataFreshnessStatus:
    if series.sync_status == MarketDataSyncStatus.PARTIAL:
        return MarketDataFreshnessStatus.PARTIAL
    if series.sync_status == MarketDataSyncStatus.FAILED and series.end_time is None:
        return MarketDataFreshnessStatus.FAILED
    if series.end_time is None:
        return MarketDataFreshnessStatus.UNKNOWN

    return evaluate_timestamp_freshness(series.end_time, series.timeframe, now)


def evaluate_timestamp_freshness(
    end_time: datetime,
    timeframe: Timeframe,
    now: datetime | None = None,
) -> MarketDataFreshnessStatus:
    checked_at = now or datetime.now(UTC)
    freshness_window = FRESHNESS_WINDOWS[timeframe]
    if checked_at - _as_aware_datetime(end_time) <= freshness_window:
        return MarketDataFreshnessStatus.FRESH
    return MarketDataFreshnessStatus.STALE


def _as_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _decimal_field(payload: dict[object, object], key: str) -> Decimal:
    value = payload[key]
    if not isinstance(value, str | int | float | Decimal):
        raise TypeError
    return Decimal(str(value))


def provider_failure(
    plan: MarketDataSyncPlan,
    error_code: str,
    message: str | None = None,
) -> MarketDataSyncResult:
    return MarketDataSyncResult(
        sync_status=MarketDataSyncStatus.FAILED,
        freshness_status=MarketDataFreshnessStatus.FAILED,
        provider_name=plan.provider_name,
        provider_symbol=plan.provider_symbol,
        provider_exchange=plan.provider_exchange,
        provider_timeframe=plan.provider_timeframe,
        error_code=error_code,
        error_message=message or provider_failure_message(error_code),
    )


def provider_failure_message(error_code: str) -> str:
    messages = {
        "unsupported_timeframe": (
            "Provider sync does not support this timeframe here. Use TradingView CSV "
            "fallback for this review cycle."
        ),
        "provider_transport_error": (
            "Provider request could not be completed. Retry later, reduce scope, or use "
            "TradingView CSV fallback."
        ),
        "provider_rate_limited": (
            "Provider rate limit was reached. Wait, reduce the sync scope, or use "
            "TradingView CSV fallback."
        ),
        "provider_symbol_or_entitlement": (
            "Provider rejected the symbol, timeframe, or entitlement. Verify provider "
            "coverage outside evidence channels or use TradingView CSV fallback."
        ),
        "provider_invalid_response": (
            "Provider response could not be used safely. Use TradingView CSV fallback "
            "and record only sanitized status evidence."
        ),
        "provider_empty_response": (
            "Provider returned no usable candles. Verify symbol coverage or use "
            "TradingView CSV fallback."
        ),
        "duplicate_provider_candles": (
            "Provider returned duplicate candle timestamps. Use TradingView CSV "
            "fallback until the provider result is reviewed."
        ),
        "provider_error": (
            "Provider rejected the request. Verify configuration and coverage outside "
            "evidence channels or use TradingView CSV fallback."
        ),
    }
    return messages.get(
        error_code,
        "Provider sync failed. Use TradingView CSV fallback and record only sanitized status evidence.",
    )
