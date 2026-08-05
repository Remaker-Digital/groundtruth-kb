"""Tests for the no-index bridge file writer.

The writer only creates status-bearing numbered bridge files. Dispatcher/TAFE
state and helper-level latest-status validation live above this module.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project import registry_control_plane
from groundtruth_kb.project.registry_control_plane import (
    append_passive_observation,
    load_registry_snapshot,
    registry_currentness,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

from scripts import gtkb_bridge_writer as writer
from scripts.bridge_work_intent_registry import acquire
from scripts.gtkb_bridge_writer import (
    PRIME_STATUSES,
    VALID_STATUSES,
    BridgeComplianceError,
    BridgeConflictError,
    BridgeEnvelopeError,
    BridgePublicationError,
    BridgeTransitionError,
    publish_lo_verdict,
    write_bridge_file,
)
from scripts.windows_subprocess import no_window_subprocess_kwargs

AUTHOR_METADATA = {
    "author_identity": "Codex",
    "author_harness_id": "A",
    "author_session_context_id": "session-123",
    "author_model": "GPT-5.5",
    "author_model_version": "5.5",
    "author_model_configuration": "Extra High",
}


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=check,
        **no_window_subprocess_kwargs(),
    )


def _author_metadata_lines(session_id: str = "reviewed-session") -> str:
    return (
        "author_identity: fixture\n"
        "author_harness_id: T\n"
        f"author_session_context_id: {session_id}\n"
        "author_model: fixture-model\n"
        "author_model_version: fixture-version\n"
        "author_model_configuration: fixture-config\n"
    )


def _valid_proposal_body(*, include_requirement_sufficiency: bool = True) -> str:
    requirement_sufficiency = (
        "## Requirement Sufficiency\n\nExisting requirements sufficient.\n\n" if include_requirement_sufficiency else ""
    )
    return (
        "NEW\n\n"
        "# Test Proposal\n\n"
        "bridge_kind: prime_proposal\n"
        "Document: docthing\n"
        "Version: 001\n"
        "Project Authorization: PAUTH-PROJECT-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-1234\n"
        'target_paths: ["scripts/example.py"]\n\n'
        "## Summary\n\n"
        "Test proposal.\n\n"
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001`\n\n"
        "## Owner Decisions / Input\n\n"
        "No new owner decision is required.\n\n"
        "## Prior Deliberations\n\n"
        "_No prior deliberations: unit test fixture._\n\n"
        f"{requirement_sufficiency}"
        "## Spec-Derived Verification Plan\n\n"
        "- `groundtruth-kb/.venv/Scripts/python.exe -m pytest "
        "platform_tests/scripts/test_gtkb_bridge_writer.py -q --tb=short`\n\n"
        "## Risk And Rollback\n\n"
        "Remove the fixture output.\n"
    )


def _applicability_preflight_section() -> str:
    return (
        "## Applicability Preflight\n\n"
        "- packet_hash: `sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`\n"
        "- missing_required_specs: []\n"
    )


def _write_applicability_config(root: Path) -> None:
    config = root / "config" / "governance" / "spec-applicability.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("rules = []\n", encoding="utf-8")


def _valid_go_verdict() -> str:
    return (
        "GO\n\n"
        "# GO Verdict\n\n"
        "bridge_kind: lo_verdict\n"
        "Document: docthing\n"
        "Version: 002\n"
        "Responds to: bridge/docthing-001.md\n\n"
        "## Verdict\n\n"
        "GO.\n\n"
        f"{_applicability_preflight_section()}"
    )


def _valid_no_go_verdict() -> str:
    return (
        "NO-GO\n\n"
        "# NO-GO Verdict\n\n"
        "bridge_kind: lo_verdict\n"
        "Document: nogothing\n"
        "Version: 002\n"
        "Responds to: bridge/nogothing-001.md\n\n"
        "## Verdict\n\n"
        "NO-GO.\n"
    )


def _valid_verified_verdict() -> str:
    return (
        "VERIFIED\n\n"
        "# VERIFIED Verdict\n\n"
        "bridge_kind: lo_verdict\n"
        "Document: verifiedthing\n"
        "Version: 004\n"
        "Responds to: bridge/verifiedthing-003.md\n"
        "Reviewed report: bridge/verifiedthing-003.md\n"
        "Recommended commit type: `fix:`\n\n"
        "## Verdict\n\n"
        "VERIFIED.\n\n"
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001`\n\n"
        f"{_applicability_preflight_section()}\n"
        "## Spec-to-Test Mapping\n\n"
        "| Specification | Test or Verification Command | Executed | Result |\n"
        "| --- | --- | --- | --- |\n"
        "| `GOV-FILE-BRIDGE-AUTHORITY-001` | "
        "`pytest platform_tests/scripts/test_gtkb_bridge_writer.py` | yes | PASS |\n\n"
        "## Commands Executed\n\n"
        "- `pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q`\n\n"
        "## Commit Finalization Evidence\n\n"
        "- Finalization helper: `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`\n"
        "- Intended commit subject: `fix: fixture`\n"
        "- Same-transaction path set:\n"
        "- `scripts/example.py`\n"
        "- `bridge/verifiedthing-004.md`\n"
    )


def _stage_reviewed_file(tmp_path: Path, slug: str, version: int = 1, status: str = "NEW") -> None:
    _write_applicability_config(tmp_path)
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir(exist_ok=True)
    (bridge_dir / f"{slug}-{version:03d}.md").write_text(
        f"{status}\n{_author_metadata_lines()}\n# Reviewed artifact\n",
        encoding="utf-8",
    )


def _enable_typed_publication(tmp_path: Path) -> None:
    canonical = tmp_path / "config" / "registry" / "sot-artifacts.toml"
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
    canonical.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    canonical.write_text("schema_version = 1\n", encoding="utf-8")
    packaged.write_bytes(canonical.read_bytes())
    (tmp_path / "groundtruth.db").write_bytes(b"fixture")


def _enable_real_typed_publication(tmp_path: Path, slug: str, session_id: str) -> None:
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    (bridge / "baseline-001.md").write_text("NEW\n", encoding="utf-8")
    record = SoTArtifact(
        id="bridge-versioned-files",
        domain="bridge_protocol",
        lifecycle="active",
        storage_path="bridge/*-[0-9][0-9][0-9].md",
        authority_spec_id="GOV-FILE-BRIDGE-AUTHORITY-001",
        mutation_api="governed bridge publication",
        versioning_policy="git_tracked",
        backup_policy="git_tracked",
        health_check_function="",
        owner_role="shared",
        restore_action="git_restore",
        coverage_mode="glob",
    )
    payload = serialize_registry([record])
    canonical = tmp_path / "config" / "registry" / "sot-artifacts.toml"
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
    canonical.parent.mkdir(parents=True)
    packaged.parent.mkdir(parents=True)
    canonical.write_bytes(payload)
    packaged.write_bytes(payload)
    db_path = tmp_path / "groundtruth.db"
    KnowledgeDB(db_path=db_path)
    sync_projection([record], db_path, changed_by="test", change_reason="writer crash fixture")
    append_passive_observation(
        record_ids=[record.id],
        actor_session=session_id,
        changed_by="test",
        change_reason="establish bridge aggregate preimage",
        project_root=tmp_path,
    )
    assert acquire(slug, session_id, project_root=tmp_path)


def _typed_publication_content(status: str, document_name: str, version: int) -> str:
    return (
        f"{status}\n"
        + _author_metadata_lines("session-123")
        + "\n# Typed Publication\n\n"
        + f"bridge_kind: fixture\nDocument: {document_name}\nVersion: {version:03d}\n"
    )


def test_write_bridge_file_creates_numbered_file_with_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    path = write_bridge_file("docthing", 1, _valid_proposal_body(), tmp_path, author_metadata=AUTHOR_METADATA)

    assert path == tmp_path / "bridge" / "docthing-001.md"
    written = path.read_text(encoding="utf-8")
    assert written.startswith("NEW\n::init gtkb pb\n::open build\n")
    assert "author_identity: Codex\n" in written
    assert "author_session_context_id: session-123\n" in written
    assert "## Requirement Sufficiency\n\nExisting requirements sufficient." in written
    assert not (tmp_path / "bridge" / "INDEX.md").exists()


@pytest.mark.parametrize(
    "status",
    ("NEW", "REVISED", "NO-ACTION", "GO", "NO-GO", "VERIFIED"),
)
def test_typed_publication_observes_before_claim_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = f"typed-{status.lower().replace('-', '')}"
    target = tmp_path / "bridge" / f"{document_name}-001.md"
    events: list[str] = []

    monkeypatch.setattr(
        writer,
        "run_bridge_compliance_audit",
        lambda **_kwargs: {"decision": "pass"},
    )
    monkeypatch.setattr(
        writer,
        "_run_provider_verdict_guards",
        lambda **_kwargs: ({"decision": "pass"},),
    )

    def mint(**kwargs: object) -> dict[str, object]:
        assert kwargs["status"] == status
        assert kwargs["target_path"] == target
        events.append("mint")
        return {"capability": "typed-capability", "target_path": str(target)}

    def consume(**kwargs: object) -> None:
        assert target.read_bytes() == kwargs["content"]
        assert events == ["mint"]
        events.append("consume-current")

    def release(*_args: object, **_kwargs: object) -> None:
        assert events == ["mint", "consume-current"]
        events.append("release")

    monkeypatch.setattr(registry_control_plane, "mint_bridge_publication_capability", mint)
    monkeypatch.setattr(registry_control_plane, "consume_bridge_publication_capability", consume)
    monkeypatch.setattr(writer, "_release_claim", release)

    path = write_bridge_file(
        document_name,
        1,
        _typed_publication_content(status, document_name, 1),
        tmp_path,
        require_author_metadata=False,
    )

    assert path == target
    assert events == ["mint", "consume-current", "release"]


def test_pending_publication_sidecar_is_secret_free_and_recovers_after_process_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = "typed-durable-pending"
    relative_target = f"bridge/{document_name}-001.md"
    target = tmp_path / relative_target
    events: list[str] = []

    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())
    monkeypatch.setattr(
        registry_control_plane,
        "mint_bridge_publication_capability",
        lambda **_kwargs: {
            "capability": "raw-secret-must-not-persist",
            "capability_hash": "sha256:" + "a" * 64,
            "content_digest": "sha256:" + "b" * 64,
            "target_path": relative_target,
        },
    )
    monkeypatch.setattr(
        registry_control_plane,
        "consume_bridge_publication_capability",
        lambda **_kwargs: events.append("consume"),
    )

    def recover(**kwargs: object) -> registry_control_plane.BridgePublicationReceipt:
        events.append(f"recover:{kwargs['mode']}")
        return registry_control_plane.BridgePublicationReceipt(
            capability_hash="sha256:" + "a" * 64,
            revision_id="revision-test",
            target_path=relative_target,
            aggregate_digest="sha256:" + "e" * 64,
            capability_state="consumed",
        )

    monkeypatch.setattr(registry_control_plane, "recover_bridge_publication", recover, raising=False)
    monkeypatch.setattr(writer, "_release_claim", lambda *_args, **_kwargs: events.append("release"))

    write_bridge_file(
        document_name,
        1,
        _typed_publication_content("VERIFIED", document_name, 1),
        tmp_path,
        require_author_metadata=False,
        release_claim=False,
    )

    sidecars = list((tmp_path / ".gtkb-state" / "bridge-publication-pending").glob("*.json"))
    assert len(sidecars) == 1
    assert "raw-secret-must-not-persist" not in sidecars[0].read_text(encoding="utf-8")
    writer._PENDING_BRIDGE_PUBLICATIONS.clear()

    writer.finalize_pending_bridge_publication(target, tmp_path)

    assert events == ["consume", "recover:finalize", "release"]
    assert not sidecars[0].exists()


def test_pending_publication_sidecar_rolls_back_after_process_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = "typed-durable-rollback"
    relative_target = f"bridge/{document_name}-001.md"
    target = tmp_path / relative_target
    events: list[tuple[str, str]] = []

    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())
    monkeypatch.setattr(
        registry_control_plane,
        "mint_bridge_publication_capability",
        lambda **_kwargs: {
            "capability": "rollback-secret-must-not-persist",
            "capability_hash": "sha256:" + "c" * 64,
            "content_digest": "sha256:" + "d" * 64,
            "target_path": relative_target,
        },
    )
    monkeypatch.setattr(
        registry_control_plane,
        "consume_bridge_publication_capability",
        lambda **_kwargs: None,
    )

    def recover(**kwargs: object) -> None:
        events.append((str(kwargs["mode"]), str(kwargs["session_id"])))

    monkeypatch.setattr(registry_control_plane, "recover_bridge_publication", recover, raising=False)

    write_bridge_file(
        document_name,
        1,
        _typed_publication_content("VERIFIED", document_name, 1),
        tmp_path,
        require_author_metadata=False,
        release_claim=False,
    )
    sidecars = list((tmp_path / ".gtkb-state" / "bridge-publication-pending").glob("*.json"))
    assert len(sidecars) == 1
    assert "rollback-secret-must-not-persist" not in sidecars[0].read_text(encoding="utf-8")
    writer._PENDING_BRIDGE_PUBLICATIONS.clear()

    writer.rollback_pending_bridge_publication(target, tmp_path, reason="outer transaction failed")

    assert events == [("rollback", "session-123")]
    assert not sidecars[0].exists()


def test_hard_exit_between_create_and_consume_recovers_in_fresh_process(tmp_path: Path) -> None:
    document_name = "typed-hard-exit"
    session_id = "session-123"
    _enable_real_typed_publication(tmp_path, document_name, session_id)
    content = _typed_publication_content("NEW", document_name, 1)
    child = """
