from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    AssetClass,
    Bias,
    MarketDataFreshnessStatus,
    MarketDataStatus,
    Timeframe,
)
from app.models.market_data import IndicatorSnapshot, MarketDataCandle, MarketDataSeries
from app.models.watchlist import WatchlistItem
from app.services.indicators import calculate_indicator_snapshots, indicator_input_from_model

STOCK_BENCHMARK_SYMBOLS = ("SPY", "QQQ")
CRYPTO_BENCHMARK_GROUPS = {
    "BTC": ("BTC", "BTCUSD", "BTCUSDT", "BTC-USD"),
    "ETH": ("ETH", "ETHUSD", "ETHUSDT", "ETH-USD"),
}
CRYPTO_BENCHMARK_SYMBOLS = (
    *CRYPTO_BENCHMARK_GROUPS["BTC"],
    *CRYPTO_BENCHMARK_GROUPS["ETH"],
)
RELATIVE_STRENGTH_UNDERPERFORMANCE = Decimal("0.02")
HIGH_CONFIDENCE_SCORE_CAP = 79


@dataclass(frozen=True)
class MarketContextAssessment:
    risk_flags: list[str]
    no_trade_reasons: list[str]
    score_cap: int | None = None


@dataclass(frozen=True)
class BenchmarkContext:
    symbol: str
    regime: Bias
    freshness_status: MarketDataFreshnessStatus
    percent_change: Decimal | None


@dataclass(frozen=True)
class BenchmarkRequirementStatus:
    key: str
    accepted_symbols: list[str]
    status: str
    present_symbol: str | None = None
    latest_daily_freshness: MarketDataFreshnessStatus | None = None
    message: str = ""


@dataclass(frozen=True)
class BenchmarkContextStatus:
    asset_class: AssetClass
    requirements: list[BenchmarkRequirementStatus]
    guidance: str


def assess_market_context(
    db: Session,
    source_series: MarketDataSeries,
    candidate_daily_candles: list[MarketDataCandle],
) -> MarketContextAssessment:
    if source_series.watchlist_item.asset_class == AssetClass.STOCK:
        return assess_stock_context(db, source_series, candidate_daily_candles)
    if source_series.watchlist_item.asset_class == AssetClass.CRYPTO:
        return assess_crypto_context(db, source_series, candidate_daily_candles)
    return MarketContextAssessment(risk_flags=[], no_trade_reasons=[])


def benchmark_context_status(db: Session, user_id: int) -> list[BenchmarkContextStatus]:
    items = list(
        db.scalars(
            select(WatchlistItem)
            .where(WatchlistItem.user_id == user_id)
            .where(WatchlistItem.is_active.is_(True))
        )
    )
    return [
        BenchmarkContextStatus(
            asset_class=AssetClass.STOCK,
            requirements=[
                requirement_status(items, "SPY", ["SPY"]),
                requirement_status(items, "QQQ", ["QQQ"]),
            ],
            guidance=(
                "Stocks use stored daily SPY/QQQ context for market regime and relative "
                "strength review. Add/import daily data manually; no live data is fetched."
            ),
        ),
        BenchmarkContextStatus(
            asset_class=AssetClass.CRYPTO,
            requirements=[
                requirement_status(items, key, list(symbols))
                for key, symbols in CRYPTO_BENCHMARK_GROUPS.items()
            ],
            guidance=(
                "Crypto uses stored daily BTC/ETH context for regime review. Accepted ticker "
                "variants are listed below; data remains manual or provider-synced only."
            ),
        ),
    ]


def assess_stock_context(
    db: Session,
    source_series: MarketDataSeries,
    candidate_daily_candles: list[MarketDataCandle],
) -> MarketContextAssessment:
    benchmarks = load_benchmark_contexts(db, source_series, STOCK_BENCHMARK_SYMBOLS)
    if not benchmarks:
        return MarketContextAssessment(
            risk_flags=["stock_benchmark_context_missing"],
            no_trade_reasons=[],
            score_cap=HIGH_CONFIDENCE_SCORE_CAP,
        )

    risk_flags = stale_context_flags(benchmarks, "stock_benchmark_context")
    no_trade_reasons: list[str] = []
    regimes = [benchmark.regime for benchmark in benchmarks]
    if all(regime == Bias.BEARISH for regime in regimes):
        no_trade_reasons.append("stock_market_regime_bearish")
    elif any(regime != Bias.BULLISH for regime in regimes):
        risk_flags.append("stock_market_regime_mixed")

    relative_strength_flag = relative_strength_flag_for(
        candidate_daily_candles,
        benchmarks,
        underperforming_blocker=(not regimes or any(regime != Bias.BULLISH for regime in regimes)),
    )
    if relative_strength_flag == "relative_strength_underperforming_blocker":
        no_trade_reasons.append("relative_strength_underperforming")
    elif relative_strength_flag is not None:
        risk_flags.append(relative_strength_flag)

    return MarketContextAssessment(
        risk_flags=dedupe(risk_flags),
        no_trade_reasons=dedupe(no_trade_reasons),
        score_cap=HIGH_CONFIDENCE_SCORE_CAP if risk_flags else None,
    )


