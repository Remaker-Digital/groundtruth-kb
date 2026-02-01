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
# Logging (WI #149 — structured logging)
# ---------------------------------------------------------------------------

from src.multi_tenant.structured_logging import configure_structured_logging  # noqa: E402

configure_structured_logging()
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
from src.chat.endpoints import router as chat_router  # noqa: E402
from src.multi_tenant.admin_conversation_api import router as admin_inbox_router  # noqa: E402
from src.multi_tenant.admin_knowledge_api import router as admin_knowledge_router  # noqa: E402
from src.multi_tenant.admin_analytics_api import router as admin_analytics_router  # noqa: E402
from src.multi_tenant.admin_team_api import router as admin_team_router  # noqa: E402
from src.multi_tenant.admin_gdpr_api import router as admin_gdpr_router  # noqa: E402
from src.integrations.shopify_gdpr_webhooks import router as shopify_gdpr_router  # noqa: E402
from src.multi_tenant.admin_audit_api import router as admin_audit_router  # noqa: E402

app.include_router(provisioning_router)
app.include_router(checkout_router)
app.include_router(packs_router)
app.include_router(portal_router)
app.include_router(usage_router)
app.include_router(webhooks_router)
app.include_router(shopify_billing_router)
app.include_router(dashboard_router)
app.include_router(config_router)
app.include_router(chat_router)
app.include_router(admin_inbox_router)
app.include_router(admin_knowledge_router)
app.include_router(admin_analytics_router)
app.include_router(admin_team_router)
app.include_router(admin_gdpr_router)
app.include_router(shopify_gdpr_router)
app.include_router(admin_audit_router)

# ---------------------------------------------------------------------------
# Tenant authentication + rate limiting (Decisions #4-5, WI #18/#27-28)
# ---------------------------------------------------------------------------

from src.multi_tenant.middleware import (  # noqa: E402
    RateLimitMiddleware,
    TenantAuthMiddleware,
    configure_tenant_resolution,
)

# ---------------------------------------------------------------------------
# Pipeline resilience — concurrency control + circuit breakers (WI #44-46)
# ---------------------------------------------------------------------------

from src.multi_tenant.pipeline_resilience import (  # noqa: E402
    TenantConcurrencyMiddleware,
    get_circuit_breaker_registry,
)

# ---------------------------------------------------------------------------
# Security middleware — body limits, JSON depth, security headers (WI #157-159)
# ---------------------------------------------------------------------------

from src.multi_tenant.security_middleware import (  # noqa: E402
    JsonDepthValidationMiddleware,
    RequestBodyLimitMiddleware,
    SecurityHeadersMiddleware,
)

# ---------------------------------------------------------------------------
# API versioning middleware (WI #140)
# ---------------------------------------------------------------------------

from src.multi_tenant.api_versioning import ApiVersionMiddleware  # noqa: E402

# ---------------------------------------------------------------------------
# OpenTelemetry tenant-aware tracing (Work Items #39-40)
# ---------------------------------------------------------------------------

from src.multi_tenant.otel_tracing import (  # noqa: E402
    CorrelationMiddleware,
    configure_logging as configure_tenant_logging,
    configure_tracing,
)

# ---------------------------------------------------------------------------
# Middleware stack
#
# Starlette processes middleware in REVERSE registration order.
# Registration order (first registered = outermost = runs last):
#   1. SecurityHeadersMiddleware   — security response headers (outermost)
#   2. ApiVersionMiddleware        — X-API-Version on every response
#   3. RequestBodyLimitMiddleware  — reject oversized payloads early
#   4. CorrelationMiddleware       — sets CorrelationContext (needs TenantContext)
#   5. JsonDepthValidationMiddleware — reject deeply nested JSON (needs body)
#   6. TenantConcurrencyMiddleware — enforces per-tenant concurrency limits
#   7. RateLimitMiddleware         — enforces per-tenant rate limits + headers
#   8. TenantAuthMiddleware        — authenticates and injects TenantContext
#
# Execution order (innermost registered = runs first):
#   TenantAuthMiddleware → RateLimitMiddleware →
#   TenantConcurrencyMiddleware → JsonDepthValidation →
#   CorrelationMiddleware → RequestBodyLimit →
#   ApiVersion → SecurityHeaders → handler
# ---------------------------------------------------------------------------

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ApiVersionMiddleware)
app.add_middleware(RequestBodyLimitMiddleware)
app.add_middleware(CorrelationMiddleware)
app.add_middleware(JsonDepthValidationMiddleware)
app.add_middleware(TenantConcurrencyMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantAuthMiddleware)


