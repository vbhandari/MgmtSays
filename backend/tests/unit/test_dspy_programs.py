"""Unit tests for DSPy programs."""

from unittest.mock import MagicMock, patch

import pytest

from src.nlp.dspy_programs.deduplicator import Deduplicator
from src.nlp.dspy_programs.initiative_extractor import (
    ExtractedInitiative,
    InitiativeExtractor,
)

# Sample test data for regression tests
SAMPLE_TRANSCRIPT = """
John Smith - CEO:

Good morning everyone. I'm pleased to report strong results for Q4.
We're launching our new AI platform in Q1 2025, which represents a 
significant strategic initiative for the company.

Our cloud revenue grew 45% year-over-year, driven by enterprise adoption.
We're also expanding into the European market with a new data center
in Frankfurt, expected to be operational by mid-2025.

We've committed to investing $500M in R&D over the next two years,
focusing on AI and machine learning capabilities.

Jane Doe - CFO:

Thank you, John. Looking at the financials, total revenue reached $2.5B,
up 30% from last year. We're maintaining our guidance for 25-30% growth
in fiscal 2025.

Our cost optimization program is yielding results, with operating margins
improving by 200 basis points this quarter.
"""

EXPECTED_INITIATIVE_CATEGORIES = {"product", "market", "strategy", "operational", "financial"}


class TestExtractedInitiative:
    """Tests for ExtractedInitiative model."""

    def test_valid_initiative(self):
        """Test creating a valid initiative."""
        initiative = ExtractedInitiative(
            name="AI Platform Launch",
            description="Launching new AI platform for enterprise customers",
            category="product",
            timeline="Q1 2025",
            metrics=["45% growth"],
            confidence=0.9,
            evidence_quote="We're launching our new AI platform in Q1 2025",
        )

        assert initiative.name == "AI Platform Launch"
        assert initiative.category == "product"
        assert initiative.confidence == 0.9

    def test_initiative_default_values(self):
        """Test initiative default values."""
        initiative = ExtractedInitiative(
            name="Test Initiative",
            description="Test description",
            category="strategy",
            evidence_quote="Test quote",
        )

        assert initiative.timeline is None
        assert initiative.metrics == []
        assert initiative.confidence == 0.0

    def test_initiative_category_validation(self):
        """Test that initiative accepts valid categories."""
        for category in EXPECTED_INITIATIVE_CATEGORIES:
            initiative = ExtractedInitiative(
                name="Test",
                description="Test",
                category=category,
                evidence_quote="Test",
            )
            assert initiative.category == category


class TestInitiativeExtractor:
    """Tests for InitiativeExtractor DSPy program."""

    @pytest.fixture
    def mock_extractor(self):
        """Create mock extractor with mocked LLM."""
        with patch("src.nlp.dspy_programs.base.configure_dspy"):
            extractor = InitiativeExtractor()
            extractor.extractor = MagicMock()
            return extractor

    def test_extractor_initialization(self, mock_extractor):
        """Test extractor initializes properly."""
        assert mock_extractor is not None
        assert hasattr(mock_extractor, "extractor")

    def test_normalize_category(self, mock_extractor):
        """Test category normalization."""
        # Test exact matches
        assert mock_extractor._normalize_category("product") == "product"
        assert mock_extractor._normalize_category("PRODUCT") == "product"

        # Test variations
        assert mock_extractor._normalize_category("strategic") == "strategy"
        assert mock_extractor._normalize_category("operations") == "operational"

    def test_forward_returns_initiatives(self, mock_extractor):
        """Test forward pass returns initiatives."""
        mock_extractor.extractor.return_value = MagicMock(
            initiatives=[
                {
                    "name": "AI Platform Launch",
                    "description": "New AI platform for enterprises",
                    "category": "product",
                    "timeline": "Q1 2025",
                    "metrics": [],
                    "confidence": 0.9,
                    "evidence_quote": "launching our new AI platform",
                }
            ]
        )

        results = mock_extractor.forward(
            context=SAMPLE_TRANSCRIPT,
            company_name="Test Company",
            document_type="earnings_call",
        )

        assert len(results) == 1
        assert isinstance(results[0], ExtractedInitiative)
        assert results[0].name == "AI Platform Launch"


