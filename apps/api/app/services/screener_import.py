import csv
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Any

from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import (
    AssetClass,
    ScreenerImportSource,
    ScreenerImportStatus,
    ScreenerResultStatus,
)
from app.models.screener import ScreenerImport, ScreenerResult
from app.schemas.screener import ScreenerResultFilters, ScreenerResultPage, ScreenerResultRead
from app.schemas.watchlist import WatchlistItemCreate
from app.services.watchlist import (
    DuplicateWatchlistSymbolError,
    create_watchlist_item,
    get_watchlist_item_by_symbol,
)

MAX_SCREENER_UPLOAD_BYTES = 1 * 1024 * 1024
MAX_SCREENER_ROWS = 500
MAX_SCREENER_UPLOAD_ROWS = 2_000
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9._:/=\-]{1,32}$")

HEADER_ALIASES = {
    "symbol": {"symbol", "ticker", "ticker no.", "ticker no", "ticker_no"},
    "name": {"name", "description", "company"},
    "exchange": {"exchange", "market"},
    "sector": {"sector"},
    "industry": {"industry"},
    "currency": {"currency"},
    "price": {"price", "last", "close"},
    "change_percent": {"change %", "change % 1d", "change_percent", "change"},
    "volume": {"volume"},
    "relative_volume": {"relative volume", "rel volume", "relative_volume"},
    "market_cap": {"market cap", "market capitalization", "market_cap"},
    "rsi14": {"rsi (14)", "rsi14", "rsi"},
    "ema20": {"ema20", "exponential moving average (20)"},
    "ema50": {"ema50", "exponential moving average (50)"},
    "ema200": {"ema200", "exponential moving average (200)"},
}
NUMERIC_FIELDS = {
    "price",
    "change_percent",
    "volume",
    "relative_volume",
    "market_cap",
    "rsi14",
    "ema20",
    "ema50",
    "ema200",
}


@dataclass(frozen=True)
class ScreenerImportError:
    row: int | None
    field: str | None
    message: str

    def to_dict(self) -> dict[str, object | None]:
        return {"row": self.row, "field": self.field, "message": self.message}


@dataclass(frozen=True)
class ParsedScreenerRow:
    values: dict[str, Any]
    raw_metadata: dict[str, str]
    duplicate_key: tuple[str, str, str | None]


@dataclass(frozen=True)
class ParsedScreenerCsv:
    rows: list[ParsedScreenerRow]
    errors: list[ScreenerImportError]
    duplicate_count: int


def import_screener_csv(
    db: Session,
    user_id: int,
    asset_class: AssetClass,
    file_name: str | None,
    content: str,
    screener_preset: str | None = None,
) -> tuple[ScreenerImport | None, list[ScreenerImportError]]:
    parsed_csv = parse_screener_csv(content, asset_class)
    rows = parsed_csv.rows
    errors = parsed_csv.errors
    if errors and not rows:
        return None, errors

    duplicate_count = parsed_csv.duplicate_count
    rejected_count = len(errors)
    status = (
        ScreenerImportStatus.PARTIAL
        if rejected_count or duplicate_count
        else ScreenerImportStatus.IMPORTED
    )

    import_record = ScreenerImport(
        user_id=user_id,
        source=ScreenerImportSource.TRADINGVIEW_SCREENER_CSV,
        file_name=sanitize_file_name(file_name),
        asset_class=asset_class,
        screener_preset=normalize_optional_text(screener_preset, 120),
        row_count=len(rows) + rejected_count,
        accepted_count=sum(
            1 for row in rows if row.values["status"] == ScreenerResultStatus.CANDIDATE
        ),
        rejected_count=rejected_count,
        duplicate_count=duplicate_count,
        status=status,
        validation_errors=[error.to_dict() for error in errors] or None,
    )
    db.add(import_record)
    db.flush()

    result_by_key: dict[tuple[str, str, str | None], ScreenerResult] = {}
    for row in rows:
        duplicate_of = result_by_key.get(row.duplicate_key)
        result = ScreenerResult(
            screener_import_id=import_record.id,
            user_id=user_id,
            duplicate_of=duplicate_of,
            raw_metadata=row.raw_metadata or None,
            **row.values,
        )
        db.add(result)
        db.flush()
        result_by_key.setdefault(row.duplicate_key, result)

    db.commit()
    db.refresh(import_record)
    return import_record, errors


