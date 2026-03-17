"""Superadmin API -- Entitlement CRUD and feature flag management.

Domain sub-module for SPEC-1816 (Superadmin Entitlement Management API)
and SPEC-1824 (Feature Flag System). Endpoints are registered on the
shared router from _monolith.

Endpoints:
  GET  /entitlements              — List all entitlement config documents
  GET  /entitlements/{config_key} — Read a single entitlement document
  PUT  /entitlements/{config_key} — Write (create/update) an entitlement document
  GET  /entitlements/history      — Audit history for entitlement changes
  GET  /entitlements/diff         — Compare current vs frozen fallback

  GET  /feature-flags             — List all feature flags
  PUT  /feature-flags             — Write the feature flags document
  GET  /feature-flags/evaluate    — Evaluate a flag for a tenant

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
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
# Pydantic models
# ---------------------------------------------------------------------------


class EntitlementDocumentResponse(CamelCaseModel):
    """Single entitlement configuration document."""

    config_type: str
    config_key: str
    value: dict[str, Any]
    version: int
    updated_at: str
    updated_by: str | None = None


class EntitlementListResponse(CamelCaseModel):
    """List of all entitlement configuration documents."""

    documents: list[EntitlementDocumentResponse]
    total: int


class EntitlementWriteRequest(CamelCaseModel):
    """Request body for writing an entitlement configuration document."""

    value: dict[str, Any] = Field(
        ..., description="Configuration payload (tier configs, pricing, gates, etc.)",
    )
    change_reason: str = Field(
        default="",
        description="Optional reason for this change (SPEC-1828 audit trail)",
    )


class EntitlementWriteResponse(CamelCaseModel):
    """Response after writing an entitlement configuration document."""

    config_type: str
    config_key: str
    version: int
    updated_at: str
    cache_invalidated: bool = False


class EntitlementDiffEntry(CamelCaseModel):
    """Single diff entry comparing current vs frozen value."""

    config_key: str
    has_live_doc: bool
    frozen_keys: list[str] = Field(default_factory=list)
    live_keys: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)


class EntitlementDiffResponse(CamelCaseModel):
    """Comparison of live Cosmos documents vs frozen fallback."""

    entries: list[EntitlementDiffEntry]
    total_checked: int


class FeatureFlagEntry(CamelCaseModel):
    """A single feature flag definition."""

    name: str
    enabled: bool = True
    scope: str = Field(
        default="global",
        description="Flag scope: global, per_tier, or per_tenant",
    )
    tiers: list[str] | None = Field(
        default=None,
        description="Tiers where flag is enabled (when scope=per_tier)",
    )
    tenant_ids: list[str] | None = Field(
        default=None,
        description="Tenant IDs where flag is enabled (when scope=per_tenant)",
    )
    description: str = ""


class FeatureFlagsDocument(CamelCaseModel):
    """The full feature flags document."""

    flags: dict[str, FeatureFlagEntry] = Field(default_factory=dict)


class FeatureFlagsResponse(CamelCaseModel):
    """Response from reading feature flags."""

    flags: dict[str, FeatureFlagEntry] = Field(default_factory=dict)
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class FeatureFlagEvalResult(CamelCaseModel):
    """Result of evaluating a feature flag for a specific tenant."""

    flag_name: str
    enabled: bool
    reason: str


# ---------------------------------------------------------------------------
# Helper: get PlatformConfigRepository
# ---------------------------------------------------------------------------


def _get_platform_repo():
    """Get the PlatformConfigRepository, lazy import to avoid circular deps."""
    from src.multi_tenant.repositories.platform import PlatformConfigRepository
    return PlatformConfigRepository()


# Known entitlement config types and their valid keys
_ENTITLEMENT_CONFIG_TYPES: dict[str, str] = {
    # config_key → config_type mapping
    "all_tiers": "tier_config",
    "pricing": "entitlements",
    "pack_pricing": "entitlements",
    "sla_targets": "entitlements",
    "website_limits": "entitlements",
    "integration_gates": "entitlements",
    "field_gates": "entitlements",
    "global_config": "entitlements",
}


def _resolve_config_type(config_key: str) -> str:
    """Resolve config_key to its config_type partition key."""
    ct = _ENTITLEMENT_CONFIG_TYPES.get(config_key)
    if ct is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown entitlement config_key '{config_key}'. "
            f"Valid keys: {sorted(_ENTITLEMENT_CONFIG_TYPES.keys())}",
        )
    return ct


# ---------------------------------------------------------------------------
# Entitlement CRUD endpoints (SPEC-1816 / WI-1416)
# ---------------------------------------------------------------------------


@router.get(
    "/entitlements",
    response_model=EntitlementListResponse,
    summary="List all entitlement configuration documents (SPEC-1816)",
    description=(
        "Returns all entitlement documents from platform_config. "
        "Includes tier configs, pricing, gates, SLA targets, etc."
    ),
    status_code=200,
)
async def list_entitlements() -> EntitlementListResponse:
    """List all entitlement configuration documents."""
    repo = _get_platform_repo()

    documents: list[EntitlementDocumentResponse] = []

    for config_key, config_type in _ENTITLEMENT_CONFIG_TYPES.items():
        doc = await repo.get_config(config_type, config_key)
        if doc is not None:
            documents.append(EntitlementDocumentResponse(
                config_type=doc.get("config_type", config_type),
                config_key=doc.get("config_key", config_key),
                value=doc.get("value", {}),
                version=doc.get("version", 1),
                updated_at=doc.get("updated_at", ""),
                updated_by=doc.get("updated_by"),
            ))

    return EntitlementListResponse(documents=documents, total=len(documents))


@router.get(
    "/entitlements/diff",
    response_model=EntitlementDiffResponse,
    summary="Compare live entitlements vs frozen fallback",
    description=(
        "Shows which entitlement documents exist in Cosmos vs the frozen "
        "fallback compiled into the codebase. Useful for verifying that "
        "seed_entitlements.py has been run and all documents are present."
    ),
    status_code=200,
)
async def diff_entitlements() -> EntitlementDiffResponse:
    """Compare live Cosmos documents against frozen fallback."""
    from src.multi_tenant.entitlement_service import FROZEN_ENTITLEMENTS

    repo = _get_platform_repo()
    entries: list[EntitlementDiffEntry] = []

    # Map frozen keys to their config_key equivalents
    frozen_map: dict[str, dict[str, Any]] = {
        "all_tiers": FROZEN_ENTITLEMENTS.get("tiers", {}),
        "pricing": FROZEN_ENTITLEMENTS.get("pricing", {}),
        "pack_pricing": FROZEN_ENTITLEMENTS.get("pack_pricing", {}),
        "sla_targets": FROZEN_ENTITLEMENTS.get("sla_targets", {}),
        "website_limits": FROZEN_ENTITLEMENTS.get("website_limits", {}),
        "integration_gates": FROZEN_ENTITLEMENTS.get("integration_gates", {}),
        "field_gates": FROZEN_ENTITLEMENTS.get("field_gates", {}),
        "global_config": FROZEN_ENTITLEMENTS.get("global_config", {}),
    }

    for config_key, config_type in _ENTITLEMENT_CONFIG_TYPES.items():
        doc = await repo.get_config(config_type, config_key)
        live_value = doc.get("value", {}) if doc else {}
        frozen_value = frozen_map.get(config_key, {})

        frozen_keys = sorted(frozen_value.keys()) if isinstance(frozen_value, dict) else []
        live_keys = sorted(live_value.keys()) if isinstance(live_value, dict) else []

        differences: list[str] = []
        if not doc:
            differences.append("No live document — using frozen fallback only")
        elif frozen_keys != live_keys:
            added = set(live_keys) - set(frozen_keys)
            removed = set(frozen_keys) - set(live_keys)
            if added:
                differences.append(f"Keys added in live: {sorted(added)}")
            if removed:
                differences.append(f"Keys missing from live: {sorted(removed)}")

        entries.append(EntitlementDiffEntry(
            config_key=config_key,
            has_live_doc=doc is not None,
            frozen_keys=frozen_keys,
            live_keys=live_keys,
            differences=differences,
        ))

    return EntitlementDiffResponse(entries=entries, total_checked=len(entries))


@router.get(
    "/entitlements/history",
    summary="Entitlement change audit history",
    description=(
        "Returns audit log entries for entitlement configuration changes. "
        "Uses the platform audit log (event_type = CONFIG_CHANGE, "
        "action = entitlement_*)."
    ),
    status_code=200,
)
async def entitlement_history(
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
) -> dict[str, Any]:
    """Get audit trail of entitlement configuration changes."""
    from src.multi_tenant.repositories.platform import AuditLogRepository

    audit_repo = AuditLogRepository()

    # Query audit log for entitlement changes (cross-partition)
    query = (
        "SELECT * FROM c "
        "WHERE c.event_type = @event_type "
        "AND STARTSWITH(c.payload.action, 'entitlement_') "
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
                "config_key": payload.get("config_key"),
                "actor": item.get("actor"),
                "timestamp": item.get("timestamp"),
                "previous_version": payload.get("previous_version"),
                "new_version": payload.get("new_version"),
                "change_reason": payload.get("change_reason", ""),
                "diff_summary": payload.get("diff_summary", []),
            })
    except Exception:
        logger.warning("Audit log query failed for entitlement history", exc_info=True)

    return {"entries": items, "total": len(items), "skip": skip, "limit": limit}


@router.get(
    "/entitlements/{config_key}",
    response_model=EntitlementDocumentResponse,
    summary="Read a single entitlement document (SPEC-1816)",
    description="Read a specific entitlement configuration document by key.",
    responses={
        400: {"description": "Unknown config_key"},
        404: {"description": "Document not found in Cosmos (frozen fallback available)"},
    },
    status_code=200,
)
async def get_entitlement(config_key: str) -> EntitlementDocumentResponse:
    """Read a single entitlement configuration document."""
    config_type = _resolve_config_type(config_key)
    repo = _get_platform_repo()

    doc = await repo.get_config(config_type, config_key)
    if doc is None:
        # Return frozen fallback info in error
        raise HTTPException(
            status_code=404,
            detail=f"No live document for '{config_key}' in Cosmos. "
            "The system is using frozen fallback values. "
            "Run seed_entitlements.py to populate.",
        )

    return EntitlementDocumentResponse(
        config_type=doc.get("config_type", config_type),
        config_key=doc.get("config_key", config_key),
        value=doc.get("value", {}),
        version=doc.get("version", 1),
        updated_at=doc.get("updated_at", ""),
        updated_by=doc.get("updated_by"),
    )


@router.put(
    "/entitlements/{config_key}",
    response_model=EntitlementWriteResponse,
    summary="Write an entitlement document (SPEC-1816)",
    description=(
        "Create or update an entitlement configuration document. "
        "Increments the version number. Invalidates both in-process "
        "and Redis caches so all replicas pick up the change."
    ),
    responses={
        400: {"description": "Unknown config_key"},
    },
    status_code=200,
)
async def put_entitlement(
    config_key: str,
    body: EntitlementWriteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EntitlementWriteResponse:
    """Write an entitlement configuration document.

    Upserts into Cosmos, increments version, and invalidates caches.
    """
    config_type = _resolve_config_type(config_key)
    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing to get current version
    existing = await repo.get_config(config_type, config_key)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    # Build and upsert the document
    doc = PlatformConfigDocument(
        id=f"{config_type}:{config_key}",
        config_type=config_type,
        config_key=config_key,
        value=body.value,
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
        svc.invalidate_cache(config_key)
        await svc.invalidate_redis(config_key)
        cache_invalidated = True
    except Exception:
        logger.warning("Cache invalidation failed for %s", config_key, exc_info=True)

    # Audit log (SPEC-1828: old/new value snapshots + change reason)
    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository
        audit = AuditLogRepository()

        # Compute key-level diff for the audit trail
        old_keys = sorted(existing.get("value", {}).keys()) if existing else []
        new_keys = sorted(body.value.keys())
        diff_summary: list[str] = []
        if set(old_keys) != set(new_keys):
            added = sorted(set(new_keys) - set(old_keys))
            removed = sorted(set(old_keys) - set(new_keys))
            if added:
                diff_summary.append(f"added: {added}")
            if removed:
                diff_summary.append(f"removed: {removed}")

        await audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            tenant_id="__platform__",
            actor=actor,
            actor_type="admin",
            payload={
                "action": "entitlement_updated",
                "config_type": config_type,
                "config_key": config_key,
                "previous_version": previous_version,
                "new_version": new_version,
                "change_reason": body.change_reason,
                "old_keys": old_keys,
                "new_keys": new_keys,
                "diff_summary": diff_summary,
            },
        )
    except Exception:
        logger.warning("Audit log failed for entitlement write", exc_info=True)

    logger.info(
        "Entitlement updated: %s:%s v%d→v%d (by %s)%s",
        config_type, config_key, previous_version, new_version, actor,
        f" reason={body.change_reason}" if body.change_reason else "",
    )

    return EntitlementWriteResponse(
        config_type=config_type,
        config_key=config_key,
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )


# ---------------------------------------------------------------------------
# Feature Flag endpoints (SPEC-1824 / WI-1422)
# ---------------------------------------------------------------------------

_FF_CONFIG_TYPE = "feature_flags"
_FF_CONFIG_KEY = "flags"


async def _read_flags_doc() -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Read the feature flags document from Cosmos.

    Returns (raw_doc, flags_dict). raw_doc is None if not found.
    """
    repo = _get_platform_repo()
    doc = await repo.get_config(_FF_CONFIG_TYPE, _FF_CONFIG_KEY)
    if doc is None:
        return None, {}
    return doc, doc.get("value", {})


