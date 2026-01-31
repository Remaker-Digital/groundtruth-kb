"""Response explainability — per-response decision trace.

Work Item #86 (Decision #28+/32): Captures the full decision context for
each AI response in the pipeline, enabling merchant transparency, audit
compliance, and debugging.

The decision trace records:
    - Profile factors used (Layer 1)
    - Knowledge sources matched with relevance scores (Knowledge Retrieval)
    - Memory signals (Layer 2-3 contributions)
    - A/B variant active (future Smart Rollout)
    - Tenant config overrides applied
    - Model attribution per pipeline stage
    - Critic assessment (verdict, flags, modifications)
    - Pipeline timing (per-stage latency)

Storage: per-conversation in Cosmos DB (conversations collection).
Access: merchant dashboard, CSV export, audit trail.

Architecture references:
    - Decision #28+: Response explainability framework
    - Decision #32: Test cases and validation framework
    - SystemPromptBuilder.explain(): Prompt composition trace (upstream)

Dependencies:
    - system_prompt_builder.py: SystemPromptBuilder.explain()
    - cosmos_schema.py: CustomerProfileDocument, ConversationDocument

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Decision trace models
# ---------------------------------------------------------------------------


@dataclass
class KnowledgeSource:
    """A knowledge base entry matched during retrieval."""

    entry_id: str = ""
    entry_type: str = ""  # product | faq | policy | custom
    title: str = ""
    relevance_score: float = 0.0
    matched_query: str = ""


@dataclass
class MemorySignal:
    """A Layer 2-3 memory signal that contributed to the response."""

    layer: int = 2  # 2 = conversation history, 3 = learned patterns
    source_conversation_id: str = ""
    chunk_summary: str = ""
    similarity_score: float = 0.0
    signal_type: str = ""  # "prior_conversation" | "learned_pattern"


@dataclass
class CriticAssessment:
    """Critic/Supervisor evaluation result."""

    verdict: str = "unknown"  # "approved" | "rejected" | "modified" | "timeout" | "error"
    flags: list[str] = field(default_factory=list)
    modifications: list[str] = field(default_factory=list)
    latency_ms: float = 0.0


@dataclass
class StageAttribution:
    """Model attribution for a single pipeline stage."""

    stage: str = ""  # "intent_classifier", "knowledge_retrieval", etc.
    model: str = ""  # "gpt-4o-mini", "gpt-4o", "text-embedding-3-large"
    latency_ms: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    cost_estimate: float = 0.0  # Estimated cost in USD


@dataclass
class ResponseDecisionTrace:
    """Complete per-response decision trace (Decision #28+).

    Captures every factor that influenced a specific AI response.
    Stored per-conversation, accessible via merchant dashboard.

    This is the core data structure for the explainability framework.
    """

    # Identifiers
    conversation_id: str = ""
    tenant_id: str = ""
    customer_id: str = ""
    message_index: int = 0  # Which response in the conversation

    # Timestamp
    timestamp: str = ""

    # Layer 1: Profile factors
    profile_factors_used: list[str] = field(default_factory=list)
    profile_data_sources: list[str] = field(default_factory=list)
    profile_is_stale: bool = False
    profile_is_empty: bool = False

    # Knowledge retrieval
    knowledge_sources: list[KnowledgeSource] = field(default_factory=list)
    knowledge_query: str = ""
    knowledge_results_count: int = 0

    # Layer 2-3: Memory signals
    memory_signals: list[MemorySignal] = field(default_factory=list)
    memory_consent_status: str = ""  # "granted" | "denied" | "not_asked"
    memory_history_depth_days: int | None = None

    # A/B variant (future Smart Rollout — Phase 3)
    ab_variant: str | None = None
    ab_experiment_id: str | None = None

    # Tenant configuration
    config_version: int = 0
    config_overrides_applied: list[str] = field(default_factory=list)
    custom_instructions_present: bool = False

    # Model attribution (per pipeline stage)
    stage_attributions: list[StageAttribution] = field(default_factory=list)
    total_latency_ms: float = 0.0
    total_cost_estimate: float = 0.0

    # Critic assessment
    critic: CriticAssessment = field(default_factory=CriticAssessment)

    # Intent classification result
    detected_intent: str = ""
    intent_confidence: float = 0.0

    # Response metadata
    response_language: str = "en"
    was_escalated: bool = False
    escalation_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dict for storage.

        Converts nested dataclasses to dicts. Used when persisting
        the trace in the conversation document.
        """
        result: dict[str, Any] = {
            "conversation_id": self.conversation_id,
            "tenant_id": self.tenant_id,
            "customer_id": self.customer_id,
            "message_index": self.message_index,
            "timestamp": self.timestamp,
            "profile": {
                "factors_used": self.profile_factors_used,
                "data_sources": self.profile_data_sources,
                "is_stale": self.profile_is_stale,
                "is_empty": self.profile_is_empty,
            },
            "knowledge": {
                "query": self.knowledge_query,
                "results_count": self.knowledge_results_count,
                "sources": [
                    {
                        "entry_id": ks.entry_id,
                        "entry_type": ks.entry_type,
                        "title": ks.title,
                        "relevance_score": ks.relevance_score,
                    }
                    for ks in self.knowledge_sources
                ],
            },
            "memory": {
                "consent_status": self.memory_consent_status,
                "history_depth_days": self.memory_history_depth_days,
                "signals": [
                    {
                        "layer": ms.layer,
                        "source_conversation_id": ms.source_conversation_id,
                        "similarity_score": ms.similarity_score,
                        "signal_type": ms.signal_type,
                        "chunk_summary": ms.chunk_summary,
                    }
                    for ms in self.memory_signals
                ],
            },
            "config": {
                "version": self.config_version,
                "overrides_applied": self.config_overrides_applied,
                "custom_instructions_present": self.custom_instructions_present,
            },
            "pipeline": {
                "stages": [
                    {
                        "stage": sa.stage,
                        "model": sa.model,
                        "latency_ms": sa.latency_ms,
                        "tokens_input": sa.tokens_input,
                        "tokens_output": sa.tokens_output,
                        "cost_estimate": sa.cost_estimate,
                    }
                    for sa in self.stage_attributions
                ],
                "total_latency_ms": self.total_latency_ms,
                "total_cost_estimate": self.total_cost_estimate,
            },
            "critic": {
                "verdict": self.critic.verdict,
                "flags": self.critic.flags,
                "modifications": self.critic.modifications,
                "latency_ms": self.critic.latency_ms,
            },
            "intent": {
                "detected": self.detected_intent,
                "confidence": self.intent_confidence,
            },
            "response": {
                "language": self.response_language,
                "was_escalated": self.was_escalated,
                "escalation_reason": self.escalation_reason,
            },
        }

        # A/B variant (only if active)
        if self.ab_variant:
            result["ab_test"] = {
                "variant": self.ab_variant,
                "experiment_id": self.ab_experiment_id,
            }

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResponseDecisionTrace:
        """Deserialize from a stored dict."""
        trace = cls(
            conversation_id=data.get("conversation_id", ""),
            tenant_id=data.get("tenant_id", ""),
            customer_id=data.get("customer_id", ""),
            message_index=data.get("message_index", 0),
            timestamp=data.get("timestamp", ""),
        )

        # Profile
        profile = data.get("profile", {})
        trace.profile_factors_used = profile.get("factors_used", [])
        trace.profile_data_sources = profile.get("data_sources", [])
        trace.profile_is_stale = profile.get("is_stale", False)
        trace.profile_is_empty = profile.get("is_empty", False)

        # Knowledge
        knowledge = data.get("knowledge", {})
        trace.knowledge_query = knowledge.get("query", "")
        trace.knowledge_results_count = knowledge.get("results_count", 0)
        trace.knowledge_sources = [
            KnowledgeSource(**ks) for ks in knowledge.get("sources", [])
        ]

        # Memory
        memory = data.get("memory", {})
        trace.memory_consent_status = memory.get("consent_status", "")
        trace.memory_history_depth_days = memory.get("history_depth_days")
        trace.memory_signals = [
            MemorySignal(**ms) for ms in memory.get("signals", [])
        ]

        # Config
        config = data.get("config", {})
        trace.config_version = config.get("version", 0)
        trace.config_overrides_applied = config.get("overrides_applied", [])
        trace.custom_instructions_present = config.get("custom_instructions_present", False)

        # Pipeline
        pipeline = data.get("pipeline", {})
        trace.total_latency_ms = pipeline.get("total_latency_ms", 0.0)
        trace.total_cost_estimate = pipeline.get("total_cost_estimate", 0.0)
        trace.stage_attributions = [
            StageAttribution(**sa) for sa in pipeline.get("stages", [])
        ]

        # Critic
        critic = data.get("critic", {})
        trace.critic = CriticAssessment(
            verdict=critic.get("verdict", "unknown"),
            flags=critic.get("flags", []),
            modifications=critic.get("modifications", []),
            latency_ms=critic.get("latency_ms", 0.0),
        )

        # Intent
        intent = data.get("intent", {})
        trace.detected_intent = intent.get("detected", "")
        trace.intent_confidence = intent.get("confidence", 0.0)

        # Response
        response = data.get("response", {})
        trace.response_language = response.get("language", "en")
        trace.was_escalated = response.get("was_escalated", False)
        trace.escalation_reason = response.get("escalation_reason", "")

        # A/B
        ab_test = data.get("ab_test", {})
        trace.ab_variant = ab_test.get("variant")
        trace.ab_experiment_id = ab_test.get("experiment_id")

        return trace


# ---------------------------------------------------------------------------
# DecisionTraceBuilder — fluent builder for constructing traces
# ---------------------------------------------------------------------------


class DecisionTraceBuilder:
    """Fluent builder for constructing a ResponseDecisionTrace.

    Used during pipeline execution to incrementally build the trace
    as each stage completes.

    Usage:
        builder = DecisionTraceBuilder(conversation_id, tenant_id, customer_id)
        builder.set_profile_context(prompt_trace)
        builder.add_knowledge_source(entry_id, title, score)
        builder.add_memory_signal(layer=2, conv_id, similarity)
        builder.add_stage("response_generator", "gpt-4o", latency, tokens_in, tokens_out)
        builder.set_critic_result(verdict, flags)
        trace = builder.build()
    """

    def __init__(
        self,
        conversation_id: str,
        tenant_id: str,
        customer_id: str = "",
        message_index: int = 0,
    ) -> None:
        from datetime import datetime, timezone
        self._trace = ResponseDecisionTrace(
            conversation_id=conversation_id,
            tenant_id=tenant_id,
            customer_id=customer_id,
            message_index=message_index,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._start_time = time.monotonic()

    def set_profile_context(
        self,
        prompt_trace: dict[str, Any],
    ) -> DecisionTraceBuilder:
        """Set profile context from SystemPromptBuilder.explain() output."""
        self._trace.profile_data_sources = prompt_trace.get(
            "customer_context_sources", [],
        )
        self._trace.profile_factors_used = prompt_trace.get(
            "tenant_config_fields", [],
        )
        self._trace.config_version = prompt_trace.get("config_version", 0)
        self._trace.custom_instructions_present = prompt_trace.get(
            "custom_instructions_present", False,
        )
        self._trace.config_overrides_applied = prompt_trace.get(
            "tenant_config_fields", [],
        )
        self._trace.memory_history_depth_days = prompt_trace.get(
            "history_depth_days",
        )
        return self

    def set_profile_state(
        self,
        is_stale: bool = False,
        is_empty: bool = False,
    ) -> DecisionTraceBuilder:
        """Record profile freshness state."""
        self._trace.profile_is_stale = is_stale
        self._trace.profile_is_empty = is_empty
        return self

    def set_consent(
        self,
        consent_status: str,
    ) -> DecisionTraceBuilder:
        """Record customer consent status."""
        self._trace.memory_consent_status = consent_status
        return self

    def add_knowledge_source(
        self,
        entry_id: str,
        title: str,
        relevance_score: float,
        entry_type: str = "",
        matched_query: str = "",
    ) -> DecisionTraceBuilder:
        """Record a knowledge base source used in the response."""
        self._trace.knowledge_sources.append(KnowledgeSource(
            entry_id=entry_id,
            entry_type=entry_type,
            title=title,
            relevance_score=relevance_score,
            matched_query=matched_query,
        ))
        self._trace.knowledge_results_count = len(self._trace.knowledge_sources)
        return self

    def set_knowledge_query(self, query: str) -> DecisionTraceBuilder:
        """Record the query sent to knowledge retrieval."""
        self._trace.knowledge_query = query
        return self

    def add_memory_signal(
        self,
        layer: int,
        source_conversation_id: str = "",
        similarity_score: float = 0.0,
        signal_type: str = "prior_conversation",
        chunk_summary: str = "",
    ) -> DecisionTraceBuilder:
        """Record a memory signal from Layer 2 or Layer 3."""
        self._trace.memory_signals.append(MemorySignal(
            layer=layer,
            source_conversation_id=source_conversation_id,
            similarity_score=similarity_score,
            signal_type=signal_type,
            chunk_summary=chunk_summary,
        ))
        return self

    def add_stage(
        self,
        stage: str,
        model: str,
        latency_ms: float,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_estimate: float = 0.0,
    ) -> DecisionTraceBuilder:
        """Record model attribution for a pipeline stage."""
        self._trace.stage_attributions.append(StageAttribution(
            stage=stage,
            model=model,
            latency_ms=latency_ms,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_estimate=cost_estimate,
        ))
        return self

    def set_intent(
        self,
        intent: str,
        confidence: float = 0.0,
    ) -> DecisionTraceBuilder:
        """Record intent classification result."""
        self._trace.detected_intent = intent
        self._trace.intent_confidence = confidence
        return self

    def set_critic_result(
        self,
        verdict: str,
        flags: list[str] | None = None,
        modifications: list[str] | None = None,
        latency_ms: float = 0.0,
    ) -> DecisionTraceBuilder:
        """Record Critic/Supervisor assessment."""
        self._trace.critic = CriticAssessment(
            verdict=verdict,
            flags=flags or [],
            modifications=modifications or [],
            latency_ms=latency_ms,
        )
        return self

    def set_escalation(
        self,
        escalated: bool,
        reason: str = "",
    ) -> DecisionTraceBuilder:
        """Record whether the response was escalated."""
        self._trace.was_escalated = escalated
        self._trace.escalation_reason = reason
        return self

    def set_language(self, language: str) -> DecisionTraceBuilder:
        """Record response language."""
        self._trace.response_language = language
        return self

    def build(self) -> ResponseDecisionTrace:
        """Finalize and return the decision trace.

        Computes total latency and cost from stage attributions.
        """
        elapsed = (time.monotonic() - self._start_time) * 1000
        self._trace.total_latency_ms = elapsed

        self._trace.total_cost_estimate = sum(
            sa.cost_estimate for sa in self._trace.stage_attributions
        )

        return self._trace
