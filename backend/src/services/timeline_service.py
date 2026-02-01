"""Timeline service for temporal insight views."""

from datetime import datetime, timedelta
from collections import defaultdict

from src.repositories.analysis_repository import (
    AnalysisRepository,
    InsightRepository,
    InitiativeRepository,
)
from src.utils.exceptions import NotFoundError
from src.utils.helpers import extract_quarter_year, format_quarter


class TimelineService:
    """Service for timeline operations."""

    def __init__(self, repository: AnalysisRepository):
        self.repository = repository
        self.insight_repo = InsightRepository(repository.db)
        self.initiative_repo = InitiativeRepository(repository.db)

    async def get_timeline(
        self,
        company_id: str,
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        group_by: str = "quarter",
    ) -> dict:
        """
        Get timeline of insights for a company.
        
        Groups insights by time period and tracks new vs. reiterated.
        """
        # Get all insights
        insights, total = await self.insight_repo.get_by_company(
            company_id=company_id,
            category=category,
            offset=0,
            limit=1000,  # Get all for timeline
        )

        if not insights:
            return {
                "company_id": company_id,
                "items": [],
                "total_insights": 0,
                "period_count": 0,
                "earliest_date": None,
                "latest_date": None,
            }

        # Group by period
        grouped = defaultdict(list)
        
        for insight in insights:
            if insight.first_mentioned_at:
                period_key = self._get_period_key(insight.first_mentioned_at, group_by)
                grouped[period_key].append(insight)

        # Build timeline items
        items = []
        for period_key in sorted(grouped.keys()):
            period_insights = grouped[period_key]
            period_start, period_end = self._get_period_bounds(period_key, group_by)
            
            items.append({
                "period": period_key,
                "period_start": period_start,
                "period_end": period_end,
                "insights": [
                    {
                        "id": i.id,
                        "title": i.title,
                        "category": i.category,
                        "confidence_score": i.confidence_score,
                        "is_new": i.is_new,
                        "is_reiterated": i.is_reiterated,
                    }
                    for i in period_insights
                ],
                "new_count": sum(1 for i in period_insights if i.is_new),
                "reiterated_count": sum(1 for i in period_insights if i.is_reiterated),
                "modified_count": sum(1 for i in period_insights if i.is_modified),
            })

        # Calculate date range
        dates = [i.first_mentioned_at for i in insights if i.first_mentioned_at]
        earliest = min(dates) if dates else None
        latest = max(dates) if dates else None

        return {
            "company_id": company_id,
            "items": items,
            "total_insights": total,
            "period_count": len(items),
            "earliest_date": earliest,
            "latest_date": latest,
        }

    async def get_trends(self, company_id: str) -> dict:
        """Get trend analysis for a company."""
        insights, _ = await self.insight_repo.get_by_company(
            company_id=company_id,
            offset=0,
            limit=1000,
        )

        # Category distribution
        category_dist = defaultdict(int)
        for insight in insights:
            category_dist[insight.category] += 1

        # New vs reiterated over time
        new_by_period = defaultdict(int)
        reiterated_by_period = defaultdict(int)
        
        for insight in insights:
            if insight.first_mentioned_at:
                period = self._get_period_key(insight.first_mentioned_at, "quarter")
                if insight.is_new:
                    new_by_period[period] += 1
                if insight.is_reiterated:
                    reiterated_by_period[period] += 1

        # Most discussed initiatives
        initiatives, _ = await self.initiative_repo.get_by_company(
            company_id=company_id,
            offset=0,
            limit=10,
        )
        most_discussed = [
            i.id for i in sorted(initiatives, key=lambda x: x.mention_count, reverse=True)[:5]
        ]

        return {
            "company_id": company_id,
            "new_initiatives": [
                {"period": p, "count": c, "category_breakdown": {}}
                for p, c in sorted(new_by_period.items())
            ],
            "reiterated_initiatives": [
                {"period": p, "count": c, "category_breakdown": {}}
                for p, c in sorted(reiterated_by_period.items())
            ],
            "category_distribution": dict(category_dist),
            "most_discussed": most_discussed,
        }

    async def get_initiative_history(
        self,
        company_id: str,
        initiative_id: str,
    ) -> dict:
        """Get the history of a specific initiative."""
        initiative = await self.initiative_repo.get_by_id(initiative_id)
        if not initiative or initiative.company_id != company_id:
            raise NotFoundError("Initiative", initiative_id)

        # Get all insights for this initiative
        from sqlalchemy import select
        from src.models.db.analysis import InsightModel
        
        result = await self.repository.db.execute(
            select(InsightModel)
            .where(InsightModel.initiative_id == initiative_id)
            .order_by(InsightModel.first_mentioned_at)
        )
        insights = list(result.scalars().all())

        history = []
        for i, insight in enumerate(insights):
            mention_type = "first" if i == 0 else ("modified" if insight.is_modified else "reiterated")
            history.append({
                "document_id": insight.first_mentioned_document_id or "",
                "document_title": "",  # Would need to join with documents
                "document_date": insight.first_mentioned_at,
                "mention_type": mention_type,
                "quote": insight.description[:200],
                "confidence_score": insight.confidence_score,
            })

        return {
            "initiative_id": initiative_id,
            "name": initiative.name,
            "category": initiative.category,
            "history": history,
            "total_mentions": len(history),
            "first_mentioned": initiative.first_mentioned_at,
            "last_mentioned": initiative.last_mentioned_at,
        }

    def _get_period_key(self, dt: datetime, group_by: str) -> str:
        """Get period key for grouping."""
        if group_by == "quarter":
            q, y = extract_quarter_year(dt)
            return format_quarter(q, y)
        elif group_by == "year":
            return str(dt.year)
        elif group_by == "month":
            return dt.strftime("%Y-%m")
        return format_quarter(*extract_quarter_year(dt))

    def _get_period_bounds(self, period_key: str, group_by: str) -> tuple[datetime, datetime]:
        """Get start and end dates for a period."""
        if group_by == "quarter":
            # Parse "Q2 2024"
            parts = period_key.split()
            q = int(parts[0][1])
            y = int(parts[1])
            start_month = (q - 1) * 3 + 1
            start = datetime(y, start_month, 1)
            if q == 4:
                end = datetime(y + 1, 1, 1) - timedelta(days=1)
            else:
                end = datetime(y, start_month + 3, 1) - timedelta(days=1)
            return start, end
        elif group_by == "year":
            y = int(period_key)
            return datetime(y, 1, 1), datetime(y, 12, 31)
        elif group_by == "month":
            y, m = map(int, period_key.split("-"))
            start = datetime(y, m, 1)
            if m == 12:
                end = datetime(y + 1, 1, 1) - timedelta(days=1)
            else:
                end = datetime(y, m + 1, 1) - timedelta(days=1)
            return start, end
        return datetime.now(), datetime.now()
