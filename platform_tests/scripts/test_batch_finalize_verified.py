from __future__ import annotations

import json
import sqlite3
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import batch_finalize_verified as batch
from scripts import bridge_work_intent_registry
from scripts import check_protected_commit_authorization as gate


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result.stdout.strip()


def _repo(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "GTKB Test")
    _git(root, "config", "user.email", "gtkb-test@example.invalid")
    (root / "candidate.txt").write_text("base\n", encoding="utf-8")
    (root / "unrelated.txt").write_text("base\n", encoding="utf-8")
    _git(root, "add", "candidate.txt", "unrelated.txt")
    _git(root, "commit", "-q", "-m", "base")
    hooks = root / ".githooks"
    hooks.mkdir()
    hook = hooks / "pre-commit"
    hook.write_text(
        "#!/bin/sh\n"
        "# scripts/check_protected_commit_authorization.py --staged\n"
        'test "$(git diff --cached --name-only)" = "candidate.txt"\n',
        encoding="utf-8",
        newline="\n",
    )
    hook.chmod(0o755)
    _git(root, "config", "core.hooksPath", ".githooks")


def _candidate(root: Path) -> batch.CandidatePlan:
    digest = batch._path_digest(root, "candidate.txt")
    return batch.CandidatePlan(
        slug="gtkb-fixture",
        verdict_path="candidate.txt",
        verdict_digest=digest,
        intended_subject="fix: finalize fixture",
        declared_paths=("candidate.txt",),
        selected_paths=("candidate.txt",),
        unchanged_declared_paths=(),
        excluded_dirty_paths=(),
        path_digests=(("candidate.txt", digest),),
        reasons=(),
    )


def _authority_packet() -> dict[str, object]:
    return {
        "packet_hash": "sha256:" + "a" * 64,
        "implementation_start": {"session_id": "prime-session"},
        "project_authorization": {"id": batch.PROJECT_AUTHORIZATION_ID, "project_id": "PROJECT-TEST"},
    }


def test_manifest_relation_allows_declared_clean_path_but_denies_undeclared_staged_path() -> None:
    assert (
        gate._transaction_manifest_relation_errors(
            ["scripts/changed.py", "platform_tests/scripts/declared_but_clean.py"],
            ["scripts/changed.py"],
        )
        == []
    )
    assert gate._transaction_manifest_relation_errors(
        ["scripts/changed.py"],
        ["scripts/changed.py", "scripts/undeclared.py"],
    ) == ["same-transaction manifest does not equal the staged path set; missing=['scripts/undeclared.py']"]


def test_report_changed_rows_exclude_a_later_foreign_dirty_path(tmp_path: Path) -> None:
    report = """## Files Changed

| Path | Insertions | Deletions |
|---|---:|---:|
| `scripts/owned.py` | 4 | 1 |

`scripts/declared-but-unchanged.py` was declared but was **not modified**.
"""
    paths, error = batch._reported_changed_paths(tmp_path, report)

    assert error is None
    assert paths == ("scripts/owned.py",)


def test_discovery_excludes_cleanup_evidence_and_non_direct_paths(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / "bridge" / "cleanup-evidence").mkdir(parents=True)
    direct = tmp_path / "bridge" / "gtkb-direct-004.md"
    nested = tmp_path / "bridge" / "cleanup-evidence" / "gtkb-orphan-004.md"
    direct.write_text("VERIFIED\n", encoding="utf-8")
    nested.write_text("VERIFIED\n", encoding="utf-8")

    assert batch.discover_terminal_verified(
        tmp_path,
        dirty_paths={
            "bridge/gtkb-direct-004.md",
            "bridge/cleanup-evidence/gtkb-orphan-004.md",
        },
    ) == ("bridge/gtkb-direct-004.md",)


def test_recovery_required_publication_is_an_explicit_skip(tmp_path: Path) -> None:
    conn = sqlite3.connect(tmp_path / "groundtruth.db")
    try:
        conn.execute(
            "CREATE TABLE sot_registry_bridge_publication_capabilities (target_path TEXT, capability_state TEXT)"
        )
        conn.execute(
            "INSERT INTO sot_registry_bridge_publication_capabilities VALUES (?, ?)",
            ("bridge/gtkb-fixture-004.md", "recovery_required"),
        )
        conn.commit()
    finally:
        conn.close()

    reason = batch._publication_reason(
        tmp_path,
        "bridge/gtkb-fixture-004.md",
        "sha256:" + "0" * 64,
    )

    assert reason == batch.SkipReason(
        "publication_capability_not_consumed",
        "bridge publication capability is not consumed ('recovery_required')",
    )


