"""DSPy-based initiative deduplicator."""

import logging
from typing import Any

import dspy

from src.nlp.dspy_programs.base import configure_dspy
from src.nlp.dspy_programs.initiative_extractor import ExtractedInitiative


logger = logging.getLogger(__name__)


class DeduplicationSignature(dspy.Signature):
    """Identify duplicate or highly similar initiatives."""
    
    initiative_a: str = dspy.InputField(
        desc="First initiative name and description"
    )
    initiative_b: str = dspy.InputField(
        desc="Second initiative name and description"
    )
    
    is_duplicate: bool = dspy.OutputField(
        desc="True if initiatives refer to the same strategic initiative"
    )
    similarity_score: float = dspy.OutputField(
        desc="Similarity score 0-1"
    )
    reasoning: str = dspy.OutputField(
        desc="Brief explanation of the similarity assessment"
    )


class MergeSignature(dspy.Signature):
    """Merge multiple similar initiatives into a canonical form."""
    
    initiatives: list[str] = dspy.InputField(
        desc="List of similar initiative descriptions to merge"
    )
    
    canonical_name: str = dspy.OutputField(
        desc="Best name for the merged initiative"
    )
    canonical_description: str = dspy.OutputField(
        desc="Comprehensive description combining all inputs"
    )
    combined_metrics: list[str] = dspy.OutputField(
        desc="All unique metrics from the inputs"
    )
    combined_timeline: str = dspy.OutputField(
        desc="Most specific timeline information"
    )


class InitiativeDeduplicator(dspy.Module):
    """
    Identifies and merges duplicate initiatives.
    
    Uses semantic similarity to find duplicates, then merges
    them into canonical forms while preserving all evidence.
    """

    def __init__(self, similarity_threshold: float = 0.7):
        super().__init__()
        configure_dspy()
        
        self.similarity_threshold = similarity_threshold
        self.comparator = dspy.ChainOfThought(DeduplicationSignature)
        self.merger = dspy.ChainOfThought(MergeSignature)

    def forward(
        self,
        initiatives: list[ExtractedInitiative | dict],
    ) -> list[dict]:
        """
        Deduplicate a list of initiatives.
        
        Args:
            initiatives: List of initiatives (as ExtractedInitiative or dict)
            
        Returns:
            Deduplicated list with merged initiatives
        """
        if not initiatives:
            return []

        # Convert to dicts if needed
        init_dicts = []
        for init in initiatives:
            if isinstance(init, ExtractedInitiative):
                init_dicts.append(init.model_dump())
            else:
                init_dicts.append(init)

        # Find duplicate groups
        groups = self._find_duplicate_groups(init_dicts)

        # Merge each group
        merged = []
        for group in groups:
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged_init = self._merge_group(group)
                merged.append(merged_init)

        return merged

    def _find_duplicate_groups(
        self,
        initiatives: list[dict],
    ) -> list[list[dict]]:
        """Group initiatives by similarity."""
        if not initiatives:
            return []

        # Track which initiatives have been grouped
        grouped = set()
        groups = []

        for i, init_a in enumerate(initiatives):
            if i in grouped:
                continue

            group = [init_a]
            grouped.add(i)

            for j, init_b in enumerate(initiatives[i + 1:], start=i + 1):
                if j in grouped:
                    continue

                # Compare initiatives
                is_dup, score = self._compare_initiatives(init_a, init_b)

                if is_dup:
                    group.append(init_b)
                    grouped.add(j)

            groups.append(group)

        return groups

    def _compare_initiatives(
        self,
        init_a: dict,
        init_b: dict,
    ) -> tuple[bool, float]:
        """Compare two initiatives for similarity."""
        text_a = f"{init_a.get('name', '')}: {init_a.get('description', '')}"
        text_b = f"{init_b.get('name', '')}: {init_b.get('description', '')}"

        try:
            result = self.comparator(
                initiative_a=text_a,
                initiative_b=text_b,
            )

            is_duplicate = result.is_duplicate
            score = float(result.similarity_score)

            return is_duplicate and score >= self.similarity_threshold, score
        except Exception as e:
            logger.warning(f"Comparison failed, using fallback: {e}")
            # Fallback to simple text comparison
            return self._simple_compare(text_a, text_b)

    def _simple_compare(self, text_a: str, text_b: str) -> tuple[bool, float]:
        """Simple text-based similarity fallback."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())

        if not words_a or not words_b:
            return False, 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        
        score = intersection / union if union > 0 else 0.0
        return score >= self.similarity_threshold, score

    def _merge_group(self, group: list[dict]) -> dict:
        """Merge a group of similar initiatives."""
        if len(group) == 1:
            return group[0]

        # Prepare descriptions for merging
        descriptions = [
            f"{init.get('name', '')}: {init.get('description', '')}"
            for init in group
        ]

        try:
            result = self.merger(initiatives=descriptions)

            # Collect all evidence
            all_evidence = []
            all_metrics = []
            all_sources = []
            highest_confidence = 0.0
            best_category = group[0].get("category", "strategy")

            for init in group:
                if init.get("evidence_quote"):
                    all_evidence.append(init["evidence_quote"])
                if init.get("metrics"):
                    all_metrics.extend(init["metrics"])
                if init.get("source_chunk_id"):
                    all_sources.append(init["source_chunk_id"])
                if init.get("confidence", 0) > highest_confidence:
                    highest_confidence = init["confidence"]
                    best_category = init.get("category", "strategy")

            # Deduplicate metrics
            unique_metrics = list(set(result.combined_metrics + all_metrics))

            return {
                "name": result.canonical_name,
                "description": result.canonical_description,
                "category": best_category,
                "timeline": result.combined_timeline or group[0].get("timeline"),
                "metrics": unique_metrics,
                "confidence": highest_confidence,
                "evidence_quotes": all_evidence,
                "source_chunk_ids": all_sources,
                "merged_count": len(group),
            }
        except Exception as e:
            logger.warning(f"Merge failed, using first initiative: {e}")
            # Fallback to first initiative with combined sources
            result = group[0].copy()
            result["merged_count"] = len(group)
            result["source_chunk_ids"] = [
                init.get("source_chunk_id")
                for init in group
                if init.get("source_chunk_id")
            ]
            return result

    async def deduplicate_batch(
        self,
        initiatives: list[dict],
        batch_size: int = 50,
    ) -> list[dict]:
        """
        Deduplicate a large batch of initiatives.
        
        Processes in batches to handle large datasets.
        
        Args:
            initiatives: All initiatives to deduplicate
            batch_size: Size of processing batches
            
        Returns:
            Deduplicated initiatives
        """
        if len(initiatives) <= batch_size:
            return self.forward(initiatives)

        # Process in batches, then merge results
        all_merged = []
        
        for i in range(0, len(initiatives), batch_size):
            batch = initiatives[i:i + batch_size]
            merged = self.forward(batch)
            all_merged.extend(merged)

        # Final deduplication pass on merged results
        if len(all_merged) > batch_size:
            return await self.deduplicate_batch(all_merged, batch_size)
        
        return self.forward(all_merged)
