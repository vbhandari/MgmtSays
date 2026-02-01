"""Insight response schemas."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EvidenceResponse(BaseModel):
    """Evidence/citation response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    quote: str
    context: str | None = None
    page_number: int | None = None
    section: str | None = None
    relevance_score: float


class InsightResponse(BaseModel):
    """Insight response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    initiative_id: str | None = None
    title: str
    description: str
    category: str
    confidence_score: float
    confidence_level: str
    first_mentioned_at: datetime | None = None
    mention_count: int = 1
    is_new: bool = True
    is_reiterated: bool = False
    is_modified: bool = False
    created_at: datetime


class InsightDetailResponse(InsightResponse):
    """Insight detail response with evidence."""

    evidence: list[EvidenceResponse] = []
    related_insights: list[str] = []  # IDs of related insights


class InsightListResponse(BaseModel):
    """Paginated insight list response."""

    items: list[InsightResponse]
    total: int
    page: int
    page_size: int

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.page * self.page_size < self.total


class AnalysisStatusResponse(BaseModel):
    """Analysis status response."""

    analysis_id: str
    status: str  # pending, processing, completed, failed
    message: str | None = None
    progress: float | None = None  # 0-1
    started_at: datetime | None = None
    completed_at: datetime | None = None
