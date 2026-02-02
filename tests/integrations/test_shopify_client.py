"""Shopify GraphQL Client tests — ShopifyGraphQLClient unit tests.

Test IDs: SHC-01 through SHC-15.

Validates:
    - GraphQL query and variable construction (SHC-01, SHC-02)
    - Client setup: endpoint URL, headers, pool limits, timeout, API version (SHC-03..SHC-07)
    - Error handling: HTTP errors, non-200, invalid JSON, GraphQL errors (SHC-08..SHC-12)
    - Successful execution returns data dict (SHC-13)
    - Context manager protocol (SHC-14)
    - Singleton env var validation (SHC-15)

All network calls are mocked via httpx.AsyncClient.post.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.integrations.shopify_client import (
    ShopifyAPIError,
    ShopifyGraphQLClient,
    ShopifyGraphQLError,
    _API_VERSION,
    _MAX_CONNECTIONS,
    _MAX_KEEPALIVE,
    _TIMEOUT_SECONDS,
    get_shopify_client,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STORE_URL = "test-store.myshopify.com"
ACCESS_TOKEN = "shpat_test_token_abc123"
SAMPLE_QUERY = "{ shop { name } }"
SAMPLE_VARIABLES = {"first": 10, "cursor": "abc"}


def _make_response(
    status_code: int = 200,
    json_data: dict | None = None,
    text: str = "",
    *,
    json_raises: bool = False,
) -> MagicMock:
    """Build a mock httpx.Response with configurable behaviour."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.text = text or (str(json_data) if json_data else "")
    if json_raises:
        resp.json.side_effect = ValueError("Not JSON")
    elif json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.return_value = {}
    return resp


def _client() -> ShopifyGraphQLClient:
    """Create a client with test credentials."""
    return ShopifyGraphQLClient(STORE_URL, ACCESS_TOKEN)


# ===================================================================
# SHC-01: GraphQL query construction (query only)
# ===================================================================


class TestQueryConstruction:
    """SHC-01: execute() sends correct JSON payload for query-only calls."""

    @pytest.mark.unit
    async def test_query_only_payload(self) -> None:
        """POST body contains 'query' key and no 'variables' key."""
        client = _client()
        mock_response = _make_response(json_data={"data": {"shop": {"name": "Test"}}})

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
            await client.execute(SAMPLE_QUERY)

            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            payload = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
            assert payload["query"] == SAMPLE_QUERY
            assert "variables" not in payload

        await client.close()


# ===================================================================
# SHC-02: GraphQL query with variables
# ===================================================================


class TestQueryWithVariables:
    """SHC-02: execute() includes variables in payload when provided."""

    @pytest.mark.unit
    async def test_query_with_variables_payload(self) -> None:
        """POST body contains both 'query' and 'variables' keys."""
        client = _client()
        mock_response = _make_response(json_data={"data": {"products": []}})

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
            await client.execute(SAMPLE_QUERY, variables=SAMPLE_VARIABLES)

            payload = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
            assert payload["query"] == SAMPLE_QUERY
            assert payload["variables"] == SAMPLE_VARIABLES

        await client.close()


# ===================================================================
# SHC-03: Client setup — endpoint URL construction
# ===================================================================


class TestEndpointURL:
    """SHC-03: Endpoint URL is constructed correctly from store_url and api_version."""

    @pytest.mark.unit
    async def test_endpoint_url_plain(self) -> None:
        """Plain store_url produces correct GraphQL endpoint."""
        client = ShopifyGraphQLClient("my-store.myshopify.com", ACCESS_TOKEN)
        assert client._endpoint == f"https://my-store.myshopify.com/admin/api/{_API_VERSION}/graphql.json"
        await client.close()

    @pytest.mark.unit
    async def test_endpoint_url_strips_protocol(self) -> None:
        """https:// prefix is stripped from store_url before constructing endpoint."""
        client = ShopifyGraphQLClient("https://my-store.myshopify.com", ACCESS_TOKEN)
        assert client._endpoint == f"https://my-store.myshopify.com/admin/api/{_API_VERSION}/graphql.json"
        await client.close()

    @pytest.mark.unit
    async def test_endpoint_url_strips_trailing_slash(self) -> None:
        """Trailing slash is stripped from store_url."""
        client = ShopifyGraphQLClient("my-store.myshopify.com/", ACCESS_TOKEN)
        assert client._endpoint == f"https://my-store.myshopify.com/admin/api/{_API_VERSION}/graphql.json"
        await client.close()

    @pytest.mark.unit
    async def test_endpoint_url_custom_api_version(self) -> None:
        """Custom api_version is used in the endpoint URL."""
        client = ShopifyGraphQLClient(STORE_URL, ACCESS_TOKEN, api_version="2024-10")
        assert "/api/2024-10/" in client._endpoint
        await client.close()


