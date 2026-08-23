"""Tests for the protected commit authorization pre-commit gate."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.registry_control_plane import (
    apply_registry_transaction,
    consume_observation_capability,
    mint_observation_capability,
    serialize_registry,
)
from groundtruth_kb.project.sot_registry import SoTArtifact, sync_projection

from scripts import bridge_applicability_preflight as applicability_preflight
from scripts import implementation_authorization

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_protected_commit_authorization.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_protected_commit_authorization", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_protected_commit_authorization"] = module
    spec.loader.exec_module(module)
    return module


def _seed_registered_commit_fixture(root: Path, storage_path: str = "registered.txt") -> Path:
    member = root / storage_path
    member.parent.mkdir(parents=True, exist_ok=True)
    member.write_text("before\n", encoding="utf-8")
    records = [
        SoTArtifact(
            id="registered-member",
            domain="control_surface",
            lifecycle="active",
            storage_path=storage_path,
            authority_spec_id="GOV-PLATFORM-SOT-REGISTRY-001",
            mutation_api="fixture",
            versioning_policy="git_tracked",
            backup_policy="git_tracked",
            health_check_function="",
            owner_role="shared",
            restore_action="git_restore",
            coverage_mode="exact",
        )
    ]
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        root
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
    db_path = root / "groundtruth.db"
    knowledge = KnowledgeDB(db_path=db_path)
    knowledge.close()
    sync_projection(records, db_path, changed_by="test", change_reason="fixture")
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        actor_session="pb-session",
        changed_by="test/prime-builder",
        change_reason="WI-5441 commit fixture",
        start_packet_hash="sha256:packet",
        pauth_id="PAUTH-WI5441-TEST",
        bridge_id="gtkb-wi5441-registry-control-plane-reverse-coverage",
        project_root=root,
    )
    return member


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _seed_bridge_publication_commit_fixture(root: Path, rel_paths: list[str]) -> dict[str, str]:
    _init_committed_paths(root, ["baseline.txt"])
    contents: dict[str, bytes] = {}
    for rel_path in rel_paths:
        payload = f"NEW\n# Synthetic publication for {rel_path}\n".encode()
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        contents[rel_path] = payload

    records = [
        SoTArtifact(
            id="bridge-versioned-files",
            domain="bridge_protocol",
            lifecycle="active",
            storage_path="bridge/*-[0-9][0-9][0-9].md",
            authority_spec_id="GOV-FILE-BRIDGE-AUTHORITY-001",
            mutation_api="governed_bridge_writer",
            versioning_policy="git_tracked",
            backup_policy="git_tracked",
            health_check_function="",
            owner_role="shared",
            restore_action="git_restore",
            coverage_mode="glob",
        )
    ]
    registry = root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        root
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
    db_path = root / "groundtruth.db"
    knowledge = KnowledgeDB(db_path=db_path)
    knowledge.close()
    sync_projection(records, db_path, changed_by="test", change_reason="bridge fixture")
    apply_registry_transaction(
        records,
        operation="legacy_bootstrap",
        actor_session="pb-session",
        changed_by="test/prime-builder",
        change_reason="WI-5441 bridge publication fixture",
        start_packet_hash="sha256:packet",
        pauth_id="PAUTH-WI5441-TEST",
        bridge_id="gtkb-wi5441-bridge-publication-capability-commit-clearance",
        project_root=root,
    )

    capability_hashes: dict[str, str] = {}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        for index, rel_path in enumerate(rel_paths, start=1):
            latest = conn.execute(
                "SELECT * FROM sot_artifact_revisions WHERE entry_id = ? ORDER BY rowid DESC LIMIT 1",
                ("bridge-versioned-files",),
            ).fetchone()
            assert latest is not None
            stem = Path(rel_path).stem
            document_name, version_text = stem.rsplit("-", 1)
            revision_id = f"bridge-publication-revision-{index}"
            capability_hash = _sha256(f"capability-{index}".encode())
            capability_hashes[rel_path] = capability_hash
            conn.execute(
                """
                INSERT INTO sot_artifact_revisions (
                    revision_id, entry_id, canonical_relative_path, object_kind,
                    content_digest, size_bytes, observed_at, actor_session,
                    operation, predecessor_revision_id, changed_by, changed_at,
                    change_reason, capability_hash, bridge_id, start_packet_hash,
                    pauth_decision, journal_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL)
                """,
                (
                    revision_id,
                    latest["entry_id"],
                    latest["canonical_relative_path"],
                    latest["object_kind"],
                    latest["content_digest"],
                    latest["size_bytes"],
                    "2026-01-01T00:01:00Z",
                    "lo-session",
                    "bridge_publication",
                    latest["revision_id"],
                    "test/loyal-opposition",
                    "2026-01-01T00:01:00Z",
                    "synthetic governed bridge publication",
                    capability_hash,
                    document_name,
                ),
            )
            conn.execute(
                """
                INSERT INTO sot_registry_bridge_publication_capabilities (
                    capability_hash, authority_kind, document_name, version, status,
                    target_path, content_digest, compliance_digest, transition_digest,
                    claim_session, author_session_context_id, aggregate_entry_id,
                    aggregate_preimage_digest, operation, expires_at, capability_state,
                    created_at, consumed_at, result_digest, revision_id,
                    compensation_revision_id, compensation_digest, failure_reason
                ) VALUES (
                    ?, 'bridge_publication', ?, ?, 'NEW', ?, ?, ?, ?,
                    'lo-session', 'lo-session', 'bridge-versioned-files', ?,
                    'bridge_publication', '2026-01-01T00:02:00Z', 'consumed',
                    '2026-01-01T00:00:00Z', '2026-01-01T00:01:00Z', ?, ?,
                    NULL, NULL, NULL
                )
                """,
                (
                    capability_hash,
                    document_name,
                    int(version_text),
                    rel_path,
                    _sha256(contents[rel_path]),
                    _sha256(f"compliance-{index}".encode()),
                    _sha256(f"transition-{index}".encode()),
                    latest["content_digest"],
                    _sha256(f"result-{index}".encode()),
                    revision_id,
                ),
            )
        conn.commit()
    finally:
        conn.close()

    subprocess.run(["git", "add", "--", *rel_paths], cwd=root, check=True)
    return capability_hashes


def _author(role: str, session_id: str) -> str:
    return f"""author_identity: {role}/codex
author_harness_id: A
author_session_context_id: {session_id}
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: test
"""


def _write_transaction_chain(
    root: Path,
    module,
    monkeypatch: pytest.MonkeyPatch,
    *,
    bridge_id: str = "gtkb-wi5629-fixture",
    protected_paths: list[str] | None = None,
    reviewer_session: str = "lo-session",
    report_session: str = "pb-session",
) -> tuple[list[str], str, str]:
    protected_paths = protected_paths or [
        "scripts/bridge_lifecycle_resolver.py",
        "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
    ]
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    proposal = f"bridge/{bridge_id}-001.md"
    go = f"bridge/{bridge_id}-002.md"
    report = f"bridge/{bridge_id}-003.md"
    verdict = f"bridge/{bridge_id}-004.md"
    selected_paths = [*protected_paths, report, verdict]

    (root / proposal).write_text(
        f"""NEW
{_author("prime-builder", "proposal-session")}
# Proposal

Document: {bridge_id}
Version: 001

target_paths: {json.dumps(protected_paths)}
""",
        encoding="utf-8",
    )
    (root / go).write_text(
        f"""GO
{_author("loyal-opposition", "go-session")}
# Verdict

Document: {bridge_id}
Version: 002
Responds to: {proposal}
""",
        encoding="utf-8",
    )
    (root / report).write_text(
        f"""NEW
{_author("prime-builder", report_session)}
# Implementation Report

bridge_kind: implementation_report
Document: {bridge_id}
Version: 003
Responds to: {go}
""",
        encoding="utf-8",
    )
    manifest = "\n".join(f"- `{path}`" for path in selected_paths)
    (root / verdict).write_text(
        f"""VERIFIED
{_author("loyal-opposition", reviewer_session)}
# Verification

bridge_kind: lo_verdict
Document: {bridge_id}
Version: 004
Responds to: {report}

## Commit Finalization Evidence

- Finalization helper: `fixture`
- Intended commit subject: `fix: fixture`
- Same-transaction path set:
{manifest}
- Final commit SHA is emitted after commit creation.
""",
        encoding="utf-8",
    )

    project_authorization = {
        "id": "PAUTH-TEST",
        "project_id": "PROJECT-TEST",
        "work_item_id": "WI-TEST",
        "proposal_project_id": "PROJECT-TEST",
        "version": 1,
        "normalized_envelope_hash": "test-envelope",
        "target_classifications": [{"path": path, "mutation_class": "source"} for path in protected_paths],
        "evaluator_id": "test-evaluator",
        "evaluator_version": "1",
        "evaluator_sha256": "test-evaluator-sha",
        "taxonomy_version": "1",
        "taxonomy_sha256": "test-taxonomy-sha",
    }
    packet = {
        "bridge_id": bridge_id,
        "created_at": "2026-07-19T00:00:00Z",
        "expires_at": "2099-07-19T00:00:00Z",
        "go_file": go,
        "latest_status": "GO",
        "project_authorization": project_authorization,
        "proposal_file": proposal,
        "schema_version": 2,
        "spec_links": ["GOV-FILE-BRIDGE-AUTHORITY-001"],
        "target_path_globs": protected_paths,
    }
    packet["packet_hash"] = module.packet_hash(packet)
    pre_start_hash = packet["packet_hash"]
    packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = {
        "schema_version": 2,
        "bridge_id": bridge_id,
        "finalized_at": "2026-07-19T00:00:00Z",
        "session_id": "pb-start-session",
        "pre_start_packet_hash": pre_start_hash,
        "target_path_globs": protected_paths,
        "work_intent_claim": {
            "thread_slug": bridge_id,
            "session_id": "pb-start-session",
            "claim_kind": "go_implementation",
            "acting_role": "prime-builder",
            "session_envelope_id": "SENV-pb-start-session",
            "acting_role_attestation": "role-attestation:SENV-pb-start-session:1:0123456789abcdef",
            "project_id": "PROJECT-TEST",
        },
        "role_attestation": {
            "schema_version": 1,
            "invoking_context": "pb-start-session",
            "session_envelope_id": "SENV-pb-start-session",
            "subject": "gtkb",
            "init_command_digest": "test-init-command-digest",
            "binding_created_at": "2026-07-19T00:00:00Z",
            "role": "prime-builder",
            "source_event": "exact_init",
            "issuer": "test/exact-init",
            "attested_at": "2026-07-19T00:00:00Z",
            "evidence_reference": "role-attestation:SENV-pb-start-session:1:0123456789abcdef",
        },
        "project_authorization_decision": {"allowed": True},
    }
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    monkeypatch.setattr(
        module,
        "validate_packet_project_authorization_operation",
        lambda root, packet, *, requested_operations, target_paths: {
            "operation_time_decisions": [{"allowed": True}],
            "requested_operations": requested_operations,
            "target_paths": target_paths,
        },
    )
    return selected_paths, report, verdict


def _corrected_report_resolution(tmp_path: Path, *, controlling_go: str | None):
    bridge_id = "gtkb-corrected-report-fixture"
    proposal = f"bridge/{bridge_id}-001.md"
    go = f"bridge/{bridge_id}-002.md"
    first_report = f"bridge/{bridge_id}-003.md"
    no_go = f"bridge/{bridge_id}-004.md"
    corrected_report = f"bridge/{bridge_id}-005.md"
    verdict = f"bridge/{bridge_id}-006.md"
    protected_paths = [
        "scripts/authority.py",
        "platform_tests/scripts/test_authority.py",
    ]
    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)
    (tmp_path / proposal).write_text(
        f"NEW\n\ntarget_paths: {json.dumps(protected_paths)}\n",
        encoding="utf-8",
    )
    controlling_line = f"Controlling GO: {controlling_go}\n" if controlling_go else ""
    (tmp_path / corrected_report).write_text(
        f"REVISED\n\nbridge_kind: implementation_report\nResponds to: {no_go}\n{controlling_line}",
        encoding="utf-8",
    )
    versions = (
        SimpleNamespace(path=proposal, status="NEW", author_role="prime-builder", responds_to=None),
        SimpleNamespace(path=go, status="GO", author_role="loyal-opposition", responds_to=proposal),
        SimpleNamespace(path=first_report, status="NEW", author_role="prime-builder", responds_to=go),
        SimpleNamespace(
            path=no_go,
            status="NO-GO",
            author_role="loyal-opposition",
            responds_to=first_report,
        ),
        SimpleNamespace(
            path=corrected_report,
            status="REVISED",
            author_role="prime-builder",
            responds_to=no_go,
        ),
        SimpleNamespace(
            path=verdict,
            status="VERIFIED",
            author_role="loyal-opposition",
            responds_to=corrected_report,
        ),
    )
    return SimpleNamespace(latest_strict_state=versions[-1], audit_versions=versions), (
        proposal,
        go,
        corrected_report,
    )


def test_approved_chain_accepts_explicit_controlling_go_after_report_no_go(
    tmp_path: Path,
) -> None:
    module = _load_module()
    go = "bridge/gtkb-corrected-report-fixture-002.md"
    resolution, (proposal, _, report) = _corrected_report_resolution(tmp_path, controlling_go=go)

    chain = module._approved_chain(tmp_path, resolution)

    assert chain.proposal_path == proposal
    assert chain.go_path == go
    assert chain.report_path == report
    assert chain.target_paths == (
        "scripts/authority.py",
        "platform_tests/scripts/test_authority.py",
    )


def test_approved_chain_rejects_fully_roleless_legacy_chain(tmp_path: Path) -> None:
    module = _load_module()
    bridge_id = "gtkb-roleless-legacy-chain"
    proposal = f"bridge/{bridge_id}-001.md"
    go = f"bridge/{bridge_id}-002.md"
    report = f"bridge/{bridge_id}-003.md"
    verdict = f"bridge/{bridge_id}-004.md"
    (tmp_path / "bridge").mkdir(parents=True, exist_ok=True)
    (tmp_path / proposal).write_text(
        'NEW\n\ntarget_paths: ["scripts/authority.py"]\n',
        encoding="utf-8",
    )
    (tmp_path / report).write_text(
        f"NEW\n\nbridge_kind: implementation_report\nResponds to: {go}\n",
        encoding="utf-8",
    )
    versions = (
        SimpleNamespace(path=proposal, status="NEW", author_role=None, responds_to=None),
        SimpleNamespace(path=go, status="GO", author_role=None, responds_to=proposal),
        SimpleNamespace(path=report, status="NEW", author_role=None, responds_to=go),
        SimpleNamespace(path=verdict, status="VERIFIED", author_role=None, responds_to=report),
    )
    resolution = SimpleNamespace(latest_strict_state=versions[-1], audit_versions=versions)

    with pytest.raises(module.GateError, match="not linked to a Prime implementation report"):
        module._approved_chain(tmp_path, resolution)


@pytest.mark.parametrize(
    "controlling_go",
    [
        None,
        "bridge/gtkb-corrected-report-fixture-004.md",
        "bridge/gtkb-corrected-report-fixture-099.md",
    ],
)
def test_approved_chain_rejects_missing_or_non_go_controlling_link(
    tmp_path: Path,
    controlling_go: str | None,
) -> None:
    module = _load_module()
    resolution, _ = _corrected_report_resolution(tmp_path, controlling_go=controlling_go)

    with pytest.raises(
        module.GateError,
        match="implementation report is not linked to its approving GO",
    ):
        module._approved_chain(tmp_path, resolution)


def test_approved_chain_rejects_duplicate_controlling_go_headers(
    tmp_path: Path,
) -> None:
    module = _load_module()
    go = "bridge/gtkb-corrected-report-fixture-002.md"
    resolution, (_, _, report) = _corrected_report_resolution(tmp_path, controlling_go=go)
    report_path = tmp_path / report
    report_path.write_text(
        report_path.read_text(encoding="utf-8") + f"Controlling GO: `{go}`\n",
        encoding="utf-8",
    )

    with pytest.raises(module.GateError, match="more than one Controlling GO"):
        module._approved_chain(tmp_path, resolution)


def _stage_transaction(root: Path, selected_paths: list[str], report: str, verdict: str) -> None:
    hooks = root / "empty-hooks"
    hooks.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    proposal = report.replace("-003.md", "-001.md")
    go = report.replace("-003.md", "-002.md")
    subprocess.run(["git", "add", "--", proposal, go], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture predecessors",
        ],
        cwd=root,
        check=True,
    )
    for rel_path in selected_paths:
        if rel_path in {report, verdict}:
            continue
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# staged implementation\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", *selected_paths], cwd=root, check=True)


def _init_committed_paths(root: Path, paths: list[str]) -> None:
    hooks = root / "empty-hooks"
    hooks.mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    for rel_path in paths:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# baseline {rel_path}\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", *paths], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture baseline",
        ],
        cwd=root,
        check=True,
    )


def _seed_current_project_authorization(root: Path) -> None:
    (root / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    taxonomy_source = REPO_ROOT / "config" / "governance" / "project-authorization-operation-taxonomy.toml"
    taxonomy_target = root / "config" / "governance" / taxonomy_source.name
    taxonomy_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(taxonomy_source, taxonomy_target)
    conn = sqlite3.connect(root / "groundtruth.db")
    try:
        conn.execute("CREATE TABLE current_projects (id TEXT PRIMARY KEY, status TEXT NOT NULL)")
        conn.execute(
            """CREATE TABLE current_project_authorizations (
                id TEXT PRIMARY KEY,
                version INTEGER,
                project_id TEXT NOT NULL,
                status TEXT NOT NULL,
                authorization_name TEXT,
                owner_decision_deliberation_id TEXT,
                scope_summary TEXT,
                expires_at TEXT,
                supersedes TEXT,
                superseded_by TEXT,
                allowed_mutation_classes TEXT,
                forbidden_operations TEXT,
                included_work_item_ids TEXT,
                excluded_work_item_ids TEXT,
                included_spec_ids TEXT,
                excluded_spec_ids TEXT
            )"""
        )
        conn.execute("INSERT INTO current_projects (id, status) VALUES ('PROJECT-TEST', 'active')")
        conn.execute(
            """INSERT INTO current_project_authorizations VALUES
               (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "PAUTH-TEST",
                1,
                "PROJECT-TEST",
                "active",
                "Fixture authorization",
                "DELIB-TEST",
                "Authorize the exact source and test fixture.",
                None,
                json.dumps([]),
                json.dumps([]),
                json.dumps(["source", "test"]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
                json.dumps([]),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def test_blocks_protected_path_without_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert result["findings"][0]["path"] == "scripts/foo.py"


def test_dot_prefixed_protected_surfaces_are_blocked_without_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    paths = [
        ".claude/hooks/h.py",
        ".codex/gtkb-hooks/h.py",
        ".github/workflows/ci.yml",
        ".claude/settings.json",
        ".codex/hooks.json",
    ]
    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == set(paths)


def test_live_go_packet_allows_protected_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "bridge_id": "gtkb-example",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-example.json",
                "valid": True,
                "target_path_globs": ["scripts/foo.py"],
                "error": None,
            }
        ],
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "pass"
    assert result["cleared"][0]["evidence"] == "live_go_packet"


def test_terminal_verified_thread_allows_without_live_packet(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(
        tmp_path,
        module,
        monkeypatch,
        bridge_id="gtkb-example",
        protected_paths=["scripts/foo.py"],
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal",
        ],
        cwd=tmp_path,
        check=True,
    )
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "pass"
    assert result["cleared"][0]["evidence"] == "terminal_verified_bridge_thread"

    proposal_path = tmp_path / report.replace("-003.md", "-001.md")
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace("scripts/foo.py", "scripts/worktree-evil.py"),
        encoding="utf-8",
    )
    pinned_result = module.evaluate(tmp_path, paths=["scripts/foo.py"])
    assert pinned_result["status"] == "pass"

    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-example.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["target_path_globs"] = ["scripts/packet-evil.py"]
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    tampered_result = module.evaluate(tmp_path, paths=["scripts/packet-evil.py"])
    assert tampered_result["status"] == "fail"


def test_terminal_verified_packet_root_must_be_an_object(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(
        tmp_path,
        module,
        monkeypatch,
        bridge_id="gtkb-terminal-root",
        protected_paths=["scripts/foo.py"],
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal",
        ],
        cwd=tmp_path,
        check=True,
    )
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-terminal-root.json"
    packet_path.write_text("[]", encoding="utf-8")
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert any(
        "decoded packet root is not an object" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )


