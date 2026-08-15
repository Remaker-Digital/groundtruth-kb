"""Specification-derived tests for WI-5953 in-place receipt recovery."""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import registry_control_plane
from groundtruth_kb.project.registry_control_plane import (
    RegistryAuthorizationError,
    RegistryRecoveryRequired,
    apply_registry_transaction,
    ensure_control_plane_schema,
    load_registry_snapshot,
    recover_recovery_required_bridge_publication_capability,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

DOCUMENT = "recovery-required-publication-fixture"
VERSION = 2
STATUS = "NO-GO"
TARGET = f"bridge/{DOCUMENT}-{VERSION:03d}.md"
OWNER_AUTHORIZATION = "DELIB-WI5953-RECOVERY-TEST"
OPERATOR_SESSION = "recovery-operator-session"
AUTHOR_SESSION = "review-author-session"
PRIOR_FAILURE = "bridge publication aggregate preimage cannot be restored exactly"


def _record(record_id: str, storage_path: str, coverage_mode: str = "exact") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-FILE-BRIDGE-AUTHORITY-001",
        mutation_api="gt registry register",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _bridge_content(*, document: str, version: int, status: str, session_id: str) -> bytes:
    prior = f"bridge/{document}-{version - 1:03d}.md"
    return (
        f"{status}\n"
        "::init gtkb pb\n"
        "::open build\n\n"
        "author_identity: loyal-opposition/codex/test\n"
        "author_harness_id: test\n"
        f"author_session_context_id: {session_id}\n"
        "author_model: fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: unit-test\n"
        "author_metadata_source: unit-test\n\n"
        "bridge_kind: lo_verdict\n"
        f"Document: {document}\n"
        f"Version: {version:03d}\n"
        f"Responds to: {prior}\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-5953\n"
        'target_paths: ["groundtruth.db"]\n'
    ).encode()


def _proposal_content(document: str) -> bytes:
    return (
        "REVISED\n"
        "::init gtkb lo\n"
        "::open build\n\n"
        "author_identity: prime-builder/codex/test\n"
        "author_harness_id: test\n"
        "author_session_context_id: proposal-author-session\n"
        "author_model: fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: unit-test\n"
        "author_metadata_source: unit-test\n\n"
        "bridge_kind: prime_proposal\n"
        f"Document: {document}\n"
        "Version: 001\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-5953\n"
        'target_paths: ["groundtruth.db"]\n'
    ).encode()


def _fixture(
    tmp_path: Path,
    *,
    document: str = DOCUMENT,
    status: str = STATUS,
    failure_reason: str = PRIOR_FAILURE,
    transition_algorithm: str = registry_control_plane.TRANSITION_EVIDENCE_ALGORITHM_SCHEMA_V2,
) -> dict[str, object]:
    """Build a recovery fixture.

    ``transition_algorithm`` selects the era the seeded row is minted under.
    Seeding a TRUE legacy row (WI-5953) is what the prior fixture could not do:
    it always minted through the schema-v2 helper, so it could never reproduce
    the production row that failed the first authorized invocation.
    """
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    proposal = bridge_dir / f"{document}-001.md"
    proposal.write_bytes(_proposal_content(document))
    content = _bridge_content(document=document, version=VERSION, status=status, session_id=AUTHOR_SESSION)
    target = bridge_dir / f"{document}-{VERSION:03d}.md"
    target.write_bytes(content)

    records = [_record("bridge-versioned-files", "bridge/*-[0-9][0-9][0-9].md", "glob")]
    registry = tmp_path / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        tmp_path
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    registry.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")
    kwargs: dict[str, object] = {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        actor_session="test-session",
        changed_by="test/prime-builder",
        change_reason="fixture registration",
        start_packet_hash="sha256:test-start",
        pauth_id="PAUTH-WI5953-TEST",
        bridge_id=document,
        **kwargs,
    )

    _digest_for = {
        name: registry_control_plane._historical_bridge_publication_transition_digest(
            tmp_path,
            document_name=document,
            version=VERSION,
            status=status,
            content=content,
            algorithm=name,
        )
        for name in registry_control_plane.SUPPORTED_TRANSITION_EVIDENCE_ALGORITHMS
    }
    legacy_digest = _digest_for[registry_control_plane.TRANSITION_EVIDENCE_ALGORITHM_LEGACY_UNVERSIONED]
    schema_v2_digest = _digest_for[registry_control_plane.TRANSITION_EVIDENCE_ALGORITHM_SCHEMA_V2]
    # The seeded row carries whichever era this fixture is minting.
    transition_digest = _digest_for[transition_algorithm]
    thread_file_vector = registry_control_plane._historical_bridge_publication_thread_file_vector(
        tmp_path,
        document_name=document,
        version=VERSION,
    )
    content_digest = registry_control_plane._sha256_bytes(content)
    snapshot = load_registry_snapshot(**kwargs)
    aggregate = snapshot.resolver.resolve(f"bridge/{document}-{VERSION:03d}.md")
    assert aggregate is not None
    aggregate_digest = registry_control_plane.artifact_content_state(tmp_path, aggregate)[0]
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        ensure_control_plane_schema(conn)
        older_capability = "sha256:" + "1" * 64
        newest_capability = "sha256:" + "2" * 64
        common = (
            "bridge_publication",
            document,
            VERSION,
            status,
            f"bridge/{document}-{VERSION:03d}.md",
            content_digest,
            "sha256:test-compliance",
            transition_digest,
            "original-claim-session",
            AUTHOR_SESSION,
            aggregate.id,
            aggregate_digest,
            "bridge_publication",
            "2000-01-01T00:00:00Z",
            "2026-08-10T00:00:00Z",
        )
        conn.execute(
            """
            INSERT INTO sot_registry_bridge_publication_capabilities (
                capability_hash, authority_kind, document_name, version, status,
                target_path, content_digest, compliance_digest, transition_digest,
                claim_session, author_session_context_id, aggregate_entry_id,
                aggregate_preimage_digest, operation, expires_at, capability_state,
                created_at, consumed_at, result_digest, revision_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'consumed', ?, ?, ?, ?)
            """,
            (
                older_capability,
                *common,
                "2026-08-10T00:00:01Z",
                "sha256:older-result",
                "SOTREV-OLDER",
            ),
        )
        conn.execute(
            """
            INSERT INTO sot_registry_bridge_publication_capabilities (
                capability_hash, authority_kind, document_name, version, status,
                target_path, content_digest, compliance_digest, transition_digest,
                claim_session, author_session_context_id, aggregate_entry_id,
                aggregate_preimage_digest, operation, expires_at, capability_state,
                created_at, failure_reason
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'recovery_required', ?, ?)
            """,
            (newest_capability, *common, failure_reason),
        )
        conn.commit()

    sidecar = registry_control_plane._bridge_publication_pending_sidecar_path(tmp_path, target)
    sidecar.parent.mkdir(parents=True)
    sidecar.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "capability_hash": newest_capability,
                "content_digest": content_digest,
                "created_at": "2026-08-10T00:00:00Z",
                "document_name": document,
                "session_id": "original-claim-session",
                "status": status,
                "target_path": f"bridge/{document}-{VERSION:03d}.md",
                "version": VERSION,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        tuple_rows = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities "
            "WHERE document_name = ? AND version = ? ORDER BY rowid ASC",
            (document, VERSION),
        ).fetchall()
        older_rowid = tuple_rows[0]["rowid"]
        older_digest = registry_control_plane._json_digest(dict(tuple_rows[0]))
        newest_rowid = tuple_rows[-1]["rowid"]
    return {
        "document": document,
        "content": content,
        "content_digest": content_digest,
        "target": target,
        "target_bytes": target.read_bytes(),
        "sidecar": sidecar,
        "sidecar_bytes": sidecar.read_bytes(),
        "newest_capability": newest_capability,
        "newest_rowid": newest_rowid,
        "older_capability": older_capability,
        "older_rowid": older_rowid,
        "older_digest": older_digest,
        "transition_algorithm": transition_algorithm,
        "legacy_digest": legacy_digest,
        "schema_v2_digest": schema_v2_digest,
        "thread_file_vector": thread_file_vector,
        "kwargs": kwargs,
    }


