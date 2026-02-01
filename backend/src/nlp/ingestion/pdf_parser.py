"""PDF document parser using PyMuPDF."""

import io
from pathlib import Path

from src.nlp.ingestion.parser import ParsedDocument


class PDFParser:
    """Parser for PDF documents."""

    def supports(self, filename: str) -> bool:
        """Check if this parser supports the file."""
        return Path(filename).suffix.lower() == ".pdf"

    async def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Parse PDF document.
        
        Args:
            content: PDF file content
            filename: Original filename
            
        Returns:
            ParsedDocument with extracted text and metadata
        """
        import fitz  # PyMuPDF

        doc = fitz.open(stream=content, filetype="pdf")
        
        # Extract metadata
        metadata = {
            "filename": filename,
            "page_count": doc.page_count,
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "creator": doc.metadata.get("creator", ""),
            "creation_date": doc.metadata.get("creationDate", ""),
        }

        # Extract text from each page
        pages = []
        full_text_parts = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            full_text_parts.append(text)
            
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "width": page.rect.width,
                "height": page.rect.height,
            })

        # Extract tables if possible
        tables = self._extract_tables(doc)

        doc.close()

        return ParsedDocument(
            text="\n\n".join(full_text_parts),
            metadata=metadata,
            pages=pages,
            tables=tables,
        )

    def _extract_tables(self, doc) -> list[dict]:
        """Extract tables from PDF (basic implementation)."""
        tables = []
        
        # This is a simplified table extraction
        # For production, consider using tabula-py or camelot
        for page_num, page in enumerate(doc):
            # Look for table-like structures
            tabs = page.find_tables()
            for i, tab in enumerate(tabs):
                try:
                    table_data = tab.extract()
                    if table_data:
                        tables.append({
                            "page": page_num + 1,
                            "table_index": i,
                            "data": table_data,
                        })
                except Exception:
                    continue

        return tables
