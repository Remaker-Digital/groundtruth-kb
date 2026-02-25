"""Tests for WI-E3: Trial expiry warning emails.

Verifies:
    - Email template renders correctly for each warning tier (7d, 3d, 1d)
    - send_trial_expiry_warning() sends via ACS and handles failures
    - Background warning loop sends emails for expiring tenants
    - Deduplication via trial_warnings_sent field
    - Skips tenants without email addresses
    - Invalid warning tier returns False

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.trial_expiry_email import (
    _EXPIRY_WARNING_BODY,
    _URGENCY_CONFIG,
    send_trial_expiry_warning,
)


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------


class TestExpiryWarningTemplate:
    """Verify the HTML body template renders for each urgency tier."""

    @pytest.mark.parametrize("tier", ["7d", "3d", "1d"])
    def test_template_renders_for_tier(self, tier):
        config = _URGENCY_CONFIG[tier]
        days_label = {"7d": "7 days", "3d": "3 days", "1d": "1 day"}[tier]
        rendered = _EXPIRY_WARNING_BODY.format(
            urgency_intro=config["urgency_intro"],
            urgency_message=config["urgency_message"],
            days_remaining=days_label,
            badge_bg=config["badge_bg"],
            badge_border=config["badge_border"],
            badge_color=config["badge_color"],
            tenant_id="t-test",
            admin_login_url="https://example.com/admin/standalone/",
        )
        assert days_label in rendered
        assert config["urgency_intro"] in rendered
        assert "Sign in to Dashboard" in rendered
        assert "t-test" in rendered


# ---------------------------------------------------------------------------
# send_trial_expiry_warning()
# ---------------------------------------------------------------------------


class TestSendTrialExpiryWarning:
    """Tests for the send function."""

    @pytest.mark.asyncio
    async def test_returns_false_for_empty_email(self):
        result = await send_trial_expiry_warning("", "t-001", "7d")
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_for_invalid_tier(self):
        result = await send_trial_expiry_warning("a@b.com", "t-001", "99d")
        assert result is False

    @pytest.mark.asyncio
    async def test_acs_success(self):
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.status = "Succeeded"
        mock_poller.result.return_value = mock_result

        mock_client = MagicMock()
        mock_client.begin_send.return_value = mock_poller

        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.return_value = mock_client
            result = await send_trial_expiry_warning(
                "merchant@example.com", "t-acs", "3d",
            )

        assert result is True
        msg = mock_client.begin_send.call_args[0][0]
        assert "3 days" in msg["content"]["subject"]

    @pytest.mark.asyncio
    async def test_acs_failure_returns_false(self):
        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "endpoint=test;key=test"}),
            patch("azure.communication.email.EmailClient") as mock_cls,
        ):
            mock_cls.from_connection_string.side_effect = Exception("ACS down")
            result = await send_trial_expiry_warning(
                "merchant@example.com", "t-fail", "1d",
            )
        assert result is False

    @pytest.mark.asyncio
    async def test_no_provider_returns_false(self):
        with patch.dict("os.environ", {}, clear=True):
            result = await send_trial_expiry_warning(
                "merchant@example.com", "t-none", "7d",
            )
        assert result is False


# ---------------------------------------------------------------------------
# Background warning loop
# ---------------------------------------------------------------------------


class TestTrialWarningLoop:
    """Tests for _trial_warning_loop logic."""

    @pytest.mark.asyncio
    async def test_sends_warning_and_patches_sent_marker(self):
        """Warning loop sends email and records the tier in trial_warnings_sent."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        # Create a trial tenant expiring in 2 days (should trigger 3d warning)
        expiry = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        await fake_repo.upsert("t-warn", {
            "id": "t-warn",
            "tenant_id": "t-warn",
            "status": "active",
            "billing_channel": "trial",
            "trial_expires_at": expiry,
            "customer_email": "trial@example.com",
            "trial_warnings_sent": [],
        })

        # Mock list_expiring_trials to return our tenant for 3d and 7d tiers
        async def mock_list_expiring(within_iso):
            # Parse the within_iso to determine which tier this query is for
            within_dt = datetime.fromisoformat(within_iso)
            now = datetime.now(timezone.utc)
            days_ahead = (within_dt - now).days
            # Our tenant expires in 2 days, so it should show for 3d and 7d
            if days_ahead >= 2:
                return [await fake_repo.read("t-warn", "t-warn")]
            return []

        fake_repo.list_expiring_trials = mock_list_expiring

        with (
            patch(
                "src.multi_tenant.repository.TenantRepository",
                return_value=fake_repo,
            ),
            patch(
                "src.multi_tenant.trial_expiry_email.send_trial_expiry_warning",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_send,
            patch("src.app.background._WARNING_SCAN_STARTUP_DELAY", 0),
            patch("src.app.background._WARNING_SCAN_INTERVAL", 0),
        ):
            from src.app.background import _trial_warning_loop

            # Run one iteration by cancelling after first sleep
            task = asyncio.create_task(_trial_warning_loop())
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Should have sent the 7d warning (7 days window captures 2-day-out tenant)
        assert mock_send.call_count >= 1
        first_call = mock_send.call_args_list[0]
        assert first_call[1]["to_email"] == "trial@example.com"
        assert first_call[1]["warning_tier"] == "7d"

        # Verify sent marker was patched
        doc = await fake_repo.read("t-warn", "t-warn")
        assert "7d" in doc.get("trial_warnings_sent", [])

    @pytest.mark.asyncio
    async def test_skips_already_sent_warning(self):
        """Warning loop skips tenants that already received the warning."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        expiry = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        await fake_repo.upsert("t-skip", {
            "id": "t-skip",
            "tenant_id": "t-skip",
            "status": "active",
            "billing_channel": "trial",
            "trial_expires_at": expiry,
            "customer_email": "skip@example.com",
            "trial_warnings_sent": ["7d", "3d"],  # Both already sent
        })

        async def mock_list_expiring(within_iso):
            return [await fake_repo.read("t-skip", "t-skip")]

        fake_repo.list_expiring_trials = mock_list_expiring

        with (
            patch(
                "src.multi_tenant.repository.TenantRepository",
                return_value=fake_repo,
            ),
            patch(
                "src.multi_tenant.trial_expiry_email.send_trial_expiry_warning",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_send,
            patch("src.app.background._WARNING_SCAN_STARTUP_DELAY", 0),
            patch("src.app.background._WARNING_SCAN_INTERVAL", 0),
        ):
            from src.app.background import _trial_warning_loop

            task = asyncio.create_task(_trial_warning_loop())
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Should only send the 1d warning (7d and 3d already sent)
        for call in mock_send.call_args_list:
            assert call[1]["warning_tier"] not in ("7d", "3d")

    @pytest.mark.asyncio
    async def test_skips_tenant_without_email(self):
        """Warning loop skips tenants that have no customer_email."""
        from tests.helpers.fake_tenant_repo import FakeTenantRepo

        fake_repo = FakeTenantRepo()
        expiry = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
        await fake_repo.upsert("t-noemail", {
            "id": "t-noemail",
            "tenant_id": "t-noemail",
            "status": "active",
            "billing_channel": "trial",
            "trial_expires_at": expiry,
            "customer_email": None,
            "trial_warnings_sent": [],
        })

        async def mock_list_expiring(within_iso):
            return [await fake_repo.read("t-noemail", "t-noemail")]

        fake_repo.list_expiring_trials = mock_list_expiring

        with (
            patch(
                "src.multi_tenant.repository.TenantRepository",
                return_value=fake_repo,
            ),
            patch(
                "src.multi_tenant.trial_expiry_email.send_trial_expiry_warning",
                new_callable=AsyncMock,
            ) as mock_send,
            patch("src.app.background._WARNING_SCAN_STARTUP_DELAY", 0),
            patch("src.app.background._WARNING_SCAN_INTERVAL", 0),
        ):
            from src.app.background import _trial_warning_loop

            task = asyncio.create_task(_trial_warning_loop())
            await asyncio.sleep(0.1)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        mock_send.assert_not_called()
