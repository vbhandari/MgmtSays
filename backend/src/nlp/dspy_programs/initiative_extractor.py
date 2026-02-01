"""DSPy-based initiative extractor."""

from typing import Any
import logging

import dspy
from pydantic import BaseModel, Field

from src.nlp.dspy_programs.base import configure_dspy


logger = logging.getLogger(__name__)


class ExtractedInitiative(BaseModel):
    """An extracted strategic initiative."""
    
    name: str = Field(description="Short name for the initiative (3-7 words)")
    description: str = Field(description="Detailed description of the initiative")
    category: str = Field(description="Category: strategy, product, market, operational, financial")
    timeline: str | None = Field(default=None, description="Mentioned timeline or deadline")
    metrics: list[str] = Field(default_factory=list, description="Any mentioned metrics or KPIs")
    confidence: float = Field(default=0.0, description="Confidence score 0-1")
    evidence_quote: str = Field(description="Direct quote from source text")


class InitiativeExtractionSignature(dspy.Signature):
    """Extract strategic initiatives from management disclosure text."""
    
    context: str = dspy.InputField(
        desc="Text chunk from management disclosure (earnings call, annual report, etc.)"
    )
    company_name: str = dspy.InputField(
        desc="Name of the company"
    )
    document_type: str = dspy.InputField(
        desc="Type of document: earnings_call, annual_report, investor_presentation, etc."
    )
    
    initiatives: list[dict] = dspy.OutputField(
        desc="""List of strategic initiatives extracted. Each initiative should have:
        - name: Short name (3-7 words)
        - description: Detailed description
        - category: One of [strategy, product, market, operational, financial]
        - timeline: Mentioned timeline if any
        - metrics: List of mentioned metrics/KPIs
        - confidence: Float 0-1 indicating extraction confidence
        - evidence_quote: Direct quote supporting the initiative"""
    )


class InitiativeExtractor(dspy.Module):
    """
    Extracts strategic initiatives from management disclosures.
    
    Uses DSPy's structured output capabilities to extract
    well-defined initiative objects with citations.
    """

    def __init__(self):
        super().__init__()
        configure_dspy()
        
        self.extractor = dspy.ChainOfThought(InitiativeExtractionSignature)

    def forward(
        self,
        context: str,
        company_name: str,
        document_type: str = "earnings_call",
    ) -> list[ExtractedInitiative]:
        """
        Extract initiatives from text.
        
        Args:
            context: Text chunk to analyze
            company_name: Company name for context
            document_type: Type of source document
            
        Returns:
            List of extracted initiatives
        """
        result = self.extractor(
            context=context,
            company_name=company_name,
            document_type=document_type,
        )

        initiatives = []
        for init_dict in result.initiatives:
            try:
                initiative = ExtractedInitiative(
                    name=init_dict.get("name", ""),
                    description=init_dict.get("description", ""),
                    category=self._normalize_category(init_dict.get("category", "strategy")),
                    timeline=init_dict.get("timeline"),
                    metrics=init_dict.get("metrics", []),
                    confidence=float(init_dict.get("confidence", 0.5)),
                    evidence_quote=init_dict.get("evidence_quote", ""),
                )
                initiatives.append(initiative)
            except Exception as e:
                logger.warning(f"Failed to parse initiative: {e}")
                continue

        return initiatives

    def _normalize_category(self, category: str) -> str:
        """Normalize category to valid values."""
        valid_categories = {"strategy", "product", "market", "operational", "financial"}
        normalized = category.lower().strip()
        
        if normalized in valid_categories:
            return normalized
        
        # Map common variations
        mapping = {
            "strategic": "strategy",
            "products": "product",
            "marketing": "market",
            "operations": "operational",
            "finance": "financial",
            "growth": "strategy",
            "expansion": "market",
            "cost": "operational",
            "revenue": "financial",
        }
        
        return mapping.get(normalized, "strategy")

    async def extract_from_chunks(
        self,
        chunks: list[dict],
        company_name: str,
        document_type: str = "earnings_call",
    ) -> list[ExtractedInitiative]:
        """
        Extract initiatives from multiple chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'text' key
            company_name: Company name
            document_type: Document type
            
        Returns:
            All extracted initiatives (may contain duplicates)
        """
        all_initiatives = []

        for chunk in chunks:
            text = chunk.get("text", "")
            if not text.strip():
                continue

            try:
                initiatives = self.forward(
                    context=text,
                    company_name=company_name,
                    document_type=document_type,
                )
                
                # Add source metadata
                for init in initiatives:
                    init_dict = init.model_dump()
                    init_dict["source_chunk_id"] = chunk.get("id")
                    init_dict["source_metadata"] = chunk.get("metadata", {})
                
                all_initiatives.extend(initiatives)
            except Exception as e:
                logger.error(f"Failed to extract from chunk: {e}")
                continue

        return all_initiatives
