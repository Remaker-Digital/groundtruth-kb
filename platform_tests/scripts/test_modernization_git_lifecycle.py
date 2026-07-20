"""Frozen black-box acceptance for the modernization Git lifecycle service."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from scripts.run_with_status import _terminate_process_tree
from scripts.windows_subprocess import hidden_process_popen_kwargs

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check_modernization_git_lifecycle.py"
EXPECTED = {f"GIT-LIFECYCLE-A{i}" for i in range(1, 27)}
CHILD_TIMEOUT_SECONDS = 600
WRAPPER_TIMEOUT_SECONDS = 750
ACTIVITY_TIMEOUT_SECONDS = 900
MAX_DIAGNOSTIC_CHARS = 4_000


def _bounded_diagnostic(value: str | bytes | None) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return (value or "")[-MAX_DIAGNOSTIC_CHARS:]


def _run_checker(
    *,
    popen_factory: Callable[..., Any] = subprocess.Popen,
    terminate_process_tree: Callable[[Any], None] = _terminate_process_tree,
) -> subprocess.CompletedProcess[str]:
    popen_kwargs = hidden_process_popen_kwargs(new_process_group=True)
    if os.name != "nt":
        popen_kwargs["start_new_session"] = True
    process = popen_factory(
        [sys.executable, str(CHECKER), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **popen_kwargs,
    )
    try:
        stdout, stderr = process.communicate(timeout=CHILD_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(process)
        pytest.fail(
            f"Git lifecycle checker exceeded {CHILD_TIMEOUT_SECONDS} seconds; "
            f"terminated process tree (pid={process.pid}).\n"
            f"stdout:\n{_bounded_diagnostic(exc.stdout)}\n"
            f"stderr:\n{_bounded_diagnostic(exc.stderr)}"
        )
    return subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)


@pytest.mark.timeout(WRAPPER_TIMEOUT_SECONDS)
def test_frozen_modernization_git_lifecycle_contract() -> None:
    assert CHILD_TIMEOUT_SECONDS < WRAPPER_TIMEOUT_SECONDS < ACTIVITY_TIMEOUT_SECONDS
    result = _run_checker()
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assertions = {item["id"]: item for item in report["assertions"]}
    assert report["capability"] == "CAP-GIT-LIFECYCLE"
    assert report["status"] == "PASS"
    assert set(assertions) == EXPECTED
    assert all(item["status"] == "PASS" and item["evidence"] for item in assertions.values())


def test_checker_timeout_terminates_process_tree_and_fails() -> None:
    class HungChecker:
        args = [sys.executable, str(CHECKER), "--json"]
        pid = 4242
        returncode = None

        def communicate(self, *, timeout: int) -> tuple[str, str]:
            raise subprocess.TimeoutExpired(
                self.args,
                timeout,
                output="partial stdout",
                stderr="partial stderr",
            )

    process = HungChecker()
    popen_calls: list[dict[str, Any]] = []
    terminated: list[Any] = []

    def popen_factory(*_args: object, **kwargs: Any) -> HungChecker:
        popen_calls.append(kwargs)
        return process

    with pytest.raises(
        pytest.fail.Exception,
        match=f"exceeded {CHILD_TIMEOUT_SECONDS} seconds",
    ):
        _run_checker(
            popen_factory=popen_factory,
            terminate_process_tree=terminated.append,
        )

    assert terminated == [process]
    assert popen_calls[0]["stdout"] is subprocess.PIPE
    assert popen_calls[0]["stderr"] is subprocess.PIPE
    if os.name == "nt":
        creationflags = int(popen_calls[0]["creationflags"])
        assert creationflags & subprocess.CREATE_NO_WINDOW
        assert creationflags & subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        assert popen_calls[0]["start_new_session"] is True
