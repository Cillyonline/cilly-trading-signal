from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.screener import MAX_SCREENER_UPLOAD_BYTES
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403
from app.models.alert import Alert
from app.models.enums import (
    AssetClass,
    ScreenerImportSource,
    ScreenerImportStatus,
    ScreenerResultStatus,
    UserRole,
)
from app.models.screener import ScreenerImport, ScreenerResult
from app.models.signal import Signal
from app.models.trade import Trade
from app.models.user import User


@pytest.fixture()
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    test_client = TestClient(app)
    test_client.testing_session_factory = TestingSessionLocal  # type: ignore[attr-defined]
    login(test_client)

    yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def login(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "change-this-password"},
    )
    assert response.status_code == 200


def post_screener_import(
    client: TestClient,
    csv_content: str,
    asset_class: str = "stock",
    file_name: str = "screener.csv",
    screener_preset: str | None = "US review candidates",
) -> object:
    data = {"asset_class": asset_class}
    if screener_preset is not None:
        data["screener_preset"] = screener_preset
    return client.post(
        "/api/screener/imports",
        data=data,
        files={"file": (file_name, csv_content, "text/csv")},
    )


def valid_screener_csv() -> str:
    return "\n".join(
        [
            "Symbol,Name,Exchange,Sector,Price,Change %,Volume,Relative Volume,Market Cap,RSI (14)",
            "AAPL,Apple Inc.,NASDAQ,Technology,190.50,1.25%,1.2M,1.10,2.5T,55.2",
            "MSFT,Microsoft Corp.,NASDAQ,Technology,420.00,-0.50%,900K,0.95,3.1T,60.1",
        ]
    )


def test_import_screener_csv_persists_candidates(client: TestClient) -> None:
    response = post_screener_import(client, valid_screener_csv())

    assert response.status_code == 201
    body = response.json()
    assert body["source"] == "tradingview_screener_csv"
    assert body["asset_class"] == "stock"
    assert body["file_name"] == "screener.csv"
    assert body["screener_preset"] == "US review candidates"
    assert body["row_count"] == 2
    assert body["accepted_count"] == 2
    assert body["rejected_count"] == 0
    assert body["duplicate_count"] == 0
    assert body["status"] == "imported"

    results_response = client.get("/api/screener/results")
    assert results_response.status_code == 200
    results = results_response.json()
    assert [result["symbol"] for result in results] == ["MSFT", "AAPL"]
    assert {result["status"] for result in results} == {"candidate"}
    assert all(result["watchlist_item_id"] is None for result in results)


