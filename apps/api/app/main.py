from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, imports, performance, signals, trades, watchlist
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
    app.include_router(auth.router, prefix="/api")
    app.include_router(imports.router, prefix="/api")
    app.include_router(performance.router, prefix="/api")
    app.include_router(signals.router, prefix="/api")
    app.include_router(trades.router, prefix="/api")
    app.include_router(watchlist.router, prefix="/api")
    return app


app = create_app()
