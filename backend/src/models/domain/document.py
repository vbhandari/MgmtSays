"""Document domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentType(str, Enum):
    """Types of documents supported."""

    ANNUAL_REPORT = "annual_report"
    QUARTERLY_REPORT = "quarterly_report"
    EARNINGS_CALL = "earnings_call"
    INVESTOR_PRESENTATION = "investor_presentation"
    PRESS_RELEASE = "press_release"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Document:
    """Document domain entity."""

    id: str
    company_id: str
    filename: str
    file_type: str  # pdf, docx, pptx, txt
    file_size: int
    storage_path: str
    
    # Metadata
    title: Optional[str] = None
    document_type: DocumentType = DocumentType.OTHER
    document_date: Optional[datetime] = None
    
    # Processing
    status: ProcessingStatus = ProcessingStatus.PENDING
    content_hash: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    chunk_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    
    # Error info
    error_message: Optional[str] = None

    @property
    def is_processed(self) -> bool:
        """Check if document has been processed."""
        return self.status == ProcessingStatus.COMPLETED

    @property
    def display_title(self) -> str:
        """Get display title (uses filename if title not set)."""
        return self.title or self.filename
