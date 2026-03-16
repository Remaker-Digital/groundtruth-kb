# Agent Red Customer Experience — SLIM Routing Service
#
# Standalone SLIM server that provides the peer-to-peer mesh routing service
# for AGNTCY SDK transport (Tier 1 per SPEC-1802). All agent containers and
# the API gateway connect to this service as clients to establish SLIM
# transport for A2A messaging.
#
# Deployment: Azure Container App with HTTP/2 ingress on port 8443.
# Environment variables:
#   SLIM_LISTEN_ADDR  — Server listen address (default: 0.0.0.0:8443)
#   SLIM_SHARED_SECRET — Shared secret for app authentication (required)
#   SLIM_SERVICE_NAME  — Service name (default: agent-red-slim)
#   LOG_LEVEL          — Logging level (default: INFO)
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys

logger = logging.getLogger(__name__)


def _configure_logging() -> None:
    """Configure logging for the SLIM server."""
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )


async def run_slim_server() -> None:
    """Run the SLIM routing service.

    Creates a SLIM Service with a server configuration and runs it
    until shutdown signal is received.
    """
    import slim_bindings as sb

    listen_addr = os.environ.get("SLIM_LISTEN_ADDR", "0.0.0.0:8443")
    shared_secret = os.environ.get("SLIM_SHARED_SECRET", "")
    service_name = os.environ.get("SLIM_SERVICE_NAME", "agent-red-slim")

    if not shared_secret:
        logger.error(
            "SLIM_SHARED_SECRET is required. Set it as an environment variable."
        )
        sys.exit(1)

    if len(shared_secret) < 32:
        logger.error(
            "SLIM_SHARED_SECRET must be at least 32 characters (got %d).",
            len(shared_secret),
        )
        sys.exit(1)

    logger.info(
        "Starting SLIM routing service: listen=%s, service=%s",
        listen_addr, service_name,
    )

    # Initialize SLIM bindings with defaults (logging, crypto provider)
    sb.initialize_with_defaults()
    logger.info(
        "SLIM bindings initialized: version=%s, build=%s",
        sb.get_version(), sb.get_build_info(),
    )

    # Create the SLIM service
    service = sb.create_service(service_name)
    logger.info("SLIM service created: %s", service_name)

    # Create server config (insecure for internal Container Apps communication;
    # TLS termination is handled by Azure Container Apps Envoy proxy)
    server_config = sb.new_insecure_server_config(listen_addr)
    logger.info("Server config: %s", server_config)

    # Set up shutdown signal handling
    shutdown_event = asyncio.Event()

    def _signal_handler(sig: int, _frame: object) -> None:
        logger.info("Received signal %s — initiating shutdown", sig)
        shutdown_event.set()

    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGINT, _signal_handler)

    # Run the SLIM server in a background task
    server_task = asyncio.create_task(
        _run_server(service, server_config)
    )

    # Wait for shutdown signal
    await shutdown_event.wait()

    logger.info("Shutting down SLIM service...")
    try:
        await service.shutdown_async()
    except Exception as exc:
        logger.warning("Error during SLIM shutdown: %s", exc)

    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

    logger.info("SLIM routing service stopped")


async def _run_server(
    service: object,
    server_config: object,
) -> None:
    """Run the SLIM server (blocking until cancelled)."""
    try:
        logger.info("SLIM server starting on configured address...")
        await service.run_server_async(server_config)
    except asyncio.CancelledError:
        logger.info("SLIM server task cancelled")
    except Exception as exc:
        logger.exception("SLIM server error: %s", exc)
        raise


if __name__ == "__main__":
    _configure_logging()
    asyncio.run(run_slim_server())
