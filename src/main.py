"""
Agent Red Customer Experience — FastAPI application entrypoint.

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
    title="Agent Red Customer Experience",
    description=(
        "AI-powered customer experience platform API.\n\n"
        "## Authentication\n\n"
        "Three authentication methods are supported:\n"
        "- **Shopify Session Token**: `Authorization: Bearer <jwt>` — for Shopify embedded apps\n"
        "- **API Key**: `X-API-Key: <key>` — for direct-channel merchants\n"
        "- **Widget Key**: `X-Widget-Key: pk_live_...` — for client-side chat widgets "
        "(scoped to `/api/chat/*`)\n\n"
        "## Rate Limits\n\n"
        "Per-tenant rate limits are enforced. Check `X-RateLimit-Limit`, "
        "`X-RateLimit-Remaining`, and `X-RateLimit-Reset` response headers.\n\n"
        "---\n"
        "© 2026 Remaker Digital. All rights reserved."
    ),
    version="1.0.0",
    docs_url="/docs" if os.environ.get("ENVIRONMENT") == "development" else None,
    redoc_url="/redoc" if os.environ.get("ENVIRONMENT") == "development" else None,
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "system", "description": "Health and readiness probes"},
        {"name": "checkout", "description": "Stripe Checkout session management"},
        {"name": "billing", "description": "Billing portal and usage reporting"},
        {"name": "packs", "description": "Conversation pack purchases"},
        {"name": "webhooks", "description": "Stripe and Shopify webhook handlers"},
        {"name": "shopify-billing", "description": "Shopify Billing API integration"},
        {"name": "shopify-gdpr", "description": "Shopify GDPR mandatory webhooks"},
        {"name": "dashboard", "description": "Usage dashboard and billing transparency"},
        {"name": "config", "description": "Tenant configuration management"},
        {"name": "chat", "description": "Chat API: conversations, streaming, WebSocket"},
        {"name": "admin-conversations", "description": "Conversation inbox management"},
        {"name": "admin-knowledge", "description": "Knowledge base CRUD"},
        {"name": "admin-analytics", "description": "Analytics summaries and insights"},
        {"name": "admin-team", "description": "Team member management"},
        {"name": "admin-gdpr", "description": "GDPR data export, deletion, and consent"},
        {"name": "admin-audit", "description": "Audit log query and export"},
        {"name": "admin-profiles", "description": "Customer profile management"},
        {"name": "trial", "description": "Trial tier lifecycle management"},
        {"name": "security", "description": "API key and widget key rotation"},
    ],
    responses={
        401: {"description": "Authentication required or invalid credentials"},
        403: {"description": "Tenant inactive or insufficient permissions"},
        429: {"description": "Rate limit exceeded"},
        503: {"description": "Service not initialized"},
    },
)

# ---------------------------------------------------------------------------
# Global exception handler (catches unhandled exceptions in route handlers)
# ---------------------------------------------------------------------------

import traceback  # noqa: E402

from fastapi import Request  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402


@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch and log unhandled exceptions to aid production debugging."""
    _logger = logging.getLogger("src.main")
    _logger.error(
        "Unhandled exception: path=%s method=%s error=%s\n%s",
        request.url.path, request.method, exc,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error."},
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
from src.multi_tenant.trial_management import trial_router  # noqa: E402
from src.multi_tenant.security_hardening import rotation_router  # noqa: E402
from src.multi_tenant.admin_customer_profile_api import router as admin_profile_router  # noqa: E402

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
app.include_router(trial_router)
app.include_router(rotation_router)
app.include_router(admin_profile_router)

# ---------------------------------------------------------------------------
# Shopify Embedded Admin SPA (static files + catch-all for SPA routing)
# ---------------------------------------------------------------------------

import pathlib  # noqa: E402

from fastapi.responses import FileResponse, HTMLResponse  # noqa: E402
from starlette.staticfiles import StaticFiles  # noqa: E402

_admin_shopify_dist = pathlib.Path(__file__).resolve().parent.parent / "admin" / "shopify" / "dist"

if _admin_shopify_dist.is_dir():
    # Serve static assets (JS, CSS, sourcemaps) from the Vite build output
    app.mount(
        "/admin/shopify/assets",
        StaticFiles(directory=str(_admin_shopify_dist / "assets")),
        name="admin-shopify-assets",
    )

    @app.get("/admin/shopify/{full_path:path}", include_in_schema=False)
    async def _admin_shopify_spa(full_path: str) -> FileResponse:
        """Catch-all route for the Shopify embedded admin SPA.

        All client-side routes (/, /inbox, /billing, etc.) return the same
        index.html so React Router can handle routing. This is standard SPA
        behaviour — the server always returns the shell HTML, and the
        JavaScript app determines what to render based on the URL.
        """
        return FileResponse(str(_admin_shopify_dist / "index.html"))

    @app.get("/admin/shopify", include_in_schema=False)
    async def _admin_shopify_index() -> FileResponse:
        """Serve the Shopify embedded admin SPA root."""
        return FileResponse(str(_admin_shopify_dist / "index.html"))

    logger.info("Shopify embedded admin SPA mounted at /admin/shopify")
else:
    logger.warning(
        "Shopify admin SPA dist directory not found at %s — "
        "embedded admin will not be available", _admin_shopify_dist,
    )

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
from src.multi_tenant.security_hardening import PreAuthRateLimitMiddleware  # noqa: E402

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
#   1. SecurityHeadersMiddleware    — security response headers (outermost)
#   2. ApiVersionMiddleware         — X-API-Version on every response
#   3. RequestBodyLimitMiddleware   — reject oversized payloads early
#   4. CorrelationMiddleware        — sets CorrelationContext (needs TenantContext)
#   5. JsonDepthValidationMiddleware — reject deeply nested JSON (needs body)
#   6. TenantConcurrencyMiddleware  — enforces per-tenant concurrency limits
#   7. RateLimitMiddleware          — enforces per-tenant rate limits + headers
#   8. TenantAuthMiddleware         — authenticates and injects TenantContext
#   9. PreAuthRateLimitMiddleware   — blocks IPs with excessive failed auth (WI #163)
#
# Execution order (innermost registered = runs first):
#   PreAuthRateLimitMiddleware → TenantAuthMiddleware →
#   RateLimitMiddleware → TenantConcurrencyMiddleware →
#   JsonDepthValidation → CorrelationMiddleware →
#   RequestBodyLimit → ApiVersion → SecurityHeaders → handler
# ---------------------------------------------------------------------------

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ApiVersionMiddleware)
app.add_middleware(RequestBodyLimitMiddleware)
app.add_middleware(CorrelationMiddleware)
app.add_middleware(JsonDepthValidationMiddleware)
app.add_middleware(TenantConcurrencyMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantAuthMiddleware)
app.add_middleware(PreAuthRateLimitMiddleware)


