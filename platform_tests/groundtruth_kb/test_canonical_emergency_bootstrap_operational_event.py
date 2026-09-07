from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from groundtruth_kb.operational_event import OperationalEventError, OperationalEventService


def _body(state: str = "declared") -> dict[str, object]:
    return {
        "bundle_id": "bundle-26efc112",
        "bundle_digest": "26efc11249c7d6b8d2d7e21bf8e4e995465427344d9153bdba8a5462588284a5",
        "lifecycle_state": state,
        "carrier_graph": ["WI-7164", "WI-7167", "WI-7170", "WI-7173", "WI-7176", "WI-7179"],
        "work_item_id": "WI-7164",
        "project_id": "PROJECT-GTKB-OPERATIONAL-EVENT-WRITER-SELF-BOOTSTRAP",
        "formal_ids": ["GOV-GTKB-EMERGENCY-BOOTSTRAP-001"],
        "targets": ["groundtruth-kb/src/groundtruth_kb/operational_event.py"],
        "allowed_effects": ["writer_repair"],
        "non_goals": ["WI-7073-import"],
        "preimages": {"operational_event.py": "MISSING"},
        "expected_postimages": {"operational_event.py": "implemented"},
        "tests": ["TEST-12226"],
        "containment": "stop on mismatch",
        "owner_act": "DELIB-20260826173005-v3",
        "proposal": "v009",
        "review": "v010",
        "recorded_immediately_after_writer_restoration": True,
    }


def test_wi7164_canonical_emergency_bootstrap_operational_event(tmp_path: Path) -> None:
    db_path = tmp_path / "events.db"
    service = OperationalEventService(db_path)
    created = service.create("OE-WI7164", _body(), "idem-create", "pb-session")
    assert created["version"] == 1
    assert service.show("OE-WI7164") == created
    assert service.inspect("OE-WI7164")["versions"] == 1
    assert service.verify("OE-WI7164")["valid"] is True

    assert service.create("OE-WI7164", _body(), "idem-create", "pb-session") == created
    with pytest.raises(OperationalEventError, match="idempotency_conflict"):
        service.create("OE-WI7164", {**_body(), "extra": True}, "idem-create", "pb-session")

    appended = service.append(
        "OE-WI7164",
        1,
        {**_body("carrier_effects_recorded_pending_independent_verification"), "results": ["PASS"]},
        "idem-append",
        "pb-session",
    )
    assert appended["version"] == 2
    with pytest.raises(OperationalEventError, match="stale_version"):
        service.append("OE-WI7164", 1, _body(), "different", "pb-session")

    with sqlite3.connect(db_path) as connection:
        before = connection.execute("SELECT COUNT(*) FROM operational_events").fetchone()[0]
        with pytest.raises(sqlite3.DatabaseError):
            connection.execute("UPDATE operational_events SET id='changed'")
        after = connection.execute("SELECT COUNT(*) FROM operational_events").fetchone()[0]
    assert before == after == 2
    assert json.loads(appended["body_json"])["bundle_id"] == "bundle-26efc112"
