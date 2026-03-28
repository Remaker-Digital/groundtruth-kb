"""Agent dispatch mixin — IC, KR, and RG agent call methods.

Provides intent classification, knowledge retrieval, and response
generation dispatch methods for ChatPipeline. Routes through the
canonical transport stack: SLIM/gRPC → NATS → HTTP(S) → 503.

SPEC-1802: All environments use the same dispatch algorithm.
In-process dispatch is NOT part of the canonical pipeline.

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

# SPEC-1802 canonical dispatch — same in ALL environments:
#   Tier 1: SLIM/gRPC transport (primary — when physically possible)
#   Tier 2: NATS JetStream transport (fallback — when physically possible)
#   Tier 3: HTTP(S) containers (last resort — when higher tiers unavailable)
#   Fail:   503 with tier-diagnostic reason
#
# In-process dispatch is NOT part of the canonical pipeline (DCL-002).
# There is no in-process fallback — all agents run in dedicated containers.
_ENVIRONMENT = os.environ.get("ENVIRONMENT", "development").lower()


class AgentDispatchMixin:
    """Mixin providing agent dispatch methods for ChatPipeline.

    Methods on this mixin access instance attributes set by ChatPipeline.__init__:
    _ic_agent, _kr_agent, _rg_agent, _agent_urls, _get_http_client(),
    _current_tenant_id, _current_preferences, _current_tenant.

    Canonical dispatch priority (SPEC-1802) — same in ALL environments:
        Tier 1: SLIM/gRPC transport (primary — when physically possible)
        Tier 2: NATS JetStream transport (fallback — when physically possible)
        Tier 3: HTTP(S) containers (last resort — when higher tiers unavailable)
        Fail:   503 with tier-diagnostic reason

    Tiers 1 and 2 are unified behind _transport_available() — the SDK
    singleton selects SLIM or NATS based on endpoint configuration. Tier 3 HTTP
    is explicitly a last resort per SPEC-1802 and emits warnings when used.

    In-process dispatch is NOT part of the canonical pipeline (DCL-002).
    All agents run in dedicated containers — there is no in-process fallback.
    """

    def _transport_available(self) -> bool:
        """Check if AGNTCY transport is available for A2A routing."""
        try:
            from src.multi_tenant.agntcy_sdk_integration import _transport
            return _transport is not None
        except Exception:
            return False

    def _warn_http_failure_mode(self, agent_name: str) -> None:
        """SPEC-1802: Log warning when dispatching via HTTP (failure mode).

        HTTP containers are Tier 3 (failure mode), not normal operation.
        This method is called when transport (SLIM/NATS) is unavailable
        and dispatch falls through to HTTP containers.
        """
        logger.warning(
            "SPEC-1802: Dispatching %s via HTTP containers (Tier 3 failure mode). "
            "Transport (SLIM/NATS) is unavailable. This is not normal operation.",
            agent_name,
        )

    def _require_transport_or_fail(self, agent_name: str) -> None:
        """SPEC-1780/SPEC-1802: Raise 503 if all transport tiers exhausted.

        SLIM/gRPC is mandatory. In-process dispatch is not an option.
        All environments require functioning transport (SLIM → NATS → HTTP).
        """
        from fastapi import HTTPException

        logger.error(
            "All dispatch tiers exhausted for agent=%s in %s. "
            "SPEC-1802: SLIM(T1) + NATS(T2) + HTTP(T3) all failed. "
            "In-process dispatch is not available.",
            agent_name, _ENVIRONMENT,
        )
        raise HTTPException(
            status_code=503,
            detail=(
                f"Agent dispatch unavailable: {agent_name}. "
                f"All transport tiers exhausted in {_ENVIRONMENT} environment. "
                "Contact platform administrator."
            ),
        )

    async def _call_via_transport(
        self,
        agent_topic: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Route an agent call through SLIM/NATS transport (SPEC-1525).

        Uses AGNTCY SDK v0.5.4 A2AClientFactory with A2A protocol.
        SPEC-1802: SLIM/gRPC is always the primary transport.
        Resolves agent topic via AGNTCY Directory (SPEC-1789) with
        static fallback.
        """
        import uuid

        from a2a.types import (
            Message as A2AMessage,
            MessageSendParams,
            Role,
            SendMessageRequest,
            TextPart,
        )

        from src.multi_tenant.agntcy_directory import get_agent_topic
        from src.multi_tenant.agntcy_sdk_integration import create_a2a_client

        # SPEC-1789: Resolve agent topic via Directory (falls back to static)
        resolved_topic = get_agent_topic(agent_topic)

        tenant_id = getattr(self, "_current_tenant_id", "")
        conversation_id = getattr(self, "_current_conversation_id", "")
        trace_id = getattr(self, "_current_trace_id", "")

        # Create A2A client (cached per topic)
        client = await create_a2a_client(resolved_topic)

        # Build A2A SendMessageRequest with payload as JSON text part
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            jsonrpc="2.0",
            method="message/send",
            params=MessageSendParams(
                message=A2AMessage(
                    role=Role.user,
                    message_id=str(uuid.uuid4()),
                    parts=[TextPart(kind="text", text=json.dumps(payload))],
                    metadata={
                        "tenant_id": tenant_id,
                        "conversation_id": conversation_id,
                        "trace_id": trace_id,
                    },
                ),
            ),
        )

        response = await client.send_message(request)
        logger.debug(
            "A2A transport call: topic=%s (resolved=%s) tenant=%s trace=%s",
            agent_topic, resolved_topic, tenant_id, trace_id,
        )

        # Extract result from A2A response
        result = response.root
        if hasattr(result, "error"):
            raise RuntimeError(
                f"A2A call to {agent_topic} failed: {result.error}"
            )

        # Extract text parts from the response message/task
        success_result = result.result
        if hasattr(success_result, "status"):
            # It's a Task — get the status message
            msg = success_result.status.message
        else:
            # It's a direct Message
            msg = success_result

        if msg and msg.parts:
            for part in msg.parts:
                if hasattr(part, "text"):
                    try:
                        return json.loads(part.text)
                    except (json.JSONDecodeError, TypeError):
                        return {"result": part.text}

        return {"result": str(success_result)}

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
        per SPEC-1802 canonical dispatch (SLIM → NATS → HTTP → 503).
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
                    self._warn_http_failure_mode("intent-classifier")
                    span.set_attribute("dispatch.mode", "http")
                    return await self._call_intent_classifier_http(message, system_prompt)
                except Exception as exc:
                    logger.warning("HTTP IC call failed: %s", exc)
            # SPEC-1802 / DCL-002: All tiers exhausted — 503. No in-process fallback.
            self._require_transport_or_fail("intent-classifier")
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
        per SPEC-1802 canonical dispatch (SLIM → NATS → HTTP → 503).
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
                    self._warn_http_failure_mode("knowledge-retrieval")
                    span.set_attribute("dispatch.mode", "http")
                    return await self._call_knowledge_retrieval_http(message, intent, system_prompt)
                except Exception as exc:
                    logger.warning("HTTP KR call failed: %s", exc)
            # SPEC-1802 / DCL-002: All tiers exhausted — 503. No in-process fallback.
            self._require_transport_or_fail("knowledge-retrieval")
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

        Per-interface transport policy (DCL-002 v4, owner-approved 2026-03-28):
        RG token streaming uses the gateway's in-process ResponseGeneratorAgent
        as the intended production path. This is not a fallback — it is the
        correct interface-level choice for token streaming.

        Rationale (INSIGHTS-2026-03-28-01-10, INSIGHTS-2026-03-28-01-20):
        - SLIM: does not support point-to-point streaming (NotImplementedError)
        - NATS: connection drops during long streaming (Container Apps idle timeout)
        - HTTP to RG container: Container Apps outbound networking drops Azure
          OpenAI streaming connections mid-response (~17 tokens)
        - Gateway in-process: proven reliable (gateway's Azure OpenAI client
          streams successfully from the same Container Apps environment)

        Non-streaming agents (IC, KR, CR, EH) continue containerized dispatch
        via SLIM/NATS/HTTP cascade per SPEC-1802.

        WI #93-96: The ``model`` parameter allows Layer 4 fine-tuned
        models to override the default gpt-4o for Enterprise tenants
        with the fine-tuning add-on enabled.
        """
        # RG token streaming: gateway in-process (intended production path).
        # DCL-002 v4: in-process RG streaming is the per-interface transport
        # decision, not a fallback. Owner-approved 2026-03-28.
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
        from src.multi_tenant.agntcy_directory import get_agent_topic
        from src.multi_tenant.agntcy_sdk_integration import create_a2a_client

        tenant_id = getattr(self, "_current_tenant_id", "")
        conversation_id = getattr(self, "_current_conversation_id", "")
        trace_id = getattr(self, "_current_trace_id", "")

        remaining_ms = budget.remaining_ms
        timeout_seconds = max(0.5, remaining_ms / 1000)

        # SPEC-1789: Resolve via Directory with static fallback
        rg_topic = get_agent_topic("response-generator")
        client = create_a2a_client(rg_topic)
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
                "timeout_seconds": read_timeout,
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

            # Tier 3: HTTP container (failure mode per SPEC-1802)
            if USE_AGENT_CONTAINERS:
                try:
                    self._warn_http_failure_mode("co-pilot")
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

            # SPEC-1802 / DCL-002: All tiers exhausted — 503. No in-process fallback.
            self._require_transport_or_fail("co-pilot")
        except Exception:
            span.set_status(trace.StatusCode.ERROR)
            raise
        finally:
            span.end()
