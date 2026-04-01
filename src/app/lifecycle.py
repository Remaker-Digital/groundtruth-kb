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


# ---------------------------------------------------------------------------
# Pre-fork secret generation (SPEC-1846 fix)
# ---------------------------------------------------------------------------
# When uvicorn runs with --workers N, the parent process imports this module,
# HMAC verification secret for VerificationRunner (SPEC-1846).
#
# CRITICAL: With uvicorn --workers 4, each worker is a separate process.
# os.environ changes made at import time in the parent do NOT reliably
# propagate to forked workers (confirmed by diagnostic logging: 4 workers
# each had different secret fingerprints).
#
# Solution: Use a shared temp file as a cross-worker secret store.
# The first process to start writes the secret; all others read it.
# The file is in /tmp (container-local, not shared across replicas).
_VERIFICATION_SECRET_PATH = "/tmp/.agent-red-verification-secret"

def _ensure_verification_secret() -> str:
    """Ensure INTERNAL_VERIFICATION_SECRET is set consistently across all workers.

    Uses a temp file as a cross-worker coordination mechanism:
    1. If env var already set (e.g., by Azure config), use it.
    2. If temp file exists, read secret from it.
    3. Otherwise, generate a new secret, write to file, set env var.
    """
    import secrets as _secrets

    # Explicit env var takes priority (e.g., set in Azure Container App config)
    existing = os.environ.get("INTERNAL_VERIFICATION_SECRET", "")
    if existing:
        return existing

    # Try reading from shared temp file (written by first worker/parent)
    try:
        with open(_VERIFICATION_SECRET_PATH, "r") as f:
            secret = f.read().strip()
            if secret:
                os.environ["INTERNAL_VERIFICATION_SECRET"] = secret
                logger.info("Loaded INTERNAL_VERIFICATION_SECRET from shared file")
                return secret
    except FileNotFoundError:
        pass

    # First process: generate and write
    secret = _secrets.token_hex(32)
    try:
        with open(_VERIFICATION_SECRET_PATH, "w") as f:
            f.write(secret)
        os.chmod(_VERIFICATION_SECRET_PATH, 0o600)  # Owner-only read/write
    except OSError:
        logger.warning("Could not write verification secret to %s", _VERIFICATION_SECRET_PATH)

    os.environ["INTERNAL_VERIFICATION_SECRET"] = secret
    logger.info("Generated INTERNAL_VERIFICATION_SECRET (written to shared file)")
    return secret

_ensure_verification_secret()



# =========================================================================
# Middleware registration
# =========================================================================

