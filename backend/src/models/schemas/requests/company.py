"""Company request schemas."""

from pydantic import BaseModel, Field, field_validator


class CompanyCreate(BaseModel):
    """Schema for creating a new company."""

    ticker: str = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Stock ticker symbol (1-5 uppercase letters)",
        examples=["AAPL", "MSFT", "GOOGL"],
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Company name",
        examples=["Apple Inc.", "Microsoft Corporation"],
    )
    description: str | None = Field(
        None,
        max_length=2000,
        description="Optional company description",
    )
    sector: str | None = Field(
        None,
        max_length=100,
        description="Company sector",
        examples=["Technology", "Healthcare", "Finance"],
    )
    industry: str | None = Field(
        None,
        max_length=100,
        description="Company industry",
        examples=["Software", "Biotechnology", "Banking"],
    )

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        """Validate and normalize ticker symbol."""
        v = v.upper().strip()
        if not v.isalpha():
            raise ValueError("Ticker must contain only letters")
        return v


class CompanyUpdate(BaseModel):
    """Schema for updating a company."""

    name: str | None = Field(
        None,
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        None,
        max_length=2000,
    )
    sector: str | None = Field(
        None,
        max_length=100,
    )
    industry: str | None = Field(
        None,
        max_length=100,
    )
