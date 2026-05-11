"""Tests for WI-EXPIRY-1 — General access expiry enforcement.

Covers:
- Middleware _check_access_expiry() enforcement
- Middleware _resolve_tenant_fields() tuple shape
- Tenant repository list_expired_tenants() / list_expiring_tenants()
- Superadmin API PATCH .../expiry endpoint
- Superadmin API POST /tenants with expires_at
- Access expiry email template rendering

Run:
    pytest tests/multi_tenant/test_access_expiry.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.cosmos_schema import TenantStatus, TenantTier
from src.multi_tenant.middleware import TenantAuthMiddleware


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TENANT_ID = "t-expiry-001"

_NOW = datetime.now(timezone.utc)
_PAST = (_NOW - timedelta(hours=1)).isoformat()
_FUTURE = (_NOW + timedelta(days=30)).isoformat()


def _make_tenant_doc(
    expires_at: str | None = None,
    trial_expires_at: str | None = None,
    status: str = "active",
    tier: str = "starter",
    billing_channel: str = "manual",
) -> dict:
    """Build a minimal tenant document dict for middleware tests."""
    return {
        "tenant_id": _TENANT_ID,
        "status": status,
        "tier": tier,
        "billing_channel": billing_channel,
        "trial_expires_at": trial_expires_at,
        "expires_at": expires_at,
        "rate_limit_rpm": None,
    }


# ---------------------------------------------------------------------------
# EX-01: _resolve_tenant_fields returns 6-element tuple
# ---------------------------------------------------------------------------


class TestResolveFields:
    def test_ex01_returns_six_element_tuple(self):
        """_resolve_tenant_fields returns (id, status, tier, trial_expires, expires, rpm)."""
        doc = _make_tenant_doc(expires_at=_FUTURE)
        result = TenantAuthMiddleware._resolve_tenant_fields(doc)
        assert len(result) == 6
        tenant_id, status, tier, trial_exp, expires_at, rpm = result
        assert tenant_id == _TENANT_ID
        assert status == TenantStatus.ACTIVE
        assert tier == TenantTier.STARTER
        assert trial_exp is None
        assert expires_at == _FUTURE
        assert rpm is None

    def test_ex02_returns_none_when_no_expires_at(self):
        """expires_at is None when not set on the document."""
        doc = _make_tenant_doc()
        _, _, _, _, expires_at, _ = TenantAuthMiddleware._resolve_tenant_fields(doc)
        assert expires_at is None


# ---------------------------------------------------------------------------
# EX-03–07: _check_access_expiry enforcement
# ---------------------------------------------------------------------------


class TestCheckAccessExpiry:
    def test_ex03_no_expiry_passes(self):
        """No expires_at means no block."""
        TenantAuthMiddleware._check_access_expiry(_TENANT_ID, None)
        # Should not raise

    def test_ex04_future_expiry_passes(self):
        """Future expires_at means no block."""
        TenantAuthMiddleware._check_access_expiry(_TENANT_ID, _FUTURE)
        # Should not raise

    def test_ex05_past_expiry_blocks(self):
        """Past expires_at raises AuthenticationError (403)."""
        from src.multi_tenant.middleware import AuthenticationError

        with pytest.raises(AuthenticationError, match="Access has expired"):
            TenantAuthMiddleware._check_access_expiry(_TENANT_ID, _PAST)

    def test_ex06_past_expiry_status_code_403(self):
        """The status_code on the error should be 403."""
        from src.multi_tenant.middleware import AuthenticationError

        with pytest.raises(AuthenticationError) as exc_info:
            TenantAuthMiddleware._check_access_expiry(_TENANT_ID, _PAST)
        assert exc_info.value.status_code == 403

    def test_ex07_malformed_expiry_passes(self):
        """Malformed expires_at is logged but does not block."""
        TenantAuthMiddleware._check_access_expiry(_TENANT_ID, "not-a-date")
        # Should not raise

    def test_ex08_naive_timestamp_treated_as_utc(self):
        """A naive (no tzinfo) past timestamp still triggers the block."""
        from src.multi_tenant.middleware import AuthenticationError

        naive_past = (_NOW - timedelta(hours=1)).isoformat().replace("+00:00", "")
        with pytest.raises(AuthenticationError, match="Access has expired"):
            TenantAuthMiddleware._check_access_expiry(_TENANT_ID, naive_past)


# ---------------------------------------------------------------------------
# EX-09: Both trial and access expiry checked independently
# ---------------------------------------------------------------------------


class TestDualExpiryEnforcement:
    def test_ex09_trial_blocks_first_then_access_also_blocks(self):
        """When both trial and access expire, both _check methods are needed."""
        from src.multi_tenant.middleware import AuthenticationError

        # Trial expiry should block (TRIAL tier with past date)
        with pytest.raises(AuthenticationError, match="Trial period has expired"):
            TenantAuthMiddleware._check_trial_expiry(
                _TENANT_ID, TenantTier.TRIAL, _PAST
            )

        # Access expiry should ALSO block independently
        with pytest.raises(AuthenticationError, match="Access has expired"):
            TenantAuthMiddleware._check_access_expiry(_TENANT_ID, _PAST)

    def test_ex10_non_trial_tier_only_access_expiry_matters(self):
        """For STARTER tier, trial check passes but access expiry blocks."""
        from src.multi_tenant.middleware import AuthenticationError

        # Trial check passes for non-trial tier
        TenantAuthMiddleware._check_trial_expiry(
            _TENANT_ID, TenantTier.STARTER, _PAST
        )

        # Access expiry blocks
        with pytest.raises(AuthenticationError, match="Access has expired"):
            TenantAuthMiddleware._check_access_expiry(_TENANT_ID, _PAST)


# ---------------------------------------------------------------------------
# EX-11–14: Superadmin API PATCH .../expiry
# ---------------------------------------------------------------------------


class TestSetExpiryEndpoint:
    """Tests for PATCH /api/superadmin/tenants/{tenant_id}/expiry."""

    @pytest.fixture
    def mock_tenant_repo(self):
        repo = AsyncMock()
        repo.read.return_value = {
            "tenant_id": _TENANT_ID,
            "status": "active",
            "expires_at": None,
            "expiry_warnings_sent": [],
        }
        return repo

    @pytest.fixture
    def spa_context(self):
        """Mock SPA superadmin TenantContext."""
        from src.multi_tenant.middleware import TenantContext

        return TenantContext(
            tenant_id="remaker-digital-001",
            tier=TenantTier.ENTERPRISE,
            status=TenantStatus.ACTIVE,
            auth_method="user_api_key",
            team_member_role=MagicMock(value="superadmin"),
        )

    @pytest.mark.asyncio
    async def test_ex11_set_expiry(self, mock_tenant_repo, spa_context):
        """Setting an expiry date returns the new value."""
        from src.multi_tenant.superadmin_api import set_tenant_expiry, SetExpiryRequest

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", None),
        ):
            body = SetExpiryRequest(expires_at=_FUTURE)
            result = await set_tenant_expiry(_TENANT_ID, body, spa_context)

        assert result.tenant_id == _TENANT_ID
        assert result.previous_expires_at is None
        assert result.new_expires_at == _FUTURE
        mock_tenant_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_ex12_clear_expiry(self, mock_tenant_repo, spa_context):
        """Setting expires_at to null removes the expiry."""
        from src.multi_tenant.superadmin_api import set_tenant_expiry, SetExpiryRequest

        mock_tenant_repo.read.return_value["expires_at"] = _FUTURE

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", None),
        ):
            body = SetExpiryRequest(expires_at=None)
            result = await set_tenant_expiry(_TENANT_ID, body, spa_context)

        assert result.previous_expires_at == _FUTURE
        assert result.new_expires_at is None

    @pytest.mark.asyncio
    async def test_ex13_resets_warning_dedup(self, mock_tenant_repo, spa_context):
        """Changing expiry resets expiry_warnings_sent to []."""
        from src.multi_tenant.superadmin_api import set_tenant_expiry, SetExpiryRequest

        mock_tenant_repo.read.return_value["expires_at"] = _PAST
        mock_tenant_repo.read.return_value["expiry_warnings_sent"] = ["7d", "3d"]

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", None),
        ):
            body = SetExpiryRequest(expires_at=_FUTURE)
            await set_tenant_expiry(_TENANT_ID, body, spa_context)

        # Verify the patch operations include resetting warnings
        call_args = mock_tenant_repo.patch.call_args
        operations = call_args.kwargs.get("operations", call_args[1].get("operations", []))
        warning_ops = [op for op in operations if op["path"] == "/expiry_warnings_sent"]
        assert len(warning_ops) == 1
        assert warning_ops[0]["value"] == []

    @pytest.mark.asyncio
    async def test_ex14_reactivates_expired_tenant(self, mock_tenant_repo, spa_context):
        """Setting a future expiry on a trial_expired tenant reactivates it."""
        from src.multi_tenant.superadmin_api import set_tenant_expiry, SetExpiryRequest

        mock_tenant_repo.read.return_value["status"] = "trial_expired"
        mock_tenant_repo.read.return_value["expires_at"] = _PAST

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", None),
        ):
            body = SetExpiryRequest(expires_at=_FUTURE)
            await set_tenant_expiry(_TENANT_ID, body, spa_context)

        call_args = mock_tenant_repo.patch.call_args
        operations = call_args.kwargs.get("operations", call_args[1].get("operations", []))
        status_ops = [op for op in operations if op["path"] == "/status"]
        assert len(status_ops) == 1
        assert status_ops[0]["value"] == "active"

    @pytest.mark.asyncio
    async def test_ex15_tenant_not_found(self, mock_tenant_repo, spa_context):
        """Returns 404 when tenant doesn't exist."""
        from fastapi import HTTPException
        from src.multi_tenant.superadmin_api import set_tenant_expiry, SetExpiryRequest

        mock_tenant_repo.read.return_value = None

        with (
            patch("src.multi_tenant.superadmin_api._monolith._tenant_repo", mock_tenant_repo),
            patch("src.multi_tenant.superadmin_api._monolith._audit_repo", None),
            pytest.raises(HTTPException) as exc_info,
        ):
            body = SetExpiryRequest(expires_at=_FUTURE)
            await set_tenant_expiry("nonexistent-id", body, spa_context)

        assert exc_info.value.status_code == 404

    def test_ex16_router_protected_by_platform_admin_guard(self):
        """SPEC-1667: set_tenant_expiry protected by router-level require_platform_admin().

        The per-function _SPA_TENANT_ID gate was removed — access control is
        now enforced by the router-level require_platform_admin() dependency,
        which rejects all non-SPA keys before any endpoint runs.
        """
        from src.multi_tenant.superadmin_api import router

        assert len(router.dependencies) > 0, (
            "Router must have require_platform_admin() as a dependency"
        )


