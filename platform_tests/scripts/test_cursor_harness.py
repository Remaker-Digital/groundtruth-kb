# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/cursor_harness.py, the headless Cursor Agent shim in groundtruth_kb.cursor_harness.

c123 (batch design WP2 2.1): the shim selects no role. It has no --skill option, no skill route aliases and no Loyal
Opposition skill set. The dispatched prompt, whose first line is the init line, reaches Cursor Agent as it came, and
every run that Cursor Agent ends with exit 0 and an empty stdout fails closed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from groundtruth_kb import cursor_harness


def _load_harness():
    return cursor_harness


def test_cursor_adaptation_metadata_is_compact_and_names_no_skill_route() -> None:
    harness = _load_harness()
    payload = harness.cursor_adaptation_metadata()

    assert payload["harness_id"] == "E"
    assert payload["adaptation_label"] == "cursor-native-cli"
    # c123 (batch design WP2 2.1): no skill routes, so no alias table and no alias fingerprint; v2 marks the change.
    assert payload["adaptation_version"] == "cursor-native-cli-v2"
    assert "skill_route_aliases" not in payload
    assert set(payload["input_fingerprints"]) == {
        "scripts/cursor_harness.py",
        "groundtruth_kb/cursor_harness.py",
        "groundtruth_kb/local_env.py",
    }
    assert "governed_lo_publication" not in payload
    assert payload["raw_prompt_included"] is False
    assert all(value.startswith("sha256:") for value in payload["input_fingerprints"].values())
    assert "Follow the GT-KB skill contract" not in repr(payload)


def test_resolve_agent_command_uses_standalone_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda name: "C:/Tools/agent.exe" if name == "agent" else None)

    assert harness._resolve_agent_command() == ["C:/Tools/agent.exe"]


def test_resolve_agent_command_uses_cursor_agent_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(
        harness.shutil,
        "which",
        lambda name: "C:/Tools/cursor-agent.exe" if name == "cursor-agent" else None,
    )

    assert harness._resolve_agent_command() == ["C:/Tools/cursor-agent.exe"]


def test_resolve_agent_command_keeps_standalone_path_before_direct_cursor_agent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    harness = _load_harness()
    version = tmp_path / "cursor-agent" / "versions" / "2026.06.26-7079533"
    version.mkdir(parents=True)
    (version / "node.exe").write_text("", encoding="utf-8")
    (version / "index.js").write_text("", encoding="utf-8")
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(harness.os, "name", "nt", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda name: "C:/Tools/agent.exe" if name == "agent" else None)

    assert harness._resolve_agent_command() == ["C:/Tools/agent.exe"]


def test_resolve_agent_command_prefers_direct_cursor_agent_before_windows_wrappers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    harness = _load_harness()
    root = tmp_path / "cursor-agent"
    version = root / "versions" / "2026.06.26-7079533"
    version.mkdir(parents=True)
    node = version / "node.exe"
    index = version / "index.js"
    node.write_text("", encoding="utf-8")
    index.write_text("", encoding="utf-8")
    (root / "agent.CMD").write_text("@echo off\n", encoding="utf-8")
    (root / "agent.ps1").write_text("Write-Output agent\n", encoding="utf-8")
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(harness.os, "name", "nt", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda _name: None)

    assert harness._resolve_agent_command() == [str(node), str(index)]


def test_resolve_agent_command_prefers_direct_cursor_agent_before_path_wrapper(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    harness = _load_harness()
    root = tmp_path / "cursor-agent"
    version = root / "versions" / "2026.06.26-7079533"
    version.mkdir(parents=True)
    node = version / "node.exe"
    index = version / "index.js"
    node.write_text("", encoding="utf-8")
    index.write_text("", encoding="utf-8")
    path_wrapper = root / "agent.CMD"
    path_wrapper.write_text("@echo off\n", encoding="utf-8")
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(harness.os, "name", "nt", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda name: str(path_wrapper) if name == "agent" else None)

    assert harness._resolve_agent_command() == [str(node), str(index)]


def test_resolve_agent_command_falls_back_to_windows_wrapper_without_direct_cursor_agent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    harness = _load_harness()
    root = tmp_path / "cursor-agent"
    (root / "versions" / "2026.06.26-7079533").mkdir(parents=True)
    wrapper = root / "agent.cmd"
    wrapper.write_text("@echo off\n", encoding="utf-8")
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(harness.os, "name", "nt", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda _name: None)

    assert harness._resolve_agent_command() == [str(wrapper)]


def test_resolve_agent_command_rejects_cursor_gui_override_without_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.setenv("CURSOR_AGENT_BIN", "C:/Users/mike/AppData/Local/Programs/Cursor/cursor.exe")
    calls: list[str] = []

    def fake_probe(path: str) -> bool:
        calls.append(path)
        return True

    monkeypatch.setattr(harness, "_cursor_supports_agent_subcommand", fake_probe)

    with pytest.raises(harness.CursorHarnessError, match="Cursor GUI launcher"):
        harness._resolve_agent_command()
    assert calls == []


def test_cursor_agent_subcommand_support_refuses_gui_launcher_without_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="Subcommands\n  agent        Start the Cursor agent in your terminal.\n",
            stderr="",
        )

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness._cursor_supports_agent_subcommand("C:/Tools/cursor.cmd") is False
    assert calls == []


