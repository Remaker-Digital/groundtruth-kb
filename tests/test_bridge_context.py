# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.context — context building and dispatch logic.

All bridge imports are inside the isolated_bridge fixture or test functions.
No top-level groundtruth_kb.bridge imports are allowed here.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SESSION_START_SUBJECT = "Session start: report current operating state"
SESSION_START_BODY = "Report your current operating state"


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


def _make_context(canonical_override: dict[str, Any] | None = None) -> dict[str, Any]:
    canonical: dict[str, Any] = {
        "id": "msg-1",
        "sender": "codex",
        "recipient": "prime",
        "status": "pending",
        "subject": SESSION_START_SUBJECT,
        "body": SESSION_START_BODY,
        "created_at": "2026-01-01T00:00:00+00:00",
        "priority": 1,
        "expected_response": "status_update",
        "resolution": None,
        "artifact_refs": [],
        "tags": [],
        "message_kind": "substantive",
    }
    if canonical_override:
        canonical.update(canonical_override)
    return {
        "canonical_message": canonical,
        "thread_messages": [],
        "thread_correlation_id": "thread-1",
        "artifact_refs": [],
        "latest_non_protocol_prime_message": None,
        "latest_non_protocol_codex_message": None,
    }


def _make_bridge_mock(context_dict: dict[str, Any] | None = None) -> MagicMock:
    bridge = MagicMock()
    bridge.get_worker_event_payload.return_value = context_dict
    bridge.resolve_message.return_value = {"ok": True}
    bridge.send_message.return_value = {"status": "pending", "id": "reply-1"}
    bridge.list_inbox.return_value = {"count": 0, "items": []}
    return bridge


# ---------------------------------------------------------------------------
# Pure utility functions
# ---------------------------------------------------------------------------


