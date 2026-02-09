"""
Multi-tenant data isolation end-to-end tests (MT-1014→MT-1016).

Verifies that two tenants cannot read each other's data through
the TenantScopedRepository, confirming the partition key enforcement
and query-level tenant isolation.

Master Test Plan: §4 Gap Register — Multi-Tenant Isolation (1.0-required)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import (
    ConversationStatus,
    TenantTier,
)
from src.multi_tenant.repository import (
    ConversationRepository,
    CustomerProfileRepository,
    KnowledgeBaseRepository,
    TenantScopedRepository,
)


# ---------------------------------------------------------------------------
# Constants for two isolated tenants
# ---------------------------------------------------------------------------

TENANT_A = "t-isolation-alpha"
TENANT_B = "t-isolation-beta"


# ---------------------------------------------------------------------------
# Shared mock container
# ---------------------------------------------------------------------------


class MockContainer:
    """In-memory mock for Cosmos DB container with tenant isolation semantics."""

    def __init__(self):
        self._items: dict[str, dict] = {}

    async def create_item(self, body: dict, **kwargs) -> dict:
        key = f"{body['tenant_id']}:{body['id']}"
        self._items[key] = body.copy()
        return body

    async def read_item(self, item: str, partition_key: str, **kwargs) -> dict:
        key = f"{partition_key}:{item}"
        if key not in self._items:
            raise Exception("Not found")
        return self._items[key].copy()

    async def upsert_item(self, body: dict, **kwargs) -> dict:
        key = f"{body['tenant_id']}:{body['id']}"
        self._items[key] = body.copy()
        return body

    async def delete_item(self, item: str, partition_key: str, **kwargs) -> None:
        key = f"{partition_key}:{item}"
        self._items.pop(key, None)

    def query_items(self, query: str, parameters: list | None = None, **kwargs):
        """Return items matching the partition key (tenant_id) from parameters."""
        partition_key = kwargs.get("partition_key")
        results = []
        for key, item in self._items.items():
            if partition_key and item.get("tenant_id") == partition_key:
                results.append(item.copy())
            elif not partition_key:
                # Cross-partition query — filter by parameters if possible
                results.append(item.copy())
        return MockQueryIterator(results)


class MockQueryIterator:
    """Async iterator over query results."""

    def __init__(self, items: list[dict]):
        self._items = items

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._items:
            raise StopAsyncIteration
        return self._items.pop(0)


# ---------------------------------------------------------------------------
# Helper to seed data directly into the mock container
# ---------------------------------------------------------------------------


async def _seed(container: MockContainer, doc: dict) -> None:
    """Seed a document directly into the mock container, bypassing repo validation."""
    await container.create_item(doc)


# ---------------------------------------------------------------------------
# MT-1014: Conversation isolation between tenants
# ---------------------------------------------------------------------------


class TestConversationIsolation:
    """MT-1014: Tenant A cannot read Tenant B's conversations."""

    @pytest.mark.asyncio
    async def test_cross_tenant_conversation_read_fails(self):
        """Reading Tenant B's conversation with Tenant A's ID raises error."""
        container = MockContainer()
        repo = ConversationRepository()

        # Patch the container property
        with patch.object(type(repo), "_container", new_callable=lambda: property(lambda self: container)):
            # Seed conversations directly into mock container
            await _seed(container, {
                "id": "conv-alpha-001",
                "tenant_id": TENANT_A,
                "status": ConversationStatus.ACTIVE.value,
                "messages": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            await _seed(container, {
                "id": "conv-beta-001",
                "tenant_id": TENANT_B,
                "status": ConversationStatus.ACTIVE.value,
                "messages": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })

            # Tenant A can read their own conversation
            result_a = await repo.read(TENANT_A, "conv-alpha-001")
            assert result_a["tenant_id"] == TENANT_A

            # Tenant A trying to read Tenant B's conversation fails
            # (partition key mismatch — Cosmos DB won't find it)
            with pytest.raises(Exception):
                await repo.read(TENANT_A, "conv-beta-001")

    @pytest.mark.asyncio
    async def test_conversation_query_scoped_to_tenant(self):
        """Query only returns conversations belonging to the requesting tenant."""
        container = MockContainer()
        repo = ConversationRepository()

        with patch.object(type(repo), "_container", new_callable=lambda: property(lambda self: container)):
            # Seed conversations for both tenants
            for i in range(3):
                await _seed(container, {
                    "id": f"conv-a-{i}",
                    "tenant_id": TENANT_A,
                    "status": ConversationStatus.ACTIVE.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
            for i in range(2):
                await _seed(container, {
                    "id": f"conv-b-{i}",
                    "tenant_id": TENANT_B,
                    "status": ConversationStatus.ACTIVE.value,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })

            # Query for Tenant A's conversations
            results_a = await repo.query(
                TENANT_A,
                query_text="SELECT * FROM c WHERE c.tenant_id = @tid",
                parameters=[{"name": "@tid", "value": TENANT_A}],
            )

            assert len(results_a) == 3
            for item in results_a:
                assert item["tenant_id"] == TENANT_A


# ---------------------------------------------------------------------------
# MT-1015: Knowledge base isolation between tenants
# ---------------------------------------------------------------------------


class TestKnowledgeBaseIsolation:
    """MT-1015: Tenant A cannot access Tenant B's KB entries."""

    @pytest.mark.asyncio
    async def test_cross_tenant_kb_read_fails(self):
        """Reading Tenant B's KB entry with Tenant A's ID raises error."""
        container = MockContainer()
        repo = KnowledgeBaseRepository()

        with patch.object(type(repo), "_container", new_callable=lambda: property(lambda self: container)):
            await _seed(container, {
                "id": "kb-alpha-001",
                "tenant_id": TENANT_A,
                "title": "Alpha FAQ",
                "content": "Alpha content",
                "entry_type": "faq",
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            await _seed(container, {
                "id": "kb-beta-001",
                "tenant_id": TENANT_B,
                "title": "Beta FAQ",
                "content": "Beta content",
                "entry_type": "faq",
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })

            # Tenant A can read their own KB entry
            result = await repo.read(TENANT_A, "kb-alpha-001")
            assert result["title"] == "Alpha FAQ"

            # Tenant A cannot read Tenant B's KB entry
            with pytest.raises(Exception):
                await repo.read(TENANT_A, "kb-beta-001")

    @pytest.mark.asyncio
    async def test_kb_query_scoped_to_tenant(self):
        """KB queries only return entries for the requesting tenant."""
        container = MockContainer()
        repo = KnowledgeBaseRepository()

        with patch.object(type(repo), "_container", new_callable=lambda: property(lambda self: container)):
            await _seed(container, {
                "id": "kb-a-1",
                "tenant_id": TENANT_A,
                "title": "A Article",
                "content": "A content",
                "entry_type": "faq",
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            await _seed(container, {
                "id": "kb-b-1",
                "tenant_id": TENANT_B,
                "title": "B Article",
                "content": "B content",
                "entry_type": "faq",
                "status": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })

            results_a = await repo.query(
                TENANT_A,
                query_text="SELECT * FROM c WHERE c.tenant_id = @tid",
                parameters=[{"name": "@tid", "value": TENANT_A}],
            )

            assert len(results_a) == 1
            assert results_a[0]["tenant_id"] == TENANT_A
            assert results_a[0]["title"] == "A Article"


# ---------------------------------------------------------------------------
# MT-1016: Customer profile isolation between tenants
# ---------------------------------------------------------------------------


class TestCustomerProfileIsolation:
    """MT-1016: Tenant A cannot access Tenant B's customer profiles."""

    @pytest.mark.asyncio
    async def test_cross_tenant_profile_read_fails(self):
        """Reading Tenant B's profile with Tenant A's ID raises error."""
        container = MockContainer()
        repo = CustomerProfileRepository()

        with patch.object(type(repo), "_container", new_callable=lambda: property(lambda self: container)):
            await _seed(container, {
                "id": "profile-alpha-001",
                "tenant_id": TENANT_A,
                "customer_id": "cust-001",
                "email": "alpha@example.com",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            await _seed(container, {
                "id": "profile-beta-001",
                "tenant_id": TENANT_B,
                "customer_id": "cust-002",
                "email": "beta@example.com",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })

            # Tenant A reads their own — succeeds
            result = await repo.read(TENANT_A, "profile-alpha-001")
            assert result["email"] == "alpha@example.com"

            # Tenant A reads Tenant B's — fails (partition key mismatch)
            with pytest.raises(Exception):
                await repo.read(TENANT_A, "profile-beta-001")

    @pytest.mark.asyncio
    async def test_profile_query_scoped_to_tenant(self):
        """Profile queries only return entries for the requesting tenant."""
        container = MockContainer()
        repo = CustomerProfileRepository()

        with patch.object(type(repo), "_container", new_callable=lambda: property(lambda self: container)):
            await _seed(container, {
                "id": "p-a-1",
                "tenant_id": TENANT_A,
                "customer_id": "cust-a",
                "email": "a@example.com",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            await _seed(container, {
                "id": "p-b-1",
                "tenant_id": TENANT_B,
                "customer_id": "cust-b",
                "email": "b@example.com",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })

            results = await repo.query(
                TENANT_A,
                query_text="SELECT * FROM c WHERE c.tenant_id = @tid",
                parameters=[{"name": "@tid", "value": TENANT_A}],
            )

            assert len(results) == 1
            assert results[0]["tenant_id"] == TENANT_A
