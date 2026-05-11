# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Idle tenant detection and auto-downgrade (SPEC-1835).

Detects tenants with no activity and triggers notification/downgrade workflows.
Activity is tracked via last_activity_at timestamp, coalesced to 1-hour granularity.

Background job scans all tenants and classifies idle state:
  - 30 days: notification email
  - 60 days: downgrade offer
  - 90 days: auto-downgrade to Starter (with 7-day advance notice)
  - 180 days: marked for archival review

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Idle thresholds (SPEC-1835)
# ---------------------------------------------------------------------------

IDLE_THRESHOLDS = {
    "notification": 30,       # Days idle → email notification
    "downgrade_offer": 60,    # Days idle → downgrade offer email
    "auto_downgrade": 90,     # Days idle → auto-downgrade to Starter
    "archival_review": 180,   # Days idle → marked for manual archival review
}

# Advance notice period for auto-downgrade (days)
AUTO_DOWNGRADE_NOTICE_DAYS = 7

# Coalesce activity updates to this granularity (seconds)
ACTIVITY_COALESCE_SECONDS = 3600  # 1 hour


# ---------------------------------------------------------------------------
# Activity tracking (WI-1456)
# ---------------------------------------------------------------------------


def should_update_activity(
    last_activity_at: str | None,
    now: datetime | None = None,
) -> bool:
    """Check if activity timestamp should be updated (1-hour coalescing).

    Returns True if last_activity_at is None or older than ACTIVITY_COALESCE_SECONDS.
    """
    if last_activity_at is None:
        return True

    if now is None:
        now = datetime.now(UTC)

    try:
        last = datetime.fromisoformat(last_activity_at)
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        elapsed = (now - last).total_seconds()
        return elapsed >= ACTIVITY_COALESCE_SECONDS
    except (ValueError, TypeError):
        return True


def classify_idle_state(
    last_activity_at: str | None,
    now: datetime | None = None,
) -> str:
    """Classify a tenant's idle state based on last_activity_at.

    Returns one of: 'active', 'notification', 'downgrade_offer',
    'auto_downgrade', 'archival_review'.
    """
    if last_activity_at is None:
        return "archival_review"  # No activity ever recorded

    if now is None:
        now = datetime.now(UTC)

    try:
        last = datetime.fromisoformat(last_activity_at)
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        idle_days = (now - last).days
    except (ValueError, TypeError):
        return "archival_review"

    if idle_days >= IDLE_THRESHOLDS["archival_review"]:
        return "archival_review"
    elif idle_days >= IDLE_THRESHOLDS["auto_downgrade"]:
        return "auto_downgrade"
    elif idle_days >= IDLE_THRESHOLDS["downgrade_offer"]:
        return "downgrade_offer"
    elif idle_days >= IDLE_THRESHOLDS["notification"]:
        return "notification"
    else:
        return "active"


# ---------------------------------------------------------------------------
# Idle scan job (WI-1455)
# ---------------------------------------------------------------------------


async def scan_idle_tenants(
    tenant_repo: Any = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Scan all tenants and classify idle state.

    Returns summary of idle tenants by category.
    Does NOT take action — just reports. Actions are taken by separate handlers.
    """
    if now is None:
        now = datetime.now(UTC)

    if tenant_repo is None:
        try:
            from src.multi_tenant.repositories.tenant import TenantConfigRepository
            tenant_repo = TenantConfigRepository()
        except Exception:
            logger.warning("Cannot scan idle tenants: TenantConfigRepository not available")
            return {"error": "repo_unavailable", "scanned": 0}

    try:
        tenants = await tenant_repo.list_tenants()
    except Exception:
        logger.warning("Failed to list tenants for idle scan", exc_info=True)
        return {"error": "list_failed", "scanned": 0}

    results: dict[str, list[dict[str, Any]]] = {
        "active": [],
        "notification": [],
        "downgrade_offer": [],
        "auto_downgrade": [],
        "archival_review": [],
    }

    for tenant in tenants:
        tenant_id = tenant.get("tenant_id", tenant.get("id", ""))
        last_activity = tenant.get("last_activity_at")
        tier = tenant.get("tier", "starter")
        status = tenant.get("status", "active")

        # Skip already inactive tenants
        if status not in ("active", "trial"):
            continue

        state = classify_idle_state(last_activity, now)
        results[state].append({
            "tenant_id": tenant_id,
            "tier": tier,
            "last_activity_at": last_activity,
            "idle_days": _compute_idle_days(last_activity, now),
        })

    return {
        "scanned": sum(len(v) for v in results.values()),
        "active": len(results["active"]),
        "notification": len(results["notification"]),
        "downgrade_offer": len(results["downgrade_offer"]),
        "auto_downgrade": len(results["auto_downgrade"]),
        "archival_review": len(results["archival_review"]),
        "details": results,
    }


def _compute_idle_days(last_activity_at: str | None, now: datetime) -> int:
    """Compute days since last activity."""
    if last_activity_at is None:
        return 999
    try:
        last = datetime.fromisoformat(last_activity_at)
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        return (now - last).days
    except (ValueError, TypeError):
        return 999


# ---------------------------------------------------------------------------
# Idle report endpoint helper (WI-1457)
# ---------------------------------------------------------------------------


def format_idle_report(scan_result: dict[str, Any]) -> dict[str, Any]:
    """Format scan results for the superadmin API response.

    Returns a clean report with counts and top idle tenants per category.
    """
    return {
        "scanned": scan_result.get("scanned", 0),
        "summary": {
            "active": scan_result.get("active", 0),
            "notification_pending": scan_result.get("notification", 0),
            "downgrade_offer_pending": scan_result.get("downgrade_offer", 0),
            "auto_downgrade_pending": scan_result.get("auto_downgrade", 0),
            "archival_review_pending": scan_result.get("archival_review", 0),
        },
        "action_required": (
            scan_result.get("auto_downgrade", 0) > 0
            or scan_result.get("archival_review", 0) > 0
        ),
    }
