"""Structural chunking based on document structure."""

from dataclasses import dataclass

from src.nlp.ingestion.parser import ParsedDocument
from src.nlp.chunking.semantic import Chunk


class StructuralChunker:
    """
    Structural chunker that preserves document hierarchy.
    
    Chunks documents based on their natural structure:
    - PDF pages
    - Document sections/headings
    - Speaker turns in transcripts
    - Tables as separate chunks
    """

    def __init__(
        self,
        max_chunk_size: int = 2000,
        include_tables: bool = True,
    ):
        self.max_chunk_size = max_chunk_size
        self.include_tables = include_tables

    async def chunk_document(
        self,
        parsed_doc: ParsedDocument,
        document_id: str,
    ) -> list[Chunk]:
        """
        Chunk document based on its structure.
        
        Args:
            parsed_doc: The parsed document
            document_id: Document ID
            
        Returns:
            List of structure-aware chunks
        """
        chunks = []
        chunk_idx = 0

        # Chunk by pages if available (PDFs)
        if parsed_doc.pages:
            for page in parsed_doc.pages:
                page_chunks = self._chunk_page(
                    page,
                    document_id,
                    chunk_idx,
                )
                chunks.extend(page_chunks)
                chunk_idx += len(page_chunks)

        # Chunk by sections if available
        elif parsed_doc.sections:
            for section_idx, section in enumerate(parsed_doc.sections):
                section_chunks = self._chunk_section(
                    section,
                    document_id,
                    section_idx,
                    chunk_idx,
                )
                chunks.extend(section_chunks)
                chunk_idx += len(section_chunks)

        # Fallback to simple text chunking
        else:
            chunks = self._chunk_text(
                parsed_doc.text,
                parsed_doc.metadata,
                document_id,
            )

        # Add table chunks
        if self.include_tables and parsed_doc.tables:
            table_chunks = self._chunk_tables(
                parsed_doc.tables,
                document_id,
                chunk_idx,
            )
            chunks.extend(table_chunks)

        return chunks

    def _chunk_page(
        self,
        page: dict,
        document_id: str,
        start_idx: int,
    ) -> list[Chunk]:
        """Chunk a single page."""
        text = page.get("text", "")
        page_num = page.get("page_number", 1)

        if len(text) <= self.max_chunk_size:
            return [
                Chunk(
                    id=f"{document_id}_page_{page_num}",
                    text=text,
                    metadata={
                        "page_number": page_num,
                        "document_id": document_id,
                        "chunk_type": "page",
                    },
                )
            ]

        # Split large pages
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.max_chunk_size and current_chunk:
                chunks.append(
                    Chunk(
                        id=f"{document_id}_page_{page_num}_part_{len(chunks)}",
                        text=" ".join(current_chunk),
                        metadata={
                            "page_number": page_num,
                            "document_id": document_id,
                            "chunk_type": "page_part",
                            "part_index": len(chunks),
                        },
                    )
                )
                current_chunk = []
                current_length = 0

            current_chunk.append(word)
            current_length += word_length

        if current_chunk:
            chunks.append(
                Chunk(
                    id=f"{document_id}_page_{page_num}_part_{len(chunks)}",
                    text=" ".join(current_chunk),
                    metadata={
                        "page_number": page_num,
                        "document_id": document_id,
                        "chunk_type": "page_part",
                        "part_index": len(chunks),
                    },
                )
            )

        return chunks

    def _chunk_section(
        self,
        section: dict,
        document_id: str,
        section_idx: int,
        start_idx: int,
    ) -> list[Chunk]:
        """Chunk a document section."""
        heading = section.get("heading", "")
        content = section.get("content", [])
        speaker_role = section.get("speaker_role")

        if isinstance(content, list):
            text = "\n".join(content)
        else:
            text = content

        full_text = f"{heading}\n\n{text}" if heading else text

        if len(full_text) <= self.max_chunk_size:
            return [
                Chunk(
                    id=f"{document_id}_section_{section_idx}",
                    text=full_text,
                    metadata={
                        "section_heading": heading,
                        "section_index": section_idx,
                        "document_id": document_id,
                        "chunk_type": "section",
                        "speaker_role": speaker_role,
                    },
                )
            ]

        # Split large sections while preserving heading context
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = [heading] if heading else []
        current_length = len(heading) if heading else 0

        for para in paragraphs:
            if current_length + len(para) > self.max_chunk_size and len(current_chunk) > 1:
                chunks.append(
                    Chunk(
                        id=f"{document_id}_section_{section_idx}_part_{len(chunks)}",
                        text="\n\n".join(current_chunk),
                        metadata={
                            "section_heading": heading,
                            "section_index": section_idx,
                            "document_id": document_id,
                            "chunk_type": "section_part",
                            "part_index": len(chunks),
                            "speaker_role": speaker_role,
                        },
                    )
                )
                # Start new chunk with heading context
                current_chunk = [f"[Continued from: {heading}]"] if heading else []
                current_length = len(current_chunk[0]) if current_chunk else 0

            current_chunk.append(para)
            current_length += len(para)

        if current_chunk:
            chunks.append(
                Chunk(
                    id=f"{document_id}_section_{section_idx}_part_{len(chunks)}",
                    text="\n\n".join(current_chunk),
                    metadata={
                        "section_heading": heading,
                        "section_index": section_idx,
                        "document_id": document_id,
                        "chunk_type": "section_part",
                        "part_index": len(chunks),
                        "speaker_role": speaker_role,
                    },
                )
            )

        return chunks

    def _chunk_text(
        self,
        text: str,
        metadata: dict,
        document_id: str,
    ) -> list[Chunk]:
        """Simple text chunking fallback."""
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            if current_length + len(para) > self.max_chunk_size and current_chunk:
                chunks.append(
                    Chunk(
                        id=f"{document_id}_chunk_{len(chunks)}",
                        text="\n\n".join(current_chunk),
                        metadata={
                            **metadata,
                            "document_id": document_id,
                            "chunk_index": len(chunks),
                            "chunk_type": "text",
                        },
                    )
                )
                current_chunk = []
                current_length = 0

            current_chunk.append(para)
            current_length += len(para)

        if current_chunk:
            chunks.append(
                Chunk(
                    id=f"{document_id}_chunk_{len(chunks)}",
                    text="\n\n".join(current_chunk),
                    metadata={
                        **metadata,
                        "document_id": document_id,
                        "chunk_index": len(chunks),
                        "chunk_type": "text",
                    },
                )
            )

        return chunks

    def _chunk_tables(
        self,
        tables: list[dict],
        document_id: str,
        start_idx: int,
    ) -> list[Chunk]:
        """Create chunks from tables."""
        chunks = []

        for i, table in enumerate(tables):
            table_data = table.get("data", [])
            page = table.get("page")

            # Convert table to text representation
            table_text = self._table_to_text(table_data)

            chunks.append(
                Chunk(
                    id=f"{document_id}_table_{i}",
                    text=table_text,
                    metadata={
                        "document_id": document_id,
                        "chunk_type": "table",
                        "table_index": i,
                        "page_number": page,
                        "row_count": len(table_data),
                        "col_count": len(table_data[0]) if table_data else 0,
                    },
                )
            )

        return chunks

    def _table_to_text(self, table_data: list[list]) -> str:
        """Convert table data to text representation."""
        if not table_data:
            return ""

        # Use markdown table format
        lines = []
        
        for i, row in enumerate(table_data):
            line = "| " + " | ".join(str(cell) for cell in row) + " |"
            lines.append(line)
            
            # Add header separator after first row
            if i == 0:
                separator = "| " + " | ".join("---" for _ in row) + " |"
                lines.append(separator)

        return "\n".join(lines)
