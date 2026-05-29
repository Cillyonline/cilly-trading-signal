from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.models.enums import (
    MarketDataFreshnessStatus,
    MarketDataSource,
    MarketDataSyncStatus,
    Timeframe,
)
from app.models.market_data import MarketDataSeries

FRESHNESS_WINDOWS = {
    Timeframe.ONE_WEEK: timedelta(days=14),
    Timeframe.ONE_DAY: timedelta(days=3),
    Timeframe.FOUR_HOURS: timedelta(hours=24),
}


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
class MarketDataSyncResult:
    sync_status: MarketDataSyncStatus
    freshness_status: MarketDataFreshnessStatus
    provider_name: str | None = None
    provider_symbol: str | None = None
    provider_exchange: str | None = None
    provider_timeframe: str | None = None
    data_end_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None


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

    result = (provider or NoopMarketDataProvider()).sync(plan)
    apply_market_data_sync_result(series, result, completed_at)
    return result


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

    checked_at = now or datetime.now(UTC)
    freshness_window = FRESHNESS_WINDOWS[series.timeframe]
    if checked_at - _as_aware_datetime(series.end_time) <= freshness_window:
        return MarketDataFreshnessStatus.FRESH
    return MarketDataFreshnessStatus.STALE


def _as_aware_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
