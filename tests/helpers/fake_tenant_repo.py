"""FakeTenantRepo — in-memory test double for TenantRepository.

Implements the same async interface used by ``provisioning.py``:
    upsert, create, read, patch, find_by_stripe_customer_id,
    find_by_shopify_domain, find_by_api_key_hash.

Usage in test fixtures::

    from tests.helpers.fake_tenant_repo import FakeTenantRepo

    @pytest.fixture(autouse=True)
    def fake_tenant_repo():
        repo = FakeTenantRepo()
        configure_provisioning_repo(repo, team_repo=None)
        yield repo
        configure_provisioning_repo(None, team_repo=None)

For sync tests that need to call async provisioning functions, use
``run_sync``::

    from tests.helpers.fake_tenant_repo import run_sync
    tenant = run_sync(provision_tenant(billing_channel=BillingChannel.STRIPE, ...))

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import copy
from typing import Any


class FakeTenantRepo:
    """In-memory implementation of TenantRepository for testing.

    Supports upsert, create, read, patch, and cross-partition find methods.
    Patch operations follow the Cosmos DB JSON Patch format:
        {"op": "set", "path": "/field_name", "value": new_value}
    """

    def __init__(self) -> None:
        self.store: dict[str, dict[str, Any]] = {}

    async def upsert(self, tenant_id: str, document: Any) -> dict[str, Any]:
        """Create or replace a document."""
        if hasattr(document, "model_dump"):
            doc = document.model_dump(mode="json")
        elif isinstance(document, dict):
            doc = copy.deepcopy(document)
        else:
            doc = dict(document)
        self.store[tenant_id] = doc
        return doc

    async def create(self, tenant_id: str, document: Any) -> dict[str, Any]:
        """Create a new document (alias for upsert in fake)."""
        return await self.upsert(tenant_id, document)

    async def read(self, tenant_id: str, document_id: str) -> dict[str, Any] | None:
        """Read a document by partition key + document ID."""
        return copy.deepcopy(self.store.get(tenant_id))

    async def patch(
        self,
        tenant_id: str,
        document_id: str,
        operations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Apply patch operations to a document."""
        doc = self.store.get(tenant_id)
        if doc is None:
            raise RuntimeError(f"Document not found: {tenant_id}")
        for op in operations:
            if op["op"] == "set":
                # "/field_name" → "field_name"
                field = op["path"].lstrip("/")
                doc[field] = op["value"]
        return copy.deepcopy(doc)

    async def find_by_stripe_customer_id(
        self, stripe_customer_id: str,
    ) -> dict[str, Any] | None:
        """Cross-partition lookup by Stripe customer ID."""
        for doc in self.store.values():
            if doc.get("stripe_customer_id") == stripe_customer_id:
                return copy.deepcopy(doc)
        return None

    async def find_by_shopify_domain(
        self, shopify_shop_domain: str,
    ) -> dict[str, Any] | None:
        """Cross-partition lookup by Shopify shop domain."""
        for doc in self.store.values():
            if doc.get("shopify_shop_domain") == shopify_shop_domain:
                return copy.deepcopy(doc)
        return None

    async def find_by_api_key_hash(
        self, api_key_hash: str,
    ) -> dict[str, Any] | None:
        """Cross-partition lookup by API key hash."""
        for doc in self.store.values():
            if doc.get("api_key_hash") == api_key_hash:
                return copy.deepcopy(doc)
        return None


class FakeDomainIndexRepo:
    """In-memory implementation of DomainIndexRepository for testing.

    Maps domain identifiers (stripe_customer_id, shopify_shop_domain)
    to tenant IDs, supporting lookup, upsert, and delete.
    """

    def __init__(self) -> None:
        self.index: dict[str, str] = {}

    async def lookup(self, domain: str) -> str | None:
        return self.index.get(domain)

    async def upsert(self, domain: str, tenant_id: str, channel: str = "") -> None:
        self.index[domain] = tenant_id

    async def delete(self, domain: str) -> None:
        self.index.pop(domain, None)


def run_sync(coro: Any) -> Any:
    """Run an async coroutine synchronously.

    Intended for sync test methods that need to call async provisioning
    functions (e.g., ``provision_tenant``) for test setup.

    Uses ``asyncio.run()`` which creates and closes a new event loop.
    Safe to call from the main test thread even when Starlette's
    TestClient has its own event loop in a background thread.
    """
    return asyncio.run(coro)
