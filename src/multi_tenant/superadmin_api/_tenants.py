"""Superadmin API -- Tenant directory, CRUD, tier override, expiry.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Body, Depends, HTTPException, Query
from pydantic import Field, field_validator

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType, TenantTier
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


class TenantSummaryItem(CamelCaseModel):
    """Single tenant in the directory listing.

    SPEC-1843 v6 boundary: ``customer_email`` and ``shopify_shop_domain``
    are TENANCY MANAGEMENT data (SPEC-1637: required for tenancy setup,
    billing, and technical communication).  These are superadmin contact
    and storefront identifiers, NOT end-customer PII.

    WI-1641: fields restored after S137 audit found WI-1611 over-applied
    the ZK mandate.
    """

    tenant_id: str
    status: str
    tier: str | None = None
    billing_channel: str | None = None
    customer_email: str | None = None
    shopify_shop_domain: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    deactivated_at: str | None = None
    consent_status: str | None = None
    expires_at: str | None = None


class TenantDirectoryResponse(CamelCaseModel):
    """Paginated tenant directory response."""


    tenants: list[TenantSummaryItem]
    total: int
    skip: int
    limit: int


class TenantDistributionSummary(CamelCaseModel):
    """Aggregate tenant distribution statistics."""


    total_tenants: int = 0
    by_status: dict[str, int] = Field(default_factory=dict)
    by_tier: dict[str, int] = Field(default_factory=dict)
    by_billing_channel: dict[str, int] = Field(default_factory=dict)


class TierOverrideResponse(CamelCaseModel):
    """Response after setting a tenant's subscription tier."""

    tenant_id: str
    previous_tier: str | None = None
    new_tier: str
    updated_at: str


VALID_TIERS = {t.value for t in TenantTier}