def test_cursor_agent_subcommand_support_requires_headless_help(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="Subcommands\n  agent        Start the Cursor agent in your terminal.\n",
            stderr="",
        )

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness._cursor_supports_agent_subcommand("C:/Tools/agent.exe") is False
    assert calls[0][0] == ["C:/Tools/agent.exe", "agent", "--help"]
    assert calls[0][1]["creationflags"] if harness.os.name == "nt" else "creationflags" not in calls[0][1]


def test_cursor_agent_subcommand_support_accepts_headless_help(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()

    def fake_run(command, **kwargs):
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="Usage: agent [options]\n  -p, --print\n  --output-format <format>\n",
            stderr="",
        )

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness._cursor_supports_agent_subcommand("C:/Tools/agent.exe") is True


def test_resolve_agent_command_rejects_cursor_override_without_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.setenv("CURSOR_AGENT_BIN", "C:/Users/mike/AppData/Local/Programs/Cursor/cursor.exe")

    with pytest.raises(harness.CursorHarnessError, match="Cursor GUI launcher"):
        harness._resolve_agent_command()


def test_resolve_agent_command_does_not_probe_cursor_gui_launcher_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness, "_windows_cursor_agent_direct_commands", lambda: ())
    monkeypatch.setattr(harness, "_windows_cursor_agent_candidates", lambda: ())
    which_calls: list[str] = []

    def fake_which(name: str) -> str | None:
        which_calls.append(name)
        return "C:/Tools/cursor.cmd" if name == "cursor" else None

    monkeypatch.setattr(harness.shutil, "which", fake_which)

    with pytest.raises(harness.CursorHarnessError, match="Cursor Agent CLI not found"):
        harness._resolve_agent_command()
    assert which_calls == ["agent", "cursor-agent"]


def test_resolve_agent_command_rejects_cursor_without_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness, "_windows_cursor_agent_direct_commands", lambda: ())
    monkeypatch.setattr(harness, "_windows_cursor_agent_candidates", lambda: ())

    def fake_which(name: str) -> str | None:
        return "C:/Tools/cursor.exe" if name == "cursor" else None

    monkeypatch.setattr(harness.shutil, "which", fake_which)

    with pytest.raises(harness.CursorHarnessError, match="Cursor Agent CLI not found"):
        harness._resolve_agent_command()


@pytest.mark.parametrize("mode", [None, "plan", "ask"])
def test_bridge_review_main_preserves_requested_mode_and_agent_output(mode, monkeypatch, capsys):
    harness = _load_harness()
    calls = []
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    monkeypatch.setattr(harness, "_load_project_env_local", lambda **_kwargs: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout='{"message":"CLI delivery acknowledged"}\n', stderr="")

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    # c123 (batch design WP2 2.1): no --skill; the init line that leads the dispatched prompt carries the role.
    args = [
        "--prompt",
        "::init gtkb lo\n::open build\nReview assigned work",
        "--output-format",
        "json",
        "--timeout",
        "30",
    ]
    if mode:
        args += ["--mode", mode]
    assert harness.main(args) == 0
    command, kwargs = calls[0]
    assert command[:1] == ["C:/Tools/agent.exe"]
    assert command[command.index("--output-format") + 1] == "json"
    assert ("--mode" in command) == bool(mode)
    if mode:
        assert command[command.index("--mode") + 1] == mode
    # c123 (batch design WP2 2.1): the prompt reaches Cursor Agent as it came, with no skill text before it.
    assert command[-1] == args[1]
    assert "GTKB_BRIDGE_VERDICT_ENVELOPE" not in command[-1]
    assert kwargs["cwd"] == str(Path.cwd())
    assert kwargs["capture_output"] is True
    assert kwargs["timeout"] == 30.0
    assert capsys.readouterr().out == '{"message":"CLI delivery acknowledged"}\n'


