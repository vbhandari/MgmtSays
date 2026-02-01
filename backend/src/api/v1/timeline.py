"""Timeline endpoints for viewing insights over time."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.models.schemas.responses.timeline import (
    TimelineResponse,
    TimelineItemResponse,
)
from src.services.timeline_service import TimelineService
from src.services.analysis_service import AnalysisService
from src.repositories.analysis_repository import AnalysisRepository
from src.utils.exceptions import NotFoundError

router = APIRouter()


def get_timeline_service(db: AsyncSession = Depends(get_db)) -> TimelineService:
    """Get timeline service with database session."""
    return TimelineService(AnalysisRepository(db))


@router.get("/company/{company_id}", response_model=TimelineResponse)
async def get_company_timeline(
    company_id: str,
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    group_by: str = "quarter",
    service: TimelineService = Depends(get_timeline_service),
):
    """
    Get timeline of insights for a company.
    
    Returns insights organized chronologically, grouped by time period.
    
    - **company_id**: ID of the company
    - **category**: Optional filter by category
    - **start_date**: Optional start date (YYYY-MM-DD)
    - **end_date**: Optional end date (YYYY-MM-DD)
    - **group_by**: Grouping period (quarter, year, month)
    """
    try:
        timeline = await service.get_timeline(
            company_id=company_id,
            category=category,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )
        return TimelineResponse.model_validate(timeline)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )


@router.get("/company/{company_id}/trends")
async def get_insight_trends(
    company_id: str,
    service: TimelineService = Depends(get_timeline_service),
):
    """
    Get trend analysis for a company's insights.
    
    Returns:
    - New initiatives per period
    - Reiterated initiatives
    - Modified/updated initiatives
    - Category distribution over time
    """
    try:
        trends = await service.get_trends(company_id)
        return trends
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )


@router.get("/company/{company_id}/initiative/{initiative_id}/history")
async def get_initiative_history(
    company_id: str,
    initiative_id: str,
    service: TimelineService = Depends(get_timeline_service),
):
    """
    Get the history of a specific initiative across documents.
    
    Shows when the initiative was first mentioned, reiterated, and any changes over time.
    """
    try:
        history = await service.get_initiative_history(
            company_id=company_id,
            initiative_id=initiative_id,
        )
        return history
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Initiative not found",
        )
