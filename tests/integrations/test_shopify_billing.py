"""Unit tests for Shopify Billing API integration (SHB-01 to SHB-15).

Covers:
    - shopify_billing.py: create_subscription, confirm_subscription,
      record_shopify_usage, get_billing_status, _get_tier_pricing,
      _is_test_mode, Decimal arithmetic, tier/interval validation

Run:
    pytest tests/integrations/test_shopify_billing.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.shopify_billing import (
    VALID_INTERVALS,
    VALID_TIERS,
    _INTERVAL_MAP,
    _auto_enable_shopify_mcp,
    _get_tier_pricing,
    _is_test_mode,
    _shop_subscriptions,
    confirm_subscription,
    create_subscription,
    get_billing_status,
    record_shopify_usage,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_shop_subscriptions():
    """Reset in-memory subscription store before and after each test."""
    _shop_subscriptions.clear()
    yield
    _shop_subscriptions.clear()


@pytest.fixture()
def mock_shopify_client():
    """Return a mock ShopifyGraphQLClient with an async execute method."""
    client = MagicMock()
    client.execute = AsyncMock()
    return client


@pytest.fixture()
def _patch_shopify_client(mock_shopify_client):
    """Patch get_shopify_client() to return the mock client."""
    with patch(
        "src.integrations.shopify_billing.get_shopify_client",
        return_value=mock_shopify_client,
    ):
        yield mock_shopify_client


@pytest.fixture()
def _patch_provisioning():
    """Patch provision_tenant and activate_tenant in shopify_billing module."""
    tenant_record = MagicMock()
    tenant_record.tenant_id = "tenant-test-001"
    tenant_record.status = MagicMock()
    tenant_record.status.value = "active"

    with patch(
        "src.integrations.shopify_billing.provision_tenant",
        return_value=tenant_record,
    ) as mock_provision, patch(
        "src.integrations.shopify_billing.activate_tenant",
        return_value=tenant_record,
    ) as mock_activate:
        yield mock_provision, mock_activate


def _graphql_subscription_response(
    sub_id: str = "gid://shopify/AppSubscription/12345",
    name: str = "Agent Red Starter (Monthly)",
    status: str = "PENDING",
    confirmation_url: str = "https://example.myshopify.com/admin/charges/confirm",
) -> dict:
    """Build a mock appSubscriptionCreate GraphQL response."""
    return {
        "appSubscriptionCreate": {
            "appSubscription": {
                "id": sub_id,
                "name": name,
                "status": status,
                "createdAt": "2026-02-01T00:00:00Z",
                "currentPeriodEnd": "2026-03-01T00:00:00Z",
            },
            "confirmationUrl": confirmation_url,
            "userErrors": [],
        },
    }


def _graphql_active_subscription_response(
    sub_id: str = "gid://shopify/AppSubscription/12345",
    name: str = "Agent Red Starter (Monthly)",
    usage_line_item_id: str = "gid://shopify/AppSubscriptionLineItem/99",
) -> dict:
    """Build a mock activeSubscriptions query response with a usage line item."""
    return {
        "currentAppInstallation": {
            "activeSubscriptions": [
                {
                    "id": sub_id,
                    "name": name,
                    "status": "ACTIVE",
                    "createdAt": "2026-02-01T00:00:00Z",
                    "currentPeriodEnd": "2026-03-01T00:00:00Z",
                    "lineItems": [
                        {
                            "id": "gid://shopify/AppSubscriptionLineItem/1",
                            "plan": {
                                "pricingDetails": {
                                    "__typename": "AppRecurringPricing",
                                    "price": {"amount": "149.00", "currencyCode": "USD"},
                                    "interval": "EVERY_30_DAYS",
                                },
                            },
                        },
                        {
                            "id": usage_line_item_id,
                            "plan": {
                                "pricingDetails": {
                                    "__typename": "AppUsagePricing",
                                    "cappedAmount": {"amount": "500.00", "currencyCode": "USD"},
                                    "terms": "Overage billing terms",
                                },
                            },
                        },
                    ],
                },
            ],
        },
    }


def _graphql_usage_record_response(record_id: str = "gid://shopify/AppUsageRecord/777") -> dict:
    """Build a mock appUsageRecordCreate GraphQL response."""
    return {
        "appUsageRecordCreate": {
            "appUsageRecord": {
                "id": record_id,
                "createdAt": "2026-02-01T12:00:00Z",
            },
            "userErrors": [],
        },
    }


# ===================================================================
# SHB-01: create_subscription Starter monthly
# ===================================================================


class TestCreateSubscriptionStarterMonthly:
    """SHB-01: Create a Starter monthly subscription."""

    @pytest.mark.asyncio
    async def test_starter_monthly_returns_correct_fields(self, _patch_shopify_client):
        """Starter monthly subscription returns expected base price and overage cap."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response(
            name="Agent Red Starter (Monthly)",
        )

        result = await create_subscription(
            shop_domain="test-store.myshopify.com",
            tier="starter",
            interval="month",
        )

        assert result["tier"] == "starter"
        assert result["interval"] == "month"
        assert result["base_price"] == 149.00
        assert result["overage_cap"] == 500.00
        assert result["subscription_name"] == "Agent Red Starter (Monthly)"
        assert result["confirmation_url"] is not None

    @pytest.mark.asyncio
    async def test_starter_monthly_includes_usage_line_item(self, _patch_shopify_client):
        """Monthly subscription mutation includes both recurring and usage line items."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response()

        await create_subscription(
            shop_domain="test-store.myshopify.com",
            tier="starter",
            interval="month",
        )

        call_args = _patch_shopify_client.execute.call_args
        variables = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("variables", {})
        line_items = variables["lineItems"]
        assert len(line_items) == 2
        assert "appRecurringPricingDetails" in line_items[0]["plan"]
        assert "appUsagePricingDetails" in line_items[1]["plan"]


# ===================================================================
# SHB-02: create_subscription Professional monthly
# ===================================================================


class TestCreateSubscriptionProfessionalMonthly:
    """SHB-02: Create a Professional monthly subscription."""

    @pytest.mark.asyncio
    async def test_professional_monthly_pricing(self, _patch_shopify_client):
        """Professional monthly uses $399 base and $1,000 overage cap."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response(
            name="Agent Red Professional (Monthly)",
        )

        result = await create_subscription(
            shop_domain="pro-store.myshopify.com",
            tier="professional",
            interval="month",
        )

        assert result["tier"] == "professional"
        assert result["base_price"] == 399.00
        assert result["overage_cap"] == 1000.00
        assert result["subscription_name"] == "Agent Red Professional (Monthly)"


