"""Tests for the in-conversation identity preprocessor (P0-AUTH-FIX).

Covers:
    preprocess_identity() — 18 tests
    1. Already verified → action=none (short circuit)
    2. Email message → sends OTP, returns email_received
    3. Valid 6-digit code after OTP sent → otp_received
    4. Invalid 6-digit code → otp_invalid
    5. Non-email, non-OTP message → action=none (pass-through)
    6. "skip" during OTP pending → skip_verification
    7. "continue as guest" during OTP → skip_verification
    8. Email in short sentence → email_received (flexible extraction)
    9. OTP code without prior OTP send → action=none
    10. Rate limit: >3 OTP attempts → otp_rate_limited
    11. Conversation not found → action=none
    12. Malformed email → action=none
    13. "it's alice@example.com" → email_received (flexible extraction)
    14. "email: alice@example.com" → email_received (flexible extraction)
    15. Two emails in one message → action=none (ambiguous)
    16. Long message >200 chars with email → action=none (safety guard)
    17. Skip phrase NOT during OTP pending → action=none (passes to AI)
    18. _extract_email unit tests

Run:
    pytest tests/chat/test_identity_preprocessor.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.chat.identity_preprocessor import (
    IdentityAction,
    _MAX_OTP_ATTEMPTS,
    _MAX_SMS_OTP_ATTEMPTS,
    _extract_email,
    _extract_phone,
    preprocess_identity,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_conv_doc(**overrides) -> dict:
    """Create a mock conversation document."""
    defaults = {
        "id": "conv-001",
        "tenant_id": "test-tenant",
        "customer_verified": False,
        "identity_email": None,
        "identity_otp_sent_at": None,
        "identity_otp_attempts": 0,
        "identity_phone": None,
        "identity_sms_sent_at": None,
        "identity_sms_attempts": 0,
        "phone_verified": False,
    }
    defaults.update(overrides)
    return defaults


@pytest.fixture()
def mock_conv_repo():
    """Create a mock ConversationRepository."""
    repo = MagicMock()
    repo.read = AsyncMock()
    repo.patch = AsyncMock()
    return repo


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPreprocessIdentity:
    """In-conversation identity preprocessor."""

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_already_verified_returns_none(self, MockRepo):
        """Already verified customer → action=none (short circuit)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(customer_verified=True))

        result = await preprocess_identity("conv-001", "test-tenant", "hello")

        assert result.action == "none"
        assert result.system_message is None

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._send_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_email_message_sends_otp(self, MockRepo, mock_send_otp):
        """Entire message is email → sends OTP, returns email_received."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        repo.patch = AsyncMock()
        mock_send_otp.return_value = True

        result = await preprocess_identity("conv-001", "test-tenant", "alice@example.com")

        assert result.action == "email_received"
        assert result.email == "alice@example.com"
        assert "verification code" in result.system_message.lower()
        mock_send_otp.assert_called_once_with(email="alice@example.com", tenant_id="test-tenant")

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._verify_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_valid_otp_code_returns_otp_received(self, MockRepo, mock_verify_otp):
        """Valid 6-digit code after OTP sent → otp_received."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
            identity_otp_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_otp_attempts=0,
        ))
        repo.patch = AsyncMock()
        mock_verify_otp.return_value = True

        result = await preprocess_identity("conv-001", "test-tenant", "123456")

        assert result.action == "otp_received"
        assert result.email == "alice@example.com"
        assert "verified" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._verify_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_invalid_otp_code_returns_otp_invalid(self, MockRepo, mock_verify_otp):
        """Invalid 6-digit code → otp_invalid."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
            identity_otp_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_otp_attempts=0,
        ))
        repo.patch = AsyncMock()
        mock_verify_otp.return_value = False

        result = await preprocess_identity("conv-001", "test-tenant", "999999")

        assert result.action == "otp_invalid"
        assert "doesn't look right" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_normal_message_passes_through(self, MockRepo):
        """Non-email, non-OTP message → action=none (pass to AI)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())

        result = await preprocess_identity(
            "conv-001", "test-tenant", "What is your return policy?",
        )

        assert result.action == "none"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_skip_during_otp_pending(self, MockRepo):
        """'skip' during OTP pending → skip_verification."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
            identity_otp_sent_at=datetime.now(timezone.utc).isoformat(),
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "skip")

        assert result.action == "skip_verification"
        assert "without verification" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_continue_as_guest_during_otp_pending(self, MockRepo):
        """'continue as guest' during OTP pending → skip_verification."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
            identity_otp_sent_at=datetime.now(timezone.utc).isoformat(),
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "continue as guest")

        assert result.action == "skip_verification"

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._send_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_email_in_short_sentence_detected(self, MockRepo, mock_send_otp):
        """Email embedded in a short sentence → flexible extraction detects it."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        repo.patch = AsyncMock()
        mock_send_otp.return_value = True

        result = await preprocess_identity(
            "conv-001", "test-tenant",
            "my email is alice@example.com",
        )

        assert result.action == "email_received"
        assert result.email == "alice@example.com"
        mock_send_otp.assert_called_once_with(email="alice@example.com", tenant_id="test-tenant")

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_otp_code_without_prior_send(self, MockRepo):
        """6-digit code but no OTP was sent → action=none (defense)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_otp_sent_at=None,
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "123456")

        # Without OTP context, 6 digits is NOT treated as a code
        assert result.action == "none"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_rate_limit_exceeded_rejects(self, MockRepo):
        """More than 3 OTP attempts → otp_rate_limited."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
            identity_otp_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_otp_attempts=_MAX_OTP_ATTEMPTS,
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "123456")

        assert result.action == "otp_rate_limited"
        assert "maximum" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_conversation_not_found_returns_none(self, MockRepo):
        """Conversation not in DB → action=none (error handling)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(side_effect=Exception("Not found"))

        result = await preprocess_identity("conv-001", "test-tenant", "hello")

        assert result.action == "none"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_malformed_email_not_detected(self, MockRepo):
        """Malformed email → action=none (validation)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())

        # Various malformed emails
        for bad_email in ["notanemail", "@missing.com", "user@", "a b@c.com"]:
            result = await preprocess_identity("conv-001", "test-tenant", bad_email)
            assert result.action == "none", f"Expected none for '{bad_email}'"

    # --- Flexible email extraction tests (GAP-1 fix) -----------------------

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._send_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_flexible_email_its_pattern(self, MockRepo, mock_send_otp):
        """'it's alice@example.com' → flexible extraction detects email."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        repo.patch = AsyncMock()
        mock_send_otp.return_value = True

        result = await preprocess_identity(
            "conv-001", "test-tenant", "it's alice@example.com",
        )

        assert result.action == "email_received"
        assert result.email == "alice@example.com"

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._send_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_flexible_email_colon_pattern(self, MockRepo, mock_send_otp):
        """'email: alice@example.com' → flexible extraction detects email."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        repo.patch = AsyncMock()
        mock_send_otp.return_value = True

        result = await preprocess_identity(
            "conv-001", "test-tenant", "email: alice@example.com",
        )

        assert result.action == "email_received"
        assert result.email == "alice@example.com"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_two_emails_in_message_ambiguous(self, MockRepo):
        """Two emails in one message → action=none (ambiguous, don't guess)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())

        result = await preprocess_identity(
            "conv-001", "test-tenant",
            "I bought from alice@ex.com and bob@ex.com",
        )

        assert result.action == "none"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_long_message_with_email_not_extracted(self, MockRepo):
        """Long message >200 chars with email → not extracted (safety guard)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())

        long_msg = "A" * 180 + " alice@example.com " + "B" * 30
        result = await preprocess_identity(
            "conv-001", "test-tenant", long_msg,
        )

        assert result.action == "none"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_skip_phrase_not_during_otp_pending(self, MockRepo):
        """Skip phrase without OTP pending → passes to AI (no interception)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_otp_sent_at=None,  # No OTP pending
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "skip")

        # "skip" is not an email, not an OTP code, and no OTP pending
        assert result.action == "none"


