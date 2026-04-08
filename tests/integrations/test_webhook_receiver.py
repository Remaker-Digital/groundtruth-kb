"""Tests for Universal Webhook Receiver (SPEC-1766).

Tests cover: per-vendor signature verification (Zendesk, Intercom,
Shopify, Slack), event ID extraction, dedup, async processing,
error isolation, invalid payloads.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import time

import pytest

from src.integrations.webhook_receiver import (
    SLACK_TIMESTAMP_TOLERANCE,
    DedupStore,
    SignatureVerifier,
    WebhookEvent,
    WebhookReceiver,
    extract_event_id,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

WEBHOOK_SECRET = "whsec_test_secret_key"


@pytest.fixture
def receiver() -> WebhookReceiver:
    return WebhookReceiver()


# ===================================================================
# Signature Verification
# ===================================================================


class TestZendeskSignature:
    """SPEC-1766: Zendesk HMAC-SHA256 verification."""

    def test_valid_signature(self) -> None:
        body = b'{"event":"ticket.created"}'
        sig = base64.b64encode(
            hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).digest()
        ).decode()
        headers = {"x-zendesk-webhook-signature": sig}
        assert SignatureVerifier.verify_zendesk(body, WEBHOOK_SECRET, headers) is True

    def test_invalid_signature(self) -> None:
        body = b'{"event":"ticket.created"}'
        headers = {"x-zendesk-webhook-signature": "invalid"}
        assert SignatureVerifier.verify_zendesk(body, WEBHOOK_SECRET, headers) is False

    def test_missing_header(self) -> None:
        body = b'{"event":"ticket.created"}'
        assert SignatureVerifier.verify_zendesk(body, WEBHOOK_SECRET, {}) is False


class TestIntercomSignature:
    """SPEC-1766: Intercom x-hub-signature-256 verification."""

    def test_valid_signature(self) -> None:
        body = b'{"type":"notification"}'
        sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
        headers = {"x-hub-signature-256": f"sha256={sig}"}
        assert SignatureVerifier.verify_intercom(body, WEBHOOK_SECRET, headers) is True

    def test_invalid_signature(self) -> None:
        body = b'{"type":"notification"}'
        headers = {"x-hub-signature-256": "sha256=wrong"}
        assert SignatureVerifier.verify_intercom(body, WEBHOOK_SECRET, headers) is False


class TestShopifySignature:
    """SPEC-1766: Shopify HMAC-SHA256 (base64) verification."""

    def test_valid_signature(self) -> None:
        body = b'{"topic":"orders/create"}'
        sig = base64.b64encode(
            hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).digest()
        ).decode()
        headers = {"x-shopify-hmac-sha256": sig}
        assert SignatureVerifier.verify_shopify(body, WEBHOOK_SECRET, headers) is True

    def test_invalid_signature(self) -> None:
        body = b'{"topic":"orders/create"}'
        headers = {"x-shopify-hmac-sha256": "invalid"}
        assert SignatureVerifier.verify_shopify(body, WEBHOOK_SECRET, headers) is False


class TestSlackSignature:
    """SPEC-1766: Slack HMAC-SHA256 with timestamp replay check."""

    def test_valid_signature(self) -> None:
        body = b'{"event":"message"}'
        ts = str(int(time.time()))
        sig_basestring = f"v0:{ts}:{body.decode()}"
        sig = hmac.new(
            WEBHOOK_SECRET.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
        headers = {
            "x-slack-request-timestamp": ts,
            "x-slack-signature": f"v0={sig}",
        }
        assert SignatureVerifier.verify_slack(body, WEBHOOK_SECRET, headers) is True

    def test_replay_attack_rejected(self) -> None:
        """Old timestamp is rejected (replay attack)."""
        body = b'{"event":"message"}'
        old_ts = str(int(time.time()) - SLACK_TIMESTAMP_TOLERANCE - 100)
        sig_basestring = f"v0:{old_ts}:{body.decode()}"
        sig = hmac.new(
            WEBHOOK_SECRET.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
        headers = {
            "x-slack-request-timestamp": old_ts,
            "x-slack-signature": f"v0={sig}",
        }
        assert SignatureVerifier.verify_slack(body, WEBHOOK_SECRET, headers) is False

    def test_missing_timestamp(self) -> None:
        body = b'{"event":"message"}'
        headers = {"x-slack-signature": "v0=abc"}
        assert SignatureVerifier.verify_slack(body, WEBHOOK_SECRET, headers) is False

    def test_invalid_timestamp(self) -> None:
        body = b'{"event":"message"}'
        headers = {
            "x-slack-request-timestamp": "not-a-number",
            "x-slack-signature": "v0=abc",
        }
        assert SignatureVerifier.verify_slack(body, WEBHOOK_SECRET, headers) is False


# ===================================================================
# Event ID Extraction
# ===================================================================


class TestEventIdExtraction:
    """SPEC-1766: Per-vendor event ID extraction."""

    def test_zendesk_header(self) -> None:
        headers = {"x-zendesk-webhook-id": "evt-123"}
        assert extract_event_id("zendesk", headers, {}) == "evt-123"

    def test_shopify_header(self) -> None:
        headers = {"x-shopify-webhook-id": "wh-456"}
        assert extract_event_id("shopify", headers, {}) == "wh-456"

    def test_payload_id(self) -> None:
        """Falls back to payload 'id' field."""
        assert extract_event_id("unknown", {}, {"id": "p-789"}) == "p-789"

    def test_payload_event_id(self) -> None:
        assert extract_event_id("unknown", {}, {"event_id": "e-1"}) == "e-1"

    def test_no_event_id(self) -> None:
        """Returns None when no event ID found."""
        assert extract_event_id("unknown", {}, {"data": "value"}) is None


# ===================================================================
# Dedup Store
# ===================================================================


class TestDedupStore:
    """SPEC-1766: Idempotency dedup store."""

    @pytest.mark.asyncio
    async def test_first_event_not_duplicate(self) -> None:
        store = DedupStore()
        assert await store.is_duplicate("evt-1") is False

    @pytest.mark.asyncio
    async def test_second_event_is_duplicate(self) -> None:
        store = DedupStore()
        await store.is_duplicate("evt-1")
        assert await store.is_duplicate("evt-1") is True

    @pytest.mark.asyncio
    async def test_different_events_not_duplicates(self) -> None:
        store = DedupStore()
        await store.is_duplicate("evt-1")
        assert await store.is_duplicate("evt-2") is False

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        store = DedupStore()
        await store.is_duplicate("evt-1")
        store.clear()
        assert await store.is_duplicate("evt-1") is False


# ===================================================================
# WebhookReceiver
# ===================================================================


class TestWebhookReceiver:
    """SPEC-1766: Full webhook receive flow."""

    @pytest.mark.asyncio
    async def test_accept_valid_zendesk_webhook(self, receiver: WebhookReceiver) -> None:
        """Valid Zendesk webhook is accepted."""
        body = b'{"id":"evt-1","type":"ticket.created"}'
        sig = base64.b64encode(
            hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).digest()
        ).decode()
        result = await receiver.receive(
            tenant_id="t-1",
            integration_id="zendesk-main",
            vendor="zendesk",
            body=body,
            headers={"X-Zendesk-Webhook-Signature": sig},
            signing_secret=WEBHOOK_SECRET,
        )
        assert result["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_reject_invalid_signature(self, receiver: WebhookReceiver) -> None:
        """Invalid signature is rejected."""
        result = await receiver.receive(
            tenant_id="t-1",
            integration_id="zendesk-main",
            vendor="zendesk",
            body=b'{"id":"evt-1"}',
            headers={"X-Zendesk-Webhook-Signature": "invalid"},
            signing_secret=WEBHOOK_SECRET,
        )
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_signature"

    @pytest.mark.asyncio
    async def test_reject_invalid_json(self, receiver: WebhookReceiver) -> None:
        """Invalid JSON payload is rejected (for unknown vendor)."""
        result = await receiver.receive(
            tenant_id="t-1",
            integration_id="custom",
            vendor="custom",  # No verifier
            body=b"not json{{{",
            headers={},
            signing_secret=WEBHOOK_SECRET,
        )
        assert result["status"] == "rejected"
        assert result["reason"] == "invalid_payload"

    @pytest.mark.asyncio
    async def test_dedup_duplicate(self, receiver: WebhookReceiver) -> None:
        """Duplicate event_id is detected and skipped."""
        body = b'{"id":"evt-dup","type":"update"}'
        # First call (no signature verifier for "custom")
        r1 = await receiver.receive(
            tenant_id="t-1",
            integration_id="custom",
            vendor="custom",
            body=body,
            headers={},
            signing_secret="",
        )
        assert r1["status"] == "accepted"

        # Second call same event_id
        r2 = await receiver.receive(
            tenant_id="t-1",
            integration_id="custom",
            vendor="custom",
            body=body,
            headers={},
            signing_secret="",
        )
        assert r2["status"] == "duplicate"

    @pytest.mark.asyncio
    async def test_handler_called(self, receiver: WebhookReceiver) -> None:
        """Registered handler is called for accepted events."""
        events: list[WebhookEvent] = []

        async def handler(event: WebhookEvent) -> None:
            events.append(event)

        receiver.register_handler("custom", handler)

        body = b'{"id":"evt-h1","type":"test"}'
        await receiver.receive(
            tenant_id="t-1",
            integration_id="custom",
            vendor="custom",
            body=body,
            headers={},
            signing_secret="",
        )

        # Let background task complete
        await asyncio.sleep(0.05)
        assert len(events) == 1
        assert events[0].event_id == "evt-h1"
        assert events[0].tenant_id == "t-1"

    @pytest.mark.asyncio
    async def test_handler_error_isolated(self, receiver: WebhookReceiver) -> None:
        """Handler errors don't affect the 'accepted' response."""
        async def bad_handler(event: WebhookEvent) -> None:
            raise ValueError("handler crash")

        receiver.register_handler("custom", bad_handler)

        body = b'{"id":"evt-err","type":"test"}'
        result = await receiver.receive(
            tenant_id="t-1",
            integration_id="custom",
            vendor="custom",
            body=body,
            headers={},
            signing_secret="",
        )
        assert result["status"] == "accepted"
        await asyncio.sleep(0.05)
        assert receiver.stats["handler_errors"] == 1

    @pytest.mark.asyncio
    async def test_stats(self, receiver: WebhookReceiver) -> None:
        """Stats track events, duplicates, and errors."""
        body = b'{"id":"evt-s1"}'
        await receiver.receive("t-1", "c", "custom", body, {}, "")
        await receiver.receive("t-1", "c", "custom", body, {}, "")  # dup
        assert receiver.stats["events_received"] == 1
        assert receiver.stats["duplicates_ignored"] == 1


# ===================================================================
# WebhookEvent
# ===================================================================


class TestWebhookEvent:
    """SPEC-1766: WebhookEvent model."""

    def test_to_dict(self) -> None:
        event = WebhookEvent(
            tenant_id="t-1",
            integration_id="zendesk",
            vendor="zendesk",
            payload={"key": "value"},
            headers={"h": "v"},
            event_id="evt-1",
            event_type="ticket.created",
        )
        d = event.to_dict()
        assert d["tenant_id"] == "t-1"
        assert d["event_id"] == "evt-1"
        assert d["event_type"] == "ticket.created"
        assert "received_at" in d
