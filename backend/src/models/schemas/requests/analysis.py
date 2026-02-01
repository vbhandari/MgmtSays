"""Analysis request schemas."""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Schema for analysis request."""

    company_id: str = Field(
        ...,
        description="ID of the company to analyze",
    )
    document_ids: list[str] | None = Field(
        None,
        description="Optional list of specific document IDs to analyze. If not provided, all documents will be analyzed.",
    )
    categories: list[str] | None = Field(
        None,
        description="Optional list of categories to focus on",
        examples=[["strategy", "expansion", "product"]],
    )
    force_rerun: bool = Field(
        False,
        description="Force re-analysis even if recent results exist",
    )


class AnalysisCancelRequest(BaseModel):
    """Schema for cancelling an analysis."""

    reason: str | None = Field(
        None,
        max_length=500,
        description="Optional reason for cancellation",
    )