# ---------------------------------------------------------------------------
# Startup: tenant resolution configuration (Decision #4)
# ---------------------------------------------------------------------------

from src.multi_tenant.cosmos_client import get_cosmos_manager  # noqa: E402
from src.multi_tenant.repository import TenantRepository  # noqa: E402


@app.on_event("startup")
async def _startup_cosmos_db() -> None:
    """Initialize Cosmos DB client and database connection.

    Must run before any startup event that uses repositories.
    """
    try:
        cosmos = get_cosmos_manager()
        await cosmos._ensure_client()
        logger.info("Cosmos DB client initialized")
    except Exception as exc:
        logger.warning(
            "Cosmos DB initialization failed — database operations will be "
            "unavailable until connection is established: %s", exc,
        )


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


@app.on_event("shutdown")
async def _shutdown_cosmos_db() -> None:
    """Close the Cosmos DB client on application shutdown."""
    cosmos = get_cosmos_manager()
    await cosmos.close()


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
# Admin Customer Profile API (WI #142)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_customer_profile_api import configure_admin_profile_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_profile_services() -> None:
    """Initialize the Admin Customer Profile API.

    Wires CustomerProfileService into the admin profile endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.customer_profile_service import get_profile_service

        configure_admin_profile_services(profile_service=get_profile_service())
        logger.info("Admin customer profile API initialized (5 endpoints)")
    except Exception:
        logger.warning(
            "Admin customer profile initialization failed — profile endpoints "
            "will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Pattern extraction service — Layer 3 cross-session learning (WI #90-92)
# ---------------------------------------------------------------------------

from src.multi_tenant.pattern_extraction import get_pattern_service  # noqa: E402


@app.on_event("startup")
async def _startup_pattern_service() -> None:
    """Initialize the PatternExtractionService (Layer 3).

    Configures the service in dev mode (in-memory store) at startup.
    Production deployment wires a Cosmos DB pattern repository.
    Non-fatal: Layer 3 degrades gracefully when unconfigured.
    """
    try:
        service = get_pattern_service()
        service.configure()
        logger.info("PatternExtractionService initialized (Layer 3, dev mode)")
    except Exception:
        logger.warning(
            "PatternExtractionService initialization failed — Layer 3 "
            "pattern learning unavailable."
        )


# ---------------------------------------------------------------------------
# Fine-tuning pipeline service — Layer 4 dedicated model training (WI #93-96)
# ---------------------------------------------------------------------------

from src.multi_tenant.fine_tuning_pipeline import get_fine_tuning_service  # noqa: E402


@app.on_event("startup")
async def _startup_fine_tuning_service() -> None:
    """Initialize the FineTuningPipelineService (Layer 4).

    Configures the service in dev mode (in-memory store) at startup.
    Production deployment wires a Cosmos DB model repository.
    Non-fatal: Layer 4 degrades gracefully when unconfigured.
    Enterprise add-on ($299/mo) — tier-gated at the service level.
    """
    try:
        service = get_fine_tuning_service()
        service.configure()
        logger.info("FineTuningPipelineService initialized (Layer 4, dev mode)")
    except Exception:
        logger.warning(
            "FineTuningPipelineService initialization failed — Layer 4 "
            "fine-tuning pipeline unavailable."
        )


# ---------------------------------------------------------------------------
# API key rotation service (WI #159)
# ---------------------------------------------------------------------------

from src.multi_tenant.security_hardening import configure_key_rotation_services  # noqa: E402


@app.on_event("startup")
async def _startup_key_rotation() -> None:
    """Initialize the API key rotation service.

    Wires TenantSecretService and TenantRepository into the key
    rotation endpoints.
    """
    try:
        from src.multi_tenant.repository import TenantRepository

        configure_key_rotation_services(
            secret_service=get_secret_service(),
            tenant_repo=TenantRepository(),
        )
        logger.info("API key rotation service initialized (2 endpoints)")
    except Exception:
        logger.warning(
            "API key rotation initialization failed — key rotation "
            "endpoints will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Trial management service (WI #120-128)
# ---------------------------------------------------------------------------

from src.multi_tenant.trial_management import configure_trial_service  # noqa: E402
from src.multi_tenant.trial_management import TrialManagementService  # noqa: E402
from src.multi_tenant.data_retention import (  # noqa: E402
    DataRetentionService,
    configure_retention_service,
)
from src.multi_tenant.archival_pipeline import (  # noqa: E402
    ArchivalPipelineService,
    configure_archival_service,
)
from src.multi_tenant.alert_delivery import (  # noqa: E402
    AlertDeliveryService,
    DashboardAlertChannel,
    LogAlertChannel,
    configure_alert_service,
)


@app.on_event("startup")
async def _startup_trial_service() -> None:
    """Initialize the Trial Management Service.

    Wires tenant, usage, conversation, profile, knowledge, and audit
    repositories into the trial service for provisioning, expiry,
    cap enforcement, and conversion operations.
    Non-fatal: trial endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import (
            AuditLogRepository,
            ConversationRepository,
            CustomerProfileRepository,
            KnowledgeBaseRepository,
            TenantRepository,
            UsageRepository,
        )

        trial_service = TrialManagementService(
            tenant_repo=TenantRepository(),
            usage_repo=UsageRepository(),
            conversation_repo=ConversationRepository(),
            profile_repo=CustomerProfileRepository(),
            knowledge_repo=KnowledgeBaseRepository(),
            audit_repo=AuditLogRepository(),
        )
        configure_trial_service(trial_service)
        logger.info("Trial management service initialized (3 endpoints)")
    except Exception:
        logger.warning(
            "Trial management service initialization failed — trial "
            "endpoints will return 503 until dependencies are available."
        )


