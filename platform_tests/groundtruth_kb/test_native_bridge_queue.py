"""Current action FIFO, canonical priority and read-only queue preservation."""

import json
from datetime import datetime
from pathlib import Path

import pytest
from groundtruth_kb.bridge.native import NativeBridgeService
from groundtruth_kb.dashboard_swimlane import _snapshot_from_report
from psycopg import sql

from platform_tests.groundtruth_kb.bridge_fixtures import bridge as bridge
from platform_tests.groundtruth_kb.bridge_fixtures import claim, deliver
from platform_tests.groundtruth_kb.finalization_fixtures import commit_product, post, two_members, verify
from platform_tests.groundtruth_kb.native_fixtures import native as native
from platform_tests.groundtruth_kb.native_fixtures import put, work_fields

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


def report(client):
    response = client.get("/v1/bridge/state-report")
    assert response.status_code == 200, response.text
    return response.json()


def test_report_empty_is_a_timestamped_observation_and_preserves_state(bridge):
    service, client, _, _ = bridge
    before = state(service)
    result = report(client)
    assert datetime.fromisoformat(result.pop("observed_at")).tzinfo is not None
    assert result == {
        "attempts": [],
        "attempt_counts": {},
        "unfiled_attempt_count": 0,
        "active_status_mix": [],
        "active_claim_count": 0,
        "queues": {role: {"role": role, "eligible": [], "blocked": []} for role in ("pb", "lo")},
    }
    assert state(service) == before


def test_report_includes_unfiled_and_advisory_without_claiming_work_ownership(bridge):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "z-advisory", "lo1", 1, "ADVISORY", work_item_id=None)
    reserved = claim(client, "a-unfiled", "pb1", 0, "NEW")
    assert reserved.status_code == 200, reserved.text
    before = state(service)
    result = report(client)
    assert [row["id"] for row in result["attempts"]] == ["a-unfiled", "z-advisory"]
    assert result["attempt_counts"] == {"active": 2}
    assert result["active_status_mix"] == [{"status": "ADVISORY", "count": 1}]
    assert result["unfiled_attempt_count"] == result["active_claim_count"] == 1
    unfiled, advisory = result["attempts"]
    assert set(unfiled) == {
        "id",
        "work_item_id",
        "project_id",
        "head_version",
        "head_status",
        "disposition",
        "created_at",
        "closed_at",
        "terminal_commit",
        "head_created_at",
        "next_artifact_claim",
    }
    assert unfiled["work_item_id"] == "WI-1" and unfiled["project_id"] == "PROJECT-1"
    assert unfiled["head_version"] == 0 and unfiled["head_status"] is None
    assert unfiled["head_created_at"] is None and unfiled["terminal_commit"] is None
    assert unfiled["next_artifact_claim"] == {
        "next_version": 1,
        "intended_status": "NEW",
        "expires_at": reserved.json()["expires_at"],
    }
    assert advisory["work_item_id"] is None and advisory["project_id"] is None
    assert advisory["next_artifact_claim"] is None and advisory["head_status"] == "ADVISORY"
    assert advisory["disposition"] == "active"
    for role in ("pb", "lo"):
        assert result["queues"][role] == {"role": role, "eligible": [], "blocked": []}
    # A report has no delivery capability, author/context identifiers or payload.
    assert "Authored content" not in json.dumps(result)
    assert state(service) == before
    repeated = report(client)
    repeated.pop("observed_at")
    result.pop("observed_at")
    assert repeated == result


def test_report_claim_expiry_exposes_current_head_without_mutating_expired_claim(bridge):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "review", "pb1", 1, "NEW")
    reserved = claim(client, "review", "lo1", 1, "GO")
    assert reserved.status_code == 200, reserved.text
    held = report(client)
    displayed = _snapshot_from_report(held)
    assert displayed["summary"]["active_claim_count"] == 1
    assert displayed["threads"][0]["queue"] is None
    assert held["active_claim_count"] == 1 and held["queues"]["lo"]["eligible"] == []
    assert held["attempts"][0]["next_artifact_claim"]["next_version"] == 2
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second'").format(
                sql.Identifier(tx.schema)
            )
        )
    before = state(service)
    expired = report(client)
    displayed = _snapshot_from_report(expired)
    assert displayed["summary"]["active_claim_count"] == 0
    assert displayed["threads"][0]["queue"] == {"role": "lo", "state": "eligible"}
    assert expired["active_claim_count"] == 0
    assert expired["attempts"][0]["next_artifact_claim"] is None
    assert [row["id"] for row in expired["queues"]["lo"]["eligible"]] == ["review"]
    assert expired["attempts"][0]["head_created_at"] == expired["queues"]["lo"]["eligible"][0]["action_created_at"]
    assert state(service) == before


