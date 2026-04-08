"""Tests for SPEC-1836: User Feedback Mechanism (Thumbs Up/Down).

Verifies feedback submission, storage, rate limiting, and aggregate metrics.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


class TestFeedbackSubmission:
    """SPEC-1836: Feedback stored in conversation document."""

    @pytest.mark.asyncio
    async def test_positive_feedback_stored(self):
        """TEST-10448: Positive feedback stored in conversation feedback[] array."""
        from src.multi_tenant.conversation_feedback import submit_feedback

        mock_repo = AsyncMock()
        mock_repo.get_conversation.return_value = {
            "id": "conv-001",
            "tenant_id": "tenant-001",
            "messages": [{"role": "user"}, {"role": "assistant"}, {"role": "user"}, {"role": "assistant"}],
            "feedback": [],
        }
        mock_repo.update_conversation.return_value = True

        result = await submit_feedback(
            repo=mock_repo,
            conversation_id="conv-001",
            tenant_id="tenant-001",
            message_index=1,
            rating="positive",
        )

        assert result["status"] == "recorded"
        update_call = mock_repo.update_conversation.call_args
        feedback_array = update_call[1].get("feedback") or update_call[0][1].get("feedback", [])
        assert len(feedback_array) == 1
        assert feedback_array[0]["rating"] == "positive"
        assert feedback_array[0]["message_index"] == 1

    @pytest.mark.asyncio
    async def test_negative_feedback_with_comment(self):
        """TEST-10449: Negative feedback with 200-char comment stored."""
        from src.multi_tenant.conversation_feedback import submit_feedback

        mock_repo = AsyncMock()
        mock_repo.get_conversation.return_value = {
            "id": "conv-001",
            "tenant_id": "tenant-001",
            "messages": [{"role": "user"}, {"role": "assistant"}],
            "feedback": [],
        }
        mock_repo.update_conversation.return_value = True

        comment = "The response didn't address my question about billing." * 3  # ~150 chars

        result = await submit_feedback(
            repo=mock_repo,
            conversation_id="conv-001",
            tenant_id="tenant-001",
            message_index=1,
            rating="negative",
            comment=comment,
        )

        assert result["status"] == "recorded"

    @pytest.mark.asyncio
    async def test_feedback_rate_limit_max_10(self):
        """TEST-10450: 11th feedback submission rejected with 429."""
        from src.multi_tenant.conversation_feedback import submit_feedback, FeedbackRateLimitError

        mock_repo = AsyncMock()
        mock_repo.get_conversation.return_value = {
            "id": "conv-001",
            "tenant_id": "tenant-001",
            "messages": [{"role": "user"}, {"role": "assistant"}] * 12,
            "feedback": [{"message_index": i, "rating": "positive"} for i in range(10)],
        }

        with pytest.raises(FeedbackRateLimitError):
            await submit_feedback(
                repo=mock_repo,
                conversation_id="conv-001",
                tenant_id="tenant-001",
                message_index=11,
                rating="positive",
            )

    @pytest.mark.asyncio
    async def test_comment_max_500_chars(self):
        """SPEC-1836 req 4: Comment max 500 chars."""
        from src.multi_tenant.conversation_feedback import submit_feedback, FeedbackValidationError

        mock_repo = AsyncMock()
        mock_repo.get_conversation.return_value = {
            "id": "conv-001",
            "tenant_id": "tenant-001",
            "messages": [{"role": "user"}, {"role": "assistant"}],
            "feedback": [],
        }

        with pytest.raises(FeedbackValidationError):
            await submit_feedback(
                repo=mock_repo,
                conversation_id="conv-001",
                tenant_id="tenant-001",
                message_index=1,
                rating="negative",
                comment="x" * 501,
            )


class TestFeedbackMetrics:
    """SPEC-1836: Aggregate feedback metrics."""

    @pytest.mark.asyncio
    async def test_satisfaction_rate_computed(self):
        """TEST-10451: satisfaction_rate = positive / total rated."""
        from src.multi_tenant.conversation_feedback import compute_feedback_metrics

        feedback_data = [
            {"rating": "positive"},
            {"rating": "positive"},
            {"rating": "negative"},
            {"rating": "positive"},
        ]

        metrics = compute_feedback_metrics(feedback_data)
        assert metrics["satisfaction_rate"] == 0.75  # 3/4
        assert metrics["total_rated"] == 4
        assert metrics["positive_count"] == 3
        assert metrics["negative_count"] == 1

    @pytest.mark.asyncio
    async def test_feedback_rate_computed(self):
        """SPEC-1836 req 7: feedback_rate = rated / total messages."""
        from src.multi_tenant.conversation_feedback import compute_feedback_rate

        total_messages = 20
        rated_count = 8

        rate = compute_feedback_rate(rated_count, total_messages)
        assert rate == 0.4  # 8/20

    @pytest.mark.asyncio
    async def test_empty_feedback_returns_zero(self):
        """No feedback should return 0 satisfaction rate without error."""
        from src.multi_tenant.conversation_feedback import compute_feedback_metrics

        metrics = compute_feedback_metrics([])
        assert metrics["satisfaction_rate"] == 0.0
        assert metrics["total_rated"] == 0
