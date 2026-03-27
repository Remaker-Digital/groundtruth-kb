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
from aiohttp import web

logger = logging.getLogger(__name__)

# Health sidecar port (separate from SLIM protocol port)
_HEALTH_PORT = int(os.environ.get("SLIM_HEALTH_PORT", "8080"))


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

    # Start health sidecar (HTTP /healthz on _HEALTH_PORT for Container Apps probes)
    health_runner = await _start_health_sidecar(service_name)

    # Wait for shutdown signal
    await shutdown_event.wait()

    logger.info("Shutting down SLIM service...")
    try:
        await health_runner.cleanup()
    except Exception as exc:
        logger.warning("Error stopping health sidecar: %s", exc)
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


async def _start_health_sidecar(service_name: str) -> web.AppRunner:
    """Start a lightweight HTTP health server for Container Apps probes.

    SLIM speaks its own protocol on port 8443, so health probes need
    a separate HTTP endpoint. This sidecar responds to /healthz on
    _HEALTH_PORT with a 200 OK.
    """
    app = web.Application()

    async def _healthz(_request: web.Request) -> web.Response:
        return web.json_response({"status": "ok", "service": service_name})

    app.router.add_get("/healthz", _healthz)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", _HEALTH_PORT)
    await site.start()
    logger.info("Health sidecar listening on 0.0.0.0:%d/healthz", _HEALTH_PORT)
    return runner


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