def test_evaluation_pins_one_head_oid_across_index_and_terminal_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(
        tmp_path,
        module,
        monkeypatch,
        bridge_id="gtkb-pinned-head",
        protected_paths=["scripts/foo.py"],
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    commit_args = [
        "git",
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        f"core.hooksPath={tmp_path / 'empty-hooks'}",
        "commit",
        "-qm",
    ]
    subprocess.run([*commit_args, "good terminal"], cwd=tmp_path, check=True)
    old_oid = subprocess.run(
        ["git", "rev-parse", "HEAD^{commit}"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    proposal_path = tmp_path / report.replace("-003.md", "-001.md")
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8").replace("scripts/foo.py", "scripts/head-evil.py"),
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "--", report.replace("-003.md", "-001.md")],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run([*commit_args, "tampered successor"], cwd=tmp_path, check=True)
    new_oid = subprocess.run(
        ["git", "rev-parse", "HEAD^{commit}"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(["git", "update-ref", "HEAD", old_oid, new_oid], cwd=tmp_path, check=True)
    subprocess.run(["git", "read-tree", old_oid], cwd=tmp_path, check=True)
    implementation_path = tmp_path / "scripts" / "foo.py"
    implementation_path.write_text("# staged after captured head\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", "scripts/foo.py"], cwd=tmp_path, check=True)
    original_resolve = module._resolve_head_oid

    def advance_symbolic_head(root: Path) -> str:
        captured = original_resolve(root)
        assert captured == old_oid
        subprocess.run(["git", "update-ref", "HEAD", new_oid, old_oid], cwd=root, check=True)
        return captured

    monkeypatch.setattr(module, "_resolve_head_oid", advance_symbolic_head)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "pass"
    assert result["protected_paths"] == ["scripts/foo.py"]
    assert result["cleared"][0]["evidence"] == "terminal_verified_bridge_thread"


def test_routine_paths_short_circuit_before_packet_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()

    def fail_if_called(root):
        raise AssertionError("routine paths must not read implementation packets")

    monkeypatch.setattr(module, "list_named_packets", fail_if_called)

    result = module.evaluate(
        tmp_path,
        paths=[
            "memory/MEMORY.md",
            "docs/guide.md",
            "bridge/thread-note.md",
            ".gtkb-state/state.json",
            "independent-progress-assessments/report.md",
        ],
    )

    assert result["status"] == "pass"
    assert result["protected_paths"] == []


def test_verified_bridge_file_without_finalization_evidence_blocks(
    tmp_path: Path,
) -> None:
    module = _load_module()
    bridge_file = tmp_path / "bridge" / "gtkb-example-004.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text(
        """VERIFIED

# Verdict

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest fixture` | yes | PASS |
""",
        encoding="utf-8",
    )

    result = module.evaluate(tmp_path, paths=["bridge/gtkb-example-004.md"])

    assert result["status"] == "fail"
    assert "Commit Finalization Evidence" in result["findings"][0]["reason"]


def test_verified_bridge_file_with_finalization_evidence_passes(tmp_path: Path) -> None:
    module = _load_module()
    bridge_file = tmp_path / "bridge" / "gtkb-example-004.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text(
        """VERIFIED

# Verdict

## Commit Finalization Evidence

- Finalization helper: `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`
- Same-transaction path set:
- `scripts/foo.py`
- `bridge/gtkb-example-003.md`
- `bridge/gtkb-example-004.md`
""",
        encoding="utf-8",
    )

    result = module.evaluate(tmp_path, paths=["bridge/gtkb-example-004.md"])

    assert result["status"] == "pass"
    assert result["findings"] == []


def test_corrupt_packet_blocks_protected_path_when_no_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "path": ".gtkb-state/implementation-authorizations/by-bridge/bad.json",
                "bridge_id": None,
                "valid": False,
                "target_path_globs": [],
                "error": "corrupt or unreadable",
            }
        ],
    )

    result = module.evaluate(tmp_path, paths=["scripts/foo.py"])

    assert result["status"] == "fail"
    assert "evidence_errors" in result["findings"][0]


def test_groundtruth_db_and_githooks_are_protected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=["groundtruth.db", ".githooks/pre-commit"])

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == {
        "groundtruth.db",
        ".githooks/pre-commit",
    }


def test_bridge_index_and_runtime_state_paths_are_protected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    paths = [
        "bridge/INDEX.md",
        ".gtkb-state/implementation-authorizations/current.json",
        ".gtkb-state/work-intent/thread.json",
        ".gtkb-state/bridge-poller/dispatch-state.json",
        ".gtkb-state/dispatcher-daemon/status.json",
    ]
    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "fail"
    assert {finding["path"] for finding in result["findings"]} == set(paths)


def test_non_verified_numbered_bridge_files_remain_helper_commit_compatible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()

    def fail_if_called(root):
        raise AssertionError("non-VERIFIED numbered bridge files should not read implementation packets")

    monkeypatch.setattr(module, "list_named_packets", fail_if_called)
    bridge_file = tmp_path / "bridge" / "example-003.md"
    bridge_file.parent.mkdir()
    bridge_file.write_text("NEW\n\n# Implementation report\n", encoding="utf-8")

    result = module.evaluate(tmp_path, paths=["bridge/example-003.md"])

    assert result["status"] == "pass"
    assert result["protected_paths"] == []


def test_json_shape_for_cli_paths(tmp_path: Path, capsys, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    exit_code = module.main(["--project-root", str(tmp_path), "--paths", "scripts/foo.py", "--json"])
    parsed = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert parsed["status"] == "fail"
    assert parsed["protected_paths"] == ["scripts/foo.py"]
    assert set(parsed) == {
        "status",
        "findings",
        "cleared",
        "skipped_unprotected",
        "protected_paths",
        "audit_gaps",
        "evidence_summary",
    }
    assert "transaction-local" not in parsed["findings"][0]["reason"]

    human_exit = module.main(["--project-root", str(tmp_path), "--paths", "scripts/foo.py"])
    human_output = capsys.readouterr().out
    assert human_exit == 1
    assert "transaction-local" not in human_output
    assert "committed terminal VERIFIED evidence" in human_output


def test_evidence_sources_are_loaded_once_for_343_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    calls = {"live": 0, "verified": 0}

    def live_packets(root):
        calls["live"] += 1
        return [
            {
                "bridge_id": "gtkb-live",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-live.json",
                "valid": True,
                "target_path_globs": ["scripts/live-*.py"],
                "error": None,
            }
        ]

    def verified_entry(root):
        calls["verified"] += 1
        return [("gtkb-verified", ["scripts/verified-*.py"])], [], 1

    monkeypatch.setattr(module, "list_named_packets", live_packets)
    monkeypatch.setattr(
        module,
        "_load_verified_evidence",
        lambda root, head_oid=None, protected_paths=None: verified_entry(root),
    )
    paths = [f"scripts/live-{index}.py" for index in range(172)] + [
        f"scripts/verified-{index}.py" for index in range(171)
    ]

    result = module.evaluate(tmp_path, paths=paths)

    assert result["status"] == "pass"
    assert len(result["cleared"]) == 343
    assert calls == {"live": 1, "verified": 1}
    assert result["evidence_summary"] == {
        "live_go_packets_scanned": 1,
        "live_go_packets_valid": 1,
        "terminal_verified_packets_scanned": 1,
        "terminal_verified_threads_loaded": 1,
    }


def test_live_go_precedence_and_errors_match_snapshot_decisions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "list_named_packets",
        lambda root: [
            {
                "bridge_id": None,
                "path": ".gtkb-state/implementation-authorizations/by-bridge/bad.json",
                "valid": False,
                "target_path_globs": [],
                "error": "corrupt or unreadable",
            },
            {
                "bridge_id": "gtkb-live",
                "path": ".gtkb-state/implementation-authorizations/by-bridge/gtkb-live.json",
                "valid": True,
                "target_path_globs": ["scripts/shared.py"],
                "error": None,
            },
        ],
    )
    monkeypatch.setattr(
        module,
        "_load_verified_evidence",
        lambda root, head_oid=None, protected_paths=None: (
            [("gtkb-verified", ["scripts/shared.py", "scripts/verified.py"])],
            [],
            1,
        ),
    )

    result = module.evaluate(
        tmp_path,
        paths=["scripts/shared.py", "scripts/verified.py", "scripts/unauthorized.py"],
    )

    assert result["status"] == "fail"
    assert result["cleared"] == [
        {
            "path": "scripts/shared.py",
            "status": "cleared",
            "evidence": "live_go_packet",
            "source": "gtkb-live",
        },
        {
            "path": "scripts/verified.py",
            "status": "cleared",
            "evidence": "terminal_verified_bridge_thread",
            "source": "gtkb-verified",
        },
    ]
    assert result["findings"][0]["path"] == "scripts/unauthorized.py"
    assert result["findings"][0]["evidence_errors"] == [
        ".gtkb-state/implementation-authorizations/by-bridge/bad.json: corrupt or unreadable"
    ]


def test_transaction_local_verified_manifest_clears_wi5629_shaped_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    immutable_checks = {"anchors": False, "independence": False}
    proposal = report.replace("-003.md", "-001.md")

    def validate_anchors(content: str, project_root: Path):
        del content
        with pytest.raises(PermissionError):
            (project_root / proposal).write_text("transient anchor tamper\n", encoding="utf-8")
        immutable_checks["anchors"] = True
        return []

    def validate_independence(content: str, bridge_id: str, project_root: Path, **kwargs):
        del content, bridge_id, kwargs
        with pytest.raises(PermissionError):
            (project_root / report).write_text("transient independence tamper\n", encoding="utf-8")
        immutable_checks["independence"] = True
        return None

    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", validate_anchors)
    monkeypatch.setattr(module, "verdict_self_review_reason", validate_independence)
    pauth_calls = []

    def validate_pauth(root, packet, *, requested_operations, target_paths):
        pauth_calls.append((requested_operations, target_paths))
        return {"operation_time_decisions": [{"allowed": True}]}

    monkeypatch.setattr(module, "validate_packet_project_authorization_operation", validate_pauth)
    (tmp_path / verdict).write_text("MALFORMED WORKTREE BYTES\n", encoding="utf-8")

    result = module.evaluate(tmp_path)

    assert result["status"] == "pass"
    assert [item["evidence"] for item in result["cleared"]] == [
        "transaction_local_verified_manifest",
        "transaction_local_verified_manifest",
    ]
    assert {item["source"] for item in result["cleared"]} == {"gtkb-wi5629-fixture"}
    assert immutable_checks == {"anchors": True, "independence": True}
    assert pauth_calls == [
        (
            ["protected_mutation"],
            [
                "scripts/bridge_lifecycle_resolver.py",
                "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
            ],
        )
    ]


def test_finalized_packet_uses_real_current_pauth_validation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    protected_paths, _, _ = _write_transaction_chain(tmp_path, module, monkeypatch)
    protected_paths = protected_paths[:2]
    _seed_current_project_authorization(tmp_path)
    monkeypatch.setattr(
        module,
        "validate_packet_project_authorization_operation",
        implementation_authorization.validate_packet_project_authorization_operation,
    )
    bridge_id = "gtkb-wi5629-fixture"
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    row = implementation_authorization._project_authorization_row(tmp_path, "PAUTH-TEST")
    packet["project_authorization"] = implementation_authorization.validate_project_authorization_row(
        tmp_path,
        row,
        proposal_project_id="PROJECT-TEST",
        work_item_id=None,
        spec_links=packet["spec_links"],
        target_paths=protected_paths,
        requested_operations=["protected_mutation"],
    )
    start = packet.pop("implementation_start")
    packet.pop("packet_hash")
    packet["schema_version"] = 2
    packet["packet_hash"] = module.packet_hash(packet)
    start["pre_start_packet_hash"] = packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = start
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    chain = module._ApprovedChain(
        proposal_path=f"bridge/{bridge_id}-001.md",
        go_path=f"bridge/{bridge_id}-002.md",
        report_path=f"bridge/{bridge_id}-003.md",
        target_paths=tuple(protected_paths),
    )

    loaded, errors = module._load_finalized_packet(tmp_path, bridge_id, chain, protected_paths)

    assert errors == []
    assert loaded is not None

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute("UPDATE current_project_authorizations SET status = 'revoked' WHERE id = 'PAUTH-TEST'")
        conn.commit()
    finally:
        conn.close()
    loaded, errors = module._load_finalized_packet(tmp_path, bridge_id, chain, protected_paths)
    assert loaded is None
    assert any("PAUTH validation failed" in error and "not active" in error for error in errors)

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE current_project_authorizations SET status = 'active', expires_at = '2000-01-01T00:00:00Z' "
            "WHERE id = 'PAUTH-TEST'"
        )
        conn.commit()
    finally:
        conn.close()
    loaded, errors = module._load_finalized_packet(tmp_path, bridge_id, chain, protected_paths)
    assert loaded is None
    assert any("PAUTH validation failed" in error and "expired" in error for error in errors)


