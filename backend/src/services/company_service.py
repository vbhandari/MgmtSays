"""Company service for business logic."""

from src.models.schemas.requests.company import CompanyCreate, CompanyUpdate
from src.models.db.company import CompanyModel
from src.repositories.company_repository import CompanyRepository
from src.utils.exceptions import NotFoundError, ValidationError


class CompanyService:
    """Service for company operations."""

    def __init__(self, repository: CompanyRepository):
        self.repository = repository

    async def list_companies(
        self,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[CompanyModel], int]:
        """List companies with optional search."""
        return await self.repository.search(
            query=search,
            offset=offset,
            limit=limit,
        )

    async def create_company(self, data: CompanyCreate) -> CompanyModel:
        """Create a new company."""
        # Check for duplicate ticker
        if await self.repository.ticker_exists(data.ticker):
            raise ValidationError(
                f"Company with ticker '{data.ticker}' already exists",
                field="ticker",
            )

        return await self.repository.create(
            ticker=data.ticker.upper(),
            name=data.name,
            description=data.description,
            sector=data.sector,
            industry=data.industry,
        )

    async def get_company(self, company_id: str) -> CompanyModel:
        """Get company by ID."""
        company = await self.repository.get_by_id(company_id)
        if not company:
            raise NotFoundError("Company", company_id)
        return company

    async def get_company_by_ticker(self, ticker: str) -> CompanyModel:
        """Get company by ticker symbol."""
        company = await self.repository.get_by_ticker(ticker)
        if not company:
            raise NotFoundError("Company", ticker)
        return company

    async def get_company_with_stats(self, company_id: str) -> CompanyModel:
        """Get company with document and analysis counts."""
        company = await self.repository.get_with_stats(company_id)
        if not company:
            raise NotFoundError("Company", company_id)
        return company

    async def update_company(
        self,
        company_id: str,
        data: CompanyUpdate,
    ) -> CompanyModel:
        """Update company information."""
        company = await self.repository.get_by_id(company_id)
        if not company:
            raise NotFoundError("Company", company_id)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return company

        updated = await self.repository.update(company_id, **update_data)
        return updated

    async def delete_company(self, company_id: str) -> None:
        """Delete a company and all associated data."""
        if not await self.repository.exists(company_id):
            raise NotFoundError("Company", company_id)
        
        await self.repository.delete(company_id)
