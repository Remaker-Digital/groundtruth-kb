"""Read-only poll helper for bridge thread completion (WI-4864)."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any

TERMINAL_SUCCESS: frozenset[str] = frozenset({"VERIFIED"})
TERMINAL_STOP: frozenset[str] = frozenset({"WITHDRAWN", "DEFERRED"})


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


def evaluate_thread_state(
    payload: dict[str, Any] | None,
    *,
    success: frozenset[str] = TERMINAL_SUCCESS,
    stop: frozenset[str] = TERMINAL_STOP,
) -> dict[str, Any]:
    """Classify a show_thread payload into a structured outcome dict.

    Returns keys: outcome, latest_status, latest_version, latest_path, terminal.
    """
    if payload is None:
        return {
            "outcome": "absent",
            "latest_status": None,
            "latest_version": None,
            "latest_path": None,
            "terminal": False,
        }
    raw_status = payload.get("latest_status") or ""
    latest_status = raw_status.upper() if raw_status else ""
    chain = payload.get("version_chain") or []
    latest_version = chain[0]["version"] if chain else None
    latest_path = payload.get("latest_path")
    if latest_status in success:
        return {
            "outcome": "verified",
            "latest_status": latest_status,
            "latest_version": latest_version,
            "latest_path": latest_path,
            "terminal": True,
        }
    if latest_status in stop:
        return {
            "outcome": "stopped",
            "latest_status": latest_status,
            "latest_version": latest_version,
            "latest_path": latest_path,
            "terminal": True,
        }
    return {
        "outcome": "pending",
        "latest_status": latest_status,
        "latest_version": latest_version,
        "latest_path": latest_path,
        "terminal": False,
    }


def _default_git_runner(
    args: list[str],
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, **_no_window_subprocess_kwargs())


def verdict_committed(
    project_root: Path,
    latest_path: str | None,
    *,
    git_runner: Any = None,
) -> bool:
    """Return True when the latest verdict file is tracked AND committed in git."""
    if not latest_path:
        return False
    runner = git_runner if git_runner is not None else _default_git_runner
    tracked = runner(["git", "ls-files", "--error-unmatch", latest_path], project_root)
    if tracked.returncode != 0:
        return False
    logged = runner(["git", "log", "-1", "--", latest_path], project_root)
    return logged.returncode == 0 and bool(logged.stdout.strip())


def wait_for_thread(
    project_root: Path,
    slug: str,
    *,
    until: str = "verified",
    timeout_seconds: float = 3600.0,
    poll_interval_seconds: float = 30.0,
    require_commit: bool = True,
    reader: Any = None,
    now: Any = None,
    sleep: Any = None,
    commit_checker: Any = None,
) -> dict[str, Any]:
    """Poll a bridge thread until terminal or timeout.

    Returns a dict with: outcome, latest_status, latest_version,
    committed, elapsed_seconds, polls.

    Exit signals:
    - "verified": thread reached VERIFIED and (if require_commit) finalize committed.
    - "stopped": thread reached a non-success terminal (WITHDRAWN, DEFERRED).
    - "timeout": deadline elapsed before a terminal+committed state.
    """
    from groundtruth_kb.bridge.read_commands import show_thread as _show_thread

    _reader = reader if reader is not None else _show_thread
    _now = now if now is not None else time.monotonic
    _sleep = sleep if sleep is not None else time.sleep
    _commit_checker = commit_checker if commit_checker is not None else verdict_committed

    start = _now()
    polls = 0

    while True:
        payload = _reader(project_root, slug)
        polls += 1
        state = evaluate_thread_state(payload)
        elapsed = _now() - start

        if state["terminal"]:
            if state["outcome"] == "verified":
                if require_commit:
                    committed = _commit_checker(project_root, state["latest_path"])
                    if committed:
                        return {
                            "outcome": "verified",
                            "latest_status": state["latest_status"],
                            "latest_version": state["latest_version"],
                            "committed": True,
                            "elapsed_seconds": elapsed,
                            "polls": polls,
                        }
                    # VERIFIED but finalize commit not yet landed — keep polling
                    if elapsed >= timeout_seconds:
                        return {
                            "outcome": "timeout",
                            "latest_status": state["latest_status"],
                            "latest_version": state["latest_version"],
                            "committed": False,
                            "elapsed_seconds": elapsed,
                            "polls": polls,
                        }
                    _sleep(poll_interval_seconds)
                    continue
                return {
                    "outcome": "verified",
                    "latest_status": state["latest_status"],
                    "latest_version": state["latest_version"],
                    "committed": False,
                    "elapsed_seconds": elapsed,
                    "polls": polls,
                }
            # stopped — WITHDRAWN or DEFERRED
            return {
                "outcome": state["outcome"],
                "latest_status": state["latest_status"],
                "latest_version": state["latest_version"],
                "committed": False,
                "elapsed_seconds": elapsed,
                "polls": polls,
            }

        # Not terminal yet — check timeout before sleeping
        if elapsed >= timeout_seconds:
            return {
                "outcome": "timeout",
                "latest_status": state["latest_status"],
                "latest_version": state["latest_version"],
                "committed": False,
                "elapsed_seconds": elapsed,
                "polls": polls,
            }
        _sleep(poll_interval_seconds)
