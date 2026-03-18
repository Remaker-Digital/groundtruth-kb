"""Tests for SPEC-1838: Quality scores KB table (WI-1463).

Verifies that quality_scores table exists in schema, and
insert/get methods work correctly.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB, SCHEMA_SQL


class TestQualityScoresSchema:
    """WI-1463: quality_scores table in KB schema."""

    def test_schema_has_quality_scores_table(self):
        assert "CREATE TABLE IF NOT EXISTS quality_scores" in SCHEMA_SQL

    def test_schema_has_session_id_unique(self):
        assert "UNIQUE(session_id)" in SCHEMA_SQL

    def test_schema_has_all_metric_columns(self):
        for col in ["spec_coverage", "defect_escape_rate", "assertion_strength",
                     "change_failure_rate", "test_freshness", "coverage_delta",
                     "composite_score"]:
            assert col in SCHEMA_SQL, f"Missing column: {col}"

    def test_schema_has_details_json(self):
        assert "details TEXT" in SCHEMA_SQL


class TestQualityScoresCRUD:
    """WI-1463: Insert and query quality scores."""

    @pytest.fixture
    def kb(self, tmp_path):
        """Create a temporary KB for testing."""
        db_path = tmp_path / "test.db"
        return KnowledgeDB(str(db_path))

    def test_insert_and_get(self, kb):
        result = kb.insert_quality_score(
            session_id="S200",
            spec_coverage=0.85,
            defect_escape_rate=0.02,
            assertion_strength=0.70,
            change_failure_rate=0.03,
            test_freshness=0.95,
            coverage_delta=2.0,
            composite_score=88.5,
            details={"weights": {"spec_coverage": 0.20}},
        )
        assert result["session_id"] == "S200"
        assert result["composite_score"] == 88.5

        fetched = kb.get_quality_score("S200")
        assert fetched is not None
        assert fetched["spec_coverage"] == 0.85

    def test_get_nonexistent_returns_none(self, kb):
        assert kb.get_quality_score("S999") is None

    def test_get_quality_scores_returns_multiple(self, kb):
        """get_quality_scores(last=N) returns up to N records."""
        for i in range(5):
            kb.insert_quality_score(
                session_id=f"S{200+i}",
                spec_coverage=0.80 + i * 0.01,
                defect_escape_rate=0.02,
                assertion_strength=0.70,
                change_failure_rate=0.03,
                test_freshness=0.95,
                coverage_delta=float(i),
                composite_score=85.0 + i,
            )

        scores = kb.get_quality_scores(last=3)
        assert len(scores) == 3
        # All 5 inserted, only 3 returned
        all_scores = kb.get_quality_scores(last=10)
        assert len(all_scores) == 5

    def test_upsert_same_session(self, kb):
        """INSERT OR REPLACE allows updating same session."""
        kb.insert_quality_score(
            session_id="S200",
            spec_coverage=0.80,
            defect_escape_rate=0.02,
            assertion_strength=0.70,
            change_failure_rate=0.03,
            test_freshness=0.95,
            coverage_delta=1.0,
            composite_score=85.0,
        )
        kb.insert_quality_score(
            session_id="S200",
            spec_coverage=0.85,
            defect_escape_rate=0.01,
            assertion_strength=0.75,
            change_failure_rate=0.02,
            test_freshness=0.96,
            coverage_delta=2.0,
            composite_score=90.0,
        )
        fetched = kb.get_quality_score("S200")
        assert fetched["composite_score"] == 90.0