# ===================================================================
# SHC-04: Client setup — access token in headers
# ===================================================================


class TestAccessTokenHeader:
    """SHC-04: X-Shopify-Access-Token header is set on the HTTP client."""

    @pytest.mark.unit
    async def test_access_token_header(self) -> None:
        """HTTP client default headers include the access token."""
        client = _client()
        headers = client._http_client.headers
        assert headers["X-Shopify-Access-Token"] == ACCESS_TOKEN
        await client.close()

    @pytest.mark.unit
    async def test_content_type_header(self) -> None:
        """HTTP client default headers include application/json content type."""
        client = _client()
        headers = client._http_client.headers
        assert headers["Content-Type"] == "application/json"
        await client.close()


# ===================================================================
# SHC-05: Client setup — connection pool limits
# ===================================================================


class TestConnectionPoolLimits:
    """SHC-05: httpx connection pool uses configured limits."""

    @pytest.mark.unit
    async def test_max_connections_constant(self) -> None:
        """_MAX_CONNECTIONS constant is 20."""
        assert _MAX_CONNECTIONS == 20

    @pytest.mark.unit
    async def test_max_keepalive_constant(self) -> None:
        """_MAX_KEEPALIVE constant is 5."""
        assert _MAX_KEEPALIVE == 5

    @pytest.mark.unit
    async def test_pool_limits_applied(self) -> None:
        """Client is constructed with httpx.Limits using the configured values."""
        with patch("src.integrations.shopify_client.httpx.AsyncClient") as mock_cls:
            mock_cls.return_value = MagicMock()
            ShopifyGraphQLClient(STORE_URL, ACCESS_TOKEN)

            call_kwargs = mock_cls.call_args.kwargs
            limits = call_kwargs["limits"]
            assert limits.max_connections == _MAX_CONNECTIONS
            assert limits.max_keepalive_connections == _MAX_KEEPALIVE


# ===================================================================
# SHC-06: Client setup — timeout
# ===================================================================


class TestTimeout:
    """SHC-06: httpx timeout matches configured value."""

    @pytest.mark.unit
    async def test_timeout_value(self) -> None:
        """Client timeout matches _TIMEOUT_SECONDS constant."""
        client = _client()
        timeout = client._http_client.timeout
        assert timeout.connect == _TIMEOUT_SECONDS
        assert timeout.read == _TIMEOUT_SECONDS
        assert _TIMEOUT_SECONDS == 30.0
        await client.close()


# ===================================================================
# SHC-07: Client setup — default API version
# ===================================================================


class TestDefaultAPIVersion:
    """SHC-07: Default API version is 2025-01."""

    @pytest.mark.unit
    async def test_default_api_version_constant(self) -> None:
        """_API_VERSION is '2025-01'."""
        assert _API_VERSION == "2025-01"

    @pytest.mark.unit
    async def test_default_api_version_in_endpoint(self) -> None:
        """Client constructed without explicit api_version uses the default."""
        client = _client()
        assert f"/api/{_API_VERSION}/" in client._endpoint
        await client.close()


# ===================================================================
# SHC-08: HTTP error handling (httpx.HTTPError -> ShopifyAPIError)
# ===================================================================


