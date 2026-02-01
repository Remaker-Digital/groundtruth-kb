"""Admin GDPR API — data export, deletion, and consent management (WI #180).

Provides REST endpoints for the merchant admin dashboard's Settings page
GDPR controls:

    POST /api/gdpr/export           — Export tenant or customer data
    POST /api/gdpr/delete           — Delete tenant or customer data
    GET  /api/gdpr/consent          — Get tenant consent status
    PUT  /api/gdpr/consent          — Update tenant consent status
    PUT  /api/gdpr/consent/customer — Update customer consent status

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* only).

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §7: WI #180 — GDPR endpoints
    - Decision #7-10: PII scrubbing, grace periods, export/deletion, consent
    - gdpr_services.py: DataExportService, DataDeletionService, ConsentManager

Dependencies:
    - gdpr_services.py: DataExportService, DataDeletionService,
      ConsentManager, DataStoreRegistry, GracePeriodActiveError
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ExportRequest(BaseModel):
    """Request body for POST /api/gdpr/export."""

    scope: str = Field(
        description="Export scope: 'tenant' (all data) or 'customer' (single customer)",
    )
    customer_id: str | None = Field(
        default=None,
        description="Customer ID (required when scope='customer')",
    )


class ExportResponse(BaseModel):
    """Response for a data export operation."""

    export_id: str
    tenant_id: str
    customer_id: str | None = None
    export_type: str = Field(description="'tenant' or 'customer'")
    stores_exported: list[str] = Field(description="Data stores that were exported")
    data: dict[str, Any] = Field(description="Exported data by store")
    exported_at: str
    errors: list[str] = Field(default_factory=list)


class DeleteRequest(BaseModel):
    """Request body for POST /api/gdpr/delete."""

    scope: str = Field(
        description="Deletion scope: 'tenant' (all data) or 'customer' (single customer)",
    )
    customer_id: str | None = Field(
        default=None,
        description="Customer ID (required when scope='customer')",
    )
    force: bool = Field(
        default=False,
        description="Skip grace period check (tenant scope only)",
    )


class DeleteResponse(BaseModel):
    """Response for a data deletion operation."""

    deletion_id: str
    tenant_id: str
    customer_id: str | None = None
    deletion_type: str = Field(description="'tenant' or 'customer'")
    stores_deleted: list[str] = Field(description="Data stores that were deleted from")
    details: dict[str, Any] = Field(description="Per-store deletion results")
    deleted_at: str
    errors: list[str] = Field(default_factory=list)


class ConsentStatusResponse(BaseModel):
    """Response for GET /api/gdpr/consent."""

    tenant_id: str
    consent_status: str = Field(description="Current consent status: granted, denied, or not_asked")


class UpdateConsentRequest(BaseModel):
    """Request body for PUT /api/gdpr/consent."""

    consent_status: str = Field(
        description="New consent status: 'granted' or 'denied'",
    )


class UpdateConsentResponse(BaseModel):
    """Response for consent update operations."""

    tenant_id: str
    customer_id: str | None = None
    previous_status: str | None = None
    new_status: str


class UpdateCustomerConsentRequest(BaseModel):
    """Request body for PUT /api/gdpr/consent/customer."""

    customer_id: str = Field(description="Customer identifier")
    consent_status: str = Field(
        description="New consent status: 'granted' or 'denied'",
    )


# ---------------------------------------------------------------------------
# Valid consent statuses
# ---------------------------------------------------------------------------

VALID_CONSENT_STATUSES = {"granted", "denied"}


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_export_service: Any | None = None
_deletion_service: Any | None = None
_consent_manager: Any | None = None
_tenant_repo: Any | None = None


def configure_admin_gdpr_services(
    export_service: Any,
    deletion_service: Any,
    consent_manager: Any,
    tenant_repo: Any | None = None,
) -> None:
    """Wire the admin GDPR API to its backing services.

    Called during app startup after GDPR services are initialised.
    """
    global _export_service, _deletion_service, _consent_manager, _tenant_repo
    _export_service = export_service
    _deletion_service = deletion_service
    _consent_manager = consent_manager
    _tenant_repo = tenant_repo
    logger.info("Admin GDPR API services configured")


def _get_export_service() -> Any:
    if _export_service is None:
        raise HTTPException(
            status_code=503,
            detail="GDPR export services not initialised",
        )
    return _export_service


def _get_deletion_service() -> Any:
    if _deletion_service is None:
        raise HTTPException(
            status_code=503,
            detail="GDPR deletion services not initialised",
        )
    return _deletion_service


def _get_consent_manager() -> Any:
    if _consent_manager is None:
        raise HTTPException(
            status_code=503,
            detail="GDPR consent services not initialised",
        )
    return _consent_manager


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/gdpr", tags=["admin-gdpr"])


# ---------------------------------------------------------------------------
# POST /api/gdpr/export — Export tenant or customer data
# ---------------------------------------------------------------------------


@router.post("/export", response_model=ExportResponse)
async def export_data(
    request: ExportRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ExportResponse:
    """Export data for GDPR right of access (Article 15) and portability (Article 20).

    Exports all data from registered data stores. Scope determines
    whether the entire tenant's data or a specific customer's data is exported.
    """
    if request.scope not in ("tenant", "customer"):
        raise HTTPException(
            status_code=400,
            detail="Invalid scope. Must be 'tenant' or 'customer'.",
        )

    if request.scope == "customer" and not request.customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id is required when scope='customer'.",
        )

    service = _get_export_service()

    if request.scope == "tenant":
        result = await service.export_tenant(ctx.tenant_id)
    else:
        result = await service.export_customer(ctx.tenant_id, request.customer_id)

    logger.info(
        "GDPR export completed: scope=%s tenant=%s customer=%s export_id=%s",
        request.scope,
        ctx.tenant_id[:8],
        request.customer_id,
        result.export_id,
    )

    return ExportResponse(
        export_id=result.export_id,
        tenant_id=result.tenant_id,
        customer_id=result.customer_id,
        export_type=result.export_type,
        stores_exported=result.stores_exported,
        data=result.data,
        exported_at=result.exported_at,
        errors=result.errors,
    )


# ---------------------------------------------------------------------------
# POST /api/gdpr/delete — Delete tenant or customer data
# ---------------------------------------------------------------------------


@router.post("/delete", response_model=DeleteResponse)
async def delete_data(
    request: DeleteRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeleteResponse:
    """Delete data for GDPR right to erasure (Article 17).

    Performs cascading deletion across all registered data stores.
    Tenant-level deletion checks the grace period unless force=True.
    Customer-level deletion proceeds immediately (GDPR requires
    processing without undue delay).
    """
    if request.scope not in ("tenant", "customer"):
        raise HTTPException(
            status_code=400,
            detail="Invalid scope. Must be 'tenant' or 'customer'.",
        )

    if request.scope == "customer" and not request.customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id is required when scope='customer'.",
        )

    service = _get_deletion_service()

    from src.multi_tenant.gdpr_services import GracePeriodActiveError

    try:
        if request.scope == "tenant":
            result = await service.delete_tenant(
                ctx.tenant_id, force=request.force,
            )
        else:
            result = await service.delete_customer(
                ctx.tenant_id, request.customer_id,
            )
    except GracePeriodActiveError as exc:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Grace period still active for tenant. "
                f"Data deletion blocked until {exc.grace_period_ends_at}. "
                f"Use force=true to override."
            ),
        )

    logger.info(
        "GDPR deletion completed: scope=%s tenant=%s customer=%s deletion_id=%s",
        request.scope,
        ctx.tenant_id[:8],
        request.customer_id,
        result.deletion_id,
    )

    return DeleteResponse(
        deletion_id=result.deletion_id,
        tenant_id=result.tenant_id,
        customer_id=result.customer_id,
        deletion_type=result.deletion_type,
        stores_deleted=result.stores_deleted,
        details=result.details,
        deleted_at=result.deleted_at,
        errors=result.errors,
    )


# ---------------------------------------------------------------------------
# GET /api/gdpr/consent — Get tenant consent status
# ---------------------------------------------------------------------------


@router.get("/consent", response_model=ConsentStatusResponse)
async def get_consent_status(
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConsentStatusResponse:
    """Get the tenant's current consent status for Persistent Customer Memory.

    Consent gates Layers 2-4 of the memory system. Layer 1 (basic
    customer profiles) is always active regardless of consent.
    """
    if _tenant_repo is None:
        raise HTTPException(
            status_code=503,
            detail="GDPR consent services not initialised",
        )

    try:
        tenant_doc = await _tenant_repo.read(ctx.tenant_id, ctx.tenant_id)
        consent = tenant_doc.get("consent_status", "not_asked")
    except Exception:
        logger.exception(
            "Error reading tenant consent: tenant=%s", ctx.tenant_id[:8],
        )
        consent = "not_asked"

    return ConsentStatusResponse(
        tenant_id=ctx.tenant_id,
        consent_status=consent,
    )


# ---------------------------------------------------------------------------
# PUT /api/gdpr/consent — Update tenant consent status
# ---------------------------------------------------------------------------


@router.put("/consent", response_model=UpdateConsentResponse)
async def update_consent(
    request: UpdateConsentRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> UpdateConsentResponse:
    """Update the tenant's consent status for Persistent Customer Memory.

    Setting consent to 'denied' prevents new Layer 2-4 data from being
    stored. Existing data is not automatically deleted at the tenant
    level — use customer-level consent denial or explicit data deletion
    for individual customer data removal.
    """
    if request.consent_status not in VALID_CONSENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status '{request.consent_status}'. "
            f"Valid values: {sorted(VALID_CONSENT_STATUSES)}",
        )

    manager = _get_consent_manager()

    from src.multi_tenant.cosmos_schema import ConsentStatus

    new_status = ConsentStatus(request.consent_status)
    result = await manager.update_tenant_consent(
        tenant_id=ctx.tenant_id,
        new_status=new_status,
        actor=ctx.user_id or "admin",
    )

    logger.info(
        "Tenant consent updated: tenant=%s %s → %s",
        ctx.tenant_id[:8],
        result.get("previous_status"),
        result.get("new_status"),
    )

    return UpdateConsentResponse(
        tenant_id=ctx.tenant_id,
        previous_status=result.get("previous_status"),
        new_status=result.get("new_status", request.consent_status),
    )


# ---------------------------------------------------------------------------
# PUT /api/gdpr/consent/customer — Update customer consent status
# ---------------------------------------------------------------------------


@router.put("/consent/customer", response_model=UpdateConsentResponse)
async def update_customer_consent(
    request: UpdateCustomerConsentRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> UpdateConsentResponse:
    """Update a specific customer's consent status.

    Setting consent to 'denied' triggers automatic deletion of the
    customer's Layer 2-4 data (memory vectors, pattern extractions)
    per GDPR Article 17. Layer 1 profile data is retained for
    operational purposes.
    """
    if request.consent_status not in VALID_CONSENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status '{request.consent_status}'. "
            f"Valid values: {sorted(VALID_CONSENT_STATUSES)}",
        )

    manager = _get_consent_manager()

    from src.multi_tenant.cosmos_schema import ConsentStatus

    new_status = ConsentStatus(request.consent_status)
    result = await manager.update_customer_consent(
        tenant_id=ctx.tenant_id,
        customer_id=request.customer_id,
        new_status=new_status,
        actor=ctx.user_id or "admin",
    )

    logger.info(
        "Customer consent updated: tenant=%s customer=%s %s → %s",
        ctx.tenant_id[:8],
        request.customer_id,
        result.get("previous_status"),
        result.get("new_status"),
    )

    return UpdateConsentResponse(
        tenant_id=ctx.tenant_id,
        customer_id=request.customer_id,
        previous_status=result.get("previous_status"),
        new_status=result.get("new_status", request.consent_status),
    )