import os
import sys
from pathlib import Path
from groundtruth_kb.project import registry_control_plane
from scripts import gtkb_bridge_writer as writer

root = Path(sys.argv[1])
document_name = sys.argv[2]
content = sys.argv[3]
writer.run_bridge_compliance_audit = lambda **_kwargs: {"decision": "pass"}
writer._run_provider_verdict_guards = lambda **_kwargs: ()
registry_control_plane.consume_bridge_publication_capability = lambda **_kwargs: os._exit(71)
writer.write_bridge_file(
    document_name,
    1,
    content,
    root,
    require_author_metadata=False,
    release_claim=False,
)
"""

    crashed = subprocess.run(
        [sys.executable, "-c", child, str(tmp_path), document_name, content],
        text=True,
        capture_output=True,
        check=False,
        **no_window_subprocess_kwargs(),
    )

    assert crashed.returncode == 71, crashed.stderr
    target = tmp_path / "bridge" / f"{document_name}-001.md"
    written = target.read_text(encoding="utf-8")
    assert written.startswith("NEW\n::init gtkb pb\n::open build\n")
    assert f"Document: {document_name}\n" in written
    sidecars = list((tmp_path / ".gtkb-state" / "bridge-publication-pending").glob("*.json"))
    assert len(sidecars) == 1
    sidecar = json.loads(sidecars[0].read_text(encoding="utf-8"))
    assert "capability" not in sidecar
    assert sidecar["capability_hash"].startswith("sha256:")

    writer.finalize_pending_bridge_publication(target, tmp_path)

    assert not sidecars[0].exists()
    assert writer._claim_holder(tmp_path, document_name) is None
    snapshot = load_registry_snapshot(project_root=tmp_path)
    assert registry_currentness(
        snapshot,
        project_root=tmp_path,
        db_path=tmp_path / "groundtruth.db",
        record_ids={"bridge-versioned-files"},
    )["current"]


@pytest.mark.parametrize("crash_window", ("before_commit", "after_commit"))
def test_rollback_recovery_is_idempotent_across_hard_exit_windows(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    crash_window: str,
) -> None:
    document_name = f"typed-rollback-{crash_window}"
    session_id = "session-123"
    _enable_real_typed_publication(tmp_path, document_name, session_id)
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())
    target = write_bridge_file(
        document_name,
        1,
        _typed_publication_content("NEW", document_name, 1),
        tmp_path,
        require_author_metadata=False,
        release_claim=False,
    )
    writer._PENDING_BRIDGE_PUBLICATIONS.clear()
    child = """
