"""Tests for groundtruth_kb.assertions module."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.assertions import (
    format_summary,
    run_all_assertions,
    run_single_assertion,
    run_spec_assertions,
)
from groundtruth_kb.db import KnowledgeDB


@pytest.fixture()
def project_dir(tmp_path: Path) -> Path:
    """Create a minimal project directory with some files for assertion testing."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("def hello():\n    return 'world'\n", encoding="utf-8")
    (src / "utils.py").write_text("MAX_RETRIES = 3\nTIMEOUT = 30\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Test Project\n", encoding="utf-8")
    (tmp_path / "groundtruth.toml").write_text("[groundtruth]\n", encoding="utf-8")
    return tmp_path


@pytest.fixture()
def db(tmp_path: Path) -> KnowledgeDB:
    """Create a fresh KnowledgeDB in a temp directory."""
    db_path = tmp_path / "test.db"
    db = KnowledgeDB(db_path=db_path)
    yield db
    db.close()


# ---------------------------------------------------------------------------
# run_single_assertion
# ---------------------------------------------------------------------------


class TestGrepAssertion:
    def test_grep_finds_match(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep", "pattern": "def hello", "file": "src/main.py", "description": "hello exists"},
            project_dir,
        )
        assert result["passed"] is True
        assert "1 match" in result["detail"]

    def test_grep_no_match(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep", "pattern": "def goodbye", "file": "src/main.py", "description": "goodbye exists"},
            project_dir,
        )
        assert result["passed"] is False
        assert "0 match" in result["detail"]

    def test_grep_min_count(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {
                "type": "grep", "pattern": r"\w+ = \d+", "file": "src/utils.py",
                "min_count": 2, "description": "two constants",
            },
            project_dir,
        )
        assert result["passed"] is True

    def test_grep_missing_file(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep", "pattern": "anything", "file": "nonexistent.py", "description": "missing file"},
            project_dir,
        )
        assert result["passed"] is False
        assert "not found" in result["detail"].lower()

    def test_grep_glob_file_pattern(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep", "pattern": "def hello", "file": "**/*.py", "description": "hello in any .py"},
            project_dir,
        )
        assert result["passed"] is True

    def test_grep_missing_file_field(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep", "pattern": "something", "description": "no file"},
            project_dir,
        )
        assert result["passed"] is False
        assert "missing" in result["detail"].lower()

    def test_grep_field_alias_target(self, project_dir: Path) -> None:
        """The 'target' field should work as an alias for 'file'."""
        result = run_single_assertion(
            {"type": "grep", "pattern": "def hello", "target": "src/main.py", "description": "alias test"},
            project_dir,
        )
        assert result["passed"] is True

    def test_grep_field_alias_query(self, project_dir: Path) -> None:
        """The 'query' field should work as an alias for 'pattern'."""
        result = run_single_assertion(
            {"type": "grep", "query": "def hello", "file": "src/main.py", "description": "query alias"},
            project_dir,
        )
        assert result["passed"] is True


class TestGlobAssertion:
    def test_glob_finds_file(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "glob", "pattern": "**/main.py", "description": "main.py exists"},
            project_dir,
        )
        assert result["passed"] is True

    def test_glob_no_match(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "glob", "pattern": "**/nonexistent.xyz", "description": "file missing"},
            project_dir,
        )
        assert result["passed"] is False

    def test_glob_with_contains(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "glob", "pattern": "**/*.py", "contains": "def hello", "description": "py with hello"},
            project_dir,
        )
        assert result["passed"] is True

    def test_glob_contains_not_found(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "glob", "pattern": "**/*.py", "contains": "class Nonexistent", "description": "no class"},
            project_dir,
        )
        assert result["passed"] is False


