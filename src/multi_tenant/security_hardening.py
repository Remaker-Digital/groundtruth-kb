"""
Security hardening utilities — input/output sanitization, auth rate limiting,
and API key rotation.

Implements WI #159-163 from the security hardening backlog:
    - WI #159: API key rotation endpoint and mechanism
    - WI #160: Input sanitization for path parameters
    - WI #161: Output sanitization for AI responses
    - WI #163: Rate limiting on authentication endpoints (pre-auth)

Architecture references:
    - Decision #4: API key authentication
    - Decision #5: Per-tenant rate limits
    - Decision #6: Key Vault per-tenant secrets

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import html
import logging
import re
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# WI #160: Input sanitization for path parameters
# ---------------------------------------------------------------------------

# Valid patterns for common path parameters
_TENANT_ID_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)
_CONVERSATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")
_GENERIC_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{1,256}$")

# Characters that should never appear in path parameters
_DANGEROUS_CHARS = re.compile(r"[\x00-\x1f\x7f\\<>\"'`{}|^~]")
_PATH_TRAVERSAL = re.compile(r"\.\./|\.\.\\|%2e%2e|%252e")


def sanitize_tenant_id(tenant_id: str) -> str:
    """Validate and return a tenant_id or raise ValueError.

    Tenant IDs must be valid UUID v4 format. Rejects:
    - Path traversal sequences
    - Null bytes
    - Non-UUID formats

    Args:
        tenant_id: The tenant ID to validate.

    Returns:
        The validated tenant_id (unchanged if valid).

    Raises:
        ValueError: If tenant_id is not a valid UUID.
    """
    if not tenant_id or not _TENANT_ID_PATTERN.match(tenant_id):
        raise ValueError(f"Invalid tenant_id format: must be UUID v4")
    return tenant_id


def sanitize_path_param(value: str, param_name: str = "parameter") -> str:
    """Validate a generic path parameter.

    Rejects:
    - Null bytes (\\x00)
    - Path traversal (../ or ..\\)
    - Control characters
    - HTML/script injection characters
    - Excessively long values (>256 chars)

    Args:
        value: The path parameter value.
        param_name: Name of the parameter (for error messages).

    Returns:
        The validated value (unchanged if valid).

    Raises:
        ValueError: If the value contains dangerous characters.
    """
    if not value:
        raise ValueError(f"Empty {param_name}")

    if len(value) > 256:
        raise ValueError(f"{param_name} too long (max 256 characters)")

    if _DANGEROUS_CHARS.search(value):
        raise ValueError(f"{param_name} contains invalid characters")

    if _PATH_TRAVERSAL.search(value.lower()):
        raise ValueError(f"{param_name} contains path traversal sequence")

    return value


def sanitize_conversation_id(conversation_id: str) -> str:
    """Validate a conversation ID.

    Conversation IDs are alphanumeric with underscores and hyphens.

    Args:
        conversation_id: The conversation ID to validate.

    Returns:
        The validated conversation_id.

    Raises:
        ValueError: If conversation_id format is invalid.
    """
    if not conversation_id or not _CONVERSATION_ID_PATTERN.match(conversation_id):
        raise ValueError("Invalid conversation_id format")
    return conversation_id


# ---------------------------------------------------------------------------
# WI #161: Output sanitization for AI responses
# ---------------------------------------------------------------------------

# Patterns that could be rendered as executable in HTML contexts
_HTML_TAG_PATTERN = re.compile(r"<(?:script|iframe|object|embed|form|input|button|link|meta|base|style)\b", re.IGNORECASE)
_EVENT_HANDLER_PATTERN = re.compile(r"\bon\w+\s*=", re.IGNORECASE)
_JAVASCRIPT_URI_PATTERN = re.compile(r"javascript\s*:", re.IGNORECASE)
_DATA_URI_PATTERN = re.compile(r"data\s*:\s*text/html", re.IGNORECASE)

# Markdown injection patterns
_MARKDOWN_IMAGE_INJECTION = re.compile(r"!\[([^\]]*)\]\(javascript:", re.IGNORECASE)
_MARKDOWN_LINK_INJECTION = re.compile(r"\[([^\]]*)\]\(javascript:", re.IGNORECASE)


def sanitize_ai_response(text: str) -> str:
    """Sanitize AI response text for safe rendering.

    Removes or escapes content that could be rendered as executable
    in HTML or markdown contexts. The Critic agent validates safety
    of the AI response content; this function handles format-level
    injection that the Critic doesn't catch.

    Sanitization rules:
    - Strip dangerous HTML tags (script, iframe, object, embed, form, etc.)
    - Remove event handler attributes (onclick, onload, etc.)
    - Remove javascript: URI schemes
    - Remove data:text/html URIs
    - Escape markdown-based script injection
    - Preserve safe markdown formatting (bold, italic, lists, code blocks)

    Args:
        text: The AI response text.

    Returns:
        Sanitized text safe for rendering.
    """
    if not text:
        return text

    # Remove dangerous HTML tags
    result = _HTML_TAG_PATTERN.sub("[removed]", text)

    # Remove event handlers (onclick=, onload=, etc.)
    result = _EVENT_HANDLER_PATTERN.sub("[removed]=", result)

    # Remove javascript: URIs
    result = _JAVASCRIPT_URI_PATTERN.sub("[removed]:", result)

    # Remove data:text/html URIs
    result = _DATA_URI_PATTERN.sub("[removed]:", result)

    # Sanitize markdown injection
    result = _MARKDOWN_IMAGE_INJECTION.sub(r"![\1]([removed]:", result)
    result = _MARKDOWN_LINK_INJECTION.sub(r"[\1]([removed]:", result)

    return result


def sanitize_for_html(text: str) -> str:
    """Escape text for safe embedding in HTML contexts.

    Uses Python's html.escape() for full HTML entity encoding.
    Use this when inserting text into HTML templates.

    Args:
        text: The text to escape.

    Returns:
        HTML-escaped text.
    """
    if not text:
        return text
    return html.escape(text, quote=True)


# ---------------------------------------------------------------------------
# WI #163: Pre-authentication rate limiting
# ---------------------------------------------------------------------------

# Maximum failed auth attempts per IP before temporary block
MAX_FAILED_AUTH_PER_IP = 10
# Window for counting failed attempts (seconds)
FAILED_AUTH_WINDOW_SECONDS = 300  # 5 minutes
# Block duration after exceeding failed auth limit (seconds)
AUTH_BLOCK_DURATION_SECONDS = 900  # 15 minutes


# ---------------------------------------------------------------------------
# Distributed rate limiting abstraction (SPEC-1626)
# ---------------------------------------------------------------------------


class RateLimitBackend:
    """Protocol for pluggable rate limit storage backends.

    The sliding-window-counter pattern is duplicated across 5+ modules
    (email_verification, magic_link_auth, widget_otp_verification,
    admin_apikey_api, standalone_auth). This abstraction allows all of
    them to share the same interface while supporting different storage
    backends:

        - ``InMemoryRateLimitBackend``: Current behavior — single-process,
          no external dependencies. Suitable for development and
          single-replica deployments.
        - Future: ``RedisRateLimitBackend``, ``CosmosRateLimitBackend``
          for multi-replica horizontal scaling.

    Usage::

        backend = get_rate_limit_backend()
        if backend.is_limited("ip:192.168.1.1", max_requests=3, window_seconds=300):
            return  # Rate limited
    """

    def is_limited(self, key: str, *, max_requests: int, window_seconds: float) -> bool:
        """Check and record a request. Returns True if rate limited."""
        raise NotImplementedError

    def reset(self, key: str) -> None:
        """Clear rate limit state for a key (e.g., on successful auth)."""
        raise NotImplementedError

    def cleanup(self) -> int:
        """Remove expired entries. Returns count of removed entries."""
        raise NotImplementedError


class InMemoryRateLimitBackend(RateLimitBackend):
    """In-memory sliding window rate limiter — single-process only.

    Thread-safe for asyncio (cooperative multitasking). For horizontal
    scaling across multiple replicas, swap to a Redis or Cosmos backend.
    """

    def __init__(self) -> None:
        self._windows: dict[str, list[float]] = {}

    def is_limited(self, key: str, *, max_requests: int, window_seconds: float) -> bool:
        now = time.time()
        window_start = now - window_seconds
        if key in self._windows:
            self._windows[key] = [
                ts for ts in self._windows[key] if ts > window_start
            ]
        requests = self._windows.get(key, [])
        if len(requests) >= max_requests:
            return True
        self._windows.setdefault(key, []).append(now)
        return False

    def reset(self, key: str) -> None:
        self._windows.pop(key, None)

    def cleanup(self) -> int:
        now = time.time()
        removed = 0
        empty_keys = []
        for key, timestamps in self._windows.items():
            before = len(timestamps)
            self._windows[key] = [ts for ts in timestamps if ts > now - 600]
            removed += before - len(self._windows[key])
            if not self._windows[key]:
                empty_keys.append(key)
        for key in empty_keys:
            del self._windows[key]
            removed += 1
        return removed


# -- Singleton accessor for the rate limit backend -------------------------

_rate_limit_backend: RateLimitBackend | None = None


def get_rate_limit_backend() -> RateLimitBackend:
    """Return the shared rate limit backend (creates InMemory if none set)."""
    global _rate_limit_backend
    if _rate_limit_backend is None:
        _rate_limit_backend = InMemoryRateLimitBackend()
    return _rate_limit_backend


def set_rate_limit_backend(backend: RateLimitBackend) -> None:
    """Swap the rate limit backend (e.g., to Redis for production)."""
    global _rate_limit_backend
    _rate_limit_backend = backend


# ---------------------------------------------------------------------------
# Pre-auth rate limiting (original implementation)
# ---------------------------------------------------------------------------


@dataclass
class _AuthAttemptTracker:
    """Tracks failed authentication attempts per IP address."""

    timestamps: list[float] = field(default_factory=list)
    blocked_until: float = 0.0


class PreAuthRateLimiter:
    """Rate limiter for failed authentication attempts.

    Tracks failed authentication attempts by IP address and temporarily
    blocks IPs that exceed the threshold. This prevents brute-force
    API key guessing attacks.

    This limiter runs BEFORE tenant resolution, so it operates on
    IP addresses rather than tenant IDs. It complements the per-tenant
    RateLimitMiddleware which runs after authentication.

    Configuration:
        max_attempts: Max failed auth attempts per window (default 10)
        window_seconds: Rolling window for attempt counting (default 300s)
        block_seconds: Block duration after exceeding limit (default 900s)
    """

    def __init__(
        self,
        max_attempts: int = MAX_FAILED_AUTH_PER_IP,
        window_seconds: int = FAILED_AUTH_WINDOW_SECONDS,
        block_seconds: int = AUTH_BLOCK_DURATION_SECONDS,
    ) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._block_seconds = block_seconds
        self._trackers: dict[str, _AuthAttemptTracker] = defaultdict(
            _AuthAttemptTracker
        )

    def is_blocked(self, client_ip: str) -> bool:
        """Check if an IP is currently blocked.

        Args:
            client_ip: The client's IP address.

        Returns:
            True if the IP is blocked.
        """
        tracker = self._trackers.get(client_ip)
        if tracker is None:
            return False

        now = time.monotonic()
        if tracker.blocked_until > now:
            return True

        # Block expired — reset
        if tracker.blocked_until > 0:
            tracker.blocked_until = 0.0
            tracker.timestamps.clear()

        return False

    def record_failure(self, client_ip: str) -> bool:
        """Record a failed authentication attempt.

        Args:
            client_ip: The client's IP address.

        Returns:
            True if the IP is now blocked (threshold exceeded).
        """
        now = time.monotonic()
        tracker = self._trackers[client_ip]

        # Prune old attempts outside the window
        cutoff = now - self._window_seconds
        tracker.timestamps = [t for t in tracker.timestamps if t > cutoff]

        # Record this attempt
        tracker.timestamps.append(now)

        # Check threshold
        if len(tracker.timestamps) >= self._max_attempts:
            tracker.blocked_until = now + self._block_seconds
            logger.warning(
                "IP blocked for failed auth attempts: ip=%s attempts=%d blocked_for=%ds",
                client_ip, len(tracker.timestamps), self._block_seconds,
            )
            return True

        return False

    def record_success(self, client_ip: str) -> None:
        """Record a successful authentication (resets failure counter).

        Args:
            client_ip: The client's IP address.
        """
        if client_ip in self._trackers:
            del self._trackers[client_ip]

    def get_remaining_attempts(self, client_ip: str) -> int:
        """Get remaining allowed failed attempts for an IP.

        Args:
            client_ip: The client's IP address.

        Returns:
            Number of remaining attempts before block.
        """
        tracker = self._trackers.get(client_ip)
        if tracker is None:
            return self._max_attempts

        now = time.monotonic()
        cutoff = now - self._window_seconds
        recent = sum(1 for t in tracker.timestamps if t > cutoff)
        return max(0, self._max_attempts - recent)

    def cleanup(self) -> int:
        """Remove expired tracker entries.

        Returns:
            Number of entries removed.
        """
        now = time.monotonic()
        cutoff = now - self._window_seconds
        expired = [
            ip for ip, tracker in self._trackers.items()
            if tracker.blocked_until < now and all(t <= cutoff for t in tracker.timestamps)
        ]
        for ip in expired:
            del self._trackers[ip]
        return len(expired)


# Module-level singleton
_pre_auth_limiter: PreAuthRateLimiter | None = None


def get_pre_auth_limiter() -> PreAuthRateLimiter:
    """Get the module-level pre-auth rate limiter singleton."""
    global _pre_auth_limiter
    if _pre_auth_limiter is None:
        _pre_auth_limiter = PreAuthRateLimiter()
    return _pre_auth_limiter


# Background cleanup task (SPEC-1623)
_cleanup_task: Any = None
_CLEANUP_INTERVAL_SECONDS = 300  # 5 minutes


async def _pre_auth_cleanup_loop() -> None:
    """Periodically remove expired entries from the pre-auth rate limiter."""
    import asyncio

    while True:
        await asyncio.sleep(_CLEANUP_INTERVAL_SECONDS)
        try:
            removed = get_pre_auth_limiter().cleanup()
            if removed > 0:
                logger.info("Pre-auth cleanup: removed %d expired tracker entries", removed)
        except Exception:
            logger.debug("Pre-auth cleanup cycle failed", exc_info=True)


async def start_pre_auth_cleanup() -> None:
    """Start the pre-auth cleanup background task (SPEC-1623)."""
    import asyncio

    global _cleanup_task  # noqa: PLW0603
    _cleanup_task = asyncio.create_task(_pre_auth_cleanup_loop())
    logger.info("Pre-auth cleanup task started (%ds interval)", _CLEANUP_INTERVAL_SECONDS)


async def stop_pre_auth_cleanup() -> None:
    """Stop the pre-auth cleanup background task."""
    import asyncio

    global _cleanup_task  # noqa: PLW0603
    if _cleanup_task and not _cleanup_task.done():
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("Pre-auth cleanup task stopped")
    _cleanup_task = None


class PreAuthRateLimitMiddleware:
    """ASGI middleware that blocks IPs with too many failed auth attempts.

    Integrates with the TenantAuthMiddleware: when auth fails, the
    failure is recorded against the client IP. After exceeding the
    threshold, all requests from that IP are blocked for a cooldown
    period.

    This middleware should be registered AFTER TenantAuthMiddleware
    in the Starlette stack (meaning it runs BEFORE auth due to reverse
    order).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._limiter = get_pre_auth_limiter()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Skip rate limiting for auth-exempt paths (health, webhooks, docs)
        path = scope.get("path", "")
        from src.multi_tenant.auth import is_auth_exempt

        if is_auth_exempt(path):
            await self.app(scope, receive, send)
            return

        # Extract client IP
        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        # Check if blocked
        if self._limiter.is_blocked(client_ip):
            if scope["type"] == "http":
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many failed authentication attempts. "
                        "Please try again later.",
                    },
                    headers={"Retry-After": str(AUTH_BLOCK_DURATION_SECONDS)},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


