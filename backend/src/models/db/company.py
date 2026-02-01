"""Company database model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base, TimestampMixin, UUIDMixin, generate_uuid

if TYPE_CHECKING:
    from src.models.db.document import DocumentModel
    from src.models.db.analysis import AnalysisModel, InitiativeModel


class CompanyModel(Base, UUIDMixin, TimestampMixin):
    """Company database model."""

    __tablename__ = "companies"

    # Primary fields
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    analyses: Mapped[list["AnalysisModel"]] = relationship(
        "AnalysisModel",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    initiatives: Mapped[list["InitiativeModel"]] = relationship(
        "InitiativeModel",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("ix_companies_name_search", "name"),
    )

    def __init__(self, **kwargs):
        if "id" not in kwargs:
            kwargs["id"] = generate_uuid()
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, ticker={self.ticker}, name={self.name})>"
