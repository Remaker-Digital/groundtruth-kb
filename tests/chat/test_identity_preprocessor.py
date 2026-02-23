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
    _extract_email,
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
