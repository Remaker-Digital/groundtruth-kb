"""
Avatar upload endpoint — D22 capability.

Accepts PNG/JPEG avatar images, validates format and size, stores as
base64 data URI in the tenant's config (widget_agent_avatar_url field).

Routes:
    POST /api/admin/avatar/upload — Upload avatar image (PNG/JPEG, max 256KB)
    DELETE /api/admin/avatar       — Remove avatar (reset to default)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import base64
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from src.multi_tenant.middleware import get_tenant_context, TenantContext

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_AVATAR_BYTES = 256 * 1024  # 256KB
ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg"}
MIME_TO_EXT = {"image/png": "png", "image/jpeg": "jpeg", "image/jpg": "jpeg"}

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AvatarUploadResponse(BaseModel):
    """Response for avatar upload."""

    success: bool
    avatar_url: str | None = Field(
        default=None,
        description="Data URI of the uploaded avatar (base64-encoded)",
    )
    size_bytes: int = 0
    message: str = ""


class AvatarDeleteResponse(BaseModel):
    """Response for avatar deletion."""

    success: bool
    message: str = ""


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/avatar", tags=["admin-avatar"])


@router.post("/upload", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(..., description="Avatar image (PNG or JPEG, max 256KB)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> AvatarUploadResponse:
    """Upload an avatar image for the chat widget agent.

    The image is validated for format (PNG/JPEG) and size (max 256KB),
    then stored as a base64 data URI in the tenant's config
    (widget_agent_avatar_url field).
    """
    # Validate content type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{content_type}'. Allowed: PNG, JPEG.",
        )

    # Read and validate size
    data = await file.read()
    if len(data) > MAX_AVATAR_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(data)} bytes). Maximum: {MAX_AVATAR_BYTES} bytes (256KB).",
        )

    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")

    # Encode as data URI
    mime = "image/png" if content_type == "image/png" else "image/jpeg"
    b64 = base64.b64encode(data).decode("ascii")
    data_uri = f"data:{mime};base64,{b64}"

    # Persist to draft via activation service (handles draft-only tenants)
    from src.multi_tenant.activation_service import get_activation_service

    activation_svc = get_activation_service()
    result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        changes={"widget_agent_avatar_url": data_uri},
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(status_code=500, detail="Failed to save avatar.")

    logger.info(
        "Avatar uploaded for tenant %s: %d bytes, %s",
        ctx.tenant_id[:8], len(data), mime,
    )

    return AvatarUploadResponse(
        success=True,
        avatar_url=data_uri,
        size_bytes=len(data),
        message="Avatar uploaded successfully.",
    )


@router.delete("", response_model=AvatarDeleteResponse)
async def delete_avatar(
    ctx: TenantContext = Depends(get_tenant_context),
) -> AvatarDeleteResponse:
    """Remove the avatar image (resets to default)."""
    from src.multi_tenant.activation_service import get_activation_service

    activation_svc = get_activation_service()
    result = await activation_svc.save_draft(
        tenant_id=ctx.tenant_id,
        tier=ctx.tier,
        changes={"widget_agent_avatar_url": None},
        actor=f"admin:{ctx.tenant_id}",
    )

    if not result or not result.success:
        raise HTTPException(status_code=500, detail="Failed to remove avatar.")

    logger.info("Avatar removed for tenant %s", ctx.tenant_id[:8])

    return AvatarDeleteResponse(
        success=True,
        message="Avatar removed. Default avatar will be used.",
    )