# ===================================================================
# SHB-03: create_subscription Enterprise monthly
# ===================================================================


class TestCreateSubscriptionEnterpriseMonthly:
    """SHB-03: Create an Enterprise monthly subscription."""

    @pytest.mark.asyncio
    async def test_enterprise_monthly_pricing(self, _patch_shopify_client):
        """Enterprise monthly uses $999 base and $2,000 overage cap."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response(
            name="Agent Red Enterprise (Monthly)",
        )

        result = await create_subscription(
            shop_domain="enterprise-store.myshopify.com",
            tier="enterprise",
            interval="month",
        )

        assert result["tier"] == "enterprise"
        assert result["base_price"] == 999.00
        assert result["overage_cap"] == 2000.00
        assert result["subscription_name"] == "Agent Red Enterprise (Monthly)"


# ===================================================================
# SHB-04: create_subscription annual (no usage line items)
# ===================================================================


class TestCreateSubscriptionAnnual:
    """SHB-04: Annual subscriptions omit usage line items per Shopify limitation."""

    @pytest.mark.asyncio
    async def test_annual_has_single_recurring_line_item(self, _patch_shopify_client):
        """Annual subscription mutation includes only the recurring line item."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response(
            name="Agent Red Professional (Annual)",
        )

        await create_subscription(
            shop_domain="annual-store.myshopify.com",
            tier="professional",
            interval="year",
        )

        call_args = _patch_shopify_client.execute.call_args
        variables = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("variables", {})
        line_items = variables["lineItems"]
        assert len(line_items) == 1
        assert "appRecurringPricingDetails" in line_items[0]["plan"]

    @pytest.mark.asyncio
    async def test_annual_uses_annual_total_price(self, _patch_shopify_client):
        """Annual subscription uses annual_total ($3,990) not monthly ($399)."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response()

        result = await create_subscription(
            shop_domain="annual-store.myshopify.com",
            tier="professional",
            interval="year",
        )

        assert result["base_price"] == 3990.00

    @pytest.mark.asyncio
    async def test_annual_overage_cap_is_zero(self, _patch_shopify_client):
        """Annual subscription reports $0 overage cap since usage billing is not included."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response()

        result = await create_subscription(
            shop_domain="annual-store.myshopify.com",
            tier="starter",
            interval="year",
        )

        assert result["overage_cap"] == 0.00

    @pytest.mark.asyncio
    async def test_annual_interval_maps_to_shopify_annual(self, _patch_shopify_client):
        """Annual interval maps to Shopify's ANNUAL enum in the GraphQL mutation."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response()

        await create_subscription(
            shop_domain="annual-store.myshopify.com",
            tier="starter",
            interval="year",
        )

        call_args = _patch_shopify_client.execute.call_args
        variables = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("variables", {})
        recurring_details = variables["lineItems"][0]["plan"]["appRecurringPricingDetails"]
        assert recurring_details["interval"] == "ANNUAL"


# ===================================================================
# SHB-05: Decimal arithmetic — overage rate precision
# ===================================================================


class TestDecimalOveragePrecision:
    """SHB-05: Overage rate uses Decimal arithmetic, not float."""

    @pytest.mark.asyncio
    async def test_overage_uses_decimal_multiplication(self, _patch_shopify_client):
        """Usage charge computed as Decimal(overage_count) * Decimal(overage_rate)."""
        # Set up an active subscription with usage line item
        _shop_subscriptions["decimal-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": "gid://shopify/AppSubscriptionLineItem/99",
            "tier": "professional",
            "interval": "month",
            "status": "active",
            "pricing": _get_tier_pricing("professional"),
        }

        _patch_shopify_client.execute.return_value = _graphql_usage_record_response()

        result = await record_shopify_usage(
            shop_domain="decimal-store.myshopify.com",
            overage_count=100,
            idempotency_key="key-001",
        )

        # Professional overage rate is $0.025
        # 100 * 0.025 = 2.50 exactly
        assert result["amount"] == 2.50
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_decimal_avoids_float_errors(self, _patch_shopify_client):
        """Decimal prevents floating-point precision loss (e.g. 0.1 + 0.2 != 0.3)."""
        _shop_subscriptions["float-test.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": "gid://shopify/AppSubscriptionLineItem/99",
            "tier": "starter",
            "interval": "month",
            "status": "active",
            "pricing": _get_tier_pricing("starter"),
        }

        _patch_shopify_client.execute.return_value = _graphql_usage_record_response()

        result = await record_shopify_usage(
            shop_domain="float-test.myshopify.com",
            overage_count=3,
            idempotency_key="key-float",
        )

        # Starter rate $0.04 * 3 = $0.12 exactly (not 0.12000000000000001)
        assert result["amount"] == 0.12


# ===================================================================
# SHB-06: Decimal quantize to cents
# ===================================================================


class TestDecimalQuantizeToCents:
    """SHB-06: Charge amounts are quantized to two decimal places (cents)."""

    @pytest.mark.asyncio
    async def test_quantize_rounds_to_cents(self, _patch_shopify_client):
        """Overage amount is quantized to 0.01 (cents) regardless of rate precision."""
        _shop_subscriptions["quantize-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": "gid://shopify/AppSubscriptionLineItem/99",
            "tier": "professional",
            "interval": "month",
            "status": "active",
            "pricing": _get_tier_pricing("professional"),
        }

        _patch_shopify_client.execute.return_value = _graphql_usage_record_response()

        # 7 conversations * $0.025 = $0.175 → quantized to $0.18 (banker's rounding)
        # or $0.17 depending on rounding mode — verify it has 2 decimal places
        await record_shopify_usage(
            shop_domain="quantize-store.myshopify.com",
            overage_count=7,
            idempotency_key="key-quantize",
        )

        # Verify the amount string passed to Shopify has exactly 2 decimal places
        call_args = _patch_shopify_client.execute.call_args
        variables = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("variables", {})
        amount_str = variables["price"]["amount"]
        # Decimal("0.175").quantize(Decimal("0.01")) → "0.18" with ROUND_HALF_EVEN
        assert "." in amount_str
        decimal_places = len(amount_str.split(".")[1])
        assert decimal_places == 2

    @pytest.mark.asyncio
    async def test_quantize_exact_cents_unchanged(self, _patch_shopify_client):
        """Amounts that are already exact cents are not altered by quantize."""
        _shop_subscriptions["exact-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": "gid://shopify/AppSubscriptionLineItem/99",
            "tier": "starter",
            "interval": "month",
            "status": "active",
            "pricing": _get_tier_pricing("starter"),
        }

        _patch_shopify_client.execute.return_value = _graphql_usage_record_response()

        # 25 * $0.04 = $1.00 exactly
        result = await record_shopify_usage(
            shop_domain="exact-store.myshopify.com",
            overage_count=25,
            idempotency_key="key-exact",
        )

        assert result["amount"] == 1.00


# ===================================================================
# SHB-07: confirm_subscription calls provisioning
# ===================================================================


class TestConfirmSubscriptionProvisioning:
    """SHB-07: confirm_subscription invokes provision_tenant and activate_tenant."""

    @pytest.mark.asyncio
    async def test_confirm_calls_provision_and_activate(
        self,
        _patch_shopify_client,
        _patch_provisioning,
    ):
        """Confirmation flow provisions and immediately activates the tenant."""
        mock_provision, mock_activate = _patch_provisioning

        _patch_shopify_client.execute.return_value = _graphql_active_subscription_response()

        # Pre-populate subscription from create_subscription step
        _shop_subscriptions["confirm-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/12345",
            "tier": "starter",
            "interval": "month",
            "status": "pending_approval",
            "pricing": _get_tier_pricing("starter"),
        }

        result = await confirm_subscription(shop_domain="confirm-store.myshopify.com")

        mock_provision.assert_called_once()
        mock_activate.assert_called_once()
        assert result["status"] == "active"
        assert result["tenant_id"] == "tenant-test-001"

    @pytest.mark.asyncio
    async def test_confirm_stores_usage_line_item_id(
        self,
        _patch_shopify_client,
        _patch_provisioning,
    ):
        """Confirmation extracts and stores the usage line item ID for overage recording."""
        _patch_shopify_client.execute.return_value = _graphql_active_subscription_response(
            usage_line_item_id="gid://shopify/AppSubscriptionLineItem/42",
        )

        _shop_subscriptions["confirm-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/12345",
            "tier": "starter",
            "interval": "month",
            "status": "pending_approval",
            "pricing": _get_tier_pricing("starter"),
        }

        result = await confirm_subscription(shop_domain="confirm-store.myshopify.com")

        assert result["usage_line_item_id"] == "gid://shopify/AppSubscriptionLineItem/42"
        assert _shop_subscriptions["confirm-store.myshopify.com"]["usage_line_item_id"] == (
            "gid://shopify/AppSubscriptionLineItem/42"
        )

    @pytest.mark.asyncio
    async def test_confirm_no_active_subscription(
        self,
        _patch_shopify_client,
    ):
        """Confirmation with no active subscription returns no_active_subscription status."""
        _patch_shopify_client.execute.return_value = {
            "currentAppInstallation": {
                "activeSubscriptions": [],
            },
        }

        result = await confirm_subscription(shop_domain="empty-store.myshopify.com")

        assert result["status"] == "no_active_subscription"


# ===================================================================
# SHB-08: get_billing_status returns subscription details
# ===================================================================


class TestGetBillingStatusWithSubscription:
    """SHB-08: get_billing_status returns active subscription details."""

    @pytest.mark.asyncio
    async def test_active_subscription_details(self, _patch_shopify_client):
        """Active subscription returns full status with name, dates, and line items."""
        _patch_shopify_client.execute.return_value = _graphql_active_subscription_response(
            sub_id="gid://shopify/AppSubscription/555",
            name="Agent Red Professional (Monthly)",
        )

        result = await get_billing_status(shop_domain="active-store.myshopify.com")

        assert result["shop_domain"] == "active-store.myshopify.com"
        assert result["has_active_subscription"] is True
        assert result["subscription_name"] == "Agent Red Professional (Monthly)"
        assert result["status"] == "ACTIVE"
        assert result["subscription_id"] == "gid://shopify/AppSubscription/555"
        assert len(result["line_items"]) == 2


# ===================================================================
# SHB-09: get_billing_status no subscription returns empty
# ===================================================================


class TestGetBillingStatusNoSubscription:
    """SHB-09: get_billing_status returns has_active_subscription=False when none exists."""

    @pytest.mark.asyncio
    async def test_no_subscription_returns_false(self, _patch_shopify_client):
        """Store with no active subscription returns minimal response."""
        _patch_shopify_client.execute.return_value = {
            "currentAppInstallation": {
                "activeSubscriptions": [],
            },
        }

        result = await get_billing_status(shop_domain="empty-store.myshopify.com")

        assert result["shop_domain"] == "empty-store.myshopify.com"
        assert result["has_active_subscription"] is False
        assert "subscription_name" not in result


# ===================================================================
# SHB-10: record_shopify_usage creates usage record
# ===================================================================


class TestRecordShopifyUsage:
    """SHB-10: record_shopify_usage creates a Shopify usage charge."""

    @pytest.mark.asyncio
    async def test_usage_record_created_successfully(self, _patch_shopify_client):
        """Valid usage recording returns success with amount and record ID."""
        _shop_subscriptions["usage-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": "gid://shopify/AppSubscriptionLineItem/99",
            "tier": "starter",
            "interval": "month",
            "status": "active",
            "pricing": _get_tier_pricing("starter"),
        }

        _patch_shopify_client.execute.return_value = _graphql_usage_record_response(
            record_id="gid://shopify/AppUsageRecord/999",
        )

        result = await record_shopify_usage(
            shop_domain="usage-store.myshopify.com",
            overage_count=50,
            idempotency_key="key-usage-001",
        )

        assert result["success"] is True
        assert result["amount"] == 2.00  # 50 * $0.04
        assert result["record_id"] == "gid://shopify/AppUsageRecord/999"
        assert result["idempotency_key"] == "key-usage-001"
        assert result["shop_domain"] == "usage-store.myshopify.com"

    @pytest.mark.asyncio
    async def test_usage_record_description_contains_tier_info(self, _patch_shopify_client):
        """Usage record description includes tier name, included count, and rate."""
        _shop_subscriptions["desc-store.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": "gid://shopify/AppSubscriptionLineItem/99",
            "tier": "professional",
            "interval": "month",
            "status": "active",
            "pricing": _get_tier_pricing("professional"),
        }

        _patch_shopify_client.execute.return_value = _graphql_usage_record_response()

        result = await record_shopify_usage(
            shop_domain="desc-store.myshopify.com",
            overage_count=10,
            idempotency_key="key-desc",
        )

        assert "professional" in result["description"]
        assert "5,000" in result["description"]
        assert "$0.025" in result["description"]


# ===================================================================
# SHB-11: record_shopify_usage no subscription -> ValueError
# ===================================================================


class TestRecordUsageNoSubscription:
    """SHB-11: record_shopify_usage raises ValueError when no subscription exists."""

    @pytest.mark.asyncio
    async def test_no_subscription_raises_value_error(self):
        """Recording usage without an existing subscription raises ValueError."""
        with pytest.raises(ValueError, match="No subscription found"):
            await record_shopify_usage(
                shop_domain="unknown-store.myshopify.com",
                overage_count=10,
                idempotency_key="key-no-sub",
            )

    @pytest.mark.asyncio
    async def test_no_usage_line_item_raises_value_error(self):
        """Recording usage when subscription has no usage line item raises ValueError."""
        _shop_subscriptions["no-usage-item.myshopify.com"] = {
            "subscription_id": "gid://shopify/AppSubscription/1",
            "usage_line_item_id": None,  # Annual plan — no usage line item
            "tier": "starter",
            "interval": "year",
            "status": "active",
            "pricing": _get_tier_pricing("starter"),
        }

        with pytest.raises(ValueError, match="No usage line item found"):
            await record_shopify_usage(
                shop_domain="no-usage-item.myshopify.com",
                overage_count=10,
                idempotency_key="key-no-item",
            )


# ===================================================================
# SHB-12: Invalid tier -> ValueError
# ===================================================================


class TestInvalidTier:
    """SHB-12: Invalid tier raises ValueError from _get_tier_pricing and create_subscription."""

    @pytest.mark.asyncio
    async def test_invalid_tier_in_create_subscription(self, _patch_shopify_client):
        """create_subscription with invalid tier raises ValueError."""
        with pytest.raises(ValueError, match="Invalid tier"):
            await create_subscription(
                shop_domain="bad-tier.myshopify.com",
                tier="premium",
                interval="month",
            )

    def test_get_tier_pricing_invalid_tier(self):
        """_get_tier_pricing raises ValueError for unknown tier."""
        with pytest.raises(ValueError, match="Invalid tier 'gold'"):
            _get_tier_pricing("gold")

    def test_get_tier_pricing_empty_string(self):
        """_get_tier_pricing raises ValueError for empty string."""
        with pytest.raises(ValueError, match="Invalid tier"):
            _get_tier_pricing("")


# ===================================================================
# SHB-13: Invalid interval -> ValueError
# ===================================================================


class TestInvalidInterval:
    """SHB-13: Invalid interval raises ValueError from create_subscription."""

    @pytest.mark.asyncio
    async def test_invalid_interval_raises_value_error(self, _patch_shopify_client):
        """create_subscription with invalid interval raises ValueError."""
        with pytest.raises(ValueError, match="Invalid interval"):
            await create_subscription(
                shop_domain="bad-interval.myshopify.com",
                tier="starter",
                interval="quarterly",
            )

    @pytest.mark.asyncio
    async def test_weekly_interval_rejected(self, _patch_shopify_client):
        """Intervals outside the valid set (month, year) are rejected."""
        with pytest.raises(ValueError, match="Invalid interval 'week'"):
            await create_subscription(
                shop_domain="bad-interval.myshopify.com",
                tier="starter",
                interval="week",
            )


# ===================================================================
# SHB-14: Test mode env var
# ===================================================================


class TestIsTestMode:
    """SHB-14: _is_test_mode reads SHOPIFY_BILLING_TEST env var."""

    def test_default_is_test_mode(self):
        """Default (no env var) returns True (test mode)."""
        with patch.dict("os.environ", {}, clear=True):
            # Remove SHOPIFY_BILLING_TEST if present
            import os
            os.environ.pop("SHOPIFY_BILLING_TEST", None)
            assert _is_test_mode() is True

    def test_explicit_true(self):
        """SHOPIFY_BILLING_TEST=true returns True."""
        with patch.dict("os.environ", {"SHOPIFY_BILLING_TEST": "true"}):
            assert _is_test_mode() is True

    def test_explicit_True_uppercase(self):
        """SHOPIFY_BILLING_TEST=True (capitalized) returns True."""
        with patch.dict("os.environ", {"SHOPIFY_BILLING_TEST": "True"}):
            assert _is_test_mode() is True

    def test_explicit_false(self):
        """SHOPIFY_BILLING_TEST=false returns False (live billing)."""
        with patch.dict("os.environ", {"SHOPIFY_BILLING_TEST": "false"}):
            assert _is_test_mode() is False

    async def test_test_flag_passed_to_mutation(self, _patch_shopify_client):
        """The test flag from _is_test_mode() is passed to the GraphQL mutation."""
        _patch_shopify_client.execute.return_value = _graphql_subscription_response()

        await create_subscription(
            shop_domain="test-flag.myshopify.com",
            tier="starter",
            interval="month",
        )

        call_args = _patch_shopify_client.execute.call_args
        variables = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get("variables", {})
        # Default env should have test=True
        assert "test" in variables


# ===================================================================
# SHB-15: _get_tier_pricing returns correct values
# ===================================================================


class TestGetTierPricingValues:
    """SHB-15: _get_tier_pricing returns correct pricing for each tier."""

    def test_starter_pricing(self):
        """Starter tier has $149/mo, $1,490/yr, $0.04 overage, 1,000 included."""
        pricing = _get_tier_pricing("starter")
        assert pricing["monthly"] == Decimal("149.00")
        assert pricing["annual_total"] == Decimal("1490.00")
        assert pricing["overage_rate"] == Decimal("0.04")
        assert pricing["included_conversations"] == 1000
        assert pricing["capped_amount"] == Decimal("500.00")
        assert pricing["name"] == "Agent Red Starter"

    def test_professional_pricing(self):
        """Professional tier has $399/mo, $3,990/yr, $0.025 overage, 5,000 included."""
        pricing = _get_tier_pricing("professional")
        assert pricing["monthly"] == Decimal("399.00")
        assert pricing["annual_total"] == Decimal("3990.00")
        assert pricing["overage_rate"] == Decimal("0.025")
        assert pricing["included_conversations"] == 5000
        assert pricing["capped_amount"] == Decimal("1000.00")
        assert pricing["name"] == "Agent Red Professional"

    def test_enterprise_pricing(self):
        """Enterprise tier has $999/mo, $9,990/yr, $0.015 overage, 20,000 included."""
        pricing = _get_tier_pricing("enterprise")
        assert pricing["monthly"] == Decimal("999.00")
        assert pricing["annual_total"] == Decimal("9990.00")
        assert pricing["overage_rate"] == Decimal("0.015")
        assert pricing["included_conversations"] == 20000
        assert pricing["capped_amount"] == Decimal("2000.00")
        assert pricing["name"] == "Agent Red Enterprise"

    def test_valid_tiers_frozenset(self):
        """VALID_TIERS contains exactly the three expected tiers."""
        assert VALID_TIERS == frozenset({"starter", "professional", "enterprise"})

    def test_valid_intervals_frozenset(self):
        """VALID_INTERVALS contains exactly month and year."""
        assert VALID_INTERVALS == frozenset({"month", "year"})

    def test_interval_map_values(self):
        """_INTERVAL_MAP maps to Shopify's GraphQL billing interval enums."""
        assert _INTERVAL_MAP["month"] == "EVERY_30_DAYS"
        assert _INTERVAL_MAP["year"] == "ANNUAL"

    def test_all_tiers_have_required_keys(self):
        """Every tier returned by _get_tier_pricing has all required keys."""
        required_keys = {"name", "monthly", "annual_total", "overage_rate", "included_conversations", "capped_amount"}
        for tier_name in VALID_TIERS:
            tier_data = _get_tier_pricing(tier_name)
            missing = required_keys - set(tier_data.keys())
            assert not missing, f"Tier '{tier_name}' missing keys: {missing}"

    def test_all_prices_are_decimal(self):
        """All monetary values from _get_tier_pricing use Decimal, not float."""
        for tier_name in VALID_TIERS:
            tier_data = _get_tier_pricing(tier_name)
            for key in ("monthly", "annual_total", "overage_rate", "capped_amount"):
                assert isinstance(tier_data[key], Decimal), (
                    f"Tier '{tier_name}' key '{key}' is {type(tier_data[key])}, expected Decimal"
                )


