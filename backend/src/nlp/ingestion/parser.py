"""Document parser - routes to appropriate parser based on file type."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class ParsedDocument:
    """Parsed document content."""

    text: str
    metadata: dict
    pages: list[dict] | None = None
    sections: list[dict] | None = None
    tables: list[dict] | None = None


class ParserProtocol(Protocol):
    """Protocol for document parsers."""

    async def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """Parse document content."""
        ...

    def supports(self, filename: str) -> bool:
        """Check if parser supports the file type."""
        ...


class DocumentParser:
    """Main document parser that routes to appropriate specialized parser."""

    def __init__(self):
        self._parsers: list[ParserProtocol] = []
        self._register_parsers()

    def _register_parsers(self):
        """Register available parsers."""
        from src.nlp.ingestion.docx_parser import DocxParser
        from src.nlp.ingestion.pdf_parser import PDFParser
        from src.nlp.ingestion.pptx_parser import PptxParser
        from src.nlp.ingestion.text_parser import TextParser
        from src.nlp.ingestion.transcript_parser import TranscriptParser

        self._parsers = [
            PDFParser(),
            DocxParser(),
            PptxParser(),
            TranscriptParser(),
            TextParser(),  # Fallback for plain text
        ]

    async def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Parse document using appropriate parser.
        
        Args:
            content: File content as bytes
            filename: Original filename (used to determine parser)
            
        Returns:
            ParsedDocument with extracted content
            
        Raises:
            ValueError: If no parser supports the file type
        """
        for parser in self._parsers:
            if parser.supports(filename):
                return await parser.parse(content, filename)

        raise ValueError(f"Unsupported file type: {Path(filename).suffix}")

    def get_supported_types(self) -> list[str]:
        """Get list of supported file extensions."""
        return [".pdf", ".docx", ".doc", ".pptx", ".ppt", ".txt", ".md", ".html", ".htm"]
