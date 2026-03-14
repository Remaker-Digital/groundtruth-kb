"""Superadmin API -- Pipeline observatory, service messages, platform admin management.

Domain sub-module extracted from the superadmin_api monolith.
Endpoints are registered on the shared router from _monolith.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import Body, Depends, HTTPException, Query
from pydantic import Field

from src.multi_tenant.api_models import CamelCaseModel
from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import AuditEventType
from src.multi_tenant.middleware import get_tenant_context

from src.multi_tenant.superadmin_api import _monolith as _state

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline Observatory (SPEC-1579..1583)
# ---------------------------------------------------------------------------

# Pipeline topology definition — the 7-agent pipeline
PIPELINE_AGENTS = [
    "intent-classifier",
    "knowledge-retrieval",
    "response-generator",
    "escalation-handler",
    "analytics-collector",
    "critic-supervisor",
    "co-pilot",
]

PIPELINE_EDGES = [
    ("intent-classifier", "knowledge-retrieval"),
    ("intent-classifier", "escalation-handler"),
    ("intent-classifier", "co-pilot"),
    ("knowledge-retrieval", "response-generator"),
    ("response-generator", "critic-supervisor"),
    ("critic-supervisor", "analytics-collector"),
    ("escalation-handler", "analytics-collector"),
]


class PipelineNodeMetrics(CamelCaseModel):
    """Metrics for a single agent node."""

    agent: str
    invocation_count: int = 0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0
    avg_tokens_in: float = 0.0
    avg_tokens_out: float = 0.0
    avg_cost: float = 0.0


class PipelineEdgeMetrics(CamelCaseModel):
    """Metrics for a transition between agents."""

    source: str
    target: str
    volume: int = 0
    avg_transition_latency_ms: float = 0.0
    drop_off_rate: float = 0.0


class PipelineTopologyResponse(CamelCaseModel):
    """Full pipeline topology with metrics (SPEC-1579)."""

    nodes: list[PipelineNodeMetrics]
    edges: list[PipelineEdgeMetrics]
    total_conversations: int = 0
    period: str = "24h"


class AgentDetailMetrics(CamelCaseModel):
    """Detailed metrics for a single agent (SPEC-1580)."""

    agent: str
    invocation_count: int = 0
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate: float = 0.0
    error_log: list[dict[str, Any]] = Field(default_factory=list)
    latency_trend: list[dict[str, Any]] = Field(default_factory=list)
    token_usage_trend: list[dict[str, Any]] = Field(default_factory=list)
    cost_trend: list[dict[str, Any]] = Field(default_factory=list)


class TenantPipelineSummary(CamelCaseModel):
    """Pipeline metrics summary for a single tenant (SPEC-1581)."""

    tenant_id: str
    display_name: str
    tier: str | None = None
    total_conversations: int = 0
    billable_conversations: int = 0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    escalation_rate: float = 0.0
    token_consumption: int = 0
    cost: float = 0.0
    estimated_ru: float = 0.0
    resolution_rate: float = 0.0


class TenantComparisonResponse(CamelCaseModel):
    """Tenant comparison table (SPEC-1581)."""

    tenants: list[TenantPipelineSummary]
    total: int = 0
    sort_by: str = "total_conversations"
    sort_order: str = "desc"


class TenantDetailMetrics(CamelCaseModel):
    """Detailed metrics for a single tenant (SPEC-1582)."""

    tenant_id: str
    display_name: str
    total_conversations: int = 0
    volume_trend: list[dict[str, Any]] = Field(default_factory=list)
    cost_trend: list[dict[str, Any]] = Field(default_factory=list)
    agent_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    intent_distribution: list[dict[str, Any]] = Field(default_factory=list)
    recent_conversations: list[dict[str, Any]] = Field(default_factory=list)


class DatabaseMetricsResponse(CamelCaseModel):
    """Database operational metrics (SPEC-1583)."""

    collections: list[dict[str, Any]] = Field(default_factory=list)
    total_documents: int = 0
    estimated_storage_mb: float = 0.0
    per_tenant: list[dict[str, Any]] = Field(default_factory=list)
    ru_trend: list[dict[str, Any]] = Field(default_factory=list)


# Module-level service reference for pipeline metrics

@router.get(
    "/pipeline/topology",
    response_model=PipelineTopologyResponse,
    summary="Get pipeline topology with traffic metrics",
    status_code=200,
)
async def get_pipeline_topology(
    period: str = "24h",

) -> PipelineTopologyResponse:
    """Return 7-agent pipeline topology with aggregate metrics (SPEC-1579)."""
    # Build nodes with baseline metrics
    nodes = []
    for agent_name in PIPELINE_AGENTS:
        nodes.append(PipelineNodeMetrics(agent=agent_name))

    # Build edges
    edges = []
    for src, tgt in PIPELINE_EDGES:
        edges.append(PipelineEdgeMetrics(source=src, target=tgt))

    # When connected to production, these would be populated from
    # conversation pipeline_trace data via Cosmos DB queries.
    # For now, return the topology structure with zero metrics.
    total_conversations = 0
    if _state._tenant_repo is not None:
        try:
            tenant_ids = await _state._tenant_repo.list_active_tenant_ids()
            total_conversations = len(tenant_ids) * 10  # Estimate
        except Exception:
            pass

    return PipelineTopologyResponse(
        nodes=nodes,
        edges=edges,
        total_conversations=total_conversations,
        period=period,
    )


@router.get(
    "/pipeline/agents/{agent}/metrics",
    response_model=AgentDetailMetrics,
    summary="Get detailed metrics for a single agent",
    status_code=200,
)
async def get_agent_metrics(
    agent: str,
    period: str = "24h",

) -> AgentDetailMetrics:
    """Return detailed performance metrics for one agent (SPEC-1580)."""
    if agent not in PIPELINE_AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent: {agent}. Valid agents: {', '.join(PIPELINE_AGENTS)}",
        )

    return AgentDetailMetrics(agent=agent)


@router.get(
    "/pipeline/tenants",
    response_model=TenantComparisonResponse,
    summary="Get tenant pipeline comparison",
    status_code=200,
)
async def get_tenant_comparison(
    sort_by: str = "total_conversations",
    sort_order: str = "desc",
    tier: str | None = None,

) -> TenantComparisonResponse:
    """Return all tenants with pipeline metrics (SPEC-1581, SPEC-1785)."""
    tenants: list[TenantPipelineSummary] = []

    if _state._tenant_repo is not None:
        try:
            # Fetch tenant details in a single cross-partition query
            # so the comparison table shows human-readable names (SPEC-1785).
            query = (
                "SELECT c.tenant_id, c.customer_email, c.brand_name, c.tier "
                "FROM c WHERE c.status = 'active'"
            )
            async for item in _state._tenant_repo._container.query_items(
                query=query,
                max_item_count=500,
            ):
                tid = item.get("tenant_id", "")
                # Display priority: brand_name > customer_email > tenant_id
                display = (
                    item.get("brand_name")
                    or item.get("customer_email")
                    or tid
                )
                tenants.append(TenantPipelineSummary(
                    tenant_id=tid,
                    display_name=display,
                    tier=item.get("tier"),
                ))
        except Exception as exc:
            logger.warning("Failed to list tenants for pipeline: %s", exc)

    # Apply tier filter
    if tier:
        tenants = [t for t in tenants if t.tier == tier]

    return TenantComparisonResponse(
        tenants=tenants,
        total=len(tenants),
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/pipeline/tenants/{tenant_id}/metrics",
    response_model=TenantDetailMetrics,
    summary="Get detailed pipeline metrics for a tenant",
    status_code=200,
)
async def get_tenant_pipeline_metrics(
    tenant_id: str,
    period: str = "24h",

) -> TenantDetailMetrics:
    """Return detailed pipeline metrics for a single tenant (SPEC-1582)."""
    return TenantDetailMetrics(
        tenant_id=tenant_id,
        display_name=tenant_id,
    )


@router.get(
    "/pipeline/database",
    response_model=DatabaseMetricsResponse,
    summary="Get database operational metrics",
    status_code=200,
)
async def get_database_metrics(

) -> DatabaseMetricsResponse:
    """Return Cosmos DB operational metrics (SPEC-1583)."""
    return DatabaseMetricsResponse()


# ---------------------------------------------------------------------------
# Service Messages (SPEC-1646, SPEC-1647, SPEC-1648)
# ---------------------------------------------------------------------------


class ServiceMessageRequest(CamelCaseModel):
    """Request body for sending a service message."""

    subject: str = Field(
        ..., min_length=1, max_length=200,
        description="Email subject line",
    )
    body: str = Field(
        ..., min_length=1, max_length=10000,
        description="HTML body content for the service message",
    )
    filter_status: list[str] | None = Field(
        default=None,
        description="Filter recipients by tenant status (e.g. ['active', 'initialized'])",
    )
    filter_tier: list[str] | None = Field(
        default=None,
        description="Filter recipients by subscription tier (e.g. ['professional', 'enterprise'])",
    )


class ServiceMessageRecipient(CamelCaseModel):
    """A resolved recipient for preview purposes."""

    tenant_id: str
    email: str
    tier: str | None = None
    status: str | None = None


class ServiceMessagePreviewResponse(CamelCaseModel):
    """Preview of recipients before sending."""

    recipients: list[ServiceMessageRecipient]
    total_count: int


class ServiceMessageSendResponse(CamelCaseModel):
    """Result of sending a service message."""

    total_recipients: int
    sent_count: int
    failed_count: int
    errors: list[str] = Field(default_factory=list)
    success: bool


@router.post(
    "/service-messages/preview",
    response_model=ServiceMessagePreviewResponse,
    summary="Preview service message recipients",
    description=(
        "Resolves the list of superadmin email addresses that would receive "
        "a service message with the given filters. Does not send anything."
    ),
    status_code=200,
)
async def preview_service_message_recipients(
    filter_status: list[str] | None = Query(None, description="Filter by tenant status"),
    filter_tier: list[str] | None = Query(None, description="Filter by subscription tier"),
    ctx: TenantContext = Depends(get_tenant_context),
) -> ServiceMessagePreviewResponse:
    """Resolve and return the recipient list for a service message."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    recipients = await _resolve_service_message_recipients(
        filter_status=filter_status,
        filter_tier=filter_tier,
    )
    return ServiceMessagePreviewResponse(
        recipients=recipients,
        total_count=len(recipients),
    )