def test_readonly_database_open_never_creates_a_missing_store(tmp_path: Path) -> None:
    with pytest.raises(sqlite3.OperationalError, match="database is absent"):
        batch._open_db_readonly(tmp_path)

    assert not (tmp_path / "groundtruth.db").exists()


def test_batch_manifest_binds_candidate_head_packet_claim_and_selected_set(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    candidate = batch.CandidatePlan(
        slug="gtkb-fixture",
        verdict_path="bridge/gtkb-fixture-004.md",
        verdict_digest="sha256:" + "b" * 64,
        intended_subject="fix: fixture",
        declared_paths=("scripts/owned.py", "bridge/gtkb-fixture-004.md"),
        selected_paths=("scripts/owned.py", "bridge/gtkb-fixture-004.md"),
        unchanged_declared_paths=(),
        excluded_dirty_paths=(),
        path_digests=(),
        reasons=(),
    )
    authority = _authority_packet()
    payload = batch._manifest_payload(
        candidate=candidate,
        head_oid="a" * 40,
        head_ref="refs/heads/main",
        authority_packet=authority,
        plan_digest="sha256:" + "c" * 64,
    )
    runtime = tmp_path / gate.BATCH_FINALIZATION_REL
    runtime.mkdir(parents=True)
    manifest = runtime / "fixture.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setenv(gate.BATCH_FINALIZATION_ENV, manifest.relative_to(tmp_path).as_posix())
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "prime-session")
    monkeypatch.setattr(gate, "load_named_packet", lambda root, slug: authority)
    monkeypatch.setattr(
        bridge_work_intent_registry,
        "current_holder",
        lambda slug, project_root: {
            "session_id": "prime-session",
            "claim_kind": "go_implementation",
            "acting_role": "prime-builder",
        },
    )
    monkeypatch.setattr(gate, "validate_packet_project_authorization_operation", lambda *args, **kwargs: {})
    monkeypatch.setattr(gate, "_batch_foreign_claim_errors", lambda *args, **kwargs: [])
    monkeypatch.setattr(gate, "_resolve_head_ref", lambda *args, **kwargs: "refs/heads/main")
    monkeypatch.setattr(
        gate,
        "_staged_index_content_digest",
        lambda root, path, snapshot: ("sha256:" + "b" * 64, None),
    )
    snapshot = SimpleNamespace(
        head_oid="a" * 40,
        selected_paths=("bridge/gtkb-fixture-004.md", "scripts/owned.py"),
    )

    loaded, errors = gate._load_batch_finalization_authority(
        tmp_path,
        snapshot=snapshot,
        candidate_path="bridge/gtkb-fixture-004.md",
        bridge_id="gtkb-fixture",
        manifest_paths=["scripts/owned.py", "bridge/gtkb-fixture-004.md"],
        protected_paths=["scripts/owned.py"],
    )

    assert loaded is authority
    assert errors == []

    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "foreign-session")
    loaded, errors = gate._load_batch_finalization_authority(
        tmp_path,
        snapshot=snapshot,
        candidate_path="bridge/gtkb-fixture-004.md",
        bridge_id="gtkb-fixture",
        manifest_paths=["scripts/owned.py", "bridge/gtkb-fixture-004.md"],
        protected_paths=["scripts/owned.py"],
    )
    assert loaded is None
    assert "batch-finalization invoking session does not own the authority claim" in errors
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "prime-session")

    original_link_check = gate._path_is_linklike
    monkeypatch.setattr(gate, "_path_is_linklike", lambda path: Path(path).name == ".gtkb-state")
    loaded, errors = gate._load_batch_finalization_authority(
        tmp_path,
        snapshot=snapshot,
        candidate_path="bridge/gtkb-fixture-004.md",
        bridge_id="gtkb-fixture",
        manifest_paths=["scripts/owned.py", "bridge/gtkb-fixture-004.md"],
        protected_paths=["scripts/owned.py"],
    )
    assert loaded is None
    assert "batch-finalization manifest path is linked or escapes its governed runtime directory" in errors
    monkeypatch.setattr(gate, "_path_is_linklike", original_link_check)

    payload["selected_paths"].append("scripts/undeclared.py")
    payload["manifest_hash"] = gate._batch_manifest_hash(payload)
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    loaded, errors = gate._load_batch_finalization_authority(
        tmp_path,
        snapshot=snapshot,
        candidate_path="bridge/gtkb-fixture-004.md",
        bridge_id="gtkb-fixture",
        manifest_paths=["scripts/owned.py", "bridge/gtkb-fixture-004.md"],
        protected_paths=["scripts/owned.py"],
    )
    assert loaded is None
    assert "batch-finalization manifest selected path set differs from the copied index" in errors


