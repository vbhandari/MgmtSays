"""PPTX document parser using python-pptx."""

from pathlib import Path

from src.nlp.ingestion.parser import ParsedDocument


class PptxParser:
    """Parser for PowerPoint PPTX documents."""

    def supports(self, filename: str) -> bool:
        """Check if this parser supports the file."""
        suffix = Path(filename).suffix.lower()
        return suffix in [".pptx", ".ppt"]

    async def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Parse PPTX document.

        Args:
            content: PPTX file content
            filename: Original filename

        Returns:
            ParsedDocument with extracted text and metadata
        """

        # Extract metadata
        core_props = prs.core_properties
        metadata = {
            "filename": filename,
            "title": core_props.title or "",
            "author": core_props.author or "",
            "subject": core_props.subject or "",
            "created": str(core_props.created) if core_props.created else "",
            "modified": str(core_props.modified) if core_props.modified else "",
            "slide_count": len(prs.slides),
        }

        # Extract text from slides
        slides = []
        full_text_parts = []
        tables = []

        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text_parts = []
            slide_title = None

            for shape in slide.shapes:
                # Extract title
                if shape.has_text_frame:
                    text = self._extract_text_from_shape(shape)
                    if text:
                        slide_text_parts.append(text)
                        # First text shape with content is often the title
                        if (
                            slide_title is None
                            and shape.shape_type
                            and hasattr(shape, 'is_placeholder')
                            and shape.is_placeholder
                        ):
                            placeholder_type = shape.placeholder_format.type
                            if placeholder_type and placeholder_type.name in ['TITLE', 'CENTER_TITLE']:
                                slide_title = text

                # Extract tables
                if shape.has_table:
                    table_data = self._extract_table(shape.table)
                    if table_data:
                        tables.append({
                            "slide": slide_num,
                            "data": table_data,
                        })

            slide_text = "\n".join(slide_text_parts)
            if slide_text.strip():
                full_text_parts.append(f"--- Slide {slide_num} ---\n{slide_text}")
                slides.append({
                    "slide_number": slide_num,
                    "title": slide_title,
                    "text": slide_text,
                })

        # Build sections from slides
        sections = self._build_sections(slides)

        return ParsedDocument(
            text="\n\n".join(full_text_parts),
            metadata=metadata,
            pages=slides,  # Using pages field for slides
            sections=sections if sections else None,
            tables=tables if tables else None,
        )

    def _extract_text_from_shape(self, shape) -> str:
        """Extract text from a shape with text frame."""
        if not shape.has_text_frame:
            return ""

        paragraphs = []
        for paragraph in shape.text_frame.paragraphs:
            text = paragraph.text.strip()
            if text:
                paragraphs.append(text)

        return "\n".join(paragraphs)

    def _extract_table(self, table) -> list[list[str]]:
        """Extract data from a table shape."""
        rows = []
        for row in table.rows:
            cells = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                cells.append(cell_text)
            rows.append(cells)
        return rows

    def _build_sections(self, slides: list[dict]) -> list[dict]:
        """Build sections from slides based on titles."""
        sections = []
        current_section = None

        for slide in slides:
            title = slide.get("title")
            text = slide.get("text", "")

            if title:
                # Start new section
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "heading": title,
                    "heading_level": 1,
                    "slide_number": slide["slide_number"],
                    "content": [text] if text else [],
                }
            elif current_section:
                # Add to current section
                if text:
                    current_section["content"].append(text)
            else:
                # No title yet, create untitled section
                current_section = {
                    "heading": f"Slide {slide['slide_number']}",
                    "heading_level": 2,
                    "slide_number": slide["slide_number"],
                    "content": [text] if text else [],
                }

        # Add last section
        if current_section:
            sections.append(current_section)

        return sections
