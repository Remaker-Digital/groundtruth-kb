"""Tests for Pipeline Observatory API (SPEC-1579..1583).

Validates topology, per-agent, tenant comparison, per-tenant detail,
and database metrics endpoints.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.superadmin_api import (
    AgentDetailMetrics,
    DatabaseMetricsResponse,
    InfrastructureTopologyResponse,
    PipelineTopologyResponse,
    TenantComparisonResponse,
    TenantDetailMetrics,
    configure_superadmin_services,
    get_agent_metrics,
    get_database_metrics,
    get_infrastructure_topology,
    get_pipeline_topology,
    get_tenant_comparison,
    get_tenant_pipeline_metrics,
    INFRASTRUCTURE_EDGES_DEF,
    INFRASTRUCTURE_NODES,
)
from src.multi_tenant.pipeline_metrics import get_pipeline_agents, get_pipeline_edges


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(
        return_value=["tenant-001", "tenant-002"]
    )

    # get_tenant_comparison uses _container.query_items as async iterator
    async def _async_query_items(**kwargs):
        for item in [
            {"tenant_id": "tenant-001", "customer_email": "t1@test.com", "tier": "starter"},
            {"tenant_id": "tenant-002", "customer_email": "t2@test.com", "tier": "professional"},
        ]:
            yield item

    container_mock = MagicMock()
    container_mock.query_items = _async_query_items
    repo._container = container_mock
    return repo


@pytest.fixture()
def superadmin_ctx():
    ctx = MagicMock()
    ctx.tenant_id = "remaker-digital-001"
    ctx.team_member_role = "superadmin"
    return ctx


@pytest.fixture(autouse=True)
def _configure_services(mock_tenant_repo):
    configure_superadmin_services(
        tenant_repo=mock_tenant_repo,
        audit_repo=MagicMock(),
    )


# ---------------------------------------------------------------------------
# TestPipelineTopology -- SPEC-1579
# ---------------------------------------------------------------------------

class TestPipelineTopology:
    """Tests for pipeline topology endpoint."""

    @pytest.mark.asyncio
    async def test_topology_returns_all_agents(self, superadmin_ctx):
        """GET /pipeline/topology returns 7 agent nodes (TEST-2754)."""
        result = await get_pipeline_topology(period="24h")
        assert isinstance(result, PipelineTopologyResponse)
        assert len(result.nodes) == 7
        agent_names = {n.agent for n in result.nodes}
        assert agent_names == set(get_pipeline_agents())

    @pytest.mark.asyncio
    async def test_topology_returns_edges(self, superadmin_ctx):
        """GET /pipeline/topology returns pipeline edges (TEST-2755)."""
        result = await get_pipeline_topology(period="24h")
        assert len(result.edges) == len(get_pipeline_edges())
        for edge in result.edges:
            assert edge.source in get_pipeline_agents()
            assert edge.target in get_pipeline_agents()

    @pytest.mark.asyncio
    async def test_topology_period_parameter(self, superadmin_ctx):
        """Period parameter is reflected in response (TEST-2756)."""
        result = await get_pipeline_topology(period="7d")
        assert result.period == "7d"

    @pytest.mark.asyncio
    async def test_node_metrics_structure(self, superadmin_ctx):
        """Each node has required metric fields (TEST-2757)."""
        result = await get_pipeline_topology(period="24h")
        node = result.nodes[0]
        assert hasattr(node, "invocation_count")
        assert hasattr(node, "avg_latency_ms")
        assert hasattr(node, "p50_latency_ms")
        assert hasattr(node, "p95_latency_ms")
        assert hasattr(node, "error_rate")
        assert hasattr(node, "avg_tokens_in")
        assert hasattr(node, "avg_cost")


# ---------------------------------------------------------------------------
# TestAgentMetrics -- SPEC-1580
# ---------------------------------------------------------------------------

class TestAgentMetrics:
    """Tests for per-agent detailed metrics."""

    @pytest.mark.asyncio
    async def test_valid_agent_returns_metrics(self, superadmin_ctx):
        """GET /pipeline/agents/{agent}/metrics returns details (TEST-2758)."""
        result = await get_agent_metrics(
            agent="intent-classifier", period="24h"
        )
        assert isinstance(result, AgentDetailMetrics)
        assert result.agent == "intent-classifier"

    @pytest.mark.asyncio
    async def test_unknown_agent_returns_404(self, superadmin_ctx):
        """Unknown agent name returns 404 (TEST-2759)."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_agent_metrics(
                agent="nonexistent-agent", period="24h"
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_agent_metrics_fields(self, superadmin_ctx):
        """Agent detail includes trend arrays (TEST-2760)."""
        result = await get_agent_metrics(
            agent="response-generator", period="24h"
        )
        assert hasattr(result, "latency_trend")
        assert hasattr(result, "token_usage_trend")
        assert hasattr(result, "cost_trend")
        assert hasattr(result, "error_log")


