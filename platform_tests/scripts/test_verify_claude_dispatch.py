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
# c123 (owner decision B1): the dispatched permission posture every Claude argv here carries, with owner decision B5's
# setting sources, and host B's corrected registration (batch design WP2 2.4 change 1).
POSTURE = [
    "--permission-mode",
    "bypassPermissions",
    "--setting-sources",
    "project",
    "--strict-mcp-config",
    "--disallowedTools",
    "WebFetch,WebSearch",
]
DISPATCHED_ARGV = ["claude", "--model", "claude-sonnet-5", "--effort", "max", *POSTURE, "-p", "{{PROMPT}}"] + [
    "--add-dir",
    "{{PROJECT_ROOT}}",
    "--output-format",
    "json",
]
INTERPRETER = "groundtruth-kb/.venv/Scripts/pythonw.exe"
ADAPTER = "scripts/claude_hook_adapter.py"
STATIC_CHECKS = ["headless argv", "headless executable", "permission posture", "hook interpreter", "hook adapter"]


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
        "invocation_surfaces": {"headless": {"argv": ["claude", *POSTURE, "-p", "{{PROMPT}}"]}},
        "status": "suspended",
    }
    record.update(overrides)
    return record


def _hook_command(target: str, *, variable: str = "$CLAUDE_PROJECT_DIR", adapter: bool = True) -> str:
    """One hook command in the projector's settings_json form (c123; batch design WP2 2.4)."""
    if adapter:
        return f'"{variable}/{INTERPRETER}" -B "{variable}/{ADAPTER}" --deadline 13 {target} --harness claude'
    return f'"{variable}/{INTERPRETER}" -B "{variable}/{target}" --harness claude'


def _project_hooks(root: Path, *commands: str, interpreter: bool = True, adapter: bool = True) -> Path:
    """A projected .claude/settings.json; the interpreter and the adapter it names exist unless told otherwise."""
    groups = [
        {"matcher": "Write|Edit|Bash", "hooks": [{"type": "command", "command": command, "timeout": 15}]}
        for command in commands or (_hook_command("scripts/implementation_start_gate.py"),)
    ]
    settings = root / ".claude" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps({"autoMemoryEnabled": False, "hooks": {"PreToolUse": groups}}), encoding="utf-8")
    for present, relative in ((interpreter, INTERPRETER), (adapter, ADAPTER)):
        if present:
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_bytes(b"")
    return settings


def test_suspended_installation_can_pass_prerequisites_without_dispatchability(
    tmp_path: Path, native_harness_record
) -> None:
    module = _load_module()
    native_harness_record(tmp_path, _claude_record())
    _project_hooks(tmp_path)

    result = module.evaluate_readiness(project_root=tmp_path, executable_resolver=lambda _name: "claude.exe")

    assert result["static_ok"] is True
    assert result["harness_qualification"] == "unqualified"
    assert not ({"ready", "dispatchable", "dispatchable_now", "can_receive_dispatch", "role"} & result.keys())
    assert result["status"] == "suspended"


