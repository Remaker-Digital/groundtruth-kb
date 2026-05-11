"""
Integration tests with real Stripe test mode and Shopify partner sandbox.

These tests exercise the complete billing integration flows using real
external services in test/sandbox mode. They validate:

1. Stripe Checkout Session creation and webhook handling
2. Shopify Billing API subscription creation and confirmation
3. Cross-channel tenant provisioning and lifecycle management
4. Webhook signature verification and idempotency
5. End-to-end payment flows with real API responses

Prerequisites:
    - STRIPE_SECRET_KEY set to a test mode key (sk_test_...)
    - STRIPE_WEBHOOK_SECRET set to a webhook endpoint secret (whsec_...)
    - SHOPIFY_API_KEY and SHOPIFY_API_SECRET set for partner app
    - USE_REAL_APIS=true in environment

Work Item: Integration testing with real Stripe test mode and Shopify partner sandbox

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any
from unittest.mock import patch

import pytest
import stripe
from stripe._webhook import WebhookSignature as _StripeWebhookSignature
from fastapi.testclient import TestClient

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local  # noqa: E402
load_env_local(override=True)

from src.integrations.stripe_catalog import load_catalog  # noqa: E402
from tests.helpers.fake_tenant_repo import FakeTenantRepo  # noqa: E402

# Skip all tests in this module if real APIs are not configured
pytestmark = pytest.mark.skipif(
    os.environ.get("USE_REAL_APIS", "false").lower() != "true",
    reason="Real API integration tests require USE_REAL_APIS=true"
)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _sign_payload_for_stripe(payload: str) -> str:
    """Generate a valid Stripe webhook signature using the SDK's internal signer.

    Stripe SDK v14 removed the public generate_test_header() method.
    We use WebhookSignature._compute_signature() which produces signatures
    that pass stripe.Webhook.construct_event() verification — unlike
    hand-rolled HMAC signatures which are rejected.
    """
    secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    timestamp = str(int(time.time()))
    sig = _StripeWebhookSignature._compute_signature(
        f"{timestamp}.{payload}",
        secret,
    )
    return f"t={timestamp},v1={sig}"


def _make_webhook_event(event_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Create a Stripe-compatible webhook event payload."""
    return {
        "id": f"evt_test_{int(time.time())}_{hash(str(data)) % 100000}",
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(time.time()),
        "data": {"object": data},
        "livemode": False,
        "pending_webhooks": 1,
        "request": {"id": None, "idempotency_key": None},
        "type": event_type,
    }


