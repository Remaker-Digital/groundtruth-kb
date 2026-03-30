# Agent Red Customer Experience — AGNTCY Directory Integration
#
# Provides dynamic agent discovery via the AGNTCY Directory registry,
# replacing the hardcoded AgentTopic enum for agent routing (SPEC-1789).
#
# Architecture:
#   - Agents register with the Directory on container startup
#   - Gateway resolves agent endpoints via Directory lookup
#   - Falls back to static AgentTopic enum when Directory is unavailable
#   - Directory server address configured via AGNTCY_DIRECTORY_ADDR env var
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Directory server address (gRPC). Empty = Directory unavailable.
DIRECTORY_ADDR = os.environ.get("AGNTCY_DIRECTORY_ADDR", "")

# Organization namespace for agent names in the Directory
ORG_NAMESPACE = os.environ.get(
    "AGNTCY_SLIM_ORG_NAMESPACE", "remaker-digital/agent-red"
)

# Agent version (matches product version for consistency)
AGENT_VERSION = os.environ.get("PRODUCT_VERSION", "1.89.0")

# Agent names sourced from registry (SPEC-1852). Lazy-loaded to avoid
# import-time initialization of the plugin registry.
_agent_names_cache: tuple[str, ...] | None = None


def _get_agent_names() -> tuple[str, ...]:
    global _agent_names_cache
    if _agent_names_cache is None:
        from src.agents.plugins.registry import PluginAgentRegistry
        _agent_names_cache = tuple(
            PluginAgentRegistry.get_instance().get_core_agent_ids()
        )
    return _agent_names_cache


# ---------------------------------------------------------------------------
# Directory Client Singleton
# ---------------------------------------------------------------------------

_directory_client: Any | None = None
_directory_available: bool = False

# Agent registry cache: agent_name -> resolved metadata
_agent_cache: dict[str, dict[str, Any]] = {}


def _get_directory_client() -> Any | None:
    """Return the singleton Directory client, or None if unavailable."""
    global _directory_client, _directory_available

    if _directory_client is not None:
        return _directory_client

    if not DIRECTORY_ADDR:
        logger.info(
            "AGNTCY Directory not configured (AGNTCY_DIRECTORY_ADDR empty). "
            "Using static agent registry."
        )
        _directory_available = False
        return None

    try:
        from agntcy.dir_sdk.client.client import Client, Config

        config = Config(server_address=DIRECTORY_ADDR)
        _directory_client = Client(config=config)
        _directory_available = True
        logger.info(
            "AGNTCY Directory client connected: addr=%s", DIRECTORY_ADDR
        )
        return _directory_client
    except Exception as exc:
        logger.warning(
            "AGNTCY Directory client creation failed (addr=%s): %s. "
            "Falling back to static agent registry.",
            DIRECTORY_ADDR, exc,
        )
        _directory_available = False
        return None


# ---------------------------------------------------------------------------
# Agent Registration (called by agent containers on startup)
# ---------------------------------------------------------------------------


def register_agent(
    agent_name: str,
    *,
    capabilities: list[str] | None = None,
    endpoint: str = "",
    metadata: dict[str, str] | None = None,
) -> bool:
    """Register an agent with the AGNTCY Directory.

    Called during agent container startup. If Directory is unavailable,
    registration is skipped (agents still work via static routing).

    Args:
        agent_name: Agent identifier (e.g., "intent-classifier").
        capabilities: List of capability tags (e.g., ["classify", "intent"]).
        endpoint: Agent's HTTP endpoint for direct routing.
        metadata: Additional metadata key-value pairs.

    Returns:
        True if registration succeeded, False otherwise.
    """
    client = _get_directory_client()
    if client is None:
        logger.debug(
            "Skipping Directory registration for %s (Directory unavailable)",
            agent_name,
        )
        return False

    try:
        from agntcy.dir.routing.v1 import routing_service_pb2

        # Build the fully qualified agent name
        fq_name = f"{ORG_NAMESPACE}/{agent_name}"

        req = routing_service_pb2.PublishRequest(
            name=fq_name,
            version=AGENT_VERSION,
        )

        client.publish(req)
        logger.info(
            "Agent registered with Directory: name=%s version=%s",
            fq_name, AGENT_VERSION,
        )

        # Cache the registration
        _agent_cache[agent_name] = {
            "name": fq_name,
            "version": AGENT_VERSION,
            "capabilities": capabilities or [],
            "endpoint": endpoint,
            "metadata": metadata or {},
            "registered": True,
        }
        return True
    except Exception as exc:
        logger.warning(
            "Directory registration failed for %s: %s", agent_name, exc,
        )
        return False


