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


class _RepairBridge:
    def __init__(self, context: dict) -> None:
        self._context = context
        self.sent_messages: list[dict] = []
        self.resolved_messages: list[dict] = []

    def get_worker_event_payload(self, message_ref: str, agent: str | None = None) -> dict:
        assert message_ref == "m-1"
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
        return {"ok": True, "status": "new", "id": "repair-1"}

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
                "status": "new",
                "subject": "Review note",
            },
            "thread_correlation_id": "m-1",
            "artifact_refs": ["structured-artifact.md"],
            "thread_sla": {"risk_types": ["ack_breach"]},
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
        due_claimed=[],
        project_dir=tmp_path,
    )

    assert len(contexts) == 1
    context = contexts[0]
    assert context["already_reviewed_hint"] is True
    assert set(context["wake_reasons"]) == {"ack_breach", "explicit:m-1", "new"}
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
                "status": "new",
                "subject": "Wrapped payload",
            },
            "thread_correlation_id": "m-1",
            "artifact_refs": ["artifact.md"],
            "thread_sla": {"risk_types": []},
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
        due_claimed=[],
        project_dir=tmp_path,
    )

    assert len(contexts) == 1
    assert contexts[0]["canonical_message"]["id"] == "m-1"


def test_build_prompt_scopes_work_and_requires_structured_corrections(tmp_path) -> None:
    snapshot = tmp_path / "snapshot.json"
    snapshot.write_text("{}", encoding="utf-8")

    prompt = context_builder.build_prompt(
        "codex",
        snapshot,
        [{"id": "m-1"}],
        [],
        [
            {
                "canonical_message": {"id": "m-1", "status": "invalid", "subject": "Malformed request"},
                "thread_correlation_id": "m-1",
                "wake_reasons": ["invalid"],
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


def test_repair_terminal_thread_outputs_sends_valid_peer_message_and_supersedes_invalids(tmp_path) -> None:
    report = tmp_path / "INSIGHTS-2026-03-29-TEST-NOTE.md"
    report.write_text("note", encoding="utf-8")
    bridge = _RepairBridge(
        {
            "canonical_message": {
                "id": "m-1",
                "status": "done",
                "priority": 2,
                "sender": "prime",
                "recipient": "codex",
                "subject": "Delta review request",
            },
            "thread_correlation_id": "m-1",
            "artifact_refs": [str(report.name)],
            "thread_sla": {"risk_types": []},
            "thread_messages": [
                {
                    "id": "bad-1",
                    "sender": "codex",
                    "recipient": "prime",
                    "message_kind": "substantive",
                    "status": "invalid",
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
    assert sent["payload"]["expected_response"] == "acknowledgement"
    assert sent["payload"]["action_items"]
    assert sent["payload"]["artifact_refs"] == [
        {"type": "file", "path": str(report.resolve()), "note": "Bridge artifact"}
    ]
    assert bridge.resolved_messages == [
        {
            "message_id": "bad-1",
            "agent": "owner",
            "outcome": "superseded",
            "resolution": "Superseded by repaired canonical outbound bridge message repair-1 on thread m-1.",
        }
    ]


def test_select_dispatch_batch_caps_targets_and_preserves_order() -> None:
    contexts = [
        {"canonical_message": {"id": "m-1"}},
        {"canonical_message": {"id": "m-2"}},
        {"canonical_message": {"id": "m-3"}},
    ]
    new_items = [{"id": "m-2"}, {"id": "m-4"}]
    due_claimed = [{"id": "m-3"}, {"id": "m-5"}]

    batch = context_builder.select_dispatch_batch(
        contexts,
        new_items,
        due_claimed,
        max_targets=2,
    )

    assert batch["target_ids"] == ["m-1", "m-2"]
    assert batch["deferred_ids"] == ["m-3", "m-4", "m-5"]
    assert [item["canonical_message"]["id"] for item in batch["contexts"]] == ["m-1", "m-2"]
    assert batch["new_items"] == [{"id": "m-2"}]
    assert batch["due_claimed"] == []
