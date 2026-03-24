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
import src.multi_tenant.security_hardening as _security_hardening_mod


# ---------------------------------------------------------------------------
# Tenant context factories — reusable across all test modules
# ---------------------------------------------------------------------------

STARTER_TENANT_ID = "t-starter-001"
PROFESSIONAL_TENANT_ID = "t-pro-002"
ENTERPRISE_TENANT_ID = "t-ent-003"


@pytest.fixture(autouse=True)
def _reset_pre_auth_rate_limiter():
    """Reset the pre-auth rate limiter before each test.

    The PreAuthRateLimiter is a module-level singleton that accumulates
    failed auth attempts across tests. Without this reset, tests that
    intentionally send unauthenticated requests (e.g., testing auth
    rejection) would cause later tests to be blocked.
    """
    limiter = _security_hardening_mod.get_pre_auth_limiter()
    limiter._trackers.clear()
    yield
    limiter._trackers.clear()


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

# SPA platform admin key (ar_spa_ prefix triggers isolated auth path)
TEST_SPA_KEY = "ar_spa_plat_test_spa_key_001"

# Per-user API key (ar_user_ prefix triggers user auth path)
TEST_USER_KEY = "ar_user_test_user_key_001"

# Widget key (pk_live_ prefix, must pass validate_widget_key_format)
TEST_WIDGET_KEY = "pk_live_abcd1234efgh_5678ijkl9012mnop"


