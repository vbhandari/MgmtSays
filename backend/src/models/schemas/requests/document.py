"""Document request schemas."""

from datetime import date
from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    """Schema for document upload metadata."""

    company_id: str = Field(
        ...,
        description="ID of the company this document belongs to",
    )
    title: str | None = Field(
        None,
        max_length=500,
        description="Document title (defaults to filename)",
    )
    document_type: str | None = Field(
        None,
        description="Document type classification",
        examples=["annual_report", "earnings_call", "investor_presentation"],
    )
    document_date: date | None = Field(
        None,
        description="Document date (YYYY-MM-DD)",
    )


class DocumentProcessRequest(BaseModel):
    """Schema for document processing request."""

    force_reprocess: bool = Field(
        False,
        description="Force reprocessing even if already processed",
    )
