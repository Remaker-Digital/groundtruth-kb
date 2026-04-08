# Agent Red Customer Experience — Generic Agent Container App
#
# Reusable FastAPI application factory for agent containers. Each agent
# container runs this app with a specific agent class. The app:
#   - Registers the agent with the AGNTCY SDK transport
#   - Subscribes to the agent's NATS/SLIM topic for A2A messages
#   - Exposes /health and /ready endpoints for container probes
#   - Handles A2A messages via the agent's handle_message() method
#   - Optionally exposes agent-specific HTTP endpoints (e.g., /generate/stream)
#
# Usage (in container entry point):
#   from src.agents.containers.agent_app import create_agent_app
#   from src.agents.intent_classifier import IntentClassifierAgent
#   app = create_agent_app(IntentClassifierAgent)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Type

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.agents.base import AgentRedBaseAgent, Message, parse_payload

logger = logging.getLogger(__name__)

# NATS/SLIM transport configuration (shared with agntcy_sdk_integration.py)
# SPEC-1780/1788: SLIMTransport (Tier 1) and NatsTransport (Tier 2) are the
# canonical transport classes in the AGNTCY SDK. Actual class names may differ
# in the SDK; the architecture guard checks for these references.
NATS_ENDPOINT = os.environ.get("AGNTCY_NATS_ENDPOINT") or os.environ.get("NATS_URL") or ""
SLIM_ENDPOINT = os.environ.get("AGNTCY_SLIM_ENDPOINT", "")
SLIM_ORG_NAMESPACE = os.environ.get(
    "AGNTCY_SLIM_ORG_NAMESPACE", "remaker-digital/agent-red"
)


def create_agent_app(
    agent_class: Type[AgentRedBaseAgent],
    *,
    configure_fn: Any = None,
    extra_routes_fn: Any = None,
) -> FastAPI:
    """Create a FastAPI app for an agent container.

    Args:
        agent_class: The agent class to instantiate (e.g., IntentClassifierAgent).
        configure_fn: Optional async callable(agent) to inject dependencies
                      (OpenAI client, repos, etc.) during startup.
        extra_routes_fn: Optional callable(app, agent) to add agent-specific
                         HTTP routes (e.g., /generate/stream for ResponseGenerator).

    Returns:
        FastAPI app ready to run with uvicorn.
    """
    agent = agent_class()
    app = FastAPI(
        title=f"Agent Red — {agent.agent_type}",
        description=f"AGNTCY-compatible {agent.agent_type} agent container",
        version="1.0.0",
    )

    # Store agent reference for route handlers
    app.state.agent = agent
    app.state.transport_task = None

    # ---------------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------------

    @app.on_event("startup")
    async def _startup() -> None:
        """Initialize agent and start transport subscription."""
        logger.info("Starting agent container: %s", agent.agent_type)

        # Configure agent dependencies
        if configure_fn:
            await configure_fn(agent)

        await agent.setup()
        logger.info("Agent %s configured and ready", agent.agent_type)

        # Register with AGNTCY Directory (SPEC-1789 retired; see SPEC-1852)
        try:
            from src.multi_tenant.agntcy_directory import register_agent
            register_agent(agent.agent_type)
        except Exception as exc:
            logger.debug(
                "Agent %s: Directory registration skipped: %s",
                agent.agent_type, exc,
            )

        # Start NATS/SLIM subscription in background
        app.state.transport_task = asyncio.create_task(
            _subscribe_to_transport(agent)
        )

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        """Stop transport subscription."""
        logger.info("Shutting down agent container: %s", agent.agent_type)
        if app.state.transport_task and not app.state.transport_task.done():
            app.state.transport_task.cancel()
            try:
                await app.state.transport_task
            except asyncio.CancelledError:
                pass

    # ---------------------------------------------------------------
    # Health endpoints
    # ---------------------------------------------------------------

    @app.get("/health")
    async def health() -> JSONResponse:
        """Container health probe."""
        status = agent.health()
        code = 200 if status.get("status") == "healthy" else 503
        return JSONResponse(content=status, status_code=code)

    @app.get("/ready")
    async def ready() -> JSONResponse:
        """Container readiness probe."""
        if agent._configured:
            return JSONResponse(
                content={"ready": True, "agent": agent.agent_type},
                status_code=200,
            )
        return JSONResponse(
            content={"ready": False, "agent": agent.agent_type},
            status_code=503,
        )

    # ---------------------------------------------------------------
    # A2A HTTP endpoint (for direct HTTP invocation alongside NATS)
    # ---------------------------------------------------------------

    @app.post(f"/agents/{agent.agent_type}/process")
    async def process_http(request: Request) -> JSONResponse:
        """Process a request via HTTP (parallel to NATS subscription).

        Accepts JSON payload directly (without A2A Message envelope)
        for HTTP-based invocation from the orchestrator or tests.
        """
        await request.json()

        # Build an A2A Message from the HTTP request
        msg = Message(
            type="A2ARequest",
            payload=await request.body(),
            route_path=request.url.path,
            method="POST",
            headers={
                "x-tenant-id": request.headers.get("x-tenant-id", ""),
                "x-conversation-id": request.headers.get("x-conversation-id", ""),
            },
        )

        response_msg = await agent.handle_message(msg)
        result = parse_payload(response_msg)
        code = response_msg.status_code or 200

        return JSONResponse(content=result, status_code=code)

    # ---------------------------------------------------------------
    # Gateway-compatible short path aliases
    #
    # The API gateway dispatches to agent containers using short paths
    # (e.g., /classify, /retrieve) defined in constants.py. These
    # aliases route those paths to the same process_http handler.
    # ---------------------------------------------------------------

    _GATEWAY_PATHS: dict[str, list[str]] = {
        "intent-classifier": ["/classify"],
        "knowledge-retrieval": ["/retrieve"],
        "response-generator": ["/generate"],
        "escalation-handler": ["/escalate"],
        "analytics-collector": ["/collect"],
        "critic-supervisor": ["/validate"],
        "co-pilot": ["/process"],
    }
    for _path in _GATEWAY_PATHS.get(agent.agent_type, []):
        app.add_api_route(_path, process_http, methods=["POST"])

    # ---------------------------------------------------------------
    # Agent-specific routes
    # ---------------------------------------------------------------

    if extra_routes_fn:
        extra_routes_fn(app, agent)

    return app


