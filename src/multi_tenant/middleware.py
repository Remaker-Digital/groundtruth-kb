"""
FastAPI middleware and dependencies for tenant resolution and rate limiting.

Wires the authentication module into the HTTP request pipeline. Provides:

1. TenantAuthMiddleware — Starlette middleware that authenticates every
   request and injects TenantContext into request.state.
2. get_tenant_context() — FastAPI dependency that extracts the
   TenantContext from request.state for use in route handlers.
3. require_tier() — FastAPI dependency factory that enforces minimum
   tier requirements on specific endpoints.
4. RateLimitMiddleware — Per-tenant rate limiting (Decision #5).

Usage in route handlers:
    from src.multi_tenant.middleware import get_tenant_context, require_tier
    from src.multi_tenant.auth import TenantContext

    @router.get("/data")
    async def get_data(ctx: TenantContext = Depends(get_tenant_context)):
        # ctx.tenant_id is guaranteed to be valid and authenticated
        results = await repo.query(ctx.tenant_id, ...)
        return results

    @router.post("/advanced")
    async def advanced_feature(
        ctx: TenantContext = Depends(require_tier(TenantTier.PROFESSIONAL)),
    ):
        # Only Professional and Enterprise tenants can access this
        ...

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any, Callable

from fastapi import Depends, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from src.multi_tenant.auth import (
    API_KEY_HEADER,
    AuthenticationError,
    TenantContext,
    TenantInactiveError,
    extract_bearer_token,
    extract_shop_domain,
    is_auth_exempt,
    validate_tenant_status,
    verify_api_key,
    verify_shopify_session_token,
)
from src.multi_tenant.cosmos_schema import TIER_DEFAULTS, TenantStatus, TenantTier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tenant resolution functions
#
# These are injected into the middleware at startup. They default to None
# and must be set via configure_tenant_resolution() before the middleware
# processes authenticated requests.
# ---------------------------------------------------------------------------

_resolve_by_shop_domain: Callable | None = None
_resolve_by_api_key_hash: Callable | None = None


def configure_tenant_resolution(
    resolve_by_shop_domain: Callable,
    resolve_by_api_key_hash: Callable,
) -> None:
    """Configure the tenant resolution functions.

    Called once during application startup after repositories are
    initialized.

    Args:
        resolve_by_shop_domain: Async function that accepts a shop
            domain string and returns a tenant dict or None.
        resolve_by_api_key_hash: Async function that accepts an API
            key hash string and returns a tenant dict or None.
    """
    global _resolve_by_shop_domain, _resolve_by_api_key_hash
    _resolve_by_shop_domain = resolve_by_shop_domain
    _resolve_by_api_key_hash = resolve_by_api_key_hash
    logger.info("Tenant resolution functions configured")


# ---------------------------------------------------------------------------
# TenantAuthMiddleware
# ---------------------------------------------------------------------------


class TenantAuthMiddleware(BaseHTTPMiddleware):
    """Authenticate every request and inject TenantContext.

    Processing order:
        1. Check if path is auth-exempt (webhooks, health, docs).
        2. Extract credentials (Bearer token or X-API-Key header).
        3. Verify credentials (JWT decode or API key hash lookup).
        4. Resolve tenant_id from verified identity.
        5. Validate tenant status (ACTIVE or PAST_DUE).
        6. Store TenantContext in request.state.tenant_context.
        7. Forward to route handler.

    On authentication failure, returns a JSON error response without
    forwarding to the handler. This prevents any unauthenticated
    code from executing.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        # Skip auth for exempt paths
        if is_auth_exempt(request.url.path):
            return await call_next(request)

        try:
            tenant_context = await self._authenticate(request)
            request.state.tenant_context = tenant_context
        except AuthenticationError as exc:
            logger.warning(
                "Auth failed: path=%s method=%s error=%s",
                request.url.path, request.method, exc.message,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.message},
            )

        return await call_next(request)

    async def _authenticate(self, request: Request) -> TenantContext:
        """Authenticate the request and return a TenantContext.

        Tries Shopify session token first (Bearer), then API key.
        """
        # Try Shopify session token (Authorization: Bearer <jwt>)
        authorization = request.headers.get("authorization")
        bearer_token = extract_bearer_token(authorization)

        if bearer_token:
            return await self._auth_shopify(bearer_token)

        # Try API key (X-API-Key header)
        api_key = request.headers.get(API_KEY_HEADER)
        if api_key:
            return await self._auth_api_key(api_key)

        # No credentials provided
        raise AuthenticationError(
            "Authentication required. Provide a Shopify session token "
            "(Authorization: Bearer <token>) or an API key (X-API-Key header)."
        )

    async def _auth_shopify(self, token: str) -> TenantContext:
        """Authenticate via Shopify session token."""
        # Verify JWT and extract claims
        payload = verify_shopify_session_token(token)
        shop_domain = extract_shop_domain(payload)

        if not shop_domain:
            raise AuthenticationError(
                "Could not extract shop domain from session token."
            )

        # Resolve tenant by shop domain
        if _resolve_by_shop_domain is None:
            raise AuthenticationError(
                "Tenant resolution not configured.", status_code=500,
            )

        tenant = await _resolve_by_shop_domain(shop_domain)
        if tenant is None:
            raise AuthenticationError(
                f"No tenant found for shop domain: {shop_domain}"
            )

        tenant_id = tenant["tenant_id"]
        status = TenantStatus(tenant.get("status", "active"))
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None

        # Validate tenant is allowed to make requests
        validate_tenant_status(tenant_id, status)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="shopify_session",
            shop_domain=shop_domain,
            user_id=payload.get("sub"),
            session_id=payload.get("sid"),
        )

    async def _auth_api_key(self, api_key: str) -> TenantContext:
        """Authenticate via API key."""
        if _resolve_by_api_key_hash is None:
            raise AuthenticationError(
                "Tenant resolution not configured.", status_code=500,
            )

        tenant = await verify_api_key(api_key, _resolve_by_api_key_hash)

        tenant_id = tenant["tenant_id"]
        status = TenantStatus(tenant.get("status", "active"))
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None

        validate_tenant_status(tenant_id, status)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="api_key",
        )


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------


