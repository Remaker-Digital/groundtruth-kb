# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.doctor — workstation readiness checks."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from groundtruth_kb.project.doctor import (
    DoctorReport,
    ToolCheck,
    _check_db_schema,
    _check_git,
    _check_groundtruth_toml,
    _check_hooks,
    _check_python,
    _check_rules,
    _check_settings_classifiers,
    run_doctor,
)

# ---------------------------------------------------------------------------
# _check_python
# ---------------------------------------------------------------------------


def test_check_python_passes() -> None:
    """_check_python() returns pass since Python 3.11+ is running."""
    result = _check_python()
    assert isinstance(result, ToolCheck)
    assert result.name == "Python"
    assert result.found is True
    # Must be running 3.11+ in test env (pyproject.toml requires python_requires >= "3.11")
    assert result.status == "pass"


# ---------------------------------------------------------------------------
# _check_git
# ---------------------------------------------------------------------------


def test_check_git_returns_tool_check() -> None:
    """_check_git() returns a ToolCheck (git is expected to be present in CI)."""
    result = _check_git()
    assert isinstance(result, ToolCheck)
    assert result.name == "Git"


# ---------------------------------------------------------------------------
# _check_groundtruth_toml
# ---------------------------------------------------------------------------


def test_check_groundtruth_toml_missing(tmp_path: Path) -> None:
    """_check_groundtruth_toml() with missing file → fail."""
    result = _check_groundtruth_toml(tmp_path)
    assert result.status == "fail"
    assert result.found is False


def test_check_groundtruth_toml_valid(tmp_path: Path) -> None:
    """_check_groundtruth_toml() with valid file → pass."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    result = _check_groundtruth_toml(tmp_path)
    assert result.status == "pass"
    assert result.found is True


def test_check_groundtruth_toml_invalid(tmp_path: Path) -> None:
    """_check_groundtruth_toml() with invalid TOML → fail."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("this is not = valid toml [\n", encoding="utf-8")
    result = _check_groundtruth_toml(tmp_path)
    assert result.status == "fail"


# ---------------------------------------------------------------------------
# _check_db_schema
# ---------------------------------------------------------------------------


def test_check_db_schema_missing(tmp_path: Path) -> None:
    """_check_db_schema() with missing db → fail."""
    result = _check_db_schema(tmp_path)
    assert result.status == "fail"
    assert result.found is False


def test_check_db_schema_valid(tmp_path: Path) -> None:
    """_check_db_schema() with correct schema → pass."""
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE specifications (id TEXT PRIMARY KEY)")
    conn.execute("CREATE TABLE tests (id TEXT PRIMARY KEY)")
    conn.execute("CREATE TABLE work_items (id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()
    result = _check_db_schema(tmp_path)
    assert result.status == "pass"
    assert result.found is True


def test_check_db_schema_missing_tables(tmp_path: Path) -> None:
    """_check_db_schema() with db missing expected tables → fail."""
    db_path = tmp_path / "groundtruth.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE only_one_table (id TEXT PRIMARY KEY)")
    conn.commit()
    conn.close()
    result = _check_db_schema(tmp_path)
    assert result.status == "fail"


# ---------------------------------------------------------------------------
# _check_hooks
# ---------------------------------------------------------------------------


def test_check_hooks_no_dir(tmp_path: Path) -> None:
    """_check_hooks() with no hooks dir → fail."""
    result = _check_hooks(tmp_path, "local-only")
    assert result.status == "fail"
    assert result.found is False


def test_check_hooks_all_required_present(tmp_path: Path) -> None:
    """_check_hooks() with all required hooks → pass."""
    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # local-only profile requires: assertion-check.py, spec-classifier.py
    for name in ("assertion-check.py", "spec-classifier.py"):
        (hooks_dir / name).write_text("# hook", encoding="utf-8")
    result = _check_hooks(tmp_path, "local-only")
    assert result.status == "pass"


def test_check_hooks_missing_required_is_warning(tmp_path: Path) -> None:
    """_check_hooks() with missing required hooks → warning."""
    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # Only one hook present
    (hooks_dir / "assertion-check.py").write_text("# hook", encoding="utf-8")
    result = _check_hooks(tmp_path, "local-only")
    assert result.status == "warning"


# ---------------------------------------------------------------------------
# _check_rules
# ---------------------------------------------------------------------------


def test_check_rules_no_dir(tmp_path: Path) -> None:
    """_check_rules() with no rules dir → fail."""
    result = _check_rules(tmp_path, "local-only")
    assert result.status == "fail"


def test_check_rules_with_files(tmp_path: Path) -> None:
    """_check_rules() with rule files → pass."""
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "prime-builder.md").write_text("# rule", encoding="utf-8")
    result = _check_rules(tmp_path, "local-only")
    assert result.status == "pass"


