"""
Tenant-scoped data access layer.

Enforces mandatory tenant_id on every Cosmos DB operation, preventing
cross-tenant data leaks. All application code accesses the database
through these repository classes — direct Cosmos DB container access
is prohibited outside this module.

Architecture reference: Decision #1 (TenantScopedRepository)

Repository hierarchy:
    TenantScopedRepository    — Base class enforcing tenant_id isolation
    ├── TenantRepository      — tenants collection (CRUD + lookup by channel ID)
    ├── ConversationRepository — conversations collection (lifecycle, billing queries)
    ├── UsageRepository        — usage collection (counters, packs, idempotency)
    ├── CustomerProfileRepository — customer_profiles collection (Layer 1)
    ├── KnowledgeBaseRepository — knowledge_bases collection (product/FAQ data)
    ├── MemoryVectorRepository  — memory_vectors collection (Layer 2 + vector search)
    └── PreferencesRepository   — preferences collection (versioned config)

    PlatformScopedRepository  — Base class for platform-wide collections
    ├── PlatformConfigRepository — platform_config collection
    └── AuditLogRepository       — audit_log collection (append-only)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, TypeVar

from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)
from pydantic import BaseModel

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import (
    COLLECTION_AUDIT_LOG,
    COLLECTION_CONVERSATIONS,
    COLLECTION_CUSTOMER_PROFILES,
    COLLECTION_KNOWLEDGE_BASES,
    COLLECTION_MEMORY_VECTORS,
    COLLECTION_PLATFORM_CONFIG,
    COLLECTION_PREFERENCES,
    COLLECTION_TENANTS,
    COLLECTION_USAGE,
    TIER_DEFAULTS,
    AuditEventType,
    AuditLogDocument,
    ConversationDocument,
    ConversationStatus,
    CustomerProfileDocument,
    IdempotencyKeyDocument,
    KnowledgeBaseDocument,
    MemoryVectorDocument,
    PackBalanceDocument,
    PlatformConfigDocument,
    PreferencesDocument,
    TenantDocument,
    TenantStatus,
    TenantTier,
    UsageCounterDocument,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class TenantIsolationError(Exception):
    """Raised when an operation would violate tenant isolation."""


class DocumentNotFoundError(Exception):
    """Raised when a requested document does not exist."""

    def __init__(self, collection: str, document_id: str, tenant_id: str) -> None:
        self.collection = collection
        self.document_id = document_id
        self.tenant_id = tenant_id
        super().__init__(
            f"Document not found: {collection}/{document_id} (tenant={tenant_id})"
        )


class DocumentConflictError(Exception):
    """Raised when a create would conflict with an existing document."""


# ---------------------------------------------------------------------------
# Base: TenantScopedRepository
# ---------------------------------------------------------------------------


class TenantScopedRepository:
    """Base repository enforcing mandatory tenant_id on every operation.

    Every read, write, query, and delete passes through this class,
    which validates that tenant_id is present and uses it as the
    Cosmos DB partition key. This makes cross-tenant data access
    structurally impossible.

    Subclasses define collection-specific query methods but inherit
    all CRUD operations from this base.
    """

    def __init__(self, collection_name: str) -> None:
        self._collection_name = collection_name

    @property
    def _container(self) -> Any:
        """Get the Cosmos DB ContainerProxy for this collection."""
        return get_cosmos_manager().get_container(self._collection_name)

    def _validate_tenant_id(self, tenant_id: str) -> None:
        """Validate that tenant_id is non-empty.

        Raises:
            TenantIsolationError: If tenant_id is empty or None.
        """
        if not tenant_id:
            raise TenantIsolationError(
                f"tenant_id is required for all {self._collection_name} operations. "
                "Empty or None tenant_id would bypass tenant isolation."
            )

    def _validate_document_tenant(self, document: dict[str, Any], tenant_id: str) -> None:
        """Validate that a document's tenant_id matches the expected value.

        Raises:
            TenantIsolationError: If the document's tenant_id doesn't match.
        """
        doc_tenant = document.get("tenant_id")
        if doc_tenant != tenant_id:
            raise TenantIsolationError(
                f"Document tenant_id mismatch: expected={tenant_id}, "
                f"found={doc_tenant} in {self._collection_name}/{document.get('id')}"
            )

    async def create(self, tenant_id: str, document: BaseModel) -> dict[str, Any]:
        """Create a new document in the collection.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document: Pydantic model to persist.

        Returns:
            The created document as a dict (includes Cosmos DB system fields).

        Raises:
            TenantIsolationError: If tenant_id is missing or mismatched.
            DocumentConflictError: If a document with the same ID exists.
        """
        self._validate_tenant_id(tenant_id)
        body = document.model_dump(by_alias=True)

        # Enforce tenant_id in the document body
        if body.get("tenant_id") != tenant_id:
            raise TenantIsolationError(
                f"Document tenant_id ({body.get('tenant_id')}) does not match "
                f"operation tenant_id ({tenant_id}). "
                "This prevents accidental cross-tenant writes."
            )

        try:
            result = await self._container.create_item(body=body)
            logger.debug(
                "Created %s/%s for tenant=%s",
                self._collection_name, body.get("id"), tenant_id,
            )
            return result
        except CosmosResourceExistsError as exc:
            raise DocumentConflictError(
                f"Document already exists: {self._collection_name}/{body.get('id')} "
                f"(tenant={tenant_id})"
            ) from exc

    async def read(self, tenant_id: str, document_id: str) -> dict[str, Any]:
        """Read a document by ID within a tenant partition.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document_id: Document ID to read.

        Returns:
            The document as a dict.

        Raises:
            TenantIsolationError: If tenant_id is missing.
            DocumentNotFoundError: If the document doesn't exist.
        """
        self._validate_tenant_id(tenant_id)

        try:
            result = await self._container.read_item(
                item=document_id,
                partition_key=tenant_id,
            )
            # Double-check: verify the returned document belongs to this tenant.
            # This is a defense-in-depth check — partition key should guarantee
            # isolation, but we verify anyway.
            self._validate_document_tenant(result, tenant_id)
            return result
        except CosmosResourceNotFoundError as exc:
            raise DocumentNotFoundError(
                self._collection_name, document_id, tenant_id,
            ) from exc

    async def upsert(self, tenant_id: str, document: BaseModel) -> dict[str, Any]:
        """Create or update a document.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document: Pydantic model to persist.

        Returns:
            The upserted document as a dict.

        Raises:
            TenantIsolationError: If tenant_id is missing or mismatched.
        """
        self._validate_tenant_id(tenant_id)
        body = document.model_dump(by_alias=True)

        if body.get("tenant_id") != tenant_id:
            raise TenantIsolationError(
                f"Document tenant_id ({body.get('tenant_id')}) does not match "
                f"operation tenant_id ({tenant_id})."
            )

        result = await self._container.upsert_item(body=body)
        logger.debug(
            "Upserted %s/%s for tenant=%s",
            self._collection_name, body.get("id"), tenant_id,
        )
        return result

    async def patch(
        self,
        tenant_id: str,
        document_id: str,
        operations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Patch a document with partial updates.

        Uses Cosmos DB patch operations (RFC 6902) for atomic updates
        without reading the full document first. Ideal for counter
        increments and single-field updates.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document_id: Document ID to patch.
            operations: List of patch operations, e.g.:
                [{"op": "incr", "path": "/total_conversations", "value": 1}]

        Returns:
            The patched document as a dict.

        Raises:
            TenantIsolationError: If tenant_id is missing.
            DocumentNotFoundError: If the document doesn't exist.
        """
        self._validate_tenant_id(tenant_id)

        try:
            result = await self._container.patch_item(
                item=document_id,
                partition_key=tenant_id,
                patch_operations=operations,
            )
            logger.debug(
                "Patched %s/%s for tenant=%s (%d ops)",
                self._collection_name, document_id, tenant_id, len(operations),
            )
            return result
        except CosmosResourceNotFoundError as exc:
            raise DocumentNotFoundError(
                self._collection_name, document_id, tenant_id,
            ) from exc

    async def delete(self, tenant_id: str, document_id: str) -> None:
        """Delete a document by ID within a tenant partition.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document_id: Document ID to delete.

        Raises:
            TenantIsolationError: If tenant_id is missing.
            DocumentNotFoundError: If the document doesn't exist.
        """
        self._validate_tenant_id(tenant_id)

        try:
            await self._container.delete_item(
                item=document_id,
                partition_key=tenant_id,
            )
            logger.debug(
                "Deleted %s/%s for tenant=%s",
                self._collection_name, document_id, tenant_id,
            )
        except CosmosResourceNotFoundError as exc:
            raise DocumentNotFoundError(
                self._collection_name, document_id, tenant_id,
            ) from exc

    async def query(
        self,
        tenant_id: str,
        query_text: str,
        parameters: list[dict[str, Any]] | None = None,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a SQL query scoped to a single tenant partition.

        The tenant_id is always passed as the partition key, ensuring
        queries never cross tenant boundaries.

        Args:
            tenant_id: Tenant partition key (mandatory).
            query_text: Cosmos DB SQL query string.
            parameters: Query parameters, e.g.:
                [{"name": "@status", "value": "active"}]
            max_items: Maximum number of items to return.

        Returns:
            List of matching documents.

        Raises:
            TenantIsolationError: If tenant_id is missing.
        """
        self._validate_tenant_id(tenant_id)

        items: list[dict[str, Any]] = []
        kwargs: dict[str, Any] = {
            "query": query_text,
            "partition_key": tenant_id,
        }
        if parameters:
            kwargs["parameters"] = parameters
        if max_items:
            kwargs["max_item_count"] = max_items

        async for item in self._container.query_items(**kwargs):
            # Defense-in-depth: verify every returned item belongs to this tenant
            if item.get("tenant_id") != tenant_id:
                logger.error(
                    "TENANT ISOLATION BREACH: query on %s returned item with "
                    "tenant_id=%s, expected=%s. Item suppressed.",
                    self._collection_name, item.get("tenant_id"), tenant_id,
                )
                continue
            items.append(item)
            if max_items and len(items) >= max_items:
                break

        return items

    async def query_count(
        self,
        tenant_id: str,
        query_text: str,
        parameters: list[dict[str, Any]] | None = None,
    ) -> int:
        """Execute a COUNT query scoped to a single tenant partition.

        Args:
            tenant_id: Tenant partition key (mandatory).
            query_text: SQL query returning a count, e.g.:
                "SELECT VALUE COUNT(1) FROM c WHERE c.is_billable = true"
            parameters: Query parameters.

        Returns:
            The count result.
        """
        self._validate_tenant_id(tenant_id)

        kwargs: dict[str, Any] = {
            "query": query_text,
            "partition_key": tenant_id,
        }
        if parameters:
            kwargs["parameters"] = parameters

        async for item in self._container.query_items(**kwargs):
            return item  # COUNT queries return a single scalar

        return 0


# ---------------------------------------------------------------------------
# Collection 1: TenantRepository
# ---------------------------------------------------------------------------


class TenantRepository(TenantScopedRepository):
    """Repository for the tenants collection.

    Provides tenant CRUD operations and lookup by channel identifiers
    (Stripe customer ID, Shopify shop domain).
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_TENANTS)

    async def get_by_stripe_customer_id(
        self, tenant_id: str, stripe_customer_id: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by Stripe customer ID within a partition.

        Note: This queries within a known tenant partition. For
        cross-partition lookup by Stripe ID (e.g., webhook processing),
        use find_by_stripe_customer_id() which performs a cross-partition query.
        """
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c WHERE c.stripe_customer_id = @stripe_id"
            ),
            parameters=[{"name": "@stripe_id", "value": stripe_customer_id}],
            max_items=1,
        )
        return results[0] if results else None

    async def find_by_stripe_customer_id(
        self, stripe_customer_id: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by Stripe customer ID (cross-partition).

        Used during webhook processing where tenant_id is unknown.
        This performs a cross-partition query — use sparingly.

        Args:
            stripe_customer_id: Stripe cus_... identifier.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.stripe_customer_id = @stripe_id",
            parameters=[{"name": "@stripe_id", "value": stripe_customer_id}],
            enable_cross_partition_query=True,
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_shopify_domain(
        self, shopify_shop_domain: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by Shopify shop domain (cross-partition).

        Used during Shopify webhook/auth processing where tenant_id
        is unknown.

        Args:
            shopify_shop_domain: *.myshopify.com domain.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.shopify_shop_domain = @domain",
            parameters=[{"name": "@domain", "value": shopify_shop_domain}],
            enable_cross_partition_query=True,
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_api_key_hash(
        self, api_key_hash: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by API key hash (cross-partition).

        Used during API key authentication where tenant_id is unknown.
        This performs a cross-partition query — use sparingly.

        Args:
            api_key_hash: SHA-256 hex digest of the API key.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.api_key_hash = @hash",
            parameters=[{"name": "@hash", "value": api_key_hash}],
            enable_cross_partition_query=True,
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def list_by_status(
        self, tenant_id: str, status: TenantStatus,
    ) -> list[dict[str, Any]]:
        """List tenants with a specific status (within partition)."""
        return await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.status = @status",
            parameters=[{"name": "@status", "value": status.value}],
        )

    async def update_status(
        self, tenant_id: str, status: TenantStatus,
    ) -> dict[str, Any]:
        """Update a tenant's lifecycle status."""
        now = datetime.now(timezone.utc).isoformat()
        operations = [
            {"op": "set", "path": "/status", "value": status.value},
            {"op": "set", "path": "/updated_at", "value": now},
        ]

        if status == TenantStatus.GRACE_PERIOD:
            operations.append({"op": "set", "path": "/deactivated_at", "value": now})

        return await self.patch(tenant_id, tenant_id, operations)


# ---------------------------------------------------------------------------
# Collection 2: ConversationRepository
# ---------------------------------------------------------------------------


class ConversationRepository(TenantScopedRepository):
    """Repository for the conversations collection.

    Supports conversation lifecycle management and billing queries
    needed by the ConversationMeter (Work Items #71-72).
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_CONVERSATIONS)

    async def list_billable(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
    ) -> list[dict[str, Any]]:
        """List billable conversations in a date range.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive). None = now.
        """
        query_text = (
            "SELECT * FROM c "
            "WHERE c.is_billable = true "
            "AND c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [
            {"name": "@since", "value": since},
        ]
        if until:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        query_text += " ORDER BY c.started_at DESC"

        return await self.query(tenant_id, query_text, params)

    async def count_billable(
        self, tenant_id: str, since: str, until: str | None = None,
    ) -> int:
        """Count billable conversations in a date range."""
        query_text = (
            "SELECT VALUE COUNT(1) FROM c "
            "WHERE c.is_billable = true "
            "AND c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [
            {"name": "@since", "value": since},
        ]
        if until:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        return await self.query_count(tenant_id, query_text, params)

    async def list_by_customer(
        self,
        tenant_id: str,
        customer_id: str,
        max_items: int = 50,
    ) -> list[dict[str, Any]]:
        """List conversations for a specific customer, newest first."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.customer_id = @customer_id "
                "ORDER BY c.started_at DESC"
            ),
            parameters=[{"name": "@customer_id", "value": customer_id}],
            max_items=max_items,
        )

    async def find_active(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any] | None:
        """Find the active conversation for a customer (at most one)."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.customer_id = @customer_id "
                "AND c.status = @status"
            ),
            parameters=[
                {"name": "@customer_id", "value": customer_id},
                {"name": "@status", "value": ConversationStatus.ACTIVE.value},
            ],
            max_items=1,
        )
        return results[0] if results else None

    async def append_message(
        self,
        tenant_id: str,
        conversation_id: str,
        message: dict[str, Any],
    ) -> dict[str, Any]:
        """Append a message to a conversation's transcript.

        Uses patch operations for atomic append without read-modify-write.
        """
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "add", "path": "/messages/-", "value": message},
                {"op": "incr", "path": "/message_count", "value": 1},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    async def end_conversation(
        self,
        tenant_id: str,
        conversation_id: str,
        status: ConversationStatus,
    ) -> dict[str, Any]:
        """Mark a conversation as ended."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "set", "path": "/status", "value": status.value},
                {"op": "set", "path": "/ended_at", "value": now},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )


