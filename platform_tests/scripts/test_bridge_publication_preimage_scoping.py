# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Specification-derived tests for WI-5977 thread-scoped compensation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import registry_control_plane
from groundtruth_kb.project.registry_control_plane import (
    RegistryRecoveryRequired,
    apply_registry_transaction,
    compensate_bridge_publication,
    consume_bridge_publication_capability,
    load_registry_snapshot,
    mint_bridge_publication_capability,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

from scripts.bridge_work_intent_registry import acquire


def _record() -> SoTArtifact:
    return SoTArtifact(
        id="bridge-versioned-files",
        domain="control_surface",
        lifecycle="active",
        storage_path="bridge/*-[0-9][0-9][0-9].md",
        authority_spec_id="GOV-FILE-BRIDGE-AUTHORITY-001",
        mutation_api="gt registry register",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode="glob",
    )


def _fixture(tmp_path: Path) -> tuple[str, dict[str, object]]:
    session_id = "publication-session"
    (tmp_path / "bridge").mkdir()
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
    records = [_record()]
    payload = serialize_registry(records)
    registry.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        actor_session="test-session",
        changed_by="test/prime-builder",
        change_reason="WI-5977 fixture transaction",
        start_packet_hash="sha256:test-start",
        pauth_id="PAUTH-WI5977-TEST",
        bridge_id="gtkb-w0p-finalization-machinery-repair",
        project_root=tmp_path,
        registry_path=registry,
        packaged_registry_path=packaged,
        db_path=db_path,
    )
    return session_id, {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }


def _content(
    slug: str,
    session_id: str,
    *,
    version: int = 1,
    status: str = "NEW",
) -> bytes:
    role = "lo" if status in {"GO", "NO-GO", "VERIFIED"} else "pb"
    identity = "loyal-opposition/test" if role == "lo" else "prime-builder/test"
    lines = [
        status,
        f"::init gtkb {role}",
        "::open test" if role == "lo" else "::open build",
        "",
        f"author_identity: {identity}",
        "author_harness_id: test",
        f"author_session_context_id: {session_id}",
        "author_model: fixture",
        "author_model_version: fixture",
        "author_model_configuration: unit-test",
        "author_metadata_source: unit-test",
        "",
        f"Document: {slug}",
        f"Version: {version:03d}",
    ]
    if version > 1:
        lines.append(f"Responds to: bridge/{slug}-{version - 1:03d}.md")
    lines.extend(("", f"# {slug} v{version}", ""))
    return "\n".join(lines).encode()


def _publish(
    slug: str,
    session_id: str,
    kwargs: dict[str, object],
    *,
    version: int = 1,
    status: str = "NEW",
) -> tuple[dict[str, object], Path, bytes]:
    assert acquire(slug, session_id, project_root=kwargs["project_root"])
    target = Path(kwargs["project_root"]) / "bridge" / f"{slug}-{version:03d}.md"
    content = _content(slug, session_id, version=version, status=status)
    minted = mint_bridge_publication_capability(
        document_name=slug,
        version=version,
        status=status,
        target_path=target,
        content=content,
        session_id=session_id,
        compliance_digest=f"sha256:test-compliance-{slug}-{version}",
        **kwargs,
    )
    target.write_bytes(content)
    consume_bridge_publication_capability(
        capability=minted["capability"],
        target_path=target,
        content=content,
        session_id=session_id,
        changed_by="test",
        change_reason=f"publish {slug} v{version}",
        **kwargs,
    )
    return minted, target, content


def _capability_row(kwargs: dict[str, object], capability_hash: str) -> sqlite3.Row:
    with sqlite3.connect(str(kwargs["db_path"])) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (capability_hash,),
        ).fetchone()
    assert row is not None
    return row


def test_unrelated_thread_append_is_not_a_compensation_veto(tmp_path: Path) -> None:
    session_id, kwargs = _fixture(tmp_path)
    first, first_target, _ = _publish("publication-a", session_id, kwargs)
    _, unrelated_target, _ = _publish("publication-b", session_id, kwargs)

    receipt = compensate_bridge_publication(
        capability=first["capability"],
        target_path=first_target,
        session_id=session_id,
        reason="downstream failure after unrelated publication",
        changed_by="test",
        **kwargs,
    )

    assert receipt.capability_state == "compensated"
    assert not first_target.exists()
    assert unrelated_target.is_file()
    assert receipt.aggregate_digest != first["aggregate_preimage_digest"]
    assert _capability_row(kwargs, first["capability_hash"])["capability_state"] == "compensated"
    snapshot = load_registry_snapshot(**kwargs)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=kwargs["db_path"],
        record_ids={"bridge-versioned-files"},
    )["current"]


