"""
6-agent pipeline orchestrator for the Chat API.

Executes the AI conversation pipeline for each customer message:
    1. Intent Classification (IC) — categorize customer intent
    2. Knowledge Retrieval (KR) — fetch relevant product/FAQ data
    3. Response Generation (RG) — compose AI response (streamed via SSE)
    4. Critic/Supervisor (CR) — validate response safety (fail-closed)
    5. Escalation Handler (ESC) — triggered when IC detects escalation intent
    6. Analytics Collector (AN) — async event for metrics (fire-and-forget)

The pipeline integrates:
    - PipelineTimeoutBudget: per-stage timeout enforcement (8s hard deadline)
    - SystemPromptBuilder: dynamic per-agent prompt assembly
    - CustomerProfileService: Layer 1 customer context injection
    - ConversationVectorizer: Layer 2 semantic history search
    - DecisionTraceBuilder: per-response explainability
    - CriticPolicy: fail-closed safety gate (stream-then-validate, Decision UI-5)

The pipeline produces an async generator of StreamEvent objects for SSE
delivery. The endpoints module consumes this generator to produce the
HTTP SSE response.

Architecture references:
    - UI-UX-ARCHITECTURE-DECISIONS.md §3: Chat API Specification
    - Decision UI-5: SSE stream-then-validate with Critic retraction
    - Decision #15: Layered timeout budget (8s pipeline deadline)
    - Decision #23: SystemPromptBuilder per-agent prompt composition
    - Decision #50: Fail-closed Critic policy

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from src.chat.models import (
    StreamEvent,
    done_event,
    error_event,
    retracted_event,
    stage_event,
    token_event,
    validated_event,
)
from src.chat.session import ConversationSession
from src.multi_tenant.conversation_meter import ConversationMeter
from src.multi_tenant.conversation_vectorizer import ConversationVectorizer
from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    ConversationStatus,
    CustomerProfileDocument,
    PreferencesDocument,
    TenantDocument,
    TenantTier,
)
from src.multi_tenant.critic_policy import SAFE_FALLBACK_MESSAGE, CriticPolicy
from src.multi_tenant.customer_profile_service import CustomerProfileService
from src.multi_tenant.pipeline_resilience import (
    PipelineTimeoutBudget,
    PipelineTimeoutError,
    ServiceUnavailableError,
    call_with_breaker,
)
from src.multi_tenant.response_explainability import DecisionTraceBuilder
from src.multi_tenant.system_prompt_builder import (
    AgentRole,
    SystemPromptBuilder,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants — agent HTTP endpoints (configurable via environment)
# ---------------------------------------------------------------------------

# Default agent URLs — overridden by environment variables in production.
# These match the Container App private IPs from CLAUDE.md.
AGENT_URLS: dict[str, str] = {
    "intent-classifier": os.environ.get(
        "AGENT_INTENT_CLASSIFIER_URL", "http://10.0.1.10:8080"
    ),
    "knowledge-retrieval": os.environ.get(
        "AGENT_KNOWLEDGE_RETRIEVAL_URL", "http://10.0.1.6:8080"
    ),
    "response-generator": os.environ.get(
        "AGENT_RESPONSE_GENERATOR_URL", "http://10.0.1.8:8080"
    ),
    "escalation-handler": os.environ.get(
        "AGENT_ESCALATION_HANDLER_URL", "http://10.0.1.11:8080"
    ),
    "analytics-collector": os.environ.get(
        "AGENT_ANALYTICS_COLLECTOR_URL", "http://10.0.1.9:8080"
    ),
}

# Agent HTTP paths
AGENT_CLASSIFY_PATH = "/classify"
AGENT_RETRIEVE_PATH = "/retrieve"
AGENT_GENERATE_PATH = "/generate"
AGENT_GENERATE_STREAM_PATH = "/generate/stream"
AGENT_ESCALATE_PATH = "/escalate"
AGENT_ANALYTICS_PATH = "/collect"

# Escalation intent value from the Intent Classifier
ESCALATION_INTENT = "escalation"


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------


class ChatPipeline:
    """Orchestrates the 6-agent pipeline for a single conversation turn.

    For each customer message, the pipeline:
        1. Builds per-agent system prompts (SystemPromptBuilder)
        2. Loads customer context (Layer 1 profile + Layer 2 history)
        3. Classifies intent (IC)
        4. Retrieves knowledge (KR)
        5. Generates response with SSE streaming (RG)
        6. Validates via Critic (CR) — stream-then-validate
        7. Fires analytics event (AN, async)
        8. Handles escalation if detected (ESC)

    The pipeline produces an async generator of StreamEvent objects.
    """

    def __init__(
        self,
        *,
        session: ConversationSession,
        prompt_builder: SystemPromptBuilder,
        profile_service: CustomerProfileService,
        vectorizer: ConversationVectorizer | None = None,
        critic: CriticPolicy | None = None,
        meter: ConversationMeter | None = None,
        agent_urls: dict[str, str] | None = None,
    ) -> None:
        self._session = session
        self._prompt_builder = prompt_builder
        self._profile_service = profile_service
        self._vectorizer = vectorizer
        self._critic = critic
        self._meter = meter
        self._agent_urls = agent_urls or AGENT_URLS
        self._http_client: httpx.AsyncClient | None = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the shared HTTP client with connection pooling."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(connect=1.0, read=5.0, write=1.0, pool=1.0),
                limits=httpx.Limits(
                    max_connections=100,
                    max_keepalive_connections=20,
                ),
            )
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client. Called during app shutdown."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # -------------------------------------------------------------------
    # Main pipeline entry point
    # -------------------------------------------------------------------

    async def execute(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        *,
        tenant: TenantDocument,
        preferences: PreferencesDocument,
        customer_id: str | None = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Execute the full pipeline for a customer message.

        Yields StreamEvent objects for SSE delivery. The caller wraps
        this generator in a StreamingResponse.

        Args:
            tenant_id: Tenant identifier.
            conversation_id: Active conversation.
            customer_message: The customer's message text.
            tenant: Tenant document (for prompt builder).
            preferences: Resolved merchant preferences.
            customer_id: Optional customer identifier for profile lookup.

        Yields:
            StreamEvent objects (stage, token, validated/retracted, done/error).
        """
        budget = PipelineTimeoutBudget()
        trace = DecisionTraceBuilder()
        tier = tenant.tier or TenantTier.STARTER

        try:
            # ---------------------------------------------------------------
            # Phase 0: Load customer context (Layer 1 + Layer 2)
            # ---------------------------------------------------------------
            profile = await self._load_customer_profile(
                tenant_id, customer_id, tier, customer_message, trace,
            )

            # Build system prompts for all agents
            prompts = self._prompt_builder.build_all(
                tenant=tenant,
                preferences=preferences,
                customer_profile=profile,
            )

            # Record prompt trace for explainability
            prompt_trace = self._prompt_builder.explain(
                AgentRole.RESPONSE_GENERATOR, tenant, preferences, profile,
            )
            trace.set_profile_context(prompt_trace)

            # ---------------------------------------------------------------
            # Phase 1: Intent Classification
            # ---------------------------------------------------------------
            yield stage_event("intent-classifier", "started")

            intent_result = await budget.execute_with_budget(
                "intent-classifier",
                self._call_intent_classifier(
                    customer_message, prompts[AgentRole.INTENT_CLASSIFIER],
                ),
            )

            intent = intent_result.get("intent", "general_inquiry")
            confidence = intent_result.get("confidence", 0.0)
            trace.add_stage(
                "intent-classifier",
                model=intent_result.get("model", "gpt-4o-mini"),
                latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
                tokens_input=intent_result.get("tokens_input", 0),
                tokens_output=intent_result.get("tokens_output", 0),
            )

            yield stage_event(
                "intent-classifier", "completed",
                latency_ms=int(budget.stages[-1].elapsed_ms) if budget.stages else None,
            )

            # ---------------------------------------------------------------
            # Phase 1b: Escalation check
            # ---------------------------------------------------------------
            if intent == ESCALATION_INTENT:
                async for event in self._handle_escalation(
                    tenant_id, conversation_id, customer_message,
                    prompts[AgentRole.ESCALATION_HANDLER], budget, trace,
                ):
                    yield event
                return

            # ---------------------------------------------------------------
            # Phase 2: Knowledge Retrieval
            # ---------------------------------------------------------------
            yield stage_event("knowledge-retrieval", "started")

            knowledge_result = await budget.execute_with_budget(
                "knowledge-retrieval",
                self._call_knowledge_retrieval(
                    customer_message, intent, prompts[AgentRole.KNOWLEDGE_RETRIEVAL],
                ),
            )

            knowledge_context = knowledge_result.get("context", "")
            sources = knowledge_result.get("sources", [])
            for source in sources:
                trace.add_knowledge_source(
                    entry_id=source.get("id", ""),
                    title=source.get("title", ""),
                    relevance_score=source.get("score", 0.0),
                    entry_type=source.get("type", ""),
                )
            trace.add_stage(
                "knowledge-retrieval",
                model=knowledge_result.get("model", "text-embedding-3-large"),
                latency_ms=budget.stages[-1].elapsed_ms if len(budget.stages) >= 2 else 0,
                tokens_input=knowledge_result.get("tokens_input", 0),
                tokens_output=knowledge_result.get("tokens_output", 0),
            )

            yield stage_event(
                "knowledge-retrieval", "completed",
                latency_ms=int(budget.stages[-1].elapsed_ms) if len(budget.stages) >= 2 else None,
            )

            # ---------------------------------------------------------------
            # Phase 3: Response Generation (streamed)
            # ---------------------------------------------------------------
            yield stage_event("response-generator", "started")
            rg_start = time.monotonic()

            full_response = ""
            sequence = 0

            async for chunk in self._call_response_generator_stream(
                customer_message=customer_message,
                intent=intent,
                knowledge_context=knowledge_context,
                system_prompt=prompts[AgentRole.RESPONSE_GENERATOR],
                budget=budget,
            ):
                full_response += chunk
                sequence += 1
                yield token_event(chunk, sequence)

            rg_elapsed = (time.monotonic() - rg_start) * 1000
            trace.add_stage(
                "response-generator",
                model="gpt-4o",
                latency_ms=rg_elapsed,
            )

            yield stage_event(
                "response-generator", "completed",
                latency_ms=int(rg_elapsed),
            )

            # ---------------------------------------------------------------
            # Phase 4: Critic validation (stream-then-validate, Decision UI-5)
            # ---------------------------------------------------------------
            yield stage_event("critic-supervisor", "started")

            approved, safe_text, critic_result = await self._validate_with_critic(
                tenant_id, conversation_id, full_response, customer_message, budget,
            )

            trace.set_critic_result(
                verdict=critic_result.verdict.value if critic_result.verdict else "unavailable",
                flags=critic_result.flags,
                latency_ms=critic_result.latency_ms,
            )

            yield stage_event(
                "critic-supervisor", "completed",
                latency_ms=int(critic_result.latency_ms),
            )

            if approved:
                # Record AI message with the (possibly modified) approved text
                message_id = await self._session.add_ai_message(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    content=safe_text,
                    agents_invoked=[s.stage for s in budget.stages],
                    model_used="gpt-4o",
                    critic_passed=True,
                    metadata={
                        "intent": intent,
                        "confidence": confidence,
                        "total_latency_ms": budget.elapsed_ms,
                    },
                )
                yield validated_event(conversation_id, message_id)
            else:
                # Critic rejected — retract streamed text, deliver fallback
                message_id = await self._session.add_ai_message(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    content=safe_text,
                    agents_invoked=[s.stage for s in budget.stages],
                    model_used="gpt-4o",
                    critic_passed=False,
                    metadata={
                        "intent": intent,
                        "retraction_reason": critic_result.block_reason.value
                        if critic_result.block_reason
                        else "unknown",
                    },
                )
                yield retracted_event(
                    fallback_text=safe_text,
                    reason=critic_result.block_reason.value
                    if critic_result.block_reason
                    else "rejected",
                )

            # ---------------------------------------------------------------
            # Phase 5: Analytics (fire-and-forget)
            # ---------------------------------------------------------------
            asyncio.create_task(
                self._fire_analytics(
                    tenant_id, conversation_id, intent, budget, trace,
                )
            )

            # Build and store decision trace
            decision_trace = trace.build()
            logger.debug(
                "Pipeline complete: conv=%s intent=%s critic=%s latency=%.0fms",
                conversation_id, intent, approved, budget.elapsed_ms,
            )

            # Final turn count from the session
            state = await self._session.get_conversation(tenant_id, conversation_id)
            yield done_event(conversation_id, state.turn_count)

        except PipelineTimeoutError as exc:
            logger.warning(
                "Pipeline timeout: conv=%s stage=%s budget=%dms elapsed=%.0fms",
                conversation_id, exc.stage, exc.budget_ms, exc.elapsed_ms,
            )
            yield error_event(
                "Response took too long. Please try again.",
                code="pipeline_timeout",
            )
            yield done_event(conversation_id, 0)

        except ServiceUnavailableError as exc:
            logger.warning(
                "Service unavailable: conv=%s service=%s",
                conversation_id, exc.service_name,
            )
            yield error_event(
                "A required service is temporarily unavailable. Please try again shortly.",
                code="service_unavailable",
            )
            yield done_event(conversation_id, 0)

        except Exception:
            logger.exception(
                "Pipeline error: conv=%s", conversation_id,
            )
            yield error_event(
                "An unexpected error occurred. Please try again.",
                code="internal_error",
            )
            yield done_event(conversation_id, 0)

    # -------------------------------------------------------------------
    # Customer context loading (Layer 1 + Layer 2)
    # -------------------------------------------------------------------

    async def _load_customer_profile(
        self,
        tenant_id: str,
        customer_id: str | None,
        tier: TenantTier,
        query: str,
        trace: DecisionTraceBuilder,
    ) -> CustomerProfileDocument | None:
        """Load Layer 1 profile and Layer 2 memory context."""
        if not customer_id:
            return None

        try:
            profile = await self._profile_service.get_profile(tenant_id, customer_id)
        except Exception:
            logger.debug("Profile lookup failed for %s — continuing without", customer_id)
            return None

        # Layer 2: semantic history search (consent-gated)
        if profile and self._vectorizer:
            consent = getattr(profile, "consent_status", ConsentStatus.NOT_ASKED)
            if consent == ConsentStatus.GRANTED:
                try:
                    history_results = await self._vectorizer.search_history(
                        tenant_id=tenant_id,
                        customer_id=customer_id,
                        query=query,
                        tier=tier,
                        consent_status=consent,
                    )
                    if history_results:
                        compressed = ConversationVectorizer.compress_for_prompt(
                            history_results,
                        )
                        for result in history_results:
                            trace.add_memory_signal(
                                source="conversation_history",
                                content_preview=result.get("chunk_text", "")[:80],
                                relevance_score=result.get("score", 0.0),
                                age_days=result.get("age_days", 0),
                            )
                except Exception:
                    logger.debug(
                        "Layer 2 search failed for %s — continuing without history",
                        customer_id,
                    )

        return profile

    # -------------------------------------------------------------------
    # Agent HTTP calls
    # -------------------------------------------------------------------

    async def _call_intent_classifier(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Intent Classification agent via HTTP."""
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

    async def _call_knowledge_retrieval(
        self,
        message: str,
        intent: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Knowledge Retrieval agent via HTTP."""
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

    async def _call_response_generator_stream(
        self,
        customer_message: str,
        intent: str,
        knowledge_context: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
    ) -> AsyncGenerator[str, None]:
        """Call the Response Generator with SSE streaming.

        Yields text chunks as they arrive from the Response Generator.
        The budget's remaining time is used as the read timeout.
        """
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
                # SSE format: "data: {text}" or raw text chunks
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

    async def _validate_with_critic(
        self,
        tenant_id: str,
        conversation_id: str,
        response_text: str,
        customer_message: str,
        budget: PipelineTimeoutBudget,
    ) -> tuple[bool, str, Any]:
        """Validate the generated response via the Critic (fail-closed).

        If no CriticPolicy is configured, returns the safe fallback
        (fail-closed by default — no unvalidated responses).
        """
        if not self._critic:
            # Fail-closed: no Critic configured means no response delivered
            from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult, CriticVerdict

            fallback_result = CriticResult(
                approved=False,
                verdict=None,
                block_reason=CriticBlockReason.UNAVAILABLE,
                flags=[],
                modified_response=None,
                latency_ms=0.0,
                critic_instance="none",
            )
            return False, SAFE_FALLBACK_MESSAGE, fallback_result

        return await self._critic.require_critic_approval(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            response_text=response_text,
            customer_message=customer_message,
        )

    # -------------------------------------------------------------------
    # Escalation handling
    # -------------------------------------------------------------------

    async def _handle_escalation(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        system_prompt: str,
        budget: PipelineTimeoutBudget,
        trace: DecisionTraceBuilder,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Handle escalation: call Escalation agent, update session."""
        yield stage_event("escalation-handler", "started")

        try:
            esc_result = await budget.execute_with_budget(
                "escalation-handler",
                self._call_escalation_handler(customer_message, system_prompt),
            )

            reason = esc_result.get("reason", "Customer requested human agent")
            trace.add_stage(
                "escalation-handler",
                model=esc_result.get("model", "gpt-4o-mini"),
                latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
            )

            yield stage_event("escalation-handler", "completed")

        except (PipelineTimeoutError, Exception) as exc:
            logger.warning(
                "Escalation agent failed: conv=%s error=%s — proceeding with default",
                conversation_id, exc,
            )
            reason = "Customer requested human agent"

        # Escalate the conversation in the session
        await self._session.escalate_conversation(
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            escalation_reason=reason,
        )

        # Yield escalation system message as a token event
        escalation_msg = (
            "I'm connecting you with a member of our support team. "
            "A human agent will be with you shortly."
        )
        yield token_event(escalation_msg, 1)
        yield validated_event(conversation_id, "escalation")
        yield done_event(conversation_id, 0)

    async def _call_escalation_handler(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Escalation Handler agent via HTTP."""
        url = self._agent_urls.get("escalation-handler", "")
        client = await self._get_http_client()

        response = await client.post(
            f"{url.rstrip('/')}{AGENT_ESCALATE_PATH}",
            json={
                "message": message,
                "system_prompt": system_prompt,
            },
        )
        response.raise_for_status()
        return response.json()

    # -------------------------------------------------------------------
    # Analytics (fire-and-forget)
    # -------------------------------------------------------------------

    async def _fire_analytics(
        self,
        tenant_id: str,
        conversation_id: str,
        intent: str,
        budget: PipelineTimeoutBudget,
        trace: DecisionTraceBuilder,
    ) -> None:
        """Send analytics event asynchronously (non-blocking)."""
        try:
            url = self._agent_urls.get("analytics-collector", "")
            client = await self._get_http_client()

            await client.post(
                f"{url.rstrip('/')}{AGENT_ANALYTICS_PATH}",
                json={
                    "tenant_id": tenant_id,
                    "conversation_id": conversation_id,
                    "intent": intent,
                    "stages": [
                        {
                            "stage": s.stage,
                            "elapsed_ms": s.elapsed_ms,
                            "succeeded": s.succeeded,
                        }
                        for s in budget.stages
                    ],
                    "total_latency_ms": budget.elapsed_ms,
                },
                timeout=httpx.Timeout(connect=1.0, read=2.0, write=1.0, pool=1.0),
            )
        except Exception:
            # Analytics is fire-and-forget — never block the pipeline
            logger.debug(
                "Analytics event failed for conv=%s — non-critical",
                conversation_id,
            )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_pipeline: ChatPipeline | None = None


def get_chat_pipeline() -> ChatPipeline:
    """Get the module-level ChatPipeline singleton.

    Returns a pipeline with default dependencies. For testing, use
    ChatPipeline() directly with injected mocks.
    """
    global _pipeline
    if _pipeline is None:
        from src.multi_tenant.customer_profile_service import get_profile_service
        from src.multi_tenant.system_prompt_builder import get_prompt_builder

        from src.chat.session import get_conversation_session

        _pipeline = ChatPipeline(
            session=get_conversation_session(),
            prompt_builder=get_prompt_builder(),
            profile_service=get_profile_service(),
        )
    return _pipeline


def configure_chat_pipeline(
    session: ConversationSession,
    prompt_builder: SystemPromptBuilder,
    profile_service: CustomerProfileService,
    vectorizer: ConversationVectorizer | None = None,
    critic: CriticPolicy | None = None,
    meter: ConversationMeter | None = None,
    agent_urls: dict[str, str] | None = None,
) -> ChatPipeline:
    """Configure the module-level singleton with explicit dependencies.

    Called during app startup (main.py) after all services are initialized.
    """
    global _pipeline
    _pipeline = ChatPipeline(
        session=session,
        prompt_builder=prompt_builder,
        profile_service=profile_service,
        vectorizer=vectorizer,
        critic=critic,
        meter=meter,
        agent_urls=agent_urls,
    )
    return _pipeline
