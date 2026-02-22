"""Unit tests for provisioning lifecycle + Stripe webhook event handlers.

Covers:
    - provisioning.py: provision, activate, update, deactivate, flag, lookup
    - stripe_webhooks.py: idempotency, event routing, handler branches

All provisioning functions are async and persist to Cosmos DB via
TenantRepository. Tests use a FakeTenantRepo that stores documents
in-memory and implements the same interface (upsert, patch, read,
find_by_stripe_customer_id, find_by_shopify_domain).

Run:
    pytest tests/integrations/test_provisioning_webhooks.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from src.integrations.provisioning import (
    BillingChannel,
    TenantRecord,
    TenantStatus,
    _GRACE_PERIOD,
    activate_tenant,
    auto_provision_superadmin,
    configure_provisioning_repo,
    deactivate_tenant,
    flag_payment_issue,
    get_tenant,
    provision_tenant,
    provision_trial_tenant,
    update_tenant,
)
from tests.helpers.fake_tenant_repo import FakeTenantRepo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def fake_tenant_repo():
    """Wire a FakeTenantRepo into the provisioning module for each test."""
    repo = FakeTenantRepo()
    configure_provisioning_repo(repo, team_repo=None)
    yield repo
    # Clean up module-level reference
    configure_provisioning_repo(None, team_repo=None)


# ===================================================================
# provisioning.py — provision_tenant
# ===================================================================

class TestProvisionTenant:
    """PROV-01: Tenant creation and re-provisioning."""

    @pytest.mark.asyncio
    async def test_new_stripe_tenant(self, fake_tenant_repo):
        t = await provision_tenant(
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
        assert t.tenant_id in fake_tenant_repo.store

    @pytest.mark.asyncio
    async def test_new_shopify_tenant(self, fake_tenant_repo):
        t = await provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            tier="professional",
            interval="month",
            shopify_shop_domain="alice.myshopify.com",
            shopify_subscription_id="gid://shopify/AppSubscription/123",
        )
        assert t.billing_channel == BillingChannel.SHOPIFY
        assert t.shopify_shop_domain == "alice.myshopify.com"
        # Verify stored in fake repo
        doc = await fake_tenant_repo.find_by_shopify_domain("alice.myshopify.com")
        assert doc is not None

    @pytest.mark.asyncio
    async def test_re_provision_existing_stripe_tenant(self, fake_tenant_repo):
        t1 = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_re",
        )
        original_id = t1.tenant_id

        t2 = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="professional",
            stripe_customer_id="cus_re",
        )
        # Same tenant, updated tier
        assert t2.tenant_id == original_id
        assert t2.tier == "professional"
        assert t2.status == TenantStatus.PROVISIONING

    @pytest.mark.asyncio
    async def test_re_provision_clears_grace_period(self, fake_tenant_repo):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_grace",
        )
        # Simulate deactivation via direct repo patch
        await fake_tenant_repo.patch(t.tenant_id, t.tenant_id, [
            {"op": "set", "path": "/status", "value": "grace_period"},
            {"op": "set", "path": "/deactivated_at", "value": datetime.now(timezone.utc).isoformat()},
            {"op": "set", "path": "/grace_period_ends_at", "value": datetime.now(timezone.utc).isoformat()},
        ])

        t2 = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_grace",
        )
        assert t2.deactivated_at is None
        assert t2.grace_period_ends_at is None

    @pytest.mark.asyncio
    async def test_provision_with_addons(self):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="enterprise",
            addons=["multi-language", "white-label"],
            stripe_customer_id="cus_addons",
        )
        assert t.addons == ["multi-language", "white-label"]

    @pytest.mark.asyncio
    async def test_provision_generates_uuid(self):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_uuid",
        )
        assert len(t.tenant_id) == 36  # UUID format
        assert "-" in t.tenant_id

    @pytest.mark.asyncio
    async def test_provision_timestamps_are_iso8601(self):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_ts",
        )
        # Verify timestamps are ISO 8601 strings
        assert isinstance(t.created_at, str)
        assert isinstance(t.updated_at, str)
        # Should be parseable
        datetime.fromisoformat(t.created_at)
        datetime.fromisoformat(t.updated_at)


# ===================================================================
# provisioning.py — activate_tenant
# ===================================================================

class TestActivateTenant:
    """PROV-02: Tenant activation after payment confirmation."""

    @pytest.mark.asyncio
    async def test_activate_by_tenant_id(self):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_act",
        )
        assert t.status == TenantStatus.PROVISIONING

        result = await activate_tenant(tenant_id=t.tenant_id)
        assert result is not None
        assert result.status == TenantStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_activate_by_stripe_customer_id(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_act_stripe",
        )
        result = await activate_tenant(stripe_customer_id="cus_act_stripe")
        assert result is not None
        assert result.status == TenantStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_activate_by_shop_domain(self):
        await provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            shopify_shop_domain="shop.myshopify.com",
        )
        result = await activate_tenant(shopify_shop_domain="shop.myshopify.com")
        assert result is not None
        assert result.status == TenantStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_activate_not_found(self):
        result = await activate_tenant(tenant_id="nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_activate_clears_deactivation_fields(self, fake_tenant_repo):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_clear",
        )
        # Simulate prior deactivation
        now_iso = datetime.now(timezone.utc).isoformat()
        await fake_tenant_repo.patch(t.tenant_id, t.tenant_id, [
            {"op": "set", "path": "/deactivated_at", "value": now_iso},
            {"op": "set", "path": "/grace_period_ends_at", "value": now_iso},
        ])

        result = await activate_tenant(stripe_customer_id="cus_clear")
        assert result.deactivated_at is None
        assert result.grace_period_ends_at is None


# ===================================================================
# provisioning.py — update_tenant
# ===================================================================

class TestUpdateTenant:
    """PROV-03: Tenant plan updates (tier, interval, addons)."""

    @pytest.mark.asyncio
    async def test_update_tier(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_upd",
        )
        result = await update_tenant(tier="professional", stripe_customer_id="cus_upd")
        assert result.tier == "professional"

    @pytest.mark.asyncio
    async def test_update_interval(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_int",
        )
        result = await update_tenant(interval="year", stripe_customer_id="cus_int")
        assert result.interval == "year"

    @pytest.mark.asyncio
    async def test_update_addons(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            addons=["a"],
            stripe_customer_id="cus_addon",
        )
        result = await update_tenant(addons=["a", "b", "c"], stripe_customer_id="cus_addon")
        assert result.addons == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_update_clears_addons(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            addons=["multi-language"],
            stripe_customer_id="cus_clr",
        )
        result = await update_tenant(addons=[], stripe_customer_id="cus_clr")
        assert result.addons == []

    @pytest.mark.asyncio
    async def test_update_none_keeps_current(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_keep",
        )
        result = await update_tenant(tier=None, stripe_customer_id="cus_keep")
        assert result.tier == "starter"  # Unchanged

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        result = await update_tenant(tier="enterprise", tenant_id="nonexistent")
        assert result is None


# ===================================================================
# provisioning.py — deactivate_tenant
# ===================================================================

class TestDeactivateTenant:
    """PROV-04: Tenant deactivation with 30-day grace period."""

    @pytest.mark.asyncio
    async def test_deactivate_sets_grace_period(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_deact",
        )
        await activate_tenant(stripe_customer_id="cus_deact")

        result = await deactivate_tenant(stripe_customer_id="cus_deact")
        assert result.status == TenantStatus.GRACE_PERIOD
        assert result.deactivated_at is not None
        assert result.grace_period_ends_at is not None

    @pytest.mark.asyncio
    async def test_grace_period_is_30_days(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_30d",
        )
        result = await deactivate_tenant(stripe_customer_id="cus_30d")
        # Parse ISO timestamps and verify 30-day delta
        deactivated = datetime.fromisoformat(result.deactivated_at)
        grace_end = datetime.fromisoformat(result.grace_period_ends_at)
        delta = grace_end - deactivated
        assert delta == _GRACE_PERIOD

    @pytest.mark.asyncio
    async def test_deactivate_not_found(self):
        result = await deactivate_tenant(tenant_id="nonexistent")
        assert result is None


# ===================================================================
# provisioning.py — flag_payment_issue
# ===================================================================

class TestFlagPaymentIssue:
    """PROV-05: Payment failure flagging."""

    @pytest.mark.asyncio
    async def test_flag_sets_past_due(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_flag",
        )
        await activate_tenant(stripe_customer_id="cus_flag")

        result = await flag_payment_issue(stripe_customer_id="cus_flag")
        assert result.status == TenantStatus.PAST_DUE

    @pytest.mark.asyncio
    async def test_flag_not_found(self):
        result = await flag_payment_issue(tenant_id="nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_flag_updates_timestamp(self):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_ts",
        )
        old_updated = t.updated_at
        result = await flag_payment_issue(stripe_customer_id="cus_ts")
        # updated_at should be >= the original (ISO string comparison works for ISO 8601)
        assert result.updated_at >= old_updated


# ===================================================================
# provisioning.py — get_tenant
# ===================================================================

class TestGetTenant:
    """PROV-06: Tenant lookup by various identifiers."""

    @pytest.mark.asyncio
    async def test_get_by_tenant_id(self):
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_get",
        )
        result = await get_tenant(tenant_id=t.tenant_id)
        assert result is not None
        assert result.tenant_id == t.tenant_id

    @pytest.mark.asyncio
    async def test_get_by_stripe_id(self):
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            stripe_customer_id="cus_get_stripe",
        )
        result = await get_tenant(stripe_customer_id="cus_get_stripe")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_by_shop_domain(self):
        await provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            shopify_shop_domain="getshop.myshopify.com",
        )
        result = await get_tenant(shopify_shop_domain="getshop.myshopify.com")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_not_found(self):
        result = await get_tenant(tenant_id="nonexistent")
        assert result is None


# ===================================================================
# provisioning.py — provision_trial_tenant
# ===================================================================

class TestProvisionTrialTenant:
    """PROV-08: Trial tenant provisioning."""

    @pytest.mark.asyncio
    async def test_trial_tenant_created(self, fake_tenant_repo):
        t = await provision_trial_tenant(
            customer_email="trial@example.com",
            trial_duration_days=14,
            conversation_limit=50,
        )
        assert t.status == TenantStatus.ACTIVE
        assert t.billing_channel == BillingChannel.TRIAL
        assert t.tier == "trial"
        assert t.customer_email == "trial@example.com"
        # Verify stored in repo
        doc = fake_tenant_repo.store.get(t.tenant_id)
        assert doc is not None
        assert doc.get("trial_conversation_limit") == 50

    @pytest.mark.asyncio
    async def test_trial_tenant_has_expiry(self, fake_tenant_repo):
        t = await provision_trial_tenant(trial_duration_days=7)
        doc = fake_tenant_repo.store.get(t.tenant_id)
        trial_end = datetime.fromisoformat(doc["trial_expires_at"])
        created = datetime.fromisoformat(doc["created_at"])
        delta = trial_end - created
        assert delta == timedelta(days=7)


# ===================================================================
# provisioning.py — Full lifecycle integration
# ===================================================================

class TestTenantLifecycle:
    """PROV-07: Full provision → activate → update → deactivate → re-provision."""

    @pytest.mark.asyncio
    async def test_full_stripe_lifecycle(self):
        # 1. Provision
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_lifecycle",
            customer_email="lifecycle@test.com",
        )
        assert t.status == TenantStatus.PROVISIONING

        # 2. Activate
        t = await activate_tenant(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.ACTIVE

        # 3. Update tier
        t = await update_tenant(tier="professional", stripe_customer_id="cus_lifecycle")
        assert t.tier == "professional"
        assert t.status == TenantStatus.ACTIVE

        # 4. Payment failure
        t = await flag_payment_issue(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.PAST_DUE

        # 5. Payment recovered
        t = await activate_tenant(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.ACTIVE

        # 6. Cancel
        t = await deactivate_tenant(stripe_customer_id="cus_lifecycle")
        assert t.status == TenantStatus.GRACE_PERIOD
        assert t.grace_period_ends_at is not None

        # 7. Re-subscribe
        t = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="enterprise",
            stripe_customer_id="cus_lifecycle",
        )
        assert t.status == TenantStatus.PROVISIONING
        assert t.tier == "enterprise"
        assert t.deactivated_at is None

    @pytest.mark.asyncio
    async def test_cross_channel_isolation(self, fake_tenant_repo):
        """Stripe and Shopify tenants are independent."""
        s1 = await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_iso_1",
        )
        s2 = await provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            tier="professional",
            shopify_shop_domain="iso.myshopify.com",
        )
        assert s1.tenant_id != s2.tenant_id
        assert len(fake_tenant_repo.store) == 2

        # Deactivating one doesn't affect the other
        await deactivate_tenant(stripe_customer_id="cus_iso_1")
        shopify_tenant = await get_tenant(shopify_shop_domain="iso.myshopify.com")
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

        # Verify tenant was created
        t = await get_tenant(stripe_customer_id="cus_wh_sub")
        assert t is not None
        assert t.tier == "professional"

    @pytest.mark.asyncio
    async def test_subscription_checkout_with_superadmin(self):
        """Checkout with customer_details triggers superadmin auto-provisioning."""
        from src.integrations.stripe_webhooks import handle_checkout_completed

        mock_team_repo = AsyncMock()

        event = {
            "data": {
                "object": {
                    "id": "cs_sub_sa",
                    "mode": "subscription",
                    "customer": "cus_wh_sa",
                    "subscription": "sub_wh_sa",
                    "customer_details": {"email": "owner@merchant.com"},
                    "metadata": {
                        "agent_red_tier": "starter",
                        "agent_red_interval": "month",
                    },
                    "client_reference_id": None,
                },
            },
        }

        with patch(
            "src.multi_tenant.repository.TeamMemberRepository",
            return_value=mock_team_repo,
        ):
            result = await handle_checkout_completed(event)

        assert result["action"] == "provision_tenant"
        assert result["stripe_customer_id"] == "cus_wh_sa"
        assert "superadmin_api_key" in result
        assert result["superadmin_api_key"].startswith("ar_user_")

        # Verify superadmin team member was created
        mock_team_repo.create.assert_called_once()
        created_doc = mock_team_repo.create.call_args[0][1]
        assert created_doc.email == "owner@merchant.com"
        assert created_doc.role.value == "superadmin"
        assert created_doc.invited_by == "system"

        # Verify tenant was created in repo
        t = await get_tenant(stripe_customer_id="cus_wh_sa")
        assert t is not None
        assert t.tier == "starter"

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
        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_wh_del",
        )
        await activate_tenant(stripe_customer_id="cus_wh_del")

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

        t = await get_tenant(stripe_customer_id="cus_wh_del")
        assert t.status == TenantStatus.GRACE_PERIOD


# ===================================================================
# stripe_webhooks.py — Event handler: invoice.payment_failed
# ===================================================================

class TestHandlePaymentFailed:
    """WH-04: Payment failure → tenant flagged."""

    @pytest.mark.asyncio
    async def test_payment_failed_flags_tenant(self):
        from src.integrations.stripe_webhooks import handle_payment_failed

        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_wh_fail",
        )
        await activate_tenant(stripe_customer_id="cus_wh_fail")

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

        t = await get_tenant(stripe_customer_id="cus_wh_fail")
        assert t.status == TenantStatus.PAST_DUE


# ===================================================================
# stripe_webhooks.py — Event handler: invoice.payment_succeeded
# ===================================================================

class TestHandlePaymentSucceeded:
    """WH-05: Payment success → usage reset on renewal."""

    @pytest.mark.asyncio
    async def test_renewal_resets_usage(self):
        from src.integrations.stripe_webhooks import handle_payment_succeeded

        await provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            stripe_customer_id="cus_wh_pay",
        )
        await activate_tenant(stripe_customer_id="cus_wh_pay")

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


# ---------------------------------------------------------------------------
# Superadmin auto-provisioning
# ---------------------------------------------------------------------------


class TestAutoProvisionSuperadmin:
    """Test auto_provision_superadmin utility."""

    @pytest.mark.asyncio
    async def test_creates_superadmin_member(self):
        mock_repo = AsyncMock()
        with patch("src.multi_tenant.repository.TeamMemberRepository", return_value=mock_repo):
            key = await auto_provision_superadmin("tenant-001", "owner@example.com")
        assert key is not None
        assert key.startswith("ar_user_")
        mock_repo.create.assert_called_once()
        args = mock_repo.create.call_args
        assert args[0][0] == "tenant-001"  # tenant_id
        doc = args[0][1]
        assert doc.email == "owner@example.com"
        assert doc.role.value == "superadmin"
        assert doc.invited_by == "system"

    @pytest.mark.asyncio
    async def test_returns_none_without_email(self):
        key = await auto_provision_superadmin("tenant-001", "")
        assert key is None

    @pytest.mark.asyncio
    async def test_returns_none_on_failure(self):
        mock_repo = AsyncMock()
        mock_repo.create.side_effect = RuntimeError("Cosmos unavailable")
        with patch("src.multi_tenant.repository.TeamMemberRepository", return_value=mock_repo):
            key = await auto_provision_superadmin("tenant-001", "owner@example.com")
        assert key is None

    @pytest.mark.asyncio
    async def test_key_hash_stored(self):
        mock_repo = AsyncMock()
        with patch("src.multi_tenant.repository.TeamMemberRepository", return_value=mock_repo):
            key = await auto_provision_superadmin("tenant-001", "owner@example.com")
        doc = mock_repo.create.call_args[0][1]
        assert doc.user_api_key_hash is not None
        assert doc.user_api_key_prefix == key[:12] + "..."

    @pytest.mark.asyncio
    async def test_member_id_format(self):
        mock_repo = AsyncMock()
        with patch("src.multi_tenant.repository.TeamMemberRepository", return_value=mock_repo):
            await auto_provision_superadmin("tenant-001", "owner@example.com")
        doc = mock_repo.create.call_args[0][1]
        assert doc.id == "tenant-001:owner@example.com"
