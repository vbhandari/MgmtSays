"""Reranker for improving retrieval quality."""

from typing import TYPE_CHECKING
import logging

from src.config.settings import get_settings


if TYPE_CHECKING:
    from src.nlp.retrieval.hybrid import RetrievalResult


logger = logging.getLogger(__name__)


class Reranker:
    """
    Reranks retrieval results for improved relevance.
    
    Uses cross-encoder models when available, falls back to
    simple heuristics otherwise.
    """

    def __init__(self, model_name: str | None = None):
        self.settings = get_settings()
        self.model_name = model_name or self.settings.reranker_model
        self._model = None

    def _load_model(self):
        """Lazy load the reranker model."""
        if self._model is not None:
            return

        if not self.model_name:
            logger.info("No reranker model configured, using simple scoring")
            return

        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            logger.info(f"Loaded reranker model: {self.model_name}")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed, using simple scoring"
            )
        except Exception as e:
            logger.error(f"Failed to load reranker model: {e}")

    async def rerank(
        self,
        query: str,
        results: list["RetrievalResult"],
        top_k: int = 10,
    ) -> list["RetrievalResult"]:
        """
        Rerank retrieval results.
        
        Args:
            query: Original search query
            results: Initial retrieval results
            top_k: Number of top results to return
            
        Returns:
            Reranked results
        """
        if not results:
            return []

        self._load_model()

        if self._model:
            return await self._rerank_with_model(query, results, top_k)
        else:
            return await self._rerank_heuristic(query, results, top_k)

    async def _rerank_with_model(
        self,
        query: str,
        results: list["RetrievalResult"],
        top_k: int,
    ) -> list["RetrievalResult"]:
        """Rerank using cross-encoder model."""
        # Prepare query-document pairs
        pairs = [(query, r.text) for r in results]

        # Score pairs
        scores = self._model.predict(pairs)

        # Update scores and sort
        for i, result in enumerate(results):
            result.score = float(scores[i])

        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
        return sorted_results[:top_k]

    async def _rerank_heuristic(
        self,
        query: str,
        results: list["RetrievalResult"],
        top_k: int,
    ) -> list["RetrievalResult"]:
        """
        Simple heuristic reranking.
        
        Boosts scores based on:
        - Exact query term matches
        - Query term coverage
        - Position in document
        """
        query_terms = set(query.lower().split())

        for result in results:
            text_lower = result.text.lower()
            text_terms = set(text_lower.split())

            # Calculate term overlap
            overlap = len(query_terms & text_terms)
            coverage = overlap / len(query_terms) if query_terms else 0

            # Check for exact phrase match
            exact_match = query.lower() in text_lower

            # Calculate boost
            boost = 0.0
            if exact_match:
                boost += 0.2
            boost += coverage * 0.1

            # Check for important metadata
            metadata = result.metadata
            if metadata.get("speaker_role") in ["CEO", "CFO", "President"]:
                boost += 0.1

            # Apply boost
            result.score = result.score + boost

        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
        return sorted_results[:top_k]
