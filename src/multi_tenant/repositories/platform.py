"""
Platform-scoped repositories — platform_config and audit_log collections.

These collections are NOT partitioned by tenant_id. They use
functional partition keys (config_type, time_partition).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from azure.cosmos.exceptions import CosmosResourceNotFoundError

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import (
    COLLECTION_ADMIN_DOCUMENTATION,
    COLLECTION_AUDIT_LOG,
    COLLECTION_PLATFORM_CONFIG,
    AdminDocumentationDocument,
    AuditEventType,
    AuditLogDocument,
    PlatformConfigDocument,
)

logger = logging.getLogger(__name__)


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

        SPEC-1843 / WI-1616: All payloads are sanitized through
        ``sanitize_audit_payload()`` before persistence — non-allowlisted
        fields are stripped and PII patterns are scrubbed.

        Args:
            event_type: One of the 18 defined AuditEventType values.
            tenant_id: Which tenant the event relates to.
            actor: Who/what triggered the event.
            actor_type: user | system | webhook | admin.
            payload: Event-specific data (sanitized before write).
            conversation_id: Related conversation ID.
            request_id: HTTP request trace ID.

        Returns:
            The created audit log document.
        """
        from src.multi_tenant.audit_sanitizer import sanitize_audit_payload

        now = datetime.now(timezone.utc)
        time_partition = now.strftime("%Y-%m")

        sanitized_payload = sanitize_audit_payload(payload or {})

        doc = AuditLogDocument(
            id=str(uuid.uuid4()),
            time_partition=time_partition,
            event_type=event_type,
            tenant_id=tenant_id,
            actor=actor,
            actor_type=actor_type,
            payload=sanitized_payload,
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
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
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
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
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


# ---------------------------------------------------------------------------
# Collection 18: AdminDocumentationRepository (SPEC-1559)
# ---------------------------------------------------------------------------


class AdminDocumentationRepository(PlatformScopedRepository):
    """Repository for the admin_documentation_vectors collection.

    Platform-scoped — shared across all tenants. Partition key is
    ``/document_category`` (e.g., "dashboard", "knowledge_base").

    Used by the Co-pilot agent to retrieve product documentation
    when team members ask about Agent Red admin features.

    (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
    """

    def __init__(self) -> None:
        super().__init__(COLLECTION_ADMIN_DOCUMENTATION)

    async def upsert_document(
        self, doc: AdminDocumentationDocument,
    ) -> dict[str, Any]:
        """Create or replace a documentation entry."""
        body = doc.model_dump(by_alias=True, exclude_none=True)
        return await self._container.upsert_item(body=body)

    async def get_by_id(
        self, document_category: str, doc_id: str,
    ) -> dict[str, Any] | None:
        """Read a single documentation entry by ID."""
        try:
            return await self._container.read_item(
                item=doc_id, partition_key=document_category,
            )
        except CosmosResourceNotFoundError:
            return None

    async def list_by_category(
        self, document_category: str, active_only: bool = True,
    ) -> list[dict[str, Any]]:
        """List all documentation entries in a category."""
        query = "SELECT * FROM c"
        params: list[dict[str, Any]] = []
        if active_only:
            query += " WHERE c.is_active = true"

        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query,
            parameters=params,
            partition_key=document_category,
        ):
            items.append(item)
        return items

    async def list_all_active(self) -> list[dict[str, Any]]:
        """List all active documentation entries (cross-partition).

        Used for full-corpus BM25 scoring and re-embedding.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query="SELECT * FROM c WHERE c.is_active = true",
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
        ):
            items.append(item)
        return items

    async def list_all_lightweight(self) -> list[dict[str, Any]]:
        """List active docs without embedding field (~24KB savings per entry).

        Used for BM25 keyword scoring where embeddings are not needed.
        """
        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=(
                "SELECT c.id, c.document_category, c.title, c.content, "
                "c.section, c.tags, c.content_hash, c.is_active "
                "FROM c WHERE c.is_active = true"
            ),
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
        ):
            items.append(item)
        return items

    async def vector_search(
        self,
        document_category: str,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search within a specific document category.

        Uses Cosmos DB DiskANN vector index with cosine similarity.
        """
        query_text = (
            "SELECT c.id, c.document_category, c.title, c.content, "
            "c.section, c.tags, c.source_file, "
            "VectorDistance(c.embedding, @embedding) AS similarity "
            "FROM c "
            "WHERE c.is_active = true "
            "ORDER BY VectorDistance(c.embedding, @embedding) "
            "OFFSET 0 LIMIT @top_k"
        )
        params = [
            {"name": "@embedding", "value": embedding},
            {"name": "@top_k", "value": top_k},
        ]

        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
            partition_key=document_category,
        ):
            items.append(item)
            if len(items) >= top_k:
                break
        return items

    async def vector_search_all_categories(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Semantic search across ALL documentation categories.

        Cross-partition vector search — used when the Co-pilot doesn't
        know which category the team member's question falls into.
        """
        query_text = (
            "SELECT c.id, c.document_category, c.title, c.content, "
            "c.section, c.tags, c.source_file, "
            "VectorDistance(c.embedding, @embedding) AS similarity "
            "FROM c "
            "WHERE c.is_active = true "
            "ORDER BY VectorDistance(c.embedding, @embedding) "
            "OFFSET 0 LIMIT @top_k"
        )
        params = [
            {"name": "@embedding", "value": embedding},
            {"name": "@top_k", "value": top_k},
        ]

        items: list[dict[str, Any]] = []
        async for item in self._container.query_items(
            query=query_text,
            parameters=params,
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
        ):
            items.append(item)
            if len(items) >= top_k:
                break
        return items

    async def count_all(self) -> int:
        """Count all active documentation entries."""
        async for item in self._container.query_items(
            query="SELECT VALUE COUNT(1) FROM c WHERE c.is_active = true",
            # cross-partition is automatic when partition_key is omitted (azure-cosmos >=4.9)
        ):
            return item
        return 0
