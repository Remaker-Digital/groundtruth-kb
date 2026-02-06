"""Admin API Key Management API — generate, rotate, revoke API keys (WI #159).

Provides REST endpoints for merchant API key lifecycle management:

    GET    /api/admin/api-keys       — Get current API key metadata (prefix, created)
    POST   /api/admin/api-keys       — Generate a new API key (only if none exists)
    POST   /api/admin/api-keys/rotate — Rotate: generate new key, invalidate old
    DELETE /api/admin/api-keys       — Revoke the current API key

API keys are the primary authentication mechanism for direct-channel (Stripe)
merchants. Shopify merchants use session tokens but may also use API keys for
programmatic access.

Security properties:
    - Keys are never stored in plaintext (SHA-256 hash only in Cosmos DB)
    - The raw key is returned ONCE at generation time and never again
    - Key format: ar_live_{tenant_prefix}_{random} (40 chars)
    - Rotation creates new key + updates hash atomically
    - All operations logged to audit trail (SECURITY_EVENT)

Architecture references:
    - Decision #4: Triple auth (Shopify JWT + API key + widget key)
    - Decision #13: Audit logging for security events
    - WI #159: API key rotation endpoint

Dependencies:
    - auth.py: hash_api_key()
    - repository.py: TenantRepository
    - cosmos_schema.py: TenantDocument, AuditEventType

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import secrets
import string
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.multi_tenant.auth import TenantContext, hash_api_key
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_KEY_PREFIX = "ar_live_"
API_KEY_RANDOM_LENGTH = 32  # 32 chars of randomness
API_KEY_ALPHABET = string.ascii_letters + string.digits


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ApiKeyMetadataResponse(BaseModel):
    """API key metadata (never includes the raw key)."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    has_key: bool = Field(description="Whether an API key is currently set")
    key_prefix: str | None = Field(
        default=None, description="First 12 chars of the key (for identification)"
    )
    created_at: str | None = Field(
        default=None, description="ISO 8601 timestamp when the key was created"
    )
    last_rotated_at: str | None = Field(
        default=None, description="ISO 8601 timestamp of last rotation"
    )


class ApiKeyGeneratedResponse(BaseModel):
    """Response returned when a new API key is generated.

    The raw key is returned ONCE and never stored or retrievable again.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    api_key: str = Field(description="The raw API key — save this, it cannot be retrieved again")
    key_prefix: str = Field(description="First 12 chars for future identification")
    created_at: str = Field(description="ISO 8601 timestamp")
    message: str = Field(
        default="Save this API key securely. It will not be shown again.",
    )


class ApiKeyRevokedResponse(BaseModel):
    """Confirmation of key revocation."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    revoked: bool = True
    revoked_at: str = Field(description="ISO 8601 timestamp")


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------


def generate_api_key(tenant_id: str) -> str:
    """Generate a new API key with tenant-specific prefix.

    Format: ar_live_{tenant_prefix}_{random}
    Example: ar_live_tn8f3c_AbCdEf...

    The tenant prefix aids visual identification without revealing the
    full tenant_id.
    """
    tenant_prefix = tenant_id[:6] if len(tenant_id) >= 6 else tenant_id
    random_part = "".join(
        secrets.choice(API_KEY_ALPHABET) for _ in range(API_KEY_RANDOM_LENGTH)
    )
    return f"{API_KEY_PREFIX}{tenant_prefix}_{random_part}"


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(
    prefix="/api/admin/api-keys",
    tags=["API Key Management"],
)

# Service injection (wired at startup)
_tenant_repo: Any = None
_audit_repo: Any = None


def configure_apikey_services(
    tenant_repo: Any,
    audit_repo: Any | None = None,
) -> None:
    """Inject repository dependencies at app startup."""
    global _tenant_repo, _audit_repo
    _tenant_repo = tenant_repo
    _audit_repo = audit_repo