@router.get(
    "/feature-flags",
    response_model=FeatureFlagsResponse,
    summary="List all feature flags (SPEC-1824)",
    description="Read the current feature flag configuration.",
    status_code=200,
)
async def list_feature_flags() -> FeatureFlagsResponse:
    """List all feature flags."""
    doc, flags_value = await _read_flags_doc()

    # Convert raw dicts to FeatureFlagEntry
    flags: dict[str, FeatureFlagEntry] = {}
    for name, entry in flags_value.items():
        if isinstance(entry, dict):
            flags[name] = FeatureFlagEntry(
                name=name,
                enabled=entry.get("enabled", True),
                scope=entry.get("scope", "global"),
                tiers=entry.get("tiers"),
                tenant_ids=entry.get("tenant_ids"),
                description=entry.get("description", ""),
            )

    return FeatureFlagsResponse(
        flags=flags,
        version=doc.get("version", 0) if doc else 0,
        updated_at=doc.get("updated_at") if doc else None,
        updated_by=doc.get("updated_by") if doc else None,
    )


@router.put(
    "/feature-flags",
    response_model=EntitlementWriteResponse,
    summary="Write feature flags document (SPEC-1824)",
    description=(
        "Create or update the feature flags configuration. "
        "Replaces the entire flags document. Invalidates caches."
    ),
    status_code=200,
)
async def put_feature_flags(
    body: FeatureFlagsDocument,
    ctx: TenantContext = Depends(get_tenant_context),
) -> EntitlementWriteResponse:
    """Write the feature flags document."""
    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing
    existing = await repo.get_config(_FF_CONFIG_TYPE, _FF_CONFIG_KEY)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    # Serialize flags to plain dicts for Cosmos storage
    flags_payload: dict[str, Any] = {}
    for name, entry in body.flags.items():
        flags_payload[name] = entry.model_dump(exclude_none=True)

    doc = PlatformConfigDocument(
        id=f"{_FF_CONFIG_TYPE}:{_FF_CONFIG_KEY}",
        config_type=_FF_CONFIG_TYPE,
        config_key=_FF_CONFIG_KEY,
        value=flags_payload,
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
        svc.invalidate_cache(_FF_CONFIG_KEY)
        await svc.invalidate_redis(_FF_CONFIG_KEY)
        cache_invalidated = True
    except Exception:
        logger.warning("Cache invalidation failed for feature flags", exc_info=True)

    # Audit log
    try:
        from src.multi_tenant.repositories.platform import AuditLogRepository
        audit = AuditLogRepository()
        await audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            tenant_id="__platform__",
            actor=actor,
            actor_type="admin",
            payload={
                "action": "entitlement_feature_flags_updated",
                "config_key": _FF_CONFIG_KEY,
                "previous_version": previous_version,
                "new_version": new_version,
                "flag_count": len(flags_payload),
            },
        )
    except Exception:
        logger.warning("Audit log failed for feature flag write", exc_info=True)

    logger.info(
        "Feature flags updated: v%d→v%d, %d flags (by %s)",
        previous_version, new_version, len(flags_payload), actor,
    )

    return EntitlementWriteResponse(
        config_type=_FF_CONFIG_TYPE,
        config_key=_FF_CONFIG_KEY,
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )


@router.get(
    "/feature-flags/evaluate",
    response_model=FeatureFlagEvalResult,
    summary="Evaluate a feature flag for a tenant (SPEC-1824)",
    description=(
        "Evaluate whether a specific feature flag is enabled for a given "
        "tenant. Checks global → per_tier → per_tenant scoping."
    ),
    responses={
        404: {"description": "Flag not found"},
    },
    status_code=200,
)
async def evaluate_feature_flag(
    flag_name: str = Query(..., description="Feature flag name"),
    tenant_id: str = Query(..., description="Tenant ID to evaluate for"),
    tier: str = Query("starter", description="Tenant's current tier"),
) -> FeatureFlagEvalResult:
    """Evaluate a feature flag for a specific tenant."""
    _, flags_value = await _read_flags_doc()

    flag_data = flags_value.get(flag_name)
    if flag_data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Feature flag '{flag_name}' not found",
        )

    if not isinstance(flag_data, dict):
        return FeatureFlagEvalResult(
            flag_name=flag_name, enabled=False, reason="Invalid flag data",
        )

    # Master kill switch
    if not flag_data.get("enabled", True):
        return FeatureFlagEvalResult(
            flag_name=flag_name, enabled=False, reason="Flag globally disabled",
        )

    scope = flag_data.get("scope", "global")

    if scope == "global":
        return FeatureFlagEvalResult(
            flag_name=flag_name, enabled=True, reason="Global scope — enabled for all",
        )

    if scope == "per_tier":
        allowed_tiers = flag_data.get("tiers", [])
        if tier in allowed_tiers:
            return FeatureFlagEvalResult(
                flag_name=flag_name, enabled=True,
                reason=f"Tier '{tier}' is in allowed tiers",
            )
        return FeatureFlagEvalResult(
            flag_name=flag_name, enabled=False,
            reason=f"Tier '{tier}' not in allowed tiers: {allowed_tiers}",
        )

    if scope == "per_tenant":
        allowed_tenants = flag_data.get("tenant_ids", [])
        if tenant_id in allowed_tenants:
            return FeatureFlagEvalResult(
                flag_name=flag_name, enabled=True,
                reason=f"Tenant '{tenant_id[:12]}...' is in allowed tenants",
            )
        return FeatureFlagEvalResult(
            flag_name=flag_name, enabled=False,
            reason=f"Tenant not in allowed tenant list ({len(allowed_tenants)} tenants)",
        )

    return FeatureFlagEvalResult(
        flag_name=flag_name, enabled=False, reason=f"Unknown scope: {scope}",
    )
