from __future__ import annotations

import copy
import json

import bridge_worker_context as context_builder


class _FakeBridge:
    def __init__(self, context: dict) -> None:
        self._context = context

    def get_worker_event_payload(self, message_ref: str, agent: str | None = None) -> dict:
        assert message_ref == "m-1"
        assert agent == "codex"
        return copy.deepcopy(self._context)


class _FakeWrappedBridge:
    def __init__(self, context: dict) -> None:
        self._context = context

    def get_worker_event_payload(self, message_ref: str, agent: str | None = None) -> dict:
        assert message_ref == "m-1"
        assert agent == "codex"
        return {"ok": True, "context": copy.deepcopy(self._context)}


class _MapBridge:
    def __init__(self, contexts: dict[str, dict]) -> None:
        self._contexts = contexts
        self.calls: list[str] = []

    def get_worker_event_payload(self, message_ref: str, agent: str | None = None) -> dict:
        assert agent == "codex"
        self.calls.append(message_ref)
        return copy.deepcopy(self._contexts[message_ref])

    def list_threads(self, *, agent: str, status: str, limit: int) -> dict:
        raise AssertionError("list_threads should not be called in this test")


class _RepairBridge:
    def __init__(self, context: dict, *, pending_items: list[dict] | None = None) -> None:
        self._context = context
        self._pending_items = pending_items or []
        self.sent_messages: list[dict] = []
        self.resolved_messages: list[dict] = []

    def get_worker_event_payload(self, message_ref: str, agent: str | None = None) -> dict:
        assert message_ref == self._context["canonical_message"]["id"]
        assert agent == "codex"
        return copy.deepcopy(self._context)

    def send_message(
        self,
        *,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        payload_json: str,
        tags_json: str,
        priority: int,
        correlation_id: str | None = None,
    ) -> dict:
        self.sent_messages.append(
            {
                "sender": sender,
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "payload": json.loads(payload_json),
                "tags": json.loads(tags_json),
                "priority": priority,
                "correlation_id": correlation_id,
            }
        )
        return {"ok": True, "status": "pending", "id": "repair-1"}

    def resolve_message(self, *, message_id: str, agent: str, outcome: str, resolution: str) -> dict:
        self.resolved_messages.append(
            {
                "message_id": message_id,
                "agent": agent,
                "outcome": outcome,
                "resolution": resolution,
            }
        )
        return {"ok": True}

    def list_inbox(self, *, agent: str, status: str, limit: int) -> dict:
        assert agent == "codex"
        assert status == "pending"
        return {"count": len(self._pending_items), "items": copy.deepcopy(self._pending_items[:limit])}


def test_build_contexts_prefers_structured_artifact_refs(tmp_path) -> None:
    structured = tmp_path / "structured-artifact.md"
    structured.write_text("structured", encoding="utf-8")
    discovered_dir = tmp_path / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
    discovered_dir.mkdir(parents=True)
    discovered = discovered_dir / "INSIGHTS-2026-03-29-TEST-NOTE.md"
    discovered.write_text("note", encoding="utf-8")

    bridge = _FakeBridge(
        {
            "canonical_message": {
                "id": "m-1",
                "status": "pending",
                "subject": "Review note",
            },
            "thread_correlation_id": "m-1",
            "artifact_refs": ["structured-artifact.md"],
            "thread_messages": [
                {"id": "m-1", "body": "See INSIGHTS-2026-03-29-TEST-NOTE.md for details."}
            ],
            "latest_non_protocol_codex_message": {
                "id": "m-0",
                "subject": "Previous review",
                "created_at": "2026-03-29T00:00:00+00:00",
            },
            "latest_non_protocol_prime_message": None,
        }
    )

    contexts = context_builder.build_contexts(
        bridge,
        agent="codex",
        explicit_refs=["m-1"],
        new_items=[{"id": "m-1"}],

        project_dir=tmp_path,
    )

    assert len(contexts) == 1
    context = contexts[0]
    assert context["already_reviewed_hint"] is True
    assert set(context["wake_reasons"]) == {"explicit:m-1", "new"}
    assert context["referenced_artifacts"] == [
        {"path": str(discovered.resolve()), "source": "artifact-name"},
        {"path": str(structured.resolve()), "source": "structured-artifact-ref"},
    ]


