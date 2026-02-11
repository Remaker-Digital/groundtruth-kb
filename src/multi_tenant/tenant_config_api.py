"""Configuration API — RESTful endpoints for tenant configuration management.

Work Item #65 (Decision #22): Layer 3 of the 5-layer tenant configuration
system — 10 RESTful endpoints wrapping the TenantConfigProcessor.

Endpoints:
    GET    /api/config              — Current resolved config
    PUT    /api/config              — Partial config update
    POST   /api/config/validate     — Dry-run validation (no persist)
    POST   /api/config/reset        — Reset to tier defaults
    GET    /api/config/diff         — Overrides vs. tier defaults
    GET    /api/config/schema       — Field metadata for UI rendering
    GET    /api/config/schema/{step} — Fields for a specific onboarding step
    GET    /api/config/versions     — Version history
    GET    /api/config/versions/{version} — Specific historical version
    GET    /api/config/named        — List named configurations (C3)
    POST   /api/config/named        — Save current config as named (C3)
    POST   /api/config/named/{name}/activate — Activate a named config (C3)
    DELETE /api/config/named/{name} — Delete a named config (C3)
    GET    /api/config/widget-appearances           — List named appearances (C4)
    POST   /api/config/widget-appearances           — Save appearance as named (C4)
    POST   /api/config/widget-appearances/{name}/activate — Activate appearance (C4)
    DELETE /api/config/widget-appearances/{name}    — Delete appearance (C4)
    POST   /api/config/rollback     — Roll back to a previous version
    GET    /api/config/test-mode              — Test Mode status (C2)
    POST   /api/config/test-mode/activate     — Activate Test Mode (C2)
    POST   /api/config/test-mode/deactivate   — Deactivate Test Mode (C2)
    PUT    /api/config/test-mode/percentage   — Update routing percentage (C2)

All endpoints derive tenant_id and tier from the authenticated TenantContext
— never from query parameters.  Tenant isolation is enforced at every level:
auth middleware → processor → repository.

Architecture references:
    - Decision #22: 5-layer tenant configuration management
    - Work Item #65: Configuration API (10 endpoints)
    - Work Item #64: TenantConfigProcessor (upstream dependency)
    - Work Item #63: tenant_config_schema (upstream dependency)

Dependencies:
    - tenant_config_processor.py: get_config_processor
    - tenant_config_schema.py: export_schema_for_api, get_fields_by_step, OnboardingStep
    - middleware.py: get_tenant_context
    - auth.py: TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.tenant_config_processor import (
    ConfigReadResult,
    ConfigRollbackResult,
    ConfigUpdateResult,
    ConfigVersionInfo,
    NamedConfigSummary,
    get_config_processor,
)
from src.multi_tenant.tenant_config_schema import (
    OnboardingStep,
    TierGate,
    export_schema_for_api,
    get_fields_by_step,
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


class ConfigUpdateResponse(BaseModel):
    """Response for config update operations."""

    success: bool
    version: int = 0
    errors: list[dict[str, str]] = Field(default_factory=list)
    warnings: list[dict[str, str]] = Field(default_factory=list)
    changes: dict[str, Any] = Field(default_factory=dict)
    resolved_config: dict[str, Any] = Field(default_factory=dict)


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


class StepFieldsResponse(BaseModel):
    """Response containing fields for a specific onboarding step."""

    step_number: int
    step_name: str
    fields: list[dict[str, Any]]
    total_fields: int = 0


class OnboardingFieldResponse(BaseModel):
    """A single config field for onboarding step rendering."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    key: str
    label: str
    description: str
    type: str
    default_value: Any = None
    current_value: Any = None
    tier_gate: str | None = None
    step_order: int = 0
    group: str = ""


