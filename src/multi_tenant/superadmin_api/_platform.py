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

from src.multi_tenant.pipeline_metrics import get_aggregator
from src.multi_tenant.superadmin_api import _monolith as _state
from src.multi_tenant.superadmin_api._pii_mask import mask_brand, mask_email

router = _state.router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pipeline Observatory (SPEC-1579..1583, SPEC-1852)
# ---------------------------------------------------------------------------

# Pipeline topology now sourced from registry (SPEC-1852)
from src.multi_tenant.pipeline_metrics import get_pipeline_agents, get_pipeline_edges


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
    """Detailed metrics for a single tenant (SPEC-1582).

    SPEC-1843: ``intent_distribution`` and ``recent_conversations`` have been
    removed (WI-1607).  These fields exposed tenant conversation content and
    customer intent text to the platform operator, violating the zero-knowledge
    mandate.  Only aggregate operational metrics are retained.
    """

    tenant_id: str
    display_name: str
    total_conversations: int = 0
    volume_trend: list[dict[str, Any]] = Field(default_factory=list)
    cost_trend: list[dict[str, Any]] = Field(default_factory=list)
    agent_breakdown: list[dict[str, Any]] = Field(default_factory=list)


class DatabaseMetricsResponse(CamelCaseModel):
    """Database operational metrics (SPEC-1583)."""

    collections: list[dict[str, Any]] = Field(default_factory=list)
    total_documents: int = 0
    estimated_storage_mb: float = 0.0
    per_tenant: list[dict[str, Any]] = Field(default_factory=list)
    ru_trend: list[dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Infrastructure Topology (SPEC-1786)
# ---------------------------------------------------------------------------

class InfrastructureNode(CamelCaseModel):
    """A node in the infrastructure topology graph."""

    node_id: str
    label: str
    category: str  # "agent", "azure", "ingress", "egress"
    node_type: str  # e.g. "container-app", "cosmos-db", "redis", etc.
    status: str = "healthy"  # "healthy", "degraded", "error"
    metrics: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, float] = Field(default_factory=dict)  # x, y for layout


class InfrastructureEdge(CamelCaseModel):
    """A directed edge between infrastructure nodes."""

    source: str
    target: str
    label: str = ""
    volume: int = 0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    protocol: str = ""  # "HTTPS", "TCP", "gRPC", "WebSocket"


class InfrastructureTopologyResponse(CamelCaseModel):
    """Full infrastructure topology with traffic flow (SPEC-1786)."""

    nodes: list[InfrastructureNode]
    edges: list[InfrastructureEdge]
    period: str = "24h"
    total_requests: int = 0


# Pre-defined infrastructure topology layout
# Spatial positions represent logical architecture layers
INFRASTRUCTURE_NODES = [
    # Ingress layer (y=0)
    InfrastructureNode(
        node_id="shopify-webhook", label="Shopify Webhook",
        category="ingress", node_type="webhook",
        position={"x": 0, "y": 0},
    ),
    InfrastructureNode(
        node_id="widget", label="Chat Widget",
        category="ingress", node_type="widget",
        position={"x": 1, "y": 0},
    ),
    InfrastructureNode(
        node_id="standalone-admin", label="Standalone Admin",
        category="ingress", node_type="spa",
        position={"x": 2, "y": 0},
    ),
    InfrastructureNode(
        node_id="provider-admin", label="Provider Admin",
        category="ingress", node_type="spa",
        position={"x": 3, "y": 0},
    ),
    InfrastructureNode(
        node_id="shopify-admin", label="Shopify Admin",
        category="ingress", node_type="embedded-app",
        position={"x": 4, "y": 0},
    ),
    # API Gateway (y=1)
    InfrastructureNode(
        node_id="api-gateway", label="API Gateway",
        category="azure", node_type="container-app",
        position={"x": 2, "y": 1},
    ),
    # Pipeline agents (y=2)
    InfrastructureNode(
        node_id="intent-classifier", label="Intent Classifier",
        category="agent", node_type="container-app",
        position={"x": 0, "y": 2},
    ),
    InfrastructureNode(
        node_id="knowledge-retrieval", label="Knowledge Retrieval",
        category="agent", node_type="container-app",
        position={"x": 1, "y": 2},
    ),
    InfrastructureNode(
        node_id="response-generator", label="Response Generator",
        category="agent", node_type="container-app",
        position={"x": 2, "y": 2},
    ),
    InfrastructureNode(
        node_id="escalation-handler", label="Escalation Handler",
        category="agent", node_type="container-app",
        position={"x": 3, "y": 2},
    ),
    InfrastructureNode(
        node_id="analytics-collector", label="Analytics Collector",
        category="agent", node_type="container-app",
        position={"x": 4, "y": 2},
    ),
    InfrastructureNode(
        node_id="critic-supervisor", label="Critic Supervisor",
        category="agent", node_type="container-app",
        position={"x": 1.5, "y": 3},
    ),
    InfrastructureNode(
        node_id="co-pilot", label="Co-Pilot",
        category="agent", node_type="container-app",
        position={"x": 3.5, "y": 3},
    ),
    # Infrastructure services (y=4)
    InfrastructureNode(
        node_id="cosmos-db", label="Cosmos DB",
        category="azure", node_type="cosmos-db",
        position={"x": 0.5, "y": 4},
    ),
    InfrastructureNode(
        node_id="redis", label="Redis Cache",
        category="azure", node_type="redis",
        position={"x": 1.5, "y": 4},
    ),
    InfrastructureNode(
        node_id="azure-openai", label="Azure OpenAI",
        category="azure", node_type="openai",
        position={"x": 2.5, "y": 4},
    ),
    InfrastructureNode(
        node_id="nats", label="NATS JetStream",
        category="azure", node_type="nats",
        position={"x": 3.5, "y": 4},
    ),
    InfrastructureNode(
        node_id="key-vault", label="Key Vault",
        category="azure", node_type="key-vault",
        position={"x": 4.5, "y": 4},
    ),
    # CDN (y=5)
    InfrastructureNode(
        node_id="cdn", label="CDN (Widget JS)",
        category="azure", node_type="cdn",
        position={"x": 2, "y": 5},
    ),
]

