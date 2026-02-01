"""Search and Q&A endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.api.deps import get_db
from src.utils.exceptions import NotFoundError

router = APIRouter()


# Request/Response schemas
class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, max_length=1000)
    company_id: str | None = None
    document_ids: list[str] | None = None
    top_k: int = Field(default=10, ge=1, le=50)
    rerank: bool = True


class SearchResult(BaseModel):
    """Search result schema."""
    text: str
    score: float
    metadata: dict


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: list[SearchResult]
    total: int


class QuestionRequest(BaseModel):
    """Question request schema."""
    question: str = Field(..., min_length=1, max_length=1000)
    company_id: str
    document_ids: list[str] | None = None


class Citation(BaseModel):
    """Citation schema."""
    quote: str
    document_id: str
    document_title: str
    speaker: str | None = None
    location: str | None = None


class AnswerResponse(BaseModel):
    """Answer response schema."""
    question: str
    answer: str
    confidence: float
    citations: list[Citation]
    related_topics: list[str]


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Search through indexed documents using semantic search.
    
    This endpoint uses hybrid retrieval combining:
    - Semantic search (vector similarity)
    - Keyword matching (BM25)
    - Cross-encoder reranking for improved relevance
    
    - **query**: Search query text
    - **company_id**: Optional company filter
    - **document_ids**: Optional list of document IDs to search within
    - **top_k**: Number of results to return (default: 10)
    - **rerank**: Whether to use cross-encoder reranking (default: true)
    """
    # Import here to avoid circular imports
    from src.nlp.retrieval.hybrid import HybridRetriever
    from src.nlp.retrieval.reranker import Reranker
    from src.nlp.indexing.vector_store import VectorStoreManager
    from src.core.config import get_settings
    
    settings = get_settings()
    
    try:
        # Initialize retriever
        vector_store = VectorStoreManager(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        
        # Determine collection name
        collection_name = f"company_{request.company_id}" if request.company_id else "global"
        
        # Retrieve results
        retriever = HybridRetriever(
            vector_store=vector_store,
            collection_name=collection_name,
        )
        
        results = await retriever.retrieve(
            query=request.query,
            top_k=request.top_k * 2 if request.rerank else request.top_k,
            filter_metadata={"document_ids": request.document_ids} if request.document_ids else None,
        )
        
        # Rerank if requested
        if request.rerank and results:
            reranker = Reranker()
            results = await reranker.rerank(
                query=request.query,
                chunks=results,
                top_k=request.top_k,
            )
        
        return SearchResponse(
            query=request.query,
            results=[
                SearchResult(
                    text=r.text,
                    score=r.score,
                    metadata=r.metadata,
                )
                for r in results[:request.top_k]
            ],
            total=len(results),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(
    request: QuestionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question about a company's disclosures.
    
    This endpoint:
    1. Retrieves relevant context using hybrid search
    2. Uses DSPy's QuestionAnswerer to generate an answer
    3. Returns the answer with citations and related topics
    
    - **question**: The question to answer
    - **company_id**: Company ID to search within
    - **document_ids**: Optional list of specific documents to search
    """
    from src.nlp.retrieval.hybrid import HybridRetriever
    from src.nlp.retrieval.reranker import Reranker
    from src.nlp.indexing.vector_store import VectorStoreManager
    from src.nlp.dspy_programs.question_answerer import QuestionAnswerer
    from src.nlp.dspy_programs.base import configure_dspy
    from src.core.config import get_settings
    from src.repositories.document_repository import DocumentRepository
    
    settings = get_settings()
    
    try:
        # Configure DSPy
        configure_dspy(settings.llm_provider, settings.openai_api_key or settings.anthropic_api_key)
        
        # Initialize retriever
        vector_store = VectorStoreManager(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        
        collection_name = f"company_{request.company_id}"
        
        retriever = HybridRetriever(
            vector_store=vector_store,
            collection_name=collection_name,
        )
        
        # Retrieve context
        context_chunks = await retriever.retrieve(
            query=request.question,
            top_k=20,
            filter_metadata={"document_ids": request.document_ids} if request.document_ids else None,
        )
        
        # Rerank
        reranker = Reranker()
        context_chunks = await reranker.rerank(
            query=request.question,
            chunks=context_chunks,
            top_k=10,
        )
        
        # Prepare context
        context = "\n\n".join([
            f"[Source {i+1}] {chunk.text}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Get answer using DSPy
        qa = QuestionAnswerer()
        result = qa.answer(
            question=request.question,
            context=context,
        )
        
        # Get document titles for citations
        doc_repo = DocumentRepository(db)
        doc_map = {}
        for chunk in context_chunks:
            doc_id = chunk.metadata.get("document_id")
            if doc_id and doc_id not in doc_map:
                try:
                    doc = await doc_repo.get(doc_id)
                    doc_map[doc_id] = doc.title
                except NotFoundError:
                    doc_map[doc_id] = "Unknown Document"
        
        # Build citations
        citations = []
        for evidence in result.evidence[:5]:  # Limit to 5 citations
            doc_id = evidence.get("document_id", "")
            citations.append(Citation(
                quote=evidence.get("quote", ""),
                document_id=doc_id,
                document_title=doc_map.get(doc_id, "Unknown"),
                speaker=evidence.get("speaker"),
                location=evidence.get("location"),
            ))
        
        return AnswerResponse(
            question=request.question,
            answer=result.answer,
            confidence=result.confidence,
            citations=citations,
            related_topics=result.related_topics[:5],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}",
        )