async def get_tenant_context(request: Request) -> TenantContext:
    """FastAPI dependency: extract TenantContext from request state.

    Usage:
        @router.get("/data")
        async def handler(ctx: TenantContext = Depends(get_tenant_context)):
            ...

    Raises:
        HTTPException 401: If no TenantContext is present (should not
            happen if TenantAuthMiddleware is installed).
    """
    ctx = getattr(request.state, "tenant_context", None)
    if ctx is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. TenantContext not found in request.",
        )
    return ctx


def require_tier(minimum_tier: TenantTier) -> Callable:
    """FastAPI dependency factory: enforce minimum subscription tier.

    Usage:
        @router.post("/advanced")
        async def handler(
            ctx: TenantContext = Depends(require_tier(TenantTier.PROFESSIONAL)),
        ):
            ...

    Tier ordering: STARTER < PROFESSIONAL < ENTERPRISE
    """
    _tier_order = {
        TenantTier.STARTER: 0,
        TenantTier.PROFESSIONAL: 1,
        TenantTier.ENTERPRISE: 2,
    }

    async def dependency(request: Request) -> TenantContext:
        ctx = await get_tenant_context(request)

        if ctx.tier is None:
            raise HTTPException(
                status_code=403,
                detail="Subscription tier not set. Cannot verify access.",
            )

        ctx_level = _tier_order.get(ctx.tier, -1)
        required_level = _tier_order.get(minimum_tier, 0)

        if ctx_level < required_level:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"This feature requires {minimum_tier.value} tier or higher. "
                    f"Current tier: {ctx.tier.value}."
                ),
            )

        return ctx

    return dependency


# ---------------------------------------------------------------------------
# Per-tenant rate limiting (Decision #5)
# ---------------------------------------------------------------------------


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-tenant rate limiting based on subscription tier.

    Rate limits (requests per minute):
        Starter:      10 rpm
        Professional: 50 rpm
        Enterprise:  200 rpm

    Uses a sliding window counter per tenant. When the limit is
    exceeded, returns HTTP 429 with Retry-After header.

    This is an in-memory implementation suitable for single-instance
    deployments. For multi-instance, replace with a shared store
    (Redis or Cosmos DB atomic counters).
    """

    def __init__(self, app: Any, **kwargs: Any) -> None:
        super().__init__(app, **kwargs)
        # {tenant_id: [(timestamp, count), ...]}
        self._windows: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._window_size = 60.0  # 1 minute sliding window

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        # Only rate-limit authenticated requests
        ctx: TenantContext | None = getattr(request.state, "tenant_context", None)
        if ctx is None:
            return await call_next(request)

        # Determine rate limit for this tenant's tier
        limit = self._get_limit(ctx)
        if limit is None:
            return await call_next(request)

        # Check and update rate counter
        now = time.monotonic()
        tenant_id = ctx.tenant_id

        # Clean expired entries
        window = self._windows[tenant_id]
        cutoff = now - self._window_size
        self._windows[tenant_id] = [
            (ts, count) for ts, count in window if ts > cutoff
        ]

        # Count requests in window
        current_count = sum(count for _, count in self._windows[tenant_id])

        if current_count >= limit:
            retry_after = int(self._window_size)
            logger.warning(
                "Rate limit exceeded: tenant=%s tier=%s limit=%d/min current=%d",
                tenant_id, ctx.tier, limit, current_count,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded.",
                    "limit": limit,
                    "window": "60s",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        # Record this request
        self._windows[tenant_id].append((now, 1))

        return await call_next(request)

    def _get_limit(self, ctx: TenantContext) -> int | None:
        """Get the rate limit for a tenant based on tier.

        Returns None if no rate limit applies (e.g., unknown tier).
        """
        if ctx.tier is None:
            return None

        defaults = TIER_DEFAULTS.get(ctx.tier.value, {})
        return defaults.get("rate_limit_rpm")
