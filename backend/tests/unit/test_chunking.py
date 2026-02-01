"""Unit tests for chunking modules."""

import pytest
from src.nlp.ingestion.parser import ParsedDocument
from src.nlp.chunking.semantic import SemanticChunker, Chunk
from src.nlp.chunking.structural import StructuralChunker


class TestSemanticChunker:
    """Tests for SemanticChunker."""

    @pytest.fixture
    def chunker(self):
        return SemanticChunker(chunk_size=500, chunk_overlap=50)

    @pytest.fixture
    def sample_document(self):
        return ParsedDocument(
            text="""
            This is the first paragraph of the document. It contains some 
            important information about the company's strategy.
            
            This is the second paragraph. It discusses the financial results
            and provides detailed metrics about revenue growth.
            
            The third paragraph covers market expansion plans and 
            international operations. The company is focusing on Europe.
            """,
            metadata={"filename": "test.pdf", "page_count": 1},
        )

    @pytest.mark.asyncio
    async def test_chunk_document_returns_chunks(self, chunker, sample_document):
        """Test that chunking produces Chunk objects."""
        chunks = await chunker.chunk_document(sample_document, "doc_123")
        
        assert len(chunks) > 0
        assert all(isinstance(c, Chunk) for c in chunks)

    @pytest.mark.asyncio
    async def test_chunk_ids_are_unique(self, chunker, sample_document):
        """Test that chunk IDs are unique."""
        chunks = await chunker.chunk_document(sample_document, "doc_123")
        chunk_ids = [c.id for c in chunks]
        
        assert len(chunk_ids) == len(set(chunk_ids))

    @pytest.mark.asyncio
    async def test_chunk_metadata_includes_document_id(self, chunker, sample_document):
        """Test that chunks include document ID in metadata."""
        chunks = await chunker.chunk_document(sample_document, "doc_123")
        
        for chunk in chunks:
            assert chunk.metadata.get("document_id") == "doc_123"

    @pytest.mark.asyncio
    async def test_chunk_by_sections(self, chunker):
        """Test chunking with sections."""
        doc = ParsedDocument(
            text="Full document text",
            metadata={"filename": "transcript.html"},
            sections=[
                {
                    "heading": "CEO Remarks",
                    "speaker_role": "CEO",
                    "content": ["This is what the CEO said about strategy."],
                },
                {
                    "heading": "CFO Remarks",
                    "speaker_role": "CFO",
                    "content": ["Financial overview and guidance."],
                },
            ],
        )
        
        chunks = await chunker.chunk_by_sections(doc, "doc_456")
        
        assert len(chunks) >= 2
        # Check that section metadata is preserved
        headings = [c.metadata.get("section_heading") for c in chunks]
        assert "CEO Remarks" in headings or "CFO Remarks" in headings

    def test_estimate_chunk_count(self, chunker):
        """Test chunk count estimation."""
        short_text = "Short text"
        long_text = "Long text " * 1000
        
        assert chunker.estimate_chunk_count(short_text) == 1
        assert chunker.estimate_chunk_count(long_text) > 1


class TestStructuralChunker:
    """Tests for StructuralChunker."""

    @pytest.fixture
    def chunker(self):
        return StructuralChunker(max_chunk_size=1000)

    @pytest.mark.asyncio
    async def test_chunk_with_pages(self, chunker):
        """Test chunking document with pages."""
        doc = ParsedDocument(
            text="All the text",
            metadata={"filename": "report.pdf"},
            pages=[
                {"page_number": 1, "text": "Page 1 content"},
                {"page_number": 2, "text": "Page 2 content"},
            ],
        )
        
        chunks = await chunker.chunk_document(doc, "doc_789")
        
        assert len(chunks) == 2
        assert any(c.metadata.get("page_number") == 1 for c in chunks)
        assert any(c.metadata.get("page_number") == 2 for c in chunks)

    @pytest.mark.asyncio
    async def test_chunk_with_sections(self, chunker):
        """Test chunking document with sections."""
        doc = ParsedDocument(
            text="All text",
            metadata={"filename": "doc.html"},
            sections=[
                {"heading": "Introduction", "content": ["Intro content"]},
                {"heading": "Conclusion", "content": ["Conclusion content"]},
            ],
        )
        
        chunks = await chunker.chunk_document(doc, "doc_101")
        
        assert len(chunks) >= 2

    @pytest.mark.asyncio
    async def test_chunk_tables_separately(self, chunker):
        """Test that tables are chunked separately."""
        doc = ParsedDocument(
            text="Document with tables",
            metadata={"filename": "report.pdf"},
            tables=[
                {"page": 1, "data": [["Header1", "Header2"], ["Val1", "Val2"]]},
            ],
        )
        
        chunks = await chunker.chunk_document(doc, "doc_102")
        
        table_chunks = [c for c in chunks if c.metadata.get("chunk_type") == "table"]
        assert len(table_chunks) == 1

    def test_table_to_text(self, chunker):
        """Test table conversion to markdown."""
        table_data = [
            ["Name", "Value"],
            ["Revenue", "$100M"],
            ["Growth", "25%"],
        ]
        
        result = chunker._table_to_text(table_data)
        
        assert "| Name | Value |" in result
        assert "| Revenue | $100M |" in result
        assert "---" in result  # Header separator
