"""Knowledge Score Service — observable knowledge quality metrics (SPEC-1873).

Computes a per-tenant knowledge quality score (0-100) from four factors:

    1. Coverage ratio    (40%) — fraction of queries answered without escalation
    2. Relevance score   (30%) — average KR relevance_score across conversations
    3. Escalation rate   (20%) — inverted gap escalation rate (lower = better)
    4. Freshness         (10%) — fraction of KB entries updated within 30 days

Also provides gap detection and clustering for the unanswered-question
review workflow.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------

# Factor weights (must sum to 1.0)
WEIGHT_COVERAGE = 0.40
WEIGHT_RELEVANCE = 0.30
WEIGHT_ESCALATION = 0.20
WEIGHT_FRESHNESS = 0.10

# Relevance threshold below which a conversation is "unanswered"
RELEVANCE_THRESHOLD = 0.3

# KB freshness window (days)
FRESHNESS_WINDOW_DAYS = 30


@dataclass
class KnowledgeScoreBreakdown:
    """Per-factor breakdown of the knowledge score."""
    coverage: float = 0.0       # 0-1
    relevance: float = 0.0      # 0-1
    escalation: float = 0.0     # 0-1 (inverted: 1.0 = no escalations)
    freshness: float = 0.0      # 0-1
    composite: float = 0.0      # 0-100
    total_conversations: int = 0
    unanswered_count: int = 0
    kb_entry_count: int = 0
    fresh_entry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": round(self.composite, 1),
            "factors": {
                "coverage": round(self.coverage, 3),
                "relevance": round(self.relevance, 3),
                "escalation_rate": round(1.0 - self.escalation, 3),
                "freshness": round(self.freshness, 3),
            },
            "total_conversations": self.total_conversations,
            "unanswered_count": self.unanswered_count,
            "kb_entry_count": self.kb_entry_count,
            "fresh_entry_count": self.fresh_entry_count,
        }


def compute_knowledge_score(
    *,
    total_conversations: int,
    answered_conversations: int,
    avg_relevance: float,
    escalation_count: int,
    kb_entry_count: int,
    fresh_entry_count: int,
) -> KnowledgeScoreBreakdown:
    """Compute the knowledge quality score from raw metrics.

    Args:
        total_conversations: Total conversations in the scoring window.
        answered_conversations: Conversations resolved without escalation/error.
        avg_relevance: Mean KR relevance_score across all conversations (0-1).
        escalation_count: Conversations escalated due to knowledge gaps.
        kb_entry_count: Total KB entries for the tenant.
        fresh_entry_count: KB entries updated within FRESHNESS_WINDOW_DAYS.

    Returns:
        KnowledgeScoreBreakdown with all factors and composite (0-100).
    """
    breakdown = KnowledgeScoreBreakdown(
        total_conversations=total_conversations,
        unanswered_count=total_conversations - answered_conversations,
        kb_entry_count=kb_entry_count,
        fresh_entry_count=fresh_entry_count,
    )

    # Coverage: answered / total
    if total_conversations > 0:
        breakdown.coverage = answered_conversations / total_conversations
    else:
        breakdown.coverage = 1.0  # No conversations = no gaps

    # Relevance: direct avg (already 0-1)
    breakdown.relevance = max(0.0, min(1.0, avg_relevance))

    # Escalation: inverted rate (1.0 = no escalations)
    if total_conversations > 0:
        esc_rate = escalation_count / total_conversations
        breakdown.escalation = 1.0 - esc_rate
    else:
        breakdown.escalation = 1.0

    # Freshness: fraction of entries updated recently
    if kb_entry_count > 0:
        breakdown.freshness = fresh_entry_count / kb_entry_count
    else:
        breakdown.freshness = 0.0  # No KB = 0 freshness

    # Composite (0-100)
    raw = (
        WEIGHT_COVERAGE * breakdown.coverage
        + WEIGHT_RELEVANCE * breakdown.relevance
        + WEIGHT_ESCALATION * breakdown.escalation
        + WEIGHT_FRESHNESS * breakdown.freshness
    )
    breakdown.composite = round(raw * 100, 1)

    return breakdown


# ---------------------------------------------------------------------------
# Trend computation
# ---------------------------------------------------------------------------

def compute_trend(
    current: float,
    previous: float | None,
) -> dict[str, Any]:
    """Compute trend direction and delta."""
    if previous is None:
        return {"direction": "=", "delta": 0.0, "previous": None}
    delta = current - previous
    if abs(delta) < 0.5:
        direction = "="
    elif delta > 0:
        direction = "up"
    else:
        direction = "down"
    return {"direction": direction, "delta": round(delta, 1), "previous": round(previous, 1)}


# ---------------------------------------------------------------------------
# Gap detection & clustering
# ---------------------------------------------------------------------------

@dataclass
class GapCluster:
    """A cluster of unanswered questions grouped by intent."""
    intent: str
    sample_question: str
    frequency: int
    last_occurrence: str  # ISO 8601
    conversation_ids: list[str] = field(default_factory=list)
    suggested_action: str = ""
    priority_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "sample_question": self.sample_question,
            "frequency": self.frequency,
            "last_occurrence": self.last_occurrence,
            "suggested_action": self.suggested_action,
            "priority_score": round(self.priority_score, 2),
            "conversation_ids": self.conversation_ids[:5],  # Limit sample
        }


def classify_unanswered(
    conversation: dict[str, Any],
) -> bool:
    """Determine if a conversation is 'unanswered' based on knowledge resolution.

    A conversation is unanswered when:
    - KR returned 0 sources, OR
    - All KR sources have relevance_score < RELEVANCE_THRESHOLD, OR
    - Conversation ended in escalation/error status
    """
    status = conversation.get("status", "")
    if status in ("escalated", "error"):
        return True

    # Check pipeline_trace for knowledge resolution quality
    trace = conversation.get("pipeline_trace") or {}
    # If no trace, we can't determine — treat as potentially answered
    if not trace:
        return False

    # Check if we have knowledge source info in metadata
    metadata = conversation.get("metadata") or {}
    sources = metadata.get("sources") or []

    if not sources:
        # No structured sources — check if intent was knowledge-seeking
        intent = trace.get("detected_intent") or trace.get("intent", "")
        # Greetings and farewells don't need KB answers
        if intent in ("greeting", "farewell", "thanks"):
            return False
        # For other intents, absence of sources in a knowledge-seeking
        # context indicates a potential gap
        return True

    # All sources below threshold
    if all(s.get("relevance_score", 0) < RELEVANCE_THRESHOLD for s in sources if isinstance(s, dict)):
        return True

    return False


def cluster_gaps(
    unanswered_conversations: list[dict[str, Any]],
    *,
    now: datetime | None = None,
) -> list[GapCluster]:
    """Group unanswered conversations by detected intent and compute priority.

    Priority = frequency * recency_weight where recency_weight decays
    for older conversations (exponential with 7-day half-life).
    """
    if now is None:
        now = datetime.now(timezone.utc)

    # Group by intent
    by_intent: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for conv in unanswered_conversations:
        trace = conv.get("pipeline_trace") or {}
        intent = trace.get("detected_intent") or trace.get("intent", "unknown")
        by_intent[intent].append(conv)

    clusters: list[GapCluster] = []
    for intent, convs in by_intent.items():
        # Find most recent occurrence
        timestamps = []
        for c in convs:
            ts = c.get("started_at") or c.get("last_activity_at") or ""
            if ts:
                timestamps.append(ts)

        last_occurrence = max(timestamps) if timestamps else now.isoformat()

        # Sample question from most recent conversation
        latest = max(convs, key=lambda c: c.get("started_at", ""), default=convs[0])
        # Use the first customer message or conversation metadata
        sample_q = latest.get("first_message") or latest.get("customer_message") or f"[{intent}]"

        # Compute priority: frequency * recency_weight
        frequency = len(convs)
        try:
            last_dt = datetime.fromisoformat(last_occurrence.replace("Z", "+00:00"))
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            days_ago = (now - last_dt).total_seconds() / 86400
        except (ValueError, TypeError):
            days_ago = 30.0
        recency_weight = 2 ** (-days_ago / 7.0)  # 7-day half-life
        priority_score = frequency * recency_weight

        # Suggest KB action
        suggested_action = _suggest_action(intent, convs)

        clusters.append(GapCluster(
            intent=intent,
            sample_question=sample_q[:200],
            frequency=frequency,
            last_occurrence=last_occurrence,
            conversation_ids=[c.get("conversation_id", "") for c in convs[:5]],
            suggested_action=suggested_action,
            priority_score=priority_score,
        ))

    # Sort by priority (descending)
    clusters.sort(key=lambda c: c.priority_score, reverse=True)
    return clusters


def _suggest_action(intent: str, conversations: list[dict[str, Any]]) -> str:
    """Generate a suggested KB action based on the gap pattern."""
    # Simple heuristic based on intent classification
    intent_lower = intent.lower()

    if any(kw in intent_lower for kw in ("product", "item", "price", "stock", "inventory")):
        return "Add product information entry"
    if any(kw in intent_lower for kw in ("return", "refund", "exchange", "warranty")):
        return "Add returns/refund policy FAQ"
    if any(kw in intent_lower for kw in ("shipping", "delivery", "tracking", "order")):
        return "Add shipping/delivery FAQ"
    if any(kw in intent_lower for kw in ("discount", "coupon", "promo", "sale")):
        return "Add promotions/discounts FAQ"
    if any(kw in intent_lower for kw in ("contact", "support", "help", "agent")):
        return "Review escalation paths — ensure human handoff is smooth"
    if any(kw in intent_lower for kw in ("account", "login", "password", "sign")):
        return "Add account management FAQ"

    # Frequency-based suggestion
    if len(conversations) >= 5:
        return f"Add FAQ entry — {len(conversations)} customers asked about this"
    return "Add FAQ entry for this topic"
