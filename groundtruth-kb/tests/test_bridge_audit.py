# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.audit.

Bridge imports are lazy per tests/test_bridge_import_hygiene.py rule.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def _audit() -> SimpleNamespace:
    """Lazy-import bridge.audit per test_bridge_import_hygiene rule."""
    from groundtruth_kb.bridge.audit import (
        AUDIT_FILENAME,
        emit_audit_event,
        emit_bootstrap_event,
        emit_transition_event,
        read_audit_log,
    )

    return SimpleNamespace(
        AUDIT_FILENAME=AUDIT_FILENAME,
        emit_audit_event=emit_audit_event,
        emit_bootstrap_event=emit_bootstrap_event,
        emit_transition_event=emit_transition_event,
        read_audit_log=read_audit_log,
    )


def test_emit_audit_event_appends_jsonl_line(tmp_path: Path) -> None:
    a = _audit()
    a.emit_audit_event(tmp_path, "test_kind", {"foo": "bar"})
    contents = (tmp_path / a.AUDIT_FILENAME).read_text(encoding="utf-8")
    assert contents.endswith("\n")
    assert '"kind": "test_kind"' in contents
    assert '"foo": "bar"' in contents


def test_emit_multiple_events_produces_multiple_lines(tmp_path: Path) -> None:
    a = _audit()
    a.emit_audit_event(tmp_path, "a", {})
    a.emit_audit_event(tmp_path, "b", {})
    a.emit_audit_event(tmp_path, "c", {})
    lines = (tmp_path / a.AUDIT_FILENAME).read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3


def test_read_audit_log_round_trip(tmp_path: Path) -> None:
    a = _audit()
    a.emit_audit_event(tmp_path, "kind_a", {"k1": "v1"})
    a.emit_audit_event(tmp_path, "kind_b", {"k2": 42})
    events = a.read_audit_log(tmp_path)
    assert len(events) == 2
    assert events[0].kind == "kind_a"
    assert events[0].payload == {"k1": "v1"}
    assert events[1].kind == "kind_b"
    assert events[1].payload == {"k2": 42}


def test_read_audit_log_returns_empty_for_missing_file(tmp_path: Path) -> None:
    a = _audit()
    assert a.read_audit_log(tmp_path) == ()


def test_read_audit_log_skips_malformed_lines(tmp_path: Path) -> None:
    a = _audit()
    audit_file = tmp_path / a.AUDIT_FILENAME
    audit_file.write_text(
        '{"kind": "ok", "ts": "2026-04-28T00:00:00+00:00"}\n'
        "this is not json\n"
        '{"kind": "ok2", "ts": "2026-04-28T00:00:01+00:00"}\n',
        encoding="utf-8",
    )
    events = a.read_audit_log(tmp_path)
    assert len(events) == 2
    assert {e.kind for e in events} == {"ok", "ok2"}


def test_emit_bootstrap_event_records_documents_seen(tmp_path: Path) -> None:
    a = _audit()
    a.emit_bootstrap_event(tmp_path, documents_seen=42)
    [event] = a.read_audit_log(tmp_path)
    assert event.kind == "bootstrap"
    assert event.payload["documents_seen"] == 42
    assert event.payload["transitions_routable"] == 0
    assert event.payload["corrupt_checkpoint_recovered"] is False


def test_emit_bootstrap_event_with_corrupt_recovery(tmp_path: Path) -> None:
    a = _audit()
    a.emit_bootstrap_event(
        tmp_path,
        documents_seen=10,
        corrupt_checkpoint_recovered=True,
        detail="JSON parse failed at line 3",
    )
    [event] = a.read_audit_log(tmp_path)
    assert event.payload["corrupt_checkpoint_recovered"] is True
    assert event.payload["detail"] == "JSON parse failed at line 3"


def test_emit_transition_event_records_routing_outcome(tmp_path: Path) -> None:
    a = _audit()
    a.emit_transition_event(
        tmp_path,
        outcome="routable",
        document_name="foo",
        from_status="NEW",
        to_status="GO",
        to_file="bridge/foo-002.md",
        recipient="prime",
    )
    [event] = a.read_audit_log(tmp_path)
    assert event.kind == "transition"
    assert event.payload["outcome"] == "routable"
    assert event.payload["document_name"] == "foo"
    assert event.payload["from_status"] == "NEW"
    assert event.payload["to_status"] == "GO"
    assert event.payload["to_file"] == "bridge/foo-002.md"
    assert event.payload["recipient"] == "prime"


def test_emit_transition_event_for_new_document_uses_null_from_status(
    tmp_path: Path,
) -> None:
    a = _audit()
    a.emit_transition_event(
        tmp_path,
        outcome="routable",
        document_name="new_doc",
        from_status=None,
        to_status="NEW",
        to_file="bridge/new_doc-001.md",
        recipient="codex",
    )
    [event] = a.read_audit_log(tmp_path)
    assert event.payload["from_status"] is None
    assert event.payload["recipient"] == "codex"