def test_batch_authority_replaces_only_current_pauth_drift_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bridge_id = "gtkb-fixture"
    packet_dir = tmp_path / gate.BY_BRIDGE_PACKETS_REL
    packet_dir.mkdir(parents=True)
    target_paths = ["scripts/owned.py"]
    project_authorization = {
        "id": batch.PROJECT_AUTHORIZATION_ID,
        "project_id": "PROJECT-TEST",
        "version": 1,
        "target_classifications": [{"path": "scripts/owned.py", "mutation_class": "source"}],
    }
    packet: dict[str, object] = {
        "bridge_id": bridge_id,
        "created_at": "2026-08-08T00:00:00Z",
        "expires_at": "2099-08-08T00:00:00Z",
        "go_file": f"bridge/{bridge_id}-002.md",
        "latest_status": "GO",
        "project_authorization": project_authorization,
        "proposal_file": f"bridge/{bridge_id}-001.md",
        "schema_version": 2,
        "spec_links": ["GOV-FILE-BRIDGE-AUTHORITY-001"],
        "target_path_globs": target_paths,
    }
    packet["packet_hash"] = gate.packet_hash(packet)
    pre_start_hash = packet.pop("packet_hash")
    packet["schema_version"] = 3
    packet["implementation_start"] = {
        "schema_version": 1,
        "bridge_id": bridge_id,
        "finalized_at": "2026-08-08T00:01:00Z",
        "target_path_globs": target_paths,
        "session_id": "prime-session",
        "work_intent_claim": {
            "thread_slug": bridge_id,
            "session_id": "prime-session",
            "claim_kind": "go_implementation",
            "acting_role": "prime-builder",
            "project_id": "PROJECT-TEST",
        },
        "worker_role_provenance": {
            "schema_version": 1,
            "session_id": "prime-session",
            "role": "prime-builder",
        },
        "project_authorization_decision": {"allowed": True},
        "pre_start_packet_hash": pre_start_hash,
    }
    packet["packet_hash"] = gate.packet_hash(packet)
    (packet_dir / f"{bridge_id}.json").write_text(json.dumps(packet), encoding="utf-8")
    chain = gate._ApprovedChain(
        proposal_path=f"bridge/{bridge_id}-001.md",
        go_path=f"bridge/{bridge_id}-002.md",
        report_path=f"bridge/{bridge_id}-003.md",
        target_paths=tuple(target_paths),
    )
    monkeypatch.setattr(gate, "_packet_binding_errors", lambda *args, **kwargs: [])

    def drift(*args, **kwargs):
        raise gate.AuthorizationError("Project authorization version drifted since packet creation")

    monkeypatch.setattr(gate, "validate_packet_project_authorization_operation", drift)
    ordinary, ordinary_errors = gate._load_finalized_packet(tmp_path, bridge_id, chain, target_paths)
    assert ordinary is None
    assert any("version drifted" in error for error in ordinary_errors)

    carrier = {
        "project_authorization": {
            "id": batch.PROJECT_AUTHORIZATION_ID,
            "project_id": "PROJECT-TEST",
        }
    }
    loaded, errors = gate._load_finalized_packet(
        tmp_path,
        bridge_id,
        chain,
        target_paths,
        batch_authority_packet=carrier,
    )
    assert loaded is not None
    assert errors == []

    def revoked(*args, **kwargs):
        raise gate.AuthorizationError("Project authorization is not active")

    monkeypatch.setattr(gate, "validate_packet_project_authorization_operation", revoked)
    loaded, errors = gate._load_finalized_packet(
        tmp_path,
        bridge_id,
        chain,
        target_paths,
        batch_authority_packet=carrier,
    )
    assert loaded is None
    assert any("not active" in error for error in errors)

    monkeypatch.setattr(gate, "validate_packet_project_authorization_operation", lambda *args, **kwargs: {})
    loaded, errors = gate._load_finalized_packet(
        tmp_path,
        bridge_id,
        chain,
        target_paths,
        batch_authority_packet={"project_authorization": {"id": "PAUTH-OTHER", "project_id": "PROJECT-OTHER"}},
    )
    assert loaded is not None
    assert errors == []


