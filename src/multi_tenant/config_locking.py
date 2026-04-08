"""Configuration optimistic locking — prevents concurrent overwrites (C14).

Uses Cosmos DB ETags for optimistic concurrency control. When saving a draft,
the client must provide the ETag received from the last read. If another user
has modified the document in between, the ETag won't match and the save is
rejected with 409 Conflict.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)


class ConfigLockStatus(CamelCaseModel):
    """Current lock/version status of a config document."""

    tenant_id: str
    config_state: str
    etag: str = Field(description="Cosmos DB ETag — pass this on save to prevent overwrites")
    version: int
    last_modified_by: str | None = None
    last_modified_at: str | None = None


class ConfigSaveWithLockRequest(CamelCaseModel):
    """Request body that includes an etag for optimistic locking."""

    etag: str = Field(description="ETag from the last config read. Required to prevent concurrent overwrites.")
    changes: dict[str, Any] = Field(description="Config fields to update")


class ConfigConflictResponse(CamelCaseModel):
    """409 Conflict response with details about who modified the config."""

    detail: str
    current_etag: str
    last_modified_by: str | None = None
    last_modified_at: str | None = None


router = APIRouter(prefix="/api/admin/config/lock", tags=["config-locking"])


# Module-level service reference
_preferences_repo = None


def configure_config_locking(preferences_repo) -> None:
    """Wire the preferences repository into the config locking module."""
    global _preferences_repo
    _preferences_repo = preferences_repo
    logger.info("Config locking service configured")


def _get_repo():
    if _preferences_repo is None:
        raise HTTPException(status_code=503, detail="Config locking service not initialised")
    return _preferences_repo


@router.get(
    "/status",
    response_model=ConfigLockStatus,
    summary="Get current config lock status",
    description=(
        "Returns the current ETag and version of the draft config. Use this ETag when saving to prevent concurrent "
        "overwrites."
    ),
)
async def get_lock_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigLockStatus:
    """Get the current etag/version of the draft config."""
    repo = _get_repo()

    # Read the draft preferences document
    docs = await repo.query(
        tenant_id=ctx.tenant_id,
        query_text="SELECT * FROM c WHERE c.config_state = 'draft' ORDER BY c.version DESC",
        parameters=[],
        max_items=1,
    )

    if not docs:
        # No draft — return the active config's etag
        docs = await repo.query(
            tenant_id=ctx.tenant_id,
            query_text=(
                "SELECT * FROM c WHERE (c.config_state = 'active' "
                "OR NOT IS_DEFINED(c.config_state)) ORDER BY c.version DESC"
            ),
            parameters=[],
            max_items=1,
        )

    if not docs:
        raise HTTPException(status_code=404, detail="No configuration found")

    doc = docs[0]
    return ConfigLockStatus(
        tenant_id=ctx.tenant_id,
        config_state=doc.get("config_state", "active"),
        etag=doc.get("_etag", ""),
        version=doc.get("version", 0),
        last_modified_by=doc.get("last_modified_by"),
        last_modified_at=doc.get("updated_at"),
    )


@router.post(
    "/validate",
    response_model=ConfigLockStatus,
    summary="Validate an ETag is still current",
    description="Checks if the provided ETag matches the current document. Returns 409 if stale.",
    responses={409: {"model": ConfigConflictResponse}},
)
async def validate_etag(
    etag: str = Query(..., description="ETag to validate"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConfigLockStatus:
    """Validate that an ETag is still current (not stale)."""
    repo = _get_repo()

    docs = await repo.query(
        tenant_id=ctx.tenant_id,
        query_text="SELECT * FROM c WHERE c.config_state = 'draft' ORDER BY c.version DESC",
        parameters=[],
        max_items=1,
    )

    if not docs:
        docs = await repo.query(
            tenant_id=ctx.tenant_id,
            query_text=(
                "SELECT * FROM c WHERE (c.config_state = 'active' "
                "OR NOT IS_DEFINED(c.config_state)) ORDER BY c.version DESC"
            ),
            parameters=[],
            max_items=1,
        )

    if not docs:
        raise HTTPException(status_code=404, detail="No configuration found")

    doc = docs[0]
    current_etag = doc.get("_etag", "")

    if current_etag != etag:
        raise HTTPException(
            status_code=409,
            detail="Configuration has been modified by another user. Please refresh and try again.",
        )

    return ConfigLockStatus(
        tenant_id=ctx.tenant_id,
        config_state=doc.get("config_state", "active"),
        etag=current_etag,
        version=doc.get("version", 0),
        last_modified_by=doc.get("last_modified_by"),
        last_modified_at=doc.get("updated_at"),
    )