def test_main_can_force_read_only_plan_mode(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    calls = []
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="{}\n", stderr="")

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness.main(["--prompt", "inspect only", "--mode", "plan", "--output-format", "json"]) == 0
    command, _kwargs = calls[0]
    assert command[-3:] == ["--mode", "plan", "inspect only"]
    assert capsys.readouterr().out == "{}\n"


def test_main_uses_no_window_creationflags_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    calls = []
    expected_flag = 0x08000000

    monkeypatch.setattr(harness.os, "name", "nt", raising=False)
    monkeypatch.setattr(harness.subprocess, "CREATE_NO_WINDOW", expected_flag, raising=False)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/cursor.cmd", "agent"])

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        # c123 (batch design WP2 2.1): every run needs stdout now, so the fixture agent writes some.
        return subprocess.CompletedProcess(command, 0, stdout="agent stdout\n", stderr="")

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness.main(["--prompt", "ordinary prompt"]) == 0
    assert calls[0][1]["creationflags"] & expected_flag


def test_bridge_review_zero_output_success_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout=" \n", stderr=""),
    )

    exit_code = harness.main(["--prompt", "::init gtkb lo\nreview this"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    # c123 (batch design WP2 2.1): one refusal for every run, naming no skill, route or role.
    assert captured.err == "cursor_harness: Cursor Agent produced no stdout\n"


def test_verification_zero_output_success_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    exit_code = harness.main(["--prompt", "::init gtkb lo\nverify this"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    # c123 (batch design WP2 2.1): one refusal for every run, naming no skill, route or role.
    assert captured.err == "cursor_harness: Cursor Agent produced no stdout\n"


def test_non_bridge_zero_output_success_also_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """c123 (batch design WP2 2.1): inverted. No role skill marks bridge work any more, so every run needs stdout."""
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    exit_code = harness.main(["--prompt", "ordinary prompt"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "cursor_harness: Cursor Agent produced no stdout\n"


def test_failed_run_without_stdout_keeps_the_agent_exit_code(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """c123 (batch design WP2 2.1): the empty-stdout refusal follows exit 0 only; a failed run keeps its own code."""
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 3, stdout="", stderr="agent failed\n"),
    )

    exit_code = harness.main(["--prompt", "ordinary prompt"])

    captured = capsys.readouterr()
    assert exit_code == 3
    assert captured.out == ""
    assert captured.err == "agent failed\n"


def test_timeout_returns_124_with_safe_context_and_partial_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    prompt = "owner prompt must not appear in timeout diagnostic"

    monkeypatch.setattr(harness, "_load_project_env_local", lambda **_kwargs: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])

    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=command,
            timeout=kwargs["timeout"],
            output="partial stdout\n",
            stderr=b"partial stderr\n",
        )

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    exit_code = harness.main(
        [
            "--prompt",
            prompt,
            "--output-format",
            "json",
            "--mode",
            "plan",
            "--timeout",
            "7",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 124
    assert "partial stdout" in captured.out
    assert "partial stderr" in captured.err
    assert "Cursor Agent timed out after 7s" in captured.err
    assert "exit=124" in captured.err
    assert "executable=agent.exe" in captured.err
    # c123 (batch design WP2 2.1): the diagnostic has no skill field.
    assert "skill=" not in captured.err
    assert "output_format=json" in captured.err
    assert "mode=plan" in captured.err
    assert prompt not in captured.out
    assert prompt not in captured.err
    assert "--workspace" not in captured.err


def test_timeout_redacts_and_truncates_partial_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    key_name = "api" + "_key"
    secret_value = "S" * 24

    monkeypatch.setattr(harness, "_TIMEOUT_CAPTURE_LIMIT_BYTES", 64)
    monkeypatch.setattr(harness, "_load_project_env_local", lambda **_kwargs: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])

    def fake_run(command, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=command,
            timeout=kwargs["timeout"],
            output=f"before {key_name}={secret_value} after " + ("x" * 120),
            stderr=None,
        )

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness.main(["--prompt", "ordinary prompt", "--timeout", "3"]) == 124

    captured = capsys.readouterr()
    assert f"{key_name}=[REDACTED]" in captured.out
    assert secret_value not in captured.out
    assert "partial stdout truncated to 64 bytes" in captured.out
    assert "partial_stdout_bytes=" in captured.err


@pytest.mark.parametrize(
    "skill_arguments",
    [
        ["--skill", "bridge-review"],
        ["--skill", "verification"],
        ["--skill=bridge-review"],
        ["--skill", "../.codex/skills/review"],
        ["--skill", "../../peer"],
        ["--skill", "/absolute"],
        ["--skill", "C:/peer"],
    ],
)
def test_skill_option_is_refused_before_environment_or_launch(skill_arguments, monkeypatch, capsys):
    """c123 (batch design WP2 2.1): no argument selects a skill; any --skill is a usage error before any read."""
    harness = _load_harness()

    def forbidden(*args, **kwargs):
        pytest.fail("A --skill argument must be refused before environment loading or launch")

    monkeypatch.setattr(harness, "_load_project_env_local", forbidden)
    monkeypatch.setattr(harness.subprocess, "run", forbidden)
    with pytest.raises(SystemExit) as error:
        harness.main(["--prompt", "review this", *skill_arguments])
    assert error.value.code == 2
    assert "unrecognized arguments: --skill" in capsys.readouterr().err


def test_prompt_carries_no_skill_text_from_own_or_peer_projections(tmp_path, monkeypatch):
    """c123 (batch design WP2 2.1): no skill is loaded, its own or a peer's; the prompt goes as it came."""
    harness = _load_harness()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(harness, "_load_project_env_local", lambda **_kwargs: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_cursor_agent_env", lambda **_kwargs: {})
    for tree in (".agents", ".codex", ".claude"):
        skill = tmp_path / tree / "skills" / "gtkb-verify" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(f"Instruction from {tree}", encoding="utf-8")
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    calls = []

    def launch(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="agent stdout\n", stderr="")

    monkeypatch.setattr(harness.subprocess, "run", launch)
    prompt = "::init gtkb lo\nVerify the dispatched report"
    assert harness.main(["--prompt", prompt]) == 0
    assert calls[0][-1] == prompt
    assert not any("Instruction from" in part for part in calls[0])
    after = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert after == before


@pytest.mark.parametrize("identifier", [None, "GTKB_BRIDGE_POLLER_RUN_ID", "GTKB_INHERITED_SESSION_ID"])
@pytest.mark.parametrize("outcome,exit_code", [("success", 0), ("failure", 7), ("timeout", 124)])
def test_main_never_infers_other_process_ownership(identifier, outcome, exit_code, monkeypatch, tmp_path, capsys):
    harness = _load_harness()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(harness, "_load_project_env_local", lambda **_kwargs: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_cursor_agent_env", lambda **kwargs: {})
    for key in ["GTKB_BRIDGE_POLLER_RUN_ID", "GTKB_INHERITED_SESSION_ID"]:
        monkeypatch.delenv(key, raising=False)
    if identifier:
        monkeypatch.setenv(identifier, "inherited-label-is-not-process-ownership")

    def forbidden_process_enumeration(*args, **kwargs):
        pytest.fail("The Cursor worker must not enumerate other processes")

    monkeypatch.setitem(sys.modules, "psutil", SimpleNamespace(process_iter=forbidden_process_enumeration))
    sentinel = tmp_path / "unrelated.txt"
    sentinel.write_bytes(b"Unrelated bytes must survive the launch outcome.")
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    calls = []

    def launch(command, **kwargs):
        calls.append((command, kwargs))
        if outcome == "timeout":
            raise subprocess.TimeoutExpired(
                command, kwargs["timeout"], output="partial stdout\n", stderr="partial stderr\n"
            )
        return subprocess.CompletedProcess(command, exit_code, stdout="agent stdout\n", stderr="agent stderr\n")

    monkeypatch.setattr(harness.subprocess, "run", launch)
    assert harness.main(["--prompt", "owner prompt", "--timeout", "5"]) == exit_code
    assert len(calls) == 1
    assert calls[0][1]["cwd"] == str(tmp_path)
    assert calls[0][1]["timeout"] == 5
    captured = capsys.readouterr()
    if outcome == "timeout":
        assert captured.out == "partial stdout\n"
        assert captured.err.startswith("partial stderr\n")
        assert "Cursor Agent timed out after 5s" in captured.err
        assert "owner prompt" not in captured.err
    else:
        assert captured.out == "agent stdout\n"
        assert captured.err == "agent stderr\n"
    after = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert after == before


@pytest.mark.parametrize("timeout", ["0", "-1", "inf", "nan"])
def test_main_invalid_timeout_refuses_before_environment_or_launch(timeout, monkeypatch):
    harness = _load_harness()

    def forbidden(**kwargs):
        pytest.fail("Invalid timeout must refuse before environment loading")

    monkeypatch.setattr(harness, "_load_project_env_local", forbidden)
    with pytest.raises(SystemExit) as error:
        harness.main(["--prompt", "not launched", "--timeout", timeout])
    assert error.value.code == 2
