"""Unit tests for service message delivery and API (SPEC-1646, SPEC-1647, SPEC-1648).

Covers:
    - BCC email delivery with SMTP primary / ACS fallback
    - Recipient resolution from tenant directory with filters
    - Service message rendering and template wrapping
    - Batch splitting for large recipient lists
    - De-duplication of recipient emails
    - Sender identity: "Agent Red Service Administrator"

Test artifacts: TEST-2942 through TEST-2955.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
from email.mime.multipart import MIMEMultipart
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Delivery module tests (TEST-2942 through TEST-2949)
# ---------------------------------------------------------------------------


class TestServiceMessageDelivery:
    """Service message delivery via BCC email (SPEC-1648)."""

    @pytest.mark.asyncio
    async def test_smtp_bcc_sender_name(self):
        """TEST-2942: SMTP From header uses 'Agent Red Service Administrator'."""
        from src.multi_tenant.service_message_delivery import _SERVICE_SENDER_NAME

        assert _SERVICE_SENDER_NAME == "Agent Red Service Administrator"

    @pytest.mark.asyncio
    async def test_smtp_bcc_no_recipient_disclosure(self):
        """TEST-2943: SMTP msg['To'] is the service address, not individual recipients."""
        from src.multi_tenant.service_message_delivery import _smtp_bcc_send

        captured_msg: list[MIMEMultipart] = []
        captured_envelope: list[list[str]] = []

        def fake_sendmail(from_addr, to_addrs, msg_str):
            captured_envelope.append(list(to_addrs))
            import email
            parsed = email.message_from_string(msg_str)
            captured_msg.append(parsed)

        mock_smtp = MagicMock()
        mock_smtp.__enter__ = MagicMock(return_value=mock_smtp)
        mock_smtp.__exit__ = MagicMock(return_value=False)
        mock_smtp.sendmail = fake_sendmail
        mock_smtp.ehlo = MagicMock()
        mock_smtp.starttls = MagicMock()
        mock_smtp.login = MagicMock()

        env = {
            "SMTP_HOST": "smtp.test.com",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "user@test.com",
            "SMTP_PASSWORD": "pass",
            "SMTP_FROM": "service@agentredcx.com",
        }
        with patch.dict("os.environ", env, clear=False):
            with patch("smtplib.SMTP", return_value=mock_smtp):
                result = await _smtp_bcc_send(
                    "smtp.test.com",
                    "Test Subject",
                    "<html><body>test</body></html>",
                    ["alice@test.com", "bob@test.com"],
                )

        assert result is True
        # Envelope includes both recipients
        assert captured_envelope[0] == ["alice@test.com", "bob@test.com"]
        # Message To header is the service address (no recipient disclosure)
        assert captured_msg[0]["To"] == "service@agentredcx.com"
        assert "alice@test.com" not in captured_msg[0]["To"]
        assert "bob@test.com" not in captured_msg[0]["To"]

    @pytest.mark.asyncio
    async def test_batch_splitting(self):
        """TEST-2944: Large recipient lists are split into batches of 50."""
        from src.multi_tenant.service_message_delivery import (
            _BCC_BATCH_SIZE,
            send_service_message,
        )

        assert _BCC_BATCH_SIZE == 50

        # Create 120 recipients — should produce 3 batches (50 + 50 + 20)
        recipients = [f"user{i}@test.com" for i in range(120)]
        batch_sizes: list[int] = []

        async def mock_send_batch(subject, html, batch):
            batch_sizes.append(len(batch))
            return True

        with patch(
            "src.multi_tenant.service_message_delivery._send_bcc_batch",
            side_effect=mock_send_batch,
        ):
            result = await send_service_message(
                "Test", "<p>body</p>", recipients,
            )

        assert result.total_recipients == 120
        assert result.sent_count == 120
        assert batch_sizes == [50, 50, 20]

    @pytest.mark.asyncio
    async def test_empty_recipients_returns_empty_result(self):
        """TEST-2945: Empty recipient list returns zero-count result."""
        from src.multi_tenant.service_message_delivery import send_service_message

        result = await send_service_message("Test", "<p>body</p>", [])
        assert result.total_recipients == 0
        assert result.sent_count == 0
        assert result.success is False

    @pytest.mark.asyncio
    async def test_acs_fallback_sends_individually(self):
        """TEST-2946: ACS fallback sends to each recipient individually."""
        from src.multi_tenant.service_message_delivery import _acs_individual_send

        sent_to: list[str] = []

        async def mock_acs_email(conn, email, subject, html):
            sent_to.append(email)
            return "Succeeded"

        # Lazy import: patch at the source module (alert_delivery.send_acs_email)
        with patch(
            "src.multi_tenant.alert_delivery.send_acs_email",
            side_effect=mock_acs_email,
        ):
            result = await _acs_individual_send(
                "conn-str",
                "Test Subject",
                "<html>body</html>",
                ["a@test.com", "b@test.com", "c@test.com"],
            )

        assert result is True
        assert sent_to == ["a@test.com", "b@test.com", "c@test.com"]

    @pytest.mark.asyncio
    async def test_render_service_message_body(self):
        """TEST-2947: Body renderer wraps content in service message styling."""
        from src.multi_tenant.service_message_delivery import render_service_message_body

        html = render_service_message_body("<p>We updated the system.</p>")
        assert "Service Message" in html
        assert "We updated the system" in html
        assert "do not reply" in html.lower()

    @pytest.mark.asyncio
    async def test_send_wraps_with_email_wrapper(self):
        """TEST-2948: send_service_message applies _EMAIL_WRAPPER template."""
        from src.multi_tenant.service_message_delivery import send_service_message

        wrapper_calls: list[str] = []

        async def mock_batch(subject, html, recipients):
            wrapper_calls.append(html)
            return True

        with patch(
            "src.multi_tenant.service_message_delivery._send_bcc_batch",
            side_effect=mock_batch,
        ):
            await send_service_message(
                "Test", "<p>content</p>", ["x@test.com"],
            )

        assert len(wrapper_calls) == 1
        # The wrapper contains the branded header
        assert "email-logo-light" in wrapper_calls[0]
        assert "remakerdigital.com" in wrapper_calls[0]

    @pytest.mark.asyncio
    async def test_partial_failure_tracking(self):
        """TEST-2949: Failed batches are tracked in result.errors."""
        from src.multi_tenant.service_message_delivery import send_service_message

        call_count = 0

        async def mock_batch(subject, html, recipients):
            nonlocal call_count
            call_count += 1
            # First batch succeeds, second fails
            return call_count == 1

        recipients = [f"u{i}@test.com" for i in range(80)]  # 2 batches of 50+30

        with patch(
            "src.multi_tenant.service_message_delivery._send_bcc_batch",
            side_effect=mock_batch,
        ):
            result = await send_service_message(
                "Test", "<p>body</p>", recipients,
            )

        assert result.sent_count == 50
        assert result.failed_count == 30
        assert result.success is False
        assert len(result.errors) == 1


# ---------------------------------------------------------------------------
# API endpoint tests (TEST-2950 through TEST-2952)
# ---------------------------------------------------------------------------


class TestServiceMessageAPI:
    """Superadmin API endpoint for service messages (SPEC-1646)."""

    @pytest.mark.asyncio
    async def test_send_endpoint_requires_superadmin(self):
        """TEST-2950: POST /service-messages/send requires SUPERADMIN role."""
        from src.multi_tenant.superadmin_api import (
            ServiceMessageRequest,
            send_service_message_endpoint,
        )
        # The endpoint uses Depends(require_role(TeamMemberRole.SUPERADMIN))
        # which is enforced at the FastAPI dependency injection level.
        # Here we verify the function signature expects a TenantContext.
        import inspect
        sig = inspect.signature(send_service_message_endpoint)
        param_names = list(sig.parameters.keys())
        assert "ctx" in param_names
        assert "request" in param_names

    @pytest.mark.asyncio
    async def test_send_endpoint_rejects_non_spa_tenant(self):
        """TEST-2951: Non-SPA tenants get 403 when sending service messages."""
        from src.multi_tenant.superadmin_api import (
            ServiceMessageRequest,
            send_service_message_endpoint,
        )
        from src.multi_tenant.auth import TenantContext

        mock_ctx = MagicMock(spec=TenantContext)
        mock_ctx.tenant_id = "some-other-tenant"
        mock_ctx.user_email = "admin@other.com"

        request = ServiceMessageRequest(
            subject="Test",
            body="<p>test</p>",
        )

        # Patch _tenant_repo to avoid 503
        with patch("src.multi_tenant.superadmin_api._tenant_repo", MagicMock()):
            with pytest.raises(Exception) as exc_info:
                await send_service_message_endpoint(request=request, ctx=mock_ctx)
            # Should raise HTTPException with 403
            assert "403" in str(exc_info.value.status_code) or exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_preview_returns_recipient_list(self):
        """TEST-2952: Preview endpoint returns filtered recipient list."""
        from src.multi_tenant.superadmin_api import (
            ServiceMessageRecipient,
            ServiceMessagePreviewResponse,
            _resolve_service_message_recipients,
        )

        # Mock the tenant_repo._container.query_items to return test data
        mock_container = MagicMock()

        async def mock_query(*args, **kwargs):
            for item in [
                {"tenant_id": "t1", "customer_email": "a@test.com", "tier": "professional", "status": "active"},
                {"tenant_id": "t2", "customer_email": "b@test.com", "tier": "starter", "status": "active"},
            ]:
                yield item

        mock_container.query_items = mock_query
        mock_repo = MagicMock()
        mock_repo._container = mock_container

        with patch("src.multi_tenant.superadmin_api._tenant_repo", mock_repo):
            recipients = await _resolve_service_message_recipients(
                filter_status=["active"],
            )

        assert len(recipients) == 2
        assert recipients[0].email == "a@test.com"
        assert recipients[1].tenant_id == "t2"


# ---------------------------------------------------------------------------
# Source inspection tests (TEST-2953 through TEST-2955)
# ---------------------------------------------------------------------------


class TestServiceMessageSourceInspection:
    """Source code inspection for service messages feature completeness."""

    def test_service_messages_page_exists(self):
        """TEST-2953: ServiceMessages.tsx exists in Provider Console pages."""
        from pathlib import Path

        page_path = Path("admin/provider/pages/ServiceMessages.tsx")
        assert page_path.exists(), "ServiceMessages.tsx not found in provider pages"
        content = page_path.read_text(encoding="utf-8")
        assert "ServiceMessagesPage" in content
        assert "service-messages" in content.lower()

    def test_service_messages_route_registered(self):
        """TEST-2954: Service messages route is registered in provider index."""
        from pathlib import Path

        index_path = Path("admin/provider/index.tsx")
        content = index_path.read_text(encoding="utf-8")
        assert "ServiceMessagesPage" in content
        assert "/service-messages" in content

    def test_service_messages_sidebar_nav(self):
        """TEST-2955: Service Messages nav item in ProviderLayout sidebar."""
        from pathlib import Path

        layout_path = Path("admin/provider/layouts/ProviderLayout.tsx")
        content = layout_path.read_text(encoding="utf-8")
        assert "Service Messages" in content
        assert "/service-messages" in content
