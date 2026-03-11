"""API versioning headers middleware (WI #140).

Adds API version information to all responses via headers. This allows
clients to detect version changes and handle deprecation notices.

Headers added:
    X-API-Version: 1.0.0 (API contract version, changes on breaking changes)
    X-Product-Version: 1.25.1 (deployment/release version, changes every release)
    X-API-Deprecation-Notice: (only when deprecated paths are accessed)

The version follows semantic versioning. Breaking changes increment the
major version. The version is maintained in one place (this module) and
propagated via response headers.

Architecture references:
    - Decision #24: API versioning strategy (header-based, not URL-based)
    - Shopify API versioning pattern (quarterly, header-based)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# API version
# ---------------------------------------------------------------------------

API_VERSION = "1.0.0"

# Product release version — updated with each deployment.
# This is displayed in the admin sidebar footer and returned via
# the X-Product-Version response header on all API calls.
PRODUCT_VERSION = "1.82.0"

# Deprecated paths — these still work but clients should migrate.
# Format: {path_prefix: deprecation_message}
DEPRECATED_PATHS: dict[str, str] = {
    # No deprecated paths at launch
}


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


class ApiVersionMiddleware:
    """ASGI middleware that adds API versioning headers to all responses.

    Adds X-API-Version to every HTTP response. If the request path matches
    a deprecated endpoint, adds X-API-Deprecation-Notice with migration
    guidance.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Check for deprecated path
        deprecation_notice: str | None = None
        for prefix, notice in DEPRECATED_PATHS.items():
            if path.startswith(prefix):
                deprecation_notice = notice
                break

        async def send_with_version(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-api-version", API_VERSION.encode()))
                headers.append((b"x-product-version", PRODUCT_VERSION.encode()))

                if deprecation_notice:
                    headers.append(
                        (b"x-api-deprecation-notice", deprecation_notice.encode())
                    )

                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_with_version)
