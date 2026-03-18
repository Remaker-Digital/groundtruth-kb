"""Tests for SPEC-1841: Untested Spec Backfill Program.

Verifies risk tier classification, untested spec identification,
and skeleton test generation.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.quality_metrics.backfill_untested_specs import (
    RISK_TIERS,
    classify_risk_tier,
    find_untested_specs,
    get_backfill_summary,
)


class TestRiskTierClassification:
    """SPEC-1841: Risk tier classification."""

    def test_four_risk_tiers(self):
        assert set(RISK_TIERS.keys()) == {"critical", "high", "medium", "low"}

    def test_auth_spec_is_critical(self):
        spec = {"title": "Authentication middleware", "description": "Handles auth"}
        assert classify_risk_tier(spec) == "critical"

    def test_chat_spec_is_critical(self):
        spec = {"title": "Chat endpoint", "description": "Customer chat"}
        assert classify_risk_tier(spec) == "critical"

    def test_api_spec_is_high(self):
        spec = {"title": "API rate limiting", "description": "Rate limit config"}
        assert classify_risk_tier(spec) == "high"

    def test_admin_spec_is_medium(self):
        spec = {"title": "Superadmin diagnostics", "description": "Admin monitoring"}
        assert classify_risk_tier(spec) == "medium"

    def test_unknown_spec_is_low(self):
        spec = {"title": "Documentation format", "description": "Internal docs"}
        assert classify_risk_tier(spec) == "low"


class TestFindUntestedSpecs:
    """Find and classify untested specs."""

    def test_filters_to_implemented_verified(self):
        mock_kb = MagicMock()
        mock_kb.get_untested_specs.return_value = [
            {"id": "SPEC-1", "status": "implemented", "title": "Chat auth"},
            {"id": "SPEC-2", "status": "specified", "title": "Future feature"},
            {"id": "SPEC-3", "status": "verified", "title": "Rate limiter"},
        ]
        result = find_untested_specs(mock_kb)
        assert len(result) == 2
        assert all(s["status"] in ("implemented", "verified") for s in result)

    def test_adds_risk_tier(self):
        mock_kb = MagicMock()
        mock_kb.get_untested_specs.return_value = [
            {"id": "SPEC-1", "status": "implemented", "title": "Auth module"},
        ]
        result = find_untested_specs(mock_kb)
        assert result[0]["risk_tier"] == "critical"

    def test_sorted_by_risk_tier(self):
        mock_kb = MagicMock()
        mock_kb.get_untested_specs.return_value = [
            {"id": "SPEC-1", "status": "implemented", "title": "Documentation"},
            {"id": "SPEC-2", "status": "implemented", "title": "Chat widget"},
            {"id": "SPEC-3", "status": "implemented", "title": "API endpoint"},
        ]
        result = find_untested_specs(mock_kb)
        tiers = [s["risk_tier"] for s in result]
        tier_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        assert tiers == sorted(tiers, key=lambda t: tier_order[t])


class TestBackfillSummary:
    """get_backfill_summary for reporting."""

    def test_summary_structure(self):
        mock_kb = MagicMock()
        mock_kb.get_untested_specs.return_value = [
            {"id": "SPEC-1", "status": "implemented", "title": "Auth"},
            {"id": "SPEC-2", "status": "implemented", "title": "Docs format"},
        ]
        summary = get_backfill_summary(mock_kb)
        assert "total_untested" in summary
        assert "by_tier" in summary
        assert "top_5_critical" in summary
        assert summary["total_untested"] == 2
