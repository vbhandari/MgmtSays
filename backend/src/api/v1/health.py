"""Health check endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.config.settings import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str
    environment: str
    database: str
    vector_store: str


class ReadinessResponse(BaseModel):
    """Readiness check response."""

    ready: bool
    checks: dict[str, bool]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version="0.1.0",
        environment=settings.environment,
        database="unknown",
        vector_store="unknown",
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check that verifies all dependencies are available.
    
    Checks:
    - Database connectivity
    - Vector store connectivity
    """
    checks = {
        "database": False,
        "vector_store": False,
    }

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:
        pass

    # Check vector store (ChromaDB)
    try:
        import chromadb
        settings = get_settings()
        client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        client.heartbeat()
        checks["vector_store"] = True
    except Exception:
        pass

    return ReadinessResponse(
        ready=all(checks.values()),
        checks=checks,
    )


@router.get("/live")
async def liveness_check():
    """Simple liveness check - returns 200 if the service is running."""
    return {"status": "alive"}