def test_list_screener_results_filters_and_sorts_candidates(client: TestClient) -> None:
    stock_import = post_screener_import(client, valid_screener_csv()).json()
    crypto_csv = "\n".join(
        [
            "Symbol,Exchange,Price,Volume,Relative Volume,RSI (14)",
            "BTCUSDT,BINANCE,68000,2.5M,1.30,58.0",
            "ETHUSDT,BINANCE,3600,900K,0.80,49.0",
        ]
    )
    post_screener_import(client, crypto_csv, asset_class="crypto")

    response = client.get(
        "/api/screener/results",
        params={
            "asset_class": "crypto",
            "exchange": "binance",
            "min_relative_volume": "1.0",
            "min_rsi14": "50",
            "sort_by": "volume",
            "sort_direction": "asc",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert [result["symbol"] for result in body] == ["BTCUSDT"]
    assert body[0]["asset_class"] == "crypto"

    stock_response = client.get(
        "/api/screener/results",
        params={
            "screener_import_id": stock_import["id"],
            "sort_by": "relative_volume",
            "sort_direction": "desc",
        },
    )

    assert stock_response.status_code == 200
    assert [result["symbol"] for result in stock_response.json()] == ["AAPL", "MSFT"]


def test_list_screener_results_filters_by_status(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())
    result = next(
        result
        for result in client.get("/api/screener/results").json()
        if result["symbol"] == "AAPL"
    )
    client.post(f"/api/screener/results/{result['id']}/watchlist")

    response = client.get("/api/screener/results", params={"status": "watchlist_added"})

    assert response.status_code == 200
    body = response.json()
    assert [result["symbol"] for result in body] == ["AAPL"]
    assert body[0]["status"] == "watchlist_added"


def test_list_screener_results_adds_review_only_priority(client: TestClient) -> None:
    csv_content = "\n".join(
        [
            "Symbol,Price,Volume,Relative Volume,RSI (14),EMA50",
            "NVDA,900,2500000,1.50,62,850",
            "THIN,10,,,88,12",
            "MID,50,500000,0.90,55,52",
        ]
    )
    post_screener_import(client, csv_content)

    response = client.get(
        "/api/screener/results", params={"sort_by": "symbol", "sort_direction": "asc"}
    )

    assert response.status_code == 200
    by_symbol = {result["symbol"]: result for result in response.json()}
    assert by_symbol["NVDA"]["review_priority"] == "high_review_priority"
    assert "liquidity_visible" in by_symbol["NVDA"]["review_priority_reasons"]
    assert by_symbol["THIN"]["review_priority"] == "low_review_priority"
    assert "volume_missing" in by_symbol["THIN"]["review_priority_reasons"]
    assert by_symbol["MID"]["review_priority"] == "normal"


def test_list_screener_results_page_returns_counts_and_page_items(client: TestClient) -> None:
    rows = ["Symbol,Volume,Relative Volume,RSI (14)"]
    rows.extend(f"AAPL{index},{1000 + index},1.{index},5{index}.0" for index in range(5))
    post_screener_import(client, "\n".join(rows))

    response = client.get(
        "/api/screener/results/page",
        params={"page": 2, "page_size": 2, "sort_by": "rank", "sort_direction": "asc"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 5
    assert body["page"] == 2
    assert body["page_size"] == 2
    assert body["total_pages"] == 3
    assert [result["symbol"] for result in body["items"]] == ["AAPL2", "AAPL3"]


def test_list_screener_results_page_applies_filters(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())

    response = client.get(
        "/api/screener/results/page",
        params={"min_relative_volume": "1.0", "sort_by": "relative_volume"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [result["symbol"] for result in body["items"]] == ["AAPL"]


def test_get_screener_import_returns_results(client: TestClient) -> None:
    created = post_screener_import(client, valid_screener_csv()).json()

    response = client.get(f"/api/screener/imports/{created['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert len(body["results"]) == 2
    assert {result["symbol"] for result in body["results"]} == {"AAPL", "MSFT"}


def test_list_screener_imports_requires_authentication(client: TestClient) -> None:
    client.post("/api/auth/logout")

    response = client.get("/api/screener/imports")

    assert response.status_code == 401


def test_import_screener_csv_rejects_missing_symbol_column(client: TestClient) -> None:
    response = post_screener_import(client, "Name,Price\nApple Inc.,190.50")

    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"row": None, "field": "symbol", "message": "Missing required column: symbol"}
    ]

    assert client.get("/api/screener/imports").json() == []


def test_import_screener_csv_rejects_invalid_symbol(client: TestClient) -> None:
    response = post_screener_import(client, "Symbol,Price\nAAPL<script>,190.50")

    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"row": 2, "field": "symbol", "message": "Symbol contains unsupported characters."}
    ]
    assert client.get("/api/screener/imports").json() == []


def test_import_screener_csv_rejects_invalid_numeric_value(client: TestClient) -> None:
    response = post_screener_import(client, "Symbol,Price\nAAPL,not-a-number")

    assert response.status_code == 422
    assert response.json()["detail"] == [
        {"row": 2, "field": "price", "message": "Invalid number."}
    ]
    assert client.get("/api/screener/imports").json() == []


def test_import_screener_csv_marks_duplicate_rows(client: TestClient) -> None:
    csv_content = "\n".join(
        [
            "Symbol,Exchange,Price",
            "AAPL,NASDAQ,190.50",
            "AAPL,NASDAQ,191.00",
        ]
    )

    response = post_screener_import(client, csv_content)

    assert response.status_code == 201
    body = response.json()
    assert body["accepted_count"] == 1
    assert body["duplicate_count"] == 1
    assert body["rejected_count"] == 1
    assert body["status"] == "partial"
    assert body["validation_errors"] == [
        {"row": 3, "field": "symbol", "message": "Duplicate screener row in import."}
    ]

    results = client.get("/api/screener/results").json()
    assert len(results) == 1
    assert results[0]["symbol"] == "AAPL"
    assert results[0]["status"] == "candidate"


def test_import_screener_csv_rejects_oversized_upload(client: TestClient) -> None:
    csv_content = "Symbol\n" + ("AAPL\n" * (MAX_SCREENER_UPLOAD_BYTES // 5 + 1))

    response = post_screener_import(client, csv_content)

    assert response.status_code == 413
    assert response.json()["detail"] == [
        {
            "row": None,
            "field": "file",
            "message": f"CSV file must be at most {MAX_SCREENER_UPLOAD_BYTES} bytes.",
        }
    ]


def test_import_screener_csv_enforces_candidate_row_limit(client: TestClient) -> None:
    rows = ["Symbol"]
    rows.extend(f"AAPL{index}" for index in range(501))

    response = post_screener_import(client, "\n".join(rows))

    assert response.status_code == 201
    body = response.json()
    assert body["accepted_count"] == 500
    assert body["rejected_count"] == 1
    assert body["status"] == "partial"
    assert body["validation_errors"] == [
        {
            "row": None,
            "field": "file",
            "message": "CSV can import at most 500 candidate rows.",
        }
    ]


def test_convert_screener_result_creates_watchlist_item_only(client: TestClient) -> None:
    imported = post_screener_import(client, valid_screener_csv()).json()
    result = next(
        result
        for result in client.get("/api/screener/results").json()
        if result["symbol"] == "AAPL"
    )

    response = client.post(f"/api/screener/results/{result['id']}/watchlist")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == result["id"]
    assert body["symbol"] == "AAPL"
    assert body["status"] == "watchlist_added"
    assert body["watchlist_item_id"] is not None

    watchlist = client.get("/api/watchlist").json()
    assert len(watchlist) == 1
    assert watchlist[0]["id"] == body["watchlist_item_id"]
    assert watchlist[0]["symbol"] == "AAPL"
    assert watchlist[0]["name"] == "Apple Inc."
    assert watchlist[0]["asset_class"] == "stock"
    assert watchlist[0]["exchange"] == "NASDAQ"

    with client.testing_session_factory() as db:  # type: ignore[attr-defined]
        assert db.query(Signal).count() == 0
        assert db.query(Trade).count() == 0
        assert db.query(Alert).count() == 0

    import_detail = client.get(f"/api/screener/imports/{imported['id']}").json()
    converted = next(result for result in import_detail["results"] if result["symbol"] == "AAPL")
    assert converted["watchlist_item_id"] == body["watchlist_item_id"]
    assert converted["status"] == "watchlist_added"


def test_bulk_update_screener_results_marks_review_statuses_only(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())
    results = client.get(
        "/api/screener/results", params={"sort_by": "symbol", "sort_direction": "asc"}
    ).json()

    response = client.patch(
        "/api/screener/results/status",
        json={"result_ids": [result["id"] for result in results], "status": "ignored"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["requested_count"] == 2
    assert body["updated_count"] == 2
    assert body["skipped_count"] == 0
    assert {result["status"] for result in body["results"]} == {"ignored"}
    ignored = client.get("/api/screener/results", params={"status": "ignored"}).json()
    assert {result["symbol"] for result in ignored} == {"AAPL", "MSFT"}


def test_bulk_update_screener_results_skips_watchlist_linked_results(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())
    results = client.get(
        "/api/screener/results", params={"sort_by": "symbol", "sort_direction": "asc"}
    ).json()
    aapl = next(result for result in results if result["symbol"] == "AAPL")
    msft = next(result for result in results if result["symbol"] == "MSFT")
    converted = client.post(f"/api/screener/results/{aapl['id']}/watchlist").json()

    response = client.patch(
        "/api/screener/results/status",
        json={"result_ids": [converted["id"], msft["id"], 9999], "status": "rejected"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["requested_count"] == 3
    assert body["updated_count"] == 1
    assert body["skipped_count"] == 2
    assert set(body["skipped_result_ids"]) == {converted["id"], 9999}
    updated_results = client.get("/api/screener/results").json()
    assert (
        next(result for result in updated_results if result["symbol"] == "AAPL")["status"]
        == "watchlist_added"
    )
    assert (
        next(result for result in updated_results if result["symbol"] == "MSFT")["status"]
        == "rejected"
    )


def test_bulk_update_screener_results_rejects_non_review_status(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())
    result = client.get("/api/screener/results").json()[0]

    response = client.patch(
        "/api/screener/results/status",
        json={"result_ids": [result["id"]], "status": "watchlist_added"},
    )

    assert response.status_code == 422


def test_convert_screener_result_links_existing_watchlist_duplicate(client: TestClient) -> None:
    watchlist_response = client.post(
        "/api/watchlist",
        json={"symbol": "AAPL", "asset_class": "stock", "name": "Existing Apple"},
    )
    assert watchlist_response.status_code == 201
    existing_item = watchlist_response.json()
    post_screener_import(client, valid_screener_csv())
    result = next(
        result
        for result in client.get("/api/screener/results").json()
        if result["symbol"] == "AAPL"
    )

    response = client.post(f"/api/screener/results/{result['id']}/watchlist")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "duplicate"
    assert body["watchlist_item_id"] == existing_item["id"]
    watchlist = client.get("/api/watchlist").json()
    assert len(watchlist) == 1
    assert watchlist[0]["name"] == "Existing Apple"


def test_convert_screener_result_is_idempotent(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())
    result = client.get("/api/screener/results").json()[0]

    first_response = client.post(f"/api/screener/results/{result['id']}/watchlist")
    second_response = client.post(f"/api/screener/results/{result['id']}/watchlist")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["watchlist_item_id"] == first_response.json()["watchlist_item_id"]
    assert len(client.get("/api/watchlist").json()) == 1


def test_convert_screener_result_requires_authentication(client: TestClient) -> None:
    post_screener_import(client, valid_screener_csv())
    result = client.get("/api/screener/results").json()[0]
    client.post("/api/auth/logout")

    response = client.post(f"/api/screener/results/{result['id']}/watchlist")

    assert response.status_code == 401


def test_convert_screener_result_hides_other_users_result(client: TestClient) -> None:
    with client.testing_session_factory() as db:  # type: ignore[attr-defined]
        other_user = User(
            email="other@example.com",
            password_hash="not-used",
            display_name="Other User",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)
        other_import = ScreenerImport(
            user_id=other_user.id,
            source=ScreenerImportSource.TRADINGVIEW_SCREENER_CSV,
            asset_class=AssetClass.STOCK,
            row_count=1,
            accepted_count=1,
            rejected_count=0,
            duplicate_count=0,
            status=ScreenerImportStatus.IMPORTED,
        )
        db.add(other_import)
        db.flush()
        other_result = ScreenerResult(
            screener_import_id=other_import.id,
            user_id=other_user.id,
            symbol="NVDA",
            asset_class=AssetClass.STOCK,
            status=ScreenerResultStatus.CANDIDATE,
        )
        db.add(other_result)
        db.commit()
        result_id = other_result.id

    response = client.post(f"/api/screener/results/{result_id}/watchlist")

    assert response.status_code == 404
    assert client.get("/api/watchlist").json() == []
