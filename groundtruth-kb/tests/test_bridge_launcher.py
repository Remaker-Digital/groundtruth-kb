# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.launcher.

All bridge imports are inside the isolated_bridge fixture or test functions.
No top-level groundtruth_kb.bridge imports are allowed here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Any:
    """Redirect PRIME_BRIDGE_DB to tmp_path and purge cached bridge modules."""
    bridge_db = tmp_path / "bridge.db"
    monkeypatch.setenv("PRIME_BRIDGE_DB", str(bridge_db))
    for key in list(sys.modules):
        if key.startswith("groundtruth_kb.bridge"):
            del sys.modules[key]
    yield tmp_path
    for key in list(sys.modules):
        if key.startswith("groundtruth_kb.bridge"):
            del sys.modules[key]


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


def test_build_parser_returns_parser(isolated_bridge: Path) -> None:
    """build_parser() returns an ArgumentParser instance."""
    from groundtruth_kb.bridge.launcher import build_parser  # noqa: PLC0415

    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_has_agent_arg(isolated_bridge: Path) -> None:
    """build_parser() parser accepts --agent codex."""
    from groundtruth_kb.bridge.launcher import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args(["--agent", "codex"])
    assert args.agent == "codex"


def test_build_parser_has_json_output_arg(isolated_bridge: Path) -> None:
    """build_parser() parser accepts --json-output."""
    from groundtruth_kb.bridge.launcher import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args(["--json-output"])
    assert args.json_output is True


def test_build_parser_defaults(isolated_bridge: Path) -> None:
    """build_parser() sets expected defaults."""
    from groundtruth_kb.bridge.launcher import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args([])
    assert args.agent == "codex"
    assert args.cadence_minutes == 9
    assert args.timeout_seconds == 20


# ---------------------------------------------------------------------------
# main() tests — mock the heavy logic
# ---------------------------------------------------------------------------


def test_main_help_exits(isolated_bridge: Path) -> None:
    """main() with --help raises SystemExit(0)."""
    from groundtruth_kb.bridge.launcher import build_parser  # noqa: PLC0415

    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--help"])
    assert exc_info.value.code == 0


def test_main_with_healthy_worker_returns_0(isolated_bridge: Path) -> None:
    """main() when worker is already healthy prints and returns 0."""
    from groundtruth_kb.bridge import launcher  # noqa: PLC0415

    healthy_worker = {"pid": 1234, "agent": "codex", "source": "health", "state": "idle"}
    with (
        patch("sys.argv", ["launcher", "--agent", "codex"]),
        patch.object(launcher, "_discover_running_worker", return_value=healthy_worker),
        patch.object(launcher, "_consume_stdin_if_present"),
    ):
        result = launcher.main()
    assert result == 0


def test_main_with_no_worker_falls_back(isolated_bridge: Path, tmp_path: Path) -> None:
    """main() when no healthy worker attempts to start one (may fail in test env)."""
    from groundtruth_kb.bridge import launcher  # noqa: PLC0415

    exc = RuntimeError("resident worker did not publish healthy state")
    with (
        patch("sys.argv", ["launcher", "--agent", "codex", "--project-dir", str(tmp_path)]),
        patch.object(launcher, "_discover_running_worker", return_value=None),
        patch.object(launcher, "_scheduled_task_exists", return_value=False),
        patch.object(launcher, "_start_detached", side_effect=exc),
        patch.object(launcher, "_run_once_wake", return_value=(True, "done")),
        patch.object(launcher, "_consume_stdin_if_present"),
    ):
        result = launcher.main()
    # Either 0 (oneshot fallback succeeded) or the function handled the exception
    assert result == 0


def test_main_with_scheduled_task(isolated_bridge: Path, tmp_path: Path) -> None:
    """main() when scheduled task exists, starts it."""
    from groundtruth_kb.bridge import launcher  # noqa: PLC0415

    healthy_worker = {"pid": 9999, "agent": "codex", "source": "scheduled-task", "state": "idle"}
    call_count: list[int] = [0]

    def discover_side_effect(project_dir: Path, agent: str) -> Any:
        call_count[0] += 1
        if call_count[0] == 1:
            return None  # First call: not healthy
        return healthy_worker  # Second call: now healthy

    with (
        patch("sys.argv", ["launcher", "--agent", "codex", "--project-dir", str(tmp_path)]),
        patch.object(launcher, "_discover_running_worker", side_effect=discover_side_effect),
        patch.object(launcher, "_scheduled_task_exists", return_value=True),
        patch.object(launcher, "_try_start_scheduled_task", return_value=True),
        patch("time.sleep"),
        patch.object(launcher, "_consume_stdin_if_present"),
    ):
        result = launcher.main()
    assert result == 0


def test_main_scheduled_task_not_windows(isolated_bridge: Path) -> None:
    """_scheduled_task_exists returns False on non-Windows."""
    import os

    from groundtruth_kb.bridge import launcher  # noqa: PLC0415

    with patch.object(os, "name", "posix"):
        result = launcher._scheduled_task_exists("codex")  # type: ignore[attr-defined]
    assert result is False


def test_main_try_start_scheduled_task_not_windows(isolated_bridge: Path) -> None:
    """_try_start_scheduled_task returns False on non-Windows."""
    import os

    from groundtruth_kb.bridge import launcher  # noqa: PLC0415

    with patch.object(os, "name", "posix"):
        result = launcher._try_start_scheduled_task("codex")  # type: ignore[attr-defined]
    assert result is False
