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
NATS_ENDPOINT = os.environ.get("AGNTCY_NATS_ENDPOINT", "nats://localhost:4222")
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
        body = await request.json()

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
            get_agntcy_factory,
            get_default_transport,
        )

        transport = get_default_transport()
        if transport is None:
            logger.warning(
                "Agent %s: no transport configured — running in HTTP-only mode. "
                "A2A messages will not be received via NATS/SLIM.",
                agent.agent_type,
            )
            return

        topic = agent.create_agent_topic()
        logger.info(
            "Agent %s: subscribing to topic '%s' on transport",
            agent.agent_type, topic,
        )

        # SDK transport subscription loop
        # The transport.subscribe() method is transport-specific;
        # for NATS it returns an async iterator of Messages.
        async for message in transport.subscribe(topic):
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
