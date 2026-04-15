# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.worker public functions.

All bridge imports are inside the isolated_bridge fixture or test functions.
No top-level groundtruth_kb.bridge imports are allowed here.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
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


def _write_health_file(hooks_dir: Path, agent: str, **fields: Any) -> None:
    """Helper: write a health JSON file for a given agent."""
    hooks_dir.mkdir(parents=True, exist_ok=True)
    doc = {"agent": agent, "status": "idle", "pid": 1234, "updated_at": datetime.now(UTC).isoformat(), **fields}
    (hooks_dir / f".bridge-worker-{agent}-health.json").write_text(json.dumps(doc), encoding="utf-8")


# ---------------------------------------------------------------------------
# resident_worker_is_healthy
# ---------------------------------------------------------------------------


def test_resident_worker_is_healthy_missing_file(isolated_bridge: Path, tmp_path: Path) -> None:
    """No health file → (False, 'missing-health')."""
    from groundtruth_kb.bridge.worker import resident_worker_is_healthy  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    healthy, state = resident_worker_is_healthy("codex", hooks_dir=hooks_dir)
    assert healthy is False
    assert state == "missing-health"


def test_resident_worker_is_healthy_idle_recent(isolated_bridge: Path, tmp_path: Path) -> None:
    """Status=idle with recent timestamp → (True, 'idle')."""
    from groundtruth_kb.bridge.worker import resident_worker_is_healthy  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    _write_health_file(hooks_dir, "codex", status="idle", updated_at=datetime.now(UTC).isoformat())
    healthy, state = resident_worker_is_healthy("codex", hooks_dir=hooks_dir)
    assert healthy is True
    assert state == "idle"


def test_resident_worker_is_healthy_idle_stale(isolated_bridge: Path, tmp_path: Path) -> None:
    """Status=idle with stale timestamp → (False, 'idle-stale')."""
    from groundtruth_kb.bridge.worker import HEALTHY_IDLE_SECONDS, resident_worker_is_healthy  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    stale_time = (datetime.now(UTC) - timedelta(seconds=HEALTHY_IDLE_SECONDS + 10)).isoformat()
    _write_health_file(hooks_dir, "codex", status="idle", updated_at=stale_time)
    healthy, state = resident_worker_is_healthy("codex", hooks_dir=hooks_dir)
    assert healthy is False
    assert state == "idle-stale"


def test_resident_worker_is_healthy_busy_recent(isolated_bridge: Path, tmp_path: Path) -> None:
    """Status=busy with recent dispatch_started_at → (True, 'busy')."""
    from groundtruth_kb.bridge.worker import resident_worker_is_healthy  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    _write_health_file(
        hooks_dir,
        "codex",
        status="busy",
        updated_at=datetime.now(UTC).isoformat(),
        dispatch_started_at=datetime.now(UTC).isoformat(),
        dispatch_timeout_seconds=900,
    )
    healthy, state = resident_worker_is_healthy("codex", hooks_dir=hooks_dir)
    assert healthy is True
    assert state == "busy"


def test_resident_worker_is_healthy_requires_hooks_or_project_dir(isolated_bridge: Path, tmp_path: Path) -> None:
    """Calling with neither hooks_dir nor project_dir raises ValueError."""
    from groundtruth_kb.bridge.worker import resident_worker_is_healthy  # noqa: PLC0415

    with pytest.raises(ValueError, match="hooks_dir"):
        resident_worker_is_healthy("codex")


# ---------------------------------------------------------------------------
# resident_worker_health_snapshot
# ---------------------------------------------------------------------------


def test_resident_worker_health_snapshot_valid_file(isolated_bridge: Path, tmp_path: Path) -> None:
    """Returns dict when health file exists and is valid JSON."""
    from groundtruth_kb.bridge.worker import resident_worker_health_snapshot  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    _write_health_file(hooks_dir, "prime", status="idle")
    result = resident_worker_health_snapshot("prime", hooks_dir=hooks_dir)
    assert isinstance(result, dict)
    assert result["agent"] == "prime"


def test_resident_worker_health_snapshot_missing_file(isolated_bridge: Path, tmp_path: Path) -> None:
    """Returns None when health file doesn't exist."""
    from groundtruth_kb.bridge.worker import resident_worker_health_snapshot  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    result = resident_worker_health_snapshot("prime", hooks_dir=hooks_dir)
    assert result is None


# ---------------------------------------------------------------------------
# resident_worker_should_defer
# ---------------------------------------------------------------------------


