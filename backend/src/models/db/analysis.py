"""Analysis, Insight, Evidence, and Initiative database models."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin, generate_uuid

if TYPE_CHECKING:
    from src.models.db.company import CompanyModel
    from src.models.db.document import DocumentModel


class AnalysisModel(Base, UUIDMixin, TimestampMixin):
    """Analysis job database model."""

    __tablename__ = "analyses"

    # Foreign keys
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    document_ids: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    categories: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Results
    insight_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    company: Mapped["CompanyModel"] = relationship("CompanyModel", back_populates="analyses")
    insights: Mapped[list["InsightModel"]] = relationship(
        "InsightModel",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_analyses_company_status", "company_id", "status"),
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = generate_uuid()
        super().__init__(**kwargs)


class InitiativeModel(Base, UUIDMixin, TimestampMixin):
    """Initiative (grouped insights) database model."""

    __tablename__ = "initiatives"

    # Foreign keys
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Content
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Temporal tracking
    first_mentioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_mentioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_document_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Aggregated metrics
    mention_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    document_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    avg_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Keywords for matching
    keywords: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Relationships
    company: Mapped["CompanyModel"] = relationship("CompanyModel", back_populates="initiatives")
    insights: Mapped[list["InsightModel"]] = relationship(
        "InsightModel",
        back_populates="initiative",
    )

    __table_args__ = (
        Index("ix_initiatives_company_category", "company_id", "category"),
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = generate_uuid()
        super().__init__(**kwargs)


class InsightModel(Base, UUIDMixin, TimestampMixin):
    """Insight database model."""

    __tablename__ = "insights"

    # Foreign keys
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    initiative_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("initiatives.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    # Confidence
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False)

    # Temporal
    first_mentioned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    first_mentioned_document_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    mention_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Status tracking
    is_new: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_reiterated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_modified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    analysis: Mapped["AnalysisModel"] = relationship("AnalysisModel", back_populates="insights")
    initiative: Mapped[Optional["InitiativeModel"]] = relationship("InitiativeModel", back_populates="insights")
    evidence: Mapped[list["EvidenceModel"]] = relationship(
        "EvidenceModel",
        back_populates="insight",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_insights_company_category", "company_id", "category"),
        Index("ix_insights_confidence", "confidence_score"),
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = generate_uuid()
        super().__init__(**kwargs)


class EvidenceModel(Base, UUIDMixin, TimestampMixin):
    """Evidence/citation database model."""

    __tablename__ = "evidence"

    # Foreign keys
    insight_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("insights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Citation details
    quote: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    section: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    paragraph_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Chunk reference
    chunk_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    chunk_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relevance
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    insight: Mapped["InsightModel"] = relationship("InsightModel", back_populates="evidence")
    document: Mapped["DocumentModel"] = relationship("DocumentModel", back_populates="evidence")

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = generate_uuid()
        super().__init__(**kwargs)