def test_build_contexts_accepts_wrapped_runtime_payload(tmp_path) -> None:
    artifact = tmp_path / "artifact.md"
    artifact.write_text("artifact", encoding="utf-8")
    bridge = _FakeWrappedBridge(
        {
            "canonical_message": {
                "id": "m-1",
                "status": "pending",
                "subject": "Wrapped payload",
            },
            "thread_correlation_id": "m-1",
            "artifact_refs": ["artifact.md"],
            "thread_messages": [],
            "latest_non_protocol_codex_message": None,
            "latest_non_protocol_prime_message": None,
        }
    )

    contexts = context_builder.build_contexts(
        bridge,
        agent="codex",
        explicit_refs=["m-1"],
        new_items=[],

        project_dir=tmp_path,
    )

    assert len(contexts) == 1
    assert contexts[0]["canonical_message"]["id"] == "m-1"


def test_build_contexts_preserves_new_then_explicit_order(tmp_path) -> None:
    bridge = _MapBridge(
        {
            "m-new": {
                "canonical_message": {"id": "m-new", "status": "pending", "subject": "New"},
                "thread_correlation_id": "m-new",
                "artifact_refs": [],
                "thread_messages": [],
                "latest_non_protocol_codex_message": None,
                "latest_non_protocol_prime_message": None,
            },
            "m-explicit": {
                "canonical_message": {"id": "m-explicit", "status": "pending", "subject": "Explicit"},
                "thread_correlation_id": "m-explicit",
                "artifact_refs": [],
                "thread_messages": [],
                "latest_non_protocol_codex_message": None,
                "latest_non_protocol_prime_message": None,
            },
        }
    )

    contexts = context_builder.build_contexts(
        bridge,
        agent="codex",
        explicit_refs=["m-explicit"],
        new_items=[{"id": "m-new"}],

        project_dir=tmp_path,
    )

    assert [context["canonical_message"]["id"] for context in contexts] == [
        "m-new",
        "m-explicit",
    ]


def test_build_contexts_caps_context_building_to_dispatch_window(tmp_path) -> None:
    bridge = _MapBridge(
        {
            "m-1": {
                "canonical_message": {"id": "m-1", "status": "pending", "subject": "One"},
                "thread_correlation_id": "m-1",
                "artifact_refs": [],
                "thread_messages": [],
                "latest_non_protocol_codex_message": None,
                "latest_non_protocol_prime_message": None,
            },
            "m-2": {
                "canonical_message": {"id": "m-2", "status": "pending", "subject": "Two"},
                "thread_correlation_id": "m-2",
                "artifact_refs": [],
                "thread_messages": [],
                "latest_non_protocol_codex_message": None,
                "latest_non_protocol_prime_message": None,
            },
            "m-3": {
                "canonical_message": {"id": "m-3", "status": "pending", "subject": "Three"},
                "thread_correlation_id": "m-3",
                "artifact_refs": [],
                "thread_messages": [],
                "latest_non_protocol_codex_message": None,
                "latest_non_protocol_prime_message": None,
            },
        }
    )

    contexts = context_builder.build_contexts(
        bridge,
        agent="codex",
        explicit_refs=[],
        new_items=[{"id": "m-1"}, {"id": "m-2"}, {"id": "m-3"}],

        project_dir=tmp_path,
        max_contexts=2,
    )

    assert [context["canonical_message"]["id"] for context in contexts] == ["m-1", "m-2"]
    assert bridge.calls == ["m-1", "m-2"]


def test_build_prompt_scopes_work_and_requires_structured_corrections(tmp_path) -> None:
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text("{}", encoding="utf-8")

    prompt = context_builder.build_prompt(
        "codex",
        snapshot,
        [{"id": "m-1"}],
        [
            {
                "canonical_message": {"id": "m-1", "status": "failed", "subject": "Malformed request"},
                "thread_correlation_id": "m-1",
                "wake_reasons": ["failed"],
                "latest_non_protocol_codex_message": None,
                "latest_non_protocol_prime_message": None,
                "already_reviewed_hint": False,
                "referenced_artifacts": [],
            }
        ],
        project_dir=tmp_path,
    )

    assert "Process only the target thread summaries plus the pending inbox IDs listed in the canonical bridge snapshot" in prompt
    assert "use `send_correction_message(...)`" in prompt
    assert "do not send freeform correction traffic via `send_message(...)`" in prompt
    assert "Do not send protocol acknowledgements" in prompt