class TestHTTPErrorHandling:
    """SHC-08: httpx.HTTPError during POST is wrapped in ShopifyAPIError."""

    @pytest.mark.unit
    async def test_http_error_raises_shopify_api_error(self) -> None:
        """httpx.HTTPError becomes ShopifyAPIError."""
        client = _client()

        with patch.object(
            client._http_client,
            "post",
            new_callable=AsyncMock,
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            with pytest.raises(ShopifyAPIError, match="HTTP request failed"):
                await client.execute(SAMPLE_QUERY)

        await client.close()

    @pytest.mark.unit
    async def test_http_error_preserves_cause(self) -> None:
        """ShopifyAPIError wraps the original httpx exception as __cause__."""
        client = _client()
        original = httpx.TimeoutException("timed out")

        with patch.object(
            client._http_client,
            "post",
            new_callable=AsyncMock,
            side_effect=original,
        ):
            with pytest.raises(ShopifyAPIError) as exc_info:
                await client.execute(SAMPLE_QUERY)
            assert exc_info.value.__cause__ is original

        await client.close()


# ===================================================================
# SHC-09: Non-200 status response -> ShopifyAPIError
# ===================================================================


class TestNon200Response:
    """SHC-09: Non-200 HTTP status raises ShopifyAPIError."""

    @pytest.mark.unit
    async def test_401_raises_shopify_api_error(self) -> None:
        """HTTP 401 raises ShopifyAPIError with status code in message."""
        client = _client()
        mock_response = _make_response(status_code=401, text="Unauthorized")

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyAPIError, match="HTTP 401"):
                await client.execute(SAMPLE_QUERY)

        await client.close()

    @pytest.mark.unit
    async def test_500_raises_shopify_api_error(self) -> None:
        """HTTP 500 raises ShopifyAPIError."""
        client = _client()
        mock_response = _make_response(status_code=500, text="Internal Server Error")

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyAPIError, match="HTTP 500"):
                await client.execute(SAMPLE_QUERY)

        await client.close()

    @pytest.mark.unit
    async def test_429_raises_shopify_api_error(self) -> None:
        """HTTP 429 (rate limit) raises ShopifyAPIError."""
        client = _client()
        mock_response = _make_response(status_code=429, text="Throttled")

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyAPIError, match="HTTP 429"):
                await client.execute(SAMPLE_QUERY)

        await client.close()


# ===================================================================
# SHC-10: Invalid JSON response -> ShopifyAPIError
# ===================================================================


class TestInvalidJSONResponse:
    """SHC-10: Response with invalid JSON raises ShopifyAPIError."""

    @pytest.mark.unit
    async def test_invalid_json_raises_shopify_api_error(self) -> None:
        """Non-JSON 200 response raises ShopifyAPIError."""
        client = _client()
        mock_response = _make_response(status_code=200, text="<html>not json</html>", json_raises=True)

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyAPIError, match="Invalid JSON"):
                await client.execute(SAMPLE_QUERY)

        await client.close()


# ===================================================================
# SHC-11: GraphQL errors in response body -> ShopifyGraphQLError
# ===================================================================


class TestGraphQLErrors:
    """SHC-11: GraphQL errors field in response raises ShopifyGraphQLError."""

    @pytest.mark.unit
    async def test_graphql_error_raises_shopify_graphql_error(self) -> None:
        """Single GraphQL error raises ShopifyGraphQLError with correct message."""
        client = _client()
        mock_response = _make_response(
            json_data={
                "errors": [{"message": "Field 'foo' doesn't exist on type 'Shop'"}],
            },
        )

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyGraphQLError) as exc_info:
                await client.execute(SAMPLE_QUERY)

            assert len(exc_info.value.errors) == 1
            assert "Field 'foo'" in exc_info.value.errors[0]

        await client.close()


# ===================================================================
# SHC-12: Multiple GraphQL errors
# ===================================================================


class TestMultipleGraphQLErrors:
    """SHC-12: Multiple GraphQL errors are all captured."""

    @pytest.mark.unit
    async def test_multiple_graphql_errors(self) -> None:
        """All error messages are captured in ShopifyGraphQLError.errors list."""
        client = _client()
        mock_response = _make_response(
            json_data={
                "errors": [
                    {"message": "Error one"},
                    {"message": "Error two"},
                    {"message": "Error three"},
                ],
            },
        )

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyGraphQLError) as exc_info:
                await client.execute(SAMPLE_QUERY)

            assert len(exc_info.value.errors) == 3
            assert exc_info.value.errors[0] == "Error one"
            assert exc_info.value.errors[1] == "Error two"
            assert exc_info.value.errors[2] == "Error three"

        await client.close()

    @pytest.mark.unit
    async def test_graphql_error_string_format(self) -> None:
        """GraphQL errors that are plain strings (not dicts) are handled."""
        client = _client()
        mock_response = _make_response(
            json_data={
                "errors": ["simple string error"],
            },
        )

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(ShopifyGraphQLError) as exc_info:
                await client.execute(SAMPLE_QUERY)

            assert exc_info.value.errors[0] == "simple string error"

        await client.close()


# ===================================================================
# SHC-13: Successful execute returns data dict
# ===================================================================


