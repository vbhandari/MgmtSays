"""Document service for business logic."""

from datetime import datetime

from src.models.db.document import DocumentModel
from src.repositories.document_repository import DocumentRepository
from src.storage.base import BaseStorage
from src.utils.exceptions import NotFoundError, ValidationError, DocumentProcessingError
from src.utils.helpers import compute_file_hash, sanitize_filename
from src.utils.validators import get_document_type


class DocumentService:
    """Service for document operations."""

    def __init__(self, repository: DocumentRepository, storage: BaseStorage):
        self.repository = repository
        self.storage = storage

    async def list_documents(
        self,
        company_id: str | None = None,
        document_type: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DocumentModel], int]:
        """List documents with optional filtering."""
        return await self.repository.list_all(
            company_id=company_id,
            document_type=document_type,
            offset=offset,
            limit=limit,
        )

    async def upload_document(
        self,
        company_id: str,
        filename: str,
        content: bytes,
        content_type: str | None = None,
        document_type: str | None = None,
        title: str | None = None,
        date: str | None = None,
    ) -> DocumentModel:
        """Upload and store a new document."""
        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        
        # Compute hash for deduplication
        content_hash = compute_file_hash(content)
        
        # Check for duplicate
        existing = await self.repository.get_by_hash(content_hash)
        if existing and existing.company_id == company_id:
            raise ValidationError(
                "This document has already been uploaded",
                field="file",
            )

        # Determine file type
        file_type = get_document_type(safe_filename)
        if not file_type:
            raise ValidationError(
                "Unsupported file type",
                field="file",
            )

        # Store file
        storage_path = await self.storage.save(
            content=content,
            filename=safe_filename,
            company_id=company_id,
        )

        # Parse date if provided
        document_date = None
        if date:
            try:
                document_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                pass

        # Create database record
        document = await self.repository.create(
            company_id=company_id,
            filename=safe_filename,
            file_type=file_type,
            file_size=len(content),
            storage_path=storage_path,
            content_hash=content_hash,
            title=title or safe_filename,
            document_type=document_type,
            document_date=document_date,
            status="pending",
        )

        return document

    async def get_document(self, document_id: str) -> DocumentModel:
        """Get document by ID."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document", document_id)
        return document

    async def delete_document(self, document_id: str) -> None:
        """Delete a document."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document", document_id)
        
        # Delete from storage
        await self.storage.delete(document.storage_path)
        
        # Delete from database
        await self.repository.delete(document_id)

    async def process_document(self, document_id: str) -> DocumentModel:
        """Process a document (parse, chunk, index)."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document", document_id)

        # Update status to processing
        await self.repository.update_status(document_id, "processing")

        try:
            # Get file content
            content = await self.storage.read(document.storage_path)
            
            # Parse document
            from src.nlp.ingestion import get_parser
            parser = get_parser(document.file_type)
            parsed = await parser.parse(content)
            
            # Update document with extracted info
            await self.repository.update(
                document_id,
                extracted_text=parsed.text,
                page_count=parsed.page_count,
                word_count=len(parsed.text.split()),
            )

            # Chunk the text
            from src.nlp.chunking import get_chunker
            chunker = get_chunker()
            chunks = await chunker.chunk(
                text=parsed.text,
                metadata={
                    "document_id": document_id,
                    "company_id": document.company_id,
                    "filename": document.filename,
                }
            )

            # Index chunks in vector store
            from src.nlp.indexing import get_index_manager
            index_manager = get_index_manager()
            await index_manager.index_chunks(
                company_id=document.company_id,
                document_id=document_id,
                chunks=chunks,
            )

            # Update status
            document = await self.repository.update_status(
                document_id,
                "completed",
                chunk_count=len(chunks),
            )

            return document

        except Exception as e:
            await self.repository.update_status(
                document_id,
                "failed",
                error_message=str(e),
            )
            raise DocumentProcessingError(
                f"Failed to process document: {e}",
                document_id=document_id,
            )

    async def get_document_content(self, document_id: str) -> str:
        """Get extracted text content of a document."""
        document = await self.repository.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document", document_id)
        
        if not document.extracted_text:
            raise DocumentProcessingError(
                "Document has not been processed yet",
                document_id=document_id,
            )
        
        return document.extracted_text
