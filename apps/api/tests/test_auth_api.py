from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.models import *  # noqa: F403
from app.services.auth import reset_login_rate_limit


@pytest.fixture()
def client() -> Iterator[TestClient]:
    reset_login_rate_limit()
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

    yield TestClient(app)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    reset_login_rate_limit()


def test_login_sets_http_only_cookie(client: TestClient) -> None:
    response = login(client)

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"
    assert "httponly" in response.headers["set-cookie"].lower()


def test_login_rejects_invalid_password(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_login_rate_limits_repeated_failed_attempts(client: TestClient) -> None:
    for _ in range(5):
        response = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password."

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "change-this-password"},
    )

    assert response.status_code == 429
    assert response.json()["detail"] == "Too many login attempts. Try again later."


def test_successful_login_clears_failed_attempts(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401

    response = login(client)
    assert response.status_code == 200

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_logout_clears_cookie(client: TestClient) -> None:
    login(client)

    response = client.post("/api/auth/logout")

    assert response.status_code == 204
    assert "cilly_session" in response.headers["set-cookie"]


def test_protected_route_rejects_unauthenticated_request(client: TestClient) -> None:
    response = client.get("/api/watchlist")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_authenticated_request_can_access_protected_route(client: TestClient) -> None:
    login(client)

    response = client.get("/api/watchlist")

    assert response.status_code == 200
    assert response.json() == []


def test_me_returns_authenticated_user(client: TestClient) -> None:
    login(client)

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"


def login(client: TestClient):
    return client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "change-this-password"},
    )
