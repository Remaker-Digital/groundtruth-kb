# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.project.doctor — workstation readiness checks."""

from __future__ import annotations

import inspect
import json
import sqlite3
from datetime import UTC
from pathlib import Path

from groundtruth_kb.project.doctor import (
    DoctorReport,
    ToolCheck,
    _check_db_schema,
    _check_deliberation_search_backend,
    _check_git,
    _check_groundtruth_toml,
    _check_hooks,
    _check_python,
    _check_rules,
    _check_settings_hook_registration_drift,
    _derive_paired_hook_id,
    run_doctor,
)
from groundtruth_kb.project.managed_registry import (
    SettingsHookRegistration,
    find_artifact_by_id,
)


def _write_deliberation_db(root: Path, *ids: str) -> None:
    from groundtruth_kb.db import KnowledgeDB

    db = KnowledgeDB(root / "groundtruth.db")
    conn = db._get_conn()
    for delib_id in ids:
        conn.execute(
            """INSERT INTO deliberations
               (id, version, source_type, title, summary, content, changed_by, changed_at, change_reason)
               VALUES (?, 1, 'report', ?, 'summary', 'content', 'test', '2026-07-06T00:00:00Z', 'test')""",
            (delib_id, delib_id),
        )
    conn.commit()
    db.close()


class _FakeChromaCollection:
    def __init__(self, metadatas: list[dict[str, str]]) -> None:
        self._metadatas = metadatas

    def count(self) -> int:
        return len(self._metadatas)

    def get(self, *, include: list[str]) -> dict[str, list[dict[str, str]]]:
        assert include == ["metadatas"]
        return {"metadatas": self._metadatas}


def _install_fake_chromadb(monkeypatch, metadatas: list[dict[str, str]]) -> None:
    from groundtruth_kb import db as db_mod

    class FakeClient:
        def __init__(self, *, path: str) -> None:
            self.path = path

        def get_collection(self, *, name: str) -> _FakeChromaCollection:
            assert name == "deliberations"
            return _FakeChromaCollection(metadatas)

    class FakeChroma:
        PersistentClient = FakeClient

    monkeypatch.setattr(db_mod, "HAS_CHROMADB", True)
    monkeypatch.setattr(db_mod, "chromadb", FakeChroma)


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
# _check_harness_metadata_freshness
# ---------------------------------------------------------------------------


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
# _check_deliberation_search_backend
# ---------------------------------------------------------------------------


def test_deliberation_search_backend_fresh_index_passes(monkeypatch, tmp_path: Path) -> None:
    _write_deliberation_db(tmp_path, "DELIB-0001", "DELIB-0002")
    (tmp_path / ".groundtruth-chroma").mkdir()
    _install_fake_chromadb(
        monkeypatch,
        [{"delib_id": "DELIB-0001"}, {"delib_id": "DELIB-0002"}, {"delib_id": "DELIB-0002"}],
    )

    result = _check_deliberation_search_backend(tmp_path)

    assert result.status == "pass"
    assert result.required is True
    assert "indexed 2/2 current deliberations" in result.message


def test_deliberation_search_backend_stale_index_fails(monkeypatch, tmp_path: Path) -> None:
    _write_deliberation_db(tmp_path, "DELIB-0001", "DELIB-0002")
    (tmp_path / ".groundtruth-chroma").mkdir()
    _install_fake_chromadb(monkeypatch, [{"delib_id": "DELIB-0001"}])

    result = _check_deliberation_search_backend(tmp_path)

    assert result.status == "fail"
    assert result.required is True
    assert result.found is True
    assert "index_stale" in result.message
    assert "indexed 1/2 current deliberations" in result.message
    assert "gt deliberations rebuild-index" in result.message


def test_deliberation_search_backend_missing_chromadb_fails(monkeypatch, tmp_path: Path) -> None:
    from groundtruth_kb import db as db_mod

    _write_deliberation_db(tmp_path, "DELIB-0001")
    monkeypatch.setattr(db_mod, "HAS_CHROMADB", False)
    monkeypatch.setattr(db_mod, "chromadb", None)

    result = _check_deliberation_search_backend(tmp_path)

    assert result.status == "fail"
    assert result.required is True
    assert result.found is False
    assert "chromadb_unavailable" in result.message


