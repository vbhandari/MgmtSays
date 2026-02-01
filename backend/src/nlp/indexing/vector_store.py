"""Vector store manager for ChromaDB integration."""

from typing import Any
import logging

from src.config.settings import get_settings


logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages vector store connections and operations.
    
    Uses ChromaDB as the default vector store with support for:
    - Collection management per company
    - Metadata filtering
    - Hybrid search preparation
    """

    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self._collections: dict = {}

    async def initialize(self):
        """Initialize connection to ChromaDB."""
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        chroma_settings = ChromaSettings(
            anonymized_telemetry=False,
            allow_reset=True,
        )

        if self.settings.chroma_host:
            # Connect to remote ChromaDB
            self._client = chromadb.HttpClient(
                host=self.settings.chroma_host,
                port=self.settings.chroma_port,
                settings=chroma_settings,
            )
            logger.info(
                f"Connected to ChromaDB at "
                f"{self.settings.chroma_host}:{self.settings.chroma_port}"
            )
        else:
            # Use persistent local ChromaDB
            self._client = chromadb.PersistentClient(
                path=self.settings.chroma_persist_dir,
                settings=chroma_settings,
            )
            logger.info(f"Using local ChromaDB at {self.settings.chroma_persist_dir}")

    async def get_or_create_collection(self, collection_name: str):
        """
        Get or create a ChromaDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection wrapped for LlamaIndex
        """
        from llama_index.vector_stores.chroma import ChromaVectorStore

        if collection_name in self._collections:
            return self._collections[collection_name]

        # Get or create ChromaDB collection
        chroma_collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

        # Wrap in LlamaIndex vector store
        vector_store = ChromaVectorStore(
            chroma_collection=chroma_collection,
        )

        self._collections[collection_name] = vector_store
        return vector_store

    async def delete_collection(self, collection_name: str) -> bool:
        """Delete a collection."""
        try:
            self._client.delete_collection(collection_name)
            if collection_name in self._collections:
                del self._collections[collection_name]
            logger.info(f"Deleted collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    async def delete_by_metadata(
        self,
        collection_name: str,
        metadata_filter: dict[str, Any],
    ) -> int:
        """
        Delete documents by metadata filter.
        
        Args:
            collection_name: Collection to delete from
            metadata_filter: Metadata key-value pairs to match
            
        Returns:
            Number of documents deleted
        """
        try:
            collection = self._client.get_collection(collection_name)
            
            # Build where clause
            where = {}
            for key, value in metadata_filter.items():
                where[key] = {"$eq": value}

            # Get matching IDs
            results = collection.get(where=where)
            ids_to_delete = results.get("ids", [])

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                logger.info(
                    f"Deleted {len(ids_to_delete)} documents from {collection_name}"
                )

            return len(ids_to_delete)
        except Exception as e:
            logger.error(f"Failed to delete by metadata: {e}")
            return 0

    async def get_by_metadata(
        self,
        collection_name: str,
        metadata_filter: dict[str, Any],
        limit: int = 1000,
    ) -> list[dict]:
        """
        Retrieve documents by metadata filter.
        
        Args:
            collection_name: Collection to query
            metadata_filter: Metadata key-value pairs to match
            limit: Maximum number of results
            
        Returns:
            List of document dictionaries
        """
        try:
            collection = self._client.get_collection(collection_name)

            # Build where clause
            where = {}
            for key, value in metadata_filter.items():
                where[key] = {"$eq": value}

            results = collection.get(
                where=where,
                limit=limit,
                include=["documents", "metadatas", "embeddings"],
            )

            documents = []
            for i, id_ in enumerate(results.get("ids", [])):
                documents.append({
                    "id": id_,
                    "text": results["documents"][i] if results.get("documents") else None,
                    "metadata": results["metadatas"][i] if results.get("metadatas") else {},
                })

            return documents
        except Exception as e:
            logger.error(f"Failed to get by metadata: {e}")
            return []

    async def update_metadata(
        self,
        collection_name: str,
        id_: str,
        metadata: dict[str, Any],
    ) -> bool:
        """
        Update metadata for a document.
        
        Args:
            collection_name: Collection containing the document
            id_: Document ID
            metadata: New metadata values
            
        Returns:
            True if updated successfully
        """
        try:
            collection = self._client.get_collection(collection_name)
            collection.update(
                ids=[id_],
                metadatas=[metadata],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update metadata for {id_}: {e}")
            return False

    def get_collection_stats(self, collection_name: str) -> dict[str, Any]:
        """Get statistics for a collection."""
        try:
            collection = self._client.get_collection(collection_name)
            return {
                "name": collection_name,
                "count": collection.count(),
            }
        except Exception:
            return {"name": collection_name, "count": 0, "exists": False}

    def list_collections(self) -> list[str]:
        """List all collections."""
        collections = self._client.list_collections()
        return [c.name for c in collections]
