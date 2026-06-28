# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for scripts/cursor_harness.py Loyal Opposition skill-route resolution (WI-4872).

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
    """WI-4872: 'bridge-review' aliases to the real proposal-review skill contract."""
    harness = _load_harness()
    content = harness._skill_system_prompt("bridge-review")
    assert content is not None
    assert "proposal-review" in content


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


def test_resolve_agent_executable_uses_agent_not_cursor_gui(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda name: "C:/Tools/agent.exe" if name == "agent" else None)

    assert harness._resolve_agent_executable() == "C:/Tools/agent.exe"


def test_resolve_agent_executable_rejects_cursor_gui_override(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.setenv("CURSOR_AGENT_BIN", "C:/Users/mike/AppData/Local/Programs/Cursor/cursor.exe")

    with pytest.raises(harness.CursorHarnessError, match="Cursor GUI launcher"):
        harness._resolve_agent_executable()


def test_resolve_agent_executable_does_not_fallback_to_cursor_gui(monkeypatch: pytest.MonkeyPatch) -> None:
    harness = _load_harness()
    monkeypatch.delenv("CURSOR_AGENT_BIN", raising=False)
    monkeypatch.setattr(harness.shutil, "which", lambda name: "C:/Tools/cursor.exe" if name == "cursor" else None)

    with pytest.raises(harness.CursorHarnessError, match="Cursor Agent CLI not found"):
        harness._resolve_agent_executable()


def test_bridge_review_main_builds_prompt_mode_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    calls = []

    monkeypatch.setattr(harness, "_resolve_agent_executable", lambda: "C:/Tools/agent.exe")
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
    assert command[0] == "C:/Tools/agent.exe"
    assert command[1:5] == ["-p", "--trust", "--workspace", str(harness.PROJECT_ROOT)]
    assert command[5:7] == ["--output-format", "text"]
    assert "SKILL CONTRACT" in command[-1]
    assert "review this bridge file" in command[-1]
    assert kwargs["cwd"] == str(harness.PROJECT_ROOT)
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["timeout"] == 30.0
    assert kwargs["env"]["GTKB_HARNESS_NAME"] == "cursor"
    assert kwargs["env"]["GTKB_HARNESS_ID"] == "E"
    assert capsys.readouterr().out == "GO\n"


def test_bridge_review_zero_output_success_fails_closed(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    harness = _load_harness()
    monkeypatch.setattr(harness, "_resolve_agent_executable", lambda: "C:/Tools/agent.exe")
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
    monkeypatch.setattr(harness, "_resolve_agent_executable", lambda: "C:/Tools/agent.exe")
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
    monkeypatch.setattr(harness, "_resolve_agent_executable", lambda: "C:/Tools/agent.exe")
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