def parse_screener_csv(content: str, asset_class: AssetClass) -> ParsedScreenerCsv:
    reader = csv.DictReader(StringIO(content))
    if not reader.fieldnames:
        return ParsedScreenerCsv(
            rows=[],
            errors=[ScreenerImportError(None, "file", "CSV header row is required.")],
            duplicate_count=0,
        )

    header_map = build_header_map(reader.fieldnames)
    if "symbol" not in header_map:
        return ParsedScreenerCsv(
            rows=[],
            errors=[ScreenerImportError(None, "symbol", "Missing required column: symbol")],
            duplicate_count=0,
        )

    rows: list[ParsedScreenerRow] = []
    errors: list[ScreenerImportError] = []
    seen_keys: set[tuple[str, str, str | None]] = set()
    duplicate_count = 0
    total_rows = 0

    for row_number, row in enumerate(reader, start=2):
        total_rows += 1
        if total_rows > MAX_SCREENER_UPLOAD_ROWS:
            errors.append(
                ScreenerImportError(
                    None,
                    "file",
                    f"CSV must contain at most {MAX_SCREENER_UPLOAD_ROWS} rows.",
                )
            )
            break
        if len(rows) >= MAX_SCREENER_ROWS:
            errors.append(
                ScreenerImportError(
                    None,
                    "file",
                    f"CSV can import at most {MAX_SCREENER_ROWS} candidate rows.",
                )
            )
            break

        parsed = parse_screener_row(row, row_number, header_map, asset_class, errors)
        if parsed is None:
            continue

        if parsed.duplicate_key in seen_keys:
            duplicate_count += 1
            errors.append(
                ScreenerImportError(
                    row_number, "symbol", "Duplicate screener row in import."
                )
            )
            continue
        seen_keys.add(parsed.duplicate_key)
        rows.append(parsed)

    if total_rows == 0:
        errors.append(ScreenerImportError(None, "file", "CSV must contain at least one row."))
    return ParsedScreenerCsv(rows=rows, errors=errors, duplicate_count=duplicate_count)


def parse_screener_row(
    row: dict[str, str | None],
    row_number: int,
    header_map: dict[str, str],
    asset_class: AssetClass,
    errors: list[ScreenerImportError],
) -> ParsedScreenerRow | None:
    symbol = normalize_symbol(row.get(header_map["symbol"]))
    if symbol is None:
        errors.append(ScreenerImportError(row_number, "symbol", "Symbol is required."))
        return None
    if not SYMBOL_PATTERN.match(symbol):
        errors.append(
            ScreenerImportError(
                row_number, "symbol", "Symbol contains unsupported characters."
            )
        )
        return None

    values: dict[str, Any] = {
        "symbol": symbol,
        "asset_class": asset_class,
        "status": ScreenerResultStatus.CANDIDATE,
        "validation_errors": None,
    }
    for field in ("name", "exchange", "currency", "sector", "industry"):
        values[field] = (
            normalize_optional_text(row.get(header_map[field]), 255)
            if field in header_map
            else None
        )

    values["exchange"] = normalize_optional_uppercase(values["exchange"])
    values["currency"] = normalize_optional_uppercase(values["currency"])
    for field in NUMERIC_FIELDS:
        values[field] = (
            parse_optional_decimal(row.get(header_map[field]), field, row_number, errors)
            if field in header_map
            else None
        )
    values["rank"] = row_number - 1

    if any(error.row == row_number for error in errors):
        return None

    raw_metadata = build_raw_metadata(row, set(header_map.values()))
    return ParsedScreenerRow(
        values=values,
        raw_metadata=raw_metadata,
        duplicate_key=(asset_class.value, symbol, values["exchange"]),
    )


def build_header_map(headers: list[str]) -> dict[str, str]:
    normalized_headers = {normalize_header(header): header for header in headers}
    header_map: dict[str, str] = {}
    for field, aliases in HEADER_ALIASES.items():
        for alias in aliases:
            if alias in normalized_headers:
                header_map[field] = normalized_headers[alias]
                break
    return header_map


def build_raw_metadata(row: dict[str, str | None], known_headers: set[str]) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for key, value in row.items():
        if key in known_headers or value is None:
            continue
        normalized_key = key.strip()[:80]
        normalized_value = value.strip()[:255]
        if normalized_key and normalized_value:
            metadata[normalized_key] = normalized_value
    return metadata


