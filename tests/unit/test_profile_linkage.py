"""Unit tests for AUTH-5: Profile linkage — customer verification flow.

Tests that:
1. OTP-verified customers get customer_verified=True on conversations
2. Shopify HMAC-verified customers get customer_verified=True
3. Unverified customers get customer_verified=False
4. OTP token enriches visitor identity from token claims
5. Invalid/expired OTP tokens are rejected gracefully

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.chat.endpoints import router
from src.chat.models import VisitorIdentity
from src.chat.session import _resolve_customer_id


# ---------------------------------------------------------------------------
# Test app + mocks
# ---------------------------------------------------------------------------


def _build_app() -> FastAPI:
    """Create a minimal FastAPI app with the chat router."""
    app = FastAPI()
    app.include_router(router)
    return app


def _mock_tenant_context(tenant_id: str = "test-tenant-001"):
    """Create a mock TenantContext."""
    ctx = MagicMock()
    ctx.tenant_id = tenant_id
    ctx.tier = MagicMock()
    ctx.tier.value = "starter"
    ctx.status = "active"
    return ctx


def _mock_prefs_repo(activated: bool = True):
    """Create a mock PreferencesRepository."""
    repo = MagicMock()
    if activated:
        repo.get_active = AsyncMock(return_value={
            "id": "prefs:v1",
            "tenant_id": "test-tenant-001",
            "activated_at": "2026-01-01T00:00:00Z",
        })
    else:
        repo.get_active = AsyncMock(return_value=None)
    return repo


def _mock_session():
    """Create a mock ConversationSession."""
    session = MagicMock()
    session.start_conversation = AsyncMock(return_value=MagicMock(
        conversation_id="conv-123",
        stream_url="/api/chat/stream/conv-123",
        ws_url="/ws/chat/conv-123",
        created_at="2026-01-01T00:00:00Z",
    ))
    return session


# ---------------------------------------------------------------------------
# _resolve_customer_id tests
# ---------------------------------------------------------------------------


class TestResolveCustomerId:
    """Test the _resolve_customer_id helper function."""

    def test_none_visitor_returns_none(self):
        assert _resolve_customer_id(None) is None

    def test_customer_id_preferred(self):
        visitor = VisitorIdentity(
            customer_id="shopify_12345",
            email="alice@example.com",
        )
        assert _resolve_customer_id(visitor) == "shopify_12345"

    def test_email_fallback(self):
        """When no customer_id, email is used as the customer identifier."""
        visitor = VisitorIdentity(email="alice@example.com", name="Alice")
        assert _resolve_customer_id(visitor) == "alice@example.com"

    def test_empty_visitor_returns_none(self):
        visitor = VisitorIdentity()
        assert _resolve_customer_id(visitor) is None


# ---------------------------------------------------------------------------
# OTP token verification in endpoint
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestOtpTokenVerification:
    """Test that OTP customer tokens are validated in the conversation start endpoint."""

    async def test_valid_otp_token_sets_verified(self):
        """A valid OTP token should result in customer_verified=True."""
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        # Mock dependencies
        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
            patch(
                "src.multi_tenant.widget_otp_verification.decode_customer_token",
                return_value={
                    "tenant_id": "test-tenant-001",
                    "email": "alice@example.com",
                    "name": "Alice",
                    "exp": 9999999999,
                },
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={
                    "visitor": {"email": "alice@example.com", "name": "Alice"},
                    "customer_token": "valid.token",
                })

            assert resp.status_code == 201

            # Verify start_conversation was called with customer_verified=True
            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                # Positional
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            assert request_arg.metadata["customer_verified"] is True

    async def test_invalid_otp_token_not_verified(self):
        """An invalid OTP token should NOT set customer_verified."""
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
            patch(
                "src.multi_tenant.widget_otp_verification.decode_customer_token",
                return_value=None,  # Invalid token
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={
                    "visitor": {"email": "alice@example.com"},
                    "customer_token": "invalid.token",
                })

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            assert request_arg.metadata["customer_verified"] is False

    async def test_otp_token_tenant_mismatch(self):
        """An OTP token for a different tenant should NOT set verified."""
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
            patch(
                "src.multi_tenant.widget_otp_verification.decode_customer_token",
                return_value={
                    "tenant_id": "DIFFERENT-TENANT",  # Wrong tenant!
                    "email": "alice@example.com",
                    "exp": 9999999999,
                },
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={
                    "visitor": {"email": "alice@example.com"},
                    "customer_token": "wrong-tenant.token",
                })

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            assert request_arg.metadata["customer_verified"] is False

    async def test_otp_token_enriches_visitor(self):
        """Valid OTP token should create visitor from token claims when no visitor provided."""
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
            patch(
                "src.multi_tenant.widget_otp_verification.decode_customer_token",
                return_value={
                    "tenant_id": "test-tenant-001",
                    "email": "alice@example.com",
                    "name": "Alice",
                    "exp": 9999999999,
                },
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # No visitor in request — only customer_token
                resp = await client.post("/api/chat/conversations", json={
                    "customer_token": "valid.token",
                })

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            # Visitor should be created from token claims
            assert request_arg.visitor is not None
            assert request_arg.visitor.email == "alice@example.com"
            assert request_arg.visitor.name == "Alice"
            assert request_arg.metadata["customer_verified"] is True


# ---------------------------------------------------------------------------
# Shopify HMAC + verification flag
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestShopifyVerificationFlag:
    """Test that Shopify HMAC verification sets customer_verified."""

    async def test_valid_shopify_hmac_sets_verified(self):
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
            patch(
                "src.multi_tenant.shopify_customer_verification.verify_shopify_customer_hmac",
                new_callable=AsyncMock,
                return_value=True,
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={
                    "visitor": {
                        "customer_id": "shopify_12345",
                        "email": "alice@shop.com",
                        "hmac": "valid_hmac_hex",
                    },
                })

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            assert request_arg.metadata["customer_verified"] is True

    async def test_failed_shopify_hmac_strips_and_not_verified(self):
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
            patch(
                "src.multi_tenant.shopify_customer_verification.verify_shopify_customer_hmac",
                new_callable=AsyncMock,
                return_value=False,
            ),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={
                    "visitor": {
                        "customer_id": "shopify_12345",
                        "hmac": "bad_hmac",
                    },
                })

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            # Visitor should be stripped (None) and not verified
            assert request_arg.visitor is None
            assert request_arg.metadata["customer_verified"] is False


# ---------------------------------------------------------------------------
# No verification (anonymous / unverified pre-chat)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
class TestUnverifiedConversation:
    """Test that unverified conversations get customer_verified=False."""

    async def test_no_token_no_hmac_not_verified(self):
        """Plain pre-chat data without OTP token or HMAC → not verified."""
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={
                    "visitor": {"email": "alice@example.com", "name": "Alice"},
                })

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            assert request_arg.metadata["customer_verified"] is False

    async def test_anonymous_not_verified(self):
        """No visitor, no token → anonymous, not verified."""
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_session = _mock_session()

        with (
            patch("src.chat.endpoints._get_session", return_value=mock_session),
            patch("src.chat.endpoints.PreferencesRepository", return_value=_mock_prefs_repo()),
        ):
            from src.multi_tenant.middleware import get_tenant_context
            app.dependency_overrides[get_tenant_context] = lambda: ctx

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post("/api/chat/conversations", json={})

            assert resp.status_code == 201

            call_args = mock_session.start_conversation.call_args
            request_arg = call_args.kwargs.get("request") or call_args[1].get("request")
            if request_arg is None:
                request_arg = call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs["request"]
            assert request_arg.metadata["customer_verified"] is False
