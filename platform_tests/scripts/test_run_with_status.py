# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the run_with_status.py dispatch wrapper Windows creationflags discipline (WI-4529).

Spec linkage: GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (the spawn decision derives from a
fresh os.name check at spawn time) + REQ-HARNESS-REGISTRY-001 (the wrapper carries
the registry-defined argv vector through to the child). The wrapper must pass
creationflags=CREATE_NO_WINDOW on Windows so dispatched harness runs do not flash
an empty console window, and must pass 0 (a no-op) off Windows.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from scripts import run_with_status

EXPECTED_WINDOWS_FLAG = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


class _RecordingProcess:
    returncode = 0
    pid = 4321

    def wait(self, timeout: float | None = None) -> int:  # noqa: ARG002 - parity with Popen.wait
        return 0

    def poll(self) -> int:
        return 0


def _invoke(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    os_name: str,
    command: list[str] | None = None,
) -> dict[str, object]:
    """Run run_with_status.main() with Popen stubbed, returning the captured Popen kwargs."""
    captured: dict[str, object] = {}

    def fake_popen(cmd_args, **kwargs):  # noqa: ANN001, ANN003 - test stub
        captured["cmd_args"] = cmd_args
        captured["kwargs"] = kwargs
        return _RecordingProcess()

    monkeypatch.setattr(run_with_status.os, "name", os_name)
    monkeypatch.setattr(run_with_status.subprocess, "Popen", fake_popen)

    status_file = tmp_path / "status.txt"
    with pytest.raises(SystemExit) as exc_info:
        run_with_status.main([str(status_file), *(command or [sys.executable, "--version"])])

    captured["exit_code"] = exc_info.value.code
    captured["status_file"] = status_file
    return captured


def test_popen_uses_create_no_window_on_windows_via_monkeypatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured = _invoke(monkeypatch, tmp_path, "nt")

    kwargs = captured["kwargs"]
    assert "creationflags" in kwargs, "wrapper must pass creationflags to Popen"
    assert kwargs["creationflags"] == EXPECTED_WINDOWS_FLAG
    # CREATE_NO_WINDOW bit must be set.
    assert kwargs["creationflags"] & 0x08000000 == 0x08000000
    assert captured["exit_code"] == 0


def test_popen_uses_no_creationflags_off_windows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = _invoke(monkeypatch, tmp_path, "posix")

    kwargs = captured["kwargs"]
    assert kwargs.get("creationflags") == 0, "off Windows creationflags must be a no-op (0)"
    assert captured["exit_code"] == 0


