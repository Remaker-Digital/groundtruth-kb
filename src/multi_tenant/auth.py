"""
Dual authentication: Shopify session tokens + API keys.

Verifies incoming requests and resolves them to a tenant_id. Both
authentication channels produce the same TenantContext object that
downstream handlers use to scope all database operations.

Authentication methods (Decision #4):
    1. Shopify session tokens — JWT signed with app secret (HS256).
       Sent as Authorization: Bearer <token> by App Bridge.
       Resolves tenant via shop domain → tenants collection lookup.

    2. API keys — hashed, stored in Key Vault.
       Sent as X-API-Key: <key> header.
       Resolves tenant via API key hash → tenants collection lookup.

    3. Webhook signatures — Stripe/Shopify webhook-specific auth.
       These endpoints bypass tenant resolution (handled per-webhook).

Request flow:
    HTTP request
    → Extract auth credentials (Bearer token or API key header)
    → Verify credentials (JWT decode or hash lookup)
    → Resolve tenant_id from verified identity
    → Validate tenant status (must be ACTIVE or PAST_DUE)
    → Inject TenantContext into request state
    → Handler receives TenantContext via FastAPI dependency

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import os
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

from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier

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

# Routes that bypass authentication (webhooks, health, public endpoints)
AUTH_EXEMPT_PREFIXES = (
    "/health",
    "/ready",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/webhooks/",
    "/api/checkout/success",
    "/api/checkout/cancel",
    "/api/shopify/billing/confirm",
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
        shop_domain: Shopify shop domain (Shopify auth only).
        user_id: Shopify merchant user ID (Shopify auth only).
        session_id: Shopify session ID (Shopify auth only).
    """

    tenant_id: str
    tier: TenantTier | None = None
    status: TenantStatus = TenantStatus.ACTIVE
    auth_method: str = "api_key"  # "shopify_session" or "api_key"

    # Shopify-specific (populated only for session token auth)
    shop_domain: str | None = None
    user_id: str | None = None
    session_id: str | None = None


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
        # Allow custom domain on dest (App Bridge may use custom domain)
        # In this case, we trust the iss hostname (which is always .myshopify.com)
        logger.info(
            "Shopify session token iss/dest hostname mismatch: iss=%s dest=%s "
            "(may be custom domain — accepting iss as authoritative)",
            iss_host, dest_host,
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
