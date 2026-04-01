"""Langfuse trace exporter — Lane 1 structural export.

SPEC-1874: Converts ResponseDecisionTrace to Langfuse trace format,
exporting only structural/metric fields. NO content-bearing fields
(no knowledge queries, titles, memory summaries, escalation reasons,
or raw message content).

Lane 1 exported fields:
    - trace_id, hashed conversation_id, hashed tenant_id
    - detected_intent, intent_confidence
    - route_target, route_agent_id, route_fallback_from
    - stage_attributions (stage, model, latency, tokens, cost, succeeded)
    - critic verdict, flags, latency
    - total_latency_ms
    - ab_variant, ab_experiment_id
    - knowledge_results_count (count only)
    - prompt_version_hash (system prompt template hash)

Controlled via LANGFUSE_ENABLED env var. Fire-and-forget from
orchestrator. Staging only.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.multi_tenant.response_explainability import ResponseDecisionTrace

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LANGFUSE_ENABLED = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
_HASH_SALT = os.getenv("LANGFUSE_HASH_SALT", "")

# ---------------------------------------------------------------------------
# Critic flag normalization (S251 Phase 0 — Codex P1 ZK boundary fix)
# ---------------------------------------------------------------------------
# Critic returns free-form flags that may echo customer text or KB content.
# Normalize to a closed set before export. Unknown flags become "other".
# Derived from Critic prompt violation categories + internal codes.

CRITIC_SAFE_FLAGS: frozenset[str] = frozenset({
    "pii_leakage",
    "secrets_exposure",
    "medical_advice",
    "legal_advice",
    "financial_advice",
    "hate_speech",
    "policy_contradiction",
    "tone_check",
    "off_topic",
    "factual_concern",
    "hallucination_risk",
    "safety_flag",
    "length_concern",
    "modified_verdict_without_text",
})

_FLAG_ALIASES: dict[str, str] = {
    "pii": "pii_leakage",
    "cross_customer": "pii_leakage",
    "secret": "secrets_exposure",
    "medical": "medical_advice",
    "legal": "legal_advice",
    "financial": "financial_advice",
    "hate": "hate_speech",
    "policy": "policy_contradiction",
    "tone": "tone_check",
    "hallucination": "hallucination_risk",
    "safety": "safety_flag",
    "length": "length_concern",
}


def _normalize_critic_flags(raw_flags: list[str]) -> list[str]:
    """Map free-form Critic flags to the closed safe set.

    Exact matches pass through. Substring aliases resolve next.
    Anything unrecognized becomes "other".
    """
    result: list[str] = []
    for flag in raw_flags:
        lower = flag.lower().strip()
        if lower in CRITIC_SAFE_FLAGS:
            result.append(lower)
            continue
        matched = False
        for alias, safe in _FLAG_ALIASES.items():
            if alias in lower:
                result.append(safe)
                matched = True
                break
        if not matched:
            result.append("other")
    return result

# Langfuse client singleton (lazy-initialised)
_langfuse_client: Any = None


def _get_client() -> Any:
    """Return the Langfuse client singleton, creating it on first call.

    Returns None if the SDK is not installed or configuration is missing.
    """
    global _langfuse_client
    if _langfuse_client is not None:
        return _langfuse_client

    try:
        from langfuse import Langfuse  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("langfuse package not installed — exporter disabled")
        return None

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "http://localhost:3000")

    if not public_key or not secret_key:
        logger.warning("LANGFUSE_PUBLIC_KEY or LANGFUSE_SECRET_KEY not set — exporter disabled")
        return None

    _langfuse_client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        host=host,
    )
    logger.info("Langfuse exporter initialised (host=%s)", host)
    return _langfuse_client


# ---------------------------------------------------------------------------
# Hashing helpers
# ---------------------------------------------------------------------------


def _hash_id(value: str) -> str:
    """One-way SHA-256 hash with salt. Irreversible.

    Returns empty string if LANGFUSE_HASH_SALT is not configured,
    which causes export_trace() to skip (fail-closed).
    """
    if not _HASH_SALT:
        return ""
    return hashlib.sha256(f"{_HASH_SALT}:{value}".encode()).hexdigest()[:16]


def _prompt_version_hash(system_prompt_template: str) -> str:
    """Hash the system prompt template to a version identifier."""
    return hashlib.sha256(system_prompt_template.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Lane 1 structural export
# ---------------------------------------------------------------------------

# Fields that must NEVER appear in Lane 1 export
_CONTENT_BEARING_FIELDS = frozenset({
    "knowledge_query",
    "knowledge_sources",  # individual source details (titles, matched_query)
    "memory_signals",     # chunk_summary, source_conversation_id
    "escalation_reason",
    "profile_factors_used",
    "profile_data_sources",
    "customer_id",
    "conversation_id",  # raw — only hashed version exported
    "tenant_id",        # raw — only hashed version exported
})


def build_lane1_payload(
    trace: ResponseDecisionTrace,
    *,
    system_prompt_template: str = "",
) -> dict[str, Any]:
    """Convert a ResponseDecisionTrace to a Lane 1 structural payload.

    Returns a flat dict suitable for Langfuse trace metadata.
    Content-bearing fields are excluded by design.
    """
    return {
        # Hashed identifiers
        "conversation_id_hash": _hash_id(trace.conversation_id),
        "tenant_id_hash": _hash_id(trace.tenant_id),
        # Intent classification
        "detected_intent": trace.detected_intent,
        "intent_confidence": trace.intent_confidence,
        # Routing decision
        "route_target": trace.route_target,
        "route_agent_id": trace.route_agent_id,
        "route_fallback_from": trace.route_fallback_from,
        # Stage attributions (structural only)
        "stage_attributions": [
            {
                "stage": sa.stage,
                "model": sa.model,
                "latency_ms": sa.latency_ms,
                "tokens_input": sa.tokens_input,
                "tokens_output": sa.tokens_output,
                "cost_estimate": sa.cost_estimate,
                "succeeded": getattr(sa, "succeeded", True),
            }
            for sa in trace.stage_attributions
        ],
        # Critic assessment (structural — flags normalized to closed enum)
        "critic_verdict": trace.critic.verdict,
        "critic_flags": _normalize_critic_flags(trace.critic.flags),
        "critic_latency_ms": trace.critic.latency_ms,
        # Timing
        "total_latency_ms": trace.total_latency_ms,
        # A/B testing
        "ab_variant": trace.ab_variant,
        "ab_experiment_id": trace.ab_experiment_id,
        # Knowledge (count only — no content)
        "knowledge_results_count": trace.knowledge_results_count,
        # Prompt version (hash only — no content)
        "prompt_version_hash": _prompt_version_hash(system_prompt_template)
        if system_prompt_template
        else None,
    }


def export_trace(
    trace: ResponseDecisionTrace,
    *,
    trace_id: str = "",
    system_prompt_template: str = "",
) -> None:
    """Export a ResponseDecisionTrace to Langfuse (Lane 1 structural only).

    Fire-and-forget: exceptions are logged and swallowed.
    No-op if LANGFUSE_ENABLED is false or client unavailable.
    """
    if not LANGFUSE_ENABLED:
        return

    if not _HASH_SALT:
        logger.warning(
            "LANGFUSE_HASH_SALT not set — Langfuse export disabled (fail-closed)"
        )
        return

    client = _get_client()
    if client is None:
        return

    try:
        payload = build_lane1_payload(
            trace,
            system_prompt_template=system_prompt_template,
        )

        tags = [
            f"intent:{payload['detected_intent']}",
            f"route:{payload['route_target']}",
            f"critic:{payload['critic_verdict']}",
        ]

        # Langfuse SDK v3: use start_as_current_observation context manager
        # (v2 client.trace() was removed in v3)
        with client.start_as_current_observation(
            as_type="span",
            name="agent-red-pipeline",
            trace_id=trace_id or None,
            metadata=payload,
            tags=tags,
        ) as root:
            # Create child spans for each pipeline stage
            for sa in payload["stage_attributions"]:
                with client.start_as_current_observation(
                    as_type="span",
                    name=sa["stage"],
                    metadata={
                        "model": sa["model"],
                        "tokens_input": sa["tokens_input"],
                        "tokens_output": sa["tokens_output"],
                        "cost_estimate": sa["cost_estimate"],
                        "succeeded": sa["succeeded"],
                    },
                ):
                    pass  # span auto-closes on context exit

        # Flush asynchronously (Langfuse SDK batches internally)
        client.flush()

        logger.debug(
            "Langfuse trace exported: trace_id=%s intent=%s latency=%.0fms",
            trace_id,
            payload["detected_intent"],
            payload["total_latency_ms"],
        )
    except Exception:
        logger.debug("Langfuse export failed (non-blocking)", exc_info=True)
