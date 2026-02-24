"""Superadmin Provider Operations API — cross-tenant visibility and control.

Provides REST endpoints exclusively for the service provider (SUPERADMIN role)
to manage and monitor the platform across all tenants. These endpoints perform
cross-partition queries and aggregate data from multiple services.

Phase 1 (Release-Blocking):
    RB-2: GET /api/superadmin/tenants           — Tenant directory with filtering
    RB-2: GET /api/superadmin/tenants/summary    — Tenant distribution summary
    RB-8: GET /api/superadmin/deployments        — Deployment event history
    RB-1: GET /api/superadmin/dashboard          — Provider ops dashboard aggregate
    RB-7: GET /api/superadmin/billing/health     — Billing/metering integrity

Phase 2 (Critical):
    C-2:  GET /api/superadmin/sla/trends         — SLA trends + error budget
    C-1:  GET /api/superadmin/queues             — Queue depth per tenant (NATS)
    C-3:  GET /api/superadmin/compliance         — Compliance summary (PII/DSAR/grace)
    C-4:  GET /api/superadmin/secrets/posture    — Secret inventory per tenant
    HV-3: GET /api/superadmin/integrations/health — Circuit breakers + MCP status

Phase 2 (Incident + Alert Management):
    HV-5: GET/POST /api/superadmin/incidents     — Incident CRUD
    RB-4: GET/POST/PUT/DELETE /api/superadmin/alerts/rules — Alert rule CRUD
          GET/POST /api/superadmin/alerts/history         — Alert history + ack

Phase 2 (MFA/TOTP):
    RB-5: GET  /api/superadmin/mfa/status        — Enrollment status
          POST /api/superadmin/mfa/enroll        — Start enrollment (QR + backup codes)
          POST /api/superadmin/mfa/confirm       — Confirm enrollment with first code
          POST /api/superadmin/mfa/verify        — Login-time TOTP verification
          POST /api/superadmin/mfa/disable       — Disable MFA (requires valid code)
          POST /api/superadmin/mfa/backup-verify — Login-time backup code verification

All endpoints require SUPERADMIN role. Widget keys and tenant-level API keys
are rejected. Only per-user API keys with SUPERADMIN role are accepted.

Architecture references:
    - Assessment: SERVICE-PROVIDER-ADMIN-MONITORING-ASSESSMENT-2026-02-17.md
    - Auth: require_role(TeamMemberRole.SUPERADMIN) from middleware.py
    - Cross-partition queries: repository.py list_active_tenant_ids() pattern

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from src.multi_tenant.api_models import CamelCaseModel

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    TenantStatus,
    TenantTier,
)
from src.multi_tenant.middleware import require_role
from src.multi_tenant.cosmos_schema import TeamMemberRole
from src.multi_tenant.repository import (
    AuditLogRepository,
    ConversationRepository,
    PreferencesRepository,
    TenantRepository,
    UsageRepository,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level service references (set via configure function)
# ---------------------------------------------------------------------------

_tenant_repo: TenantRepository | None = None
_audit_repo: AuditLogRepository | None = None
_conv_repo: ConversationRepository | None = None
_usage_repo: UsageRepository | None = None
_prefs_repo: PreferencesRepository | None = None
_nats_mgr: Any = None
_secret_service: Any = None
_incident_repo: Any = None
_alert_rule_repo: Any = None
_alert_history_repo: Any = None


def configure_superadmin_services(
    tenant_repo: TenantRepository,
    audit_repo: AuditLogRepository,
    conv_repo: ConversationRepository | None = None,
    usage_repo: UsageRepository | None = None,
    prefs_repo: PreferencesRepository | None = None,
    nats_mgr: Any = None,
    secret_service: Any = None,
    incident_repo: Any = None,
    alert_rule_repo: Any = None,
    alert_history_repo: Any = None,
) -> None:
    """Wire repositories into module-level variables.

    Called during application startup from main.py.
    """
    global _tenant_repo, _audit_repo, _conv_repo, _usage_repo, _prefs_repo
    global _nats_mgr, _secret_service
    global _incident_repo, _alert_rule_repo, _alert_history_repo
    _tenant_repo = tenant_repo
    _audit_repo = audit_repo
    _conv_repo = conv_repo
    _usage_repo = usage_repo
    _prefs_repo = prefs_repo
    _nats_mgr = nats_mgr
    _secret_service = secret_service
    _incident_repo = incident_repo
    _alert_rule_repo = alert_rule_repo
    _alert_history_repo = alert_history_repo
    logger.info("Superadmin API services configured")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class TenantSummaryItem(CamelCaseModel):
    """Single tenant in the directory listing."""


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


class DeploymentEvent(CamelCaseModel):
    """Single deployment event from audit log."""


    event_type: str
    timestamp: str
    actor: str
    payload: dict[str, Any] = Field(default_factory=dict)


class DeploymentHistoryResponse(CamelCaseModel):
    """Deployment event history response."""


    events: list[DeploymentEvent]
    total: int
    current_version: str | None = None


class DashboardHealthResponse(CamelCaseModel):
    """Provider operations dashboard aggregate."""


    timestamp: str
    system_health: dict[str, Any] = Field(default_factory=dict)
    tenant_summary: TenantDistributionSummary | None = None
    sla_summary: dict[str, Any] = Field(default_factory=dict)
    usage_summary: dict[str, Any] = Field(default_factory=dict)
    recent_deployments: list[DeploymentEvent] = Field(default_factory=list)
    recent_alerts: list[dict[str, Any]] = Field(default_factory=list)


class TenantBillingHealth(CamelCaseModel):
    """Per-tenant billing health snapshot."""


    tenant_id: str
    tier: str | None = None
    status: str = "unknown"
    reconciliation_status: str = "not_available"
    last_reconciliation: str | None = None
    discrepancy_percent: float | None = None
    needs_review: bool = False


class BillingHealthResponse(CamelCaseModel):
    """Provider-level billing health across all tenants."""


    timestamp: str
    tenants: list[TenantBillingHealth]
    total_tenants: int = 0
    tenants_needing_review: int = 0
    webhook_success_rate: float | None = None


class SLATrendPointModel(CamelCaseModel):
    """Single point in the SLA trend time series."""

    timestamp: str
    uptime_pct: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    total_requests: int


class ErrorBudgetModel(CamelCaseModel):
    """Error budget for a tier over a billing period."""

    tier: str
    period_days: int
    allowed_downtime_minutes: float
    actual_downtime_minutes: float
    budget_remaining: float
    budget_consumed_pct: float
    is_within_budget: bool


class SLATrendsResponse(CamelCaseModel):
    """SLA trends and error budget response."""

    range_days: int
    trend_points: list[SLATrendPointModel]
    error_budgets: dict[str, ErrorBudgetModel] = Field(default_factory=dict)
    generated_at: str


# ---------------------------------------------------------------------------
# C-1: Queue Depth response models
# ---------------------------------------------------------------------------


class TenantQueueInfo(CamelCaseModel):
    """Per-tenant JetStream queue metrics."""

    tenant_id: str
    stream_name: str
    messages: int = 0
    bytes: int = 0
    consumer_count: int = 0


class QueueDepthResponse(CamelCaseModel):
    """Aggregate queue depth across all tenants."""

    nats_deployed: bool = True
    total_tenants: int = 0
    total_messages: int = 0
    total_bytes: int = 0
    tenants: list[TenantQueueInfo] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# C-3: Compliance Summary response models
# ---------------------------------------------------------------------------


class TenantComplianceInfo(CamelCaseModel):
    """Per-tenant compliance snapshot."""

    tenant_id: str
    tier: str | None = None
    grace_period_ends_at: str | None = None
    grace_period_active: bool = False
    pii_scrubbing_enabled: bool = False
    dsar_request_count: int = 0
    last_dsar_request: str | None = None


class ComplianceSummaryResponse(CamelCaseModel):
    """Cross-tenant compliance overview."""

    total_tenants: int = 0
    tenants_with_pii_scrubbing: int = 0
    tenants_in_grace_period: int = 0
    total_dsar_requests: int = 0
    tenants: list[TenantComplianceInfo] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# C-4: Secret Posture response models
# ---------------------------------------------------------------------------


class TenantSecretInfo(CamelCaseModel):
    """Per-tenant secret inventory."""

    tenant_id: str
    tier: str | None = None
    secret_count: int = 0
    secrets_by_type: dict[str, int] = Field(default_factory=dict)
    has_shopify: bool = False
    has_stripe: bool = False
    has_api_key: bool = False
    oldest_secret: str | None = None
    newest_secret: str | None = None
    disabled_secrets: int = 0


class SecretPostureResponse(CamelCaseModel):
    """Cross-tenant secret posture overview."""

    total_tenants: int = 0
    total_secrets: int = 0
    secrets_by_type_global: dict[str, int] = Field(default_factory=dict)
    tenants_with_shopify: int = 0
    tenants_with_stripe: int = 0
    tenants_with_api_key: int = 0
    tenants: list[TenantSecretInfo] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# HV-3: Integration Reliability response models
# ---------------------------------------------------------------------------


class CircuitBreakerStatus(CamelCaseModel):
    """Status of a single circuit breaker."""

    service: str
    state: str
    failures: int = 0
    successes: int = 0


class McpIntegrationStatus(CamelCaseModel):
    """MCP server integration status across tenants."""

    server_name: str
    tenants_enabled: int = 0
    tenants_connected: int = 0
    tenants_errored: int = 0


class IntegrationHealthResponse(CamelCaseModel):
    """Cross-service integration health overview."""

    overall_healthy: bool = True
    circuit_breakers: list[CircuitBreakerStatus] = Field(default_factory=list)
    any_breaker_open: bool = False
    nats_deployed: bool = False
    nats_connected: bool = False
    mcp_integrations: list[McpIntegrationStatus] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/superadmin", tags=["superadmin"])


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
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
    status: str | None = Query(None, description="Filter by tenant status"),
    tier: str | None = Query(None, description="Filter by subscription tier"),
    billing_channel: str | None = Query(None, description="Filter by billing channel"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(50, ge=1, le=200, description="Page size"),
) -> TenantDirectoryResponse:
    """List all tenants across all partitions with optional filtering."""
    if not _tenant_repo:
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
    async for item in _tenant_repo._container.query_items(
        query=count_query,
        parameters=params if params else None,
        max_item_count=1,
    ):
        total = item

    # Data query with pagination via OFFSET/LIMIT
    data_query = (
        f"SELECT c.tenant_id, c.status, c.tier, c.billing_channel, "
        f"c.customer_email, c.shopify_shop_domain, c.created_at, "
        f"c.updated_at, c.deactivated_at, c.consent_status, c.expires_at "
        f"FROM c WHERE {where_clause} "
        f"ORDER BY c.created_at DESC "
        f"OFFSET {skip} LIMIT {limit}"
    )

    tenants: list[TenantSummaryItem] = []
    async for item in _tenant_repo._container.query_items(
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
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> TenantDistributionSummary:
    """Get aggregate tenant distribution statistics."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    by_status: dict[str, int] = {}
    by_tier: dict[str, int] = {}
    by_channel: dict[str, int] = {}
    total = 0

    query = (
        "SELECT c.status, c.tier, c.billing_channel FROM c"
    )
    async for item in _tenant_repo._container.query_items(
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
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> TierOverrideResponse:
    """Set a tenant's tier directly, bypassing Stripe."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Validate tier value
    if tier not in VALID_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier '{tier}'. Valid values: {sorted(VALID_TIERS)}",
        )

    # Read current tenant document
    try:
        doc = await _tenant_repo.read(tenant_id, tenant_id)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Tenant '{tenant_id}' not found")

    previous_tier = doc.get("tier")
    now = datetime.now(timezone.utc).isoformat()

    # Patch the tier field
    operations = [
        {"op": "set", "path": "/tier", "value": tier},
        {"op": "set", "path": "/updated_at", "value": now},
    ]
    await _tenant_repo.patch(tenant_id, tenant_id, operations)

    logger.info(
        "Tier override: tenant=%s %s -> %s (by %s)",
        tenant_id[:12],
        previous_tier or "none",
        tier,
        _ctx.team_member_email or "unknown",
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
    """Response from SPA tenant creation — includes one-time credentials."""

    tenant_id: str
    status: str
    tier: str
    superadmin_email: str
    superadmin_api_key: str | None = None
    widget_key: str | None = None
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
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> CreateTenantResponse:
    """Provision a new tenant from the SPA Console.

    Orchestrates the full lifecycle: create tenant → activate → provision
    superadmin → generate widget key → send welcome email. Partial failures
    are captured in the ``warnings`` field — the tenant is still created.
    """
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Only the SPA tenant can provision new tenants — prevent merchant
    # superadmins from creating tenants via their own API keys.
    _SPA_TENANT_ID = "remaker-digital-001"
    if ctx.tenant_id != _SPA_TENANT_ID:
        raise HTTPException(
            status_code=403,
            detail="Tenant provisioning is restricted to the service provider.",
        )

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

        if _prefs_repo:
            try:
                await _prefs_repo.create(result.tenant_id, prefs_doc)
            except Exception:
                await _prefs_repo.upsert(result.tenant_id, prefs_doc)
    except Exception as exc:
        logger.warning("Failed to create preferences for %s: %s", result.tenant_id, exc)
        result.errors.append(f"Preferences creation failed: {exc}")

    # Set expires_at if provided (WI-EXPIRY-1)
    if body.expires_at and _tenant_repo:
        try:
            await _tenant_repo.patch(
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

    # Audit log entry
    try:
        if _audit_repo:
            await _audit_repo.create(
                result.tenant_id,
                {
                    "id": f"audit:{result.tenant_id}:spa-create:{datetime.now(timezone.utc).isoformat()}",
                    "tenant_id": result.tenant_id,
                    "event_type": AuditEventType.CONFIG_CHANGE.value,
                    "action": "spa_tenant_created",
                    "actor": ctx.team_member_email or "spa-console",
                    "details": {
                        "merchant_name": body.merchant_name,
                        "tier": body.tier,
                        "email": body.superadmin_email,
                        "expires_at": body.expires_at,
                    },
                    "created_at": datetime.now(timezone.utc).isoformat(),
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

    return CreateTenantResponse(
        tenant_id=result.tenant_id,
        status=result.status,
        tier=result.tier,
        superadmin_email=result.superadmin_email,
        superadmin_api_key=result.superadmin_api_key,
        widget_key=result.widget_key,
        warnings=result.errors,
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
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> SetExpiryResponse:
    """Set or clear the access expiry for a tenant."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # Only the SPA tenant can manage expiry
    _SPA_TENANT_ID = "remaker-digital-001"
    if ctx.tenant_id != _SPA_TENANT_ID:
        raise HTTPException(
            status_code=403,
            detail="Expiry management is restricted to the service provider.",
        )

    # Read current tenant
    tenant_doc = await _tenant_repo.read(tenant_id)
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

    await _tenant_repo.patch(
        tenant_id=tenant_id,
        document_id=tenant_id,
        operations=operations,
    )

    # Audit log
    try:
        if _audit_repo:
            await _audit_repo.create(
                tenant_id,
                {
                    "id": f"audit:{tenant_id}:set-expiry:{now_iso}",
                    "tenant_id": tenant_id,
                    "event_type": AuditEventType.CONFIG_CHANGE.value,
                    "action": "tenant_expiry_updated",
                    "actor": ctx.team_member_email or "spa-console",
                    "details": {
                        "previous_expires_at": previous_expires_at,
                        "new_expires_at": body.expires_at,
                    },
                    "created_at": now_iso,
                },
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
# RB-8: Deployment History
# ---------------------------------------------------------------------------


@router.get(
    "/deployments",
    response_model=DeploymentHistoryResponse,
    summary="Deployment event history",
    description="Query deployment and rollback events from the audit log.",
    status_code=200,
)
async def deployment_history(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
    limit: int = Query(20, ge=1, le=100, description="Number of events"),
) -> DeploymentHistoryResponse:
    """List recent deployment and rollback audit events."""
    if not _audit_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    deploy_types = [
        AuditEventType.MODEL_DEPLOYED.value,
        AuditEventType.MODEL_ROLLED_BACK.value,
    ]

    # Cross-partition query on audit_log for deployment events
    query = (
        "SELECT c.event_type, c.timestamp, c.actor, c.payload "
        "FROM c WHERE c.event_type IN (@type1, @type2) "
        "ORDER BY c.timestamp DESC "
        f"OFFSET 0 LIMIT {limit}"
    )
    params = [
        {"name": "@type1", "value": deploy_types[0]},
        {"name": "@type2", "value": deploy_types[1]},
    ]

    events: list[DeploymentEvent] = []
    async for item in _audit_repo._container.query_items(
        query=query,
        parameters=params,
        max_item_count=limit,
    ):
        events.append(DeploymentEvent(
            event_type=item.get("event_type", ""),
            timestamp=item.get("timestamp", ""),
            actor=item.get("actor", "system"),
            payload=item.get("payload", {}),
        ))

    # Current version
    current_version: str | None = None
    try:
        from src.multi_tenant.api_versioning import PRODUCT_VERSION
        current_version = PRODUCT_VERSION
    except ImportError:
        pass

    return DeploymentHistoryResponse(
        events=events,
        total=len(events),
        current_version=current_version,
    )


# ---------------------------------------------------------------------------
# RB-1: Provider Operations Dashboard
# ---------------------------------------------------------------------------


@router.get(
    "/dashboard",
    response_model=DashboardHealthResponse,
    summary="Provider operations dashboard",
    description=(
        "Aggregate system health, tenant distribution, SLA compliance, "
        "usage levels, recent deployments, and alerts into a single response."
    ),
    status_code=200,
)
async def provider_dashboard(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> DashboardHealthResponse:
    """Get the unified provider operations dashboard data."""
    now = datetime.now(timezone.utc).isoformat()

    result = DashboardHealthResponse(timestamp=now)

    # 1. System health (from service singletons)
    health: dict[str, Any] = {}

    try:
        from src.multi_tenant.nats_isolation import get_nats_manager
        nats_mgr = get_nats_manager()
        health["nats"] = {"deployed": True, "connected": nats_mgr.is_connected}
    except Exception:
        health["nats"] = {"deployed": False, "connected": False}

    try:
        from src.multi_tenant.pipeline_resilience import get_circuit_breaker_registry
        cb_registry = get_circuit_breaker_registry()
        cb_summary = cb_registry.health_summary()
        health["circuit_breakers"] = cb_summary if cb_summary else {}
    except Exception:
        health["circuit_breakers"] = {}

    try:
        from src.multi_tenant.tenant_secret_service import get_secret_service
        secret_svc = get_secret_service()
        health["key_vault"] = await secret_svc.health_check()
    except Exception:
        health["key_vault"] = {"healthy": False}

    try:
        from src.multi_tenant.api_versioning import API_VERSION, PRODUCT_VERSION
        health["version"] = {"api": API_VERSION, "product": PRODUCT_VERSION}
    except ImportError:
        health["version"] = {}

    result.system_health = health

    # 2. Tenant distribution summary
    try:
        result.tenant_summary = await tenant_summary(_ctx=_ctx)
    except Exception as exc:
        logger.warning("Tenant summary failed: %s", exc)

    # 3. SLA summary
    try:
        from src.multi_tenant.sla_monitoring import get_sla_monitor
        sla_monitor = get_sla_monitor()
        platform_sla = sla_monitor.get_platform_summary()
        result.sla_summary = {
            "overall_compliant": platform_sla.overall_compliant,
            "uptime_pct": platform_sla.uptime_pct,
            "total_requests": platform_sla.total_requests,
            "latency": {
                "p50_ms": platform_sla.latency.p50_ms,
                "p95_ms": platform_sla.latency.p95_ms,
                "p99_ms": platform_sla.latency.p99_ms,
            },
        }
    except Exception as exc:
        logger.warning("SLA summary failed: %s", exc)
        result.sla_summary = {"error": str(exc)}

    # 4. Usage/escalation summary
    try:
        from src.multi_tenant.tenant_usage_monitor import get_usage_monitor
        usage_monitor = get_usage_monitor()
        result.usage_summary = usage_monitor.health_summary()
    except Exception as exc:
        logger.warning("Usage summary failed: %s", exc)
        result.usage_summary = {"error": str(exc)}

    # 5. Recent deployments (last 5)
    try:
        deploy_resp = await deployment_history(_ctx=_ctx, limit=5)
        result.recent_deployments = deploy_resp.events
    except Exception as exc:
        logger.warning("Deployment history failed: %s", exc)

    return result


# ---------------------------------------------------------------------------
# RB-7: Billing/Metering Integrity
# ---------------------------------------------------------------------------


@router.get(
    "/billing/health",
    response_model=BillingHealthResponse,
    summary="Provider billing health",
    description=(
        "Cross-tenant billing health: reconciliation status, metering "
        "discrepancies, and webhook processing rates."
    ),
    status_code=200,
)
async def billing_health(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> BillingHealthResponse:
    """Get provider-level billing health across all tenants."""
    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(timezone.utc).isoformat()

    # Get all tenant IDs + metadata
    tenant_data: list[dict[str, Any]] = []
    query = "SELECT c.tenant_id, c.tier, c.status FROM c WHERE c.status = 'active'"
    async for item in _tenant_repo._container.query_items(
        query=query,
        max_item_count=500,
    ):
        tenant_data.append(item)

    tenants_health: list[TenantBillingHealth] = []
    needs_review_count = 0

    # Check reconciliation status from audit log for each tenant
    for td in tenant_data:
        tid = td.get("tenant_id", "")
        health = TenantBillingHealth(
            tenant_id=tid,
            tier=td.get("tier"),
            status="healthy",
        )

        # Look for most recent reconciliation audit event
        if _audit_repo:
            try:
                recon_query = (
                    "SELECT TOP 1 c.timestamp, c.payload "
                    "FROM c WHERE c.tenant_id = @tid "
                    "AND c.event_type = @evt "
                    "ORDER BY c.timestamp DESC"
                )
                recon_params = [
                    {"name": "@tid", "value": tid},
                    {"name": "@evt", "value": AuditEventType.SUBSCRIPTION_CHANGED.value},
                ]
                async for recon_item in _audit_repo._container.query_items(
                    query=recon_query,
                    parameters=recon_params,
                    max_item_count=1,
                ):
                    payload = recon_item.get("payload", {})
                    if payload.get("action") == "billing_reconciliation":
                        health.reconciliation_status = "reconciled"
                        health.last_reconciliation = recon_item.get("timestamp")
                        disc_pct = payload.get("discrepancy_percent")
                        if disc_pct is not None:
                            health.discrepancy_percent = float(disc_pct)
                            if abs(float(disc_pct)) > 5.0:
                                health.needs_review = True
                                health.status = "review_needed"
                                needs_review_count += 1
            except Exception as exc:
                logger.debug("Reconciliation check failed for %s: %s", tid, exc)
                health.reconciliation_status = "check_failed"

        tenants_health.append(health)

    # Webhook success rate from stripe webhook counters (if available)
    webhook_rate: float | None = None
    try:
        from src.integrations.stripe_webhooks import get_webhook_stats
        stats = get_webhook_stats()
        total_wh = stats.get("total", 0)
        success_wh = stats.get("success", 0)
        if total_wh > 0:
            webhook_rate = round(success_wh / total_wh * 100, 2)
    except (ImportError, Exception):
        # Webhook stats function may not exist yet
        pass

    return BillingHealthResponse(
        timestamp=now,
        tenants=tenants_health,
        total_tenants=len(tenants_health),
        tenants_needing_review=needs_review_count,
        webhook_success_rate=webhook_rate,
    )


# ---------------------------------------------------------------------------
# C-2: SLA Trends + Error Budget
# ---------------------------------------------------------------------------


@router.get(
    "/sla/trends",
    response_model=SLATrendsResponse,
    summary="SLA trends and error budget",
    description=(
        "Historical SLA trends with uptime and latency data points. "
        "Includes error budget calculation per tier for the specified "
        "billing period."
    ),
    status_code=200,
)
async def sla_trends(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
    range_days: int = Query(7, ge=1, le=90, description="Trend range in days"),
    period_days: int = Query(30, ge=1, le=90, description="Error budget billing period"),
) -> SLATrendsResponse:
    """Get SLA trends and error budgets.

    Returns hourly or daily trend data depending on range_days:
    - 1-3 days: hourly data points
    - 4-90 days: daily rollup data points
    """
    try:
        from src.multi_tenant.repositories.sla_snapshots import SLASnapshotRepository
        from src.multi_tenant.sla_monitoring import SLAMonitoringService, SLA_TARGETS

        repo = SLASnapshotRepository()
        now = datetime.now(timezone.utc).isoformat()

        # Fetch snapshots based on range
        if range_days <= 3:
            snapshots = await repo.get_recent_hourly(hours=range_days * 24)
        else:
            snapshots = await repo.get_recent_daily(days=range_days)

        # Build trend series
        trend_data = SLAMonitoringService.build_trend_series(snapshots)
        trend_points = [
            SLATrendPointModel(
                timestamp=p.timestamp,
                uptime_pct=p.uptime_pct,
                p50_ms=p.p50_ms,
                p95_ms=p.p95_ms,
                p99_ms=p.p99_ms,
                total_requests=p.total_requests,
            )
            for p in trend_data
        ]

        # Compute error budgets per tier
        daily_for_budget = await repo.get_recent_daily(days=period_days)
        error_budgets: dict[str, ErrorBudgetModel] = {}
        for tier_name in SLA_TARGETS:
            eb = SLAMonitoringService.compute_error_budget(
                tier=tier_name,
                daily_snapshots=daily_for_budget,
                period_days=period_days,
            )
            error_budgets[tier_name] = ErrorBudgetModel(
                tier=eb.tier,
                period_days=eb.period_days,
                allowed_downtime_minutes=eb.allowed_downtime_minutes,
                actual_downtime_minutes=eb.actual_downtime_minutes,
                budget_remaining=eb.budget_remaining,
                budget_consumed_pct=eb.budget_consumed_pct,
                is_within_budget=eb.is_within_budget,
            )

        return SLATrendsResponse(
            range_days=range_days,
            trend_points=trend_points,
            error_budgets=error_budgets,
            generated_at=now,
        )
    except Exception as exc:
        logger.warning("SLA trends failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail="SLA trend data unavailable")


# ---------------------------------------------------------------------------
# C-1: Queue Depth + Job Health
# ---------------------------------------------------------------------------


@router.get(
    "/queues",
    response_model=QueueDepthResponse,
    summary="Queue depth across all tenants",
    description=(
        "Aggregate JetStream queue metrics for all active tenants. "
        "Returns per-tenant message counts, byte totals, and consumer counts."
    ),
    status_code=200,
)
async def queue_depth(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> QueueDepthResponse:
    """Get queue depth and job health metrics across all tenants."""
    if _nats_mgr is None:
        # NATS not deployed — return empty response (not an error)
        return QueueDepthResponse(
            nats_deployed=False,
            total_tenants=0, total_messages=0, total_bytes=0,
            tenants=[], errors=[],
        )
    if not _nats_mgr.is_connected:
        raise HTTPException(status_code=503, detail="NATS is not connected")

    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not configured")

    tenant_ids = await _tenant_repo.list_active_tenant_ids()
    tenants: list[TenantQueueInfo] = []
    errors: list[dict[str, str]] = []
    total_messages = 0
    total_bytes = 0

    for tid in tenant_ids:
        try:
            info = await _nats_mgr.get_tenant_stream_info(tid)
            if info is not None:
                t = TenantQueueInfo(
                    tenant_id=tid,
                    stream_name=info.get("stream_name", ""),
                    messages=info.get("messages", 0),
                    bytes=info.get("bytes", 0),
                    consumer_count=info.get("consumer_count", 0),
                )
                tenants.append(t)
                total_messages += t.messages
                total_bytes += t.bytes
        except Exception as exc:
            errors.append({
                "tenant_id": tid,
                "message": f"Failed to get stream info: {exc}",
            })

    return QueueDepthResponse(
        total_tenants=len(tenants),
        total_messages=total_messages,
        total_bytes=total_bytes,
        tenants=tenants,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# C-3: Compliance Summary
# ---------------------------------------------------------------------------


@router.get(
    "/compliance",
    response_model=ComplianceSummaryResponse,
    summary="Cross-tenant compliance overview",
    description=(
        "Compliance posture across all tenants: grace periods, "
        "PII scrubbing status, and DSAR request history."
    ),
    status_code=200,
)
async def compliance_summary(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> ComplianceSummaryResponse:
    """Get compliance summary across all tenants."""
    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not configured")

    now = datetime.now(timezone.utc)
    tenant_ids = await _tenant_repo.list_active_tenant_ids()
    tenants: list[TenantComplianceInfo] = []
    errors: list[dict[str, str]] = []
    pii_count = 0
    grace_count = 0
    total_dsar = 0

    for tid in tenant_ids:
        try:
            info = TenantComplianceInfo(tenant_id=tid)

            # Read tenant doc for tier + grace period
            try:
                tenant_doc = await _tenant_repo.read(tid)
                if tenant_doc:
                    info.tier = tenant_doc.get("tier")
                    gp_end = tenant_doc.get("grace_period_ends_at")
                    if gp_end:
                        info.grace_period_ends_at = gp_end
                        try:
                            from datetime import datetime as dt
                            ends_at = dt.fromisoformat(gp_end.replace("Z", "+00:00"))
                            info.grace_period_active = ends_at > now
                            if info.grace_period_active:
                                grace_count += 1
                        except (ValueError, TypeError):
                            pass
            except Exception:
                pass

            # Read preferences for PII scrubbing
            if _prefs_repo is not None:
                try:
                    prefs = await _prefs_repo.read(tid)
                    if prefs and prefs.get("pii_scrubbing"):
                        info.pii_scrubbing_enabled = True
                        pii_count += 1
                except Exception:
                    pass

            # Count DSAR events from audit log
            if _audit_repo is not None:
                try:
                    dsar_count = 0
                    last_dsar: str | None = None
                    dsar_types = [
                        AuditEventType.DATA_EXPORTED.value,
                        AuditEventType.CONSENT_CHANGED.value,
                        AuditEventType.DATA_DELETED.value,
                    ]
                    dsar_query = (
                        "SELECT c.timestamp FROM c "
                        "WHERE c.tenant_id = @tid "
                        "AND c.event_type IN (@t1, @t2, @t3) "
                        "ORDER BY c.timestamp DESC"
                    )
                    dsar_params = [
                        {"name": "@tid", "value": tid},
                        {"name": "@t1", "value": dsar_types[0]},
                        {"name": "@t2", "value": dsar_types[1]},
                        {"name": "@t3", "value": dsar_types[2]},
                    ]
                    async for item in _audit_repo._container.query_items(
                        query=dsar_query,
                        parameters=dsar_params,
                        max_item_count=100,
                    ):
                        dsar_count += 1
                        if last_dsar is None:
                            last_dsar = item.get("timestamp")

                    info.dsar_request_count = dsar_count
                    info.last_dsar_request = last_dsar
                    total_dsar += dsar_count
                except Exception:
                    pass

            tenants.append(info)
        except Exception as exc:
            errors.append({
                "tenant_id": tid,
                "message": f"Compliance check failed: {exc}",
            })

    return ComplianceSummaryResponse(
        total_tenants=len(tenants),
        tenants_with_pii_scrubbing=pii_count,
        tenants_in_grace_period=grace_count,
        total_dsar_requests=total_dsar,
        tenants=tenants,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# C-4: Secret Posture
# ---------------------------------------------------------------------------


@router.get(
    "/secrets/posture",
    response_model=SecretPostureResponse,
    summary="Secret posture across all tenants",
    description=(
        "Secret inventory and classification across all tenants. "
        "Shows which tenants have Shopify, Stripe, and API key secrets."
    ),
    status_code=200,
)
async def secret_posture(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> SecretPostureResponse:
    """Get secret posture across all tenants."""
    if _secret_service is None:
        raise HTTPException(status_code=503, detail="Secret service not configured")

    if _tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not configured")

    tenant_ids = await _tenant_repo.list_active_tenant_ids()
    tenants: list[TenantSecretInfo] = []
    errors: list[dict[str, str]] = []
    global_by_type: dict[str, int] = {}
    total_secrets = 0
    shopify_count = 0
    stripe_count = 0
    api_key_count = 0

    for tid in tenant_ids:
        try:
            secrets = await _secret_service.list_tenant_secrets(tid)
            info = TenantSecretInfo(tenant_id=tid)

            # Get tier from tenant doc
            try:
                tenant_doc = await _tenant_repo.read(tid)
                if tenant_doc:
                    info.tier = tenant_doc.get("tier")
            except Exception:
                pass

            info.secret_count = len(secrets)
            total_secrets += len(secrets)

            # Classify by type
            by_type: dict[str, int] = {}
            oldest: str | None = None
            newest: str | None = None
            disabled = 0

            for s in secrets:
                stype = s.get("type", "unknown")
                by_type[stype] = by_type.get(stype, 0) + 1
                global_by_type[stype] = global_by_type.get(stype, 0) + 1

                created = s.get("created")
                if created:
                    if oldest is None or created < oldest:
                        oldest = created
                    if newest is None or created > newest:
                        newest = created

                if s.get("enabled") is False:
                    disabled += 1

                # Classify integration types
                stype_lower = stype.lower()
                if "shopify" in stype_lower:
                    info.has_shopify = True
                if "stripe" in stype_lower:
                    info.has_stripe = True
                if "api_key" in stype_lower or "api-key" in stype_lower:
                    info.has_api_key = True

            info.secrets_by_type = by_type
            info.oldest_secret = oldest
            info.newest_secret = newest
            info.disabled_secrets = disabled

            if info.has_shopify:
                shopify_count += 1
            if info.has_stripe:
                stripe_count += 1
            if info.has_api_key:
                api_key_count += 1

            tenants.append(info)
        except Exception as exc:
            errors.append({
                "tenant_id": tid,
                "message": f"Secret posture check failed: {exc}",
            })

    return SecretPostureResponse(
        total_tenants=len(tenants),
        total_secrets=total_secrets,
        secrets_by_type_global=global_by_type,
        tenants_with_shopify=shopify_count,
        tenants_with_stripe=stripe_count,
        tenants_with_api_key=api_key_count,
        tenants=tenants,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# HV-3: Integration Reliability
# ---------------------------------------------------------------------------


@router.get(
    "/integrations/health",
    response_model=IntegrationHealthResponse,
    summary="Integration reliability and health",
    description=(
        "Circuit breaker states, NATS connectivity, and MCP integration "
        "status across all tenants."
    ),
    status_code=200,
)
async def integration_health(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> IntegrationHealthResponse:
    """Get integration health across all services."""
    errors: list[dict[str, str]] = []
    breakers: list[CircuitBreakerStatus] = []
    any_open = False

    # Circuit breakers
    try:
        from src.multi_tenant.pipeline_resilience import ServiceCircuitBreakerRegistry

        registry = ServiceCircuitBreakerRegistry()
        summary = registry.health_summary()
        any_open = summary.get("any_open", False)
        for svc_name, svc_status in summary.get("services", {}).items():
            breakers.append(CircuitBreakerStatus(
                service=svc_name,
                state=svc_status.get("state", "unknown"),
                failures=svc_status.get("failure_count", 0),
                successes=svc_status.get("success_count", 0),
            ))
    except Exception as exc:
        errors.append({
            "subsystem": "circuit_breakers",
            "message": f"Circuit breaker registry unavailable: {exc}",
        })

    # NATS connectivity — distinguish "not deployed" from "deployed but disconnected"
    nats_deployed = _nats_mgr is not None
    nats_connected = False
    if nats_deployed:
        try:
            nats_connected = _nats_mgr.is_connected
        except Exception as exc:
            errors.append({
                "subsystem": "nats",
                "message": f"NATS status check failed: {exc}",
            })

    # MCP integration status
    mcp_integrations: list[McpIntegrationStatus] = []
    if _tenant_repo is not None and _prefs_repo is not None:
        try:
            tenant_ids = await _tenant_repo.list_active_tenant_ids()

            storefront_enabled = 0
            storefront_connected = 0
            storefront_errored = 0
            stripe_enabled = 0
            stripe_connected = 0
            stripe_errored = 0

            for tid in tenant_ids:
                try:
                    prefs = await _prefs_repo.read(tid)
                    if prefs:
                        # Shopify Storefront MCP
                        if prefs.get("mcp_storefront_enabled"):
                            storefront_enabled += 1
                            status = prefs.get("mcp_storefront_status", "")
                            if status == "connected":
                                storefront_connected += 1
                            elif status == "error":
                                storefront_errored += 1

                        # Stripe MCP
                        if prefs.get("stripe_mcp_enabled"):
                            stripe_enabled += 1
                            status = prefs.get("stripe_mcp_status", "")
                            if status == "connected":
                                stripe_connected += 1
                            elif status == "error":
                                stripe_errored += 1
                except Exception:
                    pass

            mcp_integrations.append(McpIntegrationStatus(
                server_name="shopify-storefront",
                tenants_enabled=storefront_enabled,
                tenants_connected=storefront_connected,
                tenants_errored=storefront_errored,
            ))
            mcp_integrations.append(McpIntegrationStatus(
                server_name="stripe",
                tenants_enabled=stripe_enabled,
                tenants_connected=stripe_connected,
                tenants_errored=stripe_errored,
            ))
        except Exception as exc:
            errors.append({
                "subsystem": "mcp",
                "message": f"MCP status check failed: {exc}",
            })

    # NATS only counts against health when deployed but disconnected.
    # When not deployed, it is not a health concern.
    nats_healthy = nats_connected or (not nats_deployed)
    overall = (not any_open) and nats_healthy

    return IntegrationHealthResponse(
        overall_healthy=overall,
        circuit_breakers=breakers,
        any_breaker_open=any_open,
        nats_deployed=nats_deployed,
        nats_connected=nats_connected,
        mcp_integrations=mcp_integrations,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# HV-5: Incident Management — response models
# ---------------------------------------------------------------------------


class IncidentUpdateModel(CamelCaseModel):
    """Single update entry on an incident."""

    timestamp: str
    status: str
    message: str
    author: str = "system"


class IncidentModel(CamelCaseModel):
    """Full incident document for API response."""

    incident_id: str
    title: str
    description: str = ""
    status: str
    severity: str
    affected_services: list[str] = Field(default_factory=list)
    updates: list[IncidentUpdateModel] = Field(default_factory=list)
    created_at: str
    updated_at: str
    resolved_at: str | None = None
    created_by: str = "system"


class IncidentListResponse(CamelCaseModel):
    """List of incidents."""

    incidents: list[IncidentModel] = Field(default_factory=list)
    total: int = 0


class CreateIncidentRequest(CamelCaseModel):
    """Request body for creating an incident."""

    title: str
    description: str = ""
    severity: str = "minor"
    affected_services: list[str] = Field(default_factory=list)


class AddIncidentUpdateRequest(CamelCaseModel):
    """Request body for adding an update to an incident."""

    status: str
    message: str


# ---------------------------------------------------------------------------
# HV-5: Incident Management — endpoints
# ---------------------------------------------------------------------------


def _incident_to_model(doc: dict[str, Any]) -> IncidentModel:
    """Convert a Cosmos incident document to an API model."""
    updates = [
        IncidentUpdateModel(
            timestamp=u.get("timestamp", ""),
            status=u.get("status", ""),
            message=u.get("message", ""),
            author=u.get("author", "system"),
        )
        for u in doc.get("updates", [])
    ]
    return IncidentModel(
        incident_id=doc.get("incident_id", ""),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        status=doc.get("status", "investigating"),
        severity=doc.get("severity", "minor"),
        affected_services=doc.get("affected_services", []),
        updates=updates,
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
        resolved_at=doc.get("resolved_at"),
        created_by=doc.get("created_by", "system"),
    )


@router.get(
    "/incidents",
    response_model=IncidentListResponse,
    summary="List incidents",
    description="List all incidents (active first, then resolved).",
    status_code=200,
)
async def list_incidents(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
    limit: int = Query(50, ge=1, le=200, description="Max incidents to return"),
) -> IncidentListResponse:
    """List all incidents."""
    if _incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    docs = await _incident_repo.list_all(limit=limit)
    incidents = [_incident_to_model(d) for d in docs]
    return IncidentListResponse(incidents=incidents, total=len(incidents))


@router.post(
    "/incidents",
    response_model=IncidentModel,
    summary="Create a new incident",
    status_code=201,
)
async def create_incident(
    body: CreateIncidentRequest,
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> IncidentModel:
    """Create a new incident."""
    if _incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    created_by = ctx.team_member_email or "superadmin"
    doc = await _incident_repo.create_incident(
        title=body.title,
        description=body.description,
        severity=body.severity,
        affected_services=body.affected_services,
        created_by=created_by,
    )
    return _incident_to_model(doc)


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentModel,
    summary="Get a single incident",
    status_code=200,
)
async def get_incident(
    incident_id: str,
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> IncidentModel:
    """Get a single incident by ID."""
    if _incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    doc = await _incident_repo.find_incident(incident_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _incident_to_model(doc)


@router.post(
    "/incidents/{incident_id}/update",
    response_model=IncidentModel,
    summary="Add status update to an incident",
    status_code=200,
)
async def add_incident_update(
    incident_id: str,
    body: AddIncidentUpdateRequest,
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> IncidentModel:
    """Add a status update to an incident."""
    if _incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    # Find existing incident
    existing = await _incident_repo.find_incident(incident_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    author = ctx.team_member_email or "superadmin"
    doc = await _incident_repo.add_update(
        incident_id=incident_id,
        current_status=existing["status"],
        new_status=body.status,
        message=body.message,
        author=author,
    )
    if doc is None:
        raise HTTPException(status_code=500, detail="Failed to update incident")
    return _incident_to_model(doc)


@router.post(
    "/incidents/{incident_id}/resolve",
    response_model=IncidentModel,
    summary="Resolve an incident",
    status_code=200,
)
async def resolve_incident(
    incident_id: str,
    message: str = Body("Incident resolved", embed=True),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> IncidentModel:
    """Mark an incident as resolved."""
    if _incident_repo is None:
        raise HTTPException(status_code=503, detail="Incident service not configured")

    existing = await _incident_repo.find_incident(incident_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    if existing["status"] == "resolved":
        raise HTTPException(status_code=400, detail="Incident is already resolved")

    author = ctx.team_member_email or "superadmin"
    doc = await _incident_repo.resolve_incident(
        incident_id=incident_id,
        current_status=existing["status"],
        message=message,
        author=author,
    )
    if doc is None:
        raise HTTPException(status_code=500, detail="Failed to resolve incident")
    return _incident_to_model(doc)


# ---------------------------------------------------------------------------
# RB-4: Alert Rules — response models
# ---------------------------------------------------------------------------


class AlertConditionModel(CamelCaseModel):
    """Condition for an alert rule."""

    metric: str = ""
    operator: str = "gt"
    threshold: float = 0


class AlertRuleModel(CamelCaseModel):
    """Alert rule for API response."""

    rule_id: str
    rule_type: str
    name: str
    description: str = ""
    enabled: bool = True
    condition: AlertConditionModel = Field(default_factory=AlertConditionModel)
    notification_channels: list[str] = Field(default_factory=list)
    cooldown_minutes: int = 60
    runbook_url: str = ""
    created_at: str = ""
    updated_at: str = ""


class AlertRuleListResponse(CamelCaseModel):
    """List of alert rules."""

    rules: list[AlertRuleModel] = Field(default_factory=list)
    total: int = 0


class CreateAlertRuleRequest(CamelCaseModel):
    """Request body for creating an alert rule."""

    name: str
    rule_type: str
    description: str = ""
    condition: AlertConditionModel = Field(default_factory=AlertConditionModel)
    notification_channels: list[str] = Field(default_factory=list)
    cooldown_minutes: int = 60
    runbook_url: str = ""


class UpdateAlertRuleRequest(CamelCaseModel):
    """Request body for updating an alert rule."""

    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    condition: AlertConditionModel | None = None
    notification_channels: list[str] | None = None
    cooldown_minutes: int | None = None
    runbook_url: str | None = None


class AlertHistoryItemModel(CamelCaseModel):
    """Single alert history entry."""

    alert_id: str = ""
    alert_date: str = ""
    rule_id: str = ""
    rule_name: str = ""
    rule_type: str = ""
    triggered_at: str = ""
    resolved_at: str | None = None
    severity: str = "warning"
    message: str = ""
    metric_value: float = 0
    threshold_value: float = 0
    acknowledged: bool = False
    acknowledged_by: str | None = None


class AlertHistoryResponse(CamelCaseModel):
    """Alert history response."""

    alerts: list[AlertHistoryItemModel] = Field(default_factory=list)
    total: int = 0


# ---------------------------------------------------------------------------
# RB-5: MFA/TOTP — models
# ---------------------------------------------------------------------------


class MfaStatusResponse(CamelCaseModel):
    """MFA enrollment status for the current user."""

    mfa_enabled: bool = False
    enrolled_at: str | None = None
    backup_codes_remaining: int = 0


class MfaEnrollResponse(CamelCaseModel):
    """MFA enrollment response with QR code and backup codes."""

    qr_code_data_url: str
    provisioning_uri: str
    backup_codes: list[str] = Field(default_factory=list)
    backup_code_hashes: list[str] = Field(default_factory=list)


class MfaConfirmRequest(CamelCaseModel):
    """Confirm MFA enrollment with the first TOTP code."""

    code: str
    backup_code_hashes: list[str] = Field(default_factory=list)


class MfaVerifyRequest(CamelCaseModel):
    """Verify TOTP code at login time."""

    code: str


class MfaVerifyResponse(CamelCaseModel):
    """MFA verification response with session token."""

    mfa_token: str
    backup_codes_remaining: int | None = None


class MfaDisableRequest(CamelCaseModel):
    """Disable MFA (requires valid TOTP code)."""

    code: str


# ---------------------------------------------------------------------------
# RB-4: Alert Rules — endpoints
# ---------------------------------------------------------------------------


def _rule_to_model(doc: dict[str, Any]) -> AlertRuleModel:
    """Convert a Cosmos alert rule document to an API model."""
    cond = doc.get("condition", {})
    return AlertRuleModel(
        rule_id=doc.get("rule_id", ""),
        rule_type=doc.get("rule_type", ""),
        name=doc.get("name", ""),
        description=doc.get("description", ""),
        enabled=doc.get("enabled", True),
        condition=AlertConditionModel(
            metric=cond.get("metric", ""),
            operator=cond.get("operator", "gt"),
            threshold=cond.get("threshold", 0),
        ),
        notification_channels=doc.get("notification_channels", []),
        cooldown_minutes=doc.get("cooldown_minutes", 60),
        runbook_url=doc.get("runbook_url", ""),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at", ""),
    )


def _history_to_model(doc: dict[str, Any]) -> AlertHistoryItemModel:
    """Convert a Cosmos alert history document to an API model."""
    return AlertHistoryItemModel(
        alert_id=doc.get("id", ""),
        alert_date=doc.get("alert_date", ""),
        rule_id=doc.get("rule_id", ""),
        rule_name=doc.get("rule_name", ""),
        rule_type=doc.get("rule_type", ""),
        triggered_at=doc.get("triggered_at", ""),
        resolved_at=doc.get("resolved_at"),
        severity=doc.get("severity", "warning"),
        message=doc.get("message", ""),
        metric_value=doc.get("metric_value", 0),
        threshold_value=doc.get("threshold_value", 0),
        acknowledged=doc.get("acknowledged", False),
        acknowledged_by=doc.get("acknowledged_by"),
    )


@router.get(
    "/alerts/rules",
    response_model=AlertRuleListResponse,
    summary="List alert rules",
    status_code=200,
)
async def list_alert_rules(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> AlertRuleListResponse:
    """List all alert rules."""
    if _alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    docs = await _alert_rule_repo.list_all()
    rules = [_rule_to_model(d) for d in docs]
    return AlertRuleListResponse(rules=rules, total=len(rules))


@router.post(
    "/alerts/rules",
    response_model=AlertRuleModel,
    summary="Create alert rule",
    status_code=201,
)
async def create_alert_rule(
    body: CreateAlertRuleRequest,
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> AlertRuleModel:
    """Create a new alert rule."""
    if _alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    doc = await _alert_rule_repo.create_rule(
        name=body.name,
        rule_type=body.rule_type,
        description=body.description,
        condition=body.condition.model_dump() if body.condition else None,
        notification_channels=body.notification_channels,
        cooldown_minutes=body.cooldown_minutes,
        runbook_url=body.runbook_url,
    )
    return _rule_to_model(doc)


@router.put(
    "/alerts/rules/{rule_id}",
    response_model=AlertRuleModel,
    summary="Update alert rule",
    status_code=200,
)
async def update_alert_rule(
    rule_id: str,
    body: UpdateAlertRuleRequest,
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> AlertRuleModel:
    """Update an existing alert rule."""
    if _alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    # Find the rule first to get the rule_type (partition key)
    existing = await _alert_rule_repo.find_rule(rule_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")

    updates: dict[str, Any] = {}
    if body.name is not None:
        updates["name"] = body.name
    if body.description is not None:
        updates["description"] = body.description
    if body.enabled is not None:
        updates["enabled"] = body.enabled
    if body.condition is not None:
        updates["condition"] = body.condition.model_dump()
    if body.notification_channels is not None:
        updates["notification_channels"] = body.notification_channels
    if body.cooldown_minutes is not None:
        updates["cooldown_minutes"] = body.cooldown_minutes
    if body.runbook_url is not None:
        updates["runbook_url"] = body.runbook_url

    if not updates:
        return _rule_to_model(existing)

    doc = await _alert_rule_repo.update_rule(
        rule_id=rule_id,
        rule_type=existing["rule_type"],
        updates=updates,
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return _rule_to_model(doc)


@router.delete(
    "/alerts/rules/{rule_id}",
    summary="Delete alert rule",
    status_code=200,
)
async def delete_alert_rule(
    rule_id: str,
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> dict[str, Any]:
    """Delete an alert rule."""
    if _alert_rule_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    existing = await _alert_rule_repo.find_rule(rule_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert rule not found")

    deleted = await _alert_rule_repo.delete_rule(
        rule_id=rule_id,
        rule_type=existing["rule_type"],
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return {"deleted": True, "rule_id": rule_id}


# ---------------------------------------------------------------------------
# RB-4: Alert History — endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/alerts/history",
    response_model=AlertHistoryResponse,
    summary="Alert firing history",
    status_code=200,
)
async def alert_history(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
    days: int = Query(7, ge=1, le=90, description="Days of history"),
    limit: int = Query(100, ge=1, le=500, description="Max alerts to return"),
) -> AlertHistoryResponse:
    """List recent alert history."""
    if _alert_history_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    docs = await _alert_history_repo.list_recent(days=days, limit=limit)
    alerts = [_history_to_model(d) for d in docs]
    return AlertHistoryResponse(alerts=alerts, total=len(alerts))


@router.post(
    "/alerts/history/{alert_id}/acknowledge",
    response_model=AlertHistoryItemModel,
    summary="Acknowledge an alert",
    status_code=200,
)
async def acknowledge_alert(
    alert_id: str,
    alert_date: str = Query(..., description="Alert date (YYYY-MM-DD partition key)"),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> AlertHistoryItemModel:
    """Acknowledge an alert firing event."""
    if _alert_history_repo is None:
        raise HTTPException(status_code=503, detail="Alert service not configured")

    ack_by = ctx.team_member_email or "superadmin"
    doc = await _alert_history_repo.acknowledge(
        alert_id=alert_id,
        alert_date=alert_date,
        acknowledged_by=ack_by,
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _history_to_model(doc)


@router.post(
    "/alerts/evaluate",
    summary="Force evaluate all alert rules",
    status_code=200,
)
async def evaluate_alerts(
    _ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> dict[str, Any]:
    """Manually trigger evaluation of all enabled alert rules."""
    try:
        from src.multi_tenant.alert_engine import get_alert_engine

        engine = get_alert_engine()
        result = await engine.evaluate_all()
        return {"evaluated": True, **result}
    except ImportError:
        return {"evaluated": False, "message": "Alert engine not yet implemented"}
    except Exception as exc:
        logger.warning("Alert evaluation failed: %s", exc)
        return {"evaluated": False, "message": str(exc)}


# ---------------------------------------------------------------------------
# RB-5: MFA/TOTP — endpoints
# ---------------------------------------------------------------------------


def _get_mfa_svc():
    """Lazy import to avoid circular dependencies at module load time."""
    from src.multi_tenant.mfa_totp import get_mfa_service

    return get_mfa_service()


async def _get_team_member(ctx: TenantContext) -> dict[str, Any]:
    """Fetch the full team member document for the authenticated user.

    MFA endpoints need the full document (mfa_enabled, backup code hashes, etc.)
    but TenantContext only carries scalar identity fields.
    """
    if not ctx.team_member_id:
        raise HTTPException(status_code=401, detail="No authenticated team member")
    from src.multi_tenant.repositories.team import TeamMemberRepository

    repo = TeamMemberRepository()
    try:
        return await repo.read(ctx.tenant_id, ctx.team_member_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Team member not found")


@router.get(
    "/mfa/status",
    response_model=MfaStatusResponse,
    summary="MFA enrollment status",
    status_code=200,
)
async def mfa_status(
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> MfaStatusResponse:
    """Get MFA enrollment status for the current authenticated user."""
    member = await _get_team_member(ctx)

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    status = await svc.get_enrollment_status(member)
    return MfaStatusResponse(
        mfa_enabled=status["mfa_enabled"],
        enrolled_at=status.get("enrolled_at"),
        backup_codes_remaining=status.get("backup_codes_remaining", 0),
    )


@router.post(
    "/mfa/enroll",
    response_model=MfaEnrollResponse,
    summary="Start MFA enrollment",
    status_code=200,
)
async def mfa_enroll(
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> MfaEnrollResponse:
    """Start MFA enrollment — generates TOTP secret, QR code, and backup codes.

    The secret is stored in Key Vault immediately. Enrollment is not
    confirmed until the user provides their first valid TOTP code via
    the ``/mfa/confirm`` endpoint.
    """
    member = await _get_team_member(ctx)

    if member.get("mfa_enabled", False):
        raise HTTPException(status_code=409, detail="MFA is already enabled")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    result = await svc.start_enrollment(member)
    return MfaEnrollResponse(
        qr_code_data_url=result["qr_code_data_url"],
        provisioning_uri=result["provisioning_uri"],
        backup_codes=result["backup_codes"],
        backup_code_hashes=result["backup_code_hashes"],
    )


@router.post(
    "/mfa/confirm",
    summary="Confirm MFA enrollment",
    status_code=200,
)
async def mfa_confirm(
    body: MfaConfirmRequest = Body(...),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> dict[str, Any]:
    """Confirm MFA enrollment with the first valid TOTP code.

    After this succeeds, MFA is required for all subsequent logins.
    """
    member = await _get_team_member(ctx)

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    confirmed = await svc.confirm_enrollment(
        member=member,
        code=body.code,
        backup_code_hashes=body.backup_code_hashes,
    )
    if not confirmed:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    return {"confirmed": True, "message": "MFA enrollment confirmed"}


@router.post(
    "/mfa/verify",
    response_model=MfaVerifyResponse,
    summary="Verify TOTP code at login",
    status_code=200,
)
async def mfa_verify(
    body: MfaVerifyRequest = Body(...),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> MfaVerifyResponse:
    """Verify a TOTP code at login time and return an MFA session token.

    The returned token should be included in subsequent requests as
    the ``X-MFA-Token`` header.
    """
    member = await _get_team_member(ctx)

    if not member.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not enabled for this user")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    result = await svc.verify_code(member, body.code)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid TOTP code")

    return MfaVerifyResponse(mfa_token=result["mfa_token"])


@router.post(
    "/mfa/disable",
    summary="Disable MFA",
    status_code=200,
)
async def mfa_disable(
    body: MfaDisableRequest = Body(...),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> dict[str, Any]:
    """Disable MFA for the current user. Requires a valid TOTP code."""
    member = await _get_team_member(ctx)

    if not member.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not enabled")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    disabled = await svc.disable_mfa(member, body.code)
    if not disabled:
        raise HTTPException(status_code=400, detail="Invalid TOTP code")

    return {"disabled": True, "message": "MFA has been disabled"}


@router.post(
    "/mfa/backup-verify",
    response_model=MfaVerifyResponse,
    summary="Verify backup code at login",
    status_code=200,
)
async def mfa_backup_verify(
    body: MfaVerifyRequest = Body(...),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> MfaVerifyResponse:
    """Verify a backup code at login time. The backup code is consumed.

    Returns an MFA session token and the number of remaining backup codes.
    """
    member = await _get_team_member(ctx)

    if not member.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not enabled for this user")

    try:
        svc = _get_mfa_svc()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="MFA service not configured")

    result = await svc.verify_backup(member, body.code)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid backup code")

    return MfaVerifyResponse(
        mfa_token=result["mfa_token"],
        backup_codes_remaining=result.get("backup_codes_remaining"),
    )


# ===========================================================================
# Cost Analytics (WI #88)
# ===========================================================================


class CostBreakdownModel(CamelCaseModel):
    """Per-tenant cost breakdown by category."""

    ai_tokens: float = 0.0
    cosmos_db: float = 0.0
    storage: float = 0.0
    compute: float = 0.0
    total: float = 0.0


class TenantCostProfileModel(CamelCaseModel):
    """Cost attribution for a single tenant over a period."""

    tenant_id: str
    tier: str | None = None
    period_start: str = ""
    period_end: str = ""
    conversation_count: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    article_count: int = 0
    cost_breakdown: CostBreakdownModel = Field(default_factory=CostBreakdownModel)
    cost_per_conversation: float = 0.0
    cost_share_pct: float = 0.0


class CostOverviewResponse(CamelCaseModel):
    """Platform-wide cost overview with per-tenant breakdown."""

    period_start: str = ""
    period_end: str = ""
    total_platform_cost: float = 0.0
    total_conversations: int = 0
    total_tenants: int = 0
    avg_cost_per_tenant: float = 0.0
    avg_cost_per_conversation: float = 0.0
    tenants: list[TenantCostProfileModel] = Field(default_factory=list)
    cost_by_tier: dict[str, float] = Field(default_factory=dict)


# Token pricing (Azure OpenAI gpt-4o-mini, per 1M tokens)
_INPUT_TOKEN_COST_PER_M = 0.15
_OUTPUT_TOKEN_COST_PER_M = 0.60
# Cosmos DB serverless: ~$0.25 per 1M RU
_COSMOS_RU_COST_PER_CONV = 0.0003  # estimated RU per conversation
# Flat compute share per conversation (container app amortized)
_COMPUTE_COST_PER_CONV = 0.0002
# Storage: negligible for conversations, set per article
_STORAGE_COST_PER_ARTICLE = 0.0001


@router.get(
    "/costs",
    response_model=CostOverviewResponse,
    summary="Cost analytics — per-tenant cost attribution",
    status_code=200,
)
async def get_cost_analytics(
    days: int = Query(default=30, ge=1, le=365),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> CostOverviewResponse:
    """Compute estimated per-tenant costs based on conversation volume and token usage."""
    from datetime import datetime, timedelta, timezone

    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(timezone.utc)
    period_start = (now - timedelta(days=days)).isoformat()
    period_end = now.isoformat()

    # Query all active tenants
    tenant_ids: list[str] = []
    try:
        tenant_ids = await _tenant_repo.list_active_tenant_ids()
    except Exception:
        pass

    tenant_profiles: list[TenantCostProfileModel] = []
    total_platform_cost = 0.0
    total_conversations = 0
    cost_by_tier: dict[str, float] = {}

    for tid in tenant_ids:
        try:
            # Get tenant tier
            tenant_doc = await _tenant_repo.read(tid, tid)
            tier = tenant_doc.get("tier", "starter") if tenant_doc else "starter"

            # Count conversations in period
            conv_count = 0
            total_input = 0
            total_output = 0
            if _conv_repo:
                try:
                    convs = await _conv_repo.query(
                        tid,
                        "SELECT c.id, c.message_count, c.messages FROM c "
                        "WHERE c.started_at >= @start "
                        "ORDER BY c.started_at DESC "
                        "OFFSET 0 LIMIT 500",
                        [{"name": "@start", "value": period_start}],
                    )
                    conv_count = len(convs)
                    # Estimate tokens from messages (avg ~150 tokens/message)
                    for c in convs:
                        msg_count = c.get("message_count", 0) or len(c.get("messages", []))
                        total_input += int(msg_count * 75)   # customer msgs
                        total_output += int(msg_count * 150)  # AI responses
                except Exception:
                    pass

            # Count KB articles
            article_count = 0
            try:
                from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

                kb_repo = KnowledgeBaseRepository()
                articles = await kb_repo.query(
                    tid,
                    "SELECT VALUE COUNT(1) FROM c",
                    [],
                )
                article_count = articles[0] if articles else 0
            except Exception:
                pass

            # Calculate cost breakdown
            ai_cost = (
                (total_input / 1_000_000) * _INPUT_TOKEN_COST_PER_M
                + (total_output / 1_000_000) * _OUTPUT_TOKEN_COST_PER_M
            )
            cosmos_cost = conv_count * _COSMOS_RU_COST_PER_CONV
            storage_cost = article_count * _STORAGE_COST_PER_ARTICLE
            compute_cost = conv_count * _COMPUTE_COST_PER_CONV
            total_cost = ai_cost + cosmos_cost + storage_cost + compute_cost

            profile = TenantCostProfileModel(
                tenant_id=tid,
                tier=tier,
                period_start=period_start,
                period_end=period_end,
                conversation_count=conv_count,
                total_input_tokens=total_input,
                total_output_tokens=total_output,
                article_count=article_count,
                cost_breakdown=CostBreakdownModel(
                    ai_tokens=round(ai_cost, 6),
                    cosmos_db=round(cosmos_cost, 6),
                    storage=round(storage_cost, 6),
                    compute=round(compute_cost, 6),
                    total=round(total_cost, 6),
                ),
                cost_per_conversation=round(total_cost / max(conv_count, 1), 6),
                cost_share_pct=0.0,  # computed after totals
            )
            tenant_profiles.append(profile)
            total_platform_cost += total_cost
            total_conversations += conv_count
            cost_by_tier[tier] = cost_by_tier.get(tier, 0.0) + total_cost
        except Exception:
            logger.debug("Cost analytics failed for tenant %s", tid)

    # Compute cost share percentages
    for p in tenant_profiles:
        if total_platform_cost > 0:
            p.cost_share_pct = round(
                (p.cost_breakdown.total / total_platform_cost) * 100, 1,
            )

    # Round tier costs
    cost_by_tier = {k: round(v, 4) for k, v in cost_by_tier.items()}

    return CostOverviewResponse(
        period_start=period_start,
        period_end=period_end,
        total_platform_cost=round(total_platform_cost, 4),
        total_conversations=total_conversations,
        total_tenants=len(tenant_profiles),
        avg_cost_per_tenant=round(
            total_platform_cost / max(len(tenant_profiles), 1), 4,
        ),
        avg_cost_per_conversation=round(
            total_platform_cost / max(total_conversations, 1), 4,
        ),
        tenants=tenant_profiles,
        cost_by_tier=cost_by_tier,
    )


# ===========================================================================
# Abuse Detection (WI #89)
# ===========================================================================


class AbuseSignalModel(CamelCaseModel):
    """A single detected abuse signal."""

    tenant_id: str
    signal_type: str
    severity: str
    description: str
    detected_at: str
    metric_value: float = 0.0
    threshold: float = 0.0


class TenantAbuseProfileModel(CamelCaseModel):
    """Abuse profile for a single tenant."""

    tenant_id: str
    is_flagged: bool = False
    flagged_at: str | None = None
    flagged_by: str | None = None
    signals: list[AbuseSignalModel] = Field(default_factory=list)
    risk_score: int = 0


class AbuseOverviewResponse(CamelCaseModel):
    """Platform-wide abuse scan results."""

    total_tenants_scanned: int = 0
    flagged_count: int = 0
    signals_by_type: dict[str, int] = Field(default_factory=dict)
    high_risk_tenants: list[TenantAbuseProfileModel] = Field(default_factory=list)


class FlagTenantRequest(BaseModel):
    """Request body for POST /api/superadmin/abuse/tenant/{tenant_id}/flag."""

    flagged: bool


# Abuse detection thresholds
_RATE_ANOMALY_THRESHOLD = 100     # conversations per day
_VOLUME_SPIKE_MULTIPLIER = 3.0    # 3x above normal
_ERROR_RATE_THRESHOLD = 0.25      # 25% error rate
_TOKEN_EXHAUSTION_THRESHOLD = 500_000  # tokens per day


@router.get(
    "/abuse/signals",
    response_model=AbuseOverviewResponse,
    summary="Abuse detection — cross-tenant anomaly scan",
    status_code=200,
)
async def get_abuse_signals(
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> AbuseOverviewResponse:
    """Scan all active tenants for abuse signals and anomalous usage patterns."""
    from datetime import datetime, timedelta, timezone

    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(timezone.utc)
    day_ago = (now - timedelta(days=1)).isoformat()

    tenant_ids: list[str] = []
    try:
        tenant_ids = await _tenant_repo.list_active_tenant_ids()
    except Exception:
        pass

    high_risk: list[TenantAbuseProfileModel] = []
    signals_by_type: dict[str, int] = {}
    flagged_count = 0

    for tid in tenant_ids:
        try:
            tenant_doc = await _tenant_repo.read(tid, tid)
            is_flagged = tenant_doc.get("abuse_flagged", False) if tenant_doc else False
            flagged_at = tenant_doc.get("abuse_flagged_at") if tenant_doc else None
            flagged_by = tenant_doc.get("abuse_flagged_by") if tenant_doc else None

            if is_flagged:
                flagged_count += 1

            signals: list[AbuseSignalModel] = []

            # Check conversation volume (last 24h)
            daily_convs = 0
            error_convs = 0
            if _conv_repo:
                try:
                    results = await _conv_repo.query(
                        tid,
                        "SELECT c.status FROM c WHERE c.started_at >= @start",
                        [{"name": "@start", "value": day_ago}],
                    )
                    daily_convs = len(results)
                    error_convs = sum(
                        1 for r in results if r.get("status") == "error"
                    )
                except Exception:
                    pass

            # Rate anomaly: too many conversations per day
            if daily_convs > _RATE_ANOMALY_THRESHOLD:
                sig = AbuseSignalModel(
                    tenant_id=tid,
                    signal_type="rate_anomaly",
                    severity="high" if daily_convs > _RATE_ANOMALY_THRESHOLD * 2 else "medium",
                    description=f"{daily_convs} conversations in 24h (threshold: {_RATE_ANOMALY_THRESHOLD})",
                    detected_at=now.isoformat(),
                    metric_value=float(daily_convs),
                    threshold=float(_RATE_ANOMALY_THRESHOLD),
                )
                signals.append(sig)
                signals_by_type["rate_anomaly"] = signals_by_type.get("rate_anomaly", 0) + 1

            # Error rate: high proportion of error conversations
            if daily_convs >= 10 and error_convs / daily_convs > _ERROR_RATE_THRESHOLD:
                error_rate = error_convs / daily_convs
                sig = AbuseSignalModel(
                    tenant_id=tid,
                    signal_type="error_rate",
                    severity="critical" if error_rate > 0.5 else "high",
                    description=f"{error_rate:.0%} error rate ({error_convs}/{daily_convs})",
                    detected_at=now.isoformat(),
                    metric_value=round(error_rate, 3),
                    threshold=_ERROR_RATE_THRESHOLD,
                )
                signals.append(sig)
                signals_by_type["error_rate"] = signals_by_type.get("error_rate", 0) + 1

            # Compute risk score (0-100)
            risk_score = 0
            for s in signals:
                if s.severity == "critical":
                    risk_score += 40
                elif s.severity == "high":
                    risk_score += 25
                elif s.severity == "medium":
                    risk_score += 15
                else:
                    risk_score += 5
            if is_flagged:
                risk_score += 20
            risk_score = min(risk_score, 100)

            # Include in high-risk list if score >= 25 or flagged
            if risk_score >= 25 or is_flagged:
                profile = TenantAbuseProfileModel(
                    tenant_id=tid,
                    is_flagged=is_flagged,
                    flagged_at=flagged_at,
                    flagged_by=flagged_by,
                    signals=signals,
                    risk_score=risk_score,
                )
                high_risk.append(profile)
        except Exception:
            logger.debug("Abuse scan failed for tenant %s", tid)

    # Sort by risk score descending
    high_risk.sort(key=lambda x: x.risk_score, reverse=True)

    return AbuseOverviewResponse(
        total_tenants_scanned=len(tenant_ids),
        flagged_count=flagged_count,
        signals_by_type=signals_by_type,
        high_risk_tenants=high_risk,
    )


@router.post(
    "/abuse/tenant/{tenant_id}/flag",
    summary="Flag or unflag a tenant for abuse review",
    status_code=200,
)
async def toggle_abuse_flag(
    tenant_id: str,
    body: FlagTenantRequest = Body(...),
    ctx: TenantContext = Depends(require_role(TeamMemberRole.SUPERADMIN)),
) -> dict[str, Any]:
    """Flag or unflag a tenant for manual abuse review."""
    from datetime import datetime, timezone

    if not _tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now_iso = datetime.now(timezone.utc).isoformat()
    actor = ctx.user_id if hasattr(ctx, "user_id") else "superadmin"

    try:
        operations = [
            {"op": "set", "path": "/abuse_flagged", "value": body.flagged},
            {"op": "set", "path": "/abuse_flagged_at", "value": now_iso if body.flagged else None},
            {"op": "set", "path": "/abuse_flagged_by", "value": actor if body.flagged else None},
        ]
        await _tenant_repo.patch(
            tenant_id=tenant_id,
            document_id=tenant_id,
            operations=operations,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update flag")

    # Audit log
    if _audit_repo:
        try:
            await _audit_repo.log_event(
                tenant_id=tenant_id,
                event_type=AuditEventType.SECURITY_EVENT,
                actor_id=actor,
                resource_type="tenant",
                resource_id=tenant_id,
                details={
                    "action": "abuse_flag_toggled",
                    "flagged": body.flagged,
                },
            )
        except Exception:
            pass

    return {
        "tenant_id": tenant_id,
        "flagged": body.flagged,
        "updated_at": now_iso,
    }
