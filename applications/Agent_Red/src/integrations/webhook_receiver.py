# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Universal Webhook Receiver (SPEC-1766).

Auth-exempt endpoint that receives webhooks from external integrations.
Flow: verify signature → dedup check → enqueue → return 200 (all <1s).

Per-integration signature verification:
  - Zendesk: HMAC-SHA256 via x-zendesk-webhook-signature
  - Intercom: HMAC-SHA256 via x-hub-signature-256
  - Shopify: HMAC-SHA256 (base64) via x-shopify-hmac-sha256
  - Slack: HMAC-SHA256 via x-slack-signature with timestamp replay check

Idempotency: Redis SET with 24h TTL keyed on event_id.
Processing: asyncio background tasks with error isolation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEDUP_TTL_SECONDS = 86400  # 24 hours
SLACK_TIMESTAMP_TOLERANCE = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Signature Verification
# ---------------------------------------------------------------------------


class SignatureVerifier:
    """Per-vendor webhook signature verification."""

    @staticmethod
    def verify_zendesk(
        body: bytes, secret: str, headers: dict[str, str]
    ) -> bool:
        """Zendesk: HMAC-SHA256, header x-zendesk-webhook-signature."""
        provided = headers.get("x-zendesk-webhook-signature", "")
        expected = base64.b64encode(
            hmac.new(secret.encode(), body, hashlib.sha256).digest()
        ).decode()
        return hmac.compare_digest(provided, expected)

    @staticmethod
    def verify_intercom(
        body: bytes, secret: str, headers: dict[str, str]
    ) -> bool:
        """Intercom: HMAC-SHA256, header x-hub-signature-256."""
        provided = headers.get("x-hub-signature-256", "")
        expected_sig = hmac.new(
            secret.encode(), body, hashlib.sha256
        ).hexdigest()
        expected = f"sha256={expected_sig}"
        return hmac.compare_digest(provided, expected)

    @staticmethod
    def verify_shopify(
        body: bytes, secret: str, headers: dict[str, str]
    ) -> bool:
        """Shopify: HMAC-SHA256 (base64), header x-shopify-hmac-sha256."""
        provided = headers.get("x-shopify-hmac-sha256", "")
        expected = base64.b64encode(
            hmac.new(secret.encode(), body, hashlib.sha256).digest()
        ).decode()
        return hmac.compare_digest(provided, expected)

    @staticmethod
    def verify_slack(
        body: bytes, secret: str, headers: dict[str, str]
    ) -> bool:
        """Slack: HMAC-SHA256 with timestamp, header x-slack-signature."""
        timestamp_str = headers.get("x-slack-request-timestamp", "")
        provided = headers.get("x-slack-signature", "")

        if not timestamp_str or not provided:
            return False

        # Replay attack prevention
        try:
            timestamp = int(timestamp_str)
        except ValueError:
            return False

        if abs(time.time() - timestamp) > SLACK_TIMESTAMP_TOLERANCE:
            return False

        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        expected_sig = hmac.new(
            secret.encode(), sig_basestring.encode(), hashlib.sha256
        ).hexdigest()
        expected = f"v0={expected_sig}"
        return hmac.compare_digest(provided, expected)


# Dispatch table: vendor name → verification function
SIGNATURE_VERIFIERS: dict[str, Callable[..., bool]] = {
    "zendesk": SignatureVerifier.verify_zendesk,
    "intercom": SignatureVerifier.verify_intercom,
    "shopify": SignatureVerifier.verify_shopify,
    "slack": SignatureVerifier.verify_slack,
}


# ---------------------------------------------------------------------------
# Event ID Extraction
# ---------------------------------------------------------------------------


def extract_event_id(
    vendor: str, headers: dict[str, str], payload: dict[str, Any]
) -> str | None:
    """Extract vendor-specific event ID for idempotency.

    Each vendor provides a unique event identifier either in headers
    or payload. Falls back to None if not found (no dedup).
    """
    # Header-based event IDs
    header_map: dict[str, str] = {
        "zendesk": "x-zendesk-webhook-id",
        "intercom": "x-request-id",
        "slack": "x-slack-request-id",
    }

    header_key = header_map.get(vendor)
    if header_key and header_key in headers:
        return headers[header_key]

    # Payload-based event IDs
    if vendor == "shopify":
        # Shopify: X-Shopify-Webhook-Id header
        shopify_id = headers.get("x-shopify-webhook-id")
        if shopify_id:
            return shopify_id

    # Generic: look for common payload keys
    for key in ("id", "event_id", "webhook_id", "message_id"):
        if key in payload:
            return str(payload[key])

    return None


# ---------------------------------------------------------------------------
# Dedup Store (Redis-backed or in-memory fallback)
# ---------------------------------------------------------------------------


class DedupStore:
    """Idempotency check using Redis SET with TTL.

    Falls back to an in-memory dict for dev/testing.
    """

    def __init__(self, redis_client: Any = None) -> None:
        self._redis = redis_client
        self._memory_store: dict[str, float] = {}  # event_id -> timestamp

    async def is_duplicate(self, event_id: str) -> bool:
        """Check if this event_id has been seen within the TTL window.

        Returns True if duplicate (already processed).
        """
        if self._redis is not None:
            try:
                key = f"webhook:dedup:{event_id}"
                result = await self._redis.set(
                    key, "1", ex=DEDUP_TTL_SECONDS, nx=True
                )
                # SET NX returns True if key was set (new), None if existed
                return result is None
            except Exception as exc:
                logger.warning("Redis dedup check failed: %s", exc)
                # Fall through to memory
                pass

        # In-memory fallback
        now = time.time()
        # Clean expired entries periodically
        if len(self._memory_store) > 10000:
            cutoff = now - DEDUP_TTL_SECONDS
            self._memory_store = {
                k: v for k, v in self._memory_store.items() if v > cutoff
            }

        if event_id in self._memory_store:
            age = now - self._memory_store[event_id]
            if age < DEDUP_TTL_SECONDS:
                return True

        self._memory_store[event_id] = now
        return False

    def clear(self) -> None:
        """Clear in-memory store (testing)."""
        self._memory_store.clear()


