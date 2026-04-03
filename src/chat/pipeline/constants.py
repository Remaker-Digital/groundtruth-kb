"""Pipeline constants, environment configuration, and error classification.

Contains USE_AGENT_CONTAINERS feature flag, agent HTTP endpoint URLs,
Azure OpenAI model deployment names, intent taxonomy, and the
_classify_openai_error() utility.

R10 refactoring — extracted from pipeline.py (session 39).
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# USE_AGENT_CONTAINERS controls whether the pipeline routes through AGNTCY
# agent containers (HTTP) or calls Azure OpenAI directly.
#
# Default: True — route through AGNTCY agent containers (SPEC-1534).
# SPEC-1802 / DCL-002 v4: Non-streaming agents use SLIM → NATS → HTTP(S) → 503.
# RG token streaming uses gateway in-process (intended production path).
# ---------------------------------------------------------------------------
USE_AGENT_CONTAINERS = os.environ.get(
    "USE_AGENT_CONTAINERS", "true"
).lower() == "true"

# Default agent URLs — dynamically derived from registry (SPEC-1852).
# Only used when USE_AGENT_CONTAINERS=true.
# Defaults use Azure Container Apps internal DNS naming convention.
# ADR-001: These are Tier 3 (HTTP) endpoints used when SLIM/NATS are unavailable.
# ADR-002: Each agent runs in a dedicated container.
_CAE_FQDN = os.environ.get("CONTAINER_APP_ENV_FQDN", "")
_INTERNAL_BASE = f"http://agent-red-{{name}}.internal.{_CAE_FQDN}:8080" if _CAE_FQDN else "http://localhost:8080"


def _build_agent_urls() -> dict[str, str]:
    """Build agent URL map from registry core agents."""
    try:
        from src.agents.plugins.registry import PluginAgentRegistry
        reg = PluginAgentRegistry.get_instance()
        agent_ids = reg.get_core_agent_ids()
    except Exception:
        # Fallback for early import / test contexts
        agent_ids = [
            "intent-classifier", "knowledge-retrieval", "response-generator",
            "escalation-handler", "analytics-collector", "critic-supervisor",
            "co-pilot",
        ]

    urls: dict[str, str] = {}
    for agent_id in agent_ids:
        env_key = "AGENT_" + agent_id.upper().replace("-", "_") + "_URL"
        urls[agent_id] = os.environ.get(
            env_key, _INTERNAL_BASE.format(name=agent_id)
        )
    return urls


AGENT_URLS: dict[str, str] = _build_agent_urls()


def get_critic_urls() -> list[str]:
    """Parse Critic/Supervisor URL(s) from config.

    P1-4: Supports comma-separated URLs for multi-replica failover.
    Single URL (no commas) returns a single-element list for backward
    compatibility.
    """
    raw = AGENT_URLS.get("critic-supervisor", "")
    return [u.strip() for u in raw.split(",") if u.strip()]


# Agent HTTP paths
AGENT_CLASSIFY_PATH = "/classify"
AGENT_RETRIEVE_PATH = "/retrieve"
AGENT_GENERATE_PATH = "/generate"
AGENT_GENERATE_STREAM_PATH = "/generate/stream"
AGENT_ESCALATE_PATH = "/escalate"
AGENT_ANALYTICS_PATH = "/collect"

# Escalation intent value from the Intent Classifier
ESCALATION_INTENT = "escalation"

# Admin assistance intent — routes authenticated team members to Co-pilot (SPEC-1558)
ADMIN_ASSISTANCE_INTENT = "admin_assistance"

# Azure OpenAI model deployment names (match aoai-agentred-eastus2 deployments)
AZURE_IC_MODEL = os.environ.get("AZURE_IC_MODEL", "gpt-4o-mini")
AZURE_RG_MODEL = os.environ.get("AZURE_RG_MODEL", "gpt-4o")
AZURE_CR_MODEL = os.environ.get("AZURE_CR_MODEL", "gpt-4o-mini")
AZURE_EMBEDDING_MODEL = os.environ.get(
    "AZURE_EMBEDDING_MODEL", "text-embedding-3-large"
)
AZURE_EMBEDDING_DIMENSIONS = 3072

# Intent classification taxonomy — the set of intents the IC can return.
# 18-intent taxonomy (SPEC-1558): AGNTCY upstream 17 + admin_assistance.
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
    "admin_assistance",
]


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