# ---------------------------------------------------------------------------
# TestTenantComparison -- SPEC-1581
# ---------------------------------------------------------------------------

class TestTenantComparison:
    """Tests for tenant pipeline comparison."""

    @pytest.mark.asyncio
    async def test_returns_all_tenants(self, superadmin_ctx):
        """GET /pipeline/tenants returns tenant summaries (TEST-2761)."""
        result = await get_tenant_comparison()
        assert isinstance(result, TenantComparisonResponse)
        assert result.total == 2
        assert len(result.tenants) == 2

    @pytest.mark.asyncio
    async def test_sort_parameters(self, superadmin_ctx):
        """Sort parameters are reflected in response (TEST-2762)."""
        result = await get_tenant_comparison(
            sort_by="avg_latency_ms", sort_order="asc"
        )
        assert result.sort_by == "avg_latency_ms"
        assert result.sort_order == "asc"

    @pytest.mark.asyncio
    async def test_tenant_summary_fields(self, superadmin_ctx):
        """Each tenant has required metric fields (TEST-2763)."""
        result = await get_tenant_comparison()
        tenant = result.tenants[0]
        assert hasattr(tenant, "total_conversations")
        assert hasattr(tenant, "billable_conversations")
        assert hasattr(tenant, "avg_latency_ms")
        assert hasattr(tenant, "error_rate")
        assert hasattr(tenant, "escalation_rate")
        assert hasattr(tenant, "cost")


# ---------------------------------------------------------------------------
# TestTenantDetail -- SPEC-1582
# ---------------------------------------------------------------------------

class TestTenantDetail:
    """Tests for per-tenant pipeline detail."""

    @pytest.mark.asyncio
    async def test_returns_tenant_metrics(self, superadmin_ctx):
        """GET /pipeline/tenants/{id}/metrics returns detail (TEST-2764)."""
        result = await get_tenant_pipeline_metrics(
            tenant_id="tenant-001", period="24h"
        )
        assert isinstance(result, TenantDetailMetrics)
        assert result.tenant_id == "tenant-001"

    @pytest.mark.asyncio
    async def test_detail_includes_trends(self, superadmin_ctx):
        """Detail includes trend and breakdown arrays.

        WI-1640 / S137: intent_distribution and recent_conversations removed
        per SPEC-1843 (tenant business data). Only operational metrics retained.
        """
        result = await get_tenant_pipeline_metrics(
            tenant_id="tenant-001", period="24h"
        )
        assert hasattr(result, "volume_trend")
        assert hasattr(result, "cost_trend")
        assert hasattr(result, "agent_breakdown")
        # intent_distribution REMOVED: tenant business data (SPEC-1843)
        # recent_conversations REMOVED: tenant business data (SPEC-1843)


# ---------------------------------------------------------------------------
# TestDatabaseMetrics -- SPEC-1583
# ---------------------------------------------------------------------------

class TestDatabaseMetrics:
    """Tests for database operational metrics."""

    @pytest.mark.asyncio
    async def test_returns_database_metrics(self, superadmin_ctx):
        """GET /pipeline/database returns metrics (TEST-2766)."""
        result = await get_database_metrics()
        assert isinstance(result, DatabaseMetricsResponse)
        assert hasattr(result, "collections")
        assert hasattr(result, "total_documents")
        assert hasattr(result, "estimated_storage_mb")
        assert hasattr(result, "per_tenant")
        assert hasattr(result, "ru_trend")