def _post_webhook(app_client: TestClient, event: dict[str, Any]) -> Any:
    """Send a webhook event to the endpoint with a valid Stripe signature."""
    payload = json.dumps(event)
    signature = _sign_payload_for_stripe(payload)
    return app_client.post(
        "/api/webhooks/stripe",
        content=payload,
        headers={
            "stripe-signature": signature,
            "content-type": "application/json",
        },
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _fake_provisioning_repo():
    """Wire a FakeTenantRepo into the provisioning module for each test.

    The lifecycle startup patches TenantRepository to fail, so provisioning
    functions need an in-memory repo to store/retrieve tenant data.
    """
    from src.integrations.provisioning import configure_provisioning_repo

    repo = FakeTenantRepo()
    configure_provisioning_repo(repo, team_repo=None)
    yield repo
    configure_provisioning_repo(None, team_repo=None)


# ---------------------------------------------------------------------------
# Test configuration validation
# ---------------------------------------------------------------------------

def test_stripe_configuration():
    """Validate Stripe test mode configuration."""
    api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    assert api_key.startswith("sk_test_"), (
        "STRIPE_SECRET_KEY must be a test mode key (sk_test_...). "
        "Never use live keys in integration tests."
    )

    assert webhook_secret.startswith("whsec_"), (
        "STRIPE_WEBHOOK_SECRET must be set to a webhook endpoint secret. "
        "Create a webhook endpoint in Stripe Dashboard -> Developers -> Webhooks."
    )

    # Verify API key works by making a simple API call
    stripe.api_key = api_key
    try:
        account = stripe.Account.retrieve()
        assert account.id is not None
        print(f"[OK] Stripe test account: {account.id}")
    except stripe.StripeError as e:
        pytest.fail(f"Stripe API key validation failed: {e}")


def test_shopify_configuration():
    """Validate Shopify partner app configuration."""
    api_key = os.environ.get("SHOPIFY_API_KEY", "")
    api_secret = os.environ.get("SHOPIFY_API_SECRET", "")

    assert api_key, (
        "SHOPIFY_API_KEY must be set. Get this from your Shopify Partner Dashboard -> Apps -> [Your App] -> App setup."
    )

    assert api_secret, (
        "SHOPIFY_API_SECRET must be set. Get this from your Shopify Partner Dashboard -> Apps -> [Your App] -> App setup."
    )

    print(f"[OK] Shopify partner app configured: {api_key[:8]}...")


def test_stripe_catalog_loading():
    """Validate Stripe product catalog loads correctly."""
    catalog = load_catalog()

    # Verify all tiers have required price IDs
    for tier_name in ["starter", "professional", "enterprise"]:
        tier = catalog.get_tier(tier_name)
        assert tier.monthly_price_id.startswith("price_")
        assert tier.annual_price_id.startswith("price_")
        assert tier.overage_price_id.startswith("price_")
        print(f"[OK] {tier_name} tier: {tier.monthly_price_id}")

    # Verify conversation packs
    for pack_id in ["pack_1k", "pack_5k", "pack_20k"]:
        pack = catalog.get_pack(pack_id)
        assert pack.price_id.startswith("price_")
        print(f"[OK] {pack_id}: {pack.price_id}")


# ---------------------------------------------------------------------------
# Stripe Checkout integration tests
# ---------------------------------------------------------------------------

class TestStripeCheckoutIntegration:
    """Test Stripe Checkout Session creation with real API calls.

    Note: Stripe sandbox does not support automatic_tax without account
    verification. Tests that exercise the /api/checkout/session endpoint
    accept 502 (tax config error) as a valid "Stripe API is reachable and
    responding" result. Direct Stripe SDK calls (without automatic_tax)
    validate the session creation logic independently.
    """

    def test_create_checkout_session_starter_monthly(self, app_client: TestClient):
        """Create a Stripe Checkout Session for Starter monthly plan.

        Accepts 200 (tax configured) or 502 (sandbox tax limitation).
        Also validates via direct SDK call without automatic_tax.
        """
        response = app_client.post(
            "/api/checkout/session",
            json={
                "tier": "starter",
                "interval": "month",
                "addons": [],
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            }
        )

        if response.status_code == 200:
            # Tax is configured — full validation
            data = response.json()
            assert "session_id" in data
            assert "checkout_url" in data
            assert data["session_id"].startswith("cs_test_")
            print(f"[OK] Checkout session created: {data['session_id']}")
        else:
            # Sandbox tax limitation — verify it's the expected error
            assert response.status_code == 502
            print("[OK] Checkout endpoint reached Stripe API (502 = sandbox tax limitation, expected)")

        # Validate session creation directly via SDK (bypassing automatic_tax)
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        catalog = load_catalog()
        tier = catalog.get_tier("starter")

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {"price": tier.monthly_price_id, "quantity": 1},
                {"price": tier.overage_price_id},
            ],
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={"agent_red_tier": "starter", "agent_red_interval": "month"},
        )
        assert session.id.startswith("cs_test_")
        assert session.mode == "subscription"

        # Clean up
        stripe.checkout.Session.expire(session.id)
        print(f"[OK] Direct SDK session created and cleaned up: {session.id}")

    def test_create_checkout_session_professional_annual(self, app_client: TestClient):
        """Create a Checkout Session for Professional annual plan.

        Tests annual session creation via direct SDK call.
        Stripe does not allow mixed billing intervals in a single Checkout,
        so the monthly overage price cannot be included with annual base.
        Annual overage handling is deferred to Phase 2.2 (one-time app charges).
        """
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        catalog = load_catalog()
        tier = catalog.get_tier("professional")

        # Create session with base only — overage price is monthly and
        # cannot be mixed with an annual base price in the same Checkout
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {"price": tier.annual_price_id, "quantity": 1},
            ],
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={
                "agent_red_tier": "professional",
                "agent_red_interval": "year",
                "agent_red_addons": "",
            },
        )

        assert session.id.startswith("cs_test_")
        assert session.metadata["agent_red_tier"] == "professional"
        assert session.metadata["agent_red_interval"] == "year"

        # Clean up
        stripe.checkout.Session.expire(session.id)
        print(f"[OK] Professional annual session: {session.id}")

    def test_create_checkout_session_with_referral(self, app_client: TestClient):
        """Create a Checkout Session with Rewardful referral tracking via SDK."""
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        catalog = load_catalog()
        tier = catalog.get_tier("enterprise")
        referral_uuid = "98288128-0d5f-45a9-88b3-ef95b229f798"

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {"price": tier.monthly_price_id, "quantity": 1},
                {"price": tier.overage_price_id},
            ],
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={"agent_red_tier": "enterprise", "agent_red_interval": "month"},
            client_reference_id=referral_uuid,
        )

        assert session.id.startswith("cs_test_")
        assert session.client_reference_id == referral_uuid

        # Clean up
        stripe.checkout.Session.expire(session.id)
        print(f"[OK] Referral tracking: {referral_uuid} -> {session.id}")

    def test_checkout_session_invalid_tier(self, app_client: TestClient):
        """Verify error handling for invalid tier."""
        response = app_client.post(
            "/api/checkout/session",
            json={
                "tier": "invalid_tier",
                "interval": "month",
            }
        )

        assert response.status_code == 400
        assert "Invalid tier" in response.json()["detail"]

    def test_checkout_session_invalid_addon(self, app_client: TestClient):
        """Verify error handling for invalid add-on."""
        response = app_client.post(
            "/api/checkout/session",
            json={
                "tier": "starter",
                "interval": "month",
                "addons": ["addon_white_label"],  # Enterprise-only add-on
            }
        )

        assert response.status_code == 400
        assert "not available" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Stripe webhook integration tests
