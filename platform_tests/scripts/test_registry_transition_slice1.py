# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Specification-derived tests for WI-5928 Slice 1 registry identity-transition surface.

Governing specifications (carried forward from
bridge/gtkb-wi5928-registry-transition-surface-slice1-003.md GO at -004):

- DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001 - transition request/apply is the
  only lawful path for coverage-mode / membership identity transitions; apply is gated
  on an OPS envelope, a matching active request, a matching independent bridge GO, and
  fresh operation-time revalidation.
- GOV-PLATFORM-SOT-REGISTRY-001 - a coverage-mode transition plus membership removal
  commits through the transition surface and the registry validates afterward.
- DCL-SOT-REGISTRY-PROJECTION-PARITY-001 - declaration/projection parity holds after a
  transition apply.

Binding start holds proven here:
- Hold 1 (request journal hygiene): a transition request never leaves the transaction
  journal in a non-terminal state (dedicated capability table).
- Hold 2 (apply digest binding): apply revalidates the bound generation digest.
- Hold 3 (no live mutation): every test runs against fixture registry paths only.
- Hold 6 (independent GO per apply): apply rejects a same-session (self-review) GO.

Slice 1 scope: membership-set removals and in-place coverage-mode changes only.
Move/rename/delete transitions are deferred and rejected.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    RegistryAuthorizationError,
    RegistryGenerationConflict,
    _nonterminal_journal,
    amend_artifact,
    load_registry_snapshot,
    serialize_registry,
    transition_apply,
    transition_request,
    validate_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

_OWNER_EVIDENCE = {
    "bridge_id": "gtkb-wi5928-registry-transition-surface-slice1",
    "pauth_id": "PAUTH-WI5928-TEST",
    "owner_decision": "DELIB-202668163",
}
_INDEPENDENT_GO = {
    "status": "GO",
    "bridge_id": "gtkb-wi5928-registry-transition-apply",
    "author_session_context_id": "lo-reviewer-session",
}
_OPS_ENVELOPE = {"envelope_id": "OPS-ENV-TEST", "activity": "ops"}


def _record(record_id: str, storage_path: str, coverage_mode: str = "exact") -> SoTArtifact:
    return SoTArtifact(
        id=record_id,
        domain="control_surface",
        lifecycle="active",
        storage_path=storage_path,
        authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
        mutation_api="gt registry transition",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode=coverage_mode,
    )


def _initial_records() -> list[SoTArtifact]:
    # Overlap-clean starting generation: an opaque container plus two exact members
    # under it, and one unrelated recursive tree that must survive the transition.
    return [
        _record("pkg-container", "pkg/", "opaque_container"),
        _record("pkg-a", "pkg/a.py", "exact"),
        _record("pkg-b", "pkg/b.py", "exact"),
        _record("other-tree", "other/", "recursive"),
    ]


def _fixture_generation(tmp_path: Path, records: list[SoTArtifact]) -> dict[str, Path]:
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
    # registry_identity_state requires each active declaration's path to exist on disk
    # (recursive/opaque_container => directory; exact => a file).
    for rec in records:
        if rec.coverage_mode == "virtual":
            continue
        target = tmp_path / rec.storage_path.rstrip("/")
        if rec.coverage_mode in {"recursive", "opaque_container"}:
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("# fixture\n", encoding="utf-8")
    return {
        "project_root": tmp_path,
        "registry_path": registry,
        "packaged_registry_path": packaged,
        "db_path": db_path,
    }


def _auth(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "actor_session": "prime-apply-session",
        "changed_by": "test/prime-builder",
        "change_reason": "WI-5928 transition test",
        "start_packet_hash": "sha256:test-start",
        "pauth_id": "PAUTH-WI5928-TEST",
        "bridge_id": "gtkb-wi5928-registry-transition-surface-slice1",
    }
    base.update(overrides)
    return base


def _open_request(paths: dict[str, Path]) -> dict[str, object]:
    return transition_request(
        entry_id="pkg-container",
        operation="coverage_and_membership",
        owner_evidence=_OWNER_EVIDENCE,
        coverage_changes={"pkg-container": "recursive"},
        removals=["pkg-a", "pkg-b"],
        expiry_seconds=900,
        **_auth(),
        **paths,
    )


