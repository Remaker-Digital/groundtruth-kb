"""Tests for the GT-KB isolation program backstop."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "isolation_program_backstop.py"
RELEASE_GATE_PATH = Path(__file__).resolve().parents[2] / "scripts" / "release_candidate_gate.py"


def _load_backstop_module():
    spec = importlib.util.spec_from_file_location("isolation_program_backstop", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["isolation_program_backstop"] = module
    spec.loader.exec_module(module)
    return module


def _load_gate_module():
    spec = importlib.util.spec_from_file_location("release_candidate_gate", RELEASE_GATE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["release_candidate_gate"] = module
    spec.loader.exec_module(module)
    return module


def test_backstop_clean_tree_exit_zero(tmp_path: Path) -> None:
    mod = _load_backstop_module()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "clean.py").write_text("print('clean')\n", encoding="utf-8")

    payload = mod.scan(tmp_path)

    assert payload["status"] == "pass"
    assert payload["violations"] == []
    assert payload["allowed_references"] == []
    assert payload["scanned_files"] == ["scripts/clean.py"]


def test_backstop_detects_unauthorized_application_reference(tmp_path: Path) -> None:
    mod = _load_backstop_module()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "bad.py").write_text(
        'TARGET = "applications/Agent_Red/src/app.py"\n',
        encoding="utf-8",
    )

    payload = mod.scan(tmp_path, include_history=True)

    assert payload["status"] == "fail"
    assert payload["violations"] == [
        {
            "path": "scripts/bad.py",
            "line": 1,
            "column": 11,
            "reference": "applications/Agent_Red/src/app.py",
            "reason": None,
        }
    ]


def test_backstop_allows_documented_cross_scope_references(tmp_path: Path) -> None:
    mod = _load_backstop_module()
    bridge = tmp_path / "bridge"
    rules = tmp_path / ".claude" / "rules"
    tests = tmp_path / "platform_tests"
    bridge.mkdir()
    rules.mkdir(parents=True)
    tests.mkdir()
    (bridge / "thread.md").write_text("Historical ref: applications/Agent_Red/src/app.py\n", encoding="utf-8")
    (rules / "project-root-boundary.md").write_text("Convention: applications/<name>/\n", encoding="utf-8")
    (tests / "fixture.py").write_text('REF = "applications/Demo_App/file.txt"\n', encoding="utf-8")

    payload = mod.scan(tmp_path, include_history=True)

    assert payload["status"] == "pass"
    assert payload["violations"] == []
    reasons = {item["reason"] for item in payload["allowed_references"]}
    assert reasons == {"bridge history", "governance and operating-model rule", "platform test fixture"}


def test_backstop_prunes_generated_temp_directories(tmp_path: Path) -> None:
    mod = _load_backstop_module()
    temp_dir = tmp_path / ".pytest-basetemp-codex"
    temp_dir.mkdir()
    (temp_dir / "bad.py").write_text('REF = "applications/Agent_Red/src/app.py"\n', encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "clean.py").write_text("print('clean')\n", encoding="utf-8")

    payload = mod.scan(tmp_path)

    assert payload["status"] == "pass"
    assert payload["violations"] == []
    assert payload["scanned_files"] == ["scripts/clean.py"]


def test_backstop_default_scan_excludes_history_surfaces(tmp_path: Path) -> None:
    mod = _load_backstop_module()
    (tmp_path / "bridge").mkdir()
    (tmp_path / "bridge" / "thread.md").write_text("applications/Agent_Red/src/app.py\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "clean.py").write_text("print('clean')\n", encoding="utf-8")

    payload = mod.scan(tmp_path)

    assert payload["status"] == "pass"
    assert payload["violations"] == []
    assert payload["scanned_files"] == ["scripts/clean.py"]


def test_backstop_json_cli_shape(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "bad.py").write_text("applications/Agent_Red\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--project-root", str(tmp_path), "--json"],
        text=True,
        capture_output=True,
        encoding="utf-8",
        timeout=30,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert set(payload) == {"status", "project_root", "violations", "allowed_references", "scanned_files"}
    assert payload["status"] == "fail"
    assert payload["violations"][0]["path"] == "scripts/bad.py"


def test_release_gate_fails_closed_when_backstop_script_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = _load_gate_module()
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    with pytest.raises(gate.GateFailure, match="backstop script is missing"):
        gate._check_isolation_program_backstop()


def test_release_gate_fails_closed_when_backstop_command_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    gate = _load_gate_module()
    script_dir = tmp_path / "scripts"
    script_dir.mkdir()
    (script_dir / "isolation_program_backstop.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
    monkeypatch.setattr(gate, "PROJECT_ROOT", tmp_path)

    def fake_run(command, *, timeout=300, env=None):
        raise gate.GateFailure("Command failed after 0.1s: " + " ".join(command))

    monkeypatch.setattr(gate, "_run", fake_run)

    with pytest.raises(gate.GateFailure, match="isolation_program_backstop.py"):
        gate._check_isolation_program_backstop()


def test_release_gate_invokes_backstop_before_pytest(monkeypatch: pytest.MonkeyPatch) -> None:
    gate = _load_gate_module()
    commands = []

    def fake_run(command, *, timeout=300, env=None):
        commands.append(command)

    monkeypatch.setattr(gate, "_run", fake_run)

    gate._python_gates()

    backstop_index = commands.index([sys.executable, "scripts/isolation_program_backstop.py"])
    pytest_index = next(
        index for index, command in enumerate(commands) if command[:3] == [sys.executable, "-m", "pytest"]
    )
    assert backstop_index < pytest_index
    assert "platform_tests/scripts/test_isolation_program_backstop.py" in commands[pytest_index]
