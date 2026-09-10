"""Current action FIFO, canonical priority and read-only queue preservation."""

import json
from datetime import datetime

import pytest
from psycopg import sql

from platform_tests.groundtruth_kb.test_native_authority_service import native as native
from platform_tests.groundtruth_kb.test_native_authority_service import put, work_fields
from platform_tests.groundtruth_kb.test_native_bridge import bridge as bridge
from platform_tests.groundtruth_kb.test_native_bridge import claim, deliver
from platform_tests.groundtruth_kb.test_native_project_finalization import post, verify

pytestmark = [pytest.mark.integration, pytest.mark.timeout(120)]


def queue(client):
    response = client.get("/v1/bridge/queue", params={"role": "lo"})
    assert response.status_code == 200, response.text
    return response.json()


def add(client, number, **fields):
    result = put(client, "work-items", f"WI-{number}", work_fields(**fields), project_id="PROJECT-1")
    assert result.status_code == 200, result.text


def state(service):
    with service.kernel.transaction(read_only=True) as tx:
        result = {}
        for table in ("bridge_attempts", "bridge_items", "work_intent_claims", "work_items", "projects"):
            tx.cursor.execute(
                sql.SQL("SELECT * FROM {}.{} ORDER BY 1,2").format(sql.Identifier(tx.schema), sql.Identifier(table))
            )
            result[table] = list(tx.cursor.fetchall())
        return result


def test_revision_is_a_new_fifo_action_and_queue_reads_preserve_all_rows(bridge):
    service, client, contexts, _root = bridge
    add(client, 2)
    deliver(client, contexts, "older-attempt", "pb1", 1, "NEW")
    deliver(client, contexts, "older-attempt", "lo1", 2, "NO-GO")
    deliver(client, contexts, "waiting-review", "pb1", 1, "NEW", work_item_id="WI-2")
    deliver(client, contexts, "older-attempt", "pb1", 3, "REVISED")
    before = state(service)
    expected = ["waiting-review", "older-attempt"]
    for _ in range(3):
        assert [r["id"] for r in queue(client)["eligible"]] == expected
        report = client.get("/v1/bridge/state-report").json()
        assert [r["id"] for r in report["queues"]["lo"]["eligible"]] == expected
    assert state(service) == before


def test_canonical_priority_dominates_fifo_and_live_claim_is_excluded(bridge):
    service, client, contexts, _root = bridge
    add(client, 2, priority="P0")
    deliver(client, contexts, "old-p1", "pb1", 1, "NEW")
    deliver(client, contexts, "new-p0", "pb1", 1, "NEW", work_item_id="WI-2")
    assert [r["id"] for r in queue(client)["eligible"]] == ["new-p0", "old-p1"]
    reserved = claim(client, "new-p0", "lo1", 1, "GO", work_item_id="WI-2")
    assert reserved.status_code == 200, reserved.text
    before = state(service)
    assert [r["id"] for r in queue(client)["eligible"]] == ["old-p1"]
    assert state(service) == before
    released = client.post(
        "/v1/bridge/new-p0/release", json={"native_context_id": "lo1", "fence": reserved.json()["fence"]}
    )
    assert released.status_code == 200
    assert [r["id"] for r in queue(client)["eligible"]] == ["new-p0", "old-p1"]


def test_exact_timestamp_ties_use_stable_identity(bridge):
    service, client, contexts, _root = bridge
    add(client, 2)
    deliver(client, contexts, "z-first", "pb1", 1, "NEW")
    deliver(client, contexts, "a-second", "pb1", 1, "NEW", work_item_id="WI-2")
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_items SET created_at=%s").format(sql.Identifier(tx.schema)),
            (datetime.fromisoformat("2026-01-01T00:00:00+00:00"),),
        )
    assert [r["id"] for r in queue(client)["eligible"]] == ["a-second", "z-first"]


def test_fresh_verification_enters_after_waiting_review_and_retry_preserves_age(bridge):
    service, client, contexts, root = bridge
    verify(client, contexts, root, 1, "code.py")
    add(client, 2)
    deliver(client, contexts, "waiting-review", "pb1", 1, "NEW", work_item_id="WI-2")
    (root / "code.py").write_text("changed = 2\n", encoding="utf-8")
    # Exercise the production request operation in its real database transaction.
    from groundtruth_kb.project.native_finalization import NativeProjectFinalization

    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id=%s FOR UPDATE").format(sql.Identifier(tx.schema)),
            ("chain-1",),
        )
        row = dict(tx.cursor.fetchone())
        NativeProjectFinalization._request_verification(tx, [row], "verified_bytes_changed", {"paths": ["code.py"]})
    add(client, 3)
    deliver(client, contexts, "later-review", "pb1", 1, "NEW", work_item_id="WI-3")
    first = queue(client)["eligible"]
    assert [r["id"] for r in first] == ["waiting-review", "chain-1", "later-review"]
    time = first[1]["action_created_at"]
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("SELECT * FROM {}.bridge_attempts WHERE id=%s FOR UPDATE").format(sql.Identifier(tx.schema)),
            ("chain-1",),
        )
        row = dict(tx.cursor.fetchone())
        NativeProjectFinalization._request_verification(tx, [row], "commit_not_confirmed", {"retry": True})
    before = state(service)
    repeated = queue(client)["eligible"]
    assert [r["id"] for r in repeated] == ["waiting-review", "chain-1", "later-review"]
    assert repeated[1]["action_created_at"] == time
    assert state(service) == before


def test_public_commit_preparation_records_one_pending_verification_age(bridge):
    service, client, contexts, root = bridge
    verify(client, contexts, root, 1, "code.py")
    (root / "code.py").write_text("changed = 2\n", encoding="utf-8")
    result = post(client, "prepare-commit")
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "fresh_verification_required"
    first = queue(client)["eligible"][0]["action_created_at"]
    assert datetime.fromisoformat(first).tzinfo is not None
    repeated = post(client, "prepare-commit")
    assert repeated.json()["status"] == "fresh_verification_required"
    assert queue(client)["eligible"][0]["action_created_at"] == first
    before = state(service)
    assert client.get("/v1/bridge/state-report").json()["queues"]["lo"]["eligible"][0]["action_created_at"] == first
    assert state(service) == before


@pytest.mark.parametrize(
    "failure",
    [
        "invalid JSON",
        "{}",
        "null",
        json.dumps({"requested_at": "not-a-date"}),
        json.dumps({"requested_at": "2026-01-01T00:00:00"}),
    ],
)
def test_unknown_verification_age_is_blocked_without_inventing_time(bridge, failure):
    service, client, contexts, root = bridge
    verify(client, contexts, root, 1, "code.py")
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_attempts SET finalization_failure=%s WHERE id=%s").format(
                sql.Identifier(tx.schema)
            ),
            (failure, "chain-1"),
        )
    before = state(service)
    result = queue(client)
    assert not result["eligible"]
    assert result["blocked"][0]["id"] == "chain-1"
    assert result["blocked"][0]["reason"] == "queue_action_time_unavailable"
    assert state(service) == before
