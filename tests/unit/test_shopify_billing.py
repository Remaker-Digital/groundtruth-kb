"""
Tests for Shopify Billing API integration — src/integrations/shopify_billing.py.

Covers: _get_tier_pricing, _is_test_mode, create_subscription,
        confirm_subscription, record_shopify_usage, get_billing_status,
        subscribe_endpoint, confirm_endpoint, status_endpoint,
        _shop_subscriptions tracking, pricing catalog validation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.integrations.shopify_billing import (
    VALID_INTERVALS,
    VALID_TIERS,
    _get_tier_pricing,
    _is_test_mode,
    _shop_subscriptions,
    confirm_subscription,
    create_subscription,
    get_billing_status,
    record_shopify_usage,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture(autouse=True)
def _clear_shop_subscriptions():
    """Clear in-memory subscription tracking between tests."""
    _shop_subscriptions.clear()
    yield
    _shop_subscriptions.clear()


# ---------------------------------------------------------------------------
# Tests — Pricing catalog
# ---------------------------------------------------------------------------


class TestPricingCatalog:
    """Tests for pricing configuration and validation."""

    def test_valid_tiers(self):
        assert "starter" in VALID_TIERS
        assert "professional" in VALID_TIERS
        assert "enterprise" in VALID_TIERS

    def test_valid_intervals(self):
        assert "month" in VALID_INTERVALS
        assert "year" in VALID_INTERVALS

    def test_get_tier_pricing_valid(self):
        pricing = _get_tier_pricing("starter")
        assert pricing["monthly"] == Decimal("149.00")
        assert pricing["annual_total"] == Decimal("1490.00")
        assert pricing["overage_rate"] == Decimal("0.04")

    def test_get_tier_pricing_invalid(self):
        with pytest.raises(ValueError, match="Invalid tier"):
            _get_tier_pricing("imaginary_tier")

    def test_all_tiers_have_required_fields(self):
        required_fields = {
            "name", "monthly", "annual_total", "overage_rate",
            "included_conversations", "capped_amount",
        }
        for tier in VALID_TIERS:
            pricing = _get_tier_pricing(tier)
            for field in required_fields:
                assert field in pricing, f"Missing {field} in {tier}"

    def test_professional_higher_than_starter(self):
        starter = _get_tier_pricing("starter")
        pro = _get_tier_pricing("professional")
        assert pro["monthly"] > starter["monthly"]
        assert pro["included_conversations"] > starter["included_conversations"]

    def test_enterprise_highest(self):
        pro = _get_tier_pricing("professional")
        ent = _get_tier_pricing("enterprise")
        assert ent["monthly"] > pro["monthly"]
        assert ent["included_conversations"] > pro["included_conversations"]


# ---------------------------------------------------------------------------
# Tests — _is_test_mode
# ---------------------------------------------------------------------------


class TestIsTestMode:
    """Tests for _is_test_mode helper."""

    def test_default_is_test(self):
        with patch.dict("os.environ", {"SHOPIFY_BILLING_TEST": "true"}):
            assert _is_test_mode() is True

    def test_production_mode(self):
        with patch.dict("os.environ", {"SHOPIFY_BILLING_TEST": "false"}):
            assert _is_test_mode() is False


# ---------------------------------------------------------------------------
# Tests — create_subscription
# ---------------------------------------------------------------------------


class TestCreateSubscription:
    """Tests for create_subscription."""

    @pytest.mark.asyncio
    async def test_monthly_subscription(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "appSubscriptionCreate": {
                "appSubscription": {
                    "id": "gid://shopify/AppSubscription/123",
                    "name": "Agent Red Starter (Monthly)",
                    "status": "PENDING",
                },
                "confirmationUrl": "https://test.myshopify.com/admin/charges/confirm",
                "userErrors": [],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await create_subscription("test.myshopify.com", "starter", "month")

        assert result["confirmation_url"]
        assert result["tier"] == "starter"
        assert result["interval"] == "month"
        assert result["base_price"] == 149.0
        assert result["overage_cap"] == 500.0  # Capped amount for starter

        # Should track in _shop_subscriptions
        assert "test.myshopify.com" in _shop_subscriptions

    @pytest.mark.asyncio
    async def test_annual_subscription_no_usage(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "appSubscriptionCreate": {
                "appSubscription": {
                    "id": "gid://shopify/AppSubscription/456",
                    "name": "Agent Red Starter (Annual)",
                    "status": "PENDING",
                },
                "confirmationUrl": "https://test.myshopify.com/admin/charges/confirm",
                "userErrors": [],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await create_subscription("test.myshopify.com", "starter", "year")

        assert result["base_price"] == 1490.0
        assert result["overage_cap"] == 0.0  # Annual has no usage line item

    @pytest.mark.asyncio
    async def test_invalid_tier(self):
        with pytest.raises(ValueError, match="Invalid tier"):
            await create_subscription("test.myshopify.com", "invalid", "month")

    @pytest.mark.asyncio
    async def test_invalid_interval(self):
        with pytest.raises(ValueError, match="Invalid interval"):
            await create_subscription("test.myshopify.com", "starter", "weekly")

    @pytest.mark.asyncio
    async def test_graphql_user_errors(self):
        from src.integrations.shopify_client import ShopifyGraphQLError

        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "appSubscriptionCreate": {
                "appSubscription": {},
                "confirmationUrl": "",
                "userErrors": [
                    {"field": "lineItems", "message": "Invalid price amount"},
                ],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            with pytest.raises(ShopifyGraphQLError):
                await create_subscription("test.myshopify.com", "starter", "month")

    @pytest.mark.asyncio
    async def test_custom_return_url(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "appSubscriptionCreate": {
                "appSubscription": {
                    "id": "gid://shopify/AppSubscription/789",
                },
                "confirmationUrl": "https://test.myshopify.com/confirm",
                "userErrors": [],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await create_subscription(
                "test.myshopify.com", "starter", "month",
                return_url="https://example.com/callback",
            )

        # Verify the custom return URL was passed to the mutation
        call_args = mock_client.execute.call_args
        variables = call_args.args[1]
        assert variables["returnUrl"] == "https://example.com/callback"


# ---------------------------------------------------------------------------
# Tests — confirm_subscription
# ---------------------------------------------------------------------------


class TestConfirmSubscription:
    """Tests for confirm_subscription."""

    @pytest.mark.asyncio
    async def test_confirm_success(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "currentAppInstallation": {
                "activeSubscriptions": [
                    {
                        "id": "gid://shopify/AppSubscription/123",
                        "name": "Agent Red Starter (Monthly)",
                        "status": "ACTIVE",
                        "createdAt": "2026-01-01T00:00:00Z",
                        "currentPeriodEnd": "2026-02-01T00:00:00Z",
                        "lineItems": [
                            {
                                "id": "gid://line/1",
                                "plan": {
                                    "pricingDetails": {
                                        "__typename": "AppRecurringPricing",
                                        "price": {"amount": "149.00", "currencyCode": "USD"},
                                        "interval": "EVERY_30_DAYS",
                                    },
                                },
                            },
                            {
                                "id": "gid://line/2",
                                "plan": {
                                    "pricingDetails": {
                                        "__typename": "AppUsagePricing",
                                        "cappedAmount": {"amount": "500.00", "currencyCode": "USD"},
                                        "terms": "Overage billing...",
                                    },
                                },
                            },
                        ],
                    },
                ],
            },
        })

        # Pre-populate subscription info (as if create_subscription was called first)
        _shop_subscriptions["test.myshopify.com"] = {
            "subscription_id": None,
            "tier": "starter",
            "interval": "month",
        }

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client), \
             patch("src.integrations.shopify_billing.provision_tenant") as mock_prov, \
             patch("src.integrations.shopify_billing.activate_tenant") as mock_activate:
            tenant = MagicMock()
            tenant.tenant_id = "t-001"
            tenant.status.value = "active"
            mock_prov.return_value = tenant
            mock_activate.return_value = MagicMock(status=MagicMock(value="active"))

            result = await confirm_subscription("test.myshopify.com")

        assert result["status"] == "active"
        assert result["usage_line_item_id"] == "gid://line/2"
        assert result["tenant_id"] == "t-001"

    @pytest.mark.asyncio
    async def test_confirm_no_active_subscription(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "currentAppInstallation": {
                "activeSubscriptions": [],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await confirm_subscription("test.myshopify.com")

        assert result["status"] == "no_active_subscription"

    @pytest.mark.asyncio
    async def test_confirm_without_prior_creation(self):
        """Subscription confirmed without going through our create flow."""
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "currentAppInstallation": {
                "activeSubscriptions": [
                    {
                        "id": "gid://shopify/AppSubscription/999",
                        "name": "Unknown Plan",
                        "status": "ACTIVE",
                        "lineItems": [],
                    },
                ],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client), \
             patch("src.integrations.shopify_billing.provision_tenant") as mock_prov, \
             patch("src.integrations.shopify_billing.activate_tenant") as mock_activate:
            tenant = MagicMock()
            tenant.tenant_id = "t-new"
            tenant.status.value = "active"
            mock_prov.return_value = tenant
            mock_activate.return_value = None

            result = await confirm_subscription("unknown-shop.myshopify.com")

        # Should still create a shop subscription entry
        assert "unknown-shop.myshopify.com" in _shop_subscriptions


# ---------------------------------------------------------------------------
# Tests — record_shopify_usage
# ---------------------------------------------------------------------------


class TestRecordShopifyUsage:
    """Tests for record_shopify_usage."""

    @pytest.mark.asyncio
    async def test_record_usage_success(self):
        _shop_subscriptions["test.myshopify.com"] = {
            "subscription_id": "gid://sub/1",
            "usage_line_item_id": "gid://line/2",
            "tier": "starter",
            "pricing": {
                "overage_rate": Decimal("0.04"),
                "included_conversations": 1000,
            },
        }

        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "appUsageRecordCreate": {
                "appUsageRecord": {
                    "id": "gid://record/1",
                    "createdAt": "2026-01-15T00:00:00Z",
                },
                "userErrors": [],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await record_shopify_usage(
                "test.myshopify.com", overage_count=10, idempotency_key="key_001",
            )

        assert result["success"] is True
        assert result["amount"] == 0.40  # 10 * $0.04
        assert result["record_id"] == "gid://record/1"

    @pytest.mark.asyncio
    async def test_record_usage_no_subscription(self):
        with pytest.raises(ValueError, match="No subscription found"):
            await record_shopify_usage(
                "unknown.myshopify.com", overage_count=5, idempotency_key="key_002",
            )

    @pytest.mark.asyncio
    async def test_record_usage_no_line_item(self):
        _shop_subscriptions["test.myshopify.com"] = {
            "subscription_id": "gid://sub/1",
            "usage_line_item_id": None,  # Annual plan — no usage line
        }

        with pytest.raises(ValueError, match="No usage line item"):
            await record_shopify_usage(
                "test.myshopify.com", overage_count=5, idempotency_key="key_003",
            )

    @pytest.mark.asyncio
    async def test_record_usage_graphql_errors(self):
        _shop_subscriptions["test.myshopify.com"] = {
            "subscription_id": "gid://sub/1",
            "usage_line_item_id": "gid://line/2",
            "tier": "starter",
            "pricing": {"overage_rate": Decimal("0.04"), "included_conversations": 1000},
        }

        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "appUsageRecordCreate": {
                "appUsageRecord": None,
                "userErrors": [
                    {"field": "price", "message": "Exceeds capped amount"},
                ],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await record_shopify_usage(
                "test.myshopify.com", overage_count=100000, idempotency_key="key_004",
            )

        assert result["success"] is False
        assert "errors" in result


# ---------------------------------------------------------------------------
# Tests — get_billing_status
# ---------------------------------------------------------------------------


class TestGetBillingStatus:
    """Tests for get_billing_status."""

    @pytest.mark.asyncio
    async def test_active_subscription(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "currentAppInstallation": {
                "activeSubscriptions": [
                    {
                        "id": "gid://sub/1",
                        "name": "Agent Red Starter (Monthly)",
                        "status": "ACTIVE",
                        "createdAt": "2026-01-01",
                        "currentPeriodEnd": "2026-02-01",
                        "lineItems": [
                            {
                                "id": "gid://line/1",
                                "plan": {
                                    "pricingDetails": {
                                        "__typename": "AppRecurringPricing",
                                    },
                                },
                            },
                        ],
                    },
                ],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await get_billing_status("test.myshopify.com")

        assert result["has_active_subscription"] is True
        assert result["subscription_name"] == "Agent Red Starter (Monthly)"
        assert result["status"] == "ACTIVE"

    @pytest.mark.asyncio
    async def test_no_subscription(self):
        mock_client = AsyncMock()
        mock_client.execute = AsyncMock(return_value={
            "currentAppInstallation": {
                "activeSubscriptions": [],
            },
        })

        with patch("src.integrations.shopify_billing.get_shopify_client", return_value=mock_client):
            result = await get_billing_status("test.myshopify.com")

        assert result["has_active_subscription"] is False


# ---------------------------------------------------------------------------
# Tests — HTTP Endpoints
# ---------------------------------------------------------------------------


class TestSubscribeEndpoint:
    """Tests for POST /api/shopify/billing/subscribe."""

    @pytest.mark.asyncio
    async def test_subscribe_success(self):
        app = _make_app()

        with patch("src.integrations.shopify_billing.create_subscription") as mock_create:
            mock_create.return_value = {
                "confirmation_url": "https://shopify.com/confirm",
                "subscription_name": "Agent Red Starter (Monthly)",
                "tier": "starter",
                "interval": "month",
                "base_price": 149.0,
                "overage_cap": 500.0,
            }

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/shopify/billing/subscribe",
                    json={
                        "tier": "starter",
                        "interval": "month",
                        "shop_domain": "test.myshopify.com",
                    },
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["confirmation_url"] == "https://shopify.com/confirm"
        assert body["tier"] == "starter"

    @pytest.mark.asyncio
    async def test_subscribe_invalid_tier(self):
        app = _make_app()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/shopify/billing/subscribe",
                json={
                    "tier": "platinum",
                    "interval": "month",
                    "shop_domain": "test.myshopify.com",
                },
            )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_subscribe_invalid_interval(self):
        app = _make_app()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/api/shopify/billing/subscribe",
                json={
                    "tier": "starter",
                    "interval": "weekly",
                    "shop_domain": "test.myshopify.com",
                },
            )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_subscribe_shopify_api_error(self):
        from src.integrations.shopify_client import ShopifyAPIError

        app = _make_app()

        with patch("src.integrations.shopify_billing.create_subscription") as mock_create:
            mock_create.side_effect = ShopifyAPIError("Connection failed")

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/shopify/billing/subscribe",
                    json={
                        "tier": "starter",
                        "interval": "month",
                        "shop_domain": "test.myshopify.com",
                    },
                )

        assert resp.status_code == 502


class TestConfirmEndpoint:
    """Tests for GET /api/shopify/billing/confirm."""

    @pytest.mark.asyncio
    async def test_confirm_success(self):
        app = _make_app()

        with patch("src.integrations.shopify_billing.confirm_subscription") as mock_confirm:
            mock_confirm.return_value = {
                "status": "active",
                "subscription_name": "Agent Red Starter (Monthly)",
            }

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(
                    "/api/shopify/billing/confirm?shop=test.myshopify.com",
                )

        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    @pytest.mark.asyncio
    async def test_confirm_missing_shop(self):
        app = _make_app()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/shopify/billing/confirm")

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_confirm_shopify_error(self):
        from src.integrations.shopify_client import ShopifyAPIError

        app = _make_app()

        with patch("src.integrations.shopify_billing.confirm_subscription") as mock_confirm:
            mock_confirm.side_effect = ShopifyAPIError("API down")

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(
                    "/api/shopify/billing/confirm?shop=test.myshopify.com",
                )

        assert resp.status_code == 502


class TestStatusEndpoint:
    """Tests for GET /api/shopify/billing/status."""

    @pytest.mark.asyncio
    async def test_status_success(self):
        app = _make_app()

        with patch("src.integrations.shopify_billing.get_billing_status") as mock_status:
            mock_status.return_value = {
                "shop_domain": "test.myshopify.com",
                "has_active_subscription": True,
                "subscription_name": "Agent Red Starter (Monthly)",
                "status": "ACTIVE",
                "created_at": "2026-01-01",
                "current_period_end": "2026-02-01",
            }

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(
                    "/api/shopify/billing/status?shop=test.myshopify.com",
                )

        assert resp.status_code == 200
        body = resp.json()
        assert body["has_active_subscription"] is True

    @pytest.mark.asyncio
    async def test_status_shopify_error(self):
        from src.integrations.shopify_client import ShopifyAPIError

        app = _make_app()

        with patch("src.integrations.shopify_billing.get_billing_status") as mock_status:
            mock_status.side_effect = ShopifyAPIError("API error")

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get(
                    "/api/shopify/billing/status?shop=test.myshopify.com",
                )

        assert resp.status_code == 502
