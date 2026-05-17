from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import alerts, auth, export, health, imports, performance, signals, trades
from app.api.routes import watchlist, webhooks
from app.api.routes import settings as settings_routes
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(alerts.router, prefix="/api")
    app.include_router(export.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    app.include_router(imports.router, prefix="/api")
    app.include_router(performance.router, prefix="/api")
    app.include_router(settings_routes.router, prefix="/api")
    app.include_router(signals.router, prefix="/api")
    app.include_router(trades.router, prefix="/api")
    app.include_router(watchlist.router, prefix="/api")
    app.include_router(webhooks.router, prefix="/api")
    return app


app = create_app()
