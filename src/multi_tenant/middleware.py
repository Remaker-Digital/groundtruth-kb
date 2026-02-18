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
    WIDGET_KEY_HEADER,
    AuthenticationError,
    TenantContext,
    TenantInactiveError,
    extract_bearer_token,
    extract_shop_domain,
    is_auth_exempt,
    is_user_api_key,
    is_widget_key_allowed_path,
    validate_tenant_status,
    verify_api_key,
    verify_shopify_session_token,
    verify_user_api_key,
    verify_widget_key,
)
from src.multi_tenant.magic_link_auth import verify_magic_link_session_token
from src.multi_tenant.cosmos_schema import (
    TIER_DEFAULTS,
    TeamMemberRole,
    TenantStatus,
    TenantTier,
)

from datetime import datetime, timezone

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
_resolve_by_widget_key_hash: Callable | None = None
_resolve_by_user_api_key_hash: Callable | None = None


def configure_tenant_resolution(
    resolve_by_shop_domain: Callable,
    resolve_by_api_key_hash: Callable,
    resolve_by_widget_key_hash: Callable | None = None,
    resolve_by_user_api_key_hash: Callable | None = None,
) -> None:
    """Configure the tenant resolution functions.

    Called once during application startup after repositories are
    initialized.

    Args:
        resolve_by_shop_domain: Async function that accepts a shop
            domain string and returns a tenant dict or None.
        resolve_by_api_key_hash: Async function that accepts an API
            key hash string and returns a tenant dict or None.
        resolve_by_widget_key_hash: Async function that accepts a widget
            key hash string and returns a tenant dict or None.
            Optional — widget key auth is disabled if not provided.
        resolve_by_user_api_key_hash: Async function that accepts a user
            API key hash and returns {team_member, tenant} or None.
            Optional — per-user auth is disabled if not provided.
    """
    global _resolve_by_shop_domain, _resolve_by_api_key_hash
    global _resolve_by_widget_key_hash, _resolve_by_user_api_key_hash
    _resolve_by_shop_domain = resolve_by_shop_domain
    _resolve_by_api_key_hash = resolve_by_api_key_hash
    _resolve_by_widget_key_hash = resolve_by_widget_key_hash
    _resolve_by_user_api_key_hash = resolve_by_user_api_key_hash
    logger.info("Tenant resolution functions configured")


# ---------------------------------------------------------------------------
# TenantAuthMiddleware
# ---------------------------------------------------------------------------


