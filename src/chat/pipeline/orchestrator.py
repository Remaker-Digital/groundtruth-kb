"""ChatPipeline orchestrator — main pipeline entry point.

Contains the ChatPipeline class which inherits from AgentDispatchMixin,
CriticEscalationMixin, and AnalyticsMixin. The execute() async generator
and __init__ / close / _init_agents / _load_customer_profile methods
live here.

R10 refactoring — extracted from pipeline.py (session 39).
(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
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
from src.chat.pipeline.agent_dispatch import AgentDispatchMixin
from src.chat.pipeline.analytics import AnalyticsMixin
from src.chat.pipeline.constants import (
    AGENT_URLS,
    ESCALATION_INTENT,
    USE_AGENT_CONTAINERS,
)
from src.chat.pipeline.constants import _classify_openai_error
from src.chat.pipeline.critic_escalation import CriticEscalationMixin
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
from src.multi_tenant.critic_policy import CriticPolicy
from src.multi_tenant.customer_profile_service import CustomerProfileService
from src.multi_tenant.pipeline_resilience import (
    PipelineTimeoutBudget,
    PipelineTimeoutError,
    ServiceUnavailableError,
)
from src.multi_tenant.response_explainability import DecisionTraceBuilder
from src.multi_tenant.system_prompt_builder import (
    AgentRole,
    SystemPromptBuilder,
)

# Azure OpenAI direct integration (WI #207 -- Issue #32)
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


class ChatPipeline(AgentDispatchMixin, CriticEscalationMixin, AnalyticsMixin):
    """Orchestrates the 6-agent pipeline for a single conversation turn.

    For each customer message, the pipeline:
        1. Builds per-agent system prompts (SystemPromptBuilder)
        2. Loads customer context (Layer 1 profile + Layer 2 history)
        3. Classifies intent (IC)
        4. Retrieves knowledge (KR)
        5. Generates response with SSE streaming (RG)
        6. Validates via Critic (CR) -- stream-then-validate
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
        are only created when USE_AGENT_CONTAINERS is False -- when True,
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
        """Run the full pipeline for a customer message.

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

        # Store tenant_id, tenant doc, and preferences for knowledge retrieval
        self._current_tenant_id = tenant_id
        self._current_tenant = tenant
        self._current_preferences = preferences

        # Configure per-tenant PII scrubbing on stored transcripts
        pii_enabled = getattr(preferences, "pii_scrubbing", False) is True
        self._session.set_pii_scrubber(pii_enabled)

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
                    pass  # Non-fatal -- best-effort identity extraction

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
                        # A/B experiment active -- deterministic assignment
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
                        # No A/B experiment -- use fine-tuned model directly
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
                        "Layer 4 model selection failed -- falling back "
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
                # Critic rejected -- retract streamed text, deliver fallback
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
            logger.debug("Profile lookup failed for %s -- continuing without", customer_id)
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
                        "Layer 2 search failed for %s -- continuing without history",
                        customer_id,
                    )

        return profile