# ---------------------------------------------------------------------------
# WI #159: API key rotation
# ---------------------------------------------------------------------------

rotation_router = APIRouter(prefix="/api/keys", tags=["security"])

# Service reference (set during app startup)
_secret_service: Any = None
_tenant_repo: Any = None


def configure_key_rotation_services(
    secret_service: Any,
    tenant_repo: Any,
) -> None:
    """Wire services for API key rotation endpoints."""
    global _secret_service, _tenant_repo
    _secret_service = secret_service
    _tenant_repo = tenant_repo


class KeyRotationResponse(BaseModel):
    """Response from API key rotation."""

    new_api_key: str
    old_key_valid_until: str
    message: str


class WidgetKeyRotationResponse(BaseModel):
    """Response from widget key rotation."""

    new_widget_key: str
    message: str


def _generate_api_key() -> str:
    """Generate a new API key.

    Format: arx_{random_hex_40}
    """
    return f"arx_{secrets.token_hex(20)}"


def _generate_widget_key(tenant_id: str) -> str:
    """Generate a new publishable widget key.

    Delegates to the canonical implementation in auth.py.
    Kept as a private wrapper for backward compatibility within this module.
    """
    from src.multi_tenant.auth import generate_widget_key

    return generate_widget_key(tenant_id)