def requirement_status(
    items: list[WatchlistItem], key: str, accepted_symbols: list[str]
) -> BenchmarkRequirementStatus:
    accepted = {symbol.upper() for symbol in accepted_symbols}
    item = next((candidate for candidate in items if candidate.symbol.upper() in accepted), None)
    if item is None:
        return BenchmarkRequirementStatus(
            key=key,
            accepted_symbols=accepted_symbols,
            status="missing_symbol",
            message=f"Add one active watchlist symbol for {key} benchmark context.",
        )

    daily_series = latest_daily_series(item)
    if daily_series is None:
        return BenchmarkRequirementStatus(
            key=key,
            accepted_symbols=accepted_symbols,
            status="missing_daily_data",
            present_symbol=item.symbol,
            message=f"Import or sync daily data for {item.symbol} before relying on context.",
        )

    if daily_series.freshness_status != MarketDataFreshnessStatus.FRESH:
        return BenchmarkRequirementStatus(
            key=key,
            accepted_symbols=accepted_symbols,
            status=daily_series.freshness_status.value,
            present_symbol=item.symbol,
            latest_daily_freshness=daily_series.freshness_status,
            message=f"Daily context for {item.symbol} is {daily_series.freshness_status.value}.",
        )

    return BenchmarkRequirementStatus(
        key=key,
        accepted_symbols=accepted_symbols,
        status="ready",
        present_symbol=item.symbol,
        latest_daily_freshness=daily_series.freshness_status,
        message=f"Stored fresh daily context is available for {item.symbol}.",
    )


def latest_daily_series(item: WatchlistItem) -> MarketDataSeries | None:
    daily_series = [
        series for series in item.market_data_series if series.timeframe == Timeframe.ONE_DAY
    ]
    return max(
        daily_series,
        key=lambda series: (series.end_time or series.imported_at, series.id),
        default=None,
    )


def assess_crypto_context(
    db: Session,
    source_series: MarketDataSeries,
    candidate_daily_candles: list[MarketDataCandle],
) -> MarketContextAssessment:
    benchmarks = load_benchmark_contexts(db, source_series, CRYPTO_BENCHMARK_SYMBOLS)
    if not benchmarks:
        return MarketContextAssessment(
            risk_flags=["crypto_regime_context_missing"],
            no_trade_reasons=[],
            score_cap=HIGH_CONFIDENCE_SCORE_CAP,
        )

    risk_flags = stale_context_flags(benchmarks, "crypto_regime_context")
    no_trade_reasons: list[str] = []
    btc_eth_regimes = [benchmark.regime for benchmark in benchmarks]
    if btc_eth_regimes and all(regime == Bias.BEARISH for regime in btc_eth_regimes):
        no_trade_reasons.append("crypto_regime_bearish")
    elif any(regime != Bias.BULLISH for regime in btc_eth_regimes):
        risk_flags.append("crypto_regime_mixed")

    relative_strength_flag = relative_strength_flag_for(
        candidate_daily_candles,
        benchmarks,
        underperforming_blocker=(
            not btc_eth_regimes or any(regime != Bias.BULLISH for regime in btc_eth_regimes)
        ),
    )
    if relative_strength_flag == "relative_strength_underperforming_blocker":
        no_trade_reasons.append("relative_strength_underperforming")
    elif relative_strength_flag is not None:
        risk_flags.append(relative_strength_flag)

    return MarketContextAssessment(
        risk_flags=dedupe(risk_flags),
        no_trade_reasons=dedupe(no_trade_reasons),
        score_cap=HIGH_CONFIDENCE_SCORE_CAP if risk_flags else None,
    )