def test_collision_marks_every_candidate_without_mutating_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def candidate(slug: str) -> batch.CandidatePlan:
        return batch.CandidatePlan(
            slug=slug,
            verdict_path=f"bridge/{slug}-004.md",
            verdict_digest="sha256:" + "a" * 64,
            intended_subject="fix: fixture",
            declared_paths=("scripts/shared.py",),
            selected_paths=("scripts/shared.py",),
            unchanged_declared_paths=(),
            excluded_dirty_paths=(),
            path_digests=(),
            reasons=(),
        )

    items = {
        "bridge/gtkb-one-004.md": candidate("gtkb-one"),
        "bridge/gtkb-two-004.md": candidate("gtkb-two"),
    }
    monkeypatch.setattr(batch, "_head", lambda root: "a" * 40)
    monkeypatch.setattr(batch, "_dirty_paths", lambda root: set(items))
    monkeypatch.setattr(batch, "_staged_paths", lambda root: set())
    monkeypatch.setattr(batch, "load_named_packet", lambda root, slug: _authority_packet())
    monkeypatch.setattr(batch, "discover_terminal_verified", lambda root, slug=None, dirty_paths=None: tuple(items))
    monkeypatch.setattr(
        batch,
        "_candidate_plan",
        lambda root, path, **kwargs: items[path],
    )

    plan = batch.build_plan(tmp_path)

    assert [reason.code for item in plan.candidates for reason in item.reasons] == [
        "dirty_path_collision",
        "dirty_path_collision",
    ]
    assert list(tmp_path.iterdir()) == []


def test_commit_uses_disposable_index_and_preserves_unrelated_staging(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo(tmp_path)
    head = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "candidate.txt").write_text("candidate change\n", encoding="utf-8")
    (tmp_path / "unrelated.txt").write_text("unrelated staged change\n", encoding="utf-8")
    _git(tmp_path, "add", "unrelated.txt")
    monkeypatch.setattr(batch, "_foreign_claim_collisions", lambda *args, **kwargs: {})

    commit = batch._commit_candidate(
        tmp_path,
        _candidate(tmp_path),
        authority_packet=_authority_packet(),
        plan_digest="sha256:" + "c" * 64,
        expected_head=head,
        expected_ref=batch._head_ref(tmp_path, head),
    )

    assert _git(tmp_path, "rev-parse", "HEAD") == commit
    assert _git(tmp_path, "diff-tree", "--no-commit-id", "--name-only", "-r", commit) == "candidate.txt"
    assert _git(tmp_path, "diff", "--cached", "--name-only") == "unrelated.txt"
    message = _git(tmp_path, "show", "-s", "--format=%B", commit)
    assert "Prime-operated finalization of a reviewer-authored VERIFIED verdict." in message
    assert batch.OWNER_DECISION_ID in message


