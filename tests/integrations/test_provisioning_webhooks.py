"""Unit tests for provisioning lifecycle + Stripe webhook event handlers.

Covers:
    - provisioning.py: provision, activate, update, deactivate, flag, lookup
    - stripe_webhooks.py: idempotency, event routing, handler branches

Run:
    pytest tests/integrations/test_provisioning_webhooks.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.provisioning import (
    BillingChannel,
    TenantRecord,
    TenantStatus,
    _GRACE_PERIOD_SECONDS,
    _shopify_index,
    _stripe_index,
    _tenants,
    activate_tenant,
    deactivate_tenant,
    flag_payment_issue,
    get_tenant,
    provision_tenant,
    update_tenant,
)


# ---------------------------------------------------------------------------
# Fixtures — clear in-memory stores between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _clear_tenant_stores():
    """Reset module-level in-memory stores before each test."""
    _tenants.clear()
    _stripe_index.clear()
    _shopify_index.clear()
    yield
    _tenants.clear()
    _stripe_index.clear()
    _shopify_index.clear()


# ===================================================================
# provisioning.py — provision_tenant
# ===================================================================

class TestProvisionTenant:
    """PROV-01: Tenant creation and re-provisioning."""

    def test_new_stripe_tenant(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_test_001",
            stripe_subscription_id="sub_test_001",
            customer_email="alice@example.com",
        )
        assert t.status == TenantStatus.PROVISIONING
        assert t.billing_channel == BillingChannel.STRIPE
        assert t.tier == "starter"
        assert t.interval == "month"
        assert t.stripe_customer_id == "cus_test_001"
        assert t.customer_email == "alice@example.com"
        assert t.tenant_id in _tenants
        assert _stripe_index["cus_test_001"] == t.tenant_id

    def test_new_shopify_tenant(self):
        t = provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            tier="professional",
            interval="month",
            shopify_shop_domain="alice.myshopify.com",
            shopify_subscription_id="gid://shopify/AppSubscription/123",
        )
        assert t.billing_channel == BillingChannel.SHOPIFY
        assert t.shopify_shop_domain == "alice.myshopify.com"
        assert _shopify_index["alice.myshopify.com"] == t.tenant_id

    def test_re_provision_existing_stripe_tenant(self):
        t1 = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_re",
        )
        original_id = t1.tenant_id

        t2 = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="professional",
            stripe_customer_id="cus_re",
        )
        # Same tenant, updated tier
        assert t2.tenant_id == original_id
        assert t2.tier == "professional"
        assert t2.status == TenantStatus.PROVISIONING

    def test_re_provision_clears_grace_period(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_grace",
        )
        # Simulate deactivation
        t.status = TenantStatus.GRACE_PERIOD
        t.deactivated_at = int(time.time())
        t.grace_period_ends_at = int(time.time()) + _GRACE_PERIOD_SECONDS

        t2 = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_grace",
        )
        assert t2.deactivated_at is None
        assert t2.grace_period_ends_at is None

    def test_provision_with_addons(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="enterprise",
            addons=["multi-language", "white-label"],
            stripe_customer_id="cus_addons",
        )
        assert t.addons == ["multi-language", "white-label"]

    def test_provision_generates_uuid(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_uuid",
        )
        assert len(t.tenant_id) == 36  # UUID format
        assert "-" in t.tenant_id


# ===================================================================
# provisioning.py — activate_tenant
# ===================================================================

class TestActivateTenant:
    """PROV-02: Tenant activation after payment confirmation."""

    def test_activate_by_tenant_id(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_act",
        )
        assert t.status == TenantStatus.PROVISIONING

        result = activate_tenant(tenant_id=t.tenant_id)
        assert result is not None
        assert result.status == TenantStatus.ACTIVE

    def test_activate_by_stripe_customer_id(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_act_stripe",
        )
        result = activate_tenant(stripe_customer_id="cus_act_stripe")
        assert result is not None
        assert result.status == TenantStatus.ACTIVE

    def test_activate_by_shop_domain(self):
        t = provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            shopify_shop_domain="shop.myshopify.com",
        )
        result = activate_tenant(shopify_shop_domain="shop.myshopify.com")
        assert result is not None
        assert result.status == TenantStatus.ACTIVE

    def test_activate_not_found(self):
        result = activate_tenant(tenant_id="nonexistent")
        assert result is None

    def test_activate_clears_deactivation_fields(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_clear",
        )
        t.deactivated_at = int(time.time())
        t.grace_period_ends_at = int(time.time()) + 1000

        result = activate_tenant(stripe_customer_id="cus_clear")
        assert result.deactivated_at is None
        assert result.grace_period_ends_at is None


# ===================================================================
# provisioning.py — update_tenant
# ===================================================================

class TestUpdateTenant:
    """PROV-03: Tenant plan updates (tier, interval, addons)."""

    def test_update_tier(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_upd",
        )
        result = update_tenant(tier="professional", stripe_customer_id="cus_upd")
        assert result.tier == "professional"

    def test_update_interval(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_int",
        )
        result = update_tenant(interval="year", stripe_customer_id="cus_int")
        assert result.interval == "year"

    def test_update_addons(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            addons=["a"],
            stripe_customer_id="cus_addon",
        )
        result = update_tenant(addons=["a", "b", "c"], stripe_customer_id="cus_addon")
        assert result.addons == ["a", "b", "c"]

    def test_update_clears_addons(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            addons=["multi-language"],
            stripe_customer_id="cus_clr",
        )
        result = update_tenant(addons=[], stripe_customer_id="cus_clr")
        assert result.addons == []

    def test_update_none_keeps_current(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_keep",
        )
        result = update_tenant(tier=None, stripe_customer_id="cus_keep")
        assert result.tier == "starter"  # Unchanged

    def test_update_not_found(self):
        result = update_tenant(tier="enterprise", tenant_id="nonexistent")
        assert result is None


# ===================================================================
# provisioning.py — deactivate_tenant
# ===================================================================

class TestDeactivateTenant:
    """PROV-04: Tenant deactivation with 30-day grace period."""

    def test_deactivate_sets_grace_period(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_deact",
        )
        activate_tenant(stripe_customer_id="cus_deact")

        result = deactivate_tenant(stripe_customer_id="cus_deact")
        assert result.status == TenantStatus.GRACE_PERIOD
        assert result.deactivated_at is not None
        assert result.grace_period_ends_at is not None

    def test_grace_period_is_30_days(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_30d",
        )
        result = deactivate_tenant(stripe_customer_id="cus_30d")
        expected_delta = _GRACE_PERIOD_SECONDS  # 30 * 24 * 60 * 60
        actual_delta = result.grace_period_ends_at - result.deactivated_at
        assert actual_delta == expected_delta

    def test_deactivate_not_found(self):
        result = deactivate_tenant(tenant_id="nonexistent")
        assert result is None


# ===================================================================
# provisioning.py — flag_payment_issue
# ===================================================================

class TestFlagPaymentIssue:
    """PROV-05: Payment failure flagging."""

    def test_flag_sets_past_due(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_flag",
        )
        activate_tenant(stripe_customer_id="cus_flag")

        result = flag_payment_issue(stripe_customer_id="cus_flag")
        assert result.status == TenantStatus.PAST_DUE

    def test_flag_not_found(self):
        result = flag_payment_issue(tenant_id="nonexistent")
        assert result is None

    def test_flag_updates_timestamp(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_ts",
        )
        old_updated = t.updated_at
        # Small delay to ensure timestamp changes
        flag_payment_issue(stripe_customer_id="cus_ts")
        assert t.updated_at >= old_updated


# ===================================================================
# provisioning.py — get_tenant
# ===================================================================

class TestGetTenant:
    """PROV-06: Tenant lookup by various identifiers."""

    def test_get_by_tenant_id(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_get",
        )
        result = get_tenant(tenant_id=t.tenant_id)
        assert result is not None
        assert result.tenant_id == t.tenant_id

    def test_get_by_stripe_id(self):
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_get_stripe",
        )
        result = get_tenant(stripe_customer_id="cus_get_stripe")
        assert result is not None

    def test_get_by_shop_domain(self):
        t = provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            shopify_shop_domain="getshop.myshopify.com",
        )
        result = get_tenant(shopify_shop_domain="getshop.myshopify.com")
        assert result is not None

    def test_get_not_found(self):
        result = get_tenant(tenant_id="nonexistent")
        assert result is None


# ===================================================================
# provisioning.py — Full lifecycle integration
# ===================================================================

class TestTenantLifecycle:
    """PROV-07: Full provision → activate → update → deactivate → re-provision."""

    def test_full_stripe_lifecycle(self):
        # 1. Provision
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_lifecycle",
            customer_email="lifecycle@test.com",
        )
        assert t.status == TenantStatus.PROVISIONING

        # 2. Activate
        t = activate_tenant(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.ACTIVE

        # 3. Update tier
        t = update_tenant(tier="professional", stripe_customer_id="cus_lifecycle")
        assert t.tier == "professional"
        assert t.status == TenantStatus.ACTIVE

        # 4. Payment failure
        t = flag_payment_issue(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.PAST_DUE

        # 5. Payment recovered
        t = activate_tenant(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.ACTIVE

        # 6. Cancel
        t = deactivate_tenant(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.GRACE_PERIOD
        assert t.grace_period_ends_at is not None

        # 7. Re-subscribe
        t = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="enterprise",
            stripe_customer_id="cus_lifecycle",
        )
        assert t.status == TenantStatus.PROVISIONING
        assert t.tier == "enterprise"
        assert t.deactivated_at is None

    def test_cross_channel_isolation(self):
        """Stripe and Shopify tenants are independent."""
        s1 = provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_iso_1",
        )
        s2 = provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            tier="professional",
            shopify_shop_domain="iso.myshopify.com",
        )
        assert s1.tenant_id != s2.tenant_id
        assert len(_tenants) == 2

        # Deactivating one doesn't affect the other
        deactivate_tenant(stripe_customer_id="cus_iso_1")
        shopify_tenant = get_tenant(shopify_shop_domain="iso.myshopify.com")
        assert shopify_tenant.status != TenantStatus.GRACE_PERIOD


# ===================================================================
# stripe_webhooks.py — Idempotency
# ===================================================================

class TestWebhookIdempotency:
    """WH-01: Duplicate event detection."""

    def test_first_event_not_duplicate(self):
        from src.integrations.stripe_webhooks import _is_duplicate

        assert _is_duplicate("evt_first_001") is False

    def test_second_event_is_duplicate(self):
        from src.integrations.stripe_webhooks import _is_duplicate

        _is_duplicate("evt_dup_001")  # First call
        assert _is_duplicate("evt_dup_001") is True

    def test_different_events_not_duplicates(self):
        from src.integrations.stripe_webhooks import _is_duplicate

        _is_duplicate("evt_a")
        assert _is_duplicate("evt_b") is False


# ===================================================================
# stripe_webhooks.py — Event handler: checkout.session.completed
# ===================================================================

class TestHandleCheckoutCompleted:
    """WH-02: Checkout completion → provisioning or pack credit."""

    @pytest.mark.asyncio
    async def test_subscription_checkout(self):
        from src.integrations.stripe_webhooks import handle_checkout_completed

        event = {
            "data": {
                "object": {
                    "id": "cs_sub_001",
                    "mode": "subscription",
                    "customer": "cus_wh_sub",
                    "subscription": "sub_wh_001",
                    "customer_email": "webhook@test.com",
                    "metadata": {
                        "agent_red_tier": "professional",
                        "agent_red_interval": "month",
                    },
                    "client_reference_id": None,
                },
            },
        }
        result = await handle_checkout_completed(event)
        assert result["action"] == "provision_tenant"
        assert result["stripe_customer_id"] == "cus_wh_sub"

        # Verify tenant was created in the in-memory store
        t = get_tenant(stripe_customer_id="cus_wh_sub")
        assert t is not None
        assert t.tier == "professional"

    @pytest.mark.asyncio
    async def test_pack_purchase(self):
        from src.integrations.stripe_webhooks import handle_checkout_completed

        event = {
            "data": {
                "object": {
                    "id": "cs_pack_001",
                    "mode": "payment",
                    "customer": "cus_wh_pack",
                    "metadata": {
                        "agent_red_pack": "pack_1000",
                        "agent_red_pack_conversations": "1000",
                    },
                    "client_reference_id": None,
                },
            },
        }
        result = await handle_checkout_completed(event)
        assert result["action"] == "pack_purchased"


# ===================================================================
# stripe_webhooks.py — Event handler: customer.subscription.deleted
# ===================================================================

class TestHandleSubscriptionDeleted:
    """WH-03: Subscription cancellation → grace period."""

    @pytest.mark.asyncio
    async def test_subscription_cancelled(self):
        from src.integrations.stripe_webhooks import handle_subscription_deleted

        # Pre-provision a tenant
        provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_wh_del",
        )
        activate_tenant(stripe_customer_id="cus_wh_del")

        event = {
            "data": {
                "object": {
                    "id": "sub_del_001",
                    "customer": "cus_wh_del",
                    "metadata": {"agent_red_tier": "starter"},
                    "canceled_at": 1700000000,
                    "ended_at": 1700000000,
                },
            },
        }
        result = await handle_subscription_deleted(event)
        assert result["action"] == "subscription_cancelled"
        assert result["grace_period_days"] == 30

        t = get_tenant(stripe_customer_id="cus_wh_del")
        assert t.status == TenantStatus.GRACE_PERIOD


# ===================================================================
# stripe_webhooks.py — Event handler: invoice.payment_failed
# ===================================================================

class TestHandlePaymentFailed:
    """WH-04: Payment failure → tenant flagged."""

    @pytest.mark.asyncio
    async def test_payment_failed_flags_tenant(self):
        from src.integrations.stripe_webhooks import handle_payment_failed

        provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_wh_fail",
        )
        activate_tenant(stripe_customer_id="cus_wh_fail")

        event = {
            "data": {
                "object": {
                    "id": "in_fail_001",
                    "subscription": "sub_fail_001",
                    "customer": "cus_wh_fail",
                    "amount_due": 14900,
                    "currency": "usd",
                    "attempt_count": 1,
                    "next_payment_attempt": 1700100000,
                    "billing_reason": "subscription_cycle",
                },
            },
        }
        result = await handle_payment_failed(event)
        assert result["action"] == "payment_failed"

        t = get_tenant(stripe_customer_id="cus_wh_fail")
        assert t.status == TenantStatus.PAST_DUE


# ===================================================================
# stripe_webhooks.py — Event handler: invoice.payment_succeeded
# ===================================================================

class TestHandlePaymentSucceeded:
    """WH-05: Payment success → usage reset on renewal."""

    @pytest.mark.asyncio
    async def test_renewal_resets_usage(self):
        from src.integrations.stripe_webhooks import handle_payment_succeeded

        provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_wh_pay",
        )
        activate_tenant(stripe_customer_id="cus_wh_pay")

        event = {
            "data": {
                "object": {
                    "id": "in_pay_001",
                    "subscription": "sub_pay_001",
                    "customer": "cus_wh_pay",
                    "amount_paid": 14900,
                    "currency": "usd",
                    "billing_reason": "subscription_cycle",
                    "period_start": 1700000000,
                    "period_end": 1702600000,
                },
            },
        }
        result = await handle_payment_succeeded(event)
        assert result["action"] == "payment_succeeded"
        assert result.get("usage_reset") is True

    @pytest.mark.asyncio
    async def test_initial_payment_no_reset(self):
        from src.integrations.stripe_webhooks import handle_payment_succeeded

        event = {
            "data": {
                "object": {
                    "id": "in_init_001",
                    "subscription": "sub_init_001",
                    "customer": "cus_wh_init",
                    "amount_paid": 14900,
                    "currency": "usd",
                    "billing_reason": "subscription_create",
                    "period_start": 1700000000,
                    "period_end": 1702600000,
                },
            },
        }
        result = await handle_payment_succeeded(event)
        assert result["action"] == "payment_succeeded"
        assert result.get("usage_reset") is not True
