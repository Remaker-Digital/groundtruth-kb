# tests/test_host/test_api.py — Test Host API endpoint tests
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

"""
Tests for test_host.main — FastAPI endpoints for triggering, monitoring,
and cancelling test runs. Uses httpx TestClient for in-process testing.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def _patch_cosmos():
    """Patch CosmosClient to avoid real Azure calls."""
    with patch("test_host.cosmos_writer.CosmosClient") as mock_client:
        container = MagicMock()
        mock_client.return_value.get_database_client.return_value \
            .get_container_client.return_value = container
        yield container


@pytest.fixture
def _cosmos_env(monkeypatch):
    """Set Cosmos env vars for test host."""
    monkeypatch.setenv("COSMOS_DB_ENDPOINT", "https://mock.documents.azure.com:443/")
    monkeypatch.setenv("COSMOS_DB_KEY", "mock-key-for-testing")
    monkeypatch.setenv("COSMOS_DB_DATABASE", "test-db")


@pytest.fixture
async def client(_patch_cosmos, _cosmos_env):
    """Async HTTP client for test host app."""
    # Reset module-level state between tests
    import test_host.main as app_module
    app_module._active_runner = None
    app_module._active_task = None

    async with AsyncClient(
        transport=ASGITransport(app=app_module.app),
        base_url="http://test",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    """Test host liveness probe."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_has_status(self, client):
        data = (await client.get("/health")).json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_has_service_name(self, client):
        data = (await client.get("/health")).json()
        assert data["service"] == "test-host"

    @pytest.mark.asyncio
    async def test_health_has_timestamp(self, client):
        data = (await client.get("/health")).json()
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_health_no_active_run(self, client):
        data = (await client.get("/health")).json()
        assert data["active_run"] is None


# ---------------------------------------------------------------------------
# GET /suites
# ---------------------------------------------------------------------------

class TestSuitesEndpoint:
    """Suite listing endpoint."""

    @pytest.mark.asyncio
    async def test_suites_returns_200(self, client):
        resp = await client.get("/suites")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_suites_returns_list(self, client):
        data = (await client.get("/suites")).json()
        assert "suites" in data
        assert isinstance(data["suites"], list)

    @pytest.mark.asyncio
    async def test_suites_count(self, client):
        data = (await client.get("/suites")).json()
        assert len(data["suites"]) >= 12  # Individual + composite

    @pytest.mark.asyncio
    async def test_suites_each_has_name(self, client):
        data = (await client.get("/suites")).json()
        for s in data["suites"]:
            assert "name" in s
            assert s["name"]  # Non-empty


# ---------------------------------------------------------------------------
# POST /run
# ---------------------------------------------------------------------------

class TestRunEndpoint:
    """Test run trigger endpoint."""

    @pytest.mark.asyncio
    async def test_run_returns_202(self, client):
        resp = await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })
        assert resp.status_code == 202

    @pytest.mark.asyncio
    async def test_run_returns_run_id(self, client):
        data = (await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })).json()
        assert "run_id" in data
        assert data["run_id"].startswith("run-")

    @pytest.mark.asyncio
    async def test_run_custom_run_id(self, client):
        data = (await client.post("/run", json={
            "run_id": "custom-run-42",
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })).json()
        assert data["run_id"] == "custom-run-42"

    @pytest.mark.asyncio
    async def test_run_unknown_suite_returns_400(self, client):
        resp = await client.post("/run", json={
            "suite": "nonexistent",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })
        assert resp.status_code == 400
        assert "Unknown suite" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_run_without_cosmos_returns_500(self, client, monkeypatch):
        monkeypatch.delenv("COSMOS_DB_ENDPOINT", raising=False)
        monkeypatch.delenv("COSMOS_DB_KEY", raising=False)
        resp = await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })
        assert resp.status_code == 500

    @pytest.mark.asyncio
    async def test_concurrent_run_returns_409(self, client):
        """Only one run at a time."""
        # First run should succeed
        resp1 = await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })
        assert resp1.status_code == 202

        # Second run should be rejected
        resp2 = await client.post("/run", json={
            "suite": "unit",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })
        assert resp2.status_code == 409


# ---------------------------------------------------------------------------
# GET /status/{run_id}
# ---------------------------------------------------------------------------

class TestStatusEndpoint:
    """Status polling endpoint."""

    @pytest.mark.asyncio
    async def test_status_unknown_run_returns_404(self, client):
        resp = await client.get("/status/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_status_after_trigger(self, client):
        data = (await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })).json()
        run_id = data["run_id"]

        resp = await client.get(f"/status/{run_id}")
        assert resp.status_code == 200
        status = resp.json()
        assert status["run_id"] == run_id
        assert status["suite"] == "property"
        assert "status" in status

    @pytest.mark.asyncio
    async def test_status_has_counter_fields(self, client):
        data = (await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })).json()

        status = (await client.get(f"/status/{data['run_id']}")).json()
        for field in ["total_tests", "completed", "passed", "failed", "skipped", "errored"]:
            assert field in status, f"Missing field: {field}"
            assert isinstance(status[field], int)


# ---------------------------------------------------------------------------
# POST /cancel/{run_id}
# ---------------------------------------------------------------------------

class TestCancelEndpoint:
    """Run cancellation endpoint."""

    @pytest.mark.asyncio
    async def test_cancel_unknown_run_returns_404(self, client):
        resp = await client.post("/cancel/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_active_run(self, client):
        data = (await client.post("/run", json={
            "suite": "property",
            "environment": "staging",
            "target_url": "https://staging.example.com",
        })).json()

        resp = await client.post(f"/cancel/{data['run_id']}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"