def test_canonical_hook_is_pinned_even_when_local_config_is_redirected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo(tmp_path)
    head = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "candidate.txt").write_text("candidate change\n", encoding="utf-8")
    hostile = tmp_path / ".hostile-hooks"
    hostile.mkdir()
    (hostile / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8", newline="\n")
    (hostile / "pre-commit").chmod(0o755)
    _git(tmp_path, "config", "core.hooksPath", ".hostile-hooks")
    (tmp_path / ".githooks" / "pre-commit").write_text(
        "#!/bin/sh\n# scripts/check_protected_commit_authorization.py --staged\nexit 1\n",
        encoding="utf-8",
        newline="\n",
    )
    monkeypatch.setattr(batch, "_foreign_claim_collisions", lambda *args, **kwargs: {})

    with pytest.raises(batch.CandidateRefusal, match="pre-commit gate refused"):
        batch._commit_candidate(
            tmp_path,
            _candidate(tmp_path),
            authority_packet=_authority_packet(),
            plan_digest="sha256:" + "c" * 64,
            expected_head=head,
            expected_ref=batch._head_ref(tmp_path, head),
        )

    assert _git(tmp_path, "rev-parse", "HEAD") == head


def test_same_oid_symbolic_branch_switch_is_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo(tmp_path)
    head = _git(tmp_path, "rev-parse", "HEAD")
    expected_ref = batch._head_ref(tmp_path, head)
    _git(tmp_path, "branch", "other")
    _git(tmp_path, "switch", "-q", "other")
    (tmp_path / "candidate.txt").write_text("candidate change\n", encoding="utf-8")
    monkeypatch.setattr(batch, "_foreign_claim_collisions", lambda *args, **kwargs: {})

    with pytest.raises(batch.BatchFinalizationError, match="symbolic HEAD ref changed"):
        batch._commit_candidate(
            tmp_path,
            _candidate(tmp_path),
            authority_packet=_authority_packet(),
            plan_digest="sha256:" + "c" * 64,
            expected_head=head,
            expected_ref=expected_ref,
        )

    assert _git(tmp_path, "rev-parse", "HEAD") == head


def test_main_is_retired_by_owner_decision(tmp_path: Path) -> None:
    """Owner decision 2026-09-07: the batch finalizer is inert until the project-commit lifecycle slice."""
    with pytest.raises(batch.BatchFinalizationError, match="retired by owner decision"):
        batch.main(["--project-root", str(tmp_path), "plan"])


def test_hook_refusal_leaves_head_and_real_index_untouched(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo(tmp_path)
    head = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / ".githooks" / "pre-commit").write_text(
        "#!/bin/sh\n# scripts/check_protected_commit_authorization.py --staged\nexit 1\n",
        encoding="utf-8",
        newline="\n",
    )
    (tmp_path / "candidate.txt").write_text("candidate change\n", encoding="utf-8")
    (tmp_path / "unrelated.txt").write_text("unrelated staged change\n", encoding="utf-8")
    _git(tmp_path, "add", "unrelated.txt")
    index_before = (tmp_path / ".git" / "index").read_bytes()
    monkeypatch.setattr(batch, "_foreign_claim_collisions", lambda *args, **kwargs: {})

    with pytest.raises(batch.CandidateRefusal, match="pre-commit gate refused"):
        batch._commit_candidate(
            tmp_path,
            _candidate(tmp_path),
            authority_packet=_authority_packet(),
            plan_digest="sha256:" + "c" * 64,
            expected_head=head,
            expected_ref=batch._head_ref(tmp_path, head),
        )

    assert _git(tmp_path, "rev-parse", "HEAD") == head
    assert (tmp_path / ".git" / "index").read_bytes() == index_before
    assert _git(tmp_path, "diff", "--cached", "--name-only") == "unrelated.txt"
    assert not list((tmp_path / gate.BATCH_FINALIZATION_REL).glob("*.json"))


def test_post_authorization_disposable_index_tamper_is_denied(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo(tmp_path)
    head = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / ".githooks" / "pre-commit").write_text(
        "#!/bin/sh\n"
        "# scripts/check_protected_commit_authorization.py --staged\n"
        "blob=$(printf 'tampered\\n' | git hash-object -w --stdin)\n"
        "git update-index --cacheinfo 100644,$blob,candidate.txt\n",
        encoding="utf-8",
        newline="\n",
    )
    (tmp_path / "candidate.txt").write_text("candidate change\n", encoding="utf-8")
    (tmp_path / "unrelated.txt").write_text("unrelated staged change\n", encoding="utf-8")
    _git(tmp_path, "add", "unrelated.txt")
    index_before = (tmp_path / ".git" / "index").read_bytes()
    monkeypatch.setattr(batch, "_foreign_claim_collisions", lambda *args, **kwargs: {})

    with pytest.raises(batch.BatchFinalizationError, match="disposable Git index changed"):
        batch._commit_candidate(
            tmp_path,
            _candidate(tmp_path),
            authority_packet=_authority_packet(),
            plan_digest="sha256:" + "c" * 64,
            expected_head=head,
            expected_ref=batch._head_ref(tmp_path, head),
        )

    assert _git(tmp_path, "rev-parse", "HEAD") == head
    assert (tmp_path / ".git" / "index").read_bytes() == index_before
    assert _git(tmp_path, "diff", "--cached", "--name-only") == "unrelated.txt"


def test_candidate_path_already_staged_is_refused_before_commit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _repo(tmp_path)
    head = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "candidate.txt").write_text("candidate change\n", encoding="utf-8")
    _git(tmp_path, "add", "candidate.txt")
    monkeypatch.setattr(batch, "_foreign_claim_collisions", lambda *args, **kwargs: {})

    with pytest.raises(batch.CandidateRefusal, match="real staged index"):
        batch._commit_candidate(
            tmp_path,
            _candidate(tmp_path),
            authority_packet=_authority_packet(),
            plan_digest="sha256:" + "c" * 64,
            expected_head=head,
            expected_ref=batch._head_ref(tmp_path, head),
        )

    assert _git(tmp_path, "rev-parse", "HEAD") == head
    assert _git(tmp_path, "diff", "--cached", "--name-only") == "candidate.txt"
