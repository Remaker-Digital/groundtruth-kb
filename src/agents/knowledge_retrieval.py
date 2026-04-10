# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# Agent Red Customer Experience — Knowledge Retrieval Agent
#
# Retrieves relevant knowledge base articles for a customer query using
# hybrid vector + BM25 search with Reciprocal Rank Fusion (RRF).
# Falls back to keyword search if the vectorizer is unavailable.
#
# Extracted from pipeline.py _call_knowledge_retrieval_direct().
#
# Input payload:
#   {"message": str, "intent": str, "system_prompt": str,
#    "tenant_id": str, "preferences": dict (optional),
#    "mcp_configs": list[dict] (optional), "tenant_shop_domain": str (optional)}
#
# Output payload:
#   {"context": str, "sources": [{"id": str, "title": str, ...}],
#    "model": str, "tokens_input": int, "tokens_output": int,
#    "mcp_trace": dict (optional)}
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import logging
import os
import time
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)

AZURE_EMBEDDING_MODEL = os.environ.get(
    "AZURE_EMBEDDING_MODEL", "text-embedding-3-large"
)

# Stopwords for fallback keyword search
_STOP = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall",
    "of", "in", "to", "for", "with", "on", "at", "by", "from",
    "and", "or", "but", "not", "no", "so", "if", "as", "it",
    "its", "this", "that", "what", "which", "who", "how",
    "your", "you", "my", "me", "i", "we", "our", "they",
    "their", "them", "he", "she", "his", "her",
}


