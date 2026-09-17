from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import verify_codex_dispatch as verify


def _record(argv=None, **overrides):
    return {
        "id": "A",
        "harness_name": "codex",
        "harness_type": "codex",
        "status": "registered",
        "invocation_surfaces": {
            "headless": {
                "argv": argv
                if argv is not None
                else ["codex", "exec", "--model", "fixture-model", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]
            }
        },
        **overrides,
    }


def _acl_ok(root):
    return {"ok": True, "needs_repair": False, "risky_deny_count": 0, "errors": [], "checked_count": 1}


def _evaluate(root, **kwargs):
    return verify.evaluate_readiness(
        project_root=root, executable_resolver=lambda name: "fixture-codex", acl_checker=_acl_ok, **kwargs
    )


def test_native_launch_checks_do_not_establish_dispatch_or_runtime_qualification(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record(can_receive_dispatch=True, role="prime-builder"))
    result = _evaluate(tmp_path)
    assert result["probe_passed"] is True
    assert result["authority_source"] == "native_harness_record"
    assert result["status"] == "registered"
    for field in ("harness_qualification", "model_profile_conformance", "permissions_behavior", "window_behavior"):
        assert result[field] == "unqualified"
    assert (
        not {"dispatchable", "static_dispatchable", "can_receive_dispatch", "role", "headless_argv", "required_model"}
        & result.keys()
    )


@pytest.mark.parametrize("model,profile", [("fixture-model-one", ":workspace"), ("fixture-model-two", ":read-only")])
def test_native_model_and_profile_arguments_are_preserved_without_claiming_conformance(
    tmp_path, native_harness_record, model, profile
):
    argv = ["codex", "exec", "--model", model, "-c", f'default_permissions="{profile}"', "{{PROMPT}}"]
    native_harness_record(tmp_path, _record(argv))
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="READY", stderr="")

    report = _evaluate(tmp_path, require_live=True, live_prompt="fixture prompt", live_runner=runner, timeout=5)
    assert calls[0][0] == ["fixture-codex", *argv[1:-1], "fixture prompt"]
    assert calls[0][1]["cwd"] == tmp_path
    assert calls[0][1]["stdin"] is subprocess.DEVNULL
    assert calls[0][1]["timeout"] == 5
    assert report["probe_passed"] is True
    assert report["model_profile_conformance"] == "unqualified"
    assert report["permissions_behavior"] == "unqualified"
    assert report["window_behavior"] == "unqualified"


@pytest.mark.parametrize("root_args", [["--cd", "{{PROJECT_ROOT}}"], [], ["--cd", "selected-absolute"]])
def test_selected_project_root_and_default_cwd_are_accepted(tmp_path, native_harness_record, root_args):
    args = [str(tmp_path) if p == "selected-absolute" else p for p in root_args]
    native_harness_record(tmp_path, _record(["codex", "exec", "{{PROMPT}}", *args]))
    assert _evaluate(tmp_path)["probe_passed"] is True


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["codex", None],
        ["codex", ""],
        "codex exec",
        ["codex", "exec", "--cd"],
        ["codex", "exec", "--cd", "foreign-root"],
        ["codex", "exec", "--cd", "{{PROJECT_ROOT}}", "--cd", "foreign-root"],
        ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox"],
    ],
)
def test_invalid_launch_prerequisites_prevent_acl_and_prompt_operations(tmp_path, native_harness_record, argv):
    native_harness_record(tmp_path, _record(argv))

    def forbidden(*args, **kwargs):
        pytest.fail("Invalid prerequisites must prevent ACL and prompt operations")

    result = verify.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda name: "fixture-codex",
        acl_checker=forbidden,
        require_live=True,
        live_runner=forbidden,
    )
    assert result["probe_passed"] is False
    assert result["acl_probe"] is None and result["live_probe"] is None


def test_missing_executable_prevents_acl_and_prompt_operations(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())
    calls = []
    result = verify.evaluate_readiness(
        project_root=tmp_path, executable_resolver=lambda name: None, acl_checker=lambda root: calls.append(root)
    )
    assert result["probe_passed"] is False
    assert result["first_failed_check"] == "executable"
    assert not calls


