from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import bridge_poller
import prime_bridge_runtime as runtime


def _valid_payload() -> str:
    return json.dumps(
        {
            "expected_response": "advisory_review",
            "response_window": "short",
            "artifact_refs": ["artifact.md"],
            "action_items": ["review the note"],
        }
    )


def _ack_payload() -> str:
    return json.dumps(
        {
            "expected_response": "acknowledgement",
            "response_window": "session",
            "artifact_refs": ["proposal.md"],
            "action_items": ["acknowledge receipt"],
        }
    )


class _FakeBridge:
    def __init__(self, items: list[dict]) -> None:
        self._items = items

    def list_inbox(self, *, agent: str, status: str, limit: int) -> dict:
        assert status == "new"
        return {"count": len(self._items), "items": list(self._items)}

    def claim_message(self, *, message_id: str, agent: str) -> dict:
        return {"claimed": True}

    def resolve_message(self, **_: object) -> dict:
        return {"ok": True}


def test_list_inbox_new_excludes_invalid(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    invalid_result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Malformed review request",
        body="missing structured fields",
        payload_json="{}",
    )
    valid_result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Valid review request",
        body="structured",
        payload_json=_valid_payload(),
    )

    new_inbox = runtime.list_inbox(agent="prime", status="new", limit=10)
    invalid_inbox = runtime.list_inbox(agent="prime", status="invalid", limit=10)

    assert [item["id"] for item in new_inbox["items"]] == [valid_result["id"]]
    assert [item["id"] for item in invalid_inbox["items"]] == [invalid_result["id"]]


def test_root_ack_request_is_valid_without_correlation(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Please acknowledge this proposal review request",
        body="proposal attached",
        payload_json=_ack_payload(),
    )

    assert result["status"] == "new"
    assert result["validation_errors"] == []


def test_reply_like_message_without_correlation_stays_invalid(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Status update without thread",
        body="still working",
        payload_json=json.dumps({"response_type": "status_update"}),
    )

    assert result["status"] == "invalid"
    assert "missing correlation_id for reply-like peer message" in result["validation_errors"]


def test_resolve_message_reference_allows_sender_lookup(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    sent = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Sender-visible message",
        body="body",
        payload_json=_valid_payload(),
    )

    resolved = runtime.resolve_message_reference(sent["id"], recipient="codex")
    assert resolved is not None
    assert resolved["id"] == sent["id"]


def test_legacy_null_thread_row_is_repaired_for_ack_correlation(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    root = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Legacy root",
        body="body",
        payload_json=_valid_payload(),
    )

    with runtime._conn() as conn:
        conn.execute("UPDATE messages SET thread_id = NULL WHERE id = ?", (root["id"],))
        conn.execute("DELETE FROM threads WHERE thread_id = ?", (root["id"],))
        conn.execute(f"PRAGMA user_version = {runtime.SCHEMA_VERSION_CURRENT}")
        conn.commit()

    ack = runtime.send_message(
        sender="prime",
        recipient="codex",
        subject="Accepted: Legacy root",
        body="ack",
        payload_json=json.dumps({"response_type": "accepted"}),
        tags_json=json.dumps(["protocol", "accepted", "bridge-sync"]),
        correlation_id=root["id"],
    )

    assert ack["status"] == "new"
    assert ack["validation_errors"] == []


def test_invalid_message_wakes_sender_only() -> None:
    event = {
        "event_type": "message.invalid",
        "details": {"sender": "codex", "recipient": "prime"},
    }

    assert bridge_poller._notification_should_wake("codex", event) is True
    assert bridge_poller._notification_should_wake("prime", event) is False


def test_handle_inbox_suppresses_repeat_wake_for_same_message(tmp_path: Path) -> None:
    item = {
        "id": "m-1",
        "sender": "prime",
        "recipient": "codex",
        "subject": "Review this",
        "status": "new",
        "payload": {"expected_response": "acknowledgement"},
        "tags": [],
        "message_kind": "substantive",
    }
    bridge = _FakeBridge([item])
    state = {"last_wake_by_message": {}}
    log_file = tmp_path / "poller.log"

    first = bridge_poller._handle_inbox(
        bridge,
        "codex",
        "prime",
        log_file,
        state=state,
        project_dir=tmp_path,
        write_enabled=True,
    )
    assert first["wake_candidates"] == ["m-1"]
    assert first["surfaced"] == 1

    bridge_poller._record_wake_launch(state, first["wake_candidates"])

    second = bridge_poller._handle_inbox(
        bridge,
        "codex",
        "prime",
        log_file,
        state=state,
        project_dir=tmp_path,
        write_enabled=True,
    )
    assert second["wake_candidates"] == []
    assert second["surfaced"] == 0


def test_handle_inbox_ignores_invalid_items_for_wake(tmp_path: Path) -> None:
    item = {
        "id": "m-invalid",
        "sender": "prime",
        "recipient": "codex",
        "subject": "Malformed closure",
        "status": "invalid",
        "payload": {},
        "tags": [],
        "message_kind": "substantive",
    }
    bridge = _FakeBridge([item])
    log_file = tmp_path / "poller.log"

    handled = bridge_poller._handle_inbox(
        bridge,
        "codex",
        "prime",
        log_file,
        state={"last_wake_by_message": {}},
        project_dir=tmp_path,
        write_enabled=True,
    )

    assert handled["invalid_inbox"] == 1
    assert handled["wake_candidates"] == []
    assert handled["surfaced"] == 0


