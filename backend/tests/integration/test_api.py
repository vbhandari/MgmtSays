"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test basic health check endpoint."""
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_detailed(self, client: AsyncClient):
        """Test detailed health check."""
        response = await client.get("/api/v1/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "vector_store" in data


@pytest.mark.integration
class TestCompanyEndpoints:
    """Tests for company API endpoints."""

    @pytest.mark.asyncio
    async def test_create_company(self, client: AsyncClient, sample_company_data):
        """Test creating a company via API."""
        response = await client.post(
            "/api/v1/companies",
            json=sample_company_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_company_data["name"]
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_companies(self, client: AsyncClient):
        """Test listing companies."""
        response = await client.get("/api/v1/companies")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_company_not_found(self, client: AsyncClient):
        """Test getting non-existent company returns 404."""
        response = await client.get("/api/v1/companies/nonexistent-id")

        assert response.status_code == 404


@pytest.mark.integration
class TestDocumentEndpoints:
    """Tests for document API endpoints."""

    @pytest.mark.asyncio
    async def test_upload_document_validation(self, client: AsyncClient):
        """Test document upload validation."""
        # Missing required fields should fail
        response = await client.post(
            "/api/v1/documents",
            data={"company_id": "123"},
            # No file attached
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(self, client: AsyncClient):
        """Test that invalid file types are rejected."""
        response = await client.post(
            "/api/v1/documents",
            data={"company_id": "test-company"},
            files={"file": ("test.exe", b"binary content", "application/octet-stream")},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_list_documents_by_company(self, client: AsyncClient):
        """Test listing documents for a company."""
        response = await client.get(
            "/api/v1/documents",
            params={"company_id": "test-company"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_documents_with_pagination(self, client: AsyncClient):
        """Test document listing with pagination."""
        response = await client.get(
            "/api/v1/documents",
            params={"page": 1, "page_size": 10},
        )

        assert response.status_code == 200
        data = response.json()
        # Check pagination response structure
        if isinstance(data, dict):
            assert "page" in data or "items" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, client: AsyncClient):
        """Test getting a non-existent document returns 404."""
        response = await client.get("/api/v1/documents/nonexistent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_document(self, client: AsyncClient):
        """Test deleting a non-existent document returns 404."""
        response = await client.delete("/api/v1/documents/nonexistent-id")

        assert response.status_code == 404


@pytest.mark.integration
class TestAnalysisEndpoints:
    """Tests for analysis API endpoints."""

    @pytest.mark.asyncio
    async def test_search_requires_query(self, client: AsyncClient):
        """Test that search requires a query."""
        response = await client.post(
            "/api/v1/analysis/search",
            json={"company_id": "123"},
            # No query provided
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_initiatives_endpoint(self, client: AsyncClient):
        """Test initiatives listing endpoint."""
        response = await client.get(
            "/api/v1/analysis/initiatives",
            params={"company_id": "test-company"},
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_insights_by_company(self, client: AsyncClient):
        """Test getting insights by company."""
        response = await client.get(
            "/api/v1/analysis/insights",
            params={"company_id": "test-company"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
