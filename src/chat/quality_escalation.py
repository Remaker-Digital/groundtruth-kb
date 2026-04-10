# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CQ-6: Quality-aware escalation (SPEC-0185 / WI-1516).

Provides quality-driven escalation recommendations.  When the AI's
quality scores drop below a configurable threshold for several
consecutive turns, this module recommends escalating the conversation
to a human agent.

The recommendation is *advisory* — it adds context to the escalation
decision made in CriticEscalationMixin, not a hard override.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.chat.models import QualityScore

logger = logging.getLogger(__name__)

# Defaults
DEFAULT_ESCALATION_THRESHOLD = 2.5  # quality below this triggers concern
DEFAULT_CONSECUTIVE_TURNS = 3  # how many low turns before recommending


@dataclass(frozen=True)
class QualityEscalationConfig:
    """Configurable thresholds for quality-triggered escalation."""

    escalation_threshold: float = DEFAULT_ESCALATION_THRESHOLD
    consecutive_low_turns: int = DEFAULT_CONSECUTIVE_TURNS
    enabled: bool = True


@dataclass(frozen=True)
class QualityEscalationRecommendation:
    """Recommendation to escalate based on quality scores."""

    should_escalate: bool
    reason: str
    severity: str  # "none", "warning", "critical"
    recent_scores: list[float] = field(default_factory=list)
    threshold: float = DEFAULT_ESCALATION_THRESHOLD


def should_quality_escalate(
    turn_scores: list[QualityScore],
    config: QualityEscalationConfig | None = None,
) -> QualityEscalationRecommendation:
    """Evaluate whether recent quality warrants escalation.

    Args:
        turn_scores: Per-turn quality scores for the current conversation,
            in chronological order (most recent last).
        config: Optional quality escalation config.  Uses defaults if None.

    Returns:
        QualityEscalationRecommendation with escalation advice.
    """
    if config is None:
        config = QualityEscalationConfig()

    if not config.enabled or not turn_scores:
        return QualityEscalationRecommendation(
            should_escalate=False,
            reason="Quality escalation disabled or no scores available",
            severity="none",
        )

    # Check the most recent N turns
    n = config.consecutive_low_turns
    recent = turn_scores[-n:] if len(turn_scores) >= n else turn_scores
    recent_overalls = [s.overall for s in recent]

    low_count = sum(1 for s in recent_overalls if s < config.escalation_threshold)

    if len(recent) >= n and low_count == n:
        # All recent turns below threshold → recommend escalation
        mean_score = sum(recent_overalls) / len(recent_overalls)
        severity = "critical" if mean_score < 2.0 else "warning"
        return QualityEscalationRecommendation(
            should_escalate=True,
            reason=(
                f"Quality below {config.escalation_threshold} for "
                f"{n} consecutive turns (mean: {mean_score:.1f})"
            ),
            severity=severity,
            recent_scores=recent_overalls,
            threshold=config.escalation_threshold,
        )

    if low_count > 0 and len(recent) >= n:
        # Some low turns but not all → no escalation, but note it
        return QualityEscalationRecommendation(
            should_escalate=False,
            reason=f"{low_count}/{n} recent turns below threshold",
            severity="none",
            recent_scores=recent_overalls,
            threshold=config.escalation_threshold,
        )

    return QualityEscalationRecommendation(
        should_escalate=False,
        reason="Quality within acceptable range",
        severity="none",
        recent_scores=recent_overalls,
        threshold=config.escalation_threshold,
    )
