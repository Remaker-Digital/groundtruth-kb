"""Agent dispatch mixin — IC, KR, and RG agent call methods.

Provides intent classification, knowledge retrieval, and response
generation dispatch methods for ChatPipeline. Routes to in-process
A2A agents (default) or AGNTCY HTTP containers.

R10 refactoring — extracted from pipeline.py (session 39).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

import httpx

from src.chat.pipeline.constants import (
    AGENT_CLASSIFY_PATH,
    AGENT_GENERATE_STREAM_PATH,
    AGENT_RETRIEVE_PATH,
    USE_AGENT_CONTAINERS,
)

if TYPE_CHECKING:
    from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget

logger = logging.getLogger(__name__)


class AgentDispatchMixin:
    """Mixin providing agent dispatch methods for ChatPipeline.

    Methods on this mixin access instance attributes set by ChatPipeline.__init__:
    _ic_agent, _kr_agent, _rg_agent, _agent_urls, _get_http_client(),
    _current_tenant_id, _current_preferences, _current_tenant.
    """

    # -------------------------------------------------------------------
    # Intent Classification
    # -------------------------------------------------------------------

    async def _call_intent_classifier(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Classify customer intent.

        Routes to Azure OpenAI directly (default) or AGNTCY container
        based on USE_AGENT_CONTAINERS flag.
        """
        if USE_AGENT_CONTAINERS:
            return await self._call_intent_classifier_http(message, system_prompt)
        return await self._call_intent_classifier_direct(message, system_prompt)

    async def _call_intent_classifier_direct(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Classify intent via in-process IntentClassifierAgent (A2A).

        Delegates to the extracted agent module which encapsulates the
        Azure OpenAI GPT-4o-mini call with JSON mode structured output.
        """
        return await self._ic_agent.process(
            {"message": message, "system_prompt": system_prompt},
            {},
        )

    async def _call_intent_classifier_http(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Intent Classification agent via HTTP (AGNTCY container)."""
        url = self._agent_urls.get("intent-classifier", "")
        client = await self._get_http_client()

        response = await client.post(
            f"{url.rstrip('/')}{AGENT_CLASSIFY_PATH}",
            json={
                "message": message,
                "system_prompt": system_prompt,
            },
        )
        response.raise_for_status()
        return response.json()

    # -------------------------------------------------------------------
    # Knowledge Retrieval
    # -------------------------------------------------------------------

    async def _call_knowledge_retrieval(
        self,
        message: str,
        intent: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Retrieve relevant knowledge for the customer message.

        Routes to Azure OpenAI embeddings + Cosmos DB (default) or
        AGNTCY container based on USE_AGENT_CONTAINERS flag.
        """
        if USE_AGENT_CONTAINERS:
            return await self._call_knowledge_retrieval_http(message, intent, system_prompt)
        return await self._call_knowledge_retrieval_direct(message, intent, system_prompt)

    async def _call_knowledge_retrieval_direct(
        self,
        message: str,
        intent: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Retrieve knowledge via in-process KnowledgeRetrievalAgent (A2A).

        Delegates to the extracted agent module which encapsulates both
        hybrid vector + BM25 search and keyword fallback paths.
        """
        tenant_id = getattr(self, "_current_tenant_id", None)
        prefs = getattr(self, "_current_preferences", None)
        tenant = getattr(self, "_current_tenant", None)

        # Build preferences dict for the agent
        prefs_dict: dict[str, Any] = {}
        if prefs:
            if prefs.retrieval_top_k is not None:
                prefs_dict["retrieval_top_k"] = prefs.retrieval_top_k
            if prefs.retrieval_vector_weight is not None:
                prefs_dict["retrieval_vector_weight"] = prefs.retrieval_vector_weight
            if prefs.retrieval_bm25_weight is not None:
                prefs_dict["retrieval_bm25_weight"] = prefs.retrieval_bm25_weight
            if prefs.retrieval_min_score is not None:
                prefs_dict["retrieval_min_score"] = prefs.retrieval_min_score
            if prefs.intent_source_mapping:
                prefs_dict["intent_source_mapping"] = prefs.intent_source_mapping

        # Resolve MCP server configurations (AGNTCY Phase 3)
        import dataclasses as _dc

        mcp_configs: list[dict[str, Any]] = []
        tenant_shop_domain: str | None = None
        if prefs and tenant:
            try:
                from src.multi_tenant.mcp_client import resolve_mcp_configs

                configs = resolve_mcp_configs(prefs, tenant)
                mcp_configs = [_dc.asdict(c) for c in configs]
                tenant_shop_domain = getattr(tenant, "shopify_shop_domain", None)
            except Exception:
                logger.debug("MCP config resolution failed", exc_info=True)

        return await self._kr_agent.process(
            {
                "message": message,
                "intent": intent,
                "tenant_id": tenant_id or "",
                "preferences": prefs_dict,
                "mcp_configs": mcp_configs,
                "tenant_shop_domain": tenant_shop_domain,
            },
            {"x-tenant-id": tenant_id or ""},
        )

    async def _call_knowledge_retrieval_http(
        self,
        message: str,
        intent: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Knowledge Retrieval agent via HTTP (AGNTCY container)."""
        url = self._agent_urls.get("knowledge-retrieval", "")
        client = await self._get_http_client()

        response = await client.post(
            f"{url.rstrip('/')}{AGENT_RETRIEVE_PATH}",
            json={
                "message": message,
                "intent": intent,
                "system_prompt": system_prompt,
            },
        )
        response.raise_for_status()
        return response.json()

    # -------------------------------------------------------------------
    # Response Generation (streaming)
    # -------------------------------------------------------------------

    async def _call_response_generator_stream(
        self,
        customer_message: str,
        intent: str,
        knowledge_context: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        model: str = "gpt-4o",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming AI response.

        Routes to Azure OpenAI directly (default) or AGNTCY container
        based on USE_AGENT_CONTAINERS flag.

        WI #93-96: The ``model`` parameter allows Layer 4 fine-tuned
        models to override the default gpt-4o for Enterprise tenants
        with the fine-tuning add-on enabled.
        """
        if USE_AGENT_CONTAINERS:
            async for chunk in self._call_response_generator_stream_http(
                customer_message, intent, knowledge_context,
                system_prompt, budget, model,
            ):
                yield chunk
        else:
            async for chunk in self._call_response_generator_stream_direct(
                customer_message, intent, knowledge_context,
                system_prompt, budget, model,
                conversation_history=conversation_history,
            ):
                yield chunk

    async def _call_response_generator_stream_direct(
        self,
        customer_message: str,
        intent: str,
        knowledge_context: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        model: str = "gpt-4o",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response via in-process ResponseGeneratorAgent (A2A).

        Delegates to the extracted agent module's generate_stream() method
        which encapsulates knowledge context injection, greeting handling,
        temperature selection, and multi-turn history.
        """
        remaining_ms = budget.remaining_ms
        timeout_seconds = max(0.5, remaining_ms / 1000)

        async for chunk in self._rg_agent.generate_stream(
            customer_message=customer_message,
            intent=intent,
            knowledge_context=knowledge_context,
            system_prompt=system_prompt,
            model=model,
            conversation_history=conversation_history,
            timeout_seconds=timeout_seconds,
        ):
            yield chunk

    async def _call_response_generator_stream_http(
        self,
        customer_message: str,
        intent: str,
        knowledge_context: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        model: str = "gpt-4o",
    ) -> AsyncGenerator[str, None]:
        """Call the Response Generator via HTTP (AGNTCY container) with SSE streaming."""
        url = self._agent_urls.get("response-generator", "")
        client = await self._get_http_client()

        remaining_ms = budget.remaining_ms
        read_timeout = max(0.5, remaining_ms / 1000)

        async with client.stream(
            "POST",
            f"{url.rstrip('/')}{AGENT_GENERATE_STREAM_PATH}",
            json={
                "message": customer_message,
                "intent": intent,
                "knowledge_context": knowledge_context,
                "system_prompt": system_prompt,
                "model": model,
                "enable_prefix_caching": True,
            },
            timeout=httpx.Timeout(
                connect=1.0,
                read=read_timeout,
                write=1.0,
                pool=1.0,
            ),
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        parsed = json.loads(data)
                        chunk = parsed.get("text", parsed.get("content", ""))
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        yield data
                elif not line.startswith("event:") and not line.startswith(":"):
                    yield line
