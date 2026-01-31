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
    POST   /api/config/rollback     — Roll back to a previous version

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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TenantTier
from src.multi_tenant.middleware import get_tenant_context
from src.multi_tenant.tenant_config_processor import (
    ConfigReadResult,
    ConfigRollbackResult,
    ConfigUpdateResult,
    ConfigVersionInfo,
    get_config_processor,
)
from src.multi_tenant.tenant_config_schema import (
    OnboardingStep,
    export_schema_for_api,
    get_fields_by_step,
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


class ConfigResponse(BaseModel):
    """Standard config read response."""

    tenant_id: str
    tier: str
    version: int
    config: dict[str, Any]
    from_cache: bool = False


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


class StepFieldsResponse(BaseModel):
    """Response containing fields for a specific onboarding step."""

    step_number: int
    step_name: str
    fields: list[dict[str, Any]]
    total_fields: int = 0


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
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/config", tags=["configuration"])


# ---------------------------------------------------------------------------
# 1. GET /api/config — Current resolved config
# ---------------------------------------------------------------------------

@router.get("", response_model=ConfigResponse)
async def get_config(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigResponse:
    """Get the fully resolved current configuration.

    Returns the tenant's configuration with all inheritance applied:
    platform defaults → tier defaults → tenant overrides.

    The result may come from a 60-second in-memory cache.
    """
    processor = get_config_processor()
    tier = _resolve_tier(ctx)

    result = await processor.get_config(ctx.tenant_id, tier)

    return ConfigResponse(
        tenant_id=result.tenant_id,
        tier=result.tier,
        version=result.version,
        config=result.config,
        from_cache=result.from_cache,
    )


# ---------------------------------------------------------------------------
# 2. PUT /api/config — Partial config update
# ---------------------------------------------------------------------------

@router.put("", response_model=ConfigUpdateResponse)
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

@router.post("/validate", response_model=ConfigValidateResponse)
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

@router.post("/reset", response_model=ConfigUpdateResponse)
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

@router.get("/diff", response_model=ConfigDiffResponse)
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

@router.get("/schema", response_model=ConfigSchemaResponse)
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

@router.get("/schema/{step}", response_model=StepFieldsResponse)
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
    from src.multi_tenant.tenant_config_schema import TierGate
    gate_rank = {TierGate.ALL: 0, TierGate.PROFESSIONAL_PLUS: 1, TierGate.ENTERPRISE_ONLY: 2}
    rank = tier_rank.get(tier, 0)

    available_fields = [
        f for f in fields
        if gate_rank.get(f.tier_gate, 0) <= rank
    ]

    # Build response
    from src.multi_tenant.tenant_config_schema import resolve_defaults
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

    step_name = onboarding_step.name.lower().replace("_", " ").title()

    return StepFieldsResponse(
        step_number=step,
        step_name=step_name,
        fields=field_dicts,
        total_fields=len(field_dicts),
    )


# ---------------------------------------------------------------------------
# 8. GET /api/config/versions — Version history
# ---------------------------------------------------------------------------

@router.get("/versions", response_model=ConfigVersionListResponse)
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

@router.get("/versions/{version}", response_model=ConfigResponse)
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
# 10. POST /api/config/rollback — Roll back to a previous version
# ---------------------------------------------------------------------------

@router.post("/rollback", response_model=ConfigRollbackResponse)
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
# Helpers
# ---------------------------------------------------------------------------


def _derive_actor(ctx: TenantContext) -> str:
    """Derive an actor identifier from the auth context for audit logging."""
    if ctx.user_id:
        return f"user:{ctx.user_id}"
    if ctx.shop_domain:
        return f"shopify:{ctx.shop_domain}"
    return f"tenant:{ctx.tenant_id[:8]}"
