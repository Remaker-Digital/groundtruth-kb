"""Root test configuration — shared fixtures for all test suites.

Provides:
    - FastAPI TestClient (sync and async)
    - Mock Cosmos DB (CosmosManager + container stubs)
    - Mock NATS (TenantNATSManager)
    - Mock Key Vault (TenantSecretService)
    - Tenant context factories for all tiers
    - Authenticated request helpers (API key + Shopify JWT)
    - Tenant resolution wiring for middleware tests

Work Item #103 (Test Infrastructure).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import (
    BillingChannel,
    TenantDocument,
    TenantStatus,
    TenantTier,
    TIER_DEFAULTS,
)

# Import modules that will be patched — ensures they're in sys.modules
# before patch() tries to resolve the dotted path.
import src.multi_tenant.cosmos_client as _cosmos_client_mod
import src.multi_tenant.nats_isolation as _nats_isolation_mod
import src.multi_tenant.tenant_secret_service as _secret_service_mod
import src.multi_tenant.pipeline_resilience as _pipeline_resilience_mod


# ---------------------------------------------------------------------------
# Tenant context factories — reusable across all test modules
# ---------------------------------------------------------------------------

STARTER_TENANT_ID = "t-starter-001"
PROFESSIONAL_TENANT_ID = "t-pro-002"
ENTERPRISE_TENANT_ID = "t-ent-003"


@pytest.fixture
def starter_context() -> TenantContext:
    """Active Starter-tier tenant context (API key auth)."""
    return make_tenant_context(
        tenant_id=STARTER_TENANT_ID,
        tier=TenantTier.STARTER,
    )


@pytest.fixture
def professional_context() -> TenantContext:
    """Active Professional-tier tenant context (API key auth)."""
    return make_tenant_context(
        tenant_id=PROFESSIONAL_TENANT_ID,
        tier=TenantTier.PROFESSIONAL,
    )


@pytest.fixture
def enterprise_context() -> TenantContext:
    """Active Enterprise-tier tenant context (Shopify session auth)."""
    return make_tenant_context(
        tenant_id=ENTERPRISE_TENANT_ID,
        tier=TenantTier.ENTERPRISE,
        auth_method="shopify_session",
        shop_domain="enterprise-shop.myshopify.com",
    )


def make_tenant_context(
    tenant_id: str = STARTER_TENANT_ID,
    tier: TenantTier = TenantTier.STARTER,
    status: TenantStatus = TenantStatus.ACTIVE,
    auth_method: str = "api_key",
    shop_domain: str | None = None,
    user_id: str | None = None,
    session_id: str | None = None,
) -> TenantContext:
    """Build a TenantContext with sensible defaults.

    Usable as both a direct call and a base for fixture customization.
    """
    return TenantContext(
        tenant_id=tenant_id,
        tier=tier,
        status=status,
        auth_method=auth_method,
        shop_domain=shop_domain,
        user_id=user_id,
        session_id=session_id,
    )


# ---------------------------------------------------------------------------
# Tenant document factories
# ---------------------------------------------------------------------------

def make_tenant_document(
    tenant_id: str = STARTER_TENANT_ID,
    tier: TenantTier = TenantTier.STARTER,
    status: TenantStatus = TenantStatus.ACTIVE,
    billing_channel: BillingChannel = BillingChannel.STRIPE,
    api_key_hash: str | None = None,
    shop_domain: str | None = None,
) -> dict[str, Any]:
    """Build a tenant document dict matching the Cosmos DB shape.

    Returns a plain dict (as Cosmos DB queries return), not a
    TenantDocument Pydantic model — matching how the middleware
    receives tenant data from repository lookups.
    """
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": tenant_id,
        "tenant_id": tenant_id,
        "status": status.value,
        "billing_channel": billing_channel.value,
        "tier": tier.value,
        "interval": "month",
        "addons": [],
        "stripe_customer_id": f"cus_test_{tenant_id}" if billing_channel == BillingChannel.STRIPE else None,
        "stripe_subscription_id": f"sub_test_{tenant_id}" if billing_channel == BillingChannel.STRIPE else None,
        "shopify_shop_domain": shop_domain,
        "shopify_subscription_id": None,
        "customer_email": f"{tenant_id}@test.example.com",
        "consent_status": "not_asked",
        "api_key_hash": api_key_hash,
        "rate_limit_rpm": None,
        "max_concurrent": None,
        "created_at": now,
        "updated_at": now,
        "deactivated_at": None,
        "grace_period_ends_at": None,
    }
    return doc


# ---------------------------------------------------------------------------
# API key helpers
# ---------------------------------------------------------------------------

# Deterministic test API keys — one per tier
TEST_API_KEY_STARTER = "arsk_test_starter_key_001"
TEST_API_KEY_PROFESSIONAL = "arsk_test_pro_key_002"
TEST_API_KEY_ENTERPRISE = "arsk_test_ent_key_003"


def hash_test_api_key(api_key: str) -> str:
    """Hash an API key the same way auth.py does."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