def _call(fixture: dict[str, object], **overrides: object):
    arguments = {
        "document_name": fixture["document"],
        "version": VERSION,
        "target_path": fixture["target"],
        "content": fixture["content"],
        "session_id": OPERATOR_SESSION,
        "owner_authorization": OWNER_AUTHORIZATION,
        "expected_capability_hash": fixture["newest_capability"],
        "expected_content_digest": fixture["content_digest"],
        "expected_status": STATUS,
        "expected_failure_reason": PRIOR_FAILURE,
        "expected_sidecar_digest": registry_control_plane._sha256_bytes(fixture["sidecar_bytes"]),
        "expected_tuple_row_count": 2,
        "expected_predecessor_rowid": fixture["older_rowid"],
        "expected_predecessor_capability_hash": fixture["older_capability"],
        "expected_predecessor_state": "consumed",
        "expected_predecessor_digest": fixture["older_digest"],
        "expected_selected_rowid": fixture["newest_rowid"],
        "transition_evidence_algorithm": fixture["transition_algorithm"],
        "expected_legacy_transition_digest": fixture["legacy_digest"],
        "expected_schema_v2_transition_digest": fixture["schema_v2_digest"],
        "expected_thread_file_vector": fixture["thread_file_vector"],
        **fixture["kwargs"],
    }
    arguments.update(overrides)
    return recover_recovery_required_bridge_publication_capability(**arguments)


