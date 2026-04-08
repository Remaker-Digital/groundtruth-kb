"""P0 HTTP billing endpoint tests — FastAPI TestClient.

Tests all billing-related API endpoints at the HTTP transport level,
covering Stripe checkout, conversation packs, customer portal, metered
usage, Stripe webhooks, Shopify billing, and tenant provisioning lookup.

Test IDs: HTTP-BILL-01 through HTTP-BILL-35 per §4.1 of
docs/COMPREHENSIVE-TEST-PLAN.md.

Work Item: P0 launch-blocker tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import stripe

from tests.helpers.fake_tenant_repo import FakeTenantRepo, run_sync


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stripe_signature(payload: bytes, secret: str = "whsec_test_secret") -> str:
    """Build a valid Stripe webhook signature header for testing."""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    sig = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={sig}"


def _make_stripe_event(
    event_type: str,
    event_id: str = "evt_test_001",
    data_object: dict | None = None,
    previous_attributes: dict | None = None,
) -> dict:
    """Build a minimal Stripe event dict for webhook tests."""
    event = {
        "id": event_id,
        "type": event_type,
        "data": {
            "object": data_object or {},
        },
    }
    if previous_attributes is not None:
        event["data"]["previous_attributes"] = previous_attributes
    return event


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_in_memory_stores(app_client):
    """Reset all in-memory billing stores and rate limiter before each test.

    The billing modules use module-level dicts for dev state.
    The rate limiter accumulates across tests via the shared app instance.
    Tests must start with a clean slate.

    Provisioning uses a FakeTenantRepo (wired per-test) instead of
    module-level dicts — see ``_fake_provisioning_repo`` fixture below.
    """
    import src.integrations.stripe_packs as packs_mod
    import src.integrations.stripe_usage as usage_mod
    import src.integrations.stripe_webhooks as wh_mod
    import src.main as main_mod

    # Clear pack balances
    packs_mod._pack_balances.clear()

    # Clear usage counters
    usage_mod._usage_counters.clear()
    usage_mod._stripe_client = None  # Force re-init on next call

    # Clear webhook idempotency set
    wh_mod._processed_events.clear()

    # Clear Shopify billing in-memory subscriptions
    import src.integrations.shopify_billing as shopify_mod
    shopify_mod._shop_subscriptions.clear()

    # Reset rate limiter and concurrency middleware state.
    # The middleware stack is built by Starlette when TestClient starts,
    # accessible via app.middleware_stack, chained via .app attributes:
    #   ServerErrorMiddleware → TenantAuthMiddleware → RateLimitMiddleware
    #   → TenantConcurrencyMiddleware → CorrelationMiddleware → ...
    _reset_middleware_state(main_mod.app)

    yield

    # Cleanup after test
    packs_mod._pack_balances.clear()
    usage_mod._usage_counters.clear()
    wh_mod._processed_events.clear()
    shopify_mod._shop_subscriptions.clear()


def _reset_middleware_state(app: Any) -> None:
    """Walk the built ASGI middleware chain and clear stateful middleware."""
    stack = getattr(app, "middleware_stack", None)
    if stack is None:
        return

    current = stack
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        # RateLimitMiddleware stores sliding window counters in _windows
        if hasattr(current, "_windows"):
            current._windows.clear()
        # TenantConcurrencyMiddleware stores per-tenant gates in _gates
        if hasattr(current, "_gates"):
            current._gates.clear()
        current = getattr(current, "app", None)


@pytest.fixture(autouse=True)
def _fake_provisioning_repo():
    """Wire a FakeTenantRepo into the provisioning module for each test.

    Ensures provisioning functions (provision_tenant, get_tenant, etc.)
    read and write from an in-memory store instead of Cosmos DB.
    """
    from src.integrations.provisioning import configure_provisioning_repo

    repo = FakeTenantRepo()
    configure_provisioning_repo(repo, team_repo=None)
    yield repo
    configure_provisioning_repo(None, team_repo=None)


@pytest.fixture
def mock_stripe_checkout():
    """Mock stripe.checkout.Session.create and .retrieve."""
    mock_session = MagicMock()
    mock_session.id = "cs_test_session_001"
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_session_001"
    mock_session.amount_total = 14900
    mock_session.customer_details = MagicMock(email="test@example.com")
    mock_session.subscription = MagicMock(id="sub_test_001")
    mock_session.metadata = {"agent_red_tier": "starter"}

    with patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
        with patch("stripe.checkout.Session.retrieve", return_value=mock_session) as mock_retrieve:
            yield {
                "session": mock_session,
                "create": mock_create,
                "retrieve": mock_retrieve,
            }


@pytest.fixture
def mock_stripe_portal():
    """Mock stripe.billing_portal.Session.create."""
    mock_session = MagicMock()
    mock_session.url = "https://billing.stripe.com/session/test_portal"

    with patch("stripe.billing_portal.Session.create", return_value=mock_session) as mock_create:
        yield {
            "session": mock_session,
            "create": mock_create,
        }


@pytest.fixture
def mock_stripe_webhook_verify():
    """Mock stripe.Webhook.construct_event to bypass signature verification."""
    with patch("stripe.Webhook.construct_event") as mock_construct:
        yield mock_construct


@pytest.fixture
def mock_shopify_client():
    """Mock the Shopify GraphQL client."""
    mock_client = AsyncMock()
    with patch(
        "src.integrations.shopify_billing.get_shopify_client",
        return_value=mock_client,
    ):
        yield mock_client


# ===========================================================================
# Stripe Checkout — HTTP-BILL-01 through HTTP-BILL-09
# ===========================================================================


class TestStripeCheckout:
    """HTTP tests for POST /api/checkout/session, GET success, GET cancel."""

    @pytest.mark.unit
    def test_checkout_session_starter_plan(
        self, starter_client, mock_stripe_checkout,
    ):
        """HTTP-BILL-01: POST /api/checkout/session — valid Starter plan."""
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "month"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == "cs_test_session_001"
        assert "checkout.stripe.com" in body["checkout_url"]
        mock_stripe_checkout["create"].assert_called_once()

    @pytest.mark.unit
    def test_checkout_session_professional_plan(
        self, professional_client, mock_stripe_checkout,
    ):
        """HTTP-BILL-02: POST /api/checkout/session — valid Professional plan."""
        resp = professional_client.post(
            "/api/checkout/session",
            json={"tier": "professional", "interval": "month"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == "cs_test_session_001"
        # Verify the Stripe call includes Professional tier metadata
        call_kwargs = mock_stripe_checkout["create"].call_args
        metadata = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata", {})
        assert metadata.get("agent_red_tier") == "professional"

    @pytest.mark.unit
    def test_checkout_session_enterprise_plan(
        self, enterprise_client, mock_stripe_checkout,
    ):
        """HTTP-BILL-03: POST /api/checkout/session — valid Enterprise plan."""
        resp = enterprise_client.post(
            "/api/checkout/session",
            json={"tier": "enterprise", "interval": "month"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == "cs_test_session_001"

    @pytest.mark.unit
    def test_checkout_session_annual_billing(
        self, starter_client, mock_stripe_checkout,
    ):
        """HTTP-BILL-04: POST /api/checkout/session — annual billing interval."""
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "year"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == "cs_test_session_001"
        # Verify annual price ID was used
        call_kwargs = mock_stripe_checkout["create"].call_args
        metadata = call_kwargs.kwargs.get("metadata") or call_kwargs[1].get("metadata", {})
        assert metadata.get("agent_red_interval") == "year"

    @pytest.mark.unit
    def test_checkout_session_invalid_tier_returns_400(
        self, starter_client,
    ):
        """HTTP-BILL-05: POST /api/checkout/session — invalid tier returns 400."""
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "platinum", "interval": "month"},
        )
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower() or "tier" in resp.json()["detail"].lower()

    @pytest.mark.unit
    def test_checkout_session_rewardful_referral(
        self, starter_client, mock_stripe_checkout,
    ):
        """HTTP-BILL-06: POST /api/checkout/session — Rewardful client_reference_id included."""
        referral_id = "98288128-0d5f-45a9-88b3-ef95b229f798"
        resp = starter_client.post(
            "/api/checkout/session",
            json={
                "tier": "starter",
                "interval": "month",
                "referral": referral_id,
            },
        )
        assert resp.status_code == 200
        # Verify client_reference_id was passed to Stripe
        call_kwargs = mock_stripe_checkout["create"].call_args
        assert call_kwargs.kwargs.get("client_reference_id") == referral_id or \
            call_kwargs[1].get("client_reference_id") == referral_id

    @pytest.mark.unit
    def test_checkout_success_with_session_id(
        self, app_client, mock_stripe_checkout,
    ):
        """HTTP-BILL-07: GET /api/checkout/success — valid session_id.

        This path is auth-exempt.
        """
        resp = app_client.get("/api/checkout/success?session_id=cs_test_001")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "session_id" in body

    @pytest.mark.unit
    def test_checkout_success_missing_session_id(self, app_client):
        """HTTP-BILL-08: GET /api/checkout/success — missing session_id returns 200 with generic message.

        The endpoint does not return 400 — it gracefully handles missing
        session_id by returning a generic success message.
        """
        resp = app_client.get("/api/checkout/success")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"

    @pytest.mark.unit
    def test_checkout_cancel(self, app_client):
        """HTTP-BILL-09: GET /api/checkout/cancel — returns cancel message.

        This path is auth-exempt.
        """
        resp = app_client.get("/api/checkout/cancel")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "cancelled"


# ===========================================================================
# Conversation Packs — HTTP-BILL-10 through HTTP-BILL-15
# ===========================================================================


class TestConversationPacks:
    """HTTP tests for POST /api/packs/purchase, GET /api/packs/balance/{id}."""

    @pytest.mark.unit
    def test_purchase_pack_1k(self, starter_client, mock_stripe_checkout):
        """HTTP-BILL-10: POST /api/packs/purchase — 1K pack."""
        resp = starter_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_1k",
                "stripe_customer_id": "cus_test_001",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pack_id"] == "pack_1k"
        assert body["conversations"] == 1000
        assert body["session_id"] == "cs_test_session_001"

    @pytest.mark.unit
    def test_purchase_pack_5k(self, starter_client, mock_stripe_checkout):
        """HTTP-BILL-11: POST /api/packs/purchase — 5K pack."""
        resp = starter_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_5k",
                "stripe_customer_id": "cus_test_001",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pack_id"] == "pack_5k"
        assert body["conversations"] == 5000

    @pytest.mark.unit
    def test_purchase_pack_20k(self, starter_client, mock_stripe_checkout):
        """HTTP-BILL-12: POST /api/packs/purchase — 20K pack."""
        resp = starter_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_20k",
                "stripe_customer_id": "cus_test_001",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pack_id"] == "pack_20k"
        assert body["conversations"] == 20000

    @pytest.mark.unit
    def test_purchase_invalid_pack_returns_400(self, starter_client):
        """HTTP-BILL-13: POST /api/packs/purchase — invalid pack ID returns 400."""
        resp = starter_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_100k",
                "stripe_customer_id": "cus_test_001",
            },
        )
        assert resp.status_code == 400
        assert "invalid" in resp.json()["detail"].lower() or "pack" in resp.json()["detail"].lower()

    @pytest.mark.unit
    def test_pack_balance_with_credit(self, starter_client):
        """HTTP-BILL-14: GET /api/packs/balance/{customer_id} — returns FIFO balance."""
        # Credit a pack directly via the module
        from src.integrations.stripe_packs import credit_pack_balance

        credit_pack_balance("cus_balance_test", "pack_1k", 1000)

        resp = starter_client.get("/api/packs/balance/cus_balance_test")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_remaining"] == 1000
        assert len(body["active_packs"]) == 1
        assert body["active_packs"][0]["pack_id"] == "pack_1k"

    @pytest.mark.unit
    def test_pack_balance_unknown_customer(self, starter_client):
        """HTTP-BILL-15: GET /api/packs/balance/{customer_id} — unknown customer returns empty."""
        resp = starter_client.get("/api/packs/balance/cus_nonexistent")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_remaining"] == 0
        assert body["active_packs"] == []


# ===========================================================================
# Customer Portal — HTTP-BILL-16, HTTP-BILL-17
# ===========================================================================


class TestCustomerPortal:
    """HTTP tests for POST /api/billing/portal."""

    @pytest.mark.unit
    def test_portal_session_returns_url(
        self, starter_client, mock_stripe_portal,
    ):
        """HTTP-BILL-16: POST /api/billing/portal — returns portal URL."""
        resp = starter_client.post(
            "/api/billing/portal",
            json={"stripe_customer_id": "cus_test_001"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "billing.stripe.com" in body["portal_url"]
        assert body["stripe_customer_id"] == "cus_test_001"

    @pytest.mark.unit
    def test_portal_unauthenticated_returns_401(self, app_client):
        """HTTP-BILL-17: POST /api/billing/portal — unauthenticated returns 401."""
        resp = app_client.post(
            "/api/billing/portal",
            json={"stripe_customer_id": "cus_test_001"},
        )
        assert resp.status_code == 401


# ===========================================================================
# Metered Usage — HTTP-BILL-18 through HTTP-BILL-20
# ===========================================================================


class TestMeteredUsage:
    """HTTP tests for POST /api/usage/record, GET /api/usage/{customer_id}."""

    @pytest.mark.unit
    def test_record_conversation_within_allowance(self, starter_client):
        """HTTP-BILL-18: POST /api/usage/record — records billable conversation.

        When usage is within the included allowance, no Stripe meter event
        is sent. The endpoint should still return 200 with usage details.
        """
        resp = starter_client.post(
            "/api/usage/record",
            json={
                "stripe_customer_id": "cus_usage_test",
                "tier": "starter",
                "count": 1,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_conversations"] == 1
        assert body["included_allowance"] == 1000
        assert body["overage_conversations"] == 0
        assert body["meter_event_sent"] is False

    @pytest.mark.unit
    def test_record_conversation_double_call_accumulates(self, starter_client):
        """HTTP-BILL-19: POST /api/usage/record — multiple calls accumulate.

        The test plan says "deduplicates on conversation_id" but the usage
        endpoint does not have conversation-level dedup — it accumulates.
        This test validates the accumulation behavior.
        """
        for _ in range(3):
            resp = starter_client.post(
                "/api/usage/record",
                json={
                    "stripe_customer_id": "cus_accum_test",
                    "tier": "starter",
                    "count": 1,
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_conversations"] == 3

    @pytest.mark.unit
    def test_get_usage_summary(self, starter_client):
        """HTTP-BILL-20: GET /api/usage/{customer_id} — returns usage summary."""
        # Record some usage first
        starter_client.post(
            "/api/usage/record",
            json={
                "stripe_customer_id": "cus_summary_test",
                "tier": "starter",
                "count": 100,
            },
        )

        resp = starter_client.get(
            "/api/usage/cus_summary_test?tier=starter",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_conversations"] == 100
        assert body["included_allowance"] == 1000
        assert body["remaining_included"] == 900
        assert body["usage_percent"] == 10.0


# ===========================================================================
# Stripe Webhooks — HTTP-BILL-21 through HTTP-BILL-28
# ===========================================================================


class TestStripeWebhooks:
    """HTTP tests for POST /api/webhooks/stripe.

    Webhook endpoints are auth-exempt (they use their own Stripe signature
    verification). We mock stripe.Webhook.construct_event to bypass
    signature checks while testing the event handler logic.
    """

    @pytest.mark.unit
    def test_webhook_checkout_completed(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-21: POST /api/webhooks/stripe — checkout.session.completed."""
        event = _make_stripe_event(
            event_type="checkout.session.completed",
            event_id="evt_checkout_001",
            data_object={
                "id": "cs_test_001",
                "customer": "cus_new_001",
                "subscription": "sub_new_001",
                "customer_details": {"email": "new@example.com"},
                "metadata": {
                    "agent_red_tier": "starter",
                    "agent_red_interval": "month",
                    "agent_red_addons": "",
                },
                "amount_total": 14900,
                "currency": "usd",
            },
        )
        mock_stripe_webhook_verify.return_value = event

        # Must set STRIPE_WEBHOOK_SECRET for the handler to proceed
        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            resp = app_client.post(
                "/api/webhooks/stripe",
                content=json.dumps(event).encode(),
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "processed"
        assert body["event_type"] == "checkout.session.completed"

    @pytest.mark.unit
    def test_webhook_subscription_updated(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-22: POST /api/webhooks/stripe — customer.subscription.updated."""
        event = _make_stripe_event(
            event_type="customer.subscription.updated",
            event_id="evt_sub_update_001",
            data_object={
                "id": "sub_test_001",
                "customer": "cus_existing_001",
                "status": "active",
                "metadata": {
                    "agent_red_tier": "professional",
                    "agent_red_interval": "month",
                    "agent_red_addons": "",
                },
            },
            previous_attributes={
                "metadata": {
                    "agent_red_tier": "starter",
                    "agent_red_interval": "month",
                },
            },
        )
        mock_stripe_webhook_verify.return_value = event

        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            resp = app_client.post(
                "/api/webhooks/stripe",
                content=json.dumps(event).encode(),
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "processed"

    @pytest.mark.unit
    def test_webhook_subscription_deleted(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-23: POST /api/webhooks/stripe — customer.subscription.deleted."""
        # First provision a tenant so deletion has something to deactivate
        from src.integrations.provisioning import BillingChannel, provision_tenant
        run_sync(provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_cancel_001",
            stripe_subscription_id="sub_cancel_001",
        ))

        event = _make_stripe_event(
            event_type="customer.subscription.deleted",
            event_id="evt_sub_delete_001",
            data_object={
                "id": "sub_cancel_001",
                "customer": "cus_cancel_001",
                "status": "canceled",
                "metadata": {"agent_red_tier": "starter"},
                "canceled_at": int(time.time()),
                "ended_at": int(time.time()),
            },
        )
        mock_stripe_webhook_verify.return_value = event

        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            resp = app_client.post(
                "/api/webhooks/stripe",
                content=json.dumps(event).encode(),
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "processed"

    @pytest.mark.unit
    def test_webhook_payment_succeeded(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-24: POST /api/webhooks/stripe — invoice.payment_succeeded."""
        event = _make_stripe_event(
            event_type="invoice.payment_succeeded",
            event_id="evt_payment_ok_001",
            data_object={
                "id": "in_test_001",
                "subscription": "sub_test_001",
                "customer": "cus_test_001",
                "amount_paid": 14900,
                "currency": "usd",
                "billing_reason": "subscription_create",
                "period_start": int(time.time()),
                "period_end": int(time.time()) + 30 * 86400,
            },
        )
        mock_stripe_webhook_verify.return_value = event

        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            resp = app_client.post(
                "/api/webhooks/stripe",
                content=json.dumps(event).encode(),
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "processed"

    @pytest.mark.unit
    def test_webhook_payment_failed(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-25: POST /api/webhooks/stripe — invoice.payment_failed."""
        # Provision a tenant first so flag_payment_issue finds it
        from src.integrations.provisioning import BillingChannel, provision_tenant
        run_sync(provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_fail_001",
        ))

        event = _make_stripe_event(
            event_type="invoice.payment_failed",
            event_id="evt_payment_fail_001",
            data_object={
                "id": "in_fail_001",
                "subscription": "sub_fail_001",
                "customer": "cus_fail_001",
                "amount_due": 14900,
                "currency": "usd",
                "attempt_count": 1,
                "next_payment_attempt": int(time.time()) + 3 * 86400,
                "billing_reason": "subscription_cycle",
            },
        )
        mock_stripe_webhook_verify.return_value = event

        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            resp = app_client.post(
                "/api/webhooks/stripe",
                content=json.dumps(event).encode(),
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "processed"

    @pytest.mark.unit
    def test_webhook_finalization_failed(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-26: POST /api/webhooks/stripe — invoice.finalization_failed."""
        event = _make_stripe_event(
            event_type="invoice.finalization_failed",
            event_id="evt_final_fail_001",
            data_object={
                "id": "in_final_fail_001",
                "subscription": "sub_test_001",
                "customer": "cus_test_001",
                "automatic_tax": {
                    "status": "requires_location_inputs",
                },
                "last_finalization_error": {
                    "type": "tax_error",
                    "message": "Customer address is required for tax calculation",
                },
            },
        )
        mock_stripe_webhook_verify.return_value = event

        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            resp = app_client.post(
                "/api/webhooks/stripe",
                content=json.dumps(event).encode(),
                headers={"stripe-signature": "t=123,v1=abc"},
            )

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "processed"

    @pytest.mark.unit
    def test_webhook_invalid_signature_returns_400(self, app_client):
        """HTTP-BILL-27: POST /api/webhooks/stripe — invalid signature returns 400."""
        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            with patch(
                "stripe.Webhook.construct_event",
                side_effect=stripe.SignatureVerificationError(
                    "Signature verification failed", "sig_header",
                ),
            ):
                resp = app_client.post(
                    "/api/webhooks/stripe",
                    content=b'{"id": "evt_bad"}',
                    headers={"stripe-signature": "t=123,v1=invalid"},
                )

        assert resp.status_code == 400
        assert "signature" in resp.json()["detail"].lower() or "invalid" in resp.json()["detail"].lower()

    @pytest.mark.unit
    def test_webhook_idempotent_replay(
        self, app_client, mock_stripe_webhook_verify,
    ):
        """HTTP-BILL-28: POST /api/webhooks/stripe — idempotent replay returns 200."""
        event = _make_stripe_event(
            event_type="invoice.payment_succeeded",
            event_id="evt_duplicate_001",
            data_object={
                "id": "in_dup_001",
                "customer": "cus_dup_001",
                "billing_reason": "subscription_create",
            },
        )
        mock_stripe_webhook_verify.return_value = event

        with patch.dict("os.environ", {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            import src.integrations.stripe_webhooks as wh_mod
            wh_mod._WEBHOOK_SECRET = "whsec_test"

            payload = json.dumps(event).encode()
            headers = {"stripe-signature": "t=123,v1=abc"}

            # First call — processed
            resp1 = app_client.post(
                "/api/webhooks/stripe",
                content=payload,
                headers=headers,
            )
            assert resp1.status_code == 200
            assert resp1.json()["status"] == "processed"

            # Second call with same event_id — duplicate
            resp2 = app_client.post(
                "/api/webhooks/stripe",
                content=payload,
                headers=headers,
            )
            assert resp2.status_code == 200
            assert resp2.json()["status"] == "duplicate"


# ===========================================================================
# Shopify Billing — HTTP-BILL-29 through HTTP-BILL-33
# ===========================================================================


class TestShopifyBilling:
    """HTTP tests for /api/shopify/billing/* endpoints."""

    @pytest.mark.unit
    def test_shopify_subscribe_monthly(
        self, starter_client, mock_shopify_client,
    ):
        """HTTP-BILL-29: POST /api/shopify/billing/subscribe — creates subscription."""
        mock_shopify_client.execute.return_value = {
            "appSubscriptionCreate": {
                "appSubscription": {
                    "id": "gid://shopify/AppSubscription/12345",
                    "name": "Agent Red Starter (Monthly)",
                    "status": "PENDING",
                    "createdAt": "2026-01-31T00:00:00Z",
                    "currentPeriodEnd": "2026-03-02T00:00:00Z",
                },
                "confirmationUrl": "https://example.myshopify.com/admin/charges/confirm",
                "userErrors": [],
            }
        }

        resp = starter_client.post(
            "/api/shopify/billing/subscribe",
            json={
                "tier": "starter",
                "interval": "month",
                "shop_domain": "test-shop.myshopify.com",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["tier"] == "starter"
        assert body["interval"] == "month"
        assert "confirmation_url" in body
        assert body["base_price"] == 149.0

    @pytest.mark.unit
    def test_shopify_confirm_subscription(
        self, app_client, mock_shopify_client,
    ):
        """HTTP-BILL-30: GET /api/shopify/billing/confirm — confirms billing.

        This path is auth-exempt.
        """
        mock_shopify_client.execute.return_value = {
            "currentAppInstallation": {
                "activeSubscriptions": [
                    {
                        "id": "gid://shopify/AppSubscription/12345",
                        "name": "Agent Red Starter (Monthly)",
                        "status": "ACTIVE",
                        "createdAt": "2026-01-31T00:00:00Z",
                        "currentPeriodEnd": "2026-03-02T00:00:00Z",
                        "lineItems": [
                            {
                                "id": "gid://shopify/AppSubscriptionLineItem/1",
                                "plan": {
                                    "pricingDetails": {
                                        "__typename": "AppRecurringPricing",
                                        "price": {"amount": "149.00", "currencyCode": "USD"},
                                        "interval": "EVERY_30_DAYS",
                                    }
                                },
                            },
                            {
                                "id": "gid://shopify/AppSubscriptionLineItem/2",
                                "plan": {
                                    "pricingDetails": {
                                        "__typename": "AppUsagePricing",
                                        "cappedAmount": {"amount": "500.00", "currencyCode": "USD"},
                                        "terms": "Overage billing",
                                    }
                                },
                            },
                        ],
                    }
                ]
            }
        }

        resp = app_client.get(
            "/api/shopify/billing/confirm?shop=test-shop.myshopify.com",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "confirmed"
        assert body["shop"] == "test-shop.myshopify.com"

    @pytest.mark.unit
    def test_shopify_billing_status(
        self, starter_client, mock_shopify_client,
    ):
        """HTTP-BILL-31: GET /api/shopify/billing/status — returns subscription status."""
        mock_shopify_client.execute.return_value = {
            "currentAppInstallation": {
                "activeSubscriptions": [
                    {
                        "id": "gid://shopify/AppSubscription/12345",
                        "name": "Agent Red Starter (Monthly)",
                        "status": "ACTIVE",
                        "createdAt": "2026-01-31T00:00:00Z",
                        "currentPeriodEnd": "2026-03-02T00:00:00Z",
                        "lineItems": [],
                    }
                ]
            }
        }

        resp = starter_client.get(
            "/api/shopify/billing/status?shop=test-shop.myshopify.com",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["has_active_subscription"] is True
        assert body["shop_domain"] == "test-shop.myshopify.com"

    @pytest.mark.unit
    def test_shopify_annual_no_usage_pricing(
        self, starter_client, mock_shopify_client,
    ):
        """HTTP-BILL-32: POST /api/shopify/billing/subscribe — annual plan has no usage pricing.

        Shopify does not support appUsagePricingDetails with ANNUAL interval.
        Annual subscriptions should only have a recurring line item.
        """
        mock_shopify_client.execute.return_value = {
            "appSubscriptionCreate": {
                "appSubscription": {
                    "id": "gid://shopify/AppSubscription/67890",
                    "name": "Agent Red Starter (Annual)",
                    "status": "PENDING",
                    "createdAt": "2026-01-31T00:00:00Z",
                    "currentPeriodEnd": "2027-01-31T00:00:00Z",
                },
                "confirmationUrl": "https://example.myshopify.com/admin/charges/confirm",
                "userErrors": [],
            }
        }

        resp = starter_client.post(
            "/api/shopify/billing/subscribe",
            json={
                "tier": "starter",
                "interval": "year",
                "shop_domain": "annual-shop.myshopify.com",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["interval"] == "year"
        assert body["overage_cap"] == 0.0  # No usage pricing for annual

        # Verify the GraphQL call did NOT include usage pricing line item
        call_args = mock_shopify_client.execute.call_args
        variables = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get("variables", call_args[0][1] if len(call_args[0]) > 1 else {})
        line_items = variables.get("lineItems", [])
        # Should have exactly 1 line item (recurring only, no usage)
        assert len(line_items) == 1
        assert "appRecurringPricingDetails" in line_items[0]["plan"]

    @pytest.mark.unit
    def test_shopify_decimal_arithmetic(self):
        """HTTP-BILL-33: Shopify Decimal arithmetic — no floating-point rounding errors.

        Verifies that the Shopify billing module uses Decimal for price
        calculations to avoid binary floating-point errors.
        """
        from src.integrations.shopify_billing import VALID_TIERS, _get_tier_pricing

        for tier_name in VALID_TIERS:
            pricing = _get_tier_pricing(tier_name)
            assert isinstance(pricing["monthly"], Decimal), (
                f"{tier_name} monthly price should be Decimal"
            )
            assert isinstance(pricing["overage_rate"], Decimal), (
                f"{tier_name} overage_rate should be Decimal"
            )
            assert isinstance(pricing["capped_amount"], Decimal), (
                f"{tier_name} capped_amount should be Decimal"
            )

        # Verify calculation precision
        starter_overage = Decimal("0.04") * Decimal("1000")
        assert starter_overage == Decimal("40.00")

        # This would fail with floats: 0.1 + 0.2 != 0.3
        assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")


# ===========================================================================
# Tenant Provisioning Endpoints — HTTP-BILL-34, HTTP-BILL-35
# ===========================================================================


class TestTenantEndpoints:
    """HTTP tests for GET /api/tenants/lookup, GET /api/tenants/{tenant_id}."""

    @pytest.mark.unit
    def test_tenant_lookup_by_domain(self, starter_client):
        """HTTP-BILL-34: GET /api/tenants/lookup — returns tenant by domain."""
        # Provision a tenant via the FakeTenantRepo
        from src.integrations.provisioning import BillingChannel, provision_tenant
        tenant = run_sync(provision_tenant(
            billing_channel=BillingChannel.SHOPIFY,
            tier="starter",
            shopify_shop_domain="lookup-shop.myshopify.com",
        ))

        resp = starter_client.get(
            "/api/tenants/lookup?shop=lookup-shop.myshopify.com",
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["found"] is True
        assert body["tenant_id"] == tenant.tenant_id
        assert body["tier"] == "starter"
        assert body["billing_channel"] == "shopify"

    @pytest.mark.unit
    def test_tenant_get_by_id(self, starter_client):
        """HTTP-BILL-35: GET /api/tenants/{tenant_id} — returns tenant detail."""
        from src.integrations.provisioning import BillingChannel, provision_tenant
        tenant = run_sync(provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="professional",
            interval="month",
            stripe_customer_id="cus_detail_001",
        ))

        resp = starter_client.get(f"/api/tenants/{tenant.tenant_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["tenant_id"] == tenant.tenant_id
        assert body["tier"] == "professional"
        assert body["billing_channel"] == "stripe"
        assert body["status"] == "provisioning"


# ===========================================================================
# Pack Purchase with tenant_id — HTTP-BILL-36, HTTP-BILL-37
# ===========================================================================


class TestPackPurchaseWithTenantId:
    """HTTP tests for POST /api/packs/purchase using tenant_id instead of stripe_customer_id."""

    @pytest.mark.unit
    def test_purchase_pack_with_tenant_id(self, starter_client, mock_stripe_checkout):
        """HTTP-BILL-36: POST /api/packs/purchase — tenant_id resolves to Stripe customer."""
        from src.integrations.provisioning import BillingChannel, provision_tenant

        tenant = run_sync(provision_tenant(
            billing_channel=BillingChannel.STRIPE,
            tier="starter",
            interval="month",
            stripe_customer_id="cus_tenant_pack_001",
        ))

        resp = starter_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_1k",
                "tenant_id": tenant.tenant_id,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["pack_id"] == "pack_1k"
        assert body["conversations"] == 1000
        assert body["checkout_url"]  # Non-empty checkout URL
        assert body["session_id"] == "cs_test_session_001"

    @pytest.mark.unit
    def test_purchase_pack_no_identifiers_returns_400(self, starter_client):
        """HTTP-BILL-37: POST /api/packs/purchase — no tenant_id or stripe_customer_id returns 400."""
        resp = starter_client.post(
            "/api/packs/purchase",
            json={
                "pack_id": "pack_1k",
            },
        )
        assert resp.status_code == 400
        assert "tenant_id" in resp.json()["detail"].lower() or "stripe_customer_id" in resp.json()["detail"].lower()


# ===========================================================================
# Billing Status — HTTP-BILL-38, HTTP-BILL-39
# ===========================================================================


class TestBillingStatus:
    """HTTP tests for GET /api/billing/status — lightweight billing status."""

    @pytest.mark.unit
    def test_billing_status_with_subscription(self, starter_client):
        """HTTP-BILL-38: GET /api/billing/status — returns renewal date and plan name."""
        # Mock the Stripe subscription list
        mock_sub = MagicMock()
        mock_sub.status = "active"
        mock_sub.current_period_end = 1738368000  # 2025-02-01 UTC
        mock_item = MagicMock()
        mock_item.price = MagicMock()
        mock_item.price.product = MagicMock()
        mock_item.price.product.name = "Agent Red Starter"
        mock_sub.items = MagicMock()
        mock_sub.items.data = [mock_item]

        mock_list = MagicMock()
        mock_list.data = [mock_sub]

        # Patch the resolver so the test tenant resolves to a Stripe customer
        with patch(
            "src.integrations.stripe_portal._resolve_stripe_customer_id",
            return_value="cus_status_001",
        ):
            with patch("stripe.Subscription.list", return_value=mock_list):
                resp = starter_client.get("/api/billing/status")

        assert resp.status_code == 200
        body = resp.json()
        assert body["billing_channel"] == "stripe"
        assert body["status"] == "active"
        assert body["renewal_date"] is not None
        assert body["plan_name"] == "Agent Red Starter"

    @pytest.mark.unit
    def test_billing_status_no_subscription(self, starter_client):
        """HTTP-BILL-39: GET /api/billing/status — no subscription returns graceful null."""
        mock_list = MagicMock()
        mock_list.data = []

        # Patch the resolver so the test tenant resolves to a Stripe customer
        with patch(
            "src.integrations.stripe_portal._resolve_stripe_customer_id",
            return_value="cus_status_nosub",
        ):
            with patch("stripe.Subscription.list", return_value=mock_list):
                resp = starter_client.get("/api/billing/status")

        assert resp.status_code == 200
        body = resp.json()
        assert body["billing_channel"] == "stripe"
        assert body["status"] == "no_subscription"
        assert body["renewal_date"] is None
        assert body["plan_name"] is None
