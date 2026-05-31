from fastapi.testclient import TestClient

from app.api.routes import health
from app.main import create_app


def test_health_check_returns_service_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Cilly Trading Signal API",
        "version": "0.1.0",
        "environment": "development",
    }


def test_detailed_health_check_returns_safe_status(monkeypatch) -> None:
    class HealthySession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def execute(self, statement):
            return None

    monkeypatch.setattr(health, "SessionLocal", HealthySession)
    client = TestClient(create_app())

    response = client.get("/api/health/details")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Cilly Trading Signal API"
    assert body["version"] == "0.1.0"
    assert body["environment"] == "development"
    assert body["checks"]["database"] == {"status": "ok", "reachable": True}
    assert body["checks"]["migrations"] == {
        "status": "ok",
        "expected_latest_revision": "20260530_0008",
        "expected_latest_revision_present": True,
    }
    assert body["checks"]["configuration"] == {
        "status": "ok",
        "safe_config_summary_only": True,
        "auth_cookie_secure": False,
        "market_data_provider_sync_enabled": False,
        "telegram_alert_routing_enabled": False,
    }
    serialized = response.text.lower()
    assert "secret" not in serialized
    assert "password" not in serialized
    assert "database_url" not in serialized


def test_detailed_health_check_reports_database_failure(monkeypatch) -> None:
    class FailingSession:
        def __enter__(self):
            raise health.SQLAlchemyError("database unavailable")

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr(health, "SessionLocal", FailingSession)
    client = TestClient(create_app())

    response = client.get("/api/health/details")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == {"status": "degraded", "reachable": False}
