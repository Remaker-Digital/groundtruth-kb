# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Specification-derived tests for the WI-5441 registry control plane."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, replace
from pathlib import Path

import pytest
from click.testing import CliRunner
from scripts.bridge_work_intent_registry import acquire
from scripts.bridge_work_intent_registry import release as release_claim

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    IMPLEMENTATION_ARTIFACTS,
    LEGACY_COVERAGE_MODES,
    RegistryAuthorizationError,
    RegistryCoverageError,
    RegistryProjectionMismatch,
    RegistryRecoveryRequired,
    RegistryResolver,
    RegistryTransactionInProgress,
    amend_artifact,
    append_passive_observation,
    apply_registry_transaction,
    bootstrap_legacy_registry,
    census_registry,
    compensate_bridge_publication,
    consume_bridge_publication_capability,
    consume_observation_capability,
    load_registry_snapshot,
    mint_bridge_publication_capability,
    mint_observation_capability,
    preview_registry_registration,
    recover_registry,
    recover_wi5441_bridge_aggregate,
    register_artifacts,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import (
    SoTArtifact,
    _load_toml_unlocked,
    load_toml,
    sync_projection,
)


def _record(record_id: str, storage_path: str, coverage_mode: str = "exact") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="gt registry register",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _fixture_generation(tmp_path: Path, records: list[SoTArtifact]) -> tuple[Path, Path, Path]:
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
    return registry, packaged, db_path


def _transaction_kwargs(tmp_path: Path, registry: Path, packaged: Path, db_path: Path) -> dict[str, object]:
    return {
        "actor_session": "test-session",
        "changed_by": "test/prime-builder",
        "change_reason": "WI-5441 test transaction",
        "start_packet_hash": "sha256:test-start",
        "pauth_id": "PAUTH-WI5441-TEST",
        "bridge_id": "gtkb-wi5441-registry-control-plane-reverse-coverage",
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }


def test_reviewed_legacy_map_is_exactly_fifty_and_explicit() -> None:
    assert len(LEGACY_COVERAGE_MODES) == 50
    assert set(LEGACY_COVERAGE_MODES.values()) == {
        "exact",
        "recursive",
        "glob",
        "opaque_container",
        "virtual",
    }
    assert LEGACY_COVERAGE_MODES["bridge-versioned-files"] == "glob"
    assert LEGACY_COVERAGE_MODES["generated-runtime-state-tree"] == "opaque_container"
    assert LEGACY_COVERAGE_MODES["governance-config-tree"] == "recursive"


def test_resolver_rejects_unsafe_case_collision_and_overlap() -> None:
    with pytest.raises(RegistryCoverageError, match="project-relative"):
        RegistryResolver([_record("escape", "../outside.txt")])
    with pytest.raises(RegistryCoverageError, match="case-fold"):
        RegistryResolver([_record("one", "A.txt"), _record("two", "a.txt")])
    with pytest.raises(RegistryCoverageError, match="ambiguous"):
        RegistryResolver(
            [
                _record("tree", "tree/", "recursive"),
                _record("leaf", "tree/leaf.txt"),
            ]
        )


def test_opaque_container_authorizes_operations_without_claiming_child_identity() -> None:
    opaque = _record("runtime", ".gtkb-state/", "opaque_container")
    resolver = RegistryResolver([opaque])

    assert resolver.resolve(".gtkb-state/transactions/one.json") is None
    assert resolver.resolve_operation_path(".gtkb-state/transactions/one.json") == opaque
    assert resolver.resolve_operation_path("outside.json") is None


