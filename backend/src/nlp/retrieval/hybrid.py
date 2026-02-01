"""Hybrid retriever combining semantic and keyword search."""

from dataclasses import dataclass
from typing import Any
import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.schema import NodeWithScore

from src.config.settings import get_settings
from src.nlp.indexing.manager import IndexManager
from src.nlp.retrieval.reranker import Reranker


logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from retrieval."""
    
    chunk_id: str
    text: str
    score: float
    metadata: dict
    document_id: str | None = None


class HybridRetriever:
    """
    Hybrid retriever combining semantic search with optional keyword boosting.
    
    Features:
    - Vector similarity search via LlamaIndex
    - Metadata filtering
    - Optional reranking
    - Citation tracking
    """

    def __init__(
        self,
        index_manager: IndexManager,
        use_reranker: bool = True,
    ):
        self.index_manager = index_manager
        self.settings = get_settings()
        self.use_reranker = use_reranker
        self.reranker = Reranker() if use_reranker else None

    async def retrieve(
        self,
        query: str,
        company_id: str,
        top_k: int = 10,
        document_ids: list[str] | None = None,
        metadata_filters: dict[str, Any] | None = None,
        min_score: float = 0.0,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Search query
            company_id: Company to search within
            top_k: Maximum number of results
            document_ids: Optional list of document IDs to filter
            metadata_filters: Optional metadata filters
            min_score: Minimum similarity score threshold
            
        Returns:
            List of RetrievalResult ordered by relevance
        """
        # Get index for company
        index = await self.index_manager.get_or_create_index(company_id)

        # Build retriever with filters
        retriever = self._build_retriever(
            index=index,
            top_k=top_k * 2 if self.use_reranker else top_k,  # Get more for reranking
            document_ids=document_ids,
            metadata_filters=metadata_filters,
        )

        # Retrieve nodes
        nodes = retriever.retrieve(query)

        # Convert to results
        results = []
        for node_with_score in nodes:
            if node_with_score.score and node_with_score.score < min_score:
                continue

            result = RetrievalResult(
                chunk_id=node_with_score.node.id_,
                text=node_with_score.node.get_content(),
                score=node_with_score.score or 0.0,
                metadata=node_with_score.node.metadata,
                document_id=node_with_score.node.metadata.get("document_id"),
            )
            results.append(result)

        # Rerank if enabled
        if self.use_reranker and self.reranker and len(results) > 0:
            results = await self.reranker.rerank(query, results, top_k=top_k)

        return results[:top_k]

    async def retrieve_for_document(
        self,
        query: str,
        company_id: str,
        document_id: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """
        Retrieve chunks from a specific document.
        
        Useful for finding citations within a known document.
        """
        return await self.retrieve(
            query=query,
            company_id=company_id,
            top_k=top_k,
            document_ids=[document_id],
        )

    async def retrieve_multi_query(
        self,
        queries: list[str],
        company_id: str,
        top_k: int = 10,
        document_ids: list[str] | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve using multiple query variations.
        
        Useful for improving recall by searching with
        different phrasings of the same question.
        """
        all_results: dict[str, RetrievalResult] = {}

        for query in queries:
            results = await self.retrieve(
                query=query,
                company_id=company_id,
                top_k=top_k,
                document_ids=document_ids,
            )

            for result in results:
                if result.chunk_id not in all_results:
                    all_results[result.chunk_id] = result
                else:
                    # Keep the higher score
                    if result.score > all_results[result.chunk_id].score:
                        all_results[result.chunk_id] = result

        # Sort by score and return top_k
        sorted_results = sorted(
            all_results.values(),
            key=lambda r: r.score,
            reverse=True,
        )

        return sorted_results[:top_k]

    def _build_retriever(
        self,
        index: VectorStoreIndex,
        top_k: int,
        document_ids: list[str] | None = None,
        metadata_filters: dict[str, Any] | None = None,
    ) -> VectorIndexRetriever:
        """Build a retriever with optional filters."""
        from llama_index.core.vector_stores import (
            MetadataFilters,
            MetadataFilter,
            FilterOperator,
            FilterCondition,
        )

        filters = []

        # Add document ID filter
        if document_ids:
            filters.append(
                MetadataFilter(
                    key="document_id",
                    value=document_ids,
                    operator=FilterOperator.IN,
                )
            )

        # Add custom metadata filters
        if metadata_filters:
            for key, value in metadata_filters.items():
                filters.append(
                    MetadataFilter(
                        key=key,
                        value=value,
                        operator=FilterOperator.EQ,
                    )
                )

        # Create metadata filters if any
        metadata_filters_obj = None
        if filters:
            metadata_filters_obj = MetadataFilters(
                filters=filters,
                condition=FilterCondition.AND,
            )

        return VectorIndexRetriever(
            index=index,
            similarity_top_k=top_k,
            filters=metadata_filters_obj,
        )

    async def get_context_window(
        self,
        chunk_id: str,
        company_id: str,
        window_size: int = 2,
    ) -> list[RetrievalResult]:
        """
        Get surrounding chunks for context.
        
        Useful for expanding citations to include nearby content.
        
        Args:
            chunk_id: Center chunk ID
            company_id: Company identifier
            window_size: Number of chunks before/after to include
            
        Returns:
            List of chunks including the center and surrounding chunks
        """
        # Parse chunk ID to find document and chunk index
        # Format: {document_id}_chunk_{index}
        parts = chunk_id.rsplit("_chunk_", 1)
        if len(parts) != 2:
            return []

        document_id = parts[0]
        try:
            center_index = int(parts[1])
        except ValueError:
            return []

        # Get chunks from the same document
        results = []
        for i in range(center_index - window_size, center_index + window_size + 1):
            target_id = f"{document_id}_chunk_{i}"
            
            # Retrieve the specific chunk
            chunk_results = await self.index_manager.get_document_chunks(
                document_id=document_id,
                company_id=company_id,
            )

            for chunk in chunk_results:
                if chunk.get("id") == target_id:
                    results.append(
                        RetrievalResult(
                            chunk_id=chunk["id"],
                            text=chunk.get("text", ""),
                            score=1.0 if chunk["id"] == chunk_id else 0.9,
                            metadata=chunk.get("metadata", {}),
                            document_id=document_id,
                        )
                    )
                    break

        return sorted(results, key=lambda r: r.chunk_id)
