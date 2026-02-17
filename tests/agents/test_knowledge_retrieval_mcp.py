"""Tests for Knowledge Retrieval agent MCP integration (AGNTCY Phase 3A).

Covers: _try_mcp_augmentation, _find_search_tool, _merge_results,
backward compatibility, end-to-end process() flow with MCP.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.knowledge_retrieval import (
    AZURE_EMBEDDING_MODEL,
    KnowledgeRetrievalAgent,
)
from src.multi_tenant.mcp_client import McpToolResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_kb_result(context: str = "KB article content", sources: int = 2) -> dict[str, Any]:
    """Build a standard KB result dict."""
    return {
        "context": context,
        "sources": [
            {"id": f"kb-{i}", "title": f"Article {i}", "entry_type": "faq"}
            for i in range(sources)
        ],
        "model": AZURE_EMBEDDING_MODEL,
        "tokens_input": 50,
        "tokens_output": 0,
    }


def _make_mcp_result(
    context: str = "Product data from storefront",
    sources: int = 1,
    trace: bool = True,
) -> dict[str, Any]:
    """Build a standard MCP result dict."""
    result: dict[str, Any] = {
        "context": context,
        "sources": [
            {
                "id": f"mcp-{i}",
                "title": f"Storefront: search_products",
                "source_type": "mcp",
                "server_name": "shopify-storefront",
                "tool_name": "search_products",
            }
            for i in range(sources)
        ],
        "model": "mcp",
        "tokens_input": 0,
        "tokens_output": 0,
    }
    if trace:
        result["mcp_trace"] = {
            "servers_queried": ["shopify-storefront"],
            "tools_invoked": [
                {"tool": "search_products", "elapsed_ms": 250, "success": True,
                 "server": "shopify-storefront"},
            ],
            "total_elapsed_ms": 300,
        }
    return result


def _make_mcp_configs() -> list[dict[str, Any]]:
    """Build a minimal mcp_configs list for payload injection."""
    return [{
        "server_name": "shopify-storefront",
        "server_url": "https://test-shop.myshopify.com/api/mcp",
        "server_type": "shopify-storefront",
        "enabled": True,
        "read_only": True,
        "shop_domain": "test-shop.myshopify.com",
        "tool_allowlist": [],
        "timeout_ms": 3000,
    }]


def _mock_vectorizer(results: list[dict[str, Any]] | None = None) -> MagicMock:
    """Create a mock KnowledgeVectorizer."""
    v = MagicMock()
    v._configured = True
    v.search = AsyncMock(return_value=results or [])
    v.format_for_pipeline = MagicMock(return_value={
        "context": "KB article content",
        "sources": [{"id": "kb-0", "title": "Article 0"}],
    })
    # Make format_for_pipeline a staticmethod-like call
    return v


_SENTINEL_NO_TOOLS = object()


def _mock_mcp_client(
    available_tools: list[dict[str, Any]] | None | object = None,
    call_result: McpToolResult | None = None,
) -> AsyncMock:
    """Create a mock AgentRedMcpClient returned by create_tenant_mcp_client."""
    client = AsyncMock()
    if available_tools is _SENTINEL_NO_TOOLS:
        client.available_tools = []
    elif available_tools is not None:
        client.available_tools = available_tools
    else:
        client.available_tools = [
            {"name": "search_products", "description": "Search", "input_schema": {}},
        ]
    client.connect = AsyncMock()
    client.close = AsyncMock()
    if call_result is None:
        call_result = McpToolResult(
            tool_name="search_products",
            content=[{"type": "text", "text": "Storefront product data"}],
            is_error=False,
            elapsed_ms=200,
            server_name="shopify-storefront",
        )
    client.call_tool = AsyncMock(return_value=call_result)
    return client


# ---------------------------------------------------------------------------
# TestKrMcpMergeStrategy — KRMCP-01 to KRMCP-05
# ---------------------------------------------------------------------------


class TestKrMcpMergeStrategy:
    """Static _merge_results method — context ordering and source tagging."""

    def test_krmcp_01_both_populated(self) -> None:
        """KRMCP-01: Both KB and MCP results produce combined context."""
        kb = _make_kb_result("KB context here")
        mcp = _make_mcp_result("MCP product data")

        merged = KnowledgeRetrievalAgent._merge_results(kb, mcp)

        assert "KB context here" in merged["context"]
        assert "### Storefront Data" in merged["context"]
        assert "MCP product data" in merged["context"]
        # KB context comes first
        assert merged["context"].index("KB context") < merged["context"].index("Storefront Data")

    def test_krmcp_02_kb_only(self) -> None:
        """KRMCP-02: KB-only returns KB result unchanged."""
        kb = _make_kb_result()
        merged = KnowledgeRetrievalAgent._merge_results(kb, None)
        assert merged is kb

    def test_krmcp_03_mcp_only(self) -> None:
        """KRMCP-03: MCP-only returns MCP result unchanged."""
        mcp = _make_mcp_result()
        merged = KnowledgeRetrievalAgent._merge_results(None, mcp)
        assert merged is mcp

    def test_krmcp_04_sources_combined_with_type_tags(self) -> None:
        """KRMCP-04: Sources from both are combined; KB tagged source_type=kb."""
        kb = _make_kb_result(sources=2)
        mcp = _make_mcp_result(sources=1)

        merged = KnowledgeRetrievalAgent._merge_results(kb, mcp)

        assert len(merged["sources"]) == 3  # 2 KB + 1 MCP
        # KB sources tagged
        assert merged["sources"][0].get("source_type") == "kb"
        assert merged["sources"][1].get("source_type") == "kb"
        # MCP source already tagged
        assert merged["sources"][2].get("source_type") == "mcp"

    def test_krmcp_05_mcp_trace_preserved(self) -> None:
        """KRMCP-05: mcp_trace from MCP result preserved in merged output."""
        kb = _make_kb_result()
        mcp = _make_mcp_result(trace=True)

        merged = KnowledgeRetrievalAgent._merge_results(kb, mcp)

        assert "mcp_trace" in merged
        assert merged["mcp_trace"]["servers_queried"] == ["shopify-storefront"]


# ---------------------------------------------------------------------------
# TestFindSearchTool — KRMCP-06 to KRMCP-08
# ---------------------------------------------------------------------------


class TestFindSearchTool:
    """Static _find_search_tool method — tool selection priority."""

    def test_krmcp_06_search_prefix_preferred(self) -> None:
        """KRMCP-06: search_ prefix is preferred over get_ prefix."""
        tools = [
            {"name": "get_product", "description": "Get product"},
            {"name": "search_products", "description": "Search products"},
        ]
        assert KnowledgeRetrievalAgent._find_search_tool(tools) == "search_products"

    def test_krmcp_07_fallback_to_first(self) -> None:
        """KRMCP-07: Falls back to first tool if no priority prefix matches."""
        tools = [
            {"name": "product_info", "description": "Product info"},
            {"name": "collection_data", "description": "Collection data"},
        ]
        assert KnowledgeRetrievalAgent._find_search_tool(tools) == "product_info"

    def test_krmcp_08_empty_returns_none(self) -> None:
        """KRMCP-08: Returns None for empty tool list."""
        assert KnowledgeRetrievalAgent._find_search_tool([]) is None


# ---------------------------------------------------------------------------
# TestKrMcpAugmentation — KRMCP-09 to KRMCP-18
# ---------------------------------------------------------------------------


class TestKrMcpAugmentation:
    """KR agent MCP augmentation integration."""

    @pytest.mark.asyncio
    async def test_krmcp_09_mcp_augments_kb(self) -> None:
        """KRMCP-09: process() with MCP configs merges KB + MCP results."""
        agent = KnowledgeRetrievalAgent()
        vectorizer = _mock_vectorizer([{"title": "Test", "content": "KB data", "rrf_score": 0.5}])
        agent.configure(knowledge_vectorizer=vectorizer)

        mock_client = _mock_mcp_client()

        with patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            return_value={
                "context": "KB article content",
                "sources": [{"id": "kb-0", "title": "Article 0"}],
            },
        ):
            with patch(
                "src.multi_tenant.mcp_client.create_tenant_mcp_client",
                return_value=mock_client,
            ):
                with patch(
                    "src.multi_tenant.mcp_client.parse_mcp_server_configs",
                ) as mock_parse:
                    from src.multi_tenant.mcp_client import McpServerConfig
                    mock_parse.return_value = [McpServerConfig(
                        server_name="shopify-storefront",
                        server_url="https://test.myshopify.com/api/mcp",
                        server_type="shopify-storefront",
                    )]

                    result = await agent.process(
                        payload={
                            "message": "do you have shoes?",
                            "intent": "product_inquiry",
                            "tenant_id": "t-001",
                            "preferences": {"retrieval_top_k": 5},
                            "mcp_configs": _make_mcp_configs(),
                            "tenant_shop_domain": "test.myshopify.com",
                        },
                        headers={"x-tenant-id": "t-001"},
                    )

        assert "context" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_krmcp_10_mcp_failure_fallthrough(self) -> None:
        """KRMCP-10: MCP failure falls through — KB result still returned."""
        agent = KnowledgeRetrievalAgent()
        vectorizer = _mock_vectorizer([{"title": "Test", "content": "data", "rrf_score": 0.5}])
        agent.configure(knowledge_vectorizer=vectorizer)

        with patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            return_value={
                "context": "KB content",
                "sources": [{"id": "kb-0", "title": "Article"}],
            },
        ):
            with patch(
                "src.multi_tenant.mcp_client.create_tenant_mcp_client",
                side_effect=RuntimeError("connection failed"),
            ):
                with patch(
                    "src.multi_tenant.mcp_client.parse_mcp_server_configs",
                ) as mock_parse:
                    from src.multi_tenant.mcp_client import McpServerConfig
                    mock_parse.return_value = [McpServerConfig(
                        server_name="shopify-storefront",
                        server_url="https://test.myshopify.com/api/mcp",
                        server_type="shopify-storefront",
                    )]

                    result = await agent.process(
                        payload={
                            "message": "do you have shoes?",
                            "intent": "product_inquiry",
                            "tenant_id": "t-001",
                            "preferences": {"retrieval_top_k": 5},
                            "mcp_configs": _make_mcp_configs(),
                        },
                        headers={"x-tenant-id": "t-001"},
                    )

        # KB result still available
        assert result["context"] == "KB content"
        # No MCP trace since it failed completely
        assert "mcp_trace" not in result or result.get("mcp_trace") is None

    @pytest.mark.asyncio
    async def test_krmcp_11_no_configs_skips_mcp(self) -> None:
        """KRMCP-11: Empty mcp_configs skips MCP augmentation entirely."""
        agent = KnowledgeRetrievalAgent()
        vectorizer = _mock_vectorizer([{"title": "Test", "content": "data", "rrf_score": 0.5}])
        agent.configure(knowledge_vectorizer=vectorizer)

        with patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            return_value={
                "context": "KB only",
                "sources": [],
            },
        ):
            result = await agent.process(
                payload={
                    "message": "hello",
                    "intent": "general_inquiry",
                    "tenant_id": "t-001",
                    "preferences": {},
                    "mcp_configs": [],
                },
                headers={"x-tenant-id": "t-001"},
            )

        assert result["context"] == "KB only"
        assert "mcp_trace" not in result

    @pytest.mark.asyncio
    async def test_krmcp_12_try_mcp_returns_none_on_empty_configs(self) -> None:
        """KRMCP-12: _try_mcp_augmentation returns None for empty config list."""
        agent = KnowledgeRetrievalAgent()
        result = await agent._try_mcp_augmentation(
            message="shoes", mcp_configs=[], tenant_shop_domain=None,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_krmcp_13_try_mcp_returns_none_on_invalid_configs(self) -> None:
        """KRMCP-13: _try_mcp_augmentation returns None for all-invalid configs."""
        agent = KnowledgeRetrievalAgent()
        # Missing server_url → parse returns empty
        result = await agent._try_mcp_augmentation(
            message="shoes",
            mcp_configs=[{"server_name": "bad"}],
            tenant_shop_domain=None,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_krmcp_14_try_mcp_success(self) -> None:
        """KRMCP-14: _try_mcp_augmentation returns context + trace on success."""
        agent = KnowledgeRetrievalAgent()
        mock_client = _mock_mcp_client()

        with patch(
            "src.multi_tenant.mcp_client.create_tenant_mcp_client",
            return_value=mock_client,
        ):
            with patch(
                "src.multi_tenant.mcp_client.parse_mcp_server_configs",
            ) as mock_parse:
                from src.multi_tenant.mcp_client import McpServerConfig
                mock_parse.return_value = [McpServerConfig(
                    server_name="shopify-storefront",
                    server_url="https://test.myshopify.com/api/mcp",
                    server_type="shopify-storefront",
                )]

                result = await agent._try_mcp_augmentation(
                    message="shoes",
                    mcp_configs=_make_mcp_configs(),
                    tenant_shop_domain="test.myshopify.com",
                )

        assert result is not None
        assert "Storefront product data" in result["context"]
        assert result["mcp_trace"]["servers_queried"] == ["shopify-storefront"]
        assert len(result["sources"]) == 1
        assert result["sources"][0]["source_type"] == "mcp"

    @pytest.mark.asyncio
    async def test_krmcp_15_try_mcp_no_search_tool(self) -> None:
        """KRMCP-15: MCP server with no matching search tool returns None."""
        agent = KnowledgeRetrievalAgent()
        mock_client = _mock_mcp_client(available_tools=_SENTINEL_NO_TOOLS)  # No tools

        with patch(
            "src.multi_tenant.mcp_client.create_tenant_mcp_client",
            return_value=mock_client,
        ):
            with patch(
                "src.multi_tenant.mcp_client.parse_mcp_server_configs",
            ) as mock_parse:
                from src.multi_tenant.mcp_client import McpServerConfig
                mock_parse.return_value = [McpServerConfig(
                    server_name="shopify-storefront",
                    server_url="https://test.myshopify.com/api/mcp",
                    server_type="shopify-storefront",
                )]

                result = await agent._try_mcp_augmentation(
                    message="shoes",
                    mcp_configs=_make_mcp_configs(),
                    tenant_shop_domain="test.myshopify.com",
                )

        # No tool found → no results, should return None (no tool traces either)
        assert result is None

    @pytest.mark.asyncio
    async def test_krmcp_16_try_mcp_tool_call_error(self) -> None:
        """KRMCP-16: Tool call error produces trace with success=False."""
        agent = KnowledgeRetrievalAgent()
        mock_client = _mock_mcp_client()
        mock_client.call_tool = AsyncMock(side_effect=RuntimeError("tool error"))

        with patch(
            "src.multi_tenant.mcp_client.create_tenant_mcp_client",
            return_value=mock_client,
        ):
            with patch(
                "src.multi_tenant.mcp_client.parse_mcp_server_configs",
            ) as mock_parse:
                from src.multi_tenant.mcp_client import McpServerConfig
                mock_parse.return_value = [McpServerConfig(
                    server_name="shopify-storefront",
                    server_url="https://test.myshopify.com/api/mcp",
                    server_type="shopify-storefront",
                )]

                result = await agent._try_mcp_augmentation(
                    message="shoes",
                    mcp_configs=_make_mcp_configs(),
                    tenant_shop_domain="test.myshopify.com",
                )

        # Should get a result with empty context but trace showing failure
        assert result is not None
        assert result["context"] == ""
        assert len(result["mcp_trace"]["tools_invoked"]) == 1
        assert result["mcp_trace"]["tools_invoked"][0]["success"] is False


# ---------------------------------------------------------------------------
# TestKrMcpBackwardCompat — KRMCP-19 to KRMCP-20
# ---------------------------------------------------------------------------


class TestKrMcpBackwardCompat:
    """Backward compatibility — KR works without any MCP fields."""

    @pytest.mark.asyncio
    async def test_krmcp_19_no_mcp_fields_in_payload(self) -> None:
        """KRMCP-19: Payload without mcp_configs works as before."""
        agent = KnowledgeRetrievalAgent()
        vectorizer = _mock_vectorizer([{"title": "Test", "content": "data", "rrf_score": 0.5}])
        agent.configure(knowledge_vectorizer=vectorizer)

        with patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            return_value={
                "context": "KB content only",
                "sources": [{"id": "kb-0", "title": "Article"}],
            },
        ):
            result = await agent.process(
                payload={
                    "message": "hello",
                    "intent": "general_inquiry",
                    "tenant_id": "t-001",
                    "preferences": {},
                    # No mcp_configs, no tenant_shop_domain
                },
                headers={"x-tenant-id": "t-001"},
            )

        assert result["context"] == "KB content only"
        assert "mcp_trace" not in result

    @pytest.mark.asyncio
    async def test_krmcp_20_empty_tenant_id(self) -> None:
        """KRMCP-20: Empty tenant_id returns empty result."""
        agent = KnowledgeRetrievalAgent()

        result = await agent.process(
            payload={"message": "hello"},
            headers={},
        )

        assert result["context"] == ""
        assert result["sources"] == []
