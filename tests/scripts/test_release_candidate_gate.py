"""Tests for the non-deploying release candidate gate script."""

from __future__ import annotations

import importlib.util
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


def test_secret_manifest_check_fails_when_generated_manifest_exists(tmp_path, monkeypatch):
    gate = _load_gate_module()
    unsafe = tmp_path / "scripts" / "deploy" / "production-gateway-generated.yaml"
    unsafe.parent.mkdir(parents=True)
    unsafe.write_text("secret: should-not-exist\n", encoding="utf-8")
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

    sync_commands = [cmd for cmd in commands if cmd[:4] == ["powershell", "-ExecutionPolicy", "Bypass", "-File"]]
    admin_build_envs = [
        env
        for cmd, env in zip(commands, envs)
        if cmd[:3] == ["npm", "--prefix", os.path.join("admin", "standalone")]
        or cmd[:3] == ["npm", "--prefix", os.path.join("admin", "provider")]
        or cmd[:3] == ["npm", "--prefix", os.path.join("admin", "shopify")]
    ]
    assert len(sync_commands) == 1
    assert len(admin_build_envs) == 3
    assert all(env and env.get("npm_config_ignore_scripts") == "true" for env in admin_build_envs)


def test_python_gate_runs_codex_hook_parity_before_pytest(monkeypatch):
    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    parity_index = commands.index([sys.executable, "scripts/check_codex_hook_parity.py"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    assert parity_index < pytest_index
    assert "tests/scripts/test_codex_hook_parity.py" in commands[pytest_index]
    assert "tests/scripts/test_standing_backlog_harvest.py" in commands[pytest_index]
    assert "tests/scripts/test_session_self_initialization.py" in commands[pytest_index]
    assert "tests/scripts/test_gtkb_dashboard_control_plane.py" in commands[pytest_index]
    assert "tests/hooks/test_workstream_focus.py" in commands[pytest_index]
    assert "tests/integrations/test_usage_consumption.py" in commands[pytest_index]


def test_python_gate_runs_environment_isolation_before_pytest(monkeypatch):
    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    env_index = commands.index([sys.executable, "scripts/check_environment_isolation.py"])
    parity_index = commands.index([sys.executable, "scripts/check_codex_hook_parity.py"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    assert parity_index < env_index < pytest_index
    assert "tests/scripts/test_check_environment_isolation.py" in commands[pytest_index]


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
    assert "tests/scripts/test_gtkb_overlay.py" in commands[pytest_index]


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
    assert "tests/scripts/test_gtkb_scoped_client.py" in commands[pytest_index]
