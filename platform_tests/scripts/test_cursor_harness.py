# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/cursor_harness.py Loyal Opposition skill-route resolution.

The harness-registry Cursor invocation surfaces pass the canonical LO route keys
'bridge-review' / 'verification', which have no SKILL.md. These tests assert the
alias resolution maps them to the real skill contracts so headless LO dispatch
loads a contract instead of failing closed, while genuinely unknown routes still
fail closed.
"""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HARNESS_PATH = _REPO_ROOT / "scripts" / "cursor_harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("cursor_harness_test", _HARNESS_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skill_route_alias_bridge_review_resolves() -> None:
    """WI-4933: 'bridge-review' aliases to the bridge protocol contract."""
    harness = _load_harness()
    content = harness._skill_system_prompt("bridge-review")
    assert content is not None
    assert "name: gtkb-bridge" in content
    assert "Operate the bridge protocol" in content


def test_skill_route_alias_verification_resolves() -> None:
    """WI-4872: 'verification' aliases to the real verify skill contract."""
    harness = _load_harness()
    content = harness._skill_system_prompt("verification")
    assert content is not None
    assert "verify" in content.lower()


def test_skill_route_non_aliased_resolves() -> None:
    """A real skill name resolves directly (no alias needed)."""
    harness = _load_harness()
    content = harness._skill_system_prompt("proposal-review")
    assert content is not None


def test_skill_route_unknown_still_raises() -> None:
    """Genuinely unknown routes still fail closed (CursorHarnessError preserved)."""
    harness = _load_harness()
    with pytest.raises(harness.CursorHarnessError, match="unknown skill route"):
        harness._skill_system_prompt("definitely-not-a-skill")


def test_skill_route_none_returns_none() -> None:
    """No skill route yields no system prompt."""
    harness = _load_harness()
    assert harness._skill_system_prompt(None) is None


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


def test_resolve_agent_command_accepts_cursor_agent_override(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.setenv("CURSOR_AGENT_BIN", "C:/Users/mike/AppData/Local/Programs/Cursor/cursor.exe")
    monkeypatch.setattr(harness, "_cursor_supports_agent_subcommand", lambda _path: True)

    assert harness._resolve_agent_command() == [
        "C:/Users/mike/AppData/Local/Programs/Cursor/cursor.exe",
        "agent",
    ]


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

    assert harness._cursor_supports_agent_subcommand("C:/Tools/cursor.cmd") is False
    assert calls[0][0] == ["C:/Tools/cursor.cmd", "agent", "--help"]
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

    assert harness._cursor_supports_agent_subcommand("C:/Tools/cursor.cmd") is True


def test_resolve_agent_command_rejects_cursor_override_without_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.setenv("CURSOR_AGENT_BIN", "C:/Users/mike/AppData/Local/Programs/Cursor/cursor.exe")
    monkeypatch.setattr(harness, "_cursor_supports_agent_subcommand", lambda _path: False)

    with pytest.raises(harness.CursorHarnessError, match="without an unambiguous headless `agent` subcommand"):
        harness._resolve_agent_command()


def test_resolve_agent_command_falls_back_to_cursor_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness, "_windows_cursor_agent_direct_commands", lambda: ())
    monkeypatch.setattr(harness, "_windows_cursor_agent_candidates", lambda: ())

    def fake_which(name: str) -> str | None:
        return "C:/Tools/cursor.cmd" if name == "cursor" else None

    monkeypatch.setattr(harness.shutil, "which", fake_which)
    monkeypatch.setattr(harness, "_cursor_supports_agent_subcommand", lambda _path: True)

    assert harness._resolve_agent_command() == ["C:/Tools/cursor.cmd", "agent"]


def test_resolve_agent_command_rejects_cursor_without_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness, "_windows_cursor_agent_direct_commands", lambda: ())
    monkeypatch.setattr(harness, "_windows_cursor_agent_candidates", lambda: ())

    def fake_which(name: str) -> str | None:
        return "C:/Tools/cursor.exe" if name == "cursor" else None

    monkeypatch.setattr(harness.shutil, "which", fake_which)
    monkeypatch.setattr(harness, "_cursor_supports_agent_subcommand", lambda _path: False)

    with pytest.raises(harness.CursorHarnessError, match="Cursor Agent CLI not found"):
        harness._resolve_agent_command()


def test_bridge_review_main_builds_prompt_mode_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    calls = []

    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/cursor.cmd", "agent"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: "SKILL CONTRACT" if skill else None)

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="GO\n", stderr="")

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    exit_code = harness.main(
        [
            "--prompt",
            "review this bridge file",
            "--skill",
            "bridge-review",
            "--output-format",
            "text",
            "--timeout",
            "30",
        ]
    )

    assert exit_code == 0
    command, kwargs = calls[0]
    assert command[:2] == ["C:/Tools/cursor.cmd", "agent"]
    assert command[2:6] == ["-p", "--trust", "--workspace", str(harness.PROJECT_ROOT)]
    assert command[6:8] == ["--output-format", "text"]
    assert "SKILL CONTRACT" in command[-1]
    assert "review this bridge file" in command[-1]
    assert kwargs["cwd"] == str(harness.PROJECT_ROOT)
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["timeout"] == 30.0
    assert kwargs["env"]["GTKB_HARNESS_NAME"] == "cursor"
    assert kwargs["env"]["GTKB_HARNESS_ID"] == "E"
    assert capsys.readouterr().out == "GO\n"


def test_main_uses_no_window_creationflags_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    calls = []
    expected_flag = 0x08000000

    monkeypatch.setattr(harness.os, "name", "nt", raising=False)
    monkeypatch.setattr(harness.subprocess, "CREATE_NO_WINDOW", expected_flag, raising=False)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/cursor.cmd", "agent"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: None)

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(harness.subprocess, "run", fake_run)

    assert harness.main(["--prompt", "ordinary prompt"]) == 0
    assert calls[0][1]["creationflags"] & expected_flag


def test_bridge_review_zero_output_success_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: "SKILL CONTRACT" if skill else None)
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout=" \n", stderr=""),
    )

    exit_code = harness.main(["--prompt", "review this", "--skill", "bridge-review"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "produced no stdout" in captured.err
    assert "bridge-review" in captured.err


def test_verification_zero_output_success_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: "SKILL CONTRACT" if skill else None)
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    exit_code = harness.main(["--prompt", "verify this", "--skill", "verification"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "produced no stdout" in captured.err
    assert "verification" in captured.err


def test_non_bridge_zero_output_success_is_preserved(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: "SKILL CONTRACT" if skill else None)
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )

    exit_code = harness.main(["--prompt", "ordinary prompt"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.out == ""
    assert captured.err == ""


def test_cursor_agent_provenance_records_only_new_processes() -> None:
    harness = _load_harness()
    before = {
        (10, 100.0): {
            "pid": 10,
            "ppid": 1,
            "name": "agent.exe",
            "create_time_epoch": 100.0,
        }
    }
    after = {
        **before,
        (11, 200.0): {
            "pid": 11,
            "ppid": 1,
            "name": "cursor-agent.exe",
            "create_time_epoch": 200.0,
        },
        (12, 90.0): {
            "pid": 12,
            "ppid": 1,
            "name": "cursor-agent.exe",
            "create_time_epoch": 90.0,
        },
    }

    records = harness._cursor_agent_provenance_records(
        before,
        after,
        dispatch_root_pid=900,
        started_at_epoch=150.0,
    )

    assert records == [{"pid": 11, "create_time_epoch": 200.0, "dispatch_root_pid": 900}]


def test_dispatch_main_records_new_cursor_agent_provenance(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    snapshots = [
        {},
        {
            (21, 300.0): {
                "pid": 21,
                "ppid": 1,
                "name": "cursor-agent.exe",
                "create_time_epoch": 300.0,
            }
        },
    ]
    merged: list[dict] = []

    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "dispatch-123")
    monkeypatch.setattr(harness, "_load_project_env_local", lambda: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: None)
    monkeypatch.setattr(harness.os, "getpid", lambda: 901)
    monkeypatch.setattr(harness.time, "time", lambda: 250.0)
    monkeypatch.setattr(harness, "_cursor_agent_snapshot", lambda _project_root: snapshots.pop(0))
    monkeypatch.setattr(
        harness, "_merge_cursor_agent_provenance", lambda _project_root, records: merged.extend(records)
    )
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr=""),
    )

    assert harness.main(["--prompt", "dispatch prompt"]) == 0

    assert merged == [{"pid": 21, "create_time_epoch": 300.0, "dispatch_root_pid": 901}]
    assert capsys.readouterr().out == "ok\n"


def test_interactive_main_does_not_record_cursor_agent_provenance(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    merged: list[dict] = []

    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)
    monkeypatch.delenv("GTKB_INHERITED_SESSION_ID", raising=False)
    monkeypatch.setattr(harness, "_load_project_env_local", lambda: None)
    monkeypatch.setattr(harness, "_resolve_agent_command", lambda: ["C:/Tools/agent.exe"])
    monkeypatch.setattr(harness, "_skill_system_prompt", lambda skill: None)
    monkeypatch.setattr(
        harness, "_merge_cursor_agent_provenance", lambda _project_root, records: merged.extend(records)
    )
    monkeypatch.setattr(
        harness.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr=""),
    )

    assert harness.main(["--prompt", "ordinary prompt"]) == 0

    assert merged == []
    assert capsys.readouterr().out == "ok\n"