import os
import sys
from pathlib import Path
from groundtruth_kb.project import registry_control_plane

root = Path(sys.argv[1])
target = Path(sys.argv[2])
window = sys.argv[3]
if window == "before_commit":
    registry_control_plane._append_revision = lambda *_args, **_kwargs: os._exit(72)
else:
    real_unlink = Path.unlink
    def crash_on_quarantine_cleanup(path, *args, **kwargs):
        if path.parent.name == "bridge-publication-recovery":
            os._exit(73)
        return real_unlink(path, *args, **kwargs)
    Path.unlink = crash_on_quarantine_cleanup
registry_control_plane.recover_bridge_publication(
    target_path=target,
    session_id="session-123",
    mode="rollback",
    changed_by="test",
    change_reason="hard-exit rollback fixture",
    project_root=root,
)
"""
    expected_exit = 72 if crash_window == "before_commit" else 73

    crashed = subprocess.run(
        [sys.executable, "-c", child, str(tmp_path), str(target), crash_window],
        text=True,
        capture_output=True,
        check=False,
        **no_window_subprocess_kwargs(),
    )

    assert crashed.returncode == expected_exit, crashed.stderr
    assert not target.exists()
    quarantine = list((tmp_path / ".gtkb-state" / "bridge-publication-recovery").glob("*.rollback"))
    assert len(quarantine) == 1

    writer.rollback_pending_bridge_publication(target, tmp_path, reason="resume hard-exit rollback")

    assert not target.exists()
    assert not quarantine[0].exists()
    assert not list((tmp_path / ".gtkb-state" / "bridge-publication-pending").glob("*.json"))


def test_sidecar_cleanup_failure_does_not_compensate_released_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = "typed-sidecar-cleanup"
    relative_target = f"bridge/{document_name}-001.md"
    target = tmp_path / relative_target
    events: list[str] = []
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())
    monkeypatch.setattr(
        registry_control_plane,
        "mint_bridge_publication_capability",
        lambda **_kwargs: {
            "capability": "cleanup-secret",
            "capability_hash": "sha256:" + "a" * 64,
            "content_digest": "sha256:" + "b" * 64,
            "target_path": relative_target,
        },
    )
    monkeypatch.setattr(
        registry_control_plane,
        "consume_bridge_publication_capability",
        lambda **_kwargs: events.append("consume"),
    )
    monkeypatch.setattr(writer, "_release_claim", lambda *_args, **_kwargs: events.append("release"))
    monkeypatch.setattr(
        registry_control_plane,
        "compensate_bridge_publication",
        lambda **_kwargs: pytest.fail("cleanup failure must not compensate a completed publication"),
    )
    monkeypatch.setattr(
        writer,
        "_delete_pending_publication_sidecar",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("injected cleanup failure")),
    )

    written = write_bridge_file(
        document_name,
        1,
        _typed_publication_content("NEW", document_name, 1),
        tmp_path,
        require_author_metadata=False,
    )

    assert written == target
    assert target.exists()
    assert events == ["consume", "release"]


def test_restart_recovery_rejects_sidecar_capability_hash_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document_name = "typed-sidecar-binding"
    session_id = "session-123"
    _enable_real_typed_publication(tmp_path, document_name, session_id)
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())
    target = write_bridge_file(
        document_name,
        1,
        _typed_publication_content("NEW", document_name, 1),
        tmp_path,
        require_author_metadata=False,
        release_claim=False,
    )
    writer._PENDING_BRIDGE_PUBLICATIONS.clear()
    sidecar = next((tmp_path / ".gtkb-state" / "bridge-publication-pending").glob("*.json"))
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    payload["capability_hash"] = "sha256:" + "f" * 64
    sidecar.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(registry_control_plane.RegistryAuthorizationError, match="exact.*row"):
        writer.finalize_pending_bridge_publication(target, tmp_path)

    assert target.exists()
    assert sidecar.exists()
    assert writer._claim_holder(tmp_path, document_name) is not None


@pytest.mark.parametrize(
    "failure",
    ("create", "reread", "consume", "currentness", "release"),
)
def test_typed_publication_failures_compensate_and_retain_claim(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = f"typed-failure-{failure}"
    target = tmp_path / "bridge" / f"{document_name}-001.md"
    events: list[str] = []

    monkeypatch.setattr(
        writer,
        "run_bridge_compliance_audit",
        lambda **_kwargs: {"decision": "pass"},
    )
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())

    def mint(**_kwargs: object) -> dict[str, object]:
        events.append("mint")
        return {"capability": "typed-capability", "target_path": str(target)}

    def consume(**_kwargs: object) -> None:
        events.append("consume")
        if failure in {"consume", "currentness"}:
            raise RuntimeError(f"forced {failure} failure")

    def compensate(**_kwargs: object) -> None:
        events.append("compensate")
        target.unlink(missing_ok=True)

    def release(*_args: object, **_kwargs: object) -> None:
        events.append("release-attempt")
        if failure == "release":
            raise RuntimeError("forced release failure")
        events.append("release-success")

    monkeypatch.setattr(registry_control_plane, "mint_bridge_publication_capability", mint)
    monkeypatch.setattr(registry_control_plane, "consume_bridge_publication_capability", consume)
    monkeypatch.setattr(registry_control_plane, "compensate_bridge_publication", compensate)
    monkeypatch.setattr(writer, "_release_claim", release)

    if failure == "create":
        original_open = Path.open

        def fail_create(path: Path, *args: object, **kwargs: object):
            if path == target and args and args[0] == "x":
                raise OSError("forced create failure")
            return original_open(path, *args, **kwargs)

        monkeypatch.setattr(Path, "open", fail_create)
    elif failure == "reread":
        original_read_text = Path.read_text

        def fail_reread(path: Path, *args: object, **kwargs: object) -> str:
            if path == target:
                raise OSError("forced reread failure")
            return original_read_text(path, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", fail_reread)

    with pytest.raises((OSError, BridgePublicationError), match=failure):
        write_bridge_file(
            document_name,
            1,
            _typed_publication_content("NEW", document_name, 1),
            tmp_path,
            require_author_metadata=False,
        )

    assert events[0] == "mint"
    assert events.count("compensate") == 1
    assert "release-success" not in events
    assert not target.exists()


def test_typed_publication_compensation_failure_retains_repair_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = "typed-repair-required"
    target = tmp_path / "bridge" / f"{document_name}-001.md"

    monkeypatch.setattr(
        writer,
        "run_bridge_compliance_audit",
        lambda **_kwargs: {"decision": "pass"},
    )
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: ())
    monkeypatch.setattr(
        registry_control_plane,
        "mint_bridge_publication_capability",
        lambda **_kwargs: {
            "capability": "typed-capability",
            "target_path": str(target),
        },
    )
    monkeypatch.setattr(
        registry_control_plane,
        "consume_bridge_publication_capability",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("forced consume failure")),
    )
    monkeypatch.setattr(
        registry_control_plane,
        "compensate_bridge_publication",
        lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("forced compensation failure")),
    )
    monkeypatch.setattr(
        writer,
        "_release_claim",
        lambda *_args, **_kwargs: pytest.fail("claim must remain held"),
    )

    with pytest.raises(BridgePublicationError, match="REPAIR_REQUIRED"):
        write_bridge_file(
            document_name,
            1,
            _typed_publication_content("NEW", document_name, 1),
            tmp_path,
            require_author_metadata=False,
        )

    assert target.is_file()


def test_typed_publication_compliance_failure_precedes_mint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_typed_publication(tmp_path)
    document_name = "typed-compliance-denial"
    target = tmp_path / "bridge" / f"{document_name}-001.md"
    monkeypatch.setattr(
        writer,
        "run_bridge_compliance_audit",
        lambda **_kwargs: (_ for _ in ()).throw(BridgeComplianceError("forced compliance failure")),
    )
    monkeypatch.setattr(
        registry_control_plane,
        "mint_bridge_publication_capability",
        lambda **_kwargs: pytest.fail("mint must follow successful compliance"),
    )

    with pytest.raises(BridgeComplianceError, match="compliance failure"):
        write_bridge_file(
            document_name,
            1,
            _typed_publication_content("NEW", document_name, 1),
            tmp_path,
            require_author_metadata=False,
        )

    assert not target.exists()


def test_write_bridge_file_rejects_existing_numbered_file(tmp_path: Path) -> None:
    target = tmp_path / "bridge" / "conflict-001.md"
    target.parent.mkdir()
    target.write_text("NEW\nexisting\n", encoding="utf-8")

    with pytest.raises(BridgeConflictError, match="already exists"):
        write_bridge_file("conflict", 1, "NEW\nnew body\n", tmp_path, require_author_metadata=False)

    assert target.read_text(encoding="utf-8") == "NEW\nexisting\n"


def test_write_bridge_file_rejects_non_positive_version(tmp_path: Path) -> None:
    with pytest.raises(BridgeTransitionError, match="version must be positive"):
        write_bridge_file("bad", 0, "NEW\n", tmp_path, require_author_metadata=False)


def test_write_bridge_file_accepts_pre_metadata_content_when_injection_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    _stage_reviewed_file(tmp_path, "docthing")
    content = "GO\n" + _author_metadata_lines("reviewer-session") + "\n" + _valid_go_verdict().split("\n", 1)[1]

    path = write_bridge_file("docthing", 2, content, tmp_path, require_author_metadata=False)

    written = path.read_text(encoding="utf-8")
    assert written.startswith("GO\n::init gtkb lo\n::open test\n")
    assert _author_metadata_lines("reviewer-session") in written
    assert "# GO Verdict" in written


def test_no_action_is_valid_prime_authored_status() -> None:
    assert "NO-ACTION" in VALID_STATUSES
    assert "NO-ACTION" in PRIME_STATUSES
    assert (
        frozenset({"NEW", "REVISED", "GO", "NO-GO", "NO-ACTION", "VERIFIED", "ADVISORY", "DEFERRED", "WITHDRAWN"})
        == VALID_STATUSES
    )


def test_write_bridge_file_materializes_no_action_envelope(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    path = write_bridge_file(
        "no-action-thread",
        3,
        "NO-ACTION\n\nbridge_kind: prime_response\nDocument: no-action-thread\n",
        tmp_path,
        author_metadata=AUTHOR_METADATA,
    )

    assert path.read_text(encoding="utf-8").startswith("NO-ACTION\n::init gtkb pb\n::open build\n")


def test_write_bridge_file_rejects_mismatched_envelope_role(tmp_path: Path) -> None:
    with pytest.raises(BridgeEnvelopeError, match="responder-role mismatch"):
        write_bridge_file(
            "bad-envelope",
            1,
            "NEW\n::init gtkb lo\n::open build\n\nbridge_kind: prime_proposal\n",
            tmp_path,
            author_metadata=AUTHOR_METADATA,
        )


def test_write_bridge_file_rejects_invalid_envelope_activity(tmp_path: Path) -> None:
    with pytest.raises(BridgeEnvelopeError, match="invalid"):
        write_bridge_file(
            "bad-activity",
            1,
            "NEW\n::init gtkb pb\n::open unknown\n\nbridge_kind: prime_proposal\n",
            tmp_path,
            author_metadata=AUTHOR_METADATA,
        )


def test_write_bridge_file_rejects_envelope_for_unmapped_status(tmp_path: Path) -> None:
    with pytest.raises(BridgeEnvelopeError, match="no formal responder-role"):
        write_bridge_file(
            "advisory-envelope",
            1,
            "ADVISORY\n::init gtkb lo\n::open deliberation\n\nbridge_kind: loyal_opposition_advisory\n",
            tmp_path,
            author_metadata=AUTHOR_METADATA,
        )


def test_write_bridge_file_rejects_version_in_git_history(tmp_path: Path) -> None:
    """write_bridge_file raises BridgeConflictError when the target version exists in
    git history but is absent from disk (deleted-then-recreate attempt, WI-4740)."""
    try:
        _git(tmp_path, "init", "--quiet")
        _git(tmp_path, "config", "user.email", "test@example.com")
        _git(tmp_path, "config", "user.name", "Test Runner")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("git not available in test environment")

    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    committed = bridge_dir / "gtkb-history-guard-001.md"
    committed.write_text("GO\n\n# Original verdict\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-m", "initial bridge file")

    # Delete from disk — now committed in history but absent on disk.
    committed.unlink()

    with pytest.raises(BridgeConflictError, match="git history"):
        write_bridge_file(
            "gtkb-history-guard",
            1,
            "NEW\n\n# Recreate attempt - should fail\n",
            project_root=tmp_path,
            require_author_metadata=False,
        )


def test_write_bridge_file_rejects_malformed_proposal_before_disk_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def deny_requirement_sufficiency(**_kwargs):
        raise BridgeComplianceError("Requirement Sufficiency")

    monkeypatch.setattr(writer, "run_bridge_compliance_audit", deny_requirement_sufficiency)

    with pytest.raises(BridgeComplianceError, match="Requirement Sufficiency"):
        write_bridge_file(
            "docthing",
            1,
            _valid_proposal_body(include_requirement_sufficiency=False),
            tmp_path,
            author_metadata=AUTHOR_METADATA,
        )

    assert not (tmp_path / "bridge" / "docthing-001.md").exists()


@pytest.mark.parametrize(
    ("slug", "content_factory"),
    [
        ("docthing", _valid_go_verdict),
        ("nogothing", _valid_no_go_verdict),
        ("verifiedthing", _valid_verified_verdict),
    ],
)
def test_write_bridge_file_allows_valid_verdicts_without_proposal_only_sections(
    tmp_path: Path,
    slug: str,
    content_factory,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    _stage_reviewed_file(tmp_path, slug)
    if slug == "verifiedthing":
        _stage_reviewed_file(tmp_path, slug, version=2, status="GO")
        _stage_reviewed_file(tmp_path, slug, version=3, status="NEW")
        version = 4
    else:
        version = 2

    path = write_bridge_file(slug, version, content_factory(), tmp_path, author_metadata=AUTHOR_METADATA)

    written = path.read_text(encoding="utf-8")
    assert "## Requirement Sufficiency" not in written
    assert "author_session_context_id: session-123" in written


PROVIDER_METADATA = {
    "author_identity": "Alibaba Cloud Studio H",
    "author_harness_id": "H",
    "author_session_context_id": "dispatch-H-1",
    "author_model": "deepseek-v4-pro",
    "author_model_version": "v4",
    "author_model_configuration": "provider fixture",
}


def _provider_thread(tmp_path: Path, *, bridge_kind: str = "prime_proposal") -> None:
    _write_applicability_config(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir(exist_ok=True)
    (bridge / "provider-thread-001.md").write_text(
        "NEW\n\nbridge_kind: " + bridge_kind + "\nDocument: provider-thread\n",
        encoding="utf-8",
    )


def _provider_go_content(**metadata_overrides: str) -> str:
    metadata = dict(PROVIDER_METADATA)
    metadata.update(metadata_overrides)
    metadata_lines = "".join(f"{key}: {value}\n" for key, value in metadata.items())
    return (
        "GO\n"
        f"{metadata_lines}\n"
        "bridge_kind: lo_verdict\n"
        "Document: provider-thread\n"
        "Version: 002\n"
        "Responds to: bridge/provider-thread-001.md\n\n"
        "## Applicability Preflight\n\n"
        "- missing_required_specs: []\n"
    )


def _prepare_provider_mocks(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[tuple[str, str]]:
    released: list[tuple[str, str]] = []
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "loyal-opposition", "harness_id": "H"},
    )
    monkeypatch.setattr(
        writer,
        "_claim_holder",
        lambda *_args, **_kwargs: {"session_id": "dispatch-H-1"},
    )
    monkeypatch.setattr(writer, "_run_provider_verdict_guards", lambda **_kwargs: None)
    monkeypatch.setattr(
        writer,
        "_release_claim",
        lambda _root, slug, session_id: released.append((slug, session_id)),
    )
    return released


def test_write_bridge_file_exclusive_create_closes_exists_check_race(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "bridge/race-002.md"
    _stage_reviewed_file(tmp_path, "race")

    def create_racing_target(_target: Path, _root: Path) -> bool:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("GO\n\nracing writer\n", encoding="utf-8")
        return False

    monkeypatch.setattr(writer, "_bridge_file_committed_in_git", create_racing_target)
    if hasattr(writer, "run_bridge_compliance_audit"):
        monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    with pytest.raises(BridgeConflictError, match="already exists"):
        write_bridge_file(
            "race",
            2,
            _provider_go_content().replace("provider-thread", "race"),
            tmp_path,
            require_author_metadata=False,
        )

    assert target.read_text(encoding="utf-8") == "GO\n\nracing writer\n"


def test_publish_lo_verdict_computes_next_path_and_releases_claim_after_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    released = _prepare_provider_mocks(monkeypatch, tmp_path)
    if hasattr(writer, "run_bridge_compliance_audit"):
        monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    result = publish_lo_verdict(
        "provider-thread",
        "GO",
        _provider_go_content(),
        tmp_path,
        session_id="dispatch-H-1",
        harness_name="alibaba-cloud-studio",
        author_metadata=PROVIDER_METADATA,
    )

    assert result.verdict_path == "bridge/provider-thread-002.md"
    assert result.claim_released is True
    assert released == [("provider-thread", "dispatch-H-1")]
    assert (tmp_path / result.verdict_path).read_text(encoding="utf-8").startswith("GO\n::init gtkb lo\n::open test\n")


def test_publish_lo_verdict_denies_wrong_role_before_mutation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _provider_thread(tmp_path)
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "prime-builder", "harness_id": "H"},
    )

    with pytest.raises(BridgePublicationError, match="loyal-opposition"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    assert not (tmp_path / "bridge/provider-thread-002.md").exists()


def test_publish_lo_verdict_denies_missing_or_other_session_claim(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    monkeypatch.setattr(
        writer,
        "_resolve_lo_worker",
        lambda *_args, **_kwargs: {"role": "loyal-opposition", "harness_id": "H"},
    )
    monkeypatch.setattr(writer, "_claim_holder", lambda *_args, **_kwargs: None)

    with pytest.raises(BridgePublicationError, match="active claim"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    monkeypatch.setattr(writer, "_claim_holder", lambda *_args, **_kwargs: {"session_id": "dispatch-H-2"})
    with pytest.raises(BridgePublicationError, match="another session"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )


def test_publish_lo_verdict_normalizes_trusted_runtime_model_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    _prepare_provider_mocks(monkeypatch, tmp_path)
    if hasattr(writer, "run_bridge_compliance_audit"):
        monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    stale_values = {
        "author_model": "model-authored-name",
        "author_model_version": "model-authored-version",
        "author_model_configuration": "model-authored configuration",
    }
    result = publish_lo_verdict(
        "provider-thread",
        "GO",
        _provider_go_content(**stale_values),
        tmp_path,
        session_id="dispatch-H-1",
        harness_name="alibaba-cloud-studio",
        author_metadata=PROVIDER_METADATA,
    )

    written = (tmp_path / result.verdict_path).read_text(encoding="utf-8")
    for key in writer.PROVIDER_RUNTIME_MODEL_FIELDS:
        assert f"{key}: {PROVIDER_METADATA[key]}" in written
        assert stale_values[key] not in written


def test_publish_lo_verdict_fills_missing_runtime_model_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    _prepare_provider_mocks(monkeypatch, tmp_path)
    if hasattr(writer, "run_bridge_compliance_audit"):
        monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    content = _provider_go_content()
    for key in writer.PROVIDER_RUNTIME_MODEL_FIELDS:
        content = content.replace(f"{key}: {PROVIDER_METADATA[key]}\n", "")

    result = publish_lo_verdict(
        "provider-thread",
        "GO",
        content,
        tmp_path,
        session_id="dispatch-H-1",
        harness_name="alibaba-cloud-studio",
        author_metadata=PROVIDER_METADATA,
    )

    written = (tmp_path / result.verdict_path).read_text(encoding="utf-8")
    for key in writer.PROVIDER_RUNTIME_MODEL_FIELDS:
        assert f"{key}: {PROVIDER_METADATA[key]}" in written


@pytest.mark.parametrize(
    ("field", "untrusted_value"),
    [
        ("author_identity", "loyal-opposition/other"),
        ("author_harness_id", "other-harness"),
        ("author_session_context_id", "other-session"),
    ],
)
def test_publish_lo_verdict_denies_non_model_metadata_conflict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    untrusted_value: str,
) -> None:
    _provider_thread(tmp_path)
    _prepare_provider_mocks(monkeypatch, tmp_path)

    with pytest.raises(BridgePublicationError, match=rf"metadata conflict for {field}"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(**{field: untrusted_value}),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )


@pytest.mark.parametrize("field", writer.PROVIDER_RUNTIME_MODEL_FIELDS)
def test_publish_lo_verdict_denies_missing_trusted_runtime_model_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    _provider_thread(tmp_path)
    _prepare_provider_mocks(monkeypatch, tmp_path)
    incomplete_metadata = dict(PROVIDER_METADATA)
    incomplete_metadata[field] = ""

    with pytest.raises(BridgePublicationError, match=rf"missing trusted author metadata: {field}"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=incomplete_metadata,
        )


def test_publish_lo_verdict_denies_stale_response_version_and_guard_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _provider_thread(tmp_path)
    released = _prepare_provider_mocks(monkeypatch, tmp_path)

    stale = _provider_go_content().replace("bridge/provider-thread-001.md", "bridge/provider-thread-000.md")
    with pytest.raises(BridgePublicationError, match="respond to current latest"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            stale,
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    wrong_version = _provider_go_content().replace("Version: 002", "Version: 003")
    with pytest.raises(BridgePublicationError, match="Version must be 002"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            wrong_version,
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    def deny_guard(**_kwargs):
        raise BridgePublicationError("scanner-safe credential denial")

    monkeypatch.setattr(writer, "_run_provider_verdict_guards", deny_guard)
    with pytest.raises(BridgePublicationError, match="credential denial"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )

    assert not (tmp_path / "bridge/provider-thread-002.md").exists()
    assert released == []

    (tmp_path / "bridge/provider-thread-001.md").write_text(
        "NEW\n\nbridge_kind: implementation_report\nDocument: provider-thread\n",
        encoding="utf-8",
    )
    with pytest.raises(BridgeTransitionError, match="invalid after NEW"):
        publish_lo_verdict(
            "provider-thread",
            "GO",
            _provider_go_content(),
            tmp_path,
            session_id="dispatch-H-1",
            harness_name="alibaba-cloud-studio",
            author_metadata=PROVIDER_METADATA,
        )


def test_provider_hunk_coverage_recognizes_binary_patch_diff_git_header(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "groundtruth.db").write_bytes(b"\x00GTKB binary original\x00\n")
    _git(tmp_path, "add", "--", "groundtruth.db")
    _git(tmp_path, "commit", "-m", "chore: seed binary fixture")
    (tmp_path / "groundtruth.db").write_bytes(b"\x00GTKB binary reviewed\x01\n")
    patch_text = _git(tmp_path, "diff", "--binary", "--", "groundtruth.db").stdout
    assert "GIT binary patch" in patch_text
    assert "+++ b/groundtruth.db" not in patch_text
    (tmp_path / "groundtruth-db.patch").write_text(patch_text, encoding="utf-8", newline="\n")

    covered = writer._hunk_patch_covered_paths(tmp_path, ["groundtruth-db.patch"])

    assert covered == {"groundtruth.db"}


def test_provider_hunk_coverage_rejects_declared_size_mismatch(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "--", "scripts/feature.py")
    _git(tmp_path, "commit", "-m", "chore: seed feature fixture")
    (tmp_path / "scripts" / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    patch_text = _git(tmp_path, "diff", "--", "scripts/feature.py").stdout
    patch_path = tmp_path / "feature.patch"
    patch_path.write_text(patch_text, encoding="utf-8", newline="\n")
    latest_content = (
        "NEW\n\nbridge_kind: implementation_report\n\n## Hunk Patch Evidence\n\n"
        "- Hunk patch: `feature.patch`\n"
        "- Patch SHA-256: `" + __import__("hashlib").sha256(patch_path.read_bytes()).hexdigest() + "`\n"
        f"- Patch size: `{len(patch_path.read_bytes()) + 1}` bytes\n"
    )

    with pytest.raises(BridgePublicationError, match="size mismatch"):
        writer._hunk_patch_covered_paths(tmp_path, ["feature.patch"], latest_content=latest_content)


def test_provider_hunk_coverage_rejects_corrupt_patch(tmp_path: Path) -> None:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test User")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "--", "scripts/feature.py")
    _git(tmp_path, "commit", "-m", "chore: seed feature fixture")
    (tmp_path / "corrupt.patch").write_text(
        """diff --git a/scripts/feature.py b/scripts/feature.py
--- a/scripts/feature.py
+++ b/scripts/feature.py
@@ -1 +1 @@
-VALUE = 1
""",
        encoding="utf-8",
        newline="\n",
    )

    with pytest.raises(BridgePublicationError, match="not Git-applyable"):
        writer._hunk_patch_covered_paths(tmp_path, ["corrupt.patch"])


def test_write_bridge_file_appends_closing_instruction_footer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-5935 Slice E: every filed bridge artifact carries the closing instruction."""
    monkeypatch.setattr(writer, "run_bridge_compliance_audit", lambda **_kwargs: {"decision": "pass"})

    path = write_bridge_file("closing-footer", 1, _valid_proposal_body(), tmp_path, author_metadata=AUTHOR_METADATA)
    written = path.read_text(encoding="utf-8")
    assert writer._CLOSING_INSTRUCTION in written
    assert written.rstrip().endswith(writer._CLOSING_INSTRUCTION)