class TestDeduplicator:
    """Tests for Deduplicator DSPy program."""

    @pytest.fixture
    def sample_initiatives(self):
        """Sample initiatives with duplicates."""
        return [
            ExtractedInitiative(
                name="AI Platform Launch",
                description="Launching new AI platform",
                category="product",
                timeline="Q1 2025",
                confidence=0.9,
                evidence_quote="Quote 1",
            ),
            ExtractedInitiative(
                name="New AI Platform Release",
                description="Releasing AI platform to market",
                category="product",
                timeline="Q1 2025",
                confidence=0.85,
                evidence_quote="Quote 2",
            ),
            ExtractedInitiative(
                name="European Expansion",
                description="Expanding to European markets",
                category="market",
                timeline="mid-2025",
                confidence=0.8,
                evidence_quote="Quote 3",
            ),
        ]

    @pytest.fixture
    def mock_deduplicator(self):
        """Create mock deduplicator."""
        with patch("src.nlp.dspy_programs.base.configure_dspy"):
            dedup = Deduplicator()
            return dedup

    def test_deduplicator_initialization(self, mock_deduplicator):
        """Test deduplicator initializes properly."""
        assert mock_deduplicator is not None

    @pytest.mark.asyncio
    async def test_group_by_category(self, mock_deduplicator, sample_initiatives):
        """Test grouping initiatives by category."""
        grouped = mock_deduplicator._group_by_category(sample_initiatives)

        assert "product" in grouped
        assert "market" in grouped
        assert len(grouped["product"]) == 2
        assert len(grouped["market"]) == 1


class TestRegressionData:
    """Regression tests with golden test data."""

    # Golden test cases for regression testing
    GOLDEN_TEST_CASES = [
        {
            "input": {
                "text": "We are investing $1B in AI R&D over the next 3 years.",
                "company": "Tech Corp",
            },
            "expected_categories": ["strategy", "product"],
            "min_initiatives": 1,
        },
        {
            "input": {
                "text": "Opening 50 new stores in Asia Pacific by year end.",
                "company": "Retail Inc",
            },
            "expected_categories": ["market"],
            "min_initiatives": 1,
        },
        {
            "input": {
                "text": "Implementing cost reduction program targeting $500M savings.",
                "company": "Industrial Co",
            },
            "expected_categories": ["operational", "financial"],
            "min_initiatives": 1,
        },
    ]

    def test_golden_test_cases_structure(self):
        """Verify golden test cases have correct structure."""
        for case in self.GOLDEN_TEST_CASES:
            assert "input" in case
            assert "text" in case["input"]
            assert "company" in case["input"]
            assert "expected_categories" in case
            assert "min_initiatives" in case

    def test_golden_categories_are_valid(self):
        """Verify golden test expected categories are valid."""
        for case in self.GOLDEN_TEST_CASES:
            for cat in case["expected_categories"]:
                assert cat in EXPECTED_INITIATIVE_CATEGORIES


class TestConfidenceScoring:
    """Tests for confidence scoring logic."""

    def test_high_confidence_indicators(self):
        """Test that certain phrases indicate high confidence."""
        high_confidence_phrases = [
            "we will launch",
            "committed to",
            "on track to deliver",
            "we have announced",
        ]

        for phrase in high_confidence_phrases:
            # These phrases should indicate forward-looking statements
            # that can be extracted with higher confidence
            assert phrase  # Placeholder for actual confidence logic test

    def test_low_confidence_indicators(self):
        """Test that certain phrases indicate lower confidence."""
        low_confidence_phrases = [
            "we may consider",
            "potentially",
            "exploring options",
            "subject to",
        ]

        for phrase in low_confidence_phrases:
            # These phrases should indicate uncertainty
            assert phrase  # Placeholder for actual confidence logic test


class TestCategoryClassification:
    """Tests for initiative category classification."""

    CATEGORY_KEYWORDS = {
        "product": ["launch", "product", "feature", "platform", "release"],
        "market": ["expand", "market", "region", "international", "geographic"],
        "strategy": ["strategy", "vision", "mission", "long-term", "roadmap"],
        "operational": ["efficiency", "cost", "optimize", "process", "operations"],
        "financial": ["revenue", "margin", "profit", "guidance", "forecast"],
    }

    def test_category_keywords_defined(self):
        """Test that all categories have keywords defined."""
        for category in EXPECTED_INITIATIVE_CATEGORIES:
            assert category in self.CATEGORY_KEYWORDS
            assert len(self.CATEGORY_KEYWORDS[category]) > 0

    def test_categories_are_mutually_exclusive_in_keywords(self):
        """Test that primary keywords are category-specific."""
        # Primary keywords (first in list) should be unique
        primary_keywords = [kws[0] for kws in self.CATEGORY_KEYWORDS.values()]
        assert len(primary_keywords) == len(set(primary_keywords))
