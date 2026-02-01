"""Document database model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin, generate_uuid

if TYPE_CHECKING:
    from src.models.db.company import CompanyModel
    from src.models.db.analysis import EvidenceModel


class DocumentModel(Base, UUIDMixin, TimestampMixin):
    """Document database model."""

    __tablename__ = "documents"

    # Foreign keys
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # File info
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pdf, docx, pptx, txt
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Metadata
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    document_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # annual_report, earnings_call, etc.
    document_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Processing status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, processing, completed, failed
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Extracted text (stored separately for large documents)
    extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    company: Mapped["CompanyModel"] = relationship("CompanyModel", back_populates="documents")
    evidence: Mapped[list["EvidenceModel"]] = relationship(
        "EvidenceModel",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("ix_documents_company_date", "company_id", "document_date"),
        Index("ix_documents_status", "status"),
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = generate_uuid()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"
