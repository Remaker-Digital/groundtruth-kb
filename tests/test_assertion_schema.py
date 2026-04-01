"""Tests for groundtruth_kb.assertion_schema module."""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.assertion_schema import validate_assertion, validate_assertion_list
from groundtruth_kb.db import KnowledgeDB


# ---------------------------------------------------------------------------
# validate_assertion — valid cases
# ---------------------------------------------------------------------------


class TestValidAssertions:
    def test_valid_grep(self) -> None:
        errors = validate_assertion({"type": "grep", "pattern": "hello", "file": "src/main.py"})
        assert errors == []

    def test_valid_grep_with_aliases(self) -> None:
        errors = validate_assertion({"type": "grep", "query": "hello", "target": "src/main.py"})
        assert errors == []

    def test_valid_glob(self) -> None:
        errors = validate_assertion({"type": "glob", "pattern": "**/*.py"})
        assert errors == []

    def test_valid_grep_absent(self) -> None:
        errors = validate_assertion({"type": "grep_absent", "pattern": "SECRET", "file": "src/main.py"})
        assert errors == []

    def test_valid_file_exists_with_file(self) -> None:
        errors = validate_assertion({"type": "file_exists", "file": "src/main.py"})
        assert errors == []

    def test_valid_file_exists_with_path_alias(self) -> None:
        """Legacy file_exists rows use 'path' — must be accepted."""
        errors = validate_assertion({"type": "file_exists", "path": "src/chat/quality_scorer.py"})
        assert errors == []

    def test_valid_count(self) -> None:
        errors = validate_assertion({
            "type": "count", "pattern": "x", "file": "a.py", "operator": "==", "expected": 5,
        })
        assert errors == []

    def test_valid_json_path(self) -> None:
        errors = validate_assertion({"type": "json_path", "file": "config.json", "path": "project.name"})
        assert errors == []

    def test_valid_all_of(self) -> None:
        errors = validate_assertion({
            "type": "all_of",
            "assertions": [
                {"type": "file_exists", "file": "a.py"},
                {"type": "grep", "pattern": "x", "file": "b.py"},
            ],
        })
        assert errors == []

    def test_non_machine_type_passes(self) -> None:
        errors = validate_assertion({"type": "visual", "description": "UI looks good"})
        assert errors == []

    def test_plain_text_passes(self) -> None:
        errors = validate_assertion("Check manually")
        assert errors == []


# ---------------------------------------------------------------------------
# validate_assertion — error cases
# ---------------------------------------------------------------------------