def test_prospective_audit_tree_is_index_complete_and_ignores_live_gate_tamper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    gate_path = tmp_path / ".claude" / "hooks" / "bridge-compliance-gate.py"
    gate_path.parent.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py", gate_path)
    (tmp_path / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "add",
            "--",
            ".claude/hooks/bridge-compliance-gate.py",
            "groundtruth.toml",
        ],
        cwd=tmp_path,
        check=True,
    )
    hooks = tmp_path / "empty-hooks"
    hooks.mkdir()
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture authority",
        ],
        cwd=tmp_path,
        check=True,
    )
    bridge_id = "gtkb-hermetic-audit-fixture"
    candidate_rel = f"bridge/{bridge_id}-001.md"
    candidate_path = tmp_path / candidate_rel
    candidate_path.parent.mkdir()
    candidate_path.write_text(
        f"""ADVISORY
{_author("loyal-opposition", "019f0000-0000-7000-8000-000000000001")}
bridge_kind: governance_advisory
Document: {bridge_id}
Version: 001
Author: Loyal Opposition (Codex, harness A)
Date: 2026-07-19 UTC

# Hermetic audit fixture

## Source

Focused WI-5633 test fixture.

## Claim

The compliance audit must use only the prospective index snapshot.

## Owner Decision Needed

None.

## Recommended Prime Action

Retain fail-closed snapshot isolation.

## Classification Slot

Non-dispatchable governance advisory test fixture.
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "--", candidate_rel], cwd=tmp_path, check=True)
    hostile = tmp_path / "hostile-runtime"
    hostile.mkdir()
    marker = tmp_path / "sitecustomize-executed"
    (hostile / "sitecustomize.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('injected', encoding='utf-8')\n",
        encoding="utf-8",
    )
    (hostile / "git.cmd").write_text("@echo hostile-git-executed\r\n@exit /b 99\r\n", encoding="utf-8")
    monkeypatch.setenv("PYTHONPATH", str(hostile))
    monkeypatch.setenv("PYTHONHOME", str(hostile))
    monkeypatch.setenv("PATH", str(hostile))

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, bridge_id, index_snapshot) as bridge_snapshot,
    ):
        snapshot_root = bridge_snapshot.root
        assert snapshot_root.parent == tmp_path / ".gtkb-state"
        assert (snapshot_root / ".claude" / "hooks" / "bridge-compliance-gate.py").is_file()
        snapshot_candidate = snapshot_root / candidate_rel
        candidate = snapshot_candidate.read_text(encoding="utf-8")
        gate_path.write_text(
            "raise RuntimeError('live worktree gate must not execute')\n",
            encoding="utf-8",
        )

        audit = module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=candidate,
        )
        assert snapshot_candidate.is_file()

    assert audit["decision"] == "pass"
    assert not marker.exists()

    mutation_blocked = False

    def mutate_snapshot_authority(*, file_path: Path, content: str, project_root: Path):
        nonlocal mutation_blocked
        del file_path, content
        with pytest.raises(PermissionError):
            (project_root / "groundtruth.toml").write_text("tampered during audit\n", encoding="utf-8")
        mutation_blocked = True
        return {"decision": "pass"}

    monkeypatch.setattr(module, "run_bridge_compliance_audit", mutate_snapshot_authority)
    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, bridge_id, index_snapshot) as bridge_snapshot,
    ):
        module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=(bridge_snapshot.root / candidate_rel).read_text(encoding="utf-8"),
        )
    assert mutation_blocked is True


def test_transaction_local_manifest_must_equal_complete_staged_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    verdict_path = tmp_path / verdict
    verdict_path.write_text(
        verdict_path.read_text(encoding="utf-8").replace(
            "- `platform_tests/scripts/test_bridge_lifecycle_resolver.py`\n",
            "",
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "--", verdict], cwd=tmp_path, check=True)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda content, project_root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        "manifest does not equal the staged path set" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )
    assert "transaction-local VERIFIED manifest evidence" in module._format_human(
        result,
        transaction_available=True,
    )


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        ("duplicate", "duplicate path"),
        ("glob", "glob path"),
        ("second_candidate", "exactly one VERIFIED candidate"),
    ],
)
def test_transaction_local_manifest_rejects_each_ambiguous_form(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    expected: str,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    verdict_path = tmp_path / verdict
    content = verdict_path.read_text(encoding="utf-8")
    staged = [verdict]
    if failure == "duplicate":
        content = content.replace(
            "- `scripts/bridge_lifecycle_resolver.py`\n",
            "- `scripts/bridge_lifecycle_resolver.py`\n- `scripts/bridge_lifecycle_resolver.py`\n",
        )
    elif failure == "glob":
        content = content.replace("- `scripts/bridge_lifecycle_resolver.py`\n", "- `scripts/*.py`\n")
    else:
        second_candidate = "bridge/gtkb-other-004.md"
        (tmp_path / second_candidate).write_text(
            content.replace("gtkb-wi5629-fixture", "gtkb-other"),
            encoding="utf-8",
        )
        staged.append(second_candidate)
    verdict_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", "--", *staged], cwd=tmp_path, check=True)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(expected in error for finding in result["findings"] for error in finding.get("evidence_errors", []))


@pytest.mark.parametrize(
    ("manifest_path", "expected"),
    [
        ("../outside.py", "path escape"),
        (".git/config", "forbidden Git path"),
        ("scripts/*.py", "glob path"),
        ("scripts/", "directory shorthand"),
        (" scripts/leading.py", "non-canonical or unsafe"),
        ("scripts/back\\slash.py", "non-canonical or unsafe"),
        ("scripts/CON.txt", "non-canonical or unsafe"),
    ],
)
def test_transaction_manifest_rejects_unsafe_path_forms(
    tmp_path: Path,
    manifest_path: str,
    expected: str,
) -> None:
    module = _load_module()
    content = f"""VERIFIED

## Commit Finalization Evidence

- Same-transaction path set:
- `{manifest_path}`
"""

    _, errors = module._parse_transaction_manifest(tmp_path, content)

    assert any(expected in error for error in errors)


def test_transaction_manifest_rejects_casefold_collision(tmp_path: Path) -> None:
    module = _load_module()
    content = """VERIFIED

## Commit Finalization Evidence

- Same-transaction path set:
- `Scripts/Authority.py`
- `scripts/authority.py`
"""

    _, errors = module._parse_transaction_manifest(tmp_path, content)

    assert any("casefold or Unicode collision" in error for error in errors)


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        ("self_review", "same-session self-review"),
        ("duplicate_session", "exactly one author_session_context_id"),
        ("duplicate_report_session", "exactly one author_session_context_id"),
        ("missing_packet", "implementation-start packet is absent"),
        ("corrupt_json", "packet is not valid JSON"),
        ("packet_root", "packet root is not an object"),
        ("packet_hash", "packet hash mismatch"),
        ("packet_schema", "unsupported schema"),
        ("missing_start", "packet is not finalized"),
        ("start_schema", "implementation-start evidence has an unsupported schema"),
        ("missing_start_session", "implementation-start lacks a session id"),
        ("missing_claim", "lacks a work-intent claim"),
        ("claim_kind", "claim kind is not go_implementation"),
        ("claim_role", "claim acting role is not prime-builder"),
        ("claim_session", "claim session differs from start session"),
        ("wrong_bridge", "names another bridge"),
        ("not_finalized", "packet is not finalized"),
        ("decision_denied", "lacks an allowed project decision"),
        ("missing_pauth", "lacks project authorization"),
        # WI-5824 Fix B (DELIB-202667723): ambient-now expiry no longer denies
        # transaction-local evidence; this fixture's mutated packet (expiry in
        # 2000, finalized_at in 2026) is the never-live-at-implementation shape,
        # which stays fail-closed under the implementation-time-authority rule.
        ("expired", "was not live at implementation"),
        ("invalid_expiry", "packet has invalid expiry"),
        ("proposal_drift", "resolver-approved proposal"),
        ("go_drift", "resolver-approved GO"),
        ("prestart_hash", "pre-start packet hash mismatch"),
        ("session_drift", "attested context differs from start session"),
        ("attestation_schema", "role-attestation schema is unsupported"),
        ("attestation_role", "attested role is not prime-builder"),
        ("attestation_source", "role authority is not exact-init"),
        ("claim_envelope", "claim envelope differs from role attestation"),
        ("claim_attestation", "claim reference differs from role attestation"),
        ("claim_project", "claim project differs from packet PAUTH"),
        ("out_of_scope", "target scope differs"),
        ("pauth_denied", "protected-mutation PAUTH validation failed"),
    ],
)
def test_transaction_local_candidate_fails_closed_on_provenance_and_packet_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    expected: str,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    if failure == "self_review":
        report_path = tmp_path / report
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace("pb-session", "lo-session"),
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "--", report], cwd=tmp_path, check=True)
    elif failure == "duplicate_session":
        verdict_path = tmp_path / verdict
        verdict_path.write_text(
            verdict_path.read_text(encoding="utf-8") + "\nauthor_session_context_id: second-reviewer-session\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "--", verdict], cwd=tmp_path, check=True)
    elif failure == "duplicate_report_session":
        report_path = tmp_path / report
        report_path.write_text(
            report_path.read_text(encoding="utf-8") + "\nauthor_session_context_id: second-pb-session\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "--", report], cwd=tmp_path, check=True)
    elif failure == "pauth_denied":
        monkeypatch.setattr(
            module,
            "validate_packet_project_authorization_operation",
            lambda *args, **kwargs: (_ for _ in ()).throw(module.AuthorizationError("current PAUTH denied")),
        )
    else:
        packet_path = (
            tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-wi5629-fixture.json"
        )
        if failure == "missing_packet":
            packet_path.unlink()
            packet = None
        elif failure == "corrupt_json":
            packet_path.write_text("{", encoding="utf-8")
            packet = None
        elif failure == "packet_root":
            packet_path.write_text("[]", encoding="utf-8")
            packet = None
        else:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        if packet is not None:
            if failure == "packet_hash":
                packet["packet_hash"] = "sha256:wrong"
            elif failure == "packet_schema":
                packet["schema_version"] = 2
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_start":
                packet.pop("implementation_start")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "start_schema":
                packet["implementation_start"]["schema_version"] = 1
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_start_session":
                packet["implementation_start"].pop("session_id")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_claim":
                packet["implementation_start"].pop("work_intent_claim")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_kind":
                packet["implementation_start"]["work_intent_claim"]["claim_kind"] = "draft_review"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_role":
                packet["implementation_start"]["work_intent_claim"]["acting_role"] = "loyal-opposition"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_session":
                packet["implementation_start"]["work_intent_claim"]["session_id"] = "other-session"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "wrong_bridge":
                packet["implementation_start"]["bridge_id"] = "gtkb-other"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "not_finalized":
                packet["implementation_start"].pop("finalized_at")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "decision_denied":
                packet["implementation_start"]["project_authorization_decision"] = {"allowed": False}
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "missing_pauth":
                packet.pop("project_authorization")
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "expired":
                packet["expires_at"] = "2000-01-01T00:00:00Z"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "invalid_expiry":
                packet["expires_at"] = "not-a-timestamp"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "proposal_drift":
                packet["proposal_file"] = "bridge/gtkb-other-001.md"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "go_drift":
                packet["go_file"] = "bridge/gtkb-other-002.md"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "prestart_hash":
                packet["implementation_start"]["pre_start_packet_hash"] = "sha256:wrong"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "session_drift":
                packet["implementation_start"]["role_attestation"]["invoking_context"] = "other-session"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "attestation_schema":
                packet["implementation_start"]["role_attestation"]["schema_version"] = 2
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "attestation_role":
                packet["implementation_start"]["role_attestation"]["role"] = "loyal-opposition"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "attestation_source":
                packet["implementation_start"]["role_attestation"]["source_event"] = "owner_role_change"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_envelope":
                packet["implementation_start"]["work_intent_claim"]["session_envelope_id"] = "SENV-other"
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_attestation":
                packet["implementation_start"]["work_intent_claim"]["acting_role_attestation"] = (
                    "role-attestation:SENV-other:1:fedcba9876543210"
                )
                packet["packet_hash"] = module.packet_hash(packet)
            elif failure == "claim_project":
                packet["implementation_start"]["work_intent_claim"]["project_id"] = "PROJECT-OTHER"
                packet["packet_hash"] = module.packet_hash(packet)
            else:
                packet["target_path_globs"] = ["scripts/bridge_lifecycle_resolver.py"]
                packet["implementation_start"]["target_path_globs"] = packet["target_path_globs"]
                packet["packet_hash"] = module.packet_hash(packet)
            packet_path.write_text(json.dumps(packet), encoding="utf-8")

    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda content, project_root: [])

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        finding.get("path") == verdict and any(expected in error for error in finding.get("evidence_errors", []))
        for finding in result["findings"]
    )


def test_explicit_paths_mode_never_grants_transaction_local_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    monkeypatch.setattr(module, "list_named_packets", lambda root: [])

    result = module.evaluate(tmp_path, paths=selected_paths)

    assert result["status"] == "fail"
    assert all(item.get("evidence") != "transaction_local_verified_manifest" for item in result["cleared"])


def test_cli_rejects_staged_and_explicit_paths_together() -> None:
    module = _load_module()

    with pytest.raises(SystemExit):
        module.main(["--staged", "--paths", "scripts/foo.py"])


def test_index_snapshot_includes_deletions_and_both_rename_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["scripts/delete.py", "scripts/old.py"])
    subprocess.run(["git", "rm", "-q", "--", "scripts/delete.py"], cwd=tmp_path, check=True)
    subprocess.run(["git", "mv", "scripts/old.py", "scripts/new.py"], cwd=tmp_path, check=True)

    with module._index_snapshot(tmp_path) as snapshot:
        assert set(snapshot.selected_paths) == {
            "scripts/delete.py",
            "scripts/old.py",
            "scripts/new.py",
        }
        assert snapshot.status_by_path == {
            "scripts/delete.py": "D",
            "scripts/old.py": "R-source",
            "scripts/new.py": "R-destination",
        }

    monkeypatch.setattr(module, "list_named_packets", lambda root: [])
    result = module.evaluate(tmp_path)
    assert result["status"] == "fail"
    assert set(result["protected_paths"]) == {
        "scripts/delete.py",
        "scripts/old.py",
        "scripts/new.py",
    }


@pytest.mark.parametrize("exit_kind", ["normal", "exception", "interrupt"])
def test_index_snapshot_uses_scratch_root_and_cleans_every_exit(
    tmp_path: Path,
    exit_kind: str,
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["tracked.txt"])
    index_text = subprocess.run(
        ["git", "rev-parse", "--git-path", "index"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    index_path = Path(index_text)
    if not index_path.is_absolute():
        index_path = tmp_path / index_path
    index_preimage = index_path.read_bytes()

    def exercise() -> None:
        with module._index_snapshot(tmp_path) as snapshot:
            assert snapshot.index_file.parent.parent == tmp_path / ".gtkb-state"
            assert snapshot.index_file.parent.name.startswith(".gtkb-index-")
            assert list(tmp_path.glob(".gtkb-index-*")) == []
            if exit_kind == "exception":
                raise RuntimeError("fixture exception")
            if exit_kind == "interrupt":
                raise KeyboardInterrupt

    if exit_kind == "normal":
        exercise()
    elif exit_kind == "exception":
        with pytest.raises(RuntimeError, match="fixture exception"):
            exercise()
    else:
        with pytest.raises(KeyboardInterrupt):
            exercise()

    assert index_path.read_bytes() == index_preimage
    assert list(tmp_path.glob(".gtkb-index-*")) == []
    assert list((tmp_path / ".gtkb-state").glob(".gtkb-index-*")) == []


def test_root_gitignore_defensively_ignores_transient_indexes() -> None:
    lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert lines.count(".gtkb-index-*/") == 1


@pytest.mark.parametrize(
    ("mode", "stage", "expected"),
    [
        ("120000", "0", "unsupported index mode 120000"),
        ("160000", "0", "unsupported index mode 160000"),
        ("100664", "0", "unsupported index mode 100664"),
        ("100644", "2", "unmerged index entry"),
    ],
)
def test_raw_index_inventory_rejects_links_gitlinks_modes_and_unmerged_entries(
    mode: str,
    stage: str,
    expected: str,
) -> None:
    module = _load_module()
    raw = f"{mode} {'0' * 40} {stage}\tscripts/unsafe.py\0".encode()

    with pytest.raises(module.GateError, match=expected):
        module._parse_index_inventory(raw)


def test_raw_index_materialization_bypasses_smudge_and_eol_filters(
    tmp_path: Path,
) -> None:
    module = _load_module()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitattributes").write_text("*.txt text eol=crlf\n", encoding="utf-8")
    (tmp_path / "authority.txt").write_bytes(b"authority\n")
    subprocess.run(
        ["git", "add", "--", ".gitattributes", "authority.txt"],
        cwd=tmp_path,
        check=True,
    )
    hooks = tmp_path / "empty-hooks"
    hooks.mkdir()
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "raw materialization fixture",
        ],
        cwd=tmp_path,
        check=True,
    )

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, "gtkb-unused", index_snapshot) as bridge_snapshot,
    ):
        assert (bridge_snapshot.root / "authority.txt").read_bytes() == b"authority\n"


def test_scratch_root_rejects_parent_junction_or_reparse_point(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    scratch = tmp_path / ".gtkb-state"
    scratch.mkdir()
    original = module._path_is_linklike
    monkeypatch.setattr(
        module,
        "_path_is_linklike",
        lambda path: path == scratch or original(path),
    )

    with pytest.raises(module.GateError, match="symlink, junction, or reparse"):
        module._scratch_root(tmp_path)


def test_raw_materialization_ignores_replace_refs_and_git_environment_injection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["authority.txt"])
    original = subprocess.run(
        ["git", "rev-parse", ":authority.txt"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    original_bytes = subprocess.run(
        ["git", "cat-file", "blob", original],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    ).stdout
    replacement = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=tmp_path,
        check=True,
        input="replacement bytes\n",
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(["git", "replace", original, replacement], cwd=tmp_path, check=True)
    hostile = tmp_path / "hostile-objects"
    hostile.mkdir()
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(hostile))
    monkeypatch.setenv("GIT_ALTERNATE_OBJECT_DIRECTORIES", str(hostile))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.hooksPath")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(hostile))

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, "gtkb-unused", index_snapshot) as bridge_snapshot,
    ):
        assert index_snapshot.object_format == "sha1"
        assert (bridge_snapshot.root / "authority.txt").read_bytes() == original_bytes
        assert index_snapshot.env["GIT_NO_REPLACE_OBJECTS"] == "1"
        assert "GIT_OBJECT_DIRECTORY" not in index_snapshot.env
        assert "GIT_CONFIG_COUNT" not in index_snapshot.env


@pytest.mark.parametrize(
    "raw_path",
    [
        b" scripts/leading.py",
        b"scripts/trailing.py ",
        b"scripts\\backslash.py",
        b"scripts/trailing-dot.",
        b"scripts/CON.txt",
    ],
)
def test_raw_index_inventory_rejects_noncanonical_platform_paths(
    raw_path: bytes,
) -> None:
    module = _load_module()
    raw = b"100644 " + (b"0" * 40) + b" 0\t" + raw_path + b"\0"

    with pytest.raises(module.GateError, match="non-canonical|unsafe|platform-reserved"):
        module._parse_index_inventory(raw)


@pytest.mark.parametrize(
    ("first", "second"),
    [
        ("Scripts/Authority.py", "scripts/authority.py"),
        ("scripts/\u00e9.py", "scripts/e\u0301.py"),
    ],
)
def test_raw_index_inventory_rejects_casefold_and_unicode_collisions(first: str, second: str) -> None:
    module = _load_module()
    records = [
        f"100644 {'0' * 40} 0\t{first}".encode(),
        f"100644 {'1' * 40} 0\t{second}".encode(),
    ]

    with pytest.raises(module.GateError, match="casefold or Unicode-normalized"):
        module._parse_index_inventory(b"\0".join(records) + b"\0")


def test_raw_materialization_exempts_oversized_blob_in_ledger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # WI-5659 mechanism 3 (in-ledger; DELIB-202667186 / DELIB-202667188). This
    # supersedes the prior fail-closed-on-oversized-blob contract, which made every
    # governed VERIFIED finalization impossible because tracked groundtruth.db is
    # 762,720,256 bytes. An oversized blob is now recorded IN the ledger with
    # content_exempt=True and is NOT written to disk; it is still hash-verified while
    # streaming.
    module = _load_module()
    _init_committed_paths(tmp_path, ["authority.txt"])
    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 1)

    with (
        module._index_snapshot(tmp_path) as index_snapshot,
        module._bridge_snapshot(tmp_path, "gtkb-unused", index_snapshot) as bridge_snapshot,
    ):
        entry = bridge_snapshot.ledger["authority.txt"]
        assert entry.content_exempt is True
        assert entry.oid and entry.size >= 0 and entry.mode
        assert not (bridge_snapshot.root / "authority.txt").exists()


def test_index_snapshot_parser_fails_closed_on_unsupported_status() -> None:
    module = _load_module()

    with pytest.raises(module.GateError, match="unsupported staged Git status"):
        module._parse_staged_name_status(b"T\x00scripts/type-change.py\x00")

    with pytest.raises(module.GateError, match="non-canonical path bytes"):
        module._parse_staged_name_status(b"A\x00 scripts/leading.py\x00")


def test_git_resolution_ignores_hostile_path_at_module_startup(tmp_path: Path) -> None:
    hostile = tmp_path / "hostile-path"
    hostile.mkdir()
    marker = tmp_path / "hostile-git-executed"
    (hostile / "git.cmd").write_text(
        f"@echo hostile>{marker}\r\n@exit /b 0\r\n",
        encoding="utf-8",
    )
    hostile_posix = hostile / "git"
    hostile_posix.write_text(
        f"#!/bin/sh\nprintf hostile > {marker!s}\nexit 0\n",
        encoding="utf-8",
    )
    hostile_posix.chmod(0o755)
    child = f"""
import importlib.util
import json
import pathlib
import sys
spec = importlib.util.spec_from_file_location("checker_startup_fixture", {str(SCRIPT_PATH)!r})
module = importlib.util.module_from_spec(spec)
sys.modules["checker_startup_fixture"] = module
spec.loader.exec_module(module)
result = module._run_git(pathlib.Path({str(REPO_ROOT)!r}), "--version", text=True)
print(json.dumps({{"path": module._trusted_git_executable(), "returncode": result.returncode, "stdout": result.stdout}}))
"""
    env = os.environ.copy()
    env["PATH"] = str(hostile)
    result = subprocess.run(
        [str(Path(sys.executable).resolve()), "-I", "-B", "-c", child],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["path"]).resolve().parent != hostile.resolve()
    assert payload["returncode"] == 0
    assert payload["stdout"].startswith("git version ")
    assert not marker.exists()


def test_copied_index_cannot_be_replaced_between_consumers(tmp_path: Path) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["authority.txt"])
    replacement = tmp_path / "replacement-index"
    replacement.write_bytes((tmp_path / ".git" / "index").read_bytes())

    with module._index_snapshot(tmp_path) as snapshot:
        module._index_entries(tmp_path, snapshot)
        with pytest.raises(OSError):
            os.replace(replacement, snapshot.index_file)
        assert module._staged_text(tmp_path, "authority.txt", snapshot).startswith("# baseline")


def test_committed_terminal_snapshot_blocks_transient_substitution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal chain",
        ],
        cwd=tmp_path,
        check=True,
    )
    head_oid = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    original_resolver = module.resolve_bridge_lifecycle
    attempts: list[str] = []

    def attack_snapshot(snapshot_root: Path, bridge_id: str):
        proposal = snapshot_root / f"bridge/{bridge_id}-001.md"
        replacement = snapshot_root.parent / "replacement-proposal.md"
        replacement.write_text("NO-GO\n", encoding="utf-8")
        with pytest.raises(OSError):
            os.replace(replacement, proposal)
        attempts.append("entry")
        renamed_root = snapshot_root.with_name(f"{snapshot_root.name}-renamed")
        with pytest.raises(OSError):
            os.replace(snapshot_root, renamed_root)
        attempts.append("root")
        return original_resolver(snapshot_root, bridge_id)

    monkeypatch.setattr(module, "resolve_bridge_lifecycle", attack_snapshot)
    evidence, errors, count = module._load_verified_evidence(tmp_path, head_oid=head_oid)

    assert count == 1
    assert not errors
    assert evidence
    assert attempts == ["entry", "root"]


def test_snapshot_hardlink_race_fails_closed_on_link_count_drift(
    tmp_path: Path,
) -> None:
    module = _load_module()
    bridge_id = "gtkb-hardlink-race-fixture"
    rel_path = f"bridge/{bridge_id}-001.md"
    _init_committed_paths(tmp_path, [rel_path])
    head_oid = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    hardlink = tmp_path / ".gtkb-state" / "hardlink-race"

    with module._bridge_snapshot(tmp_path, bridge_id, head_oid=head_oid) as snapshot:
        authority = snapshot.root / rel_path
        with (
            pytest.raises(module.GateError, match="identity drifted"),
            module._immutable_snapshot(snapshot),
        ):
            os.link(authority, hardlink)

    hardlink.unlink()


# --- WI-5657: superseded predecessor VERIFIED handling ------------------------
#
# Governing specs: GOV-FILE-BRIDGE-AUTHORITY-001 (Mandatory VERIFIED
# Commit-Finalization Gate); DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001.
# A superseded predecessor VERIFIED (a first-line-VERIFIED versioned bridge file
# with a higher-numbered same-slug version STAGED in the same commit transaction)
# is non-authoritative history: excluded from the transaction VERIFIED-candidate
# count and from the terminal-VERIFIED finalization-evidence finding, while the
# single latest VERIFIED candidate keeps full validation and zero live candidates
# fail closed. Supersession is scoped to the staged transaction, never the ambient
# worktree, so an untracked/parked higher-numbered draft cannot false-positively
# supersede a genuine latest VERIFIED.


def _wi5657_write_bridge(root: Path, slug: str, version: int, status: str) -> str:
    bridge_dir = root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    rel = f"bridge/{slug}-{version:03d}.md"
    (root / rel).write_text(f"{status}\n\n# {slug} v{version:03d}\n", encoding="utf-8")
    return rel


def _wi5657_git_init_stage(root: Path, staged: list[str]) -> None:
    hooks = root / "empty-hooks"
    hooks.mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    (root / ".seed").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", ".seed"], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "seed",
        ],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "add", "--", *staged], cwd=root, check=True)


def _wi5657_snap(selected_paths: list[str]):
    return type("_Snap", (), {"selected_paths": list(selected_paths)})()


def test_wi5657_staged_higher_sibling_marks_superseded() -> None:
    module = _load_module()
    snap = _wi5657_snap(["bridge/slug-a-004.md", "bridge/slug-a-007.md"])
    assert module._superseded_versioned_bridge("bridge/slug-a-004.md", snap) is True
    assert module._superseded_versioned_bridge("bridge/slug-a-007.md", snap) is False


def test_wi5657_exact_slug_matching_prefix_sharing_not_sibling() -> None:
    module = _load_module()
    # `slug-a` and `slug-a-v2` are DIFFERENT numbered chains (distinct bridge_id).
    snap = _wi5657_snap(["bridge/slug-a-004.md", "bridge/slug-a-v2-001.md"])
    assert module._superseded_versioned_bridge("bridge/slug-a-004.md", snap) is False


def test_wi5657_non_versioned_or_none_snapshot_is_never_superseded() -> None:
    module = _load_module()
    snap = _wi5657_snap(["bridge/slug-a-007.md"])
    assert module._superseded_versioned_bridge("bridge/not-a-versioned-file.md", snap) is False
    assert module._superseded_versioned_bridge("scripts/foo.py", snap) is False
    # A None snapshot (non-transaction context) never marks anything superseded.
    assert module._superseded_versioned_bridge("bridge/slug-a-004.md", None) is False


def test_wi5657_untracked_worktree_higher_sibling_does_not_supersede_staged_latest(
    tmp_path: Path,
) -> None:
    # Regression guard (adversarial-review finding): an untracked/parked higher-numbered
    # same-slug file in the worktree must NOT mark a STAGED genuine latest VERIFIED as
    # superseded. Supersession is scoped to the staged transaction only.
    module = _load_module()
    slug = "gtkb-wi5657-untracked-guard"
    v6 = _wi5657_write_bridge(tmp_path, slug, 6, "VERIFIED")  # staged genuine latest
    _wi5657_git_init_stage(tmp_path, [v6])
    _wi5657_write_bridge(tmp_path, slug, 7, "NEW")  # untracked parked draft, NOT staged
    with module._index_snapshot(tmp_path) as snap:
        _evidence, errors, candidate_path = module._load_transaction_verified_evidence(tmp_path, [], snap)
    assert "found 2" not in " ".join(errors)
    # -006 is NOT superseded by the untracked -007; it remains the sole live candidate.
    assert candidate_path == v6


def test_wi5657_superseded_verified_yields_no_finalization_finding(
    tmp_path: Path,
) -> None:
    # Superseded predecessor (-004) with a higher STAGED sibling (-007) -> no finding.
    module = _load_module()
    v4 = _wi5657_write_bridge(tmp_path, "slug-b", 4, "VERIFIED")
    v7 = _wi5657_write_bridge(tmp_path, "slug-b", 7, "VERIFIED")
    _wi5657_git_init_stage(tmp_path, [v4, v7])
    with module._index_snapshot(tmp_path) as snap:
        assert module._verified_bridge_finalization_finding(tmp_path, v4, snap) is None
        # The latest (-007) is not superseded and lacks evidence -> finding still fires.
        finding = module._verified_bridge_finalization_finding(tmp_path, v7, snap)
    assert finding is not None
    assert "Commit Finalization Evidence" in finding["reason"]


def test_wi5657_non_superseded_terminal_verified_without_evidence_yields_finding(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _wi5657_write_bridge(tmp_path, "slug-c", 4, "VERIFIED")  # sole latest, lacks evidence
    finding = module._verified_bridge_finalization_finding(tmp_path, "bridge/slug-c-004.md", None)
    assert finding is not None
    assert "Commit Finalization Evidence" in finding["reason"]


def test_wi5657_superseded_plus_latest_yields_single_candidate_not_found_two(
    tmp_path: Path,
) -> None:
    # Case 1: -004 VERIFIED (superseded) + -005 NO-GO + -007 VERIFIED (latest), all staged.
    module = _load_module()
    slug = "gtkb-wi5657-fixture-case1"
    v4 = _wi5657_write_bridge(tmp_path, slug, 4, "VERIFIED")
    v5 = _wi5657_write_bridge(tmp_path, slug, 5, "NO-GO")
    v7 = _wi5657_write_bridge(tmp_path, slug, 7, "VERIFIED")
    _wi5657_git_init_stage(tmp_path, [v4, v5, v7])
    with module._index_snapshot(tmp_path) as snap:
        _evidence, errors, candidate_path = module._load_transaction_verified_evidence(tmp_path, [], snap)
    assert "found 2" not in " ".join(errors), f"superseded -004 must be excluded from candidate count: {errors}"
    assert candidate_path == v7


def test_wi5657_only_superseded_verified_with_latest_nogo_yields_zero_candidates(
    tmp_path: Path,
) -> None:
    # Case 3: -004 VERIFIED superseded by staged -005 NO-GO; no live VERIFIED candidate remains.
    module = _load_module()
    slug = "gtkb-wi5657-fixture-case3"
    v4 = _wi5657_write_bridge(tmp_path, slug, 4, "VERIFIED")
    v5 = _wi5657_write_bridge(tmp_path, slug, 5, "NO-GO")
    _wi5657_git_init_stage(tmp_path, [v4, v5])
    with module._index_snapshot(tmp_path) as snap:
        result = module._load_transaction_verified_evidence(tmp_path, [], snap)
    assert result == (None, [], None)


# --- WI-5658: protected-commit checker performance (hoist ls-tree; git timeout) -
#
# Governing specs: GOV-FILE-BRIDGE-AUTHORITY-001 (the commit-finalization gate must
# be fast enough to run as a pre-commit hook); DCL-VERIFIED-SPEC-DERIVED-TESTING-
# MANDATORY-001. The committed-bridge enumeration is hoisted out of the
# _load_verified_evidence per-packet loop (O(packets + files) instead of
# O(packets x files)), and every _run_git call is timeout-bounded and fails closed.


def test_wi5658_run_git_times_out_fails_closed(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "_git_command", lambda *a: ["git", *a])
    monkeypatch.setattr(module, "_sanitized_subprocess_env", lambda **k: {})

    def _raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["git"], timeout=kwargs.get("timeout"))

    monkeypatch.setattr(module.subprocess, "run", _raise_timeout)
    result = module._run_git(tmp_path, "ls-tree", "-r", "HEAD", text=True)
    # Fails closed (non-zero) with a timeout message instead of hanging or raising.
    assert result.returncode == 124
    assert "timed out" in result.stderr


def test_wi5658_committed_bridge_entries_by_id_groups_by_exact_slug(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _init_committed_paths(
        tmp_path,
        [
            "bridge/slug-a-001.md",
            "bridge/slug-a-002.md",
            "bridge/slug-a-v2-001.md",
            "bridge/slug-b-001.md",
            "bridge/not-a-versioned-file.md",
        ],
    )
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    grouped = module._committed_bridge_entries_by_id(tmp_path, head)
    assert {e.rel_path for e in grouped.get("slug-a", ())} == {
        "bridge/slug-a-001.md",
        "bridge/slug-a-002.md",
    }
    # Exact-slug: slug-a-v2 is a DIFFERENT chain, not folded into slug-a.
    assert {e.rel_path for e in grouped.get("slug-a-v2", ())} == {"bridge/slug-a-v2-001.md"}
    assert {e.rel_path for e in grouped.get("slug-b", ())} == {"bridge/slug-b-001.md"}
    # Non-versioned bridge files are excluded.
    assert all("not-a-versioned-file" not in e.rel_path for entries in grouped.values() for e in entries)


def test_wi5658_load_verified_evidence_enumerates_committed_bridge_once(monkeypatch, tmp_path: Path) -> None:
    # Core perf property: for N packets, the committed bridge tree is enumerated via
    # ls-tree exactly ONCE (not once per packet, which was the O(packets x files) hang).
    module = _load_module()
    _init_committed_paths(tmp_path, ["bridge/seed-001.md"])
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    pkt_dir = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    pkt_dir.mkdir(parents=True, exist_ok=True)
    for i in range(5):
        (pkt_dir / f"slug-{i}.json").write_text(json.dumps({"bridge_id": f"slug-{i}"}), encoding="utf-8")

    ls_tree_calls = {"n": 0}
    real_run_git = module._run_git

    def _counting_run_git(root, *args, **kwargs):
        if args and args[0] == "ls-tree":
            ls_tree_calls["n"] += 1
        return real_run_git(root, *args, **kwargs)

    monkeypatch.setattr(module, "_run_git", _counting_run_git)
    module._load_verified_evidence(tmp_path, head_oid=head)
    assert ls_tree_calls["n"] == 1, (
        f"committed bridge tree must be enumerated once, not per-packet; got {ls_tree_calls['n']}"
    )


# --- WI-5659: pre-filter verified-evidence to staged protected paths ----------
#
# Governing specs: GOV-FILE-BRIDGE-AUTHORITY-001 (the commit-finalization gate
# must be fast enough to run as a pre-commit hook) and
# DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001. _load_verified_evidence skips
# the expensive _bridge_snapshot + resolve_bridge_lifecycle for packets whose
# stored target_path_globs authorize NONE of the staged protected paths. By the
# _packet_binding_errors invariant (a packet counts as evidence only when its
# stored target_path_globs == the resolver-approved chain.target_paths, and
# _verified_authorization matches those exact globs) and because verified_errors
# are only diagnostic context on already-failing paths, the pre-filter cannot
# change any cleared/finding authorization outcome; it only avoids resolving
# irrelevant packets (~471 -> typically 1-3, collapsing the 460.8s hang).


class _Wi5659RaisingSnapshot:
    """Stand-in for _bridge_snapshot that records the bridge_id reaching the
    expensive resolution path, then fails closed so the packet lands in errors
    (never evidence). Proves ONLY relevant packets are expensively resolved."""

    def __init__(self, reached: list[str], bridge_id: str, exc: Exception) -> None:
        self._reached = reached
        self._bridge_id = bridge_id
        self._exc = exc

    def __enter__(self):
        self._reached.append(self._bridge_id)
        raise self._exc

    def __exit__(self, *exc_info) -> bool:
        return False


def _wi5659_write_packet(root: Path, bridge_id: str, globs: list[str]) -> None:
    pkt_dir = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    pkt_dir.mkdir(parents=True, exist_ok=True)
    (pkt_dir / f"{bridge_id}.json").write_text(
        json.dumps({"bridge_id": bridge_id, "target_path_globs": list(globs)}),
        encoding="utf-8",
    )


def _wi5659_head(root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _wi5659_spy_snapshot(module, monkeypatch: pytest.MonkeyPatch, reached: list[str]) -> None:
    monkeypatch.setattr(
        module,
        "_bridge_snapshot",
        lambda root, bridge_id, *a, **k: _Wi5659RaisingSnapshot(reached, bridge_id, module.GateError("wi5659-spy")),
    )


def test_wi5659_prefilter_resolves_only_matching_packets(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["bridge/seed-001.md"])
    head = _wi5659_head(tmp_path)
    # Exact-match globs so relevance does not depend on wildcard semantics; the
    # pre-filter reuses the same path_authorized predicate as authorization.
    _wi5659_write_packet(tmp_path, "rel-exact", ["scripts/target.py"])
    _wi5659_write_packet(tmp_path, "rel-multi", ["scripts/unrelated.py", "scripts/target.py"])
    _wi5659_write_packet(tmp_path, "irr-exact", ["scripts/other.py"])
    _wi5659_write_packet(tmp_path, "irr-docs", ["docs/readme.md"])
    _wi5659_write_packet(tmp_path, "irr-noglobs", [])
    reached: list[str] = []
    _wi5659_spy_snapshot(module, monkeypatch, reached)

    evidence, errors, count = module._load_verified_evidence(
        tmp_path, head_oid=head, protected_paths=["scripts/target.py"]
    )

    # Only packets whose stored globs authorize the staged path are resolved.
    assert set(reached) == {"rel-exact", "rel-multi"}
    # terminal_verified_packets_scanned stays TOTAL (evidence_summary honesty).
    assert count == 5
    # Both resolved packets hit the fail-closed spy -> errors, never evidence.
    assert evidence == []
    assert len(errors) == 2


def test_wi5659_prefilter_none_is_full_scan(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["bridge/seed-001.md"])
    head = _wi5659_head(tmp_path)
    for bid, globs in (
        ("a", ["scripts/a.py"]),
        ("b", ["docs/b.md"]),
        ("c", ["x/c.py"]),
    ):
        _wi5659_write_packet(tmp_path, bid, globs)
    reached: list[str] = []
    _wi5659_spy_snapshot(module, monkeypatch, reached)

    # protected_paths=None preserves legacy full-scan behavior: every packet is
    # expensively resolved (backward compatibility for callers that omit it).
    _evidence, _errors, count = module._load_verified_evidence(tmp_path, head_oid=head, protected_paths=None)

    assert set(reached) == {"a", "b", "c"}
    assert count == 3


def test_wi5659_prefilter_preserves_authorization_outcome() -> None:
    # Algebraic property backing the safety claim (NOT the end-to-end proof; see
    # test_wi5659_prefilter_integrated_real_chain_equivalence for real resolution).
    # Filtering an evidence list down to the entries that authorize a staged
    # protected path preserves _verified_authorization's per-path cleared decision
    # AND its source, because every authorizing entry survives the filter in its
    # original order. This isolates WHY the production pre-filter (which drops
    # exactly the non-authorizing packets) cannot change any authorization outcome.
    module = _load_module()
    full_evidence = [
        ("t-target", ["scripts/target.py"]),
        ("t-multi", ["scripts/x.py", "scripts/target.py"]),
        ("t-other", ["docs/readme.md"]),
        ("t-unrelated", ["other/thing.py"]),
    ]
    staged_protected = ["scripts/target.py", "scripts/nope.py"]
    pre_evidence = [
        entry
        for entry in full_evidence
        if any(module.path_authorized({"target_path_globs": entry[1]}, rel) for rel in staged_protected)
    ]
    # Only the two entries authorizing scripts/target.py survive the pre-filter.
    assert {entry[0] for entry in pre_evidence} == {"t-target", "t-multi"}
    for rel in staged_protected:
        full_res = module._verified_authorization(full_evidence, [], rel)
        pre_res = module._verified_authorization(pre_evidence, [], rel)
        assert (full_res[0], full_res[1]) == (pre_res[0], pre_res[1]), f"authorization outcome differs for {rel}"
    # Non-trivial: one staged path is authorized, the other is not.
    assert module._verified_authorization(pre_evidence, [], "scripts/target.py")[0] is True
    assert module._verified_authorization(pre_evidence, [], "scripts/nope.py")[0] is False


def test_wi5659_prefilter_scales_past_pre_commit_budget(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    import time

    module = _load_module()
    _init_committed_paths(tmp_path, ["bridge/seed-001.md"])
    head = _wi5659_head(tmp_path)
    # ~450 irrelevant packets + 1 relevant, mirroring the ~471-packet prod load
    # that made the full scan take 460.8s.
    for index in range(450):
        _wi5659_write_packet(tmp_path, f"irr-{index:03d}", [f"other/mod-{index}.py"])
    _wi5659_write_packet(tmp_path, "relevant", ["scripts/target.py"])
    reached: list[str] = []
    _wi5659_spy_snapshot(module, monkeypatch, reached)

    start = time.perf_counter()
    _evidence, _errors, count = module._load_verified_evidence(
        tmp_path, head_oid=head, protected_paths=["scripts/target.py"]
    )
    elapsed = time.perf_counter() - start

    # Deterministic proof of the perf mechanism: only the 1 relevant packet is
    # expensively resolved; the other 450 are skipped by the cheap pre-filter.
    assert reached == ["relevant"]
    assert count == 451
    # Loose wall-clock guard: skipping 450 packets keeps the scan far under budget.
    assert elapsed < 20.0, f"pre-filter scan took {elapsed:.2f}s"


def test_wi5659_prefilter_integrated_real_chain_equivalence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # End-to-end proof (real resolution, NOT mocked) that the pre-filter is
    # outcome-preserving. A genuine committed VERIFIED chain resolves to real
    # evidence via _bridge_snapshot + resolve_bridge_lifecycle + the
    # _packet_binding_errors invariant (packet.target_path_globs ==
    # chain.target_paths). The pre-filter must (a) return byte-identical evidence
    # when a staged protected path matches the chain, and (b) skip the chain
    # entirely (no evidence) when no staged path matches -- while the scanned count
    # stays total in both cases. This is the test the adversarial-review lens
    # flagged as missing; it exercises the binding invariant the safety rests on.
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture verified chain",
        ],
        cwd=tmp_path,
        check=True,
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    # Baseline full scan: the committed chain resolves to REAL VERIFIED evidence.
    ev_full, err_full, count_full = module._load_verified_evidence(tmp_path, head_oid=head)
    assert count_full == 1
    assert err_full == []
    assert ev_full, "committed VERIFIED chain must resolve to evidence in the full scan"
    a_target = selected_paths[0]  # a path the chain's proposal (and packet globs) authorize
    assert any(a_target in globs for _bid, globs in ev_full)

    # (a) Staged protected path MATCHES the chain -> byte-identical real evidence.
    ev_match, err_match, count_match = module._load_verified_evidence(
        tmp_path, head_oid=head, protected_paths=[a_target]
    )
    assert ev_match == ev_full
    assert err_match == err_full
    assert count_match == 1  # terminal_verified_packets_scanned stays total

    # (b) No staged protected path matches -> chain skipped, no evidence, count total.
    ev_none, _err_none, count_none = module._load_verified_evidence(
        tmp_path, head_oid=head, protected_paths=["totally/unrelated-xyz.py"]
    )
    assert ev_none == []
    assert count_none == 1


# --- WI-5659 mechanism 2: batch prospective-tree materialization --------------
#
# Governing specs: GOV-FILE-BRIDGE-AUTHORITY-001 (the commit-finalization gate
# must complete as a pre-commit hook); DCL-VERIFIED-SPEC-DERIVED-TESTING-
# MANDATORY-001. Authorized by DELIB-202667185 (PAUTH v2). `_materialize_entries`
# streams every blob through ONE `git cat-file --batch` process instead of two
# subprocess spawns per entry. This changes only HOW blobs are fetched: the tree
# stays index-complete and every per-blob verification, size limit, and ledger
# field is preserved. Fail-closed behavior is asserted explicitly below because a
# batch stream has failure modes (missing/ambiguous objects, short reads,
# malformed record terminators) the per-entry path did not.


class _FakeBatchProcess:
    """Minimal stand-in for a `git cat-file --batch` Popen handle."""

    def __init__(self, payload: bytes) -> None:
        self.stdin = io.BytesIO()
        self.stdout = io.BytesIO(payload)
        self.stderr = io.BytesIO(b"")
        self.returncode = 0

    def poll(self):
        return 0

    def kill(self) -> None:
        return None

    def communicate(self, timeout=None):
        return (b"", b"")


def _wi5659_single_entry(module, tmp_path: Path):
    """Commit one file and return (snapshot-context-manager factory, entry)."""
    _init_committed_paths(tmp_path, ["only.txt"])
    return module


def test_wi5659_batch_ledger_matches_per_entry_reference(tmp_path: Path) -> None:
    # Ledger equivalence: the batch path must produce the same content-derived
    # ledger fields (mode/sha256/size) AND the same materialized bytes as the
    # retained per-entry reference implementation `_blob_ledger_entry`.
    # device/inode/link_count are per-file identity of two distinct trees, so
    # they are intentionally not compared.
    module = _load_module()
    _init_committed_paths(tmp_path, ["a.txt", "sub/b.txt", "sub/deep/c.bin"])
    batch_root = tmp_path / "batch-tree"
    ref_root = tmp_path / "ref-tree"
    batch_root.mkdir()
    ref_root.mkdir()

    with module._index_snapshot(tmp_path) as snap:
        entries = module._index_entries(tmp_path, snap)
        batch = module._materialize_entries(
            tmp_path,
            batch_root,
            entries,
            env=snap.env,
            object_format=snap.object_format,
        )
        reference: dict[str, object] = {}
        for entry in entries:
            destination = ref_root / entry.rel_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            reference[entry.rel_path] = module._blob_ledger_entry(
                tmp_path,
                destination,
                entry,
                env=snap.env,
                object_format=snap.object_format,
            )

    assert set(batch) == set(reference)
    assert batch, "fixture must materialize at least one entry"
    for rel_path, ref_entry in reference.items():
        got = batch[rel_path]
        assert (got.mode, got.sha256, got.size) == (
            ref_entry.mode,
            ref_entry.sha256,
            ref_entry.size,
        ), rel_path
        # Materialized bytes are byte-identical between the two paths.
        assert (batch_root / rel_path).read_bytes() == (ref_root / rel_path).read_bytes(), rel_path


def test_wi5659_batch_uses_one_process_for_all_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Deterministic proof of the perf mechanism: N entries cost ONE cat-file
    # process, not 2N spawns (the 159.4 ms/entry -> ~1 ms/entry change).
    module = _load_module()
    paths = [f"f{index}.txt" for index in range(12)]
    _init_committed_paths(tmp_path, paths)
    out_root = tmp_path / "tree"
    out_root.mkdir()

    spawns = {"n": 0}
    real_popen = subprocess.Popen

    def counting_popen(*args, **kwargs):
        spawns["n"] += 1
        return real_popen(*args, **kwargs)

    with module._index_snapshot(tmp_path) as snap:
        entries = module._index_entries(tmp_path, snap)
        monkeypatch.setattr(module.subprocess, "Popen", counting_popen)
        ledger = module._materialize_entries(
            tmp_path, out_root, entries, env=snap.env, object_format=snap.object_format
        )

    assert len(ledger) == len(entries) >= 12
    assert spawns["n"] == 1, f"batch materialization must spawn exactly one cat-file process; got {spawns['n']}"


def _wi5659_run_batch_with_payload(module, tmp_path: Path, monkeypatch, payload: bytes):
    """Materialize a one-entry index against a faked batch stream."""
    out_root = tmp_path / "tree"
    out_root.mkdir(exist_ok=True)
    with module._index_snapshot(tmp_path) as snap:
        entries = module._index_entries(tmp_path, snap)
        monkeypatch.setattr(module.subprocess, "Popen", lambda *a, **k: _FakeBatchProcess(payload))
        return module._materialize_entries(tmp_path, out_root, entries, env=snap.env, object_format=snap.object_format)


def test_wi5659_batch_missing_object_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # `<oid> missing` (and `<oid> ambiguous`) are 2-field headers -> GateError.
    module = _load_module()
    _init_committed_paths(tmp_path, ["only.txt"])
    with module._index_snapshot(tmp_path) as snap:
        oid = module._index_entries(tmp_path, snap)[0].oid
    with pytest.raises(module.GateError, match="could not read raw index blob"):
        _wi5659_run_batch_with_payload(module, tmp_path, monkeypatch, f"{oid} missing\n".encode("ascii"))


def test_wi5659_batch_hash_mismatch_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Defense in depth: content that does not hash to the indexed object id must
    # fail closed even though a real content-addressed git could not produce it.
    module = _load_module()
    _init_committed_paths(tmp_path, ["only.txt"])
    with module._index_snapshot(tmp_path) as snap:
        oid = module._index_entries(tmp_path, snap)[0].oid
    tampered = b"tampered-bytes"
    payload = f"{oid} blob {len(tampered)}\n".encode("ascii") + tampered + b"\n"
    with pytest.raises(module.GateError, match="do not hash to indexed object id"):
        _wi5659_run_batch_with_payload(module, tmp_path, monkeypatch, payload)


def test_wi5659_batch_malformed_terminator_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # A record whose trailing newline is missing must not be silently accepted.
    module = _load_module()
    _init_committed_paths(tmp_path, ["only.txt"])
    with module._index_snapshot(tmp_path) as snap:
        entry = module._index_entries(tmp_path, snap)[0]
    content = (tmp_path / entry.rel_path).read_bytes()
    payload = f"{entry.oid} blob {len(content)}\n".encode("ascii") + content  # no trailing b"\n"
    with pytest.raises(module.GateError, match="malformed batch record terminator"):
        _wi5659_run_batch_with_payload(module, tmp_path, monkeypatch, payload)


def test_wi5659_batch_exempts_oversized_blob_and_enforces_tree_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # In-ledger mechanism 3: an oversized blob is exempted (in-ledger, absent from
    # disk), not fatal. MAX_TREE_BYTES is still enforced for MATERIALIZED
    # (non-exempt) blobs, whose written bytes are what consume the budget.
    module = _load_module()
    _init_committed_paths(tmp_path, ["a.txt", "b.txt"])

    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 2)  # every fixture blob is oversized
    out_root = tmp_path / "tree-blob"
    out_root.mkdir()
    with module._index_snapshot(tmp_path) as snap:
        entries = module._index_entries(tmp_path, snap)
        ledger = module._materialize_entries(
            tmp_path, out_root, entries, env=snap.env, object_format=snap.object_format
        )
    assert ledger and all(e.content_exempt for e in ledger.values())
    assert set(ledger) == {e.rel_path for e in entries}
    assert not any((out_root / rel).exists() for rel in ledger)

    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 64 * 1024 * 1024)
    monkeypatch.setattr(module, "MAX_TREE_BYTES", 3)
    out_root2 = tmp_path / "tree-total"
    out_root2.mkdir()
    with module._index_snapshot(tmp_path) as snap:
        entries = module._index_entries(tmp_path, snap)
        with pytest.raises(module.GateError, match="prospective tree exceeds"):
            module._materialize_entries(
                tmp_path,
                out_root2,
                entries,
                env=snap.env,
                object_format=snap.object_format,
            )


# --- WI-5659 mechanism 3 (in-ledger) + mechanism 4: ledger exemption + scope ---
#
# Authorized by DELIB-202667186 / DELIB-202667188 (mechanism 3, in-ledger) and
# DELIB-202667187 (mechanism 4). Oversized blobs are recorded IN the ledger with
# content_exempt=True and their mode/oid/declared size, are hash-verified while
# streaming, are NOT written to disk, and do NOT consume MAX_TREE_BYTES.
# _verify_snapshot_ledger compares the on-disk file set to the NON-exempt ledger
# keys, asserts exempt entries are absent from disk, and (mechanism 4) verifies
# tracked .gtkb-state/* files while ignoring only runtime audit scratch (never in
# the ledger).


def _wi5659_grow_and_commit(tmp_path: Path, rel: str, nbytes: int) -> None:
    (tmp_path / rel).write_bytes(b"x" * nbytes)
    subprocess.run(["git", "add", "--", rel], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            f"grow {rel}",
        ],
        cwd=tmp_path,
        check=True,
    )


def _wi5659_materialize_all(module, tmp_path: Path, out_root: Path):
    with module._index_snapshot(tmp_path) as snap:
        entries = module._index_entries(tmp_path, snap)
        return module._materialize_entries(tmp_path, out_root, entries, env=snap.env, object_format=snap.object_format)


def test_wi5659_exempt_entry_recorded_in_ledger_absent_from_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["big.txt", "small.txt"])
    _wi5659_grow_and_commit(tmp_path, "big.txt", 4096)
    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 1024)  # big.txt exempt, small.txt not
    out_root = tmp_path / "tree"
    out_root.mkdir()
    ledger = _wi5659_materialize_all(module, tmp_path, out_root)

    assert ledger["big.txt"].content_exempt is True
    assert ledger["big.txt"].oid and ledger["big.txt"].size > 1024
    assert ledger["small.txt"].content_exempt is False
    assert not (out_root / "big.txt").exists()
    assert (out_root / "small.txt").is_file()
    # Enumeration completeness is provable from the ledger alone.
    assert set(ledger) == {"big.txt", "small.txt"}
    # The exemption-aware verifier passes with no false drift.
    module._verify_snapshot_ledger(module._BridgeSnapshot(root=out_root, ledger=ledger))


def test_wi5659_exempt_blob_streaming_hash_mismatch_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["only.txt"])
    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 2)
    with module._index_snapshot(tmp_path) as snap:
        oid = module._index_entries(tmp_path, snap)[0].oid
    tampered = b"tampered-oversized-bytes"
    payload = f"{oid} blob {len(tampered)}\n".encode("ascii") + tampered + b"\n"
    with pytest.raises(module.GateError, match="do not hash to indexed object id"):
        _wi5659_run_batch_with_payload(module, tmp_path, monkeypatch, payload)


def test_wi5659_content_file_at_exempt_path_is_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["big.txt"])
    _wi5659_grow_and_commit(tmp_path, "big.txt", 4096)
    monkeypatch.setattr(module, "MAX_BLOB_BYTES", 1024)
    out_root = tmp_path / "tree"
    out_root.mkdir()
    ledger = _wi5659_materialize_all(module, tmp_path, out_root)
    assert ledger["big.txt"].content_exempt is True
    # Planting a content file at the exempt path must fail closed.
    (out_root / "big.txt").write_bytes(b"smuggled")
    with pytest.raises(module.GateError, match="must not exist on disk|file set drifted"):
        module._verify_snapshot_ledger(module._BridgeSnapshot(root=out_root, ledger=ledger))


def test_wi5659_tracked_gtkb_state_files_are_verified_not_skipped(
    tmp_path: Path,
) -> None:
    module = _load_module()
    tracked_state = ".gtkb-state/tracked-evidence.json"
    _init_committed_paths(tmp_path, [tracked_state, "normal.txt"])
    out_root = tmp_path / "tree"
    out_root.mkdir()
    ledger = _wi5659_materialize_all(module, tmp_path, out_root)
    assert tracked_state in ledger and not ledger[tracked_state].content_exempt
    assert (out_root / tracked_state).is_file()
    module._verify_snapshot_ledger(module._BridgeSnapshot(root=out_root, ledger=ledger))


def test_wi5659_audit_scratch_subtree_is_still_ignored(tmp_path: Path) -> None:
    module = _load_module()
    _init_committed_paths(tmp_path, ["normal.txt"])
    out_root = tmp_path / "tree"
    out_root.mkdir()
    ledger = _wi5659_materialize_all(module, tmp_path, out_root)
    scratch = out_root / ".gtkb-state" / "compliance-audit" / "audit-xyz"
    scratch.mkdir(parents=True)
    (scratch / "audit.json").write_text('{"decision": "pass"}', encoding="utf-8")
    # Non-ledger .gtkb-state content is ignored, not reported as drift.
    module._verify_snapshot_ledger(module._BridgeSnapshot(root=out_root, ledger=ledger))


def test_wi5659_unexpected_gtkb_state_file_outside_scratch_is_drift(
    tmp_path: Path,
) -> None:
    # LO verdict -021 P1: mechanism 4 must NOT ignore every non-ledger `.gtkb-state/`
    # path. An unexpected untracked file outside the authorized compliance-audit
    # scratch boundary must still be caught as file-set drift.
    module = _load_module()
    _init_committed_paths(tmp_path, ["normal.txt"])
    out_root = tmp_path / "tree"
    out_root.mkdir()
    ledger = _wi5659_materialize_all(module, tmp_path, out_root)
    sneaky = out_root / ".gtkb-state" / "unexpected-subtree" / "sneaky.txt"
    sneaky.parent.mkdir(parents=True)
    sneaky.write_text("sneaky", encoding="utf-8")
    with pytest.raises(module.GateError, match="file set drifted"):
        module._verify_snapshot_ledger(module._BridgeSnapshot(root=out_root, ledger=ledger))


def test_wi5659_tampering_with_tracked_gtkb_state_file_is_detected(
    tmp_path: Path,
) -> None:
    module = _load_module()
    tracked_state = ".gtkb-state/tracked-evidence.json"
    _init_committed_paths(tmp_path, [tracked_state])
    out_root = tmp_path / "tree"
    out_root.mkdir()
    ledger = _wi5659_materialize_all(module, tmp_path, out_root)
    (out_root / tracked_state).write_text("tampered payload", encoding="utf-8")
    with pytest.raises(module.GateError):
        module._verify_snapshot_ledger(module._BridgeSnapshot(root=out_root, ledger=ledger))


def test_registry_commit_accepts_coherent_journal_bound_member(tmp_path: Path) -> None:
    module = _load_module()
    _seed_registered_commit_fixture(tmp_path)

    assert module._registry_commit_findings(tmp_path, ["registered.txt"], None) == []


def test_registry_commit_reports_stale_registered_content_without_blocking(
    tmp_path: Path,
) -> None:
    module = _load_module()
    member = _seed_registered_commit_fixture(tmp_path)
    member.write_text("changed without observation\n", encoding="utf-8")

    findings, audit_gaps = module._registry_commit_assessment(tmp_path, ["registered.txt"], None)

    assert findings == []
    assert any(gap["path"] == "registered.txt" for gap in audit_gaps)


def test_registry_commit_blocks_incomplete_journal(tmp_path: Path) -> None:
    module = _load_module()
    _seed_registered_commit_fixture(tmp_path)
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE sot_registry_transaction_journal SET journal_state = 'prepared' "
            "WHERE operation = 'legacy_bootstrap'"
        )
        conn.commit()
    finally:
        conn.close()

    findings = module._registry_commit_findings(tmp_path, ["registered.txt"], None)

    assert len(findings) == 1
    assert "coherent registry authority unavailable" in findings[0]["reason"]
    assert "prepared" in findings[0]["reason"]


def test_registry_commit_blocks_registered_identity_change(tmp_path: Path) -> None:
    module = _load_module()
    _seed_registered_commit_fixture(tmp_path)
    snapshot = SimpleNamespace(status_by_path={"registered.txt": "D"})

    findings = module._registry_commit_findings(tmp_path, ["registered.txt"], snapshot)

    assert findings == [
        {
            "path": "registered.txt",
            "reason": "registered identity delete/move/rename requires separately authorized transition",
        }
    ]


@pytest.mark.parametrize("status", ["A", "M", "C-source", "C-destination", "R-source", "R-destination"])
def test_registry_commit_rejects_transient_index_recurrence(
    tmp_path: Path,
    status: str,
) -> None:
    module = _load_module()
    _seed_registered_commit_fixture(tmp_path)
    transient = ".gtkb-index-hl705ij2/index"
    snapshot = SimpleNamespace(status_by_path={transient: status})

    findings = module._registry_commit_findings(tmp_path, [transient], snapshot)

    assert findings == [
        {
            "path": transient,
            "reason": "transient Git index recurrence is forbidden; only an unregistered deletion is allowed",
        }
    ]


def test_registry_commit_allows_only_coherently_unregistered_transient_deletion(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _seed_registered_commit_fixture(tmp_path)
    transient = ".gtkb-index-hl705ij2/index"
    snapshot = SimpleNamespace(status_by_path={transient: "D"})

    assert module._registry_commit_findings(tmp_path, [transient], snapshot) == []


def test_registry_commit_blocks_registered_transient_deletion(tmp_path: Path) -> None:
    module = _load_module()
    transient = ".gtkb-index-hl705ij2/index"
    _seed_registered_commit_fixture(tmp_path, transient)
    snapshot = SimpleNamespace(status_by_path={transient: "D"})

    findings = module._registry_commit_findings(tmp_path, [transient], snapshot)

    assert findings == [
        {
            "path": transient,
            "reason": "registered identity delete/move/rename requires separately authorized transition",
        }
    ]


def test_registry_commit_blocks_transient_deletion_without_registry_authority(
    tmp_path: Path,
) -> None:
    module = _load_module()
    transient = ".gtkb-index-hl705ij2/index"
    snapshot = SimpleNamespace(status_by_path={transient: "D"})

    findings = module._registry_commit_findings(tmp_path, [transient], snapshot)

    assert findings == [
        {
            "path": transient,
            "reason": "transient Git index deletion requires coherent registry authority",
        }
    ]


def test_staged_transient_add_and_unregistered_delete_follow_recurrence_rule(
    tmp_path: Path,
) -> None:
    module = _load_module()
    transient = ".gtkb-index-hl705ij2/index"
    _init_committed_paths(tmp_path, ["baseline.txt"])
    _seed_registered_commit_fixture(tmp_path)
    target = tmp_path / transient
    target.parent.mkdir(parents=True)
    target.write_text("transient\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", transient], cwd=tmp_path, check=True)

    with module._index_snapshot(tmp_path) as snapshot:
        assert snapshot.status_by_path[transient] == "A"
        assert module._registry_commit_findings(tmp_path, [transient], snapshot)

    subprocess.run(
        ["git", "reset", "--hard", "HEAD"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    target.parent.mkdir(parents=True)
    target.write_text("transient\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", transient], cwd=tmp_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            "core.hooksPath=empty-hooks",
            "commit",
            "-qm",
            "transient fixture",
        ],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(["git", "rm", "-q", "--", transient], cwd=tmp_path, check=True)

    with module._index_snapshot(tmp_path) as snapshot:
        assert snapshot.status_by_path[transient] == "D"
        assert module._registry_commit_findings(tmp_path, [transient], snapshot) == []


def test_registry_commit_rejects_mismatched_capability_start_packet(
    tmp_path: Path,
) -> None:
    module = _load_module()
    member = _seed_registered_commit_fixture(tmp_path)
    capability = mint_observation_capability(
        target_paths=["registered.txt"],
        session_id="pb-session",
        tool_event_id="event-1",
        bridge_id="gtkb-wi5441-registry-control-plane-reverse-coverage",
        start_packet_hash="sha256:packet",
        pauth_decision={"allowed": True},
        operation="Edit",
        authorized=True,
        project_root=tmp_path,
    )
    member.write_text("observed change\n", encoding="utf-8")
    consume_observation_capability(
        capability=capability["capability"],
        target_paths=["registered.txt"],
        preimage_digests=capability["preimage_digests"],
        session_id="pb-session",
        tool_event_id="event-1",
        bridge_id="gtkb-wi5441-registry-control-plane-reverse-coverage",
        start_packet_hash="sha256:packet",
        operation="Edit",
        tool_succeeded=True,
        tool_result={"ok": True},
        changed_by="test/prime-builder",
        change_reason="WI-5441 observation",
        project_root=tmp_path,
    )
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE sot_registry_observation_capabilities SET start_packet_hash = 'sha256:mismatch' "
            "WHERE tool_event_id = 'event-1'"
        )
        conn.commit()
    finally:
        conn.close()

    findings, audit_gaps = module._registry_commit_assessment(tmp_path, ["registered.txt"], None)

    assert findings == []
    assert any("lacks automatic observation" in gap["reason"] for gap in audit_gaps)


def _staged_registry_findings(module, root: Path, rel_paths: list[str]) -> list[dict[str, object]]:
    with module._index_snapshot(root) as snapshot:
        return module._registry_commit_findings(root, rel_paths, snapshot)


def test_registry_commit_accepts_consumed_bridge_publication_after_mint_ttl(
    tmp_path: Path,
) -> None:
    module = _load_module()
    rel_path = "bridge/gtkb-publication-fixture-001.md"
    _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])

    assert _staged_registry_findings(module, tmp_path, [rel_path]) == []


def test_registry_commit_accepts_twelve_exact_bridge_publication_predecessors(
    tmp_path: Path,
) -> None:
    module = _load_module()
    rel_paths = [f"bridge/gtkb-publication-chain-{version:03d}.md" for version in range(1, 13)]
    _seed_bridge_publication_commit_fixture(tmp_path, rel_paths)

    assert _staged_registry_findings(module, tmp_path, rel_paths) == []


def test_newest_aggregate_revision_cannot_authorize_predecessor_without_exact_capability(
    tmp_path: Path,
) -> None:
    module = _load_module()
    rel_paths = [
        "bridge/gtkb-publication-predecessor-001.md",
        "bridge/gtkb-publication-predecessor-002.md",
    ]
    capability_hashes = _seed_bridge_publication_commit_fixture(tmp_path, rel_paths)
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "DELETE FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (capability_hashes[rel_paths[0]],),
        )
        conn.commit()
    finally:
        conn.close()

    findings = _staged_registry_findings(module, tmp_path, rel_paths)

    assert findings == [
        {
            "path": rel_paths[0],
            "reason": "registered bridge path lacks exact publication capability evidence",
        }
    ]


@pytest.mark.parametrize("mutation", ["missing", "minted", "expired", "compensated", "failed"])
def test_registry_commit_rejects_nonterminal_bridge_publication_attempts(
    tmp_path: Path,
    mutation: str,
) -> None:
    module = _load_module()
    rel_path = "bridge/gtkb-publication-state-001.md"
    capability_hash = _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])[rel_path]
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        if mutation == "missing":
            conn.execute(
                "DELETE FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
                (capability_hash,),
            )
        elif mutation in {"minted", "expired"}:
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities SET capability_state = ? "
                "WHERE capability_hash = ?",
                (mutation, capability_hash),
            )
        elif mutation == "compensated":
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities "
                "SET capability_state = 'compensated', compensation_revision_id = 'compensation-revision', "
                "compensation_digest = ?, failure_reason = 'rolled back' WHERE capability_hash = ?",
                (_sha256(b"compensated"), capability_hash),
            )
        else:
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities SET failure_reason = 'publication failed' "
                "WHERE capability_hash = ?",
                (capability_hash,),
            )
        conn.commit()
    finally:
        conn.close()

    findings = _staged_registry_findings(module, tmp_path, [rel_path])

    assert len(findings) == 1
    assert findings[0]["path"] == rel_path
    if mutation == "missing":
        assert findings[0]["reason"] == "registered bridge path lacks exact publication capability evidence"
    else:
        assert "publication" in str(findings[0]["reason"])


@pytest.mark.parametrize(
    "mutation",
    [
        "target_path",
        "aggregate_entry_id",
        "capability_hash",
        "revision_id",
        "bridge_id",
        "content_digest",
    ],
)
def test_registry_commit_rejects_bridge_publication_binding_mismatch(
    tmp_path: Path,
    mutation: str,
) -> None:
    module = _load_module()
    rel_path = "bridge/gtkb-publication-binding-001.md"
    capability_hash = _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])[rel_path]
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.row_factory = sqlite3.Row
    try:
        capability = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (capability_hash,),
        ).fetchone()
        assert capability is not None
        if mutation == "target_path":
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities SET target_path = ? WHERE capability_hash = ?",
                ("bridge/gtkb-other-binding-001.md", capability_hash),
            )
        elif mutation == "aggregate_entry_id":
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities SET aggregate_entry_id = 'other-entry' "
                "WHERE capability_hash = ?",
                (capability_hash,),
            )
        elif mutation == "capability_hash":
            conn.execute(
                "UPDATE sot_artifact_revisions SET capability_hash = ? WHERE revision_id = ?",
                (_sha256(b"wrong capability"), capability["revision_id"]),
            )
        elif mutation == "revision_id":
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities SET revision_id = 'missing-revision' "
                "WHERE capability_hash = ?",
                (capability_hash,),
            )
        elif mutation == "bridge_id":
            conn.execute(
                "UPDATE sot_artifact_revisions SET bridge_id = 'gtkb-other-binding' WHERE revision_id = ?",
                (capability["revision_id"],),
            )
        else:
            conn.execute(
                "UPDATE sot_registry_bridge_publication_capabilities SET content_digest = ? WHERE capability_hash = ?",
                (_sha256(b"wrong content"), capability_hash),
            )
        conn.commit()
    finally:
        conn.close()

    findings = _staged_registry_findings(module, tmp_path, [rel_path])

    assert len(findings) == 1
    assert findings[0]["path"] == rel_path


def test_registry_commit_uses_newest_bridge_publication_attempt_before_filtering(
    tmp_path: Path,
) -> None:
    module = _load_module()
    rel_path = "bridge/gtkb-publication-retry-001.md"
    original_hash = _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])[rel_path]
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.row_factory = sqlite3.Row
    try:
        original = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (original_hash,),
        ).fetchone()
        assert original is not None
        columns = [
            column[1] for column in conn.execute("PRAGMA table_info(sot_registry_bridge_publication_capabilities)")
        ]
        columns.remove("rowid")
        newer = {column: original[column] for column in columns}
        newer.update(
            {
                "capability_hash": _sha256(b"newer compensated attempt"),
                "capability_state": "compensated",
                "compensation_revision_id": "compensation-revision",
                "compensation_digest": _sha256(b"compensation"),
                "failure_reason": "newer attempt rolled back",
            }
        )
        conn.execute(
            f"INSERT INTO sot_registry_bridge_publication_capabilities ({', '.join(columns)}) "
            f"VALUES ({', '.join('?' for _ in columns)})",
            tuple(newer[column] for column in columns),
        )
        conn.commit()
    finally:
        conn.close()

    findings = _staged_registry_findings(module, tmp_path, [rel_path])

    assert findings == [
        {
            "path": rel_path,
            "reason": "bridge publication capability was compensated or failed",
        }
    ]


def test_bridge_publication_digest_uses_index_when_worktree_differs(
    tmp_path: Path,
) -> None:
    module = _load_module()
    rel_path = "bridge/gtkb-publication-index-001.md"
    _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])
    (tmp_path / rel_path).write_text("NEW\n# Worktree-only replacement\n", encoding="utf-8")

    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.row_factory = sqlite3.Row
    try:
        with module._index_snapshot(tmp_path) as snapshot:
            decision = module._bridge_publication_capability_clearance(
                conn,
                root=tmp_path,
                record_id="bridge-versioned-files",
                rel_path=rel_path,
                index_snapshot=snapshot,
            )
    finally:
        conn.close()

    assert decision == (True, "")


def test_real_git_commit_accepts_exact_bridge_publication_capabilities(
    tmp_path: Path,
) -> None:
    rel_paths = [f"bridge/gtkb-publication-commit-{version:03d}.md" for version in range(1, 4)]
    _seed_bridge_publication_commit_fixture(tmp_path, rel_paths)
    hook = tmp_path / ".git" / "hooks" / "pre-commit"
    hook.write_text(
        "#!/bin/sh\n"
        f'exec "{Path(sys.executable).as_posix()}" "{SCRIPT_PATH.as_posix()}" '
        f'--staged --project-root "{tmp_path.as_posix()}"\n',
        encoding="utf-8",
        newline="\n",
    )
    hook.chmod(0o755)

    committed = subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "commit",
            "-m",
            "test: exact bridge publication capabilities",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert committed.returncode == 0, committed.stdout + committed.stderr
    tracked = subprocess.run(
        ["git", "show", "--pretty=format:", "--name-only", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert set(tracked.stdout.splitlines()) == set(rel_paths)


@pytest.mark.parametrize(
    "operation",
    (
        "bridge_publication_compensation",
        "wi5441_bridge_aggregate_recovery",
        "amend",
        "register",
    ),
)
def test_exact_publication_evidence_survives_unrelated_aggregate_head(
    tmp_path: Path,
    operation: str,
) -> None:
    module = _load_module()
    rel_path = f"bridge/gtkb-publication-{operation.replace('_', '-')}-001.md"
    _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.row_factory = sqlite3.Row
    try:
        latest = conn.execute(
            "SELECT * FROM sot_artifact_revisions WHERE entry_id = ? ORDER BY rowid DESC LIMIT 1",
            ("bridge-versioned-files",),
        ).fetchone()
        assert latest is not None
        columns = [column[1] for column in conn.execute("PRAGMA table_info(sot_artifact_revisions)")]
        columns.remove("rowid")
        successor = {column: latest[column] for column in columns}
        successor.update(
            {
                "revision_id": f"aggregate-head-{operation}",
                "operation": operation,
                "predecessor_revision_id": latest["revision_id"],
                "changed_at": "2026-01-01T00:02:00Z",
                "change_reason": "unrelated aggregate head",
                "capability_hash": None,
                "bridge_id": None,
                "journal_id": None,
            }
        )
        conn.execute(
            f"INSERT INTO sot_artifact_revisions ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})",
            tuple(successor[column] for column in columns),
        )
        conn.commit()
    finally:
        conn.close()

    assert _staged_registry_findings(module, tmp_path, [rel_path]) == []


def test_near_match_publication_path_never_authorizes_exact_staged_path(
    tmp_path: Path,
) -> None:
    module = _load_module()
    rel_path = "bridge/gtkb-publication-near-match-001.md"
    capability_hash = _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])[rel_path]
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities SET target_path = ? WHERE capability_hash = ?",
            ("bridge/gtkb-publication-near-match-001.md.copy", capability_hash),
        )
        conn.commit()
    finally:
        conn.close()

    findings = _staged_registry_findings(module, tmp_path, [rel_path])

    assert findings == [
        {
            "path": rel_path,
            "reason": "registered bridge path lacks exact publication capability evidence",
        }
    ]


def test_report_verdict_hash_passes_before_and_after_candidate_materialization(
    tmp_path: Path,
) -> None:
    module = _load_module()
    root = tmp_path
    bridge_id = "gtkb-schema-v2-index-fixture"
    authority_paths = [
        ".claude/hooks/bridge-compliance-gate.py",
        "scripts/__init__.py",
        "scripts/bridge_applicability_preflight.py",
        "scripts/implementation_authorization.py",
        "scripts/bridge_lifecycle_resolver.py",
        "scripts/bridge_work_intent_registry.py",
        "scripts/gtkb_session_id.py",
        "scripts/bridge_author_metadata.py",
    ]
    for rel_path in authority_paths:
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel_path, target)

    (root / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    (root / ".gitignore").write_text("groundtruth.db\n.gtkb-state/\n", encoding="utf-8")
    config = root / "config" / "governance" / "spec-applicability.toml"
    config.parent.mkdir(parents=True)
    config.write_text(
        """
[[rules]]
spec_id = "SPEC-ENVIRONMENT-DESCRIPTION-001"
severity = "advisory"
rationale = "Fixture environment description."
applies_when_doc_matches = ["gtkb-schema-v2-index-fixture"]
""",
        encoding="utf-8",
    )
    proposal_rel = f"bridge/{bridge_id}-001.md"
    go_rel = f"bridge/{bridge_id}-002.md"
    source_rel = f"bridge/{bridge_id}-003.md"
    source = root / source_rel
    source.parent.mkdir()
    proposal_content = (
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n\n"
        f"{_author('prime-builder', 'pb-proposal-session')}"
        "bridge_kind: prime_proposal\n"
        f"Document: {bridge_id}\n"
        "Version: 001\n"
        'target_paths: ["scripts/example.py"]\n'
        "\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    (root / proposal_rel).write_text(proposal_content, encoding="utf-8")
    (root / go_rel).write_text(
        "GO\n"
        "::init gtkb lo\n"
        "::open test\n\n"
        f"{_author('loyal-opposition', 'lo-go-session')}"
        "bridge_kind: lo_verdict\n"
        f"Document: {bridge_id}\n"
        "Version: 002\n"
        f"Responds to: {proposal_rel}\n",
        encoding="utf-8",
    )
    source_content = (
        "NEW\n"
        "::init gtkb pb\n"
        "::open build\n\n"
        f"{_author('prime-builder', 'pb-source-session')}"
        "bridge_kind: implementation_report\n"
        f"Document: {bridge_id}\n"
        "Version: 003\n"
        f"Approved proposal: {proposal_rel}\n"
        f"Controlling GO: {go_rel}\n"
        'target_paths: ["scripts/example.py"]\n'
        "\n## Specification Links\n\n- GOV-FILE-BRIDGE-AUTHORITY-001\n"
    )
    source.write_text(source_content, encoding="utf-8")

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    committed_paths = [
        *authority_paths,
        "groundtruth.toml",
        ".gitignore",
        config.relative_to(root).as_posix(),
        proposal_rel,
        go_rel,
        source_rel,
    ]
    subprocess.run(["git", "add", "--", *committed_paths], cwd=root, check=True)
    hooks = root / "empty-hooks"
    hooks.mkdir()
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "fixture authority",
        ],
        cwd=root,
        check=True,
    )

    db_path = root / "groundtruth.db"
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("CREATE TABLE current_specifications (id TEXT PRIMARY KEY, title TEXT, status TEXT, type TEXT)")
        conn.execute(
            "INSERT INTO current_specifications VALUES (?, ?, ?, ?)",
            (
                "SPEC-ENVIRONMENT-DESCRIPTION-001",
                "Worktree-only description",
                "specified",
                "specification",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    packet = applicability_preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=root / "bridge",
        config_path=config,
        db_path=db_path,
        content_file=source,
    )
    gate_spec = importlib.util.spec_from_file_location(
        "wi5441_schema_v2_fixture_gate",
        root / ".claude" / "hooks" / "bridge-compliance-gate.py",
    )
    assert gate_spec is not None and gate_spec.loader is not None
    gate = importlib.util.module_from_spec(gate_spec)
    gate_spec.loader.exec_module(gate)

    candidate_rel = f"bridge/{bridge_id}-004.md"
    candidate_path = root / candidate_rel
    tick = chr(96)
    candidate = (
        "VERIFIED\n"
        "::init gtkb lo\n"
        "::open test\n\n"
        f"{_author('loyal-opposition', 'lo-review-session')}"
        "bridge_kind: lo_verdict\n"
        f"Document: {bridge_id}\n"
        "Version: 004\n"
        f"Responds to: {source_rel}\n\n"
        "## Applicability Preflight\n\n"
        f"- packet_hash: {packet['packet_hash']}\n"
        f"- bridge_document_name: {bridge_id}\n"
        f"- content_file: {source_rel}\n"
        f"- operative_file: {source_rel}\n"
        "- missing_required_specs: []\n"
        f"- candidate_evidence_hash: {gate.CANDIDATE_EVIDENCE_HASH_SENTINEL}\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        "- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001\n\n"
        "## Spec-to-Test Mapping\n\n"
        "| Specification | Evidence |\n"
        "| --- | --- |\n"
        "| GOV-FILE-BRIDGE-AUTHORITY-001 | Real index-only audit |\n\n"
        "## Verification Commands\n\n"
        "pytest platform_tests/scripts/test_check_protected_commit_authorization.py\n\n"
        "## Commit Finalization Evidence\n\n"
        "- Same-transaction path set:\n"
        f"- {tick}{candidate_rel}{tick}\n"
    )
    candidate_hash = gate._candidate_evidence_hash(candidate_rel, candidate, root)
    assert candidate_hash is not None
    candidate = candidate.replace(gate.CANDIDATE_EVIDENCE_HASH_SENTINEL, candidate_hash)

    live_audit = module.run_bridge_compliance_audit(
        file_path=candidate_path,
        content=candidate,
        project_root=root,
    )
    assert live_audit["decision"] == "pass"

    candidate_path.write_text(candidate, encoding="utf-8")
    subprocess.run(["git", "add", "--", candidate_rel], cwd=root, check=True)

    with (
        module._index_snapshot(root) as index_snapshot,
        module._bridge_snapshot(root, bridge_id, index_snapshot) as bridge_snapshot,
    ):
        assert not (bridge_snapshot.root / "groundtruth.db").exists()
        assert gate._canonical_project_root(bridge_snapshot.root / "bridge") == bridge_snapshot.root.resolve()
        snapshot_audit = module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=candidate,
        )
    assert snapshot_audit["decision"] == "pass"

    source.write_text(source_content + "\nSource mutation.\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", source_rel], cwd=root, check=True)
    with (
        module._index_snapshot(root) as index_snapshot,
        module._bridge_snapshot(root, bridge_id, index_snapshot) as bridge_snapshot,
        pytest.raises(module.BridgeComplianceError, match="stale packet_hash"),
    ):
        module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=candidate,
        )

    source.write_text(source_content, encoding="utf-8")
    candidate_mutation = candidate + "\nCandidate mutation.\n"
    candidate_path.write_text(candidate_mutation, encoding="utf-8")
    subprocess.run(["git", "add", "--", source_rel, candidate_rel], cwd=root, check=True)
    with (
        module._index_snapshot(root) as index_snapshot,
        module._bridge_snapshot(root, bridge_id, index_snapshot) as bridge_snapshot,
        pytest.raises(module.BridgeComplianceError, match="candidate_evidence_hash"),
    ):
        module._run_snapshot_compliance_audit(
            snapshot=bridge_snapshot,
            candidate_path=candidate_rel,
            content=candidate_mutation,
        )


# ---------------------------------------------------------------------------
# WI-5824 Fix A: state-first, null-safe capability clearance.


def _wi5824_capability_row(**overrides: object) -> dict[str, object]:
    """Duck-typed sqlite3.Row stand-in for direct clearance-helper calls."""
    row: dict[str, object] = {
        "version": 1,
        "document_name": "gtkb-state-first",
        "target_path": "bridge/gtkb-state-first-001.md",
        "aggregate_entry_id": "bridge-versioned-files",
        "authority_kind": "bridge_publication",
        "operation": "bridge_publication",
        "expires_at": "2026-01-01T00:02:00Z",
        "capability_state": "recovery_required",
        "compensation_revision_id": None,
        "compensation_digest": None,
        "consumed_at": None,
        "result_digest": "sha256:result",
        "revision_id": "revision-1",
        "failure_reason": None,
    }
    row.update(overrides)
    return row


def _wi5824_clearance(module, tmp_path: Path, row: dict[str, object]) -> tuple[bool, str]:
    return module._bridge_publication_capability_clearance(
        None,
        root=tmp_path,
        record_id="bridge-versioned-files",
        rel_path="bridge/gtkb-state-first-001.md",
        index_snapshot=None,
        capability=row,
    )


def test_capability_clearance_denies_cleanly_on_null_consumed_at(
    tmp_path: Path,
) -> None:
    """WI-5824 (a): recovery_required + consumed_at NULL is a clean state deny.

    The r2b-008 incident shape: parse_iso(None) raised AttributeError and
    killed the pre-commit hook. The deny must name the capability state and no
    exception of any kind may escape.
    """
    module = _load_module()

    allowed, reason = _wi5824_clearance(
        module,
        tmp_path,
        _wi5824_capability_row(capability_state="recovery_required", consumed_at=None),
    )

    assert allowed is False
    assert reason == "bridge publication capability is not consumed ('recovery_required')"

    # End-to-end through the staged registry assessment: the same row shape in
    # a real fixture database must yield a finding, never a traceback.
    rel_path = "bridge/gtkb-publication-nullsafe-001.md"
    capability_hash = _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])[rel_path]
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "UPDATE sot_registry_bridge_publication_capabilities "
            "SET capability_state = 'recovery_required', consumed_at = NULL WHERE capability_hash = ?",
            (capability_hash,),
        )
        conn.commit()
    finally:
        conn.close()

    findings = _staged_registry_findings(module, tmp_path, [rel_path])

    assert len(findings) == 1
    assert findings[0]["path"] == rel_path
    assert findings[0]["reason"] == "bridge publication capability is not consumed ('recovery_required')"


def test_capability_clearance_checks_state_before_consumed_timestamp(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-5824 (a): non-consumed rows deny on state before consumed_at parsing."""
    module = _load_module()
    parsed_values: list[object] = []
    real_parse_iso = implementation_authorization.parse_iso

    def recording_parse_iso(value):
        parsed_values.append(value)
        return real_parse_iso(value)

    monkeypatch.setattr(module, "parse_iso", recording_parse_iso)

    for state in ("minted", "recovery_required", "expired"):
        parsed_values.clear()
        allowed, reason = _wi5824_clearance(
            module,
            tmp_path,
            _wi5824_capability_row(capability_state=state, consumed_at="SENTINEL-NEVER-PARSED"),
        )
        assert allowed is False
        assert reason == f"bridge publication capability is not consumed ({state!r})"
        assert "SENTINEL-NEVER-PARSED" not in parsed_values


def test_capability_clearance_consumed_row_normal_path_unchanged(
    tmp_path: Path,
) -> None:
    """WI-5824 (a): consumed rows with valid timestamps clear exactly as before,
    including the staged-digest match against the copied index."""
    module = _load_module()
    rel_path = "bridge/gtkb-publication-normal-001.md"
    capability_hash = _seed_bridge_publication_commit_fixture(tmp_path, [rel_path])[rel_path]
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    conn.row_factory = sqlite3.Row
    try:
        capability = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities WHERE capability_hash = ?",
            (capability_hash,),
        ).fetchone()
        assert capability is not None
        with module._index_snapshot(tmp_path) as snapshot:
            allowed, reason = module._bridge_publication_capability_clearance(
                conn,
                root=tmp_path,
                record_id="bridge-versioned-files",
                rel_path=rel_path,
                index_snapshot=snapshot,
                capability=capability,
            )
    finally:
        conn.close()

    assert (allowed, reason) == (True, "")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("consumed_at", None),
        ("consumed_at", 12345),
        ("consumed_at", "not-a-timestamp"),
        ("expires_at", None),
        ("expires_at", 12345),
        ("expires_at", "not-a-timestamp"),
    ],
)
def test_capability_clearance_non_string_timestamps_deny_cleanly(
    tmp_path: Path,
    field: str,
    value: object,
) -> None:
    """WI-5824 (a) defense in depth: invalid timestamp shapes on a consumed row
    yield the clean incomplete-timestamp deny; no traceback for any shape."""
    module = _load_module()

    allowed, reason = _wi5824_clearance(
        module,
        tmp_path,
        _wi5824_capability_row(capability_state="consumed", **{field: value}),
    )

    assert allowed is False
    assert reason == "bridge publication capability has incomplete or invalid timestamps"


