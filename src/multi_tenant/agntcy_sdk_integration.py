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

# AGNTCY SDK imports — each import isolated to prevent one missing name from
# breaking all (lesson: v0.5.4 removed ProtocolTypes/TransportTypes enums).
try:
    from agntcy_app_sdk.factory import AgntcyFactory
except ImportError:
    AgntcyFactory = None  # type: ignore[assignment,misc]

# ProtocolTypes/TransportTypes removed in SDK v0.5.x — import individually, optional
try:
    from agntcy_app_sdk.factory import ProtocolTypes  # type: ignore[attr-defined]
except ImportError:
    ProtocolTypes = None  # type: ignore[assignment,misc]
try:
    from agntcy_app_sdk.factory import TransportTypes  # type: ignore[attr-defined]
except ImportError:
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

# NATS endpoint for fallback transport (AGNTCY_NATS_ENDPOINT preferred, NATS_URL fallback)
NATS_ENDPOINT = os.environ.get("AGNTCY_NATS_ENDPOINT") or os.environ.get("NATS_URL") or ""

# SLIM routable name prefix (org/namespace format per SDK convention)
SLIM_ORG_NAMESPACE = os.environ.get(
    "AGNTCY_SLIM_ORG_NAMESPACE", "remaker-digital/agent-red"
)

# SPEC-1802: SLIM > NATS > HTTP (failure mode). TRANSPORT_TYPE retained for
# backward compat but transport selection now always tries SLIM first, then NATS.
TRANSPORT_TYPE = os.environ.get("AGNTCY_TRANSPORT_TYPE", "slim").lower()

# mTLS configuration for SLIM transport
SLIM_TLS_INSECURE = os.environ.get("AGNTCY_SLIM_TLS_INSECURE", "false").lower() == "true"
SLIM_SHARED_SECRET = os.environ.get("AGNTCY_SLIM_SHARED_SECRET", "")

# Enable SDK tracing (Phase 5 will wire this to OpenTelemetry)
ENABLE_SDK_TRACING = os.environ.get("AGNTCY_ENABLE_TRACING", "false").lower() == "true"


class AgentTopic(str, Enum):
    """Agent topic identifiers matching AGNTCY upstream convention.

    DEPRECATED: Use PluginAgentRegistry.get_core_agent_ids() or
    agntcy_directory.get_agent_topic() for dynamic discovery (SPEC-1852).
    This enum is a static fallback only — do not add new entries here.
    Prefer registry lookups in all new code.

    These map 1:1 to the AgentRole enum in system_prompt_builder.py and to
    the NATS topic suffixes in nats_isolation.py.
    """

    INTENT_CLASSIFIER = "intent-classifier"
    KNOWLEDGE_RETRIEVAL = "knowledge-retrieval"
    RESPONSE_GENERATOR = "response-generator"
    ESCALATION_HANDLER = "escalation-handler"
    ANALYTICS_COLLECTOR = "analytics-collector"
    CRITIC_SUPERVISOR = "critic-supervisor"
    CO_PILOT = "co-pilot"


# ---------------------------------------------------------------------------
# Singleton factory
# ---------------------------------------------------------------------------

_factory: AgntcyFactory | None = None
_transport: BaseTransport | None = None
_transport_setup_ok: bool = False  # True only after transport.setup() succeeds


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

    # SPEC-1802 transport priority: SLIM > NATS JetStream > (HTTP is failure mode)
    if SLIM_ENDPOINT:
        try:
            _transport = factory.create_transport(
                transport="SLIM",
                name=f"{SLIM_ORG_NAMESPACE}/gateway",
                endpoint=SLIM_ENDPOINT,
                tls_insecure=SLIM_TLS_INSECURE,
                shared_secret_identity=SLIM_SHARED_SECRET or None,
            )
            logger.info(
                "SLIM transport created — Tier 1 active (endpoint=%s, tls_insecure=%s)",
                SLIM_ENDPOINT,
                SLIM_TLS_INSECURE,
            )
        except Exception:
            logger.warning(
                "SLIM transport creation failed — falling back to NATS",
                exc_info=True,
            )
            _transport = None

    if _transport is None and NATS_ENDPOINT:
        try:
            # WI-1314/WI-1319: NATS endpoint may be ws:// (WebSocket) when
            # running in Azure Container Apps where Envoy proxy blocks raw TCP.
            # The AGNTCY SDK and nats.py both support WebSocket URLs natively.
            nats_kwargs: dict[str, Any] = {
                "transport": "NATS",
                "name": "agent-red-nats",
                "endpoint": NATS_ENDPOINT,
            }
            # Pass allow_reconnect for resilience in container environments
            _transport = factory.create_transport(**nats_kwargs)
            logger.info(
                "NATS transport created — Tier 2 active (endpoint=%s, protocol=%s)",
                NATS_ENDPOINT,
                "websocket" if NATS_ENDPOINT.startswith("ws") else "tcp",
            )
        except Exception:
            logger.warning(
                "NATS transport creation failed (endpoint=%s) — "
                "all transports unavailable. Check: (1) NATS server is running, "
                "(2) endpoint URL is reachable, (3) WebSocket mode if in Azure "
                "Container Apps.",
                NATS_ENDPOINT,
                exc_info=True,
            )
            _transport = None

    if _transport is None:
        logger.warning(
            "No AGNTCY transport available (SLIM_ENDPOINT=%r, NATS_ENDPOINT=%r). "
            "Agent dispatch will use HTTP containers (failure mode per SPEC-1802).",
            SLIM_ENDPOINT,
            NATS_ENDPOINT,
        )
        return None  # type: ignore[return-value]

    return _transport