# ---------------------------------------------------------------------------
# Startup: tenant resolution configuration (Decision #4)
# ---------------------------------------------------------------------------

from src.multi_tenant.repository import TenantRepository  # noqa: E402


@app.on_event("startup")
async def _startup_tenant_resolution() -> None:
    """Configure tenant resolution functions for auth middleware.

    Wires TenantRepository lookup methods into the auth middleware so
    that Shopify session tokens, API keys, and publishable widget keys
    can resolve to tenant documents in Cosmos DB.
    """
    try:
        tenant_repo = TenantRepository()
        configure_tenant_resolution(
            resolve_by_shop_domain=tenant_repo.find_by_shopify_domain,
            resolve_by_api_key_hash=tenant_repo.find_by_api_key_hash,
            resolve_by_widget_key_hash=tenant_repo.find_by_widget_key_hash,
        )
        logger.info("Tenant resolution configured (Cosmos DB-backed, triple auth)")
    except Exception:
        logger.warning(
            "Tenant resolution configuration failed — auth middleware will "
            "reject authenticated requests until Cosmos DB is available."
        )


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
# Chat API services (WI #164-169, #182)
# ---------------------------------------------------------------------------

from src.chat.endpoints import configure_chat_services  # noqa: E402
from src.chat.session import ConversationSession, configure_conversation_session  # noqa: E402
from src.chat.pipeline import ChatPipeline, configure_chat_pipeline  # noqa: E402