# ---------------------------------------------------------------------------
# WI-5824 Fix B: transaction-local terminal-evidence ordering.


def _wi5824_mock_content_validators(module, monkeypatch: pytest.MonkeyPatch) -> None:
    """Neutralize verdict content-quality validators (same convention as the
    existing transaction-local e2e test); packet and chain validation stay real."""
    monkeypatch.setattr(module, "run_bridge_compliance_audit", lambda **kwargs: {"decision": "pass"})
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda content, project_root: [])
    monkeypatch.setattr(module, "verdict_self_review_reason", lambda *args, **kwargs: None)


def _wi5824_rewrite_packet_expiry(module, tmp_path: Path, bridge_id: str, expires_at: str) -> None:
    """Re-time the fixture packet with the schema-v2/v3 hash dance intact."""
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    start = packet.pop("implementation_start")
    packet.pop("packet_hash")
    packet["schema_version"] = 2
    packet["expires_at"] = expires_at
    packet["packet_hash"] = module.packet_hash(packet)
    start["pre_start_packet_hash"] = packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = start
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")


@pytest.mark.parametrize("packet_expired", [False, True])
def test_finalize_verified_same_transaction_phase_evaluation_passes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    packet_expired: bool,
) -> None:
    """WI-5824 (b): a finalize-verified transaction (implementation paths +
    same-transaction VERIFIED verdict + finalization evidence + bound finalized
    packet) passes phase evaluation with the REAL packet listing in play.

    ``packet_expired=True`` is the wi5759/wi5758 wedge shape: the packet was
    live at implementation but expired before verification; ambient-now packet
    state (route 1) is invalid, yet transaction-local terminal evidence must
    clear the staged paths. ``packet_expired=False`` locks that the
    phase-closure conclusion derived from the same in-transaction verdict
    ("implementation phase ... closed") never denies the transaction.
    """
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    _wi5824_mock_content_validators(module, monkeypatch)
    bridge_id = "gtkb-wi5629-fixture"
    if packet_expired:
        # Live at implementation (finalized 2026-07-19T00:00:00Z <= expiry),
        # expired long before the finalize-verified evaluation runs.
        _wi5824_rewrite_packet_expiry(module, tmp_path, bridge_id, "2026-07-19T02:00:00Z")

    packets, errors, scanned = module._load_live_go_evidence(tmp_path)
    assert packets == []
    assert scanned == 1
    if packet_expired:
        assert any("has expired" in error for error in errors)
    else:
        assert any("implementation phase for this proposal is closed" in error for error in errors)

    result = module.evaluate(tmp_path)

    assert result["status"] == "pass"
    assert result["evidence_summary"]["live_go_packets_scanned"] == 1
    assert result["evidence_summary"]["live_go_packets_valid"] == 0
    cleared_by_path = {item["path"]: item for item in result["cleared"]}
    for rel_path in (
        "scripts/bridge_lifecycle_resolver.py",
        "platform_tests/scripts/test_bridge_lifecycle_resolver.py",
    ):
        assert cleared_by_path[rel_path]["evidence"] == "transaction_local_verified_manifest"
        assert cleared_by_path[rel_path]["source"] == bridge_id


