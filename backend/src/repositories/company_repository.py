"""Company repository."""

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repositories.base import BaseRepository
from src.models.db.company import CompanyModel


class CompanyRepository(BaseRepository[CompanyModel]):
    """Repository for company operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, CompanyModel)

    async def get_by_ticker(self, ticker: str) -> CompanyModel | None:
        """Get company by ticker symbol."""
        result = await self.db.execute(
            select(CompanyModel).where(CompanyModel.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[CompanyModel], int]:
        """Search companies by name or ticker."""
        base_query = select(CompanyModel)
        count_query = select(func.count()).select_from(CompanyModel)

        if query:
            search_filter = or_(
                CompanyModel.ticker.ilike(f"%{query}%"),
                CompanyModel.name.ilike(f"%{query}%"),
            )
            base_query = base_query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        result = await self.db.execute(
            base_query
            .order_by(CompanyModel.ticker)
            .offset(offset)
            .limit(limit)
        )
        companies = list(result.scalars().all())

        return companies, total

    async def get_with_stats(self, id: str) -> CompanyModel | None:
        """Get company with document and analysis counts."""
        result = await self.db.execute(
            select(CompanyModel)
            .options(
                selectinload(CompanyModel.documents),
                selectinload(CompanyModel.analyses),
            )
            .where(CompanyModel.id == id)
        )
        company = result.scalar_one_or_none()
        
        if company:
            # Add computed stats
            company.document_count = len(company.documents)
            company.analysis_count = len(company.analyses)
            if company.analyses:
                completed = [a for a in company.analyses if a.status == "completed"]
                if completed:
                    company.latest_analysis_at = max(a.completed_at for a in completed if a.completed_at)
        
        return company

    async def ticker_exists(self, ticker: str, exclude_id: str | None = None) -> bool:
        """Check if ticker already exists."""
        query = select(func.count()).select_from(CompanyModel).where(
            CompanyModel.ticker == ticker.upper()
        )
        if exclude_id:
            query = query.where(CompanyModel.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one() > 0
