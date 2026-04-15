# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.handshake.

All bridge imports are inside the isolated_bridge fixture or test functions.
No top-level groundtruth_kb.bridge imports are allowed here.
"""

from __future__ import annotations

import json
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
# run_handshake parameter validation
# ---------------------------------------------------------------------------


def test_run_handshake_timeout_too_low_raises(isolated_bridge: Path) -> None:
    """timeout_seconds < 1 raises ValueError."""
    from groundtruth_kb.bridge.handshake import run_handshake  # noqa: PLC0415

    with pytest.raises(ValueError, match="timeout_seconds"):
        run_handshake(timeout_seconds=0, poll_seconds=5)


def test_run_handshake_poll_too_low_raises(isolated_bridge: Path) -> None:
    """poll_seconds < 1 raises ValueError."""
    from groundtruth_kb.bridge.handshake import run_handshake  # noqa: PLC0415

    with pytest.raises(ValueError, match="poll_seconds"):
        run_handshake(timeout_seconds=10, poll_seconds=0)


# ---------------------------------------------------------------------------
# run_handshake behavior tests (mocked)
# ---------------------------------------------------------------------------


def test_run_handshake_send_message_fails_returns_1(isolated_bridge: Path) -> None:
    """When send_message fails, run_handshake returns 1."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    with (
        patch.object(handshake, "get_latest_notification_event_id", return_value={"last_event_id": 0}),
        patch.object(handshake, "_find_existing_pending_thread", return_value=None),
        patch.object(handshake, "send_message", return_value={"ok": False, "status": "failed"}),
    ):
        result = handshake.run_handshake(timeout_seconds=5, poll_seconds=1)
    assert result == 1


def test_run_handshake_uses_existing_thread_retry(isolated_bridge: Path) -> None:
    """When existing pending thread found, retries it then times out → returns 1."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    with (
        patch.object(handshake, "get_latest_notification_event_id", return_value={"last_event_id": 0}),
        patch.object(handshake, "_find_existing_pending_thread", return_value="existing-thread-id"),
        patch.object(handshake, "retry_pending_message", return_value={"ok": True, "retry_count": 1}),
        patch.object(handshake, "get_thread", return_value={"ok": True, "thread": {"thread_messages": []}}),
        patch.object(
            handshake,
            "wait_for_notifications",
            return_value={"notified": False, "last_event_id": 0, "items": []},
        ),
    ):
        calls: list[int] = [0]

        def fake_monotonic() -> float:
            calls[0] += 1
            # First call sets deadline far ahead; subsequent calls return past deadline
            if calls[0] == 1:
                return 0.0
            return 100.0

        with patch("time.monotonic", side_effect=fake_monotonic):
            result = handshake.run_handshake(timeout_seconds=1, poll_seconds=1)
    assert result == 1


def test_run_handshake_success_returns_0(isolated_bridge: Path) -> None:
    """When a prime reply is found immediately, run_handshake returns 0."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    prime_reply = {
        "id": "reply-1",
        "sender": "prime",
        "recipient": "codex",
        "status": "pending",
        "body": "Operating state: IDLE.",
        "subject": "Re: session start",
        "created_at": "2026-01-01T00:00:00Z",
    }
    thread_with_reply = {"thread": {"thread_messages": [prime_reply]}}

    with (
        patch.object(handshake, "get_latest_notification_event_id", return_value={"last_event_id": 0}),
        patch.object(handshake, "_find_existing_pending_thread", return_value=None),
        patch.object(
            handshake,
            "send_message",
            return_value={"ok": True, "id": "req-1", "status": "pending"},
        ),
        patch.object(handshake, "get_thread", return_value=thread_with_reply),
        patch.object(handshake, "resolve_message", return_value={"ok": True}),
    ):
        result = handshake.run_handshake(timeout_seconds=10, poll_seconds=1)
    assert result == 0


def test_run_handshake_json_output(isolated_bridge: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With json_output=True, output is valid JSON."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    prime_reply = {
        "id": "reply-1",
        "sender": "prime",
        "recipient": "codex",
        "status": "pending",
        "body": "State: IDLE",
        "subject": "Re: session-start",
        "created_at": "2026-01-01T00:00:00Z",
    }
    thread_with_reply = {"thread": {"thread_messages": [prime_reply]}}

    with (
        patch.object(handshake, "get_latest_notification_event_id", return_value={"last_event_id": 0}),
        patch.object(handshake, "_find_existing_pending_thread", return_value=None),
        patch.object(
            handshake,
            "send_message",
            return_value={"ok": True, "id": "req-1", "status": "pending"},
        ),
        patch.object(handshake, "get_thread", return_value=thread_with_reply),
        patch.object(handshake, "resolve_message", return_value={"ok": True}),
    ):
        result = handshake.run_handshake(timeout_seconds=10, poll_seconds=1, json_output=True)
    assert result == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["ok"] is True


def test_run_handshake_timeout_returns_1(isolated_bridge: Path) -> None:
    """When no reply arrives before timeout, returns 1."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    with (
        patch.object(handshake, "get_latest_notification_event_id", return_value={"last_event_id": 0}),
        patch.object(handshake, "_find_existing_pending_thread", return_value=None),
        patch.object(
            handshake,
            "send_message",
            return_value={"ok": True, "id": "req-1", "status": "pending"},
        ),
        patch.object(handshake, "get_thread", return_value={"ok": True, "thread": {"thread_messages": []}}),
        patch.object(
            handshake,
            "wait_for_notifications",
            return_value={"notified": False, "last_event_id": 0, "items": []},
        ),
    ):
        counter: list[int] = [0]

        def fast_monotonic() -> float:
            counter[0] += 1
            # Return 0 first (deadline = timeout_seconds), then return past deadline
            if counter[0] <= 1:
                return 0.0
            return 50.0

        with patch("time.monotonic", side_effect=fast_monotonic):
            result = handshake.run_handshake(timeout_seconds=5, poll_seconds=1)
    assert result == 1


# ---------------------------------------------------------------------------
# main() argument parsing
# ---------------------------------------------------------------------------


def test_main_with_zero_timeout_raises_systemexit(isolated_bridge: Path) -> None:
    """main() with --timeout-seconds 0 raises SystemExit."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    with patch("sys.argv", ["handshake", "--timeout-seconds", "0"]), pytest.raises(SystemExit):
        handshake.main()


def test_main_with_zero_poll_raises_systemexit(isolated_bridge: Path) -> None:
    """main() with --poll-seconds 0 raises SystemExit."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    with patch("sys.argv", ["handshake", "--poll-seconds", "0"]), pytest.raises(SystemExit):
        handshake.main()


def test_main_calls_run_handshake(isolated_bridge: Path) -> None:
    """main() with valid args calls run_handshake."""
    from groundtruth_kb.bridge import handshake  # noqa: PLC0415

    with (
        patch("sys.argv", ["handshake", "--timeout-seconds", "5", "--poll-seconds", "1"]),
        patch.object(handshake, "run_handshake", return_value=0) as mock_run,
    ):
        result = handshake.main()
    assert result == 0
    mock_run.assert_called_once()
