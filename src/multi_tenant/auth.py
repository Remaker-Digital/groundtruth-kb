"""
Triple authentication: Shopify session tokens + API keys + publishable widget keys.

Verifies incoming requests and resolves them to a tenant_id. All three
authentication channels produce the same TenantContext object that
downstream handlers use to scope all database operations.

Authentication methods (Decisions #4, UI-6):
    1. Shopify session tokens — JWT signed with app secret (HS256).
       Sent as Authorization: Bearer <token> by App Bridge.
       Resolves tenant via shop domain → tenants collection lookup.

    2. API keys — hashed, stored in Key Vault.
       Sent as X-API-Key: <key> header.
       Resolves tenant via API key hash → tenants collection lookup.

    3. Publishable widget keys — public credentials for client-side widgets.
       Sent as X-Widget-Key: pk_live_... header (or ?key= query param for WS).
       Scoped to /api/chat/* endpoints only. Sets is_widget_auth=True on context.
       Format: pk_live_{tenant_id_hash}_{random}

    4. Webhook signatures — Stripe/Shopify webhook-specific auth.
       These endpoints bypass tenant resolution (handled per-webhook).

Request flow:
    HTTP request
    → Extract auth credentials (Bearer token, API key, or widget key)
    → Verify credentials (JWT decode, hash lookup, or widget key lookup)
    → Resolve tenant_id from verified identity
    → Validate tenant status (must be ACTIVE or PAST_DUE)
    → Inject TenantContext into request state
    → Handler receives TenantContext via FastAPI dependency

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import secrets
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    ImmatureSignatureError,
    InvalidAudienceError,
    MissingRequiredClaimError,
    PyJWTError,
)

from src.multi_tenant.cosmos_schema import TeamMemberRole, TenantStatus, TenantTier

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Shopify app credentials (set in environment)
SHOPIFY_API_KEY = os.environ.get("SHOPIFY_API_KEY", "")
SHOPIFY_API_SECRET = os.environ.get("SHOPIFY_API_SECRET", "")

# JWT verification settings (per Shopify's official library)
JWT_ALGORITHM = "HS256"
JWT_LEEWAY_SECONDS = 10
JWT_REQUIRED_CLAIMS = ["iss", "dest", "sub", "jti", "sid", "exp", "nbf", "iat", "aud"]

# API key header name
API_KEY_HEADER = "X-API-Key"

# Per-user API key prefix (distinguishes user keys from tenant keys)
USER_API_KEY_PREFIX = "ar_user_"

# Service Provider Administrator (SPA) API key prefix (SPEC-1667).
# SPA keys authenticate the platform admin console. They are completely
# isolated from all tenant credentials — the SPA has zero permissions within
# any tenancy and does not exist as a user for any tenancy.
SPA_API_KEY_PREFIX = "ar_spa_"

# Publishable widget key (Decision UI-6)
WIDGET_KEY_HEADER = "X-Widget-Key"
WIDGET_KEY_PREFIX = "pk_live_"

# Internal verification token header (SPEC-1846: cloud-native verification)
VERIFICATION_TOKEN_HEADER = "X-Verification-Token"
VERIFICATION_TOKEN_MAX_AGE_S = 900  # 15 minutes (longest suite is ~12min)

# Paths where widget key authentication is allowed.
# Widget keys are scoped to chat endpoints and widget config only — they
# cannot access billing, dashboard, or any other tenant management APIs.
# /api/config is read-only and required for widget initialization.
WIDGET_KEY_ALLOWED_PREFIXES = (
    "/api/chat/",
    "/ws/chat/",
    "/api/config",
)

# Routes that bypass authentication (webhooks, health, public endpoints)
AUTH_EXEMPT_PREFIXES = (
    "/health",
    "/ready",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/widget.js",
    "/widget/",
    "/api/webhooks/",
    "/api/shopify/gdpr/",
    "/api/checkout/",
    "/api/packs/",
    "/api/shopify/billing/confirm",
    "/api/tenants/",
    "/api/admin/api-keys/reset",
    "/api/auth/magic-link",
    "/api/auth/2fa",
    "/api/auth/spa-recovery",  # SPEC-1678: unauthenticated backup code recovery
    "/api/auth/account-recovery",  # SPEC-1677: tenant account recovery verification
    "/api/status",
    "/admin/",
    "/api/test/email-capture",  # SPEC-1687: communication capture
    "/api/admin/email/confirm",  # SPEC-1683: email change confirmation (token-based)
)


# ---------------------------------------------------------------------------
# TenantContext — request-scoped identity
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TenantContext:
    """Authenticated tenant identity for the current request.

    Injected into request state by the auth middleware. All downstream
    handlers and repository calls use this to scope operations.

    Fields:
        tenant_id: Resolved tenant identifier (UUID).
        tier: Subscription tier (for rate limiting, feature gating).
        status: Tenant lifecycle status.
        auth_method: How the request was authenticated.
        is_widget_auth: True if authenticated via publishable widget key.
            Widget-authenticated requests are scoped to /api/chat/* only
            and cannot mutate config, billing, or tenant settings.
        shop_domain: Shopify shop domain (Shopify auth only).
        user_id: Shopify merchant user ID (Shopify auth only).
        session_id: Shopify session ID (Shopify auth only).

    Per-user identity (populated for user_api_key auth):
        team_member_id: Document ID of the authenticated team member.
        team_member_email: Email address of the authenticated team member.
        team_member_role: Role of the authenticated team member.
        escalation_categories: Categories assigned to escalation agents.
    """

    tenant_id: str
    tier: TenantTier | None = None
    status: TenantStatus = TenantStatus.ACTIVE
    auth_method: str = "api_key"  # "shopify_session", "api_key", "user_api_key", "widget_key"

    # Widget key auth (Decision UI-6) — scoped to /api/chat/* only
    is_widget_auth: bool = False

    # Platform admin auth (SPEC-1667) — SPA console only.
    # When True, tenant_id is PLATFORM_ADMIN_TENANT_ID ("__platform__")
    # and the request can ONLY access /api/superadmin/* endpoints.
    is_platform_admin: bool = False

    # Trial tier (WI #119) — ISO 8601 expiry timestamp
    trial_expires_at: str | None = None

    # Per-tenant rate limit override (from TenantDocument.rate_limit_rpm).
    # None = use tier default from TIER_DEFAULTS.
    rate_limit_rpm: int | None = None

    # Shopify-specific (populated only for session token auth)
    shop_domain: str | None = None
    user_id: str | None = None
    session_id: str | None = None

    # Per-user identity (populated for user_api_key auth)
    team_member_id: str | None = None
    team_member_email: str | None = None
    team_member_role: TeamMemberRole | None = None
    escalation_categories: tuple[str, ...] = ()
    agent_access: tuple[str, ...] = ()  # SPEC-1862: direct agent chat access

    # Platform admin identity (populated for spa_api_key auth, SPEC-1667)
    platform_admin_id: str | None = None
    platform_admin_email: str | None = None
    platform_admin_role: str | None = None  # "superadmin" or "operator" (SPEC-1675)
    platform_admin_notification_email: str | None = None  # SPEC-1676 override


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class TenantInactiveError(AuthenticationError):
    """Raised when the resolved tenant is not in an active state."""

    def __init__(self, tenant_id: str, status: str) -> None:
        self.tenant_id = tenant_id
        self.tenant_status = status
        super().__init__(
            f"Tenant {tenant_id} is {status}. Access denied.",
            status_code=403,
        )


# ---------------------------------------------------------------------------
# Shopify session token verification
# ---------------------------------------------------------------------------


def verify_shopify_session_token(token: str) -> dict[str, Any]:
    """Verify and decode a Shopify session token (JWT).

    Args:
        token: The raw JWT string (without "Bearer " prefix).

    Returns:
        The decoded JWT payload as a dict.

    Raises:
        AuthenticationError: If the token is invalid, expired, or
            fails any validation check.
    """
    api_key = SHOPIFY_API_KEY or os.environ.get("SHOPIFY_API_KEY", "")
    api_secret = SHOPIFY_API_SECRET or os.environ.get("SHOPIFY_API_SECRET", "")

    if not api_key or not api_secret:
        raise AuthenticationError(
            "Shopify app credentials not configured (SHOPIFY_API_KEY, SHOPIFY_API_SECRET).",
            status_code=500,
        )

    # Decode and verify signature + standard claims
    try:
        payload = jwt.decode(
            token,
            key=api_secret,
            algorithms=[JWT_ALGORITHM],
            audience=api_key,
            leeway=JWT_LEEWAY_SECONDS,
            options={"require": JWT_REQUIRED_CLAIMS},
        )
    except ExpiredSignatureError:
        raise AuthenticationError("Shopify session token has expired.")
    except ImmatureSignatureError:
        raise AuthenticationError("Shopify session token is not yet valid (nbf).")
    except InvalidAudienceError:
        raise AuthenticationError("Shopify session token audience does not match app.")
    except MissingRequiredClaimError as exc:
        raise AuthenticationError(f"Shopify session token missing required claim: {exc}")
    except DecodeError:
        raise AuthenticationError("Shopify session token is malformed or signature invalid.")
    except PyJWTError as exc:
        raise AuthenticationError(f"Shopify session token verification failed: {exc}")

    # Validate iss/dest hostname matching
    _validate_shopify_domains(payload)

    return payload


def _validate_shopify_domains(payload: dict[str, Any]) -> None:
    """Validate that iss and dest hostnames match and are valid Shopify domains.

    iss format:  https://{shop}.myshopify.com/admin
    dest format: https://{shop}.myshopify.com

    Raises:
        AuthenticationError: If domains are invalid or don't match.
    """
    iss = payload.get("iss", "")
    dest = payload.get("dest", "")

    iss_parsed = urlparse(iss)
    dest_parsed = urlparse(dest)

    iss_host = iss_parsed.hostname or ""
    dest_host = dest_parsed.hostname or ""

    # iss must be a valid .myshopify.com domain
    if not iss_host.endswith(".myshopify.com"):
        raise AuthenticationError(
            f"Shopify session token iss hostname is not a valid Shopify domain: {iss_host}"
        )

    # iss root (without /admin path) must match dest
    # iss: https://shop.myshopify.com/admin -> host: shop.myshopify.com
    # dest: https://shop.myshopify.com -> host: shop.myshopify.com
    if iss_host != dest_host:
        # Shopify spec requires dest to match iss shop domain.
        # Mismatches could indicate token-substitution attempts.
        raise AuthenticationError(
            f"Shopify session token iss/dest hostname mismatch: "
            f"iss={iss_host} dest={dest_host}"
        )

    # Scheme must be HTTPS
    if iss_parsed.scheme != "https" or dest_parsed.scheme != "https":
        raise AuthenticationError(
            "Shopify session token iss/dest must use HTTPS."
        )


def extract_shop_domain(payload: dict[str, Any]) -> str:
    """Extract the canonical shop domain from a verified session token.

    Uses the iss claim (always .myshopify.com) as the authoritative
    shop identifier, since dest may use a custom domain.

    Returns:
        The shop domain, e.g. "example-shop.myshopify.com"
    """
    iss = payload.get("iss", "")
    iss_parsed = urlparse(iss)
    return iss_parsed.hostname or ""


# ---------------------------------------------------------------------------
# API key verification
# ---------------------------------------------------------------------------


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage and comparison.

    Uses SHA-256 for fast comparison. The key itself is never stored.

    Args:
        api_key: The raw API key string.

    Returns:
        Hex-encoded SHA-256 hash of the key.
    """
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


async def verify_api_key(
    api_key: str,
    lookup_fn: Any,
) -> dict[str, Any]:
    """Verify an API key and resolve to a tenant.

    Args:
        api_key: The raw API key from the X-API-Key header.
        lookup_fn: Async function that accepts an API key hash
            and returns a tenant document or None.
            Signature: async (key_hash: str) -> dict | None

    Returns:
        The tenant document.

    Raises:
        AuthenticationError: If the key is invalid or no tenant found.
    """
    if not api_key:
        raise AuthenticationError("API key is required.")

    key_hash = hash_api_key(api_key)
    tenant = await lookup_fn(key_hash)

    if tenant is None:
        # Timing: don't reveal whether the key exists.
        # The hash computation takes constant time regardless.
        logger.warning("API key authentication failed: no matching tenant for key hash")
        raise AuthenticationError("Invalid API key.")

    return tenant


# ---------------------------------------------------------------------------
# Per-user API key generation and verification
# ---------------------------------------------------------------------------


def generate_user_api_key(tenant_id: str) -> str:
    """Generate a new per-user API key.

    Format: ar_user_{tenant_prefix}_{random}
    Example: ar_user_rema_yZR6wMzdVDlVJhbdRPW1Vh01TkytKcQ3

    The tenant prefix (first 4 chars of tenant_id) makes keys
    visually distinguishable per tenant. The random suffix provides
    cryptographic strength.

    Args:
        tenant_id: The tenant identifier (used for prefix).

    Returns:
        The raw API key string (must be sent to user, never stored).
    """
    import secrets

    prefix = tenant_id[:4].replace("-", "")
    random_part = secrets.token_urlsafe(24)
    return f"{USER_API_KEY_PREFIX}{prefix}_{random_part}"


def is_user_api_key(api_key: str) -> bool:
    """Check if an API key is a per-user key (vs tenant key).

    User keys start with 'ar_user_', tenant keys start with 'ar_live_'.
    """
    return api_key.startswith(USER_API_KEY_PREFIX)


async def verify_user_api_key(
    api_key: str,
    lookup_fn: Any,
) -> dict[str, Any]:
    """Verify a per-user API key and resolve to a team member + tenant.

    Args:
        api_key: The raw per-user API key (ar_user_...).
        lookup_fn: Async function that accepts a user API key hash
            and returns a dict with team member + tenant data, or None.
            Expected return: {
                "team_member": TeamMemberDocument dict,
                "tenant": TenantDocument dict,
            }

    Returns:
        Dict with team_member and tenant data.

    Raises:
        AuthenticationError: If the key is invalid, member is inactive,
            or no matching team member found.
    """
    if not api_key:
        raise AuthenticationError("API key is required.")

    key_hash = hash_api_key(api_key)
    result = await lookup_fn(key_hash)

    if result is None:
        logger.warning("User API key authentication failed: no matching team member")
        raise AuthenticationError("Invalid API key.")

    # Verify team member is active
    member = result.get("team_member", {})
    if not member.get("is_active", False):
        logger.warning(
            "User API key auth failed: member %s is inactive",
            member.get("email", "unknown"),
        )
        raise AuthenticationError("Account is disabled. Contact your administrator.")

    return result


# ---------------------------------------------------------------------------
# SPA platform admin key generation and verification (SPEC-1667)
# ---------------------------------------------------------------------------


def generate_spa_api_key() -> str:
    """Generate a new SPA platform admin API key.

    Format: ar_spa_plat_{random}
    Example: ar_spa_plat_yZR6wMzdVDlVJhbdRPW1Vh01TkytKcQ3

    Unlike tenant user keys (ar_user_{tenant_prefix}_{random}), SPA keys
    have NO tenant prefix because the SPA has no tenant affiliation.
    The "plat" segment is a fixed identifier for platform-level keys.

    Returns:
        The raw API key string (must be saved immediately, never stored raw).
    """
    import secrets

    random_part = secrets.token_urlsafe(24)
    return f"{SPA_API_KEY_PREFIX}plat_{random_part}"


def is_spa_api_key(api_key: str) -> bool:
    """Check if an API key is an SPA platform admin key.

    SPA keys start with 'ar_spa_', tenant user keys with 'ar_user_'.
    These are dispatched to completely separate credential stores.
    """
    return api_key.startswith(SPA_API_KEY_PREFIX)


async def verify_spa_api_key(
    api_key: str,
    lookup_fn: Any,
) -> dict[str, Any]:
    """Verify an SPA platform admin API key (SPEC-1667).

    Resolves credentials from the platform_admins collection — completely
    isolated from all tenant team_members collections.

    Args:
        api_key: The raw SPA API key (ar_spa_...).
        lookup_fn: Async function that accepts an API key hash and returns
            a platform admin document or None.
            Signature: async (key_hash: str) -> dict | None

    Returns:
        The platform admin document.

    Raises:
        AuthenticationError: If the key is invalid, admin is inactive,
            or no matching platform admin found.
    """
    if not api_key:
        raise AuthenticationError("API key is required.")

    key_hash = hash_api_key(api_key)
    admin = await lookup_fn(key_hash)

    if admin is None:
        logger.warning("SPA API key authentication failed: no matching platform admin")
        raise AuthenticationError("Invalid API key.")

    # Verify platform admin is active
    if not admin.get("is_active", False):
        logger.warning(
            "SPA API key auth failed: admin %s is inactive",
            admin.get("email", "unknown"),
        )
        raise AuthenticationError("Platform admin account is disabled.")

    return admin


# ---------------------------------------------------------------------------
# Internal verification tokens (SPEC-1846: cloud-native verification)
# ---------------------------------------------------------------------------


def generate_verification_token(run_id: str, secret: str) -> str:
    """Generate an HMAC-signed verification token for internal test requests.

    The token is used by VerificationRunner to authenticate against the same
    container's superadmin endpoints without a Cosmos lookup — enabling health
    verification even when Cosmos is down.

    Format: "{timestamp}.{run_id}.{hmac_hex}"
    HMAC = HMAC-SHA256(secret, "{timestamp}|{run_id}")

    Args:
        run_id: The verification run identifier (e.g., "run-abc123def456").
        secret: The INTERNAL_VERIFICATION_SECRET (auto-generated at startup).

    Returns:
        The signed token string.
    """
    ts = str(int(time.time()))
    payload = f"{ts}|{run_id}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{ts}.{run_id}.{sig}"


def verify_verification_token(
    token: str,
    secret: str,
    max_age_seconds: int = VERIFICATION_TOKEN_MAX_AGE_S,
) -> dict[str, Any]:
    """Verify an HMAC-signed internal verification token.

    Args:
        token: The token string from X-Verification-Token header.
        secret: The INTERNAL_VERIFICATION_SECRET.
        max_age_seconds: Maximum token age before rejection (default 900s).

    Returns:
        {"run_id": str, "timestamp": int} on success.

    Raises:
        AuthenticationError: On any validation failure (expired, tampered, etc.).
    """
    if not token or not secret:
        raise AuthenticationError("Invalid verification token.")

    # Split: "{timestamp}.{run_id}.{hmac_hex}"
    # run_id is like "run-abc123def456" (no dots), so split on first and last dot
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthenticationError("Invalid verification token.")

    ts_str, run_id, provided_sig = parts

    # Validate timestamp
    try:
        ts = int(ts_str)
    except ValueError:
        raise AuthenticationError("Invalid verification token.")

    age = abs(time.time() - ts)
    if age > max_age_seconds:
        raise AuthenticationError("Verification token expired.")

    # Recompute and compare HMAC (constant-time)
    payload = f"{ts_str}|{run_id}"
    expected_sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not secrets.compare_digest(provided_sig, expected_sig):
        raise AuthenticationError("Invalid verification token.")

    return {"run_id": run_id, "timestamp": ts}


# ---------------------------------------------------------------------------
# Publishable widget key verification (Decision UI-6)
# ---------------------------------------------------------------------------


def generate_widget_key(tenant_id: str) -> str:
    """Generate a new publishable widget key.

    Format: pk_live_{tenant_hash}_{random}
    Example: pk_live_a7f3c9e1b2c3_d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9

    The tenant hash prefix (first 12 hex chars of SHA-256) makes keys
    visually distinguishable per tenant. The random suffix (32 hex chars)
    provides cryptographic strength.

    Args:
        tenant_id: The tenant identifier (used for hash prefix).

    Returns:
        The raw widget key (must be sent to user, never stored directly).
    """
    import secrets

    tenant_hash = hashlib.sha256(tenant_id.encode()).hexdigest()[:12]
    random_part = secrets.token_hex(16)
    return f"{WIDGET_KEY_PREFIX}{tenant_hash}_{random_part}"


def validate_widget_key_format(key: str) -> bool:
    """Check that a widget key matches the expected format.

    Format: pk_live_{tenant_id_hash}_{random}
    Example: pk_live_a7f3c9e1_x8k2m5p9

    The key must start with the WIDGET_KEY_PREFIX and contain at least
    two underscore-separated segments after the prefix.
    """
    if not key.startswith(WIDGET_KEY_PREFIX):
        return False
    suffix = key[len(WIDGET_KEY_PREFIX):]
    # Must have at least hash_random (two parts separated by _)
    parts = suffix.split("_", 1)
    return len(parts) == 2 and len(parts[0]) >= 4 and len(parts[1]) >= 4


def hash_widget_key(key: str) -> str:
    """Hash a publishable widget key for storage and comparison.

    Uses the same SHA-256 approach as API keys.
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


async def verify_widget_key(
    widget_key: str,
    lookup_fn: Any,
) -> dict[str, Any]:
    """Verify a publishable widget key and resolve to a tenant.

    Args:
        widget_key: The raw widget key (pk_live_...).
        lookup_fn: Async function that accepts a widget key hash
            and returns a tenant document or None.

    Returns:
        The tenant document.

    Raises:
        AuthenticationError: If the key is invalid or no tenant found.
    """
    if not widget_key:
        raise AuthenticationError("Widget key is required.")

    if not validate_widget_key_format(widget_key):
        raise AuthenticationError("Invalid widget key format.")

    key_hash = hash_widget_key(widget_key)
    tenant = await lookup_fn(key_hash)

    if tenant is None:
        logger.warning("Widget key authentication failed: no matching tenant")
        raise AuthenticationError("Invalid widget key.")

    return tenant


def is_widget_key_allowed_path(path: str) -> bool:
    """Check if the request path is allowed for widget key auth.

    Widget keys are scoped to /api/chat/* and /ws/chat/* only.
    """
    return path.startswith(WIDGET_KEY_ALLOWED_PREFIXES)


# ---------------------------------------------------------------------------
# Tenant status validation
# ---------------------------------------------------------------------------

# Statuses that allow normal API access
_ACTIVE_STATUSES = {TenantStatus.ACTIVE, TenantStatus.PAST_DUE}

# Statuses that allow read-only API access (future: implement read-only mode)
_READONLY_STATUSES = {TenantStatus.GRACE_PERIOD}


def validate_tenant_status(
    tenant_id: str,
    status: TenantStatus,
    allow_readonly: bool = False,
) -> None:
    """Validate that a tenant's status allows API access.

    Args:
        tenant_id: Tenant identifier (for error messages).
        status: Current tenant status.
        allow_readonly: If True, GRACE_PERIOD is also accepted.

    Raises:
        TenantInactiveError: If the tenant status doesn't allow access.
    """
    allowed = _ACTIVE_STATUSES
    if allow_readonly:
        allowed = allowed | _READONLY_STATUSES

    if status not in allowed:
        raise TenantInactiveError(tenant_id, status.value)


# ---------------------------------------------------------------------------
# Request authentication helpers
# ---------------------------------------------------------------------------


def extract_bearer_token(authorization: str | None) -> str | None:
    """Extract the token from an Authorization: Bearer <token> header.

    Returns None if the header is missing or not a Bearer token.
    """
    if not authorization:
        return None

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]


def is_auth_exempt(path: str) -> bool:
    """Check if a request path is exempt from authentication.

    Exempt paths: health checks, webhooks (have their own auth),
    checkout callbacks, OpenAPI docs.
    """
    return path.startswith(AUTH_EXEMPT_PREFIXES)
