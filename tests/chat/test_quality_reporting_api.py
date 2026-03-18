"""CQ-9: Quality reporting API model tests (SPEC-0188 / WI-1519).

Tests for QualityConversationEntry and QualitySummaryResponse models.
Endpoint integration tests require Cosmos — these are model-level unit tests.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from src.multi_tenant.superadmin_api._quality import (
    QualityConversationEntry,
    QualitySummaryResponse,
)


# ---------------------------------------------------------------------------
# QualityConversationEntry model
# ---------------------------------------------------------------------------


class TestQualityConversationEntry:
    """QualityConversationEntry model validation."""

    def test_basic_entry(self):
        entry = QualityConversationEntry(
            conversation_id="conv-123",
            overall_score=4.2,
            turn_count=5,
            scored_at="2026-03-17T12:00:00+00:00",
        )
        assert entry.conversation_id == "conv-123"
        assert entry.overall_score == 4.2
        assert entry.turn_count == 5

    def test_defaults(self):
        entry = QualityConversationEntry(
            conversation_id="conv-456",
            overall_score=3.0,
        )
        assert entry.turn_count == 0
        assert entry.scored_at == ""

    def test_camel_case_serialization(self):
        entry = QualityConversationEntry(
            conversation_id="conv-789",
            overall_score=4.5,
            turn_count=3,
        )
        data = entry.model_dump(by_alias=True)
        assert "conversationId" in data or "conversation_id" in data


# ---------------------------------------------------------------------------
# QualitySummaryResponse model
# ---------------------------------------------------------------------------


class TestQualitySummaryResponse:
    """QualitySummaryResponse model validation."""

    def test_basic_summary(self):
        summary = QualitySummaryResponse(
            mean_overall=4.1,
            trend="improving",
            score_distribution={"1-2": 2, "2-3": 5, "3-4": 15, "4-5": 28},
            total_scored=50,
            period_days=30,
        )
        assert summary.mean_overall == 4.1
        assert summary.trend == "improving"
        assert summary.total_scored == 50

    def test_empty_summary(self):
        summary = QualitySummaryResponse(
            mean_overall=0.0,
            trend="stable",
            score_distribution={"1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0},
            total_scored=0,
        )
        assert summary.total_scored == 0
        assert summary.period_days == 30  # default

    def test_declining_trend(self):
        summary = QualitySummaryResponse(
            mean_overall=2.8,
            trend="declining",
            score_distribution={"1-2": 10, "2-3": 20, "3-4": 5, "4-5": 2},
            total_scored=37,
            period_days=7,
        )
        assert summary.trend == "declining"
        assert summary.period_days == 7

    def test_distribution_sums_to_total(self):
        dist = {"1-2": 5, "2-3": 10, "3-4": 20, "4-5": 15}
        summary = QualitySummaryResponse(
            mean_overall=3.5,
            trend="stable",
            score_distribution=dist,
            total_scored=50,
        )
        assert sum(summary.score_distribution.values()) == 50

    def test_score_distribution_is_dict(self):
        summary = QualitySummaryResponse(
            mean_overall=3.0,
            trend="stable",
            score_distribution={"1-2": 0, "2-3": 0, "3-4": 0, "4-5": 0},
            total_scored=0,
        )
        assert isinstance(summary.score_distribution, dict)
        assert "1-2" in summary.score_distribution
        assert "4-5" in summary.score_distribution
