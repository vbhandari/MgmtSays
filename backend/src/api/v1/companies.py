"""Company management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, PaginationDep
from src.models.schemas.requests.company import CompanyCreate, CompanyUpdate
from src.models.schemas.responses.company import (
    CompanyResponse,
    CompanyListResponse,
    CompanyDetailResponse,
)
from src.services.company_service import CompanyService
from src.repositories.company_repository import CompanyRepository
from src.utils.exceptions import NotFoundError, ValidationError

router = APIRouter()


def get_company_service(db: AsyncSession = Depends(get_db)) -> CompanyService:
    """Get company service with database session."""
    return CompanyService(CompanyRepository(db))


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    pagination: PaginationDep,
    search: str | None = None,
    service: CompanyService = Depends(get_company_service),
):
    """
    List all companies with optional search and pagination.
    
    - **search**: Optional search query for company name or ticker
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    companies, total = await service.list_companies(
        search=search,
        offset=pagination.offset,
        limit=pagination.page_size,
    )
    return CompanyListResponse(
        items=[CompanyResponse.model_validate(c) for c in companies],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
):
    """
    Create a new company.
    
    - **ticker**: Stock ticker symbol (1-5 uppercase letters)
    - **name**: Company name
    - **description**: Optional company description
    """
    try:
        company = await service.create_company(data)
        return CompanyResponse.model_validate(company)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: str,
    service: CompanyService = Depends(get_company_service),
):
    """
    Get company details by ID.
    
    Returns company information along with document and analysis counts.
    """
    try:
        company = await service.get_company_with_stats(company_id)
        return CompanyDetailResponse.model_validate(company)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )


@router.get("/ticker/{ticker}", response_model=CompanyDetailResponse)
async def get_company_by_ticker(
    ticker: str,
    service: CompanyService = Depends(get_company_service),
):
    """
    Get company details by ticker symbol.
    
    - **ticker**: Stock ticker symbol (case-insensitive)
    """
    try:
        company = await service.get_company_by_ticker(ticker.upper())
        return CompanyDetailResponse.model_validate(company)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found",
        )


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service),
):
    """
    Update company information.
    
    All fields are optional - only provided fields will be updated.
    """
    try:
        company = await service.update_company(company_id, data)
        return CompanyResponse.model_validate(company)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: str,
    service: CompanyService = Depends(get_company_service),
):
    """
    Delete a company and all associated data.
    
    **Warning**: This will also delete all documents and analyses for this company.
    """
    try:
        await service.delete_company(company_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID '{company_id}' not found",
        )