def test_check_rules_empty_dir_is_warning(tmp_path: Path) -> None:
    """_check_rules() with empty rules dir → warning."""
    rules_dir = tmp_path / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    result = _check_rules(tmp_path, "local-only")
    assert result.status == "warning"


# ---------------------------------------------------------------------------
# _check_settings_classifiers
# ---------------------------------------------------------------------------


def test_check_settings_classifiers_no_file(tmp_path: Path) -> None:
    """Missing settings.local.json → warning."""
    result = _check_settings_classifiers(tmp_path)
    assert result.status == "warning"
    assert result.found is False


def test_check_settings_classifiers_valid_intake(tmp_path: Path) -> None:
    """Valid settings with intake-classifier.py active → pass."""
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings = {"hooks": {"UserPromptSubmit": [{"command": "python .claude/hooks/intake-classifier.py"}]}}
    (settings_dir / "settings.local.json").write_text(json.dumps(settings), encoding="utf-8")
    result = _check_settings_classifiers(tmp_path)
    assert result.status == "pass"


def test_check_settings_classifiers_both_active_warning(tmp_path: Path) -> None:
    """Both classifiers active → warning."""
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings = {
        "hooks": {
            "UserPromptSubmit": [
                {"command": "python .claude/hooks/intake-classifier.py"},
                {"command": "python .claude/hooks/spec-classifier.py"},
            ]
        }
    }
    (settings_dir / "settings.local.json").write_text(json.dumps(settings), encoding="utf-8")
    result = _check_settings_classifiers(tmp_path)
    assert result.status == "warning"


def test_check_settings_classifiers_neither_active_warning(tmp_path: Path) -> None:
    """Neither classifier active → warning."""
    settings_dir = tmp_path / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings = {"hooks": {"UserPromptSubmit": [{"command": "python .claude/hooks/other.py"}]}}
    (settings_dir / "settings.local.json").write_text(json.dumps(settings), encoding="utf-8")
    result = _check_settings_classifiers(tmp_path)
    assert result.status == "warning"


# ---------------------------------------------------------------------------
# DoctorReport
# ---------------------------------------------------------------------------


def test_doctor_report_overall_fail_if_required_fails() -> None:
    """DoctorReport.overall = 'fail' if any required check fails."""
    checks = [
        ToolCheck(name="A", required=True, found=False, status="fail"),
        ToolCheck(name="B", required=False, found=True, status="pass"),
    ]
    report = DoctorReport(checks=checks)
    assert report.overall == "fail"


def test_doctor_report_overall_warning() -> None:
    """DoctorReport.overall = 'warning' if warnings but no required fails."""
    checks = [
        ToolCheck(name="A", required=False, found=True, status="warning"),
        ToolCheck(name="B", required=True, found=True, status="pass"),
    ]
    report = DoctorReport(checks=checks)
    assert report.overall == "warning"


def test_doctor_report_overall_pass() -> None:
    """DoctorReport.overall = 'pass' if all checks pass."""
    checks = [
        ToolCheck(name="A", required=True, found=True, status="pass"),
        ToolCheck(name="B", required=False, found=True, status="pass"),
    ]
    report = DoctorReport(checks=checks)
    assert report.overall == "pass"


# ---------------------------------------------------------------------------
# run_doctor
# ---------------------------------------------------------------------------


def test_run_doctor_local_only_minimal_project(tmp_path: Path) -> None:
    """run_doctor() runs without error on a minimal local-only project dir."""
    # Create minimal project structure
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")

    report = run_doctor(tmp_path, "local-only")
    assert isinstance(report, DoctorReport)
    assert report.profile == "local-only"
    assert len(report.checks) > 0


def test_run_doctor_returns_fail_for_missing_db(tmp_path: Path) -> None:
    """run_doctor() includes a 'fail' check when groundtruth.db is missing."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")

    report = run_doctor(tmp_path, "local-only")
    db_check = next((c for c in report.checks if c.name == "Knowledge DB"), None)
    assert db_check is not None
    assert db_check.status == "fail"
