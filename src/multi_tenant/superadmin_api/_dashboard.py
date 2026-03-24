"""Superadmin API -- Dashboard, billing, SLA, queues, compliance, secrets, integrations.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.cosmos_schema import AuditEventType

from src.multi_tenant.superadmin_api import _monolith as _state
from src.multi_tenant.superadmin_api._tenants import TenantDistributionSummary, tenant_summary

router = _state.router

logger = logging.getLogger(__name__)


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
    """Provider-level billing health across all tenants.

    SPEC-1843 v6 boundary: per-tenant billing health is TENANCY MANAGEMENT
    data — the operator needs to identify which tenant has a billing
    discrepancy.  The ``tenants`` list contains only tenant_id, tier, and
    reconciliation status (no conversation content, no customer PII).

    WI-1641: ``tenants`` field restored after S137 audit found WI-1613
    over-applied the ZK mandate.
    """

    timestamp: str
    total_tenants: int = 0
    tenants_healthy: int = 0
    tenants_needing_review: int = 0
    tenants: list[TenantBillingHealth] = Field(default_factory=list)
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
    """Per-tenant secret inventory.

    Aggregates credentials from all storage locations:
    - Key Vault: tenant-{id}-* secrets (Shopify tokens, Stripe keys, etc.)
    - Cosmos DB: api_key_hash, widget_key_hash on TenantDocument
    - Cosmos DB: shopify_shop_domain, stripe_customer_id on TenantDocument
    - Key Vault: user-{member_id}-totp-seed per team member (TOTP/MFA)
    """

    tenant_id: str
    tier: str | None = None
    customer_email: str | None = None
    shopify_shop_domain: str | None = None
    secret_count: int = 0
    secrets_by_type: dict[str, int] = Field(default_factory=dict)
    has_shopify: bool = False
    has_stripe: bool = False
    has_api_key: bool = False
    totp_count: int = 0
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

    limit: int = Query(20, ge=1, le=100, description="Number of events"),
) -> DeploymentHistoryResponse:
    """List recent deployment and rollback audit events."""
    if not _state._audit_repo:
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
    async for item in _state._audit_repo._container.query_items(
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

) -> DashboardHealthResponse:
    """Get the unified provider operations dashboard data."""
    now = datetime.now(timezone.utc).isoformat()

    result = DashboardHealthResponse(timestamp=now)

    # 1. System health (from service singletons)
    health: dict[str, Any] = {}

    # Cosmos DB health — verify we can read from the tenant repo
    try:
        if _state._tenant_repo is not None:
            # Lightweight read — list_active_tenant_ids is cached/fast
            await _state._tenant_repo.list_active_tenant_ids()
            health["cosmos"] = {"healthy": True, "status": "healthy", "detail": "Connected"}
        else:
            health["cosmos"] = {"healthy": False, "status": "not_initialized", "detail": "Not initialized"}
    except Exception as exc:
        health["cosmos"] = {"healthy": False, "status": "error", "detail": str(exc)[:100]}

    # Redis health — check connection via lightweight ping
    try:
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            import redis as redis_lib
            r = redis_lib.Redis.from_url(redis_url, socket_timeout=3, username=None)
            pong = await asyncio.get_event_loop().run_in_executor(None, r.ping)
            health["redis"] = {"healthy": bool(pong), "status": "healthy", "detail": "Connected"}
            r.close()
        else:
            health["redis"] = {"healthy": False, "status": "not_configured", "detail": "REDIS_URL not set"}
    except Exception as exc:
        health["redis"] = {"healthy": False, "status": "error", "detail": str(exc)[:100]}

    # Key Vault health
    try:
        from src.multi_tenant.tenant_secret_service import get_secret_service
        secret_svc = get_secret_service()
        kv_result = await secret_svc.health_check()
        kv_result["healthy"] = kv_result.get("status") == "healthy"
        health["key_vault"] = kv_result
    except Exception:
        health["key_vault"] = {"healthy": False, "status": "error"}

    try:
        from src.multi_tenant.api_versioning import API_VERSION, PRODUCT_VERSION
        health["version"] = {"api": API_VERSION, "product": PRODUCT_VERSION}
    except ImportError:
        health["version"] = {}

    result.system_health = health

    # 2. Tenant distribution summary
    try:
        result.tenant_summary = await tenant_summary()
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
        deploy_resp = await deployment_history(limit=5)
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

) -> BillingHealthResponse:
    """Get provider-level billing health across all tenants."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    now = datetime.now(timezone.utc).isoformat()

    # Get all tenant IDs + metadata
    tenant_data: list[dict[str, Any]] = []
    query = "SELECT c.tenant_id, c.tier, c.status FROM c WHERE c.status = 'active'"
    async for item in _state._tenant_repo._container.query_items(
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
        if _state._audit_repo:
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
                async for recon_item in _state._audit_repo._container.query_items(
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

    # SPEC-1843 v6: per-tenant billing health is tenancy management data
    # (operator needs to identify which tenant has a discrepancy).
    # WI-1641: tenants list restored after S137 over-application audit.
    healthy_count = sum(1 for t in tenants_health if not t.needs_review)
    return BillingHealthResponse(
        timestamp=now,
        total_tenants=len(tenants_health),
        tenants_healthy=healthy_count,
        tenants_needing_review=needs_review_count,
        tenants=tenants_health,
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

) -> QueueDepthResponse:
    """Get queue depth and job health metrics across all tenants."""
    if _state._nats_mgr is None or not _state._nats_mgr.is_connected:
        # NATS not deployed or not connected — return empty response.
        # NATS is decommissioned (USE_AGENT_CONTAINERS=false) so this
        # is the expected path.  The frontend shows a "Not Deployed" badge.
        return QueueDepthResponse(
            nats_deployed=False,
            total_tenants=0, total_messages=0, total_bytes=0,
            tenants=[], errors=[],
        )

    if _state._tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not configured")

    tenant_ids = await _state._tenant_repo.list_active_tenant_ids()
    tenants: list[TenantQueueInfo] = []
    errors: list[dict[str, str]] = []
    total_messages = 0
    total_bytes = 0

    for tid in tenant_ids:
        try:
            info = await _state._nats_mgr.get_tenant_stream_info(tid)
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

) -> ComplianceSummaryResponse:
    """Get compliance summary across all tenants."""
    if _state._tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not configured")

    now = datetime.now(timezone.utc)
    tenant_ids = await _state._tenant_repo.list_active_tenant_ids()
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
                tenant_doc = await _state._tenant_repo.read(tid, tid)
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
            if _state._prefs_repo is not None:
                try:
                    prefs = await _state._prefs_repo.get_active(tid)
                    if prefs and prefs.get("pii_scrubbing"):
                        info.pii_scrubbing_enabled = True
                        pii_count += 1
                except Exception:
                    pass

            # Count DSAR events from audit log
            if _state._audit_repo is not None:
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
                    async for item in _state._audit_repo._container.query_items(
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
# C-4: Secret Health (aggregate only — SPEC-1843 zero-knowledge)
# ---------------------------------------------------------------------------


class SecretHealthResponse(CamelCaseModel):
    """Aggregate secret health — no per-tenant detail (SPEC-1843).

    This replaces the former ``/secrets/posture`` endpoint which exposed
    per-tenant secret inventories, customer emails, and TOTP seeds.
    """

    tenants_with_api_key: int = 0
    tenants_with_widget_key: int = 0
    tenants_missing_keys: int = 0


@router.get(
    "/health/secrets",
    response_model=SecretHealthResponse,
    summary="Aggregate secret health across tenants (SPEC-1843)",
    description=(
        "Returns aggregate counts of tenants with/without API and widget keys. "
        "No per-tenant detail, no PII, no secret values. "
        "Replaces the former /secrets/posture endpoint."
    ),
    status_code=200,
)
async def secret_health() -> SecretHealthResponse:
    """Return aggregate secret health — SPEC-1843 compliant.

    Counts only boolean key-presence flags from Cosmos DB TenantDocuments.
    Does NOT access Key Vault, TOTP seeds, or any secret values.
    """
    if _state._tenant_repo is None:
        raise HTTPException(status_code=503, detail="Service not configured")

    tenant_ids = await _state._tenant_repo.list_active_tenant_ids()
    api_key_count = 0
    widget_key_count = 0
    missing_count = 0

    for tid in tenant_ids:
        try:
            tenant_doc = await _state._tenant_repo.read(tid, tid)
            has_api = bool(tenant_doc and tenant_doc.get("api_key_hash"))
            has_widget = bool(tenant_doc and tenant_doc.get("widget_key_hash"))
            if has_api:
                api_key_count += 1
            if has_widget:
                widget_key_count += 1
            if not has_api and not has_widget:
                missing_count += 1
        except Exception:
            missing_count += 1

    return SecretHealthResponse(
        tenants_with_api_key=api_key_count,
        tenants_with_widget_key=widget_key_count,
        tenants_missing_keys=missing_count,
    )


# NOTE: GET /secrets/posture has been REMOVED (SPEC-1843 / WI-1606).
# The endpoint exposed per-tenant secret inventories, customer emails,
# TOTP seed counts, and Shopify domains — all prohibited under the
# zero-knowledge mandate. Use GET /health/secrets for aggregate health.


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

    # NATS connectivity — distinguish "not deployed" from "deployed but disconnected".
    # NATS is decommissioned (USE_AGENT_CONTAINERS=false), so treat an
    # unconnected manager as "not deployed" rather than alarming on every
    # page load.
    nats_connected = False
    if _state._nats_mgr is not None:
        try:
            nats_connected = _state._nats_mgr.is_connected
        except Exception as exc:
            errors.append({
                "subsystem": "nats",
                "message": f"NATS status check failed: {exc}",
            })
    nats_deployed = nats_connected  # Only report as deployed if actually connected

    # MCP integration status
    mcp_integrations: list[McpIntegrationStatus] = []
    if _state._tenant_repo is not None and _state._prefs_repo is not None:
        try:
            tenant_ids = await _state._tenant_repo.list_active_tenant_ids()

            storefront_enabled = 0
            storefront_connected = 0
            storefront_errored = 0
            stripe_enabled = 0
            stripe_connected = 0
            stripe_errored = 0

            for tid in tenant_ids:
                try:
                    prefs = await _state._prefs_repo.get_active(tid)
                    if prefs:
                        # Shopify Storefront MCP — uses shopify_integration_status
                        # (auto-generated config in mcp_client.py, not a separate enable flag)
                        shop_status = prefs.get("shopify_integration_status")
                        if shop_status:
                            storefront_enabled += 1
                            if shop_status == "connected":
                                storefront_connected += 1
                            elif shop_status == "error":
                                storefront_errored += 1

                        # Stripe MCP — uses explicit enable flag
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
