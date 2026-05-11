"""Tests for SPEC-1835: Idle Tenant Detection and Auto-Downgrade.

Verifies activity coalescing, idle state classification, scan job,
and report formatting.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from src.multi_tenant.idle_tenant_detection import (
    IDLE_THRESHOLDS,
    ACTIVITY_COALESCE_SECONDS,
    AUTO_DOWNGRADE_NOTICE_DAYS,
    classify_idle_state,
    format_idle_report,
    scan_idle_tenants,
    should_update_activity,
)


class TestIdleThresholds:
    """SPEC-1835: Threshold constants."""

    def test_four_thresholds(self):
        assert len(IDLE_THRESHOLDS) == 4

    def test_thresholds_ascending(self):
        vals = list(IDLE_THRESHOLDS.values())
        assert vals == sorted(vals)

    def test_threshold_values(self):
        assert IDLE_THRESHOLDS["notification"] == 30
        assert IDLE_THRESHOLDS["downgrade_offer"] == 60
        assert IDLE_THRESHOLDS["auto_downgrade"] == 90
        assert IDLE_THRESHOLDS["archival_review"] == 180

    def test_advance_notice_7_days(self):
        assert AUTO_DOWNGRADE_NOTICE_DAYS == 7

    def test_coalesce_1_hour(self):
        assert ACTIVITY_COALESCE_SECONDS == 3600


class TestShouldUpdateActivity:
    """WI-1456: Activity timestamp coalescing."""

    def test_none_always_updates(self):
        assert should_update_activity(None) is True

    def test_recent_activity_skips(self):
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(minutes=30)).isoformat()
        assert should_update_activity(recent, now) is False

    def test_old_activity_updates(self):
        now = datetime.now(timezone.utc)
        old = (now - timedelta(hours=2)).isoformat()
        assert should_update_activity(old, now) is True

    def test_exactly_1_hour_updates(self):
        now = datetime.now(timezone.utc)
        exactly = (now - timedelta(seconds=3600)).isoformat()
        assert should_update_activity(exactly, now) is True

    def test_invalid_timestamp_updates(self):
        assert should_update_activity("not-a-date") is True


class TestClassifyIdleState:
    """SPEC-1835: Idle state classification."""

    def test_active_tenant(self):
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(days=5)).isoformat()
        assert classify_idle_state(recent, now) == "active"

    def test_notification_at_30_days(self):
        now = datetime.now(timezone.utc)
        idle_30 = (now - timedelta(days=35)).isoformat()
        assert classify_idle_state(idle_30, now) == "notification"

    def test_downgrade_offer_at_60_days(self):
        now = datetime.now(timezone.utc)
        idle_60 = (now - timedelta(days=65)).isoformat()
        assert classify_idle_state(idle_60, now) == "downgrade_offer"

    def test_auto_downgrade_at_90_days(self):
        now = datetime.now(timezone.utc)
        idle_90 = (now - timedelta(days=95)).isoformat()
        assert classify_idle_state(idle_90, now) == "auto_downgrade"

    def test_archival_at_180_days(self):
        now = datetime.now(timezone.utc)
        idle_180 = (now - timedelta(days=200)).isoformat()
        assert classify_idle_state(idle_180, now) == "archival_review"

    def test_none_activity_is_archival(self):
        assert classify_idle_state(None) == "archival_review"


class TestScanIdleTenants:
    """WI-1455: Idle tenant scan job."""

    @pytest.mark.asyncio
    async def test_scan_classifies_tenants(self):
        now = datetime.now(timezone.utc)
        mock_repo = AsyncMock()
        mock_repo.list_tenants.return_value = [
            {"tenant_id": "t-active", "last_activity_at": (now - timedelta(days=1)).isoformat(),
             "tier": "professional", "status": "active"},
            {"tenant_id": "t-idle", "last_activity_at": (now - timedelta(days=45)).isoformat(),
             "tier": "professional", "status": "active"},
            {"tenant_id": "t-old", "last_activity_at": None, "tier": "starter", "status": "active"},
        ]

        result = await scan_idle_tenants(mock_repo, now)

        assert result["scanned"] == 3
        assert result["active"] == 1
        assert result["notification"] == 1
        assert result["archival_review"] == 1

    @pytest.mark.asyncio
    async def test_scan_skips_inactive_tenants(self):
        now = datetime.now(timezone.utc)
        mock_repo = AsyncMock()
        mock_repo.list_tenants.return_value = [
            {"tenant_id": "t-cancelled", "status": "cancelled",
             "last_activity_at": None, "tier": "starter"},
        ]

        result = await scan_idle_tenants(mock_repo, now)
        assert result["scanned"] == 0


class TestFormatIdleReport:
    """WI-1457: Report formatting."""

    def test_report_structure(self):
        scan_result = {
            "scanned": 10,
            "active": 7,
            "notification": 1,
            "downgrade_offer": 1,
            "auto_downgrade": 0,
            "archival_review": 1,
        }
        report = format_idle_report(scan_result)
        assert report["scanned"] == 10
        assert "summary" in report
        assert report["summary"]["active"] == 7
        assert report["action_required"] is True  # archival_review > 0

    def test_no_action_required(self):
        scan_result = {
            "scanned": 5,
            "active": 5,
            "notification": 0,
            "downgrade_offer": 0,
            "auto_downgrade": 0,
            "archival_review": 0,
        }
        report = format_idle_report(scan_result)
        assert report["action_required"] is False
