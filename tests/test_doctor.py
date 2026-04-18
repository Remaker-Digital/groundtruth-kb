# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.doctor — workstation readiness checks."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC
from pathlib import Path

from groundtruth_kb.project.doctor import (
    DoctorReport,
    ToolCheck,
    _check_bridge_poller,
    _check_db_schema,
    _check_git,
    _check_groundtruth_toml,
    _check_hooks,
    _check_python,
    _check_rules,
    _check_settings_classifiers,
    _check_settings_hook_registration_drift,
    _derive_paired_hook_id,
    run_doctor,
)
from groundtruth_kb.project.managed_registry import (
    SettingsHookRegistration,
    find_artifact_by_id,
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


# ---------------------------------------------------------------------------
# _check_bridge_poller — bridge liveness checks
# ---------------------------------------------------------------------------


def _make_status_file(tmp_path: Path, agent: str, updated_at: str, state: str = "clear") -> Path:
    """Write a bridge scan-status JSON file for *agent* under the standard path."""
    logs_dir = tmp_path / "independent-progress-assessments" / "bridge-automation" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    status_path = logs_dir / f"{agent}-scan-status.json"
    status_path.write_text(
        json.dumps({"updatedAtUtc": updated_at, "state": state, "message": "test scan"}),
        encoding="utf-8",
    )
    return status_path


def _utc_now_minus_seconds(seconds: int) -> str:
    """Return an ISO-8601 UTC timestamp for *seconds* ago."""
    from datetime import datetime, timedelta

    t = datetime.now(tz=UTC) - timedelta(seconds=seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_bridge_poller_fresh_file_ok(tmp_path: Path) -> None:
    """Status file updated < 4 min ago → OK."""
    _make_status_file(tmp_path, "claude", _utc_now_minus_seconds(60), state="clear")
    result = _check_bridge_poller(tmp_path, "claude")
    assert result.status == "pass", f"Expected pass, got {result.status}: {result.message}"
    assert "OK" in result.message


def test_bridge_poller_5_min_old_warn(tmp_path: Path) -> None:
    """Status file updated 5 min ago → WARN."""
    _make_status_file(tmp_path, "codex", _utc_now_minus_seconds(5 * 60 + 10), state="clear")
    result = _check_bridge_poller(tmp_path, "codex")
    assert result.status == "warning", f"Expected warning, got {result.status}: {result.message}"
    assert "WARN" in result.message


def test_bridge_poller_15_min_old_alarm(tmp_path: Path) -> None:
    """Status file updated 15 min ago → ALARM."""
    _make_status_file(tmp_path, "claude", _utc_now_minus_seconds(15 * 60), state="clear")
    result = _check_bridge_poller(tmp_path, "claude")
    assert result.status == "fail", f"Expected fail, got {result.status}: {result.message}"
    assert "ALARM" in result.message


def test_bridge_poller_missing_file_not_started(tmp_path: Path) -> None:
    """Missing status file → not started (WARN)."""
    result = _check_bridge_poller(tmp_path, "codex")
    assert result.status == "warning", f"Expected warning, got {result.status}: {result.message}"
    assert "not started" in result.message.lower()


def test_bridge_poller_missing_updated_at_field_alarm(tmp_path: Path) -> None:
    """Status file with missing updatedAtUtc → ALARM."""
    logs_dir = tmp_path / "independent-progress-assessments" / "bridge-automation" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / "claude-scan-status.json").write_text(
        json.dumps({"state": "clear", "message": "no timestamp"}),
        encoding="utf-8",
    )
    result = _check_bridge_poller(tmp_path, "claude")
    assert result.status == "fail", f"Expected fail, got {result.status}: {result.message}"
    assert "ALARM" in result.message or "updatedAtUtc" in result.message


def test_bridge_poller_unknown_state_no_error(tmp_path: Path) -> None:
    """Unknown state values are displayed as-is without raising an error."""
    for state in ("running", "completed", "custom-state-42"):
        _make_status_file(tmp_path, "claude", _utc_now_minus_seconds(30), state=state)
        result = _check_bridge_poller(tmp_path, "claude")
        # Should not raise; must return a ToolCheck with the state visible
        assert isinstance(result, ToolCheck)
        assert state in result.message


# ---------------------------------------------------------------------------
# _check_settings_hook_registration_drift — §B.3 generalized composite check
# Covers gtkb-da-governance-completeness-implementation-015 §B.4 cases 1-5
# plus a back-compat assertion preserving the legacy scanner-safe-writer name.
# ---------------------------------------------------------------------------


def _write_settings_hooks(target: Path, hooks: dict[str, list[dict[str, object]]]) -> None:
    """Write ``.claude/settings.json`` with the given hooks map."""
    settings_dir = target / ".claude"
    settings_dir.mkdir(parents=True, exist_ok=True)
    (settings_dir / "settings.json").write_text(json.dumps({"hooks": hooks}, indent=2) + "\n", encoding="utf-8")


def _touch_hook_file(target: Path, filename: str) -> None:
    """Create an empty ``.claude/hooks/<filename>`` so the liveness probe passes."""
    hooks_dir = target / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / filename).write_text("# stub\n", encoding="utf-8")