# ---------------------------------------------------------------------------
# SHB-MCP: Auto-enable Shopify Storefront MCP (SPEC-1782 / WI-1289)
# ---------------------------------------------------------------------------


class TestAutoEnableShopifyMcp:
    """Verify _auto_enable_shopify_mcp enables MCP for Shopify tenants."""

    @pytest.mark.asyncio
    async def test_auto_enable_calls_config_processor(self):
        """MCP config is written via config processor on Shopify provisioning."""
        mock_processor = MagicMock()
        mock_processor.update_config = AsyncMock()

        with patch(
            "src.multi_tenant.tenant_config_processor.get_config_processor",
            return_value=mock_processor,
        ):
            await _auto_enable_shopify_mcp("tenant-123", "myshop.myshopify.com")

        mock_processor.update_config.assert_called_once()
        call_kwargs = mock_processor.update_config.call_args[1]
        assert call_kwargs["tenant_id"] == "tenant-123"
        assert call_kwargs["updates"]["mcp_enabled"] is True

        servers = call_kwargs["updates"]["mcp_servers"]
        assert len(servers) == 1
        assert servers[0]["server_name"] == "shopify-storefront"
        assert servers[0]["server_type"] == "shopify-storefront"
        assert servers[0]["shop_domain"] == "myshop.myshopify.com"
        assert servers[0]["enabled"] is True
        assert servers[0]["read_only"] is True
        assert "myshop.myshopify.com" in servers[0]["server_url"]

    @pytest.mark.asyncio
    async def test_auto_enable_is_best_effort(self):
        """MCP auto-enable failure must not propagate — best-effort pattern."""
        with patch(
            "src.multi_tenant.tenant_config_processor.get_config_processor",
            side_effect=RuntimeError("Cosmos unavailable"),
        ):
            # Should NOT raise
            await _auto_enable_shopify_mcp("tenant-err", "broken.myshopify.com")

    @pytest.mark.asyncio
    async def test_auto_enable_actor_tag(self):
        """Actor tag is 'system:shopify-auto-enable' for audit traceability."""
        mock_processor = MagicMock()
        mock_processor.update_config = AsyncMock()

        with patch(
            "src.multi_tenant.tenant_config_processor.get_config_processor",
            return_value=mock_processor,
        ):
            await _auto_enable_shopify_mcp("t-1", "shop.myshopify.com")

        call_kwargs = mock_processor.update_config.call_args[1]
        assert call_kwargs["actor"] == "system:shopify-auto-enable"
