"""Analysis service for running NLP extraction."""

from datetime import datetime

from src.models.schemas.requests.analysis import AnalysisRequest
from src.models.db.analysis import AnalysisModel, InsightModel
from src.repositories.analysis_repository import (
    AnalysisRepository,
    InsightRepository,
    InitiativeRepository,
)
from src.utils.exceptions import NotFoundError, NLPError
from src.config.logging import get_logger

logger = get_logger(__name__)


class AnalysisService:
    """Service for analysis operations."""

    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
        self.insight_repo = InsightRepository(repository.db)
        self.initiative_repo = InitiativeRepository(repository.db)

    async def create_analysis(self, request: AnalysisRequest) -> AnalysisModel:
        """Create a new analysis job."""
        # Check for recent analysis if not forcing rerun
        if not request.force_rerun:
            recent = await self.repository.get_latest_completed(request.company_id)
            if recent and recent.completed_at:
                # Check if completed within last hour
                age = datetime.utcnow() - recent.completed_at.replace(tzinfo=None)
                if age.total_seconds() < 3600:
                    logger.info(f"Recent analysis found for company {request.company_id}")

        analysis = await self.repository.create(
            company_id=request.company_id,
            document_ids=request.document_ids,
            categories=request.categories,
            status="pending",
        )

        return analysis

    async def get_analysis(self, analysis_id: str) -> AnalysisModel:
        """Get analysis by ID."""
        analysis = await self.repository.get_by_id(analysis_id)
        if not analysis:
            raise NotFoundError("Analysis", analysis_id)
        return analysis

    async def run_analysis(self, analysis_id: str) -> None:
        """Run the full analysis pipeline."""
        try:
            # Update status
            await self.repository.update_progress(analysis_id, 0.0, "processing")
            
            analysis = await self.repository.get_by_id(analysis_id)
            if not analysis:
                return

            logger.info(f"Starting analysis {analysis_id} for company {analysis.company_id}")

            # Step 1: Retrieve relevant chunks (20%)
            await self.repository.update_progress(analysis_id, 0.1, "processing")
            
            from src.nlp.retrieval import get_retriever
            retriever = get_retriever()
            chunks = await retriever.retrieve(
                company_id=analysis.company_id,
                document_ids=analysis.document_ids,
            )
            
            await self.repository.update_progress(analysis_id, 0.2)

            # Step 2: Extract initiatives (60%)
            from src.nlp.dspy_programs import get_initiative_extractor
            extractor = get_initiative_extractor()
            
            raw_insights = []
            total_chunks = len(chunks)
            
            for i, chunk in enumerate(chunks):
                try:
                    extracted = await extractor.extract(chunk)
                    raw_insights.extend(extracted)
                except Exception as e:
                    logger.warning(f"Failed to extract from chunk {i}: {e}")
                
                # Update progress
                progress = 0.2 + (0.4 * (i + 1) / total_chunks)
                await self.repository.update_progress(analysis_id, progress)

            await self.repository.update_progress(analysis_id, 0.6)

            # Step 3: Deduplicate and cluster (80%)
            from src.nlp.dspy_programs import get_deduplicator
            deduplicator = get_deduplicator()
            deduplicated = await deduplicator.deduplicate(raw_insights)
            
            await self.repository.update_progress(analysis_id, 0.8)

            # Step 4: Store results (100%)
            for insight_data in deduplicated:
                # Check for existing initiative
                initiative = await self.initiative_repo.find_similar(
                    company_id=analysis.company_id,
                    name=insight_data.get("title", ""),
                    category=insight_data.get("category", "other"),
                )

                if initiative:
                    # Update existing initiative
                    initiative.mention_count += 1
                    initiative.last_mentioned_at = datetime.utcnow()
                    is_new = False
                else:
                    # Create new initiative
                    initiative = await self.initiative_repo.create(
                        company_id=analysis.company_id,
                        name=insight_data.get("title", "Unknown"),
                        description=insight_data.get("description", ""),
                        category=insight_data.get("category", "other"),
                        first_mentioned_at=datetime.utcnow(),
                        last_mentioned_at=datetime.utcnow(),
                        first_document_id=insight_data.get("document_id", ""),
                    )
                    is_new = True

                # Create insight
                confidence = insight_data.get("confidence_score", 0.5)
                insight = await self.insight_repo.create(
                    company_id=analysis.company_id,
                    analysis_id=analysis_id,
                    initiative_id=initiative.id,
                    title=insight_data.get("title", "Unknown"),
                    description=insight_data.get("description", ""),
                    category=insight_data.get("category", "other"),
                    confidence_score=confidence,
                    confidence_level="high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low",
                    is_new=is_new,
                    is_reiterated=not is_new,
                )

                # Create evidence
                for evidence_data in insight_data.get("evidence", []):
                    from src.repositories.analysis_repository import EvidenceRepository
                    evidence_repo = EvidenceRepository(self.repository.db)
                    await evidence_repo.create(
                        insight_id=insight.id,
                        document_id=evidence_data.get("document_id", ""),
                        quote=evidence_data.get("quote", ""),
                        context=evidence_data.get("context"),
                        page_number=evidence_data.get("page_number"),
                        section=evidence_data.get("section"),
                        relevance_score=evidence_data.get("relevance_score", 0.0),
                    )

            # Mark complete
            analysis.insight_count = len(deduplicated)
            await self.repository.update_progress(analysis_id, 1.0, "completed")
            
            logger.info(f"Analysis {analysis_id} completed with {len(deduplicated)} insights")

        except Exception as e:
            logger.exception(f"Analysis {analysis_id} failed: {e}")
            analysis = await self.repository.get_by_id(analysis_id)
            if analysis:
                analysis.status = "failed"
                analysis.error_message = str(e)
            raise NLPError(f"Analysis failed: {e}")

    async def get_insights(
        self,
        company_id: str,
        category: str | None = None,
        confidence_min: float | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[InsightModel], int]:
        """Get insights for a company."""
        return await self.insight_repo.get_by_company(
            company_id=company_id,
            category=category,
            confidence_min=confidence_min,
            offset=offset,
            limit=limit,
        )

    async def get_insight_detail(self, insight_id: str) -> InsightModel:
        """Get insight with evidence."""
        insight = await self.insight_repo.get_with_evidence(insight_id)
        if not insight:
            raise NotFoundError("Insight", insight_id)
        return insight

    async def clear_insights(self, company_id: str) -> None:
        """Clear all insights for a company."""
        await self.insight_repo.delete_by_company(company_id)
