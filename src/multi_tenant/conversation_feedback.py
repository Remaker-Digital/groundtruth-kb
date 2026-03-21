"""SPEC-1836: Per-message user feedback (thumbs up/down).

Feedback is stored in the conversation document's `feedback[]` array.
Each entry records the message index, rating, optional comment, and timestamp.

Rate limit: max 10 feedback entries per conversation.
Comment limit: max 500 characters.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class FeedbackValidationError(Exception):
    """Raised when feedback input fails validation (e.g., comment too long)."""


class FeedbackRateLimitError(Exception):
    """Raised when the per-conversation feedback limit (10) is exceeded."""


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FEEDBACK_PER_CONVERSATION = 10
MAX_COMMENT_LENGTH = 500
VALID_RATINGS = {"positive", "negative"}


# ---------------------------------------------------------------------------
# Core feedback submission
# ---------------------------------------------------------------------------


async def submit_feedback(
    *,
    repo: Any,
    conversation_id: str,
    tenant_id: str,
    message_index: int,
    rating: str,
    comment: str | None = None,
) -> dict[str, str]:
    """Submit thumbs-up/down feedback for a specific assistant message.

    Args:
        repo: Conversation repository (must have get_conversation/update_conversation).
        conversation_id: Target conversation ID.
        tenant_id: Tenant owning the conversation.
        message_index: Zero-based index of the assistant message being rated.
        rating: "positive" or "negative".
        comment: Optional free-text comment (max 500 chars).

    Returns:
        {"status": "recorded"} on success.

    Raises:
        FeedbackValidationError: Invalid rating or comment exceeds limit.
        FeedbackRateLimitError: Conversation already has 10 feedback entries.
    """
    # Validate rating
    if rating not in VALID_RATINGS:
        raise FeedbackValidationError(
            f"Invalid rating '{rating}'. Must be one of: {', '.join(sorted(VALID_RATINGS))}"
        )

    # Validate comment length
    if comment is not None and len(comment) > MAX_COMMENT_LENGTH:
        raise FeedbackValidationError(
            f"Comment exceeds {MAX_COMMENT_LENGTH} characters ({len(comment)} given)"
        )

    # Fetch conversation
    conversation = await repo.get_conversation(conversation_id)

    # Check rate limit
    existing_feedback: list[dict] = conversation.get("feedback", [])
    if len(existing_feedback) >= MAX_FEEDBACK_PER_CONVERSATION:
        raise FeedbackRateLimitError(
            f"Conversation {conversation_id} has reached the "
            f"maximum of {MAX_FEEDBACK_PER_CONVERSATION} feedback entries"
        )

    # Build feedback entry
    entry: dict[str, Any] = {
        "message_index": message_index,
        "rating": rating,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if comment is not None:
        entry["comment"] = comment

    # Append and persist
    updated_feedback = [*existing_feedback, entry]
    await repo.update_conversation(
        conversation_id,
        {"feedback": updated_feedback},
    )

    return {"status": "recorded"}


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def compute_feedback_metrics(feedback_data: list[dict]) -> dict[str, Any]:
    """Compute aggregate feedback metrics from a list of feedback entries.

    Returns:
        {
            "satisfaction_rate": float (0.0–1.0),
            "total_rated": int,
            "positive_count": int,
            "negative_count": int,
        }
    """
    total = len(feedback_data)
    if total == 0:
        return {
            "satisfaction_rate": 0.0,
            "total_rated": 0,
            "positive_count": 0,
            "negative_count": 0,
        }

    positive = sum(1 for f in feedback_data if f.get("rating") == "positive")
    negative = total - positive

    return {
        "satisfaction_rate": positive / total,
        "total_rated": total,
        "positive_count": positive,
        "negative_count": negative,
    }


def compute_feedback_rate(rated_count: int, total_messages: int) -> float:
    """Compute the feedback rate: proportion of messages that received ratings.

    Returns 0.0 if total_messages is 0.
    """
    if total_messages == 0:
        return 0.0
    return rated_count / total_messages