class OnboardingStepResponse(BaseModel):
    """A single onboarding step with its fields."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    step: str
    label: str
    description: str
    fields: list[OnboardingFieldResponse]
    is_complete: bool = False


class OnboardingResponse(BaseModel):
    """Full onboarding wizard data — all steps at once."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    steps: list[OnboardingStepResponse]


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
        actions = await _quick_action_repo.get_quick_actions(tenant_id)
        assignments = await _quick_action_repo.get_page_assignments(tenant_id)
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
    description="Returns the tenant's configuration with all inheritance applied: platform defaults, tier defaults, and tenant overrides. Result may come from a 60-second cache. Optionally includes quick action buttons for the specified page context.",
)
async def get_config(
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

    Returns the tenant's configuration with all inheritance applied:
    platform defaults → tier defaults → tenant overrides.

    The result may come from a 60-second in-memory cache.

    When ``page_type`` is provided, quick actions assigned to that page
    are included in the response.  The widget uses these to render
    contextual prompt buttons in the greeting area.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    result = await processor.get_config(ctx.tenant_id, tier)

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
        config=result.config,
        from_cache=result.from_cache,
        quick_actions=quick_actions,
    )


# ---------------------------------------------------------------------------
# 2. PUT /api/config — Partial config update
# ---------------------------------------------------------------------------

@router.put(
    "",
    response_model=ConfigUpdateResponse,
    summary="Update tenant configuration",
    description="Applies partial configuration changes. Only provided fields are updated; omitted fields retain their current values. Returns validation errors if any field fails validation or tier gating.",
    responses={
        400: {"description": "No configuration fields provided"},
        422: {"description": "Validation errors in submitted fields"},
    },
)
async def update_config(
    body: ConfigUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Update tenant configuration with partial changes.

    Accepts a dict of field_name → new_value. Only provided fields are
    changed; omitted fields retain their current values.

    The update is validated, merged with existing config, persisted as
    a new version, and an audit event is logged.

    Returns validation errors if any field fails validation or tier gating.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    if not body.fields:
        raise HTTPException(
            status_code=400,
            detail="No configuration fields provided",
        )

    # Derive actor from auth context
    actor = _derive_actor(ctx)

    result = await processor.update_config(
        tenant_id=ctx.tenant_id,
        tier=tier,
        changes=body.fields,
        actor=actor,
    )

    status_code = 200 if result.success else 422

    response = ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        errors=result.validation.errors,
        warnings=result.validation.warnings,
        changes=result.changes,
        resolved_config=result.resolved_config,
    )

    if not result.success:
        # Return 422 with validation errors in the body
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "errors": result.validation.errors,
                "warnings": result.validation.warnings,
            },
        )

    return response


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
        errors=result.errors,
        warnings=result.warnings,
        sanitized=result.sanitized,
    )


# ---------------------------------------------------------------------------
# 4. POST /api/config/reset — Reset to tier defaults
# ---------------------------------------------------------------------------

