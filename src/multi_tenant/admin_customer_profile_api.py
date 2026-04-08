"""Admin Customer Profile API — Layer 1 profile management (WI #142).

Provides REST endpoints for the merchant admin dashboard to view and manage
customer profiles (Persistent Customer Memory Layer 1):

    GET    /api/admin/profiles                      — List profiles (paginated)
    GET    /api/admin/profiles/{customer_id}        — Get single profile
    PUT    /api/admin/profiles/{customer_id}/consent — Update consent status
    POST   /api/admin/profiles/{customer_id}/sync   — Trigger Shopify data sync
    DELETE /api/admin/profiles/{customer_id}        — Delete profile (GDPR)

All endpoints derive tenant_id from the authenticated TenantContext — never
from query parameters. Widget key authentication is NOT accepted on these
endpoints (scoped to /api/chat/* only).

Architecture references:
    - BACKLOG-NEW-WORK-ITEMS.md: WI #142 — Customer profile endpoints
    - Decision #28: Layer 1 — Customer context profile (6 data sources)
    - Decision #10: Consent management (gates Layers 2-4, not Layer 1)
    - Decision #1: TenantScopedRepository enforces tenant isolation

Dependencies:
    - customer_profile_service.py: CustomerProfileService (CRUD, sync, consent)
    - cosmos_schema.py: CustomerProfileDocument, ConsentStatus
    - middleware.py: get_tenant_context, TenantContext

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import ConsentStatus
from src.multi_tenant.middleware import get_tenant_context

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ContactAttributeResponse(BaseModel):
    """A linked contact attribute (ADR-004)."""

    attribute_type: str
    value: str
    verified: bool = False
    source: str = ""
    added_at: str = ""


class CustomerProfileResponse(BaseModel):
    """A single customer profile for the admin dashboard."""

    customer_id: str
    tenant_id: str
    # ADR-004: Canonical identity
    canonical_id: str = ""
    contact_attributes: list[ContactAttributeResponse] = Field(default_factory=list)
    consent_status: str
    purchase_history: list[dict[str, Any]] = Field(default_factory=list)
    product_questions: list[dict[str, Any]] = Field(default_factory=list)
    region_codes: dict[str, str] = Field(default_factory=dict)
    marketing_segments: list[str] = Field(default_factory=list)
    jurisdiction_codes: dict[str, str] = Field(default_factory=dict)
    cart_contents: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    updated_at: str | None = None
    last_interaction_at: str | None = None


class ProfileListResponse(BaseModel):
    """Paginated list of customer profiles."""

    tenant_id: str
    total: int = Field(description="Total matching profiles")
    offset: int
    limit: int
    profiles: list[CustomerProfileResponse]


class ConsentUpdateRequest(BaseModel):
    """Request body for PUT /api/admin/profiles/{customer_id}/consent."""

    consent_status: str = Field(
        description="New consent status: 'granted', 'denied', or 'not_asked'",
    )


class ConsentUpdateResponse(BaseModel):
    """Response for a consent update operation."""

    customer_id: str
    tenant_id: str
    previous_status: str
    new_status: str


class ShopifySyncRequest(BaseModel):
    """Request body for POST /api/admin/profiles/{customer_id}/sync."""

    shopify_data: dict[str, Any] = Field(
        description=(
            "Normalized Shopify data dict with optional keys: "
            "orders, cart, customer"
        ),
    )


class ShopifySyncResponse(BaseModel):
    """Response for a Shopify sync operation."""

    customer_id: str
    tenant_id: str
    synced_at: str


class ProfileDeleteResponse(BaseModel):
    """Response for a profile deletion."""

    customer_id: str
    tenant_id: str
    deleted: bool


# ---------------------------------------------------------------------------
# Valid consent values
# ---------------------------------------------------------------------------

VALID_CONSENT_STATUSES = {s.value for s in ConsentStatus}


# ---------------------------------------------------------------------------
# Service accessor
# ---------------------------------------------------------------------------

_profile_service: Any | None = None
_profile_repo: Any | None = None


def configure_admin_profile_services(
    profile_service: Any,
    profile_repo: Any | None = None,
) -> None:
    """Wire the admin profile API to its backing service.

    Called during app startup after CustomerProfileService is initialised.

    Args:
        profile_service: CustomerProfileService instance.
        profile_repo: Optional CustomerProfileRepository for list/count
            queries that are not on the service itself.
    """
    global _profile_service, _profile_repo
    _profile_service = profile_service
    _profile_repo = profile_repo
    logger.info("Admin customer profile API services configured")


def _get_service() -> Any:
    """Get the CustomerProfileService, raising 503 if not initialised."""
    if _profile_service is None:
        raise HTTPException(
            status_code=503,
            detail="Admin profile services not initialised",
        )
    return _profile_service


def _get_repo() -> Any:
    """Get the CustomerProfileRepository, raising 503 if not initialised."""
    if _profile_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Admin profile repository not initialised",
        )
    return _profile_repo


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/admin/profiles", tags=["admin-profiles"])


# ---------------------------------------------------------------------------
# GET /api/admin/profiles — List customer profiles (paginated)
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=ProfileListResponse,
    summary="List customer profiles",
    description="Returns a paginated list of customer profiles. Supports filtering by consent status, ordered by most recently updated first.",
    responses={
        400: {"description": "Invalid consent_status filter value"},
        503: {"description": "Admin profile repository not initialized"},
    },
)
async def list_profiles(
    consent_status: str | None = Query(
        None,
        description="Filter by consent status (granted, denied, not_asked)",
    ),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size (max 200)"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ProfileListResponse:
    """List customer profiles for the merchant admin dashboard.

    Supports filtering by consent status. Results are ordered by most
    recently updated first.
    """
    repo = _get_repo()

    # Validate consent_status filter if provided
    if consent_status is not None and consent_status not in VALID_CONSENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status '{consent_status}'. "
            f"Valid values: {sorted(VALID_CONSENT_STATUSES)}",
        )

    # Build query conditions
    conditions: list[str] = []
    params: list[dict[str, Any]] = []

    if consent_status is not None:
        conditions.append("c.consent_status = @consent_status")
        params.append({"name": "@consent_status", "value": consent_status})

    where = (" AND " + " AND ".join(conditions)) if conditions else ""

    # Count query
    count_query = f"SELECT VALUE COUNT(1) FROM c WHERE 1=1{where}"
    total = await repo.query_count(ctx.tenant_id, count_query, params)

    # Page query with OFFSET/LIMIT
    page_query = (
        f"SELECT * FROM c WHERE 1=1{where} "
        f"ORDER BY c.updated_at DESC "
        f"OFFSET {offset} LIMIT {limit}"
    )
    profiles_raw = await repo.query(ctx.tenant_id, page_query, params)

    profiles = [
        CustomerProfileResponse(
            customer_id=p.get("customer_id", ""),
            tenant_id=ctx.tenant_id,
            canonical_id=p.get("canonical_id", ""),
            contact_attributes=[
                ContactAttributeResponse(
                    attribute_type=a.get("attribute_type", ""),
                    value=a.get("value", ""),
                    verified=a.get("verified", False),
                    source=a.get("source", ""),
                    added_at=a.get("added_at", ""),
                )
                for a in p.get("contact_attributes", [])
            ],
            consent_status=p.get("consent_status", "not_asked"),
            purchase_history=p.get("purchase_history", []),
            product_questions=p.get("product_questions", []),
            region_codes=p.get("region_codes", {}),
            marketing_segments=p.get("marketing_segments", []),
            jurisdiction_codes=p.get("jurisdiction_codes", {}),
            cart_contents=p.get("cart_contents", {}),
            created_at=p.get("created_at"),
            updated_at=p.get("updated_at"),
            last_interaction_at=p.get("last_interaction_at"),
        )
        for p in profiles_raw
    ]

    return ProfileListResponse(
        tenant_id=ctx.tenant_id,
        total=total,
        offset=offset,
        limit=limit,
        profiles=profiles,
    )


# ---------------------------------------------------------------------------
# GET /api/admin/profiles/{customer_id} — Get single profile
# ---------------------------------------------------------------------------


@router.get(
    "/{customer_id}",
    response_model=CustomerProfileResponse,
    summary="Get customer profile",
    description="Returns the full Layer 1 profile for a single customer including all 6 data sources and consent status.",
    responses={
        404: {"description": "Customer profile not found"},
        503: {"description": "Admin profile services not initialized"},
    },
)
async def get_profile(
    customer_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> CustomerProfileResponse:
    """Get a single customer profile by customer_id.

    Returns the full Layer 1 profile including all 6 data sources
    and consent status.
    """
    service = _get_service()

    profile = await service.get_profile(ctx.tenant_id, customer_id)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer profile '{customer_id}' not found",
        )

    # ADR-004: Include canonical identity fields
    contact_attrs = [
        ContactAttributeResponse(
            attribute_type=a.attribute_type.value if hasattr(a.attribute_type, "value") else str(a.attribute_type),
            value=a.value,
            verified=a.verified,
            source=a.source,
            added_at=a.added_at,
        )
        for a in getattr(profile, "contact_attributes", [])
    ]

    return CustomerProfileResponse(
        customer_id=profile.customer_id,
        tenant_id=ctx.tenant_id,
        canonical_id=getattr(profile, "canonical_id", "") or "",
        contact_attributes=contact_attrs,
        consent_status=profile.consent_status.value
        if hasattr(profile.consent_status, "value")
        else str(profile.consent_status),
        purchase_history=profile.purchase_history,
        product_questions=profile.product_questions,
        region_codes=profile.region_codes,
        marketing_segments=profile.marketing_segments,
        jurisdiction_codes=profile.jurisdiction_codes,
        cart_contents=profile.cart_contents,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        last_interaction_at=profile.last_interaction_at,
    )


# ---------------------------------------------------------------------------
# PUT /api/admin/profiles/{customer_id}/consent — Update consent
# ---------------------------------------------------------------------------


@router.put(
    "/{customer_id}/consent",
    response_model=ConsentUpdateResponse,
    summary="Update customer consent",
    description="Updates a customer's GDPR consent status for Persistent Customer Memory. Setting to 'denied' may trigger deletion of Layer 2-4 data.",
    responses={
        400: {"description": "Invalid consent_status value"},
        404: {"description": "Customer profile not found"},
        503: {"description": "Admin profile services not initialized"},
    },
)
async def update_consent(
    customer_id: str,
    request: ConsentUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ConsentUpdateResponse:
    """Update a customer's GDPR consent status for Persistent Customer Memory.

    Setting consent to 'denied' prevents new Layer 2-4 data from being
    stored and may trigger deletion of existing Layer 2-4 data via the
    ConsentManager in gdpr_services.py. Layer 1 profile data is always
    retained regardless of consent status.
    """
    if request.consent_status not in VALID_CONSENT_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status '{request.consent_status}'. "
            f"Valid values: {sorted(VALID_CONSENT_STATUSES)}",
        )

    service = _get_service()

    # Get existing profile to capture previous status
    existing = await service.get_profile(ctx.tenant_id, customer_id)
    if existing is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer profile '{customer_id}' not found",
        )

    previous = (
        existing.consent_status.value
        if hasattr(existing.consent_status, "value")
        else str(existing.consent_status)
    )

    new_status = ConsentStatus(request.consent_status)
    await service.update_consent(ctx.tenant_id, customer_id, new_status)

    logger.info(
        "Customer consent updated via admin API: tenant=%s customer=%s %s -> %s",
        ctx.tenant_id[:8],
        customer_id,
        previous,
        request.consent_status,
    )

    return ConsentUpdateResponse(
        customer_id=customer_id,
        tenant_id=ctx.tenant_id,
        previous_status=previous,
        new_status=request.consent_status,
    )


# ---------------------------------------------------------------------------
# POST /api/admin/profiles/{customer_id}/sync — Shopify data sync
# ---------------------------------------------------------------------------


@router.post(
    "/{customer_id}/sync",
    response_model=ShopifySyncResponse,
    summary="Trigger Shopify data sync",
    description="Accepts normalized Shopify data and merges it into the customer's Layer 1 profile. This is the admin-initiated equivalent of the automatic webhook-driven sync.",
    responses={
        503: {"description": "Admin profile services not initialized"},
    },
)
async def sync_shopify_data(
    customer_id: str,
    request: ShopifySyncRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ShopifySyncResponse:
    """Trigger a Shopify data sync for a customer profile.

    Accepts normalized Shopify data and merges it into the customer's
    Layer 1 profile. This is the admin-initiated equivalent of the
    automatic webhook-driven sync path.

    Expected shopify_data structure:
        - orders: [{product_id, date, rating?, review_snippet?}]
        - cart: {active: [...], abandoned: [...]}
        - customer: {country_code, province_code, locale, tags}
    """
    service = _get_service()

    profile = await service.sync_from_shopify(
        tenant_id=ctx.tenant_id,
        customer_id=customer_id,
        shopify_data=request.shopify_data,
    )

    logger.info(
        "Shopify sync triggered via admin API: tenant=%s customer=%s",
        ctx.tenant_id[:8],
        customer_id,
    )

    return ShopifySyncResponse(
        customer_id=customer_id,
        tenant_id=ctx.tenant_id,
        synced_at=profile.updated_at,
    )


# ---------------------------------------------------------------------------
# DELETE /api/admin/profiles/{customer_id} — Delete profile (GDPR)
# ---------------------------------------------------------------------------


@router.delete(
    "/{customer_id}",
    response_model=ProfileDeleteResponse,
    summary="Delete customer profile",
    description="Removes the Layer 1 customer profile document for GDPR right to erasure. Does not automatically delete Layer 2-4 data; use the GDPR deletion API for comprehensive erasure.",
    responses={
        404: {"description": "Customer profile not found"},
        503: {"description": "Admin profile services not initialized"},
    },
)
async def delete_profile(
    customer_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ProfileDeleteResponse:
    """Delete a customer profile for GDPR right to erasure (Article 17).

    Removes the Layer 1 customer profile document. This does NOT
    automatically delete Layer 2-4 data (memory vectors, pattern
    extractions) — use the GDPR deletion API (/api/gdpr/delete) for
    comprehensive cross-store data erasure.
    """
    service = _get_service()

    deleted = await service.delete_profile(ctx.tenant_id, customer_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Customer profile '{customer_id}' not found",
        )

    logger.info(
        "Customer profile deleted via admin API: tenant=%s customer=%s",
        ctx.tenant_id[:8],
        customer_id,
    )

    return ProfileDeleteResponse(
        customer_id=customer_id,
        tenant_id=ctx.tenant_id,
        deleted=True,
    )
