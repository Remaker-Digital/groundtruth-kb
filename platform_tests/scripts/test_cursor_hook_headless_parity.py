# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cursor hook no-window parity checks for WI-4925."""

from __future__ import annotations

import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CURSOR_HOOKS_PATH = PROJECT_ROOT / ".cursor" / "hooks.json"
CURSOR_ADAPTER_PATH = PROJECT_ROOT / "scripts" / "cursor_hook_adapter.py"
WORKSTREAM_FOCUS_CMD_PATH = PROJECT_ROOT / ".cursor" / "gtkb-hooks" / "workstream-focus.cmd"
RUN_CMD_NO_WINDOW = r"E:\GT-KB\.codex\gtkb-hooks\run_cmd_no_window.py"
RUN_PY_NO_WINDOW = r"E:\GT-KB\.codex\gtkb-hooks\run_py_no_window.py"
CURSOR_CMD_HOOK_ROOT = r"E:\GT-KB\.cursor\gtkb-hooks"
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


def test_cursor_hooks_use_pythonw_launcher_only() -> None:
    commands = _cursor_hook_commands()

    assert commands, "Cursor hooks.json must register hook commands"
    bare_python = [command for command in commands if re.search(r"(?i)(?:^|\s)python(?:\.exe)?\s+", command)]

    assert not bare_python, "Cursor hook commands must use pythonw.exe, not console-attached python"
    assert all("pythonw.exe " in command for command in commands)


def test_cursor_py_hooks_route_through_no_window_wrapper() -> None:
    commands = _cursor_hook_commands()
    bare_py_hooks: list[str] = []
    wrapped_py_hooks: list[str] = []
    for command in commands:
        if RUN_CMD_NO_WINDOW in command:
            continue
        if RUN_PY_NO_WINDOW in command:
            wrapped_py_hooks.append(command)
            assert command.startswith(f"pythonw.exe {RUN_PY_NO_WINDOW} "), command
            continue
        if ".py" in command.lower():
            bare_py_hooks.append(command)

    assert not bare_py_hooks, (
        "Every Cursor .py hook must route through run_py_no_window.py; bare targets: " + "; ".join(bare_py_hooks)
    )
    assert wrapped_py_hooks, "Expected Cursor .py hooks to use run_py_no_window.py"


def test_cursor_cmd_hooks_route_through_no_window_wrapper() -> None:
    commands = _cursor_hook_commands()
    cmd_hook_commands = [command for command in commands if ".cmd" in command.lower()]

    assert cmd_hook_commands, "Expected at least one Cursor .cmd hook invocation"
    for command in cmd_hook_commands:
        assert command.startswith(f"pythonw.exe {RUN_CMD_NO_WINDOW} "), command
        assert CURSOR_CMD_HOOK_ROOT in command, command
        assert not command.lower().startswith("cmd /d /s /c"), command


def test_cursor_workstream_focus_cmd_uses_pythonw() -> None:
    script = WORKSTREAM_FOCUS_CMD_PATH.read_text(encoding="utf-8")

    assert "pythonw.exe" in script
    assert not re.search(r"(?im)^\s*python(?:\.exe)?\s+", script)


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
