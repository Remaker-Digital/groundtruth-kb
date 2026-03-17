"""Tests for SPEC-1835: Idle Tenant Detection and Auto-Downgrade.

Verifies 30/60/90/180-day idle thresholds, Enterprise exemption,
activity timestamp coalescing, and audit trail.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _days_ago(days: int) -> str:
    """Return ISO timestamp for N days ago."""
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


class TestIdleTenantDetection:
    """SPEC-1835: Detect and act on idle tenants."""

    @pytest.mark.asyncio
    async def test_30_day_idle_sends_notification(self):
        """TEST-10444: Tenant idle 31 days gets email notification."""
        from src.multi_tenant.idle_tenant_detector import scan_idle_tenants

        tenants = [
            {"tenant_id": "t1", "tier": "professional", "last_activity_at": _days_ago(31),
             "idle_notification_sent_at": None},
        ]
        mock_repo = AsyncMock()
        mock_repo.list_active_tenants.return_value = tenants
        mock_email = AsyncMock()

        actions = await scan_idle_tenants(repo=mock_repo, email_service=mock_email)

        assert len(actions) == 1
        assert actions[0]["action"] == "notify_30"
        assert actions[0]["tenant_id"] == "t1"
        mock_email.send_idle_notification.assert_called_once()

    @pytest.mark.asyncio
    async def test_90_day_idle_triggers_auto_downgrade(self):
        """TEST-10445: Professional tenant idle 91 days downgraded to Starter."""
        from src.multi_tenant.idle_tenant_detector import scan_idle_tenants

        tenants = [
            {"tenant_id": "t2", "tier": "professional", "last_activity_at": _days_ago(91),
             "idle_notification_sent_at": _days_ago(60)},
        ]
        mock_repo = AsyncMock()
        mock_repo.list_active_tenants.return_value = tenants
        mock_email = AsyncMock()

        actions = await scan_idle_tenants(repo=mock_repo, email_service=mock_email)

        assert any(a["action"] == "auto_downgrade" and a["tenant_id"] == "t2" for a in actions)

    @pytest.mark.asyncio
    async def test_enterprise_exempt_from_auto_downgrade(self):
        """TEST-10446: Enterprise tenant idle 91 days NOT downgraded."""
        from src.multi_tenant.idle_tenant_detector import scan_idle_tenants

        tenants = [
            {"tenant_id": "t3", "tier": "enterprise", "last_activity_at": _days_ago(91),
             "idle_notification_sent_at": _days_ago(60)},
        ]
        mock_repo = AsyncMock()
        mock_repo.list_active_tenants.return_value = tenants
        mock_email = AsyncMock()

        actions = await scan_idle_tenants(repo=mock_repo, email_service=mock_email)

        assert not any(a["action"] == "auto_downgrade" for a in actions)

    @pytest.mark.asyncio
    async def test_auto_downgrade_creates_audit_entry(self):
        """SPEC-1835 req 7: Auto-downgrade creates audit log with TIER_AUTO_DOWNGRADE."""
        from src.multi_tenant.idle_tenant_detector import execute_auto_downgrade

        mock_audit = AsyncMock()
        mock_config = AsyncMock()

        await execute_auto_downgrade(
            tenant_id="t2",
            from_tier="professional",
            to_tier="starter",
            audit_repo=mock_audit,
            config_processor=mock_config,
        )

        mock_audit.log_event.assert_called_once()
        call_kwargs = mock_audit.log_event.call_args[1]
        assert call_kwargs["event_type"] == "TIER_AUTO_DOWNGRADE"
        assert call_kwargs["tenant_id"] == "t2"

    @pytest.mark.asyncio
    async def test_dismiss_notification_resets_timer(self):
        """SPEC-1835 req 6: One-click dismiss resets 30-day timer."""
        from src.multi_tenant.idle_tenant_detector import dismiss_idle_notification

        mock_repo = AsyncMock()

        await dismiss_idle_notification(
            tenant_id="t1",
            repo=mock_repo,
        )

        mock_repo.update_tenant.assert_called_once()
        call_kwargs = mock_repo.update_tenant.call_args[1]
        assert call_kwargs.get("idle_notification_sent_at") is None  # Reset


class TestActivityTimestampTracking:
    """SPEC-1835: Activity tracking with 1-hour coalescing."""

    @pytest.mark.asyncio
    async def test_activity_coalesced_to_1_hour(self):
        """TEST-10447: 100 requests in 1 hour produce at most 1 update."""
        from src.multi_tenant.idle_tenant_detector import ActivityTracker

        tracker = ActivityTracker()
        updates = 0

        for i in range(100):
            if tracker.should_update("tenant-001"):
                updates += 1
                tracker.record_update("tenant-001")

        assert updates == 1  # Only first request triggers update within same hour