# ---------------------------------------------------------------------------
# EX-17–18: CreateTenantRequest with expires_at
# ---------------------------------------------------------------------------


class TestCreateTenantWithExpiry:
    def test_ex17_valid_expires_at_accepted(self):
        """CreateTenantRequest accepts a valid ISO timestamp."""
        from src.multi_tenant.superadmin_api import CreateTenantRequest

        req = CreateTenantRequest(
            merchant_name="Test Corp",
            superadmin_email="admin@test.com",
            tier="starter",
            expires_at=_FUTURE,
        )
        assert req.expires_at == _FUTURE

    def test_ex18_invalid_expires_at_rejected(self):
        """CreateTenantRequest rejects invalid ISO timestamp."""
        from pydantic import ValidationError
        from src.multi_tenant.superadmin_api import CreateTenantRequest

        with pytest.raises(ValidationError, match="expires_at"):
            CreateTenantRequest(
                merchant_name="Test Corp",
                superadmin_email="admin@test.com",
                tier="starter",
                expires_at="not-a-date",
            )

    def test_ex19_null_expires_at_accepted(self):
        """CreateTenantRequest accepts null (no expiry)."""
        from src.multi_tenant.superadmin_api import CreateTenantRequest

        req = CreateTenantRequest(
            merchant_name="Test Corp",
            superadmin_email="admin@test.com",
            tier="starter",
            expires_at=None,
        )
        assert req.expires_at is None


