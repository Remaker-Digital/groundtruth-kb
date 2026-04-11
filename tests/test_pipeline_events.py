"""Tests for pipeline lifecycle events (SPEC-2099).

Covers: event recording (internal + public), atomicity with artifact mutations,
metadata contracts per Codex conditions, query methods, and index coverage.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json

import pytest

from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry


@pytest.fixture
def db(tmp_path) -> KnowledgeDB:
    db_path = tmp_path / "test_events.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


# ===========================================================================
# Public record_event API
# ===========================================================================


class TestRecordEvent:
    """Public API for external event sources (sessions, deploys, etc.)."""

    def test_record_returns_uuid(self, db):
        eid = db.record_event("session_start", "test", session_id="S1")
        assert isinstance(eid, str)
        assert len(eid) == 36  # UUID format

    def test_record_event_queryable(self, db):
        db.record_event("session_start", "test", session_id="S10")
        events = db.list_events(session_id="S10")
        assert len(events) == 1
        assert events[0]["event_type"] == "session_start"
        assert events[0]["changed_by"] == "test"

    def test_record_event_with_metadata(self, db):
        db.record_event("owner_prompt", "test", metadata={"prompt": "Add feature X"})
        events = db.list_events(event_type="owner_prompt")
        assert len(events) == 1
        meta = json.loads(events[0]["metadata"])
        assert meta["prompt"] == "Add feature X"

    def test_record_event_with_artifact(self, db):
        db.record_event("spec_transition", "test", artifact_id="SPEC-99", artifact_type="spec", artifact_version=3)
        events = db.get_events_for_artifact("spec", "SPEC-99")
        assert len(events) == 1
        assert events[0]["artifact_version"] == 3


# ===========================================================================
# Automatic emission from KnowledgeDB mutations
# ===========================================================================


class TestSpecEvents:
    """Events emitted by insert_spec and update_spec."""

    def test_insert_spec_emits_transition(self, db):
        db.insert_spec(id="SPEC-E1", title="T", status="specified", changed_by="test", change_reason="test")
        events = db.get_events_for_artifact("spec", "SPEC-E1")
        assert len(events) == 1
        e = events[0]
        assert e["event_type"] == "spec_transition"
        meta = json.loads(e["metadata"])
        assert meta["from_status"] == "new"
        assert meta["to_status"] == "specified"
        assert meta["change_reason"] == "test"

    def test_update_spec_status_change_emits(self, db):
        db.insert_spec(id="SPEC-E2", title="T", status="specified", changed_by="test", change_reason="create")
        db.update_spec("SPEC-E2", changed_by="test", change_reason="promote", status="implemented")
        events = db.get_events_for_artifact("spec", "SPEC-E2")
        assert len(events) == 2
        meta = json.loads(events[1]["metadata"])
        assert meta["from_status"] == "specified"
        assert meta["to_status"] == "implemented"

    def test_update_spec_no_status_change_no_event(self, db):
        db.insert_spec(id="SPEC-E3", title="T", status="specified", changed_by="test", change_reason="create")
        db.update_spec("SPEC-E3", changed_by="test", change_reason="typo", title="Updated T")
        events = db.get_events_for_artifact("spec", "SPEC-E3")
        assert len(events) == 1  # Only the insert event


class TestWorkItemEvents:
    """Events emitted by insert_work_item and update_work_item."""

    def test_insert_wi_emits_created(self, db):
        db.insert_work_item(
            id="WI-E1",
            title="T",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        events = db.get_events_for_artifact("work_item", "WI-E1")
        assert len(events) == 1
        e = events[0]
        assert e["event_type"] == "wi_created"
        meta = json.loads(e["metadata"])
        assert meta["origin"] == "new"
        assert meta["component"] == "test"
        assert meta["resolution_status"] == "open"

    def test_resolve_wi_emits_resolved(self, db):
        db.insert_work_item(
            id="WI-E2",
            title="T",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        db.update_work_item(
            "WI-E2", changed_by="test", change_reason="done", resolution_status="resolved", stage="resolved"
        )
        events = db.get_events_for_artifact("work_item", "WI-E2")
        assert len(events) == 2
        e = events[1]
        assert e["event_type"] == "wi_resolved"
        meta = json.loads(e["metadata"])
        assert meta["previous_resolution_status"] == "open"
        assert meta["resolution_status"] == "resolved"


class TestTestEvents:
    """Events emitted by insert_test and update_test."""

    def test_insert_test_emits_created(self, db):
        db.insert_spec(id="SPEC-T1", title="S", status="specified", changed_by="test", change_reason="setup")
        db.insert_test(
            id="TEST-E1",
            title="T",
            spec_id="SPEC-T1",
            test_type="unit",
            expected_outcome="pass",
            changed_by="test",
            change_reason="test",
        )
        events = db.get_events_for_artifact("test", "TEST-E1")
        assert len(events) == 1
        e = events[0]
        assert e["event_type"] == "test_created"
        meta = json.loads(e["metadata"])
        assert meta["spec_id"] == "SPEC-T1"
        assert meta["test_type"] == "unit"

    def test_update_test_execution_emits_executed(self, db):
        """Per Codex condition: update_test must emit test_executed when result changes."""
        db.insert_spec(id="SPEC-T2", title="S", status="specified", changed_by="test", change_reason="setup")
        db.insert_test(
            id="TEST-E2",
            title="T",
            spec_id="SPEC-T2",
            test_type="unit",
            expected_outcome="pass",
            changed_by="test",
            change_reason="test",
        )
        db.update_test(
            "TEST-E2",
            changed_by="test",
            change_reason="ran",
            last_result="pass",
            last_executed_at="2026-04-11T00:00:00Z",
        )
        events = db.get_events_for_artifact("test", "TEST-E2")
        assert len(events) == 2
        e = events[1]
        assert e["event_type"] == "test_executed"
        meta = json.loads(e["metadata"])
        assert meta["last_result"] == "pass"
        assert meta["previous_last_result"] is None
        assert meta["last_executed_at"] == "2026-04-11T00:00:00Z"
        assert meta["spec_id"] == "SPEC-T2"
        assert meta["test_type"] == "unit"

    def test_update_test_no_execution_change_no_event(self, db):
        """update_test without execution change must NOT emit test_executed."""
        db.insert_spec(id="SPEC-T3", title="S", status="specified", changed_by="test", change_reason="setup")
        db.insert_test(
            id="TEST-E3",
            title="T",
            spec_id="SPEC-T3",
            test_type="unit",
            expected_outcome="pass",
            changed_by="test",
            change_reason="test",
            last_result="pass",
            last_executed_at="2026-04-11T00:00:00Z",
        )
        db.update_test("TEST-E3", changed_by="test", change_reason="rename", title="Renamed T")
        events = db.get_events_for_artifact("test", "TEST-E3")
        assert len(events) == 1  # Only test_created, no test_executed


class TestAssertionRunEvents:
    """Events emitted by insert_assertion_run."""

    def test_assertion_run_emits_event(self, db):
        db.insert_spec(id="SPEC-A1", title="S", status="specified", changed_by="test", change_reason="setup")
        db.insert_assertion_run("SPEC-A1", 1, True, [{"result": "pass"}], "test-runner")
        events = db.get_events_for_artifact("spec", "SPEC-A1")
        # Should have spec_transition + assertion_run
        assertion_events = [e for e in events if e["event_type"] == "assertion_run"]
        assert len(assertion_events) == 1
        meta = json.loads(assertion_events[0]["metadata"])
        assert meta["overall_passed"] is True
        assert meta["triggered_by"] == "test-runner"
        assert meta["result_count"] == 1


# ===========================================================================
# Atomicity: events must be in same transaction as mutations
# ===========================================================================


class TestAtomicity:
    """Per Codex P1 condition: events share the same DB transaction as the artifact."""

    def test_spec_event_shares_transaction(self, db):
        """If insert_spec succeeds, the event must exist. No separate commit."""
        db.insert_spec(id="SPEC-AT1", title="T", status="specified", changed_by="test", change_reason="test")
        # Event must exist immediately (same commit)
        events = db.get_events_for_artifact("spec", "SPEC-AT1")
        assert len(events) == 1

    def test_event_count_matches_mutations(self, db):
        """Each mutation produces exactly one event (not zero, not two)."""
        db.insert_spec(id="SPEC-AT2", title="T", status="specified", changed_by="test", change_reason="create")
        db.update_spec("SPEC-AT2", changed_by="test", change_reason="promote", status="implemented")
        db.insert_work_item(
            id="WI-AT1",
            title="T",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        db.insert_test(
            id="TEST-AT1",
            title="T",
            spec_id="SPEC-AT2",
            test_type="unit",
            expected_outcome="pass",
            changed_by="test",
            change_reason="test",
        )
        db.update_test(
            "TEST-AT1", changed_by="test", change_reason="ran", last_result="pass", last_executed_at="2026-04-11"
        )
        s = db.get_summary()
        # 2 spec events + 1 WI + 1 test_created + 1 test_executed = 5
        assert s["pipeline_event_count"] == 5


# ===========================================================================
# Query methods
# ===========================================================================


class TestQueryMethods:
    """list_events and get_events_for_artifact query coverage."""

    def test_list_events_filter_by_type(self, db):
        db.record_event("session_start", "t", session_id="S1")
        db.record_event("session_end", "t", session_id="S1")
        db.record_event("session_start", "t", session_id="S2")
        events = db.list_events(event_type="session_start")
        assert len(events) == 2

    def test_list_events_filter_by_session(self, db):
        db.record_event("session_start", "t", session_id="S1")
        db.record_event("session_start", "t", session_id="S2")
        events = db.list_events(session_id="S1")
        assert len(events) == 1

    def test_list_events_limit(self, db):
        for i in range(20):
            db.record_event("test_event", "t", session_id=f"S{i}")
        events = db.list_events(limit=5)
        assert len(events) == 5

    def test_get_events_for_artifact_chronological(self, db):
        db.insert_spec(id="SPEC-Q1", title="T", status="specified", changed_by="test", change_reason="v1")
        db.update_spec("SPEC-Q1", changed_by="test", change_reason="v2", status="implemented")
        events = db.get_events_for_artifact("spec", "SPEC-Q1")
        assert len(events) == 2
        # Must be chronological (ASC)
        assert events[0]["timestamp"] <= events[1]["timestamp"]

    def test_get_events_for_artifact_empty(self, db):
        events = db.get_events_for_artifact("spec", "NONEXISTENT")
        assert events == []


# ===========================================================================
# Metadata contract assertions (per Codex condition)
# ===========================================================================


class TestMetadataContracts:
    """Verify required metadata fields per Codex review conditions."""

    def test_spec_transition_metadata(self, db):
        db.insert_spec(id="SPEC-M1", title="T", status="specified", changed_by="test", change_reason="reason1")
        events = db.get_events_for_artifact("spec", "SPEC-M1")
        meta = json.loads(events[0]["metadata"])
        assert "from_status" in meta
        assert "to_status" in meta
        assert "change_reason" in meta

    def test_wi_created_metadata(self, db):
        db.insert_work_item(
            id="WI-M1",
            title="T",
            origin="defect",
            component="api",
            resolution_status="open",
            priority="P1",
            source_spec_id="SPEC-99",
            source_test_id="TEST-99",
            changed_by="test",
            change_reason="test",
        )
        events = db.get_events_for_artifact("work_item", "WI-M1")
        meta = json.loads(events[0]["metadata"])
        assert meta["origin"] == "defect"
        assert meta["component"] == "api"
        assert meta["priority"] == "P1"
        assert meta["resolution_status"] == "open"
        assert meta["source_spec_id"] == "SPEC-99"
        assert meta["source_test_id"] == "TEST-99"

    def test_wi_resolved_metadata_includes_previous(self, db):
        db.insert_work_item(
            id="WI-M2",
            title="T",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        db.update_work_item(
            "WI-M2", changed_by="test", change_reason="done", resolution_status="resolved", stage="resolved"
        )
        events = db.get_events_for_artifact("work_item", "WI-M2")
        meta = json.loads(events[1]["metadata"])
        assert meta["previous_resolution_status"] == "open"
        assert meta["resolution_status"] == "resolved"

    def test_test_executed_metadata(self, db):
        db.insert_spec(id="SPEC-M2", title="S", status="specified", changed_by="test", change_reason="setup")
        db.insert_test(
            id="TEST-M1",
            title="T",
            spec_id="SPEC-M2",
            test_type="e2e",
            expected_outcome="pass",
            test_file="tests/test_foo.py",
            changed_by="test",
            change_reason="test",
        )
        db.update_test(
            "TEST-M1", changed_by="test", change_reason="ran", last_result="fail", last_executed_at="2026-04-11"
        )
        events = db.get_events_for_artifact("test", "TEST-M1")
        exec_events = [e for e in events if e["event_type"] == "test_executed"]
        assert len(exec_events) == 1
        meta = json.loads(exec_events[0]["metadata"])
        assert meta["spec_id"] == "SPEC-M2"
        assert meta["test_type"] == "e2e"
        assert meta["test_file"] == "tests/test_foo.py"
        assert meta["previous_last_result"] is None
        assert meta["last_result"] == "fail"
        assert meta["last_executed_at"] == "2026-04-11"

    def test_assertion_run_metadata(self, db):
        db.insert_spec(id="SPEC-M3", title="S", status="specified", changed_by="test", change_reason="setup")
        db.insert_assertion_run("SPEC-M3", 1, False, [{"a": 1}, {"a": 2}], "ci")
        events = db.get_events_for_artifact("spec", "SPEC-M3")
        ar_events = [e for e in events if e["event_type"] == "assertion_run"]
        meta = json.loads(ar_events[0]["metadata"])
        assert meta["overall_passed"] is False
        assert meta["triggered_by"] == "ci"
        assert meta["result_count"] == 2


# ===========================================================================
# Summary integration
# ===========================================================================


class TestSummary:
    def test_summary_includes_event_count(self, db):
        s = db.get_summary()
        assert "pipeline_event_count" in s
        assert s["pipeline_event_count"] == 0
        db.record_event("test", "t")
        s = db.get_summary()
        assert s["pipeline_event_count"] == 1


# ===========================================================================
# Repair 1: Export includes pipeline_events (Codex P1)
# ===========================================================================


class TestExport:
    """pipeline_events must be preserved in export_json()."""

    def test_export_includes_pipeline_events(self, db, tmp_path):
        db.record_event("session_start", "test", session_id="S1")
        db.insert_spec(id="SPEC-EX1", title="T", status="specified", changed_by="test", change_reason="test")
        output = tmp_path / "export.json"
        db.export_json(output_path=output)
        data = json.loads(output.read_text(encoding="utf-8"))
        assert "pipeline_events" in data["tables"], "pipeline_events missing from export"
        assert len(data["tables"]["pipeline_events"]) >= 2  # session_start + spec_transition


# ===========================================================================
# Repair 2: Non-resolution WI updates must NOT emit events (Codex P1)
# ===========================================================================


class TestWINonResolutionNoEvent:
    """title/priority edits must not emit wi_created or wi_resolved."""

    def test_priority_edit_no_event(self, db):
        db.insert_work_item(
            id="WI-NR1",
            title="T",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        db.update_work_item("WI-NR1", changed_by="test", change_reason="reprioritize", priority="P1")
        events = db.get_events_for_artifact("work_item", "WI-NR1")
        assert len(events) == 1, f"Non-resolution edit should not emit: got {len(events)} events"
        assert events[0]["event_type"] == "wi_created"

    def test_title_edit_no_event(self, db):
        db.insert_work_item(
            id="WI-NR2",
            title="Old",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        db.update_work_item("WI-NR2", changed_by="test", change_reason="rename", title="New")
        events = db.get_events_for_artifact("work_item", "WI-NR2")
        assert len(events) == 1, "Title edit should not emit event"

    def test_already_resolved_re_update_no_duplicate(self, db):
        """Re-updating a resolved WI should not emit another wi_resolved."""
        db.insert_work_item(
            id="WI-NR3",
            title="T",
            origin="new",
            component="test",
            resolution_status="open",
            changed_by="test",
            change_reason="test",
        )
        db.update_work_item(
            "WI-NR3",
            changed_by="test",
            change_reason="done",
            resolution_status="resolved",
            stage="resolved",
        )
        db.update_work_item("WI-NR3", changed_by="test", change_reason="note", title="Updated")
        events = db.get_events_for_artifact("work_item", "WI-NR3")
        resolved_events = [e for e in events if e["event_type"] == "wi_resolved"]
        assert len(resolved_events) == 1, "Should only have one wi_resolved event"


# ===========================================================================
# Repair 4: Index assertions + rollback atomicity (Codex P2)
# ===========================================================================


class TestIndexes:
    """Verify pipeline_events indexes exist in the schema."""

    def test_event_type_timestamp_index_exists(self, db):
        conn = db._get_conn()
        indexes = {r[1] for r in conn.execute("PRAGMA index_list('pipeline_events')").fetchall()}
        assert "idx_pe_event_type_ts" in indexes

    def test_artifact_index_exists(self, db):
        conn = db._get_conn()
        indexes = {r[1] for r in conn.execute("PRAGMA index_list('pipeline_events')").fetchall()}
        assert "idx_pe_artifact" in indexes

    def test_session_timestamp_index_exists(self, db):
        conn = db._get_conn()
        indexes = {r[1] for r in conn.execute("PRAGMA index_list('pipeline_events')").fetchall()}
        assert "idx_pe_session_ts" in indexes


class TestRollbackAtomicity:
    """Artifact mutation + event write must be atomic: _record_event failure rolls back both."""

    def test_event_failure_rollback_prevents_orphan_artifact(self, db, monkeypatch):
        """Regression: _record_event() failure must roll back the artifact mutation.

        Before the fix: the artifact row stayed in the open transaction and could
        be committed by a later successful insert_spec() on the same connection,
        leaving an artifact with no matching pipeline_events row.

        After the fix: rollback-on-exception in insert_spec ensures the failed
        artifact is never visible on the same connection, cannot be committed by
        a later successful mutation, and is absent after database reopen.

        This test fails against the defective pre-fix behavior.
        """
        original_record_event = KnowledgeDB._record_event

        def raising_record_event(*args, **kwargs):
            raise RuntimeError("forced event failure for atomicity test")

        # Phase 1: force _record_event to raise, attempt insert_spec
        monkeypatch.setattr(KnowledgeDB, "_record_event", staticmethod(raising_record_event))
        with pytest.raises(RuntimeError, match="forced event failure"):
            db.insert_spec(
                id="SPEC-FAIL1",
                title="Should be rolled back",
                status="specified",
                changed_by="test",
                change_reason="atomicity regression test",
            )

        # Phase 2: restore _record_event, verify same-connection state
        monkeypatch.setattr(KnowledgeDB, "_record_event", staticmethod(original_record_event))

        # Failed artifact must not be visible on the same connection after rollback
        assert db.get_spec("SPEC-FAIL1") is None, (
            "Failed artifact must not be visible on same connection after _record_event rollback"
        )

        # Phase 3: perform a later successful insert on the same connection
        db.insert_spec(
            id="SPEC-OK1",
            title="Successful insert after failure",
            status="specified",
            changed_by="test",
            change_reason="atomicity regression test — success path",
        )

        # The failed artifact must NOT have been committed by the later successful operation
        assert db.get_spec("SPEC-FAIL1") is None, (
            "Failed artifact must not be persisted by a later successful commit on the same connection"
        )
        orphan_events = db.get_events_for_artifact("spec", "SPEC-FAIL1")
        assert len(orphan_events) == 0, "No orphan pipeline_events row for the failed artifact"

        # The successful insert must have committed normally
        assert db.get_spec("SPEC-OK1") is not None
        ok_events = db.get_events_for_artifact("spec", "SPEC-OK1")
        assert len(ok_events) == 1
        assert ok_events[0]["event_type"] == "spec_transition"

        # Phase 4: reopen the database and verify persistent state
        db2 = KnowledgeDB(db_path=db.db_path)
        assert db2.get_spec("SPEC-FAIL1") is None, "Failed artifact absent after database reopen"
        reopen_orphan_events = db2.get_events_for_artifact("spec", "SPEC-FAIL1")
        assert len(reopen_orphan_events) == 0, "No orphan pipeline_events row after database reopen"

    def test_insert_creates_both_artifact_and_event(self, db):
        """Verify that after a successful insert, both artifact and event exist."""
        db.insert_spec(id="SPEC-AT1", title="T", status="specified", changed_by="test", change_reason="test")
        assert db.get_spec("SPEC-AT1") is not None
        events = db.get_events_for_artifact("spec", "SPEC-AT1")
        assert len(events) == 1
        assert events[0]["event_type"] == "spec_transition"