def _rows(fixture: dict[str, object]) -> list[sqlite3.Row]:
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities "
            "WHERE document_name = ? AND version = ? AND target_path = ? ORDER BY rowid ASC",
            (fixture["document"], VERSION, f"bridge/{fixture['document']}-{VERSION:03d}.md"),
        ).fetchall()


def _revision_count(fixture: dict[str, object]) -> int:
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        return conn.execute("SELECT COUNT(*) FROM sot_artifact_revisions").fetchone()[0]


def _insert_unrelated_capability(
    conn: sqlite3.Connection,
    fixture: dict[str, object],
    *,
    capability_hash: str,
    state: str,
) -> None:
    conn.execute(
        """
        INSERT INTO sot_registry_bridge_publication_capabilities (
            capability_hash, authority_kind, document_name, version, status,
            target_path, content_digest, compliance_digest, transition_digest,
            claim_session, author_session_context_id, aggregate_entry_id,
            aggregate_preimage_digest, operation, expires_at, capability_state,
            created_at
        )
        SELECT ?, authority_kind, 'unrelated-publication', 1, status,
               'bridge/unrelated-publication-001.md', content_digest,
               compliance_digest, transition_digest, claim_session,
               author_session_context_id, aggregate_entry_id,
               aggregate_preimage_digest, operation, expires_at, ?, created_at
        FROM sot_registry_bridge_publication_capabilities
        WHERE capability_hash = ?
        """,
        (capability_hash, state, fixture["older_capability"]),
    )


def _assert_files_unchanged(fixture: dict[str, object]) -> None:
    assert fixture["target"].read_bytes() == fixture["target_bytes"]
    assert fixture["sidecar"].read_bytes() == fixture["sidecar_bytes"]


