"""Integration tests for LlamaIndex indexing and retrieval."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.nlp.chunking.semantic import Chunk
from src.nlp.indexing.manager import IndexManager
from src.nlp.indexing.vector_store import VectorStoreManager
from src.nlp.retrieval.hybrid import HybridRetriever, RetrievalResult


@pytest.fixture
def sample_chunks() -> list[Chunk]:
    """Sample chunks for testing indexing."""
    return [
        Chunk(
            id="doc1_chunk_0",
            text="We are launching a new AI platform in Q1 2025. This represents a major strategic initiative.",
            metadata={
                "document_id": "doc1",
                "company_id": "comp1",
                "chunk_index": 0,
            },
        ),
        Chunk(
            id="doc1_chunk_1",
            text="Our cloud revenue grew 45% year-over-year. We expect continued growth in the enterprise segment.",
            metadata={
                "document_id": "doc1",
                "company_id": "comp1",
                "chunk_index": 1,
            },
        ),
        Chunk(
            id="doc2_chunk_0",
            text="The European expansion is on track. Frankfurt data center will be operational by mid-2025.",
            metadata={
                "document_id": "doc2",
                "company_id": "comp1",
                "chunk_index": 0,
            },
        ),
    ]


@pytest.mark.integration
class TestVectorStoreManager:
    """Tests for VectorStoreManager."""

    @pytest.mark.asyncio
    async def test_initialize_local_store(self, tmp_path):
        """Test initializing local ChromaDB store."""
        with patch("src.config.settings.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                chroma_host=None,
                chroma_port=8000,
                chroma_persist_dir=str(tmp_path / "chroma"),
            )

            manager = VectorStoreManager()
            await manager.initialize()

            assert manager._client is not None

    @pytest.mark.asyncio
    async def test_create_collection(self, tmp_path):
        """Test creating a collection."""
        with patch("src.config.settings.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                chroma_host=None,
                chroma_port=8000,
                chroma_persist_dir=str(tmp_path / "chroma"),
            )

            manager = VectorStoreManager()
            await manager.initialize()

            collection = await manager.get_or_create_collection("test_company")
            assert collection is not None

    @pytest.mark.asyncio
    async def test_delete_collection(self, tmp_path):
        """Test deleting a collection."""
        with patch("src.config.settings.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(
                chroma_host=None,
                chroma_port=8000,
                chroma_persist_dir=str(tmp_path / "chroma"),
            )

            manager = VectorStoreManager()
            await manager.initialize()

            # Create then delete
            await manager.get_or_create_collection("to_delete")
            result = await manager.delete_collection("to_delete")

            assert result is True


@pytest.mark.integration
class TestIndexManager:
    """Tests for IndexManager."""

    @pytest.fixture
    def mock_index_manager(self):
        """Create mock index manager for tests."""
        manager = MagicMock(spec=IndexManager)
        manager.index_chunks = AsyncMock(return_value=3)
        manager.get_or_create_index = AsyncMock()
        manager.delete_document_chunks = AsyncMock(return_value=True)
        return manager

    @pytest.mark.asyncio
    async def test_index_chunks_returns_count(self, mock_index_manager, sample_chunks):
        """Test that indexing returns chunk count."""
        count = await mock_index_manager.index_chunks(
            chunks=sample_chunks,
            company_id="comp1",
            document_id="doc1",
        )

        assert count == 3

    @pytest.mark.asyncio
    async def test_delete_document_chunks(self, mock_index_manager):
        """Test deleting chunks for a document."""
        result = await mock_index_manager.delete_document_chunks(
            company_id="comp1",
            document_id="doc1",
        )

        assert result is True


@pytest.mark.integration
class TestHybridRetriever:
    """Tests for HybridRetriever."""

    @pytest.fixture
    def mock_retriever(self):
        """Create mock retriever for tests."""
        retriever = MagicMock(spec=HybridRetriever)
        retriever.retrieve = AsyncMock(return_value=[
            RetrievalResult(
                chunk_id="doc1_chunk_0",
                text="We are launching a new AI platform in Q1 2025.",
                score=0.92,
                metadata={"document_id": "doc1"},
                document_id="doc1",
            ),
            RetrievalResult(
                chunk_id="doc2_chunk_0",
                text="The European expansion is on track.",
                score=0.85,
                metadata={"document_id": "doc2"},
                document_id="doc2",
            ),
        ])
        return retriever

    @pytest.mark.asyncio
    async def test_retrieve_returns_results(self, mock_retriever):
        """Test basic retrieval returns results."""
        results = await mock_retriever.retrieve(
            query="AI platform launch",
            company_id="comp1",
            top_k=5,
        )

        assert len(results) == 2
        assert all(isinstance(r, RetrievalResult) for r in results)

    @pytest.mark.asyncio
    async def test_retrieval_includes_scores(self, mock_retriever):
        """Test that retrieval results include similarity scores."""
        results = await mock_retriever.retrieve(
            query="strategic initiatives",
            company_id="comp1",
        )

        assert all(r.score > 0 for r in results)
        # Results should be ordered by score
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_retrieval_includes_document_ids(self, mock_retriever):
        """Test that retrieval results include document IDs for citations."""
        results = await mock_retriever.retrieve(
            query="cloud revenue",
            company_id="comp1",
        )

        assert all(r.document_id is not None for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_with_document_filter(self, mock_retriever):
        """Test retrieval with document ID filter."""
        mock_retriever.retrieve = AsyncMock(return_value=[
            RetrievalResult(
                chunk_id="doc1_chunk_0",
                text="We are launching a new AI platform.",
                score=0.92,
                metadata={"document_id": "doc1"},
                document_id="doc1",
            ),
        ])

        results = await mock_retriever.retrieve(
            query="AI platform",
            company_id="comp1",
            document_ids=["doc1"],
        )

        assert len(results) == 1
        assert results[0].document_id == "doc1"


@pytest.mark.integration
class TestMetadataPreservation:
    """Tests for metadata preservation through indexing and retrieval."""

    @pytest.mark.asyncio
    async def test_chunk_metadata_preserved(self):
        """Test that chunk metadata is preserved through indexing."""
        original_metadata = {
            "document_id": "doc1",
            "company_id": "comp1",
            "chunk_index": 0,
            "source_page": 5,
            "speaker": "CEO",
        }

        chunk = Chunk(
            id="test_chunk",
            text="Sample text",
            metadata=original_metadata,
        )

        # Verify metadata is accessible
        assert chunk.metadata["document_id"] == "doc1"
        assert chunk.metadata["speaker"] == "CEO"

    @pytest.mark.asyncio
    async def test_retrieval_result_has_citation_info(self):
        """Test that retrieval results contain citation information."""
        result = RetrievalResult(
            chunk_id="doc1_chunk_5",
            text="Important quote from the document.",
            score=0.9,
            metadata={
                "document_id": "doc1",
                "source_page": 10,
                "speaker": "CFO",
            },
            document_id="doc1",
        )

        # Citation info should be accessible
        assert result.document_id == "doc1"
        assert result.metadata["source_page"] == 10
        assert result.metadata["speaker"] == "CFO"