def test_committed_terminal_thread_still_denies_new_mutations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-5824 (b) fail-closed floor: a committed-terminal thread keeps denying
    newly staged post-terminal mutations of its target paths (wi4894-002
    denial class) when no clearing evidence exists."""
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={tmp_path / 'empty-hooks'}",
            "commit",
            "-qm",
            "fixture terminal",
        ],
        cwd=tmp_path,
        check=True,
    )
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / "gtkb-wi5629-fixture.json"
    packet_path.unlink()
    mutated = tmp_path / "scripts" / "bridge_lifecycle_resolver.py"
    mutated.write_text("# post-terminal mutation\n", encoding="utf-8")
    subprocess.run(
        ["git", "add", "--", "scripts/bridge_lifecycle_resolver.py"],
        cwd=tmp_path,
        check=True,
    )

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert [finding["path"] for finding in result["findings"]] == ["scripts/bridge_lifecycle_resolver.py"]
    assert result["findings"][0]["reason"].startswith("protected path lacks")


def test_transaction_local_multiple_verified_candidates_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-5824 (b) fail-closed floor: two live VERIFIED candidates in one
    transaction are denied by the exactly-one-candidate rule."""
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    second_verdict = "bridge/gtkb-wi5824-second-thread-002.md"
    (tmp_path / second_verdict).write_text(
        f"""VERIFIED
{_author("loyal-opposition", "other-lo-session")}
# Second verification

Document: gtkb-wi5824-second-thread
Version: 002

## Commit Finalization Evidence

- Finalization helper: `fixture`
- Intended commit subject: `fix: fixture`
- Same-transaction path set:
- `{second_verdict}`
- Final commit SHA is emitted after commit creation.
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "--", second_verdict], cwd=tmp_path, check=True)
    _wi5824_mock_content_validators(module, monkeypatch)

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        "same-transaction clearance requires exactly one VERIFIED candidate" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )


def test_transaction_local_manifest_mismatch_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-5824 (b) fail-closed floor: manifest != staged set stays a deny."""
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    verdict_path = tmp_path / verdict
    verdict_path.write_text(
        verdict_path.read_text(encoding="utf-8").replace("- `scripts/bridge_lifecycle_resolver.py`\n", ""),
        encoding="utf-8",
    )
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    _wi5824_mock_content_validators(module, monkeypatch)

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        "same-transaction manifest does not equal the staged path set" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )


def test_transaction_local_unbound_packet_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WI-5824 (b) / DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001:
    a transaction-local candidate without a bound finalized packet is denied,
    and a packet that was never live at implementation is denied."""
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)
    _wi5824_mock_content_validators(module, monkeypatch)
    bridge_id = "gtkb-wi5629-fixture"
    packet_path = tmp_path / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    original_packet = packet_path.read_text(encoding="utf-8")
    packet_path.unlink()

    result = module.evaluate(tmp_path)

    assert result["status"] == "fail"
    assert any(
        "implementation-start packet is absent" in error
        for finding in result["findings"]
        for error in finding.get("evidence_errors", [])
    )

    # Never-live packet: finalized_at after expires_at is not implementation-time
    # authority and must not clear the transaction.
    packet_path.write_text(original_packet, encoding="utf-8")
    _wi5824_rewrite_packet_expiry(module, tmp_path, bridge_id, "2026-07-18T00:00:00Z")
    never_live = module.evaluate(tmp_path)

    assert never_live["status"] == "fail"
    assert any(
        "was not live at implementation" in error
        for finding in never_live["findings"]
        for error in finding.get("evidence_errors", [])
    )


# ---------------------------------------------------------------------------
# WI-6183: invocation-local PAUTH read snapshot for copied-root audits.


def _wi6183_seed_authority_db(module, root: Path, *, omit_relation: str | None = None) -> None:
    conn = sqlite3.connect(root / "groundtruth.db")
    try:
        for relation, columns in module.PAUTH_READ_SNAPSHOT_RELATIONS:
            if relation == omit_relation:
                continue
            schema = ", ".join(f'"{column}" {declared_type}' for column, declared_type in columns)
            conn.execute(f'CREATE TABLE "{relation}" ({schema})')
        if omit_relation != "current_specifications":
            conn.execute(
                "INSERT INTO current_specifications VALUES (?, ?, ?, ?, ?)",
                ("SPEC-TEST", 1, "Fixture specification", "specified", "specification"),
            )
        if omit_relation != "current_projects":
            conn.execute(
                "INSERT INTO current_projects VALUES (?, ?, ?, ?)",
                ("PROJECT-TEST", 1, "active", None),
            )
        if omit_relation != "current_project_work_item_memberships":
            conn.execute(
                "INSERT INTO current_project_work_item_memberships VALUES (?, ?, ?, ?, ?)",
                ("PWM-TEST", 1, "PROJECT-TEST", "WI-TEST", "active"),
            )
        if omit_relation != "current_project_authorizations":
            conn.execute(
                "INSERT INTO current_project_authorizations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "PAUTH-TEST",
                    1,
                    "PROJECT-TEST",
                    "active",
                    "Fixture authorization",
                    "DELIB-TEST",
                    "Authorize exact fixture paths.",
                    json.dumps(["bridge", "source", "test"]),
                    json.dumps([]),
                    json.dumps([]),
                    json.dumps([]),
                    json.dumps([]),
                    json.dumps([]),
                    None,
                    json.dumps([]),
                    json.dumps([]),
                ),
            )
        conn.execute("CREATE TABLE unrelated_runtime_state (id TEXT, value TEXT)")
        conn.execute("INSERT INTO unrelated_runtime_state VALUES ('one', 'before')")
        conn.commit()
    finally:
        conn.close()


def _wi6183_ledger_entry(module, path: Path):
    info = path.stat()
    return module._LedgerEntry(
        mode="100644",
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        size=info.st_size,
        device=info.st_dev,
        inode=info.st_ino,
        link_count=info.st_nlink,
    )


def _wi6183_bridge_snapshot(module, root: Path, *, oversized_db_entry: bool = False):
    snapshot_root = root / ".gtkb-state" / "wi6183-snapshot"
    snapshot_root.mkdir(parents=True)
    config = snapshot_root / "groundtruth.toml"
    config.write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    taxonomy_source = REPO_ROOT / "config" / "governance" / "project-authorization-operation-taxonomy.toml"
    live_taxonomy = root / "config" / "governance" / taxonomy_source.name
    live_taxonomy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(taxonomy_source, live_taxonomy)
    taxonomy = snapshot_root / "config" / "governance" / taxonomy_source.name
    taxonomy.parent.mkdir(parents=True)
    shutil.copy2(live_taxonomy, taxonomy)
    ledger = {
        "groundtruth.toml": _wi6183_ledger_entry(module, config),
        taxonomy.relative_to(snapshot_root).as_posix(): _wi6183_ledger_entry(module, taxonomy),
    }
    if oversized_db_entry:
        ledger["groundtruth.db"] = module._LedgerEntry(
            mode="100644",
            sha256="0" * 64,
            size=module.MAX_BLOB_BYTES + 1,
            device=0,
            inode=0,
            link_count=0,
            content_exempt=True,
            oid="a" * 40,
        )
    return module._BridgeSnapshot(root=snapshot_root, ledger=ledger)


def _wi6183_pauth_packet(root: Path, *, target_path: str = "scripts/check_protected_commit_authorization.py"):
    row = implementation_authorization._project_authorization_row(root, "PAUTH-TEST")
    project_authorization = implementation_authorization.validate_project_authorization_row(
        root,
        row,
        proposal_project_id="PROJECT-TEST",
        work_item_id="WI-TEST",
        spec_links=["SPEC-TEST"],
        target_paths=[target_path],
        requested_operations=["protected_mutation"],
    )
    return {
        "schema_version": 3,
        "spec_links": ["SPEC-TEST"],
        "project_authorization": project_authorization,
    }


def _wi6183_assert_projection_absent(snapshot_root: Path) -> None:
    for suffix in ("", "-journal", "-wal", "-shm"):
        assert not Path(str(snapshot_root / "groundtruth.db") + suffix).exists()


def _wi6183_prepare_verdict_in_snapshot(snapshot_root: Path, candidate_path: str, content: str) -> str:
    """Prepare verdict bytes with the exact modules and PAUTH projection under audit."""

    wrapper = r"""
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(root / "groundtruth-kb" / "src"))
sys.path.insert(0, str(root))
from scripts.bridge_applicability_preflight import prepare_verdict_candidate

