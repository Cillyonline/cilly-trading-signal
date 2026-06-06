from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.enums import MarketDataSource, MarketDataStatus, MarketDataSyncStatus
from app.models.enums import Timeframe
from app.models.market_data import MarketDataSeries
from app.models.user import User
from app.models.watchlist import WatchlistItem
from app.schemas.analysis import MarketDataAnalysisResult
from app.schemas.imports import (
    CsvImportResult,
    ImportHistoryItem,
    MarketDataSyncRequest,
    MarketDataSyncResponse,
    ProviderTimeframeCapabilityRead,
)
from app.services.analysis import analyze_market_data_series
from app.services.csv_import import MAX_CSV_UPLOAD_BYTES, import_tradingview_csv
from app.services.market_data_sync import (
    AlphaVantageDailyProvider,
    MarketDataProvider,
    TwelveDataDailyProvider,
    YahooFinanceUnofficialProvider,
    build_market_data_sync_plan,
    provider_timeframe_capabilities,
    sync_and_persist_market_data_series,
)
from app.services.watchlist import get_watchlist_item

router = APIRouter(prefix="/imports", tags=["imports"])
DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def get_market_data_provider() -> MarketDataProvider | None:
    if not settings.market_data_provider_sync_enabled:
        return None
    provider_name = (settings.market_data_provider or "").strip().lower()
    if provider_name == "alpha_vantage" and settings.market_data_api_key:
        return AlphaVantageDailyProvider(settings.market_data_api_key)
    if provider_name == "twelve_data" and settings.market_data_api_key:
        return TwelveDataDailyProvider(settings.market_data_api_key)
    if provider_name == "yahoo_finance_unofficial":
        return YahooFinanceUnofficialProvider()
    return None


@router.post("/csv", response_model=CsvImportResult)
async def import_csv(
    db: DbSession,
    user: CurrentUser,
    watchlist_item_id: Annotated[int, Form()],
    timeframe: Annotated[Timeframe, Form()],
    file: Annotated[UploadFile, File()],
) -> CsvImportResult:
    watchlist_item = get_watchlist_item(db, user.id, watchlist_item_id)
    if watchlist_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    content_bytes = await file.read()
    if len(content_bytes) > MAX_CSV_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=[
                {
                    "row": None,
                    "field": "file",
                    "message": f"CSV file must be at most {MAX_CSV_UPLOAD_BYTES} bytes.",
                }
            ],
        )

    try:
        content = content_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from error

    result = import_tradingview_csv(
        db=db,
        watchlist_item=watchlist_item,
        timeframe=timeframe,
        file_name=file.filename,
        content=content,
    )
    if result.errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[error.model_dump() for error in result.errors],
        )
    return result


@router.get("", response_model=list[ImportHistoryItem])
def list_imports(db: DbSession, user: CurrentUser) -> list[ImportHistoryItem]:
    series_rows = db.execute(
        select(MarketDataSeries)
        .join(MarketDataSeries.watchlist_item)
        .where(WatchlistItem.user_id == user.id)
        .order_by(MarketDataSeries.imported_at.desc(), MarketDataSeries.id.desc())
    ).scalars()

    return [
        ImportHistoryItem(
            series_id=series.id,
            watchlist_item_id=series.watchlist_item_id,
            symbol=series.watchlist_item.symbol,
            timeframe=series.timeframe,
            status=series.status,
            candle_count=series.candle_count,
            start_time=series.start_time,
            end_time=series.end_time,
            imported_at=series.imported_at,
            source=series.source,
            freshness_status=series.freshness_status,
            sync_status=series.sync_status,
            last_synced_at=series.last_synced_at,
            provider_name=series.provider_name,
            file_name=series.file_name,
        )
        for series in series_rows
    ]


@router.post("/sync", response_model=MarketDataSyncResponse)
def sync_market_data(
    payload: MarketDataSyncRequest,
    db: DbSession,
    user: CurrentUser,
    provider: Annotated[MarketDataProvider | None, Depends(get_market_data_provider)],
) -> MarketDataSyncResponse:
    watchlist_item = get_watchlist_item(db, user.id, payload.watchlist_item_id)
    if watchlist_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    series = get_or_create_provider_series(db, watchlist_item, payload.timeframe)
    plan = build_market_data_sync_plan(
        symbol=watchlist_item.symbol,
        timeframe=payload.timeframe,
        provider_sync_enabled=settings.market_data_provider_sync_enabled,
        provider_name=settings.market_data_provider,
    )
    sync_and_persist_market_data_series(db, series, plan, provider)
    db.commit()
    db.refresh(series)
    return to_market_data_sync_response(series)


@router.post("/{series_id}/analyze", response_model=MarketDataAnalysisResult)
def analyze_import(series_id: int, db: DbSession, user: CurrentUser) -> MarketDataAnalysisResult:
    series = db.get(MarketDataSeries, series_id)
    if series is None or series.watchlist_item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Market data series not found.",
        )
    return analyze_market_data_series(db, series)


def get_or_create_provider_series(
    db: Session,
    watchlist_item: WatchlistItem,
    timeframe: Timeframe,
) -> MarketDataSeries:
    series = db.scalar(
        select(MarketDataSeries)
        .where(MarketDataSeries.watchlist_item_id == watchlist_item.id)
        .where(MarketDataSeries.timeframe == timeframe)
        .where(MarketDataSeries.source == MarketDataSource.PROVIDER)
        .order_by(MarketDataSeries.imported_at.desc(), MarketDataSeries.id.desc())
    )
    if series is not None:
        return series

    series = MarketDataSeries(
        watchlist_item_id=watchlist_item.id,
        source=MarketDataSource.PROVIDER,
        timeframe=timeframe,
        candle_count=0,
        status=MarketDataStatus.IMPORTED,
        sync_status=MarketDataSyncStatus.NOT_APPLICABLE,
    )
    db.add(series)
    db.flush()
    return series


def to_market_data_sync_response(series: MarketDataSeries) -> MarketDataSyncResponse:
    return MarketDataSyncResponse(
        watchlist_item_id=series.watchlist_item_id,
        series_id=series.id,
        source=series.source,
        timeframe=series.timeframe,
        provider_name=series.provider_name,
        provider_symbol=series.provider_symbol,
        provider_exchange=series.provider_exchange,
        provider_timeframe=series.provider_timeframe,
        sync_status=series.sync_status,
        freshness_status=series.freshness_status,
        last_synced_at=series.last_synced_at,
        end_time=series.end_time,
        sync_error_code=series.sync_error_code,
        sync_error_message=series.sync_error_message,
        provider_capabilities=to_provider_capability_reads(series.provider_name),
    )


def to_provider_capability_reads(
    provider_name: str | None,
) -> list[ProviderTimeframeCapabilityRead]:
    return [
        ProviderTimeframeCapabilityRead(
            timeframe=capability.timeframe,
            supported=capability.supported,
            reason=capability.reason,
        )
        for capability in provider_timeframe_capabilities(provider_name)
    ]
