"""Tests for email verification endpoints and token repository.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.multi_tenant.email_verification import (
    VerifyEmailRequest,
    VerifyEmailResponse,
    _is_rate_limited,
    _rate_limit,
    _send_verification_email,
    router,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    test_app = FastAPI()
    test_app.include_router(router)
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_rate_limit():
    _rate_limit.clear()
    yield
    _rate_limit.clear()


# Mock repos for endpoint tests — patch at the import site
# (lazy imports inside functions use `from src.multi_tenant.repositories import X`)
@pytest.fixture
def mock_repos():
    """Patch all repository classes used by the email verification endpoints."""
    mock_tenant = AsyncMock()
    mock_token = AsyncMock()
    mock_prefs = AsyncMock()

    with (
        patch(
            "src.multi_tenant.repositories.TenantRepository",
            return_value=mock_tenant,
        ),
        patch(
            "src.multi_tenant.repositories.VerificationTokenRepository",
            return_value=mock_token,
        ),
        patch(
            "src.multi_tenant.repositories.PreferencesRepository",
            return_value=mock_prefs,
        ),
    ):
        yield {
            "tenant": mock_tenant,
            "token": mock_token,
            "prefs": mock_prefs,
        }


# ---------------------------------------------------------------------------
# Rate limiter tests
# ---------------------------------------------------------------------------


class TestRateLimiter:
    def test_first_request_not_limited(self):
        assert _is_rate_limited("1.2.3.4") is False

    def test_three_requests_not_limited(self):
        assert _is_rate_limited("1.2.3.4") is False
        assert _is_rate_limited("1.2.3.4") is False
        assert _is_rate_limited("1.2.3.4") is False

    def test_fourth_request_limited(self):
        for _ in range(3):
            _is_rate_limited("1.2.3.4")
        assert _is_rate_limited("1.2.3.4") is True

    def test_different_ips_independent(self):
        for _ in range(3):
            _is_rate_limited("1.1.1.1")
        assert _is_rate_limited("1.1.1.1") is True
        assert _is_rate_limited("2.2.2.2") is False


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


class TestModels:
    def test_verify_email_request_valid(self):
        req = VerifyEmailRequest(tenant_id="t1", email="a@b.com")
        assert req.tenant_id == "t1"
        assert req.email == "a@b.com"

    def test_verify_email_response_default_message(self):
        resp = VerifyEmailResponse()
        assert "verification" in resp.message.lower()


# ---------------------------------------------------------------------------
# Request endpoint tests
# ---------------------------------------------------------------------------


class TestRequestVerification:
    @patch("src.multi_tenant.email_verification._send_verification_email", new_callable=AsyncMock)
    def test_request_returns_uniform_message(
        self, mock_send, client, mock_repos
    ):
        mock_repos["tenant"].read.return_value = {"id": "t1", "tenant_id": "t1"}
        mock_repos["token"].create_token.return_value = {"id": "tok1"}
        mock_send.return_value = True

        resp = client.post(
            "/api/auth/verify-email/request",
            json={"tenant_id": "t1", "email": "test@example.com"},
        )
        assert resp.status_code == 200
        assert "verification" in resp.json()["message"].lower()

    @patch("src.multi_tenant.email_verification._send_verification_email", new_callable=AsyncMock)
    def test_request_nonexistent_tenant_same_message(
        self, mock_send, client, mock_repos
    ):
        mock_repos["tenant"].read.return_value = None

        resp = client.post(
            "/api/auth/verify-email/request",
            json={"tenant_id": "nonexistent", "email": "test@example.com"},
        )
        assert resp.status_code == 200
        assert "verification" in resp.json()["message"].lower()
        mock_repos["token"].create_token.assert_not_called()

    def test_request_rate_limited(self, client):
        for _ in range(4):
            resp = client.post(
                "/api/auth/verify-email/request",
                json={"tenant_id": "t1", "email": "test@example.com"},
            )
        # Always 200 — no enumeration
        assert resp.status_code == 200

    @patch("src.multi_tenant.email_verification._send_verification_email", new_callable=AsyncMock)
    def test_request_creates_token(self, mock_send, client, mock_repos):
        mock_repos["tenant"].read.return_value = {"id": "t1", "tenant_id": "t1"}
        mock_repos["token"].create_token.return_value = {"id": "tok1"}
        mock_send.return_value = True

        client.post(
            "/api/auth/verify-email/request",
            json={"tenant_id": "t1", "email": "test@example.com"},
        )

        mock_repos["token"].create_token.assert_called_once()
        kwargs = mock_repos["token"].create_token.call_args.kwargs
        assert kwargs["token_type"] == "email_verification"
        assert kwargs["tenant_id"] == "t1"
        assert kwargs["email"] == "test@example.com"

    @patch("src.multi_tenant.email_verification._send_verification_email", new_callable=AsyncMock)
    def test_request_sends_email(self, mock_send, client, mock_repos):
        mock_repos["tenant"].read.return_value = {"id": "t1", "tenant_id": "t1"}
        mock_repos["token"].create_token.return_value = {"id": "tok1"}
        mock_send.return_value = True

        client.post(
            "/api/auth/verify-email/request",
            json={"tenant_id": "t1", "email": "test@example.com"},
        )

        mock_send.assert_called_once()
        assert mock_send.call_args[0][0] == "test@example.com"
        assert "Agent Red" in mock_send.call_args[0][1]


# ---------------------------------------------------------------------------
# Confirm endpoint tests
# ---------------------------------------------------------------------------


class TestConfirmVerification:
    def test_confirm_valid_token(self, client, mock_repos):
        mock_repos["token"].consume_token.return_value = {
            "id": "tok1",
            "tenant_id": "t1",
            "email": "verified@example.com",
        }
        mock_repos["prefs"].read.return_value = {"id": "t1", "tenant_id": "t1"}

        resp = client.get("/api/auth/verify-email/confirm?token=tok1")
        assert resp.status_code == 200
        assert "Email Verified" in resp.text
        assert "verified@example.com" in resp.text
        mock_repos["prefs"].patch.assert_called_once()

    def test_confirm_invalid_token(self, client, mock_repos):
        mock_repos["token"].consume_token.return_value = None

        resp = client.get("/api/auth/verify-email/confirm?token=invalid")
        assert resp.status_code == 400
        assert "Verification Failed" in resp.text

    def test_confirm_already_used_token(self, client, mock_repos):
        mock_repos["token"].consume_token.return_value = None

        resp = client.get("/api/auth/verify-email/confirm?token=used-tok")
        assert resp.status_code == 400
        assert "invalid" in resp.text.lower() or "expired" in resp.text.lower()

    def test_confirm_sets_email_verified_flag(self, client, mock_repos):
        mock_repos["token"].consume_token.return_value = {
            "id": "tok1",
            "tenant_id": "t1",
            "email": "a@b.com",
        }
        mock_repos["prefs"].read.return_value = {"id": "t1", "tenant_id": "t1"}

        client.get("/api/auth/verify-email/confirm?token=tok1")

        ops = mock_repos["prefs"].patch.call_args.kwargs["operations"]
        assert any(
            op["path"] == "/email_verified" and op["value"] is True
            for op in ops
        )
        assert any(
            op["path"] == "/notification_email" and op["value"] == "a@b.com"
            for op in ops
        )

    def test_confirm_creates_prefs_if_not_exists(self, client, mock_repos):
        mock_repos["token"].consume_token.return_value = {
            "id": "tok1",
            "tenant_id": "t1",
            "email": "new@b.com",
        }
        mock_repos["prefs"].read.return_value = None

        resp = client.get("/api/auth/verify-email/confirm?token=tok1")
        assert resp.status_code == 200
        assert "Email Verified" in resp.text
        mock_repos["prefs"].upsert.assert_called_once()


# ---------------------------------------------------------------------------
# Verification token repository tests
# ---------------------------------------------------------------------------


class TestVerificationTokenRepository:
    @pytest.fixture
    def mock_container(self):
        return AsyncMock()

    @pytest.fixture
    def repo(self, mock_container):
        with patch(
            "src.multi_tenant.repositories.verification.get_cosmos_manager"
        ) as mock_mgr:
            mock_mgr.return_value.get_container.return_value = mock_container
            from src.multi_tenant.repositories.verification import (
                VerificationTokenRepository,
            )

            repo = VerificationTokenRepository()
            repo._container  # trigger property
            yield repo

    @pytest.mark.asyncio
    async def test_create_token(self, repo, mock_container):
        mock_container.create_item.return_value = {"id": "tok1"}

        await repo.create_token(
            token_id="tok1",
            token_type="email_verification",
            tenant_id="t1",
            email="a@b.com",
        )

        doc = mock_container.create_item.call_args.kwargs["body"]
        assert doc["id"] == "tok1"
        assert doc["token_type"] == "email_verification"
        assert doc["tenant_id"] == "t1"
        assert doc["email"] == "a@b.com"
        assert doc["used"] is False
        assert doc["ttl"] == 600

    @pytest.mark.asyncio
    async def test_consume_token_valid(self, repo, mock_container):
        mock_container.read_item.return_value = {
            "id": "tok1",
            "used": False,
            "tenant_id": "t1",
            "email": "a@b.com",
        }
        mock_container.patch_item.return_value = {}

        result = await repo.consume_token("tok1", "email_verification")
        assert result is not None
        assert result["tenant_id"] == "t1"
        mock_container.patch_item.assert_called_once()

    @pytest.mark.asyncio
    async def test_consume_token_already_used(self, repo, mock_container):
        mock_container.read_item.return_value = {"id": "tok1", "used": True}
        result = await repo.consume_token("tok1", "email_verification")
        assert result is None

    @pytest.mark.asyncio
    async def test_consume_token_not_found(self, repo, mock_container):
        from azure.cosmos.exceptions import CosmosResourceNotFoundError

        mock_container.read_item.side_effect = CosmosResourceNotFoundError(
            status_code=404, message="Not found"
        )
        result = await repo.consume_token("missing", "email_verification")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_token(self, repo, mock_container):
        mock_container.delete_item.return_value = None
        result = await repo.delete_token("tok1", "email_verification")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_token_not_found(self, repo, mock_container):
        from azure.cosmos.exceptions import CosmosResourceNotFoundError

        mock_container.delete_item.side_effect = CosmosResourceNotFoundError(
            status_code=404, message="Not found"
        )
        result = await repo.delete_token("missing", "email_verification")
        assert result is False


# ---------------------------------------------------------------------------
# Email sending helper tests
# ---------------------------------------------------------------------------


class TestSendVerificationEmail:
    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"AZURE_COMM_CONNECTION_STRING": "", "SMTP_HOST": ""},
        clear=False,
    )
    async def test_no_provider_returns_false(self):
        result = await _send_verification_email(
            "a@b.com", "Subject", "<html>body</html>"
        )
        assert result is False

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"AZURE_COMM_CONNECTION_STRING": "endpoint=https://test.com;accesskey=abc"},
        clear=False,
    )
    @patch("azure.communication.email.EmailClient")
    async def test_acs_send_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.from_connection_string.return_value = mock_client
        mock_poller = MagicMock()
        mock_result = MagicMock()
        mock_result.status = "Succeeded"
        mock_poller.result.return_value = mock_result
        mock_client.begin_send.return_value = mock_poller

        result = await _send_verification_email(
            "a@b.com", "Subject", "<html>body</html>"
        )
        assert result is True

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ",
        {"AZURE_COMM_CONNECTION_STRING": "endpoint=https://test.com;accesskey=abc"},
        clear=False,
    )
    @patch("azure.communication.email.EmailClient")
    async def test_acs_send_failure(self, mock_client_cls):
        mock_client_cls.from_connection_string.side_effect = Exception("conn error")

        result = await _send_verification_email(
            "a@b.com", "Subject", "<html>body</html>"
        )
        assert result is False