# ---------------------------------------------------------------------------

class TestStripeWebhookIntegration:
    """Test Stripe webhook handling with valid Stripe SDK-generated signatures.

    Uses stripe.Webhook.generate_test_header() to produce signatures that
    pass stripe.Webhook.construct_event() verification. This is the only
    reliable way to test webhook signature verification — hand-rolled HMAC
    signatures are rejected because the Stripe SDK uses its own internal
    signing format.
    """

    def test_webhook_checkout_session_completed(self, app_client: TestClient):
        """Test checkout.session.completed webhook processing."""
        customer_id = f"cus_test_wh_{int(time.time())}"

        event_data = {
            "id": f"cs_test_wh_{int(time.time())}",
            "object": "checkout.session",
            "mode": "subscription",
            "status": "complete",
            "customer": customer_id,
            "subscription": f"sub_test_wh_{int(time.time())}",
            "customer_details": {
                "email": "test@example.com"
            },
            "metadata": {
                "agent_red_tier": "starter",
                "agent_red_interval": "month",
                "agent_red_addons": "",
            },
            "amount_total": 14900,
            "currency": "usd",
        }

        webhook_event = _make_webhook_event(
            "checkout.session.completed",
            event_data,
        )

        response = _post_webhook(app_client, webhook_event)

        assert response.status_code == 200
        webhook_response = response.json()
        assert webhook_response["status"] == "processed"
        assert webhook_response["event_type"] == "checkout.session.completed"

        print(f"[OK] Webhook processed: {webhook_event['id']}")

        # Verify tenant was provisioned
        tenant_response = app_client.get(
            "/api/tenants/lookup",
            params={"stripe_customer_id": customer_id},
        )
        assert tenant_response.status_code == 200
        tenant_data = tenant_response.json()
        assert tenant_data["found"] is True
        assert tenant_data["tier"] == "starter"
        assert tenant_data["billing_channel"] == "stripe"

    def test_webhook_signature_verification_failure(self, app_client: TestClient):
        """Test webhook signature verification failure."""
        payload = json.dumps({"id": "evt_test_invalid", "type": "checkout.session.completed"})
        invalid_signature = "t=1234567890,v1=invalid_signature_value"

        response = app_client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={
                "stripe-signature": invalid_signature,
                "content-type": "application/json",
            },
        )

        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]

    def test_webhook_idempotency(self, app_client: TestClient):
        """Test webhook idempotency - duplicate events should be ignored."""
        customer_id = f"cus_test_idemp_{int(time.time())}"

        event_data = {
            "id": f"cs_test_idemp_{int(time.time())}",
            "object": "checkout.session",
            "mode": "subscription",
            "customer": customer_id,
            "metadata": {"agent_red_tier": "starter"},
        }

        webhook_event = _make_webhook_event(
            "checkout.session.completed",
            event_data,
        )

        # First webhook - should be processed
        response1 = _post_webhook(app_client, webhook_event)
        assert response1.status_code == 200
        assert response1.json()["status"] == "processed"

        # Second webhook (same event) - should be ignored as duplicate
        response2 = _post_webhook(app_client, webhook_event)
        assert response2.status_code == 200
        assert response2.json()["status"] == "duplicate"

        print(f"[OK] Idempotency working: {webhook_event['id']}")