def test_repair_terminal_thread_outputs_sends_valid_peer_message_and_supersedes_failed(tmp_path) -> None:
    report = tmp_path / "INSIGHTS-2026-03-29-TEST-NOTE.md"
    report.write_text("note", encoding="utf-8")
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-1",
                "status": "completed",
                "priority": 2,
                "sender": "prime",
                "recipient": "codex",
                "subject": "Delta review request",
            },
            "thread_correlation_id": "m-1",
            "artifact_refs": [str(report.name)],
            "thread_messages": [
                {
                    "id": "bad-1",
                    "sender": "codex",
                    "recipient": "prime",
                    "message_kind": "substantive",
                    "status": "failed",
                    "subject": "Review complete: NO-GO",
                    "body": "Canonical report: INSIGHTS-2026-03-29-TEST-NOTE.md",
                }
            ],
            "latest_non_protocol_codex_message": None,
            "latest_non_protocol_prime_message": None,
        }
    )

    repaired = context_builder.repair_terminal_thread_outputs(
        bridge,
        agent="codex",
        target_refs=["m-1"],
        project_dir=tmp_path,
    )

    assert repaired == 1
    assert len(bridge.sent_messages) == 1
    sent = bridge.sent_messages[0]
    assert sent["sender"] == "codex"
    assert sent["recipient"] == "prime"
    assert sent["correlation_id"] == "m-1"
    assert sent["payload"]["expected_response"] == "status_update"
    assert sent["payload"]["action_items"]
    assert sent["payload"]["artifact_refs"] == [
        {"type": "file", "path": report.name, "note": "Bridge artifact"}
    ]
    assert bridge.resolved_messages == [
        {
            "message_id": "bad-1",
            "agent": "owner",
            "outcome": "failed",
            "resolution": "Superseded by repaired canonical outbound bridge message repair-1 on thread m-1.",
        }
    ]


def test_repair_terminal_thread_outputs_closes_closure_only_threads_without_peer_resend(tmp_path) -> None:
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-close",
                "status": "pending",
                "priority": 2,
                "sender": "prime",
                "recipient": "codex",
                "subject": "Re: Session start: report current operating state — COMPLETED",
                "body": (
                    "Thread completed with outcome COMPLETED.\n\n"
                    "Closure-only notification. No action required."
                ),
                "tags": ["bridge-sync", "review", "completed"],
            },
            "thread_correlation_id": "m-close",
            "artifact_refs": [],
            "thread_messages": [
                {
                    "id": "bad-close-reply",
                    "sender": "codex",
                    "recipient": "prime",
                    "message_kind": "substantive",
                    "status": "failed",
                    "subject": "Re: Session start: report current operating state — COMPLETED",
                    "body": "Closure-only response should not be re-sent.",
                }
            ],
            "latest_non_protocol_codex_message": None,
            "latest_non_protocol_prime_message": None,
        }
    )

    repaired = context_builder.repair_terminal_thread_outputs(
        bridge,
        agent="codex",
        target_refs=["m-close"],
        project_dir=tmp_path,
    )

    assert repaired == 2
    assert bridge.sent_messages == []
    assert bridge.resolved_messages == [
        {
            "message_id": "m-close",
            "agent": "codex",
            "outcome": "completed",
            "resolution": "Closure-only or receipt-only traffic on previously handled thread. No new action required.",
        },
        {
            "message_id": "bad-close-reply",
            "agent": "owner",
            "outcome": "failed",
            "resolution": "Superseded after closure-only thread cleanup on m-close.",
        },
    ]


