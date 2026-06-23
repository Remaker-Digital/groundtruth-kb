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
    _check_bridge_dispatch_liveness,
    _check_db_schema,
    _check_dispatcher_config_cli_only_guard,
    _check_git,
    _check_groundtruth_toml,
    _check_harness_metadata_freshness,
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


def _write_harness_metadata_freshness_fixture(
    root: Path,
    *,
    dispatch_cost: int = 20,
    include_routing: bool = True,
    stale_local_text: bool = False,
) -> None:
    """Create a minimal API-harness routing + dispatcher metadata fixture."""
    if include_routing:
        (root / ".api-harness").mkdir(parents=True, exist_ok=True)
        (root / ".api-harness" / "routing.toml").write_text(
            "schema_version = 1\n"
            "\n"
            "[models.kimi-k2-7-code-cloud]\n"
            'model_id = "kimi-k2.7-code:cloud"\n'
            'provider = "ollama"\n'
            "tool_calling_supported = true\n"
            'allowed_tools = ["Read", "Write"]\n'
            "\n"
            "[routing.ollama]\n"
            'default_model = "kimi-k2-7-code-cloud"\n'
            "timeout_seconds = 180\n",
            encoding="utf-8",
        )

    (root / "config" / "dispatcher").mkdir(parents=True, exist_ok=True)
    (root / "config" / "dispatcher" / "rules.toml").write_text(
        "schema_version = 1\n"
        "\n"
        "[harnesses.D]\n"
        'description = "Ollama-shim: cloud-routed LO dispatch target '
        '(current route: kimi-k2-7-code-cloud via cloud API)."\n'
        "can_receive_dispatch = true\n"
        f"dispatch_cost = {dispatch_cost}\n"
        "dispatch_quality = 62\n"
        "dispatch_availability = 95\n",
        encoding="utf-8",
    )

    (root / "harness-state").mkdir(parents=True, exist_ok=True)
    (root / "harness-state" / "harness-registry.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {
                        "id": "D",
                        "harness_name": "ollama",
                        "harness_type": "ollama",
                        "status": "suspended",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    if stale_local_text:
        canonical_text = "### ollama\n\n**Definition:** Locally hosts open-weight models via http://localhost:11434.\n"
    else:
        canonical_text = (
            "### ollama\n\n"
            "**Definition:** The GT-KB Ollama harness route is currently cloud-backed via "
            "`kimi-k2-7-code-cloud`; it is not serving local models.\n"
        )
    (root / ".claude" / "rules").mkdir(parents=True, exist_ok=True)
    (root / ".claude" / "rules" / "canonical-terminology.md").write_text(canonical_text, encoding="utf-8")
    (root / ".claude" / "rules" / "operating-model.md").write_text(canonical_text, encoding="utf-8")
    detail = root / "groundtruth-kb" / "docs" / "reference"
    detail.mkdir(parents=True, exist_ok=True)
    (detail / "canonical-terminology-detail.md").write_text(canonical_text, encoding="utf-8")


def _write_dispatcher_config_cli_only_guard_fixture(root: Path, *, omit_guard_marker: bool = False) -> None:
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "implementation_start_gate.py").write_text(
        "GTKB-DISPATCHER-CONFIG-CLI-ONLY\nconfig/dispatcher/rules.toml\n",
        encoding="utf-8",
    )
    protected_guard_text = "config/dispatcher/rules.toml\n"
    if not omit_guard_marker:
        protected_guard_text += "dispatcher_config_cli_only\n"
    (root / "scripts" / "protected_mutation_guard.py").write_text(protected_guard_text, encoding="utf-8")

    transactions = root / "groundtruth-kb" / "src" / "groundtruth_kb"
    transactions.mkdir(parents=True, exist_ok=True)
    (transactions / "bridge_dispatch_transactions.py").write_text(
        "\n".join(
            [
                "def set_eligibility(): pass",
                "def set_weights(): pass",
                "def set_caps(): pass",
                "def add_harness(): pass",
                "def remove_harness(): pass",
            ]
        ),
        encoding="utf-8",
    )

    (root / ".codex").mkdir(parents=True, exist_ok=True)
    (root / ".codex" / "hooks.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"command": "implementation-start-gate"}]}]}}),
        encoding="utf-8",
    )
    (root / ".claude").mkdir(parents=True, exist_ok=True)
    (root / ".claude" / "settings.json").write_text(
        json.dumps({"hooks": {"PreToolUse": [{"hooks": [{"command": "implementation-start-gate.py"}]}]}}),
        encoding="utf-8",
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
# _check_harness_metadata_freshness
# ---------------------------------------------------------------------------


def test_harness_metadata_freshness_clean_cloud_route_passes(tmp_path: Path) -> None:
    """Cloud-backed API-harness route with cost >= 20 and fresh text -> PASS."""
    _write_harness_metadata_freshness_fixture(tmp_path)
    result = _check_harness_metadata_freshness(tmp_path)
    assert result.status == "pass", result.message
    assert "cloud routes" in result.message


def test_harness_metadata_freshness_cloud_route_low_cost_fails(tmp_path: Path) -> None:
    """Cloud-backed API-harness route with stale cheap dispatch cost -> FAIL."""
    _write_harness_metadata_freshness_fixture(tmp_path, dispatch_cost=5)
    result = _check_harness_metadata_freshness(tmp_path)
    assert result.status == "fail"
    assert result.required is True
    assert "dispatch_cost=5" in result.message


def test_harness_metadata_freshness_missing_routing_warns(tmp_path: Path) -> None:
    """Missing routing.toml is diagnostic, not a false clean pass."""
    _write_harness_metadata_freshness_fixture(tmp_path, include_routing=False)
    result = _check_harness_metadata_freshness(tmp_path)
    assert result.status == "warning"
    assert ".api-harness/routing.toml missing" in result.message


def test_dispatcher_config_cli_only_guard_passes_with_markers_and_cli_surface(tmp_path: Path) -> None:
    _write_dispatcher_config_cli_only_guard_fixture(tmp_path)

    result = _check_dispatcher_config_cli_only_guard(tmp_path)

    assert result.status == "pass"
    assert "CLI-only guard active" in result.message


def test_dispatcher_config_cli_only_guard_fails_without_stable_guard_reason(tmp_path: Path) -> None:
    _write_dispatcher_config_cli_only_guard_fixture(tmp_path, omit_guard_marker=True)

    result = _check_dispatcher_config_cli_only_guard(tmp_path)

    assert result.status == "fail"
    assert "protected mutation guard lacks stable dispatcher_config_cli_only reason" in result.message


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
                "pending_count": 0,
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


def test_bridge_poller_fresh_file_ok(tmp_path: Path) -> None:
    """dispatch-state recipient updated < 4 min ago → OK."""
    _make_status_file(tmp_path, "claude", _utc_now_minus_seconds(60))
    result = _check_bridge_dispatch_liveness(tmp_path, "claude")
    assert result.status == "pass", f"Expected pass, got {result.status}: {result.message}"
    assert "OK" in result.message


def test_bridge_poller_5_min_old_warn(tmp_path: Path) -> None:
    """dispatch-state recipient updated 5 min ago → WARN."""
    _make_status_file(tmp_path, "codex", _utc_now_minus_seconds(5 * 60 + 10))
    result = _check_bridge_dispatch_liveness(tmp_path, "codex")
    assert result.status == "warning", f"Expected warning, got {result.status}: {result.message}"
    assert "WARN" in result.message


def test_bridge_poller_15_min_old_alarm(tmp_path: Path) -> None:
    """dispatch-state recipient updated 15 min ago → ALARM."""
    _make_status_file(tmp_path, "claude", _utc_now_minus_seconds(15 * 60))
    result = _check_bridge_dispatch_liveness(tmp_path, "claude")
    assert result.status == "fail", f"Expected fail, got {result.status}: {result.message}"
    assert "ALARM" in result.message


def test_bridge_poller_missing_file_not_started(tmp_path: Path) -> None:
    """Missing dispatch-state file → not started (WARN)."""
    result = _check_bridge_dispatch_liveness(tmp_path, "codex")
    assert result.status == "warning", f"Expected warning, got {result.status}: {result.message}"
    assert "not started" in result.message.lower()


def test_bridge_poller_missing_updated_at_field_alarm(tmp_path: Path) -> None:
    """dispatch-state with missing recipients[role].updated_at → ALARM."""
    state_path = tmp_path / _DISPATCH_STATE_REL
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "recipients": {
                    "prime-builder": {"last_result": "no_pending", "pending_count": 0},
                    "loyal-opposition": {"last_result": "no_pending", "pending_count": 0},
                },
            }
        ),
        encoding="utf-8",
    )
    result = _check_bridge_dispatch_liveness(tmp_path, "claude")
    assert result.status == "fail", f"Expected fail, got {result.status}: {result.message}"
    assert "ALARM" in result.message or "updated_at" in result.message


