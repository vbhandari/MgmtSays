"""Earnings call transcript parser."""

import re
from pathlib import Path
from dataclasses import dataclass

from src.nlp.ingestion.parser import ParsedDocument


@dataclass
class SpeakerTurn:
    """A single speaker turn in a transcript."""
    speaker: str
    role: str | None
    text: str
    timestamp: str | None = None


class TranscriptParser:
    """Parser for earnings call transcripts."""

    SUPPORTED_EXTENSIONS = [".html", ".htm"]

    # Common patterns for speaker identification
    SPEAKER_PATTERNS = [
        r"^([A-Z][A-Za-z\s\.]+)(?:\s*[-–—]\s*|\s*,\s*)(CEO|CFO|COO|CTO|CMO|President|Chairman|Analyst|Director|VP|Vice President|Executive)[:\s]*$",
        r"^([A-Z][A-Za-z\s\.]+)\s*\((CEO|CFO|COO|CTO|CMO|President|Chairman|Analyst|Director|VP|Vice President|Executive)\)[:\s]*$",
        r"^Operator[:\s]*$",
        r"^([A-Z][A-Za-z\s\.]+)[:\s]*$",
    ]

    def supports(self, filename: str) -> bool:
        """Check if this parser supports the file."""
        suffix = Path(filename).suffix.lower()
        # Check for transcript-like filenames
        name_lower = filename.lower()
        is_transcript = any(
            keyword in name_lower
            for keyword in ["transcript", "earnings", "call", "conference"]
        )
        return suffix in self.SUPPORTED_EXTENSIONS and is_transcript

    async def parse(self, content: bytes, filename: str) -> ParsedDocument:
        """
        Parse earnings call transcript.
        
        Args:
            content: HTML file content
            filename: Original filename
            
        Returns:
            ParsedDocument with structured transcript content
        """
        from bs4 import BeautifulSoup

        # Decode content
        text = content.decode("utf-8", errors="replace")
        
        # Parse HTML
        soup = BeautifulSoup(text, "html.parser")
        
        # Extract metadata from title/headers
        title = soup.find("title")
        metadata = {
            "filename": filename,
            "title": title.text.strip() if title else "",
            "type": "earnings_call_transcript",
        }

        # Try to extract date
        date_match = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
            soup.get_text(),
        )
        if date_match:
            metadata["date"] = date_match.group()

        # Extract text content
        body_text = soup.get_text(separator="\n")
        
        # Parse speaker turns
        sections = self._parse_sections(body_text)
        
        # Identify key sections
        prepared_remarks = []
        qa_section = []
        in_qa = False

        for section in sections:
            section_text = section.get("heading", "").lower()
            if "question" in section_text and "answer" in section_text:
                in_qa = True
            
            if in_qa:
                qa_section.append(section)
            else:
                prepared_remarks.append(section)

        metadata["has_qa_section"] = len(qa_section) > 0
        metadata["section_count"] = len(sections)

        return ParsedDocument(
            text=body_text,
            metadata=metadata,
            sections=sections,
        )

    def _parse_sections(self, text: str) -> list[dict]:
        """Parse transcript into speaker sections."""
        sections = []
        lines = text.split("\n")
        
        current_speaker = None
        current_role = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a speaker line
            speaker_match = self._match_speaker(line)
            
            if speaker_match:
                # Save previous section
                if current_speaker and current_content:
                    sections.append({
                        "heading": current_speaker,
                        "speaker_role": current_role,
                        "content": current_content,
                    })
                
                current_speaker = speaker_match["speaker"]
                current_role = speaker_match.get("role")
                current_content = []
            else:
                current_content.append(line)

        # Add last section
        if current_speaker and current_content:
            sections.append({
                "heading": current_speaker,
                "speaker_role": current_role,
                "content": current_content,
            })

        return sections

    def _match_speaker(self, line: str) -> dict | None:
        """Try to match a speaker line."""
        for pattern in self.SPEAKER_PATTERNS:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    return {"speaker": groups[0], "role": groups[1]}
                elif len(groups) == 1:
                    return {"speaker": groups[0], "role": None}
                else:
                    # Operator case
                    if "Operator" in line:
                        return {"speaker": "Operator", "role": "Operator"}
        return None
