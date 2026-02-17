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
    COLLECTION_AUDIT_LOG,
    COLLECTION_PLATFORM_CONFIG,
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