def test_resident_worker_should_defer_unhealthy(isolated_bridge: Path, tmp_path: Path) -> None:
    """Unhealthy worker → (False, state)."""
    from groundtruth_kb.bridge.worker import resident_worker_should_defer  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    # No health file → unhealthy
    defer, state = resident_worker_should_defer("codex", [], hooks_dir=hooks_dir)
    assert defer is False


def test_resident_worker_should_defer_idle(isolated_bridge: Path, tmp_path: Path) -> None:
    """Healthy idle worker → (True, 'idle')."""
    from groundtruth_kb.bridge.worker import resident_worker_should_defer  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    _write_health_file(hooks_dir, "codex", status="idle", updated_at=datetime.now(UTC).isoformat())
    defer, state = resident_worker_should_defer("codex", [], hooks_dir=hooks_dir)
    assert defer is True
    assert state == "idle"


def test_resident_worker_should_defer_busy_same_targets(isolated_bridge: Path, tmp_path: Path) -> None:
    """Healthy busy worker with same targets → (True, 'busy-same-targets')."""
    from groundtruth_kb.bridge.worker import resident_worker_should_defer  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    _write_health_file(
        hooks_dir,
        "codex",
        status="busy",
        updated_at=datetime.now(UTC).isoformat(),
        dispatch_started_at=datetime.now(UTC).isoformat(),
        dispatch_timeout_seconds=900,
        active_message_ids=["msg-1", "msg-2"],
    )
    defer, state = resident_worker_should_defer("codex", ["msg-1"], hooks_dir=hooks_dir)
    assert defer is True
    assert state == "busy-same-targets"


def test_resident_worker_should_defer_busy_other_targets(isolated_bridge: Path, tmp_path: Path) -> None:
    """Healthy busy worker with different targets → (False, 'busy-other-targets')."""
    from groundtruth_kb.bridge.worker import resident_worker_should_defer  # noqa: PLC0415

    hooks_dir = tmp_path / ".claude" / "hooks"
    _write_health_file(
        hooks_dir,
        "codex",
        status="busy",
        updated_at=datetime.now(UTC).isoformat(),
        dispatch_started_at=datetime.now(UTC).isoformat(),
        dispatch_timeout_seconds=900,
        active_message_ids=["msg-existing"],
    )
    defer, state = resident_worker_should_defer("codex", ["msg-different"], hooks_dir=hooks_dir)
    assert defer is False
    assert state == "busy-other-targets"


# ---------------------------------------------------------------------------
# _FileLock
# ---------------------------------------------------------------------------


def test_file_lock_acquires_and_releases(isolated_bridge: Path, tmp_path: Path) -> None:
    """_FileLock context manager acquires and releases without error."""
    from groundtruth_kb.bridge.worker import _FileLock  # noqa: PLC0415

    lock_path = tmp_path / ".claude" / "hooks" / ".test-worker.lock"
    with _FileLock(lock_path) as lock:
        assert lock is not None
        assert lock_path.exists()


def test_file_lock_busy_raises(isolated_bridge: Path, tmp_path: Path) -> None:
    """_FileLock raises when already held."""
    from groundtruth_kb.bridge.worker import _FileLock  # noqa: PLC0415

    lock_path = tmp_path / ".claude" / "hooks" / ".test-worker-busy.lock"
    with _FileLock(lock_path), pytest.raises((OSError, RuntimeError)), _FileLock(lock_path):
        pass


# ---------------------------------------------------------------------------
# build_parser
# ---------------------------------------------------------------------------


def test_build_parser_returns_parser(isolated_bridge: Path) -> None:
    """build_parser() returns an ArgumentParser."""
    from groundtruth_kb.bridge.worker import build_parser  # noqa: PLC0415

    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_build_parser_defaults(isolated_bridge: Path) -> None:
    """build_parser() sets expected defaults."""
    from groundtruth_kb.bridge.worker import build_parser  # noqa: PLC0415

    parser = build_parser()
    args = parser.parse_args([])
    assert args.agent == "codex"
    assert args.timeout_seconds == 20
    assert args.exec_timeout_seconds == 900


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def test_main_calls_run(isolated_bridge: Path, tmp_path: Path) -> None:
    """main() parses args and calls run()."""
    from groundtruth_kb.bridge import worker  # noqa: PLC0415

    with (
        patch("sys.argv", ["worker", "--agent", "codex"]),
        patch.object(worker, "run", return_value=0) as mock_run,
    ):
        result = worker.main()
    assert result == 0
    mock_run.assert_called_once()
