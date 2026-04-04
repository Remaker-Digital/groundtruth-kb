from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import bridge_resident_worker as resident_worker


def test_resident_worker_is_healthy_for_recent_busy_worker(tmp_path) -> None:
    now = datetime(2026, 3, 29, 2, 0, tzinfo=timezone.utc)
    (tmp_path / ".bridge-worker-codex-health.json").write_text(
        json.dumps(
            {
                "status": "busy",
                "updated_at": (now - timedelta(seconds=5)).isoformat(),
                "dispatch_started_at": (now - timedelta(seconds=10)).isoformat(),
                "dispatch_timeout_seconds": 30,
            }
        ),
        encoding="utf-8",
    )

    healthy, state = resident_worker.resident_worker_is_healthy(
        "codex",
        hooks_dir=tmp_path,
        now=now,
    )

    assert healthy is True
    assert state == "busy"


def test_resident_worker_should_defer_only_for_same_busy_targets(tmp_path) -> None:
    now = datetime(2026, 3, 29, 2, 0, tzinfo=timezone.utc)
    (tmp_path / ".bridge-worker-codex-health.json").write_text(
        json.dumps(
            {
                "status": "busy",
                "updated_at": (now - timedelta(seconds=5)).isoformat(),
                "dispatch_started_at": (now - timedelta(seconds=10)).isoformat(),
                "dispatch_timeout_seconds": 30,
                "active_message_ids": ["m-1"],
            }
        ),
        encoding="utf-8",
    )

    same_thread, same_state = resident_worker.resident_worker_should_defer(
        "codex",
        ["m-1"],
        hooks_dir=tmp_path,
        now=now,
    )
    other_thread, other_state = resident_worker.resident_worker_should_defer(
        "codex",
        ["m-2"],
        hooks_dir=tmp_path,
        now=now,
    )

    assert same_thread is True
    assert same_state == "busy-same-targets"
    assert other_thread is False
    assert other_state == "busy-other-targets"


def test_resident_worker_is_healthy_for_recent_noop_worker(tmp_path) -> None:
    now = datetime(2026, 3, 29, 2, 0, tzinfo=timezone.utc)
    (tmp_path / ".bridge-worker-codex-health.json").write_text(
        json.dumps(
            {
                "status": "noop",
                "updated_at": (now - timedelta(seconds=5)).isoformat(),
            }
        ),
        encoding="utf-8",
    )

    healthy, state = resident_worker.resident_worker_is_healthy(
        "codex",
        hooks_dir=tmp_path,
        now=now,
    )

    assert healthy is True
    assert state == "noop"


def test_explicit_refs_for_filters_to_relevant_agent_events() -> None:
    event_batch = {
        "notified": True,
        "items": [
            {
                "event_type": "message.invalid",
                "message_id": "m-ignore",
                "details": {"sender": "prime", "recipient": "codex"},
            },
            {
                "event_type": "message.invalid",
                "message_id": "m-correct",
                "details": {"sender": "codex", "recipient": "prime"},
            },
            {
                "event_type": "thread.response_window_breach",
                "details": {"thread_id": "t-1", "current_assignee": "codex"},
            },
            {
                "event_type": "thread.updated",
                "details": {"thread_id": "t-ignore", "current_assignee": "prime"},
            },
        ],
    }

    refs = resident_worker._explicit_refs_for("codex", event_batch)

    assert refs == ["m-correct", "t-1"]


class _FakeLatestNotificationBridge:
    def __init__(self, last_event_id: int) -> None:
        self._last_event_id = last_event_id

    def get_latest_notification_event_id(self, *, agent: str) -> dict:
        assert agent == "codex"
        return {"agent": agent, "last_event_id": self._last_event_id}


class _FakeWorkerPayloadBridge:
    def __init__(self, payloads: dict[str, dict]) -> None:
        self._payloads = payloads

    def get_worker_event_payload(self, message_ref: str, agent: str | None = None) -> dict:
        assert agent == "codex"
        return {"ok": True, "context": self._payloads[message_ref]}


def test_seed_last_event_id_uses_notification_high_water_mark() -> None:
    state = {"last_event_id": 0, "last_wake_by_message": {}}

    seeded = resident_worker._seed_last_event_id(
        "codex",
        _FakeLatestNotificationBridge(last_event_id=42),
        state,
    )

    assert seeded == 42
    assert state["last_event_id"] == 42


def test_capture_target_state_tracks_thread_progress_signature() -> None:
    bridge = _FakeWorkerPayloadBridge(
        {
            "m-1": {
                "canonical_message": {
                    "status": "new",
                    "claimed_by": None,
                    "resolved_at": None,
                },
                "latest_thread_message": {"id": "m-1"},
                "thread_messages": [{"id": "m-1"}],
            }
        }
    )

    snapshot = resident_worker._capture_target_state(bridge, "codex", ["m-1"])

    assert snapshot == {
        "m-1": {
            "canonical_status": "new",
            "claimed_by": None,
            "resolved_at": None,
            "latest_thread_message_id": "m-1",
            "message_count": 1,
        }
    }