# ---------------------------------------------------------------------------
# Collection 3: UsageRepository
# ---------------------------------------------------------------------------


class UsageRepository(TenantScopedRepository):
    """Repository for the usage collection.

    Manages usage counters, pack balances, and idempotency keys.
    Uses atomic patch operations for counter increments (no
    read-modify-write race conditions).
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_USAGE)

    # --- Usage counters ---

    async def get_or_create_counter(
        self,
        tenant_id: str,
        billing_period: str,
        tier: TenantTier | None = None,
    ) -> dict[str, Any]:
        """Get or create a usage counter for a billing period.

        Args:
            tenant_id: Tenant partition key.
            billing_period: Period identifier (e.g. "2026-02").
            tier: Tenant's current tier (used to set included_allowance
                  on new counters).

        Returns:
            The usage counter document.
        """
        doc_id = f"{tenant_id}:{billing_period}"

        try:
            return await self.read(tenant_id, doc_id)
        except DocumentNotFoundError:
            included = 0
            if tier:
                defaults = TIER_DEFAULTS.get(tier.value, {})
                included = defaults.get("included_conversations", 0)

            counter = UsageCounterDocument(
                id=doc_id,
                tenant_id=tenant_id,
                billing_period=billing_period,
                tier=tier,
                included_allowance=included,
            )
            return await self.create(tenant_id, counter)

    async def increment_conversations(
        self,
        tenant_id: str,
        billing_period: str,
        count: int = 1,
    ) -> dict[str, Any]:
        """Atomically increment the conversation counter.

        Uses Cosmos DB patch "incr" operation — no read-modify-write
        race condition.
        """
        doc_id = f"{tenant_id}:{billing_period}"
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "incr", "path": "/total_conversations", "value": count},
            ],
        )

    async def increment_overage_reported(
        self,
        tenant_id: str,
        billing_period: str,
        count: int,
    ) -> dict[str, Any]:
        """Atomically increment the overage reported counter."""
        doc_id = f"{tenant_id}:{billing_period}"
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "incr", "path": "/overage_reported", "value": count},
            ],
        )

    async def increment_pack_consumed(
        self,
        tenant_id: str,
        billing_period: str,
        count: int,
    ) -> dict[str, Any]:
        """Atomically increment the pack consumed counter."""
        doc_id = f"{tenant_id}:{billing_period}"
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "incr", "path": "/pack_consumed", "value": count},
            ],
        )

    # --- Pack balances ---

    async def create_pack(
        self, tenant_id: str, pack: PackBalanceDocument,
    ) -> dict[str, Any]:
        """Create a new pack balance entry."""
        return await self.create(tenant_id, pack)

    async def get_active_packs(
        self, tenant_id: str, now_iso: str,
    ) -> list[dict[str, Any]]:
        """Get all active (non-expired, non-depleted) packs, oldest first.

        FIFO consumption order: oldest purchased_at first.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.pack_id != null "
                "AND c.remaining > 0 "
                "AND c.expires_at > @now "
                "ORDER BY c.purchased_at ASC"
            ),
            parameters=[{"name": "@now", "value": now_iso}],
        )

    async def consume_from_pack(
        self,
        tenant_id: str,
        pack_doc_id: str,
        amount: int,
    ) -> dict[str, Any]:
        """Atomically decrement a pack's remaining balance."""
        return await self.patch(
            tenant_id=tenant_id,
            document_id=pack_doc_id,
            operations=[
                {"op": "incr", "path": "/remaining", "value": -amount},
            ],
        )

    # --- Idempotency keys ---

    async def check_idempotency(
        self, tenant_id: str, event_id: str,
    ) -> bool:
        """Check if an event has already been processed.

        Returns True if the event_id exists (duplicate), False if new.
        """
        doc_id = event_id
        try:
            await self.read(tenant_id, doc_id)
            return True  # Already processed
        except DocumentNotFoundError:
            return False  # New event

    async def record_idempotency(
        self, tenant_id: str, event_id: str, event_type: str,
    ) -> dict[str, Any]:
        """Record that an event has been processed.

        Uses create (not upsert) so duplicate attempts raise
        DocumentConflictError — providing an additional safety net
        against race conditions.
        """
        now = datetime.now(timezone.utc).isoformat()
        doc = IdempotencyKeyDocument(
            id=event_id,
            tenant_id=tenant_id,
            event_id=event_id,
            event_type=event_type,
            processed_at=now,
        )
        return await self.create(tenant_id, doc)


