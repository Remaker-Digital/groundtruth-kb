# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cursor hook no-window parity checks for WI-4925."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CURSOR_HOOKS_PATH = PROJECT_ROOT / ".cursor" / "hooks.json"
CURSOR_ADAPTER_PATH = PROJECT_ROOT / "scripts" / "cursor_hook_adapter.py"
SESSION_START_CORE = PROJECT_ROOT / "scripts" / "session_start_dispatch_core.py"
SESSION_SELF_INIT = PROJECT_ROOT / "scripts" / "session_self_initialization.py"


def _cursor_hook_commands() -> list[str]:
    hooks = json.loads(CURSOR_HOOKS_PATH.read_text(encoding="utf-8"))["hooks"]
    commands: list[str] = []
    for entries in hooks.values():
        for entry in entries:
            command = entry.get("command")
            if isinstance(command, str):
                commands.append(command)
    return commands


def test_cursor_interactive_hooks_use_venv_python_exe() -> None:
    commands = _cursor_hook_commands()

    assert commands, "Cursor hooks.json must register hook commands"
    bare_python = [command for command in commands if re.search(r"(?i)(?:^|\s)python(?:\.exe)?\s+", command)]

    assert not bare_python, "Cursor hook commands must use the venv python.exe path, not a bare interpreter"
    assert all("python.exe" in command for command in commands)
    assert all("pythonw.exe" not in command for command in commands)
    assert all("cursor_hook_adapter.py" in command for command in commands)


def test_cursor_fail_closed_hooks_use_timeout_floor_and_write_matchers() -> None:
    raw = CURSOR_HOOKS_PATH.read_text(encoding="utf-8")
    hooks = json.loads(raw)["hooks"]
    assert '"timeout": 5' not in raw

    fail_closed = [
        entry
        for event, entries in hooks.items()
        if event in {"preToolUse", "beforeSubmitPrompt", "stop", "beforeShellExecution"}
        for entry in entries
        if entry.get("failClosed") is True
    ]
    assert fail_closed
    assert all(int(entry.get("timeout") or 0) >= 30 for entry in fail_closed)

    write_only = (
        "spec-before-code.py",
        "kb-not-markdown.py",
        "destructive-gate.py",
        "credential-scan.py",
        "scanner-safe-writer.py",
        "formal-artifact-approval-gate.py",
    )
    for script in write_only:
        matching = [
            entry for entries in hooks.values() for entry in entries if script in str(entry.get("command") or "")
        ]
        assert matching, f"missing live Cursor hook for {script}"
        assert all(str(entry.get("matcher") or "").strip() for entry in matching), (
            f"{script} must have a non-empty matcher so it does not fire on Read"
        )


def test_cursor_hook_adapter_uses_create_no_window_for_inner_hooks() -> None:
    source = CURSOR_ADAPTER_PATH.read_text(encoding="utf-8")

    assert "CREATE_NO_WINDOW" in source
    assert "creationflags" in source
    assert "_windows_no_window_creationflags" in source
    assert "subprocess.run([sys.executable, str(target), *sys.argv[2:]], **run_kwargs)" in source


def test_session_start_dispatch_core_spawns_startup_service_headless() -> None:
    source = SESSION_START_CORE.read_text(encoding="utf-8")

    assert "no_window_subprocess_kwargs" in source
    assert "prefer_pythonw_executable" in source
    assert "**no_window_subprocess_kwargs()" in source


def test_session_self_initialization_command_output_is_headless() -> None:
    source = SESSION_SELF_INIT.read_text(encoding="utf-8")

    assert "from scripts.windows_subprocess import no_window_subprocess_kwargs" in source
    assert "def _command_output" in source
    command_output = source.split("def _command_output", 1)[1].split("\ndef ", 1)[0]
    assert "**no_window_subprocess_kwargs()" in command_output


def _run_adapter(target: Path, payload: dict, *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    return subprocess.run(
        [sys.executable, str(CURSOR_ADAPTER_PATH), str(target)],
        input=json.dumps(payload),
        cwd=str(cwd or PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_adapter_maps_inner_block_exit_1_to_cursor_deny_exit_2(tmp_path: Path) -> None:
    target = tmp_path / "block_exit_1.py"
    target.write_text(
        'import json, sys\nprint(json.dumps({"decision": "block", "reason": "nope"}))\nsys.exit(1)\n',
        encoding="utf-8",
    )
    completed = _run_adapter(target, {"tool_name": "Read", "tool_input": {"path": "x"}})
    payload = json.loads(completed.stdout.strip().splitlines()[-1])

    assert completed.returncode == 2
    assert payload["permission"] == "deny"
    assert payload["user_message"] == "nope"


def test_adapter_maps_empty_success_to_cursor_allow_exit_0(tmp_path: Path) -> None:
    target = tmp_path / "empty_ok.py"
    target.write_text("raise SystemExit(0)\n", encoding="utf-8")
    completed = _run_adapter(target, {"tool_name": "Read", "tool_input": {"path": "x"}})
    payload = json.loads(completed.stdout.strip().splitlines()[-1])

    assert completed.returncode == 0
    assert payload["permission"] == "allow"


def test_adapter_maps_block_json_exit_0_to_cursor_deny_exit_2(tmp_path: Path) -> None:
    target = tmp_path / "block_exit_0.py"
    target.write_text(
        'import json\nprint(json.dumps({"decision": "block", "reason": "blocked"}))\n',
        encoding="utf-8",
    )
    completed = _run_adapter(target, {"tool_name": "Read", "tool_input": {"path": "x"}})
    payload = json.loads(completed.stdout.strip().splitlines()[-1])

    assert completed.returncode == 2
    assert payload["permission"] == "deny"
    assert payload["user_message"] == "blocked"


def test_adapter_maps_empty_failure_to_cursor_deny_exit_2(tmp_path: Path) -> None:
    target = tmp_path / "empty_fail.py"
    target.write_text("raise SystemExit(1)\n", encoding="utf-8")
    completed = _run_adapter(target, {"tool_name": "Read", "tool_input": {"path": "x"}})
    payload = json.loads(completed.stdout.strip().splitlines()[-1])

    assert completed.returncode == 2
    assert payload["permission"] == "deny"


def test_adapter_resolves_relative_target_from_non_repo_cwd(tmp_path: Path) -> None:
    relative = Path(".cursor") / "hooks" / "sot-read-discipline.py"
    payload = {
        "tool_name": "Read",
        "tool_input": {"path": str(PROJECT_ROOT / "README.md")},
    }
    completed = _run_adapter(relative, payload, cwd=tmp_path)
    last = json.loads(completed.stdout.strip().splitlines()[-1])

    assert completed.returncode in {0, 2}
    assert last["permission"] in {"allow", "deny"}
    assert "Hook target not found" not in last.get("user_message", "")
