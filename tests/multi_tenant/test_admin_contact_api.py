"""Tests for Admin Contact API endpoint specifications.

Covers:
    - Router prefix verification
    - send_contact_message handler (delegates to _send_contact_email)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_contact_api import (
    ContactRequest,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _ctx(**overrides):
    ctx = MagicMock()
    ctx.tenant_id = overrides.get("tenant_id", "test-tenant-001")
    ctx.tier = MagicMock()
    ctx.tier.value = overrides.get("tier", "professional")
    ctx.user_id = overrides.get("user_id", "user-001")
    ctx.team_member_email = overrides.get("team_member_email", "admin@test.com")
    ctx.team_member_role = MagicMock()
    ctx.team_member_role.value = overrides.get("team_member_role", "admin")
    ctx.team_member_id = overrides.get("team_member_id", "member-001")
    ctx.auth_method = overrides.get("auth_method", "tenant_api_key")
    return ctx


# ---------------------------------------------------------------------------
# CONTACT-01: Router prefix
# ---------------------------------------------------------------------------


class TestRouterPrefix:
    """Verify the contact router is mounted at /api/admin."""

    def test_router_prefix_is_api_admin(self):
        assert router.prefix == "/api/admin"


# ---------------------------------------------------------------------------
# CONTACT-02: send_contact_message
# ---------------------------------------------------------------------------


class TestSendContactMessage:
    """POST /api/admin/contact delegates to _send_contact_email."""

    @pytest.mark.asyncio
    async def test_send_contact_email_success(self):
        """send_contact_message calls _send_contact_email and returns ok=True."""
        from src.multi_tenant.admin_contact_api import send_contact_message

        body = ContactRequest(
            topic="support",
            subject="Test Subject",
            message="Test message body",
        )
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_contact_api._send_contact_email",
            new_callable=AsyncMock,
            return_value=True,
        ) as mock_send:
            response = await send_contact_message(body, ctx=ctx)

        mock_send.assert_called_once()
        call_args = mock_send.call_args
        # First positional arg is the to_email (SUPPORT_EMAIL)
        assert call_args[0][0] == "support@remakerdigital.com"
        # Subject includes topic label
        assert "Support Request" in call_args[0][1]
        assert response.ok is True
        assert "sent" in response.detail.lower() or "received" in response.detail.lower()

    @pytest.mark.asyncio
    async def test_send_contact_email_failure_still_ok(self):
        """When email send fails, handler still returns ok=True (logged for review)."""
        from src.multi_tenant.admin_contact_api import send_contact_message

        body = ContactRequest(
            topic="bug_report",
            subject="Bug",
            message="Something broke",
        )
        ctx = _ctx()

        with patch(
            "src.multi_tenant.admin_contact_api._send_contact_email",
            new_callable=AsyncMock,
            return_value=False,
        ):
            response = await send_contact_message(body, ctx=ctx)

        # Even on failure, returns ok=True (logged for manual review)
        assert response.ok is True