@router.post(
    "/service-messages/send",
    response_model=ServiceMessageSendResponse,
    summary="Send a service message to tenant superadmins",
    description=(
        "Sends a bulk service message via BCC email to all tenant superadmins "
        "matching the specified filters. The sender is 'Agent Red Service "
        "Administrator'. Recipient email addresses are not disclosed to each "
        "other (SPEC-1648)."
    ),
    status_code=200,
    responses={
        422: {"description": "No recipients match the filters"},
        503: {"description": "Service not initialized"},
    },
)
async def send_service_message_endpoint(
    request: ServiceMessageRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> ServiceMessageSendResponse:
    """Send a service message to filtered tenant superadmins."""
    if not _state._tenant_repo:
        raise HTTPException(status_code=503, detail="Service not initialized")

    # SPEC-1667: Router-level require_platform_admin() guard ensures
    # only SPA platform admin keys reach this endpoint.

    # Resolve recipients
    recipients = await _resolve_service_message_recipients(
        filter_status=request.filter_status,
        filter_tier=request.filter_tier,
    )
    if not recipients:
        raise HTTPException(
            status_code=422,
            detail="No recipients match the specified filters",
        )

    # De-duplicate emails (a superadmin could be on multiple tenants)
    unique_emails = list(dict.fromkeys(r.email for r in recipients))

    # Render and send
    from src.multi_tenant.service_message_delivery import (
        render_service_message_body,
        send_service_message,
    )

    body_html = render_service_message_body(request.body)
    result = await send_service_message(
        subject=request.subject,
        body_html=body_html,
        recipient_emails=unique_emails,
    )

    # Audit log the send
    if _state._audit_repo:
        try:
            await _state._audit_repo.create({
                "id": f"svc-msg-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "tenant_id": "platform",
                "event_type": "service_message_sent",
                "actor": "spa-console",
                "details": {
                    "subject": request.subject[:100],
                    "total_recipients": result.total_recipients,
                    "sent_count": result.sent_count,
                    "failed_count": result.failed_count,
                    "filter_status": request.filter_status,
                    "filter_tier": request.filter_tier,
                },
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        except Exception:
            logger.exception("Failed to audit log service message send")

    return ServiceMessageSendResponse(
        total_recipients=result.total_recipients,
        sent_count=result.sent_count,
        failed_count=result.failed_count,
        errors=result.errors,
        success=result.success,
    )


async def _resolve_service_message_recipients(
    *,
    filter_status: list[str] | None = None,
    filter_tier: list[str] | None = None,
) -> list[ServiceMessageRecipient]:
    """Resolve superadmin emails from filtered tenant list.

    Queries the tenant directory with optional status/tier filters and
    returns a list of recipients with valid email addresses.
    """
    if not _state._tenant_repo:
        return []

    # Build cross-partition query for tenants with email addresses
    conditions = ["c.customer_email != null", "c.customer_email != ''"]
    params: list[dict[str, Any]] = []

    if filter_status:
        # IN clause for multiple status values
        placeholders = ", ".join(f"@status{i}" for i in range(len(filter_status)))
        conditions.append(f"c.status IN ({placeholders})")
        for i, s in enumerate(filter_status):
            params.append({"name": f"@status{i}", "value": s})

    if filter_tier:
        placeholders = ", ".join(f"@tier{i}" for i in range(len(filter_tier)))
        conditions.append(f"c.tier IN ({placeholders})")
        for i, t in enumerate(filter_tier):
            params.append({"name": f"@tier{i}", "value": t})

    where_clause = " AND ".join(conditions)
    query = (
        f"SELECT c.tenant_id, c.customer_email, c.tier, c.status "
        f"FROM c WHERE {where_clause} "
        f"ORDER BY c.created_at DESC"
    )

    recipients: list[ServiceMessageRecipient] = []
    async for item in _state._tenant_repo._container.query_items(
        query=query,
        parameters=params if params else None,
        max_item_count=500,
    ):
        email = item.get("customer_email", "")
        if email and "@" in email:
            recipients.append(ServiceMessageRecipient(
                tenant_id=item.get("tenant_id", ""),
                email=email,
                tier=item.get("tier"),
                status=item.get("status"),
            ))

    return recipients


# ---------------------------------------------------------------------------
# SPEC-1669: SPA Platform Admin Key Regeneration
# ---------------------------------------------------------------------------


class RegenerateKeyResponse(CamelCaseModel):
    """Response from SPA API key regeneration.

    Contains the new raw API key — displayed ONCE and never stored in
    plaintext. The caller must save it immediately.
    """

    admin_id: str
    email: str
    new_api_key: str
    regenerated_at: str
    message: str = (
        "New API key generated. Save this key immediately — "
        "it will not be shown again. The previous key is now invalid."
    )


@router.post(
    "/platform-admin/regenerate-key",
    response_model=RegenerateKeyResponse,
    summary="Regenerate SPA platform admin API key (SPEC-1669)",
    description=(
        "Generate a new ar_spa_* API key for the currently authenticated "
        "platform admin. The previous key is invalidated immediately. "
        "The new key is returned exactly once and must be saved. "
        "Key regeneration is auditable (logged with timestamp and admin_id)."
    ),
    responses={
        200: {"description": "New key generated successfully"},
        503: {"description": "Platform admin repository not initialized"},
    },
    status_code=200,
)
async def regenerate_platform_admin_key(
    ctx: TenantContext = Depends(get_tenant_context),
) -> RegenerateKeyResponse:
    """Regenerate the SPA platform admin API key (SPEC-1669).

    This endpoint:
    1. Generates a new ar_spa_* key for the authenticated platform admin.
    2. Hashes the new key and updates the platform_admins document.
    3. Returns the raw key exactly once (never stored in plaintext).
    4. The previous key is immediately invalidated (hash replaced).
    5. Logs the regeneration for audit trail.

    The caller is already authenticated via their current key (router-level
    require_platform_admin() guard). After this call, the current key is
    invalid and the new key must be used for subsequent requests.
    """
    if _state._platform_admin_repo is None:
        raise HTTPException(
            status_code=503,
            detail="Platform admin service not initialized.",
        )

    admin_id = ctx.platform_admin_id
    admin_email = ctx.platform_admin_email or "unknown"

    if not admin_id:
        raise HTTPException(
            status_code=500,
            detail="Platform admin identity not available in request context.",
        )

    # Generate new SPA API key
    from src.multi_tenant.auth import generate_spa_api_key, hash_api_key

    new_raw_key = generate_spa_api_key()
    new_key_hash = hash_api_key(new_raw_key)
    now_iso = datetime.now(timezone.utc).isoformat()

    # Update the platform admin document with the new key hash
    try:
        await _state._platform_admin_repo.update_api_key_hash(
            admin_id=admin_id,
            new_key_hash=new_key_hash,
            updated_at=now_iso,
        )
    except Exception as exc:
        logger.error(
            "SPA key regeneration failed for admin %s: %s",
            admin_id, exc,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Key regeneration failed: {exc}",
        )

    # Audit log
    logger.info(
        "SPA API key regenerated: admin_id=%s email=%s at=%s",
        admin_id, admin_email, now_iso,
    )

    if _state._audit_repo:
        try:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id="__platform__",
                actor=admin_email,
                actor_type="admin",
                payload={
                    "action": "spa_key_regenerated",
                    "admin_id": admin_id,
                    "regenerated_at": now_iso,
                    "key_hash_prefix": new_key_hash[:8],
                },
            )
        except Exception as exc:
            # Audit failure should not block key regeneration
            logger.warning("Audit log for key regeneration failed: %s", exc)

    return RegenerateKeyResponse(
        admin_id=admin_id,
        email=admin_email,
        new_api_key=new_raw_key,
        regenerated_at=now_iso,
    )


# ---------------------------------------------------------------------------
# SPEC-1675: SPA User Hierarchy and Lifecycle
# ---------------------------------------------------------------------------


class PlatformAdminUserResponse(CamelCaseModel):
    """Public representation of a platform admin user."""

    admin_id: str
    email: str
    display_name: str
    role: str  # "superadmin" or "operator"
    is_active: bool
    created_at: str | None = None
    last_login_at: str | None = None
    notification_email_address: str | None = None
    backup_codes_remaining: int = 0
    created_by: str | None = None


class CreateOperatorRequest(CamelCaseModel):
    """Request to create a new SPA operator."""

    email: str = Field(description="Email address for the new operator")
    display_name: str = Field(description="Display name for the operator")


class CreateOperatorResponse(CamelCaseModel):
    """Response from operator creation — contains raw API key (shown once)."""

    admin_id: str
    email: str
    display_name: str
    role: str = "operator"
    api_key: str = Field(description="Raw API key — save immediately, shown once")
    message: str = "Operator created. Save the API key immediately — it cannot be retrieved later."


class BackupCodesResponse(CamelCaseModel):
    """Backup recovery codes — shown once, must be saved securely."""

    admin_id: str
    codes: list[str] = Field(description="8 backup codes — save securely, shown once")
    count: int = 8
    message: str = (
        "Save these backup codes in a secure location. "
        "They cannot be retrieved later. Each code can only be used once."
    )


class UpdateNotificationEmailRequest(CamelCaseModel):
    """Request to set or clear the notification email address."""

    email: str | None = Field(
        default=None,
        description="Notification email address, or null to clear",
    )


@router.get(
    "/platform-admin/users",
    response_model=list[PlatformAdminUserResponse],
    summary="List all SPA platform admin users (SPEC-1675)",
)
async def list_platform_admin_users(
    ctx: TenantContext = Depends(get_tenant_context),
) -> list[PlatformAdminUserResponse]:
    """List all active platform admin users."""
    if _state._platform_admin_repo is None:
        raise HTTPException(status_code=503, detail="Platform admin service not initialized.")

    admins = await _state._platform_admin_repo.list_admins()
    return [
        PlatformAdminUserResponse(
            admin_id=a.get("admin_id", a.get("id", "")),
            email=a.get("email", ""),
            display_name=a.get("display_name", ""),
            role=a.get("role", "superadmin"),
            is_active=a.get("is_active", True),
            created_at=a.get("created_at"),
            last_login_at=a.get("last_login_at"),
            notification_email_address=a.get("notification_email_address"),
            backup_codes_remaining=a.get("backup_codes_remaining", 0),
            created_by=a.get("created_by"),
        )
        for a in admins
    ]


@router.post(
    "/platform-admin/users",
    response_model=CreateOperatorResponse,
    summary="Create a new SPA operator (SPEC-1675)",
    status_code=201,
)
async def create_platform_admin_operator(
    body: CreateOperatorRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> CreateOperatorResponse:
    """Create a new operator-level platform admin.

    Only the SPA superadmin can create operators. The raw API key is
    returned exactly once and must be saved immediately.
    """
    if _state._platform_admin_repo is None:
        raise HTTPException(status_code=503, detail="Platform admin service not initialized.")

    # Superadmin guard
    if ctx.platform_admin_role != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Only the SPA superadmin can create operators.",
        )

    # Check for existing admin with same email
    existing = await _state._platform_admin_repo.find_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"A platform admin with email '{body.email}' already exists.",
        )

    import secrets
    import uuid

    from src.multi_tenant.auth import generate_spa_api_key, hash_api_key

    admin_id = str(uuid.uuid4())
    raw_key = generate_spa_api_key()
    key_hash = hash_api_key(raw_key)
    now_iso = datetime.now(timezone.utc).isoformat()

    document = {
        "id": admin_id,
        "admin_id": admin_id,
        "email": body.email,
        "display_name": body.display_name,
        "api_key_hash": key_hash,
        "role": "operator",
        "is_active": True,
        "created_at": now_iso,
        "updated_at": now_iso,
        "created_by": ctx.platform_admin_id,
        "notification_email_address": None,
        "backup_recovery_code_hashes": [],
        "backup_codes_remaining": 0,
        "last_login_at": None,
    }

    await _state._platform_admin_repo.create_admin(document)

    # Audit log
    if _state._audit_repo:
        try:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id="__platform__",
                actor=ctx.platform_admin_email or "unknown",
                actor_type="admin",
                payload={
                    "action": "spa_operator_created",
                    "new_admin_id": admin_id,
                    "new_email": body.email,
                    "created_by": ctx.platform_admin_id,
                },
            )
        except Exception as exc:
            logger.warning("Audit log for operator creation failed: %s", exc)

    logger.info(
        "SPA operator created: admin_id=%s email=%s by=%s",
        admin_id, body.email, ctx.platform_admin_id,
    )

    return CreateOperatorResponse(
        admin_id=admin_id,
        email=body.email,
        display_name=body.display_name,
        api_key=raw_key,
    )


