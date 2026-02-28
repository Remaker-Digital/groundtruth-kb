# Agent Red Customer Experience — AGNTCY SDK Integration Layer
#
# This module provides Agent Red's integration with the AGNTCY platform SDK.
# It wraps AgntcyFactory as a singleton and provides transport/protocol creation
# for the 6-agent pipeline architecture.
#
# Phase 1 deliverable: SDK adoption + SLIM transport foundation.
# Phase 2 will use this module to decompose pipeline.py into containerized agents.
# Phase 3 will use create_mcp_client() for external tool integrations.
#
# AGNTCY SDK source: https://github.com/agntcy/app-sdk
# AGNTCY platform wiki: https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service/wiki
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Any

# AGNTCY SDK imports — wrapped in try/except per project lesson.
try:
    from agntcy_app_sdk.factory import AgntcyFactory, ProtocolTypes, TransportTypes
except ImportError:
    AgntcyFactory = None  # type: ignore[assignment,misc]
    ProtocolTypes = None  # type: ignore[assignment,misc]
    TransportTypes = None  # type: ignore[assignment,misc]

try:
    from agntcy_app_sdk.semantic.base import BaseAgentProtocol
except ImportError:
    BaseAgentProtocol = None  # type: ignore[assignment,misc]

try:
    from agntcy_app_sdk.semantic.message import Message
except ImportError:
    Message = None  # type: ignore[assignment,misc]

try:
    from agntcy_app_sdk.transport.base import BaseTransport
except ImportError:
    BaseTransport = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration from environment
# ---------------------------------------------------------------------------

# SLIM endpoint for agent-to-agent transport (Phase 2+)
SLIM_ENDPOINT = os.environ.get("AGNTCY_SLIM_ENDPOINT", "")

# NATS endpoint for fallback transport
NATS_ENDPOINT = os.environ.get("AGNTCY_NATS_ENDPOINT", "nats://localhost:4222")

# SLIM routable name prefix (org/namespace format per SDK convention)
SLIM_ORG_NAMESPACE = os.environ.get(
    "AGNTCY_SLIM_ORG_NAMESPACE", "remaker-digital/agent-red"
)

# Transport selection: "slim" (preferred) or "nats" (fallback)
TRANSPORT_TYPE = os.environ.get("AGNTCY_TRANSPORT_TYPE", "slim").lower()

# mTLS configuration for SLIM transport
SLIM_TLS_INSECURE = os.environ.get("AGNTCY_SLIM_TLS_INSECURE", "false").lower() == "true"
SLIM_SHARED_SECRET = os.environ.get("AGNTCY_SLIM_SHARED_SECRET", "")

# Enable SDK tracing (Phase 5 will wire this to OpenTelemetry)
ENABLE_SDK_TRACING = os.environ.get("AGNTCY_ENABLE_TRACING", "false").lower() == "true"


class AgentTopic(str, Enum):
    """Agent topic identifiers matching AGNTCY upstream convention.

    These map 1:1 to the AgentRole enum in system_prompt_builder.py and to
    the NATS topic suffixes in nats_isolation.py. They serve as the canonical
    agent identifiers for A2A and MCP protocol addressing.
    """

    INTENT_CLASSIFIER = "intent-classifier"
    KNOWLEDGE_RETRIEVAL = "knowledge-retrieval"
    RESPONSE_GENERATOR = "response-generator"
    ESCALATION_HANDLER = "escalation-handler"
    ANALYTICS_COLLECTOR = "analytics-collector"
    CRITIC_SUPERVISOR = "critic-supervisor"


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

_factory: AgntcyFactory | None = None
_transport: BaseTransport | None = None


