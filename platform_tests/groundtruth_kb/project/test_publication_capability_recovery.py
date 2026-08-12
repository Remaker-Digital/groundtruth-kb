"""Specification-derived tests for WI-5950 publication-receipt recovery."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    RegistryAuthorizationError,
    RegistryRecoveryRequired,
    apply_registry_transaction,
    consume_bridge_publication_capability,
    load_registry_snapshot,
    mint_bridge_publication_capability,
    recover_missing_bridge_publication_capability,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

from scripts.bridge_work_intent_registry import acquire


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


def _fixture(tmp_path: Path) -> tuple[str, str, bytes, Path, dict[str, object]]:
    slug = "publication-recovery-fixture"
    author_session = "original-author-session"
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
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
    registry_kwargs: dict[str, object] = {
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
        pauth_id="PAUTH-WI5950-TEST",
        bridge_id=slug,
        **registry_kwargs,
    )
    content = (
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n"
        "author_identity: prime-builder/codex\n"
        "author_harness_id: test\n"
        f"author_session_context_id: {author_session}\n"
        "author_model: fixture\n"
        "author_model_version: fixture\n"
        "author_model_configuration: unit-test\n"
        "author_metadata_source: unit-test\n\n"
        "bridge_kind: prime_proposal\n"
        f"Document: {slug}\n"
        "Version: 001\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-5950\n"
        'target_paths: ["scripts/example.py"]\n'
    ).encode()
    target = bridge_dir / f"{slug}-001.md"
    target.write_bytes(content)
    return slug, author_session, content, target, registry_kwargs


def test_recovery_command_exported() -> None:
    assert callable(recover_missing_bridge_publication_capability)


def test_recovery_requires_owner_authorization() -> None:
    with pytest.raises(RegistryAuthorizationError, match="requires owner authorization"):
        recover_missing_bridge_publication_capability(
            document_name="gtkb-test",
            version=1,
            target_path="bridge/gtkb-test-001.md",
            content=b"x",
            session_id="sess",
            owner_authorization="",
        )


def test_recovery_rejects_unknown_target(tmp_path: Path) -> None:
    slug, _, content, target, registry_kwargs = _fixture(tmp_path)
    target.unlink()

    with pytest.raises(RegistryRecoveryRequired, match="target is missing"):
        recover_missing_bridge_publication_capability(
            document_name=slug,
            version=1,
            target_path=target,
            content=content,
            session_id="recovery-session",
            owner_authorization="DELIB-WI5950-RECOVERY-TEST",
            **registry_kwargs,
        )


def test_recovery_backfills_one_consumed_receipt_without_changing_target(tmp_path: Path) -> None:
    slug, author_session, content, target, registry_kwargs = _fixture(tmp_path)

    receipt = recover_missing_bridge_publication_capability(
        document_name=slug,
        version=1,
        target_path=target,
        content=content,
        session_id="recovery-session",
        owner_authorization="DELIB-WI5950-RECOVERY-TEST",
        **registry_kwargs,
    )

    assert receipt.capability_state == "consumed"
    assert target.read_bytes() == content
    snapshot = load_registry_snapshot(**registry_kwargs)
    assert registry_currentness(
        snapshot,
        project_root=registry_kwargs["project_root"],
        db_path=registry_kwargs["db_path"],
    )["current"]
    conn = sqlite3.connect(str(registry_kwargs["db_path"]))
    try:
        row = conn.execute(
            """
            SELECT capability_state, claim_session, author_session_context_id, capability_hash,
                   operation, revision_id
            FROM sot_registry_bridge_publication_capabilities
            WHERE target_path = ?
            """,
            (f"bridge/{slug}-001.md",),
        ).fetchone()
        revision = conn.execute(
            """
            SELECT changed_by, change_reason, evidence_view
            FROM sot_artifact_revisions
            WHERE revision_id = ?
            """,
            (receipt.revision_id,),
        ).fetchone()
    finally:
        conn.close()
    assert row == (
        "consumed",
        "recovery-session",
        author_session,
        receipt.capability_hash,
        "bridge_publication",
        receipt.revision_id,
    )
    assert revision == (
        "bridge-publication-recovery",
        "owner-authorized bridge publication receipt backfill: DELIB-WI5950-RECOVERY-TEST",
        "recovery",
    )


def test_recovery_rejects_content_drift_and_duplicate_receipt(tmp_path: Path) -> None:
    slug, _, content, target, registry_kwargs = _fixture(tmp_path)

    with pytest.raises(RegistryAuthorizationError, match="target bytes do not match content"):
        recover_missing_bridge_publication_capability(
            document_name=slug,
            version=1,
            target_path=target,
            content=content + b"tampered",
            session_id="recovery-session",
            owner_authorization="DELIB-WI5950-RECOVERY-TEST",
            **registry_kwargs,
        )

    recover_missing_bridge_publication_capability(
        document_name=slug,
        version=1,
        target_path=target,
        content=content,
        session_id="recovery-session",
        owner_authorization="DELIB-WI5950-RECOVERY-TEST",
        **registry_kwargs,
    )
    with pytest.raises(RegistryAuthorizationError, match="already holds a publication capability receipt"):
        recover_missing_bridge_publication_capability(
            document_name=slug,
            version=1,
            target_path=target,
            content=content,
            session_id="recovery-session",
            owner_authorization="DELIB-WI5950-RECOVERY-TEST",
            **registry_kwargs,
        )


def test_recovery_preserves_existing_native_receipt(tmp_path: Path) -> None:
    slug, author_session, content, target, registry_kwargs = _fixture(tmp_path)
    target.unlink()
    assert acquire(slug, author_session, project_root=registry_kwargs["project_root"])
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=1,
        status="NEW",
        target_path=target,
        content=content,
        session_id=author_session,
        compliance_digest="sha256:test-compliance",
        **registry_kwargs,
    )
    target.write_bytes(content)
    consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=author_session,
        changed_by="test",
        change_reason="native receipt",
        **registry_kwargs,
    )

    with pytest.raises(RegistryAuthorizationError, match="already holds a publication capability receipt"):
        recover_missing_bridge_publication_capability(
            document_name=slug,
            version=1,
            target_path=target,
            content=content,
            session_id="recovery-session",
            owner_authorization="DELIB-WI5950-RECOVERY-TEST",
            **registry_kwargs,
        )