# ---------------------------------------------------------------------------
# Webhook Event
# ---------------------------------------------------------------------------


class WebhookEvent:
    """Parsed and validated webhook event."""

    __slots__ = (
        "tenant_id",
        "integration_id",
        "vendor",
        "event_id",
        "event_type",
        "payload",
        "headers",
        "received_at",
    )

    def __init__(
        self,
        tenant_id: str,
        integration_id: str,
        vendor: str,
        payload: dict[str, Any],
        headers: dict[str, str],
        event_id: str | None = None,
        event_type: str = "",
    ) -> None:
        self.tenant_id = tenant_id
        self.integration_id = integration_id
        self.vendor = vendor
        self.event_id = event_id or ""
        self.event_type = event_type
        self.payload = payload
        self.headers = headers
        self.received_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "integration_id": self.integration_id,
            "vendor": self.vendor,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "received_at": self.received_at,
            "payload": self.payload,
        }


# ---------------------------------------------------------------------------
# WebhookReceiver
# ---------------------------------------------------------------------------


# Handler type: async callable that processes a WebhookEvent
WebhookHandler = Callable[[WebhookEvent], Coroutine[Any, Any, None]]


class WebhookReceiver:
    """Universal webhook receiver with signature verification and dedup.

    Usage:
        receiver = WebhookReceiver()
        receiver.register_handler("zendesk", my_handler)

        # In endpoint:
        result = await receiver.receive(
            tenant_id="t-1",
            integration_id="zendesk-main",
            vendor="zendesk",
            body=request_body,
            headers=request_headers,
            signing_secret="whsec_xxx",
        )
    """

    def __init__(
        self,
        dedup_store: DedupStore | None = None,
    ) -> None:
        self._dedup = dedup_store or DedupStore()
        self._handlers: dict[str, list[WebhookHandler]] = {}
        self._background_tasks: set[asyncio.Task[None]] = set()
        self._event_count: int = 0
        self._duplicate_count: int = 0
        self._error_count: int = 0

    def register_handler(
        self, vendor: str, handler: WebhookHandler
    ) -> None:
        """Register an async handler for a vendor's webhooks."""
        if vendor not in self._handlers:
            self._handlers[vendor] = []
        self._handlers[vendor].append(handler)

    async def receive(
        self,
        tenant_id: str,
        integration_id: str,
        vendor: str,
        body: bytes,
        headers: dict[str, str],
        signing_secret: str,
    ) -> dict[str, Any]:
        """Process an incoming webhook.

        Steps:
        1. Verify signature (if verifier exists for vendor)
        2. Parse payload
        3. Extract event_id for dedup
        4. Check dedup store
        5. Enqueue for async processing
        6. Return immediately

        Returns:
            Dict with status and event metadata.
        """
        # Normalize header keys to lowercase
        headers_lower = {k.lower(): v for k, v in headers.items()}

        # 1. Verify signature
        verifier = SIGNATURE_VERIFIERS.get(vendor)
        if verifier:
            if not verifier(body, signing_secret, headers_lower):
                logger.warning(
                    "Webhook signature verification failed: "
                    "tenant=%s vendor=%s integration=%s",
                    tenant_id,
                    vendor,
                    integration_id,
                )
                return {
                    "status": "rejected",
                    "reason": "invalid_signature",
                }

        # 2. Parse payload
        try:
            payload = json.loads(body) if body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {
                "status": "rejected",
                "reason": "invalid_payload",
            }

        # 3. Extract event ID
        event_id = extract_event_id(vendor, headers_lower, payload)

        # 4. Dedup check
        if event_id:
            is_dup = await self._dedup.is_duplicate(event_id)
            if is_dup:
                self._duplicate_count += 1
                logger.debug(
                    "Duplicate webhook ignored: event_id=%s vendor=%s",
                    event_id,
                    vendor,
                )
                return {
                    "status": "duplicate",
                    "event_id": event_id,
                }

        # 5. Create event
        event = WebhookEvent(
            tenant_id=tenant_id,
            integration_id=integration_id,
            vendor=vendor,
            payload=payload,
            headers=headers_lower,
            event_id=event_id,
            event_type=payload.get("type", payload.get("event", "")),
        )
        self._event_count += 1

        # 6. Enqueue for async processing
        handlers = self._handlers.get(vendor, [])
        for handler in handlers:
            task = asyncio.create_task(
                self._safe_process(handler, event)
            )
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)

        return {
            "status": "accepted",
            "event_id": event_id or "none",
            "handlers": len(handlers),
        }

    async def _safe_process(
        self, handler: WebhookHandler, event: WebhookEvent
    ) -> None:
        """Process a webhook event with error isolation."""
        try:
            await handler(event)
        except Exception as exc:
            self._error_count += 1
            logger.error(
                "Webhook handler error: vendor=%s event_id=%s error=%s",
                event.vendor,
                event.event_id,
                exc,
            )

    # -- Stats --------------------------------------------------------------

    @property
    def stats(self) -> dict[str, int]:
        return {
            "events_received": self._event_count,
            "duplicates_ignored": self._duplicate_count,
            "handler_errors": self._error_count,
            "active_tasks": len(self._background_tasks),
        }
