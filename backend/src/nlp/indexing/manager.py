"""Index manager for LlamaIndex integration."""

from typing import Any
import logging

from llama_index.core import (
    Document as LlamaDocument,
    VectorStoreIndex,
    StorageContext,
    ServiceContext,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode

from src.config.settings import get_settings
from src.nlp.chunking.semantic import Chunk
from src.nlp.indexing.vector_store import VectorStoreManager


logger = logging.getLogger(__name__)


class IndexManager:
    """
    Manages LlamaIndex indices for document storage and retrieval.
    
    Handles:
    - Index creation and persistence
    - Document/chunk indexing
    - Index updates and deletions
    - Multi-company index isolation
    """

    def __init__(self):
        self.settings = get_settings()
        self.vector_store_manager = VectorStoreManager()
        self._indices: dict[str, VectorStoreIndex] = {}

    async def initialize(self):
        """Initialize the index manager."""
        await self.vector_store_manager.initialize()
        logger.info("IndexManager initialized")

    async def get_or_create_index(
        self,
        company_id: str,
    ) -> VectorStoreIndex:
        """
        Get or create an index for a company.
        
        Args:
            company_id: Company identifier
            
        Returns:
            VectorStoreIndex for the company
        """
        if company_id in self._indices:
            return self._indices[company_id]

        # Get vector store for company
        vector_store = await self.vector_store_manager.get_or_create_collection(
            collection_name=f"company_{company_id}",
        )

        # Create storage context
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
        )

        # Create or load index
        try:
            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                storage_context=storage_context,
            )
            logger.info(f"Loaded existing index for company {company_id}")
        except Exception:
            # Create new empty index
            index = VectorStoreIndex(
                nodes=[],
                storage_context=storage_context,
            )
            logger.info(f"Created new index for company {company_id}")

        self._indices[company_id] = index
        return index

    async def index_chunks(
        self,
        chunks: list[Chunk],
        company_id: str,
        document_id: str,
    ) -> int:
        """
        Index chunks into the vector store.
        
        Args:
            chunks: List of chunks to index
            company_id: Company identifier
            document_id: Source document ID
            
        Returns:
            Number of chunks indexed
        """
        if not chunks:
            return 0

        # Get index for company
        index = await self.get_or_create_index(company_id)

        # Convert chunks to LlamaIndex nodes
        nodes = []
        for chunk in chunks:
            node = TextNode(
                text=chunk.text,
                id_=chunk.id,
                metadata={
                    **chunk.metadata,
                    "company_id": company_id,
                    "document_id": document_id,
                },
            )
            nodes.append(node)

        # Insert nodes into index
        index.insert_nodes(nodes)

        logger.info(
            f"Indexed {len(nodes)} chunks for document {document_id} "
            f"(company: {company_id})"
        )

        return len(nodes)

    async def delete_document(
        self,
        document_id: str,
        company_id: str,
    ) -> bool:
        """
        Delete all chunks for a document from the index.
        
        Args:
            document_id: Document to delete
            company_id: Company identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            index = await self.get_or_create_index(company_id)
            
            # Delete nodes by document_id metadata filter
            # Note: This depends on the vector store implementation
            await self.vector_store_manager.delete_by_metadata(
                collection_name=f"company_{company_id}",
                metadata_filter={"document_id": document_id},
            )

            logger.info(f"Deleted document {document_id} from index")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            return False

    async def get_document_chunks(
        self,
        document_id: str,
        company_id: str,
    ) -> list[dict]:
        """
        Retrieve all chunks for a document.
        
        Args:
            document_id: Document identifier
            company_id: Company identifier
            
        Returns:
            List of chunk dictionaries
        """
        return await self.vector_store_manager.get_by_metadata(
            collection_name=f"company_{company_id}",
            metadata_filter={"document_id": document_id},
        )

    async def update_chunk_metadata(
        self,
        chunk_id: str,
        company_id: str,
        metadata_updates: dict,
    ) -> bool:
        """
        Update metadata for a specific chunk.
        
        Args:
            chunk_id: Chunk identifier
            company_id: Company identifier
            metadata_updates: Metadata to update
            
        Returns:
            True if updated successfully
        """
        return await self.vector_store_manager.update_metadata(
            collection_name=f"company_{company_id}",
            id_=chunk_id,
            metadata=metadata_updates,
        )

    def get_index_stats(self, company_id: str) -> dict[str, Any]:
        """Get statistics for a company's index."""
        if company_id not in self._indices:
            return {"exists": False}

        index = self._indices[company_id]
        return {
            "exists": True,
            "company_id": company_id,
            # Add more stats as available from the index
        }