# ---------------------------------------------------------------------------
# Collection 4: CustomerProfileRepository
# ---------------------------------------------------------------------------


class CustomerProfileRepository(TenantScopedRepository):
    """Repository for the customer_profiles collection (Layer 1)."""

    def __init__(self) -> None:
        super().__init__(COLLECTION_CUSTOMER_PROFILES)

    async def get_by_customer_id(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any] | None:
        """Get a customer profile by customer_id within a tenant."""
        doc_id = f"{tenant_id}:{customer_id}"
        try:
            return await self.read(tenant_id, doc_id)
        except DocumentNotFoundError:
            return None

    async def upsert_profile(
        self, tenant_id: str, profile: CustomerProfileDocument,
    ) -> dict[str, Any]:
        """Create or update a customer profile."""
        return await self.upsert(tenant_id, profile)

    async def update_last_interaction(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Update the last_interaction_at timestamp."""
        doc_id = f"{tenant_id}:{customer_id}"
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=doc_id,
            operations=[
                {"op": "set", "path": "/last_interaction_at", "value": now},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    async def list_with_consent(
        self, tenant_id: str, consent_status: str,
    ) -> list[dict[str, Any]]:
        """List profiles with a specific consent status."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c WHERE c.consent_status = @consent"
            ),
            parameters=[{"name": "@consent", "value": consent_status}],
        )