sys.stdout.write(
    prepare_verdict_candidate(
        candidate_path=sys.argv[2],
        content=sys.stdin.read(),
        project_root=root,
        config_path=root / "config" / "governance" / "spec-applicability.toml",
        db_path=root / "groundtruth.db",
    )
)
"""
    prepared = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-S",
            "-c",
            wrapper,
            str(snapshot_root),
            candidate_path,
        ],
        cwd=snapshot_root,
        input=content,
        text=True,
        capture_output=True,
        check=False,
    )
    assert prepared.returncode == 0, prepared.stderr
    return prepared.stdout


def test_wi6183_pauth_snapshot_projects_exact_relations_and_real_evaluator_consumes_it(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path, oversized_db_entry=True)
    bridge_id = "gtkb-wi6183-pauth-projection-fixture"
    source_rel = f"bridge/{bridge_id}-001.md"
    source_text = (
        "NEW\n\n"
        f"Document: {bridge_id}\n"
        "Project Authorization: PAUTH-TEST\n"
        "Project: PROJECT-TEST\n"
        "Work Item: WI-TEST\n\n"
        "## Specification Links\n\n- SPEC-TEST\n"
    )
    source = tmp_path / source_rel
    source.parent.mkdir()
    source.write_text(source_text, encoding="utf-8")
    applicability_config = tmp_path / "config" / "governance" / "spec-applicability.toml"
    applicability_config.write_text(
        f'[[rules]]\nspec_id = "SPEC-TEST"\nseverity = "required"\napplies_when_doc_matches = ["{bridge_id}"]\n',
        encoding="utf-8",
    )
    for live_path in (source, applicability_config):
        rel_path = live_path.relative_to(tmp_path)
        projected_path = snapshot.root / rel_path
        projected_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(live_path, projected_path)
        snapshot.ledger[rel_path.as_posix()] = _wi6183_ledger_entry(module, projected_path)
    live_applicability = applicability_preflight.build_packet(
        bridge_id=bridge_id,
        bridge_dir=tmp_path / "bridge",
        config_path=applicability_config,
        db_path=tmp_path / "groundtruth.db",
        content_file=source,
    )
    target_paths = ["scripts/check_protected_commit_authorization.py"]
    source_row = implementation_authorization._project_authorization_row(tmp_path, "PAUTH-TEST")
    project_authorization = implementation_authorization.validate_project_authorization_row(
        tmp_path,
        source_row,
        proposal_project_id="PROJECT-TEST",
        work_item_id="WI-TEST",
        spec_links=["SPEC-TEST"],
        target_paths=target_paths,
        requested_operations=["protected_mutation"],
    )
    packet = {
        "schema_version": 3,
        "spec_links": ["SPEC-TEST"],
        "project_authorization": project_authorization,
    }

    with module._pauth_read_snapshot(tmp_path, snapshot) as effective:
        projection = effective.root / "groundtruth.db"
        assert projection.is_file()
        assert effective.ledger["groundtruth.db"].content_exempt is False
        evidence = effective.ledger["groundtruth.db"].pauth_read_snapshot
        assert evidence is not None
        assert effective.pauth_source_identity == evidence.source_identity
        module._verify_snapshot_ledger(effective)
        conn = sqlite3.connect(projection)
        try:
            tables = tuple(
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
                )
            )
        finally:
            conn.close()
        assert tables == tuple(sorted(module.PAUTH_READ_SNAPSHOT_RELATION_NAMES))
        projected_applicability = applicability_preflight.build_packet(
            bridge_id=bridge_id,
            bridge_dir=effective.root / "bridge",
            config_path=effective.root / "config" / "governance" / "spec-applicability.toml",
            db_path=projection,
            content_file=effective.root / source_rel,
        )
        assert projected_applicability["packet_hash"] == live_applicability["packet_hash"]
        decision = implementation_authorization.validate_packet_project_authorization_operation(
            effective.root,
            packet,
            requested_operations=["protected_mutation"],
            target_paths=target_paths,
        )
        assert decision is not None
        assert decision["id"] == "PAUTH-TEST"

    _wi6183_assert_projection_absent(snapshot.root)
    module._verify_snapshot_ledger(snapshot)


def test_wi6183_non_pauth_route_does_not_open_or_project_authority(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    calls: list[object] = []
    monkeypatch.setattr(
        module,
        "_pauth_read_snapshot",
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    assert module._requires_pauth_read_snapshot("VERIFIED", "Project: PROJECT-TEST") is False
    assert module._requires_pauth_read_snapshot("NEW", "Project Authorization: PAUTH-TEST") is False
    assert calls == []
    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    "metadata",
    [
        "Project Authorization: PAUTH-TEST",
        "Project Authorization ID: PAUTH-TEST",
        "- Project Authorization: `PAUTH-TEST`",
        "**Project Authorization:** **PAUTH-TEST**",
        "- **Project Authorization ID:** `PAUTH-TEST`",
    ],
)
def test_wi6183_pauth_route_uses_canonical_metadata_grammar(metadata: str) -> None:
    module = _load_module()

    assert module._requires_pauth_read_snapshot("VERIFIED", metadata) is True


@pytest.mark.parametrize(
    ("mutation", "sql"),
    [
        pytest.param(
            "revoked-authorization",
            "UPDATE current_project_authorizations SET status = 'revoked' WHERE id = 'PAUTH-TEST'",
            id="revoked-authorization",
        ),
        pytest.param(
            "inactive-project",
            "UPDATE current_projects SET status = 'retired' WHERE id = 'PROJECT-TEST'",
            id="inactive-project",
        ),
        pytest.param(
            "missing-membership",
            "DELETE FROM current_project_work_item_memberships WHERE id = 'PWM-TEST'",
            id="missing-membership",
        ),
    ],
)
def test_wi6183_operation_time_authority_state_denies(
    tmp_path: Path,
    mutation: str,
    sql: str,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    packet = _wi6183_pauth_packet(tmp_path)
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(sql)
        conn.commit()
    finally:
        conn.close()
    with (
        module._pauth_read_snapshot(tmp_path, snapshot) as effective,
        pytest.raises(implementation_authorization.AuthorizationError),
    ):
        implementation_authorization.validate_packet_project_authorization_operation(
            effective.root,
            packet,
            requested_operations=["protected_mutation"],
            target_paths=["scripts/check_protected_commit_authorization.py"],
        )

    assert mutation
    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    "sql",
    [
        pytest.param(
            "UPDATE current_project_authorizations SET status = 'revoked' WHERE id = 'PAUTH-TEST'",
            id="authorization-revoked",
        ),
        pytest.param(
            "UPDATE current_projects SET status = 'retired' WHERE id = 'PROJECT-TEST'",
            id="project-inactive",
        ),
        pytest.param(
            "DELETE FROM current_project_work_item_memberships WHERE id = 'PWM-TEST'",
            id="membership-missing",
        ),
        pytest.param(
            "DELETE FROM current_specifications WHERE id = 'SPEC-TEST'",
            id="specification-non-current",
        ),
    ],
)
def test_wi6183_relevant_authority_drift_denies_and_cleans(tmp_path: Path, sql: str) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    with (
        pytest.raises(module.GateError, match="changed during protected-commit evaluation"),
        module._pauth_read_snapshot(tmp_path, snapshot),
    ):
        conn = sqlite3.connect(tmp_path / "groundtruth.db")
        try:
            conn.execute(sql)
            conn.commit()
        finally:
            conn.close()

    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    ("source_observation", "expected"),
    [
        pytest.param(2, "changed while constructing", id="post-copy"),
        pytest.param(3, "changed during protected-commit evaluation", id="post-evaluation"),
    ],
)
def test_wi6183_relation_drift_at_each_snapshot_boundary_denies_and_cleans(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    source_observation: int,
    expected: str,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    real_observe = module._observe_pauth_authority
    source_calls = 0

    def drifting_observation(conn, *, projection: bool, include_rows: bool = False):
        nonlocal source_calls
        observation, rows = real_observe(conn, projection=projection, include_rows=include_rows)
        if not projection:
            source_calls += 1
            if source_calls == source_observation:
                relations = list(observation.relations)
                relations[0] = module.replace(relations[0], rows_sha256="f" * 64)
                observation = module.replace(observation, relations=tuple(relations))
        return observation, rows

    monkeypatch.setattr(module, "_observe_pauth_authority", drifting_observation)
    with (
        pytest.raises(module.GateError, match=expected),
        module._pauth_read_snapshot(tmp_path, snapshot),
    ):
        pass

    _wi6183_assert_projection_absent(snapshot.root)


def test_wi6183_unrelated_database_churn_is_not_a_false_deny(tmp_path: Path) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    with module._pauth_read_snapshot(tmp_path, snapshot):
        conn = sqlite3.connect(tmp_path / "groundtruth.db")
        try:
            conn.execute("INSERT INTO unrelated_runtime_state VALUES ('two', 'after')")
            conn.commit()
        finally:
            conn.close()

    _wi6183_assert_projection_absent(snapshot.root)


def test_wi6183_source_identity_omits_whole_database_bytes_and_copying() -> None:
    module = _load_module()
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    identity_body = source[
        source.index("def _pauth_source_identity(") : source.index("def _verify_pauth_source_identity(")
    ]
    projection_body = source[source.index("def _pauth_read_snapshot(") : source.index("def _observe_projection_path(")]

    assert tuple(module._PAuthSourceIdentity.__dataclass_fields__) == (
        "resolved_path",
        "device",
        "inode",
        "link_count",
        "mode",
    )
    assert "read_bytes" not in identity_body
    assert "sha256" not in identity_body
    assert "copyfile" not in projection_body
    assert "copy2" not in projection_body
    assert "shutil.copy" not in projection_body


def test_wi6183_projection_tamper_denies_and_cleans(tmp_path: Path) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    with (
        pytest.raises(module.GateError, match="bytes drifted|readonly database"),
        module._pauth_read_snapshot(tmp_path, snapshot) as effective,
    ):
        projection = effective.root / "groundtruth.db"
        conn = sqlite3.connect(projection)
        try:
            conn.execute("UPDATE current_projects SET status = 'retired' WHERE id = 'PROJECT-TEST'")
            conn.commit()
        finally:
            conn.close()

    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        pytest.param("missing", "source is unavailable", id="missing"),
        pytest.param("unreadable", "access denied", id="unreadable"),
        pytest.param("locked", "database is locked", id="locked"),
        pytest.param(
            "malformed",
            "authority relations are unreadable|not a readable",
            id="malformed",
        ),
        pytest.param("schema-incomplete", "current_specifications", id="schema-incomplete"),
    ],
)
def test_wi6183_canonical_source_failures_deny_and_clean(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
    expected: str,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(
        module,
        tmp_path,
        omit_relation="current_specifications" if failure == "schema-incomplete" else None,
    )
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    source = tmp_path / "groundtruth.db"
    if failure == "missing":
        source.unlink()
    elif failure == "malformed":
        source.unlink()
        source.write_bytes(b"not a sqlite database")
    elif failure in {"unreadable", "locked"}:
        real_connect = module.sqlite3.connect

        def failing_source_connect(database, *args, **kwargs):
            if str(database).startswith(source.as_uri()) and "mode=ro" in str(database):
                message = "access denied" if failure == "unreadable" else "database is locked"
                raise sqlite3.OperationalError(message)
            return real_connect(database, *args, **kwargs)

        monkeypatch.setattr(module.sqlite3, "connect", failing_source_connect)

    with (
        pytest.raises(module.GateError, match=expected),
        module._pauth_read_snapshot(tmp_path, snapshot),
    ):
        pytest.fail("an invalid canonical PAUTH source must not yield")

    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    ("tamper", "expected"),
    [
        pytest.param(
            "path",
            "source identity binding lacks canonical ledger evidence",
            id="path",
        ),
        pytest.param("file-hash", "bytes drifted", id="file-hash"),
        pytest.param("file-size", "identity drifted", id="file-size"),
        pytest.param("source-identity", "source identity changed", id="source-identity"),
        pytest.param("schema-digest", "logical contents differ", id="schema-digest"),
        pytest.param("row-count", "logical contents differ", id="row-count"),
        pytest.param("typed-row-digest", "logical contents differ", id="typed-row-digest"),
        pytest.param(
            "construction-version",
            "construction version is unsupported",
            id="construction-version",
        ),
    ],
)
def test_wi6183_derived_ledger_tamper_denies_and_cleans(
    tmp_path: Path,
    tamper: str,
    expected: str,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    with (
        pytest.raises(module.GateError, match=expected),
        module._pauth_read_snapshot(tmp_path, snapshot) as effective,
    ):
        entry = effective.ledger["groundtruth.db"]
        evidence = entry.pauth_read_snapshot
        assert evidence is not None
        if tamper == "path":
            effective.ledger["redirected/groundtruth.db"] = effective.ledger.pop("groundtruth.db")
            module._verify_snapshot_ledger(effective)
        elif tamper == "file-hash":
            effective.ledger["groundtruth.db"] = module.replace(entry, sha256="0" * 64)
            module._verify_snapshot_ledger(effective)
        elif tamper == "file-size":
            effective.ledger["groundtruth.db"] = module.replace(entry, size=entry.size + 1)
            module._verify_snapshot_ledger(effective)
        elif tamper == "source-identity":
            tampered_identity = module.replace(evidence.source_identity, inode=evidence.source_identity.inode + 1)
            tampered_evidence = module.replace(evidence, source_identity=tampered_identity)
            effective.ledger["groundtruth.db"] = module.replace(entry, pauth_read_snapshot=tampered_evidence)
            module._verify_snapshot_ledger(effective)
        elif tamper == "construction-version":
            tampered_evidence = module.replace(evidence, construction_version=evidence.construction_version + 1)
            effective.ledger["groundtruth.db"] = module.replace(entry, pauth_read_snapshot=tampered_evidence)
            module._verify_snapshot_ledger(effective)
        else:
            relations = list(evidence.relations)
            if tamper == "schema-digest":
                relations[0] = module.replace(relations[0], schema_sha256="0" * 64)
            elif tamper == "row-count":
                relations[0] = module.replace(relations[0], row_count=relations[0].row_count + 1)
            else:
                relations[0] = module.replace(relations[0], rows_sha256="0" * 64)
            tampered_evidence = module.replace(evidence, relations=tuple(relations))
            effective.ledger["groundtruth.db"] = module.replace(entry, pauth_read_snapshot=tampered_evidence)
            module._verify_snapshot_ledger(effective)

    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    "attack",
    [
        "source-symlink",
        "source-junction",
        "source-reparse",
        "source-replacement",
        "nested-root",
        "environment-override",
        "configuration-override",
        "caller-substitution",
    ],
)
def test_wi6183_canonical_source_binding_attacks_cannot_redirect_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    source = tmp_path / "groundtruth.db"

    if attack in {"source-symlink", "source-junction", "source-reparse"}:
        real_linklike = module._path_is_linklike
        monkeypatch.setattr(
            module,
            "_path_is_linklike",
            lambda path: path == source or real_linklike(path),
        )
        with (
            pytest.raises(
                module.GateError,
                match="symlinked, junctioned, or reparse-point redirected",
            ),
            module._pauth_read_snapshot(tmp_path, snapshot),
        ):
            pytest.fail("a redirected canonical source must not yield")
    elif attack == "source-replacement":
        real_source_identity = module._pauth_source_identity
        identity_calls = 0

        def replaced_source_identity(root: Path, path: Path):
            nonlocal identity_calls
            identity_calls += 1
            identity = real_source_identity(root, path)
            return module.replace(identity, inode=identity.inode + 1) if identity_calls > 1 else identity

        monkeypatch.setattr(module, "_pauth_source_identity", replaced_source_identity)
        with (
            pytest.raises(module.GateError, match="source identity changed"),
            module._pauth_read_snapshot(tmp_path, snapshot),
        ):
            pytest.fail("a replaced canonical source must not yield")
    elif attack in {"nested-root", "caller-substitution"}:
        substitute_root = tmp_path / ("nested" if attack == "nested-root" else "foreign")
        substitute_root.mkdir()
        substitute = substitute_root / "groundtruth.db"
        shutil.copy2(source, substitute)
        with pytest.raises(module.GateError, match="not the canonical live-root"):
            module._pauth_source_identity(tmp_path, substitute)
    elif attack == "configuration-override":
        config = snapshot.root / "groundtruth.toml"
        config.write_text('[groundtruth]\ndb_path = "foreign.db"\n', encoding="utf-8")
        snapshot.ledger["groundtruth.toml"] = _wi6183_ledger_entry(module, config)
        foreign = snapshot.root / "foreign.db"
        foreign.write_bytes(b"not canonical authority")
        snapshot.ledger["foreign.db"] = _wi6183_ledger_entry(module, foreign)
        with (
            pytest.raises(module.GateError, match="configuration resolves outside"),
            module._pauth_read_snapshot(tmp_path, snapshot),
        ):
            pytest.fail("a copied-root configuration override must not yield")
    else:
        foreign = tmp_path / "foreign.db"
        shutil.copy2(source, foreign)
        foreign_hash = hashlib.sha256(foreign.read_bytes()).hexdigest()
        monkeypatch.setenv("GT_DB_PATH", str(foreign))
        with module._pauth_read_snapshot(tmp_path, snapshot) as effective:
            assert implementation_authorization.groundtruth_db_path(effective.root) == effective.root / "groundtruth.db"
        assert hashlib.sha256(foreign.read_bytes()).hexdigest() == foreign_hash

    _wi6183_assert_projection_absent(snapshot.root)


def test_wi6183_sqlite_sidecar_guards_block_injection_and_are_cleaned(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    with module._pauth_read_snapshot(tmp_path, snapshot) as effective:
        destination = effective.root / "groundtruth.db"
        for suffix in module.PAUTH_READ_SNAPSHOT_SIDECAR_SUFFIXES:
            sidecar = Path(str(destination) + suffix)
            assert sidecar.is_dir()
            with pytest.raises(OSError):
                sidecar.write_bytes(b"untrusted sidecar")

    _wi6183_assert_projection_absent(snapshot.root)


def test_wi6183_linklike_destination_and_sidecar_are_rejected_without_chmod(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    destination = tmp_path / "groundtruth.db"
    sidecar = Path(str(destination) + "-shm")
    sidecar.write_bytes(b"simulated linklike sidecar")
    real_linklike = module._path_is_linklike
    real_chmod = Path.chmod
    chmod_calls: list[Path] = []

    linklike_paths = {destination}

    def simulated_linklike(path: Path) -> bool:
        return path in linklike_paths or real_linklike(path)

    def recording_chmod(path: Path, mode: int, *args, **kwargs) -> None:
        chmod_calls.append(path)
        real_chmod(path, mode, *args, **kwargs)

    monkeypatch.setattr(module, "_path_is_linklike", simulated_linklike)
    monkeypatch.setattr(Path, "chmod", recording_chmod)
    with pytest.raises(module.GateError, match="redirected"):
        module._create_exclusive_pauth_projection_placeholder(destination)
    linklike_paths.clear()
    linklike_paths.add(sidecar)
    with pytest.raises(module.GateError, match="sidecar path is already occupied or redirected"):
        module._create_pauth_projection_sidecar_guards(destination)
    with pytest.raises(module.GateError, match="redirected cleanup artifact"):
        module._remove_pauth_projection(destination)

    assert destination not in chmod_calls
    assert sidecar not in chmod_calls
    assert not sidecar.exists()


def test_wi6183_effective_tree_limit_counts_projection_at_exact_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    with module._pauth_read_snapshot(tmp_path, snapshot) as effective:
        exact_size = sum(entry.size for entry in effective.ledger.values() if not entry.content_exempt)

    monkeypatch.setattr(module, "MAX_TREE_BYTES", exact_size)
    with module._pauth_read_snapshot(tmp_path, snapshot):
        pass

    monkeypatch.setattr(module, "MAX_TREE_BYTES", exact_size - 1)
    with (
        pytest.raises(module.GateError, match="prospective tree exceeds"),
        module._pauth_read_snapshot(tmp_path, snapshot),
    ):
        pytest.fail("an over-limit effective tree must not yield")
    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    ("mismatch", "expected"),
    [
        pytest.param("root", "configuration resolves outside", id="root"),
        pytest.param("allowlist", "relation allowlist mismatch", id="relation-allowlist"),
        pytest.param("schema", "missing required column", id="schema"),
        pytest.param("digest", "logical contents differ", id="digest"),
        pytest.param("version", "construction identity mismatch", id="version"),
    ],
)
def test_wi6183_producer_consumer_mismatch_denies_without_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mismatch: str,
    expected: str,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)

    if mismatch == "root":
        monkeypatch.setattr(module, "groundtruth_db_path", lambda _root: tmp_path / "groundtruth.db")
        with (
            pytest.raises(module.GateError, match=expected),
            module._pauth_read_snapshot(tmp_path, snapshot),
        ):
            pytest.fail("a live-root consumer fallback must not yield")
    else:
        with (
            pytest.raises(module.GateError, match=expected),
            module._pauth_read_snapshot(tmp_path, snapshot) as effective,
        ):
            projection = effective.root / "groundtruth.db"
            evidence = effective.ledger["groundtruth.db"].pauth_read_snapshot
            assert evidence is not None
            probe = effective.root / ".gtkb-state" / "compliance-audit" / f"{mismatch}.db"
            probe.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(projection, probe)
            probe.chmod(0o600)
            conn = sqlite3.connect(probe)
            try:
                if mismatch == "allowlist":
                    conn.execute("CREATE TABLE unexpected_authority (id TEXT)")
                elif mismatch == "schema":
                    conn.execute("ALTER TABLE current_projects DROP COLUMN parent_project_id")
                elif mismatch == "digest":
                    conn.execute("UPDATE current_projects SET status = 'retired' WHERE id = 'PROJECT-TEST'")
                else:
                    conn.execute(f"PRAGMA user_version={module.PAUTH_READ_SNAPSHOT_VERSION + 1}")
                conn.commit()
            finally:
                conn.close()
            try:
                module._verify_pauth_projection(probe, evidence)
            finally:
                probe.chmod(0o600)
                probe.unlink()

    _wi6183_assert_projection_absent(snapshot.root)


def test_wi6183_cleanup_failure_is_terminal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    real_cleanup = module._remove_pauth_projection

    def fail_after_cleanup(path: Path, identity, sidecar_identities) -> None:
        real_cleanup(path, identity, sidecar_identities)
        raise module.GateError("injected cleanup failure")

    monkeypatch.setattr(module, "_remove_pauth_projection", fail_after_cleanup)
    with (
        pytest.raises(module.GateError, match="injected cleanup failure"),
        module._pauth_read_snapshot(tmp_path, snapshot),
    ):
        pass

    _wi6183_assert_projection_absent(snapshot.root)


@pytest.mark.parametrize(
    ("exit_kind", "exception"),
    [
        pytest.param(
            "evaluator-denial",
            lambda module: module.GateError("injected evaluator denial"),
            id="denial",
        ),
        pytest.param(
            "evaluator-exception",
            lambda _module: RuntimeError("injected evaluator exception"),
            id="exception",
        ),
        pytest.param(
            "evaluator-timeout",
            lambda _module: subprocess.TimeoutExpired("injected evaluator", 1),
            id="timeout",
        ),
        pytest.param(
            "outer-exception",
            lambda _module: ValueError("injected outer exception"),
            id="outer-exception",
        ),
    ],
)
def test_wi6183_all_consumer_exits_run_complete_cleanup(
    tmp_path: Path,
    exit_kind: str,
    exception,
) -> None:
    module = _load_module()
    _wi6183_seed_authority_db(module, tmp_path)
    snapshot = _wi6183_bridge_snapshot(module, tmp_path)
    injected = exception(module)

    with (
        pytest.raises(type(injected)),
        module._pauth_read_snapshot(tmp_path, snapshot),
    ):
        raise injected

    assert exit_kind
    _wi6183_assert_projection_absent(snapshot.root)


def _wi6183_transaction_fixture(root: Path, module) -> tuple[str, str]:
    bridge_id = "gtkb-wi6183-transaction-fixture"
    target_rel = "scripts/wi6183_transaction_target.py"
    proposal_rel = f"bridge/{bridge_id}-001.md"
    go_rel = f"bridge/{bridge_id}-002.md"
    report_rel = f"bridge/{bridge_id}-003.md"
    verdict_rel = f"bridge/{bridge_id}-004.md"
    authority_paths = [
        ".claude/hooks/bridge-compliance-gate.py",
        "scripts/__init__.py",
        "scripts/bridge_applicability_preflight.py",
        "scripts/implementation_authorization.py",
        "scripts/bridge_lifecycle_resolver.py",
        "scripts/bridge_work_intent_registry.py",
        "scripts/gtkb_session_id.py",
        "scripts/bridge_author_metadata.py",
        "groundtruth-kb/src/groundtruth_kb/__init__.py",
        "config/governance/project-authorization-operation-taxonomy.toml",
    ]
    authority_paths.extend(
        path.relative_to(REPO_ROOT).as_posix()
        for path in sorted((REPO_ROOT / "groundtruth-kb" / "src" / "groundtruth_kb" / "governance").glob("*.py"))
    )
    for rel_path in authority_paths:
        target = root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel_path, target)
    (root / "groundtruth.toml").write_text('[groundtruth]\ndb_path = "groundtruth.db"\n', encoding="utf-8")
    (root / ".gitignore").write_text("groundtruth.db\n.gtkb-state/\n", encoding="utf-8")
    applicability_config = root / "config" / "governance" / "spec-applicability.toml"
    applicability_config.write_text(
        f'[[rules]]\nspec_id = "SPEC-TEST"\nseverity = "required"\napplies_when_doc_matches = ["{bridge_id}"]\n',
        encoding="utf-8",
    )
    target = root / target_rel
    target.write_text("VALUE = 'baseline'\n", encoding="utf-8")
    (root / "bridge").mkdir()
    (root / proposal_rel).write_text(
        f"""NEW
