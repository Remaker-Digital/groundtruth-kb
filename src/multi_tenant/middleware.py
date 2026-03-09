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

import asyncio
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
    is_spa_api_key,
    is_user_api_key,
    is_widget_key_allowed_path,
    validate_tenant_status,
    verify_api_key,
    verify_shopify_session_token,
    verify_spa_api_key,
    verify_user_api_key,
    verify_widget_key,
)
from src.multi_tenant.magic_link_auth import verify_magic_link_session_token
from src.multi_tenant.cosmos_schema import (
    PLATFORM_ADMIN_TENANT_ID,
    TIER_DEFAULTS,
    TeamMemberRole,
    TenantStatus,
    TenantTier,
)

from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# S155/SPEC-1676: Task set to prevent GC of fire-and-forget notification tasks
_spa_notification_tasks: set[asyncio.Task] = set()


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
_resolve_by_tenant_id: Callable | None = None
_resolve_by_spa_key_hash: Callable | None = None


def configure_tenant_resolution(
    resolve_by_shop_domain: Callable,
    resolve_by_api_key_hash: Callable,
    resolve_by_widget_key_hash: Callable | None = None,
    resolve_by_user_api_key_hash: Callable | None = None,
    resolve_by_tenant_id: Callable | None = None,
    resolve_by_spa_key_hash: Callable | None = None,
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
        resolve_by_tenant_id: Async function that accepts a tenant ID
            string and returns a tenant dict or None. Used by magic-link
            auth to reuse the connection-pooled repository.
        resolve_by_spa_key_hash: Async function that accepts an SPA API
            key hash and returns a platform admin document or None.
            Optional — SPA auth is disabled if not provided. (SPEC-1667)
    """
    global _resolve_by_shop_domain, _resolve_by_api_key_hash
    global _resolve_by_widget_key_hash, _resolve_by_user_api_key_hash
    global _resolve_by_tenant_id, _resolve_by_spa_key_hash
    _resolve_by_shop_domain = resolve_by_shop_domain
    _resolve_by_api_key_hash = resolve_by_api_key_hash
    _resolve_by_widget_key_hash = resolve_by_widget_key_hash
    _resolve_by_user_api_key_hash = resolve_by_user_api_key_hash
    _resolve_by_tenant_id = resolve_by_tenant_id
    _resolve_by_spa_key_hash = resolve_by_spa_key_hash
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

        # Extract client IP for pre-auth rate limiting (SPEC-1621)
        client = request.scope.get("client")
        client_ip = client[0] if client else "unknown"

        try:
            tenant_context = await self._authenticate(request)
            request.state.tenant_context = tenant_context
        except AuthenticationError as exc:
            # Record failure for brute-force protection (SPEC-1621)
            from src.multi_tenant.security_hardening import get_pre_auth_limiter
            get_pre_auth_limiter().record_failure(client_ip)
            logger.warning(
                "Auth failed: path=%s method=%s error=%s",
                request.url.path, request.method, exc.message,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.message},
            )
        except Exception as exc:
            # Record failure for brute-force protection (SPEC-1621)
            from src.multi_tenant.security_hardening import get_pre_auth_limiter
            get_pre_auth_limiter().record_failure(client_ip)
            logger.exception(
                "Unexpected error during authentication: path=%s method=%s",
                request.url.path, request.method,
            )
            return JSONResponse(
                status_code=500,
                content={"error": "Internal authentication error."},
            )

        # Record success to reset failure counter (SPEC-1621)
        from src.multi_tenant.security_hardening import get_pre_auth_limiter
        get_pre_auth_limiter().record_success(client_ip)

        # WI-1045 / SPEC-1657: Validate ?tenant= URL param against resolved tenant.
        # If the URL claims a specific tenant but the API key resolves to a
        # different one, reject the request rather than silently using the
        # key's tenant. This prevents confusion attacks where a crafted URL
        # shows tenant A's admin while the backend scopes queries to tenant B.
        url_tenant = request.query_params.get("tenant")
        if (
            url_tenant
            and not getattr(tenant_context, "is_platform_admin", False)
            and not getattr(tenant_context, "is_widget_auth", False)
            and tenant_context.tenant_id != url_tenant
        ):
            logger.warning(
                "Tenant mismatch: URL tenant=%s, auth tenant=%s, path=%s",
                url_tenant,
                tenant_context.tenant_id[:12],
                request.url.path,
            )
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Tenant parameter does not match authenticated tenant.",
                },
            )

        # SPEC-1676: Fire non-blocking login notification for SPA auth
        if getattr(tenant_context, "is_platform_admin", False):
            try:
                from src.multi_tenant.login_notification import send_login_notification
                user_agent = request.headers.get("user-agent", "")
                task = asyncio.create_task(
                    send_login_notification(
                        admin_email=tenant_context.platform_admin_email or "",
                        notification_email=tenant_context.platform_admin_notification_email,
                        client_ip=client_ip,
                        user_agent=user_agent,
                    )
                )
                # S155 async safety: prevent GC of fire-and-forget tasks
                _spa_notification_tasks.add(task)
                task.add_done_callback(_spa_notification_tasks.discard)
            except Exception as exc:
                logger.warning("Login notification setup failed: %s", exc)

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

        # Try API key (X-API-Key header or query param for SSE/WS)
        # SPEC-1562: EventSource and WebSocket connections cannot set custom
        # headers, so admin widgets pass api_key as a query parameter for
        # Co-pilot mode authentication.
        api_key = request.headers.get(API_KEY_HEADER)
        if not api_key:
            api_key = request.query_params.get("api_key")
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
    ) -> tuple[str, TenantStatus, TenantTier | None, str | None, str | None, int | None]:
        """Extract common fields from a resolved tenant document.

        Returns (tenant_id, status, tier, trial_expires_at, expires_at, rate_limit_rpm).
        """
        tenant_id = tenant["tenant_id"]
        status = TenantStatus(tenant.get("status", "active"))
        tier_str = tenant.get("tier")
        tier = TenantTier(tier_str) if tier_str else None
        trial_expires_at = tenant.get("trial_expires_at")
        expires_at = tenant.get("expires_at")
        rate_limit_rpm = tenant.get("rate_limit_rpm")
        return tenant_id, status, tier, trial_expires_at, expires_at, rate_limit_rpm

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

    @staticmethod
    def _check_access_expiry(
        tenant_id: str,
        expires_at: str | None,
    ) -> None:
        """Reject the request if general access has expired (WI-EXPIRY-1).

        Works for any billing channel and any tier. Reads the ``expires_at``
        field (distinct from ``trial_expires_at``).

        Raises AuthenticationError (403) if the current time is past
        ``expires_at``.
        """
        if not expires_at:
            return

        try:
            expires = datetime.fromisoformat(expires_at)
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expires:
                raise AuthenticationError(
                    f"Access has expired for tenant {tenant_id}. "
                    "Please contact your service provider.",
                    status_code=403,
                )
        except AuthenticationError:
            raise
        except Exception:
            # Malformed timestamp — log but don't block
            logger.warning(
                "Could not parse expires_at for tenant=%s: %s",
                tenant_id, expires_at,
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

        tenant_id, status, tier, trial_expires_at, expires_at, rl_rpm = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)
        self._check_access_expiry(tenant_id, expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="shopify_session",
            trial_expires_at=trial_expires_at,
            rate_limit_rpm=rl_rpm,
            shop_domain=shop_domain,
            user_id=payload.get("sub"),
            session_id=payload.get("sid"),
        )

    async def _auth_api_key(self, api_key: str) -> TenantContext:
        """Authenticate via API key (SPA, per-user, or tenant key).

        Detects the key type by prefix:
        - ar_spa_* → SPA platform admin key → resolves from platform_admins
        - ar_user_* → per-user API key → resolves to team member + tenant
        - ar_live_* or other → tenant API key → resolves to tenant only
        """
        # Route SPA platform admin keys through isolated auth (SPEC-1667)
        if is_spa_api_key(api_key) and _resolve_by_spa_key_hash is not None:
            logger.debug("Auth routing: SPA platform admin key detected")
            return await self._auth_spa_api_key(api_key)

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

        tenant_id, status, tier, trial_expires_at, expires_at, rl_rpm = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)
        self._check_access_expiry(tenant_id, expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="api_key",
            trial_expires_at=trial_expires_at,
            rate_limit_rpm=rl_rpm,
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

        tenant_id, status, tier, trial_expires_at, expires_at, rl_rpm = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)
        self._check_access_expiry(tenant_id, expires_at)

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
            rate_limit_rpm=rl_rpm,
            team_member_id=member.get("id"),
            team_member_email=member.get("email"),
            team_member_role=role,
            escalation_categories=tuple(member.get("escalation_categories", [])),
        )

    async def _auth_spa_api_key(self, api_key: str) -> TenantContext:
        """Authenticate via SPA platform admin API key (SPEC-1667).

        Resolves credentials from the platform_admins collection —
        completely isolated from all tenant team_members collections.
        The SPA has zero permissions within any tenancy and does not
        exist as a user for any tenancy.

        Skips tenant status validation, trial/expiry checks, and
        rate-limit-rpm resolution because these are tenant-specific
        concerns that do not apply to the platform admin.
        """
        if _resolve_by_spa_key_hash is None:
            raise AuthenticationError(
                "Platform admin authentication not configured.", status_code=500,
            )

        admin = await verify_spa_api_key(api_key, _resolve_by_spa_key_hash)

        logger.info(
            "SPA platform admin authenticated: email=%s admin_id=%s",
            admin.get("email", "unknown"),
            admin.get("admin_id", admin.get("id", "unknown")),
        )

        return TenantContext(
            tenant_id=PLATFORM_ADMIN_TENANT_ID,
            is_platform_admin=True,
            auth_method="spa_api_key",
            status=TenantStatus.ACTIVE,
            # No tier, no trial, no rate_limit_rpm, no team member fields.
            # Platform admins operate outside all tenancies.
            platform_admin_id=admin.get("admin_id", admin.get("id")),
            platform_admin_email=admin.get("email"),
            platform_admin_role=admin.get("role", "superadmin"),  # SPEC-1675
            platform_admin_notification_email=admin.get("notification_email_address"),  # SPEC-1676
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

        tenant_id, status, tier, trial_expires_at, expires_at, rl_rpm = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)
        self._check_access_expiry(tenant_id, expires_at)

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="widget_key",
            is_widget_auth=True,
            trial_expires_at=trial_expires_at,
            rate_limit_rpm=rl_rpm,
        )

    async def _auth_magic_link_session(self, token: str) -> TenantContext:
        """Authenticate via magic link session JWT.

        The JWT contains tenant_id (sub), email, and optionally
        member_id + role (for team member sessions). We resolve the
        tenant from the JWT claims, then populate the full team member
        identity on the TenantContext.
        """
        payload = verify_magic_link_session_token(token)
        if payload is None:
            raise AuthenticationError(
                "Invalid or expired session token. Please sign in again.",
            )

        tenant_id = payload.get("sub")
        if not tenant_id:
            raise AuthenticationError("Session token missing tenant ID.")

        # Resolve tenant to get status/tier using pooled resolver
        if _resolve_by_tenant_id is None:
            raise AuthenticationError(
                "Tenant resolution not configured.", status_code=500,
            )

        tenant = await _resolve_by_tenant_id(tenant_id)
        if tenant is None:
            raise AuthenticationError(
                f"No tenant found for session token: {tenant_id}",
            )

        _, status, tier, trial_expires_at, expires_at, rl_rpm = self._resolve_tenant_fields(tenant)
        validate_tenant_status(tenant_id, status)
        self._check_trial_expiry(tenant_id, tier, trial_expires_at)
        self._check_access_expiry(tenant_id, expires_at)

        # Extract team member identity from JWT claims
        member_id = payload.get("member_id")
        role_str = payload.get("role")
        role: TeamMemberRole | None = None
        escalation_cats: tuple[str, ...] = ()

        if member_id and role_str:
            try:
                role = TeamMemberRole(role_str)
            except ValueError:
                role = TeamMemberRole.VIEWER

            # For escalation agents, resolve their category assignments
            if role in (
                TeamMemberRole.ESCALATION_AGENT,
                TeamMemberRole.VIEWER,
            ):
                try:
                    from src.multi_tenant.repositories import (
                        TeamMemberRepository,
                    )
                    team_repo = TeamMemberRepository()
                    member_doc = await team_repo.read(tenant_id, member_id)
                    escalation_cats = tuple(
                        member_doc.get("escalation_categories", []),
                    )
                except Exception:
                    logger.warning(
                        "Failed to resolve escalation categories: "
                        "tenant=%s member=%s",
                        tenant_id, member_id,
                    )

        logger.debug(
            "Magic link session resolved: tenant=%s email=%s "
            "member=%s role=%s",
            tenant_id, payload.get("email"), member_id, role_str,
        )

        return TenantContext(
            tenant_id=tenant_id,
            tier=tier,
            status=status,
            auth_method="magic_link_session",
            trial_expires_at=trial_expires_at,
            rate_limit_rpm=rl_rpm,
            team_member_email=payload.get("email"),
            team_member_id=member_id,
            team_member_role=role,
            escalation_categories=escalation_cats,
        )


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------


async def get_tenant_context(request: Request) -> TenantContext:
    """FastAPI dependency: extract TenantContext from request state.

    Also enforces RBAC: non-admin roles are blocked from admin-only
    paths (config, analytics, billing, etc.). Inbox paths remain open.

    Usage:
        @router.get("/data")
        async def handler(ctx: TenantContext = Depends(get_tenant_context)):
            ...

    Raises:
        HTTPException 401: If no TenantContext is present (should not
            happen if TenantAuthMiddleware is installed).
        HTTPException 403: If the caller's role lacks permission for
            the requested path (WI #295 Phase 3).
    """
    ctx = getattr(request.state, "tenant_context", None)
    if ctx is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. TenantContext not found in request.",
        )

    # SPEC-1667: Platform admin keys MUST NOT access tenant-scoped endpoints.
    # The SPA has zero permissions within any tenancy. Only /api/superadmin/*
    # paths are accessible to platform admins.
    if getattr(ctx, "is_platform_admin", False):
        if not request.url.path.startswith("/api/superadmin"):
            raise HTTPException(
                status_code=403,
                detail="Platform admin credentials cannot access tenant endpoints. "
                       "Use tenant-specific credentials for tenant operations.",
            )

    enforce_rbac(request.url.path, ctx)
    return ctx


def require_tier(minimum_tier: TenantTier) -> Callable:
    """FastAPI dependency factory: enforce minimum subscription tier.

    Usage:
        @router.post("/advanced")
        async def handler(
            ctx: TenantContext = Depends(require_tier(TenantTier.PROFESSIONAL)),
        ):
            ...

    Tier ordering: TRIAL = STARTER < PROFESSIONAL < ENTERPRISE
    """
    _tier_order = {
        TenantTier.TRIAL: 0,
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


def require_admin_or_above() -> Callable:
    """FastAPI dependency: require admin or superadmin role.

    Used for protecting read endpoints that should not be accessible
    to escalation_agent or viewer roles (config, analytics, billing,
    team management, etc.). Inbox endpoints remain open to all roles.

    This is functionally identical to require_write_role() but
    named for clarity when protecting read-only endpoints.
    """
    return require_role(TeamMemberRole.SUPERADMIN, TeamMemberRole.ADMIN)


def require_platform_admin() -> Callable:
    """FastAPI dependency: require SPA platform admin credentials (SPEC-1667).

    Only requests authenticated with an ar_spa_* key (resolving from
    the platform_admins collection) can pass this guard. Tenant team
    member keys (ar_user_*), tenant API keys (ar_live_*), and widget
    keys (pk_live_*) are all rejected with 403.

    Usage:
        router = APIRouter(
            prefix="/api/superadmin",
            dependencies=[Depends(require_platform_admin())],
        )
    """
    async def dependency(request: Request) -> TenantContext:
        ctx = getattr(request.state, "tenant_context", None)
        if ctx is None:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated. TenantContext not found in request.",
            )

        if not getattr(ctx, "is_platform_admin", False):
            raise HTTPException(
                status_code=403,
                detail="This endpoint requires platform administrator credentials. "
                       "Tenant API keys cannot access the service provider console.",
            )

        return ctx

    return dependency


def require_spa_superadmin() -> Callable:
    """FastAPI dependency: require SPA *superadmin* credentials (SPEC-1675).

    Stricter than require_platform_admin() — rejects operator-role admins.
    Use for destructive actions like creating/deleting other SPA users.

    Usage:
        @router.post("/users", dependencies=[Depends(require_spa_superadmin())])
    """
    async def dependency(request: Request) -> TenantContext:
        ctx = getattr(request.state, "tenant_context", None)
        if ctx is None:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated. TenantContext not found in request.",
            )

        if not getattr(ctx, "is_platform_admin", False):
            raise HTTPException(
                status_code=403,
                detail="This endpoint requires platform administrator credentials.",
            )

        if getattr(ctx, "platform_admin_role", None) != "superadmin":
            raise HTTPException(
                status_code=403,
                detail="This action requires SPA superadmin privileges. "
                       "Operator accounts cannot perform this action.",
            )

        return ctx

    return dependency


# ---------------------------------------------------------------------------
# RBAC path enforcement (WI #295 Phase 3)
# ---------------------------------------------------------------------------

# Path prefixes restricted to admin/superadmin roles.
# Non-admin roles (escalation_agent, viewer) get 403 on these paths.
_ADMIN_ONLY_PREFIXES = (
    "/api/config",
    "/api/analytics",
    "/api/audit",
    "/api/gdpr",
    "/api/admin/api-keys",
    "/api/admin/knowledge",
    "/api/admin/integrations",
    "/api/admin/quick-actions",
    "/api/admin/profiles",
    "/api/admin/avatar",
    "/api/admin/contact",
    "/api/admin/ingestion",
    "/api/cost",
    "/api/admin/memory",
    "/api/admin/tier-upgrade",
    "/api/admin/config-lock",
    "/api/admin/team",
)

# Paths within admin-only prefixes that remain open to all roles.
_RBAC_OPEN_PATHS = (
    "/api/admin/team/whoami",
)

# Paths open to all authenticated roles (inbox).
_ALL_ROLES_PREFIXES = (
    "/api/admin/conversations",
    "/api/admin/team/whoami",
    "/api/chat",
)

_ADMIN_ROLE_VALUES = {
    TeamMemberRole.SUPERADMIN,
    TeamMemberRole.ADMIN,
}


def is_admin_only_path(path: str) -> bool:
    """Check if a path requires admin role access.

    Returns True if the path is under an admin-only prefix and
    is NOT explicitly listed as open to all roles.
    """
    if any(path.startswith(p) for p in _RBAC_OPEN_PATHS):
        return False
    if any(path.startswith(p) for p in _ALL_ROLES_PREFIXES):
        return False
    return any(path.startswith(p) for p in _ADMIN_ONLY_PREFIXES)


def enforce_rbac(path: str, ctx: "TenantContext") -> None:
    """Enforce RBAC on the given path for the given context.

    Raises HTTPException(403) if the caller lacks permission.
    No-op for admin/superadmin roles, tenant-level API keys (no role),
    or non-restricted paths.
    """
    if not is_admin_only_path(path):
        return

    caller_role = getattr(ctx, "team_member_role", None)

    # Tenant-level API key (ar_live_) or Shopify JWT → treated as admin
    if caller_role is None:
        return

    if caller_role in _ADMIN_ROLE_VALUES:
        return

    from fastapi import HTTPException
    raise HTTPException(
        status_code=403,
        detail="Insufficient permissions. Admin access required.",
    )


# ---------------------------------------------------------------------------
# Per-tenant rate limiting (Decision #5)
# ---------------------------------------------------------------------------


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-tenant rate limiting based on subscription tier.

    Rate limits (requests per minute):
        All tiers:   500 rpm (uniform)

    Per-tenant overrides via TenantDocument.rate_limit_rpm take
    precedence over tier defaults.

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
        self._lock = asyncio.Lock()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint,
    ) -> Response:
        # Only rate-limit authenticated requests
        ctx: TenantContext | None = getattr(request.state, "tenant_context", None)
        if ctx is None:
            return await call_next(request)

        # Platform admins operate outside all tenancies — no per-tenant
        # rate limiting applies (SPEC-1667 design: SPA skips tenant checks).
        if getattr(ctx, "is_platform_admin", False):
            return await call_next(request)

        # Determine rate limit for this tenant's tier
        limit = self._get_limit(ctx)
        if limit is None:
            return await call_next(request)

        # Atomic check-and-increment under lock to prevent
        # concurrent requests from both passing the limit check.
        now = time.monotonic()
        tenant_id = ctx.tenant_id

        async with self._lock:
            # Clean expired entries
            cutoff = now - self._window_size
            self._windows[tenant_id] = [
                (ts, count) for ts, count in self._windows[tenant_id]
                if ts > cutoff
            ]

            # Count requests in window
            current_count = sum(
                count for _, count in self._windows[tenant_id]
            )

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

            # Record this request atomically with the check
            self._windows[tenant_id].append((now, 1))
            remaining = max(0, limit - current_count - 1)

        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(self._window_size))

        return response

    def _get_limit(self, ctx: TenantContext) -> int | None:
        """Get the rate limit for a tenant.

        Resolution order:
        1. Per-tenant override (TenantContext.rate_limit_rpm) if set
        2. Tier defaults from TIER_DEFAULTS
        3. None (no rate limit) if tier is unknown

        Returns None if no rate limit applies.
        """
        # Per-tenant override takes precedence
        per_tenant = getattr(ctx, "rate_limit_rpm", None)
        if per_tenant is not None:
            return per_tenant

        if ctx.tier is None:
            return None

        defaults = TIER_DEFAULTS.get(ctx.tier.value, {})
        return defaults.get("rate_limit_rpm")