class TestExtractEmail:
    """Unit tests for _extract_email() helper function."""

    def test_strict_match_bare_email(self):
        assert _extract_email("alice@example.com") == "alice@example.com"

    def test_strict_match_uppercase(self):
        assert _extract_email("ALICE@EXAMPLE.COM") == "alice@example.com"

    def test_flexible_match_in_sentence(self):
        assert _extract_email("my email is alice@example.com") == "alice@example.com"

    def test_flexible_match_with_prefix(self):
        assert _extract_email("it's bob@test.org") == "bob@test.org"

    def test_no_email_returns_none(self):
        assert _extract_email("hello world") is None

    def test_multiple_emails_returns_none(self):
        assert _extract_email("alice@a.com and bob@b.com") is None

    def test_long_message_returns_none(self):
        assert _extract_email("X" * 195 + " alice@example.com") is None

    def test_empty_string_returns_none(self):
        assert _extract_email("") is None

    def test_whitespace_only_returns_none(self):
        assert _extract_email("   ") is None


# ---------------------------------------------------------------------------
# SPEC-1879 Phase 2A: Phone extraction + SMS OTP tests
# ---------------------------------------------------------------------------


class TestExtractPhone:
    """Unit tests for _extract_phone() helper function."""

    def test_strict_match_e164(self):
        assert _extract_phone("+15551234567") == "+15551234567"

    def test_strict_match_international(self):
        assert _extract_phone("+447911123456") == "+447911123456"

    def test_flexible_match_in_sentence(self):
        assert _extract_phone("my phone is +15551234567") == "+15551234567"

    def test_no_phone_returns_none(self):
        assert _extract_phone("hello world") is None

    def test_no_plus_prefix_returns_none(self):
        """Phone numbers without + prefix are not E.164."""
        assert _extract_phone("15551234567") is None

    def test_multiple_phones_returns_none(self):
        assert _extract_phone("+15551234567 and +15559876543") is None

    def test_long_message_returns_none(self):
        assert _extract_phone("X" * 195 + " +15551234567") is None

    def test_empty_string_returns_none(self):
        assert _extract_phone("") is None

    def test_too_short_returns_none(self):
        """Single digit after + is not valid E.164."""
        assert _extract_phone("+1") is None

    def test_leading_zero_country_code_returns_none(self):
        """E.164 country codes don't start with 0."""
        assert _extract_phone("+05551234567") is None


