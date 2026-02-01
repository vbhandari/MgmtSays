"""Plain text document parser."""

from pathlib import Path

from src.nlp.ingestion.parser import ParsedDocument


class TextParser:
    """Parser for plain text documents."""

    SUPPORTED_EXTENSIONS = [".txt", ".md", ".markdown", ".rst", ".text"]

    def supports(self, filename: str) -> bool:
        """Check if this parser supports the file."""
        suffix = Path(filename).suffix.lower()
        return suffix in self.SUPPORTED_EXTENSIONS

    async def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Parse text document.
        
        Args:
            content: Text file content
            filename: Original filename
            
        Returns:
            ParsedDocument with text content
        """
        # Try different encodings
        text = None
        for encoding in ["utf-8", "utf-16", "latin-1", "cp1252"]:
            try:
                text = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if text is None:
            raise ValueError(f"Unable to decode file: {filename}")

        # Extract sections for markdown files
        sections = None
        if Path(filename).suffix.lower() in [".md", ".markdown"]:
            sections = self._extract_markdown_sections(text)

        metadata = {
            "filename": filename,
            "char_count": len(text),
            "line_count": text.count("\n") + 1,
        }

        return ParsedDocument(
            text=text,
            metadata=metadata,
            sections=sections,
        )

    def _extract_markdown_sections(self, text: str) -> list[dict]:
        """Extract sections from markdown based on headings."""
        sections = []
        current_section = {"heading": None, "heading_level": 0, "content": []}
        
        for line in text.split("\n"):
            stripped = line.strip()
            
            # Check for markdown headings
            if stripped.startswith("#"):
                # Count heading level
                level = 0
                for char in stripped:
                    if char == "#":
                        level += 1
                    else:
                        break

                heading_text = stripped[level:].strip()
                
                # Save previous section
                if current_section["content"] or current_section["heading"]:
                    sections.append(current_section)
                
                current_section = {
                    "heading": heading_text,
                    "heading_level": level,
                    "content": [],
                }
            else:
                current_section["content"].append(line)

        # Add last section
        if current_section["content"] or current_section["heading"]:
            sections.append(current_section)

        return sections
