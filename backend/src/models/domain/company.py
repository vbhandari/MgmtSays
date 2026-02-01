"""Company domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Company:
    """Company domain entity."""

    id: str
    ticker: str
    name: str
    description: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Computed/loaded fields
    document_count: int = 0
    analysis_count: int = 0
    latest_analysis_at: Optional[datetime] = None

    def __post_init__(self):
        """Normalize ticker to uppercase."""
        self.ticker = self.ticker.upper()

    @property
    def display_name(self) -> str:
        """Get display name with ticker."""
        return f"{self.name} ({self.ticker})"