def test_fast_path_session_start_requests_replies_without_worker_dispatch(tmp_path) -> None:
    hooks_dir = tmp_path / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / ".bridge-worker-codex-health.json").write_text(
        json.dumps(
            {
                "status": "idle",
                "active_message_ids": [],
            }
        ),
        encoding="utf-8",
    )
    (hooks_dir / ".bridge-worker-prime-health.json").write_text(
        json.dumps(
            {
                "status": "running",
                "active_message_ids": [],
            }
        ),
        encoding="utf-8",
    )
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-session",
                "status": "pending",
                "priority": 1,
                "sender": "prime",
                "recipient": "codex",
                "subject": "Session start: report current operating state",
                "body": "Report your current operating state",
                "artifact_refs": ["AGENTS.md"],
            },
            "thread_correlation_id": "m-session",
            "artifact_refs": ["AGENTS.md"],
            "thread_messages": [],
            "latest_non_protocol_codex_message": None,
            "latest_non_protocol_prime_message": None,
        },
        pending_items=[
            {
                "id": "m-session",
                "subject": "Session start: report current operating state",
            }
        ],
    )

    handled = context_builder.fast_path_session_start_requests(
        bridge,
        agent="codex",
        target_refs=["m-session"],
        project_dir=tmp_path,
    )

    assert handled == 1
    assert len(bridge.sent_messages) == 1
    sent = bridge.sent_messages[0]
    assert sent["subject"] == "Codex operating state: IDLE"
    assert "Bridge inbox: 1 pending message(s)." in sent["body"]
    assert "Peer worker status: RUNNING." in sent["body"]
    assert bridge.resolved_messages == [
        {
            "message_id": "m-session",
            "agent": "codex",
            "outcome": "completed",
            "resolution": "Session-start operating-state reply sent via bridge message repair-1.",
        }
    ]


def test_fast_path_session_start_requests_auto_resolves_session_start_replies(tmp_path) -> None:
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-session-reply",
                "status": "pending",
                "priority": 2,
                "sender": "prime",
                "recipient": "codex",
                "subject": "Prime operating state — session start reply",
                "body": "Prime Builder operating state report.",
            },
            "thread_correlation_id": "m-session-thread",
            "artifact_refs": ["AGENTS.md"],
            "thread_messages": [
                {
                    "id": "m-session-root",
                    "sender": "codex",
                    "recipient": "prime",
                    "subject": "Session start: report current operating state",
                    "body": "Report your current operating state.",
                    "status": "completed",
                },
                {
                    "id": "m-session-reply",
                    "sender": "prime",
                    "recipient": "codex",
                    "subject": "Prime operating state — session start reply",
                    "body": "Prime Builder operating state report.",
                    "status": "pending",
                },
            ],
            "latest_non_protocol_codex_message": {
                "id": "m-session-root",
                "sender": "codex",
                "recipient": "prime",
                "subject": "Session start: report current operating state",
                "body": "Report your current operating state.",
                "status": "completed",
            },
            "latest_non_protocol_prime_message": {
                "id": "m-session-reply",
                "sender": "prime",
                "recipient": "codex",
                "subject": "Prime operating state — session start reply",
                "body": "Prime Builder operating state report.",
                "status": "pending",
            },
        }
    )

    handled = context_builder.fast_path_session_start_requests(
        bridge,
        agent="codex",
        target_refs=["m-session-reply"],
        project_dir=tmp_path,
    )

    assert handled == 1
    assert bridge.sent_messages == []
    assert bridge.resolved_messages == [
        {
            "message_id": "m-session-reply",
            "agent": "codex",
            "outcome": "completed",
            "resolution": "Session-start operating-state reply received automatically. No follow-up reply required.",
        }
    ]


def test_repair_terminal_thread_outputs_closes_ack_only_threads_after_protocol_change(tmp_path) -> None:
    artifact = tmp_path / "CLAUDE.md"
    artifact.write_text("bridge proof", encoding="utf-8")
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-ack",
                "status": "pending",
                "priority": 2,
                "sender": "prime",
                "recipient": "codex",
                "subject": "AUTONOMY-PROOF: Bridge round-trip test",
                "expected_response": "acknowledgement",
                "message_kind": "substantive",
            },
            "thread_correlation_id": "m-ack",
            "artifact_refs": ["CLAUDE.md"],
            "thread_messages": [],
            "latest_non_protocol_codex_message": None,
            "latest_non_protocol_prime_message": None,
        }
    )

    repaired = context_builder.repair_terminal_thread_outputs(
        bridge,
        agent="codex",
        target_refs=["m-ack"],
        project_dir=tmp_path,
    )

    assert repaired == 1
    assert bridge.sent_messages == []
    assert bridge.resolved_messages == [
        {
            "message_id": "m-ack",
            "agent": "codex",
            "outcome": "failed",
            "resolution": "Acknowledgement-only bridge requests are no longer supported. Sender must wait for a substantive reply.",
        }
    ]