def test_same_thread_successor_still_fails_closed(tmp_path: Path) -> None:
    session_id, kwargs = _fixture(tmp_path)
    first, first_target, _ = _publish("publication-a", session_id, kwargs)
    _, successor_target, _ = _publish(
        "publication-a",
        session_id,
        kwargs,
        version=2,
        status="GO",
    )

    with pytest.raises(RegistryRecoveryRequired, match="thread preimage"):
        compensate_bridge_publication(
            capability=first["capability"],
            target_path=first_target,
            session_id=session_id,
            reason="must not cross a same-thread successor",
            changed_by="test",
            **kwargs,
        )

    assert first_target.is_file()
    assert successor_target.is_file()
    assert _capability_row(kwargs, first["capability_hash"])["capability_state"] == "recovery_required"


def test_target_content_mismatch_still_fails_closed(tmp_path: Path) -> None:
    session_id, kwargs = _fixture(tmp_path)
    minted, target, content = _publish("publication-a", session_id, kwargs)
    target.write_bytes(content + b"tampered")

    with pytest.raises(RegistryRecoveryRequired, match="target bytes changed"):
        compensate_bridge_publication(
            capability=minted["capability"],
            target_path=target,
            session_id=session_id,
            reason="must retain unknown target bytes",
            changed_by="test",
            **kwargs,
        )

    assert target.read_bytes() == content + b"tampered"
    assert _capability_row(kwargs, minted["capability_hash"])["capability_state"] == "recovery_required"


def test_predecessor_body_drift_preserves_target_and_requires_recovery(tmp_path: Path) -> None:
    session_id, kwargs = _fixture(tmp_path)
    _, predecessor, predecessor_content = _publish("publication-a", session_id, kwargs)
    minted, target, target_content = _publish(
        "publication-a",
        session_id,
        kwargs,
        version=2,
        status="GO",
    )
    predecessor.write_bytes(predecessor_content + b"\nbody drift without metadata drift\n")

    with pytest.raises(RegistryRecoveryRequired, match="thread preimage changed"):
        compensate_bridge_publication(
            capability=minted["capability"],
            target_path=target,
            session_id=session_id,
            reason="must bind exact predecessor bytes",
            changed_by="test",
            **kwargs,
        )

    assert predecessor.read_bytes() == predecessor_content + b"\nbody drift without metadata drift\n"
    assert target.read_bytes() == target_content
    assert _capability_row(kwargs, minted["capability_hash"])["capability_state"] == "recovery_required"


def test_thread_and_aggregate_audit_evidence_remains_bound(tmp_path: Path) -> None:
    session_id, kwargs = _fixture(tmp_path)
    minted, target, content = _publish("publication-a", session_id, kwargs)

    receipt = compensate_bridge_publication(
        capability=minted["capability"],
        target_path=target,
        session_id=session_id,
        reason="audit evidence fixture",
        changed_by="test",
        **kwargs,
    )

    row = _capability_row(kwargs, minted["capability_hash"])
    assert row["aggregate_preimage_digest"] == minted["aggregate_preimage_digest"]
    assert row["transition_digest"] == minted["transition_digest"]
    assert row["compensation_revision_id"] == receipt.revision_id
    assert row["compensation_digest"] == registry_control_plane._json_digest(
        {
            "target_path": "bridge/publication-a-001.md",
            "aggregate_preimage_digest": minted["aggregate_preimage_digest"],
            "observed_aggregate_digest": receipt.aggregate_digest,
            "thread_transition_digest": minted["transition_digest"],
            "reason": "audit evidence fixture",
            "compensation_revision_id": receipt.revision_id,
        }
    )
    assert (
        registry_control_plane._bridge_publication_transition_digest(
            tmp_path,
            document_name="publication-a",
            version=1,
            status="NEW",
            content=content,
        )
        == minted["transition_digest"]
    )