def test_status_file_records_exit_code(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = _invoke(monkeypatch, tmp_path, "posix")

    status_file = captured["status_file"]
    assert isinstance(status_file, Path)
    assert status_file.read_text(encoding="utf-8").strip() == "0"


def test_windows_python_command_uses_sibling_pythonw_when_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    python_exe = tmp_path / "Scripts" / "python.exe"
    pythonw_exe = tmp_path / "Scripts" / "pythonw.exe"
    pythonw_exe.parent.mkdir()
    pythonw_exe.write_text("", encoding="utf-8")

    captured = _invoke(monkeypatch, tmp_path, "nt", [str(python_exe), "--version"])

    assert captured["cmd_args"][0] == str(pythonw_exe)


def test_windows_python_command_falls_back_when_pythonw_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    python_exe = tmp_path / "Scripts" / "python.exe"
    python_exe.parent.mkdir()

    captured = _invoke(monkeypatch, tmp_path, "nt", [str(python_exe), "--version"])

    assert captured["cmd_args"][0] == str(python_exe)


class _HangingProcess:
    """Stub whose wait() always times out, to exercise the lifetime-timeout path."""

    returncode = None
    pid = 4321

    def wait(self, timeout: float | None = None) -> int:
        raise subprocess.TimeoutExpired(cmd="child", timeout=timeout)

    def poll(self) -> None:
        return None


def test_worker_lifetime_timeout_records_124_and_terminates_tree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A worker exceeding the lifetime timeout is tree-terminated and the status file
    records the distinguishable timeout exit code.

    Spec linkage: GOV-FILE-BRIDGE-AUTHORITY-001 (reliability mandate -- workers must not
    hang forever) + DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (distinguishable timeout
    outcome). WI-4806 / GO at bridge/gtkb-run-with-status-worker-lifetime-timeout-002.md.
    """
    terminated: dict[str, object] = {}

    def fake_terminate(proc: object) -> None:
        terminated["proc"] = proc

    monkeypatch.setattr(run_with_status, "DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS", 1)
    monkeypatch.setattr(run_with_status, "_terminate_process_tree", fake_terminate)
    monkeypatch.setattr(run_with_status.subprocess, "Popen", lambda *a, **k: _HangingProcess())

    status_file = tmp_path / "status.txt"
    with pytest.raises(SystemExit) as exc_info:
        run_with_status.main([str(status_file), sys.executable, "-c", "import time; time.sleep(60)"])

    assert exc_info.value.code == run_with_status.TIMEOUT_EXIT_CODE
    assert status_file.read_text(encoding="utf-8").strip() == str(run_with_status.TIMEOUT_EXIT_CODE)
    assert "proc" in terminated, "the wrapped process tree must be terminated on timeout"


def _pid_alive(pid: int) -> bool:
    """True if a PID is currently running (Windows tasklist; no extra deps)."""
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
        capture_output=True,
        text=True,
    )
    return str(pid) in result.stdout


@pytest.mark.skipif(os.name != "nt", reason="tree-reaping path is Windows taskkill /T; POSIX uses killpg")
def test_terminate_process_tree_reaps_grandchild_on_windows(tmp_path: Path) -> None:
    """LO GO -002 residual-risk gate: a child that spawns a grandchild must have BOTH
    reaped, because Windows terminate()/kill() do not propagate to grandchildren."""
    gc_pidfile = tmp_path / "grandchild.pid"
    child_code = (
        "import subprocess, sys, time, pathlib; "
        "gc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']); "
        f"pathlib.Path(r'{gc_pidfile}').write_text(str(gc.pid)); "
        "time.sleep(120)"
    )
    proc = subprocess.Popen([sys.executable, "-c", child_code])
    try:
        deadline = time.time() + 15
        while not gc_pidfile.exists() and time.time() < deadline:
            time.sleep(0.1)
        assert gc_pidfile.exists(), "grandchild did not record its pid in time"
        gc_pid = int(gc_pidfile.read_text().strip())
        assert _pid_alive(proc.pid)
        assert _pid_alive(gc_pid)

        run_with_status._terminate_process_tree(proc)

        deadline = time.time() + 15
        while (_pid_alive(proc.pid) or _pid_alive(gc_pid)) and time.time() < deadline:
            time.sleep(0.2)
        assert not _pid_alive(proc.pid), "child process must be reaped"
        assert not _pid_alive(gc_pid), "grandchild process must be reaped (tree-kill)"
    finally:
        run_with_status._terminate_process_tree(proc)


# --- WI-4845: configurable worker-lifetime cap ----------------------------- #


def _wait_timeout_for(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, extra_args: list[str]) -> float | None:
    """Run main() with Popen stubbed and return the timeout passed to p.wait()."""
    recorded: dict[str, object] = {}

    class _TimeoutRecordingProcess:
        returncode = 0
        pid = 4321

        def wait(self, timeout: float | None = None) -> int:
            recorded["timeout"] = timeout
            return 0

        def poll(self) -> int:
            return 0

    monkeypatch.setattr(run_with_status.os, "name", "posix")
    monkeypatch.setattr(run_with_status.subprocess, "Popen", lambda *a, **k: _TimeoutRecordingProcess())

    status_file = tmp_path / "status.txt"
    with pytest.raises(SystemExit):
        run_with_status.main([*extra_args, str(status_file), sys.executable, "--version"])
    return recorded.get("timeout")  # type: ignore[return-value]


def test_lifetime_arg_sets_wait_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """SPEC-CENTRALIZED-DISPATCH-SERVICE-001: --lifetime N is applied as the wait timeout."""
    assert _wait_timeout_for(monkeypatch, tmp_path, ["--lifetime", "1800"]) == 1800


def test_default_lifetime_preserved_when_absent(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """DCL-DISPATCH-ENVELOPE-RULES-001: absent --lifetime keeps the bounded default (600)."""
    assert _wait_timeout_for(monkeypatch, tmp_path, []) == run_with_status.DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS


def test_lifetime_rejects_nonpositive(tmp_path: Path) -> None:
    """ADR-DISPATCHER-ARCHITECTURE-001: a non-positive or non-numeric --lifetime fails closed."""
    status_file = tmp_path / "status.txt"
    for bad in ("0", "-5", "abc"):
        with pytest.raises(SystemExit) as exc_info:
            run_with_status.main(["--lifetime", bad, str(status_file), sys.executable, "--version"])
        assert exc_info.value.code == 2, bad


def test_dispatch_lo_gets_review_lifetime() -> None:
    """SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (LO budget routing): the dispatcher routes the
    longer review lifetime to Loyal Opposition / verification dispatches and the bounded
    implementation lifetime to Prime Builder dispatches."""
    from scripts import cross_harness_bridge_trigger as trigger

    assert trigger.worker_lifetime_seconds("loyal-opposition") == 1800
    assert trigger.worker_lifetime_seconds("loyal-opposition") == trigger.LO_REVIEW_WORKER_LIFETIME_SECONDS
    assert trigger.worker_lifetime_seconds("prime-builder") == trigger.PB_IMPL_WORKER_LIFETIME_SECONDS
    assert trigger.worker_lifetime_seconds(None) is None
