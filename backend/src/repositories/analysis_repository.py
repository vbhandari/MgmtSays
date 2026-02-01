"""Analysis repository."""

from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repositories.base import BaseRepository
from src.models.db.analysis import AnalysisModel, InsightModel, EvidenceModel, InitiativeModel


class AnalysisRepository(BaseRepository[AnalysisModel]):
    """Repository for analysis operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, AnalysisModel)

    async def get_by_company(
        self,
        company_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AnalysisModel], int]:
        """Get analyses for a company."""
        filters = [AnalysisModel.company_id == company_id]
        if status:
            filters.append(AnalysisModel.status == status)

        count_result = await self.db.execute(
            select(func.count())
            .select_from(AnalysisModel)
            .where(and_(*filters))
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(AnalysisModel)
            .where(and_(*filters))
            .order_by(AnalysisModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        analyses = list(result.scalars().all())

        return analyses, total

    async def get_latest_completed(self, company_id: str) -> AnalysisModel | None:
        """Get the most recent completed analysis for a company."""
        result = await self.db.execute(
            select(AnalysisModel)
            .where(
                and_(
                    AnalysisModel.company_id == company_id,
                    AnalysisModel.status == "completed",
                )
            )
            .order_by(AnalysisModel.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        id: str,
        progress: float,
        status: str | None = None,
    ) -> None:
        """Update analysis progress."""
        analysis = await self.get_by_id(id)
        if analysis:
            analysis.progress = progress
            if status:
                analysis.status = status
                if status == "processing" and not analysis.started_at:
                    analysis.started_at = datetime.utcnow()
                elif status == "completed":
                    analysis.completed_at = datetime.utcnow()
            await self.db.flush()


class InsightRepository(BaseRepository[InsightModel]):
    """Repository for insight operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, InsightModel)

    async def get_by_company(
        self,
        company_id: str,
        category: str | None = None,
        confidence_min: float | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[InsightModel], int]:
        """Get insights for a company with filters."""
        filters = [InsightModel.company_id == company_id]
        
        if category:
            filters.append(InsightModel.category == category)
        if confidence_min is not None:
            filters.append(InsightModel.confidence_score >= confidence_min)

        count_result = await self.db.execute(
            select(func.count())
            .select_from(InsightModel)
            .where(and_(*filters))
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(InsightModel)
            .options(selectinload(InsightModel.evidence))
            .where(and_(*filters))
            .order_by(InsightModel.confidence_score.desc())
            .offset(offset)
            .limit(limit)
        )
        insights = list(result.scalars().all())

        return insights, total

    async def get_with_evidence(self, id: str) -> InsightModel | None:
        """Get insight with all evidence."""
        result = await self.db.execute(
            select(InsightModel)
            .options(selectinload(InsightModel.evidence))
            .where(InsightModel.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_analysis(self, analysis_id: str) -> list[InsightModel]:
        """Get all insights for an analysis."""
        result = await self.db.execute(
            select(InsightModel)
            .where(InsightModel.analysis_id == analysis_id)
            .order_by(InsightModel.confidence_score.desc())
        )
        return list(result.scalars().all())

    async def delete_by_company(self, company_id: str) -> int:
        """Delete all insights for a company."""
        from sqlalchemy import delete
        result = await self.db.execute(
            delete(InsightModel).where(InsightModel.company_id == company_id)
        )
        return result.rowcount


class EvidenceRepository(BaseRepository[EvidenceModel]):
    """Repository for evidence operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, EvidenceModel)

    async def get_by_insight(self, insight_id: str) -> list[EvidenceModel]:
        """Get all evidence for an insight."""
        result = await self.db.execute(
            select(EvidenceModel)
            .where(EvidenceModel.insight_id == insight_id)
            .order_by(EvidenceModel.relevance_score.desc())
        )
        return list(result.scalars().all())

    async def get_by_document(self, document_id: str) -> list[EvidenceModel]:
        """Get all evidence from a document."""
        result = await self.db.execute(
            select(EvidenceModel)
            .where(EvidenceModel.document_id == document_id)
        )
        return list(result.scalars().all())


class InitiativeRepository(BaseRepository[InitiativeModel]):
    """Repository for initiative operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, InitiativeModel)

    async def get_by_company(
        self,
        company_id: str,
        category: str | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[InitiativeModel], int]:
        """Get initiatives for a company."""
        filters = [InitiativeModel.company_id == company_id]
        
        if category:
            filters.append(InitiativeModel.category == category)
        if is_active is not None:
            filters.append(InitiativeModel.is_active == is_active)

        count_result = await self.db.execute(
            select(func.count())
            .select_from(InitiativeModel)
            .where(and_(*filters))
        )
        total = count_result.scalar_one()

        result = await self.db.execute(
            select(InitiativeModel)
            .where(and_(*filters))
            .order_by(InitiativeModel.last_mentioned_at.desc())
            .offset(offset)
            .limit(limit)
        )
        initiatives = list(result.scalars().all())

        return initiatives, total

    async def find_similar(
        self,
        company_id: str,
        name: str,
        category: str,
    ) -> InitiativeModel | None:
        """Find a similar existing initiative (for deduplication)."""
        # Simple name-based matching for now
        # Could be enhanced with embedding similarity
        result = await self.db.execute(
            select(InitiativeModel)
            .where(
                and_(
                    InitiativeModel.company_id == company_id,
                    InitiativeModel.category == category,
                    InitiativeModel.name.ilike(f"%{name[:50]}%"),
                )
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
