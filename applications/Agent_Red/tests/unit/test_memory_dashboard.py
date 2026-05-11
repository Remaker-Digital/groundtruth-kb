"""
Tests for persistent memory dashboard API — WI#139 capability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.multi_tenant.memory_dashboard import (
    router,
    configure_memory_dashboard,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.tier = "professional"
    ctx.user_id = "admin"
    return ctx


def _make_memory_repo(vectors: list | None = None, query_results: dict | None = None):
    """Create a mock memory repository."""
    repo = MagicMock()

    if query_results is None:
        query_results = {}

    async def mock_query(tenant_id, query_text, parameters=None):
        # Return different results based on query pattern
        # GROUP BY must be checked before COUNT(1) since GROUP BY queries also contain COUNT(1)
        if "GROUP BY c.customer_id" in query_text:
            from collections import defaultdict
            by_cust: dict = defaultdict(list)
            for v in (vectors or []):
                by_cust[v.get("customer_id", "")].append(v)
            return [
                {
                    "customer_id": cid,
                    "vector_count": len(vecs),
                    "conv_count": len({v.get("conversation_id") for v in vecs}),
                    "latest_date": max(
                        (v.get("conversation_date", "") for v in vecs),
                        default=None,
                    ),
                }
                for cid, vecs in by_cust.items()
            ]
        if "COUNT(1)" in query_text:
            return [len(vectors or [])]
        if "DISTINCT VALUE c.customer_id" in query_text:
            return list({v.get("customer_id", "") for v in (vectors or [])})
        if "DISTINCT VALUE c.conversation_id" in query_text:
            return list({v.get("conversation_id", "") for v in (vectors or [])})
        if "MIN(c.conversation_date)" in query_text:
            dates = [v.get("conversation_date") for v in (vectors or []) if v.get("conversation_date")]
            return [min(dates)] if dates else [None]
        if "MAX(c.conversation_date)" in query_text:
            dates = [v.get("conversation_date") for v in (vectors or []) if v.get("conversation_date")]
            return [max(dates)] if dates else [None]
        if "c.customer_id = @cid" in query_text:
            cid = None
            for p in (parameters or []):
                if p["name"] == "@cid":
                    cid = p["value"]
            return [v for v in (vectors or []) if v.get("customer_id") == cid]
        return vectors or []

    repo.query = AsyncMock(side_effect=mock_query)
    repo.delete_by_customer = AsyncMock(return_value=3)
    return repo


def _make_prefs_repo(memory_enabled: bool = True):
    """Create a mock preferences repository."""
    repo = MagicMock()
    repo.get_active = AsyncMock(return_value={"memory_enabled": memory_enabled})
    return repo


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_VECTORS = [
    {
        "id": "vec-001",
        "customer_id": "cust-aaa",
        "conversation_id": "conv-111",
        "chunk_index": 0,
        "chunk_text": "Customer asked about return policy for shoes.",
        "conversation_date": "2026-01-15T10:00:00Z",
        "topics": ["returns", "shoes"],
    },
    {
        "id": "vec-002",
        "customer_id": "cust-aaa",
        "conversation_id": "conv-111",
        "chunk_index": 1,
        "chunk_text": "Agent explained 30-day return window.",
        "conversation_date": "2026-01-15T10:00:00Z",
        "topics": ["returns"],
    },
    {
        "id": "vec-003",
        "customer_id": "cust-bbb",
        "conversation_id": "conv-222",
        "chunk_index": 0,
        "chunk_text": "Customer inquired about shipping times.",
        "conversation_date": "2026-02-01T14:00:00Z",
        "topics": ["shipping"],
    },
]

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMemoryStats:
    """Tests for GET /api/admin/memory/stats."""

    @pytest.mark.asyncio
    async def test_stats_with_data(self, mock_ctx):
        mem_repo = _make_memory_repo(SAMPLE_VECTORS)
        prefs_repo = _make_prefs_repo(memory_enabled=True)
        configure_memory_dashboard(mem_repo, prefs_repo)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/memory/stats")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total_vectors"] == 3
        assert body["total_customers"] == 2
        assert body["total_conversations_indexed"] == 2
        assert body["memory_enabled"] is True

    @pytest.mark.asyncio
    async def test_stats_memory_disabled(self, mock_ctx):
        mem_repo = _make_memory_repo([])
        prefs_repo = _make_prefs_repo(memory_enabled=False)
        configure_memory_dashboard(mem_repo, prefs_repo)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/memory/stats")

        assert resp.status_code == 200
        body = resp.json()
        assert body["memory_enabled"] is False

    @pytest.mark.asyncio
    async def test_stats_no_repo(self, mock_ctx):
        configure_memory_dashboard(None, None)
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/memory/stats")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total_vectors"] == 0
        assert body["memory_enabled"] is False


class TestMemoryCustomers:
    """Tests for GET /api/admin/memory/customers."""

    @pytest.mark.asyncio
    async def test_list_customers(self, mock_ctx):
        mem_repo = _make_memory_repo(SAMPLE_VECTORS)
        configure_memory_dashboard(mem_repo)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/memory/customers")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 2
        cust_ids = {c["customer_id"] for c in body["customers"]}
        assert "cust-aaa" in cust_ids
        assert "cust-bbb" in cust_ids


class TestCustomerMemoryDetail:
    """Tests for GET /api/admin/memory/customer/{cid}."""

    @pytest.mark.asyncio
    async def test_get_customer_vectors(self, mock_ctx):
        mem_repo = _make_memory_repo(SAMPLE_VECTORS)
        configure_memory_dashboard(mem_repo)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/memory/customer/cust-aaa")

        assert resp.status_code == 200
        body = resp.json()
        assert body["customer_id"] == "cust-aaa"
        assert body["total"] == 2  # cust-aaa has 2 vectors

    @pytest.mark.asyncio
    async def test_get_unknown_customer_returns_empty(self, mock_ctx):
        mem_repo = _make_memory_repo(SAMPLE_VECTORS)
        configure_memory_dashboard(mem_repo)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/admin/memory/customer/cust-zzz")

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0


class TestDeleteCustomerMemory:
    """Tests for DELETE /api/admin/memory/customer/{cid}."""

    @pytest.mark.asyncio
    async def test_delete_customer_memory(self, mock_ctx):
        mem_repo = _make_memory_repo(SAMPLE_VECTORS)
        configure_memory_dashboard(mem_repo)

        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.delete("/api/admin/memory/customer/cust-aaa")

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["vectors_deleted"] == 3
        mem_repo.delete_by_customer.assert_called_once_with("test-tenant-001", "cust-aaa")

    @pytest.mark.asyncio
    async def test_delete_without_repo_returns_503(self, mock_ctx):
        configure_memory_dashboard(None)
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.delete("/api/admin/memory/customer/cust-aaa")

        assert resp.status_code == 503