# ---------------------------------------------------------------------------
# Collection 5: KnowledgeBaseRepository
# ---------------------------------------------------------------------------


class KnowledgeBaseRepository(TenantScopedRepository):
    """Repository for the knowledge_bases collection."""

    def __init__(self) -> None:
        super().__init__(COLLECTION_KNOWLEDGE_BASES)

    async def list_active(
        self,
        tenant_id: str,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """List active knowledge base entries, optionally filtered."""
        query_text = "SELECT * FROM c WHERE c.is_active = true"
        params: list[dict[str, Any]] = []

        if entry_type:
            query_text += " AND c.entry_type = @type"
            params.append({"name": "@type", "value": entry_type})

        if language:
            query_text += " AND c.language = @lang"
            params.append({"name": "@lang", "value": language})

        return await self.query(tenant_id, query_text, params)

    async def search_by_tags(
        self, tenant_id: str, tags: list[str],
    ) -> list[dict[str, Any]]:
        """Find entries matching any of the given tags."""
        # ARRAY_CONTAINS with OR logic for each tag
        conditions = " OR ".join(
            f"ARRAY_CONTAINS(c.tags, @tag{i})" for i in range(len(tags))
        )
        params = [
            {"name": f"@tag{i}", "value": tag} for i, tag in enumerate(tags)
        ]

        return await self.query(
            tenant_id=tenant_id,
            query_text=f"SELECT * FROM c WHERE c.is_active = true AND ({conditions})",
            parameters=params,
        )


# ---------------------------------------------------------------------------
# Collection 6: MemoryVectorRepository
# ---------------------------------------------------------------------------


class MemoryVectorRepository(TenantScopedRepository):
    """Repository for the memory_vectors collection (Layer 2).

    Provides vector similarity search using Cosmos DB DiskANN index.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_MEMORY_VECTORS)

    async def vector_search(
        self,
        tenant_id: str,
        embedding: list[float],
        customer_id: str | None = None,
        top_k: int = 10,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar memory vectors using DiskANN.

        Args:
            tenant_id: Tenant partition key.
            embedding: Query embedding (3072 dimensions).
            customer_id: Optional filter to a specific customer.
            top_k: Number of results to return.
            since: Optional date filter (ISO 8601) — only chunks
                   from conversations after this date.

        Returns:
            List of matching chunks with similarity scores, ordered
            by similarity (most similar first).
        """
        # Build WHERE clause
        conditions = ["c.tenant_id = @tenant_id"]
        params: list[dict[str, Any]] = [
            {"name": "@tenant_id", "value": tenant_id},
            {"name": "@embedding", "value": embedding},
        ]

        if customer_id:
            conditions.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        if since:
            conditions.append("c.conversation_date >= @since")
            params.append({"name": "@since", "value": since})

        where_clause = " AND ".join(conditions)

        query_text = (
            f"SELECT c.id, c.customer_id, c.conversation_id, "
            f"c.chunk_text, c.chunk_index, c.conversation_date, c.topics, "
            f"VectorDistance(c.embedding, @embedding) AS similarity "
            f"FROM c "
            f"WHERE {where_clause} "
            f"ORDER BY VectorDistance(c.embedding, @embedding) "
            f"OFFSET 0 LIMIT @top_k"
        )
        params.append({"name": "@top_k", "value": top_k})

        # Vector search must use partition key for single-partition scope
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
            partition_key=tenant_id,
        ):
            items.append(item)
            if len(items) >= top_k:
                break

        return items

    async def list_by_conversation(
        self, tenant_id: str, conversation_id: str,
    ) -> list[dict[str, Any]]:
        """Get all chunks for a conversation, ordered by position."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.conversation_id = @conv_id "
                "ORDER BY c.chunk_index ASC"
            ),
            parameters=[{"name": "@conv_id", "value": conversation_id}],
        )

    async def delete_by_conversation(
        self, tenant_id: str, conversation_id: str,
    ) -> int:
        """Delete all chunks for a conversation. Returns count deleted."""
        chunks = await self.list_by_conversation(tenant_id, conversation_id)
        for chunk in chunks:
            await self.delete(tenant_id, chunk["id"])
        return len(chunks)

    async def delete_by_customer(
        self, tenant_id: str, customer_id: str,
    ) -> int:
        """Delete all vectors for a customer (GDPR erasure). Returns count."""
        chunks = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT c.id FROM c WHERE c.customer_id = @cid",
            parameters=[{"name": "@cid", "value": customer_id}],
        )
        for chunk in chunks:
            await self.delete(tenant_id, chunk["id"])
        return len(chunks)


# ---------------------------------------------------------------------------
# Collection 7: PreferencesRepository
# ---------------------------------------------------------------------------


class PreferencesRepository(TenantScopedRepository):
    """Repository for the preferences collection (versioned config)."""

    def __init__(self) -> None:
        super().__init__(COLLECTION_PREFERENCES)

    async def get_current(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the current (active) preferences version."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.is_current = true "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def create_version(
        self, tenant_id: str, preferences: PreferencesDocument,
    ) -> dict[str, Any]:
        """Create a new preferences version and mark it current.

        Marks the previous version as non-current first.
        """
        # Mark previous version as non-current
        current = await self.get_current(tenant_id)
        if current:
            await self.patch(
                tenant_id=tenant_id,
                document_id=current["id"],
                operations=[{"op": "set", "path": "/is_current", "value": False}],
            )

        return await self.create(tenant_id, preferences)

    async def get_version(
        self, tenant_id: str, version: int,
    ) -> dict[str, Any] | None:
        """Get a specific preferences version."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.version = @version",
            parameters=[{"name": "@version", "value": version}],
            max_items=1,
        )
        return results[0] if results else None

    async def list_versions(
        self, tenant_id: str, max_items: int = 20,
    ) -> list[dict[str, Any]]:
        """List all preference versions, newest first."""
        return await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c ORDER BY c.version DESC",
            max_items=max_items,
        )


