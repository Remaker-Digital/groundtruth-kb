"""Bounded Ollama diagnostics and direct runtime component tests.

Provider responses and hook verdicts here are controlled. The separate native
provider/CLI suite proves binding, claims, publication and project finalization
against disposable PostgreSQL; these component tests do not qualify a live host.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from platform_tests.scripts.test_provider_native_cli_delivery import create_provider_guard_fixtures
from scripts import ollama_harness, verify_ollama_dispatch

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"


@pytest.fixture(scope="module")
def verify_module():
    return verify_ollama_dispatch


@pytest.fixture(scope="module")
def ollama_harness_module():
    return ollama_harness


def _fixture_route(ollama_harness_module, *, key: str, allowed_tools: tuple[str, ...]):
    model_id = f"{key}:current"
    return ollama_harness_module.ModelRoute(
        key=key,
        model_id=model_id,
        model_version=ollama_harness_module.infer_model_version(model_id),
        tool_calling_supported=True,
        allowed_tools=allowed_tools,
    )


def test_autostart_probe_detects_windows_task(verify_module) -> None:
    captured: dict[str, object] = {}

    def _runner(args, **kwargs):  # noqa: ANN001, ANN202
        captured["args"] = args
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"scheduled_tasks":["GTKB-Ollama-Serve"],"services":[]}',
            stderr="",
        )

    result = verify_module.evaluate_ollama_autostart(
        platform="win32",
        executable_resolver=lambda _name: "powershell.exe",
        command_runner=_runner,
    )

    assert result["checked"] is True
    assert result["configured"] is True
    assert result["scheduled_tasks"] == ["GTKB-Ollama-Serve"]
    assert "warning" not in result
    assert captured["args"][:4] == ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive"]
    kwargs = captured["kwargs"]
    assert kwargs["stdin"] is subprocess.DEVNULL
    assert kwargs["creationflags"] & getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    startupinfo = kwargs.get("startupinfo")
    if sys.platform == "win32":
        assert startupinfo is not None
        assert startupinfo.dwFlags & getattr(subprocess, "STARTF_USESHOWWINDOW", 0x00000001)
        assert startupinfo.wShowWindow == getattr(subprocess, "SW_HIDE", 0)


def test_autostart_probe_warns_when_no_task_or_service(verify_module) -> None:
    def _runner(args, **kwargs):  # noqa: ANN001, ANN202
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout='{"scheduled_tasks":[],"services":[]}',
            stderr="",
        )

    result = verify_module.evaluate_ollama_autostart(
        platform="win32",
        executable_resolver=lambda _name: "powershell.exe",
        command_runner=_runner,
    )

    assert result["checked"] is True
    assert result["configured"] is False
    assert "No Windows scheduled task or service" in result["warning"]


def test_autostart_installer_script_is_guarded() -> None:
    script = (_SCRIPTS_DIR / "ops" / "install_ollama_autostart_task.ps1").read_text(encoding="utf-8")

    assert "SupportsShouldProcess" in script
    assert "Register-ScheduledTask" in script
    assert "ollama.exe" in script
    assert '-Argument "serve"' in script


def test_ollama_guard_payload_uses_its_native_identity(ollama_harness_module, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-run")
    monkeypatch.setenv("CODEX_THREAD_ID", "parent-codex-thread")
    guard_path = tmp_path / "guard.py"
    guard_path.write_text("# fixture guard\n", encoding="utf-8")
    captured: list[dict[str, object]] = []

    def guard_runner(path, payload, env, timeout):  # noqa: ANN001, ARG001
        captured.append(dict(payload))
        assert env["GTKB_AUTHOR_MODEL"] == metadata.model_id
        assert env["GTKB_AUTHOR_MODEL_VERSION"] == metadata.model_version
        assert env["GTKB_NATIVE_CONTEXT_ID"] == metadata.native_context_id
        return ollama_harness_module.GuardExecutionResult(0, "{}")

    metadata = ollama_harness_module.ModelMetadata(
        model_id="qwen3-coder-next:cloud",
        model_version="cloud",
        endpoint="http://localhost:11434",
        route_key="qwen3-coder-next-cloud",
    )
    ollama_harness_module.invoke_guard_adapter(
        "Write",
        {"path": str(tmp_path / "bridge" / "gtkb-fixture-001.md"), "content": "NEW\n"},
        metadata,
        tmp_path,
        guard_runner=guard_runner,
        guard_paths=(guard_path,),
    )

    assert captured[0]["session_id"] == metadata.native_context_id


def test_dispatch_read_missing_file_returns_model_visible_error(ollama_harness_module, tmp_path) -> None:
    metadata = ollama_harness_module.ModelMetadata(
        model_id="qwen3-coder-next:cloud",
        model_version="cloud",
        endpoint="http://localhost:11434",
        route_key="qwen3-coder-next-cloud",
    )

    result = ollama_harness_module.dispatch_tool_call(
        "Read",
        {"path": "missing-fixture.txt"},
        metadata,
        tmp_path,
    )

    assert result == "Read failed: file not found: missing-fixture.txt"


def test_dispatch_bash_nonzero_returns_model_visible_evidence(ollama_harness_module, tmp_path) -> None:
    for guard_path in ollama_harness_module.BASH_GUARDS:
        path = tmp_path / guard_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture guard\n", encoding="utf-8")

    metadata = ollama_harness_module.ModelMetadata(
        model_id="qwen3-coder-next:cloud",
        model_version="cloud",
        endpoint="http://localhost:11434",
        route_key="qwen3-coder-next-cloud",
    )

    def guard_runner(path, payload, env, timeout):  # noqa: ANN001, ARG001
        return ollama_harness_module.GuardExecutionResult(0, "{}")

    def command_runner(command, project_root, env, timeout):  # noqa: ANN001, ARG001
        return subprocess.CompletedProcess(args=command, returncode=5, stdout="out", stderr="err")

    result = ollama_harness_module.dispatch_tool_call(
        "Bash",
        {"command": "python -m groundtruth_kb --help"},
        metadata,
        tmp_path,
        guard_runner=guard_runner,
        command_runner=command_runner,
    )

    assert "Bash command exited with return code 5." in result
    assert "Command: python -m groundtruth_kb --help" in result
    assert "STDOUT:\nout" in result
    assert "STDERR:\nerr" in result


def test_default_subprocess_runners_pin_utf8_decode_options(ollama_harness_module, tmp_path, monkeypatch) -> None:
    captured: list[dict[str, object]] = []

    def fake_run(args, **kwargs):  # noqa: ANN001, ANN202
        captured.append(dict(kwargs))
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="out", stderr="err")

    monkeypatch.setattr(subprocess, "run", fake_run)

    guard_path = tmp_path / "guard.py"
    guard_path.write_text("# fixture guard\n", encoding="utf-8")

    guard_result = ollama_harness_module._default_guard_runner(
        guard_path,
        {"cwd": str(tmp_path)},
        os.environ,
        5.0,
    )
    command_result = ollama_harness_module._default_command_runner(
        "fixture command",
        tmp_path,
        os.environ,
        5.0,
    )

    assert guard_result.stdout == "out"
    assert command_result.stdout == "out"
    assert len(captured) == 2
    assert all(call["text"] is True for call in captured)
    assert all(call["encoding"] == "utf-8" for call in captured)
    assert all(call["errors"] == "replace" for call in captured)


def test_default_guard_runner_captures_utf8_bytes_invalid_under_cp1252(ollama_harness_module, tmp_path) -> None:
    guard_path = tmp_path / "guard.py"
    guard_path.write_text(
        "import sys\n"
        "sys.stdout.buffer.write(b'stdout:\\xe2\\x81\\xa0')\n"
        "sys.stderr.buffer.write(b'stderr:\\xe2\\x81\\xa0')\n",
        encoding="utf-8",
    )

    result = ollama_harness_module._default_guard_runner(
        guard_path,
        {"cwd": str(tmp_path)},
        os.environ,
        5.0,
    )

    assert result.returncode == 0
    assert result.stdout == "stdout:\u2060"
    assert result.stderr == "stderr:\u2060"


def test_dispatch_readiness_requires_full_lo_tool_set(verify_module) -> None:
    assert verify_module.OLLAMA_DISPATCH_REQUIRED_TOOLS == ("Read", "Write", "Edit", "Grep", "Glob", "Bash")


def test_default_ollama_bridge_review_route_uses_deepseek_v4_flash_cloud(ollama_harness_module, tmp_path) -> None:
    (tmp_path / ollama_harness_module.ROUTING_CONFIG_PATH.parent).mkdir(parents=True)
    (tmp_path / ollama_harness_module.ROUTING_CONFIG_PATH).write_text(
        "schema_version = 1\n"
        "[models.deepseek-v4-flash-cloud]\n"
        'model_id = "deepseek-v4-flash:cloud"\n'
        'provider = "ollama"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "[models.kimi-k2-7-code-cloud]\n"
        'model_id = "kimi-k2.7-code:cloud"\n'
        'provider = "ollama"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "[models.deepseek-v4-pro-cloud]\n"
        'model_id = "deepseek-v4-pro:cloud"\n'
        'provider = "ollama"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "[models.deepseek-v4-pro]\n"
        'model_id = "deepseek/deepseek-v4-pro"\n'
        'provider = "openrouter"\n'
        "tool_calling_supported = true\n"
        'allowed_tools = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]\n'
        "[routing.ollama]\n"
        'default_model = "deepseek-v4-flash-cloud"\n'
        "timeout_seconds = 3600\n"
        "[routing.ollama.skills]\n"
        'bridge-review = "deepseek-v4-flash-cloud"\n'
        'verification = "deepseek-v4-flash-cloud"\n'
        'implementation = "deepseek-v4-flash-cloud"\n',
        encoding="utf-8",
    )

    config = ollama_harness_module.load_routing_config(tmp_path)
    route = ollama_harness_module.resolve_model(config, None, skill="bridge-review")

    assert route.key == "deepseek-v4-flash-cloud"
    assert route.model_id == "deepseek-v4-flash:cloud"
    assert config.timeout_seconds == 3600
    assert ollama_harness_module.derive_session_timeout_from_route_timeout(config.timeout_seconds) == 3660


@pytest.mark.parametrize("exists", [True, False])
def test_read_tool_loop_returns_actual_fixture_result_and_schemas(tmp_path, exists):
    create_provider_guard_fixtures(ollama_harness, tmp_path)
    path = tmp_path / "source.txt"
    if exists:
        path.write_text("Exact readback.", encoding="utf-8")
    calls = []

    def chat(endpoint, payload, timeout):
        calls.append(payload)
        if len(calls) == 1:
            return {
                "message": {
                    "role": "assistant",
                    "tool_calls": [{"id": "read-one", "function": {"name": "Read", "arguments": {"path": str(path)}}}],
                }
            }
        result = next(m["content"] for m in reversed(payload["messages"]) if m.get("role") == "tool")
        return {"message": {"role": "assistant", "content": result}}

    route = _fixture_route(ollama_harness, key="fixture-read", allowed_tools=("Read",))
    result = ollama_harness.run_tool_loop(
        "Read the selected fixture.", route, "https://fixture.invalid", 3, tmp_path, chat_func=chat
    )
    assert len(calls) == 2 and calls[0]["tools"]
    if exists:
        assert result == "Exact readback."
    else:
        assert "file not found" in result.lower()


@pytest.mark.parametrize(
    "tool,arguments",
    [
        ("Write", {"path": "artifact.json", "content": "new"}),
        ("Edit", {"path": "artifact.json", "old_string": "old", "new_string": "new"}),
        ("Bash", {"command": "fixture-controlled-command"}),
    ],
)
@pytest.mark.parametrize("guard_exit,reason", [(0, "fixture guard denial"), (2, "guard exited nonzero")])
def test_guard_block_preserves_fixture_and_prevents_command(tool, arguments, guard_exit, reason, tmp_path):
    create_provider_guard_fixtures(ollama_harness, tmp_path)
    target = tmp_path / "artifact.json"
    target.write_text("old", encoding="utf-8")
    metadata = ollama_harness.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture-route")
    guards = []

    def block(path, payload, env, timeout):
        guards.append(payload)
        return ollama_harness.GuardExecutionResult(guard_exit, '{"decision":"block","reason":"fixture guard denial"}')

    def forbidden(*args, **kwargs):
        pytest.fail("A blocked request must not execute a command")

    with pytest.raises(ollama_harness.OllamaHarnessError, match=reason):
        ollama_harness.dispatch_tool_call(
            tool, arguments, metadata, tmp_path, guard_runner=block, command_runner=forbidden
        )
    assert guards and guards[0]["session_id"] == metadata.native_context_id
    assert target.read_text(encoding="utf-8") == "old"


def test_bash_bridge_write_is_denied_before_guards_or_command(tmp_path):
    metadata = ollama_harness.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture-route")

    def forbidden(*args, **kwargs):
        pytest.fail("A bridge-file mutation must not invoke guards or commands")

    with pytest.raises(ollama_harness.OllamaHarnessError, match="Bash bridge artifact mutation denied"):
        ollama_harness.dispatch_tool_call(
            "Bash",
            {"command": "Set-Content bridge/fixture-001.md 'GO'"},
            metadata,
            tmp_path,
            guard_runner=forbidden,
            command_runner=forbidden,
        )
    assert list(tmp_path.iterdir()) == []


def test_out_of_root_read_is_rejected_before_reading(tmp_path):
    metadata = ollama_harness.ModelMetadata("fixture-model", "v1", "https://fixture.invalid", "fixture-route")
    with pytest.raises(ollama_harness.OllamaHarnessError, match="escapes project root"):
        ollama_harness.dispatch_tool_call("Read", {"path": "../unrelated-file.txt"}, metadata, tmp_path)


@pytest.mark.parametrize("stdout,returncode", [("not JSON", 0), ("[]", 0), ('{"scheduled_tasks":[]}', 1)])
def test_invalid_autostart_response_warns_without_echoing_raw_output(stdout, returncode):
    report = verify_ollama_dispatch.evaluate_ollama_autostart(
        platform="win32",
        executable_resolver=lambda name: "powershell.exe",
        command_runner=lambda command, **kwargs: subprocess.CompletedProcess(
            command, returncode, stdout=stdout, stderr="private-response"
        ),
    )
    assert report["configured"] is False and report["warning"]
    assert "private-response" not in json.dumps(report)


def test_diagnostic_cli_help_exposes_no_mock_or_role_promotion_mode():
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS_DIR / "verify_ollama_dispatch.py"), "--help"],
        capture_output=True,
        encoding="utf-8",
        timeout=20,
    )
    assert result.returncode == 0
    assert "--skip-daemon" in result.stdout
    assert "--readiness-only" not in result.stdout
    assert "Live Mode" not in result.stdout and "Guard-Only Mode" not in result.stdout
