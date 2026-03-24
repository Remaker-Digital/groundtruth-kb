"""
Base repository classes and shared exceptions.

TenantScopedRepository enforces mandatory tenant_id on every Cosmos DB
operation, making cross-tenant data access structurally impossible.

Architecture reference: Decision #1 (TenantScopedRepository)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from typing import Any, TypeVar

from azure.cosmos.exceptions import (
    CosmosHttpResponseError,
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)
from pydantic import BaseModel

from src.multi_tenant.cosmos_client import get_cosmos_manager

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# DEK cache — module-level, shared by all repository instances (WI-1628)
# ---------------------------------------------------------------------------

_DEK_TTL_SECONDS = 300   # 5 minutes — matches credential cache
_DEK_CACHE_MAX = 500


class _DekCacheEntry:
    """TTL-bounded cache entry for an unwrapped (raw) DEK."""
    __slots__ = ("raw_dek", "wrapped_dek", "expires_at")

    def __init__(self, raw_dek: bytes, wrapped_dek: bytes) -> None:
        self.raw_dek = raw_dek
        self.wrapped_dek = wrapped_dek
        self.expires_at = time.monotonic() + _DEK_TTL_SECONDS

    @property
    def is_expired(self) -> bool:
        return time.monotonic() >= self.expires_at


# tenant_id → _DekCacheEntry
_dek_cache: dict[str, _DekCacheEntry] = {}
_dek_lock = asyncio.Lock()


async def _fetch_tenant_dek(tenant_id: str) -> _DekCacheEntry | None:
    """Fetch wrapped DEK from Key Vault, unwrap it, and return a cache entry.

    Returns None if the tenant has no DEK provisioned (pre-migration).
    """
    from src.multi_tenant.envelope_encryption import get_envelope_encryption_service
    from src.multi_tenant.tenant_secret_service import (
        TenantSecretType,
        get_secret_service,
    )

    svc = get_envelope_encryption_service()
    if svc is None:
        return None

    # Get the TenantSecretService singleton (initialized at startup)
    secret_svc = get_secret_service()
    if secret_svc is None:
        return None

    # Retrieve wrapped DEK (base64-encoded string in KV)
    wrapped_b64 = await secret_svc.get_secret(tenant_id, TenantSecretType.DEK)
    if wrapped_b64 is None:
        return None

    wrapped_dek = base64.b64decode(wrapped_b64)

    # Unwrap via the encryption service (async — calls KV in production)
    raw_dek = await svc.unwrap_key_async(wrapped_dek, tenant_id)

    return _DekCacheEntry(raw_dek=raw_dek, wrapped_dek=wrapped_dek)


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

    SPEC-1843 / WI-1626: Subclasses may declare ``_encryption_fields``
    (a frozenset of field names) to enable transparent field-level
    encryption via ``_pre_write`` / ``_post_read`` hooks.
    """

    _encryption_fields: frozenset[str] = frozenset()

    def __init__(self, collection_name: str) -> None:
        self._collection_name = collection_name

    # -- SPEC-1843 encryption hooks -----------------------------------------

    async def _pre_write(self, body: dict[str, Any], tenant_id: str) -> dict[str, Any]:
        """Encrypt sensitive fields before Cosmos DB write.

        Only encrypts fields listed in ``_encryption_fields``.
        No-op if encryption service is not initialized or no fields declared.
        """
        if not self._encryption_fields:
            return body
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service
        svc = get_envelope_encryption_service()
        if svc is None:
            return body

        # Get tenant's DEK (wrapped bytes, with raw cached internally)
        entry = await self._get_tenant_dek(tenant_id)
        if entry is None:
            return body

        doc_id = body.get("id", "unknown")
        for field in self._encryption_fields:
            if field in body and isinstance(body[field], str):
                body[field] = svc.encrypt_field(
                    entry.wrapped_dek, body[field],
                    tenant_id=tenant_id, doc_id=doc_id,
                )
        return body

    async def _post_read(self, body: dict[str, Any], tenant_id: str) -> dict[str, Any]:
        """Decrypt sensitive fields after Cosmos DB read.

        Only decrypts fields listed in ``_encryption_fields``.
        No-op if encryption service is not initialized or no fields declared.
        """
        if not self._encryption_fields:
            return body
        from src.multi_tenant.envelope_encryption import get_envelope_encryption_service
        svc = get_envelope_encryption_service()
        if svc is None:
            return body

        entry = await self._get_tenant_dek(tenant_id)
        if entry is None:
            return body

        doc_id = body.get("id", "unknown")
        for field in self._encryption_fields:
            if field in body and isinstance(body[field], str):
                body[field] = svc.decrypt_field(
                    entry.wrapped_dek, body[field],
                    tenant_id=tenant_id, doc_id=doc_id,
                )
        return body

    async def _get_tenant_dek(self, tenant_id: str) -> _DekCacheEntry | None:
        """Retrieve the DEK for a tenant with async cache + double-check lock.

        Returns a ``_DekCacheEntry`` (raw + wrapped DEK) or None if no DEK
        is provisioned for this tenant (pre-migration graceful degradation).

        Cache is module-level and shared across all repository instances.
        TTL-based expiry (5 min) balances freshness vs. Key Vault latency.
        asyncio.Lock prevents thundering herd on cache miss.
        """
        # Fast path: cache hit (no lock)
        entry = _dek_cache.get(tenant_id)
        if entry is not None and not entry.is_expired:
            return entry

        # Slow path: acquire lock, double-check, fetch if needed
        async with _dek_lock:
            # Double-check after acquiring lock
            entry = _dek_cache.get(tenant_id)
            if entry is not None and not entry.is_expired:
                return entry

            # Evict expired entry
            if entry is not None:
                del _dek_cache[tenant_id]

            # Fetch from Key Vault
            try:
                new_entry = await _fetch_tenant_dek(tenant_id)
            except Exception:
                logger.warning(
                    "Failed to fetch DEK for tenant %s — encryption inactive",
                    tenant_id,
                    exc_info=True,
                )
                return None

            if new_entry is None:
                return None

            # Evict oldest if at capacity
            if len(_dek_cache) >= _DEK_CACHE_MAX:
                oldest_key = next(iter(_dek_cache))
                del _dek_cache[oldest_key]

            _dek_cache[tenant_id] = new_entry
            return new_entry

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

        # SPEC-1843: encrypt sensitive fields before write
        body = await self._pre_write(body, tenant_id)

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
            self._validate_document_tenant(result, tenant_id)
            # SPEC-1843: decrypt sensitive fields after read
            result = await self._post_read(result, tenant_id)
            return result
        except CosmosResourceNotFoundError as exc:
            raise DocumentNotFoundError(
                self._collection_name, document_id, tenant_id,
            ) from exc

    async def upsert(self, tenant_id: str, document: BaseModel) -> dict[str, Any]:
        """Create or replace a document.

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

        # SPEC-1843: encrypt sensitive fields before write
        body = await self._pre_write(body, tenant_id)

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
        """Apply patch operations to a document.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document_id: Document to patch.
            operations: List of Cosmos DB patch operations.

        Returns:
            The patched document as a dict.
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
        """Delete a document by ID.

        Args:
            tenant_id: Tenant partition key (mandatory).
            document_id: Document to delete.

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
            # SPEC-1843: decrypt sensitive fields after read
            item = await self._post_read(item, tenant_id)
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
