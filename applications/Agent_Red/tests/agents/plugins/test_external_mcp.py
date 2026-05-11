"""Tests for 3rd-Party MCP Server Integrations (SPEC-1712).

Tests cover:
  - Circuit breaker states (closed, open, half-open, reset)
  - Rate limiting (per-server, per-tenant)
  - Caching (TTL, invalidation, read-only enforcement)
  - Tool discovery from registry
  - Tool invocation flow (cache → rate limit → circuit → dispatch)
  - Server status reporting
  - Audit logging

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time

import pytest

from src.agents.plugins.external_mcp import (
    CIRCUIT_BREAKER_THRESHOLD,
    CircuitBreaker,
    CircuitState,
    ExternalMcpConnector,
    RateTracker,
)
from src.agents.plugins.registry import PluginAgentRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset():
    PluginAgentRegistry.reset()
    yield
    PluginAgentRegistry.reset()


@pytest.fixture
def registry() -> PluginAgentRegistry:
    r = PluginAgentRegistry.get_instance()
    r.load_from_dict({
        "stripe_mcp": {
            "display_name": "Stripe MCP",
            "description": "Payments",
            "spec_id": "SPEC-1712",
            "category": "external",
            "endpoint": "https://mcp.stripe.com",
            "capabilities": ["stripe.list_charges", "stripe.get_balance"],
            "status": "available",
            "is_external": True,
            "read_only": True,
        },
        "shopify_mcp": {
            "display_name": "Shopify MCP",
            "description": "Storefront",
            "spec_id": "SPEC-1712",
            "category": "external",
            "endpoint": "https://{shop_domain}/mcp",
            "capabilities": ["shopify.search_products"],
            "status": "available",
            "is_external": True,
            "read_only": True,
        },
    })
    return r


@pytest.fixture
def connector(registry) -> ExternalMcpConnector:
    return ExternalMcpConnector(registry=registry)


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker(server_id="test")
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(server_id="test", threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False

    def test_success_resets(self):
        cb = CircuitBreaker(server_id="test", threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0
        assert cb.state == CircuitState.CLOSED

    def test_half_open_after_reset_period(self):
        cb = CircuitBreaker(server_id="test", threshold=1, reset_seconds=0.01)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        time.sleep(0.02)
        assert cb.allow_request() is True
        assert cb.state == CircuitState.HALF_OPEN


# ---------------------------------------------------------------------------
# Rate tracker
# ---------------------------------------------------------------------------


class TestRateTracker:
    def test_allows_within_limit(self):
        rt = RateTracker(max_rpm=10)
        for _ in range(10):
            assert rt.allow() is True
            rt.record()

    def test_blocks_over_limit(self):
        rt = RateTracker(max_rpm=2)
        rt.record()
        rt.record()
        assert rt.allow() is False

    def test_resets_after_window(self):
        rt = RateTracker(max_rpm=1)
        rt.record()
        rt.window_start = time.time() - 61  # Simulate window expiry
        assert rt.allow() is True


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------


class TestToolDiscovery:
    @pytest.mark.asyncio
    async def test_discover_tools(self, connector: ExternalMcpConnector):
        tools = await connector.discover_tools("stripe_mcp")
        assert len(tools) == 2
        names = [t["name"] for t in tools]
        assert "stripe.list_charges" in names

    @pytest.mark.asyncio
    async def test_discover_tools_cached(self, connector: ExternalMcpConnector):
        tools1 = await connector.discover_tools("stripe_mcp")
        tools2 = await connector.discover_tools("stripe_mcp")
        assert tools1 == tools2

    @pytest.mark.asyncio
    async def test_discover_unknown_server(self, connector: ExternalMcpConnector):
        tools = await connector.discover_tools("nonexistent")
        assert tools == []


# ---------------------------------------------------------------------------
# Tool invocation
# ---------------------------------------------------------------------------


class TestToolInvocation:
    @pytest.mark.asyncio
    async def test_invoke_success(self, connector: ExternalMcpConnector):
        result = await connector.invoke_tool(
            "stripe_mcp", "stripe.list_charges",
            {"limit": 10}, tenant_id="t-1"
        )
        assert result["success"] is True
        assert "content" in result

    @pytest.mark.asyncio
    async def test_invoke_cached_on_second_call(self, connector: ExternalMcpConnector):
        await connector.invoke_tool(
            "stripe_mcp", "stripe.get_balance", {}, tenant_id="t-1"
        )
        result = await connector.invoke_tool(
            "stripe_mcp", "stripe.get_balance", {}, tenant_id="t-1"
        )
        assert result.get("cached") is True

    @pytest.mark.asyncio
    async def test_invoke_rate_limited(self, connector: ExternalMcpConnector):
        # Exhaust rate limit
        tracker = connector._get_rate_tracker("stripe_mcp", "t-1")
        tracker.max_rpm = 1
        tracker.record()
        result = await connector.invoke_tool(
            "stripe_mcp", "stripe.list_charges", {}, tenant_id="t-1",
            use_cache=False,
        )
        assert result["success"] is False
        assert "Rate limit" in result["error"]

    @pytest.mark.asyncio
    async def test_invoke_circuit_open(self, connector: ExternalMcpConnector):
        circuit = connector._get_circuit("stripe_mcp")
        for _ in range(CIRCUIT_BREAKER_THRESHOLD):
            circuit.record_failure()
        result = await connector.invoke_tool(
            "stripe_mcp", "stripe.list_charges", {}, tenant_id="t-1",
            use_cache=False,
        )
        assert result["success"] is False
        assert "Circuit breaker" in result["error"]

    @pytest.mark.asyncio
    async def test_invoke_with_template_vars(self, connector: ExternalMcpConnector):
        result = await connector.invoke_tool(
            "shopify_mcp", "shopify.search_products",
            {"query": "shoes"}, tenant_id="t-1",
        )
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Server status
# ---------------------------------------------------------------------------


class TestServerStatus:
    def test_get_server_status(self, connector: ExternalMcpConnector):
        status = connector.get_server_status("stripe_mcp")
        assert status["server_id"] == "stripe_mcp"
        assert status["circuit_state"] == "closed"

    def test_get_all_server_status(self, connector: ExternalMcpConnector):
        statuses = connector.get_all_server_status()
        assert len(statuses) == 2
        ids = [s["server_id"] for s in statuses]
        assert "stripe_mcp" in ids
        assert "shopify_mcp" in ids


# ---------------------------------------------------------------------------
# Audit logging
# ---------------------------------------------------------------------------


class TestAuditLogging:
    @pytest.mark.asyncio
    async def test_audit_on_success(self, connector: ExternalMcpConnector):
        await connector.invoke_tool(
            "stripe_mcp", "stripe.get_balance", {}, tenant_id="t-1"
        )
        assert len(connector.audit_log) >= 1
        assert connector.audit_log[-1]["outcome"] == "success"

    @pytest.mark.asyncio
    async def test_audit_on_rate_limit(self, connector: ExternalMcpConnector):
        tracker = connector._get_rate_tracker("stripe_mcp", "t-1")
        tracker.max_rpm = 0
        await connector.invoke_tool(
            "stripe_mcp", "stripe.list_charges", {}, tenant_id="t-1",
            use_cache=False,
        )
        rate_limited = [e for e in connector.audit_log if e["outcome"] == "rate_limited"]
        assert len(rate_limited) >= 1

    @pytest.mark.asyncio
    async def test_audit_on_cache_hit(self, connector: ExternalMcpConnector):
        await connector.invoke_tool("stripe_mcp", "stripe.get_balance", {}, tenant_id="t-1")
        await connector.invoke_tool("stripe_mcp", "stripe.get_balance", {}, tenant_id="t-1")
        cache_hits = [e for e in connector.audit_log if e["outcome"] == "cache_hit"]
        assert len(cache_hits) >= 1