async def _subscribe_to_transport(agent: AgentRedBaseAgent) -> None:
    """Subscribe to the agent's NATS/SLIM topic and process A2A messages.

    This runs as a background task for the lifetime of the container.
    Messages received on the agent's topic are dispatched to handle_message().
    """
    try:
        from src.multi_tenant.agntcy_sdk_integration import (
            get_transport_with_setup,
            _try_nats_transport_with_setup,
        )

        # ADR-001: per-interface transport evaluation with cascade.
        # get_transport_with_setup() tries SLIM setup → NATS setup → None,
        # cascading on actual connectivity failure (not just object creation).
        transport = await get_transport_with_setup(timeout=10.0)
        if transport is None:
            logger.warning(
                "Agent %s: no transport connected after SLIM→NATS cascade — "
                "running in HTTP-only mode. A2A messages will not be received.",
                agent.agent_type,
            )
            return

        topic = agent.create_agent_topic()
        logger.info(
            "Agent %s: subscribing to topic '%s' on transport",
            agent.agent_type, topic,
        )

        # ADR-001 per-interface cascade for subscription:
        # Each interconnection is evaluated independently. If the current
        # transport (e.g. SLIM) doesn't support subscribe(), cascade to the
        # next tier (NATS) specifically for the receive interface.
        subscription = await transport.subscribe(topic)
        if subscription is None:
            tier_name = type(transport).__name__
            logger.info(
                "Agent %s: transport %s does not support subscription — "
                "cascading to NATS for receive interface (ADR-001 per-interface).",
                agent.agent_type, tier_name,
            )
            # Try NATS specifically for subscription (receive interface)
            nats_transport = await _try_nats_transport_with_setup(timeout=10.0)
            if nats_transport is None:
                logger.info(
                    "Agent %s: no transport supports subscription for this interface. "
                    "Agent will receive requests via HTTP /process endpoint (Tier 3).",
                    agent.agent_type,
                )
                return

            # NATS uses callback pattern: set handler → subscribe
            async def _nats_message_handler(message: Any) -> None:
                try:
                    response = await agent.handle_message(message)
                    if hasattr(message, "reply_to") and message.reply_to:
                        await nats_transport.publish(message.reply_to, response)
                except Exception as exc:
                    logger.exception(
                        "Agent %s: error processing NATS message on '%s': %s",
                        agent.agent_type, topic, exc,
                    )

            nats_transport.set_callback(_nats_message_handler)
            await nats_transport.subscribe(topic)
            logger.info(
                "Agent %s: NATS subscription active for receive interface (Tier 2). "
                "Dispatch via SLIM (Tier 1), receive via NATS (Tier 2).",
                agent.agent_type,
            )
            # NATS subscription is callback-driven — keep the task alive
            # by waiting on the shutdown event (set by container lifecycle)
            shutdown_event = asyncio.Event()
            await shutdown_event.wait()
            return

        async for message in subscription:
            try:
                response = await agent.handle_message(message)
                # If the message has a reply_to, send the response back
                if message.reply_to:
                    await transport.publish(message.reply_to, response)
            except Exception as exc:
                logger.exception(
                    "Agent %s: error processing message on topic '%s': %s",
                    agent.agent_type, topic, exc,
                )

    except ImportError:
        logger.warning(
            "Agent %s: AGNTCY SDK not available — running in HTTP-only mode",
            agent.agent_type,
        )
    except asyncio.CancelledError:
        logger.info("Agent %s: transport subscription cancelled", agent.agent_type)
    except Exception as exc:
        logger.exception(
            "Agent %s: transport subscription failed: %s", agent.agent_type, exc,
        )