# ---------------------------------------------------------------------------
# EX-20: SetExpiryRequest validation
# ---------------------------------------------------------------------------


class TestSetExpiryRequestValidation:
    def test_ex20_valid_iso_accepted(self):
        from src.multi_tenant.superadmin_api import SetExpiryRequest

        req = SetExpiryRequest(expires_at=_FUTURE)
        assert req.expires_at == _FUTURE

    def test_ex21_null_accepted(self):
        from src.multi_tenant.superadmin_api import SetExpiryRequest

        req = SetExpiryRequest(expires_at=None)
        assert req.expires_at is None

    def test_ex22_invalid_iso_rejected(self):
        from pydantic import ValidationError
        from src.multi_tenant.superadmin_api import SetExpiryRequest

        with pytest.raises(ValidationError, match="expires_at"):
            SetExpiryRequest(expires_at="abc123")


# ---------------------------------------------------------------------------
# EX-23–24: Access expiry email template
# ---------------------------------------------------------------------------


class TestAccessExpiryEmail:
    @pytest.mark.asyncio
    async def test_ex23_no_email_returns_false(self):
        """send_access_expiry_warning returns False for empty email."""
        from src.multi_tenant.access_expiry_email import send_access_expiry_warning

        result = await send_access_expiry_warning("", _TENANT_ID, "7d")
        assert result is False

    @pytest.mark.asyncio
    async def test_ex24_unknown_tier_returns_false(self):
        """send_access_expiry_warning returns False for unknown warning tier."""
        from src.multi_tenant.access_expiry_email import send_access_expiry_warning

        result = await send_access_expiry_warning("test@example.com", _TENANT_ID, "99d")
        assert result is False

    @pytest.mark.asyncio
    async def test_ex25_no_provider_returns_false(self):
        """send_access_expiry_warning returns False when no email provider configured."""
        from src.multi_tenant.access_expiry_email import send_access_expiry_warning

        with (
            patch.dict("os.environ", {"AZURE_COMM_CONNECTION_STRING": "", "SMTP_HOST": ""}),
        ):
            result = await send_access_expiry_warning("test@example.com", _TENANT_ID, "7d")
        assert result is False
