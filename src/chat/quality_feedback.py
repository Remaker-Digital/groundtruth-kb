"""CQ-8: Quality feedback loop (SPEC-0187 / WI-1518).

Analyses patterns in quality issues across recent turns and generates
short guidance text that can be injected into the system prompt to
steer the LLM towards better responses.

The feedback is *ephemeral* — it does NOT modify the stored system
prompt.  It's added at runtime and cleared once quality recovers.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from collections import Counter

from src.chat.models import QualityScore

logger = logging.getLogger(__name__)

# How many turns of sustained good quality before clearing feedback
RECOVERY_WINDOW = 10
MAX_GUIDANCE_LENGTH = 200

# Issue pattern → guidance mapping
_GUIDANCE_MAP: dict[str, str] = {
    "faithfulness": (
        "Focus on accuracy: only state facts supported by the knowledge base. "
        "Avoid speculation or unsupported claims."
    ),
    "relevancy": (
        "Stay focused on the customer's question. "
        "Answer directly before adding context."
    ),
    "tone": (
        "Maintain a professional, friendly tone. "
        "Avoid informal language or excessive enthusiasm."
    ),
    "empty": (
        "Always provide a substantive response. "
        "If unsure, acknowledge and offer to help differently."
    ),
}


class QualityFeedbackEngine:
    """Accumulates quality issues and generates runtime guidance.

    One instance per tenant conversation session.
    """

    def __init__(self) -> None:
        self._issue_history: list[list[str]] = []
        self._score_history: list[float] = []
        self._active_guidance: str | None = None

    def record_turn(self, score: QualityScore) -> None:
        """Record a scored turn's quality data."""
        self._issue_history.append(list(score.issues))
        self._score_history.append(score.overall)

    def get_quality_guidance(
        self,
        quality_threshold: float = 3.5,
    ) -> str | None:
        """Analyse recent quality patterns and return guidance text.

        Returns None if quality is good or insufficient data exists.
        The guidance string is max 200 characters.
        """
        if not self._score_history:
            return None

        # Check for recovery: last RECOVERY_WINDOW turns all above threshold
        if len(self._score_history) >= RECOVERY_WINDOW:
            recent = self._score_history[-RECOVERY_WINDOW:]
            if all(s >= quality_threshold for s in recent):
                self._active_guidance = None
                return None

        # Check if recent quality is poor
        recent_scores = self._score_history[-5:] if len(self._score_history) >= 5 else self._score_history
        mean_recent = sum(recent_scores) / len(recent_scores)

        if mean_recent >= quality_threshold:
            return self._active_guidance  # maintain existing guidance if any

        # Identify dominant issue patterns
        recent_issues = self._issue_history[-5:] if len(self._issue_history) >= 5 else self._issue_history
        all_issues = [issue for turn_issues in recent_issues for issue in turn_issues]

        if not all_issues:
            return None

        # Classify issues into categories
        category_counts: Counter[str] = Counter()
        for issue in all_issues:
            issue_lower = issue.lower()
            if "excluded" in issue_lower or "faithfulness" in issue_lower:
                category_counts["faithfulness"] += 1
            elif "relevancy" in issue_lower or "missing" in issue_lower or "expected" in issue_lower:
                category_counts["relevancy"] += 1
            elif "profanity" in issue_lower or "capitalization" in issue_lower or "tone" in issue_lower:
                category_counts["tone"] += 1
            elif "empty" in issue_lower or "short" in issue_lower:
                category_counts["empty"] += 1

        if not category_counts:
            # Issues exist but don't match known categories
            self._active_guidance = (
                "Pay close attention to response quality. "
                "Ensure accuracy, relevance, and professionalism."
            )
        else:
            # Use guidance for the most frequent issue category
            top_category = category_counts.most_common(1)[0][0]
            self._active_guidance = _GUIDANCE_MAP.get(top_category)

        # Enforce length limit
        if self._active_guidance and len(self._active_guidance) > MAX_GUIDANCE_LENGTH:
            self._active_guidance = self._active_guidance[:MAX_GUIDANCE_LENGTH]

        return self._active_guidance

    @property
    def has_active_guidance(self) -> bool:
        """Whether there is currently active quality guidance."""
        return self._active_guidance is not None

    def reset(self) -> None:
        """Clear all accumulated state."""
        self._issue_history.clear()
        self._score_history.clear()
        self._active_guidance = None
