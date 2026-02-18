"""
Tests for Stripe webhook handler — src/integrations/stripe_webhooks.py.

Covers: stripe_webhook endpoint, signature verification, idempotency,
        IP allowlist, event handlers (checkout.session.completed,
        customer.subscription.created/updated/deleted,
        invoice.payment_succeeded/failed/finalization_failed),
        _is_duplicate, _check_stripe_ip.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.integrations.stripe_webhooks import (
    _check_stripe_ip,
    _is_duplicate,
    _processed_events,
    handle_checkout_completed,
    handle_finalization_failed,
    handle_payment_failed,
    handle_payment_succeeded,
    handle_subscription_created,
    handle_subscription_deleted,
    handle_subscription_updated,
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
def _clear_processed_events():
    """Clear idempotency cache between tests."""
    _processed_events.clear()
    yield
    _processed_events.clear()


# ---------------------------------------------------------------------------
# Tests — Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    """Tests for _is_duplicate."""

    def test_first_event_not_duplicate(self):
        assert _is_duplicate("evt_001") is False

    def test_second_event_is_duplicate(self):
        _is_duplicate("evt_001")
        assert _is_duplicate("evt_001") is True

    def test_eviction_at_max_cache(self):
        # Fill cache to max
        for i in range(10_000):
            _is_duplicate(f"evt_{i:06d}")

        assert len(_processed_events) == 10_000

        # Next event should trigger eviction
        _is_duplicate("evt_new")
        assert len(_processed_events) <= 5_001  # ~half evicted + new entry


# ---------------------------------------------------------------------------
# Tests — IP Allowlist
# ---------------------------------------------------------------------------


class TestIPAllowlist:
    """Tests for _check_stripe_ip."""

    def test_disabled_always_allows(self):
        request = MagicMock()
        with patch("src.integrations.stripe_webhooks._ENABLE_IP_ALLOWLIST", False):
            assert _check_stripe_ip(request) is True

    def test_localhost_allowed(self):
        request = MagicMock()
        request.headers = {"x-forwarded-for": ""}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"

        with patch("src.integrations.stripe_webhooks._ENABLE_IP_ALLOWLIST", True):
            assert _check_stripe_ip(request) is True

    def test_stripe_ip_allowed(self):
        request = MagicMock()
        request.headers = {"x-forwarded-for": "3.18.12.63"}
        request.client = MagicMock()
        request.client.host = "10.0.0.1"

        with patch("src.integrations.stripe_webhooks._ENABLE_IP_ALLOWLIST", True):
            assert _check_stripe_ip(request) is True

    def test_unknown_ip_rejected(self):
        request = MagicMock()
        request.headers = {"x-forwarded-for": ""}
        request.client = MagicMock()
        request.client.host = "198.51.100.1"

        with patch("src.integrations.stripe_webhooks._ENABLE_IP_ALLOWLIST", True):
            assert _check_stripe_ip(request) is False

    def test_forwarded_for_takes_first_ip(self):
        request = MagicMock()
        request.headers = {"x-forwarded-for": "54.88.130.119, 10.0.0.1"}
        request.client = MagicMock()

        with patch("src.integrations.stripe_webhooks._ENABLE_IP_ALLOWLIST", True):
            assert _check_stripe_ip(request) is True


# ---------------------------------------------------------------------------
# Tests — Webhook endpoint
# ---------------------------------------------------------------------------


class TestStripeWebhook:
    """Tests for POST /api/webhooks/stripe endpoint."""

    @pytest.mark.asyncio
    async def test_missing_webhook_secret(self):
        app = _make_app()

        with patch("src.integrations.stripe_webhooks._WEBHOOK_SECRET", ""):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/webhooks/stripe",
                    content=b"{}",
                    headers={"stripe-signature": "sig_test"},
                )

        assert resp.status_code == 500

    @pytest.mark.asyncio
    async def test_invalid_signature(self):
        app = _make_app()

        with patch("src.integrations.stripe_webhooks._WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event") as mock_construct:
            import stripe
            mock_construct.side_effect = stripe.SignatureVerificationError(
                "Invalid", "sig_test"
            )
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/webhooks/stripe",
                    content=b"{}",
                    headers={"stripe-signature": "sig_test"},
                )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_payload(self):
        app = _make_app()

        with patch("src.integrations.stripe_webhooks._WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.side_effect = ValueError("Invalid payload")
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/webhooks/stripe",
                    content=b"bad",
                    headers={"stripe-signature": "sig_test"},
                )

        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_duplicate_event_returns_200(self):
        app = _make_app()
        _is_duplicate("evt_dup")  # Pre-mark as processed

        with patch("src.integrations.stripe_webhooks._WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.return_value = {
                "id": "evt_dup",
                "type": "checkout.session.completed",
                "data": {"object": {}},
            }
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/webhooks/stripe",
                    content=b"{}",
                    headers={"stripe-signature": "sig_test"},
                )

        assert resp.status_code == 200
        assert resp.json()["status"] == "duplicate"

    @pytest.mark.asyncio
    async def test_unhandled_event_type(self):
        app = _make_app()

        with patch("src.integrations.stripe_webhooks._WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event") as mock_construct:
            mock_construct.return_value = {
                "id": "evt_unknown",
                "type": "some.unknown.event",
                "data": {"object": {}},
            }
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/webhooks/stripe",
                    content=b"{}",
                    headers={"stripe-signature": "sig_test"},
                )

        assert resp.status_code == 200
        assert resp.json()["status"] == "ignored"

    @pytest.mark.asyncio
    async def test_ip_allowlist_blocks(self):
        app = _make_app()

        with patch("src.integrations.stripe_webhooks._check_stripe_ip", return_value=False):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.post(
                    "/api/webhooks/stripe",
                    content=b"{}",
                    headers={"stripe-signature": "sig"},
                )

        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Tests — Event handlers
# ---------------------------------------------------------------------------


class TestHandleCheckoutCompleted:
    """Tests for checkout.session.completed handler."""

    @pytest.mark.asyncio
    async def test_subscription_checkout(self):
        event = {
            "data": {
                "object": {
                    "id": "cs_test_001",
                    "customer": "cus_test",
                    "subscription": "sub_test",
                    "customer_details": {"email": "user@test.com"},
                    "metadata": {
                        "agent_red_tier": "starter",
                        "agent_red_interval": "month",
                    },
                    "amount_total": 14900,
                    "currency": "usd",
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.provision_tenant") as mock_prov:
            tenant = MagicMock()
            tenant.tenant_id = "t-001"
            tenant.status.value = "active"
            mock_prov.return_value = tenant

            result = await handle_checkout_completed(event)

        assert result["action"] == "provision_tenant"
        assert result["tenant_id"] == "t-001"
        assert result["tier"] == "starter"
        mock_prov.assert_called_once()

    @pytest.mark.asyncio
    async def test_pack_purchase(self):
        event = {
            "data": {
                "object": {
                    "id": "cs_pack_001",
                    "customer": "cus_test",
                    "metadata": {
                        "agent_red_pack": "pack_100",
                        "agent_red_pack_conversations": "100",
                    },
                    "amount_total": 3500,
                    "currency": "usd",
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.credit_pack_balance") as mock_credit:
            mock_credit.return_value = {"total_remaining": 200}

            result = await handle_checkout_completed(event)

        assert result["action"] == "pack_purchased"
        assert result["conversations"] == 100
        assert result["total_remaining"] == 200

    @pytest.mark.asyncio
    async def test_pack_purchase_missing_data(self):
        event = {
            "data": {
                "object": {
                    "id": "cs_bad",
                    "customer": None,
                    "metadata": {
                        "agent_red_pack": "pack_100",
                        "agent_red_pack_conversations": "0",
                    },
                },
            },
        }

        result = await handle_checkout_completed(event)
        assert result["action"] == "pack_purchase_failed"

    @pytest.mark.asyncio
    async def test_pack_invalid_conversations_value(self):
        event = {
            "data": {
                "object": {
                    "id": "cs_bad2",
                    "customer": "cus_test",
                    "metadata": {
                        "agent_red_pack": "pack_x",
                        "agent_red_pack_conversations": "not_a_number",
                    },
                },
            },
        }

        result = await handle_checkout_completed(event)
        assert result["action"] == "pack_purchase_failed"

    @pytest.mark.asyncio
    async def test_checkout_with_addons(self):
        event = {
            "data": {
                "object": {
                    "id": "cs_addon",
                    "customer": "cus_test",
                    "subscription": "sub_test",
                    "customer_details": {"email": "a@b.com"},
                    "metadata": {
                        "agent_red_tier": "professional",
                        "agent_red_interval": "month",
                        "agent_red_addons": "addon_a,addon_b",
                    },
                    "amount_total": 39900,
                    "currency": "usd",
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.provision_tenant") as mock_prov:
            tenant = MagicMock()
            tenant.tenant_id = "t-002"
            tenant.status.value = "active"
            mock_prov.return_value = tenant

            result = await handle_checkout_completed(event)

        call_kwargs = mock_prov.call_args.kwargs
        assert call_kwargs["addons"] == ["addon_a", "addon_b"]


class TestHandleSubscriptionCreated:
    """Tests for customer.subscription.created handler."""

    @pytest.mark.asyncio
    async def test_activates_tenant(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "status": "active",
                    "metadata": {
                        "agent_red_tier": "starter",
                        "agent_red_interval": "month",
                    },
                    "current_period_start": 1704067200,
                    "current_period_end": 1706745600,
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.activate_tenant") as mock_activate:
            tenant = MagicMock()
            tenant.tenant_id = "t-001"
            tenant.status.value = "active"
            mock_activate.return_value = tenant

            result = await handle_subscription_created(event)

        assert result["action"] == "subscription_activated"
        assert result["tenant_id"] == "t-001"

    @pytest.mark.asyncio
    async def test_no_tenant_yet(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "status": "active",
                    "metadata": {},
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.activate_tenant") as mock_activate:
            mock_activate.return_value = None  # No tenant yet

            result = await handle_subscription_created(event)

        assert "tenant_id" not in result


class TestHandleSubscriptionUpdated:
    """Tests for customer.subscription.updated handler."""

    @pytest.mark.asyncio
    async def test_tier_change(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "status": "active",
                    "metadata": {"agent_red_tier": "professional"},
                },
                "previous_attributes": {
                    "metadata": {"agent_red_tier": "starter"},
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.update_tenant") as mock_update:
            mock_update.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="active")
            )

            result = await handle_subscription_updated(event)

        assert "tier: starter" in result["changes"][0]

    @pytest.mark.asyncio
    async def test_status_to_past_due(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "status": "past_due",
                    "metadata": {"agent_red_tier": "starter"},
                },
                "previous_attributes": {
                    "status": "active",
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.update_tenant") as mock_update, \
             patch("src.integrations.stripe_webhooks.flag_payment_issue") as mock_flag:
            mock_update.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="past_due")
            )
            mock_flag.return_value = MagicMock(status=MagicMock(value="past_due"))

            result = await handle_subscription_updated(event)

        mock_flag.assert_called_once()
        assert result["tenant_status"] == "past_due"

    @pytest.mark.asyncio
    async def test_status_recovery_from_past_due(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "status": "active",
                    "metadata": {"agent_red_tier": "starter"},
                },
                "previous_attributes": {"status": "past_due"},
            },
        }

        with patch("src.integrations.stripe_webhooks.update_tenant") as mock_update, \
             patch("src.integrations.stripe_webhooks.activate_tenant") as mock_activate:
            mock_update.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="active")
            )
            mock_activate.return_value = MagicMock(status=MagicMock(value="active"))

            result = await handle_subscription_updated(event)

        mock_activate.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_at_period_end(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "status": "active",
                    "cancel_at_period_end": True,
                    "metadata": {"agent_red_tier": "starter"},
                },
                "previous_attributes": {"cancel_at_period_end": False},
            },
        }

        with patch("src.integrations.stripe_webhooks.update_tenant") as mock_update:
            mock_update.return_value = None

            result = await handle_subscription_updated(event)

        assert "scheduled_cancellation" in result["changes"]


class TestHandleSubscriptionDeleted:
    """Tests for customer.subscription.deleted handler."""

    @pytest.mark.asyncio
    async def test_deactivates_tenant(self):
        event = {
            "data": {
                "object": {
                    "id": "sub_001",
                    "customer": "cus_test",
                    "metadata": {"agent_red_tier": "starter"},
                    "canceled_at": 1704067200,
                    "ended_at": 1706745600,
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.deactivate_tenant") as mock_deact:
            tenant = MagicMock()
            tenant.tenant_id = "t-001"
            tenant.status.value = "deactivating"
            tenant.grace_period_ends_at = "2026-03-01"
            mock_deact.return_value = tenant

            result = await handle_subscription_deleted(event)

        assert result["action"] == "subscription_cancelled"
        assert result["grace_period_days"] == 30
        assert result["tenant_id"] == "t-001"


class TestHandlePaymentSucceeded:
    """Tests for invoice.payment_succeeded handler."""

    @pytest.mark.asyncio
    async def test_subscription_renewal_resets_usage(self):
        event = {
            "data": {
                "object": {
                    "id": "inv_001",
                    "subscription": "sub_001",
                    "customer": "cus_test",
                    "amount_paid": 14900,
                    "currency": "usd",
                    "billing_reason": "subscription_cycle",
                    "period_start": 1704067200,
                    "period_end": 1706745600,
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.reset_usage") as mock_reset, \
             patch("src.integrations.stripe_webhooks.activate_tenant") as mock_activate:
            mock_activate.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="active")
            )

            result = await handle_payment_succeeded(event)

        mock_reset.assert_called_once_with("cus_test")
        assert result["usage_reset"] is True

    @pytest.mark.asyncio
    async def test_initial_payment_no_reset(self):
        event = {
            "data": {
                "object": {
                    "id": "inv_002",
                    "subscription": "sub_001",
                    "customer": "cus_test",
                    "amount_paid": 14900,
                    "currency": "usd",
                    "billing_reason": "subscription_create",
                    "period_start": 1704067200,
                    "period_end": 1706745600,
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.reset_usage") as mock_reset, \
             patch("src.integrations.stripe_webhooks.activate_tenant") as mock_activate:
            mock_activate.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="active")
            )

            result = await handle_payment_succeeded(event)

        mock_reset.assert_not_called()
        assert "usage_reset" not in result


class TestHandlePaymentFailed:
    """Tests for invoice.payment_failed handler."""

    @pytest.mark.asyncio
    async def test_flags_payment_issue(self):
        event = {
            "data": {
                "object": {
                    "id": "inv_fail",
                    "subscription": "sub_001",
                    "customer": "cus_test",
                    "amount_due": 14900,
                    "currency": "usd",
                    "attempt_count": 1,
                    "next_payment_attempt": 1704153600,
                    "billing_reason": "subscription_cycle",
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.flag_payment_issue") as mock_flag:
            mock_flag.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="past_due")
            )

            result = await handle_payment_failed(event)

        assert result["action"] == "payment_failed"
        mock_flag.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_customer_id_skips_flag(self):
        event = {
            "data": {
                "object": {
                    "id": "inv_fail2",
                    "customer": None,
                    "amount_due": 100,
                    "currency": "usd",
                    "attempt_count": 1,
                    "next_payment_attempt": None,
                    "billing_reason": "subscription_cycle",
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.flag_payment_issue") as mock_flag:
            result = await handle_payment_failed(event)

        mock_flag.assert_not_called()


class TestHandleFinalizationFailed:
    """Tests for invoice.finalization_failed handler."""

    @pytest.mark.asyncio
    async def test_flags_payment_issue(self):
        event = {
            "data": {
                "object": {
                    "id": "inv_fin_fail",
                    "subscription": "sub_001",
                    "customer": "cus_test",
                    "automatic_tax": {"status": "requires_location_inputs"},
                    "last_finalization_error": {
                        "type": "tax_error",
                        "message": "Customer address required",
                    },
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.flag_payment_issue") as mock_flag:
            mock_flag.return_value = MagicMock(
                tenant_id="t-001", status=MagicMock(value="past_due")
            )

            result = await handle_finalization_failed(event)

        assert result["action"] == "invoice_finalization_failed"
        assert result["automatic_tax_status"] == "requires_location_inputs"
        mock_flag.assert_called_once()

    @pytest.mark.asyncio
    async def test_no_customer_skips_flag(self):
        event = {
            "data": {
                "object": {
                    "id": "inv_fin2",
                    "customer": None,
                    "automatic_tax": {},
                    "last_finalization_error": {},
                },
            },
        }

        with patch("src.integrations.stripe_webhooks.flag_payment_issue") as mock_flag:
            result = await handle_finalization_failed(event)

        mock_flag.assert_not_called()
