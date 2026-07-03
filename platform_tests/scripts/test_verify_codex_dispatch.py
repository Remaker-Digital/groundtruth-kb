from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "verify_codex_dispatch.py"


def _load_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    spec = importlib.util.spec_from_file_location("verify_codex_dispatch", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_registry(root: Path, record: dict) -> None:
    state = root / "harness-state"
    state.mkdir()
    (state / "harness-registry.json").write_text(json.dumps({"schema_version": 1, "harnesses": [record]}))


def _codex_headless_argv() -> list[str]:
    return [
        "codex",
        "exec",
        "--model",
        "gpt-5.5",
        "-c",
        'approval_policy="never"',
        "-c",
        'model_reasoning_effort="xhigh"',
        "--sandbox",
        "workspace-write",
        "{{PROMPT}}",
        "--cd",
        "{{PROJECT_ROOT}}",
    ]


def _codex_record(**overrides):
    record = {
        "can_receive_dispatch": True,
        "harness_name": "codex",
        "harness_type": "codex",
        "id": "A",
        "invocation_surfaces": {"headless": {"argv": _codex_headless_argv()}},
        "status": "active",
    }
    record.update(overrides)
    return record


def test_evaluate_readiness_reports_dispatchable_when_static_requirements_pass(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is True
    assert result["resolved_executable"] == "codex.exe"
    assert result["model_ok"] is True
    assert result["approval_policy_ok"] is True
    assert result["reasoning_effort_ok"] is True
    assert result["sandbox_ok"] is True
    assert result["sandbox_mode"] == "workspace-write"
    assert result["project_root_selector_ok"] is True


def test_evaluate_readiness_fails_when_executable_required_and_missing(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: None)

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["executable_ok"] is False


def test_evaluate_readiness_fails_without_workspace_write_sandbox(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    sandbox_index = argv.index("--sandbox")
    del argv[sandbox_index : sandbox_index + 2]
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["sandbox_ok"] is False
    assert result["sandbox_mode"] is None


def test_evaluate_readiness_fails_on_full_access_sandbox(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    argv[argv.index("--sandbox") + 1] = "danger-full-access"
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["sandbox_forbidden"] is True
    assert result["sandbox_ok"] is False


@pytest.mark.parametrize(
    ("drop_value", "result_key"),
    [
        ("gpt-5.5", "model_ok"),
        ('approval_policy="never"', "approval_policy_ok"),
        ('model_reasoning_effort="xhigh"', "reasoning_effort_ok"),
    ],
)
def test_evaluate_readiness_fails_when_required_pin_regresses(tmp_path: Path, drop_value: str, result_key: str) -> None:
    module = _load_module()
    argv = [part for part in _codex_headless_argv() if part != drop_value]
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result[result_key] is False


def test_evaluate_readiness_requires_project_root_selector(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    cd_index = argv.index("--cd")
    del argv[cd_index : cd_index + 2]
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["project_root_selector_ok"] is False


def test_evaluate_readiness_errors_for_wrong_harness_type(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record(harness_type="claude"))

    with pytest.raises(module.VerificationError, match="is not codex"):
        module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")