# --- transition_request -----------------------------------------------------


def test_request_binds_dcl_fields_and_keeps_journal_clean(tmp_path: Path) -> None:
    """DCL fields bound; Hold 1: the transaction journal stays terminal (dedicated table)."""
    paths = _fixture_generation(tmp_path, _initial_records())
    handle = _open_request(paths)

    assert handle["request_state"] == "active"
    assert handle["entry_id"] == "pkg-container"
    assert handle["source_locator"] == "pkg/"
    assert handle["current_revision_digest"].startswith("sha256:")
    assert handle["intended_membership_result"]["removals"] == ["pkg-a", "pkg-b"]
    assert handle["intended_membership_result"]["coverage_changes"] == {"pkg-container": "recursive"}
    # Hold 1: no non-terminal registry transaction journal row was created.
    assert _nonterminal_journal(paths["db_path"]) is None


def test_request_rejects_deferred_move_operation(tmp_path: Path) -> None:
    """Slice 1 scope: move/rename/delete transitions are deferred and rejected."""
    paths = _fixture_generation(tmp_path, _initial_records())
    with pytest.raises(RegistryAuthorizationError, match="deferred to a later slice"):
        transition_request(
            entry_id="pkg-container",
            operation="move",
            owner_evidence=_OWNER_EVIDENCE,
            removals=["pkg-a"],
            **_auth(),
            **paths,
        )


def test_request_requires_owner_evidence(tmp_path: Path) -> None:
    paths = _fixture_generation(tmp_path, _initial_records())
    with pytest.raises(RegistryAuthorizationError, match="owner evidence"):
        transition_request(
            entry_id="pkg-container",
            operation="coverage_and_membership",
            owner_evidence={},
            coverage_changes={"pkg-container": "recursive"},
            removals=["pkg-a", "pkg-b"],
            **_auth(),
            **paths,
        )


# --- transition_apply gates -------------------------------------------------


def test_apply_rejects_without_ops_envelope(tmp_path: Path) -> None:
    """Gate 1: an OPS envelope is required."""
    paths = _fixture_generation(tmp_path, _initial_records())
    handle = _open_request(paths)
    with pytest.raises(RegistryAuthorizationError, match="ops envelope"):
        transition_apply(
            request_id=str(handle["request_id"]),
            ops_envelope={},
            apply_authorization=_INDEPENDENT_GO,
            **_auth(),
            **paths,
        )


def test_apply_rejects_without_active_request(tmp_path: Path) -> None:
    """Gate 2: a matching active request is required."""
    paths = _fixture_generation(tmp_path, _initial_records())
    with pytest.raises(RegistryAuthorizationError, match="no matching active transition request"):
        transition_apply(
            request_id="REGTXNREQ-DOESNOTEXIST",
            ops_envelope=_OPS_ENVELOPE,
            apply_authorization=_INDEPENDENT_GO,
            **_auth(),
            **paths,
        )


def test_apply_rejects_without_independent_go(tmp_path: Path) -> None:
    """Gate 3 / Hold 6: a non-GO status and a same-session (self-review) GO are both rejected."""
    paths = _fixture_generation(tmp_path, _initial_records())
    handle = _open_request(paths)

    with pytest.raises(RegistryAuthorizationError, match="independent bridge GO"):
        transition_apply(
            request_id=str(handle["request_id"]),
            ops_envelope=_OPS_ENVELOPE,
            apply_authorization={"status": "NO-GO", "bridge_id": "x", "author_session_context_id": "lo"},
            **_auth(),
            **paths,
        )

    # A GO whose author session equals the applying session is self-review and invalid.
    with pytest.raises(RegistryAuthorizationError, match="independent session context"):
        transition_apply(
            request_id=str(handle["request_id"]),
            ops_envelope=_OPS_ENVELOPE,
            apply_authorization={
                "status": "GO",
                "bridge_id": "x",
                "author_session_context_id": "prime-apply-session",
            },
            **_auth(actor_session="prime-apply-session"),
            **paths,
        )


