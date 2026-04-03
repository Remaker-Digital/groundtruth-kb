"""Admin Presets API — G6 Vertical Template Starter Kits (SPEC-1878).

Provides REST endpoints for the OnboardingWizard's preset selection:

    GET    /api/admin/presets              — List available presets
    GET    /api/admin/presets/{preset_id}  — Get full preset detail
    POST   /api/admin/presets/{preset_id}/apply — Apply preset to tenant

All endpoints require tenant auth (same as existing admin APIs).
No tier gate — v1 presets are preferences-only, valid for all tiers.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context
from src.presets.preset_service import get_preset_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/presets", tags=["admin-presets"])


@router.get(
    "",
    summary="List available presets",
    description="Returns metadata for all vertical presets. No full content.",
)
async def list_presets(
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """List all available vertical presets."""
    svc = get_preset_service()
    presets = svc.list_presets()
    return {
        "presets": [p.to_dict() for p in presets],
        "total_count": len(presets),
    }


@router.get(
    "/{preset_id}",
    summary="Get preset detail",
    description="Returns full preset content including preferences, quick actions, and KB seed articles.",
)
async def get_preset(
    preset_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Get full detail for a specific preset."""
    svc = get_preset_service()
    preset = svc.get_preset(preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail=f"Preset not found: {preset_id}")
    return preset


@router.post(
    "/{preset_id}/apply",
    summary="Apply preset to tenant",
    description=(
        "Applies a vertical preset: saves config draft, creates quick actions "
        "with page assignments, and seeds starter KB articles. All writes go "
        "through existing surfaces (draft lifecycle for config/QA, immediate "
        "for KB). Tenant must activate draft for config changes to go live."
    ),
)
async def apply_preset(
    preset_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    """Apply a vertical preset to the authenticated tenant."""
    svc = get_preset_service()

    try:
        result = await svc.apply_preset(
            tenant_id=ctx.tenant_id,
            preset_id=preset_id,
            tier=ctx.tier or "starter",
            actor=f"user:{ctx.user_id}" if ctx.user_id else "preset_service",
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    logger.info(
        "Preset '%s' applied: tenant=%s draft=%s qa=%d kb=%d",
        preset_id, ctx.tenant_id[:8], result.draft_created,
        result.quick_actions_created, result.articles_created,
    )
    return result.to_dict()