def hash_test_api_key(api_key: str) -> str:
    """Hash an API key the same way auth.py does."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


# Pre-computed hashes for the test keys
TEST_API_KEY_HASH_STARTER = hash_test_api_key(TEST_API_KEY_STARTER)
TEST_API_KEY_HASH_PROFESSIONAL = hash_test_api_key(TEST_API_KEY_PROFESSIONAL)
TEST_API_KEY_HASH_ENTERPRISE = hash_test_api_key(TEST_API_KEY_ENTERPRISE)
TEST_SPA_KEY_HASH = hash_test_api_key(TEST_SPA_KEY)
TEST_USER_KEY_HASH = hash_test_api_key(TEST_USER_KEY)
TEST_WIDGET_KEY_HASH = hash_test_api_key(TEST_WIDGET_KEY)

# SPA platform admin document shape (returned by resolve_by_spa_key_hash)
TEST_SPA_ADMIN_DOC = {
    "id": "spa-admin-001",
    "admin_id": "spa-admin-001",
    "email": "admin@platform.test",
    "api_key_hash": TEST_SPA_KEY_HASH,
    "is_active": True,
    "role": "superadmin",
    "notification_email_address": "admin@platform.test",
    "partition_key": "__platform__",
}

# Per-user team member + tenant document shape (returned by resolve_by_user_api_key_hash)
TEST_USER_MEMBER_DOC = {
    "team_member": {
        "id": "member-001",
        "email": "user@starter.test",
        "user_api_key_hash": TEST_USER_KEY_HASH,
        "is_active": True,
        "role": "superadmin",
        "escalation_categories": [],
        "tenant_id": STARTER_TENANT_ID,
    },
    "tenant": None,  # Populated dynamically in _build_tenant_lookup_table
}


def auth_headers_api_key(api_key: str = TEST_API_KEY_STARTER) -> dict[str, str]:
    """Build request headers for API key authentication."""
    return {"X-API-Key": api_key}


def auth_headers_widget_key(widget_key: str = TEST_WIDGET_KEY) -> dict[str, str]:
    """Build request headers for widget key authentication."""
    return {"X-Widget-Key": widget_key}


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
) -> dict[str, AsyncMock]:
    """Build mock resolver functions for tenant auth middleware.

    Returns a dict of resolver functions covering all 5 auth paths:
    - resolve_by_shop_domain
    - resolve_by_api_key_hash
    - resolve_by_spa_key_hash
    - resolve_by_widget_key_hash
    - resolve_by_user_api_key_hash
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

    # Widget key hash → tenant mapping (starter tenant)
    widget_tenants = {
        TEST_WIDGET_KEY_HASH: tenants[0],  # Starter tenant
    }

    # SPA key hash → platform admin document
    spa_admins = {
        TEST_SPA_KEY_HASH: TEST_SPA_ADMIN_DOC,
    }

    # User key hash → {team_member, tenant} mapping
    user_member = dict(TEST_USER_MEMBER_DOC)
    user_member["tenant"] = tenants[0]  # Link to starter tenant
    user_members = {
        TEST_USER_KEY_HASH: user_member,
    }

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

    async def resolve_by_spa_key_hash(key_hash: str) -> dict[str, Any] | None:
        return spa_admins.get(key_hash)

    async def resolve_by_widget_key_hash(key_hash: str) -> dict[str, Any] | None:
        return widget_tenants.get(key_hash)

    async def resolve_by_user_api_key_hash(key_hash: str) -> dict[str, Any] | None:
        return user_members.get(key_hash)

    # SPEC-1644: Partition-scoped resolvers — require tenant_id from caller
    async def verify_api_key_in_partition(
        tenant_id: str, key_hash: str,
    ) -> dict[str, Any] | None:
        """Partition-scoped: only match if key hash belongs to this tenant."""
        for t in tenants:
            tid = t.get("tenant_id") or t.get("id")
            if tid == tenant_id and t.get("api_key_hash") == key_hash:
                return t
        return None

    async def verify_user_key_in_partition(
        tenant_id: str, key_hash: str,
    ) -> dict[str, Any] | None:
        """Partition-scoped: only match if user key hash is in this tenant."""
        result = user_members.get(key_hash)
        if result is None:
            return None
        member = result.get("team_member", {})
        if member.get("tenant_id") != tenant_id:
            return None
        return result

    return {
        "resolve_by_shop_domain": AsyncMock(side_effect=resolve_by_shop_domain),
        "resolve_by_api_key_hash": AsyncMock(side_effect=resolve_by_api_key_hash),
        "resolve_by_spa_key_hash": AsyncMock(side_effect=resolve_by_spa_key_hash),
        "resolve_by_widget_key_hash": AsyncMock(side_effect=resolve_by_widget_key_hash),
        "resolve_by_user_api_key_hash": AsyncMock(side_effect=resolve_by_user_api_key_hash),
        "verify_api_key_in_partition": AsyncMock(side_effect=verify_api_key_in_partition),
        "verify_user_key_in_partition": AsyncMock(side_effect=verify_user_key_in_partition),
    }


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
    import src.app.lifecycle as _lifecycle_mod
    import src.app.health as _health_mod
    from src.multi_tenant.middleware import configure_tenant_resolution

    # Patch module-level imports in the submodules where startup/ready
    # handlers actually reference them (R1 refactoring, session 31).
    with (
        patch.object(_health_mod, "get_nats_manager", return_value=mock_nats),
        patch.object(_lifecycle_mod, "get_secret_service", return_value=mock_keyvault),
        patch.object(_health_mod, "get_circuit_breaker_registry", return_value=mock_circuit_breakers),
        patch.object(_lifecycle_mod, "init_nats_manager", new_callable=AsyncMock),
        patch.object(_lifecycle_mod, "close_nats_manager", new_callable=AsyncMock),
        patch.object(_lifecycle_mod, "configure_tracing", return_value=None),
        patch.object(_lifecycle_mod, "configure_tenant_logging", return_value=None),
        patch.object(_lifecycle_mod, "TenantRepository", side_effect=Exception("mocked")),
    ):
        with TestClient(_main_mod.app, raise_server_exceptions=False) as client:
            # Wire tenant resolvers *after* TestClient startup so they are
            # not overwritten by the (now-failing) _startup_tenant_resolution.
            resolvers = _build_tenant_lookup_table()
            configure_tenant_resolution(
                resolve_by_shop_domain=resolvers["resolve_by_shop_domain"],
                resolve_by_api_key_hash=resolvers["resolve_by_api_key_hash"],
                resolve_by_spa_key_hash=resolvers["resolve_by_spa_key_hash"],
                resolve_by_widget_key_hash=resolvers["resolve_by_widget_key_hash"],
                resolve_by_user_api_key_hash=resolvers["resolve_by_user_api_key_hash"],
                verify_api_key_in_partition=resolvers["verify_api_key_in_partition"],
                verify_user_key_in_partition=resolvers["verify_user_key_in_partition"],
            )

            yield client


# ---------------------------------------------------------------------------
# Convenience: authenticated client helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def starter_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the Starter tenant."""
    return AuthenticatedClient(app_client, TEST_API_KEY_STARTER, STARTER_TENANT_ID)


@pytest.fixture
def professional_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the Professional tenant."""
    return AuthenticatedClient(app_client, TEST_API_KEY_PROFESSIONAL, PROFESSIONAL_TENANT_ID)


@pytest.fixture
def enterprise_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the Enterprise tenant."""
    return AuthenticatedClient(app_client, TEST_API_KEY_ENTERPRISE, ENTERPRISE_TENANT_ID)


