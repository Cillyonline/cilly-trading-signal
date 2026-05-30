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
