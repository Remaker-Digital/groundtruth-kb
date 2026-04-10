# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
Incident repository — CRUD for status page incidents.

Platform-scoped (not tenant-scoped). Partition key is ``status``
(investigating, identified, monitoring, resolved, scheduled).
Documents auto-expire via Cosmos DB TTL (365 days).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from azure.cosmos.exceptions import (
    CosmosResourceExistsError,
    CosmosResourceNotFoundError,
)

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import (
    COLLECTION_INCIDENTS,
    IncidentSeverity,
    IncidentStatus,
)

logger = logging.getLogger(__name__)


class IncidentRepository:
    """Repository for the incidents collection.

    Platform-scoped (not tenant-scoped). Partition key is ``status``.
    Supports CRUD operations for incident lifecycle management.
    """

    def __init__(self) -> None:
        self._collection_name = COLLECTION_INCIDENTS

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)

    async def create_incident(
        self,
        title: str,
        description: str,
        severity: str = IncidentSeverity.MINOR.value,
        affected_services: list[str] | None = None,
        created_by: str = "system",
    ) -> dict[str, Any]:
        """Create a new incident.

        Returns the created document.
        """
        now = datetime.now(UTC).isoformat()
        incident_id = f"inc-{uuid.uuid4().hex[:12]}"
        status = IncidentStatus.INVESTIGATING.value

        doc = {
            "id": incident_id,
            "incident_id": incident_id,
            "title": title,
            "description": description,
            "status": status,
            "severity": severity,
            "affected_services": affected_services or [],
            "updates": [
                {
                    "timestamp": now,
                    "status": status,
                    "message": f"Incident created: {title}",
                    "author": created_by,
                },
            ],
            "created_at": now,
            "updated_at": now,
            "resolved_at": None,
            "created_by": created_by,
        }
        result = await self._container.create_item(body=doc)
        logger.info("Incident created: id=%s title=%s", incident_id, title)
        return result

    async def get_incident(self, incident_id: str, status: str) -> dict[str, Any] | None:
        """Read a single incident by ID and status (partition key)."""
        try:
            return await self._container.read_item(
                item=incident_id,
                partition_key=status,
            )
        except CosmosResourceNotFoundError:
            return None

    async def find_incident(self, incident_id: str) -> dict[str, Any] | None:
        """Find an incident by ID across all status partitions.

        Performs a cross-partition query. Prefer ``get_incident`` when
        the status is known.
        """
        query = "SELECT * FROM c WHERE c.incident_id = @iid"
        params = [{"name": "@iid", "value": incident_id}]
        # Omit partition_key to enable cross-partition query (SDK 4.14+).
        items = self._container.query_items(
            query=query,
            parameters=params,
        )
        async for item in items:
            return item
        return None

    async def list_active(self) -> list[dict[str, Any]]:
        """List all non-resolved incidents (investigating, identified, monitoring)."""
        results: list[dict[str, Any]] = []
        for status in [
            IncidentStatus.INVESTIGATING.value,
            IncidentStatus.IDENTIFIED.value,
            IncidentStatus.MONITORING.value,
        ]:
            query = (
                "SELECT * FROM c WHERE c.status = @status "
                "ORDER BY c.created_at DESC"
            )
            params = [{"name": "@status", "value": status}]
            items = self._container.query_items(
                query=query,
                parameters=params,
                partition_key=status,
            )
            async for item in items:
                results.append(item)
        return results

    async def list_all(self, limit: int = 50) -> list[dict[str, Any]]:
        """List all incidents (cross-partition), most recent first."""
        query = "SELECT * FROM c ORDER BY c.created_at DESC OFFSET 0 LIMIT @limit"
        params = [{"name": "@limit", "value": limit}]
        # Omit partition_key to enable cross-partition query (SDK 4.14+).
        items = self._container.query_items(
            query=query,
            parameters=params,
        )
        results: list[dict[str, Any]] = []
        async for item in items:
            results.append(item)
        return results

    async def add_update(
        self,
        incident_id: str,
        current_status: str,
        new_status: str,
        message: str,
        author: str = "system",
    ) -> dict[str, Any] | None:
        """Add a status update to an incident.

        If new_status differs from current_status, the document must be
        moved to the new partition. Cosmos DB does not support partition
        key changes, so we delete + recreate.
        """
        now = datetime.now(UTC).isoformat()
        update_entry = {
            "timestamp": now,
            "status": new_status,
            "message": message,
            "author": author,
        }

        doc = await self.get_incident(incident_id, current_status)
        if not doc:
            return None

        # Append update
        updates = doc.get("updates", [])
        updates.append(update_entry)

        if new_status == current_status:
            # Same partition — patch in place
            try:
                await self._container.patch_item(
                    item=incident_id,
                    partition_key=current_status,
                    patch_operations=[
                        {"op": "set", "path": "/updates", "value": updates},
                        {"op": "set", "path": "/updated_at", "value": now},
                    ],
                )
                doc["updates"] = updates
                doc["updated_at"] = now
                return doc
            except Exception:
                logger.warning("Failed to patch incident: id=%s", incident_id)
                return None
        else:
            # Status changed — delete + recreate in new partition
            resolved_at = now if new_status == IncidentStatus.RESOLVED.value else doc.get("resolved_at")
            try:
                await self._container.delete_item(
                    item=incident_id,
                    partition_key=current_status,
                )
            except CosmosResourceNotFoundError:
                return None

            new_doc = {
                "id": incident_id,
                "incident_id": doc["incident_id"],
                "title": doc["title"],
                "description": doc["description"],
                "status": new_status,
                "severity": doc["severity"],
                "affected_services": doc.get("affected_services", []),
                "updates": updates,
                "created_at": doc["created_at"],
                "updated_at": now,
                "resolved_at": resolved_at,
                "created_by": doc.get("created_by", "system"),
            }
            try:
                result = await self._container.create_item(body=new_doc)
                logger.info(
                    "Incident status changed: id=%s %s -> %s",
                    incident_id, current_status, new_status,
                )
                return result
            except CosmosResourceExistsError:
                logger.error("Conflict recreating incident: id=%s", incident_id)
                return None

    async def resolve_incident(
        self,
        incident_id: str,
        current_status: str,
        message: str = "Incident resolved.",
        author: str = "system",
    ) -> dict[str, Any] | None:
        """Resolve an incident (convenience wrapper around add_update)."""
        return await self.add_update(
            incident_id=incident_id,
            current_status=current_status,
            new_status=IncidentStatus.RESOLVED.value,
            message=message,
            author=author,
        )