def test_apply_rejects_on_stale_digest(tmp_path: Path) -> None:
    """Gate 4 / Hold 2: a request bound to a superseded generation is stale."""
    paths = _fixture_generation(tmp_path, _initial_records())
    handle = _open_request(paths)

    # Mutate the registry generation after the request was bound.
    amend_artifact(
        "other-tree",
        {"notes": "changed after request"},
        **_auth(change_reason="advance generation"),
        **paths,
    )

    with pytest.raises(RegistryGenerationConflict, match="stale"):
        transition_apply(
            request_id=str(handle["request_id"]),
            ops_envelope=_OPS_ENVELOPE,
            apply_authorization=_INDEPENDENT_GO,
            **_auth(),
            **paths,
        )


# --- happy path -------------------------------------------------------------


def test_apply_converts_coverage_and_removes_members(tmp_path: Path) -> None:
    """An exact/opaque->recursive conversion with the mandated member removals succeeds."""
    paths = _fixture_generation(tmp_path, _initial_records())
    handle = _open_request(paths)

    receipt = transition_apply(
        request_id=str(handle["request_id"]),
        ops_envelope=_OPS_ENVELOPE,
        apply_authorization=_INDEPENDENT_GO,
        **_auth(),
        **paths,
    )
    assert receipt.operation == "transition"

    snapshot = load_registry_snapshot(**paths)
    by_id = {record.id: record for record in snapshot.records}
    assert set(by_id) == {"pkg-container", "other-tree"}  # pkg-a, pkg-b removed
    assert by_id["pkg-container"].coverage_mode == "recursive"
    assert by_id["other-tree"].coverage_mode == "recursive"  # unrelated record preserved

    # GOV-PLATFORM-SOT-REGISTRY-001 + DCL-SOT-REGISTRY-PROJECTION-PARITY-001: the registry
    # validates (schema, parity, identity, journal) after the transition. Reverse-closure
    # census is a live-tree concern exercised by the downstream WI-5925 cycle, not this
    # fixture (Hold 3: no live mutation), so it is disabled here.
    report = validate_registry(require_reverse_closure=False, **paths)
    assert report["valid"], report["errors"]


def test_apply_is_single_use(tmp_path: Path) -> None:
    """A consumed request cannot be applied again (no double-apply)."""
    paths = _fixture_generation(tmp_path, _initial_records())
    handle = _open_request(paths)
    transition_apply(
        request_id=str(handle["request_id"]),
        ops_envelope=_OPS_ENVELOPE,
        apply_authorization=_INDEPENDENT_GO,
        **_auth(),
        **paths,
    )
    with pytest.raises(RegistryAuthorizationError, match="no matching active transition request"):
        transition_apply(
            request_id=str(handle["request_id"]),
            ops_envelope=_OPS_ENVELOPE,
            apply_authorization=_INDEPENDENT_GO,
            **_auth(),
            **paths,
        )


# --- amend remains unweakened ----------------------------------------------


def test_amend_still_rejects_identity_and_coverage_changes(tmp_path: Path) -> None:
    """Acceptance: amend continues to reject coverage-mode / locality / lifecycle changes."""
    paths = _fixture_generation(tmp_path, _initial_records())
    for change in ({"coverage_mode": "recursive"}, {"storage_path": "pkg/moved.py"}, {"lifecycle": "deprecated"}):
        with pytest.raises(RegistryAuthorizationError, match="transition authority"):
            amend_artifact("pkg-a", change, **_auth(), **paths)


# --- CLI wiring -------------------------------------------------------------


def test_cli_transition_subcommands_registered() -> None:
    """gt registry transition request/apply are wired into the CLI."""
    runner = CliRunner()
    group = runner.invoke(main, ["registry", "transition", "--help"])
    assert group.exit_code == 0, group.output
    assert "request" in group.output
    assert "apply" in group.output
    for sub in ("request", "apply"):
        result = runner.invoke(main, ["registry", "transition", sub, "--help"])
        assert result.exit_code == 0, result.output
