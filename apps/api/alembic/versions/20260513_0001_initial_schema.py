"""initial schema

Revision ID: 20260513_0001
Revises:
Create Date: 2026-05-13

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "20260513_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    userrole = sa.Enum("admin", name="userrole")
    assetclass = sa.Enum("stock", "crypto", name="assetclass")
    marketdatasource = sa.Enum("tradingview_csv", "manual", "api_later", name="marketdatasource")
    timeframe = sa.Enum("1W", "1D", "4H", name="timeframe")
    marketdatastatus = sa.Enum(
        "imported", "validated", "failed", "analyzed", name="marketdatastatus"
    )
    trendstate = sa.Enum("bullish", "neutral", "bearish", name="trendstate")
    structurestate = sa.Enum(
        "higher_high_higher_low",
        "range",
        "lower_high_lower_low",
        "unclear",
        name="structurestate",
    )
    strategytype = sa.Enum("trend_pullback_long", "base_breakout_long", name="strategytype")
    signalstatus = sa.Enum(
        "watchlist",
        "armed",
        "triggered",
        "invalidated",
        "no_setup",
        "missed",
        "expired",
        name="signalstatus",
    )
    bias = sa.Enum("bullish", "neutral", "bearish", name="bias")
    scoreclass = sa.Enum("a_setup", "b_setup", "watchlist", "no_trade", name="scoreclass")
    tradestatus = sa.Enum(
        "open",
        "partial_profit",
        "break_even",
        "exit_warning",
        "exit_signal",
        "closed",
        "reviewed",
        name="tradestatus",
    )
    exitreason = sa.Enum(
        "stop_loss",
        "target_1",
        "target_2",
        "manual_exit",
        "structure_break",
        "time_stop",
        "failed_breakout",
        "other",
        name="exitreason",
    )
    tradeeventtype = sa.Enum(
        "opened",
        "stop_updated",
        "target_updated",
        "partial_exit",
        "break_even",
        "trailing_stop",
        "management_alert",
        "exit_warning",
        "exit_signal",
        "closed",
        "note",
        name="tradeeventtype",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("role", userrole, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("account_size", sa.Numeric(18, 2), nullable=True),
        sa.Column("default_risk_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("max_risk_percent", sa.Numeric(5, 2), nullable=False),
        sa.Column("min_risk_reward", sa.Numeric(8, 2), nullable=False),
        sa.Column("max_open_trades", sa.Integer(), nullable=False),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("telegram_enabled", sa.Boolean(), nullable=False),
        sa.Column("telegram_chat_id", sa.String(length=255), nullable=True),
        sa.Column("tradingview_webhook_secret", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "watchlist_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("asset_class", assetclass, nullable=False),
        sa.Column("exchange", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=16), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("last_analyzed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "symbol", name="uq_watchlist_items_user_symbol"),
    )
    op.create_index(op.f("ix_watchlist_items_symbol"), "watchlist_items", ["symbol"], unique=False)
    op.create_index(
        op.f("ix_watchlist_items_user_id"), "watchlist_items", ["user_id"], unique=False
    )

    op.create_table(
        "market_data_series",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=False),
        sa.Column("source", marketdatasource, nullable=False),
        sa.Column("timeframe", timeframe, nullable=False),
        sa.Column(
            "imported_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("candle_count", sa.Integer(), nullable=False),
        sa.Column("status", marketdatastatus, nullable=False),
        sa.Column("validation_errors", sa.JSON(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["watchlist_item_id"], ["watchlist_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_market_data_series_watchlist_item_id"),
        "market_data_series",
        ["watchlist_item_id"],
        unique=False,
    )

    op.create_table(
        "signals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=False),
        sa.Column("strategy_type", strategytype, nullable=False),
        sa.Column("status", signalstatus, nullable=False),
        sa.Column("bias", bias, nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("score_class", scoreclass, nullable=True),
        sa.Column("timeframe_context", timeframe, nullable=True),
        sa.Column("timeframe_setup", timeframe, nullable=True),
        sa.Column("timeframe_trigger", timeframe, nullable=True),
        sa.Column("entry_low", sa.Numeric(18, 8), nullable=True),
        sa.Column("entry_high", sa.Numeric(18, 8), nullable=True),
        sa.Column("trigger_level", sa.Numeric(18, 8), nullable=True),
        sa.Column("stop_loss", sa.Numeric(18, 8), nullable=True),
        sa.Column("target_1", sa.Numeric(18, 8), nullable=True),
        sa.Column("target_2", sa.Numeric(18, 8), nullable=True),
        sa.Column("risk_reward", sa.Numeric(8, 2), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("invalidation_reason", sa.Text(), nullable=True),
        sa.Column("reasoning", sa.JSON(), nullable=True),
        sa.Column("risk_flags", sa.JSON(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["watchlist_item_id"], ["watchlist_items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_signals_user_id"), "signals", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_signals_watchlist_item_id"), "signals", ["watchlist_item_id"], unique=False
    )

    op.create_table(
        "indicator_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("series_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ema20", sa.Numeric(18, 8), nullable=True),
        sa.Column("ema50", sa.Numeric(18, 8), nullable=True),
        sa.Column("ema200", sa.Numeric(18, 8), nullable=True),
        sa.Column("rsi14", sa.Numeric(8, 4), nullable=True),
        sa.Column("atr14", sa.Numeric(18, 8), nullable=True),
        sa.Column("volume_avg20", sa.Numeric(24, 8), nullable=True),
        sa.Column("relative_volume", sa.Numeric(12, 4), nullable=True),
        sa.Column("swing_high", sa.Numeric(18, 8), nullable=True),
        sa.Column("swing_low", sa.Numeric(18, 8), nullable=True),
        sa.Column("trend_state", trendstate, nullable=True),
        sa.Column("structure_state", structurestate, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["series_id"], ["market_data_series.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id", "timestamp", name="uq_indicators_series_timestamp"),
    )
    op.create_index(
        op.f("ix_indicator_snapshots_series_id"),
        "indicator_snapshots",
        ["series_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indicator_snapshots_timestamp"),
        "indicator_snapshots",
        ["timestamp"],
        unique=False,
    )

    op.create_table(
        "market_data_candles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("series_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Numeric(18, 8), nullable=False),
        sa.Column("high", sa.Numeric(18, 8), nullable=False),
        sa.Column("low", sa.Numeric(18, 8), nullable=False),
        sa.Column("close", sa.Numeric(18, 8), nullable=False),
        sa.Column("volume", sa.Numeric(24, 8), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["series_id"], ["market_data_series.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("series_id", "timestamp", name="uq_candles_series_timestamp"),
    )
    op.create_index(
        op.f("ix_market_data_candles_series_id"),
        "market_data_candles",
        ["series_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_market_data_candles_timestamp"),
        "market_data_candles",
        ["timestamp"],
        unique=False,
    )

    op.create_table(
        "trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("watchlist_item_id", sa.Integer(), nullable=False),
        sa.Column("status", tradestatus, nullable=False),
        sa.Column("strategy_type", strategytype, nullable=False),
        sa.Column("asset_class", assetclass, nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("entry_price", sa.Numeric(18, 8), nullable=False),
        sa.Column("stop_loss", sa.Numeric(18, 8), nullable=False),
        sa.Column("target_1", sa.Numeric(18, 8), nullable=True),
        sa.Column("target_2", sa.Numeric(18, 8), nullable=True),
        sa.Column("position_size", sa.Numeric(24, 8), nullable=False),
        sa.Column("fees", sa.Numeric(18, 8), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("exit_price", sa.Numeric(18, 8), nullable=True),
        sa.Column("exit_reason", exitreason, nullable=True),
        sa.Column("initial_risk_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("initial_risk_percent", sa.Numeric(8, 4), nullable=True),
        sa.Column("initial_risk_reward", sa.Numeric(8, 2), nullable=True),
        sa.Column("result_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("result_r", sa.Numeric(8, 4), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["signal_id"], ["signals.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["watchlist_item_id"], ["watchlist_items.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("signal_id"),
    )
    op.create_index(op.f("ix_trades_symbol"), "trades", ["symbol"], unique=False)
    op.create_index(op.f("ix_trades_user_id"), "trades", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_trades_watchlist_item_id"), "trades", ["watchlist_item_id"], unique=False
    )

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trade_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("setup_rule_followed", sa.Boolean(), nullable=True),
        sa.Column("entry_quality_score", sa.Integer(), nullable=True),
        sa.Column("stop_quality_score", sa.Integer(), nullable=True),
        sa.Column("exit_quality_score", sa.Integer(), nullable=True),
        sa.Column("discipline_score", sa.Integer(), nullable=True),
        sa.Column("market_context", sa.Text(), nullable=True),
        sa.Column("emotional_notes", sa.Text(), nullable=True),
        sa.Column("what_went_well", sa.Text(), nullable=True),
        sa.Column("what_went_wrong", sa.Text(), nullable=True),
        sa.Column("lesson_learned", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["trade_id"], ["trades.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trade_id"),
    )
    op.create_index(
        op.f("ix_journal_entries_user_id"), "journal_entries", ["user_id"], unique=False
    )

    op.create_table(
        "trade_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("trade_id", sa.Integer(), nullable=False),
        sa.Column("event_type", tradeeventtype, nullable=False),
        sa.Column("event_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price", sa.Numeric(18, 8), nullable=True),
        sa.Column("quantity", sa.Numeric(24, 8), nullable=True),
        sa.Column("old_value", sa.String(length=255), nullable=True),
        sa.Column("new_value", sa.String(length=255), nullable=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["trade_id"], ["trades.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_trade_events_trade_id"), "trade_events", ["trade_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_trade_events_trade_id"), table_name="trade_events")
    op.drop_table("trade_events")
    op.drop_index(op.f("ix_journal_entries_user_id"), table_name="journal_entries")
    op.drop_table("journal_entries")
    op.drop_index(op.f("ix_trades_watchlist_item_id"), table_name="trades")
    op.drop_index(op.f("ix_trades_user_id"), table_name="trades")
    op.drop_index(op.f("ix_trades_symbol"), table_name="trades")
    op.drop_table("trades")
    op.drop_index(op.f("ix_market_data_candles_timestamp"), table_name="market_data_candles")
    op.drop_index(op.f("ix_market_data_candles_series_id"), table_name="market_data_candles")
    op.drop_table("market_data_candles")
    op.drop_index(op.f("ix_indicator_snapshots_timestamp"), table_name="indicator_snapshots")
    op.drop_index(op.f("ix_indicator_snapshots_series_id"), table_name="indicator_snapshots")
    op.drop_table("indicator_snapshots")
    op.drop_index(op.f("ix_signals_watchlist_item_id"), table_name="signals")
    op.drop_index(op.f("ix_signals_user_id"), table_name="signals")
    op.drop_table("signals")
    op.drop_index(op.f("ix_market_data_series_watchlist_item_id"), table_name="market_data_series")
    op.drop_table("market_data_series")
    op.drop_index(op.f("ix_watchlist_items_user_id"), table_name="watchlist_items")
    op.drop_index(op.f("ix_watchlist_items_symbol"), table_name="watchlist_items")
    op.drop_table("watchlist_items")
    op.drop_table("settings")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    for enum_name in (
        "tradeeventtype",
        "exitreason",
        "tradestatus",
        "scoreclass",
        "bias",
        "signalstatus",
        "strategytype",
        "structurestate",
        "trendstate",
        "marketdatastatus",
        "timeframe",
        "marketdatasource",
        "assetclass",
        "userrole",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
