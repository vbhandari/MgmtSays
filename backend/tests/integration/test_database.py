"""Integration tests for database operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.db.company import CompanyModel
from src.models.db.document import DocumentModel
from src.repositories.company_repository import CompanyRepository
from src.repositories.document_repository import DocumentRepository


@pytest.mark.integration
class TestCompanyRepository:
    """Tests for CompanyRepository with real database."""

    @pytest.mark.asyncio
    async def test_create_and_get_company(self, db_session: AsyncSession):
        """Test creating and retrieving a company."""
        repo = CompanyRepository(db_session)
        
        # Create company
        company = await repo.create(
            name="Integration Test Company",
            ticker="INTG",
            industry="Technology",
        )
        
        assert company.id is not None
        assert company.name == "Integration Test Company"
        
        # Retrieve company
        retrieved = await repo.get(company.id)
        assert retrieved is not None
        assert retrieved.ticker == "INTG"

    @pytest.mark.asyncio
    async def test_get_by_ticker(self, db_session: AsyncSession):
        """Test getting company by ticker symbol."""
        repo = CompanyRepository(db_session)
        
        # Create company
        await repo.create(
            name="Ticker Test Company",
            ticker="TICK",
            industry="Finance",
        )
        
        # Get by ticker
        company = await repo.get_by_ticker("TICK")
        assert company is not None
        assert company.name == "Ticker Test Company"

    @pytest.mark.asyncio
    async def test_list_companies(self, db_session: AsyncSession):
        """Test listing all companies."""
        repo = CompanyRepository(db_session)
        
        # Create multiple companies
        await repo.create(name="Company A", ticker="CMPA")
        await repo.create(name="Company B", ticker="CMPB")
        
        # List all
        companies = await repo.list_all()
        assert len(companies) >= 2

    @pytest.mark.asyncio
    async def test_update_company(self, db_session: AsyncSession):
        """Test updating a company."""
        repo = CompanyRepository(db_session)
        
        # Create
        company = await repo.create(name="Original Name", ticker="ORIG")
        
        # Update
        updated = await repo.update(company.id, name="Updated Name")
        
        assert updated.name == "Updated Name"
        assert updated.ticker == "ORIG"  # Unchanged

    @pytest.mark.asyncio
    async def test_delete_company(self, db_session: AsyncSession):
        """Test deleting a company."""
        repo = CompanyRepository(db_session)
        
        # Create
        company = await repo.create(name="To Delete", ticker="DEL")
        
        # Delete
        result = await repo.delete(company.id)
        assert result is True
        
        # Verify deleted
        retrieved = await repo.get(company.id)
        assert retrieved is None


@pytest.mark.integration
class TestDocumentRepository:
    """Tests for DocumentRepository with real database."""

    @pytest.fixture
    async def company(self, db_session: AsyncSession):
        """Create a company for document tests."""
        repo = CompanyRepository(db_session)
        return await repo.create(name="Doc Test Company", ticker="DOCT")

    @pytest.mark.asyncio
    async def test_create_document(self, db_session: AsyncSession, company):
        """Test creating a document."""
        repo = DocumentRepository(db_session)
        
        doc = await repo.create(
            company_id=company.id,
            title="Q4 2024 Earnings Call",
            document_type="earnings_call",
            fiscal_period="Q4",
            fiscal_year=2024,
        )
        
        assert doc.id is not None
        assert doc.company_id == company.id
        assert doc.processing_status == "pending"

    @pytest.mark.asyncio
    async def test_get_by_company(self, db_session: AsyncSession, company):
        """Test getting documents by company."""
        repo = DocumentRepository(db_session)
        
        # Create multiple documents
        await repo.create(
            company_id=company.id,
            title="Q1 Call",
            document_type="earnings_call",
        )
        await repo.create(
            company_id=company.id,
            title="Q2 Call",
            document_type="earnings_call",
        )
        
        # Get by company
        docs = await repo.get_by_company(company.id)
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_update_processing_status(self, db_session: AsyncSession, company):
        """Test updating document processing status."""
        repo = DocumentRepository(db_session)
        
        doc = await repo.create(
            company_id=company.id,
            title="Processing Test",
            document_type="annual_report",
        )
        
        # Update status
        updated = await repo.update(doc.id, processing_status="completed")
        
        assert updated.processing_status == "completed"

    @pytest.mark.asyncio
    async def test_filter_by_type(self, db_session: AsyncSession, company):
        """Test filtering documents by type."""
        repo = DocumentRepository(db_session)
        
        await repo.create(
            company_id=company.id,
            title="Earnings Call",
            document_type="earnings_call",
        )
        await repo.create(
            company_id=company.id,
            title="Annual Report",
            document_type="annual_report",
        )
        
        # Filter by type
        calls = await repo.get_by_type(company.id, "earnings_call")
        assert len(calls) == 1
        assert calls[0].document_type == "earnings_call"
