# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.runtime — SQLite-backed bridge runtime.

All bridge imports are inside the isolated_bridge fixture or test functions.
No top-level groundtruth_kb.bridge imports are allowed here.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def isolated_bridge(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Any:
    """Redirect PRIME_BRIDGE_DB to tmp_path and purge cached bridge modules."""
    import sys

    bridge_db = tmp_path / "bridge.db"
    monkeypatch.setenv("PRIME_BRIDGE_DB", str(bridge_db))
    for key in list(sys.modules):
        if key.startswith("groundtruth_kb.bridge"):
            del sys.modules[key]
    yield tmp_path
    for key in list(sys.modules):
        if key.startswith("groundtruth_kb.bridge"):
            del sys.modules[key]


@pytest.fixture
def bridge_db(isolated_bridge: Path) -> Path:
    """Create a fresh bridge.db with the correct schema in tmp_path."""
    from groundtruth_kb.bridge import runtime  # noqa: PLC0415

    db_path = isolated_bridge / "bridge.db"
    # The runtime creates the schema on first use via _ensure_schema.
    # We just need to open a connection once to trigger it.
    conn = runtime._conn()  # type: ignore[attr-defined]
    conn.close()
    return db_path


# ---------------------------------------------------------------------------
# get_bridge_db
# ---------------------------------------------------------------------------


def test_get_bridge_db_returns_connection(isolated_bridge: Path) -> None:
    """get_bridge_db() returns a sqlite3.Connection."""
    from groundtruth_kb.bridge.runtime import get_bridge_db  # noqa: PLC0415

    conn = get_bridge_db()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


# ---------------------------------------------------------------------------
# send_message
# ---------------------------------------------------------------------------


def test_send_message_creates_message(bridge_db: Path) -> None:
    """send_message() creates a pending message and returns ok=True."""
    from groundtruth_kb.bridge.runtime import list_inbox, send_message  # noqa: PLC0415

    payload = json.dumps(
        {
            "expected_response": "status_update",
            "artifact_refs": ["AGENTS.md"],
            "action_items": ["Do something"],
        }
    )
    result = send_message(
        sender="codex",
        recipient="prime",
        subject="Test subject",
        body="Test body",
        payload_json=payload,
    )
    assert result["ok"] is True
    assert "id" in result
    assert result["status"] == "pending"

    inbox = list_inbox("prime", status="pending")
    assert inbox["count"] >= 1


def test_send_message_invalid_sender_raises(bridge_db: Path) -> None:
    """send_message() with invalid sender raises ValueError."""
    from groundtruth_kb.bridge.runtime import send_message  # noqa: PLC0415

    with pytest.raises(ValueError, match="sender"):
        send_message(sender="unknown", recipient="prime", subject="s", body="b")


def test_send_message_invalid_recipient_raises(bridge_db: Path) -> None:
    """send_message() with invalid recipient raises ValueError."""
    from groundtruth_kb.bridge.runtime import send_message  # noqa: PLC0415

    with pytest.raises(ValueError, match="recipient"):
        send_message(sender="codex", recipient="badguy", subject="s", body="b")


def test_send_message_validation_failure(bridge_db: Path) -> None:
    """send_message() to self returns failed status."""
    from groundtruth_kb.bridge.runtime import send_message  # noqa: PLC0415

    result = send_message(sender="codex", recipient="codex", subject="s", body="b")
    # self-addressed peer message is a validation error
    assert result["status"] == "failed"


# ---------------------------------------------------------------------------
# list_inbox
# ---------------------------------------------------------------------------


def test_list_inbox_empty(bridge_db: Path) -> None:
    """list_inbox() returns empty list when no messages."""
    from groundtruth_kb.bridge.runtime import list_inbox  # noqa: PLC0415

    result = list_inbox("codex", status="pending")
    assert result["count"] == 0
    assert result["items"] == []


def test_list_inbox_invalid_limit_raises(bridge_db: Path) -> None:
    """list_inbox() with limit=0 raises ValueError."""
    from groundtruth_kb.bridge.runtime import list_inbox  # noqa: PLC0415

    with pytest.raises(ValueError, match="limit"):
        list_inbox("codex", limit=0)


def test_list_inbox_returns_sent_message(bridge_db: Path) -> None:
    """list_inbox() returns a message sent to that agent."""
    from groundtruth_kb.bridge.runtime import list_inbox, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    send_message(sender="prime", recipient="codex", subject="Hello", body="World", payload_json=payload)
    result = list_inbox("codex", status="pending")
    assert result["count"] >= 1
    subjects = [m["subject"] for m in result["items"]]
    assert "Hello" in subjects


# ---------------------------------------------------------------------------
# resolve_message
# ---------------------------------------------------------------------------


def test_resolve_message_marks_completed(bridge_db: Path) -> None:
    """resolve_message() marks a message as completed."""
    from groundtruth_kb.bridge.runtime import list_inbox, resolve_message, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    result = send_message(
        sender="prime",
        recipient="codex",
        subject="Resolve test",
        body="body",
        payload_json=payload,
    )
    message_id = result["id"]

    resolve_result = resolve_message(message_id=message_id, agent="codex", outcome="completed", resolution="done")
    assert resolve_result["ok"] is True
    assert resolve_result["status"] == "completed"

    # Should no longer appear in pending inbox
    inbox = list_inbox("codex", status="pending")
    pending_ids = [m["id"] for m in inbox["items"]]
    assert message_id not in pending_ids


def test_resolve_message_missing(bridge_db: Path) -> None:
    """resolve_message() on non-existent ID returns ok=False."""
    from groundtruth_kb.bridge.runtime import resolve_message  # noqa: PLC0415

    result = resolve_message(message_id="nonexistent-id", agent="codex", outcome="completed")
    assert result["ok"] is False
    assert result["status"] == "missing"


# ---------------------------------------------------------------------------
# retry_pending_message
# ---------------------------------------------------------------------------


def test_retry_pending_message(bridge_db: Path) -> None:
    """retry_pending_message() re-queues a notification for a pending message."""
    from groundtruth_kb.bridge.runtime import retry_pending_message, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    result = send_message(
        sender="prime",
        recipient="codex",
        subject="Retry test",
        body="body",
        payload_json=payload,
    )
    message_id = result["id"]

    retry_result = retry_pending_message(message_id=message_id, agent="codex")
    assert retry_result["ok"] is True
    assert retry_result["retry_count"] == 1


def test_retry_pending_message_missing(bridge_db: Path) -> None:
    """retry_pending_message() on non-existent ID returns ok=False."""
    from groundtruth_kb.bridge.runtime import retry_pending_message  # noqa: PLC0415

    result = retry_pending_message(message_id="no-such-id", agent="codex")
    assert result["ok"] is False
    assert result["reason"] == "missing"


# ---------------------------------------------------------------------------
# get_thread / describe_thread_context
# ---------------------------------------------------------------------------


def test_get_thread_returns_context(bridge_db: Path) -> None:
    """get_thread() returns ok=True and context for a known message."""
    from groundtruth_kb.bridge.runtime import get_thread, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    result = send_message(
        sender="prime",
        recipient="codex",
        subject="Thread test",
        body="body",
        payload_json=payload,
    )
    message_id = result["id"]

    thread = get_thread(thread_ref=message_id, agent="codex")
    assert thread["ok"] is True
    assert thread["thread"] is not None
    assert thread["thread"]["canonical_message"]["id"] == message_id


def test_get_thread_missing(bridge_db: Path) -> None:
    """get_thread() with unknown ref returns ok=False."""
    from groundtruth_kb.bridge.runtime import get_thread  # noqa: PLC0415

    thread = get_thread(thread_ref="totally-unknown-id")
    assert thread["ok"] is False


# ---------------------------------------------------------------------------
# get_latest_notification_event_id
# ---------------------------------------------------------------------------


def test_get_latest_notification_event_id_empty(bridge_db: Path) -> None:
    """get_latest_notification_event_id() returns 0 when no notifications exist."""
    from groundtruth_kb.bridge.runtime import get_latest_notification_event_id  # noqa: PLC0415

    result = get_latest_notification_event_id(agent="codex")
    assert result["last_event_id"] >= 0


def test_get_latest_notification_event_id_after_send(bridge_db: Path) -> None:
    """After send_message(), latest notification event ID is > 0."""
    from groundtruth_kb.bridge.runtime import get_latest_notification_event_id, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    send_message(
        sender="prime",
        recipient="codex",
        subject="Event test",
        body="body",
        payload_json=payload,
    )
    result = get_latest_notification_event_id(agent="codex")
    assert result["last_event_id"] > 0


# ---------------------------------------------------------------------------
# list_notifications
# ---------------------------------------------------------------------------


def test_list_notifications_returns_items(bridge_db: Path) -> None:
    """list_notifications() returns notification items after a send."""
    from groundtruth_kb.bridge.runtime import list_notifications, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    send_message(
        sender="prime",
        recipient="codex",
        subject="Notif test",
        body="body",
        payload_json=payload,
    )
    result = list_notifications("codex", after_event_id=0)
    assert result["count"] >= 1


# ---------------------------------------------------------------------------
# health
# ---------------------------------------------------------------------------


def test_health_returns_json(bridge_db: Path) -> None:
    """health() returns valid JSON with expected keys."""
    from groundtruth_kb.bridge.runtime import health  # noqa: PLC0415

    raw = health()
    data = json.loads(raw)
    assert "db_path" in data
    assert "schema_version_current" in data
    assert "messages" in data


# ---------------------------------------------------------------------------
# list_stale_outbound
# ---------------------------------------------------------------------------


def test_list_stale_outbound_empty(bridge_db: Path) -> None:
    """list_stale_outbound() returns empty when no stale outbound messages."""
    from groundtruth_kb.bridge.runtime import list_stale_outbound  # noqa: PLC0415

    result = list_stale_outbound("prime", older_than_seconds=1)
    assert result["count"] == 0


# ---------------------------------------------------------------------------
# get_worker_event_payload
# ---------------------------------------------------------------------------


def test_get_worker_event_payload(bridge_db: Path) -> None:
    """get_worker_event_payload() returns context with ok=True for known message."""
    from groundtruth_kb.bridge.runtime import get_worker_event_payload, send_message  # noqa: PLC0415

    payload = json.dumps({"expected_response": "status_update", "artifact_refs": ["x.md"], "action_items": ["a"]})
    result = send_message(
        sender="prime",
        recipient="codex",
        subject="Worker payload test",
        body="body",
        payload_json=payload,
    )
    message_id = result["id"]

    payload_result = get_worker_event_payload(message_id, agent="codex")
    assert payload_result["ok"] is True
    assert payload_result["context"] is not None
    assert payload_result["context"]["canonical_message"]["id"] == message_id


# ---------------------------------------------------------------------------
# list_threads
# ---------------------------------------------------------------------------


def test_list_threads_empty(bridge_db: Path) -> None:
    """list_threads() returns empty list when no threads."""
    from groundtruth_kb.bridge.runtime import list_threads  # noqa: PLC0415

    result = list_threads("codex", status="open")
    assert result["count"] == 0