# Pre-computed hashes for the test keys
TEST_API_KEY_HASH_STARTER = hash_test_api_key(TEST_API_KEY_STARTER)
TEST_API_KEY_HASH_PROFESSIONAL = hash_test_api_key(TEST_API_KEY_PROFESSIONAL)
TEST_API_KEY_HASH_ENTERPRISE = hash_test_api_key(TEST_API_KEY_ENTERPRISE)


def auth_headers_api_key(api_key: str = TEST_API_KEY_STARTER) -> dict[str, str]:
    """Build request headers for API key authentication."""
    return {"X-API-Key": api_key}


def auth_headers_bearer(token: str) -> dict[str, str]:
    """Build request headers for Bearer token (Shopify session) auth."""
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Mock Cosmos DB
# ---------------------------------------------------------------------------


class MockContainerProxy:
    """In-memory mock of azure.cosmos.aio ContainerProxy.

    Supports basic CRUD operations for testing without a real database.
    Items are stored as dicts in a list, keyed by (id, partition_key).
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.items: list[dict[str, Any]] = []

    async def create_item(self, body: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        self.items.append(body)
        return body

    async def upsert_item(self, body: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        # Remove existing item with same id if present
        self.items = [
            item for item in self.items
            if item.get("id") != body.get("id")
        ]
        self.items.append(body)
        return body

    async def read_item(self, item: str, partition_key: str, **kwargs: Any) -> dict[str, Any]:
        for doc in self.items:
            if doc.get("id") == item:
                return doc
        from azure.cosmos.exceptions import CosmosResourceNotFoundError
        raise CosmosResourceNotFoundError(
            status_code=404,
            message=f"Item {item} not found",
        )

    async def delete_item(self, item: str, partition_key: str, **kwargs: Any) -> None:
        self.items = [doc for doc in self.items if doc.get("id") != item]

    async def patch_item(
        self, item: str, partition_key: str, patch_operations: list, **kwargs: Any,
    ) -> dict[str, Any]:
        for doc in self.items:
            if doc.get("id") == item:
                for op in patch_operations:
                    if op["op"] == "set":
                        path = op["path"].lstrip("/")
                        doc[path] = op["value"]
                    elif op["op"] == "incr":
                        path = op["path"].lstrip("/")
                        doc[path] = doc.get(path, 0) + op["value"]
                return doc
        from azure.cosmos.exceptions import CosmosResourceNotFoundError
        raise CosmosResourceNotFoundError(
            status_code=404,
            message=f"Item {item} not found",
        )

    def query_items(
        self, query: str, parameters: list | None = None, **kwargs: Any,
    ) -> "MockQueryIterator":
        """Return an async iterator over matching items.

        This is a simplified mock — it returns all items. Tests that
        need filtered results should pre-populate with only the
        expected items or use more targeted mocking.
        """
        return MockQueryIterator(self.items[:])

    async def read_all_items(self, **kwargs: Any) -> list[dict[str, Any]]:
        return self.items[:]


class MockQueryIterator:
    """Async iterator matching Cosmos DB query result pattern."""

    def __init__(self, items: list[dict[str, Any]]) -> None:
        self._items = items
        self._index = 0

    def __aiter__(self) -> "MockQueryIterator":
        return self

    async def __anext__(self) -> dict[str, Any]:
        if self._index >= len(self._items):
            raise StopAsyncIteration
        item = self._items[self._index]
        self._index += 1
        return item


class MockCosmosManager:
    """In-memory mock of CosmosManager singleton.

    Provides container proxies backed by MockContainerProxy instances.
    """

    def __init__(self) -> None:
        self._containers: dict[str, MockContainerProxy] = {}
        self._initialized = True

    def get_container(self, collection_name: str) -> MockContainerProxy:
        if collection_name not in self._containers:
            self._containers[collection_name] = MockContainerProxy(collection_name)
        return self._containers[collection_name]

    async def initialize(self) -> dict[str, Any]:
        return {"status": "mock_initialized"}

    async def health_check(self) -> dict[str, Any]:
        return {"status": "healthy", "detail": "Mock Cosmos DB"}

    async def close(self) -> None:
        self._containers.clear()


@pytest.fixture
def mock_cosmos() -> MockCosmosManager:
    """Provide a MockCosmosManager and patch the module-level singleton.

    Usage in tests:
        def test_something(mock_cosmos):
            container = mock_cosmos.get_container("tenants")
            # pre-populate, then exercise code that calls get_cosmos_manager()
    """
    manager = MockCosmosManager()
    with patch.object(_cosmos_client_mod, "_manager", manager):
        with patch.object(_cosmos_client_mod, "get_cosmos_manager", return_value=manager):
            yield manager


# ---------------------------------------------------------------------------
# Mock NATS
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_nats() -> MagicMock:
    """Patch the NATS manager singleton with an inert mock.

    The mock reports as connected but does not require a NATS server.
    """
    nats_mock = MagicMock()
    nats_mock.is_connected = True
    nats_mock.check_health = AsyncMock(return_value=MagicMock(
        connected=True,
        circuit_breaker_state="CLOSED",
        active_streams=0,
    ))
    nats_mock.publish = AsyncMock()
    nats_mock.subscribe = AsyncMock()
    nats_mock.provision_tenant_topics = AsyncMock()
    nats_mock.deprovision_tenant_topics = AsyncMock()
    nats_mock.close = AsyncMock()

    with patch.object(_nats_isolation_mod, "_manager", nats_mock):
        with patch.object(_nats_isolation_mod, "get_nats_manager", return_value=nats_mock):
            yield nats_mock


# ---------------------------------------------------------------------------
# Mock Key Vault
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_keyvault() -> MagicMock:
    """Patch the TenantSecretService singleton with an inert mock.

    The mock stores secrets in a plain dict and passes health checks.
    """
    kv_mock = MagicMock()
    kv_store: dict[str, str] = {}

    kv_mock.initialize = AsyncMock()
    kv_mock.close = AsyncMock()
    kv_mock.health_check = AsyncMock(return_value={"status": "healthy", "detail": "Mock Key Vault"})

    async def _store_secret(tenant_id: str, secret_type: Any, value: str) -> None:
        kv_store[f"tenant-{tenant_id}-{secret_type.value}"] = value

    async def _get_secret(tenant_id: str, secret_type: Any) -> str | None:
        return kv_store.get(f"tenant-{tenant_id}-{secret_type.value}")

    async def _delete_secret(tenant_id: str, secret_type: Any) -> None:
        kv_store.pop(f"tenant-{tenant_id}-{secret_type.value}", None)

    kv_mock.store_secret = AsyncMock(side_effect=_store_secret)
    kv_mock.get_secret = AsyncMock(side_effect=_get_secret)
    kv_mock.delete_secret = AsyncMock(side_effect=_delete_secret)
    kv_mock._store = kv_store  # Expose for test assertions

    with patch.object(_secret_service_mod, "_service", kv_mock):
        with patch.object(_secret_service_mod, "get_secret_service", return_value=kv_mock):
            yield kv_mock


# ---------------------------------------------------------------------------
# Mock circuit breaker registry
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_circuit_breakers() -> MagicMock:
    """Patch the circuit breaker registry with an empty mock."""
    registry_mock = MagicMock()
    registry_mock.health_summary = MagicMock(return_value={})
    registry_mock.reset_all = MagicMock()

    with patch.object(
        _pipeline_resilience_mod, "get_circuit_breaker_registry",
        return_value=registry_mock,
    ):
        yield registry_mock


# ---------------------------------------------------------------------------
# FastAPI TestClient
# ---------------------------------------------------------------------------


def _build_tenant_lookup_table(
    tenants: list[dict[str, Any]] | None = None,
) -> tuple[AsyncMock, AsyncMock]:
    """Build mock resolver functions for tenant auth middleware.

    Returns (resolve_by_shop_domain, resolve_by_api_key_hash) functions
    that search the provided tenant list.
    """
    if tenants is None:
        tenants = [
            make_tenant_document(
                tenant_id=STARTER_TENANT_ID,
                tier=TenantTier.STARTER,
                api_key_hash=TEST_API_KEY_HASH_STARTER,
            ),
            make_tenant_document(
                tenant_id=PROFESSIONAL_TENANT_ID,
                tier=TenantTier.PROFESSIONAL,
                api_key_hash=TEST_API_KEY_HASH_PROFESSIONAL,
            ),
            make_tenant_document(
                tenant_id=ENTERPRISE_TENANT_ID,
                tier=TenantTier.ENTERPRISE,
                billing_channel=BillingChannel.SHOPIFY,
                api_key_hash=TEST_API_KEY_HASH_ENTERPRISE,
                shop_domain="enterprise-shop.myshopify.com",
            ),
        ]

    async def resolve_by_shop_domain(domain: str) -> dict[str, Any] | None:
        for t in tenants:
            if t.get("shopify_shop_domain") == domain:
                return t
        return None

    async def resolve_by_api_key_hash(key_hash: str) -> dict[str, Any] | None:
        for t in tenants:
            if t.get("api_key_hash") == key_hash:
                return t
        return None

    return AsyncMock(side_effect=resolve_by_shop_domain), AsyncMock(side_effect=resolve_by_api_key_hash)


@pytest.fixture
def app_client(
    mock_nats: MagicMock,
    mock_keyvault: MagicMock,
    mock_circuit_breakers: MagicMock,
) -> TestClient:
    """Synchronous FastAPI TestClient with all external services mocked.

    The middleware stack is fully active (auth, rate limit, concurrency,
    correlation). Tenant resolution is wired to in-memory test data
    containing one Starter, one Professional, and one Enterprise tenant.

    Authenticate requests using the helpers:
        client.get("/api/...", headers=auth_headers_api_key(TEST_API_KEY_STARTER))
    """
    import src.main as _main_mod
    from src.multi_tenant.middleware import configure_tenant_resolution

    # Patch the references that main.py's startup/ready handlers use,
    # since main.py has already imported these names at module level.
    with (
        patch.object(_main_mod, "get_nats_manager", return_value=mock_nats),
        patch.object(_main_mod, "get_secret_service", return_value=mock_keyvault),
        patch.object(_main_mod, "get_circuit_breaker_registry", return_value=mock_circuit_breakers),
        patch.object(_main_mod, "init_nats_manager", new_callable=AsyncMock),
        patch.object(_main_mod, "close_nats_manager", new_callable=AsyncMock),
        patch.object(_main_mod, "configure_tracing", return_value=None),
        patch.object(_main_mod, "configure_tenant_logging", return_value=None),
        patch.object(_main_mod, "TenantRepository", side_effect=Exception("mocked")),
    ):
        with TestClient(_main_mod.app, raise_server_exceptions=False) as client:
            # Wire tenant resolvers *after* TestClient startup so they are
            # not overwritten by the (now-failing) _startup_tenant_resolution.
            domain_resolver, key_resolver = _build_tenant_lookup_table()
            configure_tenant_resolution(
                resolve_by_shop_domain=domain_resolver,
                resolve_by_api_key_hash=key_resolver,
            )
            yield client


# ---------------------------------------------------------------------------
# Convenience: authenticated client helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def starter_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the Starter tenant."""
    return AuthenticatedClient(app_client, TEST_API_KEY_STARTER)