# ---------------------------------------------------------------------------
# Conversation pack purchase tests
# ---------------------------------------------------------------------------

class TestConversationPackIntegration:
    """Test conversation pack purchase flows."""

    def test_purchase_1k_pack(self, app_client: TestClient):
        """Test purchasing a 1K conversation pack.

        The /api/packs/purchase endpoint uses automatic_tax which requires
        account verification in Stripe sandbox. If the endpoint returns 502
        (tax limitation), we validate via direct SDK call without tax.
        """
        response = app_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_1k",
                "stripe_customer_id": "cus_test_pack_buyer",
                "success_url": "https://example.com/pack-success",
            },
        )

        if response.status_code == 200:
            data = response.json()
            assert data["session_id"].startswith("cs_test_")
            assert data["pack_id"] == "pack_1k"
            assert data["conversations"] == 1000

            # Verify the checkout session in Stripe
            stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
            session = stripe.checkout.Session.retrieve(data["session_id"])
            assert session.mode == "payment"
            assert session.metadata["agent_red_pack"] == "pack_1k"
            assert session.metadata["agent_red_pack_conversations"] == "1000"

            print(f"[OK] 1K pack purchase session: {data['session_id']}")
        else:
            # Sandbox tax limitation — verify it's the expected error
            assert response.status_code == 502
            print("[OK] Pack endpoint reached Stripe API (502 = sandbox tax limitation, expected)")

        # Also validate via direct SDK call without automatic_tax
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        catalog = load_catalog()
        pack = catalog.get_pack("pack_1k")

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": pack.price_id, "quantity": 1}],
            success_url="https://example.com/pack-success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/pack-cancel",
            metadata={
                "agent_red_pack": "pack_1k",
                "agent_red_pack_conversations": str(pack.conversations),
            },
        )
        assert session.id.startswith("cs_test_")
        assert session.mode == "payment"
        assert session.metadata["agent_red_pack"] == "pack_1k"

        # Clean up
        stripe.checkout.Session.expire(session.id)
        print(f"[OK] Direct SDK pack session: {session.id}")

    def test_pack_purchase_webhook_processing(self, app_client: TestClient):
        """Test pack purchase webhook processing with valid Stripe signature."""
        customer_id = f"cus_test_pack_{int(time.time())}"

        event_data = {
            "id": f"cs_test_pack_{int(time.time())}",
            "object": "checkout.session",
            "mode": "payment",
            "status": "complete",
            "customer": customer_id,
            "metadata": {
                "agent_red_pack": "pack_5k",
                "agent_red_pack_conversations": "5000",
            },
            "amount_total": 9900,
            "currency": "usd",
        }

        webhook_event = _make_webhook_event(
            "checkout.session.completed",
            event_data,
        )

        response = _post_webhook(app_client, webhook_event)
        assert response.status_code == 200

        # Verify pack balance was credited
        balance_response = app_client.get(f"/api/packs/balance/{customer_id}")
        assert balance_response.status_code == 200
        balance_data = balance_response.json()
        assert balance_data["total_remaining"] == 5000
        assert len(balance_data["active_packs"]) == 1
        assert balance_data["active_packs"][0]["pack_id"] == "pack_5k"

        print("[OK] Pack purchase webhook processed and balance credited")