class TestPhoneSmsOtp:
    """SPEC-1879 Phase 2A: Phone SMS OTP flow in identity preprocessor."""

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._send_sms_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_phone_message_sends_sms_otp(self, MockRepo, mock_send_sms):
        """E.164 phone message → sends SMS OTP, returns phone_received."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        repo.patch = AsyncMock()
        mock_send_sms.return_value = True

        result = await preprocess_identity("conv-001", "test-tenant", "+15551234567")

        assert result.action == "phone_received"
        assert result.phone == "+15551234567"
        assert "verification code" in result.system_message.lower()
        mock_send_sms.assert_called_once_with(phone="+15551234567", tenant_id="test-tenant")

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._verify_sms_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_valid_sms_otp_returns_verified(self, MockRepo, mock_verify_sms):
        """Valid 6-digit code during SMS OTP pending → sms_otp_received + phone_verified."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_phone="+15551234567",
            identity_sms_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_sms_attempts=0,
        ))
        repo.patch = AsyncMock()
        mock_verify_sms.return_value = True

        result = await preprocess_identity("conv-001", "test-tenant", "123456")

        assert result.action == "sms_otp_received"
        assert result.phone == "+15551234567"
        assert "verified" in result.system_message.lower()
        # Verify phone_verified is set (NOT customer_verified)
        patch_calls = repo.patch.call_args_list
        phone_verified_set = any(
            any(op.get("path") == "/phone_verified" and op.get("value") is True for op in call.kwargs.get("operations", call.args[2] if len(call.args) > 2 else []))
            for call in patch_calls
        )
        assert phone_verified_set, "phone_verified must be set to True"

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._verify_sms_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_invalid_sms_otp_returns_invalid(self, MockRepo, mock_verify_sms):
        """Invalid 6-digit code during SMS OTP pending → sms_otp_invalid."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_phone="+15551234567",
            identity_sms_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_sms_attempts=0,
        ))
        repo.patch = AsyncMock()
        mock_verify_sms.return_value = False

        result = await preprocess_identity("conv-001", "test-tenant", "999999")

        assert result.action == "sms_otp_invalid"
        assert "doesn't look right" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_sms_otp_rate_limited(self, MockRepo):
        """More than 3 SMS OTP attempts → sms_otp_rate_limited."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_phone="+15551234567",
            identity_sms_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_sms_attempts=_MAX_SMS_OTP_ATTEMPTS,
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "123456")

        assert result.action == "sms_otp_rate_limited"
        assert "maximum" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_skip_during_sms_otp_pending(self, MockRepo):
        """'skip' during SMS OTP pending → skip_verification."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_phone="+15551234567",
            identity_sms_sent_at=datetime.now(timezone.utc).isoformat(),
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "skip")

        assert result.action == "skip_verification"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_email_takes_precedence_over_phone(self, MockRepo):
        """When email OTP is pending, email state machine handles codes."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
            identity_otp_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_phone="+15551234567",
            identity_sms_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_otp_attempts=0,
        ))
        # Email OTP pending + SMS OTP pending → email takes precedence
        with patch("src.chat.identity_preprocessor._verify_otp_for_conversation", new_callable=AsyncMock) as mock_verify:
            mock_verify.return_value = True
            repo.patch = AsyncMock()

            result = await preprocess_identity("conv-001", "test-tenant", "123456")

        # Should be email OTP verification, not SMS
        assert result.action == "otp_received"
        assert result.email == "alice@example.com"

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_phone_not_detected_when_email_collected(self, MockRepo):
        """Phone in message when email already collected → not detected (email path)."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_email="alice@example.com",
        ))

        result = await preprocess_identity("conv-001", "test-tenant", "+15551234567")

        # Phone detection only runs if no email collected
        assert result.action == "none"

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._verify_sms_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_phone_verified_does_not_set_customer_verified(self, MockRepo, mock_verify_sms):
        """Phone SMS OTP success sets phone_verified, NOT customer_verified."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc(
            identity_phone="+15551234567",
            identity_sms_sent_at=datetime.now(timezone.utc).isoformat(),
            identity_sms_attempts=0,
        ))
        repo.patch = AsyncMock()
        mock_verify_sms.return_value = True

        await preprocess_identity("conv-001", "test-tenant", "123456")

        # Check that customer_verified is never set to True
        patch_calls = repo.patch.call_args_list
        customer_verified_set = any(
            any(op.get("path") == "/customer_verified" and op.get("value") is True for op in call.kwargs.get("operations", call.args[2] if len(call.args) > 2 else []))
            for call in patch_calls
        )
        assert not customer_verified_set, "customer_verified must NOT be set by phone OTP"

    @pytest.mark.asyncio
    @patch("src.chat.identity_preprocessor._send_sms_otp_for_conversation", new_callable=AsyncMock)
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_phone_send_failure_returns_none(self, MockRepo, mock_send_sms):
        """SMS OTP send failure → action=none with system message."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        mock_send_sms.return_value = False

        result = await preprocess_identity("conv-001", "test-tenant", "+15551234567")

        assert result.action == "none"
        assert "wasn't able" in result.system_message.lower()

    @pytest.mark.asyncio
    @patch("src.multi_tenant.repository.ConversationRepository")
    async def test_phone_in_sentence_detected(self, MockRepo):
        """Phone embedded in sentence → detected via flexible extraction."""
        repo = MockRepo.return_value
        repo.read = AsyncMock(return_value=_make_conv_doc())
        repo.patch = AsyncMock()

        with patch("src.chat.identity_preprocessor._send_sms_otp_for_conversation", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True

            result = await preprocess_identity(
                "conv-001", "test-tenant", "my phone is +15551234567",
            )

        assert result.action == "phone_received"
        assert result.phone == "+15551234567"
