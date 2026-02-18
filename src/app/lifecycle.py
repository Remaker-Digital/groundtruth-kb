"""
Agent Red Customer Experience — Application lifecycle management.

Extracted from main.py: middleware registration, startup handlers, and
shutdown handlers.  Each handler function is defined at module level so
that test code can import individual handlers directly (e.g.
``from src.app.lifecycle import _startup_tenant_resolution``).

The three public entry points are:
  - register_middleware(app)
  - register_startup_handlers(app)
  - register_shutdown_handlers(app)

Usage (called from main.py):
    from src.app.lifecycle import (
        register_middleware,
        register_startup_handlers,
        register_shutdown_handlers,
    )
    register_middleware(app)
    register_startup_handlers(app)
    register_shutdown_handlers(app)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os

from fastapi import FastAPI

from src.multi_tenant.nats_isolation import (
    close_nats_manager,
    init_nats_manager,
)
from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer
from src.multi_tenant.otel_tracing import (
    configure_logging as configure_tenant_logging,
    configure_tracing,
)
from src.multi_tenant.pipeline_resilience import get_circuit_breaker_registry
from src.multi_tenant.repository import TenantRepository
from src.multi_tenant.tenant_secret_service import get_secret_service

logger = logging.getLogger(__name__)


# =========================================================================
# Middleware registration
# =========================================================================

def register_middleware(app: FastAPI) -> None:
    """Register all middleware on *app* in the correct order.

    Starlette processes middleware in REVERSE registration order.
    Registration order (first registered = outermost = runs last):
      1. SecurityHeadersMiddleware    — security response headers (outermost)
      2. ApiVersionMiddleware         — X-API-Version on every response
      3. RequestBodyLimitMiddleware   — reject oversized payloads early
      4. CorrelationMiddleware        — sets CorrelationContext (needs TenantContext)
      5. JsonDepthValidationMiddleware — reject deeply nested JSON (needs body)
      6. TenantConcurrencyMiddleware  — enforces per-tenant concurrency limits
      7. RateLimitMiddleware          — enforces per-tenant rate limits + headers
      8. TenantAuthMiddleware         — authenticates and injects TenantContext
      9. PreAuthRateLimitMiddleware   — blocks IPs with excessive failed auth (WI #163)

    Execution order (innermost registered = runs first):
      PreAuthRateLimitMiddleware → TenantAuthMiddleware →
      RateLimitMiddleware → TenantConcurrencyMiddleware →
      JsonDepthValidation → CorrelationMiddleware →
      RequestBodyLimit → ApiVersion → SecurityHeaders → handler
    """
    from src.multi_tenant.middleware import (
        RateLimitMiddleware,
        TenantAuthMiddleware,
    )
    from src.multi_tenant.pipeline_resilience import (
        TenantConcurrencyMiddleware,
    )
    from src.multi_tenant.security_middleware import (
        JsonDepthValidationMiddleware,
        RequestBodyLimitMiddleware,
        SecurityHeadersMiddleware,
    )
    from src.multi_tenant.api_versioning import ApiVersionMiddleware
    from src.multi_tenant.security_hardening import PreAuthRateLimitMiddleware
    from src.multi_tenant.otel_tracing import (
        CorrelationMiddleware,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ApiVersionMiddleware)
    app.add_middleware(RequestBodyLimitMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(JsonDepthValidationMiddleware)
    app.add_middleware(TenantConcurrencyMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantAuthMiddleware)
    app.add_middleware(PreAuthRateLimitMiddleware)


# =========================================================================
# Startup handlers (defined at module level for direct test imports)
# =========================================================================

async def _startup_cosmos_db() -> None:
    """Initialize Cosmos DB client and database connection.

    Must run before any startup event that uses repositories.
    """
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    try:
        cosmos = get_cosmos_manager()
        await cosmos._ensure_client()
        logger.info("Cosmos DB client initialized")
    except Exception as exc:
        logger.warning(
            "Cosmos DB initialization failed — database operations will be "
            "unavailable until connection is established: %s", exc,
        )


async def _startup_tenant_resolution() -> None:
    """Configure tenant resolution functions for auth middleware.

    Wires TenantRepository and TeamMemberRepository lookup methods into
    the auth middleware so that Shopify session tokens, API keys,
    publishable widget keys, and per-user API keys can resolve to
    tenant/team-member documents in Cosmos DB.
    """
    from src.multi_tenant.middleware import configure_tenant_resolution

    try:
        tenant_repo = TenantRepository()

        # Per-user API key resolution: looks up team member by key hash,
        # then fetches the associated tenant document.
        from src.multi_tenant.repository import TeamMemberRepository
        team_repo = TeamMemberRepository()

        async def resolve_user_api_key(key_hash: str) -> dict | None:
            """Resolve a per-user API key hash to team member + tenant."""
            member = await team_repo.find_by_user_api_key_hash(key_hash)
            if member is None:
                return None
            # Fetch the tenant document for this team member
            try:
                tenant = await tenant_repo.read(
                    tenant_id=member["tenant_id"],
                    document_id=member["tenant_id"],
                )
            except Exception:
                logger.warning(
                    "User API key resolved to member %s but tenant %s not found",
                    member.get("email"), member.get("tenant_id"),
                )
                return None
            return {"team_member": member, "tenant": tenant}

        configure_tenant_resolution(
            resolve_by_shop_domain=tenant_repo.find_by_shopify_domain,
            resolve_by_api_key_hash=tenant_repo.find_by_api_key_hash,
            resolve_by_widget_key_hash=tenant_repo.find_by_widget_key_hash,
            resolve_by_user_api_key_hash=resolve_user_api_key,
        )
        # Also wire Cosmos DB fallback for /api/tenants/lookup endpoint
        from src.integrations.provisioning import configure_tenant_lookup_repo
        configure_tenant_lookup_repo(tenant_repo, team_repo=team_repo)
        logger.info("Tenant resolution configured (Cosmos DB-backed, quad auth)")
    except Exception:
        logger.warning(
            "Tenant resolution configuration failed — auth middleware will "
            "reject authenticated requests until Cosmos DB is available."
        )


async def _startup_config_processor() -> None:
    """Wire TenantConfigProcessor with Cosmos DB repositories.

    Required for config persistence via PUT /api/config. Without this,
    config updates will be rejected with an error (not silently lost).
    """
    try:
        from src.multi_tenant.repository import AuditLogRepository, PreferencesRepository
        from src.multi_tenant.tenant_config_processor import get_config_processor

        prefs_repo = PreferencesRepository()
        audit_repo = AuditLogRepository()
        processor = get_config_processor()
        processor.configure(prefs_repo, audit_repo)
        logger.info("TenantConfigProcessor configured with Cosmos DB repositories")
    except Exception as exc:
        logger.error(
            "TenantConfigProcessor configuration FAILED — config updates "
            "will be rejected until Cosmos DB is available. Error: %s",
            exc,
            exc_info=True,
        )


async def _startup_conversation_meter() -> None:
    """Create and configure the ConversationMeter singleton.

    Required before dashboard services and SSE metering can use it.
    """
    try:
        from src.multi_tenant.conversation_meter import (
            ConversationMeter,
            configure_conversation_meter,
        )
        from src.multi_tenant.repository import (
            AuditLogRepository,
            ConversationRepository,
            TenantRepository,
            UsageRepository,
        )

        meter = ConversationMeter(
            conversation_repo=ConversationRepository(),
            usage_repo=UsageRepository(),
            audit_repo=AuditLogRepository(),
            tenant_repo=TenantRepository(),
        )
        configure_conversation_meter(meter)
        logger.info("ConversationMeter singleton configured")
    except Exception:
        logger.warning(
            "ConversationMeter initialization failed — metering and "
            "dashboard services will be unavailable.",
            exc_info=True,
        )


async def _startup_dashboard_services() -> None:
    """Wire usage dashboard API with Cosmos DB repositories.

    Required for GET /api/dashboard/* endpoints to return real data.
    """
    try:
        from src.multi_tenant.usage_dashboard_api import configure_dashboard_services
        from src.multi_tenant.conversation_meter import get_conversation_meter
        from src.multi_tenant.repository import ConversationRepository

        conv_repo = ConversationRepository()
        meter = get_conversation_meter()
        configure_dashboard_services(meter, conv_repo)
        logger.info("Usage dashboard services configured")
    except Exception:
        logger.warning(
            "Dashboard services configuration failed — /api/dashboard/* "
            "endpoints will return 503 until Cosmos DB is available."
        )


async def _startup_tracing() -> None:
    """Initialize OpenTelemetry tracing with tenant context injection."""
    configure_tracing()
    configure_tenant_logging()
    logger.info("OpenTelemetry tenant-aware tracing configured")


async def _startup_circuit_breakers() -> None:
    """Pre-register default circuit breakers for external dependencies."""
    registry = get_circuit_breaker_registry()
    # Azure OpenAI and Cosmos DB breakers are auto-created on first use via
    # call_with_breaker(), but pre-registering logs their presence at startup.
    logger.info(
        "Circuit breaker registry ready — %d breakers registered",
        len(registry.health_summary()),
    )


async def _startup_nats() -> None:
    """Connect to NATS JetStream on application startup."""
    try:
        await asyncio.wait_for(init_nats_manager(), timeout=10.0)
        logger.info("NATS tenant isolation manager connected")
    except (asyncio.TimeoutError, Exception):
        # Non-fatal at startup — NATS may not be available in dev/production
        logger.warning(
            "NATS connection failed at startup — tenant messaging unavailable. "
            "Set NATS_URL environment variable to configure."
        )


async def _startup_agntcy_sdk() -> None:
    """Initialize AGNTCY SDK factory and transport on application startup."""
    try:
        from src.multi_tenant.agntcy_sdk_integration import (
            get_sdk_status,
            init_agntcy_sdk,
        )

        await init_agntcy_sdk()
        status = get_sdk_status()
        logger.info("AGNTCY SDK ready: %s", status)
    except Exception:
        # Non-fatal — SDK may not be fully configured during early phases,
        # or agntcy_app_sdk version may have breaking API changes
        logger.warning(
            "AGNTCY SDK initialization failed — platform features unavailable. "
            "This is expected if AGNTCY transport endpoints are not configured."
        )


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


async def _startup_chat_services() -> None:
    """Initialize Chat API services (session + pipeline).

    Wires ConversationSession and ChatPipeline with their dependencies.
    Non-fatal: chat endpoints return 503 if initialization fails.
    """
    from src.chat.endpoints import configure_chat_services
    from src.chat.session import configure_conversation_session
    from src.chat.pipeline import configure_chat_pipeline

    try:
        from src.multi_tenant.repository import ConversationRepository, KnowledgeBaseRepository, TeamMemberRepository
        from src.multi_tenant.customer_profile_service import get_profile_service
        from src.multi_tenant.system_prompt_builder import get_prompt_builder
        from src.chat.pipeline import USE_AGENT_CONTAINERS

        conv_repo = ConversationRepository()
        team_repo = TeamMemberRepository()
        session = configure_conversation_session(
            conversation_repo=conv_repo,
            team_repo=team_repo,
        )

        # WI #207: Create KnowledgeBaseRepository for direct retrieval
        kb_repo = KnowledgeBaseRepository()

        pipeline = configure_chat_pipeline(
            session=session,
            prompt_builder=get_prompt_builder(),
            profile_service=get_profile_service(),
            kb_repo=kb_repo,
        )

        mode = "agent containers" if USE_AGENT_CONTAINERS else "direct Azure OpenAI"
        configure_chat_services(session=session, pipeline=pipeline)

        # WI #132: Wire SSE metering callback for first-chunk billing.
        # Records first_chunk_at timestamp on the conversation document
        # when the first AI token is streamed to the client.
        try:
            from src.chat.sse_manager import get_sse_manager
            from src.multi_tenant.conversation_meter import get_conversation_meter

            sse_mgr = get_sse_manager()
            meter = get_conversation_meter()

            async def _on_first_chunk(tenant_id: str, conversation_id: str) -> None:
                await meter.record_first_chunk(tenant_id, conversation_id)

            sse_mgr.configure_metering(_on_first_chunk)
            logger.info("SSE first-chunk metering callback configured")
        except Exception:
            logger.warning(
                "SSE metering callback configuration failed — "
                "first-chunk billing will not be recorded.",
                exc_info=True,
            )

        logger.info(
            "Chat API services initialized (session + pipeline, 6 endpoints, mode=%s)",
            mode,
        )
    except Exception:
        logger.warning(
            "Chat API service initialization failed — chat endpoints will "
            "return 503 until dependencies are available."
        )


async def _startup_admin_inbox_services() -> None:
    """Initialize the Admin Conversation Inbox API.

    Wires ConversationRepository into the admin inbox endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_conversation_api import configure_admin_conversation_services

    try:
        from src.multi_tenant.repository import ConversationRepository, TeamMemberRepository

        conv_repo = ConversationRepository()
        team_repo = TeamMemberRepository()
        configure_admin_conversation_services(conversation_repo=conv_repo, team_repo=team_repo)
        logger.info("Admin conversation inbox API initialized (5 endpoints)")
    except Exception:
        logger.warning(
            "Admin conversation inbox initialization failed — admin endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_knowledge_vectorizer() -> None:
    """Initialize the Knowledge Base vectorizer for hybrid retrieval.

    Configures KnowledgeVectorizer with KnowledgeBaseRepository and
    Azure OpenAI client for embedding. Used by both the chat pipeline
    (hybrid KB retrieval) and admin knowledge API (embed on create/update).

    Non-fatal: KB retrieval falls back to empty context if unavailable.
    """
    try:
        from src.multi_tenant.repository import KnowledgeBaseRepository

        kb_repo = KnowledgeBaseRepository()
        vectorizer = get_knowledge_vectorizer()

        # Create OpenAI client for embeddings (same pattern as chat pipeline)
        openai_client = None
        from src.chat.pipeline import USE_AGENT_CONTAINERS as _use_containers
        if not _use_containers:
            try:
                from src.chat.pipeline import _create_openai_client
                openai_client = _create_openai_client()
            except Exception:
                logger.warning(
                    "Azure OpenAI client creation failed for KB vectorizer — "
                    "embeddings will use dev-mode zero vectors."
                )

        vectorizer.configure(
            kb_repo=kb_repo,
            openai_client=openai_client,
        )
        logger.info("Knowledge Base vectorizer configured (hybrid retrieval enabled)")
    except Exception as exc:
        logger.warning(
            "Knowledge Base vectorizer initialization failed — "
            "KB retrieval will be unavailable: %s", exc,
        )


async def _startup_admin_knowledge_services() -> None:
    """Initialize the Admin Knowledge Base API.

    Wires KnowledgeBaseRepository and KnowledgeVectorizer into the admin
    knowledge endpoints. Embedding is triggered on create/update.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services

    try:
        from src.multi_tenant.repository import KnowledgeBaseRepository
        from src.multi_tenant.staleness_service import get_staleness_service

        kb_repo = KnowledgeBaseRepository()
        vectorizer = get_knowledge_vectorizer()
        active_vectorizer = vectorizer if vectorizer._configured else None

        # Configure staleness service (WI #219-222)
        staleness_svc = get_staleness_service()
        staleness_svc.configure(kb_repo=kb_repo, vectorizer=active_vectorizer)

        # Configure conflict scanner
        from src.multi_tenant.kb_conflict_scanner import get_conflict_scanner
        scanner = get_conflict_scanner()
        scanner.configure(kb_repo=kb_repo)

        configure_admin_knowledge_services(
            knowledge_repo=kb_repo,
            knowledge_vectorizer=active_vectorizer,
            staleness_service=staleness_svc,
            conflict_scanner=scanner,
        )
        logger.info("Admin knowledge base API initialized (10 endpoints, vectorization+staleness+scanner enabled)")
    except Exception:
        logger.warning(
            "Admin knowledge base initialization failed — admin endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_embed_unembedded_kb() -> None:
    """Embed any KB entries that lack vector embeddings.

    Queries for all tenants with knowledge base entries, then runs
    embed_unembedded() for each tenant. This ensures articles added
    via seed scripts or admin UI (without --embed flag) get vectorized
    automatically on app boot.

    Non-fatal: if embedding fails, KB retrieval falls back to BM25-only.
    """
    try:
        vectorizer = get_knowledge_vectorizer()
        if not vectorizer._configured:
            logger.info("KB vectorizer not configured — skipping auto-embedding")
            return

        # Cross-partition query to find all tenant_ids with KB entries
        from src.multi_tenant.cosmos_client import get_cosmos_manager
        from src.multi_tenant.cosmos_schema import COLLECTION_KNOWLEDGE_BASES

        cosmos = get_cosmos_manager()
        container = cosmos.get_container(COLLECTION_KNOWLEDGE_BASES)

        tenant_ids: set[str] = set()
        async for item in container.query_items(
            query=(
                "SELECT DISTINCT c.tenant_id FROM c "
                "WHERE c.is_active = true "
                "AND (NOT IS_DEFINED(c.embedding) OR c.embedding = null)"
            ),
        ):
            tid = item.get("tenant_id")
            if tid:
                tenant_ids.add(tid)

        if not tenant_ids:
            logger.info("No unembedded KB entries found — all articles are vectorized")
            return

        total_embedded = 0
        for tenant_id in sorted(tenant_ids):
            try:
                count = await vectorizer.embed_unembedded(tenant_id)
                total_embedded += count
                if count > 0:
                    logger.info(
                        "Auto-embedded %d KB entries for tenant=%s",
                        count, tenant_id[:8],
                    )
            except Exception as exc:
                logger.warning(
                    "Auto-embedding failed for tenant=%s: %s",
                    tenant_id[:8], exc,
                )

        if total_embedded > 0:
            logger.info(
                "KB auto-embedding complete: %d entries across %d tenants",
                total_embedded, len(tenant_ids),
            )
    except Exception as exc:
        logger.warning(
            "KB auto-embedding startup task failed — "
            "unembedded entries will use BM25-only retrieval: %s", exc,
        )


async def _startup_admin_analytics_services() -> None:
    """Initialize the Admin Analytics API.

    Wires ConversationRepository into the admin analytics endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_analytics_api import configure_admin_analytics_services

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


async def _startup_admin_team_services() -> None:
    """Initialize the Admin Team Management API.

    Wires TeamMemberRepository into the admin team endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_team_api import configure_admin_team_services

    try:
        from src.multi_tenant.repository import AuditLogRepository, ConversationRepository, TeamMemberRepository

        team_repo = TeamMemberRepository()
        audit_repo = AuditLogRepository()
        conv_repo = ConversationRepository()
        configure_admin_team_services(team_repo=team_repo, audit_repo=audit_repo, conv_repo=conv_repo)
        logger.info("Admin team management API initialized (5 endpoints + audit)")
    except Exception:
        logger.warning(
            "Admin team management initialization failed — team endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_admin_gdpr_services() -> None:
    """Initialize the Admin GDPR API.

    Wires DataExportService, DataDeletionService, and ConsentManager
    into the admin GDPR endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_gdpr_api import configure_admin_gdpr_services

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


async def _startup_admin_audit_services() -> None:
    """Initialize the Admin Audit Log API.

    Wires AuditLogRepository into the admin audit endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_audit_api import configure_admin_audit_services

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


async def _startup_admin_quick_action_services() -> None:
    """Initialize the Admin Quick Action API and config-serving integration.

    Wires PreferencesRepository into:
      1. Admin CRUD endpoints (/api/admin/quick-actions)
      2. Config serving (GET /api/config quick_actions field)

    Non-fatal: admin endpoints return 503 if initialization fails;
    config serving returns quick_actions: null.
    """
    from src.multi_tenant.admin_quick_action_api import configure_admin_quick_action_services
    from src.multi_tenant.tenant_config_api import configure_quick_action_serving

    try:
        from src.multi_tenant.repository import PreferencesRepository

        prefs_repo = PreferencesRepository()
        configure_admin_quick_action_services(prefs_repo=prefs_repo)
        configure_quick_action_serving(prefs_repo=prefs_repo)
        logger.info("Admin quick action API initialized (8 endpoints + config serving)")
    except Exception:
        logger.warning(
            "Admin quick action initialization failed — quick action endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_admin_profile_services() -> None:
    """Initialize the Admin Customer Profile API.

    Wires CustomerProfileService into the admin profile endpoints.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_customer_profile_api import configure_admin_profile_services

    try:
        from src.multi_tenant.customer_profile_service import get_profile_service
        from src.multi_tenant.repository import CustomerProfileRepository

        configure_admin_profile_services(
            profile_service=get_profile_service(),
            profile_repo=CustomerProfileRepository(),
        )
        logger.info("Admin customer profile API initialized (5 endpoints)")
    except Exception:
        logger.warning(
            "Admin customer profile initialization failed — profile endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_admin_apikey_services() -> None:
    """Initialize the Admin API Key Management API.

    Wires TenantRepository + AuditLogRepository for API key CRUD.
    Non-fatal: endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.admin_apikey_api import configure_apikey_services

    try:
        from src.multi_tenant.repository import AuditLogRepository

        tenant_repo = TenantRepository()
        audit_repo = AuditLogRepository()
        configure_apikey_services(
            tenant_repo=tenant_repo,
            audit_repo=audit_repo,
        )
        logger.info("Admin API key management initialized (4 endpoints)")
    except Exception:
        logger.warning(
            "Admin API key initialization failed — API key endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_superadmin_services() -> None:
    """Initialize the Superadmin Provider Operations API.

    Wires repositories for cross-tenant queries (tenant directory,
    deployment history, billing health, ops dashboard).
    Non-fatal: superadmin endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.superadmin_api import configure_superadmin_services

    try:
        from src.multi_tenant.repository import (
            AuditLogRepository,
            ConversationRepository,
            PreferencesRepository,
            TenantRepository,
            UsageRepository,
        )

        # Optional services: NATS manager and secret service for Phase 2 endpoints
        nats_mgr = None
        try:
            from src.multi_tenant.nats_isolation import get_nats_manager
            nats_mgr = get_nats_manager()
        except Exception:
            logger.debug("NATS manager not available for superadmin API")

        secret_svc = None
        try:
            secret_svc = get_secret_service()
        except Exception:
            logger.debug("Secret service not available for superadmin API")

        configure_superadmin_services(
            tenant_repo=TenantRepository(),
            audit_repo=AuditLogRepository(),
            conv_repo=ConversationRepository(),
            usage_repo=UsageRepository(),
            prefs_repo=PreferencesRepository(),
            nats_mgr=nats_mgr,
            secret_service=secret_svc,
        )
        logger.info("Superadmin provider operations API initialized (9 endpoints)")
    except Exception:
        logger.warning(
            "Superadmin API initialization failed — provider endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_pattern_service() -> None:
    """Initialize the PatternExtractionService (Layer 3).

    Configures the service in dev mode (in-memory store) at startup.
    Production deployment wires a Cosmos DB pattern repository.
    Non-fatal: Layer 3 degrades gracefully when unconfigured.
    """
    from src.multi_tenant.pattern_extraction import get_pattern_service

    try:
        service = get_pattern_service()
        service.configure()
        logger.info("PatternExtractionService initialized (Layer 3, dev mode)")
    except Exception:
        logger.warning(
            "PatternExtractionService initialization failed — Layer 3 "
            "pattern learning unavailable."
        )


async def _startup_fine_tuning_service() -> None:
    """Initialize the FineTuningPipelineService (Layer 4).

    Configures the service in dev mode (in-memory store) at startup.
    Production deployment wires a Cosmos DB model repository.
    Non-fatal: Layer 4 degrades gracefully when unconfigured.
    Enterprise add-on ($299/mo) — tier-gated at the service level.
    """
    from src.multi_tenant.fine_tuning_pipeline import get_fine_tuning_service

    try:
        service = get_fine_tuning_service()
        service.configure()
        logger.info("FineTuningPipelineService initialized (Layer 4, dev mode)")
    except Exception:
        logger.warning(
            "FineTuningPipelineService initialization failed — Layer 4 "
            "fine-tuning pipeline unavailable."
        )


async def _startup_key_rotation() -> None:
    """Initialize the API key rotation service.

    Wires TenantSecretService and TenantRepository into the key
    rotation endpoints.
    """
    from src.multi_tenant.security_hardening import configure_key_rotation_services

    try:
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


async def _startup_trial_service() -> None:
    """Initialize the Trial Management Service.

    Wires tenant, usage, conversation, profile, knowledge, and audit
    repositories into the trial service for provisioning, expiry,
    cap enforcement, and conversion operations.
    Non-fatal: trial endpoints return 503 if initialization fails.
    """
    from src.multi_tenant.trial_management import TrialManagementService, configure_trial_service

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


async def _startup_data_retention() -> None:
    """Initialize the Data Retention Service.

    Wires tenant, conversation, profile, vector, and audit repositories
    into the retention service for automated cleanup of expired data.
    Non-fatal: retention enforcement available via scheduled trigger.
    """
    from src.multi_tenant.data_retention import (
        DataRetentionService,
        configure_retention_service,
    )

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


async def _startup_archival_pipeline() -> None:
    """Initialize the Archival Pipeline Service.

    Wires tenant, conversation, profile, vector, and audit repositories
    plus an optional Blob Storage client into the archival service for
    periodic Hot->Warm data migration.
    Non-fatal: archival available via scheduled trigger.
    """
    from src.multi_tenant.archival_pipeline import (
        ArchivalPipelineService,
        configure_archival_service,
    )

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


async def _startup_alert_delivery() -> None:
    """Initialize the Alert Delivery Service.

    Registers built-in channels: Log, Dashboard, Email.
    Email channel requires AZURE_COMM_CONNECTION_STRING or SMTP_HOST
    env var to actually send — gracefully skips if unconfigured.
    """
    from src.multi_tenant.alert_delivery import (
        AlertDeliveryService,
        DashboardAlertChannel,
        EmailAlertChannel,
        LogAlertChannel,
        WebhookAlertChannel,
        configure_alert_service,
    )

    try:
        from src.multi_tenant.repository import (
            AuditLogRepository,
            PreferencesRepository,
            TenantRepository,
        )

        service = AlertDeliveryService()

        # Log channel — always available, structured logging fallback
        service.register_channel(LogAlertChannel())

        # Dashboard channel — persists alerts to Cosmos DB audit log
        try:
            audit_repo = AuditLogRepository()
            service.register_channel(DashboardAlertChannel(audit_repo))
        except Exception:
            logger.warning(
                "DashboardAlertChannel not registered — "
                "audit log repository unavailable."
            )

        # Email channel — uses preferences + tenant repos for recipient lookup
        prefs_repo = None
        try:
            prefs_repo = PreferencesRepository()
            tenant_repo = TenantRepository()
            service.register_channel(
                EmailAlertChannel(prefs_repo, tenant_repo),
            )
        except Exception:
            logger.warning(
                "EmailAlertChannel not registered — "
                "Cosmos DB may not be available."
            )

        # Webhook channel — POSTs alerts to merchant webhook URLs
        try:
            if not prefs_repo:
                prefs_repo = PreferencesRepository()
            service.register_channel(WebhookAlertChannel(prefs_repo))
        except Exception:
            logger.warning(
                "WebhookAlertChannel not registered — "
                "preferences repository unavailable."
            )

        configure_alert_service(service)
        logger.info(
            "Alert delivery service initialized (%d channels): %s",
            len(service._channels),
            service.get_registered_channels(),
        )
    except Exception:
        logger.warning(
            "Alert delivery service initialization failed — "
            "alerts will be logged only."
        )


async def _startup_activation_service() -> None:
    """Wire ActivationService with repos + config processor.

    Required for the Save -> Activate configuration lifecycle. The service
    manages draft/active/previous config states, validation, and activation.
    """
    try:
        from src.multi_tenant.activation_service import get_activation_service
        from src.multi_tenant.repository import (
            AuditLogRepository,
            KnowledgeBaseRepository,
            PreferencesRepository,
        )
        from src.multi_tenant.tenant_config_processor import get_config_processor

        service = get_activation_service()
        service.configure(
            prefs_repo=PreferencesRepository(),
            audit_repo=AuditLogRepository(),
            kb_repo=KnowledgeBaseRepository(),
            config_processor=get_config_processor(),
        )
        logger.info("ActivationService configured (Save → Activate model)")
    except Exception as exc:
        logger.warning(
            "ActivationService configuration failed — draft/activate features "
            "will be unavailable until dependencies are ready. Error: %s",
            exc,
        )


async def _startup_migration_check() -> None:
    """Check for unapplied schema migrations (warning only, no auto-apply).

    Logs a WARNING if migrations exist that haven't been applied.
    Migrations must be applied manually via: python -m src.migrations.apply
    """
    try:
        from src.migrations.apply import MigrationRunner
        from src.multi_tenant.cosmos_client import get_cosmos_manager

        cosmos = get_cosmos_manager()
        runner = MigrationRunner(cosmos)
        pending = await runner.check_pending()
        if pending:
            logger.warning(
                "Schema migrations pending: %s. "
                "Run 'python -m src.migrations.apply' to apply.",
                [m.VERSION for m in pending],
            )
        else:
            logger.info("Schema migrations: all up to date.")
    except Exception as exc:
        logger.warning("Migration check skipped: %s", exc)


# =========================================================================
# Shutdown handlers (defined at module level for direct test imports)
# =========================================================================

async def _shutdown_nats() -> None:
    """Drain and close NATS connection on application shutdown."""
    await close_nats_manager()
    logger.info("NATS tenant isolation manager closed")


async def _shutdown_agntcy_sdk() -> None:
    """Shut down AGNTCY SDK transport on application shutdown."""
    from src.multi_tenant.agntcy_sdk_integration import close_agntcy_sdk

    await close_agntcy_sdk()
    logger.info("AGNTCY SDK shut down")


async def _shutdown_cosmos_db() -> None:
    """Close the Cosmos DB client on application shutdown."""
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    cosmos = get_cosmos_manager()
    await cosmos.close()


async def _shutdown_secret_service() -> None:
    """Close the Key Vault client."""
    service = get_secret_service()
    await service.close()
    logger.info("TenantSecretService closed")


async def _shutdown_chat_pipeline() -> None:
    """Close the ChatPipeline HTTP client."""
    from src.chat.pipeline import get_chat_pipeline

    try:
        pipeline = get_chat_pipeline()
        await pipeline.close()
        logger.info("Chat pipeline HTTP client closed")
    except Exception:
        pass


# =========================================================================
# Registration functions — called from main.py
# =========================================================================

def register_startup_handlers(app: FastAPI) -> None:
    """Register all startup event handlers on *app*.

    Handler functions are defined at module level (above) so they are
    individually importable by test code.  This function simply wires
    them into FastAPI's on_event("startup") mechanism.
    """
    app.on_event("startup")(_startup_cosmos_db)
    app.on_event("startup")(_startup_tenant_resolution)
    app.on_event("startup")(_startup_config_processor)
    app.on_event("startup")(_startup_conversation_meter)
    app.on_event("startup")(_startup_dashboard_services)
    app.on_event("startup")(_startup_tracing)
    app.on_event("startup")(_startup_circuit_breakers)
    app.on_event("startup")(_startup_nats)
    app.on_event("startup")(_startup_agntcy_sdk)
    app.on_event("startup")(_startup_secret_service)
    app.on_event("startup")(_startup_chat_services)
    app.on_event("startup")(_startup_admin_inbox_services)
    app.on_event("startup")(_startup_knowledge_vectorizer)
    app.on_event("startup")(_startup_admin_knowledge_services)
    app.on_event("startup")(_startup_embed_unembedded_kb)
    app.on_event("startup")(_startup_admin_analytics_services)
    app.on_event("startup")(_startup_admin_team_services)
    app.on_event("startup")(_startup_admin_gdpr_services)
    app.on_event("startup")(_startup_admin_audit_services)
    app.on_event("startup")(_startup_admin_quick_action_services)
    app.on_event("startup")(_startup_admin_profile_services)
    app.on_event("startup")(_startup_admin_apikey_services)
    app.on_event("startup")(_startup_superadmin_services)
    app.on_event("startup")(_startup_pattern_service)
    app.on_event("startup")(_startup_fine_tuning_service)
    app.on_event("startup")(_startup_key_rotation)
    app.on_event("startup")(_startup_trial_service)
    app.on_event("startup")(_startup_data_retention)
    app.on_event("startup")(_startup_archival_pipeline)
    app.on_event("startup")(_startup_alert_delivery)
    app.on_event("startup")(_startup_activation_service)
    app.on_event("startup")(_startup_migration_check)


def register_shutdown_handlers(app: FastAPI) -> None:
    """Register all shutdown event handlers on *app*.

    Handler functions are defined at module level (above) so they are
    individually importable by test code.
    """
    app.on_event("shutdown")(_shutdown_nats)
    app.on_event("shutdown")(_shutdown_agntcy_sdk)
    app.on_event("shutdown")(_shutdown_cosmos_db)
    app.on_event("shutdown")(_shutdown_secret_service)
    app.on_event("shutdown")(_shutdown_chat_pipeline)
