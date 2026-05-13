from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"


class AssetClass(StrEnum):
    STOCK = "stock"
    CRYPTO = "crypto"


class MarketDataSource(StrEnum):
    TRADINGVIEW_CSV = "tradingview_csv"
    MANUAL = "manual"
    API_LATER = "api_later"


class Timeframe(StrEnum):
    ONE_WEEK = "1W"
    ONE_DAY = "1D"
    FOUR_HOURS = "4H"


class MarketDataStatus(StrEnum):
    IMPORTED = "imported"
    VALIDATED = "validated"
    FAILED = "failed"
    ANALYZED = "analyzed"


class TrendState(StrEnum):
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"


class StructureState(StrEnum):
    HIGHER_HIGH_HIGHER_LOW = "higher_high_higher_low"
    RANGE = "range"
    LOWER_HIGH_LOWER_LOW = "lower_high_lower_low"
    UNCLEAR = "unclear"


class StrategyType(StrEnum):
    TREND_PULLBACK_LONG = "trend_pullback_long"
    BASE_BREAKOUT_LONG = "base_breakout_long"


class SignalStatus(StrEnum):
    WATCHLIST = "watchlist"
    ARMED = "armed"
    TRIGGERED = "triggered"
    INVALIDATED = "invalidated"
    NO_SETUP = "no_setup"
    MISSED = "missed"
    EXPIRED = "expired"


class Bias(StrEnum):
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"


class ScoreClass(StrEnum):
    A_SETUP = "a_setup"
    B_SETUP = "b_setup"
    WATCHLIST = "watchlist"
    NO_TRADE = "no_trade"


class TradeStatus(StrEnum):
    OPEN = "open"
    PARTIAL_PROFIT = "partial_profit"
    BREAK_EVEN = "break_even"
    EXIT_WARNING = "exit_warning"
    EXIT_SIGNAL = "exit_signal"
    CLOSED = "closed"
    REVIEWED = "reviewed"


class ExitReason(StrEnum):
    STOP_LOSS = "stop_loss"
    TARGET_1 = "target_1"
    TARGET_2 = "target_2"
    MANUAL_EXIT = "manual_exit"
    STRUCTURE_BREAK = "structure_break"
    TIME_STOP = "time_stop"
    FAILED_BREAKOUT = "failed_breakout"
    OTHER = "other"


class TradeEventType(StrEnum):
    OPENED = "opened"
    STOP_UPDATED = "stop_updated"
    TARGET_UPDATED = "target_updated"
    PARTIAL_EXIT = "partial_exit"
    BREAK_EVEN = "break_even"
    TRAILING_STOP = "trailing_stop"
    MANAGEMENT_ALERT = "management_alert"
    EXIT_WARNING = "exit_warning"
    EXIT_SIGNAL = "exit_signal"
    CLOSED = "closed"
    NOTE = "note"