def test_bridge_poller_unknown_last_result_no_error(tmp_path: Path) -> None:
    """Unknown last_result values are displayed as-is without raising an error."""
    for state in ("running", "completed", "custom-state-42"):
        _make_status_file(tmp_path, "claude", _utc_now_minus_seconds(30), state=state)
        result = _check_bridge_dispatch_liveness(tmp_path, "claude")
        # Should not raise; must return a ToolCheck with the last_result value visible
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
        _derive_paired_hook_id("settings.hook.gov09-capture.userpromptsubmit", "userpromptsubmit")
        == "hook.gov09-capture"
    )
    assert (
        _derive_paired_hook_id("settings.hook.owner-decision-capture.posttooluse", "posttooluse")
        == "hook.owner-decision-capture"
    )


def test_settings_hook_registration_gov09_file_missing_is_fail(tmp_path: Path) -> None:
    """§B.4 case 1: bridge profile, hook file missing → ``fail``."""
    reg = _get_registration("settings.hook.gov09-capture.userpromptsubmit")
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.name == f"settings:{reg.id}"
    assert result.status == "fail"
    assert result.required is True
    assert "gov09-capture.py" in result.message


def test_settings_hook_registration_gov09_file_present_empty_event_is_warning(
    tmp_path: Path,
) -> None:
    """§B.4 case 2: hook file present, ``hooks['UserPromptSubmit']`` empty → ``warning``."""
    reg = _get_registration("settings.hook.gov09-capture.userpromptsubmit")
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
    """§B.4 case 4: gov09-capture entry appears in ``PreToolUse`` instead of ``UserPromptSubmit``
    → ``warning`` (the event-correct location is what's checked)."""
    reg = _get_registration("settings.hook.gov09-capture.userpromptsubmit")
    _touch_hook_file(tmp_path, reg.hook_filename)
    _write_settings_hooks(tmp_path, {"PreToolUse": [_hook_entry(reg.hook_filename)]})
    result = _check_settings_hook_registration_drift(tmp_path, "dual-agent", reg)
    assert result.status == "warning"


def test_settings_hook_registration_base_profile_is_pass_and_not_required(tmp_path: Path) -> None:
    """§B.4 case 5 (partial): on a non-bridge profile the check degrades to
    ``pass`` with ``required=False`` without inspecting the filesystem."""
    reg = _get_registration("settings.hook.gov09-capture.userpromptsubmit")
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
