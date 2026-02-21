"""
Integration tests for API endpoints.

Uses httpx.AsyncClient against the real FastAPI app with a test DB session.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.asyncio
class TestAnalyzeEndpoint:
    async def test_analyze_missing_fields(self, client: AsyncClient):
        resp = await client.post("/api/v1/analyses/analyze", json={})
        assert resp.status_code == 422

    async def test_analyze_invalid_owner(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/analyses/analyze",
            json={"owner": "owner/invalid", "name": "repo"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestGetAnalysis:
    async def test_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/analyses/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
