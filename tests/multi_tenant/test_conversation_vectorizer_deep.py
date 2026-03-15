"""P2 §6.6 — Conversation Vectorizer deep tests (CVD-01 to CVD-15).

Module under test: src.multi_tenant.conversation_vectorizer

Tests chunking, consent gating, tier-based history depth, prompt compression,
and the _compute_since_date static method.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.multi_tenant.conversation_vectorizer import (
    chunk_transcript,
    ConversationVectorizer,
    get_vectorizer,
    CHUNK_TARGET_TOKENS,
    CHUNK_MIN_TOKENS,
    CHARS_PER_TOKEN,
    MAX_HISTORY_TOKENS,
    EMBEDDING_DIMENSIONS,
)
from src.multi_tenant.cosmos_schema import ConsentStatus, TenantTier


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_messages(count: int, chars_per_msg: int = 200) -> list[dict]:
    """Generate a list of conversation messages."""
    msgs = []
    for i in range(count):
        role = "customer" if i % 2 == 0 else "agent"
        content = f"Message {i}: " + "x" * (chars_per_msg - len(f"Message {i}: "))
        msgs.append({"role": role, "content": content})
    return msgs


def _make_short_messages() -> list[dict]:
    """Messages that are too short to form a chunk (below min_tokens)."""
    return [{"role": "customer", "content": "Hi"}]


def _make_vector_results(count: int = 3) -> list[dict]:
    """Generate mock vector search results."""
    results = []
    for i in range(count):
        results.append({
            "chunk_text": f"Prior conversation chunk {i} about product questions.",
            "conversation_date": f"2026-01-{15 + i:02d}T10:00:00Z",
            "similarity": round(0.95 - i * 0.1, 2),
        })
    return results


def _configured_vectorizer() -> ConversationVectorizer:
    """Return a vectorizer configured with mock repos (no OpenAI client)."""
    v = ConversationVectorizer()
    mock_repo = AsyncMock()
    mock_repo.upsert = AsyncMock()
    mock_repo.vector_search = AsyncMock(return_value=[])
    mock_repo.delete_by_conversation = AsyncMock(return_value=0)
    v.configure(vector_repo=mock_repo)
    return v


# ===================================================================
# CVD-01: chunk_transcript — produces chunks in 200-300 token range
# ===================================================================


class TestCVD01ChunkSize:
    def test_produces_chunks(self):
        # 20 messages × 200 chars ≈ 4000 chars → multiple chunks
        msgs = _make_messages(20, 200)
        chunks = chunk_transcript(msgs)
        assert len(chunks) >= 2

    def test_chunk_text_is_nonempty(self):
        msgs = _make_messages(20, 200)
        chunks = chunk_transcript(msgs)
        for chunk in chunks:
            assert len(chunk) > 0


# ===================================================================
# CVD-02: chunk_transcript — short transcript below min_tokens
# ===================================================================


class TestCVD02ShortTranscript:
    def test_very_short_messages_return_empty(self):
        # "Hi" is way below CHUNK_MIN_TOKENS * CHARS_PER_TOKEN = 200 chars
        chunks = chunk_transcript(_make_short_messages())
        assert chunks == []

    def test_single_adequate_message(self):
        # One message just above min threshold
        content = "x" * (CHUNK_MIN_TOKENS * CHARS_PER_TOKEN + 10)
        msgs = [{"role": "customer", "content": content}]
        chunks = chunk_transcript(msgs)
        assert len(chunks) == 1


# ===================================================================
# CVD-03: chunk_transcript — empty messages
# ===================================================================


class TestCVD03EmptyMessages:
    def test_empty_list(self):
        assert chunk_transcript([]) == []

    def test_messages_with_no_content(self):
        msgs = [{"role": "customer", "content": ""}]
        assert chunk_transcript(msgs) == []


# ===================================================================
# CVD-04: vectorize_conversation — consent NOT_ASKED returns []
# ===================================================================


class TestCVD04ConsentNotAsked:
    async def test_not_asked_returns_empty(self):
        v = _configured_vectorizer()
        result = await v.vectorize_conversation(
            "t-001", "c-001", "conv-001",
            _make_messages(10),
            consent_status=ConsentStatus.NOT_ASKED,
        )
        assert result == []


# ===================================================================
# CVD-05: vectorize_conversation — consent DENIED returns []
# ===================================================================


class TestCVD05ConsentDenied:
    async def test_denied_returns_empty(self):
        v = _configured_vectorizer()
        result = await v.vectorize_conversation(
            "t-001", "c-001", "conv-001",
            _make_messages(10),
            consent_status=ConsentStatus.DENIED,
        )
        assert result == []


# ===================================================================
# CVD-06: vectorize_conversation — consent GRANTED processes normally
# ===================================================================


class TestCVD06ConsentGranted:
    async def test_granted_processes_chunks(self):
        v = _configured_vectorizer()
        # Enough messages to produce chunks
        msgs = _make_messages(20, 200)
        result = await v.vectorize_conversation(
            "t-001", "c-001", "conv-001",
            msgs,
            consent_status=ConsentStatus.GRANTED,
        )
        # Should return chunk IDs
        assert len(result) >= 1
        assert all("conv-001:chunk-" in cid for cid in result)

    async def test_granted_calls_repo_upsert(self):
        v = _configured_vectorizer()
        msgs = _make_messages(20, 200)
        await v.vectorize_conversation(
            "t-001", "c-001", "conv-001",
            msgs,
            consent_status=ConsentStatus.GRANTED,
        )
        # Repo upsert should have been called for each chunk
        assert v._vector_repo.upsert.call_count >= 1


# ===================================================================
# CVD-07: search_history — consent DENIED returns []
# ===================================================================


class TestCVD07SearchConsentDenied:
    async def test_denied_search_returns_empty(self):
        v = _configured_vectorizer()
        result = await v.search_history(
            "t-001", "c-001", "what was my last order?",
            TenantTier.STARTER,
            consent_status=ConsentStatus.DENIED,
        )
        assert result == []


# ===================================================================
# CVD-08: search_history — Starter tier uses 90d cutoff
# ===================================================================


class TestCVD08SearchStarterDepth:
    async def test_starter_passes_since_date(self):
        v = _configured_vectorizer()
        v._vector_repo.vector_search = AsyncMock(return_value=[])
        await v.search_history(
            "t-001", "c-001", "query",
            TenantTier.STARTER,
            consent_status=ConsentStatus.GRANTED,
        )
        call_kwargs = v._vector_repo.vector_search.call_args
        since_val = call_kwargs[1].get("since") or call_kwargs.kwargs.get("since")
        # history_depth_days removed from TIER_DEFAULTS — all tiers unlimited
        assert since_val is None


# ===================================================================
# CVD-09: search_history — Enterprise tier uses None (unlimited)
# ===================================================================


class TestCVD09SearchEnterpriseDepth:
    async def test_enterprise_passes_none_since(self):
        v = _configured_vectorizer()
        v._vector_repo.vector_search = AsyncMock(return_value=[])
        await v.search_history(
            "t-001", "c-001", "query",
            TenantTier.ENTERPRISE,
            consent_status=ConsentStatus.GRANTED,
        )
        call_kwargs = v._vector_repo.vector_search.call_args
        since_val = call_kwargs[1].get("since") or call_kwargs.kwargs.get("since")
        assert since_val is None


# ===================================================================
# CVD-10: compress_for_prompt — within token budget
# ===================================================================


class TestCVD10CompressWithinBudget:
    def test_output_within_budget(self):
        results = _make_vector_results(3)
        output = ConversationVectorizer.compress_for_prompt(results)
        max_chars = MAX_HISTORY_TOKENS * CHARS_PER_TOKEN
        assert len(output) <= max_chars + 200  # Some tolerance for header

    def test_output_contains_header(self):
        results = _make_vector_results(3)
        output = ConversationVectorizer.compress_for_prompt(results)
        assert "CONVERSATION HISTORY" in output

    def test_output_contains_dates(self):
        results = _make_vector_results(3)
        output = ConversationVectorizer.compress_for_prompt(results)
        assert "[2026-01-15]" in output


# ===================================================================
# CVD-11: compress_for_prompt — empty results
# ===================================================================


class TestCVD11CompressEmpty:
    def test_empty_results_return_empty_string(self):
        assert ConversationVectorizer.compress_for_prompt([]) == ""


# ===================================================================
# CVD-12: compress_for_prompt — truncation with "..."
# ===================================================================


class TestCVD12CompressTruncation:
    def test_long_chunks_truncated(self):
        # One very long result
        results = [{
            "chunk_text": "word " * 500,  # Very long
            "conversation_date": "2026-01-20T10:00:00Z",
            "similarity": 0.95,
        }]
        output = ConversationVectorizer.compress_for_prompt(results, max_tokens=50)
        # Should be truncated with "..."
        assert "..." in output


# ===================================================================
# CVD-13: _compute_since_date — Starter returns 90d ago
# ===================================================================


class TestCVD13SinceDateStarter:
    def test_starter_returns_90d_cutoff(self):
        # history_depth_days removed from TIER_DEFAULTS — Starter now unlimited
        since = ConversationVectorizer._compute_since_date(TenantTier.STARTER)
        assert since is None


# ===================================================================
# CVD-14: _compute_since_date — Professional returns 365d ago
# ===================================================================


class TestCVD14SinceDateProfessional:
    def test_professional_returns_365d_cutoff(self):
        # history_depth_days removed from TIER_DEFAULTS — Professional now unlimited
        since = ConversationVectorizer._compute_since_date(TenantTier.PROFESSIONAL)
        assert since is None


# ===================================================================
# CVD-15: _compute_since_date — Enterprise returns None
# ===================================================================


class TestCVD15SinceDateEnterprise:
    def test_enterprise_returns_none(self):
        since = ConversationVectorizer._compute_since_date(TenantTier.ENTERPRISE)
        assert since is None
