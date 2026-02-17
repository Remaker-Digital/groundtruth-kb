"""FastAPI application factory for Agent Red Customer Experience.

Creates and configures the FastAPI application instance with exception
handling, CORS middleware, and structured logging.

R1 refactoring — session 31.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.multi_tenant.structured_logging import configure_structured_logging


def create_app() -> FastAPI:
    """Create and return a fully configured FastAPI application.

    This factory:
    1. Creates the FastAPI instance with all metadata (tags, responses, docs_url, etc.)
    2. Registers the global exception handler
    3. Adds CORS middleware
    4. Configures structured logging

    Returns:
        A configured FastAPI application instance ready for router registration.
    """

    # --- FastAPI app creation (main.py lines 27-76) ---

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

    # --- Global exception handler (main.py lines 82-125) ---

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

    # --- CORS middleware (main.py lines 128-146) ---

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

    # --- Structured logging (main.py lines 152-155) ---

    configure_structured_logging()

    return app