@pytest.fixture
def spa_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as the SPA platform admin.

    SPEC-1644: SPA keys (ar_spa_* prefix) are exempt from ?tenant=
    requirement — they authenticate against the platform_admins
    collection, not a tenant partition.
    """
    return AuthenticatedClient(app_client, TEST_SPA_KEY)


@pytest.fixture
def user_client(app_client: TestClient) -> AuthenticatedClient:
    """TestClient pre-authenticated as a per-user (superadmin role) team member.

    SPEC-1644: User keys (ar_user_* prefix) require ?tenant= for
    partition-scoped lookup. This user belongs to the Starter tenant.
    """
    return AuthenticatedClient(app_client, TEST_USER_KEY, STARTER_TENANT_ID)


@pytest.fixture
def widget_client(app_client: TestClient) -> "WidgetAuthClient":
    """TestClient pre-authenticated with a widget key (X-Widget-Key header)."""
    return WidgetAuthClient(app_client, TEST_WIDGET_KEY)


class AuthenticatedClient:
    """Wrapper around TestClient that injects auth headers and tenant
    URL parameter automatically.

    SPEC-1644 compliance: Non-SPA API keys require ``?tenant=`` in the URL
    so the middleware can scope the lookup to a single Cosmos partition.
    When *tenant_id* is provided, every request URL is amended with the
    ``tenant`` query parameter.  SPA keys (``ar_spa_*``) are exempt — pass
    *tenant_id=None* (the default) for SPA clients.

    Usage:
        def test_usage(starter_client):
            resp = starter_client.get("/api/dashboard/usage")
            # URL becomes /api/dashboard/usage?tenant=t-starter-001
            assert resp.status_code == 200
    """

    def __init__(
        self,
        client: TestClient,
        api_key: str,
        tenant_id: str | None = None,
    ) -> None:
        self._client = client
        self._headers = auth_headers_api_key(api_key)
        self._tenant_id = tenant_id

    # -- Request helpers ------------------------------------------------------

    def _prepare(self, url: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Inject auth headers and SPEC-1644 ``?tenant=`` parameter.

        The ``params`` kwarg (used by httpx/TestClient) **replaces** any
        query string already on the URL, so we must add ``tenant`` to the
        *params* dict when it is present rather than appending to the URL.
        """
        headers = {**self._headers, **kwargs.pop("headers", {})}
        kwargs["headers"] = headers

        if self._tenant_id is not None:
            if "params" in kwargs:
                # Merge tenant into existing params dict
                existing = kwargs["params"]
                if isinstance(existing, dict):
                    existing.setdefault("tenant", self._tenant_id)
                else:
                    # params is a list of tuples or similar — convert
                    existing = dict(existing)
                    existing.setdefault("tenant", self._tenant_id)
                    kwargs["params"] = existing
            else:
                # No params kwarg — append to URL directly
                sep = "&" if "?" in url else "?"
                url = f"{url}{sep}tenant={self._tenant_id}"

        return url, kwargs

    # -- HTTP verbs -----------------------------------------------------------

    def get(self, url: str, **kwargs: Any) -> Any:
        url, kwargs = self._prepare(url, kwargs)
        return self._client.get(url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> Any:
        url, kwargs = self._prepare(url, kwargs)
        return self._client.post(url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> Any:
        url, kwargs = self._prepare(url, kwargs)
        return self._client.put(url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> Any:
        url, kwargs = self._prepare(url, kwargs)
        return self._client.patch(url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Any:
        url, kwargs = self._prepare(url, kwargs)
        return self._client.delete(url, **kwargs)

    @property
    def raw(self) -> TestClient:
        """Access the underlying TestClient for unauthenticated requests."""
        return self._client

    @property
    def tenant_id(self) -> str | None:
        """The tenant ID this client authenticates as (None for SPA)."""
        return self._tenant_id


class WidgetAuthClient:
    """Wrapper around TestClient that injects widget key headers automatically.

    Widget keys use X-Widget-Key header (not X-API-Key) and are restricted
    to /api/chat/*, /ws/chat/*, and /api/config paths only.
    """

    def __init__(self, client: TestClient, widget_key: str) -> None:
        self._client = client
        self._headers = auth_headers_widget_key(widget_key)

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


# ---------------------------------------------------------------------------
# xdist compatibility
# ---------------------------------------------------------------------------


def pytest_configure(config):
    """Register thermal-safe test markers for xdist batch execution."""
    config.addinivalue_line(
        "markers",
        "sequential: tests that must not run in parallel (live endpoints, session fixtures)",
    )