def register_middleware(app: FastAPI) -> None:
    """Register all middleware on *app* in the correct order.

    In Starlette/FastAPI, the **last** middleware added via
    ``app.add_middleware()`` becomes the **outermost** — it processes
    requests first and responses last.

    Registration order (last added = outermost = processes requests first):

      Inner (closest to route handler):
        1. SecurityHeadersMiddleware    — security response headers
        2. ApiVersionMiddleware         — X-API-Version on every response
        3. RequestBodyLimitMiddleware   — reject oversized payloads early
        4. CorrelationMiddleware        — sets CorrelationContext
        5. JsonDepthValidationMiddleware — reject deeply nested JSON
        6. TenantConcurrencyMiddleware  — per-tenant concurrency limits
        7. RateLimitMiddleware          — per-tenant RPM limiting (SPEC-1803)
        8. TenantAuthMiddleware         — authenticates, injects TenantContext
        9. TrustedProxyMiddleware       — extract real client IP from headers
      Outer (processes requests first, responses last):
       10. CORSMiddleware               — CORS headers on ALL responses

    Execution order (request → handler):
      CORSMiddleware → TrustedProxy →
      TenantAuthMiddleware → RateLimitMiddleware →
      TenantConcurrencyMiddleware →
      JsonDepthValidation → CorrelationMiddleware →
      RequestBodyLimit → ApiVersion → SecurityHeaders → handler

    SPEC-1805: RATE_LIMIT_DISABLED=true skips RateLimitMiddleware registration.
    CRITICAL: CORSMiddleware MUST be outermost so that CORS headers
    appear on every response — including 401 (auth failure) and
    503 (service unavailable).
    """
    import os

    from fastapi.middleware.cors import CORSMiddleware

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
        TrustedProxyMiddleware,
    )
    from src.multi_tenant.api_versioning import ApiVersionMiddleware
    from src.multi_tenant.otel_tracing import (
        CorrelationMiddleware,
    )

    # --- Inner middleware (closest to route handler) ---
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ApiVersionMiddleware)
    app.add_middleware(RequestBodyLimitMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(JsonDepthValidationMiddleware)
    app.add_middleware(TenantConcurrencyMiddleware)

    # SPEC-1803/1805: Per-tenant rate limiting — skipped when RATE_LIMIT_DISABLED=true
    # This env var should be set on staging to allow load testing without interference.
    if os.environ.get("RATE_LIMIT_DISABLED", "").lower() != "true":
        app.add_middleware(RateLimitMiddleware)

    app.add_middleware(TenantAuthMiddleware)

    # --- TrustedProxy: extracts real client IP from X-Forwarded-For/CF-Connecting-IP ---
    app.add_middleware(TrustedProxyMiddleware)

    # --- CORS: outermost middleware ---
    # Must be added LAST so it wraps ALL other middleware.
    # This ensures CORS headers appear on 429, 401, 403, 503 responses
    # from rate limiting, auth, and other middleware — not just 200s.
    _cors_origins = os.environ.get("APP_CORS_ORIGINS", "").split(",")
    _cors_origins = [o.strip() for o in _cors_origins if o.strip()]
    _cors_origin_regex = os.environ.get(
        "APP_CORS_ORIGIN_REGEX",
        # Allow any Shopify storefront, our own gateway, and localhost for dev
        r"https://.*\.myshopify\.com|https://.*\.azurecontainerapps\.io|http://localhost:\d+",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins,
        allow_origin_regex=_cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-API-Version", "X-Product-Version", "X-API-Deprecation-Notice"],
    )


# =========================================================================
# Startup handlers (defined at module level for direct test imports)
# =========================================================================

async def _startup_verification_secret() -> None:
    """Ensure INTERNAL_VERIFICATION_SECRET is available in this worker (SPEC-1846).

    Delegates to _ensure_verification_secret() which coordinates across
    workers via a shared temp file.
    """
    secret = _ensure_verification_secret()
    import hashlib as _hl
    fp = _hl.sha256(secret.encode()).hexdigest()[:12]
    logger.info("INTERNAL_VERIFICATION_SECRET ready: fp=%s pid=%d", fp, os.getpid())


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

        # SPEC-1644: Cross-partition user key resolution removed.
        # Per-user keys now use verify_user_key_in_partition (below).
        # This placeholder returns None to satisfy the middleware signature
        # while the partition-scoped resolver handles all real auth.
        async def resolve_user_api_key(key_hash: str) -> dict | None:
            """DEPRECATED — cross-partition user key lookup removed (SPEC-1644)."""
            logger.warning(
                "Cross-partition user key lookup attempted — "
                "this path is deprecated (SPEC-1644). Use partition-scoped auth."
            )
            return None

        async def resolve_by_tenant_id(tid: str) -> dict | None:
            """Resolve tenant by ID using pooled repository."""
            try:
                return await tenant_repo.read(tid, tid)
            except Exception:
                return None

        # SPA platform admin key resolution (SPEC-1667):
        # Resolves ar_spa_* keys from the platform_admins collection,
        # completely isolated from all tenant team_members collections.
        from src.multi_tenant.repositories.platform_admin import PlatformAdminRepository
        platform_admin_repo = PlatformAdminRepository()

        async def resolve_spa_api_key(key_hash: str) -> dict | None:
            """Resolve an SPA API key hash to a platform admin document."""
            return await platform_admin_repo.find_by_api_key_hash(key_hash)

        # SPEC-1644: Partition-scoped API key verification.
        # These closures read within a single Cosmos partition — no
        # cross-partition scan.  The caller must already know the tenant.
        async def verify_api_key_in_partition(
            tenant_id: str, key_hash: str,
        ) -> dict | None:
            """Verify a tenant API key hash within one partition."""
            return await tenant_repo.verify_key_hash(tenant_id, key_hash)

        async def verify_user_key_in_partition(
            tenant_id: str, key_hash: str,
        ) -> dict | None:
            """Verify a per-user API key hash within one partition."""
            member = await team_repo.verify_user_key_hash(tenant_id, key_hash)
            if member is None:
                return None
            try:
                tenant = await tenant_repo.read(
                    tenant_id=tenant_id,
                    document_id=tenant_id,
                )
            except Exception:
                logger.warning(
                    "User key resolved to member %s but tenant %s not found",
                    member.get("email"), tenant_id,
                )
                return None
            return {"team_member": member, "tenant": tenant}

        # SPEC-1644: Cross-partition API key lookup removed.
        # Tenant/user keys now use partition-scoped resolvers.
        # This stub satisfies the middleware signature.
        async def _deprecated_api_key_lookup(key_hash: str) -> dict | None:
            logger.warning(
                "Cross-partition API key lookup attempted — "
                "this path is deprecated (SPEC-1644). Use partition-scoped auth."
            )
            return None

        # SPEC-1644: Domain index for O(1) lookups (no cross-partition queries)
        from src.multi_tenant.repositories.domain_index import DomainIndexRepository
        domain_index_repo = DomainIndexRepository()

        async def resolve_by_shop_domain(shop_domain: str) -> dict | None:
            """Resolve shop domain using domain index (O(1) point read).

            Falls back to cross-partition query if domain index miss.
            """
            # Try domain index first — single-partition point read
            try:
                tid = await domain_index_repo.lookup(shop_domain)
                if tid:
                    return await tenant_repo.read(tid, tid)
            except Exception:
                pass
            # Fallback: cross-partition query (legacy, will be removed)
            return await tenant_repo.find_by_shopify_domain(shop_domain)

        configure_tenant_resolution(
            resolve_by_shop_domain=resolve_by_shop_domain,
            resolve_by_api_key_hash=_deprecated_api_key_lookup,
            resolve_by_widget_key_hash=tenant_repo.find_by_widget_key_hash,
            resolve_by_user_api_key_hash=resolve_user_api_key,
            resolve_by_tenant_id=resolve_by_tenant_id,
            resolve_by_spa_key_hash=resolve_spa_api_key,
            verify_api_key_in_partition=verify_api_key_in_partition,
            verify_user_key_in_partition=verify_user_key_in_partition,
        )
        # Wire Cosmos DB as the primary persistence layer for provisioning
        from src.integrations.provisioning import configure_provisioning_repo
        configure_provisioning_repo(
            tenant_repo, team_repo=team_repo,
            domain_index_repo=domain_index_repo,
        )
        logger.info("Tenant resolution configured (Cosmos DB-backed, quad auth, domain index)")
    except Exception as exc:
        logger.warning(
            "Tenant resolution configuration failed — auth middleware will "
            "reject authenticated requests until Cosmos DB is available. "
            "Error: %s", exc,
        )
        # Best-effort: even if full resolution fails, try to wire the SPA
        # resolver so the platform admin console is not locked out.
        try:
            from src.multi_tenant.repositories.platform_admin import PlatformAdminRepository
            _pa_repo = PlatformAdminRepository()

            async def _fallback_spa_key(key_hash: str) -> dict | None:
                return await _pa_repo.find_by_api_key_hash(key_hash)

            async def _noop(*_args, **_kwargs) -> None:
                return None

            configure_tenant_resolution(
                resolve_by_shop_domain=_noop,
                resolve_by_api_key_hash=_noop,
                resolve_by_spa_key_hash=_fallback_spa_key,
            )
            logger.info(
                "Fallback SPA-only auth configured — platform admin console "
                "available, merchant auth unavailable."
            )
        except Exception as inner:
            logger.error("Fallback SPA auth also failed: %s", inner)


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
    """Initialize OpenTelemetry tracing with tenant context injection.

    Uses Application Insights exporter when APPLICATIONINSIGHTS_CONNECTION_STRING
    is set (SPEC-1834). Falls back to console exporter otherwise.
    """
    from src.multi_tenant.otel_application_insights import (
        configure_tracing_with_app_insights,
    )

    result = configure_tracing_with_app_insights()
    configure_tenant_logging()

    if result["configured"]:
        logger.info(
            "OpenTelemetry tracing configured with Application Insights "
            "(sampling_rate=%.2f)",
            result["sampling_rate"],
        )
    else:
        logger.info("OpenTelemetry tracing configured (console exporter)")


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
        logger.info("AGNTCY SDK startup: importing agntcy_sdk_integration...")
        from src.multi_tenant.agntcy_sdk_integration import (
            get_sdk_status,
            init_agntcy_sdk,
        )
        logger.info("AGNTCY SDK startup: import OK, calling init_agntcy_sdk()...")
        await init_agntcy_sdk()
        status = get_sdk_status()
        logger.info("AGNTCY SDK ready: %s", status)
    except Exception:
        # Non-fatal — SDK may not be fully configured during early phases,
        # or agntcy_app_sdk version may have breaking API changes
        logger.warning(
            "AGNTCY SDK initialization failed — platform features unavailable. "
            "This is expected if AGNTCY transport endpoints are not configured.",
            exc_info=True,
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


async def _startup_envelope_encryption() -> None:
    """Initialize the EnvelopeEncryptionService (SPEC-1843 / WI-1631).

    In dev mode (no MASTER_KEK_KEY_ID), uses an in-memory test KEK.
    In staging/production, connects to Azure Key Vault for the Master KEK.

    Fail-closed (S251): In non-development environments, missing
    MASTER_KEK_KEY_ID is a fatal startup error. This prevents silent
    degradation to insecure dev-mode encryption in production.
    """
    from src.multi_tenant.envelope_encryption import (
        EnvelopeEncryptionService,
        set_envelope_encryption_service,
    )

    kek_key_id = os.environ.get("MASTER_KEK_KEY_ID")
    vault_url = os.environ.get("AZURE_KEYVAULT_URL")
    environment = os.environ.get("ENVIRONMENT", "development").lower().strip()
    dev_mode = not kek_key_id

    # S251 fail-closed: refuse to start without KEK in non-dev environments
    if dev_mode and environment in ("staging", "production"):
        logger.critical(
            "MASTER_KEK_KEY_ID is not set in %s environment. "
            "Refusing to start — field-level encryption would fall back to "
            "insecure dev-mode KEK. Set MASTER_KEK_KEY_ID to the Key Vault "
            "key versionless ID (e.g., https://<vault>/keys/agent-red-cmk).",
            environment,
        )
        raise RuntimeError(
            f"MASTER_KEK_KEY_ID required in {environment} environment"
        )

    try:
        svc = EnvelopeEncryptionService(
            dev_mode=dev_mode,
            kek_key_id=kek_key_id,
            vault_url=vault_url,
        )
        set_envelope_encryption_service(svc)
        mode_label = "DEV MODE" if dev_mode else f"KEK={kek_key_id}"
        logger.info("EnvelopeEncryptionService initialized (%s)", mode_label)
    except Exception:
        logger.warning(
            "EnvelopeEncryptionService initialization failed — "
            "field-level encryption unavailable"
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

        # Initialize CriticPolicy with Critic container URL (fail-closed safety).
        # Without CriticPolicy, every AI response is replaced with SAFE_FALLBACK_MESSAGE.
        critic = None
        try:
            from src.multi_tenant.critic_policy import CriticPolicy
            from src.chat.pipeline.constants import AGENT_URLS
            critic_url = AGENT_URLS.get("critic-supervisor", "")
            if critic_url:
                critic = CriticPolicy(critic_urls=[critic_url])
                logger.info("CriticPolicy initialized with URL: %s", critic_url)
            else:
                logger.warning("Critic URL not configured — CriticPolicy disabled (fail-closed)")
        except Exception as exc:
            logger.warning("CriticPolicy initialization failed — fail-closed: %s", exc)

        pipeline = configure_chat_pipeline(
            session=session,
            prompt_builder=get_prompt_builder(),
            profile_service=get_profile_service(),
            kb_repo=kb_repo,
            critic=critic,
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
            "return 503 until dependencies are available.",
            exc_info=True,
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


async def _startup_conversation_vectorizer() -> None:
    """Initialize the Conversation Vectorizer for Layer 2 memory.

    Configures ConversationVectorizer singleton with MemoryVectorRepository,
    Azure OpenAI client (for embeddings), and PiiScrubber.
    Non-fatal: vectorization scanner will skip if not configured.
    """
    try:
        from src.multi_tenant.conversation_vectorizer import get_vectorizer
        from src.multi_tenant.repository import MemoryVectorRepository
        from src.multi_tenant.gdpr_services import PiiScrubber

        vector_repo = MemoryVectorRepository()
        vectorizer = get_vectorizer()

        # Create OpenAI client for embeddings (same pattern as KB vectorizer)
        openai_client = None
        from src.chat.pipeline import USE_AGENT_CONTAINERS as _use_containers
        if not _use_containers:
            try:
                from src.chat.pipeline import _create_openai_client
                openai_client = _create_openai_client()
            except Exception:
                logger.warning(
                    "Azure OpenAI client creation failed for conversation vectorizer — "
                    "embeddings will use dev-mode zero vectors."
                )

        pii_scrubber = PiiScrubber()

        vectorizer.configure(
            vector_repo=vector_repo,
            openai_client=openai_client,
            pii_scrubber=pii_scrubber,
        )
        logger.info("ConversationVectorizer configured (Layer 2 memory)")
    except Exception as exc:
        logger.warning(
            "ConversationVectorizer initialization failed — "
            "Layer 2 memory vectorization unavailable: %s", exc,
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

        from src.multi_tenant.repositories.domain_index import DomainIndexRepository
        configure_shopify_gdpr_services(
            export_service=export_service,
            deletion_service=deletion_service,
            tenant_repo=tenant_repo,
            domain_index_repo=DomainIndexRepository(),
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

        # Incident + alert repositories for Phase B/C endpoints
        incident_repo = None
        alert_rule_repo = None
        alert_history_repo = None
        try:
            from src.multi_tenant.repositories.incidents import IncidentRepository
            from src.multi_tenant.repositories.alerts import (
                AlertRuleRepository,
                AlertHistoryRepository,
            )
            incident_repo = IncidentRepository()
            alert_rule_repo = AlertRuleRepository()
            alert_history_repo = AlertHistoryRepository()
        except Exception:
            logger.debug("Incident/alert repositories not available for superadmin API")

        # Platform admin repository for SPEC-1669 key regeneration
        pa_repo = None
        try:
            from src.multi_tenant.repositories.platform_admin import PlatformAdminRepository
            pa_repo = PlatformAdminRepository()
        except Exception:
            logger.debug("PlatformAdminRepository not available for superadmin API")

        configure_superadmin_services(
            tenant_repo=TenantRepository(),
            audit_repo=AuditLogRepository(),
            conv_repo=ConversationRepository(),
            usage_repo=UsageRepository(),
            prefs_repo=PreferencesRepository(),
            nats_mgr=nats_mgr,
            secret_service=secret_svc,
            incident_repo=incident_repo,
            alert_rule_repo=alert_rule_repo,
            alert_history_repo=alert_history_repo,
            platform_admin_repo=pa_repo,
        )
        logger.info("Superadmin provider operations API initialized (18 endpoints)")

        # SPEC-1678: Wire SPA recovery module with same repos
        try:
            from src.multi_tenant.spa_recovery import configure_spa_recovery
            configure_spa_recovery(
                platform_admin_repo=pa_repo,
                audit_repo=AuditLogRepository(),
            )
            logger.info("SPA recovery module initialized (SPEC-1678)")
        except Exception:
            logger.debug("SPA recovery initialization failed — recovery endpoint unavailable")

        # SPEC-1677: Wire tenant account recovery module
        try:
            from src.multi_tenant.tenant_recovery import configure_tenant_recovery
            from src.multi_tenant.repositories.verification import VerificationTokenRepository
            configure_tenant_recovery(
                tenant_repo=TenantRepository(),
                verification_repo=VerificationTokenRepository(),
                audit_repo=AuditLogRepository(),
            )
            logger.info("Tenant recovery module initialized (SPEC-1677)")
        except Exception:
            logger.debug("Tenant recovery initialization failed — recovery endpoint unavailable")
    except Exception:
        logger.warning(
            "Superadmin API initialization failed — provider endpoints "
            "will return 503 until dependencies are available."
        )


async def _startup_contact_messages() -> None:
    """Initialize the Contact Messages persistence layer (SPEC-1588).

    Wires a TenantScopedRepository for contact_messages into the
    admin contact API so submissions are persisted to Cosmos DB.
    Non-fatal: contact form still delivers email if persistence fails.
    """
    from src.multi_tenant.admin_contact_api import configure_contact_repo
    from src.multi_tenant.superadmin_contact_api import configure_superadmin_contact_services

    try:
        from src.multi_tenant.cosmos_schema import COLLECTION_CONTACT_MESSAGES
        from src.multi_tenant.repositories.base import TenantScopedRepository

        repo = TenantScopedRepository(COLLECTION_CONTACT_MESSAGES)
        configure_contact_repo(repo=repo)
        configure_superadmin_contact_services(contact_repo=repo)
        logger.info("Contact messages persistence initialized (contact_messages container)")
    except Exception:
        logger.warning(
            "Contact messages persistence initialization failed — "
            "contact form will still deliver email but messages will not be persisted."
        )


async def _startup_copilot_knowledge() -> None:
    """Initialize Co-Pilot Knowledge management (SPEC-1570..1577).

    Wires the admin_documentation_vectors Cosmos repository into the
    superadmin Co-Pilot Knowledge endpoints (document CRUD, ingestion,
    embedding, search).
    Non-fatal: Co-Pilot Knowledge pages will show 503 if unavailable.
    """
    from src.multi_tenant.superadmin_api import configure_copilot_knowledge_service

    try:
        from src.multi_tenant.repositories.platform import AdminDocumentationRepository

        repo = AdminDocumentationRepository()
        configure_copilot_knowledge_service(admin_doc_repo=repo)
        logger.info("Co-Pilot Knowledge services initialized (admin_documentation_vectors container)")
    except Exception:
        logger.warning(
            "Co-Pilot Knowledge initialization failed — "
            "knowledge management endpoints will return 503."
        )


async def _startup_copilot_docs_ingestion() -> None:
    """SPEC-1784: Auto-ingest agentredcx.com documentation into Co-Pilot Knowledge.

    Scans docs-site/docs/admin-guide/*.md (included in Docker image) and
    upserts each page into the admin_documentation_vectors collection.
    Content hashes prevent redundant embedding API calls — only new or
    changed pages are re-embedded.

    Triggered on every startup; idempotent via SHA-256 content hashes.
    This ensures Co-Pilot Knowledge is always up-to-date with the latest
    documentation version without manual intervention.
    """
    import asyncio
    import hashlib
    from datetime import datetime, timezone
    from pathlib import Path

    from src.multi_tenant.superadmin_api import _monolith as _state

    if _state._admin_doc_repo is None:
        logger.debug("Co-Pilot docs ingestion skipped — admin_doc_repo not configured")
        return

    # Try multiple paths (Docker image vs local dev)
    docs_dir: Path | None = None
    for candidate in [
        Path("docs-site/docs/admin-guide"),
        Path("docs/admin-guide"),
    ]:
        if candidate.exists():
            docs_dir = candidate
            break

    if docs_dir is None:
        logger.debug("Co-Pilot docs ingestion skipped — admin-guide directory not found")
        return

    # Also ingest intro, changelog, and getting-started guides
    extra_docs: list[Path] = []
    for extra_pattern in [
        Path("docs-site/docs/intro.md"),
        Path("docs-site/docs/changelog.md"),
        Path("docs-site/docs/getting-started"),
    ]:
        if extra_pattern.is_file():
            extra_docs.append(extra_pattern)
        elif extra_pattern.is_dir():
            extra_docs.extend(sorted(extra_pattern.glob("*.md")))

    md_files = sorted(docs_dir.glob("*.md")) + extra_docs

    if not md_files:
        logger.debug("Co-Pilot docs ingestion skipped — no markdown files found")
        return

    from src.multi_tenant.cosmos_schema import AdminDocumentationDocument

    # Category inference (same mapping as _copilot.py ingest endpoint)
    def _infer_category(stem: str) -> str:
        """Infer document category from filename stem."""
        mapping = {
            "dashboard": "dashboard",
            "knowledge": "knowledge_base",
            "widget": "widget_configuration",
            "team": "team_management",
            "inbox": "conversations",
            "conversation": "conversations",
            "analytics": "analytics",
            "custom-instruction": "custom_instructions",
            "brand": "brand_tone",
            "persona": "brand_tone",
            "polic": "business_policies",
            "escalat": "escalation_rules",
            "integrat": "integrations",
            "save": "save_activate",
            "activate": "save_activate",
            "quickstart": "getting_started",
            "getting-started": "getting_started",
            "billing": "billing",
            "account": "billing",
            "memory": "memory_privacy",
            "privacy": "memory_privacy",
            "intro": "getting_started",
            "changelog": "platform_updates",
        }
        stem_lower = stem.lower()
        for key, cat in mapping.items():
            if key in stem_lower:
                return cat
        return "getting_started"  # Default category (consistent with _copilot.py)

    created = 0
    updated = 0
    skipped = 0
    errors = 0

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            title = md_file.stem.replace("-", " ").title()
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            category = _infer_category(md_file.stem)
            doc_id = f"{category}:{md_file.stem}"
            content_hash = hashlib.sha256(f"{title}\n{content}".encode()).hexdigest()

            # Check existing — skip if content unchanged
            existing = await _state._admin_doc_repo.get_by_id(category, doc_id)
            if existing and existing.get("content_hash") == content_hash:
                skipped += 1
                continue

            now = datetime.now(timezone.utc).isoformat()
            doc = AdminDocumentationDocument(
                id=doc_id,
                document_category=category,
                title=title,
                content=content,
                source_file=str(md_file),
                content_hash=content_hash,
                tags=[category, "docs-site", "auto-ingested"],
                is_active=True,
                created_at=existing.get("created_at", now) if existing else now,
                updated_at=now,
            )
            await _state._admin_doc_repo.upsert_document(doc)

            if existing:
                updated += 1
            else:
                created += 1

            # Small yield to avoid blocking event loop on many files
            await asyncio.sleep(0)

        except Exception as exc:
            logger.warning("Co-Pilot docs ingestion error for %s: %s", md_file.name, exc)
            errors += 1

    if created or updated:
        logger.info(
            "Co-Pilot docs auto-ingestion complete: %d created, %d updated, %d skipped, %d errors",
            created, updated, skipped, errors,
        )

        # Trigger background re-embedding for new/updated documents
        try:
            from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer

            vectorizer = get_knowledge_vectorizer()
            if vectorizer._configured:
                logger.info("Triggering Co-Pilot docs re-embedding for %d new/updated documents", created + updated)
                # Fire-and-forget — embedding happens asynchronously
                asyncio.create_task(_embed_copilot_docs())
        except Exception:
            logger.debug("Co-Pilot docs re-embedding trigger skipped — vectorizer not available")
    else:
        logger.debug("Co-Pilot docs auto-ingestion: all %d documents up to date", skipped)


async def _embed_copilot_docs() -> None:
    """Background task: re-embed all active Co-Pilot documents missing embeddings."""
    from src.multi_tenant.superadmin_api import _monolith as _state

    if _state._admin_doc_repo is None:
        return

    try:
        all_docs = await _state._admin_doc_repo.list_all_active()
        needs_embed = [d for d in all_docs if not d.get("embedded_at") or not d.get("embedding")]

        if not needs_embed:
            logger.debug("Co-Pilot docs: all documents already embedded")
            return

        from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer

        vectorizer = get_knowledge_vectorizer()
        if not vectorizer._configured:
            return

        embedded = 0
        for doc in needs_embed:
            try:
                text = f"[{doc.get('document_category', 'general').upper()}] {doc['title']}\nTags: {', '.join(doc.get('tags', []))}\n{doc.get('content', '')}"
                # Truncate to 8000 chars for token limits
                text = text[:8000]

                embedding = await vectorizer._embed_text(text)
                if embedding:
                    from datetime import datetime as _dt, timezone as _tz

                    doc["embedding"] = embedding
                    doc["embedding_model"] = "text-embedding-3-large"
                    doc["embedded_at"] = _dt.now(_tz.utc).isoformat()
                    # Raw dict — use container upsert_item directly
                    await _state._admin_doc_repo._container.upsert_item(body=doc)
                    embedded += 1
            except Exception as exc:
                logger.warning("Co-Pilot docs embedding failed for %s: %s", doc.get("id"), exc)

        logger.info("Co-Pilot docs background embedding: %d/%d documents embedded", embedded, len(needs_embed))
    except Exception as exc:
        logger.warning("Co-Pilot docs background embedding error: %s", exc)


async def _startup_pipeline_observatory() -> None:
    """Enable Pipeline Observatory endpoints (SPEC-1579..1583).

    Marks the pipeline observatory as configured so topology, tenant
    comparison, and database metrics endpoints return data.
    Non-fatal: observatory pages will show empty/error states.
    """
    from src.multi_tenant.superadmin_api import configure_pipeline_observatory

    try:
        configure_pipeline_observatory(enabled=True)
        logger.info("Pipeline Observatory enabled")
    except Exception:
        logger.warning(
            "Pipeline Observatory initialization failed — "
            "observatory endpoints will return empty results."
        )

    # SPEC-1584: Wire PipelineMetricsAggregator with Cosmos client
    try:
        from src.multi_tenant.pipeline_metrics import configure_aggregator
        from src.multi_tenant.cosmos_client import get_cosmos_manager

        cosmos = get_cosmos_manager()
        configure_aggregator(cosmos_client=cosmos, cache_ttl=60)
        logger.info("Pipeline metrics aggregator configured")
    except Exception:
        logger.debug(
            "Pipeline metrics aggregator not configured — "
            "metrics will return zero values.",
            exc_info=True,
        )


async def _startup_status_api() -> None:
    """Initialize the public status API with incident repository.

    The /api/status endpoint is public (no auth) and returns active
    incidents and service status.
    Non-fatal: status page returns operational if unavailable.
    """
    from src.multi_tenant.status_api import configure_status_api

    try:
        from src.multi_tenant.repositories.incidents import IncidentRepository

        configure_status_api(incident_repo=IncidentRepository())
        logger.info("Public status API initialized (1 endpoint, no auth)")
    except Exception:
        logger.warning(
            "Public status API initialization failed — "
            "status page will report operational."
        )


async def _startup_alert_engine() -> None:
    """Initialize the AlertEngine for rule-based metric evaluation.

    Wires AlertRuleRepository, AlertHistoryRepository, and optionally
    IncidentRepository into the engine singleton.
    Non-fatal: alert evaluation will be unavailable until configured.
    """
    try:
        from src.multi_tenant.alert_engine import configure_alert_engine
        from src.multi_tenant.repositories.alerts import (
            AlertHistoryRepository,
            AlertRuleRepository,
        )

        rule_repo = AlertRuleRepository()
        history_repo = AlertHistoryRepository()

        incident_repo = None
        try:
            from src.multi_tenant.repositories.incidents import IncidentRepository
            incident_repo = IncidentRepository()
        except Exception:
            pass

        configure_alert_engine(rule_repo, history_repo, incident_repo)
        logger.info("AlertEngine configured (5 metric collectors)")
    except Exception:
        logger.warning(
            "AlertEngine initialization failed — "
            "alert evaluation will be unavailable."
        )


async def _startup_mfa_service() -> None:
    """Initialize the MfaTotpService for TOTP-based MFA.

    Wires TenantSecretService (Key Vault TOTP seed storage) and
    TeamMemberRepository (MFA enrollment state) into the service singleton.
    Non-fatal: MFA enrollment/verification will be unavailable until configured.
    """
    try:
        from src.multi_tenant.mfa_totp import configure_mfa_service
        from src.multi_tenant.repositories.team import TeamMemberRepository
        from src.multi_tenant.tenant_secret_service import TenantSecretService

        secret_service = TenantSecretService()
        team_repo = TeamMemberRepository()
        configure_mfa_service(
            secret_service=secret_service,
            team_repo=team_repo,
        )
        logger.info("MfaTotpService configured")
    except Exception:
        logger.warning(
            "MfaTotpService initialization failed — "
            "MFA will be unavailable."
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
            tenant_repo=TenantRepository(),
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


async def _startup_pre_auth_cleanup() -> None:
    """Start the pre-auth rate limiter cleanup background task (SPEC-1623)."""
    try:
        from src.multi_tenant.security_hardening import start_pre_auth_cleanup
        await start_pre_auth_cleanup()
    except Exception:
        logger.warning("Pre-auth cleanup task failed to start", exc_info=True)


async def _shutdown_pre_auth_cleanup() -> None:
    """Stop the pre-auth rate limiter cleanup background task."""
    try:
        from src.multi_tenant.security_hardening import stop_pre_auth_cleanup
        await stop_pre_auth_cleanup()
    except Exception:
        pass


async def _shutdown_cache_invalidation() -> None:
    """Stop the cross-replica cache invalidation subscriber (SPEC-1757)."""
    try:
        from src.multi_tenant.cache_invalidation import shutdown_cache_invalidation

        shutdown_cache_invalidation()
    except Exception:
        pass


async def _startup_redis_rate_limiter() -> None:
    """Initialize Redis-backed rate limiter if REDIS_URL is configured (SPEC-1626).

    When REDIS_URL is set, swaps the in-memory rate limit backend to Redis
    for distributed rate limiting across multiple replicas. Falls back to
    in-memory silently if Redis is unavailable or not configured.
    """
    redis_url = os.environ.get("REDIS_URL")
    if not redis_url:
        logger.info("REDIS_URL not set — using in-memory rate limiter")
        return

    try:
        import redis as redis_lib

        client = redis_lib.Redis.from_url(
            redis_url,
            username=None,  # Azure Cache for Redis uses key-only auth (no ACL usernames)
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=2,
            retry_on_timeout=True,
        )
        # Verify connectivity
        client.ping()

        from src.multi_tenant.security_hardening import (
            RedisRateLimitBackend,
            set_rate_limit_backend,
        )
        backend = RedisRateLimitBackend(client, key_prefix="agentred:rl:")
        set_rate_limit_backend(backend)
        logger.info("Redis rate limiter connected: %s", redis_url.split("@")[-1])

        # SPEC-1757: Start cross-replica cache invalidation subscriber
        from src.multi_tenant.cache_invalidation import configure_cache_invalidation

        configure_cache_invalidation(client)
    except ImportError:
        logger.warning("redis package not installed — using in-memory rate limiter")
    except Exception:
        logger.warning("Redis connection failed — falling back to in-memory rate limiter", exc_info=True)


async def _startup_entitlement_service() -> None:
    """Initialize the EntitlementService singleton (SPEC-1815, WI-1407).

    Wires the centralized entitlement accessor with Redis cache (if available)
    and Cosmos DB backend. Falls back to frozen entitlements if neither is
    available. Must run AFTER _startup_cosmos_db and _startup_redis_rate_limiter.
    """
    try:
        from src.multi_tenant.entitlement_service import get_entitlement_service

        svc = get_entitlement_service()

        # Reuse Redis client from REDIS_URL if available
        redis_client = None
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            try:
                import redis as redis_lib

                redis_client = redis_lib.Redis.from_url(
                    redis_url,
                    username=None,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=2,
                    retry_on_timeout=True,
                )
                redis_client.ping()
            except Exception:
                logger.warning(
                    "EntitlementService: Redis unavailable — "
                    "cache layer disabled",
                    exc_info=True,
                )
                redis_client = None

        await svc.initialize(redis_client=redis_client)
        logger.info(
            "EntitlementService initialized: redis=%s fallback=%s",
            redis_client is not None,
            svc.is_using_fallback,
        )
    except Exception:
        logger.warning(
            "EntitlementService startup failed — "
            "frozen fallback will be used",
            exc_info=True,
        )


# =========================================================================
# Registration functions — called from main.py
# =========================================================================

# -- Handler registries (SPEC-1623: lifespan migration) -------------------
# Populated by register_startup_handlers() / register_shutdown_handlers()
# and consumed by build_app_lifespan().

_lifecycle_startup_handlers: list = []
_lifecycle_shutdown_handlers: list = []


def register_startup_handlers(app: FastAPI | None = None) -> None:
    """Collect all core lifecycle startup handlers.

    Handler functions are defined at module level (above) so they are
    individually importable by test code.  The ``app`` parameter is
    accepted for backwards compatibility but is no longer used —
    handlers are collected into ``_lifecycle_startup_handlers`` and
    executed by the lifespan context manager (SPEC-1623).
    """
    _lifecycle_startup_handlers.clear()
    _lifecycle_startup_handlers.extend([
        _startup_verification_secret,
        _startup_cosmos_db,
        _startup_tenant_resolution,
        _startup_config_processor,
        _startup_conversation_meter,
        _startup_dashboard_services,
        _startup_tracing,
        _startup_circuit_breakers,
        _startup_nats,
        _startup_agntcy_sdk,
        _startup_secret_service,
        _startup_envelope_encryption,
        _startup_chat_services,
        _startup_admin_inbox_services,
        _startup_knowledge_vectorizer,
        _startup_conversation_vectorizer,
        _startup_admin_knowledge_services,
        _startup_embed_unembedded_kb,
        _startup_admin_analytics_services,
        _startup_admin_team_services,
        _startup_admin_gdpr_services,
        _startup_admin_audit_services,
        _startup_admin_quick_action_services,
        _startup_admin_profile_services,
        _startup_admin_apikey_services,
        _startup_superadmin_services,
        _startup_contact_messages,
        _startup_copilot_knowledge,
        _startup_copilot_docs_ingestion,
        _startup_pipeline_observatory,
        _startup_status_api,
        _startup_alert_engine,
        _startup_mfa_service,
        _startup_pattern_service,
        _startup_fine_tuning_service,
        _startup_key_rotation,
        _startup_trial_service,
        _startup_data_retention,
        _startup_archival_pipeline,
        _startup_alert_delivery,
        _startup_activation_service,
        _startup_migration_check,
        _startup_pre_auth_cleanup,
        _startup_redis_rate_limiter,
        _startup_entitlement_service,
    ])


def register_shutdown_handlers(app: FastAPI | None = None) -> None:
    """Collect all core lifecycle shutdown handlers.

    The ``app`` parameter is accepted for backwards compatibility but
    is no longer used (SPEC-1623).
    """
    _lifecycle_shutdown_handlers.clear()
    _lifecycle_shutdown_handlers.extend([
        _shutdown_nats,
        _shutdown_agntcy_sdk,
        _shutdown_cosmos_db,
        _shutdown_secret_service,
        _shutdown_chat_pipeline,
        _shutdown_pre_auth_cleanup,
        _shutdown_cache_invalidation,
    ])


def build_app_lifespan():
    """Build and return the FastAPI lifespan async context manager.

    Replaces the deprecated ``on_event("startup")``/``on_event("shutdown")``
    registration pattern (SPEC-1623).  Must be called AFTER all
    ``register_*`` functions have populated the handler registries.

    The lifespan executes handlers in this order:
      1. Core lifecycle startup handlers (Cosmos, NATS, tracing, …)
      2. Background task startup handlers (idle scanner, SLA, alerts, …)
      3.   — app serves requests —
      4. Background task shutdown handlers (cancel loops)
      5. Core lifecycle shutdown handlers (close Cosmos, NATS, …)
    """
    from contextlib import asynccontextmanager
    from collections.abc import AsyncIterator

    from src.app.background import _bg_startup_handlers, _bg_shutdown_handlers

    @asynccontextmanager
    async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
        # ── Startup ───────────────────────────────────────────────
        for handler in _lifecycle_startup_handlers:
            await handler()
        for handler in _bg_startup_handlers:
            await handler()
        try:
            yield
        finally:
            # ── Shutdown ──────────────────────────────────────────
            for handler in _bg_shutdown_handlers:
                await handler()
            for handler in _lifecycle_shutdown_handlers:
                await handler()

    return _lifespan
