"""
Tests for add-on checkout endpoint — WI#138 capability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.multi_tenant.addon_checkout import router, ADDON_META

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
    ctx.shop_domain = "test.myshopify.com"
    return ctx


@pytest.fixture
def mock_ctx_starter():
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-002"
    ctx.tier = "starter"
    ctx.user_id = "admin"
    ctx.shop_domain = None
    return ctx


# ---------------------------------------------------------------------------
# Tests — Add-on listing
# ---------------------------------------------------------------------------


class TestListAddons:
    """Tests for GET /api/billing/addons."""

    @pytest.mark.asyncio
    async def test_list_addons(self, mock_ctx):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/billing/addons")

        assert resp.status_code == 200
        body = resp.json()
        assert body["tenant_tier"] == "professional"
        assert body["total"] == len(ADDON_META)
        assert all(a["addon_id"] in ADDON_META for a in body["addons"])

    @pytest.mark.asyncio
    async def test_list_addons_has_prices(self, mock_ctx):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/billing/addons")

        body = resp.json()
        for addon in body["addons"]:
            assert addon["price_monthly"] > 0
            assert addon["name"]
            assert addon["description"]


class TestAddonCheckout:
    """Tests for POST /api/billing/addons/checkout."""

    @pytest.mark.asyncio
    async def test_checkout_unknown_addon_rejected(self, mock_ctx):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/billing/addons/checkout",
                json={"addon_id": "nonexistent_addon"},
            )

        assert resp.status_code == 400
        assert "Unknown add-on" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_checkout_without_catalog_returns_message(self, mock_ctx):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx

        with patch(
            "src.multi_tenant.addon_checkout.load_catalog",
            side_effect=FileNotFoundError("no catalog"),
            create=True,
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/billing/addons/checkout",
                    json={"addon_id": "advanced_analytics"},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert "not configured" in body["message"]

    @pytest.mark.asyncio
    async def test_checkout_tier_gate_enforced(self, mock_ctx_starter):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        # Mock catalog that says the addon is only available on "professional"
        mock_addon = MagicMock()
        mock_addon.available_on = ["professional", "enterprise"]
        mock_addon.price_id = "price_123"
        mock_catalog = MagicMock()
        mock_catalog.get_addon.return_value = mock_addon

        # Patch at source — the lazy import inside checkout_addon reads from
        # src.integrations.stripe_catalog.load_catalog
        with patch("src.integrations.stripe_catalog.load_catalog", return_value=mock_catalog):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/billing/addons/checkout",
                    json={"addon_id": "advanced_analytics"},
                )

        assert resp.status_code == 403
        assert "not available" in resp.json()["detail"]


class TestAddonMetadata:
    """Tests for add-on metadata consistency."""

    def test_all_addons_have_metadata(self):
        for addon_id, meta in ADDON_META.items():
            assert meta["name"], f"{addon_id} missing name"
            assert meta["description"], f"{addon_id} missing description"
            assert meta["price_monthly"] > 0, f"{addon_id} missing price"

    def test_addon_count(self):
        assert len(ADDON_META) >= 4, "Expected at least 4 add-ons"
