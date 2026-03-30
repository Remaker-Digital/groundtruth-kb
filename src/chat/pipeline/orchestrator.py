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
    ADMIN_ASSISTANCE_INTENT,
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
        self._http_lock = asyncio.Lock()
        # Background task references — prevents GC of fire-and-forget tasks
        self._background_tasks: set[asyncio.Task] = set()
        # Azure OpenAI direct client (WI #207)
        self._openai_client = openai_client
        # Knowledge base repository for direct retrieval
        self._kb_repo = kb_repo

        # WI #138: Customer context pre-computation / warm-up cache.
        # Layer 1 profile is immutable within a conversation, so we cache it
        # after the first fetch to avoid repeated Cosmos DB reads on every turn.
        # Key: "tenant_id:customer_id", Value: profile or None.
        self._profile_cache: dict[str, CustomerProfileDocument | None] = {}

        # -------------------------------------------------------------------
        # A2A agent instances (in-process, legacy)
        #
        # DCL-002: canonical dispatch uses transport/HTTP, not in-process.
        # These remain only for IC/KR/RG _direct() stubs pending Phase 3
        # dead code sweep. Analytics/Critic/Escalation agents removed (S224).
        # -------------------------------------------------------------------
        self._ic_agent: Any | None = None
        self._kr_agent: Any | None = None
        self._rg_agent: Any | None = None
        self._init_agents()

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the shared HTTP client with connection pooling.

        Uses asyncio.Lock to prevent race conditions where concurrent
        coroutines could each create a separate client, leaking connections.
        """
        async with self._http_lock:
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

    def _create_background_task(self, coro, *, name: str | None = None) -> asyncio.Task:
        """Create a fire-and-forget task with proper lifecycle management.

        Stores a reference to prevent garbage collection and attaches a
        done callback that logs unhandled exceptions and auto-discards
        the reference on completion.
        """
        task = asyncio.create_task(coro, name=name)
        self._background_tasks.add(task)

        def _on_done(t: asyncio.Task) -> None:
            self._background_tasks.discard(t)
            if not t.cancelled() and t.exception() is not None:
                logger.warning(
                    "Background task %s failed: %s",
                    t.get_name(),
                    t.exception(),
                )

        task.add_done_callback(_on_done)
        return task

    def _init_agents(self) -> None:
        """Initialize in-process A2A agent instances (legacy, SPEC-1538).

        DCL-002: canonical dispatch uses transport/HTTP → 503. In-process
        agents are retained only for IC/KR/RG _direct() stubs (pending
        Phase 3 dead code sweep) and CoPilot. Analytics, Critic, and
        Escalation agent instances removed in S224.
        """
        from src.agents.intent_classifier import IntentClassifierAgent
        from src.agents.knowledge_retrieval import KnowledgeRetrievalAgent
        from src.agents.response_generator import ResponseGeneratorAgent
        from src.agents.co_pilot import CoPilotAgent
        from src.multi_tenant.repositories.platform import AdminDocumentationRepository

        self._ic_agent = IntentClassifierAgent(openai_client=self._openai_client)
        self._kr_agent = KnowledgeRetrievalAgent(
            kb_repo=self._kb_repo,
        )
        self._rg_agent = ResponseGeneratorAgent(openai_client=self._openai_client)
        self._copilot_agent = CoPilotAgent(
            openai_client=self._openai_client,
            admin_doc_repo=AdminDocumentationRepository(),
        )

    # -------------------------------------------------------------------
    # WI #138: Pre-computation / warm-up
    # -------------------------------------------------------------------

    async def warm_up(
        self,
        tenant_id: str,
        customer_id: str | None,
        tier: "TenantTier | None" = None,
    ) -> None:
        """Pre-load customer context before the first message arrives.

        Called when the SSE connection opens (before the first customer
        message). Pre-fetches the Layer 1 customer profile and caches it
        so that ``execute()`` skips the Cosmos DB read on the first turn.

        This is fire-and-forget — failures are silently logged. The
        pipeline falls back to on-demand loading if warm-up is skipped.
        """
        if not customer_id:
            return
        cache_key = f"{tenant_id}:{customer_id}"
        if cache_key in self._profile_cache:
            return  # Already warmed up
        try:
            profile = await self._profile_service.get_profile(tenant_id, customer_id)
            self._profile_cache[cache_key] = profile
            logger.debug("Warmed up profile for %s:%s", tenant_id, customer_id)
        except Exception:
            logger.debug("Warm-up profile fetch failed for %s -- will retry in execute()", customer_id, exc_info=True)

    def invalidate_profile_cache(self, tenant_id: str, customer_id: str) -> None:
        """Invalidate a cached profile (e.g. after mid-conversation verification)."""
        cache_key = f"{tenant_id}:{customer_id}"
        self._profile_cache.pop(cache_key, None)

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
        customer_verified: bool = False,
        trace_id: str | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        team_member_role: str | None = None,
        target_agent_id: str | None = None,
        staff_domain_tags: tuple[str, ...] | None = None,
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
            customer_verified: Whether the customer has been verified via
                OTP, Shopify HMAC, or other mechanism (P0-AUTH-FIX).
            conversation_history: Prior messages as list of
                {"role": "user"|"assistant", "content": "..."} dicts
                for multi-turn context. Most recent last. Capped by caller.
            team_member_role: If set, the user is an authenticated team
                member. Routes to Co-pilot agent (SPEC-1558).

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

        # SPEC-1530: Store trace_id for A2A header propagation
        self._current_trace_id = trace_id or ""
        self._current_conversation_id = conversation_id

        # Store tenant_id, tenant doc, and preferences for knowledge retrieval
        self._current_tenant_id = tenant_id
        self._current_tenant = tenant
        self._current_preferences = preferences

        # Configure per-tenant PII scrubbing on stored transcripts
        pii_enabled = getattr(preferences, "pii_scrubbing", False) is True
        self._session.set_pii_scrubber(pii_enabled)

        # SPEC-1541: Root pipeline span for execution tree reconstruction
        from src.multi_tenant.otel_tracing import trace_pipeline_root

        pipeline_span = trace_pipeline_root(conversation_id)
        pipeline_span.set_attribute("pipeline.tenant_id", tenant_id)
        pipeline_span.set_attribute("pipeline.tier", tier.value if hasattr(tier, "value") else str(tier))

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
                    logger.debug(
                        "Identity extraction failed for %s -- non-fatal",
                        customer_id,
                        exc_info=True,
                    )

            # Build system prompts for all agents
            # P0-AUTH-FIX: A customer is "anonymous" only if they have no
            # pre-existing customer_id AND have not been verified in-conversation
            # via OTP or Shopify HMAC.  In-conversation verification sets
            # customer_verified=True on the ConversationDocument, allowing
            # previously-anonymous users to become identified mid-session.
            is_anonymous = customer_id is None and not customer_verified
            prompts = self._prompt_builder.build_all(
                tenant=tenant,
                preferences=preferences,
                customer_profile=profile,
                is_anonymous=is_anonymous,
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
            quality_experiment_variant: str | None = None
            quality_experiment_id: str | None = None

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
            # Layer 5: Quality experiment A/B routing (SPEC-0621 / WI-1522)
            #
            # If a conversation quality experiment is active for this tenant,
            # assign the customer to control/treatment and apply the variant's
            # config overrides to the quality settings for this conversation.
            # This is independent of fine-tuned model A/B experiments.
            # ---------------------------------------------------------------
            # ---------------------------------------------------------------
            # Phase 6: PII Tokenization (SPEC-1543)
            #
            # Tokenize PII in the customer message before it reaches any
            # AI agent. The tokenized message is used for IC, KR, and RG.
            # Original values are restored after Critic validation (SPEC-1544).
            # ---------------------------------------------------------------
            from src.multi_tenant.pii_tokenizer import PiiTokenizer

            customer_names: list[str] = []
            if profile:
                if hasattr(profile, "customer_name") and profile.customer_name:
                    customer_names.append(profile.customer_name)
                if hasattr(profile, "first_name") and profile.first_name:
                    customer_names.append(profile.first_name)

            pii_tokenizer = PiiTokenizer(customer_names=customer_names)
            tokenized_message = pii_tokenizer.tokenize(
                customer_message,
                conversation_id=conversation_id,
                tenant_id=tenant_id,
            )

            # ---------------------------------------------------------------
            # Phase 1: Intent Classification + Knowledge Retrieval
            #
            # WI #134: IC and KR run concurrently (asyncio.gather). Both
            # operate on the tokenized customer message and don't depend on
            # each other's output. Parallelization saves ~800ms (IC 800ms
            # budget runs in parallel with KR 1,000ms instead of sequential).
            #
            # If IC detects escalation intent, KR results are discarded
            # and the escalation handler takes over.
            # ---------------------------------------------------------------
            yield stage_event("intent-classifier", "started", trace_id=trace_id)
            yield stage_event("knowledge-retrieval", "started", trace_id=trace_id)

            # Launch both agents concurrently (using tokenized message)
            ic_task = budget.execute_with_budget(
                "intent-classifier",
                self._call_intent_classifier(
                    tokenized_message, prompts[AgentRole.INTENT_CLASSIFIER],
                ),
            )
            kr_task = budget.execute_with_budget(
                "knowledge-retrieval",
                self._call_knowledge_retrieval(
                    tokenized_message, "general_inquiry", prompts[AgentRole.KNOWLEDGE_RETRIEVAL],
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
                trace_id=trace_id,
                elapsed_ms=int(budget.elapsed_ms),
            )

            # ---------------------------------------------------------------
            # Phase 1b: IntentRouter execution-plan boundary (SPEC-1861)
            #
            # Replaces hardcoded escalation/co-pilot if/else with a
            # configurable routing engine. Default routing rules come
            # from agents.yaml; per-tenant overrides from TenantAgentOverlay.
            # All existing traffic defaults to CORE_PIPELINE.
            # ---------------------------------------------------------------
            from src.chat.pipeline.intent_router import IntentRouter, RouteTarget

            # Load tenant overlay store for IntentRouter routing decisions
            overlay_store: dict[str, dict] | None = None
            try:
                from src.multi_tenant.superadmin_api._agent_overlays import (
                    _get_tenant_overlays,
                )
                overlay_store = await _get_tenant_overlays(tenant_id) or None
            except Exception:
                logger.debug("Overlay store unavailable for routing", exc_info=True)

            # WI-4014: Hydrate binding cache from Cosmos before sync reads.
            # This is the async boundary before IntentRouter/dispatch sync code.
            try:
                from src.agents.plugins.bindings import SkillBindingService
                binding_svc = SkillBindingService.get_instance()
                if tenant_id not in binding_svc._loaded_tenants:
                    await binding_svc.load_tenant_bindings(tenant_id)
            except Exception:
                logger.debug("Binding cache hydration failed", exc_info=True)

            router = IntentRouter()
            route = router.resolve(
                tenant_id=tenant_id,
                intent=intent,
                confidence=confidence,
                team_member_role=team_member_role,
                target_agent_id=target_agent_id,
                overlay_store=overlay_store,
                tenant_tier=tier.value if hasattr(tier, "value") else str(tier),
                staff_domain_tags=staff_domain_tags,
            )
            trace.set_route_decision(
                route.target.value, route.agent_id, route.fallback_from,
            )

            if route.target == RouteTarget.ESCALATION:
                async for event in self._handle_escalation(
                    tenant_id, conversation_id, customer_message,
                    prompts[AgentRole.ESCALATION_HANDLER], budget, trace,
                ):
                    yield event
                return

            if route.target == RouteTarget.CO_PILOT:
                async for event in self._handle_co_pilot(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    customer_message=customer_message,
                    system_prompt=prompts.get(AgentRole.CO_PILOT, ""),
                    conversation_history=conversation_history or [],
                    team_member_role=team_member_role or "admin",
                    budget=budget,
                    trace=trace,
                    trace_id=trace_id,
                ):
                    yield event
                return

            if route.target == RouteTarget.PEER_AGENT:
                async for event in self._handle_peer_agent(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    customer_message=customer_message,
                    agent_id=route.agent_id or "",
                    skill_id=route.skill_id,
                    budget=budget,
                    trace=trace,
                    trace_id=trace_id,
                ):
                    yield event
                return

            if route.target == RouteTarget.ERROR:
                # Explicit target_agent_id verification failed (SPEC-1862)
                error_msg = (
                    f"Unable to connect to agent '{route.agent_id}': "
                    f"{route.error_reason or 'verification failed'}. "
                    "Please check agent availability and your access permissions."
                )
                yield token_event(error_msg, sequence=0)
                yield done_event(conversation_id, 0, trace_id=trace_id)
                return

            # CORE_PIPELINE — continue standard KR→RG→Critic flow

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
                trace_id=trace_id,
                elapsed_ms=int(budget.elapsed_ms),
            )

            # ---------------------------------------------------------------
            # Phase 3: Response Generation (streamed)
            # ---------------------------------------------------------------
            logger.info(
                "RG input: conv=%s intent=%s knowledge_len=%d sources=%d",
                conversation_id, intent,
                len(knowledge_context), len(sources),
            )
            yield stage_event("response-generator", "started", trace_id=trace_id, elapsed_ms=int(budget.elapsed_ms))
            rg_start = time.monotonic()

            full_response = ""
            sequence = 0

            try:
                async for chunk in self._call_response_generator_stream(
                    customer_message=tokenized_message,
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
                trace_id=trace_id,
                elapsed_ms=int(budget.elapsed_ms),
            )

            # ---------------------------------------------------------------
            # Phase 4: Critic validation (stream-then-validate, Decision UI-5)
            # ---------------------------------------------------------------
            yield stage_event("critic-supervisor", "started", trace_id=trace_id, elapsed_ms=int(budget.elapsed_ms))

            # Extract KB article titles so Critic knows the response
            # was generated from legitimate product knowledge.
            knowledge_titles = [s.get("title", "") for s in sources if s.get("title")]

            approved, safe_text, critic_result = await self._validate_with_critic(
                tenant_id, conversation_id, full_response, tokenized_message, budget,
                knowledge_titles=knowledge_titles,
            )

            # SPEC-1544: Detokenize PII in the response after Critic validation
            safe_text = pii_tokenizer.detokenize(
                safe_text, conversation_id, tenant_id,
            )

            trace.set_critic_result(
                verdict=critic_result.verdict.value if critic_result.verdict else "unavailable",
                flags=critic_result.flags,
                latency_ms=critic_result.latency_ms,
            )

            yield stage_event(
                "critic-supervisor", "completed",
                latency_ms=int(critic_result.latency_ms),
                trace_id=trace_id,
                elapsed_ms=int(budget.elapsed_ms),
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
                        **({"quality_experiment_variant": quality_experiment_variant,
                            "quality_experiment_id": quality_experiment_id}
                           if quality_experiment_variant else {}),
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
            self._create_background_task(
                self._fire_analytics(
                    tenant_id, conversation_id, intent, budget, trace,
                ),
                name=f"analytics-{conversation_id}",
            )

            # Build and store decision trace
            decision_trace = trace.build()

            # SPEC-1531: Persist pipeline trace on conversation metadata
            pipeline_trace = {
                "trace_id": trace_id,
                "stages": [
                    {
                        "stage": s.stage,
                        "elapsed_ms": int(s.elapsed_ms),
                        "succeeded": s.succeeded,
                    }
                    for s in budget.stages
                ],
                "total_latency_ms": int(budget.elapsed_ms),
                "intent": intent,
                "confidence": confidence,
                "critic_passed": approved,
                "model_used": response_model,
                "route_target": route.target.value,
                "route_agent_id": route.agent_id,
            }
            try:
                await self._session.update_conversation_metadata(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    metadata={"pipeline_trace": pipeline_trace},
                )
            except Exception:
                logger.debug("Failed to persist pipeline trace", exc_info=True)

            # SPEC-1855: Emit invocation events for each pipeline stage
            try:
                from src.agents.plugins.events import emit_invocation
                root_event_id = None
                for stg in budget.stages:
                    evt = emit_invocation(
                        trace_id=trace_id,
                        target_agent_id=stg.stage,
                        tenant_id=tenant_id,
                        conversation_id=conversation_id,
                        invoker="system" if root_event_id is None else "orchestrator",
                        parent_event_id=root_event_id,
                        latency_ms=stg.elapsed_ms,
                        result_class="success" if stg.succeeded else "error",
                    )
                    if root_event_id is None:
                        root_event_id = evt.event_id
            except Exception:
                logger.debug("Failed to emit invocation events", exc_info=True)

            logger.debug(
                "Pipeline complete: conv=%s intent=%s critic=%s latency=%.0fms trace=%s",
                conversation_id, intent, approved, budget.elapsed_ms, trace_id,
            )

            # Final turn count from the session
            state = await self._session.get_conversation(tenant_id, conversation_id)
            yield done_event(
                conversation_id,
                state.turn_count,
                trace_id=trace_id,
                total_latency_ms=int(budget.elapsed_ms),
            )

        except PipelineTimeoutError as exc:
            pipeline_span.set_attribute("pipeline.error", "timeout")
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
            pipeline_span.set_attribute("pipeline.error", "service_unavailable")
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
            pipeline_span.set_attribute("pipeline.error", type(exc).__name__)
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

        finally:
            # SPEC-1541: End the root pipeline span
            pipeline_span.set_attribute("pipeline.total_latency_ms", int(budget.elapsed_ms))
            pipeline_span.end()

    # -------------------------------------------------------------------
    # Co-pilot routing (SPEC-1557 / SPEC-1558)
    # -------------------------------------------------------------------

    async def _handle_peer_agent(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        agent_id: str,
        skill_id: str | None,
        budget: "PipelineTimeoutBudget",
        trace: "DecisionTraceBuilder",
        trace_id: str | None = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Route a customer message to a peer agent via binding-enforced dispatch.

        Follows the co-pilot handler pattern (SPEC-1861 / ADR-003):
        stage_event -> dispatch_with_binding -> token_event -> session ->
        agents_invoked -> invocation events -> analytics -> done_event.

        conversation_type stays 'customer' (Codex correction: route info
        is recorded in pipeline_trace and invocation events only).
        """
        yield stage_event(
            agent_id, "started",
            trace_id=trace_id,
            elapsed_ms=int(budget.elapsed_ms),
        )

        try:
            from src.agents.plugins.dispatch import PluginDispatcher
            from src.agents.plugins.events import emit_invocation

            dispatcher = PluginDispatcher()
            effective_skill = skill_id or ""

            result = await budget.execute_with_budget(
                agent_id,
                dispatcher.dispatch_with_binding(
                    tool_name=effective_skill,
                    arguments={"message": customer_message},
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    skill_id=effective_skill,
                    conversation_id=conversation_id,
                ),
            )

            response = ""
            model_used = ""
            if result.error:
                emit_invocation(
                    trace_id=trace_id,
                    invoker="intent-router",
                    target_agent_id=agent_id,
                    skill_id=effective_skill,
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    result_class="denied" if "denied" in (result.error or "") else "error",
                    policy_verdict=result.metadata.get("policy_verdict", "error"),
                    error_detail=result.error,
                    latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
                )
                logger.warning(
                    "Peer agent %s dispatch failed: %s", agent_id, result.error,
                )
                response = (
                    "I wasn't able to connect to a specialized agent for your request. "
                    "Let me help you with our standard service instead."
                )
            else:
                response = result.result.get("response", "") if result.result else ""
                model_used = result.result.get("model", "") if result.result else ""
                emit_invocation(
                    trace_id=trace_id,
                    invoker="intent-router",
                    target_agent_id=agent_id,
                    skill_id=effective_skill,
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    result_class="success",
                    policy_verdict="allowed",
                    latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
                )

            trace.add_stage(
                agent_id,
                model=model_used,
                latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
            )

            yield stage_event(
                agent_id, "completed",
                trace_id=trace_id,
                elapsed_ms=int(budget.elapsed_ms),
            )

            yield token_event(response, sequence=0)

            # Store response first to get message_id for validated_event
            message_id = await self._session.add_ai_message(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                content=response,
                agents_invoked=[agent_id],
                model_used=model_used,
                critic_passed=None,
            )

            yield validated_event(conversation_id, message_id or "")

            # Do NOT patch conversation_type — stays 'customer' (Codex P1 correction)
            # Route info is in pipeline_trace and invocation events only.

            # Persist pipeline_trace for this routed branch
            try:
                peer_trace = {
                    "trace_id": trace_id,
                    "stages": [
                        {"stage": s.stage, "elapsed_ms": int(s.elapsed_ms), "succeeded": s.succeeded}
                        for s in budget.stages
                    ],
                    "total_latency_ms": int(budget.elapsed_ms),
                    "route_target": "peer_agent",
                    "route_agent_id": agent_id,
                    "model_used": model_used,
                }
                await self._session.update_conversation_metadata(
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    metadata={"pipeline_trace": peer_trace},
                )
            except Exception:
                logger.debug("Failed to persist peer-agent pipeline_trace", exc_info=True)

            # Fire analytics
            self._create_background_task(
                self._fire_analytics(
                    tenant_id, conversation_id, "customer",
                    budget, trace,
                ),
                name=f"analytics-peer-{agent_id}-{conversation_id}",
            )

            # turn_count incremented by add_ai_message; retrieve from session
            turn_count = 0
            try:
                conv = await self._session.get_conversation(tenant_id, conversation_id)
                turn_count = conv.turn_count
            except Exception:
                pass

            yield done_event(
                conversation_id, turn_count,
                trace_id=trace_id,
                total_latency_ms=int(budget.elapsed_ms),
            )

        except PipelineTimeoutError:
            raise

        except Exception as exc:
            logger.warning(
                "Peer agent %s failed: conv=%s error=%s",
                agent_id, conversation_id, exc,
            )
            try:
                from src.agents.plugins.events import emit_invocation
                emit_invocation(
                    trace_id=trace_id,
                    invoker="intent-router",
                    target_agent_id=agent_id,
                    skill_id=skill_id or "",
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    result_class="error",
                    error_detail=str(exc),
                )
            except Exception:
                pass
            fallback = (
                "I encountered an issue connecting to a specialized agent. "
                "Please try again in a moment."
            )
            yield token_event(fallback, sequence=0)
            yield done_event(conversation_id, 0, trace_id=trace_id)

    async def _handle_co_pilot(
        self,
        tenant_id: str,
        conversation_id: str,
        customer_message: str,
        system_prompt: str,
        conversation_history: list[dict[str, str]],
        team_member_role: str,
        budget: "PipelineTimeoutBudget",
        trace: "DecisionTraceBuilder",
        trace_id: str | None = None,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Route an admin team member message to the Co-pilot agent.

        The Co-pilot performs its own hybrid retrieval from the shared
        admin_documentation_vectors collection and generates a response.
        This bypasses the standard KR→RG→Critic pipeline entirely.

        Yields StreamEvent objects matching the SSE protocol so the
        client receives stage/token/done events as usual.
        """
        yield stage_event(
            "co-pilot", "started",
            trace_id=trace_id,
            elapsed_ms=int(budget.elapsed_ms),
        )

        try:
            copilot_result = await budget.execute_with_budget(
                "co-pilot",
                self._call_co_pilot(
                    message=customer_message,
                    system_prompt=system_prompt,
                    conversation_history=conversation_history,
                    team_member_role=team_member_role,
                ),
            )

            response = copilot_result.get("response", "")
            sources = copilot_result.get("sources", [])

            trace.add_stage(
                "co-pilot",
                model=copilot_result.get("model", "gpt-4o"),
                latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
                tokens_input=copilot_result.get("tokens_input", 0),
                tokens_output=copilot_result.get("tokens_output", 0),
            )

            yield stage_event(
                "co-pilot", "completed",
                trace_id=trace_id,
                elapsed_ms=int(budget.elapsed_ms),
            )

            # SPEC-1855: Emit invocation event for co-pilot path
            try:
                from src.agents.plugins.events import emit_invocation
                emit_invocation(
                    trace_id=trace_id,
                    target_agent_id="co-pilot",
                    tenant_id=tenant_id,
                    conversation_id=conversation_id,
                    invoker="system",
                    latency_ms=budget.stages[-1].elapsed_ms if budget.stages else 0,
                    result_class="success",
                )
            except Exception:
                logger.debug("Failed to emit co-pilot invocation event", exc_info=True)

            # Emit the response as a single validated token (non-streamed)
            yield token_event(response, sequence=0)
            yield validated_event(response, trace_id=trace_id)

            # Store the response in the session (SPEC-1557)
            await self._session.add_ai_message(
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                content=response,
                agents_invoked=["co-pilot"],
                model_used=copilot_result.get("model", "gpt-4o"),
                critic_passed=None,  # Co-pilot bypasses Critic
            )

            # Mark conversation as admin_assistance + non-billable (SPEC-1561)
            await self._session._repo.patch(
                tenant_id=tenant_id,
                document_id=conversation_id,
                operations=[
                    {"op": "set", "path": "/conversation_type", "value": "admin_assistance"},
                    {"op": "set", "path": "/is_billable", "value": False},
                ],
            )

            # Fire analytics for admin conversation tracking (SPEC-1561)
            self._create_background_task(
                self._fire_analytics(
                    tenant_id, conversation_id, "admin_assistance",
                    budget, trace,
                ),
                name=f"analytics-copilot-{conversation_id}",
            )

            yield done_event(trace_id=trace_id)

        except PipelineTimeoutError:
            # Re-raise so the outer execute() handler emits a proper
            # error_event with code=pipeline_timeout.
            raise

        except Exception as exc:
            logger.warning(
                "Co-pilot failed: conv=%s error=%s",
                conversation_id, exc,
            )
            fallback = (
                "I'm the Agent Red Co-pilot, but I encountered an issue. "
                "Please try again in a moment."
            )
            yield token_event(fallback, sequence=0)
            yield validated_event(fallback, trace_id=trace_id)
            yield done_event(trace_id=trace_id)

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
        """Load Layer 1 profile (cached) and Layer 2 memory context (per-turn).

        WI #138: Layer 1 profile is cached at conversation level to avoid
        repeated Cosmos DB reads. Layer 2 memory search is query-dependent
        and runs fresh each turn.
        """
        if not customer_id:
            return None

        # Layer 1: profile (cached per conversation — WI #138)
        cache_key = f"{tenant_id}:{customer_id}"
        if cache_key in self._profile_cache:
            profile = self._profile_cache[cache_key]
        else:
            try:
                profile = await self._profile_service.get_profile(tenant_id, customer_id)
                self._profile_cache[cache_key] = profile
            except Exception:
                logger.debug("Profile lookup failed for %s -- continuing without", customer_id, exc_info=True)
                self._profile_cache[cache_key] = None
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
                        exc_info=True,
                    )

        return profile
