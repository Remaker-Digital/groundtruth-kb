"""
SLA snapshot repository — persistence for hourly/daily SLA snapshots.

Part of C-2: SLA persistence. Stores aggregated latency, uptime, and
per-tenant metrics to survive container restarts and enable trend analysis.

Collection: sla_snapshots (partition key: /snapshot_type)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.multi_tenant.cosmos_client import get_cosmos_manager
from src.multi_tenant.cosmos_schema import COLLECTION_SLA_SNAPSHOTS

logger = logging.getLogger(__name__)

SNAPSHOT_TYPE_HOURLY = "hourly"
SNAPSHOT_TYPE_DAILY = "daily"


class SLASnapshotRepository:
    """Repository for the sla_snapshots collection.

    Platform-scoped (not tenant-scoped). Partition key is snapshot_type
    with values "hourly" and "daily".
    """

    def __init__(self) -> None:
        self._collection_name = COLLECTION_SLA_SNAPSHOTS

    @property
    def _container(self) -> Any:
        return get_cosmos_manager().get_container(self._collection_name)

    async def save_hourly_snapshot(
        self,
        timestamp: datetime,
        period_start: datetime,
        period_end: datetime,
        platform_metrics: dict[str, Any],
        per_tenant: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Persist an hourly SLA snapshot.

        Args:
            timestamp: When the snapshot was taken.
            period_start: Start of the measurement window.
            period_end: End of the measurement window.
            platform_metrics: Platform-wide latency/uptime aggregates.
            per_tenant: Per-tenant latency aggregates keyed by tenant_id.

        Returns:
            The created document.
        """
        ts_str = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        doc = {
            "id": f"hourly-{ts_str}",
            "snapshot_type": SNAPSHOT_TYPE_HOURLY,
            "timestamp": ts_str,
            "period_start": period_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "period_end": period_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "platform": platform_metrics,
            "per_tenant": per_tenant,
        }
        return await self._container.upsert_item(body=doc)

    async def save_daily_rollup(
        self,
        date: str,
        platform_metrics: dict[str, Any],
        per_tenant: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Persist a daily SLA rollup computed from hourly snapshots.

        Args:
            date: Date string in YYYY-MM-DD format.
            platform_metrics: Aggregated platform metrics for the day.
            per_tenant: Aggregated per-tenant metrics for the day.

        Returns:
            The created document.
        """
        doc = {
            "id": f"daily-{date}",
            "snapshot_type": SNAPSHOT_TYPE_DAILY,
            "timestamp": f"{date}T00:00:00Z",
            "date": date,
            "platform": platform_metrics,
            "per_tenant": per_tenant,
        }
        return await self._container.upsert_item(body=doc)

    async def get_recent_hourly(
        self,
        hours: int = 24,
    ) -> list[dict[str, Any]]:
        """Fetch the most recent hourly snapshots.

        Args:
            hours: Number of most recent hourly snapshots to return.

        Returns:
            List of snapshot documents, newest first.
        """
        items: list[dict[str, Any]] = []
        query = (
            "SELECT * FROM c "
            "WHERE c.snapshot_type = @type "
            "ORDER BY c.timestamp DESC"
        )
        params = [{"name": "@type", "value": SNAPSHOT_TYPE_HOURLY}]
        async for item in self._container.query_items(
            query=query,
            parameters=params,
            partition_key=SNAPSHOT_TYPE_HOURLY,
            max_item_count=hours,
        ):
            items.append(item)
            if len(items) >= hours:
                break
        return items

    async def get_recent_daily(
        self,
        days: int = 90,
    ) -> list[dict[str, Any]]:
        """Fetch the most recent daily rollup snapshots.

        Args:
            days: Number of most recent daily rollups to return.

        Returns:
            List of rollup documents, newest first.
        """
        items: list[dict[str, Any]] = []
        query = (
            "SELECT * FROM c "
            "WHERE c.snapshot_type = @type "
            "ORDER BY c.timestamp DESC"
        )
        params = [{"name": "@type", "value": SNAPSHOT_TYPE_DAILY}]
        async for item in self._container.query_items(
            query=query,
            parameters=params,
            partition_key=SNAPSHOT_TYPE_DAILY,
            max_item_count=days,
        ):
            items.append(item)
            if len(items) >= days:
                break
        return items

    async def get_hourly_for_date(
        self,
        date: str,
    ) -> list[dict[str, Any]]:
        """Fetch all hourly snapshots for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format.

        Returns:
            List of hourly snapshot documents for that date, oldest first.
        """
        items: list[dict[str, Any]] = []
        start = f"{date}T00:00:00Z"
        end = f"{date}T23:59:59Z"
        query = (
            "SELECT * FROM c "
            "WHERE c.snapshot_type = @type "
            "AND c.timestamp >= @start "
            "AND c.timestamp <= @end "
            "ORDER BY c.timestamp ASC"
        )
        params = [
            {"name": "@type", "value": SNAPSHOT_TYPE_HOURLY},
            {"name": "@start", "value": start},
            {"name": "@end", "value": end},
        ]
        async for item in self._container.query_items(
            query=query,
            parameters=params,
            partition_key=SNAPSHOT_TYPE_HOURLY,
        ):
            items.append(item)
        return items