# ---------------------------------------------------------------------------
# Agent Discovery (called by gateway for routing)
# ---------------------------------------------------------------------------


def resolve_agent(agent_name: str) -> dict[str, Any] | None:
    """Resolve an agent by name via the AGNTCY Directory.

    Falls back to static registry if Directory is unavailable or
    the agent is not found.

    Args:
        agent_name: Agent identifier (e.g., "intent-classifier").

    Returns:
        Agent metadata dict with name, version, endpoint, capabilities.
        None if agent is not found in either Directory or static registry.
    """
    # Check cache first
    if agent_name in _agent_cache:
        return _agent_cache[agent_name]

    # Try Directory lookup
    client = _get_directory_client()
    if client is not None:
        try:
            fq_name = f"{ORG_NAMESPACE}/{agent_name}"
            response = client.resolve(fq_name, version=AGENT_VERSION)

            if response:
                agent_info = {
                    "name": fq_name,
                    "version": AGENT_VERSION,
                    "source": "directory",
                    "resolved": True,
                }
                _agent_cache[agent_name] = agent_info
                logger.debug("Agent resolved via Directory: %s", fq_name)
                return agent_info
        except Exception as exc:
            logger.debug(
                "Directory resolution failed for %s: %s (using static fallback)",
                agent_name, exc,
            )

    # Static fallback — agent exists in well-known list
    if agent_name in _get_agent_names():
        return {
            "name": f"{ORG_NAMESPACE}/{agent_name}",
            "version": AGENT_VERSION,
            "source": "static",
            "resolved": True,
        }

    return None


def list_agents() -> list[dict[str, Any]]:
    """List all known agents (from Directory + static registry).

    Returns:
        List of agent metadata dicts.
    """
    agents: list[dict[str, Any]] = []

    # Try Directory listing
    client = _get_directory_client()
    if client is not None:
        try:
            # List all published agents
            records = client.list()
            for record in records or []:
                name = getattr(record, "name", "")
                if name.startswith(f"{ORG_NAMESPACE}/"):
                    short_name = name.split("/")[-1]
                    agents.append({
                        "name": name,
                        "short_name": short_name,
                        "version": getattr(record, "version", ""),
                        "source": "directory",
                    })
        except Exception as exc:
            logger.debug("Directory listing failed: %s", exc)

    # Merge with static registry (ensure all well-known agents are listed)
    listed_names = {a.get("short_name") for a in agents}
    for agent_name in _get_agent_names():
        if agent_name not in listed_names:
            agents.append({
                "name": f"{ORG_NAMESPACE}/{agent_name}",
                "short_name": agent_name,
                "version": AGENT_VERSION,
                "source": "static",
            })

    return agents


def get_agent_topic(agent_name: str) -> str:
    """Get the transport topic for an agent.

    This replaces direct AgentTopic enum access. It resolves via Directory
    first, then falls back to the agent name as the topic (which matches
    the current AgentTopic enum values).

    Args:
        agent_name: Agent identifier (e.g., "intent-classifier").

    Returns:
        Transport topic string for the agent.
    """
    agent_info = resolve_agent(agent_name)
    if agent_info:
        # Directory-resolved agents may have custom topic routing
        return agent_info.get("topic", agent_name)
    return agent_name


# ---------------------------------------------------------------------------
# Directory status (for health checks)
# ---------------------------------------------------------------------------


def get_directory_status() -> dict[str, Any]:
    """Return Directory integration status for health endpoints."""
    return {
        "directory_configured": bool(DIRECTORY_ADDR),
        "directory_available": _directory_available,
        "directory_addr": DIRECTORY_ADDR or None,
        "registered_agents": list(_agent_cache.keys()),
        "total_known_agents": len(_get_agent_names()),
        "discovery_mode": "directory" if _directory_available else "static",
    }


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


async def init_agent_directory() -> None:
    """Initialize the AGNTCY Directory integration during startup."""
    client = _get_directory_client()
    if client is not None:
        logger.info("AGNTCY Directory initialized: addr=%s", DIRECTORY_ADDR)
    else:
        logger.info(
            "AGNTCY Directory not available — using static agent registry "
            "with %d well-known agents",
            len(_get_agent_names()),
        )


async def close_agent_directory() -> None:
    """Clean up Directory resources during shutdown."""
    global _directory_client, _directory_available
    _directory_client = None
    _directory_available = False
    _agent_cache.clear()
    logger.info("AGNTCY Directory client closed")
