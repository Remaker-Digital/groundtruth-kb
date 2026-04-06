from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bridge_poller
import prime_bridge_runtime as runtime


def _valid_payload() -> str:
    return json.dumps(
        {
            "expected_response": "advisory_review",
            "artifact_refs": ["artifact.md"],
            "action_items": ["review the note"],
        }
    )


def _unsupported_ack_payload() -> str:
    return json.dumps(
        {
            "expected_response": "acknowledgement",
            "artifact_refs": ["proposal.md"],
            "action_items": ["acknowledge receipt"],
        }
    )


class _FakeBridge:
    def __init__(self, items: list[dict]) -> None:
        self._items = items

    def list_inbox(self, *, agent: str, status: str, limit: int) -> dict:
        assert status == "pending"
        return {"count": len(self._items), "items": list(self._items)}

    def resolve_message(self, **_: object) -> dict:
        return {"ok": True}


def test_list_inbox_pending_excludes_failed(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    failed_result = runtime.send_message(
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

    pending_inbox = runtime.list_inbox(agent="prime", status="pending", limit=10)
    failed_inbox = runtime.list_inbox(agent="prime", status="failed", limit=10)

    assert [item["id"] for item in pending_inbox["items"]] == [valid_result["id"]]
    assert [item["id"] for item in failed_inbox["items"]] == [failed_result["id"]]


def test_root_ack_request_is_failed_after_protocol_change(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Please acknowledge this proposal review request",
        body="proposal attached",
        payload_json=_unsupported_ack_payload(),
    )

    assert result["status"] == "failed"
    assert (
        "invalid expected_response: acknowledgement"
        in result["validation_errors"]
    )


def test_root_status_update_request_is_valid_without_correlation(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Bridge status check",
        body="Reply with a short substantive status update.",
        payload_json=json.dumps(
            {
                "expected_response": "status_update",
                "artifact_refs": ["artifact.md"],
                "action_items": ["Send a short substantive status update"],
            }
        ),
    )

    assert result["status"] == "pending"
    assert result["validation_errors"] == []


def test_peer_reply_without_expected_response_fails(tmp_path: Path, monkeypatch) -> None:
    """In v3, replies no longer inherit structured contract from root. Replies must carry their own payload."""
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    root = runtime.send_message(
        sender="prime",
        recipient="codex",
        subject="Bridge round-trip test",
        body="Reply with a short substantive status update.",
        payload_json=json.dumps(
            {
                "expected_response": "status_update",
                "artifact_refs": [{"type": "file", "path": "CLAUDE.md", "note": "valid ref"}],
                "action_items": ["Send a short substantive reply confirming the bridge processed this thread"],
            }
        ),
    )
    assert root["status"] == "pending"

    reply = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="RE: Bridge round-trip test",
        body="Bridge processed the thread successfully.",
        payload_json=json.dumps({"message_kind": "substantive", "status": "processed"}),
        correlation_id=root["id"],
    )

    # Without expected_response in payload, the reply should fail validation
    assert reply["status"] == "failed"
    assert any("missing expected_response" in e for e in reply["validation_errors"])


def test_reply_like_message_without_correlation_stays_failed(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Status update without thread",
        body="still working",
        payload_json=json.dumps({"response_type": "status_update"}),
    )

    assert result["status"] == "failed"
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


def test_failed_message_wakes_sender_only() -> None:
    event = {
        "event_type": "message.failed",
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
        "status": "pending",
        "payload": {"expected_response": "advisory_review"},
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


def test_handle_inbox_ignores_failed_items_for_wake(tmp_path: Path) -> None:
    item = {
        "id": "m-failed",
        "sender": "prime",
        "recipient": "codex",
        "subject": "Malformed closure",
        "status": "failed",
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

    assert handled["failed_inbox"] == 1
    assert handled["wake_candidates"] == []
    assert handled["surfaced"] == 0


def test_build_worker_event_payload_includes_thread_state(tmp_path: Path, monkeypatch) -> None:
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

    failed = runtime.send_message(
        sender="prime",
        recipient="codex",
        subject="Malformed revised plan",
        body="body",
        payload_json=_valid_payload(),
        correlation_id="missing-thread",
    )
    assert failed["status"] == "failed"

    first = runtime.send_correction_message(
        sender="codex",
        failed_message_id=failed["id"],
        guidance="Use the canonical report already on disk unless a resend is still needed.",
        artifact_refs_json=json.dumps(["report.md"]),
    )
    second = runtime.send_correction_message(
        sender="codex",
        failed_message_id=failed["id"],
        guidance="duplicate call should dedupe",
        artifact_refs_json=json.dumps(["report.md"]),
    )

    correction = runtime.resolve_message_reference(first["id"], recipient="prime")

    assert first["ok"] is True
    assert first["status"] == "pending"
    assert first["validation_errors"] == []
    assert first["deduped"] is False
    assert second["ok"] is True
    assert second["id"] == first["id"]
    assert second["deduped"] is True
    assert correction is not None
    assert correction["correlation_id"] == failed["id"]
    assert correction["payload"]["response_type"] == "correction"


def test_clear_failed_messages_clears_historical_rows(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    failed = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Malformed historical request",
        body="missing structured fields",
        payload_json="{}",
    )
    assert failed["status"] == "failed"

    with runtime._conn() as conn:
        conn.execute(
            "UPDATE messages SET created_at = ? WHERE id = ?",
            ((datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(), failed["id"]),
        )
        conn.commit()

    before = runtime.get_latest_notification_event_id()["last_event_id"]
    cleared = runtime.clear_failed_messages(agent="prime", older_than_minutes=15, limit=20)
    after = runtime.get_latest_notification_event_id()["last_event_id"]

    assert cleared["ok"] is True
    assert cleared["cleared_count"] == 1
    assert cleared["cleared_ids"] == [failed["id"]]
    assert after == before


def test_clear_failed_messages_leaves_recent_failed_rows_untouched(
    tmp_path: Path,
    monkeypatch,
) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    failed = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Malformed recent request",
        body="missing structured fields",
        payload_json="{}",
    )
    assert failed["status"] == "failed"

    cleared = runtime.clear_failed_messages(agent="prime", older_than_minutes=15, limit=20)
    failed_inbox = runtime.list_inbox(agent="prime", status="failed", limit=10)

    assert cleared["ok"] is True
    assert cleared["cleared_count"] == 0
    assert failed_inbox["count"] == 1
    assert failed_inbox["items"][0]["id"] == failed["id"]


def test_handle_inbox_defers_to_resident_worker_when_healthy(tmp_path: Path) -> None:
    item = {
        "id": "m-healthy",
        "sender": "prime",
        "recipient": "codex",
        "subject": "Review this quickly",
        "status": "pending",
        "payload": {"expected_response": "advisory_review"},
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


def test_retry_pending_message(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    sent = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Review request",
        body="Please inspect artifact",
        payload_json=_valid_payload(),
    )
    assert sent["status"] == "pending"

    result = runtime.retry_pending_message(message_id=sent["id"], agent="prime")
    assert result["ok"] is True
    assert result["retry_count"] == 1

    result2 = runtime.retry_pending_message(message_id=sent["id"], agent="prime")
    assert result2["ok"] is True
    assert result2["retry_count"] == 2


def test_retry_pending_message_caps_at_max(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    sent = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Review request",
        body="Please inspect artifact",
        payload_json=_valid_payload(),
    )

    for _ in range(runtime.MAX_RETRIES):
        result = runtime.retry_pending_message(message_id=sent["id"], agent="prime")
        assert result["ok"] is True

    result = runtime.retry_pending_message(message_id=sent["id"], agent="prime")
    assert result["ok"] is False
    assert "max retries exceeded" in result["reason"]


def test_resolve_message_with_new_outcomes(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    sent = runtime.send_message(
        sender="codex",
        recipient="prime",
        subject="Review request",
        body="body",
        payload_json=_valid_payload(),
    )

    result = runtime.resolve_message(
        message_id=sent["id"],
        agent="prime",
        outcome="completed",
        resolution="Work done",
    )

    assert result["ok"] is True
    assert result["status"] == "completed"


# ---------------------------------------------------------------------------
# v3 contract enforcement tests (Codex residual from S261)
# ---------------------------------------------------------------------------


def test_self_addressed_peer_message_rejected(tmp_path: Path, monkeypatch) -> None:
    """Peer messages where sender == recipient must be rejected."""
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="codex",
        recipient="codex",
        subject="Self-addressed message",
        body="This should fail validation.",
        payload_json=_valid_payload(),
    )

    assert result["status"] == "failed"
    assert any("self-addressed" in e for e in result["validation_errors"])


def test_status_update_reply_without_correlation_id_rejected(tmp_path: Path, monkeypatch) -> None:
    """A peer status_update with response_type but no correlation_id must fail."""
    db_path = tmp_path / "bridge.db"
    monkeypatch.setattr(runtime, "DB_PATH", db_path)

    result = runtime.send_message(
        sender="prime",
        recipient="codex",
        subject="Uncorrelated status update",
        body="status update without thread context",
        payload_json=json.dumps({
            "expected_response": "status_update",
            "response_type": "status_update",
            "artifact_refs": ["CLAUDE.md"],
            "action_items": ["acknowledge status"],
        }),
    )

    assert result["status"] == "failed"
    assert any("missing correlation_id" in e for e in result["validation_errors"])


def test_correction_reply_satisfies_context_requires_action() -> None:
    """A correction (message_kind=system) from the agent must satisfy context_requires_action."""
    from bridge_worker_context import context_requires_action

    context = {
        "canonical_message": {
            "id": "m-request",
            "status": "pending",
            "sender": "prime",
            "recipient": "codex",
            "subject": "Review request",
            "expected_response": "advisory_review",
            "created_at": "2026-04-05T10:00:00+00:00",
        },
        "thread_messages": [
            {
                "id": "m-correction",
                "sender": "codex",
                "recipient": "prime",
                "message_kind": "system",
                "status": "pending",
                "created_at": "2026-04-05T10:01:00+00:00",
            },
        ],
    }

    assert context_requires_action("codex", context) is False
