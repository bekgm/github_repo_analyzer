"""
FastAPI application factory.

Assembles middleware, exception handlers, routers, and lifecycle events.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.rate_limit import limiter
from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.exceptions import AppError, NotFoundError
from app.core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hooks."""
    setup_logging()
    yield
    # Shutdown: close pools, connections, etc.


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="GitHub Repository Analyzer",
        description=(
            "Analyse any public GitHub repository: code metrics, contributor stats, "
            "language distribution, and AI-powered insights via Gemini."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:7000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Exception handlers ───────────────────────────────────────────────
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": exc.message, "code": exc.code},
        )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"error": exc.message, "code": exc.code},
        )

    # ── Routers ──────────────────────────────────────────────────────────
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(analysis_router, prefix="/api/v1")

    return app


app = create_app()