@router.delete(
    "/platform-admin/users/{admin_id}",
    summary="Deactivate an SPA operator (SPEC-1675)",
)
async def deactivate_platform_admin_user(
    admin_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, str]:
    """Deactivate a platform admin operator.

    Only the superadmin can deactivate operators. The superadmin
    cannot be deactivated, and an admin cannot deactivate themselves.
    """
    if _state._platform_admin_repo is None:
        raise HTTPException(status_code=503, detail="Platform admin service not initialized.")

    # Superadmin guard
    if ctx.platform_admin_role != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Only the SPA superadmin can deactivate operators.",
        )

    # Cannot deactivate self
    if admin_id == ctx.platform_admin_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate your own account.",
        )

    # Look up the target admin
    target = await _state._platform_admin_repo.find_by_admin_id(admin_id)
    if not target:
        raise HTTPException(status_code=404, detail="Platform admin not found.")

    # Cannot deactivate the superadmin
    if target.get("role") == "superadmin":
        raise HTTPException(
            status_code=403,
            detail="The SPA superadmin account cannot be deactivated.",
        )

    now_iso = datetime.now(timezone.utc).isoformat()
    await _state._platform_admin_repo.deactivate_admin(admin_id, now_iso)

    # Audit log
    if _state._audit_repo:
        try:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id="__platform__",
                actor=ctx.platform_admin_email or "unknown",
                actor_type="admin",
                payload={
                    "action": "spa_operator_deactivated",
                    "deactivated_admin_id": admin_id,
                    "deactivated_email": target.get("email"),
                    "deactivated_by": ctx.platform_admin_id,
                },
            )
        except Exception as exc:
            logger.warning("Audit log for operator deactivation failed: %s", exc)

    logger.info(
        "SPA operator deactivated: admin_id=%s by=%s",
        admin_id, ctx.platform_admin_id,
    )

    return {"message": f"Operator {target.get('email')} has been deactivated."}


