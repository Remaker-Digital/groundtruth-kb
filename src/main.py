"""
Agent Red Customer Experience — FastAPI application entrypoint.

Mounts all API routers and provides health/readiness endpoints.

Usage:
    uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from fastapi import FastAPI
from fastapi.responses import Response
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
        {"name": "admin-integrations", "description": "Third-party integration management"},
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
# APP_CORS_ORIGINS: comma-separated explicit origins (e.g., "https://admin.shopify.com,https://example.com")
# APP_CORS_ORIGIN_REGEX: regex for wildcard subdomains (e.g., "https://.*\\.myshopify\\.com")
_cors_origins = os.environ.get("APP_CORS_ORIGINS", "*").split(",")
_cors_origin_regex = os.environ.get("APP_CORS_ORIGIN_REGEX", None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
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
from src.multi_tenant.admin_integration_api import router as admin_integration_router  # noqa: E402

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
app.include_router(admin_integration_router)

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

    _SHOPIFY_NO_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}

    @app.get("/admin/shopify/{full_path:path}", include_in_schema=False)
    async def _admin_shopify_spa(full_path: str) -> FileResponse:
        """Catch-all route for the Shopify embedded admin SPA.

        All client-side routes (/, /inbox, /billing, etc.) return the same
        index.html so React Router can handle routing. This is standard SPA
        behaviour — the server always returns the shell HTML, and the
        JavaScript app determines what to render based on the URL.
        """
        return FileResponse(str(_admin_shopify_dist / "index.html"), headers=_SHOPIFY_NO_CACHE)

    @app.get("/admin/shopify", include_in_schema=False)
    async def _admin_shopify_index() -> FileResponse:
        """Serve the Shopify embedded admin SPA root."""
        return FileResponse(str(_admin_shopify_dist / "index.html"), headers=_SHOPIFY_NO_CACHE)

    logger.info("Shopify embedded admin SPA mounted at /admin/shopify")
else:
    logger.warning(
        "Shopify admin SPA dist directory not found at %s — "
        "embedded admin will not be available", _admin_shopify_dist,
    )


# ---------------------------------------------------------------------------
# Widget JS bundle — served at /widget.js for embedding in any page
# ---------------------------------------------------------------------------

_widget_dist = pathlib.Path(__file__).resolve().parent.parent / "widget" / "dist"
_widget_bundle = _widget_dist / "agent-red-widget.iife.js"


@app.get("/widget.js", include_in_schema=False)
async def _serve_widget_js() -> Response:
    """Serve the Agent Red chat widget IIFE bundle.

    This is the single-file JavaScript bundle that merchants (or the admin
    UI) include via a ``<script>`` tag.  It boots the Shadow DOM launcher
    and iframe conversation panel.
    """
    if not _widget_bundle.is_file():
        return JSONResponse(
            {"detail": "Widget bundle not available"},
            status_code=404,
        )
    return FileResponse(
        str(_widget_bundle),
        media_type="application/javascript",
        headers={
            "Cache-Control": "public, max-age=3600, s-maxage=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ---------------------------------------------------------------------------
# Standalone Admin SPA — production merchant admin (password-gated)
# ---------------------------------------------------------------------------
# Password gate: merchants enter a password, receive a session cookie, and
# access the full admin dashboard.  The password is set via the
# ADMIN_PREVIEW_PASSWORD environment variable on the Container App.
#
# After passing the password gate, merchants sign in with their API key
# inside the SPA for tenant-scoped access to all admin features.
# ---------------------------------------------------------------------------

import hashlib  # noqa: E402
import secrets as _secrets  # noqa: E402

from starlette.responses import Response as StarletteResponse  # noqa: E402

_admin_standalone_dist = (
    pathlib.Path(__file__).resolve().parent.parent / "admin" / "standalone" / "dist"
)
_ADMIN_INITIAL_PASSWORD = os.environ.get("ADMIN_PREVIEW_PASSWORD", "")
_ADMIN_COOKIE_NAME = "agentred_admin"
# Mutable password hash — allows runtime password changes.  Falls back to env var.
# Deterministic token derived from the password so all gateway replicas agree.
_admin_password_hash: str = (
    hashlib.sha256(f"agentred-admin:{_ADMIN_INITIAL_PASSWORD}".encode()).hexdigest()
    if _ADMIN_INITIAL_PASSWORD
    else ""
)

def _compute_cookie_value(password: str) -> str:
    """Derive a deterministic cookie token from a password."""
    return hashlib.sha256(f"agentred-admin:{password}".encode()).hexdigest()[:32]

_admin_cookie_value: str = (
    _compute_cookie_value(_ADMIN_INITIAL_PASSWORD) if _ADMIN_INITIAL_PASSWORD else ""
)
# Store the current active password for comparison during password change
_admin_current_password: str = _ADMIN_INITIAL_PASSWORD

_STANDALONE_SHARED_STYLES = """
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #0a0a0a; color: #e0e0e0; font-family: Inter, system-ui, sans-serif;
         display: flex; align-items: center; justify-content: center; min-height: 100vh; }
  .card { background: #1f1f1f; border: 1px solid #272727; border-radius: 12px;
          padding: 40px; max-width: 400px; width: 100%; text-align: center; }
  h1 { font-size: 20px; margin-bottom: 4px; color: #f5f5f5; }
  .subtitle { font-size: 14px; color: #a0a0a0; margin-bottom: 24px; }
  label { display: block; font-size: 13px; font-weight: 500; color: #a0a0a0;
          margin-bottom: 6px; text-align: left; }
  input { width: 100%; padding: 10px 14px; border: 1px solid #272727; border-radius: 8px;
          background: #141414; color: #e0e0e0; font-size: 14px; margin-bottom: 12px;
          outline: none; }
  input:focus { border-color: #ff3621; }
  button[type="submit"] { width: 100%; padding: 10px; border: none; border-radius: 8px;
           background: #ff3621; color: #fff; font-size: 14px; font-weight: 600;
           cursor: pointer; margin-top: 4px; }
  button[type="submit"]:hover { background: #e62e1a; }
  .error { color: #ff6b6b; font-size: 13px; margin-bottom: 12px; display: none; }
  .success { color: #4caf50; font-size: 13px; margin-bottom: 12px; display: none; }
  .link { color: #ff3621; font-size: 13px; text-decoration: none; cursor: pointer;
          display: inline-block; margin-top: 16px; }
  .link:hover { text-decoration: underline; }
  .logo { margin-bottom: 16px; display: block; margin-left: auto; margin-right: auto; }
"""

_LOGO_DATA_URI = "data:image/png;base64,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"

_STANDALONE_LOGIN_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Sign In</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <p class="subtitle">Customer Experience Admin</p>
  <div class="error" id="err">Incorrect password. Please try again.</div>
  <form method="POST" action="/admin/standalone/_auth">
    <label for="pw">Password</label>
    <input id="pw" type="password" name="password" placeholder="Enter your password" autofocus required/>
    <button type="submit">Sign In</button>
  </form>
  <a href="/admin/standalone/_change-password" class="link">Change password</a>
</div>
</body>
</html>"""

_STANDALONE_CHANGE_PW_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Change Password</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Change Password</h1>
  <p class="subtitle">Enter your current password and choose a new one.</p>
  <div class="error" id="err">Current password is incorrect.</div>
  <div class="success" id="ok">Password changed successfully!</div>
  <form method="POST" action="/admin/standalone/_change-password">
    <label for="current">Current Password</label>
    <input id="current" type="password" name="current_password" placeholder="Current password" autofocus required/>
    <label for="new">New Password</label>
    <input id="new" type="password" name="new_password" placeholder="New password" required minlength="6"/>
    <label for="confirm">Confirm New Password</label>
    <input id="confirm" type="password" name="confirm_password" placeholder="Confirm new password" required minlength="6"/>
    <button type="submit">Change Password</button>
  </form>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""


if _admin_standalone_dist.is_dir():

    def _check_admin_cookie(request: Request) -> bool:
        """Return True if the request has a valid admin session cookie."""
        global _admin_current_password, _admin_cookie_value
        if not _admin_current_password:
            # No password configured — allow all access
            return True
        cookie = request.cookies.get(_ADMIN_COOKIE_NAME, "")
        return cookie == _admin_cookie_value

    @app.post("/admin/standalone/_auth", include_in_schema=False)
    async def _admin_standalone_auth(request: Request) -> StarletteResponse:
        """Validate the admin password and set a session cookie."""
        global _admin_current_password, _admin_cookie_value
        form = await request.form()
        password = str(form.get("password", ""))

        if password == _admin_current_password and _admin_current_password:
            response = StarletteResponse(
                status_code=303,
                headers={"location": "/admin/standalone/"},
            )
            response.set_cookie(
                _ADMIN_COOKIE_NAME,
                _admin_cookie_value,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=86400 * 7,  # 7 days
            )
            return response

        # Wrong password — re-render login with error
        error_html = _STANDALONE_LOGIN_HTML.replace(
            'class="error" id="err"', 'class="error" id="err" style="display:block"',
        )
        return HTMLResponse(content=error_html, status_code=403)

    @app.get("/admin/standalone/_change-password", include_in_schema=False)
    async def _admin_change_password_form(request: Request) -> HTMLResponse:
        """Show the change password form."""
        return HTMLResponse(content=_STANDALONE_CHANGE_PW_HTML)

    @app.post("/admin/standalone/_change-password", include_in_schema=False)
    async def _admin_change_password(request: Request) -> StarletteResponse:
        """Process password change: verify current, set new."""
        global _admin_current_password, _admin_cookie_value, _admin_password_hash
        form = await request.form()
        current = str(form.get("current_password", ""))
        new_pw = str(form.get("new_password", ""))
        confirm = str(form.get("confirm_password", ""))

        # Validate current password
        if current != _admin_current_password or not _admin_current_password:
            error_html = _STANDALONE_CHANGE_PW_HTML.replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=error_html, status_code=403)

        # Validate new passwords match
        if new_pw != confirm:
            mismatch_html = _STANDALONE_CHANGE_PW_HTML.replace(
                'Current password is incorrect.',
                'New passwords do not match.',
            ).replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=mismatch_html, status_code=400)

        # Validate minimum length
        if len(new_pw) < 6:
            short_html = _STANDALONE_CHANGE_PW_HTML.replace(
                'Current password is incorrect.',
                'New password must be at least 6 characters.',
            ).replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=short_html, status_code=400)

        # Update the password (in-memory — persists until container restart)
        _admin_current_password = new_pw
        _admin_cookie_value = _compute_cookie_value(new_pw)
        _admin_password_hash = hashlib.sha256(
            f"agentred-admin:{new_pw}".encode(),
        ).hexdigest()

        logger.info("Admin password changed successfully (in-memory update)")

        # Show success, then redirect to sign-in with new cookie
        success_html = _STANDALONE_CHANGE_PW_HTML.replace(
            'class="success" id="ok"', 'class="success" id="ok" style="display:block"',
        )
        response = HTMLResponse(content=success_html)
        # Invalidate old session cookie so they must sign in with new password
        response.delete_cookie(_ADMIN_COOKIE_NAME)
        return response

    # IMPORTANT: Register explicit root routes BEFORE the StaticFiles mount.
    # Starlette evaluates routes in registration order; if the mount were first,
    # it could shadow the root path.  The assets mount only claims
    # /admin/standalone/assets/* and does NOT interfere with other sub-paths.

    # Cache-control headers for HTML pages: must revalidate on every load
    # so that new deployments with updated Vite hashed assets are picked up
    # immediately.  Hashed assets (/assets/*) are served by StaticFiles with
    # long-lived caching (content hash in filename = immutable).
    _NO_CACHE_HEADERS = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}

    @app.get("/admin/standalone/", include_in_schema=False)
    async def _admin_standalone_index_slash(request: Request) -> StarletteResponse:
        """Serve the standalone admin SPA root with trailing slash (password-gated)."""
        if not _check_admin_cookie(request):
            return HTMLResponse(content=_STANDALONE_LOGIN_HTML, headers=_NO_CACHE_HEADERS)
        return FileResponse(str(_admin_standalone_dist / "index.html"), headers=_NO_CACHE_HEADERS)

    @app.get("/admin/standalone", include_in_schema=False)
    async def _admin_standalone_index(request: Request) -> StarletteResponse:
        """Serve the standalone admin SPA root (password-gated)."""
        if not _check_admin_cookie(request):
            return HTMLResponse(content=_STANDALONE_LOGIN_HTML, headers=_NO_CACHE_HEADERS)
        return FileResponse(str(_admin_standalone_dist / "index.html"), headers=_NO_CACHE_HEADERS)

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
        if not _check_admin_cookie(request):
            return HTMLResponse(content=_STANDALONE_LOGIN_HTML, headers=_NO_CACHE_HEADERS)
        # Serve real static files (SVG, PNG, etc.) from dist root
        candidate = _admin_standalone_dist / full_path
        if candidate.is_file() and ".." not in full_path:
            return FileResponse(str(candidate))
        return FileResponse(str(_admin_standalone_dist / "index.html"), headers=_NO_CACHE_HEADERS)

    logger.info(
        "Standalone admin SPA mounted at /admin/standalone%s",
        " (password-gated)" if _admin_current_password else " (NO PASSWORD — open access)",
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
        await asyncio.wait_for(init_nats_manager(), timeout=10.0)
        logger.info("NATS tenant isolation manager connected")
    except (asyncio.TimeoutError, Exception):
        # Non-fatal at startup — NATS may not be available in dev/production
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
# KB Auto-Embedding on Startup
# ---------------------------------------------------------------------------


@app.on_event("startup")
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
            enable_cross_partition_query=True,
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
    WebhookAlertChannel,
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


# ---------------------------------------------------------------------------
# Test Mode service wiring (C2)
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def _startup_test_mode_service() -> None:
    """Wire TestModeService with config processor + preferences repo.

    Required for C2 — controlled rollout routing. The service uses
    the config processor for persisting test mode state changes and
    the preferences repository for reading current state.
    """
    try:
        from src.multi_tenant.repository import PreferencesRepository
        from src.multi_tenant.tenant_config_processor import get_config_processor
        from src.multi_tenant.test_mode_service import get_test_mode_service

        service = get_test_mode_service()
        processor = get_config_processor()
        prefs_repo = PreferencesRepository()
        service.configure(processor=processor, repo=prefs_repo)
        logger.info("TestModeService configured with processor + preferences repo")
    except Exception as exc:
        logger.warning(
            "TestModeService configuration failed — test mode will be "
            "unavailable until dependencies are ready. Error: %s",
            exc,
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
