"""Superadmin Provider Operations API — cross-tenant visibility and control.

Provides REST endpoints exclusively for the service provider (SUPERADMIN role)
to manage and monitor the platform across all tenants. These endpoints perform
cross-partition queries and aggregate data from multiple services.

Phase 1 (Release-Blocking):
    RB-2: GET /api/superadmin/tenants         — Tenant directory with filtering
    RB-2: GET /api/superadmin/tenants/summary  — Tenant distribution summary
    RB-8: GET /api/superadmin/deployments      — Deployment event history
    RB-1: GET /api/superadmin/dashboard        — Provider ops dashboard aggregate
    RB-7: GET /api/superadmin/billing/health   — Billing/metering integrity

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

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field

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


def configure_superadmin_services(
    tenant_repo: TenantRepository,
    audit_repo: AuditLogRepository,
    conv_repo: ConversationRepository | None = None,
    usage_repo: UsageRepository | None = None,
    prefs_repo: PreferencesRepository | None = None,
) -> None:
    """Wire repositories into module-level variables.

    Called during application startup from main.py.
    """
    global _tenant_repo, _audit_repo, _conv_repo, _usage_repo, _prefs_repo
    _tenant_repo = tenant_repo
    _audit_repo = audit_repo
    _conv_repo = conv_repo
    _usage_repo = usage_repo
    _prefs_repo = prefs_repo
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
        f"c.updated_at, c.deactivated_at, c.consent_status "
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
        health["nats"] = {"connected": nats_mgr.is_connected}
    except Exception:
        health["nats"] = {"connected": False, "error": "unavailable"}

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
