# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Cursor hook no-window parity checks for WI-4925."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_harness_parity import _load_projector

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CURSOR_ADAPTER_PATH = PROJECT_ROOT / "scripts" / "cursor_hook_adapter.py"


def _cursor_registration() -> str:
    plan = _load_projector(PROJECT_ROOT).build_plan("cursor")
    assert not plan.gaps, plan.gaps
    return plan.writes[".cursor/hooks.json"]


def _cursor_hook_commands() -> list[str]:
    hooks = json.loads(_cursor_registration())["hooks"]
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
    raw = _cursor_registration()
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
        "kb-not-markdown.py",
        "destructive-gate.py",
        "credential-scan.py",
        "scanner-safe-writer.py",
        "implementation_start_gate.py",
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
    # M15: inner hooks start bytecode-free so authored baseline hooks leave no cache behind.
    assert 'subprocess.run([sys.executable, "-B", str(target), *sys.argv[2:]], **run_kwargs)' in source


def _run_adapter(
    target: Path, payload: dict, *, cwd: Path | None = None, adapter: Path = CURSOR_ADAPTER_PATH
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(filter(None, (env.get("PYTHONPATH"), str(PROJECT_ROOT))))
    return subprocess.run(
        [sys.executable, str(adapter), str(target)],
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


def test_adapter_preserves_native_permission_deny_from_successful_process(tmp_path: Path) -> None:
    target = tmp_path / "native_deny.py"
    target.write_text(
        'import json\nprint(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", '
        '"permissionDecision": "deny", "permissionDecisionReason": "native effect refused"}}))\n',
        encoding="utf-8",
    )
    completed = _run_adapter(target, {"tool_name": "Write", "tool_input": {"path": "x"}})
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["user_message"] == "native effect refused"


def test_adapter_does_not_accept_json_from_failed_hook_process(tmp_path: Path) -> None:
    target = tmp_path / "failed_allow.py"
    target.write_text('print("{}")\nraise SystemExit(1)\n', encoding="utf-8")
    completed = _run_adapter(target, {"tool_name": "Write", "tool_input": {"path": "x"}})
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["permission"] == "deny"


def test_adapter_preserves_real_native_gate_refusal(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("GTKB_NATIVE_CONTEXT_ID", raising=False)
    destination = tmp_path / "must-not-be-written.txt"
    completed = _run_adapter(
        PROJECT_ROOT / "scripts/implementation_start_gate.py",
        {"tool_name": "Write", "tool_input": {"file_path": str(destination), "content": "blocked"}},
    )
    result = json.loads(completed.stdout)
    assert completed.returncode == 2
    assert result["permission"] == "deny"
    assert "current harness-native context identifier" in result["user_message"]
    assert not destination.exists()


@pytest.mark.timeout(300)
def test_adapter_resolves_relative_target_from_non_repo_cwd(tmp_path: Path, generated_harness_root) -> None:
    from platform_tests.scripts.sot_hook_fixtures import SUBSTITUTE, registry

    root = tmp_path / "projected-copy"
    shutil.copytree(generated_harness_root, root)
    registry(root)
    hook = Path(".harness-baseline-configuration/hooks/sot-read-discipline.py")
    adapter = root / "scripts/cursor_hook_adapter.py"
    payload = {"tool_name": "Read", "cwd": str(root), "tool_input": {"path": str(root / SUBSTITUTE)}}
    completed = _run_adapter(hook, payload, cwd=tmp_path, adapter=adapter)
    result = json.loads(completed.stdout)
    assert completed.returncode == 2 and result["permission"] == "deny", result
    assert "fixture-work" in result["user_message"]
    payload["tool_input"]["path"] = str(root / "README.md")
    allowed = _run_adapter(hook, payload, cwd=tmp_path, adapter=adapter)
    assert allowed.returncode == 0 and json.loads(allowed.stdout)["permission"] == "allow"


@pytest.mark.timeout(300)
def test_cursor_shell_adapter_preserves_event_cwd_for_registered_reads(tmp_path, generated_harness_root):
    from platform_tests.scripts.sot_hook_fixtures import registry

    root = tmp_path / "projected-copy"
    shutil.copytree(generated_harness_root, root)
    registry(root)
    (root / "derived").mkdir()
    hook = Path(".harness-baseline-configuration/hooks/sot-read-discipline.py")
    adapter = root / "scripts/cursor_hook_adapter.py"
    payload = {"tool_name": "Shell", "cwd": str(root / "derived"), "tool_input": {"command": "cat status.txt"}}
    blocked = _run_adapter(hook, payload, cwd=tmp_path, adapter=adapter)
    result = json.loads(blocked.stdout)
    assert blocked.returncode == 2 and result["permission"] == "deny", result
    assert "fixture-work" in result["user_message"]
    payload["tool_input"]["command"] = "cat unrelated.txt"
    allowed = _run_adapter(hook, payload, cwd=tmp_path, adapter=adapter)
    assert allowed.returncode == 0 and json.loads(allowed.stdout)["permission"] == "allow"
