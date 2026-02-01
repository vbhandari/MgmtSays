"""DSPy-based insight classifier."""

import logging

import dspy

from src.nlp.dspy_programs.base import configure_dspy


logger = logging.getLogger(__name__)


class InsightClassificationSignature(dspy.Signature):
    """Classify an insight or initiative into categories and assess importance."""
    
    insight_text: str = dspy.InputField(
        desc="The insight or initiative text to classify"
    )
    context: str = dspy.InputField(
        desc="Additional context from the source document"
    )
    company_industry: str = dspy.InputField(
        desc="Industry of the company"
    )
    
    primary_category: str = dspy.OutputField(
        desc="Primary category: strategy, product, market, operational, financial, technology, regulatory, competitive"
    )
    secondary_categories: list[str] = dspy.OutputField(
        desc="List of secondary categories that also apply"
    )
    importance_score: float = dspy.OutputField(
        desc="Importance score 1-10 based on strategic significance"
    )
    sentiment: str = dspy.OutputField(
        desc="Sentiment: positive, negative, neutral, mixed"
    )
    actionability: str = dspy.OutputField(
        desc="Actionability level: immediate, short_term, long_term, informational"
    )
    reasoning: str = dspy.OutputField(
        desc="Brief reasoning for the classification"
    )


class InsightClassifier(dspy.Module):
    """
    Classifies insights and initiatives into meaningful categories.
    
    Provides:
    - Category classification
    - Importance scoring
    - Sentiment analysis
    - Actionability assessment
    """

    VALID_CATEGORIES = {
        "strategy",
        "product",
        "market",
        "operational",
        "financial",
        "technology",
        "regulatory",
        "competitive",
    }

    VALID_SENTIMENTS = {"positive", "negative", "neutral", "mixed"}

    VALID_ACTIONABILITY = {"immediate", "short_term", "long_term", "informational"}

    def __init__(self):
        super().__init__()
        configure_dspy()
        
        self.classifier = dspy.ChainOfThought(InsightClassificationSignature)

    def forward(
        self,
        insight_text: str,
        context: str = "",
        company_industry: str = "technology",
    ) -> dict:
        """
        Classify an insight.
        
        Args:
            insight_text: The insight/initiative text
            context: Additional source context
            company_industry: Industry for relevance
            
        Returns:
            Classification dictionary
        """
        result = self.classifier(
            insight_text=insight_text,
            context=context,
            company_industry=company_industry,
        )

        return {
            "primary_category": self._normalize_category(result.primary_category),
            "secondary_categories": [
                self._normalize_category(c)
                for c in result.secondary_categories
            ],
            "importance_score": self._normalize_score(result.importance_score),
            "sentiment": self._normalize_sentiment(result.sentiment),
            "actionability": self._normalize_actionability(result.actionability),
            "reasoning": result.reasoning,
        }

    def _normalize_category(self, category: str) -> str:
        """Normalize to valid category."""
        normalized = category.lower().strip()
        if normalized in self.VALID_CATEGORIES:
            return normalized
        
        # Map common variations
        mapping = {
            "strategic": "strategy",
            "products": "product",
            "marketing": "market",
            "operations": "operational",
            "finance": "financial",
            "tech": "technology",
            "regulation": "regulatory",
            "competition": "competitive",
        }
        return mapping.get(normalized, "strategy")

    def _normalize_sentiment(self, sentiment: str) -> str:
        """Normalize to valid sentiment."""
        normalized = sentiment.lower().strip()
        if normalized in self.VALID_SENTIMENTS:
            return normalized
        return "neutral"

    def _normalize_actionability(self, actionability: str) -> str:
        """Normalize to valid actionability."""
        normalized = actionability.lower().strip().replace(" ", "_")
        if normalized in self.VALID_ACTIONABILITY:
            return normalized
        
        # Map variations
        if "immediate" in normalized or "now" in normalized:
            return "immediate"
        elif "short" in normalized:
            return "short_term"
        elif "long" in normalized:
            return "long_term"
        return "informational"

    def _normalize_score(self, score: float) -> float:
        """Normalize score to 1-10 range."""
        try:
            score = float(score)
            return max(1.0, min(10.0, score))
        except (ValueError, TypeError):
            return 5.0

    async def classify_batch(
        self,
        insights: list[dict],
        company_industry: str = "technology",
    ) -> list[dict]:
        """
        Classify multiple insights.
        
        Args:
            insights: List of insight dicts with 'text' and optional 'context'
            company_industry: Industry context
            
        Returns:
            List of classification results
        """
        results = []
        
        for insight in insights:
            text = insight.get("text") or insight.get("description", "")
            context = insight.get("context", "")
            
            try:
                classification = self.forward(
                    insight_text=text,
                    context=context,
                    company_industry=company_industry,
                )
                
                # Merge with original insight
                result = {**insight, **classification}
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to classify insight: {e}")
                # Return insight with default classification
                results.append({
                    **insight,
                    "primary_category": "strategy",
                    "secondary_categories": [],
                    "importance_score": 5.0,
                    "sentiment": "neutral",
                    "actionability": "informational",
                    "reasoning": "Classification failed",
                })

        return results
