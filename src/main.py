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
        {"name": "admin-quick-actions", "description": "Quick action prompt button management"},
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
    """Catch and log unhandled exceptions to aid production debugging.

    RuntimeErrors from uninitialized CosmosManager are converted to 503
    (Service Unavailable) rather than 500, allowing clients to distinguish
    between transient infrastructure issues and genuine code bugs.

    All error responses include the X-API-Version header for consistency
    with normal responses (exception handlers bypass middleware).
    """
    from src.multi_tenant.api_versioning import API_VERSION

    _logger = logging.getLogger("src.main")
    _version_headers = {"X-API-Version": API_VERSION}

    # CosmosManager not initialized → 503 Service Unavailable
    if isinstance(exc, RuntimeError) and "not initialized" in str(exc):
        _logger.warning(
            "Service unavailable (backing store not initialized): path=%s method=%s error=%s",
            request.url.path, request.method, exc,
        )
        return JSONResponse(
            status_code=503,
            content={"error": "Service temporarily unavailable. Database not initialized."},
            headers=_version_headers,
        )

    _logger.error(
        "Unhandled exception: path=%s method=%s error=%s\n%s",
        request.url.path, request.method, exc,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error."},
        headers=_version_headers,
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
    expose_headers=["X-API-Version", "X-Product-Version", "X-API-Deprecation-Notice"],
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
from src.multi_tenant.admin_quick_action_api import router as admin_quick_action_router  # noqa: E402

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
app.include_router(admin_quick_action_router)

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
_ADMIN_RESET_EMAIL = os.environ.get("ADMIN_RESET_EMAIL", "").strip().lower()
_ADMIN_COOKIE_NAME = "agentred_admin"
# Mutable password hash — allows runtime password changes.  Falls back to env var.
# Deterministic token derived from the password so all gateway replicas agree.
_admin_password_hash: str = (
    hashlib.sha256(f"agentred-admin:{_ADMIN_INITIAL_PASSWORD}".encode()).hexdigest()
    if _ADMIN_INITIAL_PASSWORD
    else ""
)
# Immutable HMAC key for reset tokens — derived from the env var password and NEVER
# changes at runtime.  This ensures all replicas always agree on the signing key,
# even after an in-memory password change on a single replica.
_ADMIN_HMAC_KEY: str = _admin_password_hash

def _compute_cookie_value(password: str) -> str:
    """Derive a deterministic cookie token from a password."""
    return hashlib.sha256(f"agentred-admin:{password}".encode()).hexdigest()[:32]

_admin_cookie_value: str = (
    _compute_cookie_value(_ADMIN_INITIAL_PASSWORD) if _ADMIN_INITIAL_PASSWORD else ""
)
# Store the current active password for comparison during password change
_admin_current_password: str = _ADMIN_INITIAL_PASSWORD

# Password reset tokens — HMAC-signed so any replica can validate without shared state.
# Token format: "<nonce>.<expiry_ts>.<hmac_hex>"
# Signed with _admin_password_hash (deterministic across replicas from env var).
import time as _time  # noqa: E402
import hmac as _hmac  # noqa: E402

_admin_used_reset_nonces: set[str] = set()  # best-effort single-use per replica
_admin_reset_rate_limit: dict[str, list[float]] = {}

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

_LOGO_DATA_URI = "data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgaWQ9IkxheWVyXzIiCiAgIHZpZXdCb3g9IjAgMCA1MjAuMDAwMDIgMTI4IgogICB2ZXJzaW9uPSIxLjEiCiAgIHdpZHRoPSI1MjAiCiAgIGhlaWdodD0iMTI4IgogICB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiAgIHhtbG5zOnN2Zz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogIDxkZWZzCiAgICAgaWQ9ImRlZnMxIj4KICAgIDxzdHlsZQogICAgICAgaWQ9InN0eWxlMSI+LmNscy0xe2ZpbGw6I2ZmZjt9LmNscy0ye2ZpbGw6bm9uZTt9LmNscy0ze2ZpbGw6I2ZmMzYyMTt9PC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QKICAgICBjbGFzcz0iY2xzLTIiCiAgICAgd2lkdGg9IjEyOC40NDQ2NCIKICAgICBoZWlnaHQ9IjEyOCIKICAgICBpZD0icmVjdDEiCiAgICAgeD0iMCIKICAgICB5PSIwIgogICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICA8cmVjdAogICAgIGNsYXNzPSJjbHMtMyIKICAgICB4PSIxLjEzOTM4MzMiCiAgICAgeT0iMS4zMjY5NjkxIgogICAgIHdpZHRoPSIxMjYuMjc3MDIiCiAgICAgaGVpZ2h0PSIxMjUuMzQ2MDYiCiAgICAgaWQ9InJlY3QyIgogICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICA8cGF0aAogICAgIGNsYXNzPSJjbHMtMSIKICAgICBkPSJtIDUwLjA5ODEzLDQzLjM2NjA0NSBoIDExLjg4MDE1NiB2IDcuMjM5MjUzIGggMC4xODA2MzQgYyAyLjI1MDk3NywtNS4zMDc4NTkgNy41NTg4MzYsLTguMzc4NjM2IDEzLjUwNTg2MSwtOC4zNzg2MzYgMS42MjU3MDYsMCAyLjQzMTYxMSwwLjIzNjIxMyAyLjc5Mjg3OSwwLjMxOTU4MyB2IDEyLjE1ODA1NCBjIC0xLjE2NzE3MywtMC40MDI5NTMgLTIuNjEyMjQ1LC0wLjU2OTY5MiAtNC4wNTczMTYsLTAuNTY5NjkyIC03LjM3ODIwMiwwIC0xMS42OTk1MjIsNC43NTIwNjIgLTExLjY5OTUyMiwxMS4yNjg3NzkgViA4NS43NzMzMzggSCA1MC4wOTgxMyB2IC00Mi40MjExODggMCB6IgogICAgIGlkPSJwYXRoMyIKICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgPGcKICAgICBpZD0iZzE0IgogICAgIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAuMDYyNTI0OTcpIj4KICAgIDxwYXRoCiAgICAgICBjbGFzcz0iY2xzLTEiCiAgICAgICBkPSJNIDI0LjYwNzkwMiw4OS41NTk3MDIgViA3My40NTU0OTEgYyAwLC0zLjg2Mjc4OCAtMy45NDYxNTcsLTQuOTg4Mjc2IC03LjQwNTk5MiwtNS4yMzgzODUgdiAtOC40NDgxMSBjIDMuNDU5ODM1LC0wLjA4MzM3IDcuNDA1OTkyLC0xLjIwODg1OCA3LjQwNTk5MiwtNC42Njg2OTMgViAzOC41MjM2NjQgYyAwLC02LjYwMDA4NiA1Ljg3NzU1LC0xMS40MzU1MTggMTEuOTA3OTQ1LC0xMS40MzU1MTggaCA2LjkxOTY3IHYgOS45NzY1NTEgaCAtMy42OTYwNDkgYyAtMy4yOTMwOTUsMCAtNC4wOTkwMDEsMS44NDgwMjUgLTQuMDk5MDAxLDQuNjY4NjkzIHYgMTQuMDA2MDc4IGMgMCw1Ljc5NDE4MiAtNC41ODUzMjMsNy43MjU1NzUgLTguMjExODk3LDguMjExODk4IHYgMC4xNjY3MzggYyAyLjgyMDY2OSwwLjQ4NjMyMyA4LjEyODUyOCwxLjkzMTM5NCA4LjIxMTg5Nyw4LjYxNDg1MSB2IDEzLjYwMzEyNiBjIDAsMi44MjA2NjggMC44MDU5MDYsNC42Njg2OTMgNC4wOTkwMDEsNC42Njg2OTMgaCAzLjY5NjA0OSB2IDkuOTA3MDc2IGggLTYuOTE5NjcgYyAtNi4wMzAzOTUsMCAtMTEuOTA3OTQ1LC00Ljc1MjA2MiAtMTEuOTA3OTQ1LC0xMS4zNTIxNDggeiIKICAgICAgIGlkPSJwYXRoMiIKICAgICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICAgIDxwYXRoCiAgICAgICBjbGFzcz0iY2xzLTEiCiAgICAgICBkPSJtIDg0Ljk5NTIyLDkxLjAwNDc3MSBoIDMuNjI2NTczIGMgMy4zNzY0NjYsMCA0LjE4MjM3MSwtMS44NDgwMjQgNC4xODIzNzEsLTQuNjY4NjkyIFYgNzIuNzMyOTUzIGMgMCwtNi42ODM0NTYgNS4zMDc4NTksLTguMTI4NTI4IDguMTI4NTI2LC04LjYxNDg1IFYgNjMuOTUxMzY0IEMgOTcuMzg5NDg3LDYzLjQ2NTA0MiA5Mi44MDQxNjQsNjEuNTMzNjQ4IDkyLjgwNDE2NCw1NS43Mzk0NjcgViA0MS43MzMzODkgYyAwLC0yLjgyMDY2OSAtMC44MDU5MDUsLTQuNjY4NjkzIC00LjE4MjM3MSwtNC42Njg2OTMgSCA4NC45OTUyMiB2IC05Ljk3NjU1MiBoIDYuOTE5NjY5IGMgNi4wMzAzOTUsMCAxMS45MDc5NDEsNC44MzU0MzIgMTEuOTA3OTQxLDExLjQzNTUxOCB2IDE2LjU3NjYzOSBjIDAsMy40NTk4MzUgMy45NDYxNiw0LjU4NTMyMyA3LjQwNiw0LjY2ODY5MyB2IDguNDQ4MTEgYyAtMy41NDMyMSwwLjIzNjIxNCAtNy40MDYsMS4zNjE3MDIgLTcuNDA2LDUuMjM4Mzg1IFYgODkuNTU5NyBjIDAsNi42MDAwODYgLTUuODc3NTQ2LDExLjM1MjE1IC0xMS45MDc5NDEsMTEuMzUyMTUgSCA4NC45OTUyMiBaIgogICAgICAgaWQ9InBhdGg0IgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogIDwvZz4KICA8ZwogICAgIGlkPSJnMTMiCiAgICAgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCwtMC40MzA3MzkpIj4KICAgIDxwYXRoCiAgICAgICBjbGFzcz0iY2xzLTEiCiAgICAgICBkPSJtIDE2Ny41MzEwNCw2NS4xNjcxNyBjIDAsLTkuNjcwODY0IDYuNzI1MTQsLTE2LjkzNzkwNiAxNS43MTUxNSwtMTYuOTM3OTA2IDQuNzY1OTYsMCA4LjQ0ODExLDIuMTM5ODE3IDEwLjI4MjI0LDQuODM1NDMyIGggMC4wNTU2IHYgLTMuOTczOTQ3IGggOC41NTkyNyB2IDMyLjIzNjIxMiBoIC04LjA3Mjk1IHYgLTQuNDA0Njg5IGggLTAuMTI1MDUgYyAtMS43MDkwOCwyLjg3NjI0OCAtNS44Nzc1NSw1LjI2NjE3NCAtMTAuODI0MTQsNS4yNjYxNzQgLTguNjg0MzMsMCAtMTUuNjA0LC03LjE1NTg4MyAtMTUuNjA0LC0xNy4wMDczODEgeiBtIDE3LjU0OTI4LDkuNDIwNzU1IGMgNS4xNDExMiwwIDguNjg0MzMsLTQuMTU0NTgxIDguNjg0MzMsLTkuMzY1MTc1IDAsLTUuMjEwNTk1IC0zLjU0MzIxLC05LjM2NTE3NiAtOC42ODQzMywtOS4zNjUxNzYgLTUuMTQxMTIsMCAtOC42ODQzMiw0LjA0MzQyMiAtOC42ODQzMiw5LjM2NTE3NiAwLDUuMzIxNzU0IDMuNTQzMiw5LjM2NTE3NSA4LjY4NDMyLDkuMzY1MTc1IHoiCiAgICAgICBpZD0icGF0aDUiCiAgICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgICA8cGF0aAogICAgICAgY2xhc3M9ImNscy0xIgogICAgICAgZD0ibSAyMTIuMzAwNDcsODkuMDI0NzQ2IDMuNjY4MjYsLTUuMjY2MTc0IGMgMS45NTkxOCwyLjA4NDIzOCA1LjE5NjcsMy40MTgxNSA5LjI0MDEyLDMuNDE4MTUgNC43NjU5NSwwIDkuMzY1MTcsLTIuMTM5ODE4IDkuMzY1MTcsLTcuODkyMzE0IHYgLTIuMzg5OTI2IGggLTAuMTI1MDUgYyAtMS43MDkwOCwyLjg3NjI0OCAtNS44Nzc1NSw1LjI2NjE3NCAtMTAuODI0MTQsNS4yNjYxNzQgLTguNjg0MzMsMCAtMTUuNjA0LC03LjE1NTg4MyAtMTUuNjA0LC0xNy4wMDczODEgMCwtOS44NTE0OTcgNi43MjUxNCwtMTYuOTM3OTA2IDE1LjcxNTE2LC0xNi45Mzc5MDYgNC43NjU5NSwwIDguNDQ4MTEsMi4xMzk4MTcgMTAuMjgyMjQsNC44MzU0MzIgaCAwLjA1NTYgdiAtMy45NzM5NDcgaCA4LjU1OTI3IHYgMjkuMTA5ODU1IGMgMCw5LjU0NTgxIC01LjYyNzQ1LDE1LjIyODgzMSAtMTYuNzU3MjgsMTUuMjI4ODMxIC02LjExMzc2LDAgLTExLjA3NDI1LC0xLjcwOTA3NSAtMTMuNTc1MzMsLTQuNDA0Njg5IHogbSAxMy4yNjk2NSwtMTQuNDM2ODIxIGMgNS4xNDExMiwwIDguNjg0MzIsLTQuMTU0NTgxIDguNjg0MzIsLTkuMzY1MTc1IDAsLTUuMjEwNTk1IC0zLjU0MzIsLTkuMzY1MTc2IC04LjY4NDMyLC05LjM2NTE3NiAtNS4xNDExMiwwIC04LjY4NDMzLDQuMDQzNDIyIC04LjY4NDMzLDkuMzY1MTc2IDAsNS4zMjE3NTQgMy41NDMyMSw5LjM2NTE3NSA4LjY4NDMzLDkuMzY1MTc1IHoiCiAgICAgICBpZD0icGF0aDYiCiAgICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgICA8cGF0aAogICAgICAgY2xhc3M9ImNscy0xIgogICAgICAgZD0ibSAyNDguNTEwNjMsNjUuMjIyNzUgYyAwLC05Ljc4MjAyMyA3LjEwMDMsLTE3LjAwNzM4MSAxNi43NTcyNywtMTcuMDA3MzgxIDguNjg0MzIsMCAxNi43MDE2OSw1Ljc1MjQ5NiAxNi43MDE2OSwxOS4xNDcxOTggdiAwLjQzMDc0MyBoIC0yNC41OTQwMSBjIDAuOTE3MDcsNC45NjA0ODYgNC4wOTkwMSw3LjAzMDgyOSA4LjA3Mjk1LDcuMDMwODI5IDIuOTMxODMsMCA1Ljc1MjUsLTEuMTY3MTczIDcuNTMxMDUsLTMuNTQzMjA1IGwgNi40MTk0NSw0LjM0OTExIGMgLTIuNzUxMTksMy4zNjI1NzEgLTYuODUwMTksNi41NDQ1MDcgLTEzLjk1MDUsNi41NDQ1MDcgLTkuNzI2NDQsMCAtMTYuOTM3OSwtNy4xNTU4ODMgLTE2LjkzNzksLTE2LjkzNzkwNiB6IG0gMjQuMjE4ODQsLTMuMjM3NTE2IGMgLTAuNjExMzgsLTQuMDQzNDIyIC0zLjM2MjU3LC02LjYwMDA4NyAtNy41MzEwNSwtNi42MDAwODcgLTMuNjEyNjcsMCAtNi45NzUyNSwyLjAxNDc2MyAtNy44MjI4NCw2LjYwMDA4NyB6IgogICAgICAgaWQ9InBhdGg3IgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMSIKICAgICAgIGQ9Im0gMjg3LjgzMzI1LDQ5LjA3Njg1NCBoIDguMDcyOTUgdiA0LjI3OTYzNSBoIDAuMTI1MDUgYyAxLjk1OTE4LC0yLjc1MTE5NCA0Ljk2MDQ5LC01LjAxNjA2NiAxMC4wODc3MSwtNS4wMTYwNjYgOC4xOTgsMCAxMi4xNzE5NSw1LjI2NjE3NSAxMi4xNzE5NSwxMy41MTk3NTYgdiAxOS40NTI4ODcgaCAtOC41NTkyNyBWIDY0LjE4MDYzMSBjIDAsLTQuNjU0Nzk4IC0xLjQ3Mjg2LC03Ljk0Nzg5NCAtNi4yMzg4MiwtNy45NDc4OTQgLTQuNzY1OTYsMCAtNy4xMDAzLDMuMzA2OTkxIC03LjEwMDMsOC4wMTczNjggdiAxNy4wNjI5NjEgaCAtOC41NTkyNyB6IgogICAgICAgaWQ9InBhdGg4IgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMSIKICAgICAgIGQ9Ik0gMzI3Ljk0Nzg4LDczLjcyNjQ0IFYgNTYuMjg4MzE3IGggLTUuMTQxMTIgdiAtNy4yMTE0NjMgaCA1LjE0MTEyIHYgLTkuMzY1MTc1IGggOC41NTkyNyB2IDkuMzY1MTc1IGggNy4xMDAzIHYgNy4yMTE0NjMgaCAtNy4xMDAzIHYgMTYuMDIwODQxIGMgMCwyLjAxNDc2NCAxLjQwMzM5LDIuNTAxMDg2IDMuMzA2OTksMi41MDEwODYgMS40NzI4NiwwIDIuOTMxODMsLTAuMzA1Njg4IDQuMDQzNDIsLTAuNTU1Nzk3IHYgNy4wMzA4MjkgYyAtMS40MDMzOSwwLjMwNTY4OCAtNC4xNTQ1OCwwLjYxMTM3NyAtNi4yMzg4MiwwLjYxMTM3NyAtNS4xNDExMiwwIC05LjY3MDg2LC0xLjgzNDEzIC05LjY3MDg2LC04LjE5ODAwMyB6IgogICAgICAgaWQ9InBhdGg5IgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMyIKICAgICAgIGQ9Im0gMzQ3LjUyNTgyLDg1LjM0MjU5MiBoIDI3LjcwNjQ3IHYgNS4wMTYwNjYgaCAtMjcuNzA2NDcgeiIKICAgICAgIGlkPSJwYXRoMTAiCiAgICAgICBzdHlsZT0iZmlsbDojZmZmZmZmO2ZpbGwtb3BhY2l0eToxO3N0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMyIKICAgICAgIGQ9Im0gMzgwLjk4NDc4LDQ5LjA3Njg1NCBoIDguMDcyOTUgdiA1LjUwMjM4OCBoIDAuMTI1MDYgYyAxLjUyODQ0LC00LjA0MzQyMiA1LjE0MTEyLC02LjM2Mzg3MyA5LjE3MDY0LC02LjM2Mzg3MyAxLjA5NzcsMCAxLjY1MzUsMC4xODA2MzQgMS45MDM2MSwwLjI1MDEwOCB2IDkuMjQwMTIyIGMgLTAuNzkyMDEsLTAuMzA1Njg5IC0xLjc3ODU1LC0wLjQzMDc0MyAtMi43NTEyLC0wLjQzMDc0MyAtNS4wMTYwNiwwIC03Ljk0Nzg5LDMuNjEyNjc5IC03Ljk0Nzg5LDguNTU5MjcgdiAxNS40Nzg5NCBoIC04LjU1OTI3IFYgNDkuMDc2ODU0IFoiCiAgICAgICBpZD0icGF0aDExIgogICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDoxLjM4OTQ5IiAvPgogICAgPHBhdGgKICAgICAgIGNsYXNzPSJjbHMtMyIKICAgICAgIGQ9Im0gNDAyLjgxMzcsNjUuMjIyNzUgYyAwLC05Ljc4MjAyMyA3LjEwMDMxLC0xNy4wMDczODEgMTYuNzU3MjcsLTE3LjAwNzM4MSA4LjY4NDMzLDAgMTYuNzAxNyw1Ljc1MjQ5NiAxNi43MDE3LDE5LjE0NzE5OCB2IDAuNDMwNzQzIGggLTI0LjU5NDAxIGMgMC45MTcwNiw0Ljk2MDQ4NiA0LjA5OSw3LjAzMDgyOSA4LjA3Mjk1LDcuMDMwODI5IDIuOTMxODMsMCA1Ljc1MjQ5LC0xLjE2NzE3MyA3LjUzMTA0LC0zLjU0MzIwNSBsIDYuNDE5NDYsNC4zNDkxMSBjIC0yLjc1MTIsMy4zNjI1NzEgLTYuODUwMiw2LjU0NDUwNyAtMTMuOTUwNSw2LjU0NDUwNyAtOS43MjY0NSwwIC0xNi45Mzc5MSwtNy4xNTU4ODMgLTE2LjkzNzkxLC0xNi45Mzc5MDYgeiBtIDI0LjIzMjc0LC0zLjIzNzUxNiBjIC0wLjYxMTM4LC00LjA0MzQyMiAtMy4zNjI1NywtNi42MDAwODcgLTcuNTMxMDUsLTYuNjAwMDg3IC0zLjYxMjY3LDAgLTYuOTc1MjQsMi4wMTQ3NjMgLTcuODIyODMsNi42MDAwODcgeiIKICAgICAgIGlkPSJwYXRoMTIiCiAgICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjEuMzg5NDkiIC8+CiAgICA8cGF0aAogICAgICAgY2xhc3M9ImNscy0zIgogICAgICAgZD0ibSA0NDAuMzE2MDksNjUuMTY3MTcgYyAwLC05LjY3MDg2NCA2LjcyNTE0LC0xNi45Mzc5MDYgMTUuNzE1MTUsLTE2LjkzNzkwNiA0Ljc2NTk2LDAgOC40MzQyMiwyLjEzOTgxNyAxMC4yODIyNCw0LjgzNTQzMiBoIDAuMDU1NiBWIDM1LjQ0NTkzOCBoIDguNTU5MjcgdiA0NS44ODEwMjMgaCAtOC4wNzI5NSB2IC00LjQwNDY4OSBoIC0wLjEyNTA1IGMgLTEuNzA5MDgsMi44NzYyNDggLTUuODc3NTUsNS4yNjYxNzQgLTEwLjgyNDE0LDUuMjY2MTc0IC04LjY4NDMzLDAgLTE1LjYwNCwtNy4xNTU4ODMgLTE1LjYwNCwtMTcuMDA3MzgxIHogbSAxNy41NDkyOCw5LjQyMDc1NSBjIDUuMTQxMTIsMCA4LjY4NDMzLC00LjE1NDU4MSA4LjY4NDMzLC05LjM2NTE3NSAwLC01LjIxMDU5NSAtMy41NDMyMSwtOS4zNjUxNzYgLTguNjg0MzMsLTkuMzY1MTc2IC01LjE0MTEyLDAgLTguNjg0MzIsNC4wNDM0MjIgLTguNjg0MzIsOS4zNjUxNzYgMCw1LjMyMTc1NCAzLjU0MzIsOS4zNjUxNzUgOC42ODQzMiw5LjM2NTE3NSB6IgogICAgICAgaWQ9InBhdGgxMyIKICAgICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MS4zODk0OSIgLz4KICA8L2c+Cjwvc3ZnPgo="

_STANDALONE_FORGOT_LINK = (
    f'  <a href="/admin/standalone/_forgot-password" class="link">Forgot your password?</a>'
    if _ADMIN_RESET_EMAIL
    else ""
)
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
{_STANDALONE_FORGOT_LINK}
</div>
</body>
</html>"""

_STANDALONE_FORGOT_PW_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Forgot Password</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Forgot password</h1>
  <p class="subtitle">Enter your email address and we'll send you a link to reset your password.</p>
  <div class="error" id="err">Please enter a valid email address.</div>
  <form method="POST" action="/admin/standalone/_forgot-password">
    <label for="email">Email address</label>
    <input id="email" type="email" name="email" placeholder="you@company.com" autofocus required/>
    <button type="submit">Send reset link</button>
  </form>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""

_STANDALONE_FORGOT_PW_SENT_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Check Your Email</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <div style="font-size:32px;margin-bottom:12px;">&#9993;</div>
  <h1>Check your email</h1>
  <p class="subtitle">If that email matches our records, we've sent a password reset link. The link expires in 15 minutes.</p>
  <p style="font-size:13px;color:#a0a0a0;line-height:1.5;margin-top:12px;">
    Don't see it? Check your spam folder.
  </p>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""

_STANDALONE_RESET_PW_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Set New Password</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Set new password</h1>
  <p class="subtitle">Choose a new password for admin access.</p>
  <div class="error" id="err">Passwords do not match.</div>
  <div class="success" id="ok">Password changed successfully!</div>
  <form method="POST" action="/admin/standalone/_reset-password">
    <input type="hidden" name="token" value="{{{{token}}}}"/>
    <label for="new">New password</label>
    <input id="new" type="password" name="new_password" placeholder="New password" autofocus required minlength="6"/>
    <label for="confirm">Confirm new password</label>
    <input id="confirm" type="password" name="confirm_password" placeholder="Confirm new password" required minlength="6"/>
    <button type="submit">Set password</button>
  </form>
  <a href="/admin/standalone/" class="link">Back to sign in</a>
</div>
</body>
</html>"""

_STANDALONE_RESET_INVALID_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Agent Red — Invalid Link</title>
<style>{_STANDALONE_SHARED_STYLES}</style>
</head>
<body>
<div class="card">
  <img src="{_LOGO_DATA_URI}" alt="Agent Red" width="200" height="49" class="logo" />
  <h1>Invalid or expired link</h1>
  <p class="subtitle">This password reset link is no longer valid. It may have expired or already been used.</p>
  <a href="/admin/standalone/_forgot-password" class="link">Request a new link</a>
</div>
</body>
</html>"""


def _generate_reset_token(ttl: int = 900) -> str:
    """Create an HMAC-signed reset token valid for *ttl* seconds.

    Format: ``<nonce>.<expiry_ts>.<hmac_hex>``
    Signed with ``_ADMIN_HMAC_KEY`` (immutable, derived from env var) so any
    replica can validate — even after an in-memory password change.
    """
    nonce = _secrets.token_urlsafe(16)
    expiry = str(int(_time.time() + ttl))
    payload = f"{nonce}.{expiry}"
    sig = _hmac.new(
        _ADMIN_HMAC_KEY.encode(), payload.encode(), "sha256",
    ).hexdigest()
    return f"{payload}.{sig}"


def _validate_reset_token(token: str) -> bool:
    """Validate an HMAC-signed reset token.

    Checks signature, expiry, and best-effort single-use nonce tracking.
    Uses ``_ADMIN_HMAC_KEY`` (immutable) so validation works on any replica.
    """
    if not token or not _ADMIN_HMAC_KEY:
        return False
    parts = token.split(".")
    if len(parts) != 3:
        return False
    nonce, expiry_str, sig = parts
    # Recompute HMAC
    payload = f"{nonce}.{expiry_str}"
    expected = _hmac.new(
        _ADMIN_HMAC_KEY.encode(), payload.encode(), "sha256",
    ).hexdigest()
    if not _hmac.compare_digest(sig, expected):
        return False
    # Check expiry
    try:
        if _time.time() > float(expiry_str):
            return False
    except ValueError:
        return False
    # Best-effort single-use check (per-replica)
    if nonce in _admin_used_reset_nonces:
        return False
    return True


def _send_admin_password_changed_email(to_email: str, forgot_password_url: str) -> bool:
    """Send a confirmation email after a successful password reset.

    Security best practice: notify the admin that their password was changed,
    and provide a self-service recovery link in case they did not initiate it.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM_ADDRESS", "noreply@agentred.com")

    if not smtp_host:
        logger.warning("SMTP_HOST not configured — cannot send password changed confirmation email")
        return False

    subject = "Your Agent Red Admin Password Has Been Reset"

    html_body = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Inter,system-ui,sans-serif;">
<div style="max-width:560px;margin:40px auto;padding:40px;background:#1f1f1f;border-radius:12px;border:1px solid #272727;">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="margin:0;font-size:20px;color:#F5F5F5;">Agent Red</h1>
    <p style="margin:4px 0 0;font-size:14px;color:#A0A0A0;">Customer Experience</p>
  </div>
  <h2 style="margin:0 0 16px;font-size:16px;color:#F5F5F5;">Password Reset Successful</h2>
  <p style="margin:0 0 16px;font-size:14px;color:#E0E0E0;line-height:1.6;">
    Your admin password has been reset successfully. You are now signed in.
  </p>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <div style="background:#2a1a1a;border:1px solid #4a2020;border-radius:8px;padding:16px;margin:0 0 16px;">
    <p style="margin:0 0 8px;font-size:13px;color:#ff6b6b;font-weight:600;">
      Did not make this change?
    </p>
    <p style="margin:0 0 12px;font-size:13px;color:#A0A0A0;line-height:1.5;">
      If you did not reset your password, someone may have access to your account.
      Reset your password immediately to secure your account.
    </p>
    <a href="{forgot_password_url}" style="display:inline-block;padding:10px 24px;background:#ff3621;color:#ffffff;font-size:13px;font-weight:600;text-decoration:none;border-radius:6px;">
      Reset Password
    </a>
  </div>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <p style="margin:0;font-size:11px;color:#787878;text-align:center;">
    Agent Red Customer Experience &mdash; A product of Remaker Digital
  </p>
</div>
</body>
</html>"""

    plain_body = (
        f"Agent Red Admin Password Reset Successful\n\n"
        f"Your admin password has been reset successfully. You are now signed in.\n\n"
        f"If you did not reset your password, someone may have access to your account.\n"
        f"Reset your password immediately: {forgot_password_url}\n"
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Agent Red <{sender}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10.0) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                server.ehlo()
                if smtp_port != 25:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

        logger.info("Admin password changed confirmation email sent to %s", to_email)
        return True

    except Exception:
        logger.exception("Failed to send admin password changed confirmation email to %s", to_email)
        return False


def _send_admin_reset_email(to_email: str, reset_url: str) -> bool:
    """Send a password reset email via SMTP.

    Reuses the same SMTP env vars as admin_apikey_api.py.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM_ADDRESS", "noreply@agentred.com")

    if not smtp_host:
        logger.warning("SMTP_HOST not configured — cannot send password reset email")
        return False

    subject = "Reset Your Agent Red Admin Password"

    html_body = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Inter,system-ui,sans-serif;">
<div style="max-width:560px;margin:40px auto;padding:40px;background:#1f1f1f;border-radius:12px;border:1px solid #272727;">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="margin:0;font-size:20px;color:#F5F5F5;">Agent Red</h1>
    <p style="margin:4px 0 0;font-size:14px;color:#A0A0A0;">Customer Experience</p>
  </div>
  <h2 style="margin:0 0 16px;font-size:16px;color:#F5F5F5;">Password Reset</h2>
  <p style="margin:0 0 16px;font-size:14px;color:#E0E0E0;line-height:1.6;">
    We received a request to reset the admin password. Click the button below to choose a new password.
  </p>
  <div style="text-align:center;margin:24px 0;">
    <a href="{reset_url}" style="display:inline-block;padding:12px 32px;background:#ff3621;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;border-radius:8px;">
      Reset Password
    </a>
  </div>
  <p style="margin:16px 0 0;font-size:13px;color:#A0A0A0;line-height:1.5;">
    This link expires in 15 minutes. If you did not request this, you can safely ignore this email.
  </p>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <p style="margin:0 0 8px;font-size:13px;color:#A0A0A0;line-height:1.5;">
    If the button doesn't work, copy and paste this link into your browser:
  </p>
  <p style="margin:0;font-family:'JetBrains Mono',monospace;font-size:11px;color:#787878;word-break:break-all;">
    {reset_url}
  </p>
  <hr style="border:none;border-top:1px solid #272727;margin:24px 0;" />
  <p style="margin:0;font-size:11px;color:#787878;text-align:center;">
    Agent Red Customer Experience &mdash; A product of Remaker Digital
  </p>
</div>
</body>
</html>"""

    plain_body = (
        f"Agent Red Admin Password Reset\n\n"
        f"We received a request to reset the admin password.\n\n"
        f"Click this link to choose a new password:\n{reset_url}\n\n"
        f"This link expires in 15 minutes.\n"
        f"If you did not request this, you can safely ignore this email.\n"
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Agent Red <{sender}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10.0) as server:
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10.0) as server:
                server.ehlo()
                if smtp_port != 25:
                    server.starttls()
                if smtp_user and smtp_pass:
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)

        logger.info("Admin password reset email sent to %s", to_email)
        return True

    except Exception:
        logger.exception("Failed to send admin password reset email to %s", to_email)
        return False


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

    # ---- Forgot password flow (email-based reset) --------------------------

    @app.get("/admin/standalone/_forgot-password", include_in_schema=False)
    async def _admin_forgot_password_form(request: Request) -> HTMLResponse:
        """Show the forgot password form (enter email)."""
        return HTMLResponse(content=_STANDALONE_FORGOT_PW_HTML)

    @app.post("/admin/standalone/_forgot-password", include_in_schema=False)
    async def _admin_forgot_password(request: Request) -> HTMLResponse:
        """Process forgot-password: validate email, send reset link."""
        global _admin_reset_rate_limit

        form = await request.form()
        email = str(form.get("email", "")).strip().lower()

        # Rate limit: 3 requests per 5 min per IP
        client_ip = request.client.host if request.client else "unknown"
        now = _time.time()
        window = 300  # 5 minutes
        hits = _admin_reset_rate_limit.get(client_ip, [])
        hits = [t for t in hits if now - t < window]
        if len(hits) >= 3:
            rate_html = _STANDALONE_FORGOT_PW_HTML.replace(
                'Please enter a valid email address.',
                'Too many requests. Please wait a few minutes and try again.',
            ).replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=rate_html, status_code=429)
        hits.append(now)
        _admin_reset_rate_limit[client_ip] = hits

        # Validate email format
        if not email or "@" not in email:
            error_html = _STANDALONE_FORGOT_PW_HTML.replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=error_html, status_code=400)

        # Check if email matches the configured reset email
        if _ADMIN_RESET_EMAIL and email == _ADMIN_RESET_EMAIL:
            # Generate HMAC-signed token (any replica can validate)
            reset_token = _generate_reset_token(ttl=900)

            # Build reset URL
            scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
            host = request.headers.get("host", request.url.netloc)
            reset_url = f"{scheme}://{host}/admin/standalone/_reset-password?token={reset_token}"

            _send_admin_reset_email(email, reset_url)

        # Always return success page (prevents email enumeration)
        return HTMLResponse(content=_STANDALONE_FORGOT_PW_SENT_HTML)

    @app.get("/admin/standalone/_reset-password", include_in_schema=False)
    async def _admin_reset_password_form(request: Request) -> HTMLResponse:
        """Show the set-new-password form if the token is valid."""
        token = request.query_params.get("token", "")
        if not _validate_reset_token(token):
            return HTMLResponse(content=_STANDALONE_RESET_INVALID_HTML, status_code=400)
        # Inject token into the hidden field
        form_html = _STANDALONE_RESET_PW_HTML.replace("{{token}}", token)
        return HTMLResponse(content=form_html)

    @app.post("/admin/standalone/_reset-password", include_in_schema=False)
    async def _admin_reset_password(request: Request) -> StarletteResponse:
        """Process password reset: validate token, auto-login user."""

        form = await request.form()
        token = str(form.get("token", ""))
        new_pw = str(form.get("new_password", ""))
        confirm = str(form.get("confirm_password", ""))

        # Validate token
        if not _validate_reset_token(token):
            return HTMLResponse(content=_STANDALONE_RESET_INVALID_HTML, status_code=400)

        # Validate passwords match
        if new_pw != confirm:
            form_html = _STANDALONE_RESET_PW_HTML.replace("{{token}}", token).replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=form_html, status_code=400)

        # Validate minimum length
        if len(new_pw) < 6:
            form_html = _STANDALONE_RESET_PW_HTML.replace("{{token}}", token).replace(
                'Passwords do not match.',
                'Password must be at least 6 characters.',
            ).replace(
                'class="error" id="err"', 'class="error" id="err" style="display:block"',
            )
            return HTMLResponse(content=form_html, status_code=400)

        # Multi-replica safety: Do NOT change the password in-memory.
        # With minReplicas > 1, an in-memory password change only affects
        # THIS replica — the other replica(s) keep the env var password,
        # causing 50% login failures and cookie mismatches.
        #
        # Instead: auto-login the user by setting the session cookie (derived
        # from the env var password, identical on all replicas) and redirect
        # to the admin dashboard.  The user gets a 7-day authenticated session
        # without needing to know the password.
        #
        # To change the actual admin password, update the ADMIN_PREVIEW_PASSWORD
        # env var on the Container App (triggers rolling restart of all replicas).

        # Mark nonce as used (best-effort single-use per replica)
        nonce = token.split(".")[0] if "." in token else ""
        if nonce:
            _admin_used_reset_nonces.add(nonce)

        logger.info("Admin password reset: auto-login via session cookie")

        # Send password-changed confirmation email (non-blocking best-effort).
        # Includes a "Reset Password" recovery link in case the admin did not
        # initiate this change (security best practice, WI #203 UX review).
        if _ADMIN_RESET_EMAIL:
            scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
            host = request.headers.get("host", request.url.hostname or "localhost")
            forgot_url = f"{scheme}://{host}/admin/standalone/_forgot-password"
            _send_admin_password_changed_email(_ADMIN_RESET_EMAIL, forgot_url)

        # Auto-login: set the session cookie and redirect to admin dashboard.
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

    Wires TenantRepository and TeamMemberRepository lookup methods into
    the auth middleware so that Shopify session tokens, API keys,
    publishable widget keys, and per-user API keys can resolve to
    tenant/team-member documents in Cosmos DB.
    """
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


# --- AGNTCY SDK lifecycle ---------------------------------------------------
from src.multi_tenant.agntcy_sdk_integration import (  # noqa: E402
    close_agntcy_sdk,
    get_sdk_status,
    init_agntcy_sdk,
)


@app.on_event("startup")
async def _startup_agntcy_sdk() -> None:
    """Initialize AGNTCY SDK factory and transport on application startup."""
    try:
        await init_agntcy_sdk()
        status = get_sdk_status()
        logger.info("AGNTCY SDK ready: %s", status)
    except Exception:
        # Non-fatal — SDK may not be fully configured during early phases
        logger.warning(
            "AGNTCY SDK initialization failed — platform features unavailable. "
            "This is expected if AGNTCY transport endpoints are not configured."
        )


@app.on_event("shutdown")
async def _shutdown_agntcy_sdk() -> None:
    """Shut down AGNTCY SDK transport on application shutdown."""
    await close_agntcy_sdk()
    logger.info("AGNTCY SDK shut down")


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
        from src.multi_tenant.repository import AuditLogRepository, TeamMemberRepository

        team_repo = TeamMemberRepository()
        audit_repo = AuditLogRepository()
        configure_admin_team_services(team_repo=team_repo, audit_repo=audit_repo)
        logger.info("Admin team management API initialized (5 endpoints + audit)")
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
# Admin Quick Action API (WI #226-229)
# ---------------------------------------------------------------------------

from src.multi_tenant.admin_quick_action_api import configure_admin_quick_action_services  # noqa: E402
from src.multi_tenant.tenant_config_api import configure_quick_action_serving  # noqa: E402


@app.on_event("startup")
async def _startup_admin_quick_action_services() -> None:
    """Initialize the Admin Quick Action API and config-serving integration.

    Wires PreferencesRepository into:
      1. Admin CRUD endpoints (/api/admin/quick-actions)
      2. Config serving (GET /api/config quick_actions field)

    Non-fatal: admin endpoints return 503 if initialization fails;
    config serving returns quick_actions: null.
    """
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
# Activation service wiring (Save → Activate model)
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def _startup_activation_service() -> None:
    """Wire ActivationService with repos + config processor.

    Required for the Save → Activate configuration lifecycle. The service
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


@app.on_event("startup")
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


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["system"])
async def health() -> dict:
    """Liveness probe — returns 200 if the process is running."""
    from src.multi_tenant.api_versioning import API_VERSION, PRODUCT_VERSION

    return {"status": "healthy", "version": API_VERSION, "product_version": PRODUCT_VERSION}


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
