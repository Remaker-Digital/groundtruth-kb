"""Tests for SMS Verification Service (SPEC-1686).

Covers:
    - Code generation (6-digit, cryptographic)
    - Code hashing (SHA-256)
    - SMS configuration detection
    - SMS sending (success / failure / unconfigured)
    - SmsVerificationService (send_code + verify_code)
    - Email fallback on SMS failure
    - Communication event emission (SPEC-1687 integration)

Run:
    pytest tests/multi_tenant/test_sms_verification.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, patch

import pytest


# -----------------------------------------------------------------------
# Code generation
# -----------------------------------------------------------------------


class TestCodeGeneration:

    def test_generate_code_is_6_digits(self):
        from src.multi_tenant.sms_verification import generate_verification_code

        code = generate_verification_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_code_is_random(self):
        from src.multi_tenant.sms_verification import generate_verification_code

        # Generate 20 codes -- should not all be identical
        codes = {generate_verification_code() for _ in range(20)}
        assert len(codes) > 1

    def test_code_digits_constant(self):
        from src.multi_tenant.sms_verification import _CODE_DIGITS

        assert _CODE_DIGITS == 6


# -----------------------------------------------------------------------
# Code hashing
# -----------------------------------------------------------------------


class TestCodeHashing:

    def test_hash_code_returns_sha256(self):
        from src.multi_tenant.sms_verification import hash_code

        result = hash_code("123456")
        expected = hashlib.sha256("123456".encode()).hexdigest()
        assert result == expected
        assert len(result) == 64

    def test_hash_code_empty_returns_empty(self):
        from src.multi_tenant.sms_verification import hash_code

        # hash_code hashes even empty strings (unlike communication_capture.hash_token)
        result = hash_code("")
        assert len(result) == 64  # SHA-256 of empty string

    def test_hash_code_deterministic(self):
        from src.multi_tenant.sms_verification import hash_code

        assert hash_code("999999") == hash_code("999999")


# -----------------------------------------------------------------------
# SMS configuration
# -----------------------------------------------------------------------


class TestSmsConfiguration:

    @patch("src.multi_tenant.sms_verification._ACS_SMS_FROM", "+15550123456")
    @patch("src.multi_tenant.sms_verification._ACS_CONNECTION_STRING", "endpoint=...")
    def test_is_sms_configured_true(self):
        from src.multi_tenant.sms_verification import is_sms_configured

        assert is_sms_configured() is True

    @patch("src.multi_tenant.sms_verification._ACS_SMS_FROM", "")
    @patch("src.multi_tenant.sms_verification._ACS_CONNECTION_STRING", "")
    def test_is_sms_configured_false_when_no_from(self):
        from src.multi_tenant.sms_verification import is_sms_configured

        assert is_sms_configured() is False

    @patch("src.multi_tenant.sms_verification._ACS_SMS_FROM", "+15550123456")
    @patch("src.multi_tenant.sms_verification._ACS_CONNECTION_STRING", "")
    def test_is_sms_configured_false_when_no_conn_string(self):
        from src.multi_tenant.sms_verification import is_sms_configured

        assert is_sms_configured() is False

# -----------------------------------------------------------------------
# SMS sending
# -----------------------------------------------------------------------


class TestSmsSending:

    @patch("src.multi_tenant.sms_verification._ACS_SMS_FROM", "")
    @pytest.mark.asyncio
    async def test_send_sms_returns_false_when_not_configured(self):
        from src.multi_tenant.sms_verification import _send_sms

        result = await _send_sms("+15550123456", "123456")
        assert result is False

    @patch("src.multi_tenant.sms_verification._ACS_SMS_FROM", "+15550000000")
    @patch("src.multi_tenant.sms_verification._ACS_CONNECTION_STRING", "endpoint=...")
    @pytest.mark.asyncio
    async def test_send_sms_success(self):
        import sys
        from unittest.mock import MagicMock

        # Mock the azure.communication.sms module since it is not installed
        mock_sms_module = MagicMock()
        sys.modules["azure.communication.sms"] = mock_sms_module
        try:
            from src.multi_tenant.sms_verification import _send_sms
            with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread:
                mock_to_thread.return_value = None
                result = await _send_sms("+15550123456", "123456")
                assert result is True
        finally:
            del sys.modules["azure.communication.sms"]

    @patch("src.multi_tenant.sms_verification._ACS_SMS_FROM", "+15550000000")
    @patch("src.multi_tenant.sms_verification._ACS_CONNECTION_STRING", "endpoint=...")
    @patch("asyncio.to_thread", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_send_sms_exception_returns_false(self, mock_to_thread):
        from src.multi_tenant.sms_verification import _send_sms

        mock_to_thread.side_effect = RuntimeError("ACS down")
        result = await _send_sms("+15550123456", "123456")
        assert result is False


# -----------------------------------------------------------------------
# SmsVerificationService.send_code -- email primary
# -----------------------------------------------------------------------


class TestSendCodeEmail:

    @pytest.mark.asyncio
    async def test_send_code_default_channel_is_email(self):
        from src.multi_tenant.sms_verification import SmsVerificationService

        svc = SmsVerificationService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock) as mock_email, \
             patch.object(svc, "_emit_event", new_callable=AsyncMock):
            result = await svc.send_code(email="user@example.com")
            assert result["channel"] == "email"
            assert len(result["code_hash"]) == 64
            assert result["ttl"] == 900
            mock_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_code_emits_communication_event(self):
        from src.multi_tenant.sms_verification import SmsVerificationService

        svc = SmsVerificationService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock) as _, \
             patch.object(svc, "_emit_event", new_callable=AsyncMock) as mock_emit:
            await svc.send_code(email="user@example.com")
            mock_emit.assert_called_once()
            call_kwargs = mock_emit.call_args.kwargs
            assert call_kwargs["channel"] == "email"
            assert "email_code" in call_kwargs["event_type"]

    @pytest.mark.asyncio
    async def test_send_code_uses_custom_purpose(self):
        from src.multi_tenant.sms_verification import SmsVerificationService

        svc = SmsVerificationService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock), \
             patch.object(svc, "_emit_event", new_callable=AsyncMock) as mock_emit:
            await svc.send_code(email="user@example.com", purpose="email_change")
            call_kwargs = mock_emit.call_args.kwargs
            assert "email_change_email_code" == call_kwargs["event_type"]

# -----------------------------------------------------------------------
# SmsVerificationService.send_code -- SMS preferred
# -----------------------------------------------------------------------


class TestSendCodeSms:

    @patch("src.multi_tenant.sms_verification.is_sms_configured", return_value=True)
    @patch("src.multi_tenant.sms_verification._send_sms", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_send_code_prefers_sms_when_configured(self, mock_send, _):
        from src.multi_tenant.sms_verification import SmsVerificationService

        mock_send.return_value = True
        svc = SmsVerificationService()
        with patch.object(svc, "_emit_event", new_callable=AsyncMock):
            result = await svc.send_code(
                email="user@example.com",
                phone="+15550123456",
                prefer_sms=True,
            )
            assert result["channel"] == "sms"
            mock_send.assert_called_once()

    @patch("src.multi_tenant.sms_verification.is_sms_configured", return_value=True)
    @patch("src.multi_tenant.sms_verification._send_sms", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_send_code_falls_back_to_email_on_sms_failure(self, mock_send, _):
        from src.multi_tenant.sms_verification import SmsVerificationService

        mock_send.return_value = False
        svc = SmsVerificationService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock) as mock_email, \
             patch.object(svc, "_emit_event", new_callable=AsyncMock):
            result = await svc.send_code(
                email="user@example.com",
                phone="+15550123456",
                prefer_sms=True,
            )
            assert result["channel"] == "email"
            mock_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_code_no_phone_uses_email(self):
        from src.multi_tenant.sms_verification import SmsVerificationService

        svc = SmsVerificationService()
        with patch.object(svc, "_send_email", new_callable=AsyncMock), \
             patch.object(svc, "_emit_event", new_callable=AsyncMock):
            result = await svc.send_code(
                email="user@example.com",
                phone="",
                prefer_sms=True,
            )
            assert result["channel"] == "email"


# -----------------------------------------------------------------------
# SmsVerificationService.verify_code
# -----------------------------------------------------------------------


class TestVerifyCode:

    @pytest.mark.asyncio
    async def test_verify_code_correct(self):
        from src.multi_tenant.sms_verification import (
            SmsVerificationService,
            hash_code,
        )

        svc = SmsVerificationService()
        hashed = hash_code("555555")
        assert await svc.verify_code(code="555555", expected_hash=hashed) is True

    @pytest.mark.asyncio
    async def test_verify_code_incorrect(self):
        from src.multi_tenant.sms_verification import (
            SmsVerificationService,
            hash_code,
        )

        svc = SmsVerificationService()
        hashed = hash_code("555555")
        assert await svc.verify_code(code="111111", expected_hash=hashed) is False

    @pytest.mark.asyncio
    async def test_verify_code_empty_code(self):
        from src.multi_tenant.sms_verification import SmsVerificationService

        svc = SmsVerificationService()
        assert await svc.verify_code(code="", expected_hash="abc") is False

    @pytest.mark.asyncio
    async def test_verify_code_empty_hash(self):
        from src.multi_tenant.sms_verification import SmsVerificationService

        svc = SmsVerificationService()
        assert await svc.verify_code(code="123456", expected_hash="") is False


# -----------------------------------------------------------------------
# TTL constant
# -----------------------------------------------------------------------


class TestTtlConstant:

    def test_ttl_is_15_minutes(self):
        from src.multi_tenant.sms_verification import _CODE_TTL

        assert _CODE_TTL == 900

    def test_verification_token_type(self):
        from src.multi_tenant.sms_verification import _VERIFICATION_TOKEN_TYPE

        assert _VERIFICATION_TOKEN_TYPE == "sms_verification"
