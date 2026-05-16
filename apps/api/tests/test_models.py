from sqlalchemy import JSON

from app.db.base import Base
from app.models import (
    IndicatorSnapshot,
    JournalEntry,
    MarketDataCandle,
    MarketDataSeries,
    Settings,
    Signal,
    Trade,
    TradeEvent,
    User,
    WatchlistItem,
)


def test_mvp_model_tables_are_registered() -> None:
    expected_tables = {
        "users",
        "settings",
        "watchlist_items",
        "market_data_series",
        "market_data_candles",
        "indicator_snapshots",
        "signals",
        "trades",
        "trade_events",
        "journal_entries",
    }

    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_core_models_use_expected_table_names() -> None:
    assert User.__tablename__ == "users"
    assert Settings.__tablename__ == "settings"
    assert WatchlistItem.__tablename__ == "watchlist_items"
    assert MarketDataSeries.__tablename__ == "market_data_series"
    assert MarketDataCandle.__tablename__ == "market_data_candles"
    assert IndicatorSnapshot.__tablename__ == "indicator_snapshots"
    assert Signal.__tablename__ == "signals"
    assert Trade.__tablename__ == "trades"
    assert TradeEvent.__tablename__ == "trade_events"
    assert JournalEntry.__tablename__ == "journal_entries"


def test_market_data_candle_has_series_timestamp_unique_constraint() -> None:
    candle_table = Base.metadata.tables["market_data_candles"]

    constraints = {constraint.name for constraint in candle_table.constraints}

    assert "uq_candles_series_timestamp" in constraints


def test_signal_reasoning_and_risk_flags_are_json_columns() -> None:
    signal_table = Base.metadata.tables["signals"]

    assert isinstance(signal_table.c.reasoning.type, JSON)
    assert isinstance(signal_table.c.risk_flags.type, JSON)
    assert isinstance(signal_table.c.no_trade_reasons.type, JSON)
