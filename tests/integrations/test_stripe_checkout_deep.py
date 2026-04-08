"""Deep Stripe Checkout tests — advanced tax, metadata, referral, and URL features.

Tests advanced features of ``src.integrations.stripe_checkout`` including
Stripe Tax compliance, subscription mode, success/cancel URL construction,
Rewardful affiliate tracking, metadata propagation, and input validation.

Test IDs: SCD-01 through SCD-10.

Work Item: Stripe Checkout deep-coverage supplement.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from tests.helpers.fake_tenant_repo import FakeTenantRepo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_middleware_state(app: Any) -> None:
    """Walk the built ASGI middleware chain and clear stateful middleware."""
    stack = getattr(app, "middleware_stack", None)
    if stack is None:
        return

    current = stack
    visited: set[int] = set()
    while current is not None and id(current) not in visited:
        visited.add(id(current))
        if hasattr(current, "_windows"):
            current._windows.clear()
        if hasattr(current, "_gates"):
            current._gates.clear()
        current = getattr(current, "app", None)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_in_memory_stores(app_client):
    """Reset all in-memory billing stores before each test.

    The billing modules use module-level dicts for dev state.
    Tests must start with a clean slate.

    Provisioning uses a FakeTenantRepo (wired per-test) instead of
    module-level dicts — see ``_fake_provisioning_repo`` fixture below.
    """
    import src.integrations.stripe_packs as packs_mod
    import src.integrations.stripe_usage as usage_mod
    import src.integrations.stripe_webhooks as wh_mod
    import src.integrations.shopify_billing as shopify_mod
    import src.main as main_mod

    packs_mod._pack_balances.clear()
    usage_mod._usage_counters.clear()
    usage_mod._stripe_client = None
    wh_mod._processed_events.clear()
    shopify_mod._shop_subscriptions.clear()
    _reset_middleware_state(main_mod.app)

    yield

    packs_mod._pack_balances.clear()
    usage_mod._usage_counters.clear()
    wh_mod._processed_events.clear()
    shopify_mod._shop_subscriptions.clear()


@pytest.fixture(autouse=True)
def _fake_provisioning_repo():
    """Wire a FakeTenantRepo into the provisioning module for each test."""
    from src.integrations.provisioning import configure_provisioning_repo

    repo = FakeTenantRepo()
    configure_provisioning_repo(repo, team_repo=None)
    yield repo
    configure_provisioning_repo(None, team_repo=None)


@pytest.fixture
def mock_stripe_checkout():
    """Mock stripe.checkout.Session.create and .retrieve.

    Returns a dict with ``session``, ``create``, and ``retrieve`` keys.
    The mock ``create`` captures all keyword arguments so tests can
    inspect the exact parameters passed to Stripe.
    """
    mock_session = MagicMock()
    mock_session.id = "cs_test_deep_001"
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_deep_001"
    mock_session.amount_total = 14900
    mock_session.customer_details = MagicMock(email="deep@example.com")
    mock_session.subscription = MagicMock(id="sub_test_deep_001")
    mock_session.metadata = {"agent_red_tier": "starter", "agent_red_interval": "month"}

    with patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
        with patch("stripe.checkout.Session.retrieve", return_value=mock_session) as mock_retrieve:
            yield {
                "session": mock_session,
                "create": mock_create,
                "retrieve": mock_retrieve,
            }


def _get_create_kwargs(mock_stripe_checkout: dict) -> dict[str, Any]:
    """Extract keyword arguments from the stripe.checkout.Session.create call.

    Handles both positional-keyword and keyword-only call conventions.
    """
    call_args = mock_stripe_checkout["create"].call_args
    # Stripe SDK calls use **kwargs exclusively
    return call_args.kwargs if call_args.kwargs else call_args[1]


# ===========================================================================
# Deep Checkout Tests — SCD-01 through SCD-10
# ===========================================================================


class TestStripeCheckoutDeep:
    """Advanced Stripe Checkout Session validation tests."""

    # -----------------------------------------------------------------------
    # SCD-01: Tax compliance — automatic_tax enabled
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd01_automatic_tax_enabled(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-01: Checkout Session enables automatic_tax for Stripe Tax compliance.

        Stripe Tax calculates sales tax / VAT based on the customer's
        billing address. All Checkout Sessions must set
        ``automatic_tax={"enabled": True}``.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "month"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        assert "automatic_tax" in kwargs, "automatic_tax must be present in Checkout Session params"
        assert kwargs["automatic_tax"] == {"enabled": True}

    # -----------------------------------------------------------------------
    # SCD-02: Tax compliance — tax_id_collection enabled
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd02_tax_id_collection_enabled(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-02: Checkout Session enables tax_id_collection for business VAT/tax IDs.

        Business customers need to provide their VAT / tax ID at checkout.
        Stripe validates the format automatically when
        ``tax_id_collection={"enabled": True}``.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "professional", "interval": "month"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        assert "tax_id_collection" in kwargs, "tax_id_collection must be present"
        assert kwargs["tax_id_collection"] == {"enabled": True}

    # -----------------------------------------------------------------------
    # SCD-03: Checkout mode is "subscription"
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd03_checkout_mode_subscription(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-03: Checkout Session mode is 'subscription' (not 'payment' or 'setup').

        Agent Red sells recurring subscriptions, so the Checkout Session
        must use mode='subscription' to create a Stripe Subscription
        alongside the payment.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "enterprise", "interval": "year"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        assert kwargs["mode"] == "subscription"

    # -----------------------------------------------------------------------
    # SCD-04: Success URL contains Stripe template variable
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd04_success_url_contains_stripe_template_var(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-04: Default success_url includes {CHECKOUT_SESSION_ID} Stripe template variable.

        Stripe replaces ``{CHECKOUT_SESSION_ID}`` with the actual session ID
        before redirecting. This allows the success page to retrieve session
        details for displaying the thank-you page.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "month"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        success_url = kwargs["success_url"]
        assert "{CHECKOUT_SESSION_ID}" in success_url, (
            f"success_url must contain Stripe template variable {{CHECKOUT_SESSION_ID}}, got: {success_url}"
        )
        assert "/api/checkout/success" in success_url

    # -----------------------------------------------------------------------
    # SCD-05: Cancel URL points to /api/checkout/cancel
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd05_cancel_url_points_to_cancel_endpoint(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-05: Default cancel_url directs the user to /api/checkout/cancel.

        When a customer abandons checkout, Stripe redirects to this URL.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "month"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        cancel_url = kwargs["cancel_url"]
        assert cancel_url.endswith("/api/checkout/cancel"), (
            f"cancel_url must end with /api/checkout/cancel, got: {cancel_url}"
        )

    # -----------------------------------------------------------------------
    # SCD-06: Custom success_url and cancel_url override defaults
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd06_custom_urls_override_defaults(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-06: When the request provides custom success_url and cancel_url, they override the defaults.

        Merchants embedding the checkout flow in their own storefront
        may need custom redirect URLs.
        """
        custom_success = "https://mystore.example.com/thank-you?session={CHECKOUT_SESSION_ID}"
        custom_cancel = "https://mystore.example.com/pricing"

        resp = starter_client.post(
            "/api/checkout/session",
            json={
                "tier": "starter",
                "interval": "month",
                "success_url": custom_success,
                "cancel_url": custom_cancel,
            },
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        assert kwargs["success_url"] == custom_success
        assert kwargs["cancel_url"] == custom_cancel

    # -----------------------------------------------------------------------
    # SCD-07: Metadata includes agent_red_tier and agent_red_interval
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd07_metadata_includes_tier_and_interval(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-07: Checkout Session metadata and subscription_data.metadata include tier and interval.

        These metadata fields are read by the Stripe webhook handler to
        determine which tier and billing interval were selected, enabling
        automatic tenant provisioning.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "professional", "interval": "year"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)

        # Session-level metadata
        session_meta = kwargs["metadata"]
        assert session_meta["agent_red_tier"] == "professional"
        assert session_meta["agent_red_interval"] == "year"

        # Subscription-level metadata (persists on the subscription object)
        sub_meta = kwargs["subscription_data"]["metadata"]
        assert sub_meta["agent_red_tier"] == "professional"
        assert sub_meta["agent_red_interval"] == "year"

    # -----------------------------------------------------------------------
    # SCD-08: Referral UUID sets client_reference_id (Rewardful)
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd08_referral_sets_client_reference_id(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-08: When a referral UUID is provided, it is set as client_reference_id.

        Rewardful's Stripe webhook integration reads client_reference_id
        to attribute the conversion to the referring affiliate.
        """
        referral_uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

        resp = starter_client.post(
            "/api/checkout/session",
            json={
                "tier": "starter",
                "interval": "month",
                "referral": referral_uuid,
            },
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        assert kwargs["client_reference_id"] == referral_uuid

    # -----------------------------------------------------------------------
    # SCD-09: No referral → client_reference_id absent
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd09_no_referral_omits_client_reference_id(
        self, starter_client, mock_stripe_checkout,
    ):
        """SCD-09: When no referral is provided, client_reference_id is not set.

        Stripe raises an error if client_reference_id is an empty string,
        so it must be omitted entirely when there is no affiliate referral.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "starter", "interval": "month"},
        )
        assert resp.status_code == 200

        kwargs = _get_create_kwargs(mock_stripe_checkout)
        assert "client_reference_id" not in kwargs, (
            "client_reference_id must not be present when no referral is provided"
        )

    # -----------------------------------------------------------------------
    # SCD-10: Invalid tier → HTTP 400
    # -----------------------------------------------------------------------

    @pytest.mark.unit
    def test_scd10_invalid_tier_returns_400(
        self, starter_client,
    ):
        """SCD-10: POST /api/checkout/session with an invalid tier returns HTTP 400.

        The endpoint must reject unknown tier names before attempting
        to create a Stripe Checkout Session.
        """
        resp = starter_client.post(
            "/api/checkout/session",
            json={"tier": "platinum_vip", "interval": "month"},
        )
        assert resp.status_code == 400
        detail = resp.json()["detail"]
        assert "platinum_vip" in detail or "Invalid tier" in detail