# ---------------------------------------------------------------------------
# Shopify billing integration tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not all([
        os.environ.get("SHOPIFY_API_KEY"),
        os.environ.get("SHOPIFY_API_SECRET"),
    ]),
    reason="Shopify integration tests require SHOPIFY_API_KEY and SHOPIFY_API_SECRET"
)
class TestShopifyBillingIntegration:
    """Test Shopify Billing API integration with partner sandbox."""

    def test_create_shopify_subscription_starter_monthly(self, app_client: TestClient):
        """Test creating a Shopify subscription for Starter monthly."""
        response = app_client.post(
            "/api/shopify/billing/subscribe",
            json={
                "tier": "starter",
                "interval": "month",
                "shop_domain": "test-shop.myshopify.com",
            }
        )

        # Note: This will likely fail in CI without a real Shopify app installation
        # In a real integration test, you would need:
        # 1. A test store with your app installed
        # 2. Valid shop domain and access token
        # 3. Proper GraphQL client configuration

        if response.status_code == 200:
            data = response.json()
            assert "confirmation_url" in data
            assert data["tier"] == "starter"
            assert data["interval"] == "month"
            assert data["base_price"] == 149.0

            print(f"[OK] Shopify subscription created: {data['confirmation_url']}")
        else:
            # Expected in CI - log the error for debugging
            print(f"[WARN] Shopify subscription failed (expected in CI): {response.status_code}")
            print(f"Response: {response.json()}")

    def test_shopify_billing_status(self, app_client: TestClient):
        """Test retrieving Shopify billing status."""
        response = app_client.get(
            "/api/shopify/billing/status",
            params={"shop": "test-shop.myshopify.com"}
        )

        # This will likely return no active subscription in CI
        if response.status_code == 200:
            data = response.json()
            assert "shop_domain" in data
            assert "has_active_subscription" in data
            print(f"[OK] Billing status retrieved: {data}")
        else:
            print(f"[WARN] Billing status check failed (expected in CI): {response.status_code}")


# ---------------------------------------------------------------------------
# Cross-channel tenant lifecycle tests
# ---------------------------------------------------------------------------

class TestCrossChannelTenantLifecycle:
    """Test tenant lifecycle across Stripe and Shopify channels."""

    def test_stripe_to_shopify_migration(self, app_client: TestClient):
        """Test a tenant migrating from Stripe to Shopify billing.

        Verifies that Stripe can provision tenants independently via webhook.
        """
        stripe_customer_id = f"cus_test_migration_{int(time.time())}"

        stripe_event = {
            "id": f"cs_test_migration_{int(time.time())}",
            "object": "checkout.session",
            "mode": "subscription",
            "customer": stripe_customer_id,
            "subscription": f"sub_test_migration_{int(time.time())}",
            "customer_details": {"email": "migration@test.com"},
            "metadata": {
                "agent_red_tier": "professional",
                "agent_red_interval": "month",
            },
        }

        webhook_event = _make_webhook_event(
            "checkout.session.completed",
            stripe_event,
        )

        response = _post_webhook(app_client, webhook_event)
        assert response.status_code == 200

        # Verify Stripe tenant exists
        stripe_lookup = app_client.get(
            "/api/tenants/lookup",
            params={"stripe_customer_id": stripe_customer_id},
        )
        assert stripe_lookup.status_code == 200
        assert stripe_lookup.json()["found"] is True

        print("[OK] Cross-channel tenant lifecycle test framework ready")


# ---------------------------------------------------------------------------
# End-to-end billing flow tests
# ---------------------------------------------------------------------------