class TestGrepAbsentAssertion:
    def test_absent_pattern_not_found(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep_absent", "pattern": "SECRET_KEY", "file": "src/main.py", "description": "no secrets"},
            project_dir,
        )
        assert result["passed"] is True

    def test_absent_pattern_found(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep_absent", "pattern": "def hello", "file": "src/main.py", "description": "hello absent"},
            project_dir,
        )
        assert result["passed"] is False

    def test_absent_missing_file(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep_absent", "pattern": "anything", "file": "nonexistent.py", "description": "trivially absent"},
            project_dir,
        )
        assert result["passed"] is True
        assert "trivially absent" in result["detail"]

    def test_absent_glob_file_pattern(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep_absent", "pattern": "SECRET_KEY", "file": "**/*.py", "description": "no secrets anywhere"},
            project_dir,
        )
        assert result["passed"] is True


class TestNonMachineAssertions:
    def test_unknown_type_skipped(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "human_review", "description": "check the UI manually"},
            project_dir,
        )
        assert result["passed"] is True
        assert result.get("skipped") is True

    def test_missing_pattern(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "grep", "file": "src/main.py", "description": "no pattern"},
            project_dir,
        )
        assert result["passed"] is False
        assert "missing" in result["detail"].lower()


# ---------------------------------------------------------------------------
# run_spec_assertions / run_all_assertions
# ---------------------------------------------------------------------------


class TestSpecAssertions:
    def test_spec_with_assertions(self, db: KnowledgeDB, project_dir: Path) -> None:
        assertions = [
            {"type": "glob", "pattern": "**/main.py", "description": "main exists"},
            {"type": "grep", "pattern": "def hello", "file": "src/main.py", "description": "hello fn"},
        ]
        db.insert_spec(
            id="SPEC-T01", title="Test spec", status="implemented",
            changed_by="test", change_reason="test",
            assertions=assertions,
        )
        spec = db.get_spec("SPEC-T01")
        result = run_spec_assertions(db, spec, "test", project_dir)
        assert result["overall_passed"] is True
        assert result["assertion_count"] == 2

    def test_spec_without_assertions(self, db: KnowledgeDB, project_dir: Path) -> None:
        db.insert_spec(
            id="SPEC-T02", title="No assertions", status="specified",
            changed_by="test", change_reason="test",
        )
        spec = db.get_spec("SPEC-T02")
        result = run_spec_assertions(db, spec, "test", project_dir)
        assert result["overall_passed"] is True
        assert result.get("skipped") is True

    def test_spec_with_text_assertion(self, db: KnowledgeDB, project_dir: Path) -> None:
        db.insert_spec(
            id="SPEC-T03", title="Text assertion", status="implemented",
            changed_by="test", change_reason="test",
            assertions=["Check manually that the UI renders correctly"],
        )
        spec = db.get_spec("SPEC-T03")
        result = run_spec_assertions(db, spec, "test", project_dir)
        assert result["overall_passed"] is True
        assert result.get("skipped") is True

    def test_run_all_assertions(self, db: KnowledgeDB, project_dir: Path) -> None:
        assertions = [{"type": "glob", "pattern": "README.md", "description": "readme exists"}]
        db.insert_spec(
            id="SPEC-A01", title="With assertion", status="implemented",
            changed_by="test", change_reason="test",
            assertions=assertions,
        )
        db.insert_spec(
            id="SPEC-A02", title="No assertion", status="specified",
            changed_by="test", change_reason="test",
        )
        summary = run_all_assertions(db, project_dir, triggered_by="test")
        assert summary["total_specs"] == 2
        assert summary["passed"] == 1
        assert summary["skipped"] == 1
        assert summary["failed"] == 0

    def test_run_single_spec_filter(self, db: KnowledgeDB, project_dir: Path) -> None:
        db.insert_spec(
            id="SPEC-F01", title="First", status="implemented",
            changed_by="test", change_reason="test",
            assertions=[{"type": "glob", "pattern": "README.md", "description": "readme"}],
        )
        db.insert_spec(
            id="SPEC-F02", title="Second", status="implemented",
            changed_by="test", change_reason="test",
            assertions=[{"type": "glob", "pattern": "MISSING.md", "description": "missing"}],
        )
        summary = run_all_assertions(db, project_dir, spec_id="SPEC-F01")
        assert summary["total_specs"] == 1
        assert summary["passed"] == 1

    def test_run_nonexistent_spec(self, db: KnowledgeDB, project_dir: Path) -> None:
        summary = run_all_assertions(db, project_dir, spec_id="NOPE-999")
        assert "error" in summary


# ---------------------------------------------------------------------------
# format_summary
# ---------------------------------------------------------------------------


class TestFormatSummary:
    def test_format_with_failures(self, db: KnowledgeDB, project_dir: Path) -> None:
        db.insert_spec(
            id="SPEC-FMT1", title="Failing spec", status="implemented",
            changed_by="test", change_reason="test",
            assertions=[{"type": "glob", "pattern": "NONEXISTENT.xyz", "description": "missing file"}],
        )
        summary = run_all_assertions(db, project_dir)
        text = format_summary(summary)
        assert "FAILURES" in text
        assert "SPEC-FMT1" in text

    def test_format_error(self) -> None:
        text = format_summary({"error": "Something went wrong"})
        assert "ERROR" in text

    def test_format_all_passed(self, db: KnowledgeDB, project_dir: Path) -> None:
        db.insert_spec(
            id="SPEC-FMT2", title="Passing spec", status="implemented",
            changed_by="test", change_reason="test",
            assertions=[{"type": "glob", "pattern": "README.md", "description": "readme"}],
        )
        summary = run_all_assertions(db, project_dir)
        text = format_summary(summary)
        assert "PASSED" in text
        assert "FAILURES" not in text