class CreateTenantRequest(CamelCaseModel):
    """Request body for SPA tenant creation."""

    merchant_name: str = Field(
        ..., min_length=1, max_length=200,
        description="Merchant display name (becomes brand_name in preferences)",
    )
    merchant_url: str | None = Field(
        default=None, max_length=500,
        description="Merchant website or Shopify domain (optional)",
    )
    superadmin_email: str = Field(
        ..., min_length=5, max_length=320,
        description="Tenant owner email — receives welcome email + SUPERADMIN key",
    )

    @field_validator("superadmin_email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        import re
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError("Invalid email address format")
        return v
    tier: str = Field(
        ...,
        description="Subscription tier: trial, starter, professional, or enterprise",
    )
    expires_at: str | None = Field(
        default=None,
        description="Optional ISO 8601 expiry timestamp. When set, tenant access "
        "is blocked after this time. Omit or null for no expiry.",
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError("expires_at must be a valid ISO 8601 timestamp")
        return v


class CreateTenantResponse(CamelCaseModel):
    """Response from SPA tenant creation.

    SPEC-1673: Raw tenant API keys are NEVER returned in API responses.
    Keys are delivered directly to the tenant superadmin via email only.
    The provider operator sees delivery status, not raw credentials.
    """

    tenant_id: str
    status: str
    tier: str
    superadmin_email: str
    keys_delivered_via_email: bool = False
    warnings: list[str] = Field(default_factory=list)


class ResendWelcomeEmailResponse(CamelCaseModel):
    """Response from resending a welcome email."""

    tenant_id: str
    sent_to: str
    sent: bool
    message: str


class SetExpiryRequest(CamelCaseModel):
    """Request body for setting/clearing tenant access expiry."""

    expires_at: str | None = Field(
        description="ISO 8601 timestamp for access expiry, or null to remove expiry.",
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError("expires_at must be a valid ISO 8601 timestamp")
        return v


class SetExpiryResponse(CamelCaseModel):
    """Response from setting/clearing tenant access expiry."""

    tenant_id: str
    previous_expires_at: str | None
    new_expires_at: str | None
    updated_at: str

# ---------------------------------------------------------------------------
# RB-2: Tenant Directory
# ---------------------------------------------------------------------------


@router.get(
    "/tenants",
    response_model=TenantDirectoryResponse,
    summary="List all tenants (cross-partition)",
    description=(
        "Provider-only: lists all tenants with filtering by status, tier, "
        "and billing channel. Performs a cross-partition Cosmos DB query."
    ),
    status_code=200,
)
async def list_all_tenants(

    status: str | None = Query(None, description="Filter by tenant status"),
    tier: str | None = Query(None, description="Filter by subscription tier"),
    billing_channel: str | None = Query(None, description="Filter by billing channel"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=500, description="Page size"),
) -> TenantDirectoryResponse:
    """List all tenants across all partitions with optional filtering."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Build cross-partition query
    conditions = []
    params: list[dict[str, Any]] = []

    if status:
        conditions.append("c.status = @status")
        params.append({"name": "@status", "value": status})
    if tier:
        conditions.append("c.tier = @tier")
        params.append({"name": "@tier", "value": tier})
    if billing_channel:
        conditions.append("c.billing_channel = @billing_channel")
        params.append({"name": "@billing_channel", "value": billing_channel})

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Count query
    count_query = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"
    total = 0
    async for item in _state._tenant_repo._container.query_items(
        query=count_query,
        parameters=params if params else None,
        max_item_count=1,
    ):
        total = item

    # Data query with pagination via OFFSET/LIMIT
    # SPEC-1843 v6 / WI-1641: customer_email and shopify_shop_domain restored
    # (tenancy management data per SPEC-1637)
    data_query = (
        f"SELECT c.tenant_id, c.status, c.tier, c.billing_channel, "
        f"c.customer_email, c.shopify_shop_domain, "
        f"c.created_at, c.updated_at, c.deactivated_at, "
        f"c.consent_status, c.expires_at "
        f"FROM c WHERE {where_clause} "
        f"ORDER BY c.created_at DESC "
        f"OFFSET {skip} LIMIT {limit}"
    )

    tenants: list[TenantSummaryItem] = []
    async for item in _state._tenant_repo._container.query_items(
        query=data_query,
        parameters=params if params else None,
        max_item_count=limit,
    ):
        tenants.append(TenantSummaryItem(**item))

    return TenantDirectoryResponse(
        tenants=tenants,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/tenants/summary",
    response_model=TenantDistributionSummary,
    summary="Tenant distribution summary",
    description="Aggregate counts by status, tier, and billing channel.",
    status_code=200,
)
async def tenant_summary(

) -> TenantDistributionSummary:
    """Get aggregate tenant distribution statistics."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    by_status: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    by_channel: dict[str, int] = {}
    total = 0

    query = (
        "SELECT c.status, c.tier, c.billing_channel FROM c"
    )
    async for item in _state._tenant_repo._container.query_items(
        query=query,
        max_item_count=500,
    ):
        total += 1
        s = item.get("status", "unknown")
        t = item.get("tier", "unknown") or "unknown"
        ch = item.get("billing_channel", "unknown") or "unknown"
        by_status[s] = by_status.get(s, 0) + 1
        by_tier[t] = by_tier.get(t, 0) + 1
        by_channel[ch] = by_channel.get(ch, 0) + 1

    return TenantDistributionSummary(
        total_tenants=total,
        by_status=by_status,
        by_tier=by_tier,
        by_billing_channel=by_channel,
    )


# ---------------------------------------------------------------------------
# Tier Override — Private support/testing control
# ---------------------------------------------------------------------------


class TierOverrideResponse(CamelCaseModel):
    """Response after setting a tenant's subscription tier."""

    tenant_id: str
    previous_tier: str | None = None
    new_tier: str
    updated_at: str


VALID_TIERS = {t.value for t in TenantTier}


@router.put(
    "/tenants/{tenant_id}/tier",
    response_model=TierOverrideResponse,
    summary="Override tenant tier (testing/support use)",
    description="Directly set a tenant's subscription tier. Intended for testing "
    "entitlement enforcement and support escalation. Does not interact "
    "with Stripe — use the billing upgrade flow for customer-facing changes.",
    responses={
        400: {"description": "Invalid tier value"},
        404: {"description": "Tenant not found"},
        503: {"description": "Service not initialized"},
    },
    status_code=200,
)
async def override_tenant_tier(
    tenant_id: str,
    tier: str = Body(..., embed=True, description="New tier value"),

) -> TierOverrideResponse:
    """Set a tenant's tier directly, bypassing Stripe."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Validate tier value
    if tier not in VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{tier}'. Valid values: {sorted(VALID_TIERS)}",
        )

    # Read current tenant document
    try:
        doc = await _state._tenant_repo.read(tenant_id, tenant_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    previous_tier = doc.get("tier")
    now = datetime.now(timezone.utc).isoformat()

    # Patch the tier field
    operations = [
        {"op": "set", "path": "/tier", "value": tier},
        {"op": "set", "path": "/updated_at", "value": now},
    ]
    await _state._tenant_repo.patch(tenant_id, tenant_id, operations)

    logger.info(
        "Tier override: tenant=%s %s -> %s (by %s)",
        tenant_id[:12],
        previous_tier or "none",
        tier,
        "spa-console",
    )

    return TierOverrideResponse(
        tenant_id=tenant_id,
        previous_tier=previous_tier,
        new_tier=tier,
        updated_at=now,
    )


# ---------------------------------------------------------------------------
# P0-PROV-1: SPA Console Tenant Provisioning
# ---------------------------------------------------------------------------


class CreateTenantRequest(CamelCaseModel):
    """Request body for SPA tenant creation."""

    merchant_name: str = Field(
        ..., min_length=1, max_length=200,
        description="Merchant display name (becomes brand_name in preferences)",
    )
    merchant_url: str | None = Field(
        default=None, max_length=500,
        description="Merchant website or Shopify domain (optional)",
    )
    superadmin_email: str = Field(
        ..., min_length=5, max_length=320,
        description="Tenant owner email — receives welcome email + SUPERADMIN key",
    )

    @field_validator("superadmin_email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        import re
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", v):
            raise ValueError("Invalid email address format")
        return v
    tier: str = Field(
        ...,
        description="Subscription tier: trial, starter, professional, or enterprise",
    )
    expires_at: str | None = Field(
        default=None,
        description="Optional ISO 8601 expiry timestamp. When set, tenant access "
        "is blocked after this time. Omit or null for no expiry.",
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError("expires_at must be a valid ISO 8601 timestamp")
        return v


class CreateTenantResponse(CamelCaseModel):
    """Response from SPA tenant creation.

    SPEC-1673: Raw tenant API keys are NEVER returned in API responses.
    Keys are delivered directly to the tenant superadmin via email only.
    The provider operator sees delivery status, not raw credentials.
    """

    tenant_id: str
    status: str
    tier: str
    superadmin_email: str
    keys_delivered_via_email: bool = False
    warnings: list[str] = Field(default_factory=list)


@router.post(
    "/tenants",
    response_model=CreateTenantResponse,
    summary="Provision a new tenant (SPA Console)",
    description=(
        "Creates a fully provisioned tenant with SUPERADMIN team member, "
        "widget key, and welcome email. For use by the service provider "
        "administrator — not exposed to merchants."
    ),
    responses={
        400: {"description": "Invalid tier value"},
        503: {"description": "Service not initialized"},
    },
    status_code=201,
)
async def create_tenant(
    body: CreateTenantRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> CreateTenantResponse:
    """Provision a new tenant from the SPA Console.

    Orchestrates the full lifecycle: create tenant → activate → provision
    superadmin → generate widget key → send welcome email. Partial failures
    are captured in the ``warnings`` field — the tenant is still created.
    """
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # SPEC-1667: Router-level require_platform_admin() guard ensures
    # only SPA platform admin keys reach this endpoint.

    # Validate tier against TenantTier enum
    if body.tier not in VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{body.tier}'. Valid values: {sorted(VALID_TIERS)}",
        )

    # Import provisioning orchestrator (lazy — avoids circular imports)
    from src.integrations.provisioning import spa_provision_tenant

    try:
        result = await spa_provision_tenant(
            merchant_name=body.merchant_name,
            merchant_url=body.merchant_url,
            superadmin_email=body.superadmin_email,
            tier=body.tier,
        )
    except RuntimeError as exc:
        logger.error("SPA tenant creation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error during SPA tenant creation: %s", exc)
        raise HTTPException(status_code=500, detail=f"Provisioning failed: {exc}")

    # Create default preferences document with merchant name.
    # IMPORTANT: Carry forward widget_key from provisioning step 4.
    # auto_provision_widget_key() creates a seed (version 0), but this
    # version 1 doc shadows it (get_active → ORDER BY version DESC).
    # Without widget_key here, activation is blocked (CP.6 defect).
    try:
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        now_iso = datetime.now(timezone.utc).isoformat()
        prefs_kwargs: dict[str, Any] = {
            "id": f"{result.tenant_id}:1",
            "tenant_id": result.tenant_id,
            "version": 1,
            "is_current": True,
            "brand_name": body.merchant_name,
            "created_at": now_iso,
            "created_by": ctx.team_member_email or "spa-console",
        }
        if result.widget_key:
            prefs_kwargs["widget_key"] = result.widget_key
        prefs_doc = PreferencesDocument(**prefs_kwargs)

        if _state._prefs_repo:
            try:
                await _state._prefs_repo.create(result.tenant_id, prefs_doc)
            except Exception:
                await _state._prefs_repo.upsert(result.tenant_id, prefs_doc)
    except Exception as exc:
        logger.warning("Failed to create preferences for %s: %s", result.tenant_id, exc)
        result.errors.append(f"Preferences creation failed: {exc}")

    # Set expires_at if provided (WI-EXPIRY-1)
    if body.expires_at and _state._tenant_repo:
        try:
            await _state._tenant_repo.patch(
                tenant_id=result.tenant_id,
                document_id=result.tenant_id,
                operations=[
                    {"op": "set", "path": "/expires_at", "value": body.expires_at},
                    {"op": "set", "path": "/updated_at", "value": datetime.now(timezone.utc).isoformat()},
                ],
            )
        except Exception as exc:
            logger.warning("Failed to set expires_at for %s: %s", result.tenant_id, exc)
            result.errors.append(f"Expiry date setting failed: {exc}")

    # Audit log entry — SPEC-1843: route through log_event() for sanitization
    try:
        if _state._audit_repo:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.TENANT_CREATED,
                tenant_id=result.tenant_id,
                actor=ctx.team_member_email or "spa-console",
                actor_type="admin",
                payload={
                    "action": "spa_tenant_created",
                    "result": "success" if not result.errors else "partial",
                },
            )
    except Exception as exc:
        logger.warning("Audit log failed for SPA tenant creation: %s", exc)

    logger.info(
        "SPA tenant created: tenant=%s tier=%s email=%s (by %s)",
        result.tenant_id[:12],
        body.tier,
        body.superadmin_email,
        ctx.team_member_email or "unknown",
    )

    # SPEC-1673: Raw keys are NEVER returned in the API response.
    # Keys were already emailed to the tenant superadmin in Step 5 of
    # spa_provision_tenant(). The provider operator only sees whether
    # email delivery succeeded.
    email_succeeded = not any("email failed" in e.lower() for e in result.errors)

    return CreateTenantResponse(
        tenant_id=result.tenant_id,
        status=result.status,
        tier=result.tier,
        superadmin_email=result.superadmin_email,
        keys_delivered_via_email=email_succeeded,
        warnings=result.errors,
    )


# ---------------------------------------------------------------------------
# Resend Welcome Email
# ---------------------------------------------------------------------------


class ResendWelcomeEmailResponse(CamelCaseModel):
    """Response from resending a welcome email."""

    tenant_id: str
    sent_to: str
    sent: bool
    message: str


@router.post(
    "/tenants/{tenant_id}/resend-welcome-email",
    response_model=ResendWelcomeEmailResponse,
    summary="Resend welcome email to a tenant",
    description=(
        "Re-sends the welcome/onboarding email to the tenant's registered "
        "email address. The email includes the admin login URL and onboarding "
        "steps but does NOT include raw API keys (those are only available at "
        "creation time). Use this after correcting email templates or when "
        "the original email was not received."
    ),
    responses={
        404: {"description": "Tenant not found"},
        422: {"description": "No email address on record for this tenant"},
        503: {"description": "Service not initialized"},
    },
)
async def resend_welcome_email(
    tenant_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ResendWelcomeEmailResponse:
    """Resend the welcome email to a tenant's registered email."""
    if not _state._tenant_repo or not _state._prefs_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # SPEC-1667: Router-level require_platform_admin() guard ensures
    # only SPA platform admin keys reach this endpoint.

    # Read the target tenant
    tenant = await _state._tenant_repo.read(tenant_id, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")

    # Find the email address — check preferences first, then tenant record
    # NOTE: Both repos return plain dicts — use .get(), NOT getattr().
    email_addr: str | None = None
    try:
        prefs = await _state._prefs_repo.get_active(tenant_id)
        if prefs:
            email_addr = prefs.get("notification_email") or prefs.get(
                "customer_email"
            )
    except Exception:
        pass

    if not email_addr:
        email_addr = tenant.get("customer_email")

    if not email_addr:
        raise HTTPException(
            status_code=422,
            detail=f"No email address on record for tenant {tenant_id[:12]}. "
            "Set a notification_email or customer_email first.",
        )

    # Send the welcome email (without raw keys — they're hashed and irrecoverable)
    from src.multi_tenant.welcome_email import send_welcome_email

    tier_name = tenant.get("tier", "unknown")
    if hasattr(tier_name, "value"):
        tier_name = tier_name.value

    try:
        sent = await send_welcome_email(
            to_email=email_addr,
            tenant_id=tenant_id,
            superadmin_key="(use your existing key — not shown for security)",
            widget_key="(use your existing key — not shown for security)",
            tier=tier_name,
        )
    except RuntimeError as exc:
        # Rate-limit (429) or ACS HTTP error — return actionable message
        return ResendWelcomeEmailResponse(
            tenant_id=tenant_id,
            sent_to=email_addr,
            sent=False,
            message=str(exc),
        )

    # Audit log — SPEC-1843: route through log_event() for sanitization
    if _state._audit_repo and sent:
        try:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.TENANT_UPDATED,
                tenant_id=tenant_id,
                actor="spa-console",
                actor_type="admin",
                payload={"action": "resend_welcome_email", "result": "sent"},
            )
        except Exception:
            logger.warning("Audit log failed for resend-welcome-email: %s", tenant_id[:8])

    return ResendWelcomeEmailResponse(
        tenant_id=tenant_id,
        sent_to=email_addr,
        sent=sent,
        message="Welcome email sent successfully" if sent else "Email delivery failed — check provider configuration",
    )


# ---------------------------------------------------------------------------
# WI-EXPIRY-1: Tenant access expiry management
# ---------------------------------------------------------------------------


class SetExpiryRequest(CamelCaseModel):
    """Request body for setting/clearing tenant access expiry."""

    expires_at: str | None = Field(
        description="ISO 8601 timestamp for access expiry, or null to remove expiry.",
    )

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at_iso(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            datetime.fromisoformat(v)
        except (ValueError, TypeError):
            raise ValueError("expires_at must be a valid ISO 8601 timestamp")
        return v


class SetExpiryResponse(CamelCaseModel):
    """Response from setting/clearing tenant access expiry."""

    tenant_id: str
    previous_expires_at: str | None
    new_expires_at: str | None
    updated_at: str


@router.patch(
    "/tenants/{tenant_id}/expiry",
    response_model=SetExpiryResponse,
    summary="Set or clear tenant access expiry",
    description=(
        "Sets, extends, or removes the access expiry date for a tenant. "
        "When expires_at is set, the tenant will be blocked after that time. "
        "Send null to remove expiry (tenant becomes indefinite). "
        "Resets expiry_warnings_sent when changing the date."
    ),
    responses={
        404: {"description": "Tenant not found"},
        503: {"description": "Service not initialized"},
    },
)
async def set_tenant_expiry(
    tenant_id: str,
    body: SetExpiryRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> SetExpiryResponse:
    """Set or clear the access expiry for a tenant."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # SPEC-1667: Router-level require_platform_admin() guard ensures
    # only SPA platform admin keys reach this endpoint.

    # Read current tenant (partition_key = document_id for tenant docs)
    tenant_doc = await _state._tenant_repo.read(tenant_id, tenant_id)
    if tenant_doc is None:
        raise HTTPException(status_code=404, detail=f"Tenant {tenant_id} not found")

    previous_expires_at = tenant_doc.get("expires_at")
    now_iso = datetime.now(timezone.utc).isoformat()

    # Build patch operations
    operations: list[dict[str, Any]] = [
        {"op": "set", "path": "/expires_at", "value": body.expires_at},
        {"op": "set", "path": "/updated_at", "value": now_iso},
    ]

    # Reset warning dedup when expiry changes (so new warnings fire)
    if body.expires_at != previous_expires_at:
        operations.append(
            {"op": "set", "path": "/expiry_warnings_sent", "value": []},
        )

    # If tenant was trial_expired and we're setting a future expiry, reactivate
    if (
        body.expires_at
        and tenant_doc.get("status") == "trial_expired"
    ):
        try:
            expires_dt = datetime.fromisoformat(body.expires_at)
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) < expires_dt:
                operations.append(
                    {"op": "set", "path": "/status", "value": "active"},
                )
        except Exception:
            pass  # Malformed — don't reactivate

    await _state._tenant_repo.patch(
        tenant_id=tenant_id,
        document_id=tenant_id,
        operations=operations,
    )

    # Audit log — SPEC-1843: route through log_event() for sanitization
    try:
        if _state._audit_repo:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_CHANGE,
                tenant_id=tenant_id,
                actor=ctx.team_member_email or "spa-console",
                actor_type="admin",
                payload={"action": "tenant_expiry_updated"},
            )
    except Exception:
        pass  # Non-fatal

    logger.info(
        "Tenant expiry updated: tenant=%s prev=%s new=%s (by %s)",
        tenant_id[:12],
        previous_expires_at or "none",
        body.expires_at or "none",
        ctx.team_member_email or "unknown",
    )

    return SetExpiryResponse(
        tenant_id=tenant_id,
        previous_expires_at=previous_expires_at,
        new_expires_at=body.expires_at,
        updated_at=now_iso,
    )


# ---------------------------------------------------------------------------
# WI-1107: Test-only tenant provisioning (non-production environments)
# ---------------------------------------------------------------------------


class TestProvisionResponse(CamelCaseModel):
    """Response from test tenant provisioning.

    Returns raw keys for automated test infrastructure. Only available
    in non-production environments (ENVIRONMENT != "production").

    SPEC-1673 compliance: This endpoint is blocked in production.
    In staging/development, test automation needs keys to exercise
    tenant-scoped API endpoints without provider holding persistent keys.
    Keys are ephemeral — used during test run and discarded.
    """

    tenant_id: str
    status: str
    tier: str
    superadmin_email: str
    user_api_key: str | None = None
    widget_key: str | None = None
    warnings: list[str] = Field(default_factory=list)


@router.post(
    "/test/provision-tenant",
    response_model=TestProvisionResponse,
    summary="Provision test tenant with keys (non-production only)",
    description=(
        "Creates a fully provisioned tenant and returns raw API keys in the "
        "response. Blocked in production (SPEC-1673). Intended for test "
        "pipeline self-provisioning (WI-1107) — the test runner creates "
        "ephemeral tenants, uses the returned keys, then cleans up."
    ),
    responses={
        403: {"description": "Blocked in production environment"},
        503: {"description": "Service not initialized"},
    },
    status_code=201,
)
async def test_provision_tenant(
    body: CreateTenantRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> TestProvisionResponse:
    """Provision a test tenant with keys returned in the response.

    This endpoint is identical to POST /tenants except it returns raw
    keys. It is blocked in production to maintain SPEC-1673 compliance.
    """
    import os as _os
    environment = _os.environ.get("ENVIRONMENT", "development").lower()
    if environment == "production":
        raise HTTPException(
            status_code=403,
            detail="Test provisioning endpoint is not available in production (SPEC-1673).",
        )

    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    if body.tier not in VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{body.tier}'. Valid values: {sorted(VALID_TIERS)}",
        )

    from src.integrations.provisioning import spa_provision_tenant

    try:
        result = await spa_provision_tenant(
            merchant_name=body.merchant_name,
            merchant_url=body.merchant_url,
            superadmin_email=body.superadmin_email,
            tier=body.tier,
        )
    except RuntimeError as exc:
        logger.error("Test tenant creation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        logger.error("Unexpected error during test tenant creation: %s", exc)
        raise HTTPException(status_code=500, detail=f"Provisioning failed: {exc}")

    # Create default preferences (same as regular provisioning)
    try:
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        now_iso = datetime.now(timezone.utc).isoformat()
        prefs_kwargs: dict[str, Any] = {
            "id": f"{result.tenant_id}:1",
            "tenant_id": result.tenant_id,
            "version": 1,
            "is_current": True,
            "brand_name": body.merchant_name,
            "created_at": now_iso,
            "created_by": ctx.team_member_email or "test-pipeline",
        }
        if result.widget_key:
            prefs_kwargs["widget_key"] = result.widget_key
        prefs_doc = PreferencesDocument(**prefs_kwargs)

        if _state._prefs_repo:
            try:
                await _state._prefs_repo.create(result.tenant_id, prefs_doc)
            except Exception:
                await _state._prefs_repo.upsert(result.tenant_id, prefs_doc)
    except Exception as exc:
        logger.warning("Failed to create preferences for test tenant %s: %s", result.tenant_id, exc)
        result.errors.append(f"Preferences creation failed: {exc}")

    # Set expires_at if provided
    if body.expires_at and _state._tenant_repo:
        try:
            await _state._tenant_repo.patch(
                tenant_id=result.tenant_id,
                document_id=result.tenant_id,
                operations=[
                    {"op": "set", "path": "/expires_at", "value": body.expires_at},
                    {"op": "set", "path": "/updated_at", "value": datetime.now(timezone.utc).isoformat()},
                ],
            )
        except Exception as exc:
            result.errors.append(f"Expiry date setting failed: {exc}")

    logger.info(
        "Test tenant provisioned: tenant=%s tier=%s email=%s env=%s (by %s)",
        result.tenant_id[:12],
        body.tier,
        body.superadmin_email,
        environment,
        ctx.team_member_email or "unknown",
    )

    # WI-1107: Return raw keys for test automation (non-production only)
    return TestProvisionResponse(
        tenant_id=result.tenant_id,
        status=result.status,
        tier=result.tier,
        superadmin_email=body.superadmin_email,
        user_api_key=result.superadmin_api_key,
        widget_key=result.widget_key,
        warnings=result.errors,
    )


# ---------------------------------------------------------------------------
# SPEC-1804: Per-tenant rate limit configuration
# ---------------------------------------------------------------------------


class RateLimitUpdateRequest(CamelCaseModel):
    """Request body to set a tenant's RPM rate limit."""

    rate_limit_rpm: int | None = Field(
        default=None,
        description="RPM limit for this tenant, or null to use tier default. "
        "Must be >= 10 (minimum floor) when set.",
    )

    @field_validator("rate_limit_rpm")
    @classmethod
    def validate_rpm_floor(cls, v: int | None) -> int | None:
        if v is not None and v < 10:
            raise ValueError(
                "rate_limit_rpm must be >= 10 (minimum floor) or null "
                "to use tier default"
            )
        return v


class RateLimitResponse(CamelCaseModel):
    """Response after updating a tenant's rate limit."""

    tenant_id: str
    rate_limit_rpm: int | None = Field(
        description="Per-tenant override (null = using tier default)",
    )
    effective_rpm: int = Field(
        description="Actual RPM in effect after resolution (override > tier > 300)",
    )


@router.patch(
    "/tenants/{tenant_id}/rate-limit",
    response_model=RateLimitResponse,
    summary="Set per-tenant RPM rate limit (SPEC-1804)",
    description="Configure the per-tenant rate limit. Set to null to revert "
    "to the tier default (300 RPM). Minimum floor is 10 RPM.",
    responses={
        404: {"description": "Tenant not found"},
        422: {"description": "Validation error (RPM < 10)"},
        503: {"description": "Service not initialized"},
    },
    status_code=200,
)
async def update_tenant_rate_limit(
    tenant_id: str,
    body: RateLimitUpdateRequest,
) -> RateLimitResponse:
    """Set or clear per-tenant RPM rate limit override."""
    from src.multi_tenant.cache_invalidation import publish_cache_invalidation
    from src.multi_tenant.cosmos_schema import (
        RATE_LIMIT_RPM_DEFAULT,
        RATE_LIMIT_RPM_FLOOR,
        TIER_DEFAULTS,
    )

    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Read current tenant document
    try:
        doc = await _state._tenant_repo.read(tenant_id, tenant_id)
    except Exception:
        raise HTTPException(
            status_code=404, detail=f"Tenant '{tenant_id}' not found"
        )

    now = datetime.now(timezone.utc).isoformat()

    # Patch the rate_limit_rpm field
    operations = [
        {"op": "set", "path": "/rate_limit_rpm", "value": body.rate_limit_rpm},
        {"op": "set", "path": "/updated_at", "value": now},
    ]
    await _state._tenant_repo.patch(tenant_id, tenant_id, operations)

    # Publish cache invalidation so all replicas pick up the change
    publish_cache_invalidation(tenant_id)

    # Compute effective RPM
    if body.rate_limit_rpm is not None:
        effective = max(RATE_LIMIT_RPM_FLOOR, body.rate_limit_rpm)
    else:
        tier = doc.get("tier", "starter")
        from src.multi_tenant.entitlement_service import get_entitlement_service
        tier_config = await get_entitlement_service().get_tier_config(tier)
        tier_rpm = tier_config.get("rate_limit_rpm")
        effective = max(
            RATE_LIMIT_RPM_FLOOR,
            tier_rpm if tier_rpm is not None else RATE_LIMIT_RPM_DEFAULT,
        )

    logger.info(
        "Rate limit updated: tenant=%s rpm=%s effective=%d (by %s)",
        tenant_id[:12],
        body.rate_limit_rpm,
        effective,
        "spa-console",
    )

    return RateLimitResponse(
        tenant_id=tenant_id,
        rate_limit_rpm=body.rate_limit_rpm,
        effective_rpm=effective,
    )


@router.get(
    "/tenants/{tenant_id}/rate-limit",
    response_model=RateLimitResponse,
    summary="Get per-tenant RPM rate limit (SPEC-1804)",
    description="Read the current rate limit for a tenant, including the "
    "effective RPM after resolution.",
    responses={
        404: {"description": "Tenant not found"},
        503: {"description": "Service not initialized"},
    },
    status_code=200,
)
async def get_tenant_rate_limit(
    tenant_id: str,
) -> RateLimitResponse:
    """Read current rate limit configuration for a tenant."""
    from src.multi_tenant.cosmos_schema import (
        RATE_LIMIT_RPM_DEFAULT,
        RATE_LIMIT_RPM_FLOOR,
        TIER_DEFAULTS,
    )

    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        doc = await _state._tenant_repo.read(tenant_id, tenant_id)
    except Exception:
        raise HTTPException(
            status_code=404, detail=f"Tenant '{tenant_id}' not found"
        )

    per_tenant_rpm = doc.get("rate_limit_rpm")

    if per_tenant_rpm is not None:
        effective = max(RATE_LIMIT_RPM_FLOOR, per_tenant_rpm)
    else:
        tier = doc.get("tier", "starter")
        from src.multi_tenant.entitlement_service import get_entitlement_service
        tier_config = await get_entitlement_service().get_tier_config(tier)
        tier_rpm = tier_config.get("rate_limit_rpm")
        effective = max(
            RATE_LIMIT_RPM_FLOOR,
            tier_rpm if tier_rpm is not None else RATE_LIMIT_RPM_DEFAULT,
        )

    return RateLimitResponse(
        tenant_id=tenant_id,
        rate_limit_rpm=per_tenant_rpm,
        effective_rpm=effective,
    )