@rotation_router.post("/rotate", response_model=KeyRotationResponse)
async def rotate_api_key(request: Request) -> KeyRotationResponse:
    """Rotate the tenant's API key.

    Generates a new API key and stores its hash. The old key remains
    valid for a 24-hour grace period to avoid service interruption
    during key rotation.

    Requires authentication (X-API-Key header with current key).
    """
    if _secret_service is None or _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Key rotation not configured")

    tenant_ctx = getattr(request.state, "tenant_context", None)
    if not tenant_ctx:
        raise HTTPException(status_code=401, detail="Authentication required")

    tenant_id = tenant_ctx.tenant_id

    # Generate new API key
    new_key = _generate_api_key()
    new_hash = hashlib.sha256(new_key.encode()).hexdigest()

    # Store old key hash for grace period (24 hours)
    import datetime as dt

    grace_until = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=24)

    # Read current key hash for grace period
    tenant = await _tenant_repo.read(tenant_id, tenant_id)
    old_hash = tenant.get("api_key_hash") if tenant else None

    # Update tenant with new key hash
    operations = [
        {"op": "set", "path": "/api_key_hash", "value": new_hash},
        {"op": "set", "path": "/updated_at", "value": dt.datetime.now(dt.timezone.utc).isoformat()},
    ]

    # Store old hash for grace period (append to a list field or separate doc)
    if old_hash:
        operations.append({
            "op": "set",
            "path": "/previous_api_key_hash",
            "value": old_hash,
        })
        operations.append({
            "op": "set",
            "path": "/previous_key_valid_until",
            "value": grace_until.isoformat(),
        })

    await _tenant_repo.patch(tenant_id, tenant_id, operations=operations)

    logger.info("API key rotated: tenant=%s grace_until=%s", tenant_id, grace_until.isoformat())

    return KeyRotationResponse(
        new_api_key=new_key,
        old_key_valid_until=grace_until.isoformat(),
        message="API key rotated. Old key valid for 24 hours.",
    )


