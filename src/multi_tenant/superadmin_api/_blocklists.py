"""Superadmin API -- Allow/block list management + maintenance mode.

Domain sub-module for SPEC-1820 (Allow/Block List Management) and
SPEC-1829 (Maintenance Mode). Endpoints are registered on the shared
router from _monolith.

Allow/Block Lists:
  GET  /blocklists              — List all active lists
  GET  /blocklists/{list_type}  — Read a specific list (ip, email_domain, tenant, user_agent)
  PUT  /blocklists/{list_type}  — Write a list
  POST /blocklists/{list_type}/check — Check if a value is blocked/allowed

Maintenance Mode:
  GET  /maintenance             — Read current maintenance state
  PUT  /maintenance             — Enable/disable/schedule maintenance mode

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
# Helper
# ---------------------------------------------------------------------------


def _get_platform_repo():
    """Get the PlatformConfigRepository, lazy import to avoid circular deps."""
    from src.multi_tenant.repositories.platform import PlatformConfigRepository
    return PlatformConfigRepository()


# ---------------------------------------------------------------------------
# Allow/block list models (SPEC-1820)
# ---------------------------------------------------------------------------

VALID_LIST_TYPES = {"ip", "email_domain", "tenant", "user_agent"}

# Config type and key for each list
_BL_CONFIG_TYPE = "blocklists"


class BlocklistEntry(CamelCaseModel):
    """A single entry in a block/allow list."""

    value: str = Field(..., min_length=1, description="The value to match (IP, domain, tenant ID, UA pattern)")
    action: str = Field(default="block", description="Action: 'block' or 'allow'")
    reason: str = Field(default="", description="Human-readable reason for this entry")
    added_by: str = Field(default="spa-console", description="Who added this entry")
    added_at: str = Field(default="", description="When this entry was added (ISO 8601)")


class BlocklistDocument(CamelCaseModel):
    """Full blocklist document for a specific list type."""

    entries: list[BlocklistEntry] = Field(default_factory=list)
    default_action: str = Field(
        default="allow",
        description="Default action when no entry matches: 'allow' or 'block'",
    )


class BlocklistResponse(CamelCaseModel):
    """Response from reading a blocklist."""

    list_type: str
    entries: list[BlocklistEntry] = Field(default_factory=list)
    default_action: str = "allow"
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class BlocklistListResponse(CamelCaseModel):
    """Response listing all blocklists."""

    lists: list[BlocklistResponse]


class BlocklistWriteResponse(CamelCaseModel):
    """Response after writing a blocklist."""

    list_type: str
    entry_count: int
    version: int
    updated_at: str
    cache_invalidated: bool = False


class BlocklistCheckRequest(CamelCaseModel):
    """Request to check if a value is blocked/allowed."""

    value: str = Field(..., min_length=1, description="Value to check")


class BlocklistCheckResponse(CamelCaseModel):
    """Response from checking a value against a blocklist."""

    list_type: str
    value: str
    action: str = Field(description="Result: 'block' or 'allow'")
    matched_entry: str | None = Field(
        default=None,
        description="The entry that matched (if any)",
    )
    reason: str = ""


# ---------------------------------------------------------------------------
# Blocklist enforcement helper (used by middleware)
# ---------------------------------------------------------------------------


def check_blocklist(list_data: dict[str, Any], value: str) -> tuple[str, str | None, str]:
    """Evaluate a value against a blocklist.

    Args:
        list_data: The blocklist document value dict with 'entries' and 'default_action'.
        value: The value to check (IP, domain, tenant ID, UA string).

    Returns:
        (action, matched_entry_value, reason) — action is 'block' or 'allow'.
    """
    entries = list_data.get("entries", [])
    default_action = list_data.get("default_action", "allow")
    value_lower = value.lower()

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        entry_value = entry.get("value", "").lower()
        if not entry_value:
            continue

        # Support prefix matching for IPs (CIDR-like: "192.168." matches "192.168.1.1")
        # Support suffix matching for domains (".example.com" matches "test.example.com")
        # Exact match otherwise
        matched = False
        if entry_value.endswith(".") or entry_value.endswith("/"):
            # Prefix match (IP ranges, path prefixes)
            matched = value_lower.startswith(entry_value)
        elif entry_value.startswith("."):
            # Suffix match (domain wildcards)
            matched = value_lower.endswith(entry_value) or value_lower == entry_value[1:]
        else:
            # Exact match
            matched = value_lower == entry_value

        if matched:
            return (
                entry.get("action", "block"),
                entry.get("value"),
                entry.get("reason", ""),
            )

    return default_action, None, f"Default action: {default_action}"


# ---------------------------------------------------------------------------
# Blocklist CRUD endpoints (SPEC-1820 / WI-1418)
# ---------------------------------------------------------------------------


def _validate_list_type(list_type: str) -> None:
    if list_type not in VALID_LIST_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid list_type '{list_type}'. Valid types: {sorted(VALID_LIST_TYPES)}",
        )


@router.get(
    "/blocklists",
    response_model=BlocklistListResponse,
    summary="List all block/allow lists (SPEC-1820)",
    description="Returns all configured block/allow lists (IP, email domain, tenant, user agent).",
    status_code=200,
)
async def list_blocklists() -> BlocklistListResponse:
    """List all block/allow lists."""
    repo = _get_platform_repo()
    lists: list[BlocklistResponse] = []

    for lt in sorted(VALID_LIST_TYPES):
        doc = await repo.get_config(_BL_CONFIG_TYPE, lt)
        if doc is not None:
            value = doc.get("value", {})
            entries = [
                BlocklistEntry(**e) if isinstance(e, dict) else e
                for e in value.get("entries", [])
            ]
            lists.append(BlocklistResponse(
                list_type=lt,
                entries=entries,
                default_action=value.get("default_action", "allow"),
                version=doc.get("version", 1),
                updated_at=doc.get("updated_at"),
                updated_by=doc.get("updated_by"),
            ))
        else:
            lists.append(BlocklistResponse(list_type=lt))

    return BlocklistListResponse(lists=lists)


@router.get(
    "/blocklists/{list_type}",
    response_model=BlocklistResponse,
    summary="Read a specific block/allow list (SPEC-1820)",
    responses={400: {"description": "Invalid list type"}},
    status_code=200,
)
async def get_blocklist(list_type: str) -> BlocklistResponse:
    """Read a specific block/allow list."""
    _validate_list_type(list_type)
    repo = _get_platform_repo()

    doc = await repo.get_config(_BL_CONFIG_TYPE, list_type)
    if doc is None:
        return BlocklistResponse(list_type=list_type)

    value = doc.get("value", {})
    entries = [
        BlocklistEntry(**e) if isinstance(e, dict) else e
        for e in value.get("entries", [])
    ]
    return BlocklistResponse(
        list_type=list_type,
        entries=entries,
        default_action=value.get("default_action", "allow"),
        version=doc.get("version", 1),
        updated_at=doc.get("updated_at"),
        updated_by=doc.get("updated_by"),
    )


@router.put(
    "/blocklists/{list_type}",
    response_model=BlocklistWriteResponse,
    summary="Write a block/allow list (SPEC-1820)",
    description=(
        "Create or update a block/allow list. Replaces the entire list. "
        "Invalidates caches so enforcement takes effect immediately."
    ),
    responses={400: {"description": "Invalid list type"}},
    status_code=200,
)
async def put_blocklist(
    list_type: str,
    body: BlocklistDocument,
    ctx: TenantContext = Depends(get_tenant_context),
) -> BlocklistWriteResponse:
    """Write a block/allow list."""
    _validate_list_type(list_type)
    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Stamp added_at on entries that don't have it
    for entry in body.entries:
        if not entry.added_at:
            entry.added_at = now_iso
        if entry.added_by == "spa-console":
            entry.added_by = actor

    # Read existing for versioning
    existing = await repo.get_config(_BL_CONFIG_TYPE, list_type)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    # Serialize entries to dicts
    payload = {
        "entries": [e.model_dump() for e in body.entries],
        "default_action": body.default_action,
    }

    doc = PlatformConfigDocument(
        id=f"{_BL_CONFIG_TYPE}:{list_type}",
        config_type=_BL_CONFIG_TYPE,
        config_key=list_type,
        value=payload,
        version=new_version,
        updated_at=now_iso,
        updated_by=actor,
    )
    await repo.set_config(doc)

    # Invalidate blocklist cache
    cache_invalidated = False
    try:
        _invalidate_blocklist_cache(list_type)
        cache_invalidated = True
    except Exception:
        logger.warning("Blocklist cache invalidation failed", exc_info=True)

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
                "action": "blocklist_updated",
                "list_type": list_type,
                "entry_count": len(body.entries),
                "previous_version": previous_version,
                "new_version": new_version,
            },
        )
    except Exception:
        logger.warning("Audit log failed for blocklist write", exc_info=True)

    logger.info(
        "Blocklist updated: %s v%d→v%d, %d entries (by %s)",
        list_type, previous_version, new_version, len(body.entries), actor,
    )

    return BlocklistWriteResponse(
        list_type=list_type,
        entry_count=len(body.entries),
        version=new_version,
        updated_at=now_iso,
        cache_invalidated=cache_invalidated,
    )


@router.post(
    "/blocklists/{list_type}/check",
    response_model=BlocklistCheckResponse,
    summary="Check a value against a block/allow list (SPEC-1820)",
    description="Test whether a specific value would be blocked or allowed.",
    responses={400: {"description": "Invalid list type"}},
    status_code=200,
)
async def check_blocklist_value(
    list_type: str,
    body: BlocklistCheckRequest,
) -> BlocklistCheckResponse:
    """Check if a value is blocked or allowed."""
    _validate_list_type(list_type)
    repo = _get_platform_repo()

    doc = await repo.get_config(_BL_CONFIG_TYPE, list_type)
    list_data = doc.get("value", {}) if doc else {}

    action, matched, reason = check_blocklist(list_data, body.value)

    return BlocklistCheckResponse(
        list_type=list_type,
        value=body.value,
        action=action,
        matched_entry=matched,
        reason=reason,
    )


# ---------------------------------------------------------------------------
# Blocklist cache (in-process, for middleware hot-path)
# ---------------------------------------------------------------------------

import time

_BLOCKLIST_CACHE_TTL = 30  # seconds — shorter than entitlements because security-critical
_blocklist_cache: dict[str, tuple[dict[str, Any], float]] = {}


def get_cached_blocklist(list_type: str) -> dict[str, Any] | None:
    """Get a cached blocklist for middleware use. Returns None on miss."""
    entry = _blocklist_cache.get(list_type)
    if entry is None:
        return None
    data, expires_at = entry
    if time.monotonic() > expires_at:
        _blocklist_cache.pop(list_type, None)
        return None
    return data


def set_cached_blocklist(list_type: str, data: dict[str, Any]) -> None:
    """Cache a blocklist for middleware use."""
    _blocklist_cache[list_type] = (data, time.monotonic() + _BLOCKLIST_CACHE_TTL)


def _invalidate_blocklist_cache(list_type: str | None = None) -> None:
    """Invalidate blocklist cache entries."""
    if list_type is None:
        _blocklist_cache.clear()
    else:
        _blocklist_cache.pop(list_type, None)


# ---------------------------------------------------------------------------
# Maintenance Mode (SPEC-1829 / WI-1423)
# ---------------------------------------------------------------------------

_MM_CONFIG_TYPE = "maintenance"
_MM_CONFIG_KEY = "mode"


class MaintenanceState(CamelCaseModel):
    """Current maintenance mode state."""

    enabled: bool = False
    message: str = Field(
        default="Service is temporarily unavailable for maintenance. Please try again shortly.",
        description="Message shown to clients during maintenance",
    )
    retry_after_seconds: int = Field(
        default=300,
        ge=60,
        le=86400,
        description="Retry-After header value in seconds (60-86400)",
    )
    scheduled_start: str | None = Field(
        default=None,
        description="ISO 8601 timestamp for scheduled maintenance start (optional)",
    )
    scheduled_end: str | None = Field(
        default=None,
        description="ISO 8601 timestamp for scheduled maintenance end (optional)",
    )
    exempt_ips: list[str] = Field(
        default_factory=list,
        description="IP addresses exempt from maintenance mode (for admin access)",
    )


class MaintenanceResponse(CamelCaseModel):
    """Full maintenance mode response including metadata."""

    state: MaintenanceState
    is_active: bool = Field(
        description="Whether maintenance mode is currently active "
        "(considers enabled flag + schedule window)",
    )
    version: int = 0
    updated_at: str | None = None
    updated_by: str | None = None


class MaintenanceWriteResponse(CamelCaseModel):
    """Response after updating maintenance mode."""

    is_active: bool
    version: int
    updated_at: str


def is_maintenance_active(state: MaintenanceState) -> bool:
    """Determine if maintenance mode is currently active.

    Considers: enabled flag, scheduled_start, and scheduled_end.
    """
    if not state.enabled:
        return False

    now = datetime.now(timezone.utc)

    # If scheduled_start is set and in the future, not yet active
    if state.scheduled_start:
        try:
            start = datetime.fromisoformat(state.scheduled_start)
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            if now < start:
                return False
        except (ValueError, TypeError):
            pass

    # If scheduled_end is set and in the past, no longer active
    if state.scheduled_end:
        try:
            end = datetime.fromisoformat(state.scheduled_end)
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            if now > end:
                return False
        except (ValueError, TypeError):
            pass

    return True


@router.get(
    "/maintenance",
    response_model=MaintenanceResponse,
    summary="Read maintenance mode state (SPEC-1829)",
    description="Returns the current maintenance mode configuration and whether it is actively enforced.",
    status_code=200,
)
async def get_maintenance() -> MaintenanceResponse:
    """Read maintenance mode state."""
    repo = _get_platform_repo()
    doc = await repo.get_config(_MM_CONFIG_TYPE, _MM_CONFIG_KEY)

    if doc is None:
        state = MaintenanceState()
        return MaintenanceResponse(state=state, is_active=False)

    value = doc.get("value", {})
    state = MaintenanceState(**value)

    return MaintenanceResponse(
        state=state,
        is_active=is_maintenance_active(state),
        version=doc.get("version", 1),
        updated_at=doc.get("updated_at"),
        updated_by=doc.get("updated_by"),
    )


@router.put(
    "/maintenance",
    response_model=MaintenanceWriteResponse,
    summary="Set maintenance mode (SPEC-1829)",
    description=(
        "Enable, disable, or schedule maintenance mode. When active, all "
        "non-health endpoints return 503 with Retry-After header."
    ),
    status_code=200,
)
async def put_maintenance(
    body: MaintenanceState,
    ctx: TenantContext = Depends(get_tenant_context),
) -> MaintenanceWriteResponse:
    """Enable, disable, or schedule maintenance mode."""
    repo = _get_platform_repo()
    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.team_member_email or "spa-console"

    # Read existing for versioning
    existing = await repo.get_config(_MM_CONFIG_TYPE, _MM_CONFIG_KEY)
    previous_version = existing.get("version", 0) if existing else 0
    new_version = previous_version + 1

    doc = PlatformConfigDocument(
        id=f"{_MM_CONFIG_TYPE}:{_MM_CONFIG_KEY}",
        config_type=_MM_CONFIG_TYPE,
        config_key=_MM_CONFIG_KEY,
        value=body.model_dump(),
        version=new_version,
        updated_at=now_iso,
        updated_by=actor,
    )
    await repo.set_config(doc)

    active = is_maintenance_active(body)

    # Invalidate maintenance cache
    _invalidate_maintenance_cache()

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
                "action": "maintenance_mode_updated",
                "enabled": body.enabled,
                "is_active": active,
                "scheduled_start": body.scheduled_start,
                "scheduled_end": body.scheduled_end,
                "previous_version": previous_version,
                "new_version": new_version,
            },
        )
    except Exception:
        logger.warning("Audit log failed for maintenance mode", exc_info=True)

    logger.info(
        "Maintenance mode %s: active=%s scheduled=%s→%s (by %s)",
        "enabled" if body.enabled else "disabled",
        active,
        body.scheduled_start or "now",
        body.scheduled_end or "indefinite",
        actor,
    )

    return MaintenanceWriteResponse(
        is_active=active,
        version=new_version,
        updated_at=now_iso,
    )


# ---------------------------------------------------------------------------
# Maintenance mode cache (in-process, for middleware hot-path)
# ---------------------------------------------------------------------------

_MAINTENANCE_CACHE_TTL = 10  # seconds — very short for fast toggling
_maintenance_cache: tuple[MaintenanceState | None, float] = (None, 0.0)


def get_cached_maintenance_state() -> MaintenanceState | None:
    """Get cached maintenance state for middleware use."""
    state, expires_at = _maintenance_cache
    if state is None or time.monotonic() > expires_at:
        return None
    return state


def set_cached_maintenance_state(state: MaintenanceState) -> None:
    """Cache maintenance state for middleware use."""
    global _maintenance_cache
    _maintenance_cache = (state, time.monotonic() + _MAINTENANCE_CACHE_TTL)


def _invalidate_maintenance_cache() -> None:
    """Invalidate maintenance state cache."""
    global _maintenance_cache
    _maintenance_cache = (None, 0.0)
