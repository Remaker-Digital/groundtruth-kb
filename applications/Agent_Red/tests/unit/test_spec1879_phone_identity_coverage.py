"""SPEC-1879 phone-identity SMS OTP coverage (WI-3212).

Deterministic coverage for the live SPEC-1879 contract in
``widget_otp_verification.py``, non-duplicative of
``test_widget_otp_verification.py::TestSmsOtpEndpoints``.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from tests.unit.test_widget_otp_verification import _build_app, _mock_tenant_context

from src.multi_tenant.widget_otp_verification import (
    _MAX_VERIFY_ATTEMPTS,
    _OTP_LENGTH,
    _OTP_TOKEN_TYPE,
    _OTP_TTL,
    _RATE_MAX,
    _RATE_WINDOW,
    _SMS_OTP_TOKEN_TYPE,
    normalize_e164,
)


class TestNormalizeE164:
    def test_valid_e164_passthrough(self) -> None:
        assert normalize_e164("+12125550100") == "+12125550100"

    def test_strips_formatting_characters(self) -> None:
        assert normalize_e164("+1 (212) 555-0100") == "+12125550100"

    def test_rejects_non_e164(self) -> None:
        assert normalize_e164("not-a-phone") is None


class TestSpec1879ParameterContract:
    def test_security_and_throttle_constants(self) -> None:
        assert _OTP_TTL == 600
        assert _RATE_MAX == 3
        assert _RATE_WINDOW == 300.0
        assert _OTP_LENGTH == 6
        assert _SMS_OTP_TOKEN_TYPE == "widget_otp_sms"
        assert _SMS_OTP_TOKEN_TYPE != _OTP_TOKEN_TYPE

    def test_max_verify_attempts_for_sms_lockout(self) -> None:
        assert _MAX_VERIFY_ATTEMPTS == 5


@pytest.mark.asyncio
class TestSmsOtpSpec1879Endpoints:
    async def test_starter_tier_blocked_without_sending_sms(self) -> None:
        app = _build_app()
        ctx = _mock_tenant_context()
        mock_send_sms = AsyncMock(return_value=True)

        with (
            patch(
                "src.multi_tenant.widget_otp_verification._check_tier_gate",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch("src.multi_tenant.widget_otp_verification._is_rate_limited", return_value=False),
            patch("src.multi_tenant.sms_verification._send_sms", mock_send_sms),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/send-sms",
                    json={"phone": "+12125550100", "name": "Alice"},
                )

        data = resp.json()
        assert data["reason"] == "tier_blocked"
        mock_send_sms.assert_not_awaited()

    async def test_send_sms_stores_hashed_code_not_plaintext(self) -> None:
        app = _build_app()
        ctx = _mock_tenant_context()
        otp_code = "123456"

        mock_token_repo = MagicMock()
        mock_token_repo.delete_token = AsyncMock(return_value=True)
        mock_token_repo.create_token = AsyncMock(return_value={"id": "otp:test-tenant-001:+12125550100"})

        mock_container = MagicMock()
        mock_container.patch_item = AsyncMock(return_value={})
        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with (
            patch(
                "src.multi_tenant.widget_otp_verification._check_tier_gate",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch("src.multi_tenant.widget_otp_verification._is_rate_limited", return_value=False),
            patch("src.multi_tenant.widget_otp_verification._generate_otp", return_value=otp_code),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch("src.multi_tenant.sms_verification._send_sms", new_callable=AsyncMock, return_value=True),
            patch("src.multi_tenant.sms_verification.hash_code", side_effect=lambda code: f"hash:{code}"),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/send-sms",
                    json={"phone": "+12125550100", "name": "Alice"},
                )

        assert resp.status_code == 200
        patch_ops = mock_container.patch_item.await_args.kwargs["patch_operations"]
        stored_hash = next(op["value"] for op in patch_ops if op["path"] == "/otp_code_hash")
        assert stored_hash == "hash:123456"
        assert stored_hash != otp_code

    async def test_verify_sms_success_consumes_token(self) -> None:
        app = _build_app()
        ctx = _mock_tenant_context()
        phone = "+12125550100"

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": f"otp:test-tenant-001:{phone}",
                "otp_code_hash": "hash:123456",
                "used": False,
                "verify_attempts": 0,
            }
        )
        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        mock_token_repo = MagicMock()
        mock_token_repo.consume_token = AsyncMock(return_value={"id": f"otp:test-tenant-001:{phone}"})

        with (
            patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos),
            patch("src.multi_tenant.repositories.VerificationTokenRepository", return_value=mock_token_repo),
            patch("src.multi_tenant.sms_verification.hash_code", side_effect=lambda code: f"hash:{code}"),
        ):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify-sms",
                    json={"phone": phone, "code": "123456"},
                )

        data = resp.json()
        assert data["verified"] is True
        assert data["phone"] == phone
        mock_token_repo.consume_token.assert_awaited_once_with(
            f"otp:test-tenant-001:{phone}",
            _SMS_OTP_TOKEN_TYPE,
        )

    async def test_verify_sms_already_used_returns_false(self) -> None:
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:+12125550100",
                "otp_code_hash": "hash:123456",
                "used": True,
            }
        )
        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify-sms",
                    json={"phone": "+12125550100", "code": "123456"},
                )

        assert resp.json()["verified"] is False

    async def test_verify_sms_locked_after_max_attempts(self) -> None:
        app = _build_app()
        ctx = _mock_tenant_context()

        mock_container = MagicMock()
        mock_container.read_item = AsyncMock(
            return_value={
                "id": "otp:test-tenant-001:+12125550100",
                "otp_code_hash": "hash:123456",
                "used": False,
                "verify_attempts": _MAX_VERIFY_ATTEMPTS,
            }
        )
        mock_container.patch_item = AsyncMock(return_value={})
        mock_cosmos = MagicMock()
        mock_cosmos.get_container = MagicMock(return_value=mock_container)

        with patch("src.multi_tenant.cosmos_client.get_cosmos_manager", return_value=mock_cosmos):
            from src.multi_tenant.middleware import get_tenant_context

            app.dependency_overrides[get_tenant_context] = lambda: ctx
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                resp = await client.post(
                    "/api/chat/otp/verify-sms",
                    json={"phone": "+12125550100", "code": "123456"},
                )

        assert resp.json()["verified"] is False
        mock_container.patch_item.assert_not_awaited()
