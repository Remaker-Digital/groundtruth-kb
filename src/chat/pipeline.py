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

        # Store tenant_id for knowledge retrieval (used by _call_knowledge_retrieval_direct)
        self._current_tenant_id = tenant_id

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
            knowledge_context = knowledge_result.get("context", "")
            sources = knowledge_result.get("sources", [])
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
                model=response_model,
            ):
                full_response += chunk
                sequence += 1
                yield token_event(chunk, sequence)

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
        """Call Azure OpenAI GPT-4o-mini for intent classification.

        Uses JSON mode to get structured output with intent and confidence.
        """
        if not self._openai_client:
            logger.warning(
                "No OpenAI client configured — returning general_inquiry default"
            )
            return {"intent": "general_inquiry", "confidence": 0.5, "model": AZURE_IC_MODEL}

        intent_list = ", ".join(INTENT_TAXONOMY)
        ic_user_prompt = (
            f"Classify the following customer message into exactly one intent.\n"
            f"Valid intents: {intent_list}\n\n"
            f"Respond with a JSON object containing:\n"
            f'- "intent": one of the valid intents listed above\n'
            f'- "confidence": a number between 0.0 and 1.0\n'
            f'- "reasoning": a brief explanation (1 sentence)\n\n'
            f"Customer message: {message}"
        )

        response = await self._openai_client.chat.completions.create(
            model=AZURE_IC_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ic_user_prompt},
            ],
            temperature=0.0,
            max_tokens=150,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {}

        intent = parsed.get("intent", "general_inquiry")
        if intent not in INTENT_TAXONOMY:
            intent = "general_inquiry"

        return {
            "intent": intent,
            "confidence": float(parsed.get("confidence", 0.5)),
            "model": AZURE_IC_MODEL,
            "tokens_input": response.usage.prompt_tokens if response.usage else 0,
            "tokens_output": response.usage.completion_tokens if response.usage else 0,
        }

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
        """Retrieve knowledge using text search on the knowledge base.

        Searches the KnowledgeBaseRepository by matching the message
        against active knowledge base entries. Falls back to empty
        context when no KB repo is configured.

        Note: This uses Cosmos DB text search (CONTAINS) rather than
        vector search. Vector search is used for Layer 2 conversation
        memory. Knowledge base entries are structured documents where
        text search is sufficient and avoids the embedding round-trip.
        """
        if not self._kb_repo:
            logger.warning(
                "No KnowledgeBaseRepository configured — "
                "returning empty knowledge context"
            )
            return {
                "context": "",
                "sources": [],
                "model": AZURE_EMBEDDING_MODEL,
            }

        # Get the tenant_id from the current execution context
        # (it's passed through the pipeline via the session)
        tenant_id = getattr(self, "_current_tenant_id", None)
        if not tenant_id:
            return {"context": "", "sources": [], "model": AZURE_EMBEDDING_MODEL}

        try:
            # Search by keyword-based matching: extract key terms from message
            # and search active KB entries
            entries = await self._kb_repo.list_active(tenant_id)

            if not entries:
                return {"context": "", "sources": [], "model": AZURE_EMBEDDING_MODEL}

            # Score entries by simple keyword relevance
            message_lower = message.lower()
            scored: list[tuple[float, dict[str, Any]]] = []

            for entry in entries:
                title = (entry.get("title") or "").lower()
                content = (entry.get("content") or "").lower()
                tags = [t.lower() for t in (entry.get("tags") or [])]

                # Simple relevance scoring
                score = 0.0
                message_words = set(message_lower.split())

                # Title match (highest weight)
                for word in message_words:
                    if len(word) > 2 and word in title:
                        score += 3.0

                # Tag match (high weight)
                for word in message_words:
                    if word in tags:
                        score += 2.0

                # Content match (moderate weight)
                for word in message_words:
                    if len(word) > 3 and word in content:
                        score += 1.0

                # Intent match boost
                intent_lower = intent.lower().replace("_", " ")
                for iword in intent_lower.split():
                    if len(iword) > 2 and (iword in title or iword in content):
                        score += 1.5

                if score > 0:
                    scored.append((score, entry))

            # Sort by score descending, take top 5
            scored.sort(key=lambda x: x[0], reverse=True)
            top_entries = scored[:5]

            if not top_entries:
                return {"context": "", "sources": [], "model": AZURE_EMBEDDING_MODEL}

            # Build context string from matched entries
            context_parts: list[str] = []
            sources: list[dict[str, Any]] = []

            for relevance, entry in top_entries:
                title = entry.get("title", "Untitled")
                content = entry.get("content", "")
                entry_type = entry.get("entry_type", "")

                # Truncate content to ~500 chars per entry
                if len(content) > 500:
                    content = content[:500] + "..."

                context_parts.append(f"[{entry_type.upper()}] {title}\n{content}")
                sources.append({
                    "id": entry.get("id", ""),
                    "title": title,
                    "score": round(relevance / 10.0, 2),  # Normalize to 0-1
                    "type": entry_type,
                })

            return {
                "context": "\n\n---\n\n".join(context_parts),
                "sources": sources,
                "model": "text-search",
                "tokens_input": 0,
                "tokens_output": 0,
            }

        except Exception as exc:
            logger.warning(
                "Knowledge retrieval failed: %s — returning empty context", exc,
            )
            return {"context": "", "sources": [], "model": AZURE_EMBEDDING_MODEL}

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
    ) -> AsyncGenerator[str, None]:
        """Stream response from Azure OpenAI directly.

        Uses the Azure OpenAI SDK's streaming chat completion API.
        The system_prompt (assembled by SystemPromptBuilder) is passed
        as a separate system message to enable Azure OpenAI's automatic
        prompt prefix caching (WI #135).
        """
        if not self._openai_client:
            logger.warning(
                "No OpenAI client configured — yielding fallback response"
            )
            yield "I'm sorry, but I'm unable to generate a response right now. Please try again shortly."
            return

        # Build user message with knowledge context
        user_content_parts: list[str] = []
        if knowledge_context:
            user_content_parts.append(
                f"RELEVANT KNOWLEDGE:\n{knowledge_context}\n"
            )
        user_content_parts.append(
            f"CUSTOMER INTENT: {intent}\n\n"
            f"CUSTOMER MESSAGE: {customer_message}"
        )
        user_content = "\n".join(user_content_parts)

        remaining_ms = budget.remaining_ms
        # Azure OpenAI SDK uses seconds for timeout
        timeout_seconds = max(0.5, remaining_ms / 1000)

        stream = await self._openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
            max_tokens=1024,
            stream=True,
            timeout=timeout_seconds,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

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
    ) -> tuple[bool, str, Any]:
        """Validate response using Azure OpenAI GPT-4o-mini directly.

        Implements the same fail-closed semantics as CriticPolicy:
        - Model approves → deliver response
        - Model rejects → block + use fallback
        - Call fails → block + use fallback (fail-closed)

        The Critic system prompt is the immutable platform base from
        SystemPromptBuilder — no tenant config injected (Decision #23).
        """
        from src.multi_tenant.critic_policy import CriticBlockReason, CriticResult, CriticVerdict

        request_id = f"critic-direct-{conversation_id}-{int(time.time() * 1000)}"
        start_time = time.monotonic()

        try:
            critic_user_prompt = (
                "Review the following AI-generated customer service response.\n\n"
                f"CUSTOMER MESSAGE:\n{customer_message}\n\n"
                f"AI RESPONSE:\n{response_text}\n\n"
                "Evaluate this response and return a JSON object with:\n"
                '- "verdict": "approved" if safe to deliver, "rejected" if unsafe, '
                '"modified" if approved with changes\n'
                '- "flags": array of any safety concerns (e.g., "potential_hallucination", '
                '"pii_detected", "brand_safety_risk")\n'
                '- "modified_response": if verdict is "modified", provide the corrected text\n'
                '- "reasoning": brief explanation of your decision\n\n'
                "Apply the safety rules from your system prompt strictly."
            )

            # Get the immutable Critic system prompt
            from src.multi_tenant.system_prompt_builder import _PLATFORM_BASE
            critic_system_prompt = _PLATFORM_BASE.get(
                AgentRole.CRITIC_SUPERVISOR, ""
            )

            response = await self._openai_client.chat.completions.create(
                model=AZURE_CR_MODEL,
                messages=[
                    {"role": "system", "content": critic_system_prompt},
                    {"role": "user", "content": critic_user_prompt},
                ],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_object"},
            )

            elapsed = (time.monotonic() - start_time) * 1000
            content = response.choices[0].message.content or "{}"

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {}

            verdict_str = parsed.get("verdict", "rejected")
            try:
                verdict = CriticVerdict(verdict_str)
            except ValueError:
                verdict = CriticVerdict.REJECTED

            approved = verdict in (CriticVerdict.APPROVED, CriticVerdict.MODIFIED)
            flags = parsed.get("flags", [])
            modified_response = parsed.get("modified_response")

            if verdict == CriticVerdict.MODIFIED and not modified_response:
                approved = False
                flags.append("modified_verdict_without_text")

            block_reason = None if approved else CriticBlockReason.REJECTED

            result = CriticResult(
                approved=approved,
                verdict=verdict,
                block_reason=block_reason,
                flags=flags,
                modified_response=modified_response if approved else None,
                latency_ms=elapsed,
                critic_instance="azure-openai-direct",
                request_id=request_id,
            )

            if approved:
                safe_text = modified_response or response_text
                return True, safe_text, result
            else:
                logger.warning(
                    "Critic (direct) rejected response: tenant=%s conv=%s "
                    "flags=%s",
                    tenant_id, conversation_id, flags,
                )
                return False, SAFE_FALLBACK_MESSAGE, result

        except Exception as exc:
            # Fail-closed: any error means block the response
            elapsed = (time.monotonic() - start_time) * 1000
            logger.warning(
                "Critic (direct) call failed — BLOCKING response "
                "(fail-closed): tenant=%s conv=%s error=%s",
                tenant_id, conversation_id, exc,
            )
            result = CriticResult(
                approved=False,
                verdict=None,
                block_reason=CriticBlockReason.ERROR,
                flags=["critic_direct_error"],
                modified_response=None,
                latency_ms=elapsed,
                critic_instance="azure-openai-direct",
                request_id=request_id,
            )
            return False, SAFE_FALLBACK_MESSAGE, result

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
        """Route escalation to Azure OpenAI directly or AGNTCY container."""
        if USE_AGENT_CONTAINERS:
            return await self._call_escalation_handler_http(message, system_prompt)
        return await self._call_escalation_handler_direct(message, system_prompt)

    async def _call_escalation_handler_direct(
        self,
        message: str,
        system_prompt: str,
    ) -> dict[str, Any]:
        """Evaluate escalation context using Azure OpenAI GPT-4o-mini."""
        if not self._openai_client:
            return {"reason": "Customer requested human agent", "model": AZURE_IC_MODEL}

        esc_user_prompt = (
            "Analyze the following customer message and determine the "
            "escalation reason. Respond with a JSON object containing:\n"
            '- "reason": a clear, concise summary of why the customer needs '
            "human assistance (1-2 sentences)\n"
            '- "urgency": "low", "medium", or "high"\n'
            '- "context_summary": brief summary for the human agent\n\n'
            f"Customer message: {message}"
        )

        try:
            response = await self._openai_client.chat.completions.create(
                model=AZURE_IC_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": esc_user_prompt},
                ],
                temperature=0.0,
                max_tokens=200,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content or "{}"
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                parsed = {}

            return {
                "reason": parsed.get("reason", "Customer requested human agent"),
                "urgency": parsed.get("urgency", "medium"),
                "context_summary": parsed.get("context_summary", ""),
                "model": AZURE_IC_MODEL,
            }
        except Exception:
            return {"reason": "Customer requested human agent", "model": AZURE_IC_MODEL}

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

        When USE_AGENT_CONTAINERS is false, analytics are logged locally
        instead of sending to the AGNTCY analytics container.
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
                # Log analytics locally when not using agent containers
                logger.info(
                    "Analytics: conv=%s intent=%s stages=%d latency=%.0fms",
                    conversation_id, intent, len(budget.stages),
                    budget.elapsed_ms,
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