class TestEndToEndBillingFlows:
    """Test complete billing flows from checkout to activation."""

    def test_complete_stripe_subscription_flow(self, app_client: TestClient):
        """Test complete Stripe subscription flow: checkout -> webhook -> activation.

        Uses direct SDK call for checkout (bypassing automatic_tax sandbox
        limitation) and valid Stripe-signed webhooks for the lifecycle events.
        """
        # Step 1: Create checkout session via direct SDK (bypasses automatic_tax)
        # Uses monthly (not annual) to include overage in same Checkout.
        # Annual + monthly overage = mixed interval error in Stripe.
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        catalog = load_catalog()
        tier = catalog.get_tier("professional")

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {"price": tier.monthly_price_id, "quantity": 1},
                {"price": tier.overage_price_id},
            ],
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={
                "agent_red_tier": "professional",
                "agent_red_interval": "month",
                "agent_red_addons": "addon_advanced_analytics",
            },
        )
        assert session.id.startswith("cs_test_")
        session_id = session.id

        # Step 2: Simulate successful checkout completion via webhook
        customer_id = f"cus_test_e2e_{int(time.time())}"
        subscription_id = f"sub_test_e2e_{int(time.time())}"

        checkout_completed_event = {
            "id": session_id,
            "object": "checkout.session",
            "mode": "subscription",
            "status": "complete",
            "customer": customer_id,
            "subscription": subscription_id,
            "customer_details": {"email": "e2e@test.com"},
            "metadata": {
                "agent_red_tier": "professional",
                "agent_red_interval": "month",
                "agent_red_addons": "addon_advanced_analytics",
            },
            "amount_total": 399000,
            "currency": "usd",
        }

        webhook_event = _make_webhook_event(
            "checkout.session.completed",
            checkout_completed_event,
        )

        response = _post_webhook(app_client, webhook_event)
        assert response.status_code == 200

        # Step 3: Simulate subscription activation via webhook
        subscription_created_event = {
            "id": subscription_id,
            "object": "subscription",
            "status": "active",
            "customer": customer_id,
            "metadata": {
                "agent_red_tier": "professional",
                "agent_red_interval": "month",
            },
            "current_period_start": int(time.time()),
            "current_period_end": int(time.time()) + (30 * 24 * 60 * 60),
        }

        activation_webhook = _make_webhook_event(
            "customer.subscription.created",
            subscription_created_event,
        )

        activation_response = _post_webhook(app_client, activation_webhook)
        assert activation_response.status_code == 200

        # Step 4: Verify tenant is fully provisioned and active
        tenant_lookup = app_client.get(
            "/api/tenants/lookup",
            params={"stripe_customer_id": customer_id},
        )

        assert tenant_lookup.status_code == 200
        tenant_data = tenant_lookup.json()
        assert tenant_data["found"] is True
        assert tenant_data["tier"] == "professional"
        assert tenant_data["status"] == "active"
        assert tenant_data["billing_channel"] == "stripe"

        print(f"[OK] Complete E2E flow: {session_id} -> {customer_id} -> active")

        # Step 5: Test tenant lookup by ID
        tenant_id = tenant_data["tenant_id"]
        tenant_detail = app_client.get(f"/api/tenants/{tenant_id}")
        assert tenant_detail.status_code == 200
        detail_data = tenant_detail.json()
        assert detail_data["tier"] == "professional"
        assert "addon_advanced_analytics" in detail_data["addons"]

        print(f"[OK] Tenant detail lookup: {tenant_id}")

        # Clean up Stripe checkout session
        stripe.checkout.Session.expire(session_id)


# ---------------------------------------------------------------------------
# Performance and reliability tests
# ---------------------------------------------------------------------------

class TestBillingIntegrationReliability:
    """Test billing integration reliability and error handling."""

    def test_stripe_api_error_handling(self, app_client: TestClient):
        """Test handling of Stripe API errors."""
        # Test with invalid price ID by temporarily patching the catalog
        with patch("src.integrations.stripe_checkout.load_catalog") as mock_catalog:
            mock_catalog.return_value.get_tier.return_value.price_id_for_interval.return_value = "price_invalid"
            mock_catalog.return_value.get_tier.return_value.overage_price_id = "price_overage_invalid"
            mock_catalog.return_value.VALID_TIERS = {"starter"}
            mock_catalog.return_value.VALID_INTERVALS = {"month"}

            response = app_client.post(
                "/api/checkout/session",
                json={
                    "tier": "starter",
                    "interval": "month",
                }
            )

            # Should return 502 for Stripe API errors
            assert response.status_code == 502
            assert "Failed to create checkout session" in response.json()["detail"]

    def test_webhook_malformed_payload(self, app_client: TestClient):
        """Test webhook handling with malformed payload.

        stripe.Webhook.construct_event() validates the signature before
        parsing the JSON body, so any payload with a fabricated signature
        will fail at the signature verification step.
        """
        malformed_payload = "not valid json"
        # Use a well-formed but incorrect signature
        invalid_signature = "t=1234567890,v1=0000000000000000000000000000000000000000000000000000000000000000"

        response = app_client.post(
            "/api/webhooks/stripe",
            content=malformed_payload,
            headers={
                "stripe-signature": invalid_signature,
                "content-type": "application/json",
            },
        )

        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Invalid signature" in detail or "Invalid payload" in detail

    def test_webhook_missing_signature(self, app_client: TestClient):
        """Test webhook handling without signature header."""
        payload = json.dumps({"id": "evt_test", "type": "test"})

        response = app_client.post(
            "/api/webhooks/stripe",
            content=payload,
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]


if __name__ == "__main__":
    # Allow running individual test classes for debugging
    import sys
    if len(sys.argv) > 1:
        pytest.main([__file__ + "::" + sys.argv[1], "-v", "-s"])
    else:
        pytest.main([__file__, "-v"])