class TenantAuthMiddleware(BaseHTTPMiddleware):
    """Authenticate every request and inject TenantContext.

    Processing order:
        1. Check if path is auth-exempt (webhooks, health, docs).
        2. Extract credentials (Bearer token, X-API-Key, or X-Widget-Key).
        3. Verify credentials (JWT decode, API key hash, or widget key hash).
        4. Resolve tenant_id from verified identity.
        5. Validate tenant status (ACTIVE or PAST_DUE).
        6. Store TenantContext in request.state.tenant_context.
        7. Forward to route handler.

    Widget key auth (Decision UI-6) is scoped to /api/chat/* and
    /ws/chat/* paths only. Requests to other paths with a widget key
    are rejected.

    On authentication failure, returns a JSON error response without
    forwarding to the handler. This prevents any unauthenticated
    code from executing.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        # Let CORS preflight (OPTIONS) through — CORSMiddleware handles these.
        if request.method == "OPTIONS":
            return await call_next(request)

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
        except Exception as exc:
            logger.exception(
                "Unexpected error during authentication: path=%s method=%s",
                request.url.path, request.method,
            )
            return JSONResponse(
                status_code=500,
                content={"error": "Internal authentication error."},
            )

        return await call_next(request)

    async def _authenticate(self, request: Request) -> TenantContext:
        """Authenticate the request and return a TenantContext.

        Tries Shopify session token first (Bearer), then API key,
        then publishable widget key.
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

        # Try publishable widget key (X-Widget-Key header or query param)
        widget_key = request.headers.get(WIDGET_KEY_HEADER)
        if not widget_key:
            # EventSource (SSE) and WebSocket connections pass the key as a
            # query parameter since browsers cannot set custom headers on
            # these connection types.
            # SSE uses ?widget_key=, WebSocket uses ?key= (both accepted).
            widget_key = (
                request.query_params.get("widget_key")
                or request.query_params.get("key")
            )

        if widget_key:
            return await self._auth_widget_key(widget_key, request.url.path)

        # Try magic link session token (X-Session-Token header)
        session_token = request.headers.get("X-Session-Token")
        if session_token:
            return await self._auth_magic_link_session(session_token)

        # No credentials provided
        raise AuthenticationError(
            "Authentication required. Provide a Shopify session token "
            "(Authorization: Bearer <token>), an API key (X-API-Key header), "
            "or a widget key (X-Widget-Key header)."
        )

    @staticmethod
    def _resolve_tenant_fields(
        tenant: dict[str, Any],
    ) -> tuple[str, TenantStatus, TenantTier | None, str | None]:
        """Extract common fields from a resolved tenant document.

        Returns (tenant_id, status, tier, trial_expires_at).
        """
        tenant_id = tenant["tenant_id"]
        status = TenantStatus(tenant.get("status", "active"))
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None
        trial_expires_at = tenant.get("trial_expires_at")
        return tenant_id, status, tier, trial_expires_at

    @staticmethod
    def _check_trial_expiry(
        tenant_id: str,
        tier: TenantTier | None,
        trial_expires_at: str | None,
    ) -> None:
        """Reject the request if the trial has expired.

        Raises AuthenticationError (403) if the tenant is on the trial
        tier and the current time is past trial_expires_at.
        """
        if tier != TenantTier.TRIAL or not trial_expires_at:
            return

        try:
            expires = datetime.fromisoformat(trial_expires_at)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires:
                raise AuthenticationError(
                    f"Trial period has expired for tenant {tenant_id}. "
                    "Please subscribe to a paid plan to continue.",
                    status_code=403,
                )
        except AuthenticationError:
            raise
        except Exception:
            # Malformed timestamp — log but don't block
            logger.warning(
                "Could not parse trial_expires_at for tenant=%s: %s",
                tenant_id, trial_expires_at,
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

        tenant_id, status, tier, trial_expires_at = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="shopify_session",
            trial_expires_at=trial_expires_at,
            shop_domain=shop_domain,
            user_id=payload.get("sub"),
            session_id=payload.get("sid"),
        )

    async def _auth_api_key(self, api_key: str) -> TenantContext:
        """Authenticate via API key (tenant key or per-user key).

        Detects the key type by prefix:
        - ar_user_* → per-user API key → resolves to team member + tenant
        - ar_live_* or other → tenant API key → resolves to tenant only
        """
        # Route per-user keys through the user auth flow
        if is_user_api_key(api_key) and _resolve_by_user_api_key_hash is not None:
            logger.debug("Auth routing: per-user API key detected (prefix=%s...)", api_key[:12])
            return await self._auth_user_api_key(api_key)

        # Tenant-level API key (legacy flow)
        logger.debug("Auth routing: tenant API key detected (prefix=%s...)", api_key[:8])
        if _resolve_by_api_key_hash is None:
            raise AuthenticationError(
                "Tenant resolution not configured.", status_code=500,
            )

        tenant = await verify_api_key(api_key, _resolve_by_api_key_hash)

        tenant_id, status, tier, trial_expires_at = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="api_key",
            trial_expires_at=trial_expires_at,
        )

    async def _auth_user_api_key(self, api_key: str) -> TenantContext:
        """Authenticate via per-user API key.

        Resolves the key to a specific team member and their tenant.
        Populates user identity fields on TenantContext.
        """
        if _resolve_by_user_api_key_hash is None:
            raise AuthenticationError(
                "Per-user authentication not configured.", status_code=500,
            )

        result = await verify_user_api_key(api_key, _resolve_by_user_api_key_hash)

        tenant = result["tenant"]
        member = result["team_member"]

        tenant_id, status, tier, trial_expires_at = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)

        # Resolve role
        role_str = member.get("role", "viewer")
        try:
            role = TeamMemberRole(role_str)
        except ValueError:
            role = TeamMemberRole.VIEWER

        logger.debug(
            "Per-user auth resolved: tenant=%s email=%s role=%s member_id=%s",
            tenant_id, member.get("email"), role.value, member.get("id"),
        )

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="user_api_key",
            trial_expires_at=trial_expires_at,
            team_member_id=member.get("id"),
            team_member_email=member.get("email"),
            team_member_role=role,
            escalation_categories=tuple(member.get("escalation_categories", [])),
        )

    async def _auth_widget_key(
        self, widget_key: str, path: str,
    ) -> TenantContext:
        """Authenticate via publishable widget key (Decision UI-6).

        Widget keys are scoped to /api/chat/* and /ws/chat/* only.
        Requests to other paths are rejected even if the key is valid.
        """
        # Enforce path scope — widget keys cannot access billing, config, etc.
        if not is_widget_key_allowed_path(path):
            raise AuthenticationError(
                "Widget key authentication is only valid for /api/chat/ endpoints."
            )

        if _resolve_by_widget_key_hash is None:
            raise AuthenticationError(
                "Widget key resolution not configured.", status_code=500,
            )

        tenant = await verify_widget_key(widget_key, _resolve_by_widget_key_hash)

        tenant_id, status, tier, trial_expires_at = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="widget_key",
            is_widget_auth=True,
            trial_expires_at=trial_expires_at,
        )

    async def _auth_magic_link_session(self, token: str) -> TenantContext:
        """Authenticate via magic link session JWT.

        The JWT contains tenant_id (sub) and email. We resolve the
        tenant from the JWT claims and build a TenantContext.
        """
        payload = verify_magic_link_session_token(token)
        if payload is None:
            raise AuthenticationError(
                "Invalid or expired session token. Please sign in again.",
            )

        tenant_id = payload.get("sub")
        if not tenant_id:
            raise AuthenticationError("Session token missing tenant ID.")

        # Resolve tenant to get status/tier
        if _resolve_by_shop_domain is None and _resolve_by_api_key_hash is None:
            raise AuthenticationError(
                "Tenant resolution not configured.", status_code=500,
            )

        # Look up tenant by ID — reuse the existing tenant resolution
        from src.multi_tenant.repositories import TenantRepository

        tenant_repo = TenantRepository()
        tenant = await tenant_repo.read(tenant_id)
        if tenant is None:
            raise AuthenticationError(
                f"No tenant found for session token: {tenant_id}",
            )

        _, status, tier, trial_expires_at = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="magic_link_session",
            trial_expires_at=trial_expires_at,
            team_member_email=payload.get("email"),
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


