"""Slice 3: S253 Phase 1 idempotent message append behavioral tests.

Tests ConversationSession.add_customer_message_idempotent() — ETag retry,
duplicate detection, in-flight guard, concurrency exhaustion.

Test plan ref: COMPREHENSIVE-TEST-PLAN-S245-S255.md Slice 3

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.chat.models import SendMessageRequest
from src.chat.session import (
    ConversationSession,
    InFlightResponseError,
    ConcurrencyExhaustedError,
)


def _make_session(repo=None, pii_scrubber=None):
    """Build a ConversationSession with mocked dependencies."""
    session = ConversationSession.__new__(ConversationSession)
    session._repo = repo or AsyncMock()
    session._pii_scrubber = pii_scrubber
    return session


def _make_doc(messages=None, turn_count=0, etag="etag-1"):
    """Build a minimal Cosmos conversation document."""
    return {
        "id": "conv-123",
        "partition_key": "tenant-1",
        "messages": messages or [],
        "turn_count": turn_count,
        "status": "active",
        "_etag": etag,
    }


def _make_request(idempotency_key=None, content="Hello"):
    """Build a SendMessageRequest."""
    return SendMessageRequest(
        conversation_id="conv-123",
        content=content,
        idempotency_key=idempotency_key,
    )


# ── Happy paths ───────────────────────────────────────────────────

class TestIdempotentAppendHappy:
    """Happy-path behavioral tests."""

    @pytest.mark.asyncio
    async def test_first_append_creates_message(self):
        """First append with idempotency_key creates message and returns response."""
        repo = AsyncMock()
        doc = _make_doc()
        repo.replace_with_etag = AsyncMock()
        session = _make_session(repo=repo)
        session._get_writable_conversation = AsyncMock(return_value=doc)

        key = str(uuid.uuid4())
        request = _make_request(idempotency_key=key)

        response = await session.add_customer_message_idempotent("tenant-1", request)

        assert response.accepted is True
        assert response.conversation_id == "conv-123"
        assert response.message_id  # non-empty
        repo.replace_with_etag.assert_awaited_once()
        # Verify the document was mutated with the new message
        written_doc = repo.replace_with_etag.call_args[0][2]
        last_msg = written_doc["messages"][-1]
        assert last_msg["metadata"]["idempotency_key"] == key

    @pytest.mark.asyncio
    async def test_duplicate_key_returns_existing_message(self):
        """Duplicate idempotency_key returns existing message without new write."""
        repo = AsyncMock()
        existing_msg = {
            "message_id": "msg-existing",
            "role": "customer",
            "content": "Hello",
            "metadata": {"idempotency_key": "key-dup"},
        }
        doc = _make_doc(messages=[existing_msg], turn_count=1)
        session = _make_session(repo=repo)
        session._get_writable_conversation = AsyncMock(return_value=doc)

        request = _make_request(idempotency_key="key-dup")

        response = await session.add_customer_message_idempotent("tenant-1", request)

        assert response.accepted is True
        assert response.message_id == "msg-existing"
        # No write should have occurred
        repo.replace_with_etag.assert_not_awaited()


# ── ETag conflict / retry ─────────────────────────────────────────

class TestIdempotentAppendRetry:
    """ETag conflict and retry behavioral tests."""

    @pytest.mark.asyncio
    async def test_etag_conflict_retries_and_succeeds(self):
        """ETag conflict on first attempt -> re-read -> succeed on second."""
        from azure.cosmos.exceptions import CosmosAccessConditionFailedError

        repo = AsyncMock()
        doc1 = _make_doc(etag="etag-1")
        doc2 = _make_doc(etag="etag-2")

        session = _make_session(repo=repo)
        # First call returns doc1, second returns doc2 (fresh)
        session._get_writable_conversation = AsyncMock(side_effect=[doc1, doc2])
        # First replace fails with ETag conflict, second succeeds
        repo.replace_with_etag = AsyncMock(
            side_effect=[CosmosAccessConditionFailedError(message="conflict"), None]
        )

        request = _make_request(idempotency_key="key-retry")

        response = await session.add_customer_message_idempotent("tenant-1", request)

        assert response.accepted is True
        assert repo.replace_with_etag.await_count == 2
        assert session._get_writable_conversation.await_count == 2

    @pytest.mark.asyncio
    async def test_all_retries_exhausted_raises(self):
        """All retries fail with ETag conflict -> ConcurrencyExhaustedError."""
        from azure.cosmos.exceptions import CosmosAccessConditionFailedError

        repo = AsyncMock()
        repo.replace_with_etag = AsyncMock(
            side_effect=CosmosAccessConditionFailedError(message="conflict")
        )

        session = _make_session(repo=repo)
        # Each retry re-reads the document; return fresh copies so in-memory
        # mutations from prior attempts don't leak the idempotency key.
        session._get_writable_conversation = AsyncMock(
            side_effect=[_make_doc(etag=f"etag-{i}") for i in range(5)]
        )

        request = _make_request(idempotency_key="key-exhaust")

        with pytest.raises(ConcurrencyExhaustedError):
            await session.add_customer_message_idempotent(
                "tenant-1", request, max_retries=3,
            )

        assert repo.replace_with_etag.await_count == 3


# ── In-flight guard ───────────────────────────────────────────────

class TestIdempotentAppendInFlight:
    """In-flight response guard behavioral tests."""

    @pytest.mark.asyncio
    async def test_in_flight_message_raises(self):
        """Last message is customer with no AI reply -> InFlightResponseError."""
        customer_msg = {
            "message_id": "msg-1",
            "role": "customer",
            "content": "waiting...",
            "metadata": {"idempotency_key": "key-other"},
        }
        doc = _make_doc(messages=[customer_msg])

        session = _make_session()
        session._get_writable_conversation = AsyncMock(return_value=doc)

        request = _make_request(idempotency_key="key-new")

        with pytest.raises(InFlightResponseError):
            await session.add_customer_message_idempotent("tenant-1", request)


# ── Backward compatibility ────────────────────────────────────────

class TestIdempotentAppendFallback:
    """Backward-compatible path without idempotency_key."""

    @pytest.mark.asyncio
    async def test_no_key_falls_back_to_non_idempotent(self):
        """No idempotency_key -> delegates to add_customer_message."""
        session = _make_session()
        mock_response = MagicMock()
        mock_response.accepted = True
        session.add_customer_message = AsyncMock(return_value=mock_response)

        request = _make_request(idempotency_key=None)

        response = await session.add_customer_message_idempotent("tenant-1", request)

        session.add_customer_message.assert_awaited_once_with("tenant-1", request)
        assert response.accepted is True