async def get_transport_with_setup(timeout: float = 10.0) -> BaseTransport:
    """Try each transport tier with actual setup(), cascading on failure.

    ADR-001: Each container interconnection is evaluated independently.
    The standing priority order SLIM → NATS → HTTP is applied per-interface,
    not globally. This function tries:

    1. SLIM: create_transport() + setup() → if setup fails, cascade
    2. NATS: create_transport() + setup() → if setup fails, cascade
    3. Return None (HTTP failure mode)

    Unlike get_default_transport() which only cascades at creation time,
    this function cascades at the *connectivity* level — a transport that
    creates successfully but fails setup() triggers the next tier.
    """
    global _transport, _transport_setup_ok
    import asyncio

    factory = get_agntcy_factory()

    # Tier 1: SLIM
    if SLIM_ENDPOINT:
        try:
            slim = factory.create_transport(
                transport="SLIM",
                name=f"{SLIM_ORG_NAMESPACE}/gateway",
                endpoint=SLIM_ENDPOINT,
                tls_insecure=SLIM_TLS_INSECURE,
                shared_secret_identity=SLIM_SHARED_SECRET or None,
            )
            logger.info(
                "SLIM transport created — attempting setup (endpoint=%s)",
                SLIM_ENDPOINT,
            )
            await asyncio.wait_for(slim.setup(), timeout=timeout)
            _transport = slim
            _transport_setup_ok = True
            logger.info("SLIM transport setup succeeded — Tier 1 active")
            return _transport
        except Exception as exc:
            logger.warning(
                "SLIM transport setup failed (%s) — cascading to NATS (Tier 2)",
                exc,
            )

    # Tier 2: NATS
    if NATS_ENDPOINT:
        try:
            nats_kwargs: dict[str, Any] = {
                "transport": "NATS",
                "name": "agent-red-nats",
                "endpoint": NATS_ENDPOINT,
            }
            nats = factory.create_transport(**nats_kwargs)
            logger.info(
                "NATS transport created — attempting setup (endpoint=%s, protocol=%s)",
                NATS_ENDPOINT,
                "websocket" if NATS_ENDPOINT.startswith("ws") else "tcp",
            )
            await asyncio.wait_for(nats.setup(), timeout=timeout)
            _transport = nats
            _transport_setup_ok = True
            logger.info("NATS transport setup succeeded — Tier 2 active")
            return _transport
        except Exception as exc:
            logger.warning(
                "NATS transport setup failed (%s) — all transports exhausted. "
                "Agent will operate in HTTP-only mode (Tier 3).",
                exc,
            )

    # Tier 3: No transport available
    _transport = None
    _transport_setup_ok = False
    logger.warning(
        "No transport connected after setup cascade. "
        "SLIM=%r (setup failed), NATS=%r (setup failed). "
        "Operating in HTTP-only mode per ADR-001.",
        SLIM_ENDPOINT, NATS_ENDPOINT,
    )
    return None  # type: ignore[return-value]


async def _try_nats_transport_with_setup(timeout: float = 10.0) -> BaseTransport:
    """Try NATS transport specifically for a single interface (e.g. receive).

    ADR-001: each interconnection is evaluated independently. When the primary
    transport (SLIM) is active for dispatch but doesn't support subscription,
    this function creates a separate NATS transport for the receive interface.

    Returns the NATS transport if setup succeeds, None otherwise.
    Does NOT modify the global _transport singleton.
    """
    import asyncio

    if not NATS_ENDPOINT:
        return None  # type: ignore[return-value]

    factory = get_agntcy_factory()
    try:
        nats = factory.create_transport(
            transport="NATS",
            name="agent-red-nats-receive",
            endpoint=NATS_ENDPOINT,
        )
        await asyncio.wait_for(nats.setup(), timeout=timeout)
        logger.info(
            "NATS transport setup succeeded for receive interface (endpoint=%s)",
            NATS_ENDPOINT,
        )
        return nats
    except Exception as exc:
        logger.warning(
            "NATS transport setup failed for receive interface: %s", exc,
        )
        return None  # type: ignore[return-value]


def _build_agent_card(agent_topic: str) -> Any:
    """Build an AgentCard for an internal pipeline agent.

    Creates a minimal AgentCard with SLIM transport as the preferred
    transport and the agent's SLIM topic as the URL.
    """
    from a2a.types import AgentCapabilities, AgentCard, AgentSkill

    slim_url = f"slim://{SLIM_ORG_NAMESPACE}/{agent_topic}"

    return AgentCard(
        name=agent_topic,
        description=f"Agent Red pipeline agent: {agent_topic}",
        url=slim_url,
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        default_input_modes=["text"],
        default_output_modes=["text"],
        preferred_transport="slimpatterns",
        skills=[
            AgentSkill(
                id=agent_topic,
                name=agent_topic,
                description=f"Process {agent_topic} requests",
                tags=[agent_topic],
            ),
        ],
    )


