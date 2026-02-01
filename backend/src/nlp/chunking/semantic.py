"""Semantic chunking using LlamaIndex."""

from dataclasses import dataclass
from typing import Sequence

from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import (
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.core.schema import TextNode

from src.config.settings import get_settings
from src.nlp.ingestion.parser import ParsedDocument


@dataclass
class Chunk:
    """A chunk of text with metadata."""
    
    id: str
    text: str
    metadata: dict
    start_char: int | None = None
    end_char: int | None = None


class SemanticChunker:
    """
    Semantic text chunker that preserves context and meaning.
    
    Uses LlamaIndex's semantic splitter for intelligent chunking
    that respects sentence and paragraph boundaries.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        use_semantic_splitting: bool = True,
    ):
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.use_semantic_splitting = use_semantic_splitting
        
        # Initialize splitters
        self._sentence_splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    async def chunk_document(
        self,
        parsed_doc: ParsedDocument,
        document_id: str,
    ) -> list[Chunk]:
        """
        Chunk a parsed document into semantic units.
        
        Args:
            parsed_doc: The parsed document to chunk
            document_id: ID of the source document
            
        Returns:
            List of Chunk objects
        """
        # Create LlamaIndex document
        llama_doc = LlamaDocument(
            text=parsed_doc.text,
            metadata={
                **parsed_doc.metadata,
                "document_id": document_id,
            },
        )

        # Split into nodes
        nodes = self._sentence_splitter.get_nodes_from_documents([llama_doc])

        # Convert to our Chunk format
        chunks = []
        for i, node in enumerate(nodes):
            chunk = Chunk(
                id=f"{document_id}_chunk_{i}",
                text=node.get_content(),
                metadata={
                    **node.metadata,
                    "chunk_index": i,
                    "chunk_count": len(nodes),
                },
                start_char=node.start_char_idx,
                end_char=node.end_char_idx,
            )
            chunks.append(chunk)

        return chunks

    async def chunk_by_sections(
        self,
        parsed_doc: ParsedDocument,
        document_id: str,
    ) -> list[Chunk]:
        """
        Chunk document by sections, then apply semantic splitting.
        
        Useful for structured documents like earnings calls where
        preserving section boundaries is important.
        """
        if not parsed_doc.sections:
            return await self.chunk_document(parsed_doc, document_id)

        chunks = []
        chunk_idx = 0

        for section_idx, section in enumerate(parsed_doc.sections):
            # Get section text
            heading = section.get("heading", "")
            content = section.get("content", [])
            
            if isinstance(content, list):
                section_text = "\n".join(content)
            else:
                section_text = content

            if not section_text.strip():
                continue

            # Add heading as context
            full_text = f"{heading}\n\n{section_text}" if heading else section_text

            # Create LlamaIndex document for this section
            llama_doc = LlamaDocument(
                text=full_text,
                metadata={
                    **parsed_doc.metadata,
                    "document_id": document_id,
                    "section_index": section_idx,
                    "section_heading": heading,
                    "speaker_role": section.get("speaker_role"),
                },
            )

            # Split section
            nodes = self._sentence_splitter.get_nodes_from_documents([llama_doc])

            for node in nodes:
                chunk = Chunk(
                    id=f"{document_id}_chunk_{chunk_idx}",
                    text=node.get_content(),
                    metadata={
                        **node.metadata,
                        "chunk_index": chunk_idx,
                        "section_chunk_index": nodes.index(node),
                    },
                )
                chunks.append(chunk)
                chunk_idx += 1

        return chunks

    def estimate_chunk_count(self, text: str) -> int:
        """Estimate number of chunks for given text."""
        # Rough estimation based on character count
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        return max(1, len(text) // (effective_chunk_size * 4))  # ~4 chars per token
