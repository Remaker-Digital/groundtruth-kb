"""Tests for F2-A: Change Impact Analysis (Phase A).

15 test cases per approved v6 scope (bridge/gtkb-spec-pipeline-f2-011.md).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest

from groundtruth_kb.assertions import AssertionTarget, _extract_assertion_targets
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.impact import ImpactConfig


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


def _insert_spec(db, id, section, assertions=None, **kw):
    """Helper to insert a spec with optional assertions list."""
    kw.setdefault("title", f"Spec {id}")
    kw.setdefault("status", "specified")
    kw.setdefault("changed_by", "test")
    kw.setdefault("change_reason", "test")
    return db.insert_spec(
        id=id,
        section=section,
        assertions=assertions,
        **kw,
    )


class TestF2AChangeImpactAnalysis:
    """15 tests for F2-A: Change Impact Analysis Phase A."""

    # ------------------------------------------------------------------
    # 1. Contained blast radius
    # ------------------------------------------------------------------
    def test_contained_blast_radius(self, db):
        """3 specs in section; add 4th; blast_radius='contained'."""
        for i in range(3):
            _insert_spec(db, f"SPEC-{i}", "widget")
        _insert_spec(db, "SPEC-TARGET", "widget")

        result = db.compute_impact("SPEC-TARGET")
        assert result["blast_radius"] == "contained"
        assert result["related_spec_count"] == 3

    # ------------------------------------------------------------------
    # 2. Systemic blast radius
    # ------------------------------------------------------------------
    def test_systemic_blast_radius(self, db):
        """25 specs in section; add 26th; blast_radius='systemic'."""
        for i in range(25):
            _insert_spec(db, f"SPEC-{i}", "core")
        _insert_spec(db, "SPEC-TARGET", "core")

        result = db.compute_impact("SPEC-TARGET")
        assert result["blast_radius"] == "systemic"
        assert result["related_spec_count"] == 25

    # ------------------------------------------------------------------
    # 3. Constraint detection
    # ------------------------------------------------------------------
    def test_constraint_detection(self, db):
        """ADR + matching-tag spec; applicable_constraints populated."""
        db.insert_spec(
            id="ADR-001",
            title="Tenant Isolation",
            status="specified",
            changed_by="test",
            change_reason="test",
            section="data-access",
            type="architecture_decision",
        )
        _insert_spec(db, "SPEC-TARGET", "data-access")

        result = db.compute_impact("SPEC-TARGET")
        constraint_ids = [c["id"] for c in result["applicable_constraints"]]
        assert "ADR-001" in constraint_ids
        assert result["touches_architecture"] is True

    # ------------------------------------------------------------------
    # 4. grep vs grep_absent conflict
    # ------------------------------------------------------------------
    def test_grep_vs_grep_absent_conflict(self, db):
        """Same file, same pattern; conflict flagged."""
        _insert_spec(
            db,
            "SPEC-A",
            "auth",
            assertions=[{"type": "grep", "file": "src/auth.py", "pattern": "def login"}],
        )
        _insert_spec(
            db,
            "SPEC-B",
            "auth",
            assertions=[{"type": "grep_absent", "file": "src/auth.py", "pattern": "def login"}],
        )

        result = db.compute_impact("SPEC-A")
        assert len(result["potential_conflicts"]) >= 1
        conflict = result["potential_conflicts"][0]
        assert conflict["file_target"] == "src/auth.py"
        assert conflict["match_target"] == "def login"

    # ------------------------------------------------------------------
    # 5. Non-machine skip
    # ------------------------------------------------------------------
    def test_non_machine_skip(self, db):
        """Visual assertion only; no conflict."""
        _insert_spec(
            db,
            "SPEC-A",
            "ui",
            assertions=[{"type": "visual", "description": "Check alignment"}],
        )
        _insert_spec(
            db,
            "SPEC-B",
            "ui",
            assertions=[{"type": "visual", "description": "Check color"}],
        )

        result = db.compute_impact("SPEC-A")
        assert result["potential_conflicts"] == []

    # ------------------------------------------------------------------
    # 6. Custom thresholds
    # ------------------------------------------------------------------
    def test_custom_thresholds(self, db):
        """ImpactConfig(contained_threshold=2); 3 related = 'moderate'."""
        for i in range(3):
            _insert_spec(db, f"SPEC-{i}", "payments")
        _insert_spec(db, "SPEC-TARGET", "payments")

        config = ImpactConfig(contained_threshold=2)
        result = db.compute_impact("SPEC-TARGET", config=config)
        assert result["blast_radius"] == "moderate"
        assert result["related_spec_count"] == 3


class TestF2AAssertionTargetExtraction:
    """Tests 7-15: typed AssertionTarget extraction and conflict edge cases."""

    # ------------------------------------------------------------------
    # 7. file_exists with path alias
    # ------------------------------------------------------------------
    def test_file_exists_path_alias(self):
        """file_exists with 'path' alias resolves to file_target."""
        assertion = {"type": "file_exists", "path": "src/main.py"}
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 1
        assert targets[0] == AssertionTarget(
            assertion_type="file_exists",
            file_target="src/main.py",
            file_is_glob=False,
        )

    # ------------------------------------------------------------------
    # 8. grep with target alias
    # ------------------------------------------------------------------
    def test_grep_target_alias(self):
        """grep with 'target' and 'query' aliases resolves correctly."""
        assertion = {"type": "grep", "target": "src/api.py", "query": "def handler"}
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 1
        assert targets[0] == AssertionTarget(
            assertion_type="grep",
            file_target="src/api.py",
            match_target="def handler",
            file_is_glob=False,
        )

    # ------------------------------------------------------------------
    # 9. json_path
    # ------------------------------------------------------------------
    def test_json_path_extraction(self):
        """json_path extracts file and dotted path as match_target."""
        assertion = {"type": "json_path", "file": "config.json", "path": "server.port"}
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 1
        assert targets[0].assertion_type == "json_path"
        assert targets[0].match_target == "server.port"
        assert targets[0].file_is_glob is False

    # ------------------------------------------------------------------
    # 10. json_path no-conflict
    # ------------------------------------------------------------------
    def test_json_path_no_conflict(self, db):
        """Two json_path: same file, different paths → no conflict."""
        _insert_spec(
            db,
            "SPEC-A",
            "config",
            assertions=[{"type": "json_path", "file": "config.json", "path": "server.port"}],
        )
        _insert_spec(
            db,
            "SPEC-B",
            "config",
            assertions=[{"type": "json_path", "file": "config.json", "path": "server.host"}],
        )

        result = db.compute_impact("SPEC-A")
        assert result["potential_conflicts"] == []

    # ------------------------------------------------------------------
    # 11. all_of composition
    # ------------------------------------------------------------------
    def test_all_of_composition(self):
        """all_of with 2 grep children; both typed targets in union."""
        assertion = {
            "type": "all_of",
            "assertions": [
                {"type": "grep", "file": "src/a.py", "pattern": "class A"},
                {"type": "grep", "file": "src/b.py", "pattern": "class B"},
            ],
        }
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 2
        files = {t.file_target for t in targets}
        assert files == {"src/a.py", "src/b.py"}

    # ------------------------------------------------------------------
    # 12. grep with file glob
    # ------------------------------------------------------------------
    def test_grep_file_glob(self):
        """grep with glob file pattern marks file_is_glob=True."""
        assertion = {"type": "grep", "file": "src/**/*.py", "pattern": "import os"}
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 1
        assert targets[0] == AssertionTarget(
            assertion_type="grep",
            file_target="src/**/*.py",
            match_target="import os",
            file_is_glob=True,
        )

    # ------------------------------------------------------------------
    # 13. Documented false-negative: literal vs file-glob
    # ------------------------------------------------------------------
    def test_literal_vs_glob_false_negative(self, db):
        """grep literal + grep glob, same pattern; NO conflict; annotation present."""
        _insert_spec(
            db,
            "SPEC-A",
            "imports",
            assertions=[{"type": "grep", "file": "src/api.py", "pattern": "import os"}],
        )
        _insert_spec(
            db,
            "SPEC-B",
            "imports",
            assertions=[{"type": "grep", "file": "src/**/*.py", "pattern": "import os"}],
        )

        result = db.compute_impact("SPEC-A")
        # No conflict flagged — this is the documented false-negative
        assert result["potential_conflicts"] == []
        # But an annotation documents the limitation
        assert any("file-glob limitation" in a for a in result["annotations"])

    # ------------------------------------------------------------------
    # 14. grep_absent with file glob
    # ------------------------------------------------------------------
    def test_grep_absent_file_glob(self):
        """grep_absent with glob file marks file_is_glob=True."""
        assertion = {"type": "grep_absent", "file": "src/**/*.py", "pattern": "import os"}
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 1
        assert targets[0] == AssertionTarget(
            assertion_type="grep_absent",
            file_target="src/**/*.py",
            match_target="import os",
            file_is_glob=True,
        )

    # ------------------------------------------------------------------
    # 15. count with file glob
    # ------------------------------------------------------------------
    def test_count_file_glob(self):
        """count with glob file marks file_is_glob=True."""
        assertion = {"type": "count", "file": "src/**/*.py", "pattern": "TODO"}
        targets = _extract_assertion_targets(assertion)
        assert len(targets) == 1
        assert targets[0] == AssertionTarget(
            assertion_type="count",
            file_target="src/**/*.py",
            match_target="TODO",
            file_is_glob=True,
        )
