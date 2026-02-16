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
import sys
import time
import traceback
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

# Azure OpenAI direct integration (WI #207 — Issue #32)
# When USE_AGENT_CONTAINERS is false (default), the pipeline calls Azure
# OpenAI directly instead of routing through AGNTCY agent containers.
# This is required because the upstream AGNTCY containers are in
# ActivationFailed state (demo mode images with no HTTP endpoints).
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None  # type: ignore[assignment,misc]

# Layer 4: Fine-tuned model selection + A/B routing (WI #93-96)
# Imported lazily inside execute() to avoid circular import at module load.

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# WI #131: Azure OpenAI error classification
# ---------------------------------------------------------------------------


def _classify_openai_error(exc: Exception) -> tuple[str, str, bool]:
    """Classify an Azure OpenAI exception into error code, message, and recoverability.

    Returns:
        (code, message, recoverable) tuple for the error_event factory.
    """
    exc_type = type(exc).__name__
    exc_msg = str(exc).lower()

    # Rate limit (HTTP 429)
    if "ratelimit" in exc_type.lower() or "429" in str(exc):
        return (
            "rate_limited",
            "AI service is temporarily busy. Please wait a moment and try again.",
            True,
        )

    # Content filter triggered (Azure OpenAI specific)
    if "content_filter" in exc_msg or "contentfilter" in exc_msg:
        return (
            "content_filtered",
            "Your message could not be processed due to content safety policies.",
            False,
        )

    # Model overloaded / server error (HTTP 503)
    if "503" in str(exc) or "overloaded" in exc_msg or "server_error" in exc_msg:
        return (
            "model_overloaded",
            "The AI model is temporarily overloaded. Please try again shortly.",
            True,
        )

    # Timeout
    if "timeout" in exc_type.lower() or "timeout" in exc_msg:
        return (
            "generation_timeout",
            "Response generation timed out. Please try again.",
            True,
        )

    # Authentication / configuration error (non-recoverable)
    if "auth" in exc_type.lower() or "401" in str(exc) or "403" in str(exc):
        return (
            "ai_configuration_error",
            "AI service configuration error. Please contact support.",
            False,
        )

    # Connection error
    if "connect" in exc_type.lower() or "connection" in exc_msg:
        return (
            "ai_connection_error",
            "Unable to connect to AI service. Please try again shortly.",
            True,
        )

    # Generic fallback
    return (
        "generation_error",
        "An error occurred while generating the response. Please try again.",
        True,
    )


# ---------------------------------------------------------------------------
# Constants — agent HTTP endpoints (configurable via environment)
# ---------------------------------------------------------------------------

# USE_AGENT_CONTAINERS controls whether the pipeline routes through AGNTCY
# agent containers (HTTP) or calls Azure OpenAI directly.
#
# Default: False — use direct Azure OpenAI calls.
# Set to "true" only when AGNTCY agent containers are healthy and serving.
USE_AGENT_CONTAINERS = os.environ.get(
    "USE_AGENT_CONTAINERS", "false"
).lower() == "true"

# Default agent URLs — overridden by environment variables in production.
# Only used when USE_AGENT_CONTAINERS=true.
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

# Azure OpenAI model deployment names (match aoai-agentred-eastus2 deployments)
AZURE_IC_MODEL = os.environ.get("AZURE_IC_MODEL", "gpt-4o-mini")
AZURE_RG_MODEL = os.environ.get("AZURE_RG_MODEL", "gpt-4o")
AZURE_CR_MODEL = os.environ.get("AZURE_CR_MODEL", "gpt-4o-mini")
AZURE_EMBEDDING_MODEL = os.environ.get(
    "AZURE_EMBEDDING_MODEL", "text-embedding-3-large"
)
AZURE_EMBEDDING_DIMENSIONS = 3072