async def _log_audit(
    tenant_id: str,
    event_type: str,
    details: dict[str, Any],
) -> None:
    """Log a security event to the audit trail."""
    if _audit_repo is None:
        return
    try:
        from src.multi_tenant.cosmos_schema import AuditEventType

        await _audit_repo.create(
            tenant_id=tenant_id,
            document={
                "id": f"audit-{secrets.token_hex(8)}",
                "tenant_id": tenant_id,
                "event_type": event_type,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "actor": "admin",
            },
        )
    except Exception:
        logger.warning("Failed to write audit log for API key operation", exc_info=True)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=ApiKeyMetadataResponse,
    summary="Get API key metadata",
    description="Returns metadata about the current API key without exposing the key itself.",
)
async def get_api_key_metadata(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyMetadataResponse:
    """Return metadata about the tenant's current API key."""
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    has_key = bool(tenant.get("api_key_hash"))
    key_prefix = tenant.get("api_key_prefix")
    created_at = tenant.get("api_key_created_at")
    last_rotated = tenant.get("api_key_last_rotated_at")

    return ApiKeyMetadataResponse(
        has_key=has_key,
        key_prefix=key_prefix,
        created_at=created_at,
        last_rotated_at=last_rotated,
    )


@router.post(
    "",
    response_model=ApiKeyGeneratedResponse,
    status_code=201,
    summary="Generate a new API key",
    description="Generate a new API key. Fails if one already exists (use rotate instead).",
)
async def generate_new_api_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyGeneratedResponse:
    """Generate a new API key for the tenant.

    Fails with 409 if a key already exists — use POST /rotate instead.
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if tenant.get("api_key_hash"):
        raise HTTPException(
            status_code=409,
            detail="API key already exists. Use POST /api/admin/api-keys/rotate to rotate.",
        )

    raw_key = generate_api_key(ctx.tenant_id)
    key_hash = hash_api_key(raw_key)
    now = datetime.now(timezone.utc).isoformat()
    key_prefix = raw_key[:12]

    # Update tenant document with new key hash + metadata
    await _tenant_repo.patch(
        item_id=ctx.tenant_id,
        partition_key=ctx.tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": key_hash},
            {"op": "set", "path": "/api_key_prefix", "value": key_prefix},
            {"op": "set", "path": "/api_key_created_at", "value": now},
        ],
    )

    await _log_audit(
        ctx.tenant_id,
        "security.event",
        {"action": "api_key_generated", "key_prefix": key_prefix},
    )

    logger.info(
        "API key generated for tenant %s (prefix: %s)",
        ctx.tenant_id,
        key_prefix,
    )

    return ApiKeyGeneratedResponse(
        api_key=raw_key,
        key_prefix=key_prefix,
        created_at=now,
    )


@router.post(
    "/rotate",
    response_model=ApiKeyGeneratedResponse,
    summary="Rotate API key",
    description="Generate a new API key, invalidating the old one immediately.",
)
async def rotate_api_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyGeneratedResponse:
    """Rotate the tenant's API key.

    Generates a new key and immediately invalidates the old one.
    The new raw key is returned once and cannot be retrieved again.
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    old_prefix = tenant.get("api_key_prefix", "none")

    raw_key = generate_api_key(ctx.tenant_id)
    key_hash = hash_api_key(raw_key)
    now = datetime.now(timezone.utc).isoformat()
    key_prefix = raw_key[:12]

    # Atomically update with new key hash
    await _tenant_repo.patch(
        item_id=ctx.tenant_id,
        partition_key=ctx.tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": key_hash},
            {"op": "set", "path": "/api_key_prefix", "value": key_prefix},
            {"op": "set", "path": "/api_key_created_at", "value": now},
            {"op": "set", "path": "/api_key_last_rotated_at", "value": now},
        ],
    )

    await _log_audit(
        ctx.tenant_id,
        "security.event",
        {
            "action": "api_key_rotated",
            "old_prefix": old_prefix,
            "new_prefix": key_prefix,
        },
    )

    logger.info(
        "API key rotated for tenant %s (old: %s → new: %s)",
        ctx.tenant_id,
        old_prefix,
        key_prefix,
    )

    return ApiKeyGeneratedResponse(
        api_key=raw_key,
        key_prefix=key_prefix,
        created_at=now,
        message="API key rotated. The old key is immediately invalid. Save this new key securely.",
    )


@router.delete(
    "",
    response_model=ApiKeyRevokedResponse,
    summary="Revoke API key",
    description="Permanently revoke the current API key. A new one must be generated to restore access.",
)
async def revoke_api_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ApiKeyRevokedResponse:
    """Revoke the tenant's API key.

    After revocation, API key authentication will fail until a new key
    is generated.
    """
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    tenant = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.get("api_key_hash"):
        raise HTTPException(status_code=404, detail="No API key to revoke")

    old_prefix = tenant.get("api_key_prefix", "unknown")
    now = datetime.now(timezone.utc).isoformat()

    # Clear key hash and metadata
    await _tenant_repo.patch(
        item_id=ctx.tenant_id,
        partition_key=ctx.tenant_id,
        operations=[
            {"op": "set", "path": "/api_key_hash", "value": None},
            {"op": "set", "path": "/api_key_prefix", "value": None},
            {"op": "set", "path": "/api_key_created_at", "value": None},
            {"op": "set", "path": "/api_key_last_rotated_at", "value": None},
        ],
    )

    await _log_audit(
        ctx.tenant_id,
        "security.event",
        {"action": "api_key_revoked", "revoked_prefix": old_prefix},
    )

    logger.info(
        "API key revoked for tenant %s (prefix: %s)",
        ctx.tenant_id,
        old_prefix,
    )

    return ApiKeyRevokedResponse(revoked_at=now)