class KnowledgeRetrievalAgent(AgentRedBaseAgent):
    """Retrieve relevant knowledge for customer queries.

    Primary path: hybrid vector + BM25 via KnowledgeVectorizer.
    Secondary path (Phase 3): MCP tool augmentation for live storefront data.
    Fallback: keyword overlap search via KnowledgeBaseRepository.
    """

    agent_type = "knowledge-retrieval"

    def __init__(
        self,
        kb_repo: Any = None,
        knowledge_vectorizer: Any = None,
    ) -> None:
        super().__init__()
        self._kb_repo = kb_repo
        self._knowledge_vectorizer = knowledge_vectorizer

    def configure(
        self,
        kb_repo: Any = None,
        knowledge_vectorizer: Any = None,
    ) -> None:
        """Inject dependencies after construction."""
        if kb_repo is not None:
            self._kb_repo = kb_repo
        if knowledge_vectorizer is not None:
            self._knowledge_vectorizer = knowledge_vectorizer
        self._configured = True

    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Retrieve knowledge for a customer message.

        Flow:
        1. Hybrid vector + BM25 search (primary).
        2. MCP tool augmentation (secondary, if configured).
        3. Merge KB + MCP results if both available.
        4. Keyword fallback (if both primary and MCP are unavailable).

        Args:
            payload: {"message": str, "intent": str, "tenant_id": str,
                      "preferences": dict, "mcp_configs": list[dict],
                      "tenant_shop_domain": str | None}
            headers: A2A headers.

        Returns:
            {"context": str, "sources": list, "model": str,
             "tokens_input": int, "tokens_output": int,
             "mcp_trace": dict (optional)}
        """
        message = payload.get("message", "")
        intent = payload.get("intent", "general_inquiry")
        tenant_id = (
            headers.get("x-tenant-id")
            or payload.get("tenant_id", "")
        )
        prefs = payload.get("preferences", {})
        mcp_configs = payload.get("mcp_configs", [])
        tenant_shop_domain = payload.get("tenant_shop_domain")

        if not tenant_id:
            return self._empty_result()

        # Step 1: Try hybrid vector search (primary)
        kb_result = await self._try_hybrid_search(
            tenant_id, message, intent, prefs,
        )

        # Step 2: Try MCP augmentation (secondary)
        mcp_result = None
        if mcp_configs:
            mcp_result = await self._try_mcp_augmentation(
                message=message,
                mcp_configs=mcp_configs,
                tenant_shop_domain=tenant_shop_domain,
            )

        # Step 3: Merge results if any are available
        if kb_result is not None or mcp_result is not None:
            return self._merge_results(kb_result, mcp_result)

        # Step 4: Keyword fallback (last resort)
        return await self._keyword_fallback(tenant_id, message)

    async def _try_hybrid_search(
        self,
        tenant_id: str,
        message: str,
        intent: str,
        prefs: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Attempt hybrid vector + BM25 search via KnowledgeVectorizer.

        Returns None if vectorizer is unavailable or fails.
        """
        try:
            from src.multi_tenant.knowledge_vectorizer import (
                KnowledgeVectorizer,
                get_knowledge_vectorizer,
            )

            vectorizer = self._knowledge_vectorizer or get_knowledge_vectorizer()
            if not getattr(vectorizer, "_configured", False):
                raise RuntimeError("KnowledgeVectorizer not configured")

            # Read retrieval params from preferences
            top_k = max(1, min(prefs.get("retrieval_top_k", 5), 20))
            vector_weight = max(0.0, min(prefs.get("retrieval_vector_weight", 0.7), 1.0))
            bm25_weight = max(0.0, min(prefs.get("retrieval_bm25_weight", 0.3), 1.0))
            entry_type = None

            # Intent-to-source routing
            intent_mapping = prefs.get("intent_source_mapping", {})
            if intent_mapping and intent in intent_mapping:
                entry_type = intent_mapping[intent]

            results = await vectorizer.search(
                tenant_id=tenant_id,
                query=message,
                top_k=top_k,
                entry_type=entry_type,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight,
            )

            # Apply minimum relevance score filter
            min_score = max(0.0, min(prefs.get("retrieval_min_score", 0.1), 1.0))
            results = [
                r for r in results
                if r.get("rrf_score", r.get("similarity", r.get("score", 0))) >= min_score
            ]

            formatted = KnowledgeVectorizer.format_for_pipeline(results)

            ctx = formatted.get("context", "")
            src = formatted.get("sources", [])
            logger.info(
                "KR hybrid: %d sources, context_len=%d",
                len(src), len(ctx),
            )

            formatted.setdefault("tokens_input", 0)
            formatted.setdefault("tokens_output", 0)
            formatted.setdefault("model", AZURE_EMBEDDING_MODEL)
            return formatted

        except Exception as exc:
            logger.warning(
                "Hybrid KB retrieval unavailable (%s) — falling back to keyword search",
                exc,
            )
            return None

    async def _try_mcp_augmentation(
        self,
        message: str,
        mcp_configs: list[dict[str, Any]],
        tenant_shop_domain: str | None = None,
    ) -> dict[str, Any] | None:
        """Attempt MCP tool invocation as secondary knowledge source.

        Connects to configured MCP servers (currently Shopify Storefront only),
        invokes read-only tools, and formats results as KR-compatible output.

        Returns ``None`` on any error (graceful degradation).

        Timeout: 3,000ms total for all MCP operations.
        """
        import asyncio

        _MCP_BUDGET_S = 3.0  # 3,000ms carved from KR's 10,000ms budget

        try:
            from src.multi_tenant.mcp_client import (
                create_tenant_mcp_client,
                parse_mcp_server_configs,
            )

            configs = parse_mcp_server_configs(mcp_configs)
            if not configs:
                return None

            start = time.monotonic()
            all_results: list[dict[str, Any]] = []
            tool_traces: list[dict[str, Any]] = []
            servers_queried: list[str] = []

            for config in configs:
                # Respect overall MCP budget
                elapsed = time.monotonic() - start
                if elapsed >= _MCP_BUDGET_S:
                    logger.debug("MCP budget exhausted after %.0fms", elapsed * 1000)
                    break

                try:
                    client = await create_tenant_mcp_client(
                        config=config,
                        tenant_shop_domain=tenant_shop_domain,
                    )
                    servers_queried.append(config.server_name)

                    remaining_s = _MCP_BUDGET_S - (time.monotonic() - start)
                    if remaining_s <= 0:
                        break

                    # Pass auth_headers if set by create_tenant_mcp_client
                    connect_kwargs: dict[str, Any] = {}
                    if hasattr(client, "_auth_headers") and client._auth_headers:
                        connect_kwargs["auth_headers"] = client._auth_headers
                    await asyncio.wait_for(
                        client.connect(**connect_kwargs), timeout=remaining_s,
                    )

                    # Find a search/query tool from available tools
                    tool_name = self._find_search_tool(client.available_tools)
                    if tool_name:
                        remaining_s = _MCP_BUDGET_S - (time.monotonic() - start)
                        if remaining_s > 0:
                            t0 = time.monotonic()
                            try:
                                result = await asyncio.wait_for(
                                    client.call_tool(tool_name, {"query": message}),
                                    timeout=remaining_s,
                                )
                                tool_elapsed = (time.monotonic() - t0) * 1000
                                tool_traces.append({
                                    "tool": tool_name,
                                    "elapsed_ms": round(tool_elapsed, 1),
                                    "success": True,
                                    "server": config.server_name,
                                })
                                # Extract text content
                                for item in result.content:
                                    if item.get("type") == "text" and item.get("text"):
                                        all_results.append({
                                            "text": item["text"],
                                            "server_name": config.server_name,
                                            "tool_name": tool_name,
                                        })
                            except Exception as tool_exc:
                                tool_elapsed = (time.monotonic() - t0) * 1000
                                tool_traces.append({
                                    "tool": tool_name,
                                    "elapsed_ms": round(tool_elapsed, 1),
                                    "success": False,
                                    "error": str(tool_exc)[:100],
                                    "server": config.server_name,
                                })
                    else:
                        logger.debug(
                            "No search tool found on %s", config.server_name,
                        )

                    await client.close()

                except Exception as exc:
                    logger.debug(
                        "MCP augmentation failed for %s: %s",
                        config.server_name, exc,
                    )

            total_elapsed = (time.monotonic() - start) * 1000

            if not all_results:
                # No MCP results — still return trace for debugging
                if tool_traces:
                    return {
                        "context": "",
                        "sources": [],
                        "model": "mcp",
                        "tokens_input": 0,
                        "tokens_output": 0,
                        "mcp_trace": {
                            "servers_queried": servers_queried,
                            "tools_invoked": tool_traces,
                            "total_elapsed_ms": round(total_elapsed, 1),
                        },
                    }
                return None

            # Format MCP results
            context_parts: list[str] = []
            sources: list[dict[str, str]] = []
            for i, r in enumerate(all_results):
                context_parts.append(r["text"])
                sources.append({
                    "id": f"mcp-{i}",
                    "title": f"Storefront: {r['tool_name']}",
                    "source_type": "mcp",
                    "server_name": r["server_name"],
                    "tool_name": r["tool_name"],
                })

            context = "\n\n".join(context_parts)
            logger.info(
                "KR MCP augmentation: %d results from %d servers in %.0fms",
                len(all_results), len(servers_queried), total_elapsed,
            )

            return {
                "context": context,
                "sources": sources,
                "model": "mcp",
                "tokens_input": 0,
                "tokens_output": 0,
                "mcp_trace": {
                    "servers_queried": servers_queried,
                    "tools_invoked": tool_traces,
                    "total_elapsed_ms": round(total_elapsed, 1),
                },
            }

        except Exception as exc:
            logger.warning("MCP augmentation unavailable (%s)", exc)
            return None

    @staticmethod
    def _find_search_tool(available_tools: list[dict[str, Any]]) -> str | None:
        """Find the best search/query tool from the server's available tools.

        Prefers tools with ``search`` in the name, then ``get``, then ``query``.
        Returns the tool name or ``None``.
        """
        priority_prefixes = ["search_", "find_", "query_", "get_", "list_"]
        for prefix in priority_prefixes:
            for tool in available_tools:
                if tool.get("name", "").lower().startswith(prefix):
                    return tool["name"]
        # Fallback: return the first tool if any exist
        return available_tools[0]["name"] if available_tools else None

    @staticmethod
    def _merge_results(
        kb_result: dict[str, Any] | None,
        mcp_result: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Merge KB search results with MCP tool results.

        KB results come first (primary source). MCP results are appended
        with a ``### Storefront Data`` header.  Sources are combined.

        Args:
            kb_result: Output from ``_try_hybrid_search()`` (may be None).
            mcp_result: Output from ``_try_mcp_augmentation()`` (may be None).

        Returns:
            Combined result in standard KR output format.
        """
        # Start with whichever result is available
        if kb_result and not mcp_result:
            return kb_result
        if mcp_result and not kb_result:
            return mcp_result

        # Both are available — merge
        kb_ctx = (kb_result or {}).get("context", "")
        mcp_ctx = (mcp_result or {}).get("context", "")

        parts: list[str] = []
        if kb_ctx:
            parts.append(kb_ctx)
        if mcp_ctx:
            parts.append(f"### Storefront Data\n{mcp_ctx}")

        context = "\n\n".join(parts)

        # Merge sources: tag KB sources
        kb_sources = list((kb_result or {}).get("sources", []))
        for src in kb_sources:
            src.setdefault("source_type", "kb")
        mcp_sources = list((mcp_result or {}).get("sources", []))

        merged: dict[str, Any] = {
            "context": context,
            "sources": kb_sources + mcp_sources,
            "model": (kb_result or {}).get("model", AZURE_EMBEDDING_MODEL),
            "tokens_input": (kb_result or {}).get("tokens_input", 0),
            "tokens_output": (kb_result or {}).get("tokens_output", 0),
        }

        # Include MCP trace if present
        mcp_trace = (mcp_result or {}).get("mcp_trace")
        if mcp_trace:
            merged["mcp_trace"] = mcp_trace

        return merged

    async def _keyword_fallback(
        self,
        tenant_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Keyword overlap search using KnowledgeBaseRepository."""
        try:
            kb_repo = self._kb_repo
            if not kb_repo:
                logger.warning("No KnowledgeBaseRepository for fallback")
                return self._empty_result()

            articles = await kb_repo.list_active(tenant_id)
            if not articles:
                logger.info("No active KB articles for tenant %s", tenant_id)
                return self._empty_result()

            query_words = {
                w for w in message.lower().split()
                if w not in _STOP and len(w) > 1
            }
            if not query_words:
                query_words = set(message.lower().split())

            scored: list[tuple[float, dict[str, Any]]] = []
            for article in articles:
                title = (article.get("title") or "").lower()
                content = (article.get("content") or "").lower()
                title_words = {w for w in title.split() if w not in _STOP}
                content_words = set(content.split())

                title_overlap = len(query_words & title_words)
                content_overlap = len(query_words & content_words)
                score = (title_overlap * 3.0 + content_overlap) / max(len(query_words), 1)

                if score > 0:
                    scored.append((score, article))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_results = scored[:5]

            if not top_results:
                top_results = [(0.5, a) for a in articles[:5]]

            context_parts: list[str] = []
            sources: list[dict[str, str]] = []
            for _score, article in top_results:
                title = article.get("title", "Untitled")
                content = article.get("content", "")
                source_url = article.get("source_url", "")
                url_line = f"\nSource: {source_url}" if source_url else ""
                context_parts.append(f"### {title}{url_line}\n{content}")
                sources.append({
                    "id": article.get("id", ""),
                    "title": title,
                    "entry_type": article.get("entry_type", ""),
                    "source_url": source_url,
                })

            context = "\n\n".join(context_parts)
            logger.info(
                "KR keyword fallback: %d results for tenant %s",
                len(top_results), tenant_id,
            )
            return {
                "context": context,
                "sources": sources,
                "model": "keyword-fallback",
                "tokens_input": 0,
                "tokens_output": 0,
            }

        except Exception as exc:
            logger.warning("KB keyword fallback failed (%s)", exc)
            return self._empty_result()

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        """Return an empty knowledge result."""
        return {
            "context": "",
            "sources": [],
            "model": AZURE_EMBEDDING_MODEL,
            "tokens_input": 0,
            "tokens_output": 0,
        }