# Intent classification taxonomy — the set of intents the IC can return.
# Matches AGNTCY's upstream 17-intent taxonomy.
INTENT_TAXONOMY = [
    "general_inquiry",
    "product_question",
    "order_status",
    "return_request",
    "exchange_request",
    "refund_request",
    "shipping_inquiry",
    "pricing_question",
    "availability_check",
    "complaint",
    "feedback",
    "account_issue",
    "payment_issue",
    "subscription_question",
    "technical_support",
    "greeting",
    "escalation",
]


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
        openai_client: Any | None = None,
        kb_repo: Any | None = None,
    ) -> None:
        self._session = session
        self._prompt_builder = prompt_builder
        self._profile_service = profile_service
        self._vectorizer = vectorizer
        self._critic = critic
        self._meter = meter
        self._agent_urls = agent_urls or AGENT_URLS
        self._http_client: httpx.AsyncClient | None = None
        # Azure OpenAI direct client (WI #207)
        self._openai_client = openai_client
        # Knowledge base repository for direct retrieval
        self._kb_repo = kb_repo

        # -------------------------------------------------------------------
        # Phase 2.4: A2A agent instances (in-process)
        #
        # When USE_AGENT_CONTAINERS is False, the pipeline delegates to
        # extracted agent modules instead of duplicating inline Azure OpenAI
        # logic. Each agent implements BaseAgentProtocol.process() and
        # encapsulates the same logic that was previously in
        # _call_*_direct() methods.
        # -------------------------------------------------------------------
        self._ic_agent: Any | None = None
        self._kr_agent: Any | None = None
        self._rg_agent: Any | None = None
        self._esc_agent: Any | None = None
        self._an_agent: Any | None = None
        self._cr_agent: Any | None = None
        self._init_agents()

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

    def _init_agents(self) -> None:
        """Initialize in-process A2A agent instances.

        Each agent is configured with the same dependencies that were
        previously used by the inline _call_*_direct() methods. The agents
        are only created when USE_AGENT_CONTAINERS is False — when True,
        the pipeline routes to external containers via HTTP.
        """
        if USE_AGENT_CONTAINERS:
            return

        from src.agents.intent_classifier import IntentClassifierAgent
        from src.agents.knowledge_retrieval import KnowledgeRetrievalAgent
        from src.agents.response_generator import ResponseGeneratorAgent
        from src.agents.escalation_handler import EscalationHandlerAgent
        from src.agents.analytics_collector import AnalyticsCollectorAgent
        from src.agents.critic_supervisor import CriticSupervisorAgent

        self._ic_agent = IntentClassifierAgent(openai_client=self._openai_client)
        self._kr_agent = KnowledgeRetrievalAgent(
            kb_repo=self._kb_repo,
        )
        self._rg_agent = ResponseGeneratorAgent(openai_client=self._openai_client)
        self._esc_agent = EscalationHandlerAgent(openai_client=self._openai_client)
        self._an_agent = AnalyticsCollectorAgent()
        self._cr_agent = CriticSupervisorAgent(openai_client=self._openai_client)

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
        conversation_history: list[dict[str, str]] | None = None,
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
            conversation_history: Prior messages as list of
                {"role": "user"|"assistant", "content": "..."} dicts
                for multi-turn context. Most recent last. Capped by caller.

        Yields:
            StreamEvent objects (stage, token, validated/retracted, done/error).
        """
        budget = PipelineTimeoutBudget()
        trace = DecisionTraceBuilder(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            customer_id=customer_id or "",
        )
        tier = tenant.tier or TenantTier.STARTER

        # Store tenant_id and preferences for knowledge retrieval
        self._current_tenant_id = tenant_id
        self._current_preferences = preferences

        try:
            # ---------------------------------------------------------------
            # Phase 0: Load customer context (Layer 1 + Layer 2)
            # ---------------------------------------------------------------
            profile = await self._load_customer_profile(
                tenant_id, customer_id, tier, customer_message, trace,
            )

            # Extract asserted identity from customer message (Issue #5b)
            if customer_id and customer_message and self._profile_service:
                try:
                    await self._profile_service.extract_and_store_identity(
                        tenant_id, customer_id, customer_message,
                    )
                except Exception:
                    pass  # Non-fatal — best-effort identity extraction

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
            # Layer 4: Fine-tuned model selection + A/B routing (WI #93-96)
            #
            # If the tenant has a fine-tuned model deployed (Enterprise
            # add-on), use it for the Response Generator instead of the
            # default gpt-4o. If an A/B experiment is active, the customer
            # is deterministically assigned to control (base model) or
            # treatment (fine-tuned model) via SHA-256 hash.
            # ---------------------------------------------------------------
            response_model = "gpt-4o"  # Default base model
            ab_variant: str | None = None
            ab_experiment_id: str | None = None

            if (
                preferences.fine_tuning_enabled
                and preferences.fine_tuning_active_model_id
            ):
                try:
                    from src.multi_tenant.fine_tuning_pipeline import (
                        get_fine_tuning_service,
                    )

                    ft_service = get_fine_tuning_service()

                    if preferences.fine_tuning_ab_experiment_id:
                        # A/B experiment active — deterministic assignment
                        experiment = await ft_service.get_experiment(
                            preferences.fine_tuning_ab_experiment_id,
                        )
                        if experiment and customer_id:
                            variant = ft_service.assign_customer_variant(
                                experiment, customer_id,
                            )
                            ab_variant = variant
                            ab_experiment_id = experiment.experiment_id
                            if variant == "treatment":
                                response_model = (
                                    preferences.fine_tuning_active_model_id
                                )
                            # else: variant == "control", keep base model
                            trace.set_ab_variant(ab_variant, ab_experiment_id)
                    else:
                        # No A/B experiment — use fine-tuned model directly
                        response_model = (
                            preferences.fine_tuning_active_model_id
                        )

                    logger.debug(
                        "Layer 4 model selection: tenant=%s model=%s "
                        "ab_variant=%s ab_experiment=%s",
                        tenant_id,
                        response_model,
                        ab_variant,
                        ab_experiment_id,
                    )
                except Exception:
                    logger.debug(
                        "Layer 4 model selection failed — falling back "
                        "to base model for tenant=%s",
                        tenant_id,
                    )
                    response_model = "gpt-4o"

            # ---------------------------------------------------------------
            # Phase 1: Intent Classification + Knowledge Retrieval
            #
            # WI #134: IC and KR run concurrently (asyncio.gather). Both
            # operate on the raw customer message and don't depend on each
            # other's output. Parallelization saves ~800ms (IC 800ms budget
            # runs in parallel with KR 1,000ms instead of sequential).
            #
            # If IC detects escalation intent, KR results are discarded
            # and the escalation handler takes over.
            # ---------------------------------------------------------------
            yield stage_event("intent-classifier", "started")
            yield stage_event("knowledge-retrieval", "started")

            # Launch both agents concurrently
            ic_task = budget.execute_with_budget(
                "intent-classifier",
                self._call_intent_classifier(
                    customer_message, prompts[AgentRole.INTENT_CLASSIFIER],
                ),
            )
            kr_task = budget.execute_with_budget(
                "knowledge-retrieval",
                self._call_knowledge_retrieval(
                    customer_message, "general_inquiry", prompts[AgentRole.KNOWLEDGE_RETRIEVAL],
                ),
            )

            intent_result, knowledge_result = await asyncio.gather(ic_task, kr_task)

            # Process IC result
            intent = intent_result.get("intent", "general_inquiry")
            confidence = intent_result.get("confidence", 0.0)
            trace.add_stage(
                "intent-classifier",
                model=intent_result.get("model", "gpt-4o-mini"),
                latency_ms=budget.stages[0].elapsed_ms if budget.stages else 0,
                tokens_input=intent_result.get("tokens_input", 0),
                tokens_output=intent_result.get("tokens_output", 0),
            )

            yield stage_event(
                "intent-classifier", "completed",
                latency_ms=int(budget.stages[0].elapsed_ms) if budget.stages else None,
            )

            # ---------------------------------------------------------------
            # Phase 1b: Escalation check (KR results discarded if escalated)
            # ---------------------------------------------------------------
            if intent == ESCALATION_INTENT:
                async for event in self._handle_escalation(
                    tenant_id, conversation_id, customer_message,
                    prompts[AgentRole.ESCALATION_HANDLER], budget, trace,
                ):
                    yield event
                return

            # Process KR result
            # For greeting intents, clear knowledge context so the
            # response generator focuses on being warm and natural
            # instead of dumping product information into a "hello".
            knowledge_context = knowledge_result.get("context", "")
            sources = knowledge_result.get("sources", [])
            if intent == "greeting":
                knowledge_context = ""
                sources = []
            for source in sources:
                trace.add_knowledge_source(
                    entry_id=source.get("id", ""),
                    title=source.get("title", ""),
                    relevance_score=source.get("score", 0.0),
                    entry_type=source.get("type", ""),
                )
            kr_stage_idx = 1 if len(budget.stages) >= 2 else 0
            trace.add_stage(
                "knowledge-retrieval",
                model=knowledge_result.get("model", "text-embedding-3-large"),
                latency_ms=budget.stages[kr_stage_idx].elapsed_ms if len(budget.stages) > kr_stage_idx else 0,
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
            logger.info(
                "RG input: conv=%s intent=%s knowledge_len=%d sources=%d",
                conversation_id, intent,
                len(knowledge_context), len(sources),
            )
            yield stage_event("response-generator", "started")
            rg_start = time.monotonic()

            full_response = ""
            sequence = 0

            try:
                async for chunk in self._call_response_generator_stream(
                    customer_message=customer_message,
                    intent=intent,
                    knowledge_context=knowledge_context,
                    system_prompt=prompts[AgentRole.RESPONSE_GENERATOR],
                    budget=budget,
                    model=response_model,
                    conversation_history=conversation_history,
                ):
                    full_response += chunk
                    sequence += 1
                    yield token_event(chunk, sequence)
            except (PipelineTimeoutError, ServiceUnavailableError):
                raise  # Let outer handlers deal with these
            except Exception as rg_exc:
                code, msg, recoverable = _classify_openai_error(rg_exc)
                logger.warning(
                    "Response generator error mid-stream: conv=%s tokens_sent=%d code=%s err=%s",
                    conversation_id, sequence, code, rg_exc,
                )
                yield error_event(
                    msg, code=code,
                    recoverable=recoverable,
                    tokens_sent=sequence,
                    stage="response-generator",
                )
                yield done_event(conversation_id, 0)
                return

            rg_elapsed = (time.monotonic() - rg_start) * 1000
            trace.add_stage(
                "response-generator",
                model=response_model,
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

            # Extract KB article titles so Critic knows the response
            # was generated from legitimate product knowledge.
            knowledge_titles = [s.get("title", "") for s in sources if s.get("title")]

            approved, safe_text, critic_result = await self._validate_with_critic(
                tenant_id, conversation_id, full_response, customer_message, budget,
                knowledge_titles=knowledge_titles,
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
                # Append source citations if enabled (RAG Phase 1)
                prefs = getattr(self, "_current_preferences", None)
                if prefs and prefs.cite_sources_in_response and sources:
                    source_titles = [s.get("title", "") for s in sources if s.get("title")]
                    if source_titles:
                        citation_line = "\n\nSources: " + ", ".join(source_titles)
                        safe_text = safe_text + citation_line

                # Record AI message with the (possibly modified) approved text
                message_id = await self._session.add_ai_message(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    content=safe_text,
                    agents_invoked=[s.stage for s in budget.stages],
                    model_used=response_model,
                    critic_passed=True,
                    metadata={
                        "intent": intent,
                        "confidence": confidence,
                        "total_latency_ms": budget.elapsed_ms,
                        **({"ab_variant": ab_variant, "ab_experiment_id": ab_experiment_id}
                           if ab_variant else {}),
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
                    model_used=response_model,
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
                recoverable=True,
                stage=exc.stage,
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
                recoverable=True,
                stage=exc.service_name,
            )
            yield done_event(conversation_id, 0)

        except Exception as exc:
            # Include exception details in SSE event for debugging
            exc_type = type(exc).__name__
            exc_msg = str(exc)[:500]  # Truncate long messages
            tb_str = traceback.format_exc()

            # Print to stderr to bypass structured logging formatter
            print(
                f"[PIPELINE FATAL] conv={conversation_id} "
                f"tenant={tenant_id}\n{tb_str}",
                file=sys.stderr, flush=True,
            )
            logger.exception(
                "Pipeline error: conv=%s type=%s msg=%s",
                conversation_id, exc_type, exc_msg,
            )
            yield error_event(
                f"An unexpected error occurred: {exc_type}: {exc_msg}",
                code="internal_error",
                recoverable=True,
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
    # Agent calls — dispatch to direct Azure OpenAI or HTTP containers
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

        return await self._kr_agent.process(
            {
                "message": message,
                "intent": intent,
                "tenant_id": tenant_id or "",
                "preferences": prefs_dict,
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

    async def _validate_with_critic(
        self,
        tenant_id: str,
        conversation_id: str,
        response_text: str,
        customer_message: str,
        budget: PipelineTimeoutBudget,
        knowledge_titles: list[str] | None = None,
    ) -> tuple[bool, str, Any]:
        """Validate the generated response via the Critic (fail-closed).

        Priority order:
        1. CriticPolicy (HTTP to AGNTCY container) — if configured
        2. Direct Azure OpenAI GPT-4o-mini validation — if OpenAI client available
        3. Fail-closed fallback — no unvalidated responses delivered

        The direct Azure OpenAI path (option 2) implements the same
        fail-closed semantics: if the model says "reject" or if the
        call fails, the response is blocked.
        """
        from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult, CriticVerdict

        # Option 1: Use CriticPolicy if configured (HTTP to AGNTCY containers)
        if self._critic:
            return await self._critic.require_critic_approval(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                response_text=response_text,
                customer_message=customer_message,
            )

        # Option 2: Direct Azure OpenAI validation (WI #207)
        if self._openai_client and not USE_AGENT_CONTAINERS:
            return await self._validate_with_critic_direct(
                tenant_id, conversation_id, response_text,
                customer_message, budget,
                knowledge_titles=knowledge_titles,
            )

        # Option 3: Fail-closed — no Critic available
        fallback_result = CriticResult(
            approved=False,
            verdict=None,
            block_reason=CriticBlockReason.UNAVAILABLE,
            flags=[],
            modified_response=None,
            latency_ms=0.0,
            critic_instance="none",
            request_id=f"critic-{conversation_id}-{int(time.time() * 1000)}",
        )
        return False, SAFE_FALLBACK_MESSAGE, fallback_result

    async def _validate_with_critic_direct(
        self,
        tenant_id: str,
        conversation_id: str,
        response_text: str,
        customer_message: str,
        budget: PipelineTimeoutBudget,
        knowledge_titles: list[str] | None = None,
    ) -> tuple[bool, str, Any]:
        """Validate response via in-process CriticSupervisorAgent (A2A).

        Delegates to the extracted agent module which encapsulates the
        fail-closed Critic validation using Azure OpenAI GPT-4o-mini.

        The agent returns a dict; this method adapts it to the
        (approved, safe_text, CriticResult) tuple expected by the caller.
        """
        from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult, CriticVerdict

        cr_result = await self._cr_agent.process(
            {
                "response_text": response_text,
                "customer_message": customer_message,
                "knowledge_titles": knowledge_titles or [],
                "conversation_id": conversation_id,
            },
            {},
        )

        approved = cr_result.get("approved", False)
        safe_text = cr_result.get("safe_text", SAFE_FALLBACK_MESSAGE)

        # Map agent dict to CriticResult dataclass for pipeline compatibility
        verdict_str = cr_result.get("verdict", "unavailable")
        try:
            verdict = CriticVerdict(verdict_str)
        except ValueError:
            verdict = None

        block_reason_str = cr_result.get("block_reason")
        block_reason = None
        if block_reason_str:
            try:
                block_reason = CriticBlockReason(block_reason_str)
            except ValueError:
                block_reason = CriticBlockReason.ERROR

        result = CriticResult(
            approved=approved,
            verdict=verdict,
            block_reason=block_reason,
            flags=cr_result.get("flags", []),
            modified_response=cr_result.get("modified_response"),
            latency_ms=cr_result.get("latency_ms", 0.0),
            critic_instance="in-process-agent",
            request_id=cr_result.get("request_id", f"critic-{conversation_id}"),
        )

        return approved, safe_text, result

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

        urgency = "medium"
        context_summary = ""

        try:
            esc_result = await budget.execute_with_budget(
                "escalation-handler",
                self._call_escalation_handler(customer_message, system_prompt),
            )

            reason = esc_result.get("reason", "Customer requested human agent")
            urgency = esc_result.get("urgency", "medium")
            context_summary = esc_result.get("context_summary", "")
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

        # Fire-and-forget: notify assigned escalation agents
        try:
            from src.multi_tenant.alert_delivery import send_escalation_alert

            logger.info(
                "Firing escalation alert: tenant=%s conversation=%s reason=%s urgency=%s",
                tenant_id, conversation_id, reason[:80], urgency,
            )
            asyncio.ensure_future(
                send_escalation_alert(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    reason=reason,
                    urgency=urgency,
                    context_summary=context_summary,
                )
            )
        except Exception:
            logger.debug("Escalation alert skipped (alert service not configured)")

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
        """Route escalation to Azure OpenAI directly or AGNTCY container."""
        if USE_AGENT_CONTAINERS:
            return await self._call_escalation_handler_http(message, system_prompt)
        return await self._call_escalation_handler_direct(message, system_prompt)

    async def _call_escalation_handler_direct(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Evaluate escalation via in-process EscalationHandlerAgent (A2A).

        Delegates to the extracted agent module which encapsulates the
        Azure OpenAI GPT-4o-mini call for escalation analysis.
        """
        return await self._esc_agent.process(
            {"message": message, "system_prompt": system_prompt},
            {},
        )

    async def _call_escalation_handler_http(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Call the Escalation Handler agent via HTTP (AGNTCY container)."""
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
        """Send analytics event asynchronously (non-blocking).

        When USE_AGENT_CONTAINERS is false, delegates to the in-process
        AnalyticsCollectorAgent. When true, sends to the AGNTCY container.
        """
        try:
            analytics_data = {
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
            }

            if USE_AGENT_CONTAINERS:
                url = self._agent_urls.get("analytics-collector", "")
                client = await self._get_http_client()
                await client.post(
                    f"{url.rstrip('/')}{AGENT_ANALYTICS_PATH}",
                    json=analytics_data,
                    timeout=httpx.Timeout(connect=1.0, read=2.0, write=1.0, pool=1.0),
                )
            else:
                # Delegate to in-process AnalyticsCollectorAgent
                await self._an_agent.process(analytics_data, {})
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


def _create_openai_client() -> Any:
    """Create an AsyncAzureOpenAI client from environment variables.

    Returns None if credentials are not configured (development mode).
    """
    if AsyncAzureOpenAI is None:
        logger.warning("openai package not installed — direct Azure OpenAI calls disabled")
        return None

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "")

    if not endpoint or not api_key:
        logger.warning(
            "AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY not set — "
            "direct Azure OpenAI calls disabled"
        )
        return None

    return AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-10-21",
    )


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
            openai_client=_create_openai_client(),
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
    openai_client: Any | None = None,
    kb_repo: Any | None = None,
) -> ChatPipeline:
    """Configure the module-level singleton with explicit dependencies.

    Called during app startup (main.py) after all services are initialized.

    When openai_client is not provided and USE_AGENT_CONTAINERS is False,
    a default AsyncAzureOpenAI client is created from environment variables.
    """
    if openai_client is None and not USE_AGENT_CONTAINERS:
        openai_client = _create_openai_client()

    global _pipeline
    _pipeline = ChatPipeline(
        session=session,
        prompt_builder=prompt_builder,
        profile_service=profile_service,
        vectorizer=vectorizer,
        critic=critic,
        meter=meter,
        agent_urls=agent_urls,
        openai_client=openai_client,
        kb_repo=kb_repo,
    )
    return _pipeline