def test_snapshot_requires_byte_identical_packaged_mirror(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    packaged.write_text("drift", encoding="utf-8")
    with pytest.raises(Exception, match="byte-identical"):
        load_registry_snapshot(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        )


def test_snapshot_reports_projection_drift_as_typed_failure(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("one", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    changed = [replace(records[0], mutation_api="changed")]
    payload = serialize_registry(changed)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)

    with pytest.raises(RegistryProjectionMismatch, match="parity failure"):
        load_registry_snapshot(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        )


@pytest.mark.parametrize(
    ("phase", "outcome"),
    [
        ("after_prepare", "old"),
        ("after_canonical_replace", "new"),
        ("after_packaged_replace", "new"),
        ("after_db_update", "new"),
        ("after_journal_commit", "new"),
    ],
)
def test_fault_phases_never_expose_mixed_generation(tmp_path: Path, phase: str, outcome: str) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    old = [_record("one", "one.txt")]
    desired = [*old, _record("two", "two.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, old)

    def fail_at(observed: str) -> None:
        if observed == phase:
            raise RuntimeError(phase)

    with pytest.raises(RuntimeError, match=phase):
        apply_registry_transaction(
            desired,
            operation="register",
            failure_injector=fail_at,
            **_transaction_kwargs(tmp_path, registry, packaged, db_path),
        )
    if phase != "after_journal_commit":
        with pytest.raises(RegistryTransactionInProgress):
            load_registry_snapshot(
                project_root=tmp_path,
                registry_path=registry,
                packaged_registry_path=packaged,
                db_path=db_path,
            )
    recover_registry(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert {record.id for record in snapshot.records} == ({"one"} if outcome == "old" else {"one", "two"})


def test_registry_recovery_marks_unknown_digest_combination_repair_required(
    tmp_path: Path,
) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    old = [_record("one", "one.txt")]
    desired = [*old, _record("two", "two.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, old)

    def fail_after_canonical(observed: str) -> None:
        if observed == "after_canonical_replace":
            raise RuntimeError(observed)

    with pytest.raises(RuntimeError, match="after_canonical_replace"):
        apply_registry_transaction(
            desired,
            operation="register",
            failure_injector=fail_after_canonical,
            **_transaction_kwargs(tmp_path, registry, packaged, db_path),
        )
    packaged.write_text("unknown generation\n", encoding="utf-8")

    with pytest.raises(RegistryRecoveryRequired, match="mixed or unknown generation"):
        recover_registry(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        )

    conn = sqlite3.connect(db_path)
    try:
        state = conn.execute(
            "SELECT journal_state FROM sot_registry_transaction_journal ORDER BY rowid DESC LIMIT 1"
        ).fetchone()[0]
    finally:
        conn.close()
    assert state == "repair_required"


def test_identical_transaction_retry_returns_same_receipt(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    records = [_record("one", "one.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    first = apply_registry_transaction(records, operation="amend", **kwargs)
    second = apply_registry_transaction(records, operation="amend", **kwargs)
    assert second.receipt_digest == first.receipt_digest
    assert second.idempotent_retry is True


def test_registry_transaction_updates_both_declaration_revisions(tmp_path: Path) -> None:
    records = [
        _record("canonical-registry", "config/registry/sot-artifacts.toml"),
        _record(
            "packaged-registry",
            "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml",
        ),
    ]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)

    apply_registry_transaction(
        records,
        operation="amend",
        **_transaction_kwargs(tmp_path, registry, packaged, db_path),
    )

    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    assert registry_currentness(snapshot, project_root=tmp_path, db_path=db_path) == {
        "current": True,
        "missing_revisions": [],
        "stale": [],
    }


def test_bootstrap_binds_exact_legacy_input_and_is_idempotent(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[2] / "config" / "registry" / "sot-artifacts.toml"
    current_records = _load_toml_unlocked(source, allow_missing_coverage=True)
    old_records = [record for record in current_records if record.id in LEGACY_COVERAGE_MODES]
    assert {record.id for record in old_records} == set(LEGACY_COVERAGE_MODES)
    legacy_payload = serialize_registry(old_records)
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
    registry.write_bytes(legacy_payload)
    packaged.write_bytes(legacy_payload)
    for artifact in IMPLEMENTATION_ARTIFACTS:
        target = tmp_path / artifact.storage_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# fixture\n", encoding="utf-8")
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(old_records, db_path, changed_by="test", change_reason="legacy fixture")
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    first = bootstrap_legacy_registry(**kwargs)
    second = bootstrap_legacy_registry(**kwargs)
    assert first.receipt_digest == second.receipt_digest
    assert second.idempotent_retry is True
    assert registry.read_bytes() == packaged.read_bytes()
    records = load_toml(registry)
    assert len(records) == 54
    assert all(record.coverage_mode is not None for record in records)


def test_census_uses_only_git_and_application_root_boundaries(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden").write_text("x", encoding="utf-8")
    (tmp_path / "applications" / "Demo").mkdir(parents=True)
    (tmp_path / "applications" / "Demo" / "hidden.py").write_text("x", encoding="utf-8")
    (tmp_path / "applications" / "registry.toml").write_text("x", encoding="utf-8")
    (tmp_path / ".gtkb-state" / "runtime").mkdir(parents=True)
    (tmp_path / ".gtkb-state" / "runtime" / "visible.log").write_text("x", encoding="utf-8")
    (tmp_path / "member.txt").write_text("x", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    census = census_registry(snapshot, project_root=tmp_path)
    paths = {entry.relative_path: entry for entry in census}
    assert paths[".git"].object_kind == "vcs_service_state"
    assert ".git/hidden" not in paths
    assert paths["applications/Demo"].object_kind == "hosted_application_root"
    assert "applications/Demo/hidden.py" not in paths
    assert "applications/registry.toml" in paths
    assert ".gtkb-state/runtime/visible.log" in paths


def test_opaque_container_may_register_a_service_owned_file(tmp_path: Path) -> None:
    records = [_record("database", "groundtruth.db", "opaque_container")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)

    snapshot = load_registry_snapshot(
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    assert snapshot.resolver.resolve("groundtruth.db") == records[0]


def test_passive_observation_records_view_without_authorizing_content(tmp_path: Path) -> None:
    member = tmp_path / "member.txt"
    member.write_text("before", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    member.write_text("direct owner edit", encoding="utf-8")

    revisions = append_passive_observation(
        target_paths=["member.txt"],
        evidence_view="working_tree",
        evidence_source_reference="filesystem-audit:test",
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM sot_artifact_revisions WHERE revision_id = ?",
            (revisions[0],),
        ).fetchone()
    finally:
        conn.close()
    assert member.read_text(encoding="utf-8") == "direct owner edit"
    assert row["actor_session"] == "unattributed_external"
    assert row["evidence_view"] == "working_tree"
    assert row["evidence_source_reference"] == "filesystem-audit:test"


def test_registration_preview_binds_generation_manifest_and_authority(tmp_path: Path) -> None:
    (tmp_path / "one.txt").write_text("one", encoding="utf-8")
    (tmp_path / "two.txt").write_text("two", encoding="utf-8")
    current = [_record("one", "one.txt")]
    addition = _record("two", "two.txt")
    registry, packaged, db_path = _fixture_generation(tmp_path, current)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    observer_digests = {
        "capability_inventory": f"sha256:{1:064x}",
        "governed_knowledge": f"sha256:{2:064x}",
        "package_and_entrypoint": f"sha256:{3:064x}",
        "physical_census": f"sha256:{4:064x}",
        "registered_dependency_closure": f"sha256:{5:064x}",
    }
    evidence_digest = f"sha256:{6:064x}"
    preview = preview_registry_registration(
        [addition],
        actor_session=str(kwargs["actor_session"]),
        start_packet_hash=str(kwargs["start_packet_hash"]),
        pauth_id=str(kwargs["pauth_id"]),
        bridge_id=str(kwargs["bridge_id"]),
        candidate_manifest_sha256="sha256:manifest",
        observer_input_digests=observer_digests,
        reconciliation_evidence_digest=evidence_digest,
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )

    receipt = register_artifacts(
        [addition],
        expected_generation_digest=preview.starting_generation_digest,
        candidate_manifest_sha256=preview.candidate_manifest_sha256,
        observer_input_digests=observer_digests,
        reconciliation_evidence_digest=evidence_digest,
        dry_run_receipt=preview.dry_run_receipt,
        **kwargs,
    )
    retry = register_artifacts(
        [addition],
        expected_generation_digest=preview.starting_generation_digest,
        candidate_manifest_sha256=preview.candidate_manifest_sha256,
        observer_input_digests=observer_digests,
        reconciliation_evidence_digest=evidence_digest,
        dry_run_receipt=preview.dry_run_receipt,
        **kwargs,
    )

    assert preview.candidate_count == 1
    assert preview.observer_input_digests == dict(sorted(observer_digests.items()))
    assert preview.reconciliation_evidence_digest == evidence_digest
    assert preview.desired_record_count == 2
    assert receipt.record_count == 2
    assert retry.idempotent_retry is True
    assert retry.journal_id == receipt.journal_id
    assert {
        record.id
        for record in load_registry_snapshot(
            project_root=tmp_path,
            registry_path=registry,
            packaged_registry_path=packaged,
            db_path=db_path,
        ).records
    } == {"one", "two"}

    with pytest.raises(RegistryAuthorizationError, match="exact dry-run receipt"):
        register_artifacts(
            [addition],
            expected_generation_digest=preview.starting_generation_digest,
            candidate_manifest_sha256=preview.candidate_manifest_sha256,
            observer_input_digests={**observer_digests, "physical_census": f"sha256:{7:064x}"},
            reconciliation_evidence_digest=evidence_digest,
            dry_run_receipt=preview.dry_run_receipt,
            **kwargs,
        )


def test_observation_capability_is_bound_single_use_and_updates_revision(tmp_path: Path) -> None:
    member = tmp_path / "member.txt"
    member.write_text("before", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }
    capability = mint_observation_capability(
        target_paths=["member.txt"],
        session_id="session",
        tool_event_id="event",
        bridge_id="bridge",
        start_packet_hash="packet",
        pauth_decision={"allowed": True},
        operation="edit",
        authorized=True,
        **kwargs,
    )
    member.write_text("after", encoding="utf-8")
    revisions = consume_observation_capability(
        capability=capability["capability"],
        target_paths=["member.txt"],
        preimage_digests=capability["preimage_digests"],
        session_id="session",
        tool_event_id="event",
        bridge_id="bridge",
        start_packet_hash="packet",
        operation="edit",
        tool_succeeded=True,
        tool_result={"ok": True},
        changed_by="test",
        change_reason="test observation",
        **kwargs,
    )
    assert len(revisions) == 1
    with pytest.raises(RegistryAuthorizationError, match="already consumed"):
        consume_observation_capability(
            capability=capability["capability"],
            target_paths=["member.txt"],
            preimage_digests=capability["preimage_digests"],
            session_id="session",
            tool_event_id="event",
            bridge_id="bridge",
            start_packet_hash="packet",
            operation="edit",
            tool_succeeded=True,
            tool_result={"ok": True},
            changed_by="test",
            change_reason="replay",
            **kwargs,
        )


def test_amend_rejects_identity_locator_coverage_and_lifecycle_fields(tmp_path: Path) -> None:
    (tmp_path / "member.txt").write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)

    for field, value in (
        ("id", "replacement"),
        ("storage_path", "replacement.txt"),
        ("coverage_mode", "recursive"),
        ("lifecycle", "deprecated"),
    ):
        with pytest.raises(RegistryAuthorizationError, match="transition authority"):
            amend_artifact("member", {field: value}, **kwargs)


def test_registry_cli_exposes_governed_control_plane_commands() -> None:
    result = CliRunner().invoke(main, ["registry", "--help"])

    assert result.exit_code == 0, result.output
    for command in ("register", "amend", "inspect", "recover", "validate"):
        assert command in result.output


def test_registry_cli_register_amend_sync_and_direct_observe_denial(tmp_path: Path) -> None:
    member = tmp_path / "member.txt"
    member.write_text("member", encoding="utf-8")
    records = [_record("member", "member.txt")]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    kwargs = _transaction_kwargs(tmp_path, registry, packaged, db_path)
    apply_registry_transaction(records, operation="legacy_bootstrap", **kwargs)
    config = tmp_path / "groundtruth.toml"
    config.write_text(
        f'[groundtruth]\nproject_root = "{tmp_path.as_posix()}"\ndb_path = "{db_path.as_posix()}"\n',
        encoding="utf-8",
    )
    second = _record("second", "second.txt")
    (tmp_path / "second.txt").write_text("second", encoding="utf-8")
    authority = [
        "--bridge-id",
        "gtkb-wi5441-registry-control-plane-reverse-coverage",
        "--session-id",
        "test-session",
        "--start-packet-hash",
        "sha256:test-start",
        "--pauth-id",
        "PAUTH-WI5441-TEST",
        "--changed-by",
        "test/prime-builder",
        "--change-reason",
        "WI-5441 CLI fixture",
    ]
    runner = CliRunner()

    registered = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "register",
            "--record-json",
            json.dumps(asdict(second)),
            *authority,
        ],
    )
    assert registered.exit_code == 0, registered.output
    assert {record.id for record in load_registry_snapshot(project_root=tmp_path).records} == {
        "member",
        "second",
    }

    amended = runner.invoke(
        main,
        [
            "--config",
            str(config),
            "registry",
            "amend",
            "second",
            "--changes-json",
            json.dumps({"notes": "amended through CLI"}),
            *authority,
        ],
    )
    assert amended.exit_code == 0, amended.output
    snapshot = load_registry_snapshot(project_root=tmp_path)
    assert next(record for record in snapshot.records if record.id == "second").notes == "amended through CLI"

    synced = runner.invoke(main, ["--config", str(config), "registry", "sync"])
    assert synced.exit_code == 0, synced.output
    assert "diagnostic-only" in synced.output

    event = tmp_path / "event.json"
    event.write_text("{}", encoding="utf-8")
    observed = runner.invoke(
        main,
        ["--config", str(config), "registry", "observe", "--event-file", str(event)],
    )
    assert observed.exit_code != 0
    assert "capability" in observed.output.lower()


def _bridge_publication_fixture(
    tmp_path: Path,
) -> tuple[str, str, bytes, Path, dict[str, object]]:
    slug = "typed-publication-fixture"
    session_id = "publication-session"
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    records = [
        _record(
            "bridge-versioned-files",
            "bridge/*-[0-9][0-9][0-9].md",
            "glob",
        )
    ]
    registry, packaged, db_path = _fixture_generation(tmp_path, records)
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        **_transaction_kwargs(tmp_path, registry, packaged, db_path),
    )
    assert acquire(slug, session_id, project_root=tmp_path)
    content = (
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n"
        "author_identity: prime-builder/codex\n"
        "author_harness_id: test\n"
        f"author_session_context_id: {session_id}\n"
        "author_model: fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: unit-test\n"
        "author_metadata_source: unit-test\n\n"
        "# Typed Publication Fixture\n\n"
        "bridge_kind: prime_proposal\n"
        f"Document: {slug}\n"
        "Version: 001\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-0001\n"
        'target_paths: ["scripts/example.py"]\n'
    ).encode()
    target = bridge_dir / f"{slug}-001.md"
    kwargs: dict[str, object] = {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }
    return slug, session_id, content, target, kwargs


def test_bridge_publication_capability_is_exact_single_use_and_current(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    receipt = consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason="typed bridge publication",
        **kwargs,
    )
    assert receipt.capability_state == "consumed"
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
    )["current"]
    with pytest.raises(RegistryAuthorizationError, match="already consumed"):
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason="replay",
            **kwargs,
        )


def test_bridge_publication_compensation_restores_preimage_currentness(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason="typed bridge publication",
        **kwargs,
    )
    receipt = compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="downstream publication failure",
        changed_by="test",
        **kwargs,
    )
    assert receipt.capability_state == "compensated"
    assert not target.exists()
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
    )["current"]


def test_bridge_publication_rejects_missing_claim(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    release_claim(slug, session_id, project_root=tmp_path)

    with pytest.raises(RegistryAuthorizationError, match="exact live work-intent claim"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )


def test_bridge_publication_rejects_session_status_path_and_compliance_mismatches(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)

    with pytest.raises(RegistryAuthorizationError, match="author session and claim session differ"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id="other-session",
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="exact requested terminal state"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="REVISED",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="invalid candidate bridge lifecycle"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=2,
            status="NEW",
            target_path=target.with_name(f"{slug}-002.md"),
            content=content.replace(b"Version: 001", b"Version: 002"),
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="target mismatch"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target.with_name("wrong-001.md"),
            content=content,
            session_id=session_id,
            compliance_digest="sha256:test-compliance",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="bindings must be non-empty"):
        mint_bridge_publication_capability(
            document_name=slug,
            version=1,
            status="NEW",
            target_path=target,
            content=content,
            session_id=session_id,
            compliance_digest="",
            **kwargs,
        )


def test_bridge_publication_rejects_content_mismatch_and_fabricated_capability(
    tmp_path: Path,
) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)

    with pytest.raises(RegistryAuthorizationError, match="content binding mismatch"):
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content + b"\n",
            session_id=session_id,
            changed_by="test",
            change_reason="tampered content",
            **kwargs,
        )
    with pytest.raises(RegistryAuthorizationError, match="unknown or fabricated"):
        consume_bridge_publication_capability(
            capability="fabricated-capability",
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason="fabricated capability",
            **kwargs,
        )
    compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="negative binding test cleanup",
        changed_by="test",
        **kwargs,
    )


def test_bridge_publication_rejects_expired_capability(tmp_path: Path) -> None:
    slug, session_id, content, target, kwargs = _bridge_publication_fixture(tmp_path)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest="sha256:test-compliance",
        **kwargs,
    )
    target.write_bytes(content)
    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities SET expires_at = ? WHERE capability_hash = ?",
            ("2000-01-01T00:00:00Z", minted["capability_hash"]),
        )

    with pytest.raises(RegistryAuthorizationError, match="capability expired"):
        consume_bridge_publication_capability(
            capability=minted["capability"],
            target_path=target,
            content=content,
            session_id=session_id,
            changed_by="test",
            change_reason="expired capability",
            **kwargs,
        )
    compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="expiry test cleanup",
        changed_by="test",
        **kwargs,
    )


def test_retired_wi5441_recovery_entry_point_fails_closed() -> None:
    with pytest.raises(RegistryAuthorizationError, match="is retired"):
        recover_wi5441_bridge_aggregate(
            actor_session="session",
            bridge_id="bridge",
            start_packet_hash="packet",
            pauth_id="pauth",
            changed_by="test",
            change_reason="must not run",
        )