def test_build_worker_event_payload_includes_thread_snapshot(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    sent = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Review request",
        body="Please inspect artifact",
        payload_json=_valid_payload(),
    )

    payload = runtime.build_worker_event_payload(sent["id"], recipient="prime")

    assert payload is not None
    assert payload["canonical_message"]["id"] == sent["id"]
    assert payload["thread_correlation_id"] == sent["id"]
    assert payload["artifact_refs"] == ["artifact.md"]
    assert payload["action_items"] == ["review the note"]
    assert payload["latest_summary"] == "Review request"


def test_get_latest_notification_event_id_returns_agent_high_water_mark(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="First review request",
        body="structured",
        payload_json=_valid_payload(),
    )
    runtime.send_message(
        sender="prime",
        recipient="codex",
        subject="Second review request",
        body="structured",
        payload_json=_valid_payload(),
    )

    latest = runtime.get_latest_notification_event_id(agent="prime")

    assert latest["last_event_id"] >= 1


def test_send_correction_message_is_valid_and_dedupes(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    invalid = runtime.send_message(
        sender="prime",
        recipient="codex",
        subject="Malformed revised plan",
        body="body",
        payload_json=_valid_payload(),
        correlation_id="missing-thread",
    )
    assert invalid["status"] == "invalid"

    first = runtime.send_correction_message(
        sender="codex",
        invalid_message_id=invalid["id"],
        guidance="Use the canonical report already on disk unless a resend is still needed.",
        artifact_refs_json=json.dumps(["report.md"]),
    )
    second = runtime.send_correction_message(
        sender="codex",
        invalid_message_id=invalid["id"],
        guidance="duplicate call should dedupe",
        artifact_refs_json=json.dumps(["report.md"]),
    )

    correction = runtime.resolve_message_reference(first["id"], recipient="prime")

    assert first["ok"] is True
    assert first["status"] == "new"
    assert first["validation_errors"] == []
    assert first["deduped"] is False
    assert second["ok"] is True
    assert second["id"] == first["id"]
    assert second["deduped"] is True
    assert correction is not None
    assert correction["correlation_id"] == invalid["id"]
    assert correction["payload"]["response_type"] == "correction"
    assert "system" in correction["tags"]


def test_handle_inbox_defers_to_resident_worker_when_healthy(tmp_path: Path) -> None:
    item = {
        "id": "m-healthy",
        "sender": "prime",
        "recipient": "codex",
        "subject": "Review this quickly",
        "status": "new",
        "payload": {"expected_response": "acknowledgement"},
        "tags": [],
        "message_kind": "substantive",
    }
    bridge = _FakeBridge([item])

    handled = bridge_poller._handle_inbox(
        bridge,
        "codex",
        "prime",
        tmp_path / "poller.log",
        state={"last_wake_by_message": {}},
        project_dir=tmp_path,
        write_enabled=True,
        resident_worker_healthy=True,
    )

    assert handled["resident_deferrals"] == 1
    assert handled["wake_candidates"] == []
    assert handled["surfaced"] == 0


def test_resident_worker_busy_on_other_thread_does_not_defer_wake(tmp_path: Path) -> None:
    now = datetime(2026, 3, 29, 10, 31, 10, tzinfo=timezone.utc)
    (tmp_path / ".bridge-worker-codex-health.json").write_text(
        json.dumps(
            {
                "status": "busy",
                "updated_at": "2026-03-29T10:31:00+00:00",
                "dispatch_started_at": "2026-03-29T10:31:00+00:00",
                "dispatch_timeout_seconds": 900,
                "active_message_ids": ["m-old"],
            }
        ),
        encoding="utf-8",
    )

    defer, state = bridge_poller._resident_worker_should_defer_wake(
        "codex",
        ["m-new"],
        hooks_dir=tmp_path,
        now=now,
    )

    assert defer is False
    assert state == "busy-other-targets"


def test_launch_agent_wake_caps_message_ids(monkeypatch, tmp_path: Path) -> None:
    launched: list[list[str]] = []

    class _DummyProcess:
        pass

    def _fake_popen(cmd: list[str], **_: object) -> _DummyProcess:
        launched.append(cmd)
        return _DummyProcess()

    monkeypatch.setattr(bridge_poller.subprocess, "Popen", _fake_popen)
    monkeypatch.setattr(bridge_poller.sys, "executable", str(tmp_path / "python.exe"))
    wake_script = tmp_path / "scripts" / "codex_bridge_wake.py"
    wake_script.parent.mkdir(parents=True)
    wake_script.write_text("# wake", encoding="utf-8")

    launched_ids = bridge_poller._launch_agent_wake(
        "codex",
        tmp_path,
        [f"m-{index}" for index in range(10)],
        tmp_path / "poller.log",
        trigger="poller-notification",
    )

    assert launched_ids == [f"m-{index}" for index in range(bridge_poller.DEFAULT_MAX_DISPATCH_TARGETS)]
    assert len(launched) == 1
    cmd = launched[0]
    passed_ids = [cmd[index + 1] for index, value in enumerate(cmd[:-1]) if value == "--message-id"]
    assert passed_ids == launched_ids