# ---------------------------------------------------------------------------
# Platform-scoped base
# ---------------------------------------------------------------------------


class PlatformScopedRepository:
    """Base repository for platform-wide collections.

    These collections are NOT partitioned by tenant_id. They use
    functional partition keys (config_type, time_partition).
    """

    def __init__(self, collection_name: str) -> None:
        self._collection_name = collection_name

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)


# ---------------------------------------------------------------------------
# Collection 8: PlatformConfigRepository
# ---------------------------------------------------------------------------


class PlatformConfigRepository(PlatformScopedRepository):
    """Repository for the platform_config collection."""

    def __init__(self) -> None:
        super().__init__(COLLECTION_PLATFORM_CONFIG)

    async def get_config(
        self, config_type: str, config_key: str,
    ) -> dict[str, Any] | None:
        """Get a specific config entry."""
        doc_id = f"{config_type}:{config_key}"
        try:
            return await self._container.read_item(
                item=doc_id,
                partition_key=config_type,
            )
        except CosmosResourceNotFoundError:
            return None

    async def set_config(
        self, config: PlatformConfigDocument,
    ) -> dict[str, Any]:
        """Create or update a config entry."""
        body = config.model_dump(by_alias=True)
        return await self._container.upsert_item(body=body)

    async def list_by_type(self, config_type: str) -> list[dict[str, Any]]:
        """List all config entries of a specific type."""
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c",
            partition_key=config_type,
        ):
            items.append(item)
        return items


