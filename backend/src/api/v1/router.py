"""Main API v1 router combining all endpoint routers."""

from fastapi import APIRouter

from src.api.v1 import companies, documents, analysis, timeline, health, search

api_router = APIRouter()

# Include all routers
api_router.include_router(
    health.router,
    tags=["Health"],
)

api_router.include_router(
    companies.router,
    prefix="/companies",
    tags=["Companies"],
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["Analysis"],
)

api_router.include_router(
    timeline.router,
    prefix="/timeline",
    tags=["Timeline"],
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"],
)
