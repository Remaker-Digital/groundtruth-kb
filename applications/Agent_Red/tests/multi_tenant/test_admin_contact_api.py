"""Tests for Admin Contact API endpoint specifications.

Covers:
    - Router prefix verification
    - send_contact_message handler (delegates to _send_contact_email)
    - Cosmos persistence (SPEC-1588): persist before email
    - Contact repo wiring (configure_contact_repo)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.admin_contact_api import (
    ContactRequest,
    configure_contact_repo,
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


# ---------------------------------------------------------------------------
# CONTACT-03: configure_contact_repo wiring
# ---------------------------------------------------------------------------


class TestConfigureContactRepo:
    """Verify configure_contact_repo sets the module-level repository."""

    def test_configure_sets_repo(self):
        import src.multi_tenant.admin_contact_api as mod

        mock_repo = MagicMock()
        original = mod._contact_repo
        try:
            configure_contact_repo(mock_repo)
            assert mod._contact_repo is mock_repo
        finally:
            mod._contact_repo = original

    def test_configure_none_clears_repo(self):
        import src.multi_tenant.admin_contact_api as mod

        original = mod._contact_repo
        try:
            configure_contact_repo(None)
            assert mod._contact_repo is None
        finally:
            mod._contact_repo = original


# ---------------------------------------------------------------------------
# CONTACT-04: Cosmos persistence before email (SPEC-1588)
# ---------------------------------------------------------------------------


class TestContactMessagePersistence:
    """Verify contact messages are persisted to Cosmos before email dispatch."""

    @pytest.mark.asyncio
    async def test_persistence_called_before_email(self):
        """ContactMessageDocument is created before email is sent."""
        from src.multi_tenant.admin_contact_api import send_contact_message
        import src.multi_tenant.admin_contact_api as mod

        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock(return_value={"id": "test"})
        original = mod._contact_repo

        call_order = []

        async def track_create(*args, **kwargs):
            call_order.append("persist")
            return {"id": "test"}

        async def track_email(*args, **kwargs):
            call_order.append("email")
            return True

        mock_repo.create = track_create

        try:
            mod._contact_repo = mock_repo
            body = ContactRequest(topic="support", subject="Test", message="Hello")
            ctx = _ctx()

            with patch(
                "src.multi_tenant.admin_contact_api._send_contact_email",
                new_callable=AsyncMock,
                side_effect=track_email,
            ):
                await send_contact_message(body, ctx=ctx)

            assert call_order == ["persist", "email"]
        finally:
            mod._contact_repo = original

    @pytest.mark.asyncio
    async def test_persistence_builds_correct_document(self):
        """ContactMessageDocument fields match request and context."""
        from src.multi_tenant.admin_contact_api import send_contact_message
        import src.multi_tenant.admin_contact_api as mod

        mock_repo = AsyncMock()
        captured_doc = None

        async def capture_create(tenant_id, doc):
            nonlocal captured_doc
            captured_doc = doc
            return {"id": "test"}

        mock_repo.create = capture_create
        original = mod._contact_repo

        try:
            mod._contact_repo = mock_repo
            body = ContactRequest(
                topic="billing",
                subject="Billing question",
                message="Need invoice",
            )
            ctx = _ctx(tenant_id="t-123", tier="professional")

            with patch(
                "src.multi_tenant.admin_contact_api._send_contact_email",
                new_callable=AsyncMock,
                return_value=True,
            ):
                await send_contact_message(body, ctx=ctx)

            assert captured_doc is not None
            assert captured_doc.tenant_id == "t-123"
            assert captured_doc.topic == "billing"
            assert captured_doc.subject == "Billing question"
            assert captured_doc.message == "Need invoice"
            assert captured_doc.status == "new"
            assert captured_doc.tier == "professional"
            assert captured_doc.member_email == "admin@test.com"
            assert captured_doc.created_at is not None
            assert captured_doc.updated_at is not None
        finally:
            mod._contact_repo = original

    @pytest.mark.asyncio
    async def test_persistence_failure_does_not_block_email(self):
        """If Cosmos persistence fails, email is still sent."""
        from src.multi_tenant.admin_contact_api import send_contact_message
        import src.multi_tenant.admin_contact_api as mod

        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock(side_effect=Exception("Cosmos unavailable"))
        original = mod._contact_repo

        try:
            mod._contact_repo = mock_repo
            body = ContactRequest(topic="support", subject="Test", message="Hello")
            ctx = _ctx()

            with patch(
                "src.multi_tenant.admin_contact_api._send_contact_email",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_email:
                response = await send_contact_message(body, ctx=ctx)

            # Email should still be called despite persistence failure
            mock_email.assert_called_once()
            assert response.ok is True
        finally:
            mod._contact_repo = original

    @pytest.mark.asyncio
    async def test_no_repo_still_sends_email(self):
        """When contact_repo is None, email is sent without persistence."""
        from src.multi_tenant.admin_contact_api import send_contact_message
        import src.multi_tenant.admin_contact_api as mod

        original = mod._contact_repo
        try:
            mod._contact_repo = None
            body = ContactRequest(topic="general", subject="Test", message="Hi")
            ctx = _ctx()

            with patch(
                "src.multi_tenant.admin_contact_api._send_contact_email",
                new_callable=AsyncMock,
                return_value=True,
            ) as mock_email:
                response = await send_contact_message(body, ctx=ctx)

            mock_email.assert_called_once()
            assert response.ok is True
        finally:
            mod._contact_repo = original