@router.post(
    "/reset",
    response_model=ConfigUpdateResponse,
    summary="Reset configuration to defaults",
    description="Resets all configuration to tier defaults. Creates a new version with only default values and clears all tenant overrides.",
)
async def reset_config(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Reset all configuration to tier defaults.

    Creates a new version with only default values. All tenant overrides
    are cleared. This action is logged in the audit trail.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    result = await processor.reset_to_defaults(
        tenant_id=ctx.tenant_id,
        tier=tier,
        actor=actor,
    )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        changes=result.changes,
        resolved_config=result.resolved_config,
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
# 5b. GET /api/config/onboarding — All onboarding steps at once
# ---------------------------------------------------------------------------

# Step labels for UI display — sentence case (only first word capitalised)
_STEP_LABELS: dict[OnboardingStep, str] = {
    OnboardingStep.BRAND_AND_TONE: "Brand and tone",
    OnboardingStep.LANGUAGES: "Languages",
    OnboardingStep.RESPONSE_STYLE: "Response style",
    OnboardingStep.KNOWLEDGE_BASE: "Knowledge base",
    OnboardingStep.BUSINESS_POLICIES: "Business policies",
    OnboardingStep.ESCALATION_RULES: "Escalation rules",
    OnboardingStep.INTEGRATIONS: "Integrations",
    OnboardingStep.MEMORY_AND_PRIVACY: "Memory and privacy",
    OnboardingStep.WIDGET_APPEARANCE: "Widget appearance",
    OnboardingStep.REVIEW_AND_LAUNCH: "Review and launch",
}

# Step descriptions for UI display
_STEP_DESCRIPTIONS: dict[OnboardingStep, str] = {
    OnboardingStep.BRAND_AND_TONE: "Set your brand name, voice, and greeting messages.",
    OnboardingStep.LANGUAGES: "Configure primary and additional languages.",
    OnboardingStep.RESPONSE_STYLE: "Control response length, formality, and emoji usage.",
    OnboardingStep.KNOWLEDGE_BASE: "Configure knowledge scope and product recommendations.",
    OnboardingStep.BUSINESS_POLICIES: "Add return, shipping, warranty, and support policies.",
    OnboardingStep.ESCALATION_RULES: "Set escalation thresholds, keywords, and notifications.",
    OnboardingStep.INTEGRATIONS: "Enable Shopify sync, Zendesk, Mailchimp, and GA4.",
    OnboardingStep.MEMORY_AND_PRIVACY: "Configure customer memory layers and data retention.",
    OnboardingStep.WIDGET_APPEARANCE: "Customize widget colors, position, and behavior.",
    OnboardingStep.REVIEW_AND_LAUNCH: "Review all settings and launch your AI agent.",
}


@router.get(
    "/onboarding",
    response_model=OnboardingResponse,
    summary="Get onboarding wizard steps",
    description="Returns all onboarding steps with their tier-filtered fields, current defaults, and completion flags for the wizard UI.",
)
async def get_onboarding_steps(
    ctx: TenantContext = Depends(get_tenant_context),
) -> OnboardingResponse:
    """Get all onboarding steps with their fields for the wizard UI.

    Returns every step in order, each with its tier-filtered fields,
    current defaults, and a completion flag (always False for now —
    completion tracking is a future enhancement).
    """
    tier = _resolve_tier(ctx)

    # Get current resolved config to populate currentValue
    processor = get_config_processor()
    config_result = await processor.get_config(ctx.tenant_id, tier)
    current_config = config_result.config if config_result else {}

    # Tier ranking for field filtering
    tier_rank = {TenantTier.STARTER: 0, TenantTier.PROFESSIONAL: 1, TenantTier.ENTERPRISE: 2}
    gate_rank = {TierGate.ALL: 0, TierGate.PROFESSIONAL_PLUS: 1, TierGate.ENTERPRISE_ONLY: 2}
    rank = tier_rank.get(tier, 0)

    defaults = resolve_defaults(tier)

    steps: list[OnboardingStepResponse] = []
    for step in OnboardingStep:
        fields = get_fields_by_step(step)

        # Filter by tier gate
        available_fields = [
            f for f in fields
            if gate_rank.get(f.tier_gate, 0) <= rank
        ]

        step_name_label = _STEP_LABELS.get(step, step.name.lower().replace("_", " "))

        field_responses = [
            OnboardingFieldResponse(
                key=f.field_name,
                label=f.display_name,
                description=f.description or f.tooltip,
                type=f.field_type.value,
                default_value=defaults.get(f.field_name),
                current_value=current_config.get(f.field_name, defaults.get(f.field_name)),
                tier_gate=f.tier_gate.value if f.tier_gate != TierGate.ALL else None,
                step_order=f.step_order,
                group=step_name_label,
            )
            for f in available_fields
        ]

        steps.append(OnboardingStepResponse(
            step=step.name.lower(),
            label=step_name_label,
            description=_STEP_DESCRIPTIONS.get(step, ""),
            fields=field_responses,
            is_complete=False,
        ))

    return OnboardingResponse(steps=steps)


# ---------------------------------------------------------------------------
# 6. GET /api/config/schema — Full field schema for UI rendering
# ---------------------------------------------------------------------------

@router.get(
    "/schema",
    response_model=ConfigSchemaResponse,
    summary="Get configuration field schema",
    description="Returns field metadata (types, validation rules, defaults, tooltips) organized by onboarding step. Fields are filtered by the tenant's tier.",
)
async def get_config_schema(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigSchemaResponse:
    """Get the configuration field schema for the tenant's tier.

    Returns field metadata (types, validation rules, defaults, tooltips,
    doc links) organized by onboarding step. Used by the Merchant
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
# 7. GET /api/config/schema/{step} — Fields for a specific onboarding step
# ---------------------------------------------------------------------------

@router.get(
    "/schema/{step}",
    response_model=StepFieldsResponse,
    summary="Get fields for onboarding step",
    description="Returns configuration fields for a specific onboarding step (1-9), filtered by the tenant's tier.",
    responses={
        400: {"description": "Invalid step number (must be 1-9)"},
    },
)
async def get_step_fields(
    step: int,
    ctx: TenantContext = Depends(get_tenant_context),
) -> StepFieldsResponse:
    """Get configuration fields for a specific onboarding step.

    Step numbers (1-9):
        1. Brand & Tone
        2. Languages
        3. Response Style
        4. Knowledge Base
        5. Business Policies
        6. Escalation Rules
        7. Integrations
        8. Memory & Privacy
        9. Review & Launch
    """
    # Validate step number
    try:
        onboarding_step = OnboardingStep(step)
    except ValueError:
        raise HTTPException(  # noqa: B904
            status_code=400,
            detail=f"Invalid step number: {step}. Must be 1-9.",
        )

    tier = _resolve_tier(ctx)

    # Get fields for this step
    fields = get_fields_by_step(onboarding_step)

    # Filter by tier gate
    tier_rank = {TenantTier.STARTER: 0, TenantTier.PROFESSIONAL: 1, TenantTier.ENTERPRISE: 2}
    gate_rank = {TierGate.ALL: 0, TierGate.PROFESSIONAL_PLUS: 1, TierGate.ENTERPRISE_ONLY: 2}
    rank = tier_rank.get(tier, 0)

    available_fields = [
        f for f in fields
        if gate_rank.get(f.tier_gate, 0) <= rank
    ]

    # Build response
    defaults = resolve_defaults(tier)

    field_dicts = [
        {
            "field_name": f.field_name,
            "display_name": f.display_name,
            "field_type": f.field_type.value,
            "default": defaults.get(f.field_name),
            "validation": {
                k: v
                for k, v in f.validation.model_dump().items()
                if v is not None
            },
            "tooltip": f.tooltip,
            "description": f.description,
            "placeholder": f.placeholder,
            "doc_link": f.doc_link,
            "affects_agents": f.affects_agents,
            "injected_in_prompt": f.injected_in_prompt,
            "tier_gate": f.tier_gate.value,
        }
        for f in available_fields
    ]

    step_name = _STEP_LABELS.get(onboarding_step, onboarding_step.name.lower().replace("_", " "))

    return StepFieldsResponse(
        step_number=step,
        step_name=step_name,
        fields=field_dicts,
        total_fields=len(field_dicts),
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
    summary="Activate named configuration",
    description="Activates a named configuration, making it the current live config. Creates a new version with the named config's stored values.",
    responses={
        404: {"description": "Named configuration not found"},
    },
)
async def activate_named_config(
    name: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Activate a named configuration as the current live config."""
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    result = await processor.activate_named_config(
        tenant_id=ctx.tenant_id,
        tier=tier,
        name=name,
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=404,
            detail=f"Named configuration '{name}' not found",
        )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        resolved_config=result.resolved_config,
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
    summary="Activate named widget appearance",
    description="Activates a named widget appearance, applying its widget_* field values to the current live config.",
    responses={
        404: {"description": "Named appearance not found"},
    },
)
async def activate_widget_appearance(
    name: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigUpdateResponse:
    """Activate a named widget appearance."""
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    result = await processor.activate_named_appearance(
        tenant_id=ctx.tenant_id,
        tier=tier,
        name=name,
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=404,
            detail=f"Named appearance '{name}' not found",
        )

    return ConfigUpdateResponse(
        success=result.success,
        version=result.version,
        resolved_config=result.resolved_config,
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
    summary="Roll back to previous version",
    description="Creates a new version with the contents of the target version. No versions are deleted and full history is preserved.",
    responses={
        404: {"description": "Target version not found"},
    },
)
async def rollback_config(
    body: ConfigRollbackRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigRollbackResponse:
    """Roll back configuration to a previous version.

    Creates a NEW version with the contents of the target version.
    No versions are deleted — full history is preserved.

    The rollback is logged in the audit trail.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    result = await processor.rollback(
        tenant_id=ctx.tenant_id,
        tier=tier,
        target_version=body.target_version,
        actor=actor,
    )

    if not result.success:
        raise HTTPException(
            status_code=404,
            detail=result.message,
        )

    return ConfigRollbackResponse(
        success=result.success,
        from_version=result.from_version,
        to_version=result.to_version,
        new_version=result.new_version,
        message=result.message,
    )


# ---------------------------------------------------------------------------
# 19. GET /api/config/test-mode — Test Mode status (C2)
# ---------------------------------------------------------------------------

@router.get(
    "/test-mode",
    summary="Get Test Mode status",
    description="Returns the current Test Mode state: enabled/disabled, percentage, overrides, activation time.",
    tags=["Test Mode"],
)
async def get_test_mode_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Return Test Mode status for the current tenant."""
    from .test_mode_service import get_test_mode_service

    service = get_test_mode_service()
    return await service.get_status(ctx.tenant_id)


# ---------------------------------------------------------------------------
# 20. POST /api/config/test-mode/activate (C2)
# ---------------------------------------------------------------------------

class TestModeActivateRequest(BaseModel):
    overrides: dict[str, Any] = Field(
        description="AI behaviour field deltas to apply during test mode",
    )
    percentage: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Percentage of sessions routed to test config (1-50)",
    )

@router.post(
    "/test-mode/activate",
    summary="Activate Test Mode",
    description="Activates Test Mode with the given AI-behaviour overrides and routing percentage.",
    tags=["Test Mode"],
)
async def activate_test_mode(
    body: TestModeActivateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Activate Test Mode."""
    from .test_mode_service import get_test_mode_service

    service = get_test_mode_service()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    result = await service.activate(
        tenant_id=ctx.tenant_id,
        tier=tier,
        overrides=body.overrides,
        percentage=body.percentage,
        actor=actor,
    )

    if not result.get("success"):
        raise HTTPException(status_code=422, detail=result.get("error", "Activation failed"))

    return result


# ---------------------------------------------------------------------------
# 21. POST /api/config/test-mode/deactivate (C2)
# ---------------------------------------------------------------------------

class TestModeDeactivateRequest(BaseModel):
    action: str = Field(
        default="abandon",
        pattern=r"^(rollout|abandon)$",
        description="'rollout' merges test overrides into production; 'abandon' discards them.",
    )

@router.post(
    "/test-mode/deactivate",
    summary="Deactivate Test Mode",
    description="Deactivates Test Mode. 'rollout' merges overrides into production config. 'abandon' discards them.",
    tags=["Test Mode"],
)
async def deactivate_test_mode(
    body: TestModeDeactivateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Deactivate Test Mode (rollout or abandon)."""
    from .test_mode_service import get_test_mode_service

    service = get_test_mode_service()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    result = await service.deactivate(
        tenant_id=ctx.tenant_id,
        tier=tier,
        action=body.action,
        actor=actor,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Deactivation failed"))

    return result


# ---------------------------------------------------------------------------
# 22. PUT /api/config/test-mode/percentage (C2)
# ---------------------------------------------------------------------------

class TestModePercentageRequest(BaseModel):
    percentage: int = Field(
        ge=1,
        le=50,
        description="New routing percentage (1-50)",
    )

@router.put(
    "/test-mode/percentage",
    summary="Update Test Mode percentage",
    description="Change the percentage of sessions routed to test config while Test Mode is active.",
    tags=["Test Mode"],
)
async def update_test_mode_percentage(
    body: TestModePercentageRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Update the test mode routing percentage."""
    from .test_mode_service import get_test_mode_service

    service = get_test_mode_service()
    tier = _resolve_tier(ctx)
    actor = _derive_actor(ctx)

    return await service.update_percentage(
        tenant_id=ctx.tenant_id,
        tier=tier,
        percentage=body.percentage,
        actor=actor,
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
