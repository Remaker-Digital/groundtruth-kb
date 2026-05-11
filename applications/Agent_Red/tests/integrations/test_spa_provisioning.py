"""Tests for SPA Console tenant provisioning orchestrator.

Covers:
    spa_provision_tenant() — 7 tests
    - Happy path (all 4 steps succeed)
    - Partial failure: superadmin provisioning fails
    - Partial failure: widget key fails
    - Complete failure: provision_tenant raises RuntimeError
    - Welcome email invoked when email provided
    - Welcome email failure appended to errors (never fail silently)
    - BillingChannel.MANUAL passed to provision_tenant

Run:
    pytest tests/integrations/test_spa_provisioning.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.integrations.provisioning import (
    BillingChannel,
    SpaProvisionResult,
    TenantRecord,
    TenantStatus,
    configure_provisioning_repo,
    spa_provision_tenant,
)
from tests.helpers.fake_tenant_repo import FakeTenantRepo


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def fake_tenant_repo():
    """Wire a FakeTenantRepo into the provisioning module for each test."""
    repo = FakeTenantRepo()
    team_repo = MagicMock()
    team_repo.create = AsyncMock()
    configure_provisioning_repo(repo, team_repo=team_repo)
    yield repo
    configure_provisioning_repo(None, team_repo=None)


def _make_tenant_record(**overrides) -> TenantRecord:
    """Create a TenantRecord with sensible defaults."""
    defaults = {
        "tenant_id": "spa-test-001",
        "status": TenantStatus.PROVISIONING,
        "billing_channel": BillingChannel.MANUAL,
        "tier": "starter",
        "customer_email": "test@example.com",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    defaults.update(overrides)
    return TenantRecord(**defaults)


# ===========================================================================
# Tests
# ===========================================================================


class TestSpaProvisionTenant:
    """SPA Console provisioning orchestrator tests."""

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.auto_provision_widget_key", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.auto_provision_superadmin", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.activate_tenant", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    async def test_happy_path_all_steps_succeed(
        self, mock_email, mock_provision, mock_activate, mock_superadmin, mock_widget,
    ):
        """All 4 provisioning steps + welcome email succeed."""
        mock_provision.return_value = _make_tenant_record()
        mock_activate.return_value = _make_tenant_record(status=TenantStatus.ACTIVE)
        mock_superadmin.return_value = "ar_user_test_abc123"
        mock_widget.return_value = "pk_live_abc_def"

        result = await spa_provision_tenant(
            merchant_name="Test Store",
            merchant_url="https://test.example.com",
            superadmin_email="admin@test.com",
            tier="starter",
        )

        assert isinstance(result, SpaProvisionResult)
        assert result.tenant_id == "spa-test-001"
        assert result.status == "active"
        assert result.tier == "starter"
        assert result.superadmin_email == "admin@test.com"
        assert result.superadmin_api_key == "ar_user_test_abc123"
        assert result.widget_key == "pk_live_abc_def"
        assert result.errors == []

        mock_provision.assert_called_once()
        mock_activate.assert_called_once()
        mock_superadmin.assert_called_once()
        mock_widget.assert_called_once()
        mock_email.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.auto_provision_widget_key", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.auto_provision_superadmin", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.activate_tenant", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    async def test_partial_failure_superadmin_fails(
        self, mock_email, mock_provision, mock_activate, mock_superadmin, mock_widget,
    ):
        """Superadmin provisioning fails — tenant+widget still created."""
        mock_provision.return_value = _make_tenant_record()
        mock_activate.return_value = _make_tenant_record(status=TenantStatus.ACTIVE)
        mock_superadmin.side_effect = Exception("Key generation failed")
        mock_widget.return_value = "pk_live_abc_def"

        result = await spa_provision_tenant(
            merchant_name="Test Store",
            merchant_url=None,
            superadmin_email="admin@test.com",
            tier="starter",
        )

        assert result.tenant_id == "spa-test-001"
        assert result.superadmin_api_key is None
        assert result.widget_key == "pk_live_abc_def"
        assert len(result.errors) == 1
        assert "Superadmin" in result.errors[0] or "superadmin" in result.errors[0].lower()

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.auto_provision_widget_key", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.auto_provision_superadmin", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.activate_tenant", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    async def test_partial_failure_widget_key_fails(
        self, mock_email, mock_provision, mock_activate, mock_superadmin, mock_widget,
    ):
        """Widget key generation fails — tenant+superadmin still created."""
        mock_provision.return_value = _make_tenant_record()
        mock_activate.return_value = _make_tenant_record(status=TenantStatus.ACTIVE)
        mock_superadmin.return_value = "ar_user_test_abc123"
        mock_widget.side_effect = Exception("Widget key generation failed")

        result = await spa_provision_tenant(
            merchant_name="Test Store",
            merchant_url=None,
            superadmin_email="admin@test.com",
            tier="starter",
        )

        assert result.tenant_id == "spa-test-001"
        assert result.superadmin_api_key == "ar_user_test_abc123"
        assert result.widget_key is None
        assert len(result.errors) == 1
        assert "widget" in result.errors[0].lower() or "Widget" in result.errors[0]

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    async def test_complete_failure_provision_raises(self, mock_provision):
        """provision_tenant raises RuntimeError — propagated to caller."""
        mock_provision.side_effect = RuntimeError("Cosmos DB unavailable")

        with pytest.raises(RuntimeError, match="Cosmos DB unavailable"):
            await spa_provision_tenant(
                merchant_name="Test Store",
                merchant_url=None,
                superadmin_email="admin@test.com",
                tier="starter",
            )

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.auto_provision_widget_key", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.auto_provision_superadmin", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.activate_tenant", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    async def test_welcome_email_called_with_email(
        self, mock_email, mock_provision, mock_activate, mock_superadmin, mock_widget,
    ):
        """Welcome email is sent when superadmin_email is provided."""
        mock_provision.return_value = _make_tenant_record()
        mock_activate.return_value = _make_tenant_record(status=TenantStatus.ACTIVE)
        mock_superadmin.return_value = "ar_user_test_abc123"
        mock_widget.return_value = "pk_live_abc_def"

        await spa_provision_tenant(
            merchant_name="Test Store",
            merchant_url="https://test.com",
            superadmin_email="admin@test.com",
            tier="professional",
        )

        mock_email.assert_called_once()
        # Verify email was passed to welcome email function
        call_args = mock_email.call_args
        assert "admin@test.com" in str(call_args)

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.auto_provision_widget_key", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.auto_provision_superadmin", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.activate_tenant", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    async def test_welcome_email_failure_appended_to_errors(
        self, mock_email, mock_provision, mock_activate, mock_superadmin, mock_widget,
    ):
        """Welcome email failure is captured in errors — never fails silently."""
        mock_provision.return_value = _make_tenant_record()
        mock_activate.return_value = _make_tenant_record(status=TenantStatus.ACTIVE)
        mock_superadmin.return_value = "ar_user_test_abc123"
        mock_widget.return_value = "pk_live_abc_def"
        mock_email.side_effect = Exception("SMTP connection refused")

        result = await spa_provision_tenant(
            merchant_name="Test Store",
            merchant_url=None,
            superadmin_email="admin@test.com",
            tier="starter",
        )

        # Tenant is still created, but the email failure is visible
        assert result.tenant_id == "spa-test-001"
        assert result.superadmin_api_key == "ar_user_test_abc123"
        assert any("Welcome email failed" in e for e in result.errors)

    @pytest.mark.asyncio
    @patch("src.integrations.provisioning.auto_provision_widget_key", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.auto_provision_superadmin", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.activate_tenant", new_callable=AsyncMock)
    @patch("src.integrations.provisioning.provision_tenant", new_callable=AsyncMock)
    @patch("src.multi_tenant.welcome_email.send_welcome_email", new_callable=AsyncMock)
    async def test_billing_channel_manual_used(
        self, mock_email, mock_provision, mock_activate, mock_superadmin, mock_widget,
    ):
        """spa_provision_tenant uses BillingChannel.MANUAL for SPA provisioning."""
        mock_provision.return_value = _make_tenant_record()
        mock_activate.return_value = _make_tenant_record(status=TenantStatus.ACTIVE)
        mock_superadmin.return_value = "ar_user_test_abc123"
        mock_widget.return_value = "pk_live_abc_def"

        await spa_provision_tenant(
            merchant_name="Test Store",
            merchant_url=None,
            superadmin_email="admin@test.com",
            tier="starter",
        )

        # Verify that provision_tenant was called with MANUAL billing channel
        call_kwargs = mock_provision.call_args
        assert "manual" in str(call_kwargs).lower() or "MANUAL" in str(call_kwargs)
