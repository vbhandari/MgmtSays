"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.middleware.cors import setup_cors
from src.api.middleware.rate_limit import setup_rate_limiting
from src.api.v1.router import api_router
from src.config.logging import get_logger, setup_logging
from src.config.settings import get_settings
from src.db.base import Base
from src.db.session import engine

# Import models to register them with Base
from src.models.db import analysis, company, document  # noqa: F401
from src.utils.exceptions import MgmtSaysError

# Path to frontend build (backend/src/main.py -> backend/src -> backend -> project_root -> frontend/dist)
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting MgmtSays API")

    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_dsn.split('@')[-1] if '@' in settings.database_dsn else settings.database_dsn}")

    # Create tables in development mode (use migrations in production)
    if settings.is_development:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down MgmtSays API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="MgmtSays API",
        description="Management Disclosure Intelligence Platform API",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Setup middleware
    setup_cors(app)
    if settings.is_production:
        setup_rate_limiting(app)

    # Register exception handlers
    @app.exception_handler(MgmtSaysError)
    async def mgmtsays_error_handler(request: Request, exc: MgmtSaysError):
        """Handle custom application errors."""
        status_code = 500
        if exc.code == "NOT_FOUND":
            status_code = 404
        elif exc.code == "VALIDATION_ERROR":
            status_code = 400
        elif exc.code == "AUTHENTICATION_ERROR":
            status_code = 401
        elif exc.code == "AUTHORIZATION_ERROR":
            status_code = 403
        elif exc.code == "RATE_LIMIT_ERROR":
            status_code = 429

        return JSONResponse(
            status_code=status_code,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        """Handle unexpected errors."""
        logger = get_logger(__name__)
        logger.exception("Unhandled exception", exc_info=exc)

        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {} if settings.is_production else {"exception": str(exc)},
            },
        )

    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)

    # Serve frontend static files (if built)
    index_html = FRONTEND_DIR / "index.html"
    if index_html.exists():
        # Serve static assets (JS, CSS, images from Vite build)
        assets_dir = FRONTEND_DIR / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

        # Serve other static files at root (favicon, etc.)
        @app.get("/favicon.ico")
        async def serve_favicon():
            favicon = FRONTEND_DIR / "favicon.ico"
            if favicon.exists():
                return FileResponse(favicon)
            return JSONResponse(status_code=404, content={"detail": "Not found"})

        # Serve index.html for SPA root
        @app.get("/")
        async def serve_spa_root():
            return FileResponse(index_html)

        # Catch-all for SPA client-side routing
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            """Serve SPA for all non-API routes."""
            # Skip API routes (handled by router above)
            if full_path.startswith("api/"):
                return JSONResponse(status_code=404, content={"detail": "Not found"})

            # Check if it's a static file in dist
            file_path = FRONTEND_DIR / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)

            # Return index.html for client-side routing (React Router)
            return FileResponse(index_html)
    else:
        # No frontend build - redirect to API docs
        @app.get("/")
        async def redirect_to_docs():
            """Redirect to API docs when frontend is not built."""
            return RedirectResponse(url="/docs")

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
    )