@pytest.fixture
def professional_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the Professional tenant."""
    return AuthenticatedClient(app_client, TEST_API_KEY_PROFESSIONAL)


@pytest.fixture
def enterprise_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the Enterprise tenant."""
    return AuthenticatedClient(app_client, TEST_API_KEY_ENTERPRISE)


class AuthenticatedClient:
    """Wrapper around TestClient that injects auth headers automatically.

    Usage:
        def test_usage(starter_client):
            resp = starter_client.get("/api/dashboard/usage")
            assert resp.status_code == 200
    """

    def __init__(self, client: TestClient, api_key: str) -> None:
        self._client = client
        self._headers = auth_headers_api_key(api_key)

    def get(self, url: str, **kwargs: Any) -> Any:
        headers = {**self._headers, **kwargs.pop("headers", {})}
        return self._client.get(url, headers=headers, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        headers = {**self._headers, **kwargs.pop("headers", {})}
        return self._client.post(url, headers=headers, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        headers = {**self._headers, **kwargs.pop("headers", {})}
        return self._client.put(url, headers=headers, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Any:
        headers = {**self._headers, **kwargs.pop("headers", {})}
        return self._client.patch(url, headers=headers, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Any:
        headers = {**self._headers, **kwargs.pop("headers", {})}
        return self._client.delete(url, headers=headers, **kwargs)

    @property
    def raw(self) -> TestClient:
        """Access the underlying TestClient for unauthenticated requests."""
        return self._client
