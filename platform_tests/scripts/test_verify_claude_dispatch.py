from __future__ import annotations

import importlib.util
import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb import cursor_readiness as verify_cursor_dispatch

from platform_tests.groundtruth_kb.native_fixtures import _serve_authority, history_count, put
from platform_tests.groundtruth_kb.native_fixtures import native as native
from scripts import verify_claude_dispatch, verify_codex_dispatch, verify_ollama_dispatch

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


def test_suspended_installation_can_pass_prerequisites_without_dispatchability(
    tmp_path: Path, native_harness_record
) -> None:
    module = _load_module()
    native_harness_record(tmp_path, _claude_record())

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert result["status"] == "suspended"


def test_legacy_dispatch_flag_cannot_establish_dispatchability(tmp_path: Path, native_harness_record) -> None:
    module = _load_module()
    native_harness_record(tmp_path, _claude_record(status="active", can_receive_dispatch=True))

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())


def test_evaluate_readiness_errors_for_wrong_harness_type(tmp_path: Path, native_harness_record) -> None:
    module = _load_module()
    native_harness_record(tmp_path, _claude_record(harness_type="codex"))

    with pytest.raises(module.VerificationError, match="is not claude"):
        module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")


def test_live_readiness_runs_bounded_prompt_probe(tmp_path: Path, native_harness_record) -> None:
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

    native_harness_record(
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
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert result["probe_passed"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert result["live_probe"]["stdout_bytes"] == len("READY\n")


def test_live_readiness_fails_closed_on_timeout(tmp_path: Path, native_harness_record) -> None:
    module = _load_module()
    native_harness_record(tmp_path, _claude_record(status="active", can_receive_dispatch=True))

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
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert result["probe_passed"] is False
    assert result["first_failed_check"].startswith("live claude prompt probe")


@pytest.mark.parametrize(
    "module", [verify_claude_dispatch, verify_codex_dispatch, verify_cursor_dispatch, verify_ollama_dispatch]
)
@pytest.mark.parametrize("timeout", [0, -1, float("inf"), float("nan")])
def test_invalid_timeout_refuses_before_any_native_or_launch_operation(module, timeout, tmp_path):
    with pytest.raises(module.VerificationError, match="finite and positive"):
        module.evaluate_readiness(project_root=tmp_path, timeout=timeout)


@pytest.mark.parametrize(
    "module", [verify_claude_dispatch, verify_codex_dispatch, verify_cursor_dispatch, verify_ollama_dispatch]
)
@pytest.mark.parametrize("argv", ["fixture-runner", ["fixture-runner", None], ["fixture-runner", ""], {}])
def test_malformed_command_is_not_repaired_into_launchable_arguments(module, argv):
    assert module._headless_argv({"invocation_surfaces": {"headless": {"argv": argv}}}) == []


def test_live_report_does_not_retain_prompt_command_output_or_exception_details(tmp_path, native_harness_record):
    private = "private-fixture-value"
    native_harness_record(tmp_path, _claude_record())

    def fail(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"], output=private, stderr=private)

    report = verify_claude_dispatch.evaluate_readiness(
        project_root=tmp_path,
        require_executable=False,
        require_live=True,
        live_prompt=private,
        live_runner=fail,
    )
    assert report["probe_passed"] is False
    assert report["live_probe"]["error"] == "TimeoutExpired"
    assert private not in json.dumps(report)
    assert "headless_argv" not in report


@pytest.mark.integration
@pytest.mark.timeout(120)
@pytest.mark.parametrize(
    "module,name,identifier",
    [
        (verify_claude_dispatch, "claude", "B"),
        (verify_codex_dispatch, "codex", "A"),
        (verify_cursor_dispatch, "cursor", "E"),
        (verify_ollama_dispatch, "ollama", "D"),
    ],
)
def test_native_reads_are_exact_fresh_and_fail_closed_without_registry_fallback(
    native,
    tmp_path,
    monkeypatch,
    module,
    name,
    identifier,
):
    service, client, *_ = native
    created = put(
        client,
        "harnesses",
        identifier,
        {
            "harness_name": name,
            "harness_type": name,
            "invocation_surfaces": {"headless": {"argv": ["fixture-runner", "{{PROMPT}}"]}},
        },
    )
    assert created.status_code == 200, created.text
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process, env = _serve_authority(tmp_path, port)
    try:
        config = tmp_path / "groundtruth.toml"
        config.write_text(f'[groundtruth]\nauthority_url="http://127.0.0.1:{port}"\n', encoding="utf-8")
        monkeypatch.delenv("GT_AUTHORITY_URL", raising=False)
        legacy = tmp_path / "harness-state/harness-registry.json"
        legacy.parent.mkdir()
        legacy.write_text(json.dumps({"harnesses": [{"id": "missing", "role": "loyal-opposition"}]}))
        monkeypatch.setenv("GTKB_HARNESS_REGISTRY_PATH", str(legacy))
        legacy_before = legacy.read_bytes()
        loader = module._load_harness_record if name in {"claude", "codex"} else module.load_harness_record
        before = history_count(service)
        first = loader(tmp_path, identifier)
        assert first["id"] == identifier and first["harness_name"] == name and first["version"] == 1
        assert history_count(service) == before
        updated = put(
            client, "harnesses", identifier, {"capabilities_ref": "updated-native-declaration"}, expected_version=1
        )
        assert updated.status_code == 200, updated.text
        before = history_count(service)
        second = loader(tmp_path, identifier)
        assert second["version"] == 2 and second["capabilities_ref"] == "updated-native-declaration"
        with pytest.raises(module.VerificationError, match="native_harness_read_failed: not_found"):
            loader(tmp_path, "missing")
        # An explicitly selected root cannot borrow its caller's configuration.
        missing = tmp_path / "no-config"
        missing.mkdir()
        monkeypatch.chdir(tmp_path)
        with pytest.raises(module.VerificationError, match="invalid_selected_configuration"):
            loader(missing, identifier)
        env.pop("GT_AUTHORITY_URL", None)
        cli = subprocess.run(
            [
                sys.executable,
                str(
                    REPO_ROOT / "scripts/verify_cursor_dispatch.py"
                    if module is verify_cursor_dispatch
                    else Path(module.__file__)
                ),
                "--project-root",
                str(tmp_path),
                "--recipient",
                "missing",
                "--json",
            ],
            cwd=missing,
            env=env,
            capture_output=True,
            encoding="utf-8",
            timeout=30,
        )
        assert cli.returncode == 2, cli.stdout + cli.stderr
        assert json.loads(cli.stdout)["error"] == "native_harness_read_failed: not_found"
        assert history_count(service) == before
        process.terminate()
        process.wait(timeout=15)
        with pytest.raises(module.VerificationError, match="native_harness_read_failed"):
            loader(tmp_path, identifier)
        assert legacy.read_bytes() == legacy_before
        assert list(missing.iterdir()) == []
        assert not (tmp_path / "groundtruth.db").exists()
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