def _hook_entry(filename: str) -> dict[str, object]:
    """Return a canonical hook entry shape referencing the given hook file."""
    return {"hooks": [{"type": "command", "command": f"python .claude/hooks/{filename}"}]}


def _get_registration(reg_id: str) -> SettingsHookRegistration:
    """Resolve a registry record as a SettingsHookRegistration (or fail)."""
    record = find_artifact_by_id(reg_id)
    assert isinstance(record, SettingsHookRegistration)
    return record


def test_derive_paired_hook_id_strips_prefix_and_event_suffix() -> None:
    """``_derive_paired_hook_id`` yields the paired ``hook.<short>`` id."""
    assert (
        _derive_paired_hook_id("settings.hook.turn-marker.userpromptsubmit", "userpromptsubmit") == "hook.turn-marker"
    )
    assert (
        _derive_paired_hook_id("settings.hook.owner-decision-capture.posttooluse", "posttooluse")
        == "hook.owner-decision-capture"
    )


def test_settings_hook_registration_turn_marker_file_missing_is_fail(tmp_path: Path) -> None:
    """§B.4 case 1: bridge profile, hook file missing → ``fail``."""
    reg = _get_registration("settings.hook.turn-marker.userpromptsubmit")
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.name == f"settings:{reg.id}"
    assert result.status == "fail"
    assert result.required is True
    assert "turn-marker.py" in result.message


def test_settings_hook_registration_turn_marker_file_present_empty_event_is_warning(
    tmp_path: Path,
) -> None:
    """§B.4 case 2: hook file present, ``hooks['UserPromptSubmit']`` empty → ``warning``."""
    reg = _get_registration("settings.hook.turn-marker.userpromptsubmit")
    _touch_hook_file(tmp_path, reg.hook_filename)
    _write_settings_hooks(tmp_path, {"UserPromptSubmit": []})
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.status == "warning"
    assert "UserPromptSubmit" in result.message
    assert "settings.json" in result.message


def test_settings_hook_registration_owner_decision_present_and_registered_is_pass(
    tmp_path: Path,
) -> None:
    """§B.4 case 3: PostToolUse record: file present, registered in correct event → ``pass``."""
    reg = _get_registration("settings.hook.owner-decision-capture.posttooluse")
    _touch_hook_file(tmp_path, reg.hook_filename)
    _write_settings_hooks(tmp_path, {"PostToolUse": [_hook_entry(reg.hook_filename)]})
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.status == "pass"
    assert "PostToolUse" in result.message


def test_settings_hook_registration_wrong_event_location_is_warning(tmp_path: Path) -> None:
    """§B.4 case 4: turn-marker entry appears in ``PreToolUse`` instead of ``UserPromptSubmit``
    → ``warning`` (the event-correct location is what's checked)."""
    reg = _get_registration("settings.hook.turn-marker.userpromptsubmit")
    _touch_hook_file(tmp_path, reg.hook_filename)
    _write_settings_hooks(tmp_path, {"PreToolUse": [_hook_entry(reg.hook_filename)]})
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.status == "warning"


def test_settings_hook_registration_base_profile_is_pass_and_not_required(tmp_path: Path) -> None:
    """§B.4 case 5 (partial): on a non-bridge profile the check degrades to
    ``pass`` with ``required=False`` without inspecting the filesystem."""
    reg = _get_registration("settings.hook.turn-marker.userpromptsubmit")
    # No hook file, no settings.json — base profile should still pass.
    result = _check_settings_hook_registration_drift(tmp_path, "local-only", reg)
    assert result.status == "pass"
    assert result.required is False
    assert "base profile" in result.message


def test_run_doctor_local_only_omits_new_settings_checks(tmp_path: Path) -> None:
    """§B.4 case 5 (integration): on ``local-only`` profile the 4 new
    ``settings:`` checks do NOT appear in the report (gated by
    ``p.includes_bridge`` AND by ``doctor_required_profiles`` filter)."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    report = run_doctor(tmp_path, "local-only")
    settings_check_names = [c.name for c in report.checks if c.name.startswith("settings:")]
    assert settings_check_names == [], (
        f"local-only profile must not emit any settings:* checks; got {settings_check_names}"
    )


def test_run_doctor_dual_agent_retains_scanner_safe_writer_check(tmp_path: Path) -> None:
    """§B.4 back-compat assertion: the existing ``scanner-safe-writer`` doctor
    check name is still present in the report for bridge profiles."""
    toml_path = tmp_path / "groundtruth.toml"
    toml_path.write_text("[groundtruth]\ndb_path = 'groundtruth.db'\n", encoding="utf-8")
    report = run_doctor(tmp_path, "dual-agent")
    names = [c.name for c in report.checks]
    assert "scanner-safe-writer" in names, f"scanner-safe-writer must remain as a distinct check name; got {names}"
