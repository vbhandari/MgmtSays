"""Unit tests for document parsers."""

import pytest

from src.nlp.ingestion.parser import DocumentParser, ParsedDocument
from src.nlp.ingestion.text_parser import TextParser
from src.nlp.ingestion.transcript_parser import TranscriptParser


class TestTextParser:
    """Tests for TextParser."""

    @pytest.fixture
    def parser(self):
        return TextParser()

    def test_supports_txt_files(self, parser):
        """Test that parser supports .txt files."""
        assert parser.supports("document.txt") is True
        assert parser.supports("DOCUMENT.TXT") is True

    def test_supports_md_files(self, parser):
        """Test that parser supports .md files."""
        assert parser.supports("readme.md") is True
        assert parser.supports("README.MD") is True

    def test_does_not_support_pdf(self, parser):
        """Test that parser does not support .pdf files."""
        assert parser.supports("document.pdf") is False

    @pytest.mark.asyncio
    async def test_parse_simple_text(self, parser):
        """Test parsing simple text content."""
        content = b"Hello, World!\nThis is a test."
        result = await parser.parse(content, "test.txt")

        assert isinstance(result, ParsedDocument)
        assert "Hello, World!" in result.text
        assert result.metadata["filename"] == "test.txt"
        assert result.metadata["line_count"] == 2

    @pytest.mark.asyncio
    async def test_parse_markdown_sections(self, parser):
        """Test that markdown sections are extracted."""
        content = b"""# Heading 1
Some content under heading 1.

## Heading 2
Content under heading 2.
"""
        result = await parser.parse(content, "test.md")

        assert result.sections is not None
        assert len(result.sections) >= 2
        assert result.sections[0]["heading"] == "Heading 1"
        assert result.sections[0]["heading_level"] == 1

    @pytest.mark.asyncio
    async def test_handles_different_encodings(self, parser):
        """Test handling of different text encodings."""
        # UTF-8 content with special characters
        content = "Café résumé naïve".encode()
        result = await parser.parse(content, "test.txt")
        assert "Café" in result.text


class TestTranscriptParser:
    """Tests for TranscriptParser."""

    @pytest.fixture
    def parser(self):
        return TranscriptParser()

    def test_supports_transcript_files(self, parser):
        """Test that parser supports transcript files."""
        assert parser.supports("Q4_earnings_call_transcript.html") is True
        assert parser.supports("conference_call.htm") is True

    def test_does_not_support_non_transcript_html(self, parser):
        """Test that parser doesn't support random HTML files."""
        assert parser.supports("index.html") is False
        assert parser.supports("page.htm") is False

    def test_speaker_pattern_matching(self, parser):
        """Test speaker pattern matching."""
        # Test CEO pattern
        result = parser._match_speaker("John Smith - CEO:")
        assert result is not None
        assert result["speaker"] == "John Smith"
        assert result["role"] == "CEO"

        # Test parenthetical role
        result = parser._match_speaker("Jane Doe (CFO):")
        assert result is not None
        assert result["speaker"] == "Jane Doe"
        assert result["role"] == "CFO"

        # Test operator
        result = parser._match_speaker("Operator:")
        assert result is not None
        assert result["speaker"] == "Operator"


class TestPptxParser:
    """Tests for PptxParser."""

    @pytest.fixture
    def parser(self):
        from src.nlp.ingestion.pptx_parser import PptxParser
        return PptxParser()

    def test_supports_pptx_files(self, parser):
        """Test that parser supports .pptx files."""
        assert parser.supports("presentation.pptx") is True
        assert parser.supports("PRESENTATION.PPTX") is True

    def test_supports_ppt_files(self, parser):
        """Test that parser supports .ppt files."""
        assert parser.supports("legacy.ppt") is True

    def test_does_not_support_pdf(self, parser):
        """Test that parser does not support .pdf files."""
        assert parser.supports("document.pdf") is False

    def test_does_not_support_docx(self, parser):
        """Test that parser does not support .docx files."""
        assert parser.supports("document.docx") is False


class TestDocumentParser:
    """Tests for main DocumentParser."""

    @pytest.fixture
    def parser(self):
        return DocumentParser()

    def test_supported_types(self, parser):
        """Test list of supported types."""
        supported = parser.get_supported_types()
        assert ".pdf" in supported
        assert ".docx" in supported
        assert ".pptx" in supported
        assert ".txt" in supported

    @pytest.mark.asyncio
    async def test_routes_to_correct_parser(self, parser):
        """Test that parser routes to correct specialized parser."""
        content = b"Simple text content"
        result = await parser.parse(content, "test.txt")

        assert isinstance(result, ParsedDocument)
        assert "Simple text content" in result.text

    @pytest.mark.asyncio
    async def test_raises_for_unsupported_type(self, parser):
        """Test that unsupported types raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            await parser.parse(b"content", "file.xyz")
