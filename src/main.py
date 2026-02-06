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
from src.multi_tenant.admin_apikey_api import router as admin_apikey_router  # noqa: E402

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
app.include_router(admin_apikey_router)

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
# Standalone Admin SPA — password-gated for UX review access
# ---------------------------------------------------------------------------
# Simple password gate: visitors enter a password, receive a session cookie,
# and can browse the standalone admin freely.  The password is set via the
# ADMIN_PREVIEW_PASSWORD environment variable.
#
# This is NOT production auth for merchants — it's a casual-trespasser gate
# so UX designers and stakeholders can access the admin without running it
# locally.  Merchant auth is handled inside the SPA (API key login page).
# ---------------------------------------------------------------------------

import hashlib  # noqa: E402
import secrets as _secrets  # noqa: E402

from starlette.responses import Response as StarletteResponse  # noqa: E402

_admin_standalone_dist = (
    pathlib.Path(__file__).resolve().parent.parent / "admin" / "standalone" / "dist"
)
_ADMIN_PREVIEW_PASSWORD = os.environ.get("ADMIN_PREVIEW_PASSWORD", "")
_ADMIN_COOKIE_NAME = "agentred_preview"
# Deterministic token derived from the password so all gateway replicas agree
_ADMIN_COOKIE_VALUE = (
    hashlib.sha256(f"agentred-preview:{_ADMIN_PREVIEW_PASSWORD}".encode()).hexdigest()[:32]
    if _ADMIN_PREVIEW_PASSWORD
    else ""
)

