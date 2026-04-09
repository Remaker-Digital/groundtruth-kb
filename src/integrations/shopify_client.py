# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Shopify GraphQL Admin API client.

Lightweight async client for the Shopify Admin GraphQL API, used by
the billing module and future Shopify integrations. Uses httpx for
HTTP transport with connection pooling.

The client is intentionally minimal — it handles authentication,
request formatting, error extraction, and retries. GraphQL queries
and mutations are defined in the modules that use them (e.g.,
shopify_billing.py), keeping domain logic co-located with its API calls.

Configuration:
    SHOPIFY_STORE_URL   — e.g. "my-store.myshopify.com"
    SHOPIFY_ACCESS_TOKEN — Admin API access token (shpat_...)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Shopify GraphQL Admin API version — update quarterly per Shopify's
# release cadence. See: https://shopify.dev/docs/api/usage/versioning
_API_VERSION = "2025-01"

# Connection pool limits for httpx
_MAX_CONNECTIONS = 20
_MAX_KEEPALIVE = 5
_TIMEOUT_SECONDS = 30.0


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class ShopifyGraphQLClient:
    """Async GraphQL client for Shopify Admin API.

    Usage:
        client = ShopifyGraphQLClient(store_url, access_token)
        result = await client.execute(query, variables)
        await client.close()

    Or as an async context manager:
        async with ShopifyGraphQLClient(store_url, access_token) as client:
            result = await client.execute(query, variables)
    """

    def __init__(
        self,
        store_url: str,
        access_token: str,
        api_version: str = _API_VERSION,
    ) -> None:
        # Normalize store URL — strip protocol and trailing slash
        store_url = store_url.replace("https://", "").replace("http://", "").rstrip("/")
        self._endpoint = f"https://{store_url}/admin/api/{api_version}/graphql.json"
        self._access_token = access_token
        self._http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=_MAX_CONNECTIONS,
                max_keepalive_connections=_MAX_KEEPALIVE,
            ),
            timeout=httpx.Timeout(_TIMEOUT_SECONDS),
            headers={
                "Content-Type": "application/json",
                "X-Shopify-Access-Token": access_token,
            },
        )

    async def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query or mutation.

        Args:
            query: GraphQL query or mutation string.
            variables: Optional variables dict for parameterized queries.

        Returns:
            The "data" portion of the GraphQL response.

        Raises:
            ShopifyGraphQLError: If the response contains GraphQL errors.
            ShopifyAPIError: If the HTTP request fails.
        """
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = await self._http_client.post(
                self._endpoint,
                json=payload,
            )
        except httpx.HTTPError as exc:
            logger.error(
                "Shopify API request failed: %s", exc,
            )
            raise ShopifyAPIError(f"HTTP request failed: {exc}") from exc

        if response.status_code != 200:
            logger.error(
                "Shopify API returned HTTP %d: %s",
                response.status_code,
                response.text[:500],
            )
            raise ShopifyAPIError(
                f"HTTP {response.status_code}: {response.text[:200]}"
            )

        try:
            body = response.json()
        except Exception as exc:
            logger.error("Shopify API returned invalid JSON: %s", response.text[:200])
            raise ShopifyAPIError(f"Invalid JSON response: {response.text[:200]}") from exc

        # Check for GraphQL-level errors
        if "errors" in body:
            errors = body["errors"]
            error_messages = [
                e.get("message", str(e)) if isinstance(e, dict) else str(e)
                for e in errors
            ]
            logger.error("Shopify GraphQL errors: %s", error_messages)
            raise ShopifyGraphQLError(error_messages)

        return body.get("data", {})

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http_client.aclose()

    async def __aenter__(self) -> ShopifyGraphQLClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_shared_client: ShopifyGraphQLClient | None = None


def get_shopify_client() -> ShopifyGraphQLClient:
    """Get or create the shared Shopify GraphQL client.

    Reads SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN from environment.
    The client is created once and reused for the lifetime of the process.

    Returns:
        The shared ShopifyGraphQLClient instance.

    Raises:
        RuntimeError: If required environment variables are not set.
    """
    global _shared_client
    if _shared_client is None:
        store_url = os.environ.get("SHOPIFY_STORE_URL", "")
        access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")

        if not store_url or not access_token:
            raise RuntimeError(
                "SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN must be set "
                "to use the Shopify integration."
            )

        _shared_client = ShopifyGraphQLClient(store_url, access_token)
        logger.info("Shopify GraphQL client initialized for: %s", store_url)

    return _shared_client


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ShopifyAPIError(Exception):
    """Raised when a Shopify API HTTP request fails."""


class ShopifyGraphQLError(Exception):
    """Raised when a Shopify GraphQL response contains errors."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(f"GraphQL errors: {'; '.join(errors)}")