class TestSuccessfulExecute:
    """SHC-13: Successful response returns the 'data' portion."""

    @pytest.mark.unit
    async def test_returns_data_dict(self) -> None:
        """execute() returns body['data'] on success."""
        client = _client()
        expected = {"shop": {"name": "My Store", "id": "gid://shopify/Shop/1"}}
        mock_response = _make_response(json_data={"data": expected})

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.execute(SAMPLE_QUERY)
            assert result == expected

        await client.close()

    @pytest.mark.unit
    async def test_returns_empty_dict_when_no_data_key(self) -> None:
        """execute() returns {} if response body has no 'data' key."""
        client = _client()
        mock_response = _make_response(json_data={"extensions": {"cost": 1}})

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response):
            result = await client.execute(SAMPLE_QUERY)
            assert result == {}

        await client.close()

    @pytest.mark.unit
    async def test_posts_to_correct_endpoint(self) -> None:
        """execute() sends POST to the constructed endpoint URL."""
        client = _client()
        mock_response = _make_response(json_data={"data": {}})

        with patch.object(client._http_client, "post", new_callable=AsyncMock, return_value=mock_response) as mock_post:
            await client.execute(SAMPLE_QUERY)

            args, kwargs = mock_post.call_args
            assert args[0] == client._endpoint

        await client.close()


# ===================================================================
# SHC-14: Context manager (async with)
# ===================================================================


class TestContextManager:
    """SHC-14: ShopifyGraphQLClient works as an async context manager."""

    @pytest.mark.unit
    async def test_async_with_returns_client(self) -> None:
        """async with block yields the client instance."""
        async with ShopifyGraphQLClient(STORE_URL, ACCESS_TOKEN) as client:
            assert isinstance(client, ShopifyGraphQLClient)
            assert client._endpoint.startswith("https://")

    @pytest.mark.unit
    async def test_async_with_closes_on_exit(self) -> None:
        """Exiting async with block closes the HTTP client."""
        client = ShopifyGraphQLClient(STORE_URL, ACCESS_TOKEN)
        with patch.object(client, "close", new_callable=AsyncMock) as mock_close:
            async with client:
                pass
            mock_close.assert_awaited_once()


# ===================================================================
# SHC-15: Singleton — get_shopify_client() env var validation
# ===================================================================


class TestSingleton:
    """SHC-15: get_shopify_client() validates env vars and creates singleton."""

    @pytest.mark.unit
    async def test_missing_store_url_raises_runtime_error(self) -> None:
        """RuntimeError raised when SHOPIFY_STORE_URL is not set."""
        # Reset the module-level singleton
        import src.integrations.shopify_client as mod
        mod._shared_client = None

        with patch.dict("os.environ", {"SHOPIFY_ACCESS_TOKEN": "tok"}, clear=True):
            with pytest.raises(RuntimeError, match="SHOPIFY_STORE_URL"):
                get_shopify_client()

    @pytest.mark.unit
    async def test_missing_access_token_raises_runtime_error(self) -> None:
        """RuntimeError raised when SHOPIFY_ACCESS_TOKEN is not set."""
        import src.integrations.shopify_client as mod
        mod._shared_client = None

        with patch.dict("os.environ", {"SHOPIFY_STORE_URL": "x.myshopify.com"}, clear=True):
            with pytest.raises(RuntimeError, match="SHOPIFY_ACCESS_TOKEN"):
                get_shopify_client()

    @pytest.mark.unit
    async def test_both_missing_raises_runtime_error(self) -> None:
        """RuntimeError raised when both env vars are missing."""
        import src.integrations.shopify_client as mod
        mod._shared_client = None

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError):
                get_shopify_client()

    @pytest.mark.unit
    async def test_valid_env_vars_create_client(self) -> None:
        """Client is created when both env vars are set."""
        import src.integrations.shopify_client as mod
        mod._shared_client = None

        with patch.dict(
            "os.environ",
            {"SHOPIFY_STORE_URL": STORE_URL, "SHOPIFY_ACCESS_TOKEN": ACCESS_TOKEN},
            clear=True,
        ):
            client = get_shopify_client()
            assert isinstance(client, ShopifyGraphQLClient)
            assert client._endpoint.endswith("/graphql.json")
            # Clean up singleton for other tests
            mod._shared_client = None

    @pytest.mark.unit
    async def test_singleton_returns_same_instance(self) -> None:
        """Subsequent calls return the same client instance."""
        import src.integrations.shopify_client as mod
        mod._shared_client = None

        with patch.dict(
            "os.environ",
            {"SHOPIFY_STORE_URL": STORE_URL, "SHOPIFY_ACCESS_TOKEN": ACCESS_TOKEN},
            clear=True,
        ):
            first = get_shopify_client()
            second = get_shopify_client()
            assert first is second
            # Clean up
            mod._shared_client = None
