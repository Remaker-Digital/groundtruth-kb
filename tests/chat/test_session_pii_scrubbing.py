"""Tests for PII scrubbing in ConversationSession message storage.

Covers:
    - set_pii_scrubber() enables/disables scrubbing
    - add_customer_message() scrubs email/phone when enabled
    - add_ai_message() scrubs email/phone when enabled
    - Scrubbing disabled by default (backward compat)
    - Scrubber can be toggled between calls

Run:
    pytest tests/chat/test_session_pii_scrubbing.py -v

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from src.chat.models import SendMessageRequest
from src.chat.session import ConversationSession
from src.multi_tenant.cosmos_schema import ConversationStatus


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "remaker-digital-001"
CONV_ID = "conv-pii-001"


def _make_session() -> tuple[ConversationSession, AsyncMock]:
    """Build a ConversationSession with mocked repo."""
    repo = AsyncMock()

    # Default: conversation exists and is active
    repo.read.return_value = {
        "id": CONV_ID,
        "tenant_id": TENANT_ID,
        "status": ConversationStatus.ACTIVE.value,
        "messages": [],
        "message_count": 0,
        "turn_count": 0,
    }
    repo.patch.return_value = None
    repo.append_message.return_value = None
    repo.query.return_value = []

    session = ConversationSession(conversation_repo=repo)
    return session, repo


def _last_appended_content(repo: AsyncMock) -> str:
    """Extract the 'content' field from the most recent append_message call."""
    call_args = repo.append_message.call_args
    message = call_args.kwargs.get("message") or call_args[0][2]
    return message["content"]


def _last_patch_content(repo: AsyncMock) -> str | None:
    """Extract the 'content' from the AI message patch add operation."""
    call_args = repo.patch.call_args
    operations = call_args.kwargs.get("operations") or call_args[0][2]
    for op in operations:
        if op.get("op") == "add" and op.get("path") == "/messages/-":
            return op["value"]["content"]
    return None


# ---------------------------------------------------------------------------
# Tests: PII scrubber configuration
# ---------------------------------------------------------------------------


class TestPiiScrubberConfig:
    """Tests for set_pii_scrubber() configuration."""

    def test_scrubber_disabled_by_default(self) -> None:
        session, _ = _make_session()
        assert session._pii_scrubber is None

    def test_set_pii_scrubber_enabled(self) -> None:
        session, _ = _make_session()
        session.set_pii_scrubber(True)
        assert session._pii_scrubber is not None

    def test_set_pii_scrubber_disabled(self) -> None:
        session, _ = _make_session()
        session.set_pii_scrubber(True)
        assert session._pii_scrubber is not None
        session.set_pii_scrubber(False)
        assert session._pii_scrubber is None

    def test_set_pii_scrubber_toggle(self) -> None:
        session, _ = _make_session()
        session.set_pii_scrubber(True)
        assert session._pii_scrubber is not None
        session.set_pii_scrubber(False)
        assert session._pii_scrubber is None
        session.set_pii_scrubber(True)
        assert session._pii_scrubber is not None


# ---------------------------------------------------------------------------
# Tests: Customer message PII scrubbing
# ---------------------------------------------------------------------------


class TestCustomerMessagePiiScrubbing:
    """Tests for PII redaction in add_customer_message()."""

    @pytest.mark.asyncio
    async def test_no_scrubbing_by_default(self) -> None:
        session, repo = _make_session()
        req = SendMessageRequest(
            conversation_id=CONV_ID,
            content="My email is john@example.com, call me at 555-123-4567",
        )
        await session.add_customer_message(TENANT_ID, req)
        stored = _last_appended_content(repo)
        assert "john@example.com" in stored
        assert "555-123-4567" in stored

    @pytest.mark.asyncio
    async def test_scrubs_email_when_enabled(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        req = SendMessageRequest(
            conversation_id=CONV_ID,
            content="Contact me at jane@company.org please",
        )
        await session.add_customer_message(TENANT_ID, req)
        stored = _last_appended_content(repo)
        assert "jane@company.org" not in stored
        assert "[REDACTED:email]" in stored

    @pytest.mark.asyncio
    async def test_scrubs_phone_when_enabled(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        req = SendMessageRequest(
            conversation_id=CONV_ID,
            content="My phone is +1 (555) 867-5309",
        )
        await session.add_customer_message(TENANT_ID, req)
        stored = _last_appended_content(repo)
        assert "867-5309" not in stored
        assert "[REDACTED:phone]" in stored

    @pytest.mark.asyncio
    async def test_scrubs_multiple_pii_patterns(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        req = SendMessageRequest(
            conversation_id=CONV_ID,
            content="Email: bob@test.com, Phone: 212-555-0100, thanks!",
        )
        await session.add_customer_message(TENANT_ID, req)
        stored = _last_appended_content(repo)
        assert "bob@test.com" not in stored
        assert "212-555-0100" not in stored
        assert "[REDACTED:email]" in stored
        assert "[REDACTED:phone]" in stored
        assert "thanks!" in stored

    @pytest.mark.asyncio
    async def test_no_pii_passes_through(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        req = SendMessageRequest(
            conversation_id=CONV_ID,
            content="I need help with my order #12345",
        )
        await session.add_customer_message(TENANT_ID, req)
        stored = _last_appended_content(repo)
        assert stored == "I need help with my order #12345"


# ---------------------------------------------------------------------------
# Tests: AI message PII scrubbing
# ---------------------------------------------------------------------------


class TestAiMessagePiiScrubbing:
    """Tests for PII redaction in add_ai_message()."""

    @pytest.mark.asyncio
    async def test_no_scrubbing_by_default(self) -> None:
        session, repo = _make_session()
        await session.add_ai_message(
            TENANT_ID, CONV_ID,
            content="I see your email is john@example.com, I'll help you.",
        )
        stored = _last_patch_content(repo)
        assert stored is not None
        assert "john@example.com" in stored

    @pytest.mark.asyncio
    async def test_scrubs_email_in_ai_response(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        await session.add_ai_message(
            TENANT_ID, CONV_ID,
            content="I've noted your email customer@shop.com for the return.",
        )
        stored = _last_patch_content(repo)
        assert stored is not None
        assert "customer@shop.com" not in stored
        assert "[REDACTED:email]" in stored

    @pytest.mark.asyncio
    async def test_scrubs_phone_in_ai_response(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        await session.add_ai_message(
            TENANT_ID, CONV_ID,
            content="I'll reach out to you at 800-555-1234.",
        )
        stored = _last_patch_content(repo)
        assert stored is not None
        assert "800-555-1234" not in stored
        assert "[REDACTED:phone]" in stored

    @pytest.mark.asyncio
    async def test_disabled_after_toggle(self) -> None:
        session, repo = _make_session()
        session.set_pii_scrubber(True)
        session.set_pii_scrubber(False)
        await session.add_ai_message(
            TENANT_ID, CONV_ID,
            content="Your email is test@example.com.",
        )
        stored = _last_patch_content(repo)
        assert stored is not None
        assert "test@example.com" in stored
