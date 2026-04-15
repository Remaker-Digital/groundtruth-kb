# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.poller.

All bridge imports are inside the isolated_bridge fixture or test functions.
No top-level groundtruth_kb.bridge imports are allowed here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

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
    """build_parser() returns an ArgumentParser."""
    from groundtruth_kb.bridge.poller import build_parser  # noqa: PLC0415

    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_required_agent(isolated_bridge: Path) -> None:
    """build_parser() requires --agent."""
    from groundtruth_kb.bridge.poller import build_parser  # noqa: PLC0415

    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])  # missing required --agent


def test_build_parser_accepts_codex(isolated_bridge: Path) -> None:
    """build_parser() accepts --agent codex."""
    from groundtruth_kb.bridge.poller import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args(["--agent", "codex"])
    assert args.agent == "codex"


def test_build_parser_once_flag(isolated_bridge: Path) -> None:
    """build_parser() accepts --once flag."""
    from groundtruth_kb.bridge.poller import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args(["--agent", "prime", "--once"])
    assert args.once is True


def test_build_parser_auto_actions_flag(isolated_bridge: Path) -> None:
    """build_parser() accepts --auto-actions flag."""
    from groundtruth_kb.bridge.poller import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args(["--agent", "codex", "--auto-actions"])
    assert args.auto_actions is True


# ---------------------------------------------------------------------------
# _FileLock
# ---------------------------------------------------------------------------


def test_file_lock_acquires_and_releases(isolated_bridge: Path, tmp_path: Path) -> None:
    """_FileLock context manager acquires and releases the lock file."""
    from groundtruth_kb.bridge.poller import _FileLock  # noqa: PLC0415

    lock_path = tmp_path / ".test-poller.lock"
    with _FileLock(lock_path) as lock:
        assert lock is not None
        assert lock_path.exists()
    # After exit, no exception should have been raised


def test_file_lock_busy_raises(isolated_bridge: Path, tmp_path: Path) -> None:
    """_FileLock raises RuntimeError when lock is already held."""
    from groundtruth_kb.bridge.poller import _FileLock  # noqa: PLC0415

    lock_path = tmp_path / ".test-poller-busy.lock"
    with _FileLock(lock_path), pytest.raises((RuntimeError, OSError)), _FileLock(lock_path):
        pass


# ---------------------------------------------------------------------------
# run() — once mode
# ---------------------------------------------------------------------------


def test_run_invalid_agent_returns_1(isolated_bridge: Path, tmp_path: Path) -> None:
    """run() with invalid agent returns 1."""
    from groundtruth_kb.bridge.poller import build_parser, run  # noqa: PLC0415

    parser = build_parser()
    # We must parse a valid agent then override it (argparse validates choices)
    args = parser.parse_args(["--agent", "codex", "--once"])
    args.agent = "invalid"  # Bypass argparse choices
    result = run(args, project_dir=tmp_path)
    assert result == 1


def test_run_once_with_no_notifications(isolated_bridge: Path, tmp_path: Path) -> None:
    """run() in --once mode with no notifications returns 0."""
    from groundtruth_kb.bridge import poller  # noqa: PLC0415

    args = poller.build_parser().parse_args(["--agent", "codex", "--once"])

    mock_bridge = MagicMock()
    mock_bridge.list_notifications.return_value = {"count": 0, "last_event_id": 0, "items": []}
    mock_bridge.list_inbox.return_value = {"count": 0, "items": []}
    mock_bridge.wait_for_notifications.return_value = {"notified": False, "last_event_id": 0, "items": []}
    mock_bridge.DB_PATH = tmp_path / "bridge.db"

    with (
        patch("groundtruth_kb.bridge.poller.resident_worker_should_defer", return_value=(False, "missing-health")),
        patch.object(sys, "modules", {**sys.modules, "groundtruth_kb.bridge.runtime": mock_bridge}),
    ):
        result = poller.run(args, project_dir=tmp_path)
    assert result == 0


def test_run_once_with_notification_processes(isolated_bridge: Path, tmp_path: Path) -> None:
    """run() in --once mode with notifications processes them and returns 0."""
    from groundtruth_kb.bridge import poller  # noqa: PLC0415

    args = poller.build_parser().parse_args(["--agent", "codex", "--once"])

    event = {
        "event_id": 1,
        "agent": "codex",
        "event_type": "message.new",
        "message_id": "msg-1",
        "subject": "Test",
        "details": {"sender": "prime", "recipient": "codex"},
    }
    mock_bridge = MagicMock()
    mock_bridge.list_notifications.return_value = {"count": 1, "last_event_id": 1, "items": [event]}
    mock_bridge.list_inbox.return_value = {"count": 0, "items": []}
    mock_bridge.DB_PATH = tmp_path / "bridge.db"

    with (
        patch("groundtruth_kb.bridge.poller.resident_worker_should_defer", return_value=(False, "missing-health")),
        patch.object(sys, "modules", {**sys.modules, "groundtruth_kb.bridge.runtime": mock_bridge}),
    ):
        result = poller.run(args, project_dir=tmp_path)
    assert result == 0


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_calls_run_and_returns(isolated_bridge: Path, tmp_path: Path) -> None:
    """main() calls run() and returns its result."""
    from groundtruth_kb.bridge import poller  # noqa: PLC0415

    with (
        patch("sys.argv", ["poller", "--agent", "codex", "--once", "--project-dir", str(tmp_path)]),
        patch.object(poller, "run", return_value=0) as mock_run,
        patch.object(poller, "_consume_stdin_if_present"),
    ):
        result = poller.main()
    assert result == 0
    mock_run.assert_called_once()
