"""Superadmin API -- Rate limit and back-off/retry configuration.

Domain sub-module for SPEC-1819 (Code-Free Runtime Configuration — rate limits)
and SPEC-1821 (Back-off and Retry Configuration). Endpoints are registered on
the shared router from _monolith.

Rate Limits:
  GET  /rate-limits              — List rate limit config per tier + global floor
  GET  /rate-limits/{tier}       — Read rate limit config for a specific tier
  PUT  /rate-limits/{tier}       — Write rate limit config for a tier
  GET  /rate-limits/history      — Audit history for rate limit changes

Back-off / Retry:
  GET  /retry-configs              — List retry configs for all services
  GET  /retry-configs/{service}    — Read retry config for a specific service
  PUT  /retry-configs/{service}    — Write retry config for a service
  GET  /retry-configs/history      — Audit history for retry config changes

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    PlatformConfigDocument,
)
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _get_platform_repo():
    """Get the PlatformConfigRepository, lazy import to avoid circular deps."""
    from src.multi_tenant.repositories.platform import PlatformConfigRepository
    return PlatformConfigRepository()


# ---------------------------------------------------------------------------
# Rate limit models (SPEC-1819 / WI-1417)
# ---------------------------------------------------------------------------

_RL_CONFIG_TYPE = "rate_limits"

VALID_RATE_LIMIT_TIERS = {"trial", "starter", "professional", "enterprise", "global"}


class RateLimitConfig(CamelCaseModel):
    """Rate limit configuration for a tier or global defaults."""

    rpm: int = Field(..., ge=1, description="Requests per minute")
    floor: int = Field(default=10, ge=0, description="Minimum RPM floor (never throttle below this)")
    burst_multiplier: float = Field(
        default=1.0, ge=1.0, le=5.0,
        description="Burst allowance multiplier (e.g. 1.5 = allow 50% burst above rpm)",
    )
    exempt_roles: list[str] = Field(
        default_factory=lambda: ["platform_admin"],
        description="Roles exempt from rate limiting",
    )


class RateLimitResponse(CamelCaseModel):
    """Response from reading a rate limit config."""

    tier: str
    config: RateLimitConfig
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class RateLimitListResponse(CamelCaseModel):
    """Response listing all rate limit configs."""

    configs: list[RateLimitResponse]
    total: int


class RateLimitWriteRequest(CamelCaseModel):
    """Request body for writing a rate limit config."""

    config: RateLimitConfig
    change_reason: str = Field(
        default="",
        description="Optional reason for this change (SPEC-1828 audit trail)",
    )


class RateLimitWriteResponse(CamelCaseModel):
    """Response after writing a rate limit config."""

    tier: str
    version: int
    updated_at: str
    cache_invalidated: bool = False


# ---------------------------------------------------------------------------
# Rate limit endpoints (SPEC-1819 / WI-1417)
# ---------------------------------------------------------------------------


@router.get(
    "/rate-limits",
    response_model=RateLimitListResponse,
    summary="List all rate limit configurations (SPEC-1819)",
    description=(
        "Returns rate limit configuration for each tier plus global defaults. "
        "If no Cosmos document exists for a tier, returns the frozen default (300 RPM)."
    ),
    status_code=200,
)
async def list_rate_limits() -> RateLimitListResponse:
    """List rate limit configurations for all tiers."""
    repo = _get_platform_repo()
    configs: list[RateLimitResponse] = []

    for tier in sorted(VALID_RATE_LIMIT_TIERS):
        doc = await repo.get_config(_RL_CONFIG_TYPE, tier)
        if doc is not None:
            value = doc.get("value", {})
            configs.append(RateLimitResponse(
                tier=tier,
                config=RateLimitConfig(**value),
                version=doc.get("version", 1),
                updated_at=doc.get("updated_at"),
                updated_by=doc.get("updated_by"),
            ))
        else:
            # Frozen default
            configs.append(RateLimitResponse(
                tier=tier,
                config=RateLimitConfig(rpm=300, floor=10),
                version=0,
                updated_at=None,
                updated_by=None,
            ))

    return RateLimitListResponse(configs=configs, total=len(configs))


@router.get(
    "/rate-limits/history",
    summary="Rate limit change audit history (SPEC-1819)",
    description="Returns audit log entries for rate limit configuration changes.",
    status_code=200,
)
async def rate_limit_history(
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
) -> dict[str, Any]:
    """Get audit trail of rate limit configuration changes."""
    from src.multi_tenant.repositories.platform import AuditLogRepository

    audit_repo = AuditLogRepository()

    query = (
        "SELECT * FROM c "
        "WHERE c.event_type = @event_type "
        "AND STARTSWITH(c.payload.action, 'rate_limit_') "
        "ORDER BY c.timestamp DESC "
        "OFFSET @skip LIMIT @limit"
    )
    params = [
        {"name": "@event_type", "value": AuditEventType.CONFIG_CHANGE.value},
        {"name": "@skip", "value": skip},
        {"name": "@limit", "value": limit},
    ]

    items: list[dict[str, Any]] = []
    try:
        async for item in audit_repo._container.query_items(
            query=query,
            parameters=params,
        ):
            payload = item.get("payload", {})
            items.append({
                "id": item.get("id"),
                "action": payload.get("action"),
                "tier": payload.get("config_key"),
                "actor": item.get("actor"),
                "timestamp": item.get("timestamp"),
                "previous_version": payload.get("previous_version"),
                "new_version": payload.get("new_version"),
                "change_reason": payload.get("change_reason", ""),
                "diff_summary": payload.get("diff_summary", []),
            })
    except Exception:
        logger.warning("Audit log query failed for rate limit history", exc_info=True)

    return {"entries": items, "total": len(items), "skip": skip, "limit": limit}


@router.get(
    "/rate-limits/{tier}",
    response_model=RateLimitResponse,
    summary="Read rate limit config for a tier (SPEC-1819)",
    description="Read the rate limit configuration for a specific tier or 'global'.",
    responses={400: {"description": "Invalid tier name"}},
    status_code=200,
)
async def get_rate_limit(tier: str) -> RateLimitResponse:
    """Read rate limit configuration for a specific tier."""
    if tier not in VALID_RATE_LIMIT_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{tier}'. Valid: {sorted(VALID_RATE_LIMIT_TIERS)}",
        )

    repo = _get_platform_repo()
    doc = await repo.get_config(_RL_CONFIG_TYPE, tier)

    if doc is not None:
        value = doc.get("value", {})
        return RateLimitResponse(
            tier=tier,
            config=RateLimitConfig(**value),
            version=doc.get("version", 1),
            updated_at=doc.get("updated_at"),
            updated_by=doc.get("updated_by"),
        )

    # Frozen default
    return RateLimitResponse(
        tier=tier,
        config=RateLimitConfig(rpm=300, floor=10),
        version=0,
    )


@router.put(
    "/rate-limits/{tier}",
    response_model=RateLimitWriteResponse,
    summary="Write rate limit config for a tier (SPEC-1819)",
    description=(
        "Create or update the rate limit configuration for a tier. "
        "Increments version. Invalidates caches."
    ),
    responses={400: {"description": "Invalid tier name"}},
    status_code=200,
)
async def put_rate_limit(
    tier: str,
    body: RateLimitWriteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> RateLimitWriteResponse:
    """Write rate limit configuration for a specific tier."""
    if tier not in VALID_RATE_LIMIT_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{tier}'. Valid: {sorted(VALID_RATE_LIMIT_TIERS)}",
        )

    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing to get current version
    existing = await repo.get_config(_RL_CONFIG_TYPE, tier)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    # Build and upsert
    value = body.config.model_dump()
    doc = PlatformConfigDocument(
        id=f"{_RL_CONFIG_TYPE}:{tier}",
        config_type=_RL_CONFIG_TYPE,
        config_key=tier,
        value=value,
        version=new_version,
        updated_at=now_iso,
        updated_by=actor,
    )
    await repo.set_config(doc)

    # Invalidate caches
    cache_invalidated = False
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        svc.invalidate_cache(f"rate_limits:{tier}")
        await svc.invalidate_redis(f"rate_limits:{tier}")
        cache_invalidated = True
    except Exception:
        logger.warning("Cache invalidation failed for rate_limits:%s", tier, exc_info=True)

    # Audit log (SPEC-1828)
    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository
        audit = AuditLogRepository()

        old_value = existing.get("value", {}) if existing else {}
        diff_summary: list[str] = []
        for k in set(list(old_value.keys()) + list(value.keys())):
            old_v = old_value.get(k)
            new_v = value.get(k)
            if old_v != new_v:
                diff_summary.append(f"{k}: {old_v} → {new_v}")

        await audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            tenant_id="__platform__",
            actor=actor,
            actor_type="admin",
            payload={
                "action": "rate_limit_updated",
                "config_type": _RL_CONFIG_TYPE,
                "config_key": tier,
                "previous_version": previous_version,
                "new_version": new_version,
                "change_reason": body.change_reason,
                "old_keys": sorted(old_value.keys()),
                "new_keys": sorted(value.keys()),
                "diff_summary": diff_summary,
            },
        )
    except Exception:
        logger.warning("Audit log failed for rate limit write", exc_info=True)

    logger.info(
        "Rate limit updated: %s v%d→v%d (by %s)%s",
        tier, previous_version, new_version, actor,
        f" reason={body.change_reason}" if body.change_reason else "",
    )

    return RateLimitWriteResponse(
        tier=tier,
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )


# ---------------------------------------------------------------------------
# Back-off / retry config models (SPEC-1821 / WI-1419)
# ---------------------------------------------------------------------------

_RC_CONFIG_TYPE = "retry_config"

VALID_SERVICES = {
    "openai", "cosmos", "redis", "smtp", "nats", "shopify",
}


class RetryConfig(CamelCaseModel):
    """Retry and back-off configuration for an external service."""

    max_retries: int = Field(default=3, ge=0, le=20, description="Maximum retry attempts")
    base_delay_ms: int = Field(default=100, ge=10, le=60000, description="Initial delay in ms")
    max_delay_ms: int = Field(default=5000, ge=100, le=300000, description="Maximum delay in ms")
    backoff_multiplier: float = Field(
        default=2.0, ge=1.0, le=10.0,
        description="Exponential backoff multiplier",
    )
    circuit_breaker_threshold: int = Field(
        default=10, ge=1, le=1000,
        description="Consecutive failures before circuit opens",
    )
    circuit_breaker_reset_s: int = Field(
        default=300, ge=10, le=3600,
        description="Seconds before half-open retry after circuit opens",
    )
    timeout_ms: int = Field(
        default=30000, ge=1000, le=300000,
        description="Request timeout in milliseconds",
    )


class RetryConfigResponse(CamelCaseModel):
    """Response from reading a retry config."""

    service: str
    config: RetryConfig
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class RetryConfigListResponse(CamelCaseModel):
    """Response listing all retry configs."""

    configs: list[RetryConfigResponse]
    total: int


class RetryConfigWriteRequest(CamelCaseModel):
    """Request body for writing a retry config."""

    config: RetryConfig
    change_reason: str = Field(
        default="",
        description="Optional reason for this change (SPEC-1828 audit trail)",
    )


class RetryConfigWriteResponse(CamelCaseModel):
    """Response after writing a retry config."""

    service: str
    version: int
    updated_at: str
    cache_invalidated: bool = False


# ---------------------------------------------------------------------------
# Retry config endpoints (SPEC-1821 / WI-1419)
# ---------------------------------------------------------------------------


@router.get(
    "/retry-configs",
    response_model=RetryConfigListResponse,
    summary="List all retry/back-off configurations (SPEC-1821)",
    description=(
        "Returns retry and back-off configuration for all external services. "
        "Missing configs return sensible defaults."
    ),
    status_code=200,
)
async def list_retry_configs() -> RetryConfigListResponse:
    """List retry configurations for all services."""
    repo = _get_platform_repo()
    configs: list[RetryConfigResponse] = []

    for service in sorted(VALID_SERVICES):
        doc = await repo.get_config(_RC_CONFIG_TYPE, service)
        if doc is not None:
            value = doc.get("value", {})
            configs.append(RetryConfigResponse(
                service=service,
                config=RetryConfig(**value),
                version=doc.get("version", 1),
                updated_at=doc.get("updated_at"),
                updated_by=doc.get("updated_by"),
            ))
        else:
            configs.append(RetryConfigResponse(
                service=service,
                config=RetryConfig(),
                version=0,
            ))

    return RetryConfigListResponse(configs=configs, total=len(configs))


@router.get(
    "/retry-configs/history",
    summary="Retry config change audit history (SPEC-1821)",
    description="Returns audit log entries for retry configuration changes.",
    status_code=200,
)
async def retry_config_history(
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
) -> dict[str, Any]:
    """Get audit trail of retry configuration changes."""
    from src.multi_tenant.repositories.platform import AuditLogRepository

    audit_repo = AuditLogRepository()

    query = (
        "SELECT * FROM c "
        "WHERE c.event_type = @event_type "
        "AND STARTSWITH(c.payload.action, 'retry_config_') "
        "ORDER BY c.timestamp DESC "
        "OFFSET @skip LIMIT @limit"
    )
    params = [
        {"name": "@event_type", "value": AuditEventType.CONFIG_CHANGE.value},
        {"name": "@skip", "value": skip},
        {"name": "@limit", "value": limit},
    ]

    items: list[dict[str, Any]] = []
    try:
        async for item in audit_repo._container.query_items(
            query=query,
            parameters=params,
        ):
            payload = item.get("payload", {})
            items.append({
                "id": item.get("id"),
                "action": payload.get("action"),
                "service": payload.get("config_key"),
                "actor": item.get("actor"),
                "timestamp": item.get("timestamp"),
                "previous_version": payload.get("previous_version"),
                "new_version": payload.get("new_version"),
                "change_reason": payload.get("change_reason", ""),
                "diff_summary": payload.get("diff_summary", []),
            })
    except Exception:
        logger.warning("Audit log query failed for retry config history", exc_info=True)

    return {"entries": items, "total": len(items), "skip": skip, "limit": limit}


@router.get(
    "/retry-configs/{service}",
    response_model=RetryConfigResponse,
    summary="Read retry config for a service (SPEC-1821)",
    description="Read the retry/back-off configuration for a specific external service.",
    responses={400: {"description": "Invalid service name"}},
    status_code=200,
)
async def get_retry_config(service: str) -> RetryConfigResponse:
    """Read retry configuration for a specific service."""
    if service not in VALID_SERVICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service '{service}'. Valid: {sorted(VALID_SERVICES)}",
        )

    repo = _get_platform_repo()
    doc = await repo.get_config(_RC_CONFIG_TYPE, service)

    if doc is not None:
        value = doc.get("value", {})
        return RetryConfigResponse(
            service=service,
            config=RetryConfig(**value),
            version=doc.get("version", 1),
            updated_at=doc.get("updated_at"),
            updated_by=doc.get("updated_by"),
        )

    return RetryConfigResponse(
        service=service,
        config=RetryConfig(),
        version=0,
    )


@router.put(
    "/retry-configs/{service}",
    response_model=RetryConfigWriteResponse,
    summary="Write retry config for a service (SPEC-1821)",
    description=(
        "Create or update the retry/back-off configuration for an external service. "
        "Increments version. Invalidates caches."
    ),
    responses={400: {"description": "Invalid service name or base_delay_ms > max_delay_ms"}},
    status_code=200,
)
async def put_retry_config(
    service: str,
    body: RetryConfigWriteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> RetryConfigWriteResponse:
    """Write retry configuration for a specific service."""
    if service not in VALID_SERVICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid service '{service}'. Valid: {sorted(VALID_SERVICES)}",
        )

    # Validate base_delay_ms <= max_delay_ms
    if body.config.base_delay_ms > body.config.max_delay_ms:
        raise HTTPException(
            status_code=400,
            detail=f"base_delay_ms ({body.config.base_delay_ms}) must not exceed "
            f"max_delay_ms ({body.config.max_delay_ms})",
        )

    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing to get current version
    existing = await repo.get_config(_RC_CONFIG_TYPE, service)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    # Build and upsert
    value = body.config.model_dump()
    doc = PlatformConfigDocument(
        id=f"{_RC_CONFIG_TYPE}:{service}",
        config_type=_RC_CONFIG_TYPE,
        config_key=service,
        value=value,
        version=new_version,
        updated_at=now_iso,
        updated_by=actor,
    )
    await repo.set_config(doc)

    # Invalidate caches
    cache_invalidated = False
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service
        svc = get_entitlement_service()
        svc.invalidate_cache(f"retry_config:{service}")
        await svc.invalidate_redis(f"retry_config:{service}")
        cache_invalidated = True
    except Exception:
        logger.warning("Cache invalidation failed for retry_config:%s", service, exc_info=True)

    # Audit log (SPEC-1828)
    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository
        audit = AuditLogRepository()

        old_value = existing.get("value", {}) if existing else {}
        diff_summary: list[str] = []
        for k in set(list(old_value.keys()) + list(value.keys())):
            old_v = old_value.get(k)
            new_v = value.get(k)
            if old_v != new_v:
                diff_summary.append(f"{k}: {old_v} → {new_v}")

        await audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            tenant_id="__platform__",
            actor=actor,
            actor_type="admin",
            payload={
                "action": "retry_config_updated",
                "config_type": _RC_CONFIG_TYPE,
                "config_key": service,
                "previous_version": previous_version,
                "new_version": new_version,
                "change_reason": body.change_reason,
                "old_keys": sorted(old_value.keys()),
                "new_keys": sorted(value.keys()),
                "diff_summary": diff_summary,
            },
        )
    except Exception:
        logger.warning("Audit log failed for retry config write", exc_info=True)

    logger.info(
        "Retry config updated: %s v%d→v%d (by %s)%s",
        service, previous_version, new_version, actor,
        f" reason={body.change_reason}" if body.change_reason else "",
    )

    return RetryConfigWriteResponse(
        service=service,
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )
