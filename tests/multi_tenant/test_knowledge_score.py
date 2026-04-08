"""Tests for Knowledge Score Service (SPEC-1873).

Covers: score computation, factor weights, gap detection, intent clustering,
priority scoring, trend computation, and suggested actions.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone


from src.multi_tenant.knowledge_score import (
    GapCluster,
    classify_unanswered,
    cluster_gaps,
    compute_knowledge_score,
    compute_trend,
)


# ---------------------------------------------------------------------------
# Score computation
# ---------------------------------------------------------------------------


class TestKnowledgeScoreComputation:
    """TEST-11031 through TEST-11035: Knowledge score factor tests."""

    def test_perfect_score(self):
        """All factors at maximum produce score of 100."""
        breakdown = compute_knowledge_score(
            total_conversations=100,
            answered_conversations=100,
            avg_relevance=1.0,
            escalation_count=0,
            kb_entry_count=50,
            fresh_entry_count=50,
        )
        assert breakdown.composite == 100.0
        assert breakdown.coverage == 1.0
        assert breakdown.relevance == 1.0
        assert breakdown.escalation == 1.0
        assert breakdown.freshness == 1.0

    def test_zero_score(self):
        """All factors at minimum produce score near 0."""
        breakdown = compute_knowledge_score(
            total_conversations=100,
            answered_conversations=0,
            avg_relevance=0.0,
            escalation_count=100,
            kb_entry_count=0,
            fresh_entry_count=0,
        )
        assert breakdown.composite == 0.0

    def test_coverage_factor_reflects_ratio(self):
        """TEST-11032: Coverage factor = answered / total."""
        breakdown = compute_knowledge_score(
            total_conversations=100,
            answered_conversations=80,
            avg_relevance=0.5,
            escalation_count=20,
            kb_entry_count=10,
            fresh_entry_count=5,
        )
        assert abs(breakdown.coverage - 0.80) < 0.05

    def test_relevance_factor_reflects_avg(self):
        """TEST-11033: Relevance factor = avg KR relevance."""
        breakdown = compute_knowledge_score(
            total_conversations=100,
            answered_conversations=90,
            avg_relevance=0.75,
            escalation_count=10,
            kb_entry_count=10,
            fresh_entry_count=5,
        )
        assert abs(breakdown.relevance - 0.75) < 0.05

    def test_escalation_factor_inverted(self):
        """TEST-11034: Escalation factor = 1 - escalation_rate."""
        breakdown = compute_knowledge_score(
            total_conversations=100,
            answered_conversations=90,
            avg_relevance=0.5,
            escalation_count=10,
            kb_entry_count=10,
            fresh_entry_count=5,
        )
        assert abs(breakdown.escalation - 0.90) < 0.05

    def test_freshness_factor_reflects_ratio(self):
        """TEST-11035: Freshness factor = fresh_entries / total_entries."""
        breakdown = compute_knowledge_score(
            total_conversations=100,
            answered_conversations=80,
            avg_relevance=0.5,
            escalation_count=20,
            kb_entry_count=100,
            fresh_entry_count=70,
        )
        assert abs(breakdown.freshness - 0.70) < 0.05

    def test_no_conversations_defaults_high(self):
        """No conversations = no gaps, so coverage and escalation default high."""
        breakdown = compute_knowledge_score(
            total_conversations=0,
            answered_conversations=0,
            avg_relevance=0.5,
            escalation_count=0,
            kb_entry_count=10,
            fresh_entry_count=5,
        )
        assert breakdown.coverage == 1.0
        assert breakdown.escalation == 1.0

    def test_no_kb_entries_zero_freshness(self):
        """No KB entries = 0 freshness."""
        breakdown = compute_knowledge_score(
            total_conversations=10,
            answered_conversations=8,
            avg_relevance=0.5,
            escalation_count=2,
            kb_entry_count=0,
            fresh_entry_count=0,
        )
        assert breakdown.freshness == 0.0

    def test_to_dict_structure(self):
        """to_dict returns expected keys."""
        breakdown = compute_knowledge_score(
            total_conversations=50,
            answered_conversations=40,
            avg_relevance=0.7,
            escalation_count=10,
            kb_entry_count=20,
            fresh_entry_count=15,
        )
        d = breakdown.to_dict()
        assert "score" in d
        assert "factors" in d
        assert set(d["factors"].keys()) == {"coverage", "relevance", "escalation_rate", "freshness"}
        assert 0 <= d["score"] <= 100

    def test_weight_sum(self):
        """Factor weights must sum to 1.0."""
        from src.multi_tenant.knowledge_score import (
            WEIGHT_COVERAGE,
            WEIGHT_ESCALATION,
            WEIGHT_FRESHNESS,
            WEIGHT_RELEVANCE,
        )
        total = WEIGHT_COVERAGE + WEIGHT_RELEVANCE + WEIGHT_ESCALATION + WEIGHT_FRESHNESS
        assert abs(total - 1.0) < 0.001


# ---------------------------------------------------------------------------
# Gap detection
# ---------------------------------------------------------------------------


class TestGapDetection:
    """TEST-11038, TEST-11039: Gap detection identifies unanswered conversations."""

    def test_escalated_conversation_is_unanswered(self):
        conv = {"status": "escalated", "pipeline_trace": {}}
        assert classify_unanswered(conv) is True

    def test_error_conversation_is_unanswered(self):
        conv = {"status": "error", "pipeline_trace": {}}
        assert classify_unanswered(conv) is True

    def test_zero_sources_is_unanswered(self):
        """TEST-11038: Conversation with 0 KR sources."""
        conv = {
            "status": "ended",
            "pipeline_trace": {"intent": "product_inquiry"},
            "metadata": {"sources": []},
        }
        assert classify_unanswered(conv) is True

    def test_low_relevance_is_unanswered(self):
        """TEST-11039: All sources below relevance threshold."""
        conv = {
            "status": "ended",
            "pipeline_trace": {"intent": "product_inquiry"},
            "metadata": {
                "sources": [
                    {"title": "A", "relevance_score": 0.1},
                    {"title": "B", "relevance_score": 0.2},
                ],
            },
        }
        assert classify_unanswered(conv) is True

    def test_good_relevance_is_answered(self):
        conv = {
            "status": "ended",
            "pipeline_trace": {"intent": "product_inquiry"},
            "metadata": {
                "sources": [
                    {"title": "A", "relevance_score": 0.8},
                ],
            },
        }
        assert classify_unanswered(conv) is False

    def test_greeting_without_sources_is_answered(self):
        """Greetings don't need KB answers."""
        conv = {
            "status": "ended",
            "pipeline_trace": {"intent": "greeting"},
            "metadata": {"sources": []},
        }
        assert classify_unanswered(conv) is False

    def test_no_trace_defaults_answered(self):
        """No pipeline trace = can't determine, treat as answered."""
        conv = {"status": "ended", "pipeline_trace": None}
        assert classify_unanswered(conv) is False


# ---------------------------------------------------------------------------
# Clustering
# ---------------------------------------------------------------------------


class TestGapClustering:
    """TEST-11037, TEST-11040, TEST-11041: Gap clustering and prioritization."""

    def test_clusters_by_intent(self):
        """TEST-11037: Gaps grouped by detected intent."""
        now = datetime(2026, 3, 30, tzinfo=timezone.utc)
        convs = [
            {"conversation_id": "c1", "status": "escalated",
             "pipeline_trace": {"detected_intent": "returns"},
             "started_at": "2026-03-29T12:00:00+00:00"},
            {"conversation_id": "c2", "status": "escalated",
             "pipeline_trace": {"detected_intent": "returns"},
             "started_at": "2026-03-28T12:00:00+00:00"},
            {"conversation_id": "c3", "status": "escalated",
             "pipeline_trace": {"detected_intent": "shipping"},
             "started_at": "2026-03-30T12:00:00+00:00"},
        ]
        clusters = cluster_gaps(convs, now=now)
        intents = {c.intent for c in clusters}
        assert "returns" in intents
        assert "shipping" in intents

    def test_sorted_by_priority(self):
        """TEST-11040: Clusters sorted by frequency * recency."""
        now = datetime(2026, 3, 30, tzinfo=timezone.utc)
        convs = []
        # 10 recent "returns" conversations
        for i in range(10):
            convs.append({
                "conversation_id": f"ret-{i}", "status": "escalated",
                "pipeline_trace": {"detected_intent": "returns"},
                "started_at": "2026-03-29T12:00:00+00:00",
            })
        # 2 old "shipping" conversations
        for i in range(2):
            convs.append({
                "conversation_id": f"ship-{i}", "status": "escalated",
                "pipeline_trace": {"detected_intent": "shipping"},
                "started_at": "2026-03-01T12:00:00+00:00",
            })
        clusters = cluster_gaps(convs, now=now)
        assert clusters[0].intent == "returns"
        assert clusters[0].frequency == 10

    def test_suggested_action_present(self):
        """TEST-11041: Gap clusters have suggested actions."""
        now = datetime(2026, 3, 30, tzinfo=timezone.utc)
        convs = [
            {"conversation_id": "c1", "status": "escalated",
             "pipeline_trace": {"detected_intent": "returns_policy"},
             "started_at": "2026-03-29T12:00:00+00:00"},
        ]
        clusters = cluster_gaps(convs, now=now)
        assert len(clusters) == 1
        assert clusters[0].suggested_action  # Non-empty

    def test_to_dict_structure(self):
        cluster = GapCluster(
            intent="product_inquiry",
            sample_question="Where is my order?",
            frequency=5,
            last_occurrence="2026-03-30T12:00:00+00:00",
            conversation_ids=["c1", "c2"],
            suggested_action="Add shipping FAQ",
            priority_score=4.5,
        )
        d = cluster.to_dict()
        assert d["intent"] == "product_inquiry"
        assert d["frequency"] == 5
        assert d["suggested_action"] == "Add shipping FAQ"


# ---------------------------------------------------------------------------
# Trend
# ---------------------------------------------------------------------------


class TestTrend:
    """TEST-11043: Knowledge score trend computation."""

    def test_improving_trend(self):
        trend = compute_trend(85.0, 75.0)
        assert trend["direction"] == "up"
        assert trend["delta"] == 10.0

    def test_declining_trend(self):
        trend = compute_trend(65.0, 80.0)
        assert trend["direction"] == "down"
        assert trend["delta"] == -15.0

    def test_stable_trend(self):
        trend = compute_trend(80.0, 80.2)
        assert trend["direction"] == "="

    def test_no_previous(self):
        trend = compute_trend(80.0, None)
        assert trend["direction"] == "="
        assert trend["previous"] is None
