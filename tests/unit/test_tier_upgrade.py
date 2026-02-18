"""
Tests for tier upgrade endpoint — D30 capability.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.multi_tenant.tier_upgrade import router, TIER_FEATURES, TIER_ORDER

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def mock_ctx_starter():
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-001"
    ctx.tier = "starter"
    ctx.user_id = "admin"
    ctx.shop_domain = "test-shop.myshopify.com"
    return ctx


@pytest.fixture
def mock_ctx_professional():
    ctx = MagicMock()
    ctx.tenant_id = "test-tenant-002"
    ctx.tier = "professional"
    ctx.user_id = "admin"
    ctx.shop_domain = "pro-shop.myshopify.com"
    return ctx


# ---------------------------------------------------------------------------
# Tests — Tier listing
# ---------------------------------------------------------------------------


class TestListTiers:
    """Tests for GET /api/billing/tiers."""

    @pytest.mark.asyncio
    async def test_list_tiers_starter(self, mock_ctx_starter):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/billing/tiers")

        assert resp.status_code == 200
        body = resp.json()
        assert body["current_tier"] == "starter"
        assert len(body["tiers"]) == 3

        # Starter should be current, Professional and Enterprise should be upgrades
        tier_map = {t["tier_id"]: t for t in body["tiers"]}
        assert tier_map["starter"]["is_current"] is True
        assert tier_map["professional"]["is_upgrade"] is True
        assert tier_map["enterprise"]["is_upgrade"] is True

    @pytest.mark.asyncio
    async def test_list_tiers_professional(self, mock_ctx_professional):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_professional

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/billing/tiers")

        body = resp.json()
        tier_map = {t["tier_id"]: t for t in body["tiers"]}
        assert tier_map["professional"]["is_current"] is True
        assert tier_map["starter"]["is_downgrade"] is True
        assert tier_map["enterprise"]["is_upgrade"] is True


class TestUpgradePreview:
    """Tests for GET /api/billing/upgrade/preview."""

    @pytest.mark.asyncio
    async def test_preview_upgrade(self, mock_ctx_starter):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/billing/upgrade/preview",
                params={"target_tier": "professional"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["direction"] == "upgrade"
        assert body["target_tier"] == "professional"
        assert body["difference_monthly"] > 0

    @pytest.mark.asyncio
    async def test_preview_downgrade(self, mock_ctx_professional):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_professional

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/billing/upgrade/preview",
                params={"target_tier": "starter"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["direction"] == "downgrade"
        assert body["difference_monthly"] < 0

    @pytest.mark.asyncio
    async def test_preview_same_tier_rejected(self, mock_ctx_starter):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/billing/upgrade/preview",
                params={"target_tier": "starter"},
            )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_preview_unknown_tier_rejected(self, mock_ctx_starter):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                "/api/billing/upgrade/preview",
                params={"target_tier": "platinum"},
            )

        assert resp.status_code == 400


class TestInitiateUpgrade:
    """Tests for POST /api/billing/upgrade."""

    @pytest.mark.asyncio
    async def test_upgrade_without_stripe_returns_error_message(self, mock_ctx_starter):
        """When Stripe catalog load fails, the endpoint should
        return a failure with an informative message."""
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        # Force catalog load to raise so the endpoint returns an error
        with patch(
            "src.integrations.stripe_catalog.load_catalog",
            side_effect=RuntimeError("Stripe not configured"),
        ):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/billing/upgrade",
                    json={"target_tier": "professional", "interval": "month"},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert body["message"]  # just verify we get an error message

    @pytest.mark.asyncio
    async def test_upgrade_same_tier_rejected(self, mock_ctx_starter):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_starter

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/billing/upgrade",
                json={"target_tier": "starter", "interval": "month"},
            )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_downgrade_returns_portal_message(self, mock_ctx_professional):
        app = _make_app()
        from src.multi_tenant.middleware import get_tenant_context
        app.dependency_overrides[get_tenant_context] = lambda: mock_ctx_professional

        # Provide a mock catalog so it doesn't try to load from disk
        mock_catalog = MagicMock()
        mock_tier = MagicMock()
        mock_tier.price_id_for_interval.return_value = "price_123"
        mock_catalog.get_tier.return_value = mock_tier

        # Downgrade path: the code loads catalog then checks direction.
        # Patch at the source so the lazy import inside the function picks it up.
        with patch.dict("sys.modules", {}):
            pass
        # Simplest approach: patch stripe_catalog.load_catalog at source
        with patch("src.integrations.stripe_catalog.load_catalog", return_value=mock_catalog):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/billing/upgrade",
                    json={"target_tier": "starter", "interval": "month"},
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "billing portal" in body["message"].lower() or "scheduled" in body["message"].lower()


class TestTierMetadata:
    """Tests for tier feature data consistency."""

    def test_all_tiers_have_features(self):
        for tier_id, info in TIER_FEATURES.items():
            assert info["label"], f"{tier_id} missing label"
            assert info["monthly_price"] > 0, f"{tier_id} missing monthly price"
            assert info["annual_price"] > 0, f"{tier_id} missing annual price"
            assert len(info["features"]) > 0, f"{tier_id} has no features"

    def test_tier_order_consistent(self):
        assert TIER_ORDER["starter"] < TIER_ORDER["professional"]
        assert TIER_ORDER["professional"] < TIER_ORDER["enterprise"]

    def test_annual_discount_applied(self):
        for tier_id, info in TIER_FEATURES.items():
            annual_monthly = info["annual_price"] / 12
            assert annual_monthly < info["monthly_price"], (
                f"{tier_id}: annual rate should be less than monthly"
            )
