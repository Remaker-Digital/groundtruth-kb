"""Tests for scripts/draft_lint.py (WI-4437, PROJECT-FABLE-INVESTIGATION).

Authorized by ``bridge/gtkb-cheap-draft-linter-002.md`` (Codex GO).

Each of the six deterministic checks is exercised on both its PASS and FAIL
branch, and a read-only contract test (DELIB-S312) parses the linter's source
to assert it performs no writes / no MemBase mutation. A fixture sqlite DB
(``current_specifications``) keeps the phantom-spec check independent of the
live ``groundtruth.db``.
"""

from __future__ import annotations

import ast
import importlib.util
import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "draft_lint.py"


@pytest.fixture(scope="module")
def lint_module():
    """Load draft_lint.py as a module without executing main()."""
    spec = importlib.util.spec_from_file_location("draft_lint", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def fixture_db(tmp_path_factory) -> Path:
    """A minimal MemBase whose current_specifications view holds two real ids."""
    db_path = tmp_path_factory.mktemp("draftlint-db") / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE current_specifications (id TEXT PRIMARY KEY)")
    conn.executemany(
        "INSERT INTO current_specifications (id) VALUES (?)",
        [("SPEC-1662",), ("GOV-FILE-BRIDGE-AUTHORITY-001",)],
    )
    conn.commit()
    conn.close()
    return db_path


# A clean draft: every required section present, real resolvable paths, real
# spec ids, no placeholders, and a concrete verification assertion.
CLEAN_DRAFT = """# Example clean proposal

## Summary
Adds a thing per HYG-019. Touches scripts/draft_lint.py only.

## Scope and Boundaries
Bounded; cites GOV-FILE-BRIDGE-AUTHORITY-001 and SPEC-1662.

## Proposed Implementation
Edit bridge/INDEX.md handling.

## Spec-Derived Verification Plan
Run pytest platform_tests; expect 5/5 PASS and ruff clean.

## Acceptance Criteria
The checks pass.

## Risk and Rollback
Low risk; revert the change.
"""


def _status(report: dict, name: str) -> str:
    return next(c["status"] for c in report["checks"] if c["name"] == name)


def test_clean_draft_passes(lint_module, fixture_db):
    report = lint_module.lint(CLEAN_DRAFT, hyg_ids={"HYG-019", "HYG-020"}, db_path=fixture_db)
    assert report["ok"] is True
    assert report["summary"]["fail"] == 0
    # Every non-skip check is a pass on the clean draft.
    for check in report["checks"]:
        assert check["status"] in {"pass", "skip"}, check


def test_cited_path_resolution_fail(lint_module, fixture_db):
    draft = CLEAN_DRAFT + "\nAlso edits scripts/this_path_does_not_exist_zzz.py\n"
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "cited_path_resolution") == "fail"
    assert report["ok"] is False


def test_cited_path_target_paths_exempt(lint_module, fixture_db):
    # A non-existent path declared on target_paths is exempt (it may be created).
    draft = 'target_paths: ["scripts/brand_new_file_zzz.py"]\n' + CLEAN_DRAFT
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "cited_path_resolution") == "pass"


def test_hyg_id_match_fail(lint_module, fixture_db):
    draft = CLEAN_DRAFT + "\nImports HYG-999 from another cluster.\n"
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "hyg_id_match") == "fail"


def test_hyg_id_skip_without_baseline(lint_module, fixture_db):
    report = lint_module.lint(CLEAN_DRAFT, hyg_ids=None, db_path=fixture_db)
    assert _status(report, "hyg_id_match") == "skip"


def test_phantom_spec_fail(lint_module, fixture_db):
    draft = CLEAN_DRAFT + "\nCites SPEC-9999999 which does not exist.\n"
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "phantom_spec") == "fail"


def test_phantom_spec_skip_when_db_missing(lint_module, tmp_path):
    report = lint_module.lint(CLEAN_DRAFT, db_path=tmp_path / "nope.db")
    assert _status(report, "phantom_spec") == "skip"


def test_required_sections_fail(lint_module, fixture_db):
    draft = CLEAN_DRAFT.replace("## Risk and Rollback", "## Notes")
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "required_sections") == "fail"
    assert any("risk" in f for f in _findings(report, "required_sections"))


def test_placeholder_fail(lint_module, fixture_db):
    draft = CLEAN_DRAFT + "\nTBD: finish this section.\n"
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "placeholder") == "fail"


def test_placeholder_template_fail(lint_module, fixture_db):
    draft = CLEAN_DRAFT + "\nReplace <topic> before filing.\n"
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "placeholder") == "fail"


def test_assertion_floor_fail_on_rubber_stamp(lint_module, fixture_db):
    # Replace the concrete verification body with pure prose.
    draft = CLEAN_DRAFT.replace(
        "Run pytest platform_tests; expect 5/5 PASS and ruff clean.",
        "We will verify the implementation works correctly and is good.",
    )
    report = lint_module.lint(draft, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "assertion_floor") == "fail"


def test_assertion_floor_pass_on_concrete(lint_module, fixture_db):
    report = lint_module.lint(CLEAN_DRAFT, hyg_ids={"HYG-019"}, db_path=fixture_db)
    assert _status(report, "assertion_floor") == "pass"


def _findings(report: dict, name: str) -> list[str]:
    return next(c["findings"] for c in report["checks"] if c["name"] == name)


def test_linter_is_read_only(lint_module):
    """DELIB-S312: the linter must perform no writes and no MemBase mutation."""
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    mutating_sql = ("insert", "update", "delete", "drop", "alter", "create table")
    for node in ast.walk(tree):
        # No file opened in a write/append/exclusive mode.
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            for arg in [*node.args, *(kw.value for kw in node.keywords)]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    assert not set("wax") & set(arg.value), f"write-mode open: {arg.value}"
        # No write/truncate attribute calls.
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"write", "writelines", "truncate"}, node.attr
        # No mutating SQL in string literals.
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lowered = node.value.lower()
            for kw in mutating_sql:
                assert kw not in lowered, f"mutating SQL literal: {kw!r}"

    # No mutating-module imports.
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not (imported & {"subprocess", "shutil", "os"}), imported


def test_main_exit_code_via_cli(lint_module, fixture_db, tmp_path, capsys):
    """End-to-end: main() returns 1 on a failing draft, 0 on a clean one."""
    bad = tmp_path / "bad.md"
    bad.write_text(CLEAN_DRAFT + "\nTBD finish me\n", encoding="utf-8")
    rc = lint_module.main([str(bad), "--db", str(fixture_db), "--hyg-ids", "HYG-019"])
    assert rc == 1

    good = tmp_path / "good.md"
    good.write_text(CLEAN_DRAFT, encoding="utf-8")
    rc = lint_module.main([str(good), "--db", str(fixture_db), "--hyg-ids", "HYG-019"])
    assert rc == 0
    out = capsys.readouterr().out
    assert '"ok": true' in out