@router.post(
    "/platform-admin/users/backup-codes",
    response_model=BackupCodesResponse,
    summary="Generate backup recovery codes for self (SPEC-1675/1678)",
)
async def generate_backup_codes(
    ctx: TenantContext = Depends(get_tenant_context),
) -> BackupCodesResponse:
    """Generate 8 backup recovery codes for the authenticated admin.

    Replaces any existing backup codes. Codes are returned in plaintext
    exactly once — they must be saved securely. Only SHA-256 hashes are
    stored in the database.
    """
    if _state._platform_admin_repo is None:
        raise HTTPException(status_code=503, detail="Platform admin service not initialized.")

    import secrets

    from src.multi_tenant.auth import hash_api_key

    admin_id = ctx.platform_admin_id
    if not admin_id:
        raise HTTPException(status_code=500, detail="Platform admin identity not available.")

    # Generate 8 random codes (8-char hex each)
    codes = [secrets.token_hex(4) for _ in range(8)]
    code_hashes = [hash_api_key(code) for code in codes]

    now_iso = datetime.now(timezone.utc).isoformat()
    await _state._platform_admin_repo.update_backup_code_hashes(
        admin_id=admin_id,
        hashes=code_hashes,
        count=len(codes),
        updated_at=now_iso,
    )

    # Audit log
    if _state._audit_repo:
        try:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.SECURITY_EVENT,
                tenant_id="__platform__",
                actor=ctx.platform_admin_email or "unknown",
                actor_type="admin",
                payload={
                    "action": "backup_codes_generated",
                    "admin_id": admin_id,
                    "count": len(codes),
                },
            )
        except Exception as exc:
            logger.warning("Audit log for backup code generation failed: %s", exc)

    logger.info(
        "Backup codes generated: admin_id=%s count=%d",
        admin_id, len(codes),
    )

    return BackupCodesResponse(
        admin_id=admin_id,
        codes=codes,
        count=len(codes),
    )


@router.put(
    "/platform-admin/users/notification-email",
    summary="Set notification email for self (SPEC-1675/1676)",
)
async def update_notification_email(
    body: UpdateNotificationEmailRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> dict[str, str]:
    """Set or clear the notification email for login alerts.

    When set, login notifications (SPEC-1676) are sent to this address
    instead of the admin's primary email.
    """
    if _state._platform_admin_repo is None:
        raise HTTPException(status_code=503, detail="Platform admin service not initialized.")

    admin_id = ctx.platform_admin_id
    if not admin_id:
        raise HTTPException(status_code=500, detail="Platform admin identity not available.")

    now_iso = datetime.now(timezone.utc).isoformat()
    await _state._platform_admin_repo.update_notification_email(
        admin_id=admin_id,
        email=body.email,
        updated_at=now_iso,
    )

    action = "set" if body.email else "cleared"
    logger.info(
        "Notification email %s: admin_id=%s email=%s",
        action, admin_id, body.email,
    )

    return {"message": f"Notification email {action} successfully."}
