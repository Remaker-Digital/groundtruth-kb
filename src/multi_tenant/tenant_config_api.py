"""Configuration API — RESTful endpoints for tenant configuration management.

Work Item #65 (Decision #22): Layer 3 of the 5-layer tenant configuration
system — RESTful endpoints wrapping TenantConfigProcessor + ActivationService.

Save → Activate model: config changes are saved as drafts and only go live
when explicitly activated.  All four configuration domains (Agent Config,
Quick Actions, Widget Config, Knowledge Base validation) activate atomically.

Endpoints:
    GET    /api/config              — Current resolved config (active or draft)
    PUT    /api/config              — Save config changes to draft
    POST   /api/config/validate     — Dry-run validation (no persist)
    POST   /api/config/reset        — Reset to tier defaults (creates draft)
    GET    /api/config/diff         — Overrides vs. tier defaults
    GET    /api/config/schema       — Field metadata for UI rendering
    GET    /api/config/versions     — Version history
    GET    /api/config/versions/{version} — Specific historical version
    GET    /api/config/named        — List named configurations (C3)
    POST   /api/config/named        — Save current config as named (C3)
    POST   /api/config/named/{name}/activate — Load named config as draft (C3)
    DELETE /api/config/named/{name} — Delete a named config (C3)
    GET    /api/config/widget-appearances           — List named appearances (C4)
    POST   /api/config/widget-appearances           — Save appearance as named (C4)
    POST   /api/config/widget-appearances/{name}/activate — Load appearance as draft (C4)
    DELETE /api/config/widget-appearances/{name}    — Delete appearance (C4)
    POST   /api/config/rollback     — Load previous version as draft
    GET    /api/config/activation-status  — Lightweight activation state check
    GET    /api/config/draft              — Full draft state + diff vs active
    POST   /api/config/draft/activate    — Validate and activate the draft
    POST   /api/config/draft/discard     — Discard all draft changes
    POST   /api/config/restore           — Restore previous activation snapshot

All endpoints derive tenant_id and tier from the authenticated TenantContext
— never from query parameters.  Tenant isolation is enforced at every level:
auth middleware → processor → repository.

Architecture references:
    - Decision #22: 5-layer tenant configuration management
    - Work Item #65: Configuration API
    - Work Item #64: TenantConfigProcessor (upstream dependency)
    - Work Item #63: tenant_config_schema (upstream dependency)

Dependencies:
    - tenant_config_processor.py: get_config_processor
    - activation_service.py: get_activation_service
    - tenant_config_schema.py: export_schema_for_api
    - middleware.py: get_tenant_context
    - auth.py: TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.activation_service import (
    get_activation_service,
)
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType, TenantTier
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.tenant_config_processor import (
    ConfigVersionInfo,
    NamedConfigSummary,
    get_config_processor,
)
from src.multi_tenant.tenant_config_schema import (
    export_schema_for_api,
    resolve_defaults,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ConfigUpdateRequest(BaseModel):
    """Request body for partial config update."""

    fields: dict[str, Any] = Field(
        description="Partial dict of field_name → new_value",
    )


class ConfigValidateRequest(BaseModel):
    """Request body for dry-run validation."""

    fields: dict[str, Any] = Field(
        description="Proposed field changes to validate",
    )


class ConfigRollbackRequest(BaseModel):
    """Request body for config rollback."""

    target_version: int = Field(
        description="Version number to roll back to",
        ge=0,
    )


class QuickActionForWidget(BaseModel):
    """Minimal quick action shape served to the widget."""

    id: str
    label: str
    prompt_template: str
    icon: str | None = None


class ConfigResponse(BaseModel):
    """Standard config read response."""

    tenant_id: str
    tier: str
    version: int
    config: dict[str, Any]
    from_cache: bool = False
    quick_actions: list[QuickActionForWidget] | None = None
    state: str = "active"


class ConfigUpdateResponse(BaseModel):
    """Response for config update operations."""

    success: bool
    version: int = 0
    errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)
    changes: dict[str, Any] = Field(default_factory=dict)
    resolved_config: dict[str, Any] = Field(default_factory=dict)
    state: str = "active"


class ConfigValidateResponse(BaseModel):
    """Response for dry-run validation."""

    valid: bool
    errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)
    sanitized: dict[str, Any] = Field(default_factory=dict)


class ConfigDiffResponse(BaseModel):
    """Response showing overrides vs. defaults."""

    tenant_id: str
    tier: str
    overrides: dict[str, Any] = Field(
        description="Fields differing from defaults: {field: {current, default}}",
    )
    override_count: int = 0


class ConfigSchemaResponse(BaseModel):
    """Response containing field metadata for UI rendering."""

    tier: str
    total_fields: int
    steps: list[dict[str, Any]]


class ConfigVersionListResponse(BaseModel):
    """Response listing config versions."""

    tenant_id: str
    versions: list[ConfigVersionInfo]
    total: int = 0


class ConfigRollbackResponse(BaseModel):
    """Response for rollback operations."""

    success: bool
    from_version: int = 0
    to_version: int = 0
    new_version: int = 0
    message: str = ""


class NamedConfigSaveRequest(BaseModel):
    """Request body for saving a named configuration."""

    name: str = Field(
        description="Configuration name (e.g. 'Holiday Mode', 'Sale Mode')",
        min_length=1,
        max_length=64,
    )


class NamedConfigListResponse(BaseModel):
    """Response listing named configurations."""

    tenant_id: str
    configs: list[NamedConfigSummary]
    total: int = 0


class NamedConfigDeleteResponse(BaseModel):
    """Response for named config deletion."""

    success: bool
    name: str
    message: str = ""


class ActivationStatusResponse(BaseModel):
    """Lightweight activation state for the admin banner."""

    has_pending_changes: bool
    active_version: int = 0
    active_activated_at: str | None = None
    draft_version: int | None = None
    is_configured: bool = False
    is_active: bool = False
    can_activate: bool = False


class DraftStateResponse(BaseModel):
    """Full draft state including diff vs active."""

    has_pending_changes: bool
    active_version: int = 0
    active_activated_at: str | None = None
    draft_version: int | None = None
    changed_fields: list[str] = Field(default_factory=list)
    draft_config: dict[str, Any] = Field(default_factory=dict)
    active_config: dict[str, Any] = Field(default_factory=dict)


class ActivateResponse(BaseModel):
    """Response for draft activation."""

    success: bool
    version: int = 0
    activated_at: str | None = None
    errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)


class PreflightResponse(BaseModel):
    """Pre-activation validation result (D35)."""

    can_activate: bool
    hard_errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)


class RestoreResponse(BaseModel):
    """Response for restoring previous configuration."""

    success: bool
    restored_version: int = 0
    restored_activated_at: str | None = None
    error: str | None = None


class DiscardResponse(BaseModel):
    """Response for discarding a draft."""

    success: bool
    message: str = ""


# ---------------------------------------------------------------------------
# Helper: resolve tier from TenantContext
# ---------------------------------------------------------------------------


def _resolve_tier(ctx: TenantContext) -> TenantTier:
    """Extract TenantTier from TenantContext, defaulting to STARTER."""
    if ctx.tier is not None:
        if isinstance(ctx.tier, TenantTier):
            return ctx.tier
        try:
            return TenantTier(ctx.tier)
        except ValueError:
            pass
    return TenantTier.STARTER


# ---------------------------------------------------------------------------
# Quick action resolution (WI #227 — widget page-filtered quick actions)
# ---------------------------------------------------------------------------

_quick_action_repo: Any | None = None


def configure_quick_action_serving(prefs_repo: Any) -> None:
    """Wire the config API to PreferencesRepository for quick action serving.

    Called during app startup.  When not configured, GET /api/config simply
    returns ``quick_actions: null`` (backward compatible).
    """
    global _quick_action_repo
    _quick_action_repo = prefs_repo
    logger.info("Quick action serving configured for GET /api/config")


async def _resolve_quick_actions(
    tenant_id: str,
    config: dict[str, Any],
    page_type: str,
    page_handle: str | None,
) -> list[QuickActionForWidget]:
    """Resolve quick action buttons for a specific page context.

    Priority:
      1. Specific handle match  (page_type + page_handle)
      2. Page-type-level match  (page_type, page_handle=null)
      3. "all" fallback         (page_type="all")
      4. Empty list             (no buttons)

    Only active actions are returned.  If ``widget_quick_actions_enabled``
    is False in the config, returns empty.
    """
    if _quick_action_repo is None:
        return []

    # Check global toggle
    if not config.get("widget_quick_actions_enabled", True):
        return []

    try:
        # Widget serves from active config only (not draft)
        actions = await _quick_action_repo.get_quick_actions_active(tenant_id)
        assignments = await _quick_action_repo.get_page_assignments_active(tenant_id)
    except Exception:
        logger.warning(
            "Quick action resolution failed for tenant=%s",
            tenant_id[:8], exc_info=True,
        )
        return []

    if not actions or not assignments:
        return []

    # Build action lookup (active only)
    action_map: dict[str, dict[str, Any]] = {}
    for a in actions:
        if a.get("is_active", True):
            action_map[a.get("id", "")] = a

    if not action_map:
        return []

    # Find matching assignment: specific handle > page type > "all"
    match: dict[str, Any] | None = None

    # Pass 1: exact handle match
    if page_handle:
        for asgn in assignments:
            if (
                asgn.get("page_type") == page_type
                and asgn.get("page_handle") == page_handle
            ):
                match = asgn
                break

    # Pass 2: page type (no handle)
    if match is None:
        for asgn in assignments:
            if (
                asgn.get("page_type") == page_type
                and not asgn.get("page_handle")
            ):
                match = asgn
                break

    # Pass 3: "all" fallback
    if match is None:
        for asgn in assignments:
            if asgn.get("page_type") == "all" and not asgn.get("page_handle"):
                match = asgn
                break

    if match is None:
        return []

    # Collect slot actions
    result: list[QuickActionForWidget] = []
    for slot_key in ("slot_1_action_id", "slot_2_action_id"):
        action_id = match.get(slot_key)
        if action_id and action_id in action_map:
            a = action_map[action_id]
            result.append(QuickActionForWidget(
                id=a.get("id", ""),
                label=a.get("label", ""),
                prompt_template=a.get("prompt_template", ""),
                icon=a.get("icon"),
            ))

    return result


# ---------------------------------------------------------------------------
# AI-generated greeting (widget_greeting_mode='ai_generated')
# ---------------------------------------------------------------------------

import random

# Greeting templates — varied, brand-aware, time-of-day-aware.
# Each template may use {brand}, {time_greeting}, and {page_hint}.
_GREETING_TEMPLATES = [
    "{time_greeting}! 👋 Welcome to {brand}. How can I help you today?",
    "{time_greeting}! I'm here to help with anything you need at {brand}.",
    "Hi there! 👋 Welcome to {brand}. What can I assist you with?",
    "{time_greeting}! Thanks for visiting {brand}. Ask me anything!",
    "Hey! 👋 Welcome to {brand}. I'm happy to help — just ask!",
]

_PAGE_GREETINGS: dict[str, list[str]] = {
    "product": [
        "{time_greeting}! 👋 Interested in this product? I can answer any questions you have.",
        "Hi! I can help with sizing, availability, or anything else about this product.",
    ],
    "collection": [
        "{time_greeting}! 👋 Browsing our collection? Let me help you find the perfect item.",
        "Hi there! Need help narrowing down your choices? I'm here to assist.",
    ],
    "cart": [
        "{time_greeting}! Have any questions before checkout? I'm here to help.",
        "Almost there! Let me know if you have questions about your order.",
    ],
}


def _generate_ai_greeting(
    config: dict[str, Any],
    page_type: str | None = None,
) -> str:
    """Generate a time-aware, brand-personalized greeting.

    Returns a contextual greeting string suitable for ``widget_greeting_message``.
    Uses templates (not LLM) for speed — no latency added to config fetch.
    """
    brand = config.get("brand_name") or config.get("widget_agent_display_name") or "us"
    now = datetime.now(timezone.utc)
    hour = now.hour

    if 5 <= hour < 12:
        time_greeting = "Good morning"
    elif 12 <= hour < 17:
        time_greeting = "Good afternoon"
    elif 17 <= hour < 22:
        time_greeting = "Good evening"
    else:
        time_greeting = "Hello"

    # Page-specific greetings when available
    templates = _PAGE_GREETINGS.get(page_type or "", _GREETING_TEMPLATES)
    template = random.choice(templates)

    return template.format(brand=brand, time_greeting=time_greeting)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/config", tags=["configuration"])


# ---------------------------------------------------------------------------
# 1. GET /api/config — Current resolved config
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=ConfigResponse,
    summary="Get current resolved configuration",
    description=(
        "Returns the tenant's active configuration with all inheritance applied. "
        "Pass ``state=draft`` to retrieve the draft instead (for admin editing). "
        "Optionally includes quick action buttons for the specified page context."
    ),
)
async def get_config(
    state: str | None = Query(
        None,
        description="Config state to fetch: 'draft' for pending changes, default returns active",
    ),
    page_type: str | None = Query(
        None,
        description="Page type for quick action filtering (e.g. product, collection, home)",
    ),
    page_handle: str | None = Query(
        None,
        description="Specific page handle for targeted quick action matching",
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigResponse:
    """Get the fully resolved current configuration.

    By default, returns the active (live) configuration — this is what
    the chat pipeline and widget use.

    When ``state=draft`` is provided, returns the draft configuration
    (for admin editing).  Falls back to the active config if no draft
    exists.

    When ``page_type`` is provided, quick actions assigned to that page
    are included in the response (always from active config for the widget).
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    if state == "draft":
        # Admin UI requesting draft for editing.
        # IMPORTANT: Always start from the full resolved active config and
        # overlay draft changes.  Returning only the changed fields caused
        # the admin UI to lose un-changed values (widget_key, colors, etc.)
        # which broke Installation display, embed snippets, and more (S104).
        activation_svc = get_activation_service()
        active_result = await processor.get_config(ctx.tenant_id, tier)
        draft_state = await activation_svc.get_draft_state(ctx.tenant_id, tier)
        if draft_state.has_pending_changes:
            # Merge: full active config + draft overrides
            merged_config = dict(active_result.config)
            merged_config.update(draft_state.draft_config)
            return ConfigResponse(
                tenant_id=ctx.tenant_id,
                tier=tier.value,
                version=draft_state.draft_version or 0,
                config=merged_config,
                from_cache=False,
                state="draft",
            )
        # No draft — return active as-is
        return ConfigResponse(
            tenant_id=active_result.tenant_id,
            tier=active_result.tier,
            version=active_result.version,
            config=active_result.config,
            from_cache=active_result.from_cache,
            state="active",
        )

    # Default: active config (pipeline, widget, admin)
    result = await processor.get_config(ctx.tenant_id, tier)

    # --- AI-generated greeting (widget_greeting_mode='ai_generated') ---
    # When greeting mode is 'ai_generated' and this is an active config fetch
    # (i.e., from the widget, not admin draft editing), generate a contextual
    # greeting and set it as widget_greeting_message so the widget renders it
    # without any runtime changes.
    response_config = result.config
    if response_config.get("widget_greeting_mode") == "ai_generated":
        response_config = dict(response_config)  # Don't mutate cached config
        response_config["widget_greeting_message"] = _generate_ai_greeting(
            response_config, page_type,
        )

    # --- Quick action resolution (WI #227) ---
    quick_actions: list[QuickActionForWidget] | None = None
    if page_type is not None:
        quick_actions = await _resolve_quick_actions(
            ctx.tenant_id, result.config, page_type, page_handle,
        )

    return ConfigResponse(
        tenant_id=result.tenant_id,
        tier=result.tier,
        version=result.version,
        config=response_config,
        from_cache=result.from_cache,
        quick_actions=quick_actions,
        state="active",
    )


