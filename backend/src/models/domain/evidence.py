"""Evidence domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Evidence:
    """
    Evidence domain entity.
    
    Represents supporting evidence/citation for an insight.
    """

    id: str
    insight_id: str
    document_id: str
    
    # Citation details
    quote: str  # Exact quoted text
    context: Optional[str] = None  # Surrounding context
    
    # Location
    page_number: Optional[int] = None
    section: Optional[str] = None
    paragraph_index: Optional[int] = None
    
    # Chunk reference (for vector store)
    chunk_id: Optional[str] = None
    chunk_index: Optional[int] = None
    
    # Relevance
    relevance_score: float = 0.0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def location_string(self) -> str:
        """Get human-readable location string."""
        parts = []
        if self.section:
            parts.append(self.section)
        if self.page_number:
            parts.append(f"Page {self.page_number}")
        return ", ".join(parts) if parts else "Unknown location"