def test_run_doctor_bridge_profile_wires_deliberation_search_backend_check() -> None:
    source = inspect.getsource(run_doctor)

    assert "checks.append(_check_deliberation_search_backend(target))" in source


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
# _check_bridge_dispatch_liveness — bridge liveness checks
# ---------------------------------------------------------------------------


_DISPATCH_STATE_REL = Path(".gtkb-state/bridge-poller/dispatch-state.json")


def _agent_to_role(agent: str) -> str:
    return {"claude": "prime-builder", "codex": "loyal-opposition"}.get(agent, agent)


def _make_status_file(
    tmp_path: Path,
    agent: str,
    updated_at: str,
    state: str = "no_pending",
    pending_count: int = 0,
) -> Path:
    """Write a smart-poller dispatch-state JSON file under the new path.

    The smart poller writes a single ``dispatch-state.json`` containing all
    recipients. To make existing per-agent tests still meaningful, this
    helper writes both ``prime`` and ``codex`` entries; the agent under
    test gets the supplied ``updated_at`` and ``last_result``, and the
    other recipient gets a fresh sentinel timestamp so cross-agent isolation
    is exercised.
    """
    role = _agent_to_role(agent)
    other_role = "loyal-opposition" if role == "prime-builder" else "prime-builder"
    state_path = tmp_path / _DISPATCH_STATE_REL
    state_path.parent.mkdir(parents=True, exist_ok=True)
    fresh_iso = _utc_now_minus_seconds(0)
    payload = {
        "schema_version": 1,
        "updated_at": fresh_iso,
        "recipients": {
            role: {
                "updated_at": updated_at,
                "last_result": state,
                "pending_count": pending_count,
                "raw_pending_count": 0,
                "filtered_terminal_count": 0,
                "signature": "test-fixture",
            },
            other_role: {
                "updated_at": fresh_iso,
                "last_result": "no_pending",
                "pending_count": 0,
                "raw_pending_count": 0,
                "filtered_terminal_count": 0,
                "signature": "test-fixture-other",
            },
        },
    }
    state_path.write_text(json.dumps(payload), encoding="utf-8")
    return state_path


def _utc_now_minus_seconds(seconds: int) -> str:
    """Return an ISO-8601 UTC timestamp for *seconds* ago."""
    from datetime import datetime, timedelta

    t = datetime.now(tz=UTC) - timedelta(seconds=seconds)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


# -- Helper-level supplemental coverage (non-substituting per GOV-19-A1) -----
# The primary public-surface (``run_doctor``) coverage lives in
# tests/test_doctor_bridge_poller.py per
# bridge/gtkb-bridge-poller-doctor-path-2026-05-02-003.md TP1-TP7. The
# tests below remain as helper-level regression coverage on the internal
# ``_check_bridge_dispatch_liveness`` contract; they do not substitute for the
# public-surface tests.


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
        _derive_paired_hook_id("settings.hook.gov09-capture.userpromptsubmit", "userpromptsubmit")
        == "hook.gov09-capture"
    )
    assert (
        _derive_paired_hook_id("settings.hook.spec-event-surfacer.posttooluse", "posttooluse")
        == "hook.spec-event-surfacer"
    )


def test_settings_hook_registration_owner_decision_present_and_registered_is_pass(
    tmp_path: Path,
) -> None:
    """§B.4 case 3: PostToolUse record: file present, registered in correct event → ``pass``."""
    reg = _get_registration("settings.hook.spec-event-surfacer.posttooluse")
    _touch_hook_file(tmp_path, reg.hook_filename)
    _write_settings_hooks(tmp_path, {"PostToolUse": [_hook_entry(reg.hook_filename)]})
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.status == "pass"
    assert "PostToolUse" in result.message


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
