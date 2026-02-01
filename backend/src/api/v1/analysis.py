"""Analysis endpoints for running NLP extraction."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, PaginationDep
from src.models.schemas.requests.analysis import AnalysisRequest
from src.models.schemas.responses.insight import (
    InsightResponse,
    InsightListResponse,
    InsightDetailResponse,
    AnalysisStatusResponse,
)
from src.services.analysis_service import AnalysisService
from src.repositories.analysis_repository import AnalysisRepository
from src.utils.exceptions import NotFoundError, NLPError

router = APIRouter()


def get_analysis_service(db: AsyncSession = Depends(get_db)) -> AnalysisService:
    """Get analysis service with database session."""
    return AnalysisService(AnalysisRepository(db))


@router.post("/run", response_model=AnalysisStatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    service: AnalysisService = Depends(get_analysis_service),
):
    """
    Trigger analysis for a company's documents.
    
    This starts an asynchronous analysis job that:
    1. Retrieves relevant document chunks
    2. Extracts strategic initiatives using DSPy
    3. Deduplicates and clusters similar initiatives
    4. Stores results with citations
    
    - **company_id**: ID of the company to analyze
    - **document_ids**: Optional list of specific document IDs to analyze
    - **force_rerun**: Whether to rerun analysis even if recent results exist
    """
    try:
        analysis = await service.create_analysis(request)
        
        # Run analysis in background
        background_tasks.add_task(
            service.run_analysis,
            analysis.id,
        )
        
        return AnalysisStatusResponse(
            analysis_id=analysis.id,
            status="pending",
            message="Analysis started. Check status endpoint for progress.",
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_id: str,
    service: AnalysisService = Depends(get_analysis_service),
):
    """
    Get the status of an analysis job.
    
    Status values:
    - **pending**: Analysis queued but not started
    - **processing**: Analysis in progress
    - **completed**: Analysis finished successfully
    - **failed**: Analysis failed with error
    """
    try:
        analysis = await service.get_analysis(analysis_id)
        return AnalysisStatusResponse(
            analysis_id=analysis.id,
            status=analysis.status,
            message=analysis.error_message,
            progress=analysis.progress,
            started_at=analysis.started_at,
            completed_at=analysis.completed_at,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found",
        )


@router.get("/company/{company_id}/insights", response_model=InsightListResponse)
async def get_company_insights(
    company_id: str,
    pagination: PaginationDep,
    category: str | None = None,
    confidence_min: float | None = None,
    service: AnalysisService = Depends(get_analysis_service),
):
    """
    Get all insights extracted for a company.
    
    - **company_id**: ID of the company
    - **category**: Filter by category (strategy, expansion, product, mna, guidance)
    - **confidence_min**: Minimum confidence score (0-1)
    - **page**: Page number
    - **page_size**: Items per page
    """
    try:
        insights, total = await service.get_insights(
            company_id=company_id,
            category=category,
            confidence_min=confidence_min,
            offset=pagination.offset,
            limit=pagination.page_size,
        )
        return InsightListResponse(
            items=[InsightResponse.model_validate(i) for i in insights],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )


@router.get("/insights/{insight_id}", response_model=InsightDetailResponse)
async def get_insight(
    insight_id: str,
    service: AnalysisService = Depends(get_analysis_service),
):
    """
    Get detailed information about a specific insight.
    
    Returns the insight along with all supporting evidence and citations.
    """
    try:
        insight = await service.get_insight_detail(insight_id)
        return InsightDetailResponse.model_validate(insight)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insight with ID '{insight_id}' not found",
        )


@router.delete("/company/{company_id}/insights", status_code=status.HTTP_204_NO_CONTENT)
async def clear_company_insights(
    company_id: str,
    service: AnalysisService = Depends(get_analysis_service),
):
    """
    Clear all insights for a company.
    
    This removes all extracted insights, allowing for a fresh analysis.
    """
    try:
        await service.clear_insights(company_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )
