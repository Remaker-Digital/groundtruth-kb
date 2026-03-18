"""Log retention policy and archival (SPEC-1837).

Enforces configurable retention periods for audit logs, API key usage records,
and alert history. Expired records are archived to Azure Blob Storage (Cool tier)
in NDJSON format before deletion.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default retention periods (SPEC-1837)
# ---------------------------------------------------------------------------

DEFAULT_RETENTION_DAYS = {
    "audit_logs": {
        "starter": 365,
        "professional": 365,
        "enterprise": None,  # Unlimited
    },
    "api_key_usage": {
        "starter": 90,
        "professional": 90,
        "enterprise": 90,
    },
    "alert_history": {
        "starter": 180,
        "professional": 180,
        "enterprise": 180,
    },
}

# Archive file naming: {tenant_id}/{collection}/{year}/{month}/archive-{date}.ndjson.gz
ARCHIVE_PATH_TEMPLATE = "{tenant_id}/{collection}/{year}/{month}/archive-{date}.ndjson.gz"


# ---------------------------------------------------------------------------
# Retention policy
# ---------------------------------------------------------------------------


def get_retention_days(
    collection: str,
    tier: str,
    custom_overrides: dict[str, int] | None = None,
) -> int | None:
    """Get retention period in days for a collection and tier.

    Args:
        collection: One of 'audit_logs', 'api_key_usage', 'alert_history'.
        tier: Tenant tier ('starter', 'professional', 'enterprise').
        custom_overrides: Enterprise custom overrides {collection: days}.

    Returns:
        Days to retain, or None for unlimited retention.
    """
    # Enterprise custom overrides take precedence
    if custom_overrides and collection in custom_overrides:
        return custom_overrides[collection]

    tier_config = DEFAULT_RETENTION_DAYS.get(collection, {})
    return tier_config.get(tier, tier_config.get("starter", 365))


def compute_cutoff_date(
    retention_days: int | None,
    now: datetime | None = None,
) -> datetime | None:
    """Compute the cutoff date for retention.

    Records older than this date should be archived.
    Returns None if retention is unlimited.
    """
    if retention_days is None:
        return None  # Unlimited — never archive

    if now is None:
        now = datetime.now(timezone.utc)

    return now - timedelta(days=retention_days)


def build_archive_path(
    tenant_id: str,
    collection: str,
    date: datetime | None = None,
) -> str:
    """Build the archive blob path for a retention batch.

    Returns path like: tenant-001/audit_logs/2026/03/archive-2026-03-17.ndjson.gz
    """
    if date is None:
        date = datetime.now(timezone.utc)

    return ARCHIVE_PATH_TEMPLATE.format(
        tenant_id=tenant_id,
        collection=collection,
        year=date.strftime("%Y"),
        month=date.strftime("%m"),
        date=date.strftime("%Y-%m-%d"),
    )


# ---------------------------------------------------------------------------
# Retention scan
# ---------------------------------------------------------------------------


def identify_expired_records(
    records: list[dict[str, Any]],
    cutoff: datetime,
    timestamp_field: str = "created_at",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Partition records into expired and retained.

    Args:
        records: List of record dicts.
        cutoff: Records with timestamp before this are expired.
        timestamp_field: Name of the timestamp field in each record.

    Returns:
        Tuple of (expired, retained) lists.
    """
    expired: list[dict[str, Any]] = []
    retained: list[dict[str, Any]] = []

    for record in records:
        ts_str = record.get(timestamp_field)
        if ts_str is None:
            retained.append(record)
            continue

        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts < cutoff:
                expired.append(record)
            else:
                retained.append(record)
        except (ValueError, TypeError):
            retained.append(record)  # Can't parse → keep

    return expired, retained


def format_ndjson(records: list[dict[str, Any]]) -> str:
    """Format records as NDJSON (newline-delimited JSON).

    Each record is serialized on a single line.
    """
    lines = []
    for record in records:
        lines.append(json.dumps(record, default=str, separators=(",", ":")))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Retention summary
# ---------------------------------------------------------------------------


def get_retention_summary(
    tenant_id: str,
    tier: str,
    custom_overrides: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Get retention policy summary for a tenant.

    Returns dict with retention days per collection and computed cutoff dates.
    """
    now = datetime.now(timezone.utc)
    collections = {}

    for collection in DEFAULT_RETENTION_DAYS:
        days = get_retention_days(collection, tier, custom_overrides)
        cutoff = compute_cutoff_date(days, now)
        collections[collection] = {
            "retention_days": days,
            "cutoff_date": cutoff.isoformat() if cutoff else None,
            "unlimited": days is None,
        }

    return {
        "tenant_id": tenant_id,
        "tier": tier,
        "collections": collections,
        "computed_at": now.isoformat(),
    }