@app.on_event("startup")
async def _startup_chat_services() -> None:
    """Initialize Chat API services (session + pipeline).

    Wires ConversationSession and ChatPipeline with their dependencies.
    Non-fatal: chat endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import ConversationRepository
        from src.multi_tenant.customer_profile_service import get_profile_service
        from src.multi_tenant.system_prompt_builder import get_prompt_builder

        conv_repo = ConversationRepository()
        session = configure_conversation_session(
            conversation_repo=conv_repo,
        )

        pipeline = configure_chat_pipeline(
            session=session,
            prompt_builder=get_prompt_builder(),
            profile_service=get_profile_service(),
        )

        configure_chat_services(session=session, pipeline=pipeline)
        logger.info(
            "Chat API services initialized (session + pipeline, 6 endpoints)"
        )
    except Exception:
        logger.warning(
            "Chat API service initialization failed — chat endpoints will "
            "return 503 until dependencies are available."
        )


@app.on_event("shutdown")
async def _shutdown_chat_pipeline() -> None:
    """Close the ChatPipeline HTTP client."""
    from src.chat.pipeline import get_chat_pipeline

    try:
        pipeline = get_chat_pipeline()
        await pipeline.close()
        logger.info("Chat pipeline HTTP client closed")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Admin Conversation Inbox API (WI #171)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_conversation_api import configure_admin_conversation_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_inbox_services() -> None:
    """Initialize the Admin Conversation Inbox API.

    Wires ConversationRepository into the admin inbox endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import ConversationRepository

        conv_repo = ConversationRepository()
        configure_admin_conversation_services(conversation_repo=conv_repo)
        logger.info("Admin conversation inbox API initialized (5 endpoints)")
    except Exception:
        logger.warning(
            "Admin conversation inbox initialization failed — admin endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Admin Knowledge Base API (WI #175)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_knowledge_services() -> None:
    """Initialize the Admin Knowledge Base API.

    Wires KnowledgeBaseRepository into the admin knowledge endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import KnowledgeBaseRepository

        kb_repo = KnowledgeBaseRepository()
        configure_admin_knowledge_services(knowledge_repo=kb_repo)
        logger.info("Admin knowledge base API initialized (5 endpoints)")
    except Exception:
        logger.warning(
            "Admin knowledge base initialization failed — admin endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Admin Analytics API (WI #176-178)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_analytics_api import configure_admin_analytics_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_analytics_services() -> None:
    """Initialize the Admin Analytics API.

    Wires ConversationRepository into the admin analytics endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import ConversationRepository

        conv_repo = ConversationRepository()
        configure_admin_analytics_services(conversation_repo=conv_repo)
        logger.info("Admin analytics API initialized (3 endpoints)")
    except Exception:
        logger.warning(
            "Admin analytics initialization failed — analytics endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Admin Team Management API (WI #179)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_team_api import configure_admin_team_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_team_services() -> None:
    """Initialize the Admin Team Management API.

    Wires TeamMemberRepository into the admin team endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import TeamMemberRepository

        team_repo = TeamMemberRepository()
        configure_admin_team_services(team_repo=team_repo)
        logger.info("Admin team management API initialized (5 endpoints)")
    except Exception:
        logger.warning(
            "Admin team management initialization failed — team endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Admin GDPR API (WI #180)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_gdpr_api import configure_admin_gdpr_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_gdpr_services() -> None:
    """Initialize the Admin GDPR API.

    Wires DataExportService, DataDeletionService, and ConsentManager
    into the admin GDPR endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.gdpr_services import (
            ConsentManager,
            DataDeletionService,
            DataExportService,
            DataStoreRegistry,
        )
        from src.multi_tenant.repository import (
            CustomerProfileRepository,
            TenantRepository,
        )

        tenant_repo = TenantRepository()
        profile_repo = CustomerProfileRepository()

        registry = DataStoreRegistry()
        # Note: CosmosDataStoreAdapter and NATSDataStoreAdapter registration
        # requires all 7+ repository instances — deferred to full GDPR init.
        # For now, the registry starts empty; export/delete will report
        # no stores until adapters are registered.

        export_service = DataExportService(registry=registry)
        deletion_service = DataDeletionService(
            registry=registry,
            tenant_repo=tenant_repo,
        )
        consent_manager = ConsentManager(
            tenant_repo=tenant_repo,
            customer_profile_repo=profile_repo,
            deletion_service=deletion_service,
        )

        configure_admin_gdpr_services(
            export_service=export_service,
            deletion_service=deletion_service,
            consent_manager=consent_manager,
            tenant_repo=tenant_repo,
        )
        logger.info("Admin GDPR API initialized (5 endpoints)")

        # Also wire the same services into the Shopify GDPR webhooks (WI #35)
        from src.integrations.shopify_gdpr_webhooks import configure_shopify_gdpr_services  # noqa: E402

        configure_shopify_gdpr_services(
            export_service=export_service,
            deletion_service=deletion_service,
            tenant_repo=tenant_repo,
        )
        logger.info("Shopify GDPR webhooks initialized (3 endpoints)")
    except Exception:
        logger.warning(
            "Admin GDPR initialization failed — GDPR endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Admin Audit Log API (WI #141)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_audit_api import configure_admin_audit_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_audit_services() -> None:
    """Initialize the Admin Audit Log API.

    Wires AuditLogRepository into the admin audit endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import AuditLogRepository

        audit_repo = AuditLogRepository()
        configure_admin_audit_services(audit_repo=audit_repo)
        logger.info("Admin audit log API initialized (2 endpoints)")
    except Exception:
        logger.warning(
            "Admin audit log initialization failed — audit endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness probe — returns 200 if the process is running."""
    from src.multi_tenant.api_versioning import API_VERSION

    return {"status": "healthy", "version": API_VERSION}


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

    # Tenant usage monitor health (WI #51)
    from src.multi_tenant.tenant_usage_monitor import get_usage_monitor

    usage_monitor = get_usage_monitor()
    result["usage_monitor"] = usage_monitor.health_summary()

    # SSE connection manager health (WI #129)
    from src.chat.sse_manager import get_sse_manager

    sse_mgr = get_sse_manager()
    result["sse_connections"] = sse_mgr.health_summary()

    # API version (WI #140)
    from src.multi_tenant.api_versioning import API_VERSION

    result["version"] = API_VERSION

    return result
