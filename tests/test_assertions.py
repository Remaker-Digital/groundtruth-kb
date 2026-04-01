"""Tests for groundtruth_kb.assertions module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from groundtruth_kb.assertions import (
    _has_parent_traversal,
    _is_absolute,
    _normalize_assertion,
    _safe_glob,
    _safe_resolve,
    _walk_path,
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
    (tmp_path / "config.json").write_text(
        json.dumps({"project": {"name": "test", "version": "1.0.0"}, "items": [{"id": 1}, {"id": 2}]}),
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "test"\nversion = "1.0.0"\n\n[project.scripts]\ngt = "groundtruth_kb.cli:main"\n',
        encoding="utf-8",
    )
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


# ---------------------------------------------------------------------------
# Phase 0: Path confinement
# ---------------------------------------------------------------------------


class TestPathConfinement:
    def test_safe_resolve_normal_path(self, project_dir: Path) -> None:
        result = _safe_resolve("src/main.py", project_dir)
        assert result is not None
        assert result.name == "main.py"

    def test_safe_resolve_rejects_parent_traversal(self, project_dir: Path) -> None:
        assert _safe_resolve("../../../etc/passwd", project_dir) is None

    def test_safe_resolve_rejects_absolute_posix(self, project_dir: Path) -> None:
        assert _safe_resolve("/etc/passwd", project_dir) is None

    def test_safe_resolve_rejects_absolute_windows(self, project_dir: Path) -> None:
        assert _safe_resolve("C:\\Windows\\System32\\config", project_dir) is None

    def test_safe_resolve_rejects_embedded_traversal(self, project_dir: Path) -> None:
        assert _safe_resolve("src/../../../secret.txt", project_dir) is None

    def test_safe_glob_normal_pattern(self, project_dir: Path) -> None:
        result = _safe_glob("**/*.py", project_dir)
        assert result is not None
        assert len(result) >= 2  # main.py and utils.py

    def test_safe_glob_rejects_parent_traversal(self, project_dir: Path) -> None:
        result = _safe_glob("../../**/*.md", project_dir)
        assert result is None

    def test_safe_glob_rejects_absolute_pattern(self, project_dir: Path) -> None:
        result = _safe_glob("/etc/**/*.conf", project_dir)
        assert result is None

    def test_has_parent_traversal_cases(self) -> None:
        assert _has_parent_traversal("../foo") is True
        assert _has_parent_traversal("foo/../bar") is True
        assert _has_parent_traversal("foo/..\\bar") is True
        assert _has_parent_traversal("..") is True
        assert _has_parent_traversal("foo/bar") is False
        assert _has_parent_traversal("foo..bar") is False  # not a traversal

    def test_is_absolute_cases(self) -> None:
        assert _is_absolute("/etc/passwd") is True
        assert _is_absolute("C:\\Windows") is True
        assert _is_absolute("src/main.py") is False
        assert _is_absolute("**/*.py") is False

    def test_grep_rejects_traversal_in_file(self, project_dir: Path) -> None:
        """Grep with parent traversal in file field should fail."""
        result = run_single_assertion(
            {"type": "grep", "pattern": "anything", "file": "../../../etc/passwd"},
            project_dir,
        )
        assert result["passed"] is False
        assert "rejected" in result["detail"].lower() or "escapes" in result["detail"].lower()

    def test_glob_rejects_traversal_in_pattern(self, project_dir: Path) -> None:
        """Glob with parent traversal should fail."""
        result = run_single_assertion(
            {"type": "glob", "pattern": "../../**/*.py"},
            project_dir,
        )
        assert result["passed"] is False
        assert "rejected" in result["detail"].lower() or "unsafe" in result["detail"].lower()


# ---------------------------------------------------------------------------
# Phase 1: Normalization
# ---------------------------------------------------------------------------


class TestNormalization:
    def test_normalize_query_to_pattern(self) -> None:
        result = _normalize_assertion({"type": "grep", "query": "hello", "file": "test.py"})
        assert result["pattern"] == "hello"

    def test_normalize_target_to_file(self) -> None:
        result = _normalize_assertion({"type": "grep", "pattern": "x", "target": "src/main.py"})
        assert result["file"] == "src/main.py"

    def test_normalize_path_to_file(self) -> None:
        result = _normalize_assertion({"type": "file_exists", "path": "src/main.py"})
        assert result["file"] == "src/main.py"

    def test_normalize_preserves_existing_canonical(self) -> None:
        orig = {"type": "grep", "pattern": "x", "file": "a.py", "target": "b.py"}
        result = _normalize_assertion(orig)
        assert result["file"] == "a.py"  # canonical takes precedence
        assert result["pattern"] == "x"


# ---------------------------------------------------------------------------
# Phase 2: New types — file_exists
# ---------------------------------------------------------------------------


class TestFileExistsAssertion:
    def test_file_exists_found(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "file_exists", "file": "src/main.py", "description": "main exists"},
            project_dir,
        )
        assert result["passed"] is True

    def test_file_exists_not_found(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "file_exists", "file": "src/nonexistent.py", "description": "missing"},
            project_dir,
        )
        assert result["passed"] is False

    def test_file_exists_directory_not_file(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "file_exists", "file": "src", "description": "dir not file"},
            project_dir,
        )
        assert result["passed"] is False

    def test_file_exists_rejects_traversal(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "file_exists", "file": "../../../etc/passwd", "description": "escape"},
            project_dir,
        )
        assert result["passed"] is False
        assert "rejected" in result["detail"].lower()

    def test_file_exists_path_alias(self, project_dir: Path) -> None:
        """The 'path' field should work as alias for 'file' (legacy compatibility)."""
        result = run_single_assertion(
            {"type": "file_exists", "path": "src/main.py", "description": "path alias"},
            project_dir,
        )
        assert result["passed"] is True

    # --- Legacy AR row shape regression tests (SPEC-0180/0183/1797) ---

    def test_legacy_spec_0180_shape(self, project_dir: Path) -> None:
        """Exact row shape from SPEC-0180: path field, no description."""
        (project_dir / "src" / "chat").mkdir(parents=True, exist_ok=True)
        (project_dir / "src" / "chat" / "quality_scorer.py").write_text("# scorer", encoding="utf-8")
        result = run_single_assertion(
            {"type": "file_exists", "path": "src/chat/quality_scorer.py"},
            project_dir,
        )
        assert result["passed"] is True

    def test_legacy_spec_1797_shape(self, project_dir: Path) -> None:
        """Exact row shape from SPEC-1797: path + description fields."""
        (project_dir / "src" / "agents" / "containers").mkdir(parents=True, exist_ok=True)
        (project_dir / "src" / "agents" / "containers" / "co_pilot_app.py").write_text("# app", encoding="utf-8")
        result = run_single_assertion(
            {"type": "file_exists", "path": "src/agents/containers/co_pilot_app.py",
             "description": "Co-pilot container entry point exists"},
            project_dir,
        )
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# Phase 2: New types — count
# ---------------------------------------------------------------------------


class TestCountAssertion:
    def test_count_equals(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "count", "pattern": r"\w+ = \d+", "file": "src/utils.py",
             "operator": "==", "expected": 2, "description": "exactly 2 constants"},
            project_dir,
        )
        assert result["passed"] is True

    def test_count_not_equals(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "count", "pattern": r"\w+ = \d+", "file": "src/utils.py",
             "operator": "!=", "expected": 5, "description": "not 5 constants"},
            project_dir,
        )
        assert result["passed"] is True

    def test_count_greater_than(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "count", "pattern": r"\w+ = \d+", "file": "src/utils.py",
             "operator": ">", "expected": 1, "description": "more than 1"},
            project_dir,
        )
        assert result["passed"] is True

    def test_count_fails_when_not_met(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "count", "pattern": r"\w+ = \d+", "file": "src/utils.py",
             "operator": "==", "expected": 99, "description": "99 constants"},
            project_dir,
        )
        assert result["passed"] is False

    def test_count_invalid_operator(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "count", "pattern": "x", "file": "src/main.py",
             "operator": "~=", "expected": 1},
            project_dir,
        )
        assert result["passed"] is False
        assert "invalid operator" in result["detail"].lower()

    def test_count_with_glob_file(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "count", "pattern": "def ", "file": "**/*.py",
             "operator": ">=", "expected": 1, "description": "at least 1 def"},
            project_dir,
        )
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# Phase 2: New types — json_path
# ---------------------------------------------------------------------------


class TestJsonPathAssertion:
    def test_json_path_matches(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "json_path", "file": "config.json", "path": "project.name",
             "expected": "test", "description": "project name"},
            project_dir,
        )
        assert result["passed"] is True

    def test_json_path_version(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "json_path", "file": "config.json", "path": "project.version",
             "expected": "1.0.0", "description": "version"},
            project_dir,
        )
        assert result["passed"] is True

    def test_json_path_mismatch(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "json_path", "file": "config.json", "path": "project.name",
             "expected": "wrong", "description": "wrong name"},
            project_dir,
        )
        assert result["passed"] is False

    def test_json_path_array_index(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "json_path", "file": "config.json", "path": "items.0.id",
             "expected": 1, "description": "first item id"},
            project_dir,
        )
        assert result["passed"] is True

    def test_json_path_missing_key(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "json_path", "file": "config.json", "path": "nonexistent.key",
             "expected": "x"},
            project_dir,
        )
        assert result["passed"] is False
        assert "not found" in result["detail"].lower()

    def test_json_path_toml_file(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "json_path", "file": "pyproject.toml", "path": "project.version",
             "expected": "1.0.0", "description": "toml version"},
            project_dir,
        )
        assert result["passed"] is True

    def test_json_path_existence_only(self, project_dir: Path) -> None:
        """No expected value — just check the path exists."""
        result = run_single_assertion(
            {"type": "json_path", "file": "config.json", "path": "project.name",
             "description": "name exists"},
            project_dir,
        )
        assert result["passed"] is True


# ---------------------------------------------------------------------------
# Phase 3: Composition — all_of / any_of
# ---------------------------------------------------------------------------


class TestAllOfAssertion:
    def test_all_pass(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "all_of", "description": "both exist", "assertions": [
                {"type": "file_exists", "file": "src/main.py"},
                {"type": "file_exists", "file": "src/utils.py"},
            ]},
            project_dir,
        )
        assert result["passed"] is True
        assert "children" in result
        assert len(result["children"]) == 2

    def test_one_fails(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "all_of", "description": "one missing", "assertions": [
                {"type": "file_exists", "file": "src/main.py"},
                {"type": "file_exists", "file": "src/nonexistent.py"},
            ]},
            project_dir,
        )
        assert result["passed"] is False

    def test_empty_children_fails(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "all_of", "description": "empty", "assertions": []},
            project_dir,
        )
        assert result["passed"] is False
        assert "empty" in result["detail"].lower()

    def test_skipped_children_only(self, project_dir: Path) -> None:
        """All non-machine children → skipped, not pass/fail."""
        result = run_single_assertion(
            {"type": "all_of", "assertions": [
                {"type": "visual", "description": "UI looks good"},
            ]},
            project_dir,
        )
        assert result.get("skipped") is True


class TestAnyOfAssertion:
    def test_one_passes(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "any_of", "description": "at least one", "assertions": [
                {"type": "file_exists", "file": "src/nonexistent.py"},
                {"type": "file_exists", "file": "src/main.py"},
            ]},
            project_dir,
        )
        assert result["passed"] is True

    def test_none_pass(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "any_of", "description": "none exist", "assertions": [
                {"type": "file_exists", "file": "nope1.py"},
                {"type": "file_exists", "file": "nope2.py"},
            ]},
            project_dir,
        )
        assert result["passed"] is False

    def test_skipped_does_not_satisfy_any_of(self, project_dir: Path) -> None:
        """Non-machine (skipped) children do NOT count as passing for any_of."""
        result = run_single_assertion(
            {"type": "any_of", "assertions": [
                {"type": "visual", "description": "looks good"},
                {"type": "file_exists", "file": "nonexistent.py"},
            ]},
            project_dir,
        )
        assert result["passed"] is False  # visual is skipped, file_exists fails

    def test_empty_children_fails(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "any_of", "description": "empty", "assertions": []},
            project_dir,
        )
        assert result["passed"] is False


class TestCompositionNesting:
    def test_nested_all_of_in_any_of(self, project_dir: Path) -> None:
        result = run_single_assertion(
            {"type": "any_of", "assertions": [
                {"type": "all_of", "assertions": [
                    {"type": "file_exists", "file": "src/main.py"},
                    {"type": "grep", "pattern": "def hello", "file": "src/main.py"},
                ]},
                {"type": "file_exists", "file": "nonexistent.py"},
            ]},
            project_dir,
        )
        assert result["passed"] is True

    def test_depth_limit_exceeded(self, project_dir: Path) -> None:
        """Nesting beyond max_depth should fail — depth error propagates up."""
        deep = {"type": "file_exists", "file": "src/main.py"}
        for _ in range(4):  # 4 levels of nesting exceeds default max_depth=3
            deep = {"type": "all_of", "assertions": [deep]}
        result = run_single_assertion(deep, project_dir)
        assert result["passed"] is False
        # The outermost all_of reports failure; the depth error is in nested children
        # Walk down to find the depth-limit failure
        node = result
        found_depth_error = False
        while "children" in node and node["children"]:
            node = node["children"][0]
            if "depth" in node.get("detail", "").lower():
                found_depth_error = True
                break
        assert found_depth_error, f"Expected depth error in nested children, got: {result}"


# ---------------------------------------------------------------------------
# Phase 2+3: format_summary with composition
# ---------------------------------------------------------------------------


class TestFormatSummaryComposition:
    def test_format_composition_failure(self, db: KnowledgeDB, project_dir: Path) -> None:
        db.insert_spec(
            id="SPEC-COMP1", title="Composed spec", status="implemented",
            changed_by="test", change_reason="test",
            assertions=[{
                "type": "all_of", "description": "both required", "assertions": [
                    {"type": "file_exists", "file": "src/main.py"},
                    {"type": "file_exists", "file": "MISSING.xyz"},
                ],
            }],
        )
        summary = run_all_assertions(db, project_dir)
        text = format_summary(summary)
        assert "FAILURES" in text
        assert "SPEC-COMP1" in text