def test_wrong_harness_type_fails_before_acl_or_launch(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record(harness_type="claude"))
    with pytest.raises(verify.VerificationError, match="not codex"):
        _evaluate(tmp_path)


@pytest.mark.parametrize(
    "cache",
    [
        {
            "result": "pass",
            "schema_version": 3,
            "verified_at": "2999-01-01T00:00:00Z",
            "visible_window_detected": False,
        },
        {"result": "fail", "visible_window_detected": True},
    ],
)
def test_old_qualification_cache_cannot_supply_or_deny_runtime_facts(
    tmp_path, native_harness_record, monkeypatch, cache
):
    native_harness_record(tmp_path, _record())
    path = tmp_path / ".gtkb-state/bridge-poller/codex-no-window-verification.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(cache), encoding="utf-8")
    before = path.read_bytes()
    original = Path.read_text

    def guarded_read(selected, *args, **kwargs):
        assert selected != path, "The retired cache must not be read"
        return original(selected, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded_read)
    result = _evaluate(tmp_path)
    assert result["probe_passed"] is True
    assert result["window_behavior"] == "unqualified"
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "payload",
    [
        None,
        {},
        {"ok": "true"},
        {"ok": True, "needs_repair": "false", "checked_count": 1},
        {"ok": True, "needs_repair": False, "checked_count": "1", "errors": []},
        {"ok": True, "needs_repair": False, "checked_count": 1, "errors": [], "returncode": 1},
    ],
)
def test_malformed_or_failed_acl_reports_never_pass(payload):
    assert verify._normalize_acl_check(payload)["ok"] is False


def test_acl_failure_prevents_prompt_launch_and_does_not_echo_error(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _record())

    def acl_failure(root):
        return {
            "ok": False,
            "needs_repair": True,
            "risky_deny_count": 1,
            "checked_count": 1,
            "errors": [],
            "error": "private diagnostic detail",
        }

    def forbidden(*args, **kwargs):
        pytest.fail("ACL failure must prevent prompt launch")

    report = verify.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda name: "fixture-codex",
        acl_checker=acl_failure,
        require_live=True,
        live_runner=forbidden,
    )
    assert report["probe_passed"] is False
    assert report["acl_probe"]["needs_repair"] is True
    assert "private diagnostic" not in json.dumps(report)


@pytest.mark.parametrize("returncode,stdout", [(1, "READY"), (0, "")])
def test_failed_or_empty_live_process_does_not_pass(tmp_path, native_harness_record, returncode, stdout):
    native_harness_record(tmp_path, _record())
    report = _evaluate(
        tmp_path,
        require_live=True,
        live_runner=lambda command, **kwargs: subprocess.CompletedProcess(
            command, returncode, stdout=stdout, stderr="private output"
        ),
    )
    assert report["probe_passed"] is False
    assert "private output" not in json.dumps(report)


def test_prompt_timeout_remains_private_and_unqualified(tmp_path, native_harness_record, monkeypatch):
    native_harness_record(tmp_path, _record())
    monkeypatch.setattr(verify, "no_window_subprocess_kwargs", lambda: {"creationflags": 0x08000000})

    def timeout(command, **kwargs):
        assert kwargs["creationflags"] == 0x08000000
        raise subprocess.TimeoutExpired(command, kwargs["timeout"], output="private response", stderr="private error")

    report = _evaluate(tmp_path, require_live=True, live_prompt="private prompt", live_runner=timeout)
    assert report["probe_passed"] is False
    assert report["live_probe"]["error"] == "TimeoutExpired"
    assert "private" not in json.dumps(report)
    assert report["window_behavior"] == "unqualified"


def test_repair_flag_is_not_an_operation_of_the_diagnostic_cli():
    with pytest.raises(SystemExit) as error:
        verify.main(["--repair-acl"])
    assert error.value.code == 2
