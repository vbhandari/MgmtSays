"""Initiative domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.models.domain.insight import InsightCategory


@dataclass
class Initiative:
    """
    Initiative domain entity.
    
    Represents a grouped/clustered strategic initiative that may span
    multiple documents and time periods.
    """

    id: str
    company_id: str
    
    # Content
    name: str
    description: str
    category: InsightCategory
    
    # Temporal tracking
    first_mentioned_at: datetime
    last_mentioned_at: datetime
    first_document_id: str
    
    # Aggregated metrics
    mention_count: int = 1
    document_count: int = 1
    avg_confidence: float = 0.0
    
    # Status
    is_active: bool = True  # Still being mentioned
    is_completed: bool = False  # Management indicated completion
    
    # Keywords for matching
    keywords: list[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def duration_days(self) -> int:
        """Get number of days initiative has been tracked."""
        delta = self.last_mentioned_at - self.first_mentioned_at
        return max(delta.days, 0)

    @property
    def is_recurring(self) -> bool:
        """Check if initiative has been mentioned multiple times."""
        return self.mention_count > 1
