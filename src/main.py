"""
Agent Red Customer Engagement — FastAPI application entrypoint.

Mounts all API routers and provides health/readiness endpoints.

Usage:
    uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Agent Red Customer Engagement",
    description="AI-powered customer engagement platform API.",
    version="1.0.0",
    docs_url="/docs" if os.environ.get("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.environ.get("ENVIRONMENT") == "development" else None,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# CORS — restrict in production via APP_CORS_ORIGINS env var
_cors_origins = os.environ.get("APP_CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from src.integrations.provisioning import router as provisioning_router  # noqa: E402
from src.integrations.stripe_checkout import router as checkout_router  # noqa: E402
from src.integrations.stripe_packs import router as packs_router  # noqa: E402
from src.integrations.stripe_portal import router as portal_router  # noqa: E402
from src.integrations.stripe_usage import router as usage_router  # noqa: E402
from src.integrations.stripe_webhooks import router as webhooks_router  # noqa: E402
from src.integrations.shopify_billing import router as shopify_billing_router  # noqa: E402
from src.multi_tenant.usage_dashboard_api import router as dashboard_router  # noqa: E402
from src.multi_tenant.tenant_config_api import router as config_router  # noqa: E402

app.include_router(provisioning_router)
app.include_router(checkout_router)
app.include_router(packs_router)
app.include_router(portal_router)
app.include_router(usage_router)
app.include_router(webhooks_router)
app.include_router(shopify_billing_router)
app.include_router(dashboard_router)
app.include_router(config_router)

# ---------------------------------------------------------------------------
# Pipeline resilience — concurrency control + circuit breakers (WI #44-46)
# ---------------------------------------------------------------------------

from src.multi_tenant.pipeline_resilience import (  # noqa: E402
    TenantConcurrencyMiddleware,
    get_circuit_breaker_registry,
)

# TenantConcurrencyMiddleware: per-tenant concurrency limiter (asyncio.Semaphore
# + queue depth).  Added BEFORE CorrelationMiddleware / AFTER
# TenantAuthMiddleware so that it has TenantContext available.
# Starlette processes middleware in reverse registration order, so this is
# registered first but runs after auth.
app.add_middleware(TenantConcurrencyMiddleware)

# ---------------------------------------------------------------------------
# OpenTelemetry tenant-aware tracing (Work Items #39-40)
# ---------------------------------------------------------------------------

from src.multi_tenant.otel_tracing import (  # noqa: E402
    CorrelationMiddleware,
    configure_logging as configure_tenant_logging,
    configure_tracing,
)

# CorrelationMiddleware: sets CorrelationContext per-request from TenantContext.
# Must be added AFTER TenantAuthMiddleware (Starlette processes in reverse order).
app.add_middleware(CorrelationMiddleware)


@app.on_event("startup")
async def _startup_tracing() -> None:
    """Initialize OpenTelemetry tracing with tenant context injection."""
    configure_tracing()
    configure_tenant_logging()
    logger.info("OpenTelemetry tenant-aware tracing configured")


@app.on_event("startup")
async def _startup_circuit_breakers() -> None:
    """Pre-register default circuit breakers for external dependencies."""
    registry = get_circuit_breaker_registry()
    # Azure OpenAI and Cosmos DB breakers are auto-created on first use via
    # call_with_breaker(), but pre-registering logs their presence at startup.
    logger.info(
        "Circuit breaker registry ready — %d breakers registered",
        len(registry.health_summary()),
    )


# ---------------------------------------------------------------------------
# NATS tenant isolation (Work Items #15-17, #26)
# ---------------------------------------------------------------------------

from src.multi_tenant.nats_isolation import (  # noqa: E402
    close_nats_manager,
    get_nats_manager,
    init_nats_manager,
)


@app.on_event("startup")
async def _startup_nats() -> None:
    """Connect to NATS JetStream on application startup."""
    try:
        await init_nats_manager()
        logger.info("NATS tenant isolation manager connected")
    except Exception:
        # Non-fatal at startup — NATS may not be available in dev
        logger.warning(
            "NATS connection failed at startup — tenant messaging unavailable. "
            "Set NATS_URL environment variable to configure."
        )


@app.on_event("shutdown")
async def _shutdown_nats() -> None:
    """Drain and close NATS connection on application shutdown."""
    await close_nats_manager()
    logger.info("NATS tenant isolation manager closed")


# ---------------------------------------------------------------------------
# Tenant secret management — Key Vault integration (Work Item #29)
# ---------------------------------------------------------------------------

from src.multi_tenant.tenant_secret_service import get_secret_service  # noqa: E402


@app.on_event("startup")
async def _startup_secret_service() -> None:
    """Initialize the TenantSecretService (Key Vault client)."""
    try:
        service = get_secret_service()
        await service.initialize()
        logger.info("TenantSecretService initialized")
    except Exception:
        logger.warning(
            "TenantSecretService initialization failed — secret management "
            "unavailable. Set AZURE_KEYVAULT_URL to configure."
        )


@app.on_event("shutdown")
async def _shutdown_secret_service() -> None:
    """Close the Key Vault client."""
    service = get_secret_service()
    await service.close()
    logger.info("TenantSecretService closed")


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness probe — returns 200 if the process is running."""
    return {"status": "healthy"}


@app.get("/ready", tags=["system"])
async def ready() -> dict:
    """Readiness probe — returns 200 if the service can accept traffic.

    Checks NATS connectivity when the manager is initialized.
    """
    result: dict[str, Any] = {"status": "ready"}

    nats_mgr = get_nats_manager()
    if nats_mgr.is_connected:
        nats_health = await nats_mgr.check_health()
        result["nats"] = {
            "connected": nats_health.connected,
            "circuit_breaker": nats_health.circuit_breaker_state,
            "active_streams": nats_health.active_streams,
        }
    else:
        result["nats"] = {"connected": False}

    # Circuit breaker health for external dependencies (WI #46)
    cb_registry = get_circuit_breaker_registry()
    cb_summary = cb_registry.health_summary()
    if cb_summary:
        result["circuit_breakers"] = {
            name: state for name, state in cb_summary.items()
        }

    # Key Vault health (WI #29)
    secret_svc = get_secret_service()
    result["key_vault"] = await secret_svc.health_check()

    return result