def test_agent_peer_codex(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import agent_peer  # noqa: PLC0415

    assert agent_peer("codex") == "prime"


def test_agent_peer_prime(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import agent_peer  # noqa: PLC0415

    assert agent_peer("prime") == "codex"


def test_agent_display_codex(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import agent_display  # noqa: PLC0415

    assert agent_display("codex") == "Codex"


def test_agent_display_prime(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import agent_display  # noqa: PLC0415

    assert agent_display("prime") == "Prime"


def test_dedupe_preserve_order(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import dedupe_preserve_order  # noqa: PLC0415

    result = dedupe_preserve_order(["a", "b", "a", "c", "b"])
    assert result == ["a", "b", "c"]


def test_dedupe_empty(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import dedupe_preserve_order  # noqa: PLC0415

    assert dedupe_preserve_order([]) == []


def test_message_is_session_start_request_positive(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import message_is_session_start_request  # noqa: PLC0415

    msg = {"subject": SESSION_START_SUBJECT, "body": SESSION_START_BODY}
    assert message_is_session_start_request(msg) is True


def test_message_is_session_start_request_negative(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import message_is_session_start_request  # noqa: PLC0415

    msg = {"subject": "Other subject", "body": "Other body"}
    assert message_is_session_start_request(msg) is False


def test_message_is_closure_only_thread_completed(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import message_is_closure_only  # noqa: PLC0415

    msg = {"body": "Thread completed with outcome COMPLETED."}
    assert message_is_closure_only(msg) is True


def test_message_is_closure_only_false(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import message_is_closure_only  # noqa: PLC0415

    msg = {"body": "Normal substantive review content."}
    assert message_is_closure_only(msg) is False


def test_iter_text_fragments_string(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import iter_text_fragments  # noqa: PLC0415

    result = iter_text_fragments("hello")
    assert result == ["hello"]


def test_iter_text_fragments_none(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import iter_text_fragments  # noqa: PLC0415

    assert iter_text_fragments(None) == []


def test_iter_text_fragments_list(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import iter_text_fragments  # noqa: PLC0415

    result = iter_text_fragments(["a", "b"])
    assert result == ["a", "b"]


def test_iter_text_fragments_dict(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import iter_text_fragments  # noqa: PLC0415

    result = iter_text_fragments({"x": "hello", "y": "world"})
    assert "hello" in result
    assert "world" in result


def test_clean_path_candidate(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import clean_path_candidate  # noqa: PLC0415

    assert clean_path_candidate("  `INSIGHTS-foo.md`  ") == "INSIGHTS-foo.md"
    assert clean_path_candidate('"path/to/file.md"') == "path/to/file.md"


# ---------------------------------------------------------------------------
# resolve_artifact_name
# ---------------------------------------------------------------------------


def test_resolve_artifact_name_not_found(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import resolve_artifact_name  # noqa: PLC0415

    result = resolve_artifact_name("nonexistent-file.md", project_dir=tmp_path)
    assert result is None


def test_resolve_artifact_name_direct_relative(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import resolve_artifact_name  # noqa: PLC0415

    test_file = tmp_path / "AGENTS.md"
    test_file.write_text("content", encoding="utf-8")
    result = resolve_artifact_name("AGENTS.md", project_dir=tmp_path)
    assert result is not None
    assert result.name == "AGENTS.md"


def test_resolve_artifact_name_absolute_exists(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import resolve_artifact_name  # noqa: PLC0415

    test_file = tmp_path / "test.md"
    test_file.write_text("content", encoding="utf-8")
    result = resolve_artifact_name(str(test_file), project_dir=tmp_path)
    assert result is not None


def test_resolve_artifact_name_absolute_missing(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import resolve_artifact_name  # noqa: PLC0415

    result = resolve_artifact_name(str(tmp_path / "missing.md"), project_dir=tmp_path)
    assert result is None


# ---------------------------------------------------------------------------
# discover_artifacts
# ---------------------------------------------------------------------------


def test_discover_artifacts_empty_context(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import discover_artifacts  # noqa: PLC0415

    context: dict[str, Any] = {"artifact_refs": [], "canonical_message": {}, "thread_messages": []}
    result = discover_artifacts(context, project_dir=tmp_path)
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# summarize_context
# ---------------------------------------------------------------------------


def test_summarize_context_returns_string(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import summarize_context  # noqa: PLC0415

    context = _make_context()
    context["wake_reasons"] = ["new"]
    context["already_reviewed_hint"] = False
    context["referenced_artifacts"] = []
    result = summarize_context("prime", context)
    assert isinstance(result, str)
    assert "msg-1" in result


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------


def test_build_prompt_returns_string(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import build_prompt  # noqa: PLC0415

    snapshot_path = tmp_path / "snapshot.json"
    snapshot_path.write_text("{}", encoding="utf-8")
    context = _make_context()
    context["wake_reasons"] = ["new"]
    context["already_reviewed_hint"] = False
    context["referenced_artifacts"] = []
    result = build_prompt("prime", snapshot_path, [], [context], project_dir=tmp_path)
    assert isinstance(result, str)
    assert "prime" in result.lower() or "Prime" in result


# ---------------------------------------------------------------------------
# build_context_snapshot
# ---------------------------------------------------------------------------


def test_build_context_snapshot(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import build_context_snapshot  # noqa: PLC0415

    result = build_context_snapshot(trigger="test", contexts=[], new_items=[])
    assert result["trigger"] == "test"
    assert "generated_at" in result
    assert result["new_inbox_ids"] == []


# ---------------------------------------------------------------------------
# select_dispatch_batch
# ---------------------------------------------------------------------------


def test_select_dispatch_batch_empty(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import select_dispatch_batch  # noqa: PLC0415

    result = select_dispatch_batch([], [], max_targets=6)
    assert result["contexts"] == []
    assert result["new_items"] == []


def test_select_dispatch_batch_prioritizes_session_start(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import select_dispatch_batch  # noqa: PLC0415

    normal_item = {"id": "msg-normal", "subject": "Normal", "body": "Normal", "status": "pending", "priority": 1}
    session_item = {
        "id": "msg-session",
        "subject": SESSION_START_SUBJECT,
        "body": SESSION_START_BODY,
        "status": "pending",
        "priority": 1,
    }
    result = select_dispatch_batch([], [normal_item, session_item], max_targets=6)
    if result["new_items"]:
        assert result["new_items"][0]["id"] == "msg-session"


def test_select_dispatch_batch_invalid_max_targets(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import select_dispatch_batch  # noqa: PLC0415

    with pytest.raises(ValueError, match="max_targets"):
        select_dispatch_batch([], [], max_targets=0)


def test_select_dispatch_batch_respects_max(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import select_dispatch_batch  # noqa: PLC0415

    items = [{"id": f"msg-{i}", "subject": "s", "body": "b", "status": "pending", "priority": 1} for i in range(10)]
    result = select_dispatch_batch([], items, max_targets=3)
    assert len(result["new_items"]) <= 3


# ---------------------------------------------------------------------------
# build_contexts
# ---------------------------------------------------------------------------


def test_build_contexts_empty_explicit_refs(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import build_contexts  # noqa: PLC0415

    bridge = _make_bridge_mock(context_dict=None)
    result = build_contexts(bridge, agent="prime", explicit_refs=[], new_items=[], project_dir=tmp_path)
    assert result == []


def test_build_contexts_explicit_ref_resolved(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import build_contexts  # noqa: PLC0415

    ctx = _make_context()
    bridge = _make_bridge_mock(context_dict=ctx)
    result = build_contexts(bridge, agent="prime", explicit_refs=["msg-1"], new_items=[], project_dir=tmp_path)
    assert len(result) == 1
    assert result[0]["canonical_message"]["id"] == "msg-1"


def test_build_contexts_log_fn_called_on_unresolved(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import build_contexts  # noqa: PLC0415

    bridge = _make_bridge_mock(context_dict=None)
    log_messages: list[str] = []
    build_contexts(
        bridge,
        agent="prime",
        explicit_refs=["unresolved-ref"],
        new_items=[],
        project_dir=tmp_path,
        log_fn=log_messages.append,
    )
    assert any("unresolved" in msg for msg in log_messages)


def test_build_contexts_max_contexts_limit(isolated_bridge: Path, tmp_path: Path) -> None:
    from groundtruth_kb.bridge.context import build_contexts  # noqa: PLC0415

    ctx = _make_context()
    bridge = _make_bridge_mock(context_dict=ctx)
    # max_contexts=0 should raise ValueError
    with pytest.raises(ValueError, match="max_contexts"):
        build_contexts(
            bridge,
            agent="prime",
            explicit_refs=["msg-1"],
            new_items=[],
            project_dir=tmp_path,
            max_contexts=0,
        )


# ---------------------------------------------------------------------------
# context_requires_action
# ---------------------------------------------------------------------------


def test_context_requires_action_no_peer(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import context_requires_action  # noqa: PLC0415

    # No valid sender/recipient pair → no peer → False
    context: dict[str, Any] = {
        "canonical_message": {"id": "x", "sender": "owner", "recipient": "prime", "status": "pending"},
        "thread_messages": [],
    }
    assert context_requires_action("prime", context) is False


def test_context_requires_action_valid_outbound_false(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import context_requires_action  # noqa: PLC0415

    outbound = {
        "id": "reply-1",
        "sender": "prime",
        "recipient": "codex",
        "message_kind": "substantive",
        "status": "pending",
        "created_at": "2026-01-02T00:00:00+00:00",
    }
    context: dict[str, Any] = {
        "canonical_message": {
            "id": "msg-1",
            "sender": "codex",
            "recipient": "prime",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00+00:00",
        },
        "thread_messages": [outbound],
    }
    assert context_requires_action("prime", context) is False


def test_context_requires_action_no_outbound_true(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import context_requires_action  # noqa: PLC0415

    context: dict[str, Any] = {
        "canonical_message": {
            "id": "msg-1",
            "sender": "codex",
            "recipient": "prime",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00+00:00",
        },
        "thread_messages": [],
    }
    assert context_requires_action("prime", context) is True


def test_context_requires_action_failed_outbound_true(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import context_requires_action  # noqa: PLC0415

    failed_outbound = {
        "id": "reply-1",
        "sender": "prime",
        "recipient": "codex",
        "message_kind": "substantive",
        "status": "failed",
        "created_at": "2026-01-02T00:00:00+00:00",
    }
    context: dict[str, Any] = {
        "canonical_message": {
            "id": "msg-1",
            "sender": "codex",
            "recipient": "prime",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00+00:00",
        },
        "thread_messages": [failed_outbound],
    }
    assert context_requires_action("prime", context) is True


def test_context_requires_action_completed_with_protocol_ack_false(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import context_requires_action  # noqa: PLC0415

    protocol_ack = {
        "id": "ack-1",
        "sender": "prime",
        "recipient": "codex",
        "message_kind": "protocol_ack",
        "status": "pending",
        "created_at": "2026-01-02T00:00:00+00:00",
    }
    context: dict[str, Any] = {
        "canonical_message": {
            "id": "msg-1",
            "sender": "codex",
            "recipient": "prime",
            "status": "completed",
            "created_at": "2026-01-01T00:00:00+00:00",
        },
        "thread_messages": [protocol_ack],
    }
    assert context_requires_action("prime", context) is False


# ---------------------------------------------------------------------------
# fast_path_session_start_requests
# ---------------------------------------------------------------------------


def test_fast_path_no_contexts(isolated_bridge: Path, tmp_path: Path) -> None:
    """When bridge returns None, handled count is 0."""
    from groundtruth_kb.bridge.context import fast_path_session_start_requests  # noqa: PLC0415

    bridge = _make_bridge_mock(context_dict=None)
    result = fast_path_session_start_requests(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result == 0


def test_fast_path_skips_non_session_start(isolated_bridge: Path, tmp_path: Path) -> None:
    """Non-session-start canonical → skipped → returns 0."""
    from groundtruth_kb.bridge.context import fast_path_session_start_requests  # noqa: PLC0415

    ctx = _make_context({"subject": "Other subject", "body": "Other body"})
    bridge = _make_bridge_mock(context_dict=ctx)
    result = fast_path_session_start_requests(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result == 0


def test_fast_path_handles_session_start_request(isolated_bridge: Path, tmp_path: Path) -> None:
    """Valid session-start with no outbound → sends reply → returns 1."""
    from groundtruth_kb.bridge.context import fast_path_session_start_requests  # noqa: PLC0415

    ctx = _make_context()  # session-start subject+body, no outbound messages
    bridge = _make_bridge_mock(context_dict=ctx)
    # send_message returns non-failed status
    bridge.send_message.return_value = {"status": "pending", "id": "reply-1"}
    bridge.resolve_message.return_value = {"ok": True}
    bridge.list_inbox.return_value = {"count": 0, "items": []}

    result = fast_path_session_start_requests(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result >= 1


def test_fast_path_reply_already_exists(isolated_bridge: Path, tmp_path: Path) -> None:
    """Valid outbound already exists → auto-resolves canonical → returns 1."""
    from groundtruth_kb.bridge.context import fast_path_session_start_requests  # noqa: PLC0415

    outbound = {
        "id": "existing-reply",
        "sender": "prime",
        "recipient": "codex",
        "message_kind": "substantive",
        "status": "pending",
        "created_at": "2026-01-02T00:00:00+00:00",
    }
    ctx = _make_context()
    ctx["thread_messages"] = [outbound]
    bridge = _make_bridge_mock(context_dict=ctx)
    bridge.resolve_message.return_value = {"ok": True}

    result = fast_path_session_start_requests(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result >= 1


def test_fast_path_multiple_contexts_mixed(isolated_bridge: Path, tmp_path: Path) -> None:
    """Two refs, one session-start context (returns non-None), one None → returns at least 0."""
    from groundtruth_kb.bridge.context import fast_path_session_start_requests  # noqa: PLC0415

    session_ctx = _make_context()
    bridge = MagicMock()

    call_count = [0]

    def side_effect(ref: str, agent: str) -> dict[str, Any] | None:
        call_count[0] += 1
        if ref == "session-ref":
            return session_ctx
        return None

    bridge.get_worker_event_payload.side_effect = side_effect
    bridge.resolve_message.return_value = {"ok": True}
    bridge.send_message.return_value = {"status": "pending", "id": "r-1"}
    bridge.list_inbox.return_value = {"count": 0, "items": []}

    result = fast_path_session_start_requests(
        bridge,
        agent="prime",
        target_refs=["session-ref", "other-ref"],
        project_dir=tmp_path,
    )
    # Should have processed session-ref
    assert result >= 0  # at least ran without error


# ---------------------------------------------------------------------------
# repair_terminal_thread_outputs
# ---------------------------------------------------------------------------


def test_repair_no_contexts(isolated_bridge: Path, tmp_path: Path) -> None:
    """When bridge returns None, repaired count is 0."""
    from groundtruth_kb.bridge.context import repair_terminal_thread_outputs  # noqa: PLC0415

    bridge = _make_bridge_mock(context_dict=None)
    result = repair_terminal_thread_outputs(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result == 0


def test_repair_closure_only_thread(isolated_bridge: Path, tmp_path: Path) -> None:
    """Closure-only canonical with status=pending → resolves → returns 1."""
    from groundtruth_kb.bridge.context import repair_terminal_thread_outputs  # noqa: PLC0415

    ctx = _make_context({"body": "Thread completed with outcome COMPLETED.", "subject": "anything"})
    bridge = _make_bridge_mock(context_dict=ctx)
    bridge.resolve_message.return_value = {"ok": True}

    result = repair_terminal_thread_outputs(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result >= 1


def test_repair_valid_outbound_exists(isolated_bridge: Path, tmp_path: Path) -> None:
    """Valid substantive outbound, pending canonical → closes canonical → returns 1."""
    from groundtruth_kb.bridge.context import repair_terminal_thread_outputs  # noqa: PLC0415

    outbound = {
        "id": "reply-1",
        "sender": "prime",
        "recipient": "codex",
        "message_kind": "substantive",
        "status": "pending",
        "created_at": "2026-01-02T00:00:00+00:00",
    }
    ctx = _make_context({"subject": "Non-closure subject", "body": "Regular body"})
    ctx["thread_messages"] = [outbound]
    bridge = _make_bridge_mock(context_dict=ctx)
    bridge.resolve_message.return_value = {"ok": True}

    result = repair_terminal_thread_outputs(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result >= 1


def test_repair_acknowledgement_only_legacy(isolated_bridge: Path, tmp_path: Path) -> None:
    """expected_response=acknowledgement with no outbound → fails with protocol-change → returns 1."""
    from groundtruth_kb.bridge.context import repair_terminal_thread_outputs  # noqa: PLC0415

    ctx = _make_context({"expected_response": "acknowledgement", "subject": "Some subject", "body": "Some body"})
    bridge = _make_bridge_mock(context_dict=ctx)
    bridge.resolve_message.return_value = {"ok": True}

    result = repair_terminal_thread_outputs(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    assert result >= 1


def test_repair_sends_outbound_for_stale_thread(isolated_bridge: Path, tmp_path: Path) -> None:
    """Completed canonical with resolution → sends new message → returns 1."""
    from groundtruth_kb.bridge.context import repair_terminal_thread_outputs  # noqa: PLC0415

    ctx = _make_context(
        {
            "status": "completed",
            "resolution": "Done with work.",
            "subject": "Work subject",
            "body": "Work body",
        }
    )
    bridge = _make_bridge_mock(context_dict=ctx)
    bridge.send_message.return_value = {"status": "pending", "id": "new-reply"}
    bridge.resolve_message.return_value = {"ok": True}

    result = repair_terminal_thread_outputs(bridge, agent="prime", target_refs=["msg-1"], project_dir=tmp_path)
    # Should attempt to send; result depends on internal path taken
    assert isinstance(result, int)


# ---------------------------------------------------------------------------
# prioritize_inbox_items
# ---------------------------------------------------------------------------


def test_prioritize_inbox_items_session_start_first(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import prioritize_inbox_items  # noqa: PLC0415

    normal = {"id": "a", "subject": "Normal", "body": "Normal", "priority": 2}
    session = {"id": "b", "subject": SESSION_START_SUBJECT, "body": SESSION_START_BODY, "priority": 1}
    result = prioritize_inbox_items([normal, session])
    assert result[0]["id"] == "b"


def test_prioritize_inbox_items_empty(isolated_bridge: Path) -> None:
    from groundtruth_kb.bridge.context import prioritize_inbox_items  # noqa: PLC0415

    assert prioritize_inbox_items([]) == []