# ---------------------------------------------------------------------------
# TestInfrastructureTopology -- SPEC-1786
# ---------------------------------------------------------------------------

class TestInfrastructureTopology:
    """Tests for infrastructure topology endpoint."""

    @pytest.mark.asyncio
    async def test_returns_infrastructure_response(self, superadmin_ctx):
        """GET /pipeline/infrastructure returns topology (SPEC-1786)."""
        result = await get_infrastructure_topology(period="24h")
        assert isinstance(result, InfrastructureTopologyResponse)
        assert result.period == "24h"

    @pytest.mark.asyncio
    async def test_includes_all_infrastructure_nodes(self, superadmin_ctx):
        """Infrastructure topology includes all defined nodes."""
        result = await get_infrastructure_topology(period="24h")
        assert len(result.nodes) == len(INFRASTRUCTURE_NODES)

    @pytest.mark.asyncio
    async def test_includes_all_infrastructure_edges(self, superadmin_ctx):
        """Infrastructure topology includes all defined edges."""
        result = await get_infrastructure_topology(period="24h")
        assert len(result.edges) == len(INFRASTRUCTURE_EDGES_DEF)

    @pytest.mark.asyncio
    async def test_node_categories(self, superadmin_ctx):
        """Nodes have valid categories."""
        result = await get_infrastructure_topology(period="24h")
        valid_categories = {"agent", "azure", "ingress", "egress"}
        for node in result.nodes:
            assert node.category in valid_categories

    @pytest.mark.asyncio
    async def test_node_positions(self, superadmin_ctx):
        """Nodes have spatial position data for topology layout."""
        result = await get_infrastructure_topology(period="24h")
        for node in result.nodes:
            assert "x" in node.position
            assert "y" in node.position

    @pytest.mark.asyncio
    async def test_includes_agent_nodes(self, superadmin_ctx):
        """Infrastructure includes all 7 pipeline agent nodes."""
        result = await get_infrastructure_topology(period="24h")
        agent_nodes = [n for n in result.nodes if n.category == "agent"]
        assert len(agent_nodes) == 7

    @pytest.mark.asyncio
    async def test_includes_azure_services(self, superadmin_ctx):
        """Infrastructure includes Azure service nodes."""
        result = await get_infrastructure_topology(period="24h")
        azure_ids = {n.node_id for n in result.nodes if n.category == "azure"}
        assert "cosmos-db" in azure_ids
        assert "redis" in azure_ids
        assert "azure-openai" in azure_ids
        assert "nats" in azure_ids
        assert "key-vault" in azure_ids

    @pytest.mark.asyncio
    async def test_includes_ingress_points(self, superadmin_ctx):
        """Infrastructure includes all ingress/egress points."""
        result = await get_infrastructure_topology(period="24h")
        ingress_ids = {n.node_id for n in result.nodes if n.category == "ingress"}
        assert "shopify-webhook" in ingress_ids
        assert "widget" in ingress_ids
        assert "standalone-admin" in ingress_ids
        assert "provider-admin" in ingress_ids

    @pytest.mark.asyncio
    async def test_edge_protocol_field(self, superadmin_ctx):
        """Edges have protocol information (SPEC-1847: runtime-detected)."""
        result = await get_infrastructure_topology(period="24h")
        protocols = {e.protocol for e in result.edges}
        assert "HTTPS" in protocols
        # SPEC-1847: Internal agent edges report the runtime transport tier
        # (SLIM, NATS, or HTTP) and RG shows "In-Process" per DCL-002 v4.
        # At least one internal transport protocol must be present.
        internal_transports = {"SLIM", "NATS", "HTTP", "In-Process"}
        assert protocols & internal_transports, (
            f"Expected at least one internal transport in {protocols}, "
            f"valid: {internal_transports}"
        )

    @pytest.mark.asyncio
    async def test_node_status_default_healthy(self, superadmin_ctx):
        """Nodes default to healthy status when no errors."""
        result = await get_infrastructure_topology(period="24h")
        for node in result.nodes:
            assert node.status in ("healthy", "degraded", "error")
