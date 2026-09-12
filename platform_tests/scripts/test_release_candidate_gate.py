"""Tests for the non-deploying release candidate gate script."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "release_candidate_gate.py"


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("release_candidate_gate", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["release_candidate_gate"] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("exit_code", [0, 5])
def test_secret_scan_report_is_private_to_each_invocation(tmp_path, monkeypatch, exit_code):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    report_paths = []

    def fake_run(command, **kwargs):
        assert kwargs["cwd"] == tmp_path
        report_path = Path(command[command.index("--report-json") + 1])
        if not report_path.is_absolute():
            report_path = tmp_path / report_path
        report_paths.append(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps({"mode": "tracked", "paths_scanned": 2, "finding_count": 0, "findings": []}),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, exit_code, stdout="", stderr="")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    for _ in range(2):
        if exit_code:
            with pytest.raises(gate.GateFailure, match="Tracked redacted secret scan failed"):
                gate._check_tracked_secret_scan()
        else:
            gate._check_tracked_secret_scan()
        assert not report_paths[-1].exists()
    assert report_paths[0] != report_paths[1]
    assert not list(tmp_path.iterdir())


def test_release_help_does_not_offer_frozen_modernization_certification(monkeypatch, capsys):
    gate = _load_gate_module()
    monkeypatch.setattr(sys, "argv", ["release_candidate_gate.py", "--help"])
    with pytest.raises(SystemExit) as exc:
        gate.main()
    assert exc.value.code == 0
    assert "modernization" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "payload",
    [
        None,
        "{",
        "[]",
        "{}",
        '{"mode":"tracked","paths_scanned":0,"finding_count":0,"findings":[]}',
        '{"mode":"tracked","paths_scanned":1,"finding_count":1,"findings":[]}',
    ],
)
def test_scan_cannot_pass_without_a_valid_current_report(tmp_path, monkeypatch, payload):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    reports = []

    def fake_run(command, **kwargs):
        report_path = Path(command[-1])
        reports.append(report_path)
        if payload is not None:
            report_path.write_text(payload, encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="PASS", stderr="")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    with pytest.raises(gate.GateFailure):
        gate._check_tracked_secret_scan()
    assert not reports[0].parent.exists()


def test_scan_cleans_partial_report_when_the_process_times_out(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    reports = []

    def timeout(command, **kwargs):
        report_path = Path(command[-1])
        reports.append(report_path)
        report_path.write_text("partial", encoding="utf-8")
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr(gate.subprocess, "run", timeout)
    with pytest.raises(subprocess.TimeoutExpired):
        gate._check_tracked_secret_scan()
    assert not reports[0].parent.exists()


def test_release_scan_runs_the_real_cli_against_tracked_files(tmp_path, monkeypatch, capsys):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True, capture_output=True)
    (tmp_path / "clean.txt").write_text("A harmless tracked fixture.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "clean.txt"], check=True, capture_output=True)
    gate._check_tracked_secret_scan()
    assert "PASS tracked redacted secret scan (1 paths, 0 findings)" in capsys.readouterr().out
    assert {p.name for p in tmp_path.iterdir()} == {".git", "clean.txt"}


def _valid_dev_inventory_payload(gate, generated_at: str | None = None) -> dict:
    _default_max_age, _relative_path, _validate = gate._dev_inventory_helpers()
    from scripts import collect_dev_environment_inventory as collector

    if generated_at is None:
        # Use a fresh timestamp so this fixture does not become stale as time
        # passes (per gtkb-env-inventory-drift-control-001-008 NO-GO F1).
        from datetime import UTC, datetime

        generated_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "schema_version": collector.SCHEMA_VERSION,
        "generated_at": generated_at,
        "project": {},
        "collector": {},
        "host": {},
        "shell": {},
        "toolchain": {},
        "harnesses": {},
        "repo_configured_surfaces": {},
        "runtime_provided_capabilities": {},
        "role_by_harness_compatibility": [
            {
                "harness": harness,
                "role": role,
                "assignment": {"status": "configured", "evidence": "test"},
                "capabilities": {
                    dimension: {"status": "unknown", "evidence": "test"}
                    for dimension in collector.CAPABILITY_DIMENSIONS
                },
            }
            for harness, role in collector.MATRIX_ROWS
        ],
        "redaction": {"status": "pass"},
        "verification": {},
    }


def _write_dev_inventory(gate, root: Path, payload: dict) -> Path:
    _default_max_age, relative_path, _validate = gate._dev_inventory_helpers()
    path = root / relative_path
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def _write_valid_secret_gate_files(root: Path) -> None:
    hooks_dir = root / ".githooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit").write_text(
        "python -m groundtruth_kb secrets scan --staged --redacted --fail-on verified-provider\n",
        encoding="utf-8",
    )
    (hooks_dir / "pre-push").write_text(
        (
            'python -m groundtruth_kb secrets scan --range "$remote_sha..$local_sha" '
            "--redacted --fail-on verified-provider\n"
        ),
        encoding="utf-8",
    )
    (hooks_dir / "setup-hooks.sh").write_text(
        "git config core.hooksPath .githooks\nchmod +x .githooks/pre-commit\nchmod +x .githooks/pre-push\n",
        encoding="utf-8",
    )


def _write_valid_secret_workflow(root: Path) -> None:
    workflow = root / ".github" / "workflows" / "gtkb-secrets-scan.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "\n".join(
            [
                "on:",
                "  pull_request:",
                "  push:",
                "  workflow_dispatch:",
                "jobs:",
                "  secrets-scan:",
                "    steps:",
                (
                    "      - run: python -m groundtruth_kb secrets scan --tracked --redacted "
                    "--report-json .quality/gtkb-secrets.json --fail-on verified-provider"
                ),
                "      - uses: actions/upload-artifact@v4",
            ]
        ),
        encoding="utf-8",
    )


def test_secret_manifest_check_fails_when_generated_manifest_exists(tmp_path, monkeypatch):
    gate = _load_gate_module()
    unsafe = tmp_path / "scripts" / "deploy" / "production-gateway-generated.yaml"
    unsafe.parent.mkdir(parents=True)
    unsafe.write_text("generated-placeholder: should-not-exist\n", encoding="utf-8")
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="Unsafe generated production manifest"):
        gate._check_secret_manifest_removed()


def test_secret_manifest_check_allows_pending_git_deletion(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    def fake_run(command, **_kwargs):
        if command[:2] == ["git", "ls-files"]:
            return subprocess.CompletedProcess(command, 0, stdout="scripts/deploy/production-gateway-generated.yaml\n")
        if command[:3] == ["git", "status", "--short"]:
            return subprocess.CompletedProcess(
                command, 0, stdout="D  scripts/deploy/production-gateway-generated.yaml\n"
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)

    gate._check_secret_manifest_removed()


def test_secret_manifest_check_fails_when_still_tracked_without_deletion(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    def fake_run(command, **_kwargs):
        if command[:2] == ["git", "ls-files"]:
            return subprocess.CompletedProcess(command, 0, stdout="scripts/deploy/production-gateway-generated.yaml\n")
        if command[:3] == ["git", "status", "--short"]:
            return subprocess.CompletedProcess(command, 0, stdout="")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)

    with pytest.raises(gate.GateFailure, match="still tracked"):
        gate._check_secret_manifest_removed()


def test_secret_gate_presence_requires_tracked_staged_scan_hook(tmp_path, monkeypatch):
    gate = _load_gate_module()
    _write_valid_secret_gate_files(tmp_path)
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    commands = []

    def fake_run(command, **_kwargs):
        commands.append(command)
        if command[:3] == ["git", "config", "--get"]:
            return subprocess.CompletedProcess(command, 0, stdout=".githooks\n")
        if command[:5] == [sys.executable, "-m", "groundtruth_kb", "secrets", "scan"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout="Usage: gt secrets scan --staged --range --paths --tracked --all-refs\n",
            )
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)

    gate._check_secret_gate_present()

    assert ["git", "config", "--get", "core.hooksPath"] in commands
    assert [sys.executable, "-m", "groundtruth_kb", "secrets", "scan", "--help"] in commands


def test_secret_gate_presence_fails_when_pre_commit_hook_is_missing(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="pre-commit hook is missing"):
        gate._check_secret_gate_present()


def test_secret_gate_presence_fails_when_pre_push_hook_is_missing(tmp_path, monkeypatch):
    gate = _load_gate_module()
    _write_valid_secret_gate_files(tmp_path)
    (tmp_path / ".githooks" / "pre-push").unlink()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="pre-push hook is missing"):
        gate._check_secret_gate_present()


def test_secret_gate_presence_fails_when_cli_help_omits_all_refs(tmp_path, monkeypatch):
    gate = _load_gate_module()
    _write_valid_secret_gate_files(tmp_path)
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    def fake_run(command, **_kwargs):
        if command[:3] == ["git", "config", "--get"]:
            return subprocess.CompletedProcess(command, 0, stdout=".githooks\n")
        if command[:5] == [sys.executable, "-m", "groundtruth_kb", "secrets", "scan"]:
            return subprocess.CompletedProcess(command, 0, stdout="Usage: gt secrets scan --staged --range\n")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)

    with pytest.raises(gate.GateFailure, match="--all-refs"):
        gate._check_secret_gate_present()


def test_secret_gate_presence_fails_when_hooks_path_is_not_portable(tmp_path, monkeypatch):
    gate = _load_gate_module()
    _write_valid_secret_gate_files(tmp_path)
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    def fake_run(command, **_kwargs):
        if command[:3] == ["git", "config", "--get"]:
            return subprocess.CompletedProcess(command, 0, stdout=".git/hooks\n")
        raise AssertionError(f"Unexpected command: {command}")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)

    with pytest.raises(gate.GateFailure, match="core.hooksPath"):
        gate._check_secret_gate_present()


def test_secret_ci_workflow_presence_requires_broad_redacted_scan(tmp_path, monkeypatch):
    gate = _load_gate_module()
    _write_valid_secret_workflow(tmp_path)
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    gate._check_secret_ci_workflow_present()


def test_secret_ci_workflow_presence_fails_when_missing(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="secret-scan workflow is missing"):
        gate._check_secret_ci_workflow_present()


def test_secret_ci_workflow_presence_fails_when_path_filtered(tmp_path, monkeypatch):
    gate = _load_gate_module()
    _write_valid_secret_workflow(tmp_path)
    workflow = tmp_path / ".github" / "workflows" / "gtkb-secrets-scan.yml"
    workflow.write_text(workflow.read_text(encoding="utf-8") + "\npaths:\n  - scripts/**\n", encoding="utf-8")
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="path filters"):
        gate._check_secret_ci_workflow_present()


def test_tracked_secret_scan_executes_gate_and_consumes_machine_evidence(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        assert kwargs["cwd"] == tmp_path
        assert kwargs["capture_output"] is True
        report_path = Path(command[-1])
        assert report_path.is_absolute()
        report_path.write_text(
            json.dumps({"mode": "tracked", "paths_scanned": 41, "finding_count": 0, "findings": []}),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 0, stdout="redacted scan passed", stderr="")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    gate._check_tracked_secret_scan()
    assert len(commands) == 1
    assert commands[0][:-1] == [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "secrets",
        "scan",
        "--tracked",
        "--redacted",
        "--fail-on",
        "verified-provider",
        "--report-json",
    ]
    assert not Path(commands[0][-1]).exists()


def test_tracked_secret_scan_fails_on_findings_without_retaining_receipts(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    reports = []

    def fake_run(command, **_kwargs):
        report_path = Path(command[-1])
        reports.append(report_path)
        report_path.write_text(
            json.dumps(
                {
                    "mode": "tracked",
                    "paths_scanned": 42,
                    "finding_count": 1,
                    "findings": [{"severity": "verified-provider", "path": "fixture.txt"}],
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 5, stdout="redacted finding", stderr="")

    monkeypatch.setattr(gate.subprocess, "run", fake_run)
    with pytest.raises(gate.GateFailure, match=r"failed \(exit 5, 1 finding\(s\)\)"):
        gate._check_tracked_secret_scan()
    assert not reports[0].exists()


def test_dev_environment_inventory_gate_passes_valid_public_inventory(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    _write_dev_inventory(gate, tmp_path, _valid_dev_inventory_payload(gate))

    gate._check_dev_environment_inventory(max_age_hours=24)


def test_dev_environment_inventory_gate_fails_when_missing(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="inventory is missing"):
        gate._check_dev_environment_inventory(max_age_hours=24)


def test_dev_environment_inventory_gate_fails_when_malformed(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    _default_max_age, relative_path, _validate = gate._dev_inventory_helpers()
    path = tmp_path / relative_path
    path.parent.mkdir(parents=True)
    path.write_text("{not json\n", encoding="utf-8")

    with pytest.raises(gate.GateFailure, match="malformed JSON"):
        gate._check_dev_environment_inventory(max_age_hours=24)


def test_dev_environment_inventory_gate_fails_when_stale(tmp_path, monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)
    _write_dev_inventory(gate, tmp_path, _valid_dev_inventory_payload(gate, generated_at="2000-01-01T00:00:00Z"))

    with pytest.raises(gate.GateFailure, match="stale"):
        gate._check_dev_environment_inventory(max_age_hours=24)


def test_dev_environment_inventory_drift_gate_fails_on_blocking_result(monkeypatch):
    gate = _load_gate_module()

    def fake_helpers():
        return lambda _root: {
            "status": "fail",
            "blocking": [{"reason": "normalized_inventory_drift", "message": "Current inventory differs"}],
        }

    monkeypatch.setattr(gate, "_dev_inventory_drift_helpers", fake_helpers)

    with pytest.raises(gate.GateFailure, match="Current inventory differs"):
        gate._check_dev_environment_inventory_drift()


def test_dev_environment_inventory_drift_gate_passes_clean_result(monkeypatch):
    gate = _load_gate_module()

    def fake_helpers():
        return lambda _root: {"status": "pass", "outcome": "clean", "blocking": []}

    monkeypatch.setattr(gate, "_dev_inventory_drift_helpers", fake_helpers)

    gate._check_dev_environment_inventory_drift()


def test_agent_red_app_root_minimization_gate_passes(tmp_path, monkeypatch, capsys):
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    class Result:
        ok = True
        actual_entries = [object(), object()]

        def first_error_message(self):
            return "no errors"

    def fake_validate(app_root, *, project_root, tracked_only):
        assert app_root == tmp_path / "applications" / "Agent_Red"
        assert project_root == tmp_path
        assert tracked_only is True
        return Result()

    monkeypatch.setattr(gate, "_agent_red_app_root_minimization_helpers", lambda: fake_validate)

    gate._check_agent_red_app_root_minimization()

    assert "PASS Agent Red app-root minimization (2 top-level artifacts)" in capsys.readouterr().out


def test_agent_red_app_root_minimization_gate_fails(monkeypatch):
    gate = _load_gate_module()

    class Result:
        ok = False
        actual_entries = []

        def first_error_message(self):
            return "unregistered_top_level_artifact: EXTRA.md has no registry entry"

    monkeypatch.setattr(gate, "_agent_red_app_root_minimization_helpers", lambda: lambda *a, **kw: Result())

    with pytest.raises(gate.GateFailure, match="EXTRA.md"):
        gate._check_agent_red_app_root_minimization()


def test_python_version_gate_requires_exact_minor():
    gate = _load_gate_module()
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    impossible = "0.0" if actual != "0.0" else "9.9"

    with pytest.raises(gate.GateFailure, match="required"):
        gate._check_python_version(impossible)


def test_frontend_gate_fails_when_npm_is_missing(monkeypatch):
    gate = _load_gate_module()
    monkeypatch.setattr(gate.shutil, "which", lambda _name: None)

    with pytest.raises(gate.GateFailure, match="npm executable"):
        gate._frontend_gates()


def test_frontend_gate_syncs_admin_env_once_and_disables_admin_lifecycle(monkeypatch):
    gate = _load_gate_module()
    commands = []
    envs = []

    def fake_which(name):
        if name in {"npm.cmd", "npm"}:
            return "npm"
        if name in {"powershell.exe", "powershell", "pwsh"}:
            return "powershell"
        return None

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)
        envs.append(env)

    monkeypatch.setattr(gate.shutil, "which", fake_which)
    monkeypatch.setattr(gate, "_run", fake_run)

    gate._frontend_gates()

    agent_red_root = os.path.join("applications", "Agent_Red")
    widget_project = os.path.join(agent_red_root, "widget")
    admin_projects = [
        os.path.join(agent_red_root, "admin", "standalone"),
        os.path.join(agent_red_root, "admin", "provider"),
        os.path.join(agent_red_root, "admin", "shopify"),
    ]
    assert commands == [
        ["npm", "--prefix", widget_project, "test"],
        ["npm", "--prefix", widget_project, "run", "build"],
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/sync-admin-env.ps1"],
        *[["npm", "--prefix", project, "run", "build"] for project in admin_projects],
    ]
    assert envs[:3] == [None, None, None]
    assert all(env and env.get("npm_config_ignore_scripts") == "true" for env in envs[3:])


def test_python_gate_runs_canonical_harness_conformance_before_pytest(monkeypatch):
    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    assert not any("scripts/check_codex_hook_parity.py" in command for command in commands)
    harness_parity_index = commands.index([sys.executable, "scripts/check_harness_parity.py", "--all"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    assert harness_parity_index < pytest_index
    assert "platform_tests/scripts/test_codex_hook_parity.py" in commands[pytest_index]
    assert "platform_tests/scripts/test_standing_backlog_harvest.py" in commands[pytest_index]
    assert "platform_tests/scripts/test_session_self_initialization.py" in commands[pytest_index]
    assert "platform_tests/scripts/test_collect_dev_environment_inventory.py" in commands[pytest_index]
    assert "platform_tests/scripts/test_check_dev_environment_inventory_drift.py" in commands[pytest_index]
    assert "platform_tests/scripts/test_gtkb_dashboard_control_plane.py" in commands[pytest_index]
    assert "platform_tests/hooks/test_workstream_focus.py" in commands[pytest_index]
    assert "applications/Agent_Red/tests/integrations/test_usage_consumption.py" in commands[pytest_index]


def test_python_gate_runs_environment_isolation_before_pytest(monkeypatch):
    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    env_index = commands.index([sys.executable, "scripts/check_environment_isolation.py"])
    assert not any("scripts/check_codex_hook_parity.py" in command for command in commands)
    harness_parity_index = commands.index([sys.executable, "scripts/check_harness_parity.py", "--all"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    assert harness_parity_index < env_index < pytest_index
    assert "platform_tests/scripts/test_check_environment_isolation.py" in commands[pytest_index]


def test_python_gate_runs_session_overlay_policy_before_pytest(monkeypatch):
    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    overlay_index = commands.index([sys.executable, "scripts/check_session_overlay_policy.py"])
    env_index = commands.index([sys.executable, "scripts/check_environment_isolation.py"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    # Overlay policy must run after the environment-isolation guard and
    # strictly before the pytest suite so drift in .groundtruth/session/overlays/
    # fails the gate before any test collection can touch it.
    assert env_index < overlay_index < pytest_index
    assert "platform_tests/scripts/test_gtkb_overlay.py" in commands[pytest_index]


def test_python_gate_runs_scoped_service_boundary_before_pytest(monkeypatch):
    """The Phase 4 scoped-service boundary checker must run before pytest.

    The no-raw-read guard in ``check_scoped_service_boundary.py`` is the
    enforcement mechanism that keeps ``_database_metrics`` on the scoped
    client. If it only ran after pytest, a regression that put a raw
    ``sqlite3.connect`` back on the summary path could still pass the
    release gate as long as tests were structured around the drift.
    """

    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    scoped_index = commands.index([sys.executable, "scripts/check_scoped_service_boundary.py"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    assert scoped_index < pytest_index
    assert "platform_tests/scripts/test_gtkb_scoped_client.py" in commands[pytest_index]


# ---------------------------------------------------------------------------
# Slice C C4 reachability tests (per GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001 NO-GO -009 F2)
# ---------------------------------------------------------------------------


def test_sot_registry_authority_requires_membership_closed_unpruned_validation(monkeypatch, capsys):
    gate = _load_gate_module()
    from groundtruth_kb.project import registry_control_plane

    calls = []

    def valid_registry(**kwargs):
        calls.append(kwargs)
        return {
            "valid": True,
            "record_count": 50,
            "declaration_digest": "sha256:test-declaration",
            "membership_reconciliation": {
                "membership_complete": True,
                "pruned_envelope_count": 0,
                "release_eligible": True,
            },
        }

    monkeypatch.setattr(registry_control_plane, "validate_registry", valid_registry)

    gate._check_sot_registry_authority()

    assert calls == [{"project_root": gate.PROJECT_ROOT, "require_reverse_closure": True}]
    assert "PASS SoT registry authority (50 records, declaration=sha256:test-declaration" in capsys.readouterr().out


def test_sot_registry_authority_fails_closed_on_membership_gap(monkeypatch):
    gate = _load_gate_module()
    from groundtruth_kb.project import registry_control_plane

    monkeypatch.setattr(
        registry_control_plane,
        "validate_registry",
        lambda **_kwargs: {
            "valid": False,
            "coherent": True,
            "errors": ["registry_membership_incomplete"],
        },
    )

    with pytest.raises(gate.GateFailure, match="registry_membership_incomplete"):
        gate._check_sot_registry_authority()


def test_sot_registry_authority_blocks_pruned_release_census(monkeypatch):
    gate = _load_gate_module()
    from groundtruth_kb.project import registry_control_plane

    monkeypatch.setattr(
        registry_control_plane,
        "validate_registry",
        lambda **_kwargs: {
            "valid": True,
            "record_count": 50,
            "declaration_digest": "sha256:test-declaration",
            "membership_reconciliation": {
                "membership_complete": True,
                "pruned_envelope_count": 2,
                "release_eligible": False,
            },
        },
    )

    with pytest.raises(gate.GateFailure, match="pruned_envelope_count=2"):
        gate._check_sot_registry_authority()