class TestInvalidAssertions:
    def test_grep_missing_pattern(self) -> None:
        errors = validate_assertion({"type": "grep", "file": "src/main.py"})
        assert any("pattern" in e.lower() for e in errors)

    def test_grep_missing_file(self) -> None:
        errors = validate_assertion({"type": "grep", "pattern": "hello"})
        assert any("file" in e.lower() for e in errors)

    def test_file_exists_missing_file(self) -> None:
        errors = validate_assertion({"type": "file_exists"})
        assert any("file" in e.lower() or "path" in e.lower() for e in errors)

    def test_count_invalid_operator(self) -> None:
        errors = validate_assertion({
            "type": "count", "pattern": "x", "file": "a.py", "operator": "~=",
        })
        assert any("operator" in e.lower() for e in errors)

    def test_count_non_integer_expected(self) -> None:
        errors = validate_assertion({
            "type": "count", "pattern": "x", "file": "a.py", "expected": "five",
        })
        assert any("integer" in e.lower() for e in errors)

    def test_json_path_missing_path(self) -> None:
        errors = validate_assertion({"type": "json_path", "file": "config.json"})
        assert any("path" in e.lower() for e in errors)

    def test_all_of_empty_children(self) -> None:
        errors = validate_assertion({"type": "all_of", "assertions": []})
        assert any("non-empty" in e.lower() for e in errors)

    def test_all_of_missing_assertions(self) -> None:
        errors = validate_assertion({"type": "all_of"})
        assert any("non-empty" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------


class TestPathSafety:
    def test_absolute_path_rejected(self) -> None:
        errors = validate_assertion({"type": "grep", "pattern": "x", "file": "/etc/passwd"})
        assert any("absolute" in e.lower() for e in errors)

    def test_parent_traversal_rejected(self) -> None:
        errors = validate_assertion({"type": "grep", "pattern": "x", "file": "../../../secret"})
        assert any("traversal" in e.lower() for e in errors)

    def test_glob_parent_traversal_rejected(self) -> None:
        errors = validate_assertion({"type": "glob", "pattern": "../../**/*.py"})
        assert any("traversal" in e.lower() for e in errors)

    def test_nested_child_path_checked(self) -> None:
        """Path safety checks propagate into composition children."""
        errors = validate_assertion({
            "type": "all_of",
            "assertions": [
                {"type": "grep", "pattern": "x", "file": "../escape.py"},
            ],
        })
        assert any("traversal" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# validate_assertion_list
# ---------------------------------------------------------------------------


class TestValidateAssertionList:
    def test_valid_list(self) -> None:
        errors = validate_assertion_list([
            {"type": "grep", "pattern": "x", "file": "a.py"},
            {"type": "glob", "pattern": "*.md"},
        ])
        assert errors == []

    def test_none_returns_empty(self) -> None:
        assert validate_assertion_list(None) == []

    def test_not_a_list_returns_error(self) -> None:
        errors = validate_assertion_list("not a list")
        assert any("list" in e.lower() for e in errors)

    def test_mixed_valid_invalid(self) -> None:
        errors = validate_assertion_list([
            {"type": "grep", "pattern": "x", "file": "a.py"},
            {"type": "grep"},  # missing pattern and file
        ])
        assert len(errors) >= 2  # at least 'missing pattern' + 'missing file'
        assert all("assertions[1]" in e for e in errors)


# ---------------------------------------------------------------------------
# DB integration — write-time validation
# ---------------------------------------------------------------------------


class TestDBWriteValidation:
    @pytest.fixture()
    def db(self, tmp_path: Path) -> KnowledgeDB:
        db_path = tmp_path / "test.db"
        _db = KnowledgeDB(db_path=db_path)
        yield _db
        _db.close()

    def test_insert_spec_rejects_invalid_assertions(self, db: KnowledgeDB) -> None:
        with pytest.raises(ValueError, match="Invalid assertions"):
            db.insert_spec(
                id="SPEC-BAD", title="Bad", status="specified",
                changed_by="test", change_reason="test",
                assertions=[{"type": "grep"}],  # missing pattern + file
            )

    def test_insert_spec_accepts_valid_assertions(self, db: KnowledgeDB) -> None:
        spec = db.insert_spec(
            id="SPEC-GOOD", title="Good", status="specified",
            changed_by="test", change_reason="test",
            assertions=[{"type": "glob", "pattern": "*.md"}],
        )
        assert spec["id"] == "SPEC-GOOD"

    def test_insert_spec_validation_opt_out(self, db: KnowledgeDB) -> None:
        """validate_assertions=False skips validation (for migration tooling)."""
        spec = db.insert_spec(
            id="SPEC-MIGR", title="Migration", status="specified",
            changed_by="test", change_reason="test",
            assertions=[{"type": "grep"}],  # would normally fail
            validate_assertions=False,
        )
        assert spec["id"] == "SPEC-MIGR"

    def test_insert_spec_accepts_legacy_file_exists_shape(self, db: KnowledgeDB) -> None:
        """The exact row shape from SPEC-0180 should pass validation."""
        spec = db.insert_spec(
            id="SPEC-FE", title="File exists legacy", status="specified",
            changed_by="test", change_reason="test",
            assertions=[{"type": "file_exists", "path": "src/chat/quality_scorer.py"}],
        )
        assert spec["id"] == "SPEC-FE"