def _get_client_config() -> Any:
    """Build a ClientConfig with SLIM as primary transport.

    SPEC-1802: SLIM/gRPC is always primary. NATS is first fallback.
    HTTP (JSONRPC) is second fallback. In-process is not an option.
    """
    from agntcy_app_sdk.semantic.a2a.client.config import (
        ClientConfig,
        NatsTransportConfig,
        SlimTransportConfig,
    )

    slim_cfg = None
    nats_cfg = None

    if SLIM_ENDPOINT:
        slim_cfg = SlimTransportConfig(
            endpoint=SLIM_ENDPOINT,
            name=f"{SLIM_ORG_NAMESPACE}/gateway",
            shared_secret_identity=SLIM_SHARED_SECRET or "slim-mls-secret-REPLACE_WITH_RANDOM_32PLUS_CHARS",
            tls_insecure=SLIM_TLS_INSECURE,
        )

    if NATS_ENDPOINT:
        nats_cfg = NatsTransportConfig(
            endpoint=NATS_ENDPOINT,
            name="agent-red-nats",
        )

    return ClientConfig(
        slim_config=slim_cfg,
        nats_config=nats_cfg,
    )


# Cache of A2A clients keyed by agent topic
_a2a_clients: dict[str, Any] = {}


async def create_a2a_client(
    agent_topic: str | AgentTopic,
    **kwargs: Any,
) -> Any:
    """Create an A2A protocol client for communicating with a specific agent.

    Uses the AGNTCY SDK v0.5.4 A2AClientFactory.connect() API.
    SPEC-1802: SLIM/gRPC is always primary transport.

    Args:
        agent_topic: The target agent's topic identifier.
        **kwargs: Additional kwargs for future extension.

    Returns:
        A2A client instance bound to the specified agent topic.

    Raises:
        RuntimeError: If no transport is configured.
    """
    from agntcy_app_sdk.semantic.a2a.client.factory import A2AClientFactory

    topic = agent_topic.value if isinstance(agent_topic, AgentTopic) else agent_topic

    # Return cached client if available
    if topic in _a2a_clients:
        return _a2a_clients[topic]

    if not SLIM_ENDPOINT and not NATS_ENDPOINT:
        raise RuntimeError(
            f"Cannot create A2A client for {topic}: no transport configured. "
            "Set AGNTCY_SLIM_ENDPOINT (required) or AGNTCY_NATS_ENDPOINT (fallback)."
        )

    card = _build_agent_card(topic)
    config = _get_client_config()

    client = await A2AClientFactory.connect(card, config)
    _a2a_clients[topic] = client
    logger.info("A2A client created for topic=%s (transport=SLIM/gRPC)", topic)
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

    # ADR-001: per-interface transport cascade with actual connectivity proof.
    # get_transport_with_setup() tries SLIM→NATS→None, cascading on setup() failure.
    transport = await get_transport_with_setup(timeout=15.0)
    if transport is not None:
        logger.info(
            "Transport ready: tier=%s, setup_ok=%s",
            "slim" if "SLIM" in type(transport).__name__.upper() else "nats",
            _transport_setup_ok,
        )
    else:
        logger.info(
            "No transport connected after cascade — SDK available for factory "
            "operations but A2A communication uses HTTP (Tier 3)."
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

    # Determine active tier per SPEC-1802
    if transport is not None:
        transport_class = type(transport).__name__
        if "SLIM" in transport_class.upper():
            active_tier = "slim"
        elif "NATS" in transport_class.upper():
            active_tier = "nats"
        else:
            active_tier = transport_class.lower()
    else:
        active_tier = None

    # Determine connection protocol (WI-1319: WebSocket vs TCP)
    nats_protocol = None
    if NATS_ENDPOINT:
        nats_protocol = "websocket" if NATS_ENDPOINT.startswith("ws") else "tcp"

    status: dict[str, Any] = {
        "sdk_initialized": factory is not None,
        "transport_type": active_tier,
        "transport_active": _transport_setup_ok,  # Actual connectivity, not just object existence
        "active_tier": active_tier or "http_failure_mode",
        "slim_endpoint": SLIM_ENDPOINT or None,
        "nats_endpoint": NATS_ENDPOINT or None,
        "nats_protocol": nats_protocol,
        "available_protocols": factory.registered_protocols() if factory else [],
        "available_transports": factory.registered_transports() if factory else [],
        "agent_topics": [t.value for t in AgentTopic],
    }

    # Include Directory status (SPEC-1852)
    try:
        from src.multi_tenant.agntcy_directory import get_directory_status
        status["directory"] = get_directory_status()
    except Exception:
        status["directory"] = {"directory_available": False}

    return status