# ---------------------------------------------------------------------------
# Collection 9: AuditLogRepository
# ---------------------------------------------------------------------------


class AuditLogRepository(PlatformScopedRepository):
    """Repository for the audit_log collection (append-only).

    Audit entries are append-only — no update or delete operations.
    Partitioned by time (YYYY-MM) for even distribution.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_AUDIT_LOG)

    async def log_event(
        self,
        event_type: AuditEventType,
        tenant_id: str,
        actor: str = "system",
        actor_type: str = "system",
        payload: dict[str, Any] | None = None,
        conversation_id: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        """Append an audit log entry.

        This is the primary method for recording audit events. It
        auto-generates the ID, timestamp, and time partition.

        Args:
            event_type: One of the 12 defined AuditEventType values.
            tenant_id: Which tenant the event relates to.
            actor: Who/what triggered the event.
            actor_type: user | system | webhook | admin.
            payload: Event-specific data (must be PII-free).
            conversation_id: Related conversation ID.
            request_id: HTTP request trace ID.

        Returns:
            The created audit log document.
        """
        now = datetime.now(timezone.utc)
        time_partition = now.strftime("%Y-%m")

        doc = AuditLogDocument(
            id=str(uuid.uuid4()),
            time_partition=time_partition,
            event_type=event_type,
            tenant_id=tenant_id,
            actor=actor,
            actor_type=actor_type,
            payload=payload or {},
            conversation_id=conversation_id,
            request_id=request_id,
            timestamp=now.isoformat(),
        )

        body = doc.model_dump(by_alias=True)
        result = await self._container.create_item(body=body)
        logger.debug(
            "Audit event logged: type=%s tenant=%s partition=%s",
            event_type.value, tenant_id, time_partition,
        )
        return result

    async def query_by_tenant(
        self,
        tenant_id: str,
        time_partition: str,
        event_type: AuditEventType | None = None,
        max_items: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit events for a tenant within a time partition.

        Args:
            tenant_id: Tenant to filter for.
            time_partition: YYYY-MM partition to query.
            event_type: Optional event type filter.
            max_items: Maximum results.
        """
        query_text = "SELECT * FROM c WHERE c.tenant_id = @tenant_id"
        params: list[dict[str, Any]] = [
            {"name": "@tenant_id", "value": tenant_id},
        ]

        if event_type:
            query_text += " AND c.event_type = @event_type"
            params.append({"name": "@event_type", "value": event_type.value})

        query_text += " ORDER BY c.timestamp DESC"

        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
            partition_key=time_partition,
            max_item_count=max_items,
        ):
            items.append(item)
            if len(items) >= max_items:
                break

        return items

    async def query_by_event_type(
        self,
        time_partition: str,
        event_type: AuditEventType,
        max_items: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit events of a specific type within a time partition."""
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT * FROM c "
                "WHERE c.event_type = @event_type "
                "ORDER BY c.timestamp DESC"
            ),
            parameters=[{"name": "@event_type", "value": event_type.value}],
            partition_key=time_partition,
            max_item_count=max_items,
        ):
            items.append(item)
            if len(items) >= max_items:
                break

        return items
