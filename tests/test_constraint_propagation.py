"""Tests for F4-A: Cross-Cutting Constraint Propagation (Phase A — Read-Only)."""

from __future__ import annotations

import pytest

from groundtruth_kb.db import KnowledgeDB


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


class TestF4AConstraintPropagation:
    """Tests for F4-A: advisory constraint lookup and coverage reporting."""

    def test_f4a_advisory_lookup(self, db):
        """ADR in matching section is returned by check_constraints_for_spec."""
        db.insert_spec(
            id="ADR-001",
            title="Tenant Isolation",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="data-access",
            type="architecture_decision",
        )
        db.insert_spec(
            id="SPEC-001",
            title="User Query",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="data-access",
        )
        constraints = db.check_constraints_for_spec("SPEC-001")
        ids = [c["id"] for c in constraints]
        assert "ADR-001" in ids

    def test_f4a_non_matching_skip(self, db):
        """Spec in different section does not match constraint."""
        db.insert_spec(
            id="ADR-002",
            title="Auth Decision",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="auth",
            type="architecture_decision",
        )
        db.insert_spec(
            id="SPEC-002",
            title="UI Component",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="frontend",
        )
        constraints = db.check_constraints_for_spec("SPEC-002")
        ids = [c["id"] for c in constraints]
        assert "ADR-002" not in ids

    def test_f4a_coverage_report(self, db):
        """get_constraint_coverage reports covered and uncovered sections."""
        db.insert_spec(
            id="ADR-003",
            title="API Design",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="api",
            type="architecture_decision",
        )
        db.insert_spec(
            id="SPEC-003",
            title="API Endpoint",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="api",
        )
        db.insert_spec(
            id="SPEC-004",
            title="Widget Style",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="frontend",
        )
        coverage = db.get_constraint_coverage()
        assert "api" in coverage["covered_sections"]
        assert "frontend" in coverage["uncovered_sections"]
        assert coverage["coverage_ratio"] > 0
        assert coverage["constraint_count"] >= 1

    def test_f4a_adr_and_dcl_filtering(self, db):
        """Both ADR and DCL types are returned, distinguishable."""
        db.insert_spec(
            id="ADR-004",
            title="Storage Decision",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="storage",
            type="architecture_decision",
        )
        db.insert_spec(
            id="DCL-001",
            title="Query Constraint",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="storage",
            type="design_constraint",
        )
        constraints = db.check_constraints_for_spec(section="storage")
        types = {c["type"] for c in constraints}
        assert "architecture_decision" in types
        assert "design_constraint" in types

    def test_f4a_empty_result(self, db):
        """No ADR/DCL specs exist — both methods return empty."""
        db.insert_spec(
            id="SPEC-005",
            title="Regular Spec",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="auth",
        )
        constraints = db.check_constraints_for_spec("SPEC-005")
        assert constraints == []

        coverage = db.get_constraint_coverage()
        assert coverage["constraint_count"] == 0
        assert coverage["coverage_ratio"] == 0

    def test_f4a_multiple_constraints(self, db):
        """Multiple constraints overlapping same section all returned."""
        for i in range(1, 4):
            db.insert_spec(
                id=f"ADR-01{i}",
                title=f"Decision {i}",
                status="specified",
                changed_by="test",
                change_reason="test",
                section="core",
                type="architecture_decision",
            )
        constraints = db.check_constraints_for_spec(section="core")
        assert len(constraints) >= 3
