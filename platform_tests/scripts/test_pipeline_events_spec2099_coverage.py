"""SPEC-2099 pipeline-events data-model & collection coverage (WI-3217).

This module is the WI-bridged deterministic coverage for the SPEC-2099
"Pipeline lifecycle metrics: data model and collection" contract, filed through
``bridge/agent-red-wi3217-pipeline-lifecycle-metrics-coverage`` (GO at ``-002``).

It is DELIBERATELY NON-DUPLICATIVE of the existing behavioral suite at
``groundtruth-kb/tests/test_pipeline_events.py``, which already covers the public
``record_event`` API, automatic emission from KnowledgeDB mutations, transaction
atomicity, query methods, metadata contracts, export, and rollback atomicity.
This file targets only the four SPEC-2099 data-model clauses that the existing
suite leaves unasserted:

1. Schema / data-model conformance — the ``pipeline_events`` table carries the
   exact SPEC-2099-required column set with the required PRIMARY KEY and NOT NULL
   constraints (and the additive ``artifact_version`` implementation extension).
2. Append-only / write-once — "This table is append-only, write-once. Events are
   never updated or deleted." (no public update/delete surface; distinct,
   immutable, unique-id rows).
3. ``duration_ms`` round-trip for timed events.
4. Full 17-value ``event_type`` vocabulary acceptance.

A single minimal automatic-emission assertion proves the side-effect collection
path is live; the exhaustive per-mutation emission coverage lives in
``groundtruth-kb/tests/test_pipeline_events.py`` and is referenced, not repeated.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.gates import GateRegistry

# The SPEC-2099 event_type enumeration (17 values).
SPEC_2099_EVENT_TYPES = (
    "session_start",
    "session_end",
    "owner_prompt",
    "owner_decision",
    "codex_proposal_sent",
    "codex_go_received",
    "codex_nogo_received",
    "build_started",
    "staging_deployed",
    "production_deployed",
    "rollback",
    "spec_transition",
    "wi_created",
    "wi_resolved",
    "test_created",
    "test_executed",
    "assertion_run",
)

# The SPEC-2099 required pipeline_events column set (artifact_version is an
# additive implementation extension, asserted separately).
SPEC_2099_REQUIRED_COLUMNS = frozenset(
    {
        "id",
        "event_type",
        "session_id",
        "artifact_id",
        "artifact_type",
        "timestamp",
        "duration_ms",
        "metadata",
        "changed_by",
    }
)


@pytest.fixture
def db(tmp_path) -> KnowledgeDB:
    db_path = tmp_path / "test_spec2099_events.db"
    registry = GateRegistry.from_config([], include_builtins=True)
    return KnowledgeDB(db_path=db_path, gate_registry=registry)


def _columns(db: KnowledgeDB) -> dict[str, dict[str, object]]:
    """Return ``{name: {"type", "notnull", "pk"}}`` from PRAGMA table_info."""
    rows = db._get_conn().execute("PRAGMA table_info('pipeline_events')").fetchall()
    # PRAGMA table_info columns: cid[0], name[1], type[2], notnull[3], dflt[4], pk[5]
    return {r[1]: {"type": r[2], "notnull": r[3], "pk": r[5]} for r in rows}


# ===========================================================================
# Clause 1: Schema / data-model conformance
# ===========================================================================


class TestSchemaConformance:
    """The pipeline_events table matches the SPEC-2099 data model."""

    def test_required_columns_present(self, db):
        cols = set(_columns(db))
        missing = SPEC_2099_REQUIRED_COLUMNS - cols
        assert not missing, f"SPEC-2099 required columns missing: {sorted(missing)}"

    def test_required_not_null_constraints(self, db):
        cols = _columns(db)
        for name in ("id", "event_type", "timestamp", "changed_by"):
            assert cols[name]["notnull"] == 1, f"{name} must be NOT NULL per SPEC-2099"

    def test_id_is_primary_key(self, db):
        cols = _columns(db)
        assert cols["id"]["pk"] >= 1, "id must be the primary key"

    def test_artifact_version_extension_present(self, db):
        # artifact_version is an additive implementation extension beyond the
        # SPEC-2099 column list; the data model recognizes it rather than
        # treating the schema as a closed set.
        assert "artifact_version" in _columns(db)


class TestIndexes:
    """SPEC-2099 collection requires queryable events; assert the indexes exist."""

    def test_required_indexes_present(self, db):
        indexes = {r[1] for r in db._get_conn().execute("PRAGMA index_list('pipeline_events')").fetchall()}
        for idx in ("idx_pe_event_type_ts", "idx_pe_artifact", "idx_pe_session_ts"):
            assert idx in indexes, f"missing index {idx}"


# ===========================================================================
# Clause 2: Append-only / write-once
# ===========================================================================


class TestAppendOnlyWriteOnce:
    """SPEC-2099: events are never updated or deleted."""

    def test_no_public_update_or_delete_surface(self, db):
        for name in (
            "update_event",
            "delete_event",
            "remove_event",
            "update_pipeline_event",
            "delete_pipeline_event",
        ):
            assert not hasattr(db, name), f"SPEC-2099 append-only violated: {name} exists"

    def test_records_are_distinct_unique_id_rows(self, db):
        ids = [db.record_event("test_event", "t", session_id=f"S{i}") for i in range(5)]
        assert len(set(ids)) == 5, "each event must receive a distinct UUID id"
        events = db.list_events(event_type="test_event", limit=100)
        assert len(events) == 5

    def test_prior_row_immutable_after_later_inserts(self, db):
        eid = db.record_event("first_event", "t", session_id="S1", metadata={"k": "v"})
        conn = db._get_conn()
        before = conn.execute("SELECT * FROM pipeline_events WHERE id = ?", (eid,)).fetchone()
        for i in range(3):
            db.record_event("later_event", "t", session_id=f"L{i}")
        after = conn.execute("SELECT * FROM pipeline_events WHERE id = ?", (eid,)).fetchone()
        assert tuple(before) == tuple(after), "a prior event row must be byte-stable after later inserts"


# ===========================================================================
# Clause 3: duration_ms round-trip
# ===========================================================================


class TestDurationMs:
    """SPEC-2099 lists duration_ms for timed events."""

    def test_duration_ms_round_trip(self, db):
        db.record_event("build_started", "t", session_id="S1", duration_ms=1234)
        ev = db.list_events(event_type="build_started")[0]
        assert ev["duration_ms"] == 1234

    def test_duration_ms_null_when_omitted(self, db):
        db.record_event("session_start", "t", session_id="S2")
        ev = db.list_events(event_type="session_start")[0]
        assert ev["duration_ms"] is None


# ===========================================================================
# Clause 4: full event_type vocabulary
# ===========================================================================


class TestEventTypeVocabulary:
    """All 17 SPEC-2099 enumerated event types are recordable and queryable."""

    def test_enumeration_has_17_types(self):
        assert len(SPEC_2099_EVENT_TYPES) == 17

    def test_all_enumerated_event_types_recordable_and_queryable(self, db):
        for et in SPEC_2099_EVENT_TYPES:
            db.record_event(et, "t", session_id="vocab")
        for et in SPEC_2099_EVENT_TYPES:
            rows = db.list_events(event_type=et, limit=10)
            assert any(r["event_type"] == et for r in rows), f"{et} not recordable/queryable"


# ===========================================================================
# Collection mechanism (minimal side-effect contract; non-duplicative)
# ===========================================================================


class TestCollectionSideEffect:
    """A representative automatic emission proves the side-effect path is live.

    Exhaustive per-mutation emission coverage (insert/update spec, work_item,
    test, assertion_run) lives in ``groundtruth-kb/tests/test_pipeline_events.py``
    and is intentionally NOT duplicated here.
    """

    def test_insert_spec_emits_spec_transition_side_effect(self, db):
        db.insert_spec(
            id="SPEC-COV2099",
            title="Coverage probe",
            status="specified",
            changed_by="t",
            change_reason="spec2099 coverage side-effect probe",
        )
        events = db.get_events_for_artifact("spec", "SPEC-COV2099")
        assert len(events) == 1
        assert events[0]["event_type"] == "spec_transition"
