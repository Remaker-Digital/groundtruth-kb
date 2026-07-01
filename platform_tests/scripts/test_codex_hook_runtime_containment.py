# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Regression tests for Codex hook runtime containment."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_CMD_NO_WINDOW = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_cmd_no_window.py"
RUN_PY_NO_WINDOW = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window.py"
RUN_CMD_NO_WINDOW_SHIM = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_cmd_no_window"
RUN_PY_NO_WINDOW_SHIM = REPO_ROOT / ".codex" / "gtkb-hooks" / "run_py_no_window"
CODEX_HOOKS = REPO_ROOT / ".codex" / "hooks.json"
BOM_SENSITIVE_CMD_WRAPPERS = (
    REPO_ROOT / ".codex" / "gtkb-hooks" / "workstream-focus.cmd",
    REPO_ROOT / ".codex" / "gtkb-hooks" / "formal-artifact-approval.cmd",
)


def _run_wrapper(
    args: list[str], *, stdin: str = "payload\n", timeout: float = 5.0
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS"] = "1"
    return subprocess.run(
        [sys.executable, *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
        env=env,
    )


def _load_run_py_no_window_module():
    spec = importlib.util.spec_from_file_location("run_py_no_window_for_test", RUN_PY_NO_WINDOW)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_codex_hooks_registry_uses_hidden_launchers_without_retired_dispatch_workers() -> None:
    hooks = json.loads(CODEX_HOOKS.read_text(encoding="utf-8"))
    groups = [group for event_groups in hooks["hooks"].values() for group in event_groups]
    commands = [hook["command"] for group in groups for hook in group["hooks"]]
    batch_catalog_text = json.dumps(_load_run_py_no_window_module().BATCHES)

    assert commands
    assert all(len(group["hooks"]) == 1 for group in groups)
    assert all(command.split()[0].lower().endswith("pythonw.exe") for command in commands)
    assert all("run_py_no_window.py" not in command for command in commands)
    assert all("run_cmd_no_window.py" not in command for command in commands)
    assert any("--batch pretooluse-bash" in command for command in commands)
    assert "implementation-start-gate.cmd" in batch_catalog_text
    assert "auto_finalize_sweep.py" in batch_catalog_text
    forbidden = (
        "cross_" + "harness_" + "bridge_" + "trigger.py",
        "single_harness_bridge_automation.py",
        "single_harness_bridge_dispatcher.py",
        "bridge-dispatch-trigger",
        "dispatcher-daemon.cmd",
        "gtkb_dispatcher_daemon.py",
    )
    assert not any(token in command for command in commands for token in forbidden)


def test_run_py_no_window_passes_finite_stdin_and_preserves_output_and_exit_code(tmp_path: Path) -> None:
    child = tmp_path / "child.py"
    child.write_text(
        "import sys\n"
        "payload = sys.stdin.read().strip()\n"
        "print(f'OUT:{payload}')\n"
        "print(f'ERR:{payload}', file=sys.stderr)\n"
        "raise SystemExit(7)\n",
        encoding="utf-8",
    )

    result = _run_wrapper([str(RUN_PY_NO_WINDOW), str(child)])

    assert result.returncode == 7
    assert result.stdout == "OUT:payload\n"
    assert result.stderr == "ERR:payload\n"


def test_extensionless_run_py_no_window_shim_delegates_to_core_wrapper(tmp_path: Path) -> None:
    child = tmp_path / "child.py"
    child.write_text("import sys\nprint(sys.stdin.read().strip())\nraise SystemExit(3)\n", encoding="utf-8")

    result = _run_wrapper([str(RUN_PY_NO_WINDOW_SHIM), str(child)])

    assert result.returncode == 3
    assert result.stdout == "payload\n"


def test_run_py_no_window_rejects_unknown_batch() -> None:
    result = _run_wrapper([str(RUN_PY_NO_WINDOW), "--batch", "missing-batch"])

    assert result.returncode == 2
    assert "unknown hook batch" in result.stderr


def test_run_py_no_window_batch_catalog_targets_exist() -> None:
    module = _load_run_py_no_window_module()

    for entries in module.BATCHES.values():
        for entry in entries:
            command = module._batch_command(entry)
            target = Path(command[1] if command[0].lower().endswith("pythonw.exe") else command[0])
            assert target.exists()


def test_run_cmd_no_window_passes_finite_stdin_and_preserves_output_and_exit_code(tmp_path: Path) -> None:
    child = tmp_path / "child.cmd"
    child.write_text(
        "@echo off\nset /p PAYLOAD=\necho OUT:%PAYLOAD%\necho ERR:%PAYLOAD% 1>&2\nexit /b 7\n",
        encoding="utf-8",
    )

    result = _run_wrapper([str(RUN_CMD_NO_WINDOW), str(child)])

    assert result.returncode == 7
    assert result.stdout == "OUT:payload\n"
    assert result.stderr == "ERR:payload \n"


def test_extensionless_run_cmd_no_window_shim_delegates_to_core_wrapper(tmp_path: Path) -> None:
    child = tmp_path / "child.cmd"
    child.write_text("@echo off\nset /p PAYLOAD=\necho %PAYLOAD%\nexit /b 3\n", encoding="utf-8")

    result = _run_wrapper([str(RUN_CMD_NO_WINDOW_SHIM), str(child)])

    assert result.returncode == 3
    assert result.stdout == "payload\n"


def test_run_cmd_no_window_times_out_stalled_child(tmp_path: Path) -> None:
    child = tmp_path / "stall.cmd"
    child.write_text(
        f'@echo off\n"{sys.executable}" -c "import time; time.sleep(10)"\n',
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["GTKB_CODEX_HOOK_CHILD_TIMEOUT_SECONDS"] = "0.2"

    result = subprocess.run(
        [sys.executable, str(RUN_CMD_NO_WINDOW), str(child)],
        text=True,
        capture_output=True,
        check=False,
        timeout=5,
        env=env,
    )

    assert result.returncode == 124
    assert "hook child timed out" in result.stderr


def test_codex_cmd_wrappers_do_not_start_with_utf8_bom() -> None:
    for path in BOM_SENSITIVE_CMD_WRAPPERS:
        assert not path.read_bytes().startswith(b"\xef\xbb\xbf"), path