def test_success_is_exact_in_place_two_to_two_and_replay_is_read_only(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    before = _rows(fixture)
    revision_count = _revision_count(fixture)

    receipt = _call(fixture)
    after = _rows(fixture)
    replay = _call(fixture)

    assert len(before) == len(after) == len(_rows(fixture)) == 2
    assert dict(after[0]) == dict(before[0])
    assert after[1]["rowid"] == before[1]["rowid"]
    assert after[1]["capability_hash"] == fixture["newest_capability"]
    assert after[1]["capability_state"] == "consumed"
    assert after[1]["failure_reason"] is None
    assert after[1]["revision_id"] == receipt.revision_id
    assert after[1]["result_digest"]
    assert replay == receipt
    assert _revision_count(fixture) == revision_count + 1
    _assert_files_unchanged(fixture)


def test_revision_and_result_bind_owner_operator_failure_and_exact_evidence(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    receipt = _call(fixture)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (fixture["newest_capability"],),
        ).fetchone()
        revision = conn.execute(
            "SELECT * FROM sot_artifact_revisions WHERE revision_id = ?",
            (receipt.revision_id,),
        ).fetchone()
    assert row is not None and revision is not None
    pauth = json.loads(revision["pauth_decision"])
    assert revision["actor_session"] == OPERATOR_SESSION
    assert revision["operation"] == "bridge_publication_recovery_required_repair"
    assert revision["evidence_view"] == "recovery"
    assert revision["evidence_source_reference"] == fixture["newest_capability"]
    assert pauth["authorization_id"] == OWNER_AUTHORIZATION
    assert pauth["prior_failure_reason"] == PRIOR_FAILURE
    assert pauth["preimage_row_count"] == 2
    assert pauth["selected_rowid"] == row["rowid"]
    assert pauth["sidecar_digest"] == registry_control_plane._sha256_bytes(fixture["sidecar_bytes"])
    assert pauth["content_digest"] == fixture["content_digest"]
    assert pauth["aggregate_digest"] == receipt.aggregate_digest
    assert row["result_digest"].startswith("sha256:")
    assert PRIOR_FAILURE in revision["change_reason"]


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"owner_authorization": ""}, "requires owner authorization"),
        ({"session_id": ""}, "requires an operator session"),
        ({"expected_capability_hash": "sha256:" + "9" * 64}, "newest.*expected capability"),
        ({"expected_content_digest": "sha256:" + "9" * 64}, "content binding mismatch"),
        ({"expected_status": "GO"}, "lifecycle status mismatch"),
        ({"expected_failure_reason": "wrong failure"}, "row binding mismatch"),
        ({"expected_sidecar_digest": "sha256:" + "9" * 64}, "sidecar digest mismatch"),
        ({"expected_tuple_row_count": 3}, "exact two-row tuple"),
        ({"expected_selected_rowid": 999}, "rowid does not match"),
        ({"expected_predecessor_rowid": 999}, "authorized predecessor preimage"),
        ({"expected_predecessor_capability_hash": "sha256:" + "8" * 64}, "predecessor preimage"),
        ({"expected_predecessor_state": "expired"}, "predecessor must be consumed"),
        ({"expected_predecessor_digest": "sha256:" + "7" * 64}, "predecessor preimage"),
        ({"target_path": "bridge/wrong-002.md"}, "exact lexical canonical target"),
        ({"version": 3}, "exact lexical canonical target"),
        ({"version": False}, "version must be a positive integer"),
    ],
)
def test_wrong_authority_or_exact_binding_fails_without_side_effects(
    tmp_path: Path,
    override: dict[str, object],
    message: str,
) -> None:
    fixture = _fixture(tmp_path)
    before = [dict(row) for row in _rows(fixture)]
    revisions = _revision_count(fixture)
    with pytest.raises(RegistryAuthorizationError, match=message):
        _call(fixture, **override)
    assert [dict(row) for row in _rows(fixture)] == before
    assert _revision_count(fixture) == revisions
    _assert_files_unchanged(fixture)