def list_screener_imports(db: Session, user_id: int) -> list[ScreenerImport]:
    return list(
        db.scalars(
            select(ScreenerImport)
            .where(ScreenerImport.user_id == user_id)
            .order_by(ScreenerImport.created_at.desc(), ScreenerImport.id.desc())
        )
    )


SCREENER_RESULT_SORT_COLUMNS = {
    "created_at": ScreenerResult.created_at,
    "symbol": ScreenerResult.symbol,
    "status": ScreenerResult.status,
    "volume": ScreenerResult.volume,
    "relative_volume": ScreenerResult.relative_volume,
    "rsi14": ScreenerResult.rsi14,
    "price": ScreenerResult.price,
    "rank": ScreenerResult.rank,
}
SCREENER_BULK_REVIEW_STATUSES = {
    ScreenerResultStatus.CANDIDATE,
    ScreenerResultStatus.IGNORED,
    ScreenerResultStatus.REJECTED,
}


def list_screener_results(
    db: Session, user_id: int, filters: ScreenerResultFilters | None = None
) -> list[ScreenerResult]:
    filters = filters or ScreenerResultFilters()
    query = build_screener_results_query(user_id, filters)
    sort_column = SCREENER_RESULT_SORT_COLUMNS.get(filters.sort_by, ScreenerResult.created_at)
    ordered_column = sort_column.asc() if filters.sort_direction == "asc" else sort_column.desc()
    return list(
        db.scalars(
            query.order_by(ordered_column, ScreenerResult.id.desc())
        )
    )


