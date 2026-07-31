from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_claude_dispatch.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("verify_claude_dispatch", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_registry(root: Path, record: dict) -> None:
    state = root / "harness-state"
    state.mkdir()
    (state / "harness-registry.json").write_text(json.dumps({"schema_version": 1, "harnesses": [record]}))


def _claude_record(**overrides):
    record = {
        "can_receive_dispatch": False,
        "harness_name": "claude",
        "harness_type": "claude",
        "id": "B",
        "invocation_surfaces": {"headless": {"argv": ["claude", "-p", "{{PROMPT}}"]}},
        "status": "suspended",
    }
    record.update(overrides)
    return record


def test_evaluate_readiness_reports_static_ok_without_claiming_dispatchable_for_suspended(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is False
    assert result["status"] == "suspended"


def test_evaluate_readiness_can_report_dispatchable_when_registry_allows_it(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record(status="active", can_receive_dispatch=True))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is True


def test_evaluate_readiness_errors_for_wrong_harness_type(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record(harness_type="codex"))

    with pytest.raises(module.VerificationError, match="is not claude"):
        module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")


def test_live_readiness_runs_bounded_prompt_probe(tmp_path: Path) -> None:
    module = _load_module()

    def fake_run(command, **kwargs):
        assert command == ["claude.exe", "-p", "Reply READY", "--add-dir", str(tmp_path)]
        assert kwargs["cwd"] == tmp_path
        assert kwargs["stdin"] == subprocess.DEVNULL
        assert kwargs["capture_output"] is True
        assert kwargs["text"] is True
        assert kwargs["timeout"] == 3
        if sys.platform.startswith("win"):
            assert kwargs["creationflags"] & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        return subprocess.CompletedProcess(command, 0, stdout="READY\n", stderr="")

    _write_registry(
        tmp_path,
        _claude_record(
            status="active",
            can_receive_dispatch=True,
            invocation_surfaces={"headless": {"argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}"]}},
        ),
    )

    result = module.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda _name: "claude.exe",
        require_live=True,
        live_prompt="Reply READY",
        timeout=3,
        live_runner=fake_run,
    )

    assert result["static_ok"] is True
    assert result["ready"] is True
    assert result["dispatchable"] is True
    assert result["dispatchable_now"] is True
    assert result["live_probe"]["stdout_bytes"] == len("READY\n")


def test_live_readiness_fails_closed_on_timeout(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _claude_record(status="active", can_receive_dispatch=True))

    def timeout_run(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    result = module.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda _name: "claude.exe",
        require_live=True,
        timeout=1,
        live_runner=timeout_run,
    )

    assert result["static_ok"] is True
    assert result["ready"] is False
    assert result["dispatchable"] is True
    assert result["dispatchable_now"] is False
    assert result["first_failed_check"].startswith("live claude prompt probe")
