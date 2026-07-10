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
        "--add-dir",
        ".codex",
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


def _acl_ok(_project_root: Path) -> dict[str, object]:
    return {
        "ok": True,
        "needs_repair": False,
        "risky_deny_count": 0,
        "errors": [],
        "checked_count": 3,
    }


def _write_live_verification(root: Path, payload: dict[str, object]) -> None:
    path = root / ".gtkb-state" / "bridge-poller" / "codex-no-window-verification.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _schema_v2_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": 2,
        "result": "pass",
        "visible_window_detected": False,
        "verified_at": "2999-01-01T00:00:00Z",
        "runs": [
            {
                "command_steps": [
                    {
                        "marker": f"marker-{run}-{step}",
                        "returncode": 0,
                        "stdout_contains_marker": True,
                    }
                    for step in range(3)
                ]
            }
            for run in range(2)
        ],
    }
    payload.update(overrides)
    return payload


def _evaluate(module, project_root: Path, executable_resolver):
    return module.evaluate_readiness(
        project_root=project_root,
        executable_resolver=executable_resolver,
        acl_checker=_acl_ok,
    )


def test_evaluate_readiness_reports_dispatchable_when_static_requirements_pass(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["dispatchable"] is True
    assert result["static_dispatchable"] is True
    assert result["live_headless_ready"] is False
    assert result["live_headless_reason"] == "missing_codex_no_window_verification"
    assert result["resolved_executable"] == "codex.exe"
    assert result["model_ok"] is True
    assert result["approval_policy_ok"] is True
    assert result["reasoning_effort_ok"] is True
    assert result["sandbox_ok"] is True
    assert result["sandbox_mode"] == "workspace-write"
    assert result["project_root_selector_ok"] is True
    assert result["codex_helper_add_dir_ok"] is True
    assert result["codex_helper_add_dir"] == ".codex"
    assert result["codex_dotdir_acl_ok"] is True
    assert result["forbidden_flags_present"] == []


def test_evaluate_readiness_reports_live_headless_failure_separately(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())
    _write_live_verification(
        tmp_path,
        {
            "result": "fail",
            "visible_window_detected": True,
            "stderr_preview": "windows sandbox: setup refresh failed with status exit code: 0xc0000142",
            "verified_at": "2999-01-01T00:00:00Z",
        },
    )

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["static_dispatchable"] is True
    assert result["dispatchable"] is True
    assert result["live_headless_ready"] is False
    assert result["live_headless_reason"] == "codex_no_window_probe_detected_visible_window"
    assert result["live_headless_failure_class"] == "codex_windows_sandbox_setup_failed_0xc0000142"
    assert result["live_headless_verification"]["visible_window_detected"] is True


def test_evaluate_readiness_accepts_schema_v2_multi_command_proof(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())
    _write_live_verification(tmp_path, _schema_v2_payload())

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["live_headless_ready"] is True
    assert result["live_headless_reason"] == "codex_no_window_verification_current"


def test_evaluate_readiness_rejects_legacy_clean_false_green_proof(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())
    _write_live_verification(
        tmp_path,
        {
            "schema_version": 1,
            "result": "pass",
            "visible_window_detected": False,
            "verified_at": "2999-01-01T00:00:00Z",
        },
    )

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["live_headless_ready"] is False
    assert result["live_headless_reason"] == "codex_no_window_verification_legacy_schema"


def test_evaluate_readiness_fails_when_executable_required_and_missing(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    result = _evaluate(module, tmp_path, lambda _name: None)

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["executable_ok"] is False


def test_evaluate_readiness_fails_without_workspace_write_sandbox(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    sandbox_index = argv.index("--sandbox")
    del argv[sandbox_index : sandbox_index + 2]
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["sandbox_ok"] is False
    assert result["sandbox_mode"] is None


def test_evaluate_readiness_fails_on_full_access_sandbox(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    argv[argv.index("--sandbox") + 1] = "danger-full-access"
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["sandbox_forbidden"] is True
    assert result["sandbox_ok"] is False


def test_evaluate_readiness_fails_on_broad_sandbox_bypass_flag(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    argv.append("--dangerously-bypass-approvals-and-sandbox")
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["forbidden_flags_present"] == ["--dangerously-bypass-approvals-and-sandbox"]


@pytest.mark.parametrize(
    "add_dir",
    [
        ".codex",
        "{{PROJECT_ROOT}}/.codex",
        None,
    ],
)
def test_evaluate_readiness_accepts_codex_helper_add_dir_forms(tmp_path: Path, add_dir: str | None) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    index = argv.index("--add-dir")
    if add_dir is None:
        argv[index + 1] = str(tmp_path / ".codex")
    else:
        argv[index + 1] = add_dir
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is True
    assert result["codex_helper_add_dir_ok"] is True


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

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result[result_key] is False


def test_evaluate_readiness_requires_project_root_selector(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    cd_index = argv.index("--cd")
    del argv[cd_index : cd_index + 2]
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["project_root_selector_ok"] is False


def test_evaluate_readiness_requires_codex_helper_add_dir(tmp_path: Path) -> None:
    module = _load_module()
    argv = _codex_headless_argv()
    add_dir_index = argv.index("--add-dir")
    del argv[add_dir_index : add_dir_index + 2]
    _write_registry(tmp_path, _codex_record(invocation_surfaces={"headless": {"argv": argv}}))

    result = _evaluate(module, tmp_path, lambda _name: "codex.exe")

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["codex_helper_add_dir_ok"] is False


def test_evaluate_readiness_fails_when_codex_dotdir_acl_needs_repair(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record())

    def acl_needs_repair(_project_root: Path) -> dict[str, object]:
        return {
            "ok": False,
            "needs_repair": True,
            "risky_deny_count": 12,
            "errors": [{"path": ".codex", "error": "child enumeration failed"}],
            "checked_count": 1,
        }

    result = module.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda _name: "codex.exe",
        acl_checker=acl_needs_repair,
    )

    assert result["static_ok"] is False
    assert result["dispatchable"] is False
    assert result["codex_dotdir_acl_ok"] is False
    assert result["codex_dotdir_acl"]["needs_repair"] is True
    assert result["codex_dotdir_acl"]["risky_deny_count"] == 12
    assert result["codex_dotdir_acl"]["errors_count"] == 1


def test_evaluate_readiness_errors_for_wrong_harness_type(tmp_path: Path) -> None:
    module = _load_module()
    _write_registry(tmp_path, _codex_record(harness_type="claude"))

    with pytest.raises(module.VerificationError, match="is not codex"):
        module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "codex.exe")
