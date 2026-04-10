# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Static file serving for Agent Red Customer Experience.

Mounts the Shopify embedded admin SPA, the provider admin console SPA,
and the widget JS bundle endpoint on the FastAPI application.

R1 refactoring — session 31. Provider admin added — session 39.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse, Response
from starlette.staticfiles import StaticFiles

logger = logging.getLogger(__name__)


def mount_static_apps(app: FastAPI) -> None:
    """Mount the admin SPAs and widget JS bundle on *app*.

    Serves:
    - Shopify embedded admin SPA at /admin/shopify
    - Provider admin console SPA at /admin/provider
    - Widget JS bundle at /widget.js

    Path calculations use parent.parent.parent because this module lives
    at src/app/static_serving.py (one level deeper than src/main.py).
    """

    # ---------------------------------------------------------------------------
    # Shopify Embedded Admin SPA (static files + catch-all for SPA routing)
    # ---------------------------------------------------------------------------

    _admin_shopify_dist = pathlib.Path(__file__).resolve().parent.parent.parent / "admin" / "shopify" / "dist"

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

            If full_path matches a real file in dist/ (e.g. primary-logo-no-wordmark.svg),
            serve that file directly.  Otherwise fall through to index.html
            for SPA client-side routing.
            """
            # Serve real static files (SVG, PNG, etc.) from dist root
            candidate = _admin_shopify_dist / full_path
            if candidate.is_file() and ".." not in full_path:
                return FileResponse(str(candidate))
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
    # Provider Admin Console SPA (static files + catch-all for SPA routing)
    # ---------------------------------------------------------------------------

    _admin_provider_dist = pathlib.Path(__file__).resolve().parent.parent.parent / "admin" / "provider" / "dist"

    if _admin_provider_dist.is_dir():
        # Serve static assets (JS, CSS, sourcemaps) from the Vite build output
        app.mount(
            "/admin/provider/assets",
            StaticFiles(directory=str(_admin_provider_dist / "assets")),
            name="admin-provider-assets",
        )

        _PROVIDER_NO_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}

        @app.get("/admin/provider/{full_path:path}", include_in_schema=False)
        async def _admin_provider_spa(full_path: str) -> FileResponse:
            """Catch-all route for the provider admin console SPA.

            If full_path matches a real file in dist/ (e.g. primary-logo-no-wordmark.svg),
            serve that file directly.  Otherwise fall through to index.html
            for SPA client-side routing.
            """
            # Serve real static files (SVG, PNG, etc.) from dist root
            candidate = _admin_provider_dist / full_path
            if candidate.is_file() and ".." not in full_path:
                return FileResponse(str(candidate))
            return FileResponse(str(_admin_provider_dist / "index.html"), headers=_PROVIDER_NO_CACHE)

        @app.get("/admin/provider", include_in_schema=False)
        async def _admin_provider_index() -> FileResponse:
            """Serve the provider admin console SPA root."""
            return FileResponse(str(_admin_provider_dist / "index.html"), headers=_PROVIDER_NO_CACHE)

        logger.info("Provider admin console SPA mounted at /admin/provider")
    else:
        logger.warning(
            "Provider admin SPA dist directory not found at %s — "
            "provider console will not be available", _admin_provider_dist,
        )

    # ---------------------------------------------------------------------------
    # Widget JS bundle — served at /widget.js for embedding in any page
    # ---------------------------------------------------------------------------

    _widget_dist = pathlib.Path(__file__).resolve().parent.parent.parent / "widget" / "dist"
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
