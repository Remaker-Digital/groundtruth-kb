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
    PipelineTopologyResponse,
    TenantComparisonResponse,
    TenantDetailMetrics,
    configure_superadmin_services,
    get_agent_metrics,
    get_database_metrics,
    get_pipeline_topology,
    get_tenant_comparison,
    get_tenant_pipeline_metrics,
    PIPELINE_AGENTS,
    PIPELINE_EDGES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_tenant_repo():
    repo = MagicMock()
    repo.list_active_tenant_ids = AsyncMock(
        return_value=["tenant-001", "tenant-002"]
    )
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
        result = await get_pipeline_topology(period="24h", _ctx=superadmin_ctx)
        assert isinstance(result, PipelineTopologyResponse)
        assert len(result.nodes) == 7
        agent_names = {n.agent for n in result.nodes}
        assert agent_names == set(PIPELINE_AGENTS)

    @pytest.mark.asyncio
    async def test_topology_returns_edges(self, superadmin_ctx):
        """GET /pipeline/topology returns pipeline edges (TEST-2755)."""
        result = await get_pipeline_topology(period="24h", _ctx=superadmin_ctx)
        assert len(result.edges) == len(PIPELINE_EDGES)
        for edge in result.edges:
            assert edge.source in PIPELINE_AGENTS
            assert edge.target in PIPELINE_AGENTS

    @pytest.mark.asyncio
    async def test_topology_period_parameter(self, superadmin_ctx):
        """Period parameter is reflected in response (TEST-2756)."""
        result = await get_pipeline_topology(period="7d", _ctx=superadmin_ctx)
        assert result.period == "7d"

    @pytest.mark.asyncio
    async def test_node_metrics_structure(self, superadmin_ctx):
        """Each node has required metric fields (TEST-2757)."""
        result = await get_pipeline_topology(period="24h", _ctx=superadmin_ctx)
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
            agent="intent-classifier", period="24h", _ctx=superadmin_ctx
        )
        assert isinstance(result, AgentDetailMetrics)
        assert result.agent == "intent-classifier"

    @pytest.mark.asyncio
    async def test_unknown_agent_returns_404(self, superadmin_ctx):
        """Unknown agent name returns 404 (TEST-2759)."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_agent_metrics(
                agent="nonexistent-agent", period="24h", _ctx=superadmin_ctx
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_agent_metrics_fields(self, superadmin_ctx):
        """Agent detail includes trend arrays (TEST-2760)."""
        result = await get_agent_metrics(
            agent="response-generator", period="24h", _ctx=superadmin_ctx
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
        result = await get_tenant_comparison(_ctx=superadmin_ctx)
        assert isinstance(result, TenantComparisonResponse)
        assert result.total == 2
        assert len(result.tenants) == 2

    @pytest.mark.asyncio
    async def test_sort_parameters(self, superadmin_ctx):
        """Sort parameters are reflected in response (TEST-2762)."""
        result = await get_tenant_comparison(
            sort_by="avg_latency_ms", sort_order="asc", _ctx=superadmin_ctx
        )
        assert result.sort_by == "avg_latency_ms"
        assert result.sort_order == "asc"

    @pytest.mark.asyncio
    async def test_tenant_summary_fields(self, superadmin_ctx):
        """Each tenant has required metric fields (TEST-2763)."""
        result = await get_tenant_comparison(_ctx=superadmin_ctx)
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
            tenant_id="tenant-001", period="24h", _ctx=superadmin_ctx
        )
        assert isinstance(result, TenantDetailMetrics)
        assert result.tenant_id == "tenant-001"

    @pytest.mark.asyncio
    async def test_detail_includes_trends(self, superadmin_ctx):
        """Detail includes trend and breakdown arrays (TEST-2765)."""
        result = await get_tenant_pipeline_metrics(
            tenant_id="tenant-001", period="24h", _ctx=superadmin_ctx
        )
        assert hasattr(result, "volume_trend")
        assert hasattr(result, "cost_trend")
        assert hasattr(result, "agent_breakdown")
        assert hasattr(result, "intent_distribution")
        assert hasattr(result, "recent_conversations")


# ---------------------------------------------------------------------------
# TestDatabaseMetrics -- SPEC-1583
# ---------------------------------------------------------------------------

class TestDatabaseMetrics:
    """Tests for database operational metrics."""

    @pytest.mark.asyncio
    async def test_returns_database_metrics(self, superadmin_ctx):
        """GET /pipeline/database returns metrics (TEST-2766)."""
        result = await get_database_metrics(_ctx=superadmin_ctx)
        assert isinstance(result, DatabaseMetricsResponse)
        assert hasattr(result, "collections")
        assert hasattr(result, "total_documents")
        assert hasattr(result, "estimated_storage_mb")
        assert hasattr(result, "per_tenant")
        assert hasattr(result, "ru_trend")
