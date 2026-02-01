"""Document repository."""

from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base import BaseRepository
from src.models.db.document import DocumentModel


class DocumentRepository(BaseRepository[DocumentModel]):
    """Repository for document operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, DocumentModel)

    async def get_by_company(
        self,
        company_id: str,
        document_type: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DocumentModel], int]:
        """Get documents for a company with optional filters."""
        filters = [DocumentModel.company_id == company_id]
        
        if document_type:
            filters.append(DocumentModel.document_type == document_type)
        if status:
            filters.append(DocumentModel.status == status)

        # Count query
        count_result = await self.db.execute(
            select(func.count())
            .select_from(DocumentModel)
            .where(and_(*filters))
        )
        total = count_result.scalar_one()

        # Data query
        result = await self.db.execute(
            select(DocumentModel)
            .where(and_(*filters))
            .order_by(DocumentModel.document_date.desc().nullslast(), DocumentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        documents = list(result.scalars().all())

        return documents, total

    async def list_all(
        self,
        company_id: str | None = None,
        document_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DocumentModel], int]:
        """List all documents with optional filters."""
        filters = []
        
        if company_id:
            filters.append(DocumentModel.company_id == company_id)
        if document_type:
            filters.append(DocumentModel.document_type == document_type)

        # Count query
        count_query = select(func.count()).select_from(DocumentModel)
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()

        # Data query
        data_query = select(DocumentModel)
        if filters:
            data_query = data_query.where(and_(*filters))
        data_query = (
            data_query
            .order_by(DocumentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(data_query)
        documents = list(result.scalars().all())

        return documents, total

    async def get_by_hash(self, content_hash: str) -> DocumentModel | None:
        """Get document by content hash (for deduplication)."""
        result = await self.db.execute(
            select(DocumentModel).where(DocumentModel.content_hash == content_hash)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        id: str,
        status: str,
        error_message: str | None = None,
        **kwargs,
    ) -> DocumentModel | None:
        """Update document processing status."""
        update_data = {"status": status, "error_message": error_message, **kwargs}
        
        if status == "processing":
            update_data["processed_at"] = None
        elif status == "completed":
            update_data["processed_at"] = datetime.utcnow()
        
        return await self.update(id, **update_data)

    async def get_unprocessed(self, limit: int = 10) -> list[DocumentModel]:
        """Get documents that need processing."""
        result = await self.db.execute(
            select(DocumentModel)
            .where(DocumentModel.status == "pending")
            .order_by(DocumentModel.created_at)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_company(self, company_id: str) -> int:
        """Count documents for a company."""
        result = await self.db.execute(
            select(func.count())
            .select_from(DocumentModel)
            .where(DocumentModel.company_id == company_id)
        )
        return result.scalar_one()