@rotation_router.post("/rotate-widget-key", response_model=WidgetKeyRotationResponse)
async def rotate_widget_key(request: Request) -> WidgetKeyRotationResponse:
    """Rotate the tenant's publishable widget key.

    Generates a new widget key. Unlike API keys, widget keys have no
    grace period — the new key takes effect immediately.

    Requires authentication (X-API-Key or Bearer token).
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Key rotation not configured")

    tenant_ctx = getattr(request.state, "tenant_context", None)
    if not tenant_ctx:
        raise HTTPException(status_code=401, detail="Authentication required")

    tenant_id = tenant_ctx.tenant_id

    # Generate new widget key
    new_key = _generate_widget_key(tenant_id)
    new_hash = hashlib.sha256(new_key.encode()).hexdigest()

    import datetime as dt

    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

    await _tenant_repo.patch(
        tenant_id,
        tenant_id,
        operations=[
            {"op": "set", "path": "/widget_key_hash", "value": new_hash},
            {"op": "set", "path": "/updated_at", "value": now_iso},
        ],
    )

    # Also update the raw key in PreferencesDocument (admin UI + activation gate).
    # Bug fix (S85): Preferences doc ID is {tenant_id}:{version}, NOT
    # {tenant_id}:active.  Must query for the active doc first to get its real ID.
    try:
        from src.multi_tenant.repositories.preferences import PreferencesRepository

        prefs_repo = PreferencesRepository()
        active_prefs = await prefs_repo.get_active(tenant_id)
        if active_prefs and active_prefs.get("id"):
            await prefs_repo.patch(
                tenant_id,
                active_prefs["id"],
                operations=[
                    {"op": "set", "path": "/widget_key", "value": new_key},
                    {"op": "set", "path": "/updated_at", "value": now_iso},
                ],
            )
        else:
            logger.warning(
                "No active PreferencesDocument found for widget_key update: "
                "tenant=%s (key will sync on next activate)",
                tenant_id,
            )
    except Exception as exc:
        logger.warning(
            "Widget key rotated on TenantDocument but PreferencesDocument "
            "update failed (will sync on next activate): tenant=%s error=%s",
            tenant_id,
            exc,
        )

    # Invalidate config cache so /api/config returns the new widget_key
    # immediately (without waiting for the 60-second cache TTL to expire).
    try:
        from src.multi_tenant.tenant_config_processor import get_config_processor

        processor = get_config_processor()
        processor._invalidate_cache(tenant_id)
    except Exception:
        pass  # Cache will expire naturally within 60s

    logger.info("Widget key rotated: tenant=%s", tenant_id)

    return WidgetKeyRotationResponse(
        new_widget_key=new_key,
        message="Widget key rotated. Update your website embed code.",
    )
