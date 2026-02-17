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
    ├── PreferencesRepository   — preferences collection (versioned config)
    └── TeamMemberRepository    — team_members collection (admin dashboard access)

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
    COLLECTION_TEAM_MEMBERS,
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
    TeamMemberDocument,
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
            # Defense-in-depth: verify every returned item belongs to this tenant.
            # Aggregate/projection queries may omit tenant_id (GROUP BY, COUNT,
            # AVG, etc.) — skip the check when tenant_id is not in the result
            # since partition_key already guarantees isolation at DB level.
            item_tenant = item.get("tenant_id")
            if item_tenant is not None and item_tenant != tenant_id:
                logger.error(
                    "TENANT ISOLATION BREACH: query on %s returned item with "
                    "tenant_id=%s, expected=%s. Item suppressed.",
                    self._collection_name, item_tenant, tenant_id,
                )
                continue
            items.append(item)
            if max_items and len(items) >= max_items:
                break

        return items

    async def cross_partition_query(
        self,
        query_text: str,
        parameters: list[dict[str, Any]] | None = None,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a cross-partition SQL query (auth-time lookups only).

        WARNING: This bypasses tenant isolation by design. It should ONLY
        be used for authentication-time lookups where the tenant is not
        yet known (e.g., resolving a per-user API key to a team member).

        The query MUST filter on an indexed field (e.g., user_api_key_hash)
        to avoid full collection scans.
        """
        items: list[dict[str, Any]] = []
        kwargs: dict[str, Any] = {
            "query": query_text,
            # Note: In azure-cosmos >=4.9, omitting partition_key
            # automatically enables cross-partition queries. The older
            # enable_cross_partition_query kwarg was removed in 4.14+.
        }
        if parameters:
            kwargs["parameters"] = parameters
        if max_items:
            kwargs["max_item_count"] = max_items

        async for item in self._container.query_items(**kwargs):
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
            # Cross-partition query (default in SDK v4+)
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
            # Cross-partition query (default in SDK v4+)
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
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_customer_email(
        self, email: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by customer email (cross-partition).

        Used during API key reset workflow where the merchant provides
        their email but has no valid API key for authentication.
        This performs a cross-partition query -- use sparingly.

        Args:
            email: The merchant's registered email address.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.customer_email = @email",
            parameters=[{"name": "@email", "value": email}],
            # Cross-partition query (default in SDK v4+)
            max_item_count=1,
        ):
            items.append(item)
            break

        return items[0] if items else None

    async def find_by_widget_key_hash(
        self, widget_key_hash: str,
    ) -> dict[str, Any] | None:
        """Find a tenant by widget key hash (cross-partition).

        Used during publishable widget key authentication (Decision UI-6)
        where tenant_id is unknown. Scoped to /api/chat/* endpoints only.

        Args:
            widget_key_hash: SHA-256 hex digest of the widget key.

        Returns:
            The tenant document, or None if not found.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.widget_key_hash = @hash",
            parameters=[{"name": "@hash", "value": widget_key_hash}],
            # Cross-partition query (default in SDK v4+)
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

    async def list_active_tenant_ids(self) -> list[str]:
        """List all active tenant IDs (cross-partition).

        Used by the idle conversation scanner to enumerate tenants.
        Performs a cross-partition query — call infrequently.
        """
        ids: list[str] = []
        async for item in self._container.query_items(
            query="SELECT c.tenant_id FROM c WHERE c.status = 'active'",
            max_item_count=100,
        ):
            tid = item.get("tenant_id")
            if tid and tid not in ids:
                ids.append(tid)
        return ids

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

    # --- Admin inbox queries (WI #171) ---

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        status: ConversationStatus | None = None,
        customer_id: str | None = None,
        since: str | None = None,
        until: str | None = None,
        assigned_to: str | None = None,
        include_archived: bool = False,
        archived_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List conversations with optional filters for admin inbox.

        Args:
            tenant_id: Tenant partition key.
            status: Filter by conversation status (active, escalated, etc.).
            customer_id: Filter by customer identifier.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            assigned_to: Filter by assigned human agent ID.
            include_archived: If True, include archived conversations.
            archived_only: If True, return only archived conversations.
            offset: Pagination offset.
            limit: Page size.
        """
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if status is not None:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status.value})

        if customer_id is not None:
            conditions.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        if since is not None:
            conditions.append("c.started_at >= @since")
            params.append({"name": "@since", "value": since})

        if until is not None:
            conditions.append("c.started_at < @until")
            params.append({"name": "@until", "value": until})

        if assigned_to is not None:
            conditions.append("c.assigned_to = @assigned_to")
            params.append({"name": "@assigned_to", "value": assigned_to})

        # Archival filter: exclude archived by default
        if archived_only:
            conditions.append("IS_DEFINED(c.archived_at) AND c.archived_at != null")
        elif not include_archived:
            conditions.append("(NOT IS_DEFINED(c.archived_at) OR c.archived_at = null)")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        query_text = (
            f"SELECT * FROM c WHERE {where_clause} "
            "ORDER BY c.last_activity_at DESC "
            "OFFSET @offset LIMIT @limit"
        )

        return await self.query(tenant_id, query_text, params)

    async def count_filtered(
        self,
        tenant_id: str,
        *,
        status: ConversationStatus | None = None,
        customer_id: str | None = None,
        since: str | None = None,
        until: str | None = None,
        assigned_to: str | None = None,
        include_archived: bool = False,
        archived_only: bool = False,
    ) -> int:
        """Count conversations matching filters (for pagination metadata)."""
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if status is not None:
            conditions.append("c.status = @status")
            params.append({"name": "@status", "value": status.value})

        if customer_id is not None:
            conditions.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        if since is not None:
            conditions.append("c.started_at >= @since")
            params.append({"name": "@since", "value": since})

        if until is not None:
            conditions.append("c.started_at < @until")
            params.append({"name": "@until", "value": until})

        if assigned_to is not None:
            conditions.append("c.assigned_to = @assigned_to")
            params.append({"name": "@assigned_to", "value": assigned_to})

        # Archival filter: exclude archived by default
        if archived_only:
            conditions.append("IS_DEFINED(c.archived_at) AND c.archived_at != null")
        elif not include_archived:
            conditions.append("(NOT IS_DEFINED(c.archived_at) OR c.archived_at = null)")

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"

        return await self.query_count(tenant_id, query_text, params)

    async def assign_agent(
        self,
        tenant_id: str,
        conversation_id: str,
        agent_id: str,
    ) -> dict[str, Any]:
        """Assign a human agent to a conversation (post-escalation)."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "set", "path": "/assigned_to", "value": agent_id},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    async def add_internal_note(
        self,
        tenant_id: str,
        conversation_id: str,
        note: dict[str, Any],
    ) -> dict[str, Any]:
        """Append an internal merchant note to a conversation."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=conversation_id,
            operations=[
                {"op": "add", "path": "/internal_notes/-", "value": note},
                {"op": "set", "path": "/last_activity_at", "value": now},
            ],
        )

    # --- Analytics aggregation queries (WI #176-178) ---

    async def count_by_status(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Count conversations grouped by status in a date range.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).

        Returns list of {status, count} dicts.
        """
        query_text = (
            "SELECT c.status, COUNT(1) AS count FROM c "
            "WHERE c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        query_text += " GROUP BY c.status"

        return await self.query(tenant_id, query_text, params)

    async def aggregate_metrics(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
    ) -> dict[str, Any]:
        """Compute aggregate conversation metrics for a date range.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).

        Returns a dict with total, billable, avg_turns, avg_messages,
        escalated, critic_passed, critic_failed counts.
        """
        query_text = (
            "SELECT "
            "COUNT(1) AS total, "
            "SUM(c.is_billable ? 1 : 0) AS billable, "
            "AVG(c.turn_count) AS avg_turns, "
            "AVG(c.message_count) AS avg_messages, "
            "SUM(c.status = 'escalated' ? 1 : 0) AS escalated, "
            "SUM(c.critic_passed = true ? 1 : 0) AS critic_passed, "
            "SUM(c.critic_passed = false ? 1 : 0) AS critic_failed "
            "FROM c WHERE c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        results = await self.query(tenant_id, query_text, params)
        if results:
            return results[0]
        return {
            "total": 0, "billable": 0, "avg_turns": 0,
            "avg_messages": 0, "escalated": 0,
            "critic_passed": 0, "critic_failed": 0,
            "avg_response_time": 0, "customer_satisfaction": 0,
        }

    async def list_agents_invoked(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        is_test_mode: bool | None = None,
    ) -> list[dict[str, Any]]:
        """List all conversations with their agents_invoked for intent analysis.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).

        Returns conversation docs with only the fields needed for
        agent/intent frequency analysis: conversation_id, agents_invoked,
        status, started_at.
        """
        query_text = (
            "SELECT c.tenant_id, c.conversation_id, c.agents_invoked, c.status, "
            "c.started_at FROM c "
            "WHERE c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        return await self.query(tenant_id, query_text, params)

    async def list_gap_conversations(
        self,
        tenant_id: str,
        since: str,
        until: str | None = None,
        limit: int = 50,
        is_test_mode: bool | None = None,
    ) -> list[dict[str, Any]]:
        """List conversations that represent potential knowledge gaps.

        Args:
            tenant_id: Tenant partition key.
            since: Start timestamp (ISO 8601, inclusive).
            until: End timestamp (ISO 8601, exclusive).
            limit: Maximum number of results.
            is_test_mode: Filter by test mode flag (None = all,
                True = test only, False = production only).

        Returns conversations with escalated or error status — these
        indicate the AI couldn't resolve the customer's issue.
        """
        query_text = (
            "SELECT c.tenant_id, c.conversation_id, c.status, c.customer_id, "
            "c.turn_count, c.message_count, c.agents_invoked, "
            "c.critic_passed, c.started_at, c.ended_at "
            "FROM c "
            "WHERE (c.status = 'escalated' OR c.status = 'error') "
            "AND c.started_at >= @since"
        )
        params: list[dict[str, Any]] = [{"name": "@since", "value": since}]

        if until is not None:
            query_text += " AND c.started_at < @until"
            params.append({"name": "@until", "value": until})

        if is_test_mode is True:
            query_text += " AND c.is_test_mode = true"
        elif is_test_mode is False:
            query_text += " AND (NOT IS_DEFINED(c.is_test_mode) OR c.is_test_mode = false)"

        query_text += " ORDER BY c.started_at DESC"
        params.append({"name": "@limit", "value": limit})
        query_text += " OFFSET 0 LIMIT @limit"

        return await self.query(tenant_id, query_text, params)


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

    async def list_active_lightweight(
        self,
        tenant_id: str,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """List active KB entries excluding the embedding field.

        Used by BM25 scoring which only needs id, title, content, and tags.
        Excludes the 3072-float embedding array to reduce Cosmos DB response
        payload (~24KB savings per entry).
        """
        query_text = (
            "SELECT c.id, c.tenant_id, c.title, c.content, c.tags, "
            "c.entry_type, c.language, c.metadata, c.source_type, "
            "c.content_hash, c.is_active "
            "FROM c WHERE c.is_active = true"
        )
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

    # --- Admin knowledge base queries (WI #175) ---

    async def list_filtered(
        self,
        tenant_id: str,
        *,
        entry_type: str | None = None,
        language: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List knowledge base entries with filters for admin management.

        Args:
            tenant_id: Tenant partition key.
            entry_type: Filter by type (product, faq, policy, custom).
            language: Filter by language code.
            is_active: Filter by active status (None = all).
            search: Substring search on title (case-insensitive via CONTAINS).
            offset: Pagination offset.
            limit: Page size.
        """
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if entry_type is not None:
            conditions.append("c.entry_type = @entry_type")
            params.append({"name": "@entry_type", "value": entry_type})

        if language is not None:
            conditions.append("c.language = @language")
            params.append({"name": "@language", "value": language})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        if search is not None:
            conditions.append(
                "(CONTAINS(LOWER(c.title), LOWER(@search))"
                " OR CONTAINS(LOWER(IS_DEFINED(c.content) ? c.content : ''), LOWER(@search)))"
            )
            params.append({"name": "@search", "value": search})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        query_text = (
            f"SELECT * FROM c WHERE {where_clause} "
            "ORDER BY c.updated_at DESC "
            "OFFSET @offset LIMIT @limit"
        )

        return await self.query(tenant_id, query_text, params)

    async def count_filtered(
        self,
        tenant_id: str,
        *,
        entry_type: str | None = None,
        language: str | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> int:
        """Count knowledge base entries matching filters (for pagination)."""
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if entry_type is not None:
            conditions.append("c.entry_type = @entry_type")
            params.append({"name": "@entry_type", "value": entry_type})

        if language is not None:
            conditions.append("c.language = @language")
            params.append({"name": "@language", "value": language})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        if search is not None:
            conditions.append(
                "(CONTAINS(LOWER(c.title), LOWER(@search))"
                " OR CONTAINS(LOWER(IS_DEFINED(c.content) ? c.content : ''), LOWER(@search)))"
            )
            params.append({"name": "@search", "value": search})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"

        return await self.query_count(tenant_id, query_text, params)

    async def soft_delete(
        self,
        tenant_id: str,
        document_id: str,
    ) -> dict[str, Any]:
        """Soft-delete a knowledge base entry (set is_active = false)."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=document_id,
            operations=[
                {"op": "set", "path": "/is_active", "value": False},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    # --- Vector search (WI #211) ---

    async def vector_search(
        self,
        tenant_id: str,
        embedding: list[float],
        *,
        top_k: int = 5,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search KB entries by vector similarity using DiskANN.

        Args:
            tenant_id: Tenant partition key.
            embedding: Query embedding (3072 dimensions).
            top_k: Number of results to return.
            entry_type: Optional filter by entry type.
            language: Optional filter by language.

        Returns:
            List of matching entries with similarity scores, ordered
            by similarity (most similar first). Only returns active
            entries with embeddings.
        """
        conditions = [
            "c.tenant_id = @tenant_id",
            "c.is_active = true",
            "c.embedding != null",
        ]
        params: list[dict[str, Any]] = [
            {"name": "@tenant_id", "value": tenant_id},
            {"name": "@embedding", "value": embedding},
        ]

        if entry_type:
            conditions.append("c.entry_type = @entry_type")
            params.append({"name": "@entry_type", "value": entry_type})

        if language:
            conditions.append("c.language = @language")
            params.append({"name": "@language", "value": language})

        where_clause = " AND ".join(conditions)

        query_text = (
            f"SELECT c.id, c.tenant_id, c.entry_type, c.title, c.content, "
            f"c.metadata, c.tags, c.language, c.source_type, "
            f"VectorDistance(c.embedding, @embedding) AS similarity "
            f"FROM c "
            f"WHERE {where_clause} "
            f"ORDER BY VectorDistance(c.embedding, @embedding) "
            f"OFFSET 0 LIMIT @top_k"
        )
        params.append({"name": "@top_k", "value": top_k})

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

    async def list_unembedded(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List active entries that have no embedding yet.

        Used by the background embedding pipeline to find entries
        that need vectorization.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.is_active = true "
                "AND (NOT IS_DEFINED(c.embedding) OR c.embedding = null) "
                "OFFSET 0 LIMIT @limit"
            ),
            parameters=[{"name": "@limit", "value": limit}],
        )

    async def list_stale_embeddings(
        self,
        tenant_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List entries whose content has changed since last embedding.

        Compares current content_hash against stored content_hash to
        detect entries that need re-embedding.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.is_active = true "
                "AND c.embedding != null "
                "AND c.content_hash != null "
                "ORDER BY c.updated_at DESC "
                "OFFSET 0 LIMIT @limit"
            ),
            parameters=[{"name": "@limit", "value": limit}],
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
    """Repository for the preferences collection (versioned config).

    Save → Activate model:
        - get_active()   reads the live config (chat pipeline, widget)
        - get_draft()    reads the draft config (admin UI edits)
        - get_previous() reads the previous activation (for Restore)
        - get_current()  backward-compat alias for get_active()
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_PREFERENCES)

    # ---- Save → Activate state queries ----

    async def get_active(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the currently activated preferences (config_state='active').

        Backward-compatible: also matches old documents with
        ``is_current=true`` that predate the config_state field.
        """
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE (c.config_state = 'active' "
                "       OR (c.is_current = true "
                "           AND NOT IS_DEFINED(c.config_state))) "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def get_draft(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the current draft preferences (config_state='draft')."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_state = 'draft' "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def get_previous(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the previous activation snapshot (config_state='previous')."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_state = 'previous' "
                "ORDER BY c.version DESC"
            ),
            max_items=1,
        )
        return results[0] if results else None

    async def get_current(self, tenant_id: str) -> dict[str, Any] | None:
        """Get the current (active) preferences version.

        Backward-compatible alias for ``get_active()``.  All existing
        callers (pipeline, widget, test mode removal) continue to work.
        """
        return await self.get_active(tenant_id)

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

    async def list_named(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List all preference versions that have a config_name."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_name != null "
                "ORDER BY c.version DESC"
            ),
            max_items=50,
        )

    async def get_by_name(
        self, tenant_id: str, config_name: str,
    ) -> dict[str, Any] | None:
        """Get a preference version by config_name."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.config_name = @config_name "
                "ORDER BY c.version DESC"
            ),
            parameters=[{"name": "@config_name", "value": config_name}],
            max_items=1,
        )
        return results[0] if results else None

    # ---- Named widget appearance queries (C4) ----

    async def list_named_appearances(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List all preference versions that have an appearance_name."""
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.appearance_name != null "
                "ORDER BY c.version DESC"
            ),
            max_items=50,
        )

    async def get_by_appearance_name(
        self, tenant_id: str, appearance_name: str,
    ) -> dict[str, Any] | None:
        """Get a preference version by appearance_name."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.appearance_name = @appearance_name "
                "ORDER BY c.version DESC"
            ),
            parameters=[{"name": "@appearance_name", "value": appearance_name}],
            max_items=1,
        )
        return results[0] if results else None

    # ---- Quick Action Prompt methods (WI #226-229) ----
    #
    # Quick action CRUD operates on the DRAFT document under the
    # Save → Activate model.  If no draft exists, reads from active
    # for display purposes.  Write operations target the draft.

    async def _get_draft_or_active(self, tenant_id: str) -> dict[str, Any] | None:
        """Get draft if it exists, otherwise active.  For quick action reads."""
        draft = await self.get_draft(tenant_id)
        if draft is not None:
            return draft
        return await self.get_active(tenant_id)

    async def get_quick_actions(self, tenant_id: str) -> list[dict[str, Any]]:
        """Get all quick action prompts for a tenant.

        Reads from draft (if exists) or active preferences document.
        """
        doc = await self._get_draft_or_active(tenant_id)
        if not doc:
            return []
        return doc.get("quick_actions", [])

    async def get_quick_actions_active(self, tenant_id: str) -> list[dict[str, Any]]:
        """Get quick actions from the ACTIVE config only (for widget serving)."""
        active = await self.get_active(tenant_id)
        if not active:
            return []
        return active.get("quick_actions", [])

    async def upsert_quick_action(
        self, tenant_id: str, action: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update a quick action in the draft preferences.

        Uses read-modify-write on the quick_actions array within the
        draft document. If no draft exists, patches the active document's
        quick_actions as a draft edit — the ActivationService is responsible
        for creating the full draft document before this is called.
        """
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            raise DocumentNotFoundError(
                self._collection_name, "draft_or_active", tenant_id,
            )

        actions: list[dict[str, Any]] = target.get("quick_actions", [])

        # Find and replace existing, or append new
        found = False
        for i, existing in enumerate(actions):
            if existing.get("id") == action["id"]:
                actions[i] = action
                found = True
                break
        if not found:
            actions.append(action)

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[{"op": "set", "path": "/quick_actions", "value": actions}],
        )
        return action

    async def delete_quick_action(
        self, tenant_id: str, action_id: str,
    ) -> bool:
        """Remove a quick action from the draft preferences.

        Also removes any page assignment references to this action ID.
        Returns True if the action was found and removed.
        """
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            return False

        actions: list[dict[str, Any]] = target.get("quick_actions", [])
        original_len = len(actions)
        actions = [a for a in actions if a.get("id") != action_id]

        if len(actions) == original_len:
            return False  # Not found

        # Also clean up assignments referencing this action
        assignments: list[dict[str, Any]] = target.get(
            "quick_action_assignments", [],
        )
        for assignment in assignments:
            if assignment.get("slot_1_action_id") == action_id:
                assignment["slot_1_action_id"] = None
            if assignment.get("slot_2_action_id") == action_id:
                assignment["slot_2_action_id"] = None

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[
                {"op": "set", "path": "/quick_actions", "value": actions},
                {"op": "set", "path": "/quick_action_assignments", "value": assignments},
            ],
        )
        return True

    async def get_page_assignments(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """Get all page-to-quick-action assignments for a tenant."""
        doc = await self._get_draft_or_active(tenant_id)
        if not doc:
            return []
        return doc.get("quick_action_assignments", [])

    async def get_page_assignments_active(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """Get page assignments from the ACTIVE config only (for widget serving)."""
        active = await self.get_active(tenant_id)
        if not active:
            return []
        return active.get("quick_action_assignments", [])

    async def upsert_page_assignment(
        self, tenant_id: str, assignment: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or update a page assignment in the draft preferences.

        Matches on page_type + page_handle combination. If a matching
        assignment exists, replaces it; otherwise appends.
        """
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            raise DocumentNotFoundError(
                self._collection_name, "draft_or_active", tenant_id,
            )

        assignments: list[dict[str, Any]] = target.get(
            "quick_action_assignments", [],
        )

        # Find and replace existing (match on page_type + page_handle)
        found = False
        for i, existing in enumerate(assignments):
            if (
                existing.get("page_type") == assignment["page_type"]
                and existing.get("page_handle") == assignment.get("page_handle")
            ):
                assignments[i] = assignment
                found = True
                break
        if not found:
            assignments.append(assignment)

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[
                {"op": "set", "path": "/quick_action_assignments", "value": assignments},
            ],
        )
        return assignment

    async def delete_page_assignment(
        self, tenant_id: str, page_type: str, page_handle: str | None = None,
    ) -> bool:
        """Remove a page assignment from draft. Returns True if found and removed."""
        target = await self.get_draft(tenant_id)
        if not target:
            target = await self.get_active(tenant_id)
        if not target:
            return False

        assignments: list[dict[str, Any]] = target.get(
            "quick_action_assignments", [],
        )
        original_len = len(assignments)
        assignments = [
            a for a in assignments
            if not (
                a.get("page_type") == page_type
                and a.get("page_handle") == page_handle
            )
        ]

        if len(assignments) == original_len:
            return False

        await self.patch(
            tenant_id=tenant_id,
            document_id=target["id"],
            operations=[
                {"op": "set", "path": "/quick_action_assignments", "value": assignments},
            ],
        )
        return True


# ---------------------------------------------------------------------------
# Collection 8: TeamMemberRepository (WI #179)
# ---------------------------------------------------------------------------


class TeamMemberRepository(TenantScopedRepository):
    """Repository for the team_members collection.

    Manages merchant team members who access the admin dashboard
    and/or handle escalated conversations.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_TEAM_MEMBERS)

    async def list_members(
        self,
        tenant_id: str,
        *,
        role: str | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List team members with optional filtering.

        Args:
            tenant_id: Tenant partition key.
            role: Filter by role (owner, admin, agent, viewer).
            is_active: Filter by active status (None = all).
            offset: Pagination offset.
            limit: Page size.
        """
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if role is not None:
            conditions.append("c.role = @role")
            params.append({"name": "@role", "value": role})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        query_text = (
            f"SELECT * FROM c WHERE {where_clause} "
            "ORDER BY c.updated_at DESC "
            "OFFSET @offset LIMIT @limit"
        )

        return await self.query(tenant_id, query_text, params)

    async def count_members(
        self,
        tenant_id: str,
        *,
        role: str | None = None,
        is_active: bool | None = None,
    ) -> int:
        """Count team members matching filters (for pagination)."""
        conditions: list[str] = []
        params: list[dict[str, Any]] = []

        if role is not None:
            conditions.append("c.role = @role")
            params.append({"name": "@role", "value": role})

        if is_active is not None:
            conditions.append("c.is_active = @is_active")
            params.append({"name": "@is_active", "value": is_active})

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where_clause}"

        return await self.query_count(tenant_id, query_text, params)

    async def find_by_email(
        self, tenant_id: str, email: str,
    ) -> dict[str, Any] | None:
        """Find a team member by email address (unique within tenant)."""
        results = await self.query(
            tenant_id=tenant_id,
            query_text="SELECT * FROM c WHERE c.email = @email",
            parameters=[{"name": "@email", "value": email}],
            max_items=1,
        )
        return results[0] if results else None

    async def deactivate(
        self, tenant_id: str, document_id: str,
    ) -> dict[str, Any]:
        """Deactivate a team member (set is_active = false)."""
        now = datetime.now(timezone.utc).isoformat()
        return await self.patch(
            tenant_id=tenant_id,
            document_id=document_id,
            operations=[
                {"op": "set", "path": "/is_active", "value": False},
                {"op": "set", "path": "/updated_at", "value": now},
            ],
        )

    async def list_active_agents(
        self, tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List active team members with the escalation_agent role.

        Used for escalation routing — returns agents who can handle
        escalated conversations.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.role IN ('agent', 'escalation_agent') AND c.is_active = true "
                "ORDER BY c.max_concurrent_conversations DESC"
            ),
        )

    async def find_by_user_api_key_hash(
        self, key_hash: str,
    ) -> dict[str, Any] | None:
        """Find a team member by their per-user API key hash.

        This is a cross-partition query (searches all tenants) because
        at auth time we don't yet know which tenant the key belongs to.

        Returns the team member document or None.
        """
        results = await self.cross_partition_query(
            query_text=(
                "SELECT * FROM c "
                "WHERE c.user_api_key_hash = @key_hash "
                "AND c.is_active = true"
            ),
            parameters=[{"name": "@key_hash", "value": key_hash}],
            max_items=1,
        )
        return results[0] if results else None

    async def list_agents_for_category(
        self, tenant_id: str, category: str,
    ) -> list[dict[str, Any]]:
        """List active escalation agents assigned to a specific category.

        Used for escalation email routing — returns agents whose
        escalation_categories list contains the given category.
        """
        return await self.query(
            tenant_id=tenant_id,
            query_text=(
                "SELECT * FROM c "
                "WHERE c.role IN ('agent', 'escalation_agent') "
                "AND c.is_active = true "
                "AND ARRAY_CONTAINS(c.escalation_categories, @category)"
            ),
            parameters=[{"name": "@category", "value": category}],
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

    def _build_audit_query(
        self,
        tenant_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
        event_type: str | None = None,
        customer_id: str | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        """Build a WHERE clause and params for audit log queries.

        Returns (where_clause, params) — caller prepends SELECT and appends
        ORDER BY / OFFSET / LIMIT as needed.
        """
        clauses = ["c.tenant_id = @tenant_id"]
        params: list[dict[str, Any]] = [
            {"name": "@tenant_id", "value": tenant_id},
        ]

        if date_from:
            clauses.append("c.timestamp >= @date_from")
            params.append({"name": "@date_from", "value": date_from})
        if date_to:
            clauses.append("c.timestamp <= @date_to")
            params.append({"name": "@date_to", "value": date_to})
        if event_type:
            clauses.append("c.event_type = @event_type")
            params.append({"name": "@event_type", "value": event_type})
        if customer_id:
            clauses.append("c.customer_id = @customer_id")
            params.append({"name": "@customer_id", "value": customer_id})

        where = " AND ".join(clauses)
        return where, params

    async def query_by_tenant(
        self,
        tenant_id: str,
        offset: int = 0,
        limit: int = 100,
        date_from: str | None = None,
        date_to: str | None = None,
        event_type: str | None = None,
        customer_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query audit events for a tenant with filtering and pagination.

        Uses cross-partition query to span multiple time partitions
        (e.g. a date range from Jan to Feb). The composite index on
        (tenant_id ASC, timestamp DESC) keeps this efficient.

        Args:
            tenant_id: Tenant to filter for.
            offset: Pagination offset.
            limit: Page size.
            date_from: Start date (ISO 8601 string, inclusive).
            date_to: End date (ISO 8601 string, inclusive).
            event_type: Optional event type filter (string value).
            customer_id: Optional customer ID filter (exact match).
        """
        where, params = self._build_audit_query(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to,
            event_type=event_type,
            customer_id=customer_id,
        )

        query_text = (
            f"SELECT * FROM c WHERE {where} "
            f"ORDER BY c.timestamp DESC "
            f"OFFSET @offset LIMIT @limit"
        )
        params.append({"name": "@offset", "value": offset})
        params.append({"name": "@limit", "value": limit})

        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
        ):
            items.append(item)

        return items

    async def count_by_tenant(
        self,
        tenant_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
        event_type: str | None = None,
        customer_id: str | None = None,
    ) -> int:
        """Count audit events matching the given filters.

        Uses the same cross-partition query approach as query_by_tenant.

        Args:
            tenant_id: Tenant to filter for.
            date_from: Start date (ISO 8601 string, inclusive).
            date_to: End date (ISO 8601 string, inclusive).
            event_type: Optional event type filter (string value).
            customer_id: Optional customer ID filter (exact match).
        """
        where, params = self._build_audit_query(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to,
            event_type=event_type,
            customer_id=customer_id,
        )

        query_text = f"SELECT VALUE COUNT(1) FROM c WHERE {where}"

        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
        ):
            return item  # COUNT returns a single integer value

        return 0

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
