"""FastAPI dependency injection utilities."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings, get_settings
from src.db.session import get_db_session


# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]


# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async for session in get_db_session():
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


# Service dependencies (will be populated as services are created)
def get_company_service():
    """Get company service instance."""
    from src.services.company_service import CompanyService
    from src.repositories.company_repository import CompanyRepository
    
    return CompanyService(CompanyRepository())


def get_document_service():
    """Get document service instance."""
    from src.services.document_service import DocumentService
    from src.repositories.document_repository import DocumentRepository
    from src.storage import get_storage
    
    return DocumentService(
        repository=DocumentRepository(),
        storage=get_storage(),
    )


def get_analysis_service():
    """Get analysis service instance."""
    from src.services.analysis_service import AnalysisService
    from src.repositories.analysis_repository import AnalysisRepository
    
    return AnalysisService(AnalysisRepository())


def get_timeline_service():
    """Get timeline service instance."""
    from src.services.timeline_service import TimelineService
    
    return TimelineService()


# Pagination dependencies
class PaginationParams:
    """Common pagination parameters."""

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be >= 1",
            )
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be between 1 and 100",
            )
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


PaginationDep = Annotated[PaginationParams, Depends()]