def test_report_keeps_one_snapshot_when_a_claim_changes_before_queue_read(bridge, monkeypatch):
    service, client, contexts, _ = bridge
    deliver(client, contexts, "review", "pb1", 1, "NEW")
    assert claim(client, "review", "lo1", 1, "GO").status_code == 200
    original = NativeBridgeService._queue
    changed = False

    def change_then_queue(instance, tx, role):
        nonlocal changed
        if not changed:
            with service.kernel.transaction() as other:
                other.cursor.execute(
                    sql.SQL("UPDATE {}.work_intent_claims SET expires_at=clock_timestamp()-interval '1 second'").format(
                        sql.Identifier(other.schema)
                    )
                )
            changed = True
        return original(instance, tx, role)

    monkeypatch.setattr(NativeBridgeService, "_queue", change_then_queue)
    first = report(client)
    assert changed and first["active_claim_count"] == 1
    assert first["attempts"][0]["next_artifact_claim"] is not None
    assert first["queues"]["lo"]["eligible"] == []
    second = report(client)
    assert second["active_claim_count"] == 0 and second["attempts"][0]["next_artifact_claim"] is None
    assert [row["id"] for row in second["queues"]["lo"]["eligible"]] == ["review"]


def test_report_reads_database_head_time_and_does_not_reconstruct_purged_head(bridge):
    service, client, contexts, root = bridge
    deliver(client, contexts, "withdrawn", "pb1", 1, "NEW")
    known_time = datetime.fromisoformat("2026-01-02T03:04:05+00:00")
    with service.kernel.transaction() as tx:
        tx.cursor.execute(
            sql.SQL("UPDATE {}.bridge_items SET created_at=%s").format(sql.Identifier(tx.schema)), (known_time,)
        )
    # Misleading file evidence cannot change the authoritative report.
    (root / "bridge").mkdir()
    (root / "bridge/withdrawn-099.md").write_text("VERIFIED\n", encoding="utf-8")
    current = report(client)["attempts"][0]
    assert current["head_created_at"] == known_time.isoformat()
    assert current["head_status"] == "NEW" and current["head_version"] == 1
    deliver(client, contexts, "withdrawn", "pb2", 2, "WITHDRAWN")
    before = state(service)
    result = report(client)
    row = result["attempts"][0]
    assert result["attempt_counts"] == {"withdrawn": 1} and result["active_status_mix"] == []
    assert row["disposition"] == "withdrawn" and row["head_status"] == "WITHDRAWN"
    assert row["head_version"] == 2 and row["head_created_at"] is None
    assert datetime.fromisoformat(row["closed_at"]).tzinfo is not None
    assert row["terminal_commit"] is None and row["next_artifact_claim"] is None
    displayed = _snapshot_from_report(result)
    assert displayed["threads"][0]["disposition"] == "withdrawn"
    assert displayed["threads"][0]["age_in_state_minutes"] is None
    assert state(service) == before


def test_report_distinguishes_review_completion_from_confirmed_project_commit(bridge):
    service, _, _, _ = bridge
    client, _, _, parent = two_members(bridge)
    before = state(service)
    reviewed = report(client)
    displayed = _snapshot_from_report(reviewed)
    assert displayed["summary"]["active_count"] == 2 and displayed["summary"]["closed_count"] == 0
    assert all(row["queue"] is None for row in displayed["threads"])
    assert reviewed["attempt_counts"] == {"active": 2}
    assert reviewed["active_status_mix"] == [{"status": "VERIFIED", "count": 2}]
    for row in reviewed["attempts"]:
        assert row["disposition"] == "active" and row["head_status"] == "VERIFIED"
        assert row["terminal_commit"] is None and row["closed_at"] is None
        assert row["head_created_at"] is not None
    assert state(service) == before
    ready = post(client, "prepare-commit").json()
    commit = commit_product(Path(ready["checkout"]["path"]))
    confirmed = post(client, "confirm-commit", commit_id=commit, expected_parent=parent)
    assert confirmed.status_code == 200 and confirmed.json()["status"] == "confirmed"
    before = state(service)
    committed = report(client)
    displayed = _snapshot_from_report(committed)
    assert displayed["summary"]["active_count"] == 0 and displayed["summary"]["closed_count"] == 2
    assert all(row["terminal_commit"] == commit and row["age_in_state_minutes"] is None for row in displayed["threads"])
    assert committed["attempt_counts"] == {"committed": 2} and committed["active_status_mix"] == []
    for row in committed["attempts"]:
        assert row["head_status"] == "VERIFIED" and row["disposition"] == "committed"
        assert row["terminal_commit"] == commit and row["closed_at"] is not None
        assert row["head_created_at"] is None and row["next_artifact_claim"] is None
    assert state(service) == before


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
