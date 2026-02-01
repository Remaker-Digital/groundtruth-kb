"""Security middleware — request body limits, JSON depth, security headers (WI #157-159).

Provides three middleware components for defense-in-depth:

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

        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                for name, value in SECURITY_HEADERS.items():
                    headers.append((name.lower().encode(), value.encode()))

                if is_https:
                    headers.append(
                        (b"strict-transport-security", HSTS_HEADER.encode())
                    )

                # Add Server-Timing header with total processing time
                elapsed_ms = (time.monotonic() - start_time) * 1000
                headers.append(
                    (b"server-timing", f"total;dur={elapsed_ms:.1f}".encode())
                )

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
