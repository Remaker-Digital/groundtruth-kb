"""
Alert repositories — CRUD for alert rules and alert history.

Two collections:
  - alert_rules: persistent rule definitions (partition key: /rule_type)
  - alert_history: firing events with 90-day TTL (partition key: /alert_date)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from azure.cosmos.exceptions import (
    CosmosResourceNotFoundError,
)

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import (
    COLLECTION_ALERT_HISTORY,
    COLLECTION_ALERT_RULES,
    AlertSeverity,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Alert Rule Repository
# ---------------------------------------------------------------------------


class AlertRuleRepository:
    """Repository for the alert_rules collection.

    Platform-scoped. Partition key is ``rule_type``.
    Rules persist until explicitly deleted (no TTL).
    """

    def __init__(self) -> None:
        self._collection_name = COLLECTION_ALERT_RULES

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)

    async def create_rule(
        self,
        name: str,
        rule_type: str,
        description: str = "",
        condition: dict[str, Any] | None = None,
        notification_channels: list[str] | None = None,
        cooldown_minutes: int = 60,
        runbook_url: str = "",
    ) -> dict[str, Any]:
        """Create a new alert rule."""
        now = datetime.now(timezone.utc).isoformat()
        rule_id = f"rule-{uuid.uuid4().hex[:12]}"

        doc = {
            "id": rule_id,
            "rule_id": rule_id,
            "rule_type": rule_type,
            "name": name,
            "description": description,
            "enabled": True,
            "condition": condition or {"metric": "", "operator": "gt", "threshold": 0},
            "notification_channels": notification_channels or [],
            "cooldown_minutes": cooldown_minutes,
            "runbook_url": runbook_url,
            "created_at": now,
            "updated_at": now,
        }
        result = await self._container.create_item(body=doc)
        logger.info("Alert rule created: id=%s name=%s type=%s", rule_id, name, rule_type)
        return result

    async def get_rule(self, rule_id: str, rule_type: str) -> dict[str, Any] | None:
        """Read a single rule."""
        try:
            return await self._container.read_item(
                item=rule_id,
                partition_key=rule_type,
            )
        except CosmosResourceNotFoundError:
            return None

    async def find_rule(self, rule_id: str) -> dict[str, Any] | None:
        """Find a rule by ID (cross-partition)."""
        query = "SELECT * FROM c WHERE c.rule_id = @rid"
        params = [{"name": "@rid", "value": rule_id}]
        items = self._container.query_items(
            query=query,
            parameters=params,
        )
        async for item in items:
            return item
        return None

    async def list_rules(self) -> list[dict[str, Any]]:
        """List all alert rules (cross-partition). Alias for list_all."""
        return await self.list_all()

    async def list_all(self) -> list[dict[str, Any]]:
        """List all alert rules (cross-partition)."""
        query = "SELECT * FROM c ORDER BY c.created_at DESC"
        items = self._container.query_items(
            query=query,
            parameters=[],
        )
        results: list[dict[str, Any]] = []
        async for item in items:
            results.append(item)
        return results

    async def list_enabled(self) -> list[dict[str, Any]]:
        """List all enabled alert rules (cross-partition)."""
        query = "SELECT * FROM c WHERE c.enabled = true"
        items = self._container.query_items(
            query=query,
            parameters=[],
        )
        results: list[dict[str, Any]] = []
        async for item in items:
            results.append(item)
        return results

    async def update_rule(
        self,
        rule_id: str,
        rule_type: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Update a rule via patch operations."""
        now = datetime.now(timezone.utc).isoformat()
        ops: list[dict[str, Any]] = [
            {"op": "set", "path": "/updated_at", "value": now},
        ]
        for key, value in updates.items():
            if key not in ("id", "rule_id", "rule_type", "created_at"):
                ops.append({"op": "set", "path": f"/{key}", "value": value})

        try:
            result = await self._container.patch_item(
                item=rule_id,
                partition_key=rule_type,
                patch_operations=ops,
            )
            logger.info("Alert rule updated: id=%s", rule_id)
            return result
        except CosmosResourceNotFoundError:
            return None

    async def delete_rule(self, rule_id: str, rule_type: str) -> bool:
        """Delete a rule. Returns True if deleted."""
        try:
            await self._container.delete_item(
                item=rule_id,
                partition_key=rule_type,
            )
            logger.info("Alert rule deleted: id=%s", rule_id)
            return True
        except CosmosResourceNotFoundError:
            return False


# ---------------------------------------------------------------------------
# Alert History Repository
# ---------------------------------------------------------------------------


class AlertHistoryRepository:
    """Repository for the alert_history collection.

    Platform-scoped. Partition key is ``alert_date`` (YYYY-MM-DD).
    Documents auto-expire via Cosmos DB TTL (90 days).
    """

    def __init__(self) -> None:
        self._collection_name = COLLECTION_ALERT_HISTORY

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)

    async def log_alert(
        self,
        rule_id: str,
        rule_name: str,
        rule_type: str,
        severity: str = AlertSeverity.WARNING.value,
        message: str = "",
        metric_value: float = 0,
        threshold_value: float = 0,
        tenant_id: str = "",
    ) -> dict[str, Any]:
        """Log an alert firing event."""
        now = datetime.now(timezone.utc)
        alert_date = now.strftime("%Y-%m-%d")
        alert_id = f"alert-{uuid.uuid4().hex[:12]}"

        doc = {
            "id": alert_id,
            "alert_date": alert_date,
            "rule_id": rule_id,
            "rule_name": rule_name,
            "rule_type": rule_type,
            "tenant_id": tenant_id,
            "triggered_at": now.isoformat(),
            "resolved_at": None,
            "severity": severity,
            "message": message,
            "metric_value": metric_value,
            "threshold_value": threshold_value,
            "acknowledged": False,
            "acknowledged_by": None,
        }
        result = await self._container.create_item(body=doc)
        logger.info("Alert logged: rule=%s severity=%s tenant=%s", rule_name, severity, tenant_id)
        return result

    async def list_recent(self, days: int = 7, limit: int = 100) -> list[dict[str, Any]]:
        """List recent alert history (cross-partition)."""
        query = (
            "SELECT * FROM c ORDER BY c.triggered_at DESC "
            "OFFSET 0 LIMIT @limit"
        )
        params = [{"name": "@limit", "value": limit}]
        items = self._container.query_items(
            query=query,
            parameters=params,
        )
        results: list[dict[str, Any]] = []
        async for item in items:
            results.append(item)
        return results

    async def acknowledge(
        self,
        alert_id: str,
        alert_date: str,
        acknowledged_by: str = "system",
    ) -> dict[str, Any] | None:
        """Mark an alert as acknowledged."""
        try:
            result = await self._container.patch_item(
                item=alert_id,
                partition_key=alert_date,
                patch_operations=[
                    {"op": "set", "path": "/acknowledged", "value": True},
                    {"op": "set", "path": "/acknowledged_by", "value": acknowledged_by},
                ],
            )
            logger.info("Alert acknowledged: id=%s by=%s", alert_id, acknowledged_by)
            return result
        except CosmosResourceNotFoundError:
            return None

    async def get_last_trigger_for_rule(
        self,
        rule_id: str,
        tenant_id: str = "",
    ) -> dict[str, Any] | None:
        """Get the most recent alert for a given rule (for cooldown check).

        Args:
            rule_id: Rule to check.
            tenant_id: When provided, scopes the cooldown check to this
                tenant so one tenant's alert does not suppress another's.
        """
        if tenant_id:
            query = (
                "SELECT * FROM c WHERE c.rule_id = @rid AND c.tenant_id = @tid "
                "ORDER BY c.triggered_at DESC OFFSET 0 LIMIT 1"
            )
            params = [
                {"name": "@rid", "value": rule_id},
                {"name": "@tid", "value": tenant_id},
            ]
        else:
            query = (
                "SELECT * FROM c WHERE c.rule_id = @rid "
                "ORDER BY c.triggered_at DESC OFFSET 0 LIMIT 1"
            )
            params = [{"name": "@rid", "value": rule_id}]
        items = self._container.query_items(
            query=query,
            parameters=params,
        )
        async for item in items:
            return item
        return None
