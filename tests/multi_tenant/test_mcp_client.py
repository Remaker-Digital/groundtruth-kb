"""Tests for MCP client module (AGNTCY Phase 3A).

Covers: McpServerConfig, shop domain validation, tool classification,
policy gate, AgentRedMcpClient, config builders, config resolvers.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.mcp_client import (
    DEFAULT_MCP_TIMEOUT_MS,
    READ_PREFIXES,
    MUTATE_PREFIXES,
    SERVER_TYPE_DEFAULTS,
    AgentRedMcpClient,
    McpServerConfig,
    McpToolBlockedError,
    McpToolResult,
    McpTimeoutError,
    McpQueryResult,
    build_storefront_mcp_config,
    classify_tool,
    create_tenant_mcp_client,
    is_tool_allowed,
    parse_mcp_server_config,
    parse_mcp_server_configs,
    resolve_mcp_configs,
    validate_shop_domain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(**overrides: Any) -> McpServerConfig:
    """Build a test McpServerConfig with sensible defaults."""
    defaults: dict[str, Any] = {
        "server_name": "test-server",
        "server_url": "https://test-shop.myshopify.com/api/mcp",
        "server_type": "shopify-storefront",
        "enabled": True,
        "read_only": True,
        "shop_domain": "test-shop.myshopify.com",
        "tool_allowlist": [],
        "timeout_ms": 3000,
    }
    defaults.update(overrides)
    return McpServerConfig(**defaults)


def _make_breaker(is_open: bool = False) -> MagicMock:
    """Create a mock circuit breaker."""
    breaker = MagicMock()
    breaker.is_open = is_open
    breaker.record_success = MagicMock()
    breaker.record_failure = MagicMock()
    return breaker


def _make_pii_scrubber() -> MagicMock:
    """Create a mock PII scrubber that uppercases text (traceable)."""
    scrubber = MagicMock()
    scrubber.scrub_text = MagicMock(side_effect=lambda t: f"[SCRUBBED:{t}]")
    return scrubber


def _make_tool_result(content_text: str = "result data", is_error: bool = False) -> MagicMock:
    """Create a mock CallToolResult from the mcp SDK."""
    text_content = SimpleNamespace(text=content_text, type="text")
    result = MagicMock()
    result.content = [text_content]
    result.isError = is_error
    return result


# ---------------------------------------------------------------------------
# TestMcpServerConfig — MCP-01 to MCP-03
# ---------------------------------------------------------------------------


class TestMcpServerConfig:
    """Configuration dataclass validation."""

    def test_mcp_01_valid_config(self) -> None:
        """MCP-01: Valid McpServerConfig with all fields."""
        cfg = _make_config()
        assert cfg.server_name == "test-server"
        assert cfg.server_url == "https://test-shop.myshopify.com/api/mcp"
        assert cfg.server_type == "shopify-storefront"
        assert cfg.enabled is True
        assert cfg.read_only is True
        assert cfg.shop_domain == "test-shop.myshopify.com"
        assert cfg.tool_allowlist == []
        assert cfg.timeout_ms == 3000

    def test_mcp_02_defaults(self) -> None:
        """MCP-02: McpServerConfig defaults for optional fields."""
        cfg = McpServerConfig(server_name="x", server_url="https://example.com")
        assert cfg.server_type == "custom"
        assert cfg.enabled is True
        assert cfg.read_only is True
        assert cfg.shop_domain is None
        assert cfg.tool_allowlist == []
        assert cfg.timeout_ms == DEFAULT_MCP_TIMEOUT_MS

    def test_mcp_03_data_models(self) -> None:
        """MCP-03: McpToolResult and McpQueryResult shape."""
        tr = McpToolResult(
            tool_name="search_products",
            content=[{"type": "text", "text": "data"}],
            is_error=False,
            elapsed_ms=100.5,
            server_name="storefront",
        )
        assert tr.tool_name == "search_products"
        assert tr.is_error is False

        qr = McpQueryResult(
            results=[tr],
            context_text="context",
            sources=[],
            trace={"servers_queried": ["storefront"]},
            total_elapsed_ms=200.0,
        )
        assert len(qr.results) == 1
        assert qr.total_elapsed_ms == 200.0


# ---------------------------------------------------------------------------
# TestShopDomainValidation — MCP-04 to MCP-08
# ---------------------------------------------------------------------------


class TestShopDomainValidation:
    """Shop domain guard — cross-tenant URL isolation."""

    def test_mcp_04_matching_domains(self) -> None:
        """MCP-04: Same myshopify.com domain matches."""
        assert validate_shop_domain(
            "https://blanco-9939.myshopify.com/api/mcp",
            "blanco-9939.myshopify.com",
        ) is True

    def test_mcp_05_mismatched_domains(self) -> None:
        """MCP-05: Different myshopify.com domain rejected."""
        assert validate_shop_domain(
            "https://other-shop.myshopify.com/api/mcp",
            "blanco-9939.myshopify.com",
        ) is False

    def test_mcp_06_non_myshopify_url(self) -> None:
        """MCP-06: Non-myshopify.com URL always rejected."""
        assert validate_shop_domain(
            "https://evil.example.com/api/mcp",
            "blanco-9939.myshopify.com",
        ) is False

    def test_mcp_07_non_myshopify_expected(self) -> None:
        """MCP-07: Non-myshopify expected domain always rejected."""
        assert validate_shop_domain(
            "https://blanco-9939.myshopify.com/api/mcp",
            "example.com",
        ) is False

    def test_mcp_08_case_insensitive(self) -> None:
        """MCP-08: Domain comparison is case-insensitive."""
        assert validate_shop_domain(
            "https://Blanco-9939.Myshopify.Com/api/mcp",
            "BLANCO-9939.MYSHOPIFY.COM",
        ) is True


# ---------------------------------------------------------------------------
# TestToolClassification — MCP-09 to MCP-14
# ---------------------------------------------------------------------------


class TestToolClassification:
    """Tool read/mutate classification by prefix and server type."""

    def test_mcp_09_read_prefix(self) -> None:
        """MCP-09: Tools with read prefixes classified as read."""
        for prefix in READ_PREFIXES:
            tool_name = f"{prefix}products"
            assert classify_tool(tool_name, "custom") == "read", tool_name

    def test_mcp_10_mutate_prefix(self) -> None:
        """MCP-10: Tools with mutate prefixes classified as mutate."""
        for prefix in MUTATE_PREFIXES:
            tool_name = f"{prefix}order"
            assert classify_tool(tool_name, "shopify-storefront") == "mutate", tool_name

    def test_mcp_11_storefront_default_read(self) -> None:
        """MCP-11: Unknown tool on shopify-storefront defaults to read."""
        assert classify_tool("product_info", "shopify-storefront") == "read"

    def test_mcp_12_unknown_server_default_mutate(self) -> None:
        """MCP-12: Unknown tool on unknown server defaults to mutate."""
        assert classify_tool("do_something", "unknown-server") == "mutate"

    def test_mcp_13_stripe_default_mutate(self) -> None:
        """MCP-13: Unknown tool on stripe server defaults to mutate."""
        assert classify_tool("balance_info", "stripe") == "mutate"

    def test_mcp_14_prefix_takes_priority(self) -> None:
        """MCP-14: Prefix classification overrides server-type default."""
        # search_ prefix = read, even on stripe (mutate default)
        assert classify_tool("search_charges", "stripe") == "read"
        # delete_ prefix = mutate, even on shopify-storefront (read default)
        assert classify_tool("delete_cache", "shopify-storefront") == "mutate"


# ---------------------------------------------------------------------------
# TestPolicyGate — MCP-15 to MCP-17
# ---------------------------------------------------------------------------


class TestPolicyGate:
    """Read-only policy gate + allowlist enforcement."""

    def test_mcp_15_read_allowed_on_readonly(self) -> None:
        """MCP-15: Read tool allowed on read-only server."""
        assert is_tool_allowed("search_products", "shopify-storefront", True, []) is True

    def test_mcp_16_mutate_blocked_on_readonly(self) -> None:
        """MCP-16: Mutate tool blocked on read-only server."""
        assert is_tool_allowed("delete_product", "shopify-storefront", True, []) is False

    def test_mcp_17_mutate_allowed_on_rw_server(self) -> None:
        """MCP-17: Mutate tool allowed on non-read-only server."""
        assert is_tool_allowed("update_order", "stripe", False, []) is True

    def test_mcp_17b_allowlist_blocks(self) -> None:
        """MCP-17b: Tool not in non-empty allowlist is blocked."""
        assert is_tool_allowed(
            "search_products", "shopify-storefront", True,
            ["list_collections"],
        ) is False

    def test_mcp_17c_allowlist_permits(self) -> None:
        """MCP-17c: Tool in non-empty allowlist is permitted."""
        assert is_tool_allowed(
            "search_products", "shopify-storefront", True,
            ["search_products", "list_collections"],
        ) is True


# ---------------------------------------------------------------------------
# TestAgentRedMcpClient — MCP-18 to MCP-24
# ---------------------------------------------------------------------------


class TestAgentRedMcpClient:
    """Core MCP client lifecycle: connect, call_tool, close."""

    @pytest.mark.asyncio
    async def test_mcp_18_connect_discovers_tools(self) -> None:
        """MCP-18: connect() discovers available tools from server via AgntcyFactory."""
        cfg = _make_config()
        client = AgentRedMcpClient(cfg)

        # Mock the AgntcyFactory MCP client (routed via create_mcp_client)
        mock_tool = SimpleNamespace(
            name="search_products",
            description="Search products",
            inputSchema=None,
        )
        mock_tools_result = SimpleNamespace(tools=[mock_tool])
        mock_session = AsyncMock()
        mock_session.initialize = AsyncMock()
        mock_session.list_tools = AsyncMock(return_value=mock_tools_result)

        # create_mcp_client returns a context manager that yields the session
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "src.multi_tenant.agntcy_sdk_integration.create_mcp_client",
            return_value=mock_cm,
        ):
            await client.connect()

        assert len(client.available_tools) == 1
        assert client.available_tools[0]["name"] == "search_products"
        await client.close()

    @pytest.mark.asyncio
    async def test_mcp_19_call_tool_success(self) -> None:
        """MCP-19: call_tool() returns McpToolResult on success."""
        cfg = _make_config()
        breaker = _make_breaker(is_open=False)
        client = AgentRedMcpClient(cfg, circuit_breaker=breaker)

        # Inject a mock session directly
        mock_result = _make_tool_result("product data")
        client._session = AsyncMock()
        client._session.call_tool = AsyncMock(return_value=mock_result)

        result = await client.call_tool("search_products", {"query": "shoes"})

        assert isinstance(result, McpToolResult)
        assert result.tool_name == "search_products"
        assert result.is_error is False
        assert len(result.content) == 1
        assert result.content[0]["type"] == "text"
        assert result.content[0]["text"] == "product data"
        breaker.record_success.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_20_call_tool_timeout(self) -> None:
        """MCP-20: call_tool() raises McpTimeoutError on timeout."""
        cfg = _make_config(timeout_ms=100)
        breaker = _make_breaker()
        client = AgentRedMcpClient(cfg, circuit_breaker=breaker)

        async def _slow_call(*args: Any, **kwargs: Any) -> None:
            await asyncio.sleep(10)

        client._session = AsyncMock()
        client._session.call_tool = _slow_call

        with pytest.raises(McpTimeoutError) as exc_info:
            await client.call_tool("search_products", {"query": "shoes"})

        assert exc_info.value.tool_name == "search_products"
        assert exc_info.value.timeout_ms == 100
        breaker.record_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_21_breaker_open_blocks(self) -> None:
        """MCP-21: call_tool() raises when circuit breaker is open."""
        cfg = _make_config()
        breaker = _make_breaker(is_open=True)
        client = AgentRedMcpClient(cfg, circuit_breaker=breaker)
        client._session = AsyncMock()

        with pytest.raises(Exception, match="mcp-test-server"):
            await client.call_tool("search_products", {"query": "shoes"})

    @pytest.mark.asyncio
    async def test_mcp_22_failure_records_on_breaker(self) -> None:
        """MCP-22: Exceptions during call_tool record failure on breaker."""
        cfg = _make_config()
        breaker = _make_breaker()
        client = AgentRedMcpClient(cfg, circuit_breaker=breaker)

        client._session = AsyncMock()
        client._session.call_tool = AsyncMock(side_effect=RuntimeError("network"))

        with pytest.raises(RuntimeError, match="network"):
            await client.call_tool("search_products", {"query": "shoes"})

        breaker.record_failure.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_23_pii_scrub_arguments(self) -> None:
        """MCP-23: PII scrubber is applied to string arguments before call."""
        cfg = _make_config()
        scrubber = _make_pii_scrubber()
        client = AgentRedMcpClient(cfg, pii_scrubber=scrubber)

        mock_result = _make_tool_result("data")
        client._session = AsyncMock()
        client._session.call_tool = AsyncMock(return_value=mock_result)

        await client.call_tool("search_products", {"query": "john@example.com"})

        # Verify scrubbed args were passed to session
        call_args = client._session.call_tool.call_args
        assert call_args[0][1]["query"] == "[SCRUBBED:john@example.com]"

    @pytest.mark.asyncio
    async def test_mcp_24_policy_blocks_mutation(self) -> None:
        """MCP-24: call_tool() raises McpToolBlockedError for mutations on read-only."""
        cfg = _make_config(read_only=True)
        client = AgentRedMcpClient(cfg)
        client._session = AsyncMock()

        with pytest.raises(McpToolBlockedError) as exc_info:
            await client.call_tool("delete_product", {"id": "123"})

        assert exc_info.value.tool_name == "delete_product"
        assert exc_info.value.reason == "mutation_blocked"

    @pytest.mark.asyncio
    async def test_mcp_24b_not_connected_raises(self) -> None:
        """MCP-24b: call_tool() raises RuntimeError if not connected."""
        cfg = _make_config()
        client = AgentRedMcpClient(cfg)
        # session is None by default

        with pytest.raises(RuntimeError, match="not connected"):
            await client.call_tool("search_products", {"query": "shoes"})


# ---------------------------------------------------------------------------
# TestBuildStorefrontConfig — MCP-25 to MCP-27
# ---------------------------------------------------------------------------


class TestBuildStorefrontConfig:
    """Storefront MCP config auto-generation."""

    def test_mcp_25_url_format(self) -> None:
        """MCP-25: build_storefront_mcp_config produces correct URL."""
        raw = build_storefront_mcp_config("blanco-9939.myshopify.com")
        assert raw["server_url"] == "https://blanco-9939.myshopify.com/api/mcp"

    def test_mcp_26_read_only_flag(self) -> None:
        """MCP-26: Storefront config is always read-only."""
        raw = build_storefront_mcp_config("test.myshopify.com")
        assert raw["read_only"] is True
        assert raw["server_type"] == "shopify-storefront"

    def test_mcp_27_timeout(self) -> None:
        """MCP-27: Storefront config uses default timeout."""
        raw = build_storefront_mcp_config("test.myshopify.com")
        assert raw["timeout_ms"] == DEFAULT_MCP_TIMEOUT_MS
        assert raw["enabled"] is True
        assert raw["tool_allowlist"] == []


# ---------------------------------------------------------------------------
# TestParseMcpServerConfig — MCP-28 to MCP-30
# ---------------------------------------------------------------------------


class TestParseMcpServerConfig:
    """Config parsing and validation."""

    def test_mcp_28_valid_config(self) -> None:
        """MCP-28: Valid raw dict parses to McpServerConfig."""
        raw = build_storefront_mcp_config("test.myshopify.com")
        cfg = parse_mcp_server_config(raw)
        assert cfg is not None
        assert cfg.server_name == "shopify-storefront"

    def test_mcp_29_missing_url_returns_none(self) -> None:
        """MCP-29: Missing server_url returns None."""
        cfg = parse_mcp_server_config({"server_name": "test"})
        assert cfg is None

    def test_mcp_30_missing_name_returns_none(self) -> None:
        """MCP-30: Missing server_name returns None."""
        cfg = parse_mcp_server_config({"server_url": "https://example.com"})
        assert cfg is None

    def test_mcp_30b_parse_multiple_filters_disabled(self) -> None:
        """MCP-30b: parse_mcp_server_configs skips disabled configs."""
        raw_list = [
            {"server_name": "a", "server_url": "https://a.com", "enabled": True},
            {"server_name": "b", "server_url": "https://b.com", "enabled": False},
            {"server_name": "c", "server_url": "https://c.com"},  # default: enabled
        ]
        configs = parse_mcp_server_configs(raw_list)
        names = [c.server_name for c in configs]
        assert "a" in names
        assert "b" not in names
        assert "c" in names


# ---------------------------------------------------------------------------
# TestResolveMcpConfigs — MCP-31 to MCP-34
# ---------------------------------------------------------------------------


class TestResolveMcpConfigs:
    """Lazy MCP config resolution from preferences + tenant."""

    def test_mcp_31_explicit_priority(self) -> None:
        """MCP-31: Explicit mcp_servers + mcp_enabled takes priority."""
        prefs = SimpleNamespace(
            mcp_enabled=True,
            mcp_servers=[
                {"server_name": "custom", "server_url": "https://custom.example.com",
                 "enabled": True},
            ],
            shopify_integration_status="connected",
        )
        tenant = SimpleNamespace(shopify_shop_domain="test.myshopify.com")
        configs = resolve_mcp_configs(prefs, tenant)
        assert len(configs) == 1
        assert configs[0].server_name == "custom"

    def test_mcp_32_auto_populate_shopify(self) -> None:
        """MCP-32: Auto-generate storefront config when Shopify connected."""
        prefs = SimpleNamespace(
            mcp_enabled=False,
            mcp_servers=[],
            shopify_integration_status="connected",
        )
        tenant = SimpleNamespace(shopify_shop_domain="blanco-9939.myshopify.com")
        configs = resolve_mcp_configs(prefs, tenant)
        assert len(configs) == 1
        assert configs[0].server_type == "shopify-storefront"
        assert "blanco-9939" in configs[0].server_url

    def test_mcp_33_disconnected_returns_empty(self) -> None:
        """MCP-33: Disconnected Shopify returns no configs."""
        prefs = SimpleNamespace(
            mcp_enabled=False,
            mcp_servers=[],
            shopify_integration_status="disconnected",
        )
        tenant = SimpleNamespace(shopify_shop_domain="blanco-9939.myshopify.com")
        configs = resolve_mcp_configs(prefs, tenant)
        assert configs == []

    def test_mcp_34_disabled_returns_empty(self) -> None:
        """MCP-34: No shop domain returns empty list."""
        prefs = SimpleNamespace(
            mcp_enabled=False,
            mcp_servers=[],
            shopify_integration_status="connected",
        )
        tenant = SimpleNamespace()  # no shopify_shop_domain
        configs = resolve_mcp_configs(prefs, tenant)
        assert configs == []


# ---------------------------------------------------------------------------
# TestCreateTenantMcpClient — MCP-35 to MCP-37
# ---------------------------------------------------------------------------


class TestCreateTenantMcpClient:
    """Factory function with shop_domain guard and breaker resolution."""

    @pytest.mark.asyncio
    async def test_mcp_35_valid_domain_passes(self) -> None:
        """MCP-35: Factory succeeds with matching shop domain."""
        cfg = _make_config(
            server_url="https://test-shop.myshopify.com/api/mcp",
            server_type="shopify-storefront",
        )
        with patch(
            "src.multi_tenant.pipeline_resilience.get_circuit_breaker",
            side_effect=RuntimeError("no registry"),
        ):
            client = await create_tenant_mcp_client(
                config=cfg,
                tenant_shop_domain="test-shop.myshopify.com",
            )
        assert isinstance(client, AgentRedMcpClient)

    @pytest.mark.asyncio
    async def test_mcp_36_mismatched_domain_raises(self) -> None:
        """MCP-36: Factory raises ValueError for mismatched shop domain."""
        cfg = _make_config(
            server_url="https://other-shop.myshopify.com/api/mcp",
            server_type="shopify-storefront",
        )
        with pytest.raises(ValueError, match="does not match"):
            await create_tenant_mcp_client(
                config=cfg,
                tenant_shop_domain="test-shop.myshopify.com",
            )

    @pytest.mark.asyncio
    async def test_mcp_37_no_domain_skips_guard(self) -> None:
        """MCP-37: Factory skips domain guard when tenant_shop_domain is None."""
        cfg = _make_config(server_type="shopify-storefront")
        with patch(
            "src.multi_tenant.pipeline_resilience.get_circuit_breaker",
            side_effect=RuntimeError("no registry"),
        ):
            client = await create_tenant_mcp_client(config=cfg)
        assert isinstance(client, AgentRedMcpClient)