def test_content_and_target_drift_fail_without_side_effects(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    before = [dict(row) for row in _rows(fixture)]
    fixture["target"].write_bytes(fixture["content"] + b"drift")
    with pytest.raises(RegistryAuthorizationError, match="target bytes do not match content"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert fixture["sidecar"].read_bytes() == fixture["sidecar_bytes"]


@pytest.mark.parametrize("target_state", ["missing", "directory"])
def test_missing_or_nonfile_target_fails_closed(tmp_path: Path, target_state: str) -> None:
    fixture = _fixture(tmp_path)
    before = [dict(row) for row in _rows(fixture)]
    fixture["target"].unlink()
    if target_state == "directory":
        fixture["target"].mkdir()
    with pytest.raises(RegistryRecoveryRequired, match="target is not a regular file"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert fixture["sidecar"].read_bytes() == fixture["sidecar_bytes"]


def test_symlink_target_fails_at_lexical_canonical_path(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    real_target = tmp_path / "real-target.md"
    real_target.write_bytes(fixture["content"])
    fixture["target"].unlink()
    try:
        os.symlink(real_target, fixture["target"])
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="target path contains a redirected component"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert real_target.read_bytes() == fixture["content"]


def test_linklike_target_detection_branch_is_exercised_without_os_privilege(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path)
    real_kind = registry_control_plane._path_object_kind

    def linklike_kind(path: Path) -> str:
        if path == fixture["target"]:
            return "symlink"
        return real_kind(path)

    monkeypatch.setattr(registry_control_plane, "_path_object_kind", linklike_kind)
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="redirected component"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


@pytest.mark.parametrize(
    ("mutation", "error_type", "message"),
    [
        ("missing", RegistryRecoveryRequired, "exactly one deterministic pending sidecar"),
        ("directory", RegistryRecoveryRequired, "sidecar is not one exact regular file"),
        ("malformed", RegistryRecoveryRequired, "sidecar is unreadable"),
        ("schema", RegistryAuthorizationError, "sidecar binding mismatch"),
        ("binding", RegistryAuthorizationError, "sidecar binding mismatch"),
        ("raw_digest", RegistryAuthorizationError, "sidecar digest mismatch"),
    ],
)
def test_pending_sidecar_failures_preserve_receipts_and_target(
    tmp_path: Path,
    mutation: str,
    error_type: type[Exception],
    message: str,
) -> None:
    fixture = _fixture(tmp_path)
    sidecar = fixture["sidecar"]
    if mutation == "missing":
        sidecar.unlink()
    elif mutation == "directory":
        sidecar.unlink()
        sidecar.mkdir()
    elif mutation == "malformed":
        sidecar.write_bytes(b"not-json")
    else:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        if mutation == "schema":
            payload["schema_version"] = 2
            sidecar.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        elif mutation == "binding":
            payload["capability_hash"] = "sha256:" + "9" * 64
            sidecar.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        else:
            sidecar.write_bytes(fixture["sidecar_bytes"] + b"\n")
    before = [dict(row) for row in _rows(fixture)]
    revisions = _revision_count(fixture)
    with pytest.raises(error_type, match=message):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert _revision_count(fixture) == revisions
    assert fixture["target"].read_bytes() == fixture["target_bytes"]


def test_symlink_pending_sidecar_fails_closed(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    real_sidecar = tmp_path / "real-sidecar.json"
    real_sidecar.write_bytes(fixture["sidecar_bytes"])
    fixture["sidecar"].unlink()
    try:
        os.symlink(real_sidecar, fixture["sidecar"])
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="sidecar path contains a redirected component"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


def test_linklike_sidecar_detection_branch_is_exercised_without_os_privilege(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path)
    real_kind = registry_control_plane._path_object_kind

    def linklike_kind(path: Path) -> str:
        if path == fixture["sidecar"]:
            return "reparse"
        return real_kind(path)

    monkeypatch.setattr(registry_control_plane, "_path_object_kind", linklike_kind)
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="sidecar path contains a redirected component"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


def test_extra_matching_pending_sidecar_fails_closed(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    extra = fixture["sidecar"].with_name(f"{fixture['target'].stem}-extra.json")
    extra.write_bytes(fixture["sidecar_bytes"])
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="exactly one deterministic pending sidecar"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


def test_invalid_current_lifecycle_fails_before_receipt_mutation(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    proposal = tmp_path / "bridge" / f"{DOCUMENT}-001.md"
    proposal.write_text("MALFORMED\n", encoding="utf-8")
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="lifecycle is invalid"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


def test_alias_symlink_target_argument_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    alias = tmp_path / "bridge" / "alias.md"
    try:
        os.symlink(fixture["target"], alias)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryAuthorizationError, match="exact lexical canonical target"):
        _call(fixture, target_path=alias)
    assert [dict(row) for row in _rows(fixture)] == before


@pytest.mark.parametrize(
    ("state", "message"),
    [
        ("minted", "zero globally minted"),
        ("expired", "not recovery_required or consumed"),
        ("compensated", "not recovery_required or consumed"),
    ],
)
def test_wrong_newest_state_fails_closed(tmp_path: Path, state: str, message: str) -> None:
    fixture = _fixture(tmp_path)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities SET capability_state = ? WHERE capability_hash = ?",
            (state, fixture["newest_capability"]),
        )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryAuthorizationError, match=message):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    _assert_files_unchanged(fixture)


def test_predecessor_mutation_is_not_silently_canonized(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities "
            "SET capability_state = 'recovery_required', consumed_at = NULL, result_digest = NULL, "
            "revision_id = NULL, failure_reason = ? WHERE capability_hash = ?",
            (PRIOR_FAILURE, fixture["older_capability"]),
        )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryAuthorizationError, match="authorized predecessor preimage"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    _assert_files_unchanged(fixture)


def test_duplicate_exact_newest_identity_is_rejected(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        row = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (fixture["newest_capability"],),
        ).fetchone()
        columns = [item[1] for item in conn.execute("PRAGMA table_info(sot_registry_bridge_publication_capabilities)")]
        values = dict(zip(columns, row, strict=True))
        values["rowid"] = None
        values["capability_hash"] = "sha256:" + "3" * 64
        insert_columns = [name for name in columns if name != "rowid"]
        conn.execute(
            f"INSERT INTO sot_registry_bridge_publication_capabilities ({', '.join(insert_columns)}) "
            f"VALUES ({', '.join('?' for _ in insert_columns)})",
            tuple(values[name] for name in insert_columns),
        )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="exactly the authorized two-row tuple"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    _assert_files_unchanged(fixture)


def test_transaction_rolls_back_revision_and_receipt_on_update_fault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path)
    before = [dict(row) for row in _rows(fixture)]
    revisions = _revision_count(fixture)
    real_append = registry_control_plane._append_revision

    def append_then_fail(*args: object, **kwargs: object) -> str:
        real_append(*args, **kwargs)
        raise RuntimeError("injected recovery revision fault")

    monkeypatch.setattr(registry_control_plane, "_append_revision", append_then_fail)
    with pytest.raises(RuntimeError, match="injected recovery revision fault"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert _revision_count(fixture) == revisions
    _assert_files_unchanged(fixture)


def test_transaction_rolls_back_after_receipt_update_fault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(tmp_path)
    before = [dict(row) for row in _rows(fixture)]
    revisions = _revision_count(fixture)
    real_hash = registry_control_plane._hash_file
    calls = 0

    def fail_post_update(path: Path) -> str:
        nonlocal calls
        calls += 1
        if calls >= 3 and path == fixture["target"]:
            raise RuntimeError("injected post-update verification fault")
        return real_hash(path)

    monkeypatch.setattr(registry_control_plane, "_hash_file", fail_post_update)
    with pytest.raises(RuntimeError, match="injected post-update verification fault"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert _revision_count(fixture) == revisions
    _assert_files_unchanged(fixture)


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("transition_digest", "sha256:wrong", "transition_digest"),
        ("authority_kind", "wrong", "authority_kind"),
        ("operation", "wrong", "operation is not typed"),
        ("aggregate_entry_id", "wrong", "aggregate_entry_id"),
        ("compensation_digest", "sha256:wrong", "compensation evidence"),
        ("revision_id", "SOTREV-PREMATURE", "terminal evidence"),
    ],
)
def test_receipt_binding_tamper_fails_closed(
    tmp_path: Path,
    column: str,
    value: str,
    message: str,
) -> None:
    fixture = _fixture(tmp_path)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.execute(
            f"UPDATE sot_registry_bridge_publication_capabilities SET {column} = ? WHERE capability_hash = ?",
            (value, fixture["newest_capability"]),
        )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryAuthorizationError, match=message):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    _assert_files_unchanged(fixture)


def test_global_minted_receipt_blocks_recovery(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        _insert_unrelated_capability(
            conn,
            fixture,
            capability_hash="sha256:" + "4" * 64,
            state="minted",
        )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryAuthorizationError, match="zero globally minted"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


def test_total_capability_cardinality_trigger_fault_rolls_back_every_effect(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    before = [dict(row) for row in _rows(fixture)]
    revisions = _revision_count(fixture)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.execute(
            f"""
            CREATE TRIGGER inject_unrelated_capability_after_recovery
            AFTER UPDATE OF capability_state ON sot_registry_bridge_publication_capabilities
            WHEN NEW.capability_hash = '{fixture["newest_capability"]}'
            BEGIN
                INSERT INTO sot_registry_bridge_publication_capabilities (
                    capability_hash, authority_kind, document_name, version, status,
                    target_path, content_digest, compliance_digest, transition_digest,
                    claim_session, author_session_context_id, aggregate_entry_id,
                    aggregate_preimage_digest, operation, expires_at, capability_state,
                    created_at
                ) VALUES (
                    'sha256:{"5" * 64}', 'bridge_publication', 'trigger-unrelated', 1, 'NO-GO',
                    'bridge/trigger-unrelated-001.md', 'sha256:trigger-content',
                    'sha256:trigger-compliance', 'sha256:trigger-transition',
                    'trigger-session', 'trigger-author', 'bridge-versioned-files',
                    'sha256:trigger-aggregate', 'bridge_publication',
                    '2000-01-01T00:00:00Z', 'expired', '2026-08-10T00:00:00Z'
                );
            END
            """
        )
    with pytest.raises(RegistryRecoveryRequired, match="capability-table cardinality changed"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert _revision_count(fixture) == revisions
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM sot_registry_bridge_publication_capabilities "
                "WHERE document_name = 'trigger-unrelated'"
            ).fetchone()[0]
            == 0
        )
    _assert_files_unchanged(fixture)


def test_consumed_replay_rejects_result_digest_tamper(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    _call(fixture)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities SET result_digest = ? WHERE capability_hash = ?",
            ("sha256:tampered", fixture["newest_capability"]),
        )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="result digest mismatch"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


@pytest.mark.parametrize(
    ("surface", "column", "value", "message"),
    [
        ("receipt", "failure_reason", "reintroduced failure", "retained a failure marker"),
        ("revision", "operation", "wrong-operation", "exact revision provenance"),
        (
            "revision",
            "evidence_source_reference",
            "sha256:wrong-source",
            "exact revision provenance",
        ),
    ],
)
def test_consumed_replay_rejects_terminal_provenance_tamper(
    tmp_path: Path,
    surface: str,
    column: str,
    value: str,
    message: str,
) -> None:
    fixture = _fixture(tmp_path)
    receipt = _call(fixture)
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        if surface == "receipt":
            conn.execute(
                f"UPDATE sot_registry_bridge_publication_capabilities SET {column} = ? WHERE capability_hash = ?",
                (value, fixture["newest_capability"]),
            )
        else:
            conn.execute(
                f"UPDATE sot_artifact_revisions SET {column} = ? WHERE revision_id = ?",
                (value, receipt.revision_id),
            )
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match=message):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before


def test_aggregate_or_lifecycle_drift_fails_closed(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    unrelated = tmp_path / "bridge" / "unrelated-001.md"
    unrelated.write_text("NEW\n", encoding="utf-8")
    before = [dict(row) for row in _rows(fixture)]
    with pytest.raises(RegistryRecoveryRequired, match="aggregate revision is not current"):
        _call(fixture)
    assert [dict(row) for row in _rows(fixture)] == before
    assert fixture["sidecar"].read_bytes() == fixture["sidecar_bytes"]


def test_exported_operation_has_no_writer_dispatcher_or_tafe_dependency() -> None:
    assert callable(recover_recovery_required_bridge_publication_capability)
    names = recover_recovery_required_bridge_publication_capability.__code__.co_names
    forbidden = {
        "gtkb_bridge_writer",
        "bridge_verdict_finalizer",
        "dispatcher_runtime",
        "legacy_tafe",
    }
    assert forbidden.isdisjoint(names)


def test_success_leaves_registry_current_and_no_minted_receipt(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    _call(fixture)
    snapshot = load_registry_snapshot(**fixture["kwargs"])
    assert registry_currentness(
        snapshot,
        project_root=fixture["kwargs"]["project_root"],
        db_path=fixture["kwargs"]["db_path"],
        record_ids={"bridge-versioned-files"},
    )["current"]
    with sqlite3.connect(str(fixture["kwargs"]["db_path"])) as conn:
        minted = conn.execute(
            "SELECT COUNT(*) FROM sot_registry_bridge_publication_capabilities WHERE capability_state = 'minted'"
        ).fetchone()[0]
    assert minted == 0


# ---------------------------------------------------------------------------
# WI-5953: explicit transition-evidence algorithm identity.
#
# The prior fixture always minted through the schema-v2 helper, so it could not
# reproduce the legacy production row (row 1865) whose binding failed the first
# authorized invocation. These cases seed a TRUE legacy row and pin both eras.
# ---------------------------------------------------------------------------

LEGACY = registry_control_plane.TRANSITION_EVIDENCE_ALGORITHM_LEGACY_UNVERSIONED
SCHEMA_V2 = registry_control_plane.TRANSITION_EVIDENCE_ALGORITHM_SCHEMA_V2


def test_legacy_seeded_row_recovers_against_legacy_reconstruction(tmp_path: Path) -> None:
    """Row 1 - a legacy-minted row binds under the legacy derivation."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    assert fixture["legacy_digest"] != fixture["schema_v2_digest"], (
        "the two eras must produce different digests or this suite proves nothing"
    )
    assert _rows(fixture)[-1]["transition_digest"] == fixture["legacy_digest"]

    _call(fixture)

    rows_after = _rows(fixture)
    assert rows_after[-1]["capability_state"] == "consumed"
    # Requirement 6: the stored digest is never rewritten.
    assert rows_after[-1]["transition_digest"] == fixture["legacy_digest"]


def test_schema_v2_seeded_row_still_recovers_unchanged(tmp_path: Path) -> None:
    """Row 2 - the modern derivation is not disturbed by the dispatch."""
    fixture = _fixture(tmp_path, transition_algorithm=SCHEMA_V2)
    assert _rows(fixture)[-1]["transition_digest"] == fixture["schema_v2_digest"]
    _call(fixture)
    assert _rows(fixture)[-1]["capability_state"] == "consumed"


def test_wrong_algorithm_label_for_legacy_row_fails_closed(tmp_path: Path) -> None:
    """Row 3 - naming the wrong era cannot bind a legacy row."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    with pytest.raises(RegistryAuthorizationError):
        _call(fixture, transition_evidence_algorithm=SCHEMA_V2)
    assert _rows(fixture)[-1]["capability_state"] == "recovery_required"
    _assert_files_unchanged(fixture)


def test_legacy_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    """Row 4 - a wrong caller-supplied legacy digest aborts before mutation."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    with pytest.raises(RegistryAuthorizationError):
        _call(fixture, expected_legacy_transition_digest="sha256:" + "0" * 64)
    assert _rows(fixture)[-1]["capability_state"] == "recovery_required"
    _assert_files_unchanged(fixture)


def test_schema_v2_digest_mismatch_fails_closed(tmp_path: Path) -> None:
    """Row 5 - the second digest is required even when recovering a legacy row."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    with pytest.raises(RegistryAuthorizationError):
        _call(fixture, expected_schema_v2_transition_digest="sha256:" + "1" * 64)
    assert _rows(fixture)[-1]["capability_state"] == "recovery_required"
    _assert_files_unchanged(fixture)


def test_thread_file_vector_drift_fails_closed(tmp_path: Path) -> None:
    """Row 6 - byte drift in any covered version aborts before mutation."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    drifted = [dict(entry) for entry in fixture["thread_file_vector"]]
    drifted[0]["size"] = int(drifted[0]["size"]) + 1
    with pytest.raises(RegistryAuthorizationError):
        _call(fixture, expected_thread_file_vector=drifted)
    assert _rows(fixture)[-1]["capability_state"] == "recovery_required"
    _assert_files_unchanged(fixture)


def test_later_versions_are_excluded_from_the_file_vector(tmp_path: Path) -> None:
    """Row 7 - a later version present does not perturb the historical vector."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    document = fixture["document"]
    before = registry_control_plane._historical_bridge_publication_thread_file_vector(
        tmp_path, document_name=document, version=VERSION
    )
    later = tmp_path / "bridge" / f"{document}-{VERSION + 1:03d}.md"
    later.write_bytes(b"GO" + bytes([10, 10]) + b"later version that must be excluded")
    after = registry_control_plane._historical_bridge_publication_thread_file_vector(
        tmp_path, document_name=document, version=VERSION
    )
    assert after == before
    assert all(int(entry["path"].split("-")[-1].split(".")[0]) <= VERSION for entry in after)


@pytest.mark.parametrize("identity", ["", "unknown_era", "schema_v3", "LEGACY_UNVERSIONED"])
def test_unsupported_or_ambiguous_algorithm_identity_is_rejected(tmp_path: Path, identity: str) -> None:
    """Row 8 - no default era; an unrecognised identity is refused."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    with pytest.raises(RegistryAuthorizationError):
        _call(fixture, transition_evidence_algorithm=identity)
    assert _rows(fixture)[-1]["capability_state"] == "recovery_required"
    _assert_files_unchanged(fixture)


def test_consumed_replay_preserves_algorithm_and_digest_provenance(tmp_path: Path) -> None:
    """Row 9 - replay is read-only and the stored evidence survives it."""
    fixture = _fixture(tmp_path, transition_algorithm=LEGACY)
    first = _call(fixture)
    revisions_after_first = _revision_count(fixture)
    replay = _call(fixture)
    assert _revision_count(fixture) == revisions_after_first, "replay must not append a revision"
    assert replay.capability_hash == first.capability_hash
    row = _rows(fixture)[-1]
    assert row["capability_state"] == "consumed"
    assert row["transition_digest"] == fixture["legacy_digest"]
    _assert_files_unchanged(fixture)