# ---------------------------------------------------------------------------
# Data retention enforcement service (WI #154)
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def _startup_data_retention() -> None:
    """Initialize the Data Retention Service.

    Wires tenant, conversation, profile, vector, and audit repositories
    into the retention service for automated cleanup of expired data.
    Non-fatal: retention enforcement available via scheduled trigger.
    """
    try:
        from src.multi_tenant.repository import (
            AuditLogRepository,
            ConversationRepository,
            CustomerProfileRepository,
            MemoryVectorRepository,
            TenantRepository,
        )

        retention_service = DataRetentionService(
            tenant_repo=TenantRepository(),
            conversation_repo=ConversationRepository(),
            profile_repo=CustomerProfileRepository(),
            vector_repo=MemoryVectorRepository(),
            audit_repo=AuditLogRepository(),
        )
        configure_retention_service(retention_service)
        logger.info("Data retention enforcement service initialized")
    except Exception:
        logger.warning(
            "Data retention service initialization failed — automated "
            "retention enforcement unavailable."
        )


# ---------------------------------------------------------------------------
# Archival pipeline service (WI #153)
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def _startup_archival_pipeline() -> None:
    """Initialize the Archival Pipeline Service.

    Wires tenant, conversation, profile, vector, and audit repositories
    plus an optional Blob Storage client into the archival service for
    periodic Hot→Warm data migration.
    Non-fatal: archival available via scheduled trigger.
    """
    try:
        from src.multi_tenant.repository import (
            AuditLogRepository,
            ConversationRepository,
            CustomerProfileRepository,
            MemoryVectorRepository,
            TenantRepository,
        )

        # Wire Azure Blob Storage client if connection string is available
        blob_client = None
        blob_conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
        if blob_conn:
            try:
                from azure.storage.blob import BlobServiceClient

                blob_client = BlobServiceClient.from_connection_string(blob_conn)
                logger.info("Azure Blob Storage client connected for archival")
            except Exception:
                logger.warning("Azure Blob Storage client creation failed — archival will run in dry-run mode")

        archival_service = ArchivalPipelineService(
            tenant_repo=TenantRepository(),
            conversation_repo=ConversationRepository(),
            profile_repo=CustomerProfileRepository(),
            vector_repo=MemoryVectorRepository(),
            audit_repo=AuditLogRepository(),
            blob_client=blob_client,
        )
        configure_archival_service(archival_service)
        logger.info("Archival pipeline service initialized (blob_client: %s)", "connected" if blob_client else "none — dry-run mode")
    except Exception:
        logger.warning(
            "Archival pipeline service initialization failed — "
            "archival operations unavailable."
        )


# ---------------------------------------------------------------------------
# Alert delivery service (WI #192)
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def _startup_alert_delivery() -> None:
    """Initialize the Alert Delivery Service.

    Registers built-in channels (Log + Dashboard). WebhookAlertChannel
    is registered per-tenant when merchants configure a webhook URL.
    """
    try:
        service = AlertDeliveryService()
        service.register_channel(LogAlertChannel())
        service.register_channel(DashboardAlertChannel())
        configure_alert_service(service)
        logger.info(
            "Alert delivery service initialized (%d channels)",
            len(service._channels),
        )
    except Exception:
        logger.warning(
            "Alert delivery service initialization failed — "
            "alerts will be logged only."
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

    # SLA monitoring (WI #151)
    from src.multi_tenant.sla_monitoring import get_sla_monitor

    sla_monitor = get_sla_monitor()
    result["sla"] = sla_monitor.health_summary()

    # Data retention service health (WI #154)
    from src.multi_tenant.data_retention import get_retention_service

    retention_svc = get_retention_service()
    result["data_retention"] = {"configured": retention_svc is not None}

    # API version (WI #140)
    from src.multi_tenant.api_versioning import API_VERSION

    result["version"] = API_VERSION

    return result