_STANDALONE_LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Preview Access</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a0a; color: #e0e0e0; font-family: Inter, system-ui, sans-serif;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; }
  .card { background: #1f1f1f; border: 1px solid #272727; border-radius: 12px;
          padding: 40px; max-width: 380px; width: 100%; text-align: center; }
  h1 { font-size: 20px; margin-bottom: 8px; color: #f5f5f5; }
  p { font-size: 14px; color: #a0a0a0; margin-bottom: 24px; }
  input { width: 100%; padding: 10px 14px; border: 1px solid #272727; border-radius: 8px;
          background: #141414; color: #e0e0e0; font-size: 14px; margin-bottom: 16px;
          outline: none; }
  input:focus { border-color: #ff3621; }
  button { width: 100%; padding: 10px; border: none; border-radius: 8px;
           background: #ff3621; color: #fff; font-size: 14px; font-weight: 600;
           cursor: pointer; }
  button:hover { background: #e62e1a; }
  .error { color: #ff6b6b; font-size: 13px; margin-bottom: 12px; display: none; }
</style>
</head>
<body>
<div class="card">
  <img src="data:image/svg+xml,%3Csvg viewBox='0 0 128 128' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='128' height='128' fill='%23ff3621' rx='0'/%3E%3Cg fill='%23fff' transform='translate(2,2) scale(0.97)'%3E%3Cpath d='M39.2 69.6V59.3c0-3.1-3.2-4-5.9-4.2v-6.8c2.8-.1 5.9-1 5.9-3.8V31c0-5.3 4.7-9.2 9.5-9.2h5.5v8h-3c-2.6 0-3.3 1.5-3.3 3.8v11.2c0 4.6-3.7 6.2-6.6 6.6v.1c2.3.4 6.5 1.6 6.6 6.9V69.3c0 2.3.6 3.8 3.3 3.8h3v8h-5.5c-4.8 0-9.5-3.8-9.5-9.1z'/%3E%3Cpath d='M56.4 34.2h9.5v5.8h.1c1.8-4.3 6-6.7 10.8-6.7 1.3 0 1.9.2 2.2.3v9.8c-.9-.3-2.1-.5-3.2-.5-5.9 0-9.4 3.8-9.4 9.1v16.7h-10V34.2z'/%3E%3Cpath d='M87.3 71.2h2.9c2.7 0 3.3-1.5 3.3-3.7V56.7c0-5.4 4.3-6.5 6.5-6.9v-.1c-2.9-.4-6.5-1.6-6.5-6.2V32.4c0-2.3-.6-3.8-3.3-3.8h-2.9v-8h5.6c4.8 0 9.5 3.9 9.5 9.2v13.3c0 2.8 3.2 3.7 5.9 3.8v6.8c-2.8.2-5.9 1.1-5.9 4.2V69.6c0 5.3-4.7 9.1-9.5 9.1H87.3z'/%3E%3C/g%3E%3C/svg%3E" alt="Agent Red" width="48" height="48" style="margin-bottom:16px;display:block;margin-left:auto;margin-right:auto" />
  <h1>Agent Red Admin Preview</h1>
  <p>Enter the preview password to continue.</p>
  <div class="error" id="err">Incorrect password. Please try again.</div>
  <form method="POST" action="/admin/standalone/_auth">
    <input type="password" name="password" placeholder="Password" autofocus required/>
    <button type="submit">Continue</button>
  </form>
</div>
</body>
</html>"""


if _admin_standalone_dist.is_dir():

    def _check_preview_cookie(request: Request) -> bool:
        """Return True if the request has a valid preview session cookie."""
        if not _ADMIN_PREVIEW_PASSWORD:
            # No password configured — allow all access
            return True
        cookie = request.cookies.get(_ADMIN_COOKIE_NAME, "")
        return cookie == _ADMIN_COOKIE_VALUE

    @app.post("/admin/standalone/_auth", include_in_schema=False)
    async def _admin_standalone_auth(request: Request) -> StarletteResponse:
        """Validate the preview password and set a session cookie."""
        form = await request.form()
        password = str(form.get("password", ""))

        if password == _ADMIN_PREVIEW_PASSWORD and _ADMIN_PREVIEW_PASSWORD:
            response = StarletteResponse(
                status_code=303,
                headers={"location": "/admin/standalone/"},
            )
            response.set_cookie(
                _ADMIN_COOKIE_NAME,
                _ADMIN_COOKIE_VALUE,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=86400 * 7,  # 7 days
            )
            return response

        # Wrong password — re-render login with error
        error_html = _STANDALONE_LOGIN_HTML.replace(
            'display: none;', 'display: block;',
        )
        return HTMLResponse(content=error_html, status_code=403)

    # IMPORTANT: Register explicit root routes BEFORE the StaticFiles mount.
    # Starlette evaluates routes in registration order; if the mount were first,
    # it could shadow the root path.  The assets mount only claims
    # /admin/standalone/assets/* and does NOT interfere with other sub-paths.

    @app.get("/admin/standalone/", include_in_schema=False)
    async def _admin_standalone_index_slash(request: Request) -> StarletteResponse:
        """Serve the standalone admin SPA root with trailing slash (password-gated)."""
        if not _check_preview_cookie(request):
            return HTMLResponse(content=_STANDALONE_LOGIN_HTML)
        return FileResponse(str(_admin_standalone_dist / "index.html"))

    @app.get("/admin/standalone", include_in_schema=False)
    async def _admin_standalone_index(request: Request) -> StarletteResponse:
        """Serve the standalone admin SPA root (password-gated)."""
        if not _check_preview_cookie(request):
            return HTMLResponse(content=_STANDALONE_LOGIN_HTML)
        return FileResponse(str(_admin_standalone_dist / "index.html"))

    # Serve static assets (JS, CSS, sourcemaps) from the Vite build output
    app.mount(
        "/admin/standalone/assets",
        StaticFiles(directory=str(_admin_standalone_dist / "assets")),
        name="admin-standalone-assets",
    )

    @app.get("/admin/standalone/{full_path:path}", include_in_schema=False)
    async def _admin_standalone_spa(request: Request, full_path: str) -> StarletteResponse:
        """Catch-all route for the standalone admin SPA (password-gated).

        If full_path matches a real file in dist/ (e.g. icon-master.svg),
        serve that file directly.  Otherwise fall through to index.html
        for SPA client-side routing.
        """
        if not _check_preview_cookie(request):
            return HTMLResponse(content=_STANDALONE_LOGIN_HTML)
        # Serve real static files (SVG, PNG, etc.) from dist root
        candidate = _admin_standalone_dist / full_path
        if candidate.is_file() and ".." not in full_path:
            return FileResponse(str(candidate))
        return FileResponse(str(_admin_standalone_dist / "index.html"))

    logger.info(
        "Standalone admin SPA mounted at /admin/standalone%s",
        " (password-gated)" if _ADMIN_PREVIEW_PASSWORD else " (NO PASSWORD — open access)",
    )
else:
    logger.warning(
        "Standalone admin SPA dist directory not found at %s — "
        "standalone admin will not be available", _admin_standalone_dist,
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
        # Also wire Cosmos DB fallback for /api/tenants/lookup endpoint
        from src.integrations.provisioning import configure_tenant_lookup_repo
        configure_tenant_lookup_repo(tenant_repo)
        logger.info("Tenant resolution configured (Cosmos DB-backed, triple auth)")
    except Exception:
        logger.warning(
            "Tenant resolution configuration failed — auth middleware will "
            "reject authenticated requests until Cosmos DB is available."
        )


@app.on_event("startup")
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


@app.on_event("startup")
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


@app.on_event("startup")
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
        from src.multi_tenant.repository import ConversationRepository, KnowledgeBaseRepository
        from src.multi_tenant.customer_profile_service import get_profile_service
        from src.multi_tenant.system_prompt_builder import get_prompt_builder
        from src.chat.pipeline import USE_AGENT_CONTAINERS

        conv_repo = ConversationRepository()
        session = configure_conversation_session(
            conversation_repo=conv_repo,
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
# Knowledge Base Vectorizer (WI #209-213 — RAG infrastructure)
# ---------------------------------------------------------------------------

from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer  # noqa: E402


@app.on_event("startup")
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


# ---------------------------------------------------------------------------
# Admin Knowledge Base API (WI #175)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_knowledge_api import configure_admin_knowledge_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_knowledge_services() -> None:
    """Initialize the Admin Knowledge Base API.

    Wires KnowledgeBaseRepository and KnowledgeVectorizer into the admin
    knowledge endpoints. Embedding is triggered on create/update.
    Non-fatal: admin endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import KnowledgeBaseRepository
        from src.multi_tenant.staleness_service import get_staleness_service

        kb_repo = KnowledgeBaseRepository()
        vectorizer = get_knowledge_vectorizer()
        active_vectorizer = vectorizer if vectorizer._configured else None

        # Configure staleness service (WI #219-222)
        staleness_svc = get_staleness_service()
        staleness_svc.configure(kb_repo=kb_repo, vectorizer=active_vectorizer)

        configure_admin_knowledge_services(
            knowledge_repo=kb_repo,
            knowledge_vectorizer=active_vectorizer,
            staleness_service=staleness_svc,
        )
        logger.info("Admin knowledge base API initialized (8 endpoints, vectorization+staleness enabled)")
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
# Admin API Key Management (WI #159)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_apikey_api import configure_apikey_services  # noqa: E402


@app.on_event("startup")
async def _startup_admin_apikey_services() -> None:
    """Initialize the Admin API Key Management API.

    Wires TenantRepository + AuditLogRepository for API key CRUD.
    Non-fatal: endpoints return 503 if initialization fails.
    """
    try:
        from src.multi_tenant.repository import TenantRepository, AuditLogRepository

        tenant_repo = TenantRepository(cosmos_manager=None)
        audit_repo = AuditLogRepository(cosmos_manager=None)
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
    EmailAlertChannel,
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

    Registers built-in channels: Log, Dashboard, Email.
    Email channel requires AZURE_COMM_CONNECTION_STRING or SMTP_HOST
    env var to actually send — gracefully skips if unconfigured.
    """
    try:
        from src.multi_tenant.repository import (
            PreferencesRepository,
            TenantRepository,
        )
        from src.multi_tenant.cosmos_client import get_cosmos_manager

        service = AlertDeliveryService()
        service.register_channel(LogAlertChannel())
        service.register_channel(DashboardAlertChannel())

        # Email channel — uses preferences + tenant repos for recipient lookup
        try:
            manager = get_cosmos_manager()
            prefs_repo = PreferencesRepository(manager)
            tenant_repo = TenantRepository(manager)
            service.register_channel(
                EmailAlertChannel(prefs_repo, tenant_repo),
            )
        except Exception:
            logger.warning(
                "EmailAlertChannel not registered — "
                "Cosmos DB may not be available."
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

    # KB retrieval metrics (WI #213)
    kb_vectorizer = get_knowledge_vectorizer()
    if kb_vectorizer._configured:
        result["kb_retrieval"] = kb_vectorizer.metrics.summary()
    else:
        result["kb_retrieval"] = {"configured": False}

    # Semantic cache health (WI #223-225)
    from src.multi_tenant.semantic_cache import get_semantic_cache

    sem_cache = get_semantic_cache()
    result["semantic_cache"] = sem_cache.health()

    # API version (WI #140)
    from src.multi_tenant.api_versioning import API_VERSION

    result["version"] = API_VERSION

    return result
