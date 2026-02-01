"""Document management endpoints."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, PaginationDep
from src.models.schemas.responses.document import (
    DocumentResponse,
    DocumentListResponse,
    DocumentDetailResponse,
)
from src.services.document_service import DocumentService
from src.repositories.document_repository import DocumentRepository
from src.storage import get_storage
from src.utils.exceptions import NotFoundError, ValidationError, DocumentProcessingError
from src.utils.validators import is_allowed_document_type, MAX_FILE_SIZE

router = APIRouter()


def get_document_service(db: AsyncSession = Depends(get_db)) -> DocumentService:
    """Get document service with database session."""
    return DocumentService(
        repository=DocumentRepository(db),
        storage=get_storage(),
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    pagination: PaginationDep,
    company_id: str | None = None,
    document_type: str | None = None,
    service: DocumentService = Depends(get_document_service),
):
    """
    List all documents with optional filtering.
    
    - **company_id**: Filter by company ID
    - **document_type**: Filter by type (pdf, docx, pptx, txt)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    documents, total = await service.list_documents(
        company_id=company_id,
        document_type=document_type,
        offset=pagination.offset,
        limit=pagination.page_size,
    )
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    company_id: str = Form(...),
    document_type: str | None = Form(None),
    title: str | None = Form(None),
    date: str | None = Form(None),
    service: DocumentService = Depends(get_document_service),
):
    """
    Upload a new document.
    
    - **file**: Document file (PDF, DOCX, PPTX, TXT)
    - **company_id**: ID of the company this document belongs to
    - **document_type**: Optional type classification (annual_report, earnings_call, investor_presentation)
    - **title**: Optional document title (defaults to filename)
    - **date**: Optional document date (YYYY-MM-DD format)
    """
    # Validate file type
    if not file.filename or not is_allowed_document_type(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: PDF, DOCX, PPTX, TXT",
        )

    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    try:
        document = await service.upload_document(
            company_id=company_id,
            filename=file.filename,
            content=content,
            content_type=file.content_type,
            document_type=document_type,
            title=title,
            date=date,
        )
        return DocumentResponse.model_validate(document)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    """
    Get document details by ID.
    
    Returns document metadata and processing status.
    """
    try:
        document = await service.get_document(document_id)
        return DocumentDetailResponse.model_validate(document)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found",
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    """
    Delete a document.
    
    This will also delete the document from storage and remove it from the vector index.
    """
    try:
        await service.delete_document(document_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found",
        )


@router.post("/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    """
    Trigger processing/reprocessing of a document.
    
    This will:
    1. Parse the document content
    2. Chunk the text
    3. Create embeddings
    4. Index in vector store
    """
    try:
        document = await service.process_document(document_id)
        return DocumentResponse.model_validate(document)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found",
        )
    except DocumentProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
):
    """
    Get the extracted text content of a document.
    
    Returns the parsed text content if available.
    """
    try:
        content = await service.get_document_content(document_id)
        return {"document_id": document_id, "content": content}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found",
        )
