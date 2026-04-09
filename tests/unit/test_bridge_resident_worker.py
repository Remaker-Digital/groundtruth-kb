from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Bridge modules live at repo root — ensure it's on sys.path for CI
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

if sys.platform != "win32":
    pytest.skip("bridge_resident_worker requires msvcrt (Windows-only)", allow_module_level=True)

import bridge_resident_worker as resident_worker  # noqa: E402


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
                "event_type": "message.failed",
                "message_id": "m-correct",
                "details": {"sender": "codex", "recipient": "prime"},
            },
            {
                "event_type": "message.resolved",
                "message_id": "t-1",
                "details": {"resolved_by": "prime", "outcome": "completed"},
                "agent": "codex",
            },
            {
                "event_type": "message.new",
                "message_id": "t-ignore",
                "details": {"sender": "prime"},
                "agent": "prime",
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


class _FakeInvalidCleanupBridge:
    def __init__(self, cleared_count: int = 0, raises: Exception | None = None) -> None:
        self.cleared_count = cleared_count
        self.raises = raises
        self.calls: list[dict[str, object]] = []

    def clear_failed_messages(self, *, agent: str, older_than_minutes: int, limit: int) -> dict:
        self.calls.append(
            {
                "agent": agent,
                "older_than_minutes": older_than_minutes,
                "limit": limit,
            }
        )
        if self.raises is not None:
            raise self.raises
        return {"ok": True, "cleared_count": self.cleared_count}


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
            "resolved_at": None,
            "latest_thread_message_id": "m-1",
            "message_count": 1,
        }
    }


def test_maybe_clear_failed_residue_runs_when_interval_elapsed(monkeypatch) -> None:
    now = datetime(2026, 4, 5, 17, 40, tzinfo=timezone.utc)
    monkeypatch.setattr(resident_worker, "_now", lambda: now)
    bridge = _FakeInvalidCleanupBridge(cleared_count=3)
    state = {"last_wake_by_message": {}}
    logs: list[str] = []

    cleared = resident_worker._maybe_clear_failed_residue(
        "codex",
        bridge,
        state,
        log_fn=logs.append,
    )

    assert cleared == 3
    assert bridge.calls == [
        {
            "agent": "codex",
            "older_than_minutes": resident_worker.FAILED_RESIDUE_MAX_AGE_MINUTES,
            "limit": resident_worker.FAILED_RESIDUE_CLEANUP_LIMIT,
        }
    ]
    assert state["last_failed_cleanup_at"] == now.isoformat()
    assert logs == ["cleared historical failed residue: agent=codex cleared_count=3"]


def test_maybe_clear_failed_residue_respects_throttle(monkeypatch) -> None:
    now = datetime(2026, 4, 5, 17, 40, tzinfo=timezone.utc)
    monkeypatch.setattr(resident_worker, "_now", lambda: now)
    bridge = _FakeInvalidCleanupBridge(cleared_count=9)
    state = {
        "last_wake_by_message": {},
        "last_failed_cleanup_at": (now - timedelta(minutes=5)).isoformat(),
    }

    cleared = resident_worker._maybe_clear_failed_residue(
        "codex",
        bridge,
        state,
        log_fn=lambda _message: None,
    )

    assert cleared == 0
    assert bridge.calls == []


def test_maybe_clear_failed_residue_logs_and_recovers_from_cleanup_error(monkeypatch) -> None:
    now = datetime(2026, 4, 5, 17, 40, tzinfo=timezone.utc)
    monkeypatch.setattr(resident_worker, "_now", lambda: now)
    bridge = _FakeInvalidCleanupBridge(raises=RuntimeError("db busy"))
    state = {"last_wake_by_message": {}}
    logs: list[str] = []

    cleared = resident_worker._maybe_clear_failed_residue(
        "prime",
        bridge,
        state,
        log_fn=logs.append,
    )

    assert cleared == 0
    assert bridge.calls == [
        {
            "agent": "prime",
            "older_than_minutes": resident_worker.FAILED_RESIDUE_MAX_AGE_MINUTES,
            "limit": resident_worker.FAILED_RESIDUE_CLEANUP_LIMIT,
        }
    ]
    assert "last_failed_cleanup_at" not in state
    assert logs == ["failed residue cleanup error: db busy"]


def test_codex_bridge_wake_script_bootstraps_project_imports() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/codex_bridge_wake.py", "--help"],
        cwd=str(resident_worker.PROJECT_DIR),
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0
    assert "Wake a bridge worker" in completed.stdout
