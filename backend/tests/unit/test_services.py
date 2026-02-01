"""Unit tests for services."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from src.services.company_service import CompanyService
from src.services.document_service import DocumentService


class TestCompanyService:
    """Tests for CompanyService."""

    @pytest.fixture
    def mock_repo(self):
        repo = MagicMock()
        repo.create = AsyncMock()
        repo.get = AsyncMock()
        repo.get_by_ticker = AsyncMock()
        repo.list_all = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        return CompanyService(company_repo=mock_repo)

    @pytest.mark.asyncio
    async def test_create_company(self, service, mock_repo, sample_company_data):
        """Test creating a company."""
        mock_repo.create.return_value = MagicMock(
            id="company_123",
            **sample_company_data,
        )

        result = await service.create_company(
            name=sample_company_data["name"],
            ticker=sample_company_data["ticker"],
            industry=sample_company_data["industry"],
        )

        mock_repo.create.assert_called_once()
        assert result.name == sample_company_data["name"]

    @pytest.mark.asyncio
    async def test_get_company_by_id(self, service, mock_repo):
        """Test getting company by ID."""
        mock_repo.get.return_value = MagicMock(id="company_123", name="Test Co")

        result = await service.get_company("company_123")

        mock_repo.get.assert_called_once_with("company_123")
        assert result.id == "company_123"

    @pytest.mark.asyncio
    async def test_get_company_not_found(self, service, mock_repo):
        """Test getting non-existent company."""
        mock_repo.get.return_value = None

        result = await service.get_company("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_companies(self, service, mock_repo):
        """Test listing companies."""
        mock_repo.list_all.return_value = [
            MagicMock(id="1", name="Company A"),
            MagicMock(id="2", name="Company B"),
        ]

        result = await service.list_companies()

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_by_ticker(self, service, mock_repo):
        """Test searching by ticker."""
        mock_repo.get_by_ticker.return_value = MagicMock(
            id="123",
            ticker="AAPL",
            name="Apple Inc.",
        )

        result = await service.get_by_ticker("AAPL")

        mock_repo.get_by_ticker.assert_called_once_with("AAPL")
        assert result.ticker == "AAPL"


class TestDocumentService:
    """Tests for DocumentService."""

    @pytest.fixture
    def mock_doc_repo(self):
        repo = MagicMock()
        repo.create = AsyncMock()
        repo.get = AsyncMock()
        repo.get_by_company = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo

    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.save = AsyncMock(return_value="path/to/file.pdf")
        storage.read = AsyncMock(return_value=b"file content")
        storage.delete = AsyncMock(return_value=True)
        return storage

    @pytest.fixture
    def service(self, mock_doc_repo, mock_storage):
        return DocumentService(
            document_repo=mock_doc_repo,
            storage=mock_storage,
        )

    @pytest.mark.asyncio
    async def test_upload_document(self, service, mock_doc_repo, mock_storage):
        """Test uploading a document."""
        mock_doc_repo.create.return_value = MagicMock(
            id="doc_123",
            title="Test Doc",
            processing_status="pending",
        )

        result = await service.upload_document(
            company_id="company_123",
            title="Test Doc",
            document_type="earnings_call",
            content=b"PDF content",
            filename="q4_call.pdf",
        )

        mock_storage.save.assert_called_once()
        mock_doc_repo.create.assert_called_once()
        assert result.processing_status == "pending"

    @pytest.mark.asyncio
    async def test_get_document(self, service, mock_doc_repo):
        """Test getting a document."""
        mock_doc_repo.get.return_value = MagicMock(
            id="doc_123",
            title="Test Document",
        )

        result = await service.get_document("doc_123")

        assert result.id == "doc_123"

    @pytest.mark.asyncio
    async def test_list_company_documents(self, service, mock_doc_repo):
        """Test listing documents for a company."""
        mock_doc_repo.get_by_company.return_value = [
            MagicMock(id="1", title="Q1 Call"),
            MagicMock(id="2", title="Q2 Call"),
        ]

        result = await service.get_company_documents("company_123")

        mock_doc_repo.get_by_company.assert_called_once_with("company_123")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_delete_document(self, service, mock_doc_repo, mock_storage):
        """Test deleting a document."""
        mock_doc_repo.get.return_value = MagicMock(
            id="doc_123",
            file_path="path/to/file.pdf",
        )
        mock_doc_repo.delete.return_value = True

        result = await service.delete_document("doc_123")

        mock_storage.delete.assert_called_once_with("path/to/file.pdf")
        mock_doc_repo.delete.assert_called_once_with("doc_123")
        assert result is True
