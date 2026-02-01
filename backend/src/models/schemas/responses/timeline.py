"""Timeline response schemas."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict

from src.models.schemas.responses.insight import InsightResponse


class TimelineItemResponse(BaseModel):
    """Single timeline item response."""

    model_config = ConfigDict(from_attributes=True)

    period: str  # e.g., "Q2 2024", "2024", "2024-06"
    period_start: datetime
    period_end: datetime
    insights: list[InsightResponse]
    new_count: int
    reiterated_count: int
    modified_count: int


class TimelineResponse(BaseModel):
    """Full timeline response."""

    company_id: str
    items: list[TimelineItemResponse]
    total_insights: int
    period_count: int
    earliest_date: datetime | None = None
    latest_date: datetime | None = None


class TrendDataPoint(BaseModel):
    """Single data point in trend analysis."""

    period: str
    count: int
    category_breakdown: dict[str, int] = {}


class TrendsResponse(BaseModel):
    """Trends analysis response."""

    company_id: str
    new_initiatives: list[TrendDataPoint]
    reiterated_initiatives: list[TrendDataPoint]
    category_distribution: dict[str, int]
    most_discussed: list[str]  # Top initiative IDs


class InitiativeHistoryItem(BaseModel):
    """Single item in initiative history."""

    document_id: str
    document_title: str
    document_date: datetime | None
    mention_type: str  # "first", "reiterated", "modified"
    quote: str
    confidence_score: float


class InitiativeHistoryResponse(BaseModel):
    """Initiative history response."""

    initiative_id: str
    name: str
    category: str
    history: list[InitiativeHistoryItem]
    total_mentions: int
    first_mentioned: datetime
    last_mentioned: datetime
