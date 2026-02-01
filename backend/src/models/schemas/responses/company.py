"""Company response schemas."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CompanyResponse(BaseModel):
    """Company response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    ticker: str
    name: str
    description: str | None = None
    sector: str | None = None
    industry: str | None = None
    created_at: datetime
    updated_at: datetime


class CompanyDetailResponse(CompanyResponse):
    """Company detail response with additional stats."""

    document_count: int = 0
    analysis_count: int = 0
    latest_analysis_at: datetime | None = None


class CompanyListResponse(BaseModel):
    """Paginated company list response."""

    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.page * self.page_size < self.total