def test_repair_terminal_thread_outputs_closes_system_ack_threads_and_supersedes_failed(tmp_path) -> None:
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-system",
                "status": "pending",
                "priority": 2,
                "sender": "prime",
                "recipient": "codex",
                "subject": "Correction: failed bridge message bad-req",
                "expected_response": "acknowledgement",
                "message_kind": "system",
            },
            "thread_correlation_id": "m-system",
            "artifact_refs": [],
            "thread_messages": [
                {
                    "id": "bad-reply",
                    "sender": "codex",
                    "recipient": "prime",
                    "message_kind": "substantive",
                    "status": "failed",
                    "subject": "Malformed correction response",
                    "body": "body",
                }
            ],
            "latest_non_protocol_codex_message": None,
            "latest_non_protocol_prime_message": None,
        }
    )

    repaired = context_builder.repair_terminal_thread_outputs(
        bridge,
        agent="codex",
        target_refs=["m-system"],
        project_dir=tmp_path,
    )

    assert repaired == 2
    assert bridge.sent_messages == []
    assert bridge.resolved_messages == [
        {
            "message_id": "m-system",
            "agent": "codex",
            "outcome": "failed",
            "resolution": "Acknowledgement-only bridge requests are no longer supported. Sender must wait for a substantive reply.",
        },
        {
            "message_id": "bad-reply",
            "agent": "owner",
            "outcome": "failed",
            "resolution": "Superseded after acknowledgement-only thread closure on m-system.",
        },
    ]


def test_context_requires_action_false_for_completed_ack_only_thread_with_protocol_ack() -> None:
    context = {
        "canonical_message": {
            "id": "m-ack-done",
            "status": "completed",
            "sender": "prime",
            "recipient": "codex",
            "subject": "AUTONOMY-PROOF: Bridge round-trip test",
            "expected_response": "acknowledgement",
            "created_at": "2026-04-05T23:41:12+00:00",
        },
        "thread_messages": [
            {
                "id": "accepted-1",
                "sender": "codex",
                "recipient": "prime",
                "message_kind": "protocol_ack",
                "status": "completed",
                "created_at": "2026-04-05T23:41:13+00:00",
            }
        ],
    }

    assert context_builder.context_requires_action("codex", context) is False


def test_select_dispatch_batch_caps_targets_and_preserves_order() -> None:
    contexts = [
        {"canonical_message": {"id": "m-1"}},
        {"canonical_message": {"id": "m-2"}},
        {"canonical_message": {"id": "m-3"}},
    ]
    new_items = [{"id": "m-2"}, {"id": "m-4"}, {"id": "m-3"}, {"id": "m-5"}]

    batch = context_builder.select_dispatch_batch(
        contexts,
        new_items,
        max_targets=2,
    )

    assert batch["target_ids"] == ["m-2", "m-4"]
    assert batch["deferred_ids"] == ["m-3", "m-5", "m-1"]
    assert [item["canonical_message"]["id"] for item in batch["contexts"]] == ["m-2"]
    assert batch["new_items"] == [{"id": "m-2"}, {"id": "m-4"}]
    assert "due_claimed" not in batch  # v3: no claimed state


def test_select_dispatch_batch_prioritizes_session_start_ahead_of_closure_traffic() -> None:
    contexts = [
        {"canonical_message": {"id": "m-handshake"}},
        {"canonical_message": {"id": "m-review"}},
        {"canonical_message": {"id": "m-close"}},
    ]
    new_items = [
        {
            "id": "m-close",
            "subject": "Re: Session start: report current operating state — COMPLETED",
            "body": "Thread completed with outcome COMPLETED.\n\nClosure-only notification. No action required.",
            "priority": 2,
        },
        {
            "id": "m-handshake",
            "subject": "Session start: report current operating state",
            "body": "Report your current operating state",
            "priority": 1,
        },
        {
            "id": "m-review",
            "subject": "Re-review request: bridge fix",
            "body": "Please review the bridge patch.",
            "priority": 2,
        },
    ]

    batch = context_builder.select_dispatch_batch(
        contexts,
        new_items,
        max_targets=2,
    )

    assert batch["target_ids"] == ["m-handshake", "m-review"]
    assert batch["deferred_ids"] == ["m-close"]
    assert [item["id"] for item in batch["new_items"]] == ["m-handshake", "m-review"]
