"""Insight domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class InsightCategory(str, Enum):
    """Categories of strategic insights."""

    STRATEGY = "strategy"
    EXPANSION = "expansion"
    PRODUCT = "product"
    MNA = "mna"  # Mergers & Acquisitions
    GUIDANCE = "guidance"
    CAPITAL_ALLOCATION = "capital_allocation"
    OPERATIONAL = "operational"
    OTHER = "other"


class ConfidenceLevel(str, Enum):
    """Confidence levels for insights."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Insight:
    """
    Insight domain entity.
    
    Represents a single extracted insight from management disclosures.
    """

    id: str
    company_id: str
    initiative_id: Optional[str]  # Links to parent initiative if grouped
    
    # Content
    title: str
    description: str
    category: InsightCategory
    
    # Confidence
    confidence_score: float  # 0-1
    confidence_level: ConfidenceLevel
    
    # Temporal
    first_mentioned_at: Optional[datetime] = None
    first_mentioned_document_id: Optional[str] = None
    mention_count: int = 1
    
    # Status tracking
    is_new: bool = True  # First time seen
    is_reiterated: bool = False  # Mentioned again
    is_modified: bool = False  # Changed from previous mention
    
    # Metadata
    analysis_id: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_high_confidence(self) -> bool:
        """Check if insight has high confidence."""
        return self.confidence_score >= 0.8

    def get_confidence_level(self) -> ConfidenceLevel:
        """Determine confidence level from score."""
        if self.confidence_score >= 0.8:
            return ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