# ---------------------------------------------------------------------------
# 2. PUT /api/config — Partial config update
# ---------------------------------------------------------------------------

@router.put(
    "",
    response_model=ConfigUpdateResponse,
    summary="Save configuration changes to draft",
    description=(
        "Saves partial configuration changes to the draft layer. Changes do "
        "NOT go live until explicitly activated via POST /draft/activate. "
        "Returns validation errors if any field fails validation or tier gating."
    ),
    responses={
        400: {"description": "No configuration fields provided"},
        422: {"description": "Validation errors in submitted fields"},
    },
)
async def update_config(
    body: ConfigUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Save configuration changes to draft.

    Accepts a dict of field_name → new_value. Only provided fields are
    changed; omitted fields retain their current values.

    Changes are saved to a draft document — the live pipeline config is
    NOT affected.  Call POST /api/config/draft/activate to promote the
    draft to active.

    Returns validation errors if any field fails validation or tier gating.
    """
    if not body.fields:
        raise HTTPException(
            status_code=400,
            detail="No configuration fields provided",
        )

    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=tier,
        changes=body.fields,
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "errors": result.errors,
                "warnings": result.warnings,
            },
        )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        errors=result.errors or [],
        warnings=result.warnings or [],
        changes=result.changes or {},
        state="draft",
    )


# ---------------------------------------------------------------------------
# 3. POST /api/config/validate — Dry-run validation
# ---------------------------------------------------------------------------

@router.post(
    "/validate",
    response_model=ConfigValidateResponse,
    summary="Validate configuration changes",
    description="Validates proposed configuration changes without persisting. Use for live preview and feedback in the merchant UI before committing.",
)
async def validate_config_endpoint(
    body: ConfigValidateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigValidateResponse:
    """Validate proposed configuration changes without persisting.

    Use this for live preview/feedback in the merchant UI before
    committing changes.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    result = await processor.validate_only(tier, body.fields)

    return ConfigValidateResponse(
        valid=result.valid,
        errors=result.errors or [],
        warnings=result.warnings or [],
        sanitized=result.sanitized or {},
    )


# ---------------------------------------------------------------------------
# 4. POST /api/config/reset — Reset to tier defaults
# ---------------------------------------------------------------------------

@router.post(
    "/reset",
    response_model=ConfigUpdateResponse,
    summary="Reset configuration to tier defaults (draft)",
    description=(
        "Creates a draft from tier defaults, discarding any existing draft. "
        "Does NOT immediately reset the live config — activate to apply."
    ),
)
async def reset_config(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Reset configuration to tier defaults (as draft).

    Creates a draft containing tier defaults.  The active (live) config
    is not affected until ``POST /api/config/draft/activate`` is called.
    """
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    result = await activation_svc.reinitialize_to_defaults(
        tenant_id=ctx.tenant_id,
        tier=tier,
        actor=actor,
    )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        changes=result.changes,
        state="draft",
    )


# ---------------------------------------------------------------------------
# 5. GET /api/config/diff — Overrides vs. defaults
# ---------------------------------------------------------------------------

@router.get(
    "/diff",
    response_model=ConfigDiffResponse,
    summary="Get config overrides vs defaults",
    description="Shows fields where the tenant's config differs from tier defaults. Useful for understanding what has been customized.",
)
async def get_config_diff(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigDiffResponse:
    """Show fields where the tenant's config differs from tier defaults.

    Useful for understanding what has been customized vs. what is at
    default values.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    diff = await processor.get_config_diff(ctx.tenant_id, tier)

    return ConfigDiffResponse(
        tenant_id=ctx.tenant_id,
        tier=tier.value,
        overrides=diff,
        override_count=len(diff),
    )




# ---------------------------------------------------------------------------
# 6. GET /api/config/schema — Full field schema for UI rendering
# ---------------------------------------------------------------------------

@router.get(
    "/schema",
    response_model=ConfigSchemaResponse,
    summary="Get configuration field schema",
    description="Returns field metadata (types, validation rules, defaults, tooltips) organized by configuration section. Fields are filtered by the tenant's tier.",
)
async def get_config_schema(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigSchemaResponse:
    """Get the configuration field schema for the tenant's tier.

    Returns field metadata (types, validation rules, defaults, tooltips,
    doc links) organized by configuration section. Used by the Merchant
    Configuration UI to render forms dynamically.

    Fields are filtered by the tenant's tier — Starter tenants don't
    see Professional/Enterprise-only fields.
    """
    tier = _resolve_tier(ctx)

    schema = export_schema_for_api(tier)

    return ConfigSchemaResponse(
        tier=schema["tier"],
        total_fields=schema["total_fields"],
        steps=schema["steps"],
    )




# ---------------------------------------------------------------------------
# 8. GET /api/config/versions — Version history
# ---------------------------------------------------------------------------

@router.get(
    "/versions",
    response_model=ConfigVersionListResponse,
    summary="List configuration versions",
    description="Returns up to 20 most recent configuration versions, newest first, with version number, timestamp, and creator.",
)
async def list_config_versions(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigVersionListResponse:
    """List configuration version history.

    Returns up to 20 most recent versions, newest first. Each entry
    includes version number, creation timestamp, creator, and whether
    it is the current active version.
    """
    processor = get_config_processor()

    versions = await processor.list_versions(ctx.tenant_id)

    return ConfigVersionListResponse(
        tenant_id=ctx.tenant_id,
        versions=versions,
        total=len(versions),
    )


# ---------------------------------------------------------------------------
# 9. GET /api/config/versions/{version} — Specific historical version
# ---------------------------------------------------------------------------

@router.get(
    "/versions/{version}",
    response_model=ConfigResponse,
    summary="Get specific configuration version",
    description="Returns the resolved configuration as it was at a specific historical version, merged with current tier defaults.",
    responses={
        404: {"description": "Configuration version not found"},
    },
)
async def get_config_version(
    version: int,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigResponse:
    """Get a specific historical configuration version.

    Returns the resolved config as it was at that version — the stored
    overrides merged with the current tier defaults.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    result = await processor.get_version(ctx.tenant_id, tier, version)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Configuration version {version} not found",
        )

    return ConfigResponse(
        tenant_id=result.tenant_id,
        tier=result.tier,
        version=result.version,
        config=result.config,
        from_cache=result.from_cache,
    )


# ---------------------------------------------------------------------------
# 10. GET /api/config/named — List named configurations (C3)
# ---------------------------------------------------------------------------

@router.get(
    "/named",
    response_model=NamedConfigListResponse,
    summary="List named configurations",
    description="Returns all named configurations for the tenant. Named configs are saved snapshots that can be activated to switch the live AI behavior.",
)
async def list_named_configs(
    ctx: TenantContext = Depends(get_tenant_context),
) -> NamedConfigListResponse:
    """List all named configurations for the tenant."""
    processor = get_config_processor()
    configs = await processor.list_named_configs(ctx.tenant_id)

    return NamedConfigListResponse(
        tenant_id=ctx.tenant_id,
        configs=configs,
        total=len(configs),
    )


# ---------------------------------------------------------------------------
# 11. POST /api/config/named — Save current config as named (C3)
# ---------------------------------------------------------------------------

@router.post(
    "/named",
    response_model=ConfigUpdateResponse,
    summary="Save configuration as named",
    description="Saves the current resolved configuration as a named snapshot. Use names like 'Holiday Mode', 'Sale Mode', etc.",
    responses={
        400: {"description": "Invalid or missing name"},
    },
)
async def save_named_config(
    body: NamedConfigSaveRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Save the current configuration as a named snapshot."""
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Configuration name is required")

    result = await processor.save_named_config(
        tenant_id=ctx.tenant_id,
        tier=tier,
        name=body.name.strip(),
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "errors": result.validation.errors,
            },
        )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        resolved_config=result.resolved_config,
    )


# ---------------------------------------------------------------------------
# 12. POST /api/config/named/{name}/activate — Activate a named config (C3)
# ---------------------------------------------------------------------------

@router.post(
    "/named/{name}/activate",
    response_model=ConfigUpdateResponse,
    summary="Load named configuration as draft",
    description=(
        "Loads a named configuration's values into the draft layer. "
        "Does NOT go live until activated via POST /draft/activate."
    ),
    responses={
        404: {"description": "Named configuration not found"},
    },
)
async def activate_named_config(
    name: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Load a named configuration as a draft.

    Retrieves the stored named config and saves its values into the
    draft layer.  The active (live) config is not affected until the
    draft is explicitly activated.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    # Retrieve the named config's stored values
    result = await processor.get_named_config_values(
        tenant_id=ctx.tenant_id,
        tier=tier,
        name=name,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Named configuration '{name}' not found",
        )

    # Save those values as a draft
    draft_result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=tier,
        changes=result,
        actor=actor,
    )

    return ConfigUpdateResponse(
        success=draft_result.success,
        version=draft_result.version,
        changes=draft_result.changes,
        state="draft",
    )


# ---------------------------------------------------------------------------
# 13. DELETE /api/config/named/{name} — Delete a named config (C3)
# ---------------------------------------------------------------------------

@router.delete(
    "/named/{name}",
    response_model=NamedConfigDeleteResponse,
    summary="Delete named configuration",
    description="Deletes a named configuration. The 'Default' configuration cannot be deleted. The underlying version history is preserved.",
    responses={
        400: {"description": "Cannot delete Default configuration"},
        404: {"description": "Named configuration not found"},
    },
)
async def delete_named_config(
    name: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> NamedConfigDeleteResponse:
    """Delete a named configuration."""
    if name.lower() == "default":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the Default configuration",
        )

    processor = get_config_processor()
    actor = _derive_actor(ctx)

    deleted = await processor.delete_named_config(
        tenant_id=ctx.tenant_id,
        name=name,
        actor=actor,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Named configuration '{name}' not found",
        )

    return NamedConfigDeleteResponse(
        success=True,
        name=name,
        message=f"Configuration '{name}' deleted",
    )


# ---------------------------------------------------------------------------
# 14. GET /api/config/widget-appearances — List named widget appearances (C4)
# ---------------------------------------------------------------------------

@router.get(
    "/widget-appearances",
    response_model=NamedConfigListResponse,
    summary="List named widget appearances",
    description="Returns all named widget appearances. These are saved snapshots of widget_* visual fields that can be switched independently from AI behavior configs.",
)
async def list_widget_appearances(
    ctx: TenantContext = Depends(get_tenant_context),
) -> NamedConfigListResponse:
    """List all named widget appearances for the tenant."""
    processor = get_config_processor()
    appearances = await processor.list_named_appearances(ctx.tenant_id)

    return NamedConfigListResponse(
        tenant_id=ctx.tenant_id,
        configs=appearances,
        total=len(appearances),
    )


# ---------------------------------------------------------------------------
# 15. POST /api/config/widget-appearances — Save current appearance as named (C4)
# ---------------------------------------------------------------------------

@router.post(
    "/widget-appearances",
    response_model=ConfigUpdateResponse,
    summary="Save widget appearance as named",
    description="Saves the current widget appearance fields as a named snapshot. Only widget_* visual/behavior fields are included.",
    responses={
        400: {"description": "Invalid or missing name"},
    },
)
async def save_widget_appearance(
    body: NamedConfigSaveRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Save the current widget appearance as a named snapshot."""
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Appearance name is required")

    result = await processor.save_named_appearance(
        tenant_id=ctx.tenant_id,
        tier=tier,
        name=body.name.strip(),
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "errors": result.validation.errors,
            },
        )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        resolved_config=result.resolved_config,
    )


# ---------------------------------------------------------------------------
# 16. POST /api/config/widget-appearances/{name}/activate (C4)
# ---------------------------------------------------------------------------

@router.post(
    "/widget-appearances/{name}/activate",
    response_model=ConfigUpdateResponse,
    summary="Load named widget appearance as draft",
    description=(
        "Loads a named widget appearance's widget_* field values into the "
        "draft layer. Does NOT go live until activated via POST /draft/activate."
    ),
    responses={
        404: {"description": "Named appearance not found"},
    },
)
async def activate_widget_appearance(
    name: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Load a named widget appearance into the draft layer.

    Retrieves the stored appearance values and saves them into the
    draft.  The active (live) config is not affected until the
    draft is explicitly activated.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    # Retrieve the named appearance's stored values
    result = await processor.get_named_appearance_values(
        tenant_id=ctx.tenant_id,
        tier=tier,
        name=name,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Named appearance '{name}' not found",
        )

    # Save those values as a draft
    draft_result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=tier,
        changes=result,
        actor=actor,
    )

    return ConfigUpdateResponse(
        success=draft_result.success,
        version=draft_result.version,
        changes=draft_result.changes,
        state="draft",
    )


# ---------------------------------------------------------------------------
# 17. DELETE /api/config/widget-appearances/{name} (C4)
# ---------------------------------------------------------------------------

@router.delete(
    "/widget-appearances/{name}",
    response_model=NamedConfigDeleteResponse,
    summary="Delete named widget appearance",
    description="Deletes a named widget appearance. The 'Default' appearance cannot be deleted.",
    responses={
        400: {"description": "Cannot delete Default appearance"},
        404: {"description": "Named appearance not found"},
    },
)
async def delete_widget_appearance(
    name: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> NamedConfigDeleteResponse:
    """Delete a named widget appearance."""
    if name.lower() == "default":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the Default appearance",
        )

    processor = get_config_processor()
    actor = _derive_actor(ctx)

    deleted = await processor.delete_named_appearance(
        tenant_id=ctx.tenant_id,
        name=name,
        actor=actor,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Named appearance '{name}' not found",
        )

    return NamedConfigDeleteResponse(
        success=True,
        name=name,
        message=f"Appearance '{name}' deleted",
    )


# ---------------------------------------------------------------------------
# 18. POST /api/config/rollback — Roll back to a previous version
# ---------------------------------------------------------------------------

@router.post(
    "/rollback",
    response_model=ConfigRollbackResponse,
    summary="Load previous version as draft",
    description=(
        "Creates a draft from the contents of a target historical version. "
        "Does NOT go live until activated via POST /draft/activate. "
        "No versions are deleted and full history is preserved."
    ),
    responses={
        404: {"description": "Target version not found"},
    },
)
async def rollback_config(
    body: ConfigRollbackRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigRollbackResponse:
    """Load a historical version as a draft.

    Retrieves the contents of the target version and saves them as
    a draft.  The active (live) config is not affected until the
    draft is explicitly activated.

    No versions are deleted — full history is preserved.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    # Get the target version's content
    version_result = await processor.get_version(
        ctx.tenant_id, tier, body.target_version,
    )
    if version_result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Configuration version {body.target_version} not found",
        )

    # Save version content as a draft
    draft_result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=tier,
        changes=version_result.config,
        actor=actor,
    )

    # Get current active version for response
    current = await processor.get_config(ctx.tenant_id, tier)

    return ConfigRollbackResponse(
        success=draft_result.success,
        from_version=current.version,
        to_version=body.target_version,
        new_version=draft_result.version,
        message=(
            f"Version {body.target_version} loaded as draft. "
            f"Activate to apply."
        ),
    )


# ---------------------------------------------------------------------------
# 19. GET /api/config/activation-status — Lightweight activation state
# ---------------------------------------------------------------------------

@router.get(
    "/activation-status",
    response_model=ActivationStatusResponse,
    summary="Get activation status",
    description=(
        "Returns a lightweight summary of the activation state: whether "
        "there are pending draft changes, the active version and activation "
        "time, and the draft version if any."
    ),
)
async def get_activation_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ActivationStatusResponse:
    """Lightweight activation state check for the admin banner.

    Designed to be polled frequently (every 30 seconds) by the frontend
    to determine whether the activation banner should be shown.
    """
    tier = _resolve_tier(ctx)
    activation_svc = get_activation_service()

    draft_state = await activation_svc.get_draft_state(ctx.tenant_id, tier)

    # A tenant is "configured" only when an active config exists with all
    # mandatory fields populated (brand_name, brand_voice, widget_key).
    is_configured = False
    is_active = False
    if draft_state.active_version > 0 and draft_state.active_activated_at:
        active = await activation_svc._prefs_repo.get_active(ctx.tenant_id)
        if active:
            brand_name = active.get("brand_name")
            brand_voice = active.get("brand_voice")
            widget_key = active.get("widget_key")
            is_configured = bool(
                brand_name and str(brand_name).strip()
                and brand_voice and str(brand_voice).strip()
                and widget_key
            )
            # is_active: config is activated AND not deactivated
            # deactivated_at on the active config means the merchant
            # explicitly disabled the widget.
            is_active = is_configured and not active.get("deactivated_at")

    # can_activate: check the relevant config (draft or active) for mandatory
    # fields so the frontend knows whether the Activate button should be
    # green (ready) or yellow (blocked).
    can_activate = False
    if draft_state.has_pending_changes:
        # Pending changes exist — check the draft document.
        doc = await activation_svc._prefs_repo.get_draft(ctx.tenant_id)
    elif is_configured and not is_active:
        # Deactivated with complete config — use the active document
        # (no separate draft exists when there are no pending changes).
        doc = active if active else None  # type: ignore[assignment]
    else:
        doc = None
    if doc:
        d_brand = doc.get("brand_name")
        d_voice = doc.get("brand_voice")
        d_wkey = doc.get("widget_key")
        can_activate = bool(
            d_brand and str(d_brand).strip()
            and d_voice and str(d_voice).strip()
            and d_wkey
        )

    return ActivationStatusResponse(
        has_pending_changes=draft_state.has_pending_changes,
        active_version=draft_state.active_version,
        active_activated_at=draft_state.active_activated_at,
        draft_version=draft_state.draft_version,
        is_configured=is_configured,
        is_active=is_active,
        can_activate=can_activate,
    )


# ---------------------------------------------------------------------------
# 19b. POST /api/config/deactivate — Deactivate the live widget
# ---------------------------------------------------------------------------


class DeactivateConfigResponse(CamelCaseModel):
    """Response for POST /config/deactivate."""

    success: bool
    deactivated_at: str
    message: str


@router.post(
    "/deactivate",
    response_model=DeactivateConfigResponse,
    summary="Deactivate live configuration",
    description=(
        "Immediately deactivates the live configuration. The chat widget "
        "stops serving on the storefront. The active configuration is "
        "preserved — re-activation is a one-click operation."
    ),
    responses={
        200: {"description": "Configuration deactivated"},
        409: {"description": "Configuration is not currently active"},
    },
)
async def deactivate_config(
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeactivateConfigResponse:
    """Deactivate the live configuration (widget stops serving)."""
    activation_svc = get_activation_service()

    active = await activation_svc._prefs_repo.get_active(ctx.tenant_id)
    if not active:
        raise HTTPException(
            status_code=409,
            detail="No active configuration to deactivate.",
        )

    if active.get("deactivated_at"):
        raise HTTPException(
            status_code=409,
            detail="Configuration is already deactivated.",
        )

    now = datetime.now(timezone.utc).isoformat()
    await activation_svc._prefs_repo.patch(
        tenant_id=ctx.tenant_id,
        document_id=active["id"],
        operations=[
            {"op": "set", "path": "/deactivated_at", "value": now},
        ],
    )

    # Invalidate config cache so pipeline picks up the change immediately
    if activation_svc._config_processor is not None:
        activation_svc._config_processor._invalidate_cache(ctx.tenant_id)

    # Audit log
    if activation_svc._audit_repo is not None:
        try:
            await activation_svc._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_UPDATED,
                tenant_id=ctx.tenant_id,
                actor=getattr(ctx, "user_id", "admin"),
                actor_type="user",
                payload={
                    "action": "config_deactivated",
                    "active_version": active.get("version", 0),
                    "deactivated_at": now,
                },
            )
        except Exception:
            logger.warning("Failed to log deactivation audit event", exc_info=True)

    logger.info(
        "Tenant %s configuration deactivated at %s",
        ctx.tenant_id[:8], now,
    )

    return DeactivateConfigResponse(
        success=True,
        deactivated_at=now,
        message="Configuration deactivated. Chat widget is no longer serving.",
    )


# ---------------------------------------------------------------------------
# 20. GET /api/config/draft — Full draft state + diff vs active
# ---------------------------------------------------------------------------

@router.get(
    "/draft",
    response_model=DraftStateResponse,
    summary="Get draft state",
    description=(
        "Returns the full draft state including the draft config, active "
        "config, and a list of fields that differ between them."
    ),
)
async def get_draft_state(
    ctx: TenantContext = Depends(get_tenant_context),
) -> DraftStateResponse:
    """Get the full draft state for the activation dialog.

    Returns draft config, active config, and the list of changed fields
    so the frontend can render a meaningful diff.
    """
    tier = _resolve_tier(ctx)
    activation_svc = get_activation_service()

    draft_state = await activation_svc.get_draft_state(ctx.tenant_id, tier)

    return DraftStateResponse(
        has_pending_changes=draft_state.has_pending_changes,
        active_version=draft_state.active_version,
        active_activated_at=draft_state.active_activated_at,
        draft_version=draft_state.draft_version,
        changed_fields=draft_state.changed_fields,
        draft_config=draft_state.draft_config,
        active_config=draft_state.active_config,
    )


# ---------------------------------------------------------------------------
# 20b. GET /api/config/draft/preflight — Pre-activation validation (D35)
# ---------------------------------------------------------------------------

@router.get(
    "/draft/preflight",
    response_model=PreflightResponse,
    summary="Pre-activation validation check",
    description=(
        "Runs activation validation rules without activating. Returns hard "
        "errors (blocking) and warnings so the frontend can show what's "
        "missing before the admin commits."
    ),
)
async def preflight_check(
    ctx: TenantContext = Depends(get_tenant_context),
) -> PreflightResponse:
    """Dry-run activation validation for the ActivationDialog.

    Called when the dialog opens to immediately show which mandatory fields
    are missing, without requiring the admin to click through confirmation.
    """
    tier = _resolve_tier(ctx)
    activation_svc = get_activation_service()

    validation = await activation_svc.validate_for_activation(ctx.tenant_id, tier)

    return PreflightResponse(
        can_activate=validation.can_activate,
        hard_errors=validation.hard_errors,
        warnings=validation.warnings,
    )


# ---------------------------------------------------------------------------
# 21. POST /api/config/draft/activate — Validate and activate the draft
# ---------------------------------------------------------------------------

@router.post(
    "/draft/activate",
    response_model=ActivateResponse,
    summary="Activate draft configuration",
    description=(
        "Validates the draft and promotes it to active. The previous active "
        "config becomes 'previous' (available for restore). Fails if "
        "hard-block validation errors exist (e.g. missing brand_name)."
    ),
    responses={
        422: {"description": "Validation errors prevent activation"},
    },
)
async def activate_draft(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ActivateResponse:
    """Validate and activate the draft configuration.

    On success, the draft becomes the live config and the previous
    active config is preserved for one-level undo via POST /restore.
    """
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    result = await activation_svc.activate(
        tenant_id=ctx.tenant_id,
        tier=tier,
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "errors": result.errors,
                "warnings": result.warnings,
            },
        )

    return ActivateResponse(
        success=result.success,
        version=result.version,
        activated_at=result.activated_at,
        errors=result.errors or [],
        warnings=result.warnings or [],
    )


# ---------------------------------------------------------------------------
# 22. POST /api/config/draft/discard — Discard all draft changes
# ---------------------------------------------------------------------------

@router.post(
    "/draft/discard",
    response_model=DiscardResponse,
    summary="Discard draft changes",
    description="Deletes the draft document. The active config is unchanged.",
)
async def discard_draft(
    ctx: TenantContext = Depends(get_tenant_context),
) -> DiscardResponse:
    """Discard all pending draft changes.

    The active (live) config is not affected.
    """
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    discarded = await activation_svc.discard_draft(
        tenant_id=ctx.tenant_id,
        actor=actor,
    )

    return DiscardResponse(
        success=True,
        message="Draft discarded" if discarded else "No draft to discard",
    )


# ---------------------------------------------------------------------------
# 23. POST /api/config/restore — Restore previous activation snapshot
# ---------------------------------------------------------------------------

@router.post(
    "/restore",
    response_model=RestoreResponse,
    summary="Restore previous configuration",
    description=(
        "Swaps the active config with the previous activation snapshot. "
        "The current active config becomes 'previous' and the previous "
        "becomes 'active'. Any pending draft is discarded."
    ),
    responses={
        400: {"description": "No previous configuration to restore"},
    },
)
async def restore_previous(
    ctx: TenantContext = Depends(get_tenant_context),
) -> RestoreResponse:
    """Restore the previous activation snapshot.

    One-level undo: the current active becomes previous, and the
    previous becomes active.  Any pending draft is discarded.
    """
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)
    activation_svc = get_activation_service()

    result = await activation_svc.restore_previous(
        tenant_id=ctx.tenant_id,
        tier=tier,
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error or "No previous configuration to restore",
        )

    return RestoreResponse(
        success=result.success,
        restored_version=result.restored_version,
        restored_activated_at=result.restored_activated_at,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _derive_actor(ctx: TenantContext) -> str:
    """Derive an actor identifier from the auth context for audit logging."""
    if ctx.user_id:
        return f"user:{ctx.user_id}"
    if ctx.shop_domain:
        return f"shopify:{ctx.shop_domain}"
    return f"tenant:{ctx.tenant_id[:8]}"
