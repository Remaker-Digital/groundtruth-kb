"""Tests for F4: Cross-Cutting Constraint Propagation (Phase A + B)."""

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


class TestF4BConstraintPropagation:
    """Tests for F4-B: constraint linkage writes via propagate_constraint()."""

    def _setup_constraint(self, db, section="data-access"):
        """Create an ADR + functional specs in the same section."""
        db.insert_spec(
            id="ADR-100",
            title="Isolation Policy",
            status="specified",
            changed_by="test",
            change_reason="test",
            section=section,
            type="architecture_decision",
        )
        db.insert_spec(
            id="SPEC-100",
            title="User Query",
            status="specified",
            changed_by="test",
            change_reason="test",
            section=section,
        )
        db.insert_spec(
            id="SPEC-101",
            title="Data Export",
            status="specified",
            changed_by="test",
            change_reason="test",
            section=section,
        )

    def test_f4b_dry_run_propagation(self, db):
        """Dry-run reports affected specs without creating new versions."""
        self._setup_constraint(db)
        v_before = db.get_spec("SPEC-100")["version"]

        result = db.propagate_constraint("ADR-100", dry_run=True)
        assert result["dry_run"] is True
        assert result["newly_linked"] == 2
        assert result["already_linked"] == 0
        ids = [a["id"] for a in result["affected_specs"]]
        assert "SPEC-100" in ids
        assert "SPEC-101" in ids

        # No version change
        assert db.get_spec("SPEC-100")["version"] == v_before

    def test_f4b_write_propagation(self, db):
        """Write propagation creates new versions with affected_by linkage."""
        self._setup_constraint(db)

        result = db.propagate_constraint("ADR-100", dry_run=False)
        assert result["newly_linked"] == 2
        assert result["dry_run"] is False

        spec = db.get_spec("SPEC-100")
        assert "ADR-100" in (spec.get("affected_by_parsed") or [])

    def test_f4b_already_linked_skip(self, db):
        """Second propagation shows already_linked, no new versions."""
        self._setup_constraint(db)
        db.propagate_constraint("ADR-100", dry_run=False)
        v_after_first = db.get_spec("SPEC-100")["version"]

        result = db.propagate_constraint("ADR-100", dry_run=False)
        assert result["already_linked"] == 2
        assert result["newly_linked"] == 0

        # No version change
        assert db.get_spec("SPEC-100")["version"] == v_after_first

    def test_f4b_excludes_constraint_peers(self, db):
        """Propagation returns only functional specs, not ADR/DCL peers."""
        self._setup_constraint(db)
        db.insert_spec(
            id="DCL-100",
            title="Query Limit",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="data-access",
            type="design_constraint",
        )

        result = db.propagate_constraint("ADR-100", dry_run=True)
        ids = [a["id"] for a in result["affected_specs"]]
        assert "DCL-100" not in ids
        assert "ADR-100" not in ids
        assert "SPEC-100" in ids

    def test_f4b_link_removal_with_reason(self, db):
        """Removing a link creates a new version with change_reason."""
        self._setup_constraint(db)
        db.propagate_constraint("ADR-100", dry_run=False)
        v_before = db.get_spec("SPEC-100")["version"]

        result = db.remove_constraint_link(
            "SPEC-100",
            "ADR-100",
            change_reason="Scope narrowing: SPEC-100 no longer in isolation scope",
        )
        assert result["removed"] is True

        spec = db.get_spec("SPEC-100")
        assert "ADR-100" not in (spec.get("affected_by_parsed") or [])
        assert spec["version"] == v_before + 1
        assert spec["change_reason"] == "Scope narrowing: SPEC-100 no longer in isolation scope"

    def test_f4b_link_removal_idempotent(self, db):
        """Removing a constraint not in affected_by returns removed=False."""
        self._setup_constraint(db)

        result = db.remove_constraint_link(
            "SPEC-100",
            "ADR-999",
            change_reason="test removal",
        )
        assert result["removed"] is False

    def test_f4b_append_only_versioning(self, db):
        """Propagation creates version N+1; original version preserved."""
        self._setup_constraint(db)
        v_original = db.get_spec("SPEC-100")["version"]

        db.propagate_constraint("ADR-100", dry_run=False)
        spec = db.get_spec("SPEC-100")
        assert spec["version"] == v_original + 1

        # Original version still in history
        history = db.get_spec_history("SPEC-100")
        versions = [h["version"] for h in history]
        assert v_original in versions
        assert v_original + 1 in versions

    def test_f4b_changed_by_and_reason_audit(self, db):
        """New version has changed_by='constraint-propagation' and non-empty reason."""
        self._setup_constraint(db)
        db.propagate_constraint("ADR-100", dry_run=False)

        spec = db.get_spec("SPEC-100")
        assert spec["changed_by"] == "constraint-propagation"
        assert "ADR-100" in spec["change_reason"]
        assert len(spec["change_reason"]) > 0
