"""Document response schemas."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Document response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    company_id: str
    filename: str
    file_type: str
    file_size: int
    title: str | None = None
    document_type: str | None = None
    document_date: datetime | None = None
    status: str
    page_count: int | None = None
    word_count: int | None = None
    created_at: datetime
    updated_at: datetime


class DocumentDetailResponse(DocumentResponse):
    """Document detail response with additional info."""

    storage_path: str
    chunk_count: int = 0
    content_hash: str | None = None
    processed_at: datetime | None = None
    error_message: str | None = None


class DocumentListResponse(BaseModel):
    """Paginated document list response."""

    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int

    @property
    def has_more(self) -> bool:
        """Check if there are more pages."""
        return self.page * self.page_size < self.total


class DocumentContentResponse(BaseModel):
    """Document content response."""

    document_id: str
    content: str
    word_count: int
    chunk_count: int