# Canonical infrastructure edges with protocols
# Per-interface transport policy (SPEC-1802 / DCL-002 v4):
# Non-streaming: SLIM (primary) → NATS (fallback) → HTTP (external)
# RG streaming: gateway in-process (intended production path)
INFRASTRUCTURE_EDGES_DEF = [
    # Ingress → API Gateway (external, HTTPS)
    ("shopify-webhook", "api-gateway", "HTTPS", "Webhook events"),
    ("widget", "api-gateway", "HTTPS/SSE", "Chat API + streaming"),
    ("standalone-admin", "api-gateway", "HTTPS", "Admin API"),
    ("provider-admin", "api-gateway", "HTTPS", "Superadmin API"),
    ("shopify-admin", "api-gateway", "HTTPS", "Shopify App API"),
    # API Gateway → Agents (internal, SLIM transport — SPEC-1802)
    ("api-gateway", "intent-classifier", "SLIM", "Pipeline dispatch"),
    ("intent-classifier", "knowledge-retrieval", "SLIM", "KB lookup"),
    ("intent-classifier", "escalation-handler", "SLIM", "Escalation"),
    ("intent-classifier", "co-pilot", "SLIM", "Agent assist"),
    ("knowledge-retrieval", "response-generator", "SLIM", "Generate"),
    ("response-generator", "critic-supervisor", "SLIM", "Review"),
    ("critic-supervisor", "analytics-collector", "SLIM", "Log"),
    ("escalation-handler", "analytics-collector", "SLIM", "Log"),
    # Agents → Infrastructure services
    ("api-gateway", "cosmos-db", "HTTPS", "Document R/W"),
    ("api-gateway", "redis", "TLS", "Cache/sessions (port 6380)"),
    ("response-generator", "azure-openai", "HTTPS", "LLM inference"),
    ("knowledge-retrieval", "cosmos-db", "HTTPS", "KB queries"),
    ("api-gateway", "nats", "TCP", "Event bus (blocked — WI-1319)"),
    ("api-gateway", "key-vault", "HTTPS", "Secrets"),
    # CDN
    ("cdn", "widget", "HTTPS", "Widget bundle"),
]


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
    aggregator = get_aggregator()
    agent_metrics, edge_metrics, total = await aggregator.get_topology_metrics(
        period=period
    )

    nodes = []
    for agent_name in get_pipeline_agents():
        am = agent_metrics.get(agent_name)
        if am:
            nodes.append(PipelineNodeMetrics(
                agent=agent_name,
                invocation_count=am.invocation_count,
                avg_latency_ms=am.avg_latency_ms,
                p50_latency_ms=am.p50_latency_ms,
                p95_latency_ms=am.p95_latency_ms,
                p99_latency_ms=am.p99_latency_ms,
                error_rate=am.error_rate,
                avg_tokens_in=am.avg_tokens_in,
                avg_tokens_out=am.avg_tokens_out,
                avg_cost=am.avg_cost,
            ))
        else:
            nodes.append(PipelineNodeMetrics(agent=agent_name))

    edges = []
    for src, tgt in get_pipeline_edges():
        em = edge_metrics.get((src, tgt))
        if em:
            edges.append(PipelineEdgeMetrics(
                source=src,
                target=tgt,
                volume=em.volume,
                avg_transition_latency_ms=em.avg_transition_latency_ms,
                drop_off_rate=em.drop_off_rate,
            ))
        else:
            edges.append(PipelineEdgeMetrics(source=src, target=tgt))

    return PipelineTopologyResponse(
        nodes=nodes,
        edges=edges,
        total_conversations=total,
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
    if agent not in get_pipeline_agents():
        raise HTTPException(
            status_code=404,
            detail=f"Unknown agent: {agent}. Valid agents: {', '.join(get_pipeline_agents())}",
        )

    aggregator = get_aggregator()
    am = await aggregator.get_agent_detail(agent, period=period)
    if am is None:
        return AgentDetailMetrics(agent=agent)

    return AgentDetailMetrics(
        agent=agent,
        invocation_count=am.invocation_count,
        avg_latency_ms=am.avg_latency_ms,
        p50_latency_ms=am.p50_latency_ms,
        p95_latency_ms=am.p95_latency_ms,
        p99_latency_ms=am.p99_latency_ms,
        error_rate=am.error_rate,
        error_log=am.error_log[:50],  # Cap at 50 entries
        latency_trend=am.latency_trend,
        token_usage_trend=am.token_usage_trend,
        cost_trend=am.cost_trend,
    )


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

    # Fetch tenant display info from directory
    # SPEC-1843 v6 / WI-1641: brand_name and customer_email restored
    # (tenancy management data). ZK masking applied (S262).
    tenant_info: dict[str, dict[str, Any]] = {}
    if _state._tenant_repo is not None:
        try:
            query = (
                "SELECT c.tenant_id, c.tier, c.brand_name, c.customer_email "
                "FROM c WHERE c.status = 'active'"
            )
            async for item in _state._tenant_repo._container.query_items(
                query=query,
                max_item_count=500,
            ):
                tid = item.get("tenant_id", "")
                tenant_info[tid] = item
        except Exception as exc:
            logger.warning("Failed to list tenants for pipeline: %s", exc)

    # Get aggregated metrics from the pipeline aggregator
    aggregator = get_aggregator()
    tenant_metrics = await aggregator.get_tenant_comparison(period="24h")

    # Merge directory info with aggregated metrics
    all_tenant_ids = set(tenant_info.keys()) | set(tenant_metrics.keys())
    for tid in all_tenant_ids:
        info = tenant_info.get(tid, {})
        metrics = tenant_metrics.get(tid)
        display = (
            mask_brand(info.get("brand_name"))
            or mask_email(info.get("customer_email"))
            or tid
        )
        t_tier = info.get("tier")

        summary = TenantPipelineSummary(
            tenant_id=tid,
            display_name=display,
            tier=t_tier,
        )
        if metrics:
            summary.total_conversations = metrics.total_conversations
            summary.billable_conversations = metrics.billable_conversations
            summary.avg_latency_ms = metrics.avg_latency_ms
            summary.error_rate = metrics.error_rate
            summary.escalation_rate = metrics.escalation_rate
            summary.token_consumption = metrics.total_tokens
            summary.cost = metrics.total_cost
            summary.estimated_ru = metrics.estimated_ru
            summary.resolution_rate = metrics.resolution_rate

        tenants.append(summary)

    # Apply tier filter
    if tier:
        tenants = [t for t in tenants if t.tier == tier]

    # Apply sorting
    sort_field = sort_by.replace("camelCase", "")  # Accept both formats
    reverse = sort_order != "asc"
    try:
        tenants.sort(
            key=lambda t: getattr(t, sort_by, 0) or 0,
            reverse=reverse,
        )
    except (AttributeError, TypeError):
        pass

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
    aggregator = get_aggregator()
    tm = await aggregator.get_tenant_detail(tenant_id, period=period)

    if tm is None:
        return TenantDetailMetrics(
            tenant_id=tenant_id,
            display_name=tenant_id,
        )

    # SPEC-1843 / WI-1607: intent_distribution and recent_conversations
    # permanently removed — operator must not see tenant conversation content.
    return TenantDetailMetrics(
        tenant_id=tenant_id,
        display_name=tm.display_name or tenant_id,
        total_conversations=tm.total_conversations,
        volume_trend=tm.volume_trend,
        cost_trend=tm.cost_trend,
        agent_breakdown=tm.agent_breakdown,
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
    aggregator = get_aggregator()
    db_data = await aggregator.get_database_metrics()

    return DatabaseMetricsResponse(
        collections=db_data.get("collections", []),
        total_documents=db_data.get("total_documents", 0),
        estimated_storage_mb=db_data.get("estimated_storage_mb", 0.0),
        per_tenant=db_data.get("per_tenant", []),
        ru_trend=db_data.get("ru_trend", []),
    )


@router.get(
    "/pipeline/infrastructure",
    response_model=InfrastructureTopologyResponse,
    summary="Get infrastructure topology with traffic flow (SPEC-1786)",
    status_code=200,
)
async def get_infrastructure_topology(
    period: str = "24h",

) -> InfrastructureTopologyResponse:
    """Return full infrastructure topology with real traffic flow data.

    Combines the static infrastructure graph (Azure services, ingress points,
    pipeline agents) with live metrics from the pipeline aggregator to show
    directional traffic volume, latency, and error rates on each edge.
    """
    aggregator = get_aggregator()
    agent_metrics, edge_metrics, total = await aggregator.get_topology_metrics(
        period=period
    )

    # Build nodes with health status from agent metrics
    nodes: list[InfrastructureNode] = []
    for node_def in INFRASTRUCTURE_NODES:
        node = InfrastructureNode(
            node_id=node_def.node_id,
            label=node_def.label,
            category=node_def.category,
            node_type=node_def.node_type,
            position=node_def.position,
        )
        # Enrich agent nodes with live metrics
        am = agent_metrics.get(node_def.node_id)
        if am and am.invocation_count > 0:
            node.status = (
                "error" if am.error_rate > 0.05
                else "degraded" if am.error_rate > 0.01
                else "healthy"
            )
            node.metrics = {
                "invocation_count": am.invocation_count,
                "avg_latency_ms": round(am.avg_latency_ms, 1),
                "error_rate": round(am.error_rate, 4),
            }
        nodes.append(node)

    # SPEC-1847 / WI-1660: Detect actual transport protocol at runtime.
    # Static edges declare "SLIM" but runtime may use NATS or HTTP fallback.
    runtime_transport = "SLIM"  # default
    try:
        from src.multi_tenant.agntcy_sdk_integration import get_sdk_status
        sdk_status = get_sdk_status()
        active = (sdk_status.get("active_tier") or "slim").upper()
        if active in ("SLIM", "NATS", "HTTP", "HTTP_FAILURE_MODE"):
            runtime_transport = active if active != "HTTP_FAILURE_MODE" else "HTTP"
    except Exception:
        pass  # Fall back to static if SDK unavailable

    # Build edges with traffic metrics
    infra_edges: list[InfrastructureEdge] = []
    for src, tgt, protocol, label in INFRASTRUCTURE_EDGES_DEF:
        # Replace static "SLIM" protocol with runtime-detected transport
        # for internal agent-to-agent edges (SPEC-1847)
        effective_protocol = protocol
        if protocol == "SLIM":
            # DCL-002 v4: RG streaming uses gateway in-process, not transport cascade
            if tgt == "response-generator":
                effective_protocol = "In-Process"
            else:
                effective_protocol = runtime_transport

        edge = InfrastructureEdge(
            source=src,
            target=tgt,
            label=label,
            protocol=effective_protocol,
        )
        # Enrich agent-to-agent edges with live metrics
        em = edge_metrics.get((src, tgt))
        if em and em.volume > 0:
            edge.volume = em.volume
            edge.avg_latency_ms = round(em.avg_transition_latency_ms, 1)
            edge.error_rate = round(em.drop_off_rate, 4)
        infra_edges.append(edge)

    return InfrastructureTopologyResponse(
        nodes=nodes,
        edges=infra_edges,
        period=period,
        total_requests=total,
    )


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

    # Audit log the send — SPEC-1843: route through log_event() for sanitization
    if _state._audit_repo:
        try:
            await _state._audit_repo.log_event(
                event_type=AuditEventType.CONFIG_CHANGE,
                tenant_id="platform",
                actor="spa-console",
                actor_type="admin",
                payload={
                    "action": "service_message_sent",
                    "count": result.sent_count,
                    "result": f"{result.sent_count} sent, {result.failed_count} failed",
                },
            )
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


class DeactivateOperatorResponse(CamelCaseModel):
    """Response for DELETE /platform-admin/users/{admin_id}."""

    message: str


@router.delete(
    "/platform-admin/users/{admin_id}",
    response_model=DeactivateOperatorResponse,
    summary="Deactivate an SPA operator (SPEC-1675)",
)
async def deactivate_platform_admin_user(
    admin_id: str,
    ctx: TenantContext = Depends(get_tenant_context),
) -> DeactivateOperatorResponse:
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

    return DeactivateOperatorResponse(
        message=f"Operator {target.get('email')} has been deactivated.",
    )


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


class NotificationEmailResponse(CamelCaseModel):
    """Response for PUT /platform-admin/users/notification-email."""

    message: str


@router.put(
    "/platform-admin/users/notification-email",
    response_model=NotificationEmailResponse,
    summary="Set notification email for self (SPEC-1675/1676)",
)
async def update_notification_email(
    body: UpdateNotificationEmailRequest,
    ctx: TenantContext = Depends(get_tenant_context),
) -> NotificationEmailResponse:
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

    return NotificationEmailResponse(message=f"Notification email {action} successfully.")