def get_agntcy_factory() -> AgntcyFactory:
    """Return the singleton AgntcyFactory instance.

    The factory provides:
      - create_transport(transport, name, endpoint, ...) → BaseTransport
      - create_client(protocol, agent_topic, transport, ...) → protocol client
      - create_app_session(max_sessions) → AppSession
      - registered_protocols() → list of available protocols
      - registered_transports() → list of available transports

    Raises RuntimeError if the SDK is not installed or import fails.
    """
    global _factory
    if _factory is None:
        _factory = AgntcyFactory(
            name="AgentRedFactory",
            enable_tracing=ENABLE_SDK_TRACING,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
        logger.info(
            "AgntcyFactory initialized (tracing=%s, protocols=%s, transports=%s)",
            ENABLE_SDK_TRACING,
            _factory.registered_protocols(),
            _factory.registered_transports(),
        )
    return _factory


def get_default_transport() -> BaseTransport:
    """Return the singleton default transport for agent-to-agent communication.

    Uses SLIM transport if AGNTCY_SLIM_ENDPOINT is configured, otherwise falls
    back to NATS transport.

    This transport is shared across all agent protocol clients. Individual agents
    use different topics (AgentTopic) on the same transport.

    Returns None-safe: callers should check if transport is available before use.
    Phase 1 may not have SLIM endpoint configured; Phase 2 requires it.
    """
    global _transport
    if _transport is not None:
        return _transport

    factory = get_agntcy_factory()

    if TRANSPORT_TYPE == "slim" and SLIM_ENDPOINT:
        _transport = factory.create_transport(
            transport="SLIM",
            name=f"{SLIM_ORG_NAMESPACE}/gateway",
            endpoint=SLIM_ENDPOINT,
            tls_insecure=SLIM_TLS_INSECURE,
            shared_secret_identity=SLIM_SHARED_SECRET or None,
        )
        logger.info(
            "SLIM transport created (endpoint=%s, tls_insecure=%s)",
            SLIM_ENDPOINT,
            SLIM_TLS_INSECURE,
        )
    elif NATS_ENDPOINT:
        _transport = factory.create_transport(
            transport="NATS",
            name="agent-red-nats",
            endpoint=NATS_ENDPOINT,
        )
        logger.info("NATS transport created (endpoint=%s)", NATS_ENDPOINT)
    else:
        logger.warning(
            "No AGNTCY transport configured. Set AGNTCY_SLIM_ENDPOINT or "
            "AGNTCY_NATS_ENDPOINT. Agent-to-agent communication unavailable."
        )
        return None  # type: ignore[return-value]

    return _transport


def create_a2a_client(
    agent_topic: str | AgentTopic,
    transport: BaseTransport | None = None,
    **kwargs: Any,
) -> Any:
    """Create an A2A protocol client for communicating with a specific agent.

    Args:
        agent_topic: The target agent's topic identifier (e.g., AgentTopic.INTENT_CLASSIFIER).
        transport: Optional override transport. Uses default if not provided.
        **kwargs: Additional kwargs passed to factory.create_client().

    Returns:
        A2A client instance bound to the specified agent topic and transport.

    Raises:
        RuntimeError: If no transport is available.
    """
    factory = get_agntcy_factory()
    t = transport or get_default_transport()
    if t is None:
        raise RuntimeError(
            f"Cannot create A2A client for {agent_topic}: no transport available. "
            "Configure AGNTCY_SLIM_ENDPOINT or AGNTCY_NATS_ENDPOINT."
        )

    topic = agent_topic.value if isinstance(agent_topic, AgentTopic) else agent_topic
    client = factory.create_client(
        "A2A",
        agent_topic=topic,
        transport=t,
        **kwargs,
    )
    logger.debug("A2A client created for topic=%s", topic)
    return client


def create_mcp_client(
    agent_topic: str,
    transport: BaseTransport | None = None,
    *,
    server_url: str | None = None,
    timeout_s: float = 30.0,
    auth_headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> Any:
    """Create an MCP protocol client for connecting to an external tool server.

    This is the mandatory entry point for all MCP connections (SPEC-1534).
    Routes through AgntcyFactory.create_client("MCP", ...) to ensure all
    MCP communication flows through the AGNTCY SDK.

    Supports two modes:
        1. **Transport-based** (A2A transport available): Uses SLIM/NATS
           transport for MCP servers reachable via the agent mesh.
        2. **HTTP-direct** (external servers): Uses AgntcyFactory with
           ``server_url``, ``timeout_s``, and ``auth_headers`` for external
           MCP servers like Shopify Storefront or Stripe.

    Args:
        agent_topic: The MCP server's topic/endpoint identifier.
        transport: Optional override transport. Falls back to HTTP-direct
            mode when no transport is available.
        server_url: HTTP URL for external MCP servers. Required when no
            transport is available.
        timeout_s: Connection timeout in seconds (default 30).
        auth_headers: Optional HTTP headers for authenticated servers
            (e.g. ``{"Authorization": "Bearer sk_..."}`` for Stripe MCP).
        **kwargs: Additional kwargs passed to factory.create_client().

    Returns:
        MCP client (async context manager yielding ClientSession).

    Raises:
        RuntimeError: If neither transport nor server_url is available.
    """
    factory = get_agntcy_factory()
    t = transport or get_default_transport()

    # Build factory kwargs
    client_kwargs: dict[str, Any] = {
        "agent_topic": agent_topic,
        **kwargs,
    }

    if t is not None:
        # Transport-based MCP (agent mesh)
        client_kwargs["transport"] = t
    elif server_url:
        # HTTP-direct MCP for external servers (Shopify, Stripe, etc.)
        client_kwargs["server_url"] = server_url
        client_kwargs["timeout"] = timeout_s
        if auth_headers:
            client_kwargs["headers"] = auth_headers
    else:
        raise RuntimeError(
            f"Cannot create MCP client for {agent_topic}: no transport or "
            "server_url available."
        )

    client = factory.create_client("MCP", **client_kwargs)
    logger.debug(
        "MCP client created for topic=%s (mode=%s)",
        agent_topic,
        "transport" if t else "http-direct",
    )
    return client


# ---------------------------------------------------------------------------
# Lifecycle management
# ---------------------------------------------------------------------------

async def init_agntcy_sdk() -> None:
    """Initialize the AGNTCY SDK during FastAPI startup.

    Called from main.py lifespan. Creates the factory singleton and optionally
    sets up the default transport if endpoints are configured.
    """
    factory = get_agntcy_factory()
    logger.info(
        "AGNTCY SDK initialized: protocols=%s, transports=%s",
        factory.registered_protocols(),
        factory.registered_transports(),
    )

    # Attempt to create default transport (may be None if not configured)
    transport = get_default_transport()
    if transport is not None:
        logger.info("Default transport ready: %s", TRANSPORT_TYPE)
    else:
        logger.info(
            "No default transport configured — SDK available for factory "
            "operations but agent-to-agent communication is not active. "
            "This is expected during Phase 1."
        )


async def close_agntcy_sdk() -> None:
    """Shut down the AGNTCY SDK during FastAPI shutdown.

    Closes the default transport connection if one was established.
    """
    global _factory, _transport
    if _transport is not None:
        try:
            # SDK transports may have sync or async close(); handle both
            import asyncio
            import inspect

            if inspect.iscoroutinefunction(getattr(_transport, "close", None)):
                await _transport.close()
            else:
                _transport.close()
            logger.info("AGNTCY transport closed")
        except Exception as exc:
            logger.warning("Error closing AGNTCY transport: %s", exc)
        _transport = None
    _factory = None
    logger.info("AGNTCY SDK shut down")


# ---------------------------------------------------------------------------
# SDK capability introspection (for health checks and diagnostics)
# ---------------------------------------------------------------------------

def get_sdk_status() -> dict[str, Any]:
    """Return current SDK integration status for health/diagnostic endpoints.

    Returns a dict suitable for inclusion in /health or /ready responses.
    """
    factory = _factory
    transport = _transport

    status: dict[str, Any] = {
        "sdk_initialized": factory is not None,
        "transport_type": TRANSPORT_TYPE if transport is not None else None,
        "transport_active": transport is not None,
        "slim_endpoint": SLIM_ENDPOINT or None,
        "nats_endpoint": NATS_ENDPOINT or None,
        "available_protocols": factory.registered_protocols() if factory else [],
        "available_transports": factory.registered_transports() if factory else [],
        "agent_topics": [t.value for t in AgentTopic],
    }
    return status