def require_role(*allowed_roles: TeamMemberRole) -> Callable:
    """FastAPI dependency factory: enforce role-based access control.

    Usage:
        @router.get("/admin-only")
        async def handler(
            ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)),
        ):
            ...

    Allows requests from users with any of the listed roles.

    Tenant-level API keys (ar_live_) are treated as ADMIN role for
    backward compatibility (widget, webhooks, and legacy admin access).
    """
    allowed = set(allowed_roles)

    async def dependency(request: Request) -> TenantContext:
        ctx = await get_tenant_context(request)

        # Tenant-level keys (ar_live_) have no per-user role — treat as admin
        caller_role = getattr(ctx, "team_member_role", None)
        if caller_role is None:
            # Legacy tenant API key or Shopify JWT — allow if ADMIN is in allowed set
            if TeamMemberRole.ADMIN in allowed:
                return ctx
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions. Per-user API key required.",
            )

        if caller_role not in allowed:
            logger.debug(
                "Role access denied: tenant=%s email=%s role=%s required=%s path=%s",
                ctx.tenant_id,
                getattr(ctx, "team_member_email", "?"),
                caller_role.value,
                ", ".join(r.value for r in allowed),
                getattr(request, "url", "?"),
            )
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {', '.join(r.value for r in allowed)}.",
            )

        return ctx

    return dependency


def require_write_role() -> Callable:
    """FastAPI dependency: require a role that can write (superadmin or admin).

    Convenience wrapper for the most common write-access check.
    Viewers and escalation agents are read-only.
    """
    return require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)


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
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )

        # Record this request
        self._windows[tenant_id].append((now, 1))
        remaining = max(0, limit - current_count - 1)

        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(self._window_size))

        return response

    def _get_limit(self, ctx: TenantContext) -> int | None:
        """Get the rate limit for a tenant based on tier.

        Returns None if no rate limit applies (e.g., unknown tier).
        """
        if ctx.tier is None:
            return None

        defaults = TIER_DEFAULTS.get(ctx.tier.value, {})
        return defaults.get("rate_limit_rpm")