def list_screener_result_page(
    db: Session, user_id: int, filters: ScreenerResultFilters
) -> ScreenerResultPage:
    query = build_screener_results_query(user_id, filters)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    sort_column = SCREENER_RESULT_SORT_COLUMNS.get(filters.sort_by, ScreenerResult.created_at)
    ordered_column = sort_column.asc() if filters.sort_direction == "asc" else sort_column.desc()
    items = list(
        db.scalars(
            query.order_by(ordered_column, ScreenerResult.id.desc())
            .offset((filters.page - 1) * filters.page_size)
            .limit(filters.page_size)
        )
    )
    return ScreenerResultPage(
        items=[to_screener_result_read(item) for item in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=max(1, ceil(total / filters.page_size)) if total else 0,
    )


def to_screener_result_read(result: ScreenerResult) -> ScreenerResultRead:
    priority, reasons = calculate_screener_review_priority(result)
    return ScreenerResultRead.model_validate(
        {
            **result.__dict__,
            "review_priority": priority,
            "review_priority_reasons": reasons,
        }
    )


def calculate_screener_review_priority(result: ScreenerResult) -> tuple[str, list[str]]:
    reasons: list[str] = []
    caution_count = 0
    supportive_count = 0

    if result.volume is None:
        caution_count += 1
        reasons.append("volume_missing")
    elif result.volume >= Decimal("1000000"):
        supportive_count += 1
        reasons.append("liquidity_visible")

    if result.relative_volume is None:
        caution_count += 1
        reasons.append("relative_volume_missing")
    elif result.relative_volume >= Decimal("1.2"):
        supportive_count += 1
        reasons.append("relative_volume_elevated")

    if result.rsi14 is None:
        caution_count += 1
        reasons.append("rsi_missing")
    elif Decimal("45") <= result.rsi14 <= Decimal("70"):
        supportive_count += 1
        reasons.append("rsi_reviewable")
    elif result.rsi14 > Decimal("80"):
        caution_count += 1
        reasons.append("rsi_extended")

    if result.price is not None and result.ema50 is not None and result.price >= result.ema50:
        supportive_count += 1
        reasons.append("price_above_ema50")

    if caution_count >= 2:
        return "low_review_priority", reasons
    if supportive_count >= 3:
        return "high_review_priority", reasons
    return "normal", reasons or ["insufficient_priority_context"]


def build_screener_results_query(user_id: int, filters: ScreenerResultFilters):
    query = select(ScreenerResult).where(ScreenerResult.user_id == user_id)
    if filters.asset_class is not None:
        query = query.where(ScreenerResult.asset_class == filters.asset_class)
    if filters.status is not None:
        query = query.where(ScreenerResult.status == filters.status)
    if filters.exchange:
        query = query.where(ScreenerResult.exchange == filters.exchange.strip().upper())
    if filters.screener_import_id is not None:
        query = query.where(ScreenerResult.screener_import_id == filters.screener_import_id)
    if filters.min_volume is not None:
        query = query.where(ScreenerResult.volume >= filters.min_volume)
    if filters.min_relative_volume is not None:
        query = query.where(ScreenerResult.relative_volume >= filters.min_relative_volume)
    if filters.min_rsi14 is not None:
        query = query.where(ScreenerResult.rsi14 >= filters.min_rsi14)
    if filters.max_rsi14 is not None:
        query = query.where(ScreenerResult.rsi14 <= filters.max_rsi14)
    return query


def get_screener_import(db: Session, user_id: int, import_id: int) -> ScreenerImport | None:
    return db.scalar(
        select(ScreenerImport)
        .where(ScreenerImport.id == import_id)
        .where(ScreenerImport.user_id == user_id)
    )


def get_screener_result(db: Session, user_id: int, result_id: int) -> ScreenerResult | None:
    return db.scalar(
        select(ScreenerResult)
        .where(ScreenerResult.id == result_id)
        .where(ScreenerResult.user_id == user_id)
    )


def bulk_update_screener_result_status(
    db: Session,
    user_id: int,
    result_ids: list[int],
    target_status: ScreenerResultStatus,
) -> tuple[list[ScreenerResult], list[int]]:
    if target_status not in SCREENER_BULK_REVIEW_STATUSES:
        return [], result_ids

    unique_ids = list(dict.fromkeys(result_ids))
    results = list(
        db.scalars(
            select(ScreenerResult)
            .where(ScreenerResult.user_id == user_id)
            .where(ScreenerResult.id.in_(unique_ids))
        )
    )
    result_by_id = {result.id: result for result in results}
    updated: list[ScreenerResult] = []
    skipped_ids: list[int] = []
    for result_id in unique_ids:
        result = result_by_id.get(result_id)
        if result is None or result.status not in SCREENER_BULK_REVIEW_STATUSES:
            skipped_ids.append(result_id)
            continue
        result.status = target_status
        updated.append(result)

    db.commit()
    for result in updated:
        db.refresh(result)
    return updated, skipped_ids


def convert_screener_result_to_watchlist(
    db: Session, user_id: int, result_id: int
) -> ScreenerResult | None:
    result = get_screener_result(db, user_id, result_id)
    if result is None:
        return None

    if result.watchlist_item_id is not None:
        return result

    existing_item = get_watchlist_item_by_symbol(db, user_id, result.symbol)

    if existing_item is not None:
        result.watchlist_item_id = existing_item.id
        result.status = ScreenerResultStatus.DUPLICATE
        db.commit()
        db.refresh(result)
        return result

    payload = WatchlistItemCreate(
        symbol=result.symbol,
        name=result.name,
        asset_class=result.asset_class,
        exchange=result.exchange,
        currency=result.currency,
    )
    try:
        item = create_watchlist_item(db, user_id, payload)
    except DuplicateWatchlistSymbolError:
        db.rollback()
        item = get_watchlist_item_by_symbol(db, user_id, result.symbol)
        if item is None:
            raise

    result.watchlist_item_id = item.id
    result.status = ScreenerResultStatus.WATCHLIST_ADDED
    db.commit()
    db.refresh(result)
    return result


def normalize_header(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").split())


def normalize_symbol(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None


def normalize_optional_uppercase(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().upper()
    return normalized or None


def normalize_optional_text(value: str | None, max_length: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized[:max_length] or None


def parse_optional_decimal(
    value: str | None, field: str, row_number: int, errors: list[ScreenerImportError]
) -> Decimal | None:
    if value is None or not value.strip():
        return None
    normalized = value.strip().replace("%", "").replace(",", "")
    multiplier = Decimal("1")
    suffix = normalized[-1:].upper()
    if suffix in {"K", "M", "B", "T"}:
        normalized = normalized[:-1]
        multiplier = {
            "K": Decimal("1000"),
            "M": Decimal("1000000"),
            "B": Decimal("1000000000"),
            "T": Decimal("1000000000000"),
        }[suffix]
    try:
        return Decimal(normalized) * multiplier
    except InvalidOperation:
        errors.append(ScreenerImportError(row_number, field, "Invalid number."))
        return None


def sanitize_file_name(file_name: str | None) -> str | None:
    if file_name is None:
        return None
    normalized = file_name.strip().replace("\\", "/").split("/")[-1]
    return normalized[:255] or None
