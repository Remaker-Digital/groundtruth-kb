# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Launcher image upload endpoint — SPEC-0245 capability.

Accepts PNG/JPEG/GIF/SVG launcher images, validates format and size,
stores as base64 data URI in the tenant's config (widget_launcher_image_url field).

Routes:
    POST /api/admin/launcher-image/upload — Upload launcher image (max 128KB)
    DELETE /api/admin/launcher-image       — Remove launcher image (reset to built-in icon)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import base64
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.multi_tenant.middleware import TenantContext, get_tenant_context

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_LAUNCHER_IMAGE_BYTES = 128 * 1024  # 128KB
ALLOWED_CONTENT_TYPES = {
    "image/png", "image/jpeg", "image/jpg",
    "image/gif", "image/svg+xml",
}

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class LauncherImageUploadResponse(BaseModel):
    """Response for launcher image upload."""

    success: bool
    image_url: str | None = Field(
        default=None,
        description="Data URI of the uploaded launcher image",
    )
    size_bytes: int = 0
    message: str = ""


class LauncherImageDeleteResponse(BaseModel):
    """Response for launcher image deletion."""

    success: bool
    message: str = ""


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/launcher-image", tags=["admin-launcher-image"])


@router.post("/upload", response_model=LauncherImageUploadResponse)
async def upload_launcher_image(
    file: UploadFile = File(
        ..., description="Launcher image (PNG, JPEG, GIF, or SVG, max 128KB)"
    ),
    ctx: TenantContext = Depends(get_tenant_context),
) -> LauncherImageUploadResponse:
    """Upload a custom launcher image for the chat widget (SPEC-0245).

    The image replaces the built-in icon when widget_launcher_icon is set
    to 'custom'. Stored as a base64 data URI in the tenant config.
    """
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{content_type}'. "
            "Allowed: PNG, JPEG, GIF, SVG.",
        )

    data = await file.read()
    if len(data) > MAX_LAUNCHER_IMAGE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(data)} bytes). "
            f"Maximum: {MAX_LAUNCHER_IMAGE_BYTES} bytes (128KB).",
        )

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    mime = content_type if content_type != "image/jpg" else "image/jpeg"
    b64 = base64.b64encode(data).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"

    from src.multi_tenant.activation_service import get_activation_service

    activation_svc = get_activation_service()
    result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        changes={
            "widget_launcher_image_url": data_uri,
            "widget_launcher_icon": "custom",
        },
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        errors = getattr(result, "errors", []) if result else []
        detail = (
            "; ".join(str(e) for e in errors)
            if errors
            else "Failed to save launcher image."
        )
        raise HTTPException(status_code=500, detail=detail)

    logger.info(
        "Launcher image uploaded for tenant %s: %d bytes, %s",
        ctx.tenant_id[:8], len(data), mime,
    )

    return LauncherImageUploadResponse(
        success=True,
        image_url=data_uri,
        size_bytes=len(data),
        message="Launcher image uploaded successfully. "
        "Set widget_launcher_icon to 'custom' to display it.",
    )


@router.delete("", response_model=LauncherImageDeleteResponse)
async def delete_launcher_image(
    ctx: TenantContext = Depends(get_tenant_context),
) -> LauncherImageDeleteResponse:
    """Remove the custom launcher image (resets to built-in icon)."""
    from src.multi_tenant.activation_service import get_activation_service

    activation_svc = get_activation_service()
    result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        changes={
            "widget_launcher_image_url": None,
            "widget_launcher_icon": "chat",
        },
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(
            status_code=500, detail="Failed to remove launcher image."
        )

    logger.info("Launcher image removed for tenant %s", ctx.tenant_id[:8])

    return LauncherImageDeleteResponse(
        success=True,
        message="Launcher image removed. Widget will use the default chat icon.",
    )
