"""Tests for MFA management endpoints on the Team API (WI #295 Phase 4).

Covers:
    - MFA-M01: GET  /{member_id}/mfa/status — MFA enrollment status
    - MFA-M02: POST /{member_id}/mfa/enroll — Start MFA enrollment
    - MFA-M03: POST /{member_id}/mfa/confirm — Confirm enrollment with TOTP
    - MFA-M04: POST /{member_id}/mfa/disable — Disable MFA
    - MFA-M05: POST /{member_id}/mfa/grant-opt-out — Grant opt-out (superadmin)
    - MFA-M06: POST /{member_id}/mfa/revoke-opt-out — Revoke opt-out (superadmin)
    - MFA-M07: Non-admin cannot access other members' MFA endpoints
    - MFA-M08: TeamMemberResponse includes MFA fields
    - MFA-M09: Opt-out restricted to superadmin

Test plan reference: §5.13 (MFA Management — WI #295 Phase 4)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.auth import TenantContext
from src.multi_tenant.cosmos_schema import TeamMemberRole
from src.multi_tenant.admin_team_api import (
    _build_member_response,
    configure_admin_team_services,
    get_mfa_status,
    start_mfa_enrollment,
    confirm_mfa_enrollment,
    disable_mfa,
    grant_mfa_opt_out,
    revoke_mfa_opt_out,
    MfaEnrollConfirmRequest,
    MfaDisableRequest,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clear_services():
    """Reset service configuration between tests."""
    configure_admin_team_services(
        team_repo=None,
        audit_repo=None,
        conv_repo=None,
        mfa_totp_service=None,
    )
    yield
    configure_admin_team_services(
        team_repo=None,
        audit_repo=None,
        conv_repo=None,
        mfa_totp_service=None,
    )


def _make_ctx(
    role: TeamMemberRole | None = TeamMemberRole.ADMIN,
    member_id: str = "member-admin",
) -> TenantContext:
    return TenantContext(
        tenant_id="t-001",
        auth_method="user_api_key",
        team_member_role=role,
        team_member_id=member_id,
    )


def _admin_member_doc(**overrides):
    defaults = {
        "id": "member-admin",
        "tenant_id": "t-001",
        "email": "admin@test.com",
        "display_name": "Admin User",
        "role": "admin",
        "is_active": True,
        "mfa_enabled": True,
        "mfa_enrolled_at": "2026-01-15T00:00:00Z",
        "mfa_backup_code_hashes": ["h1", "h2", "h3"],
        "mfa_opt_out": False,
        "phone_number": "+12125551234",
        "phone_verified": True,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-15T00:00:00Z",
    }
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# MFA-M08: TeamMemberResponse MFA fields
# ---------------------------------------------------------------------------


class TestTeamMemberResponseMfaFields:
    """MFA-M08: _build_member_response includes MFA fields."""

    def test_mfa_fields_populated(self):
        doc = _admin_member_doc()
        resp = _build_member_response(doc, "t-001")
        assert resp.mfa_enabled is True
        assert resp.mfa_opt_out is False
        assert resp.mfa_enrolled_at == "2026-01-15T00:00:00Z"
        assert resp.phone_number_set is True
        assert resp.phone_verified is True

    def test_mfa_fields_default_when_absent(self):
        doc = {
            "id": "m1", "email": "a@b.com", "display_name": "A",
            "role": "viewer", "created_at": "", "updated_at": "",
        }
        resp = _build_member_response(doc, "t-001")
        assert resp.mfa_enabled is False
        assert resp.mfa_opt_out is False
        assert resp.mfa_enrolled_at is None
        assert resp.phone_number_set is False
        assert resp.phone_verified is False


# ---------------------------------------------------------------------------
# MFA-M01: GET /{member_id}/mfa/status
# ---------------------------------------------------------------------------


class TestMfaStatus:
    """MFA-M01: MFA enrollment status."""

    @pytest.mark.asyncio
    async def test_returns_status_for_own_member(self):
        doc = _admin_member_doc()
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)
        configure_admin_team_services(team_repo=repo)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        result = await get_mfa_status("member-admin", ctx)
        assert result.mfa_enabled is True
        assert result.backup_codes_remaining == 3
        assert result.phone_number_set is True

    @pytest.mark.asyncio
    async def test_non_admin_cannot_view_other_status(self):
        repo = AsyncMock()
        configure_admin_team_services(team_repo=repo)

        ctx = _make_ctx(TeamMemberRole.ESCALATION_AGENT, "member-agent")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await get_mfa_status("member-admin", ctx)
        assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# MFA-M02: POST /{member_id}/mfa/enroll
# ---------------------------------------------------------------------------


class TestMfaEnroll:
    """MFA-M02: Start MFA enrollment."""

    @pytest.mark.asyncio
    async def test_start_enrollment_returns_qr(self):
        doc = _admin_member_doc(mfa_enabled=False, mfa_enrolled_at=None)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)

        mfa = AsyncMock()
        mfa.start_enrollment = AsyncMock(return_value={
            "qr_code_data_url": "data:image/png;base64,QR...",
            "provisioning_uri": "otpauth://totp/Agent%20Red:admin@test.com?secret=X&issuer=Agent%20Red",
            "backup_codes": ["ABCD1234", "EFGH5678"],
            "backup_code_hashes": ["h1", "h2"],
        })

        configure_admin_team_services(team_repo=repo, mfa_totp_service=mfa)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        result = await start_mfa_enrollment("member-admin", ctx)
        assert result.qr_code_data_url.startswith("data:image/png")
        assert len(result.backup_codes) == 2

    @pytest.mark.asyncio
    async def test_already_enrolled_returns_400(self):
        doc = _admin_member_doc(mfa_enabled=True)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)

        configure_admin_team_services(team_repo=repo, mfa_totp_service=AsyncMock())

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await start_mfa_enrollment("member-admin", ctx)
        assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# MFA-M03: POST /{member_id}/mfa/confirm
# ---------------------------------------------------------------------------


class TestMfaConfirm:
    """MFA-M03: Confirm MFA enrollment."""

    @pytest.mark.asyncio
    async def test_confirm_with_valid_code(self):
        doc = _admin_member_doc(mfa_enabled=False)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)

        mfa = AsyncMock()
        mfa.confirm_enrollment = AsyncMock(return_value=True)

        configure_admin_team_services(team_repo=repo, audit_repo=AsyncMock(), mfa_totp_service=mfa)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        body = MfaEnrollConfirmRequest(code="123456", backup_code_hashes=["h1", "h2"])
        result = await confirm_mfa_enrollment("member-admin", body, ctx)
        assert result["status"] == "enrolled"

    @pytest.mark.asyncio
    async def test_confirm_with_invalid_code_returns_401(self):
        doc = _admin_member_doc(mfa_enabled=False)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)

        mfa = AsyncMock()
        mfa.confirm_enrollment = AsyncMock(return_value=False)

        configure_admin_team_services(team_repo=repo, mfa_totp_service=mfa)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        body = MfaEnrollConfirmRequest(code="000000", backup_code_hashes=["h1"])
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await confirm_mfa_enrollment("member-admin", body, ctx)
        assert exc.value.status_code == 401


# ---------------------------------------------------------------------------
# MFA-M04: POST /{member_id}/mfa/disable
# ---------------------------------------------------------------------------


class TestMfaDisable:
    """MFA-M04: Disable MFA."""

    @pytest.mark.asyncio
    async def test_disable_with_valid_code(self):
        doc = _admin_member_doc(mfa_enabled=True)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)

        mfa = AsyncMock()
        mfa.disable_mfa = AsyncMock(return_value=True)

        configure_admin_team_services(team_repo=repo, audit_repo=AsyncMock(), mfa_totp_service=mfa)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        body = MfaDisableRequest(code="123456")
        result = await disable_mfa("member-admin", body, ctx)
        assert result["status"] == "disabled"

    @pytest.mark.asyncio
    async def test_disable_not_enrolled_returns_400(self):
        doc = _admin_member_doc(mfa_enabled=False)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)

        configure_admin_team_services(team_repo=repo, mfa_totp_service=AsyncMock())

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        body = MfaDisableRequest(code="123456")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await disable_mfa("member-admin", body, ctx)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_non_owner_cannot_disable_others(self):
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=_admin_member_doc())

        configure_admin_team_services(team_repo=repo, mfa_totp_service=AsyncMock())

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-other")
        body = MfaDisableRequest(code="123456")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await disable_mfa("member-admin", body, ctx)
        assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# MFA-M05 / MFA-M06: Opt-out grant/revoke (superadmin only)
# ---------------------------------------------------------------------------


class TestMfaOptOut:
    """MFA-M05/M06: Opt-out management."""

    @pytest.mark.asyncio
    async def test_superadmin_can_grant_opt_out(self):
        doc = _admin_member_doc()
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)
        repo.patch = AsyncMock()

        configure_admin_team_services(team_repo=repo, audit_repo=AsyncMock())

        ctx = _make_ctx(TeamMemberRole.SUPERADMIN, "member-super")
        result = await grant_mfa_opt_out("member-admin", ctx)
        assert result["status"] == "opt_out_granted"
        repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_admin_cannot_grant_opt_out(self):
        repo = AsyncMock()
        configure_admin_team_services(team_repo=repo)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await grant_mfa_opt_out("member-admin", ctx)
        assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_superadmin_can_revoke_opt_out(self):
        doc = _admin_member_doc(mfa_opt_out=True)
        repo = AsyncMock()
        repo.read = AsyncMock(return_value=doc)
        repo.patch = AsyncMock()

        configure_admin_team_services(team_repo=repo, audit_repo=AsyncMock())

        ctx = _make_ctx(TeamMemberRole.SUPERADMIN, "member-super")
        result = await revoke_mfa_opt_out("member-admin", ctx)
        assert result["status"] == "opt_out_revoked"

    @pytest.mark.asyncio
    async def test_admin_cannot_revoke_opt_out(self):
        repo = AsyncMock()
        configure_admin_team_services(team_repo=repo)

        ctx = _make_ctx(TeamMemberRole.ADMIN, "member-admin")
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await revoke_mfa_opt_out("member-admin", ctx)
        assert exc.value.status_code == 403
