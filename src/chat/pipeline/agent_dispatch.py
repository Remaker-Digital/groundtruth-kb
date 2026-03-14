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
import os
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Any

import httpx
from opentelemetry import trace

from src.chat.pipeline.constants import (
    AGENT_CLASSIFY_PATH,
    AGENT_GENERATE_STREAM_PATH,
    AGENT_RETRIEVE_PATH,
    USE_AGENT_CONTAINERS,
)

if TYPE_CHECKING:
    from src.multi_tenant.pipeline_resilience import PipelineTimeoutBudget

logger = logging.getLogger(__name__)

# SPEC-1780 / PB-AGNTCY-001: In deployed environments, agent dispatch
# MUST NOT silently fall back to Tier 3 (in-process). If transport and
# HTTP containers are both unavailable, fail with 503.
_ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()
_IS_DEPLOYED = _ENVIRONMENT in ("staging", "production")


class AgentDispatchMixin:
    """Mixin providing agent dispatch methods for ChatPipeline.

    Methods on this mixin access instance attributes set by ChatPipeline.__init__:
    _ic_agent, _kr_agent, _rg_agent, _agent_urls, _get_http_client(),
    _current_tenant_id, _current_preferences, _current_tenant.

    Dispatch priority (SPEC-1525):
        1. SLIM/NATS transport (when AGNTCY SDK transport is active)
        2. HTTP containers (when USE_AGENT_CONTAINERS is set)
        3. In-process direct call (default)
    """

    def _transport_available(self) -> bool:
        """Check if AGNTCY transport is available for A2A routing."""
        try:
            from src.multi_tenant.agntcy_sdk_integration import _transport
            return _transport is not None
        except Exception:
            return False

    def _require_transport_or_fail(self, agent_name: str) -> None:
        """SPEC-1780: In deployed environments, raise 503 if no transport is available.

        Called when both transport and HTTP container dispatch have failed.
        In local/development environments, allows silent Tier 3 fallback.
        In staging/production, raises HTTPException(503) to prevent silent
        degradation — the operator must fix transport infrastructure.
        """
        if _IS_DEPLOYED:
            from fastapi import HTTPException

            logger.error(
                "AGNTCY transport unavailable in %s environment for agent=%s. "
                "PB-AGNTCY-001 enforcement: refusing Tier 3 fallback.",
                _ENVIRONMENT, agent_name,
            )
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Agent dispatch unavailable: {agent_name}. "
                    f"AGNTCY transport is not active in {_ENVIRONMENT} environment. "
                    "Contact platform administrator."
                ),
            )

    async def _call_via_transport(
        self,
        agent_topic: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Route an agent call through SLIM/NATS transport (SPEC-1525).

        Includes tenant_id, conversation_id, and trace_id in message
        headers for distributed tracing.
        """
        from src.multi_tenant.agntcy_sdk_integration import create_a2a_client

        tenant_id = getattr(self, "_current_tenant_id", "")
        conversation_id = getattr(self, "_current_conversation_id", "")
        trace_id = getattr(self, "_current_trace_id", "")

        client = create_a2a_client(agent_topic)
        response = await client.send(
            payload,
            headers={
                "X-Tenant-Id": tenant_id,
                "X-Conversation-Id": conversation_id,
                "X-Trace-Id": trace_id,
            },
        )
        logger.debug(
            "A2A transport call: topic=%s tenant=%s trace=%s",
            agent_topic, tenant_id, trace_id,
        )
        return response if isinstance(response, dict) else {"result": response}

    # -------------------------------------------------------------------
    # Intent Classification
    # -------------------------------------------------------------------

    async def _call_intent_classifier(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Classify customer intent.

        Routes via SLIM/NATS transport (preferred), AGNTCY HTTP containers,
        or in-process based on configuration (SPEC-1525).
        Wrapped in trace_agent_operation() span (SPEC-1539).
        """
        from src.multi_tenant.otel_tracing import record_token_usage, trace_agent_operation

        span = trace_agent_operation("intent-classifier", "classify")
        try:
            if self._transport_available():
                try:
                    result = await self._call_via_transport(
                        "intent-classifier",
                        {"message": message, "system_prompt": system_prompt},
                    )
                    span.set_attribute("dispatch.mode", "transport")
                    return result
                except Exception as exc:
                    logger.warning("Transport IC call failed, falling back: %s", exc)
            if USE_AGENT_CONTAINERS:
                try:
                    span.set_attribute("dispatch.mode", "http")
                    return await self._call_intent_classifier_http(message, system_prompt)
                except Exception as exc:
                    logger.warning("HTTP IC call failed, falling back to in-process: %s", exc)
            # SPEC-1780: Enforce transport requirement in deployed environments
            self._require_transport_or_fail("intent-classifier")
            span.set_attribute("dispatch.mode", "in-process")
            result = await self._call_intent_classifier_direct(message, system_prompt)
            # Record token usage if available (SPEC-1540)
            if "usage" in result:
                usage = result["usage"]
                record_token_usage(
                    span,
                    usage.get("model", "gpt-4o-mini"),
                    usage.get("prompt_tokens", 0),
                    usage.get("completion_tokens", 0),
                )
            return result
        except Exception:
            span.set_status(trace.StatusCode.ERROR)  # type: ignore[attr-defined]
            raise
        finally:
            span.end()

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

        Routes via SLIM/NATS transport (preferred), AGNTCY containers,
        or in-process based on configuration (SPEC-1525).
        Wrapped in trace_agent_operation span (SPEC-1539).
        """
        from src.multi_tenant.otel_tracing import trace_agent_operation

        span = trace_agent_operation("knowledge-retrieval", "retrieve")
        try:
            if self._transport_available():
                try:
                    result = await self._call_via_transport(
                        "knowledge-retrieval",
                        {"message": message, "intent": intent, "system_prompt": system_prompt},
                    )
                    span.set_attribute("dispatch.mode", "transport")
                    return result
                except Exception as exc:
                    logger.warning("Transport KR call failed, falling back: %s", exc)
            if USE_AGENT_CONTAINERS:
                try:
                    span.set_attribute("dispatch.mode", "http")
                    return await self._call_knowledge_retrieval_http(message, intent, system_prompt)
                except Exception as exc:
                    logger.warning("HTTP KR call failed, falling back to in-process: %s", exc)
            # SPEC-1780: Enforce transport requirement in deployed environments
            self._require_transport_or_fail("knowledge-retrieval")
            span.set_attribute("dispatch.mode", "in-process")
            return await self._call_knowledge_retrieval_direct(message, intent, system_prompt)
        except Exception:
            span.set_status(trace.StatusCode.ERROR)
            raise
        finally:
            span.end()

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

        Routes via transport → HTTP → in-process (SPEC-1536, SPEC-1537).
        Transport streaming uses hybrid SSE-over-transport for the RG
        container when SLIM/NATS is active.

        WI #93-96: The ``model`` parameter allows Layer 4 fine-tuned
        models to override the default gpt-4o for Enterprise tenants
        with the fine-tuning add-on enabled.
        """
        # Priority 1: SLIM/NATS transport (SPEC-1537)
        if self._transport_available():
            try:
                async for chunk in self._call_response_generator_stream_transport(
                    customer_message, intent, knowledge_context,
                    system_prompt, budget, model,
                    conversation_history=conversation_history,
                ):
                    yield chunk
                return
            except Exception as exc:
                logger.warning("Transport RG stream failed, falling back: %s", exc)

        # Priority 2: HTTP container
        if USE_AGENT_CONTAINERS:
            try:
                async for chunk in self._call_response_generator_stream_http(
                    customer_message, intent, knowledge_context,
                    system_prompt, budget, model,
                ):
                    yield chunk
                return
            except Exception as exc:
                logger.warning("HTTP RG stream failed, falling back to in-process: %s", exc)

        # SPEC-1780: Enforce transport requirement in deployed environments
        self._require_transport_or_fail("response-generator")

        # Priority 3: In-process agent (fallback — local/development only)
        async for chunk in self._call_response_generator_stream_direct(
            customer_message, intent, knowledge_context,
            system_prompt, budget, model,
            conversation_history=conversation_history,
        ):
            yield chunk

    async def _call_response_generator_stream_transport(
        self,
        customer_message: str,
        intent: str,
        knowledge_context: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        model: str = "gpt-4o",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response via SLIM/NATS transport (SPEC-1537).

        Sends the generation request to the RG container over A2A transport
        and receives streaming chunks back. The transport layer handles
        chunked delivery; this method yields each chunk as it arrives.
        """
        from src.multi_tenant.agntcy_sdk_integration import create_a2a_client

        tenant_id = getattr(self, "_current_tenant_id", "")
        conversation_id = getattr(self, "_current_conversation_id", "")
        trace_id = getattr(self, "_current_trace_id", "")

        remaining_ms = budget.remaining_ms
        timeout_seconds = max(0.5, remaining_ms / 1000)

        client = create_a2a_client("response-generator")
        response = await client.send(
            {
                "message": customer_message,
                "intent": intent,
                "knowledge_context": knowledge_context,
                "system_prompt": system_prompt,
                "model": model,
                "conversation_history": conversation_history or [],
                "stream": True,
                "timeout_seconds": timeout_seconds,
            },
            headers={
                "X-Tenant-Id": tenant_id,
                "X-Conversation-Id": conversation_id,
                "X-Trace-Id": trace_id,
            },
        )

        # Transport may return streamed chunks as list or single response
        if isinstance(response, dict):
            chunks = response.get("chunks", [response.get("text", "")])
            for chunk in chunks:
                if chunk:
                    yield chunk
        elif isinstance(response, str):
            yield response
        else:
            logger.warning("Unexpected transport RG response type: %s", type(response))

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

    # ------------------------------------------------------------------
    # Co-pilot agent dispatch (SPEC-1557)
    # ------------------------------------------------------------------

    async def _call_co_pilot(
        self,
        message: str,
        system_prompt: str,
        conversation_history: list[dict[str, Any]] | None = None,
        team_member_role: str = "admin",
    ) -> dict[str, Any]:
        """Dispatch to the Co-pilot agent (3-tier routing).

        Args:
            message: Team member's question.
            system_prompt: Co-pilot system prompt (from SystemPromptBuilder).
            conversation_history: Prior turns in this admin conversation.
            team_member_role: Team member's role (admin, viewer, etc.).

        Returns:
            {response, sources, model, tokens_input, tokens_output}
        """
        from src.multi_tenant.otel_tracing import trace_agent_operation

        payload = {
            "message": message,
            "system_prompt": system_prompt,
            "conversation_history": conversation_history or [],
            "team_member_role": team_member_role,
            "tenant_id": getattr(self, "_current_tenant_id", ""),
        }

        span = trace_agent_operation(
            "co-pilot", "assist",
            conversation_id=getattr(self, "_current_conversation_id", None),
        )
        try:
            # Tier 1: SLIM/NATS transport
            if self._transport_available():
                try:
                    result = await self._call_via_transport("co-pilot", payload)
                    span.set_attribute("dispatch.mode", "transport")
                    return result
                except Exception as exc:
                    logger.warning("Transport co-pilot call failed: %s", exc)

            # Tier 2: HTTP container
            if USE_AGENT_CONTAINERS:
                try:
                    url = getattr(self, "_agent_urls", {}).get("co-pilot", "")
                    if url:
                        client = await self._get_http_client()
                        resp = await client.post(
                            f"{url.rstrip('/')}/process",
                            json=payload,
                            timeout=httpx.Timeout(connect=1.0, read=15.0, write=1.0, pool=1.0),
                        )
                        resp.raise_for_status()
                        span.set_attribute("dispatch.mode", "http")
                        return resp.json()
                except Exception as exc:
                    logger.warning("HTTP co-pilot call failed: %s", exc)

            # SPEC-1780: Enforce transport requirement in deployed environments
            self._require_transport_or_fail("co-pilot")

            # Tier 3: In-process direct (local/development only)
            span.set_attribute("dispatch.mode", "in-process")
            co_pilot = getattr(self, "_copilot_agent", None)
            if co_pilot:
                result = await co_pilot.process(payload, {
                    "x-tenant-id": getattr(self, "_current_tenant_id", ""),
                    "x-conversation-id": getattr(self, "_current_conversation_id", ""),
                })
                return result

            return {
                "response": "Co-pilot agent is not configured.",
                "sources": [],
                "model": "",
                "tokens_input": 0,
                "tokens_output": 0,
            }
        except Exception:
            span.set_status(trace.StatusCode.ERROR)
            raise
        finally:
            span.end()
