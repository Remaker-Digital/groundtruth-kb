"""TEST-11981 — governed durable TEST artifact update service."""

from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path

import groundtruth_kb.test_artifact_update as update_module
import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.db import SCHEMA_VERSION, KnowledgeDB
from groundtruth_kb.test_artifact_update import TestArtifactUpdateRequest as ArtifactUpdateRequest
from groundtruth_kb.test_artifact_update import update_test_artifact

PROJECT_ID = "PROJECT-TEST-WRITER"
WORK_ITEM_ID = "WI-TEST-WRITER"
BRIDGE_SLUG = "test-artifact-update-fixture"
SESSION_ID = "fixture-session-context"
SPEC_ID = "DCL-TEST-WRITER-001"
TEST_ID = "TEST-ARTIFACT-001"
RELATED_TEST_ID = "TEST-ARTIFACT-002"


def _future(minutes: int = 30) -> str:
    return (datetime.now(UTC) + timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def _past(minutes: int = 30) -> str:
    return (datetime.now(UTC) - timedelta(minutes=minutes)).isoformat().replace("+00:00", "Z")


def _write_bridge(root: Path, targets: list[str] | None = None) -> None:
    targets = [TEST_ID] if targets is None else targets
    bridge = root / "bridge"
    bridge.mkdir(exist_ok=True)
    (bridge / f"{BRIDGE_SLUG}-001.md").write_text(
        "\n".join(
            [
                "NEW",
                "::init gtkb lo",
                "::open build",
                "",
                "bridge_kind: implementation_proposal",
                f"Document: {BRIDGE_SLUG}",
                "Version: 001",
                f"Project: {PROJECT_ID}",
                f"Work Item: {WORK_ITEM_ID}",
                f"test_artifact_targets: {json.dumps(targets)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bridge / f"{BRIDGE_SLUG}-002.md").write_text(
        "\n".join(
            [
                "GO",
                "::init gtkb pb",
                "::open build",
                "",
                "bridge_kind: lo_verdict",
                f"Document: {BRIDGE_SLUG}",
                "Version: 002",
                f"Responds to: bridge/{BRIDGE_SLUG}-001.md",
                f"Project: {PROJECT_ID}",
                f"Work Item: {WORK_ITEM_ID}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _seed_db(path: Path) -> None:
    db = KnowledgeDB(db_path=path)
    db.insert_spec(
        id=SPEC_ID,
        title="Test writer authority",
        status="active",
        changed_by="fixture",
        change_reason="fixture",
        type="design_constraint",
    )
    db.insert_test(
        id=TEST_ID,
        title="Original title",
        spec_id=SPEC_ID,
        test_type="integration",
        test_file="tests/original.py",
        test_function="test_original",
        description="before",
        expected_outcome="original expectation",
        application_scope="gtkb_platform",
        changed_by="fixture",
        change_reason="fixture",
    )
    db.insert_test(
        id=RELATED_TEST_ID,
        title="Unrelated title",
        spec_id=SPEC_ID,
        test_type="unit",
        description="unrelated",
        expected_outcome="unrelated expectation",
        application_scope="gtkb_platform",
        changed_by="fixture",
        change_reason="fixture",
    )
    conn = db._get_conn()
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    conn.execute(
        """INSERT INTO projects
           (id, version, name, status, changed_by, changed_at, change_reason)
           VALUES (?, 1, ?, 'active', 'fixture', ?, 'fixture')""",
        (PROJECT_ID, PROJECT_ID, now),
    )
    conn.execute(
        """INSERT INTO work_items
           (id, version, title, origin, component, resolution_status, stage,
            changed_by, changed_at, change_reason)
           VALUES (?, 1, ?, 'fixture', 'test-writer', 'open', 'backlogged',
                   'fixture', ?, 'fixture')""",
        (WORK_ITEM_ID, WORK_ITEM_ID, now),
    )
    conn.execute(
        """INSERT INTO project_work_item_memberships
           (id, version, project_id, work_item_id, membership_role, membership_order,
            status, changed_by, changed_at, change_reason)
           VALUES (?, 1, ?, ?, 'execution_authority', 1, 'active', 'fixture', ?, 'fixture')""",
        (f"PWM-{WORK_ITEM_ID}", PROJECT_ID, WORK_ITEM_ID, now),
    )
    conn.execute(
        """INSERT INTO work_intent_claims
           (thread_slug, session_id, acquired_at, ttl_expires_at, claim_kind,
            acting_role, session_envelope_id, acting_role_attestation, project_id,
            implementation_deadline, implementation_grace_expires_at, work_item_id)
           VALUES (?, ?, ?, ?, 'go_implementation', 'prime-builder', 'SENV-fixture',
                   'role-attestation:fixture', ?, ?, ?, ?)""",
        (BRIDGE_SLUG, SESSION_ID, now, _future(), PROJECT_ID, _future(), _future(), WORK_ITEM_ID),
    )
    conn.commit()
    db.close()


@pytest.fixture()
def service_env(tmp_path: Path) -> tuple[Path, Path]:
    db_path = tmp_path / "groundtruth.db"
    _seed_db(db_path)
    _write_bridge(tmp_path)
    return tmp_path, db_path


def _request(
    *,
    key: str = "request-1",
    test_id: str = TEST_ID,
    dry_run: bool = False,
    **updates: object,
) -> ArtifactUpdateRequest:
    return ArtifactUpdateRequest(
        test_id=test_id,
        expected_version=1,
        idempotency_key=key,
        project_id=PROJECT_ID,
        work_item_id=WORK_ITEM_ID,
        bridge_slug=BRIDGE_SLUG,
        actor_session_context_id=SESSION_ID,
        changed_by="fixture-prime-builder",
        change_reason="exercise TEST-11981",
        updates={"title": "Updated title", **updates},
        dry_run=dry_run,
    )


def _insert_project_dependency(
    conn: sqlite3.Connection,
    *,
    dependency_id: str,
    prerequisite_status: str,
    dependency_kind: str,
    required_state: str,
    now: str,
    affected_gate: str = "readiness",
) -> None:
    prerequisite_id = f"PROJECT-PREREQUISITE-{dependency_id}"
    conn.execute(
        """INSERT INTO projects
           (id, version, name, status, changed_by, changed_at, change_reason)
           VALUES (?, 1, ?, ?, 'fixture', ?, 'fixture')""",
        (prerequisite_id, prerequisite_id, prerequisite_status, now),
    )
    conn.execute(
        """INSERT INTO project_dependencies
           (id, version, from_project_id, to_project_id, dependency_type,
            dependent_project_id, prerequisite_project_id, dependency_kind,
            required_prerequisite_state, affected_gate, provenance,
            registry_version, blocking_status, status, changed_by,
            changed_at, change_reason)
           VALUES (?, 1, ?, ?, 'depends_on', ?, ?, ?, ?, ?,
                   'fixture', 1, 'open', 'active', 'fixture', ?, 'fixture')""",
        (
            dependency_id,
            PROJECT_ID,
            prerequisite_id,
            PROJECT_ID,
            prerequisite_id,
            dependency_kind,
            required_state,
            affected_gate,
            now,
        ),
    )


def test_dry_run_returns_complete_postimage_and_zero_effect(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    result = update_test_artifact(db, _request(dry_run=True, description=None), project_root=root)

    assert result.status == "dry_run"
    assert result.postimage is not None
    assert set(result.postimage) == {
        "application_scope",
        "change_reason",
        "changed_by",
        "description",
        "expected_outcome",
        "id",
        "last_executed_at",
        "last_result",
        "spec_id",
        "test_class",
        "test_file",
        "test_function",
        "test_type",
        "title",
        "version",
    }
    assert result.postimage["description"] is None
    assert result.evidence["request_schema_version"] == 1
    assert result.evidence["idempotency_collision"] is False
    assert len(db.get_test_history(TEST_ID)) == 1
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


def test_apply_restart_replay_and_later_version_coexistence(service_env) -> None:
    root, db_path = service_env
    request = _request(description=None)
    db = KnowledgeDB(db_path=db_path)
    unrelated_before = db.get_test(RELATED_TEST_ID)
    applied = update_test_artifact(db, request, project_root=root)
    assert applied.status == "applied"
    assert applied.row is not None and applied.row["version"] == 2
    assert applied.row["description"] is None
    assert db.get_test(RELATED_TEST_ID) == unrelated_before
    db.close()

    later = KnowledgeDB(db_path=db_path)
    later._seed_test_version_for_test_only(
        TEST_ID,
        "fixture",
        "later independent version",
        expected_outcome="Later independent outcome",
    )
    assert later.get_test(TEST_ID)["version"] == 3
    later.close()

    for bridge_file in (root / "bridge").glob("*.md"):
        bridge_file.unlink()

    restarted = KnowledgeDB(db_path=db_path)
    replay = update_test_artifact(restarted, request, project_root=root)
    assert replay.status == "replay"
    assert replay.replayed is True
    assert replay.row is not None and replay.row["version"] == 2
    assert len(restarted.get_test_history(TEST_ID)) == 3
    restarted.close()


def test_same_key_different_payload_is_zero_effect(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    assert update_test_artifact(db, _request(), project_root=root).status == "applied"
    conflict = update_test_artifact(db, _request(title="Different"), project_root=root)
    assert conflict.status == "denied"
    assert conflict.reason_code == "idempotency_conflict"
    assert len(db.get_test_history(TEST_ID)) == 2
    db.close()


def test_omitted_fields_are_preserved_exactly(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    before = db.get_test(TEST_ID)
    result = update_test_artifact(db, _request(key="omit-preserves"), project_root=root)
    assert result.status == "applied"
    assert result.row is not None
    for field in (
        "application_scope",
        "description",
        "expected_outcome",
        "last_executed_at",
        "last_result",
        "spec_id",
        "test_class",
        "test_file",
        "test_function",
        "test_type",
    ):
        assert result.row[field] == before[field]
    db.close()


def test_definition_change_invalidates_stale_execution_result(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    db._seed_test_version_for_test_only(
        TEST_ID,
        "fixture",
        "seed prior execution",
        last_result="fail",
        last_executed_at="2026-09-04T00:00:00Z",
    )
    request = ArtifactUpdateRequest(
        **{
            **_request(key="invalidate", test_file="tests/changed.py").__dict__,
            "expected_version": 2,
        }
    )
    result = update_test_artifact(db, request, project_root=root)
    assert result.status == "applied"
    assert result.row is not None
    assert result.row["last_result"] is None
    assert result.row["last_executed_at"] is None
    db.close()


def test_pass_requires_exact_execution_evidence(service_env) -> None:
    root, db_path = service_env
    executed_at = "2026-09-04T00:00:00Z"
    base = _request(key="pass-without-evidence", last_result="pass", last_executed_at=executed_at)
    db = KnowledgeDB(db_path=db_path)
    denied = update_test_artifact(db, base, project_root=root)
    assert denied.status == "denied"
    assert "execution evidence" in (denied.recovery or "")

    allowed = ArtifactUpdateRequest(
        **_request(key="pass-with-evidence", last_result="pass", last_executed_at=executed_at).__dict__
    )
    current = db.get_test(TEST_ID)
    assert current is not None
    allowed = ArtifactUpdateRequest(
        **{
            **allowed.__dict__,
            "execution_evidence": {
                "sha256": update_module._execution_definition_digest(current),
                "executed_at": executed_at,
            },
        }
    )
    result = update_test_artifact(db, allowed, project_root=root)
    assert result.status == "applied"
    assert result.row is not None and result.row["last_result"] == "pass"
    db.close()


@pytest.mark.parametrize(
    "updates",
    [
        {"title": ""},
        {"test_type": "not-a-test-type"},
        {"application_scope": "not-an-application"},
        {"unknown_field": "not-supported"},
    ],
)
def test_invalid_postimages_fail_before_insertion(service_env, updates: dict[str, object]) -> None:
    root, db_path = service_env
    request = ArtifactUpdateRequest(
        **{
            **_request(key="invalid").__dict__,
            "updates": updates,
        }
    )
    db = KnowledgeDB(db_path=db_path)
    result = update_test_artifact(db, request, project_root=root)
    assert result.status == "denied"
    assert result.reason_code == "validation_failed"
    assert len(db.get_test_history(TEST_ID)) == 1
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


def test_stale_cas_is_zero_effect(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    db._seed_test_version_for_test_only(TEST_ID, "fixture", "advance", title="advanced")
    result = update_test_artifact(db, _request(key="stale"), project_root=root)
    assert result.reason_code == "stale_expected_version"
    assert len(db.get_test_history(TEST_ID)) == 2
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


def test_forced_readback_mismatch_rolls_back_all_effects(service_env, monkeypatch) -> None:
    root, db_path = service_env
    original = update_module._postimage_digest
    calls = 0

    def mismatching_digest(postimage):
        nonlocal calls
        calls += 1
        digest = original(postimage)
        return "0" * 64 if calls == 3 else digest

    monkeypatch.setattr(update_module, "_postimage_digest", mismatching_digest)
    db = KnowledgeDB(db_path=db_path)
    result = update_test_artifact(db, _request(key="readback-mismatch"), project_root=root)
    assert result.status == "denied"
    assert result.reason_code == "canonical_readback_mismatch"
    assert len(db.get_test_history(TEST_ID)) == 1
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


def test_forced_failure_before_commit_rolls_back_all_effects(service_env, monkeypatch) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)

    def fail_event(*args, **kwargs):
        raise sqlite3.OperationalError("forced event failure")

    monkeypatch.setattr(db, "_record_event", fail_event)
    result = update_test_artifact(db, _request(key="crash-before"), project_root=root)
    assert result.reason_code == "protected_effect_failed"
    assert len(db.get_test_history(TEST_ID)) == 1
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


def test_concurrent_duplicate_requests_have_one_winner_and_one_replay(service_env) -> None:
    root, db_path = service_env
    request = _request(key="concurrent")

    def invoke() -> str:
        db = KnowledgeDB(db_path=db_path)
        try:
            return update_test_artifact(db, request, project_root=root).status
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = sorted(pool.map(lambda _: invoke(), range(2)))
    assert statuses == ["applied", "replay"]
    db = KnowledgeDB(db_path=db_path)
    assert len(db.get_test_history(TEST_ID)) == 2
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 1
    db.close()


def test_concurrent_disjoint_requests_preserve_both_targets(service_env) -> None:
    root, db_path = service_env
    _write_bridge(root, [TEST_ID, RELATED_TEST_ID])
    requests = [
        _request(key="disjoint-1", test_id=TEST_ID, title="First target"),
        _request(key="disjoint-2", test_id=RELATED_TEST_ID, title="Second target"),
    ]

    def invoke(request: ArtifactUpdateRequest) -> str:
        db = KnowledgeDB(db_path=db_path)
        try:
            return update_test_artifact(db, request, project_root=root).status
        finally:
            db.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = sorted(pool.map(invoke, requests))
    assert statuses == ["applied", "applied"]
    db = KnowledgeDB(db_path=db_path)
    assert db.get_test(TEST_ID)["title"] == "First target"
    assert db.get_test(RELATED_TEST_ID)["title"] == "Second target"
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 2
    db.close()


@pytest.mark.parametrize("targets", [[], ["*"], ["TEST-OTHER"]])
def test_exact_typed_target_scope_is_required(service_env, targets: list[str]) -> None:
    root, db_path = service_env
    _write_bridge(root, targets)
    db = KnowledgeDB(db_path=db_path)
    result = update_test_artifact(db, _request(key="scope"), project_root=root)
    assert result.status == "denied"
    assert "target scope" in (result.recovery or "")
    assert len(db.get_test_history(TEST_ID)) == 1
    db.close()


@pytest.mark.parametrize(
    ("case", "reason_code"),
    [
        ("membership_missing", "exact_project_membership_missing_or_ambiguous"),
        ("membership_multiple", "exact_project_membership_missing_or_ambiguous"),
        ("project_inactive", "exact_execution_project_missing_or_inactive"),
        ("work_item_terminal", "exact_work_item_terminal"),
        ("formal_inactive", "applicable_formal_authority_missing_or_inactive"),
        ("claim_missing", "matching_live_work_intent_claim_missing"),
        ("claim_mismatch", "matching_live_work_intent_claim_mismatch"),
        ("claim_expired", "matching_live_work_intent_claim_expired"),
        ("dependency_unsatisfied", "project_dependency_unsatisfied"),
    ],
)
def test_live_authority_failures_are_typed_and_zero_effect(service_env, case: str, reason_code: str) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    conn = db._get_conn()
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    if case == "membership_missing":
        conn.execute("UPDATE project_work_item_memberships SET status = 'excluded'")
    elif case == "membership_multiple":
        conn.execute(
            """INSERT INTO project_work_item_memberships
               (id, version, project_id, work_item_id, membership_role,
                membership_order, status, changed_by, changed_at, change_reason)
               VALUES ('PWM-SECOND', 1, 'PROJECT-SECOND', ?,
                       'execution_authority', 2, 'active', 'fixture', ?, 'fixture')""",
            (WORK_ITEM_ID, now),
        )
    elif case == "project_inactive":
        conn.execute("UPDATE projects SET status = 'retired' WHERE id = ?", (PROJECT_ID,))
    elif case == "work_item_terminal":
        conn.execute("UPDATE work_items SET resolution_status = 'verified' WHERE id = ?", (WORK_ITEM_ID,))
    elif case == "formal_inactive":
        conn.execute("UPDATE specifications SET status = 'retired' WHERE id = ?", (SPEC_ID,))
    elif case == "claim_missing":
        conn.execute("DELETE FROM work_intent_claims")
    elif case == "claim_mismatch":
        conn.execute("UPDATE work_intent_claims SET acting_role = 'loyal-opposition'")
    elif case == "claim_expired":
        conn.execute(
            "UPDATE work_intent_claims SET ttl_expires_at = ?, implementation_grace_expires_at = ?",
            (_past(), _past()),
        )
    elif case == "dependency_unsatisfied":
        _insert_project_dependency(
            conn,
            dependency_id="PDEP-FIXTURE",
            prerequisite_status="active",
            dependency_kind="requires_project_state",
            required_state="retired",
            now=now,
        )
    else:  # pragma: no cover - parameter list and dispatcher must remain aligned
        raise AssertionError(case)
    conn.commit()

    result = update_test_artifact(db, _request(key=f"negative-{case}"), project_root=root)
    assert result.status == "denied"
    assert result.reason_code == reason_code
    assert result.recovery and "No effect committed" in result.recovery
    assert len(db.get_test_history(TEST_ID)) == 1
    assert conn.execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


@pytest.mark.parametrize("affected_gate", ["authorization", "promotion", "closure"])
def test_non_readiness_dependencies_do_not_gate_test_update(service_env, affected_gate: str) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    conn = db._get_conn()
    _insert_project_dependency(
        conn,
        dependency_id=f"PDEP-{affected_gate.upper()}",
        prerequisite_status="active",
        dependency_kind="requires_project_state",
        required_state="retired",
        affected_gate=affected_gate,
        now=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )
    conn.commit()
    result = update_test_artifact(db, _request(key=f"gate-{affected_gate}"), project_root=root)
    assert result.status == "applied"
    db.close()


def test_authorization_field_change_does_not_affect_initiated_chain(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    conn = db._get_conn()
    columns = {row[1] for row in conn.execute("PRAGMA table_info(projects)")}
    column = "authorization" if "authorization" in columns else "activation_status"
    conn.execute(f"UPDATE projects SET {column} = 'not authorized' WHERE id = ?", (PROJECT_ID,))
    conn.commit()
    result = update_test_artifact(db, _request(key="authorization-after-go"), project_root=root)
    assert result.status == "applied"
    db.close()


def test_retired_prerequisite_satisfies_required_completed_dependency(service_env) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    conn = db._get_conn()
    _insert_project_dependency(
        conn,
        dependency_id="PDEP-RETIRED-SATISFIES-COMPLETED",
        prerequisite_status="retired",
        dependency_kind="requires_project_state",
        required_state="completed",
        now=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )
    conn.commit()

    result = update_test_artifact(db, _request(key="retired-satisfies-completed"), project_root=root)

    assert result.status == "applied"
    assert result.applied is True
    assert len(db.get_test_history(TEST_ID)) == 2
    assert conn.execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 1
    db.close()


@pytest.mark.parametrize(
    ("dependency_kind", "required_state", "reason_code"),
    [
        ("unsupported_kind", "completed", "project_dependency_kind_unsupported"),
        ("", "completed", "project_dependency_kind_unsupported"),
        ("requires_project_state", "unsupported_state", "project_dependency_required_state_unsupported"),
        ("requires_project_state", "", "project_dependency_required_state_unsupported"),
    ],
)
def test_unsupported_or_malformed_dependency_definition_is_zero_effect(
    service_env,
    dependency_kind: str,
    required_state: str,
    reason_code: str,
) -> None:
    root, db_path = service_env
    db = KnowledgeDB(db_path=db_path)
    conn = db._get_conn()
    suffix = f"{dependency_kind or 'EMPTY-KIND'}-{required_state or 'EMPTY-STATE'}"
    _insert_project_dependency(
        conn,
        dependency_id=f"PDEP-{suffix}",
        prerequisite_status="retired",
        dependency_kind=dependency_kind,
        required_state=required_state,
        now=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )
    conn.commit()

    result = update_test_artifact(db, _request(key=f"invalid-dependency-{suffix}"), project_root=root)

    assert result.status == "denied"
    assert result.reason_code == reason_code
    assert result.recovery and "No effect committed" in result.recovery
    assert len(db.get_test_history(TEST_ID)) == 1
    assert conn.execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()


def test_corrupt_receipt_requires_recovery_without_new_version(service_env) -> None:
    root, db_path = service_env
    request = _request(key="corrupt")
    db = KnowledgeDB(db_path=db_path)
    assert update_test_artifact(db, request, project_root=root).status == "applied"
    db._get_conn().execute(
        "UPDATE test_artifact_update_requests SET result_payload_json = '{}' WHERE idempotency_key = 'corrupt'"
    )
    db._get_conn().commit()
    result = update_test_artifact(db, request, project_root=root)
    assert result.status == "recovery_required"
    assert len(db.get_test_history(TEST_ID)) == 2
    db.close()


def test_receipt_schema_survives_upgrade_and_reopen(tmp_path) -> None:
    db_path = tmp_path / "wi5183-upgrade.db"
    db = KnowledgeDB(db_path=db_path)
    conn = db._get_conn()
    conn.execute(
        """INSERT INTO test_artifact_update_requests
           (idempotency_key, request_schema_version, request_digest, test_id,
            expected_test_version, result_test_version, result_postimage_digest,
            result_payload_json, result_receipt_digest, project_id, work_item_id,
            bridge_slug, go_file, go_sha256, actor_session_context_id, created_at,
            changed_by, change_reason)
           VALUES ('key-1', 1, 'request', 'TEST-1', 1, 2, 'postimage', '{}',
                   'receipt', 'PROJECT-1', 'WI-1', 'bridge-1',
                   'bridge/bridge-1-002.md', 'go', 'session-1',
                   '2026-08-26T00:00:00Z', 'test', 'fixture')"""
    )
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION - 1}")
    conn.commit()
    db.close()

    upgraded = KnowledgeDB(db_path=db_path)
    assert upgraded._schema_version(upgraded._get_conn()) == SCHEMA_VERSION
    row = (
        upgraded._get_conn()
        .execute("SELECT idempotency_key, result_test_version FROM test_artifact_update_requests")
        .fetchone()
    )
    assert tuple(row) == ("key-1", 2)
    upgraded.close()

    reopened = KnowledgeDB(db_path=db_path)
    assert reopened._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 1
    reopened.close()


def test_pre_migration_database_adds_schema_without_losing_existing_rows(tmp_path) -> None:
    db_path = tmp_path / "wi5183-pre-migration.db"
    db = KnowledgeDB(db_path=db_path)
    db.insert_spec(
        id="DCL-WI5183-FIXTURE",
        title="fixture",
        status="active",
        type="design_constraint",
        changed_by="fixture",
        change_reason="fixture",
    )
    db.insert_test(
        id="TEST-WI5183-FIXTURE",
        title="fixture",
        spec_id="DCL-WI5183-FIXTURE",
        test_type="unit",
        expected_outcome="fixture",
        changed_by="fixture",
        change_reason="fixture",
    )
    conn = db._get_conn()
    conn.execute("DROP TABLE test_artifact_update_requests")
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION - 1}")
    conn.commit()
    db.close()

    upgraded = KnowledgeDB(db_path=db_path)
    conn = upgraded._get_conn()
    assert upgraded.get_test("TEST-WI5183-FIXTURE")["title"] == "fixture"
    assert conn.execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    claim_columns = {row[1] for row in conn.execute("PRAGMA table_info(work_intent_claims)")}
    assert {"claim_kind", "project_id", "work_item_id", "acting_role_attestation"} <= claim_columns
    assert upgraded._schema_version(conn) == SCHEMA_VERSION
    upgraded.close()


def test_tests_update_help_exposes_omit_clear_and_file_inputs() -> None:
    result = CliRunner().invoke(main, ["tests", "update", "--help"])
    assert result.exit_code == 0, result.output
    assert "--clear" in result.output
    assert "--description-file" in result.output
    assert "--expected-version" in result.output
    assert "--idempotency-key" in result.output


def test_cli_dry_run_returns_typed_result_without_mutation(service_env) -> None:
    root, db_path = service_env
    config = root / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\ndb_path = "{db_path.as_posix()}"\nproject_root = "{root.as_posix()}"\n',
        encoding="utf-8",
    )
    result = CliRunner().invoke(
        main,
        [
            "--config",
            str(config),
            "tests",
            "update",
            TEST_ID,
            "--expected-version",
            "1",
            "--idempotency-key",
            "cli-dry-run",
            "--project",
            PROJECT_ID,
            "--work-item",
            WORK_ITEM_ID,
            "--bridge-id",
            BRIDGE_SLUG,
            "--session-context-id",
            SESSION_ID,
            "--changed-by",
            "fixture-prime-builder",
            "--change-reason",
            "CLI dry run",
            "--title",
            "CLI title",
            "--dry-run",
            "--json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["status"] == "dry_run"
    db = KnowledgeDB(db_path=db_path)
    assert len(db.get_test_history(TEST_ID)) == 1
    assert db._get_conn().execute("SELECT COUNT(*) FROM test_artifact_update_requests").fetchone()[0] == 0
    db.close()
