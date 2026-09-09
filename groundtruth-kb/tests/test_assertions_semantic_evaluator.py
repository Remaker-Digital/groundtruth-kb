"""Structural assertion primitive coverage.

These tests exercise matching, counting and path confinement on both positive
and negative inputs. A passing file or marker check does not execute a referenced
evaluator, prove test coverage, or establish behavioral conformance.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.assertions import run_single_assertion


def _status(assertion: dict[str, object], root: Path) -> str:
    return run_single_assertion(assertion, root)["status"]


def _write(root: Path, rel: str, body: str) -> Path:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


# --- file_exists -----------------------------------------------------------


def test_file_exists_passes_for_present_file(tmp_path: Path) -> None:
    _write(tmp_path, "scripts/evaluator.py", "# evaluator\n")
    assertion = {"type": "file_exists", "file": "scripts/evaluator.py", "description": "evaluator present"}
    assert _status(assertion, tmp_path) == "PASS"


def test_file_exists_fails_for_absent_file(tmp_path: Path) -> None:
    """The dangling-reference case WI-6547 exists to close."""
    assertion = {"type": "file_exists", "file": "scripts/absent.py", "description": "evaluator present"}
    assert _status(assertion, tmp_path) == "FAIL"


# --- grep ------------------------------------------------------------------


def test_grep_passes_when_contract_marker_present(tmp_path: Path) -> None:
    _write(tmp_path, "scripts/evaluator.py", 'MARKER = "governed-two-tier-git-lifecycle"\n')
    assertion = {
        "type": "grep",
        "file": "scripts/evaluator.py",
        "pattern": "governed-two-tier-git-lifecycle",
        "min_count": 1,
        "description": "contract marker declared",
    }
    assert _status(assertion, tmp_path) == "PASS"


def test_grep_fails_when_contract_marker_absent(tmp_path: Path) -> None:
    _write(tmp_path, "scripts/evaluator.py", "# no marker here\n")
    assertion = {
        "type": "grep",
        "file": "scripts/evaluator.py",
        "pattern": "governed-two-tier-git-lifecycle",
        "min_count": 1,
        "description": "contract marker declared",
    }
    assert _status(assertion, tmp_path) == "FAIL"


def test_grep_respects_min_count(tmp_path: Path) -> None:
    """One occurrence must not satisfy a two-occurrence requirement."""
    _write(tmp_path, "notes.md", "marker\n")
    assertion = {
        "type": "grep",
        "file": "notes.md",
        "pattern": "marker",
        "min_count": 2,
        "description": "two occurrences required",
    }
    assert _status(assertion, tmp_path) == "FAIL"


# --- count -----------------------------------------------------------------


def test_count_passes_at_threshold(tmp_path: Path) -> None:
    _write(tmp_path, "tests/t.py", "assert a\nassert b\n")
    assertion = {
        "type": "count",
        "file": "tests/t.py",
        "pattern": r"\bassert\b",
        "operator": ">=",
        "expected": 2,
        "description": "at least two matching text occurrences",
    }
    assert _status(assertion, tmp_path) == "PASS"


def test_count_fails_below_threshold(tmp_path: Path) -> None:
    """A test module with a single assertion does not satisfy the two-assertion floor."""
    _write(tmp_path, "tests/t.py", "assert a\n")
    assertion = {
        "type": "count",
        "file": "tests/t.py",
        "pattern": r"\bassert\b",
        "operator": ">=",
        "expected": 2,
        "description": "at least two matching text occurrences",
    }
    assert _status(assertion, tmp_path) == "FAIL"


# --- path safety -----------------------------------------------------------


def test_assertion_cannot_escape_project_root(tmp_path: Path) -> None:
    """Traversal outside the project root must not resolve to a passing read."""
    assertion = {
        "type": "file_exists",
        "file": "../outside.txt",
        "description": "escapes the root",
    }
    assert _status(assertion, tmp_path) != "PASS"


def test_unknown_assertion_type_is_not_reported_as_pass(tmp_path: Path) -> None:
    """A non-executable assertion type must never be counted as satisfied."""
    assertion = {"type": "vibes", "file": "anything", "description": "not machine-checkable"}
    assert _status(assertion, tmp_path) != "PASS"
