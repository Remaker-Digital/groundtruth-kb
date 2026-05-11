# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Security middleware — trusted proxy, request body limits, JSON depth, security headers.

Provides four middleware components for defense-in-depth:

0. TrustedProxyMiddleware (SPEC-1663):
   Extracts real client IP from trusted reverse proxy headers
   (Cloudflare, Azure Front Door, generic X-Forwarded-For) and
   rewrites scope["client"] so all downstream middleware and endpoints
   see the correct client IP without any code changes.

1. RequestBodyLimitMiddleware (WI #157):
   Rejects request bodies exceeding 1 MB (configurable). Prevents
   memory exhaustion and DoS via oversized payloads.

2. JsonDepthValidationMiddleware (WI #158):
   Rejects JSON payloads with nesting depth > 50 levels. Prevents
   stack overflow and excessive memory use from deeply nested payloads.

3. SecurityHeadersMiddleware (WI #159):
   Adds standard security response headers to all responses:
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - X-XSS-Protection: 0 (modern browsers, CSP preferred)
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy: camera=(), microphone=(), geolocation=()
   - Cache-Control: no-store (for API responses)
   - Strict-Transport-Security (when HTTPS detected)

Architecture references:
    - Decision #5: Rate limiting and body size enforcement
    - OWASP API Security Top 10 (2023)
    - Shopify App Store security review requirements

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Maximum request body size (bytes) — 1 MB default
MAX_BODY_SIZE_BYTES = 1_048_576  # 1 MB

# Maximum JSON nesting depth
MAX_JSON_DEPTH = 50

# Trusted proxy modes (set via TRUSTED_PROXY env var)
TRUSTED_PROXY_CLOUDFLARE = "cloudflare"
TRUSTED_PROXY_FORWARDED_FOR = "x-forwarded-for"

# IPv4/IPv6 validation — loose check, not full RFC validation.
# Accepts: 192.168.1.1, ::1, 2001:db8::1, 10.0.0.1
_IP_PATTERN = re.compile(
    r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"  # IPv4
    r"|^[0-9a-fA-F:]+$"                  # IPv6 (simplified)
)


# ---------------------------------------------------------------------------
# 0. TrustedProxyMiddleware (SPEC-1663)
# ---------------------------------------------------------------------------


class TrustedProxyMiddleware:
    """ASGI middleware that extracts real client IP from reverse proxy headers.

    When running behind Cloudflare, Azure Front Door, or other reverse
    proxies, the ASGI ``scope["client"]`` contains the proxy's internal IP
    (e.g., ``10.x.x.x``), not the actual client IP. This middleware extracts
    the real IP from trusted headers and rewrites ``scope["client"]`` so
    **all downstream middleware and endpoints** see the correct client IP
    without any code changes.

    This is critical for:
    - Pre-auth rate limiting (``PreAuthRateLimitMiddleware``)
    - Per-tenant rate limiting (``RateLimitMiddleware``)
    - Magic link / OTP / email verification rate limits
    - Stripe webhook IP allowlist
    - Abuse logging and SLA monitoring

    Modes (configured via ``TRUSTED_PROXY`` env var):

    - ``"cloudflare"``: Trust ``CF-Connecting-IP`` header (set and
      overwritten by Cloudflare on every request — cannot be spoofed by
      clients). Also reads ``CF-IPCountry`` and ``CF-Ray`` into scope state.
    - ``"x-forwarded-for"``: Trust first IP in ``X-Forwarded-For`` header
      (generic reverse proxy mode — suitable when the outermost proxy
      strips/overwrites the header).
    - Unset/empty: Disabled — use direct ``scope["client"]`` IP.

    Security notes:
    - ``CF-Connecting-IP`` is safe to trust because Cloudflare always
      overwrites it with the actual connecting IP. Clients cannot spoof it.
    - ``X-Forwarded-For`` can be spoofed if intermediary proxies don't
      strip client-supplied values. Only use this mode when the outermost
      proxy (e.g., Azure Front Door) overwrites the header.
    - The middleware validates that extracted IPs look like valid IPv4/IPv6
      addresses before applying them. Invalid values are logged and ignored.

    Must be registered as the **outermost** middleware (first registered =
    outermost in Starlette's reverse-order model) so that it runs before
    all other middleware.
    """

    def __init__(self, app: ASGIApp, *, mode: str | None = None) -> None:
        self.app = app
        self.mode = (mode or os.environ.get("TRUSTED_PROXY", "")).strip().lower()
        if self.mode and self.mode not in (
            TRUSTED_PROXY_CLOUDFLARE,
            TRUSTED_PROXY_FORWARDED_FOR,
        ):
            logger.warning(
                "Unknown TRUSTED_PROXY mode %r — proxy header extraction disabled. "
                "Valid modes: 'cloudflare', 'x-forwarded-for'",
                self.mode,
            )
            self.mode = ""

        if self.mode:
            logger.info("TrustedProxyMiddleware enabled: mode=%s", self.mode)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self.mode:
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        real_ip: str | None = None
        original_ip = scope.get("client", ("unknown", 0))

        if self.mode == TRUSTED_PROXY_CLOUDFLARE:
            # CF-Connecting-IP is a single IP, always set by Cloudflare
            cf_ip = headers.get(b"cf-connecting-ip", b"").decode("latin-1").strip()
            if cf_ip and _is_valid_ip(cf_ip):
                real_ip = cf_ip
            elif cf_ip:
                logger.warning(
                    "Invalid CF-Connecting-IP header value: %r (ignored)", cf_ip,
                )

            # Store Cloudflare metadata in scope state for logging/analytics
            state = scope.setdefault("state", {})
            cf_country = headers.get(b"cf-ipcountry", b"").decode("latin-1").strip()
            cf_ray = headers.get(b"cf-ray", b"").decode("latin-1").strip()
            if cf_country:
                state["cf_ipcountry"] = cf_country
            if cf_ray:
                state["cf_ray"] = cf_ray

        elif self.mode == TRUSTED_PROXY_FORWARDED_FOR:
            # X-Forwarded-For: client, proxy1, proxy2 — first IP is the client
            xff = headers.get(b"x-forwarded-for", b"").decode("latin-1").strip()
            if xff:
                first_ip = xff.split(",")[0].strip()
                if _is_valid_ip(first_ip):
                    real_ip = first_ip
                else:
                    logger.warning(
                        "Invalid first IP in X-Forwarded-For: %r (ignored)", first_ip,
                    )

        if real_ip:
            # Preserve the original port (or 0 if not available)
            original_port = original_ip[1] if len(original_ip) > 1 else 0
            scope["client"] = (real_ip, original_port)
            logger.debug(
                "Real client IP extracted: %s (was %s, mode=%s)",
                real_ip, original_ip[0], self.mode,
            )

        await self.app(scope, receive, send)


def _is_valid_ip(value: str) -> bool:
    """Loosely validate that a string looks like an IPv4 or IPv6 address.

    This is a format sanity check, not full RFC compliance. The goal is to
    reject obvious non-IP values (injection attempts, hostnames) while
    accepting all reasonable IP address formats.
    """
    if not value or len(value) > 45:  # Max IPv6 length
        return False
    return bool(_IP_PATTERN.match(value))

# Paths exempt from body size limit (streaming endpoints may need larger)
BODY_LIMIT_EXEMPT_PREFIXES = (
    "/api/chat/stream",
)


# ---------------------------------------------------------------------------
# 1. RequestBodyLimitMiddleware (WI #157)
# ---------------------------------------------------------------------------


class RequestBodyLimitMiddleware:
    """ASGI middleware that rejects request bodies exceeding the size limit.

    Uses a raw ASGI middleware (not BaseHTTPMiddleware) to intercept the
    body before it's fully read into memory. This is more efficient than
    reading the full body and then checking the size.

    Returns HTTP 413 Payload Too Large if the Content-Length header exceeds
    the limit, or if accumulated body chunks exceed the limit.
    """

    def __init__(
        self,
        app: ASGIApp,
        max_body_size: int = MAX_BODY_SIZE_BYTES,
    ) -> None:
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check Content-Length header if present
        headers = dict(scope.get("headers", []))
        content_length_raw = headers.get(b"content-length", b"")
        if content_length_raw:
            try:
                content_length = int(content_length_raw)
                if content_length > self.max_body_size:
                    # Check exemptions
                    path = scope.get("path", "")
                    if not path.startswith(BODY_LIMIT_EXEMPT_PREFIXES):
                        response = JSONResponse(
                            status_code=413,
                            content={
                                "error": "Request body too large",
                                "max_bytes": self.max_body_size,
                            },
                        )
                        await response(scope, receive, send)
                        return
            except (ValueError, TypeError):
                pass

        # Track accumulated body size for chunked transfers
        accumulated = 0
        path = scope.get("path", "")
        is_exempt = path.startswith(BODY_LIMIT_EXEMPT_PREFIXES)

        async def size_limited_receive() -> Message:
            nonlocal accumulated
            message = await receive()
            if message["type"] == "http.request" and not is_exempt:
                body = message.get("body", b"")
                accumulated += len(body)
                if accumulated > self.max_body_size:
                    logger.warning(
                        "Request body exceeds limit: path=%s accumulated=%d max=%d",
                        path, accumulated, self.max_body_size,
                    )
                    # Raise to trigger error handling
                    raise _BodyTooLargeError()
            return message

        try:
            await self.app(scope, size_limited_receive, send)
        except _BodyTooLargeError:
            response = JSONResponse(
                status_code=413,
                content={
                    "error": "Request body too large",
                    "max_bytes": self.max_body_size,
                },
            )
            await response(scope, receive, send)


class _BodyTooLargeError(Exception):
    """Internal exception for body size limit exceeded."""


# ---------------------------------------------------------------------------
# 2. JsonDepthValidationMiddleware (WI #158)
# ---------------------------------------------------------------------------


def validate_json_depth(
    data: Any,
    max_depth: int = MAX_JSON_DEPTH,
    current_depth: int = 0,
) -> bool:
    """Validate that a JSON structure does not exceed the maximum nesting depth.

    Args:
        data: Parsed JSON data (dict, list, or scalar).
        max_depth: Maximum allowed nesting depth.
        current_depth: Current recursion depth (internal).

    Returns:
        True if the depth is within limits.

    Raises:
        ValueError: If the nesting depth exceeds max_depth.
    """
    if current_depth > max_depth:
        raise ValueError(
            f"JSON nesting depth exceeds maximum ({max_depth} levels)"
        )

    if isinstance(data, dict):
        for value in data.values():
            validate_json_depth(value, max_depth, current_depth + 1)
    elif isinstance(data, list):
        for item in data:
            validate_json_depth(item, max_depth, current_depth + 1)

    return True


class JsonDepthValidationMiddleware(BaseHTTPMiddleware):
    """Validates JSON request body nesting depth.

    Reads the request body for JSON content types and rejects payloads
    with nesting exceeding MAX_JSON_DEPTH levels.

    Only applies to requests with Content-Type: application/json.
    """

    def __init__(self, app: Any, max_depth: int = MAX_JSON_DEPTH) -> None:
        super().__init__(app)
        self.max_depth = max_depth

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return await call_next(request)

        # Only validate if there's a body
        if request.method in ("GET", "DELETE", "HEAD", "OPTIONS"):
            return await call_next(request)

        try:
            body = await request.body()
            if body:
                parsed = json.loads(body)
                validate_json_depth(parsed, self.max_depth)
        except json.JSONDecodeError:
            # Let FastAPI/Pydantic handle JSON parse errors
            pass
        except ValueError as exc:
            logger.warning(
                "JSON depth limit exceeded: path=%s error=%s",
                request.url.path, exc,
            )
            return JSONResponse(
                status_code=400,
                content={
                    "error": str(exc),
                    "max_depth": self.max_depth,
                },
            )

        return await call_next(request)


# ---------------------------------------------------------------------------
# 3. SecurityHeadersMiddleware (WI #159)
# ---------------------------------------------------------------------------


# Standard security headers for API responses
SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    # X-XSS-Protection: 0 disables the legacy XSS filter.
    # Modern approach is Content-Security-Policy (CSP).
    "X-XSS-Protection": "0",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # Prevent API responses from being cached
    "Cache-Control": "no-store",
}

# HSTS header value (1 year, include subdomains)
HSTS_HEADER = "max-age=31536000; includeSubDomains"


class SecurityHeadersMiddleware:
    """ASGI middleware that adds security headers to all HTTP responses.

    Adds standard security headers per OWASP recommendations. HSTS is
    only added when the request appears to be over HTTPS (detected via
    the X-Forwarded-Proto header or the ASGI scope scheme).

    Also records request latency for SLA monitoring (WI #191) since this
    is the outermost middleware and wraps the full request lifecycle.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        import time

        start_time = time.monotonic()

        # Detect HTTPS from scope or X-Forwarded-Proto header
        is_https = scope.get("scheme") == "https"
        if not is_https:
            headers = dict(scope.get("headers", []))
            proto = headers.get(b"x-forwarded-proto", b"").decode("latin-1")
            is_https = proto == "https"

        # Check if this is a Shopify embedded admin path — these need to be
        # frameable by Shopify's admin iframe, so X-Frame-Options: DENY must
        # be replaced with CSP frame-ancestors allowing Shopify domains.
        request_path = scope.get("path", "")
        is_shopify_admin = request_path.startswith("/admin/")

        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                for name, value in SECURITY_HEADERS.items():
                    # Skip X-Frame-Options for Shopify embedded admin (uses CSP instead)
                    if name == "X-Frame-Options" and is_shopify_admin:
                        continue
                    # Skip Cache-Control: no-store for admin static assets
                    if name == "Cache-Control" and is_shopify_admin:
                        continue
                    headers.append((name.lower().encode(), value.encode()))

                # Shopify embedded admin: allow framing from Shopify domains
                if is_shopify_admin:
                    headers.append((
                        b"content-security-policy",
                        b"frame-ancestors https://*.myshopify.com https://admin.shopify.com",
                    ))

                if is_https:
                    headers.append(
                        (b"strict-transport-security", HSTS_HEADER.encode())
                    )

                # Add Server-Timing header with total processing time
                elapsed_ms = (time.monotonic() - start_time) * 1000
                headers.append(
                    (b"server-timing", f"total;dur={elapsed_ms:.1f}".encode())
                )

                # Suppress Server header to prevent framework version leakage.
                # Uvicorn's --no-server-header flag is the primary defense;
                # this is a belt-and-suspenders fallback at the ASGI level.
                headers = [
                    (k, v) for k, v in headers
                    if k != b"server"
                ]
                headers.append((b"server", b"Agent Red"))

                message["headers"] = headers

            await send(message)

        try:
            await self.app(scope, receive, send_with_security_headers)
        finally:
            # Record latency for SLA monitoring (WI #191)
            elapsed_ms = (time.monotonic() - start_time) * 1000
            try:
                from src.multi_tenant.sla_monitoring import get_sla_monitor

                monitor = get_sla_monitor()
                # Extract tenant_id if set by TenantAuthMiddleware
                state = scope.get("state", {})
                tenant_ctx = state.get("tenant_context")
                tenant_id = (
                    getattr(tenant_ctx, "tenant_id", None)
                    if tenant_ctx
                    else None
                )
                if tenant_id:
                    monitor.record_latency(tenant_id, elapsed_ms)
                else:
                    # Platform-wide only (unauthenticated requests)
                    monitor.record_latency("__platform__", elapsed_ms)
            except Exception:
                pass  # SLA recording is best-effort
