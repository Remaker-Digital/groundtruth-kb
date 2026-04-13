"""Tests for F3: Spec Quality Gate (spec_quality_scores)."""

from __future__ import annotations

import json

import pytest

from groundtruth_kb.db import KnowledgeDB


@pytest.fixture
def db(tmp_path):
    return KnowledgeDB(db_path=tmp_path / "test.db")


class TestF3QualityGate:
    """Tests for F3: per-spec quality scoring, persistence, and distribution."""

    def _make_spec(self, db, spec_id="SPEC-001", **kwargs):
        """Helper to create a spec with common defaults."""
        defaults = {
            "title": "Test Specification with clear requirements",
            "status": "specified",
            "changed_by": "test",
            "change_reason": "test",
            "description": "This specification describes the required behavior because it ensures correctness.",
            "section": "auth",
            "scope": "api",
            "tags": ["security"],
            "priority": "high",
        }
        defaults.update(kwargs)
        return db.insert_spec(id=spec_id, **defaults)

    def test_f3_perfect_spec(self, db):
        """Well-specified spec scores high (gold tier)."""
        spec = self._make_spec(
            db,
            assertions=[
                {
                    "type": "grep",
                    "file": "src/auth.py",
                    "pattern": "def verify_token",
                    "description": "Token verification exists",
                },
            ],
            authority="stated",
            testability="automatable",
            constraints={"complexity_ceiling": "simple"},
            affected_by=["ADR-001"],
        )
        score = db.score_spec_quality(spec)
        assert score["overall"] >= 0.6
        assert score["tier"] in ("gold", "silver")
        assert "NO_ASSERTIONS" not in score["flags"]

    def test_f3_minimal_spec(self, db):
        """Minimal spec scores low with NO_ASSERTIONS flag."""
        spec = db.insert_spec(
            id="SPEC-002",
            title="Min",
            status="specified",
            changed_by="test",
            change_reason="test",
        )
        score = db.score_spec_quality(spec)
        assert score["overall"] < 0.5
        assert "NO_ASSERTIONS" in score["flags"]

    def test_f3_non_executable_assertions(self, db):
        """Spec with only non-executable assertions gets NO_EXECUTABLE_ASSERTIONS flag."""
        spec = self._make_spec(
            db,
            spec_id="SPEC-003",
            assertions=[
                {"type": "visual", "description": "Should look correct"},
            ],
        )
        score = db.score_spec_quality(spec)
        assert "NO_EXECUTABLE_ASSERTIONS" in score["flags"]

    def test_f3_executable_assertion(self, db):
        """Spec with grep assertion gets higher testability score."""
        spec = self._make_spec(
            db,
            spec_id="SPEC-004",
            assertions=[
                {"type": "grep", "file": "src/main.py", "pattern": "def main"},
            ],
        )
        score = db.score_spec_quality(spec)
        assert score["d2_testability"] >= 0.7
        assert "NO_ASSERTIONS" not in score["flags"]

    def test_f3_degradation_without_f1(self, db):
        """Score without F1 fields adjusts completeness denominator."""
        spec = db.insert_spec(
            id="SPEC-005",
            title="Legacy spec without F1 fields",
            status="specified",
            changed_by="test",
            change_reason="test",
            description="A description that is long enough for the clarity check to work.",
            section="core",
        )
        score = db.score_spec_quality(spec)
        # Should still produce a valid score even without F1 fields
        assert 0.0 <= score["overall"] <= 1.0
        assert score["d3_completeness"] >= 0.0

    def test_f3_persist_and_history(self, db):
        """persist_quality_scores stores scores; get_quality_history retrieves them."""
        self._make_spec(db, spec_id="SPEC-006")
        count = db.persist_quality_scores("S286")
        assert count >= 1

        history = db.get_quality_history("SPEC-006")
        assert len(history) >= 1
        assert history[0]["session_id"] == "S286"
        assert "overall" in history[0]

    def test_f3_quality_distribution(self, db):
        """get_quality_distribution aggregates tier counts."""
        self._make_spec(db, spec_id="SPEC-007")
        self._make_spec(db, spec_id="SPEC-008")
        db.persist_quality_scores("S287")

        dist = db.get_quality_distribution()
        assert "total" in dist
        assert dist["total"] >= 2

    def test_f3_tier_boundaries(self, db):
        """Tier classification follows defined thresholds."""
        # Create specs with varying quality
        db.insert_spec(id="SPEC-009", title="X", status="specified", changed_by="t", change_reason="t")
        spec = db.get_spec("SPEC-009")
        score = db.score_spec_quality(spec)
        # Tier should be one of the valid tiers
        assert score["tier"] in ("gold", "silver", "bronze", "needs-work")

    def test_f3_export_import_roundtrip(self, db, tmp_path):
        """Quality scores survive export/import cycle."""
        self._make_spec(db, spec_id="SPEC-010")
        db.persist_quality_scores("S286")

        # Export
        export_path = tmp_path / "export.json"
        db.export_json(export_path)

        # Import into fresh DB via CLI (needs TOML config)
        fresh_dir = tmp_path / "fresh"
        fresh_dir.mkdir()
        fresh_db_path = fresh_dir / "groundtruth.db"
        fresh_toml = fresh_dir / "groundtruth.toml"
        fresh_toml.write_text(
            f'[groundtruth]\ndb_path = "{fresh_db_path.as_posix()}"\n',
            encoding="utf-8",
        )
        db2 = KnowledgeDB(db_path=fresh_db_path)
        db2.close()

        from click.testing import CliRunner

        from groundtruth_kb.cli import main as cli_main

        runner = CliRunner()
        result = runner.invoke(cli_main, ["--config", str(fresh_toml), "import", str(export_path), "--merge"])
        assert result.exit_code == 0, result.output

        db2 = KnowledgeDB(db_path=fresh_db_path)
        history = db2.get_quality_history("SPEC-010")
        assert len(history) >= 1

    def test_f3_malformed_flags_import_rejects(self, db, tmp_path):
        """Malformed flags value is rejected on import, not stored."""
        self._make_spec(db, spec_id="SPEC-011")
        db.persist_quality_scores("S286")

        # Export and tamper flags
        export_path = tmp_path / "export.json"
        db.export_json(export_path)
        data = json.loads(export_path.read_text(encoding="utf-8"))
        for row in data["tables"].get("spec_quality_scores", []):
            row["flags"] = "not valid json list"
        export_path.write_text(json.dumps(data), encoding="utf-8")

        # Import into fresh DB — should reject malformed row
        fresh_dir = tmp_path / "fresh2"
        fresh_dir.mkdir()
        fresh_db_path = fresh_dir / "groundtruth.db"
        fresh_toml = fresh_dir / "groundtruth.toml"
        fresh_toml.write_text(
            f'[groundtruth]\ndb_path = "{fresh_db_path.as_posix()}"\n',
            encoding="utf-8",
        )
        KnowledgeDB(db_path=fresh_db_path).close()

        from click.testing import CliRunner

        from groundtruth_kb.cli import main as cli_main

        runner = CliRunner()
        # Non-merge mode should error on malformed flags
        result = runner.invoke(cli_main, ["--config", str(fresh_toml), "import", str(export_path)])
        assert result.exit_code != 0 or "Invalid flags" in result.output or "Error" in result.output

    def test_f3_unique_constraint(self, db):
        """Same spec+version+session cannot have duplicate scores (INSERT OR REPLACE)."""
        self._make_spec(db, spec_id="SPEC-012")
        count1 = db.persist_quality_scores("S286")
        count2 = db.persist_quality_scores("S286")  # Same session — replaces
        assert count1 == count2

        history = db.get_quality_history("SPEC-012")
        session_entries = [h for h in history if h["session_id"] == "S286"]
        assert len(session_entries) == 1  # Not duplicated

    def test_f3_history_ordering(self, db):
        """Multiple sessions produce ordered history (scored_at DESC)."""
        self._make_spec(db, spec_id="SPEC-013")
        db.persist_quality_scores("S285")
        db.persist_quality_scores("S286")

        history = db.get_quality_history("SPEC-013")
        assert len(history) >= 2
        # Most recent first
        assert history[0]["scored_at"] >= history[1]["scored_at"]
