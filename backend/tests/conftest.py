"""Pytest configuration and shared fixtures."""

import asyncio
from typing import AsyncGenerator, Generator
import pytest
from unittest.mock import MagicMock, AsyncMock

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.main import create_app
from src.models.db.base import Base
from src.config.settings import Settings


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        app_name="MgmtSays Test",
        environment="test",
        debug=True,
        database_url=TEST_DATABASE_URL,
        chroma_persist_dir="./test_chroma",
        openai_api_key="test-key",
        llm_provider="openai",
    )


@pytest.fixture(scope="function")
async def async_engine():
    """Create async database engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(test_settings) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    app = create_app()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_llm() -> MagicMock:
    """Create mock LLM for testing."""
    mock = MagicMock()
    mock.return_value = MagicMock(
        text="Mock LLM response",
        response_metadata={},
    )
    return mock


@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Create mock vector store."""
    mock = MagicMock()
    mock.add_documents = AsyncMock()
    mock.similarity_search = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def sample_company_data() -> dict:
    """Sample company data for tests."""
    return {
        "name": "Test Company Inc.",
        "ticker": "TEST",
        "industry": "Technology",
        "sector": "Software",
        "description": "A test company for unit tests",
    }


@pytest.fixture
def sample_document_data() -> dict:
    """Sample document data for tests."""
    return {
        "title": "Q4 2024 Earnings Call Transcript",
        "document_type": "earnings_call",
        "fiscal_period": "Q4",
        "fiscal_year": 2024,
    }


@pytest.fixture
def sample_transcript_text() -> str:
    """Sample transcript text for testing."""
    return """
    John Smith - CEO:
    
    Good morning everyone. I'm pleased to report strong results for Q4.
    We're launching our new AI platform in Q1 2025, which represents a 
    significant strategic initiative for the company.
    
    Our cloud revenue grew 45% year-over-year, driven by enterprise adoption.
    We're also expanding into the European market with a new data center
    in Frankfurt, expected to be operational by mid-2025.
    
    Jane Doe - CFO:
    
    Thank you, John. Looking at the financials, total revenue reached $2.5B,
    up 30% from last year. We're maintaining our guidance for 25-30% growth
    in fiscal 2025.
    
    We're investing heavily in R&D, with a focus on AI and machine learning
    capabilities. This investment will drive long-term growth.
    """


@pytest.fixture
def sample_initiatives() -> list[dict]:
    """Sample initiatives for testing."""
    return [
        {
            "name": "AI Platform Launch",
            "description": "Launching new AI platform for enterprise customers",
            "category": "product",
            "timeline": "Q1 2025",
            "confidence": 0.9,
        },
        {
            "name": "European Market Expansion",
            "description": "Opening Frankfurt data center for European operations",
            "category": "market",
            "timeline": "mid-2025",
            "confidence": 0.85,
        },
        {
            "name": "R&D Investment",
            "description": "Heavy investment in AI and ML capabilities",
            "category": "strategy",
            "timeline": None,
            "confidence": 0.8,
        },
    ]