::init gtkb pb
::open build

{_author("prime-builder", "wi6183-proposal-session")}
bridge_kind: prime_proposal
Document: {bridge_id}
Version: 001
Project Authorization ID: `PAUTH-TEST`
Project: PROJECT-TEST
Work Item: WI-TEST
target_paths: ["{target_rel}"]

## Specification Links

- SPEC-TEST
""",
        encoding="utf-8",
    )
    (root / go_rel).write_text(
        f"""GO
::init gtkb lo
::open test

{_author("loyal-opposition", "wi6183-go-session")}
bridge_kind: lo_verdict
Document: {bridge_id}
Version: 002
Responds to: {proposal_rel}
""",
        encoding="utf-8",
    )
    hooks = root / "empty-hooks"
    hooks.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    committed_paths = [
        *authority_paths,
        "groundtruth.toml",
        ".gitignore",
        applicability_config.relative_to(root).as_posix(),
        target_rel,
        proposal_rel,
        go_rel,
    ]
    subprocess.run(["git", "add", "--", *committed_paths], cwd=root, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Fixture",
            "-c",
            "user.email=fixture@example.invalid",
            "-c",
            f"core.hooksPath={hooks}",
            "commit",
            "-qm",
            "WI-6183 transaction authority",
        ],
        cwd=root,
        check=True,
    )
    _wi6183_seed_authority_db(module, root)
    report = root / report_rel
    report.write_text(
        f"""NEW
::init gtkb pb
::open build

{_author("prime-builder", "wi6183-report-session")}
bridge_kind: implementation_report
Document: {bridge_id}
Version: 003
Responds to: {go_rel}
Project Authorization: PAUTH-TEST
Project: PROJECT-TEST
Work Item: WI-TEST
target_paths: ["{target_rel}"]

## Specification Links

- SPEC-TEST

## Requirement Sufficiency

Existing requirements sufficient.
""",
        encoding="utf-8",
    )
    manifest_paths = [target_rel, report_rel, verdict_rel]
    manifest = "\n".join(f"- `{path}`" for path in manifest_paths)
    verdict = root / verdict_rel
    candidate = f"""VERIFIED
::init gtkb lo
::open test

{_author("loyal-opposition", "wi6183-verified-session")}
bridge_kind: lo_verdict
Document: {bridge_id}
Version: 004
Responds to: {report_rel}

## Applicability Preflight

- pending exact copied-root preparation

## Specification Links

- SPEC-TEST
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001

## Spec-to-Test Mapping

| Specification | Evidence |
| --- | --- |
| SPEC-TEST | WI-6183 transaction integration test |

## Verification Commands

pytest platform_tests/scripts/test_check_protected_commit_authorization.py

## Commit Finalization Evidence

- Finalization helper: `fixture`
- Intended commit subject: `fix: WI-6183 fixture`
- Same-transaction path set:
{manifest}
- Final commit SHA is emitted after commit creation.
"""
    target.write_text("VALUE = 'implemented'\n", encoding="utf-8")
    subprocess.run(["git", "add", "--", target_rel, report_rel], cwd=root, check=True)
    with (
        module._index_snapshot(root) as index_snapshot,
        module._bridge_snapshot(root, bridge_id, index_snapshot) as bridge_snapshot,
        module._pauth_read_snapshot(root, bridge_snapshot) as effective_snapshot,
    ):
        prepared_candidate = _wi6183_prepare_verdict_in_snapshot(
            effective_snapshot.root,
            verdict_rel,
            candidate,
        )
    verdict.write_text(prepared_candidate, encoding="utf-8")

    row = implementation_authorization._project_authorization_row(root, "PAUTH-TEST")
    project_authorization = implementation_authorization.validate_project_authorization_row(
        root,
        row,
        proposal_project_id="PROJECT-TEST",
        work_item_id="WI-TEST",
        spec_links=["SPEC-TEST"],
        target_paths=[target_rel],
        requested_operations=["protected_mutation"],
    )
    packet = {
        "bridge_id": bridge_id,
        "created_at": "2026-08-11T00:00:00Z",
        "expires_at": "2099-08-11T00:00:00Z",
        "go_file": go_rel,
        "latest_status": "GO",
        "project_authorization": project_authorization,
        "proposal_file": proposal_rel,
        "schema_version": 2,
        "spec_links": ["SPEC-TEST"],
        "target_path_globs": [target_rel],
    }
    packet["packet_hash"] = module.packet_hash(packet)
    pre_start_hash = packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = {
        "schema_version": 2,
        "bridge_id": bridge_id,
        "finalized_at": "2026-08-11T00:00:00Z",
        "session_id": "wi6183-worker-session",
        "pre_start_packet_hash": pre_start_hash,
        "target_path_globs": [target_rel],
        "work_intent_claim": {
            "thread_slug": bridge_id,
            "session_id": "wi6183-worker-session",
            "claim_kind": "go_implementation",
            "acting_role": "prime-builder",
            "session_envelope_id": "SENV-wi6183-worker-session",
            "acting_role_attestation": "role-attestation:SENV-wi6183-worker-session:1:0123456789abcdef",
            "project_id": "PROJECT-TEST",
        },
        "role_attestation": {
            "schema_version": 1,
            "invoking_context": "wi6183-worker-session",
            "session_envelope_id": "SENV-wi6183-worker-session",
            "subject": "gtkb",
            "init_command_digest": "test-init-command-digest",
            "binding_created_at": "2026-08-11T00:00:00Z",
            "role": "prime-builder",
            "source_event": "exact_init",
            "issuer": "test/exact-init",
            "attested_at": "2026-08-11T00:00:00Z",
            "evidence_reference": "role-attestation:SENV-wi6183-worker-session:1:0123456789abcdef",
        },
        "project_authorization_decision": {"allowed": True},
    }
    packet["packet_hash"] = module.packet_hash(packet)
    packet_path = root / ".gtkb-state" / "implementation-authorizations" / "by-bridge" / f"{bridge_id}.json"
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    subprocess.run(["git", "add", "--", verdict_rel], cwd=root, check=True)
    return bridge_id, target_rel


def test_wi6183_transaction_uses_one_effective_snapshot_for_compliance_and_pauth(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    bridge_id, target_rel = _wi6183_transaction_fixture(tmp_path, module)
    consumer_roots: list[tuple[str, Path]] = []
    pauth_results = []
    real_audit = module._run_snapshot_compliance_audit
    real_validate = module.validate_packet_project_authorization_operation

    def recording_audit(*, snapshot, candidate_path: str, content: str):
        assert snapshot.ledger["groundtruth.db"].pauth_read_snapshot is not None
        consumer_roots.append(("compliance", snapshot.root))
        return real_audit(snapshot=snapshot, candidate_path=candidate_path, content=content)

    def recording_validate(
        root: Path,
        packet: dict,
        *,
        requested_operations: list[str],
        target_paths: list[str],
    ):
        assert (root / "groundtruth.db").is_file()
        consumer_roots.append(("pauth", root))
        result = real_validate(
            root,
            packet,
            requested_operations=requested_operations,
            target_paths=target_paths,
        )
        pauth_results.append(result)
        return result

    monkeypatch.setattr(module, "_run_snapshot_compliance_audit", recording_audit)
    monkeypatch.setattr(module, "validate_packet_project_authorization_operation", recording_validate)
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda *args, **kwargs: [])

    with module._index_snapshot(tmp_path) as snapshot:
        evidence, errors, candidate_path = module._load_transaction_verified_evidence(
            tmp_path,
            [target_rel],
            snapshot,
        )

    assert evidence is not None
    assert evidence[0] == bridge_id
    assert candidate_path == f"bridge/{bridge_id}-004.md"
    assert [kind for kind, _root in consumer_roots] == ["compliance", "pauth"]
    assert consumer_roots[0][1] == consumer_roots[1][1]
    assert pauth_results[0]["id"] == "PAUTH-TEST"
    assert errors == []
    assert not consumer_roots[0][1].exists()


@pytest.mark.parametrize(
    "exit_kind",
    ["evaluator-denial", "evaluator-exception", "evaluator-timeout", "outer-exception"],
)
def test_wi6183_transaction_consumer_failures_clean_projection_and_sidecars(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    exit_kind: str,
) -> None:
    module = _load_module()
    bridge_id, target_rel = _wi6183_transaction_fixture(tmp_path, module)
    cleanup_paths: list[Path] = []
    real_cleanup = module._remove_pauth_projection

    def recording_cleanup(path: Path, identity, sidecar_identities) -> None:
        cleanup_paths.append(path)
        real_cleanup(path, identity, sidecar_identities)

    monkeypatch.setattr(module, "_remove_pauth_projection", recording_cleanup)
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda *args, **kwargs: [])
    if exit_kind != "outer-exception":
        if exit_kind == "evaluator-denial":
            injected = module.BridgeComplianceError("injected evaluator denial")
        elif exit_kind == "evaluator-exception":
            injected = OSError("injected evaluator exception")
        else:
            injected = subprocess.TimeoutExpired("injected evaluator", 1)

        def faulting_audit(**_kwargs):
            raise injected

        monkeypatch.setattr(module, "_run_snapshot_compliance_audit", faulting_audit)
        with module._index_snapshot(tmp_path) as snapshot:
            evidence, errors, candidate_path = module._load_transaction_verified_evidence(
                tmp_path,
                [target_rel],
                snapshot,
            )
        assert evidence is None
        assert candidate_path == f"bridge/{bridge_id}-004.md"
        assert any("VERIFIED candidate bridge-compliance audit failed" in error for error in errors)
    else:
        monkeypatch.setattr(
            module,
            "_load_finalized_packet",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("injected outer exception")),
        )
        with (
            module._index_snapshot(tmp_path) as snapshot,
            pytest.raises(RuntimeError, match="injected outer exception"),
        ):
            module._load_transaction_verified_evidence(tmp_path, [target_rel], snapshot)

    assert cleanup_paths
    for destination in cleanup_paths:
        for suffix in ("", "-journal", "-wal", "-shm"):
            assert not Path(str(destination) + suffix).exists()


def test_wi6183_non_pauth_transaction_does_not_open_projection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    selected_paths, report, verdict = _write_transaction_chain(tmp_path, module, monkeypatch)
    _stage_transaction(tmp_path, selected_paths, report, verdict)

    def unexpected_pauth_snapshot(*args, **kwargs):
        raise AssertionError("non-PAUTH transaction must not open a PAUTH read snapshot")

    monkeypatch.setattr(module, "_pauth_read_snapshot", unexpected_pauth_snapshot)
    monkeypatch.setattr(module, "validate_verdict_evidence_anchors", lambda *args, **kwargs: [])

    with module._index_snapshot(tmp_path) as snapshot:
        _evidence, _errors, candidate_path = module._load_transaction_verified_evidence(
            tmp_path,
            selected_paths,
            snapshot,
        )

    assert candidate_path == verdict


# --- WI-5998: parallel ledger verification -----------------------------------
#
# The per-entry verification loop is dispatched through a thread pool. These
# tests pin the three properties the parallelisation must not break: outcomes
# are identical to serial at every worker count, no worker exception is
# swallowed, and the reported failure is deterministic when several entries
# drift at once.

_WORKER_COUNTS = (1, 2, 8)


def _ledger_snapshot(module, root, files):
    """Build a snapshot whose ledger truthfully describes files on disk."""
    ledger = {}
    for rel, payload in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        info = path.stat()
        ledger[rel] = SimpleNamespace(
            mode="100644",
            sha256=hashlib.sha256(payload).hexdigest(),
            size=info.st_size,
            device=info.st_dev,
            inode=info.st_ino,
            link_count=info.st_nlink,
            oid="0" * 40,
            content_exempt=False,
            pauth_read_snapshot=None,
        )
    return SimpleNamespace(root=root, ledger=ledger, pauth_source_identity=None)


def _verify_outcome(module, snapshot, workers):
    """Return None on accept, or the GateError message on reject."""
    try:
        module._verify_ledger_entries(snapshot, max_workers=workers)
    except module.GateError as exc:
        return str(exc)
    return None


@pytest.mark.parametrize("workers", _WORKER_COUNTS)
def test_clean_ledger_verifies_at_every_worker_count(tmp_path, workers):
    module = _load_module()
    snapshot = _ledger_snapshot(module, tmp_path, {f"f{i}.txt": f"payload-{i}".encode() for i in range(24)})
    assert _verify_outcome(module, snapshot, workers) is None


@pytest.mark.parametrize("workers", _WORKER_COUNTS)
@pytest.mark.parametrize("drift", ["bytes", "size", "inode", "link_count", "missing", "exempt_metadata"])
def test_each_drift_class_still_fails_closed(tmp_path, workers, drift):
    module = _load_module()
    root = tmp_path / drift
    root.mkdir()
    snapshot = _ledger_snapshot(module, root, {f"f{i}.txt": f"payload-{i}".encode() for i in range(12)})
    entry = snapshot.ledger["f5.txt"]

    if drift == "bytes":
        (root / "f5.txt").write_bytes(b"tampered-payload-of-same-length!!")
        entry.size = (root / "f5.txt").stat().st_size
        entry.inode = (root / "f5.txt").stat().st_ino
    elif drift == "size":
        entry.size += 1
    elif drift == "inode":
        entry.inode += 1
    elif drift == "link_count":
        entry.link_count += 1
    elif drift == "missing":
        (root / "f5.txt").unlink()
    elif drift == "exempt_metadata":
        entry.content_exempt = True
        entry.oid = ""

    message = _verify_outcome(module, snapshot, workers)
    assert message is not None, f"drift class {drift!r} was not detected at {workers} worker(s)"


def test_parallel_outcome_matches_serial_for_every_drift_class(tmp_path):
    """Equivalence: parallel dispatch must accept and reject exactly as serial does."""
    module = _load_module()
    for drift in ("bytes", "size", "inode", "missing", "clean"):
        serial_root = tmp_path / f"serial-{drift}"
        parallel_root = tmp_path / f"parallel-{drift}"
        outcomes = []
        for root, workers in ((serial_root, 1), (parallel_root, 8)):
            root.mkdir()
            snapshot = _ledger_snapshot(module, root, {f"f{i}.txt": f"payload-{i}".encode() for i in range(16)})
            if drift == "bytes":
                (root / "f3.txt").write_bytes(b"different-bytes-entirely")
            elif drift == "size":
                snapshot.ledger["f3.txt"].size += 7
            elif drift == "inode":
                snapshot.ledger["f3.txt"].inode += 7
            elif drift == "missing":
                (root / "f3.txt").unlink()
            outcomes.append(_verify_outcome(module, snapshot, workers))
        serial_outcome, parallel_outcome = outcomes
        assert serial_outcome == parallel_outcome, (
            f"drift class {drift!r}: serial produced {serial_outcome!r} but parallel produced {parallel_outcome!r}"
        )


def test_reported_failure_is_deterministic_across_workers_and_runs(tmp_path):
    """With several entries drifting at once, the reported entry must be stable.

    ``as_completed`` yields in completion order, so without explicit ordering the
    reported entry would vary run to run. The implementation re-raises the
    failure earliest in ledger order; this pins that.
    """
    module = _load_module()
    messages = set()
    for run in range(3):
        for workers in _WORKER_COUNTS:
            root = tmp_path / f"multi-{run}-{workers}"
            root.mkdir()
            snapshot = _ledger_snapshot(
                module,
                root,
                {f"f{i:02d}.txt": f"payload-{i}".encode() for i in range(20)},
            )
            for rel in ("f03.txt", "f11.txt", "f17.txt"):
                snapshot.ledger[rel].size += 3
            messages.add(_verify_outcome(module, snapshot, workers))
    assert len(messages) == 1, f"failure report was not deterministic; saw {sorted(messages)}"
    assert "f03.txt" in messages.pop(), "the earliest drifting ledger entry should be the reported one"


def test_worker_count_is_derived_capped_and_overridable():
    module = _load_module()
    assert module._ledger_verify_worker_count(1) == 1
    assert module._ledger_verify_worker_count(100_000) == module._LEDGER_VERIFY_WORKER_CAP
    assert module._ledger_verify_worker_count(100_000, 1) == 1
    assert module._ledger_verify_worker_count(4) <= 4