def load_benchmark_contexts(
    db: Session,
    source_series: MarketDataSeries,
    benchmark_symbols: tuple[str, ...],
) -> list[BenchmarkContext]:
    benchmark_lookup = {symbol.upper() for symbol in benchmark_symbols}
    rows = list(
        db.scalars(
            select(MarketDataSeries)
            .join(WatchlistItem)
            .where(WatchlistItem.user_id == source_series.watchlist_item.user_id)
            .where(WatchlistItem.id != source_series.watchlist_item_id)
            .where(WatchlistItem.symbol.in_(benchmark_lookup))
            .where(MarketDataSeries.timeframe == Timeframe.ONE_DAY)
            .where(
                MarketDataSeries.status.in_(
                    (MarketDataStatus.ANALYZED, MarketDataStatus.VALIDATED)
                )
            )
            .order_by(MarketDataSeries.imported_at.desc(), MarketDataSeries.id.desc())
        )
    )
    latest_by_symbol: dict[str, MarketDataSeries] = {}
    for series in rows:
        symbol = series.watchlist_item.symbol.upper()
        if symbol not in latest_by_symbol:
            latest_by_symbol[symbol] = series

    contexts: list[BenchmarkContext] = []
    for series in latest_by_symbol.values():
        candles = load_candles(db, series)
        snapshots = load_snapshots(db, series)
        if not snapshots:
            snapshots = calculate_indicator_snapshots(
                [indicator_input_from_model(candle) for candle in candles]
            )
        contexts.append(build_benchmark_context(series, candles, snapshots))
    return contexts


def build_benchmark_context(
    series: MarketDataSeries,
    candles: list[MarketDataCandle],
    snapshots: list[object],
) -> BenchmarkContext:
    latest_candle = candles[-1] if candles else None
    latest_snapshot = snapshots[-1] if snapshots else None
    previous_snapshot = snapshots[-2] if len(snapshots) >= 2 else None
    regime = benchmark_regime(latest_candle, latest_snapshot, previous_snapshot)
    return BenchmarkContext(
        symbol=series.watchlist_item.symbol.upper(),
        regime=regime,
        freshness_status=series.freshness_status,
        percent_change=percent_change(candles),
    )


def benchmark_regime(
    latest_candle: MarketDataCandle | None,
    latest_snapshot: object | None,
    previous_snapshot: object | None,
) -> Bias:
    close = getattr(latest_candle, "close", None)
    ema50 = getattr(latest_snapshot, "ema50", None)
    ema200 = getattr(latest_snapshot, "ema200", None)
    previous_ema50 = getattr(previous_snapshot, "ema50", None)
    if close is None or ema50 is None or ema200 is None or previous_ema50 is None:
        return Bias.NEUTRAL
    if close > ema200 and ema50 >= previous_ema50:
        return Bias.BULLISH
    if close < ema200 and ema50 < previous_ema50:
        return Bias.BEARISH
    return Bias.NEUTRAL


def stale_context_flags(benchmarks: list[BenchmarkContext], prefix: str) -> list[str]:
    flags: list[str] = []
    for benchmark in benchmarks:
        if benchmark.freshness_status != MarketDataFreshnessStatus.FRESH:
            flags.append(f"{prefix}_{benchmark.freshness_status.value}")
    return flags


def relative_strength_flag_for(
    candidate_daily_candles: list[MarketDataCandle],
    benchmarks: list[BenchmarkContext],
    underperforming_blocker: bool,
) -> str | None:
    candidate_change = percent_change(candidate_daily_candles)
    benchmark_changes = [
        benchmark.percent_change for benchmark in benchmarks if benchmark.percent_change is not None
    ]
    if candidate_change is None or not benchmark_changes:
        return "relative_strength_unavailable"
    benchmark_change = sum(benchmark_changes, Decimal("0")) / Decimal(len(benchmark_changes))
    if candidate_change < benchmark_change - RELATIVE_STRENGTH_UNDERPERFORMANCE:
        if underperforming_blocker:
            return "relative_strength_underperforming_blocker"
        return "relative_strength_lagging"
    return None


def percent_change(candles: list[MarketDataCandle]) -> Decimal | None:
    if len(candles) < 2:
        return None
    latest = candles[-1].close
    reference = candles[-21].close if len(candles) >= 21 else candles[0].close
    if reference <= 0:
        return None
    return (latest - reference) / reference


def load_candles(db: Session, series: MarketDataSeries) -> list[MarketDataCandle]:
    return list(
        db.scalars(
            select(MarketDataCandle)
            .where(MarketDataCandle.series_id == series.id)
            .order_by(MarketDataCandle.timestamp)
        )
    )


def load_snapshots(db: Session, series: MarketDataSeries) -> list[IndicatorSnapshot]:
    return list(
        db.scalars(
            select(IndicatorSnapshot)
            .where(IndicatorSnapshot.series_id == series.id)
            .order_by(IndicatorSnapshot.timestamp)
        )
    )


def dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))
