# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Communication Capture & Audit Infrastructure (SPEC-1687).

Provides two operational modes controlled by the ENABLE_EMAIL_CAPTURE
environment variable:

1. **Capture mode** (ENABLE_EMAIL_CAPTURE=true): Stores full message
   bodies in an in-memory ring buffer, exposed via REST endpoints at
   /api/test/email-capture.  Designed for staging / CI environments
   where automated tests need to retrieve verification tokens, magic
   links, and other transient email content.

2. **Audit mode** (default): Logs structured metadata for every
   outbound communication (recipient, channel, subject, token hash)
   without storing message bodies.  Safe for production.

Both modes call emit_communication_event() -- the single integration
point that email / SMS modules invoke after dispatching a message.

CRITICAL: This module must NEVER block the calling code path.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment gate
# ---------------------------------------------------------------------------

CAPTURE_MODE = os.environ.get("ENABLE_EMAIL_CAPTURE", "").lower() in (
    "true",
    "1",
    "yes",
)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CommunicationEvent:
    """Single outbound communication record."""

    event_type: str  # e.g. 'magic_link', 'login_notification', 'otp'
    recipient: str  # email address or phone number
    channel: str  # 'email' or 'sms'
    subject: str = ""
    body: str = ""  # only populated in capture mode
    token_hash: str = ""  # SHA-256 of any embedded token/code
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    ttl_minutes: int = 0  # informational -- how long the token is valid
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Thread-safe in-memory capture store
# ---------------------------------------------------------------------------

_captured_messages: list[dict[str, Any]] = []
_capture_lock = threading.Lock()
_MAX_CAPTURED = 500  # ring-buffer ceiling


def _store_message(event: CommunicationEvent) -> None:
    """Append an event to the in-memory capture store (thread-safe)."""
    with _capture_lock:
        _captured_messages.append(asdict(event))
        # Trim oldest if we exceed the ring-buffer ceiling
        while len(_captured_messages) > _MAX_CAPTURED:
            _captured_messages.pop(0)


def get_captured_messages(
    *,
    event_type: str | None = None,
    recipient: str | None = None,
    channel: str | None = None,
) -> list[dict[str, Any]]:
    """Return captured messages, optionally filtered."""
    with _capture_lock:
        results = list(_captured_messages)
    if event_type:
        results = [m for m in results if m["event_type"] == event_type]
    if recipient:
        results = [m for m in results if m["recipient"] == recipient]
    if channel:
        results = [m for m in results if m["channel"] == channel]
    return results


def clear_captured_messages() -> int:
    """Clear all captured messages. Returns count of cleared items."""
    with _capture_lock:
        count = len(_captured_messages)
        _captured_messages.clear()
    return count


# ---------------------------------------------------------------------------
# Token hashing
# ---------------------------------------------------------------------------


def hash_token(token: str) -> str:
    """Return the SHA-256 hex digest of a token/code string."""
    if not token:
        return ""
    return hashlib.sha256(token.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Public API -- single integration point
# ---------------------------------------------------------------------------


def emit_communication_event(
    event_type: str,
    recipient: str,
    channel: str,
    *,
    subject: str = "",
    body: str = "",
    token: str = "",
    ttl_minutes: int = 0,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Record an outbound communication event.

    Called by email/SMS modules after dispatching a message.

    In **capture mode**, stores the full event (including body) in
    memory so automated tests can retrieve it via the REST API.

    In **audit mode**, logs structured metadata without the body.

    Parameters
    ----------
    event_type:
        Semantic category (e.g. 'magic_link', 'otp',
        'login_notification').
    recipient:
        Destination address (email or phone).
    channel:
        'email' or 'sms'.
    subject:
        Email subject line (optional for SMS).
    body:
        Full message body -- only stored in capture mode.
    token:
        Raw token/code embedded in the message (hashed before storage).
    ttl_minutes:
        How long the token remains valid (informational).
    metadata:
        Arbitrary key-value pairs for additional context.
    """
    token_hashed = hash_token(token)

    event = CommunicationEvent(
        event_type=event_type,
        recipient=recipient,
        channel=channel,
        subject=subject,
        body=body if CAPTURE_MODE else "",
        token_hash=token_hashed,
        ttl_minutes=ttl_minutes,
        metadata=metadata or {},
    )

    if CAPTURE_MODE:
        _store_message(event)
        logger.debug(
            "Captured %s to %s via %s (token_hash=%s)",
            event_type,
            recipient,
            channel,
            token_hashed[:12] if token_hashed else "none",
        )
    else:
        # Audit mode -- structured log, no body
        logger.info(
            "COMMS_AUDIT event_type=%s recipient=%s channel=%s "
            "subject=%r token_hash=%s ttl=%d",
            event_type,
            recipient,
            channel,
            subject,
            token_hashed[:12] if token_hashed else "none",
            ttl_minutes,
        )


# ---------------------------------------------------------------------------
# REST API (capture mode only)
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/test/email-capture",
    tags=["test-capture"],
)


class CapturedMessageResponse(BaseModel):
    """Response model for the capture endpoint."""

    count: int
    messages: list[dict[str, Any]]


class ClearResponse(BaseModel):
    """Response model for the clear endpoint."""

    cleared: int


class StoreRequest(BaseModel):
    """Request model for manually injecting a test message."""

    event_type: str
    recipient: str
    channel: str = "email"
    subject: str = ""
    body: str = ""
    token: str = ""
    ttl_minutes: int = 0
    metadata: dict[str, Any] = {}


@router.get("", response_model=CapturedMessageResponse)
async def list_captured_messages_endpoint(
    event_type: str | None = Query(None),
    recipient: str | None = Query(None),
    channel: str | None = Query(None),
) -> dict[str, Any]:
    """Return captured messages, optionally filtered by query params.

    Returns 404 when capture mode is disabled (production).
    """
    if not CAPTURE_MODE:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=404,
            content={"detail": "Capture mode is not enabled"},
        )
    messages = get_captured_messages(
        event_type=event_type,
        recipient=recipient,
        channel=channel,
    )
    return {"count": len(messages), "messages": messages}


@router.post("", response_model=CapturedMessageResponse)
async def store_captured_message(req: StoreRequest) -> dict[str, Any]:
    """Manually inject a test message into the capture store.

    Returns 404 when capture mode is disabled.
    """
    if not CAPTURE_MODE:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=404,
            content={"detail": "Capture mode is not enabled"},
        )
    emit_communication_event(
        event_type=req.event_type,
        recipient=req.recipient,
        channel=req.channel,
        subject=req.subject,
        body=req.body,
        token=req.token,
        ttl_minutes=req.ttl_minutes,
        metadata=req.metadata,
    )
    messages = get_captured_messages(recipient=req.recipient)
    return {"count": len(messages), "messages": messages}


@router.delete("", response_model=ClearResponse)
async def clear_capture_store() -> dict[str, Any]:
    """Clear all captured messages.

    Returns 404 when capture mode is disabled.
    """
    if not CAPTURE_MODE:
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=404,
            content={"detail": "Capture mode is not enabled"},
        )
    cleared = clear_captured_messages()
    return {"cleared": cleared}
