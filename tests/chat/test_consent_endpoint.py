"""Tests for the consent collection endpoint (WI #87).

Verifies:
- Consent endpoint updates customer profile and conversation document
- Invalid consent_status returns 422
- Consent change is audit-logged
- Conversation not found returns 404

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.models import ConsentUpdateRequest, ConsentUpdateResponse


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestConsentModels:
    """Verify consent request/response models."""

    def test_consent_update_request_granted(self):
        req = ConsentUpdateRequest(consent_status="granted")
        assert req.consent_status == "granted"

    def test_consent_update_request_denied(self):
        req = ConsentUpdateRequest(consent_status="denied")
        assert req.consent_status == "denied"

    def test_consent_update_response_fields(self):
        resp = ConsentUpdateResponse(
            conversation_id="conv-001",
            consent_status="granted",
            accepted=True,
        )
        assert resp.conversation_id == "conv-001"
        assert resp.consent_status == "granted"
        assert resp.accepted is True


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


class TestConsentEndpoint:
    """Tests for POST /api/chat/conversations/{id}/consent."""

    @pytest.mark.asyncio
    async def test_consent_granted_updates_profile(self):
        """Granting consent updates customer profile consent_status."""
        from src.chat.endpoints import update_consent

        mock_state = MagicMock()
        mock_state.customer_id = "cust-001"

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=mock_state)
        mock_session._conversation_repo = MagicMock()
        mock_session._conversation_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.patch = AsyncMock()

        mock_audit_repo = MagicMock()
        mock_audit_repo.log_event = AsyncMock()

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "tenant-001"

        req = ConsentUpdateRequest(consent_status="granted")

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch(
                "src.multi_tenant.repository.CustomerProfileRepository",
                return_value=mock_profile_repo,
            ),
            patch(
                "src.multi_tenant.repository.AuditLogRepository",
                return_value=mock_audit_repo,
            ),
        ):
            resp = await update_consent("conv-001", req, mock_ctx)

        assert resp.conversation_id == "conv-001"
        assert resp.consent_status == "granted"
        assert resp.accepted is True

        # Profile was patched with consent_status
        mock_profile_repo.patch.assert_called_once()
        profile_args = mock_profile_repo.patch.call_args
        assert profile_args.kwargs["document_id"] == "profile:cust-001"
        ops = profile_args.kwargs["operations"]
        assert any(
            op["path"] == "/consent_status" and op["value"] == "granted"
            for op in ops
        )

    @pytest.mark.asyncio
    async def test_consent_denied_updates_profile(self):
        """Denying consent records denied status on profile."""
        from src.chat.endpoints import update_consent

        mock_state = MagicMock()
        mock_state.customer_id = "cust-002"

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=mock_state)
        mock_session._conversation_repo = MagicMock()
        mock_session._conversation_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.patch = AsyncMock()

        mock_audit_repo = MagicMock()
        mock_audit_repo.log_event = AsyncMock()

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "tenant-001"

        req = ConsentUpdateRequest(consent_status="denied")

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch(
                "src.multi_tenant.repository.CustomerProfileRepository",
                return_value=mock_profile_repo,
            ),
            patch(
                "src.multi_tenant.repository.AuditLogRepository",
                return_value=mock_audit_repo,
            ),
        ):
            resp = await update_consent("conv-002", req, mock_ctx)

        assert resp.consent_status == "denied"
        mock_profile_repo.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_consent_invalid_status_raises_422(self):
        """Invalid consent_status value raises 422."""
        from fastapi import HTTPException

        from src.chat.endpoints import update_consent

        mock_session = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "tenant-001"

        req = ConsentUpdateRequest(consent_status="maybe")

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            pytest.raises(HTTPException) as exc_info,
        ):
            await update_consent("conv-001", req, mock_ctx)

        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_consent_conversation_not_found_raises_404(self):
        """Non-existent conversation raises 404."""
        from fastapi import HTTPException

        from src.chat.endpoints import update_consent
        from src.chat.session import ConversationNotFoundError

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(
            side_effect=ConversationNotFoundError("conv-999", "tenant-001"),
        )

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "tenant-001"

        req = ConsentUpdateRequest(consent_status="granted")

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            pytest.raises(HTTPException) as exc_info,
        ):
            await update_consent("conv-999", req, mock_ctx)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_consent_audit_logged(self):
        """Consent change is recorded in audit log."""
        from src.chat.endpoints import update_consent

        mock_state = MagicMock()
        mock_state.customer_id = "cust-001"

        mock_session = MagicMock()
        mock_session.get_state = AsyncMock(return_value=mock_state)
        mock_session._conversation_repo = MagicMock()
        mock_session._conversation_repo.patch = AsyncMock()

        mock_profile_repo = MagicMock()
        mock_profile_repo.patch = AsyncMock()

        mock_audit_repo = MagicMock()
        mock_audit_repo.log_event = AsyncMock()

        mock_ctx = MagicMock()
        mock_ctx.tenant_id = "tenant-001"

        req = ConsentUpdateRequest(consent_status="granted")

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch(
                "src.multi_tenant.repository.CustomerProfileRepository",
                return_value=mock_profile_repo,
            ),
            patch(
                "src.multi_tenant.repository.AuditLogRepository",
                return_value=mock_audit_repo,
            ),
        ):
            await update_consent("conv-001", req, mock_ctx)

        mock_audit_repo.log_event.assert_called_once()
        audit_args = mock_audit_repo.log_event.call_args
        assert audit_args.kwargs["details"]["consent_status"] == "granted"
        assert audit_args.kwargs["details"]["source"] == "widget_banner"