def test_legacy_dispatch_flag_cannot_establish_dispatchability(tmp_path: Path, native_harness_record) -> None:
    module = _load_module()
    native_harness_record(tmp_path, _claude_record(status="active", can_receive_dispatch=True))
    _project_hooks(tmp_path)

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
    _project_hooks(tmp_path)

    def fake_run(command, **kwargs):
        assert command == ["claude.exe", *POSTURE, "-p", "Reply READY", "--add-dir", str(tmp_path)]
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
            invocation_surfaces={
                "headless": {"argv": ["claude", *POSTURE, "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}"]}
            },
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
    _project_hooks(tmp_path)

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
    "extra",
    [["--init", "{{INIT_LINE}}"], ["--report={{REPORT}}"], ["--model", "{{MODEL}}"]],
    ids=["unfilled-binding", "unfilled-report", "unknown-placeholder"],
)
def test_live_probe_refuses_a_template_it_cannot_fill_without_starting_a_process(
    tmp_path: Path, native_harness_record, extra
) -> None:
    """c123 (batch design WP2 2.1): the probe fills PROMPT and PROJECT_ROOT only; any other placeholder is refused."""
    module = _load_module()
    native_harness_record(
        tmp_path,
        _claude_record(
            status="active",
            invocation_surfaces={"headless": {"argv": ["claude", *POSTURE, "-p", "{{PROMPT}}", *extra]}},
        ),
    )
    _project_hooks(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("A template the live probe cannot fill must not start a process")

    result = module.evaluate_readiness(
        project_root=tmp_path,
        executable_resolver=lambda _name: "claude.exe",
        require_live=True,
        live_runner=forbidden,
    )

    assert result["static_ok"] is True
    assert result["probe_passed"] is False
    assert result["live_probe"] == {"ok": False, "error": "InvocationError"}
    assert result["first_failed_check"] == "live claude prompt probe: InvocationError"


# c123 (batch design WP2 2.4): readiness reads the dispatched permission posture (owner decisions B1 and B5) from the
# registered argv, and requires the projected hooks it relies on to start and to fail closed.


@pytest.mark.parametrize(
    "argv",
    [
        DISPATCHED_ARGV,
        ["claude", "--permission-mode=bypassPermissions", "--setting-sources=project", "--strict-mcp-config"]
        + ["--disallowed-tools", "WebSearch WebFetch", "-p", "{{PROMPT}}"],
        ["claude", *POSTURE[:-2], "--disallowedTools", "WebFetch", "--disallowedTools", "WebSearch,Task", "-p", "x"],
    ],
    ids=["registered_b_row", "equals_forms_and_alias", "two_deny_lists"],
)
def test_the_dispatched_posture_passes_and_is_reported(tmp_path, native_harness_record, argv):
    native_harness_record(tmp_path, _claude_record(invocation_surfaces={"headless": {"argv": argv}}))
    _project_hooks(tmp_path)

    result = verify_claude_dispatch.evaluate_readiness(
        project_root=tmp_path, executable_resolver=lambda _: "claude.exe"
    )

    assert result["static_ok"] is True and result["first_failed_check"] == ""
    assert result["permission_posture"] == {"ok": True, "problems": []}
    assert [check["name"] for check in result["checks"]] == STATIC_CHECKS
    hooks = result["projected_hooks"]
    assert hooks["interpreter_ok"] is True and hooks["adapter_ok"] is True
    assert hooks["interpreters"] == [str(tmp_path / INTERPRETER)]
    assert result["harness_qualification"] == "unqualified"


C121_B_ARGV = ["claude", "--model", "claude-sonnet-5", "--effort", "max", "-p", "{{PROMPT}}"] + [
    "--add-dir",
    "{{PROJECT_ROOT}}",
    "--output-format",
    "json",
]


@pytest.mark.parametrize(
    ("argv", "problems"),
    [
        (
            C121_B_ARGV,
            [
                "no --permission-mode bypassPermissions",
                "no --strict-mcp-config",
                "WebFetch and WebSearch are not disallowed (--disallowedTools WebFetch,WebSearch)",
                "no --setting-sources project",
            ],
        ),
        (["claude", "--permission-mode", "plan", *POSTURE[2:], "-p", "{{PROMPT}}"], ["--permission-mode is 'plan'"]),
        (["claude", *POSTURE, "--permission-mode", "bypassPermissions", "-p", "x"], ["--permission-mode is given 2"]),
        (
            ["claude", *POSTURE, "--dangerously-skip-permissions", "-p", "x"],
            ["--dangerously-skip-permissions is given"],
        ),
        (["claude", *POSTURE[:-1], "WebFetch", "-p", "x"], ["WebSearch is not disallowed"]),
        (
            ["claude", *POSTURE[:-1], "WebFetch(domain:example.com),WebSearch", "-p", "x"],
            ["WebFetch is not disallowed"],
        ),
        (["claude", *POSTURE, "{{PROMPT}}"], ["the --disallowedTools list takes {{PROMPT}}"]),
        (["claude", *POSTURE[:2], "--setting-sources", "user,project", *POSTURE[4:], "-p", "x"], ["is 'user,project'"]),
        (["claude", *POSTURE, "--bare", "-p", "x"], ["--bare skips the GT-KB hooks"]),
        (["claude", *POSTURE, "--safe-mode", "-p", "x"], ["--safe-mode skips the GT-KB hooks"]),
    ],
    ids=[
        "c121_b_row",
        "other_mode",
        "mode_twice",
        "second_spelling",
        "web_search_allowed",
        "scoped_rule_keeps_the_tool",
        "list_takes_the_prompt",
        "user_settings_loaded",
        "bare",
        "safe_mode",
    ],
)
def test_a_missing_or_wrong_posture_fails_static_readiness_before_any_launch(
    tmp_path, native_harness_record, argv, problems
):
    native_harness_record(tmp_path, _claude_record(invocation_surfaces={"headless": {"argv": argv}}))
    _project_hooks(tmp_path)

    def forbidden(*args, **kwargs):
        pytest.fail("A registration without the dispatched posture must not start a session")

    result = verify_claude_dispatch.evaluate_readiness(
        project_root=tmp_path, executable_resolver=lambda _: "claude.exe", require_live=True, live_runner=forbidden
    )

    assert result["static_ok"] is False and result["probe_passed"] is False
    assert result["live_probe"] is None
    assert result["permission_posture"]["ok"] is False
    reported = result["permission_posture"]["problems"]
    for problem in problems:
        assert any(problem in line for line in reported), (problem, reported)
    assert result["first_failed_check"] == "permission posture: " + "; ".join(reported)


def test_the_hook_interpreter_must_exist_under_the_root(tmp_path, native_harness_record):
    """A hook that cannot start is a non-blocking error in Claude Code: under bypassPermissions the tool runs."""
    native_harness_record(tmp_path, _claude_record(status="active"))
    _project_hooks(tmp_path, interpreter=False)

    def forbidden(*args, **kwargs):
        pytest.fail("A root whose hook interpreter is missing must not start a session")

    result = verify_claude_dispatch.evaluate_readiness(
        project_root=tmp_path, executable_resolver=lambda _: "claude.exe", require_live=True, live_runner=forbidden
    )

    assert result["static_ok"] is False and result["live_probe"] is None
    assert result["permission_posture"]["ok"] is True
    assert result["projected_hooks"]["missing_interpreters"] == [str(tmp_path / INTERPRETER)]
    assert result["first_failed_check"] == f"hook interpreter: missing {tmp_path / INTERPRETER}"


def test_an_application_root_resolves_the_host_interpreter_its_hooks_name(tmp_path, native_harness_record):
    """Under an application the projector renders the host's interpreter and adapter two levels up."""
    application = tmp_path / "applications" / "Alpha"
    application.mkdir(parents=True)
    native_harness_record(application, _claude_record())
    command = _hook_command("scripts/implementation_start_gate.py", variable="${CLAUDE_PROJECT_DIR}/../..")
    _project_hooks(application, command, interpreter=False, adapter=False)
    for relative in (INTERPRETER, ADAPTER):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_bytes(b"")

    result = verify_claude_dispatch.evaluate_readiness(
        project_root=application, executable_resolver=lambda _: "claude.exe"
    )

    hooks = result["projected_hooks"]
    assert result["static_ok"] is True, result["first_failed_check"]
    assert Path(hooks["interpreters"][0]).resolve() == (tmp_path / INTERPRETER).resolve()
    assert Path(hooks["adapters"][0]).resolve() == (tmp_path / ADAPTER).resolve()
    assert not (application / INTERPRETER).exists() and not (application / ADAPTER).exists()


@pytest.mark.parametrize(
    ("prepare", "failed"),
    [
        (lambda root: None, "hook interpreter: the root has no readable projected .claude/settings.json"),
        (
            lambda root: (root / ".claude").mkdir() or (root / ".claude/settings.json").write_text("{}"),
            "hook interpreter: the projected .claude/settings.json registers no hook command",
        ),
        (
            lambda root: _project_hooks(root, "pythonw -B scripts/implementation_start_gate.py --harness claude"),
            "hook interpreter: 1 of 1 hook commands do not start with a quoted interpreter path",
        ),
        (
            lambda root: _project_hooks(
                root, _hook_command(".harness-baseline-configuration/hooks/x.py", adapter=False)
            ),
            f"hook adapter: 1 of 1 hook commands do not run {ADAPTER}",
        ),
    ],
    ids=["no_projection", "no_hooks", "bare_interpreter", "pre_adapter_projection"],
)
def test_projected_hooks_that_cannot_start_or_would_fail_open_fail_readiness(
    tmp_path, native_harness_record, prepare, failed
):
    native_harness_record(tmp_path, _claude_record())
    prepare(tmp_path)

    result = verify_claude_dispatch.evaluate_readiness(
        project_root=tmp_path, executable_resolver=lambda _: "claude.exe"
    )

    assert result["static_ok"] is False
    assert result["first_failed_check"] == failed


def test_a_missing_adapter_fails_readiness(tmp_path, native_harness_record):
    native_harness_record(tmp_path, _claude_record())
    _project_hooks(tmp_path, adapter=False)

    result = verify_claude_dispatch.evaluate_readiness(
        project_root=tmp_path, executable_resolver=lambda _: "claude.exe"
    )

    assert result["projected_hooks"]["interpreter_ok"] is True
    assert result["projected_hooks"]["adapter_ok"] is False
    assert result["first_failed_check"] == f"hook adapter: missing {tmp_path / ADAPTER}"


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
    _project_hooks(tmp_path)

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
