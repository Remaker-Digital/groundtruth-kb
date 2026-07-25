"""Tests for the frozen GT-KB modernization release-candidate contract."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "check_modernization_release_candidate.py"
RELEASE_GATE_PATH = REPO_ROOT / "scripts" / "release_candidate_gate.py"
MANIFEST_PATH = REPO_ROOT / "config" / "governance" / "modernization-release-candidate.json"
PB_SESSION = "00000000-0000-4000-8000-000000000001"
LO_ATTEST_SESSION = "00000000-0000-4000-8000-000000000002"
LO_AUDIT_SESSION = "00000000-0000-4000-8000-000000000003"


@pytest.fixture
def checker():
    spec = importlib.util.spec_from_file_location("check_modernization_release_candidate", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_release_gate():
    spec = importlib.util.spec_from_file_location("modernization_release_gate_integration", RELEASE_GATE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _lock(checker, manifest: dict) -> dict:
    manifest["program"]["frozen_scope_digest_sha256"] = checker.scope_digest(manifest)
    return manifest


def _prepare_actor_root(manifest: dict, root: Path) -> None:
    required_paths = {
        relative for record in manifest["scope_handles"] for relative in record["implementation_evidence_paths"]
    }
    for test in manifest["acceptance_tests"]:
        required_paths.update(test["required_paths"])
    for relative in required_paths:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)


def _write_actor_envelope(
    root: Path,
    *,
    session_id: str,
    harness_id: str,
    harness_name: str,
    role: str,
    role_source: str = "dispatcher_composition",
    dispatch_run_id: str = "test-dispatch-run",
) -> None:
    _write_json(
        root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json",
        {
            "status": "open",
            "session_id": session_id,
            "harness_id": harness_id,
            "harness_name": harness_name,
            "worker_role_provenance": {
                "schema_version": 1,
                "session_id": session_id,
                "harness_id": harness_id,
                "harness_name": harness_name,
                "role": role,
                "role_resolution_source": role_source,
                "dispatch_run_id": dispatch_run_id,
                "issued_at": "2026-07-13T00:00:00+00:00",
            },
        },
    )


def _fake_clean_run(checker, manifest: dict, monkeypatch, state_dir: Path, *, git_head: str = "a" * 40):
    def fake_git(_root: Path, *args: str) -> str:
        if args and args[0] == "status":
            return ""
        if args == ("rev-parse", "HEAD"):
            return git_head
        raise AssertionError(f"unexpected git query: {args}")

    def fake_process(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, stdout=f"PASS {' '.join(command)}\n")

    monkeypatch.setattr(checker, "_git_output", fake_git)
    monkeypatch.setattr(checker.subprocess, "run", fake_process)
    actor_root = state_dir / "actor-root"
    _prepare_actor_root(manifest, actor_root)
    _write_actor_envelope(
        actor_root,
        session_id=PB_SESSION,
        harness_id="A",
        harness_name="codex",
        role="prime-builder",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", PB_SESSION)
    report_path, report = checker.run_clean_acceptance(
        manifest,
        project_root=actor_root,
        state_dir=state_dir,
    )
    _write_actor_envelope(
        actor_root,
        session_id=LO_ATTEST_SESSION,
        harness_id="B",
        harness_name="claude",
        role="loyal-opposition",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_ATTEST_SESSION)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-dispatch-run")
    checker.attest_clean_run(
        manifest,
        run_id=report["run_id"],
        project_root=actor_root,
        state_dir=state_dir,
    )
    return report_path, report


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_completion_evidence(
    checker,
    manifest: dict,
    monkeypatch,
    state_dir: Path,
    reports: list[dict],
    *,
    audit_head: str | None = None,
    audit_digests: list[str] | None = None,
) -> None:
    git_head = reports[0]["git_head"]
    actor_root = state_dir / "actor-root"
    _write_actor_envelope(
        actor_root,
        session_id=LO_AUDIT_SESSION,
        harness_id="B",
        harness_name="claude",
        role="loyal-opposition",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_AUDIT_SESSION)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-dispatch-run")
    audit_path, audit = checker.issue_independent_audit(
        manifest,
        findings=[],
        state_dir=state_dir,
        project_root=actor_root,
    )
    if audit_head is not None or audit_digests is not None:
        audit["git_head"] = audit_head or git_head
        audit["clean_run_report_sha256s"] = (
            audit_digests if audit_digests is not None else [report["report_sha256"] for report in reports]
        )
        audit["audit_sha256"] = checker._record_digest(audit, "audit_sha256")
        _write_json(audit_path, audit)
        return
    assert audit_path.is_file()


def test_canonical_manifest_is_structurally_valid_and_covers_94_handles(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)

    assert checker.validate_manifest(manifest, project_root=REPO_ROOT, require_test_paths=True) == []
    expanded = [handle for family in manifest["scope_families"] for handle in checker._expanded_handles(family)]
    assert expanded == [record["id"] for record in manifest["scope_handles"]]
    assert len(expanded) == len(set(expanded)) == 94
    assert all(record["objective"] for record in manifest["scope_handles"])
    assert all(record["implementation_evidence_paths"] for record in manifest["scope_handles"])
    assert all(record["acceptance_test_ids"] for record in manifest["scope_handles"])
    assert len(manifest["capabilities"]) == 8
    assert len(manifest["acceptance_tests"]) == 15


def test_scope_mutation_without_owner_relock_fails_digest(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    manifest["capabilities"][0]["objective"] += " silently changed"

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert any("frozen_scope_digest_sha256 mismatch" in error for error in errors)


def test_every_scope_family_requires_exactly_one_capability(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    manifest["capabilities"].pop()
    _lock(checker, manifest)

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert "capabilities must map every scope family exactly once" in errors


def test_missing_explicit_handle_record_fails_closed(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    removed = manifest["scope_handles"].pop(10)
    _lock(checker, manifest)

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert any(removed["id"] in error and "lack explicit records" in error for error in errors)


def test_duplicate_explicit_handle_record_fails_closed(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    manifest["scope_handles"].append(dict(manifest["scope_handles"][0]))
    _lock(checker, manifest)

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert any("duplicate scope handle records: MOD-P01" in error for error in errors)


def test_unmapped_explicit_handle_record_fails_closed(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    manifest["scope_handles"][0]["acceptance_test_ids"] = []
    _lock(checker, manifest)

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert "scope_handles[0].acceptance_test_ids must be non-empty" in errors


def test_empty_handle_implementation_evidence_fails_closed(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    manifest["scope_handles"][0]["implementation_evidence_paths"] = []
    _lock(checker, manifest)

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert "scope_handles[0].implementation_evidence_paths must be non-empty" in errors


def test_handle_cannot_map_to_another_familys_acceptance_test(checker):
    manifest = checker.load_manifest(MANIFEST_PATH)
    manifest["scope_handles"][0]["acceptance_test_ids"] = ["AT-GIT-LIFECYCLE"]
    _lock(checker, manifest)

    errors = checker.validate_manifest(manifest, project_root=REPO_ROOT)

    assert any("is not mapped to family 'PROGRAM'" in error for error in errors)


def test_required_acceptance_path_absence_is_an_honest_blocker(checker, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)

    errors = checker.validate_manifest(manifest, project_root=tmp_path, require_test_paths=True)

    assert any("acceptance test path is missing" in error for error in errors)


def test_status_requires_two_runner_generated_clean_runs_and_candidate_bound_closure(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    state_dir = tmp_path / ".gtkb-state" / "modernization-release-candidate"
    reports = [_fake_clean_run(checker, manifest, monkeypatch, state_dir)[1] for _ in range(2)]
    _write_completion_evidence(checker, manifest, monkeypatch, state_dir, reports)

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=state_dir)

    assert status["ready"] is True
    assert status["qualifying_clean_passes"] == 2
    assert status["qualifying_git_head"] == "a" * 40
    assert status["qualifying_clean_run_report_sha256s"] == [report["report_sha256"] for report in reports]


def test_minimal_fabricated_clean_reports_do_not_qualify(checker, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    runs_dir = tmp_path / "runs"
    _write_json(
        runs_dir / "fabricated.json",
        {
            "schema_version": 1,
            "scope_digest_sha256": checker.scope_digest(manifest),
            "git_head": "a" * 40,
            "status": "pass",
            "complete": True,
            "clean_state_before": True,
            "clean_state_after": True,
            "results": [{"test_id": item["id"], "status": "pass"} for item in manifest["acceptance_tests"]],
        },
    )

    assert checker._qualifying_runs(manifest, tmp_path) == {}


def test_complete_self_hashed_report_without_independent_receipt_does_not_qualify(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    (tmp_path / "attestations" / f"{report['run_id']}.json").unlink()

    assert (
        checker._validate_run_report(manifest, {**report, "_path": str(report_path)}, tmp_path, now=datetime.now(UTC))
        == []
    )
    assert checker._qualifying_runs(manifest, tmp_path) == {}


def test_duplicate_clean_report_counts_only_once(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    duplicate_path = report_path.with_name("duplicate.json")
    duplicate_path.write_bytes(report_path.read_bytes())

    by_head = checker._qualifying_runs(manifest, tmp_path)

    assert len(by_head[report["git_head"]]) == 1


def test_stale_clean_report_does_not_qualify(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    stale_start = datetime.now(UTC) - timedelta(days=30)
    report["started_at"] = stale_start.isoformat()
    report["completed_at"] = (stale_start + timedelta(minutes=1)).isoformat()
    for result in report["results"]:
        result["started_at"] = stale_start.isoformat()
        result["completed_at"] = stale_start.isoformat()
        result["elapsed_seconds"] = 0.0
    report["report_sha256"] = checker._report_digest(report)
    _write_json(report_path, report)

    assert checker._qualifying_runs(manifest, tmp_path, now=datetime.now(UTC)) == {}


def test_wrong_head_independent_audit_blocks_completion(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_completion_evidence(checker, manifest, monkeypatch, tmp_path, reports, audit_head="b" * 40)

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert status["ready"] is False
    assert "independent modernization audit does not bind the twice-passing Git HEAD" in status["blockers"]


def test_audit_must_bind_the_exact_qualifying_report_digests(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_completion_evidence(
        checker,
        manifest,
        monkeypatch,
        tmp_path,
        reports,
        audit_digests=["0" * 64, "1" * 64],
    )

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert status["ready"] is False
    assert "independent modernization audit does not bind the qualifying clean-run evidence" in status["blockers"]


def test_incomplete_result_set_does_not_qualify(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    report["results"].pop()
    report["report_sha256"] = checker._report_digest(report)
    _write_json(report_path, report)

    assert checker._qualifying_runs(manifest, tmp_path) == {}


def test_tampered_command_does_not_qualify(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    report["results"][0]["command"].append("--fabricated")
    report["report_sha256"] = checker._report_digest(report)
    _write_json(report_path, report)

    assert checker._qualifying_runs(manifest, tmp_path) == {}


def test_tampered_output_evidence_does_not_qualify(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    _report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    evidence_path = tmp_path / report["results"][0]["evidence"]["path"]
    evidence_path.write_text("fabricated output\n", encoding="utf-8")

    assert checker._qualifying_runs(manifest, tmp_path) == {}


def test_result_timestamp_outside_run_interval_does_not_qualify(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    report["results"][0]["started_at"] = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    report["report_sha256"] = checker._report_digest(report)
    _write_json(report_path, report)

    assert checker._qualifying_runs(manifest, tmp_path) == {}


def test_open_p2_finding_blocks_completion(checker, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    audit = {
        "schema_version": 5,
        "issuer": "scripts/check_modernization_release_candidate.py:record-audit",
        "sequence": 1,
        "predecessor_audit_sha256": None,
        "issued_at": datetime.now(UTC).isoformat(),
        "scope_digest_sha256": checker.scope_digest(manifest),
        "git_head": None,
        "clean_run_report_sha256s": [],
        "attestation_receipt_sha256s": [],
        "independence": {"independently_reviewed": True},
        "findings": [{"id": "F-1", "severity": "P2", "status": "open"}],
    }
    audit["audit_sha256"] = checker._record_digest(audit, "audit_sha256")
    _write_json(state_dir / "audits" / "000001.json", audit)

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=state_dir)

    assert status["ready"] is False
    assert any("blocking finding is not closed: F-1" in blocker for blocker in status["blockers"])


def test_clean_runner_rejects_dirty_worktree_before_commands(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    monkeypatch.setattr(checker, "validate_manifest", lambda *args, **kwargs: [])
    monkeypatch.setattr(checker, "_git_output", lambda *args, **kwargs: " M source.py")

    with pytest.raises(checker.ManifestError, match="entirely clean"):
        checker.run_clean_acceptance(manifest, project_root=tmp_path, state_dir=tmp_path / "state")


def test_clean_runner_requires_runtime_issued_prime_builder_identity(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    monkeypatch.setattr(checker, "validate_manifest", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        checker,
        "_git_output",
        lambda _root, *args: "" if args and args[0] == "status" else "a" * 40,
    )
    monkeypatch.delenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", raising=False)

    with pytest.raises(checker.ManifestError, match="runtime-issued active session UUID"):
        checker.run_clean_acceptance(manifest, project_root=tmp_path, state_dir=tmp_path / "state")


def test_clean_runner_rejects_forged_role_envelope(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    monkeypatch.setattr(checker, "validate_manifest", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        checker,
        "_git_output",
        lambda _root, *args: "" if args and args[0] == "status" else "a" * 40,
    )
    _write_actor_envelope(
        tmp_path,
        session_id=PB_SESSION,
        harness_id="A",
        harness_name="codex",
        role="loyal-opposition",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", PB_SESSION)

    with pytest.raises(checker.ManifestError, match="active prime-builder session"):
        checker.run_clean_acceptance(manifest, project_root=tmp_path, state_dir=tmp_path / "state")


def test_incomplete_self_hashed_audit_cannot_complete_engineering_evidence(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_json(
        tmp_path / "audits" / "000001.json",
        {
            "schema_version": 5,
            "sequence": 1,
            "predecessor_audit_sha256": None,
            "scope_digest_sha256": checker.scope_digest(manifest),
            "git_head": "a" * 40,
            "clean_run_report_sha256s": [item["report_sha256"] for item in reports],
            "findings": [],
        },
    )
    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert status["ready"] is False
    assert "independent modernization audit 1 digest is invalid" in status["blockers"]


def test_independent_audit_uses_append_only_successors(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    assert len(reports) == 2
    actor_root = tmp_path / "actor-root"
    _write_actor_envelope(
        actor_root,
        session_id=LO_AUDIT_SESSION,
        harness_id="B",
        harness_name="claude",
        role="loyal-opposition",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_AUDIT_SESSION)
    first_path, first = checker.issue_independent_audit(
        manifest,
        findings=[{"id": "F-1", "severity": "P2", "status": "open"}],
        state_dir=tmp_path,
        project_root=actor_root,
    )
    with pytest.raises(checker.ManifestError, match="omits predecessor finding: F-1"):
        checker.issue_independent_audit(
            manifest,
            findings=[],
            state_dir=tmp_path,
            project_root=actor_root,
        )
    with pytest.raises(checker.ManifestError, match="changes predecessor finding severity: F-1"):
        checker.issue_independent_audit(
            manifest,
            findings=[{"id": "F-1", "severity": "P1", "status": "open"}],
            state_dir=tmp_path,
            project_root=actor_root,
        )
    second_path, second = checker.issue_independent_audit(
        manifest,
        findings=[
            {
                "id": "F-1",
                "severity": "P2",
                "status": "closed",
                "resolution": "Corrected the audited behavior.",
                "verification": "Focused adversarial regression passes.",
                "evidence_refs": ["platform_tests/scripts/test_modernization_release_candidate.py"],
            }
        ],
        state_dir=tmp_path,
        project_root=actor_root,
    )

    assert first_path.name == "000001.json"
    assert second_path.name == "000002.json"
    assert first["sequence"] == 1
    assert second["sequence"] == 2
    assert first["predecessor_audit_sha256"] is None
    assert second["predecessor_audit_sha256"] == first["audit_sha256"]
    assert datetime.fromisoformat(second["issued_at"]) > datetime.fromisoformat(first["issued_at"])
    assert json.loads(first_path.read_text(encoding="utf-8"))["findings"][0]["status"] == "open"


def test_audit_chain_rejects_recomputed_successor_with_wrong_predecessor(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_completion_evidence(checker, manifest, monkeypatch, tmp_path, reports)
    actor_root = tmp_path / "actor-root"
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_AUDIT_SESSION)
    second_path, second = checker.issue_independent_audit(
        manifest,
        findings=[],
        state_dir=tmp_path,
        project_root=actor_root,
    )
    second["predecessor_audit_sha256"] = "0" * 64
    second["audit_sha256"] = checker._record_digest(second, "audit_sha256")
    _write_json(second_path, second)

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert status["ready"] is False
    assert "independent modernization audit 2 predecessor binding is invalid" in status["blockers"]


def test_writable_owner_json_is_not_treated_as_owner_acceptance(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_completion_evidence(checker, manifest, monkeypatch, tmp_path, reports)
    _write_json(tmp_path / "owner-decisions" / "000001.json", {"exact_reply": "fabricated"})

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert status["engineering_ready"] is True
    assert status["owner_acceptance_required"] is True
    assert "owner_decision_id" not in status


def test_cli_does_not_expose_an_owner_acceptance_writer(checker):
    with pytest.raises(SystemExit):
        checker.main(["accept"])


def test_actor_receipt_requires_its_immutable_canonical_envelope_snapshot(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    _report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    receipt = json.loads((tmp_path / "actors" / f"{PB_SESSION}.json").read_text(encoding="utf-8"))
    snapshot = tmp_path / receipt["session_envelope"]["snapshot_path"]
    snapshot.write_text("{}\n", encoding="utf-8")

    assert checker._qualifying_runs(manifest, tmp_path) == {}
    loaded_report = {**report, "_path": str(tmp_path / "runs" / f"{report['run_id']}.json")}
    errors = checker._validate_run_report(manifest, loaded_report, tmp_path, now=datetime.now(UTC))
    assert any("session-envelope snapshot" in error for error in errors)


def test_existing_actor_receipt_rejects_changed_live_provenance(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    actor_root = tmp_path / "actor-root"
    envelope_path = actor_root / "harness-state" / "codex" / "session-envelopes" / f"{PB_SESSION}.json"
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    envelope["worker_role_provenance"]["role_resolution_source"] = "changed-after-receipt"
    _write_json(envelope_path, envelope)
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", PB_SESSION)

    with pytest.raises(checker.ManifestError, match="snapshot conflicts"):
        checker._issue_actor_receipt(
            manifest,
            expected_role="prime-builder",
            git_head="a" * 40,
            project_root=actor_root,
            state_dir=tmp_path,
        )


def test_attestation_rejects_same_session_as_runner(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    _report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    (tmp_path / "attestations" / f"{report['run_id']}.json").unlink()
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", PB_SESSION)

    with pytest.raises(checker.ManifestError, match="active loyal-opposition dispatcher session"):
        checker.attest_clean_run(
            manifest,
            run_id=report["run_id"],
            project_root=tmp_path / "actor-root",
            state_dir=tmp_path,
        )


def test_audit_rejects_same_session_as_run_attester(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    assert len(reports) == 2
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_ATTEST_SESSION)

    with pytest.raises(checker.ManifestError, match="session distinct from runners and run attesters"):
        checker.issue_independent_audit(
            manifest,
            findings=[],
            project_root=tmp_path / "actor-root",
            state_dir=tmp_path,
        )


def test_audit_rejects_role_shaped_envelope_without_dispatcher_authority(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    assert len(reports) == 2
    actor_root = tmp_path / "actor-root"
    _write_actor_envelope(
        actor_root,
        session_id=LO_AUDIT_SESSION,
        harness_id="B",
        harness_name="claude",
        role="loyal-opposition",
        role_source="runtime-issued-test-envelope",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_AUDIT_SESSION)
    monkeypatch.setenv("GTKB_BRIDGE_POLLER_RUN_ID", "test-dispatch-run")

    with pytest.raises(checker.ManifestError, match="dispatcher_composition"):
        checker.issue_independent_audit(
            manifest,
            findings=[],
            project_root=actor_root,
            state_dir=tmp_path,
        )


def test_audit_rejects_dispatch_envelope_outside_its_child_environment(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    assert len(reports) == 2
    actor_root = tmp_path / "actor-root"
    _write_actor_envelope(
        actor_root,
        session_id=LO_AUDIT_SESSION,
        harness_id="B",
        harness_name="claude",
        role="loyal-opposition",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_AUDIT_SESSION)
    monkeypatch.delenv("GTKB_BRIDGE_POLLER_RUN_ID", raising=False)

    with pytest.raises(checker.ManifestError, match="dispatch environment"):
        checker.issue_independent_audit(
            manifest,
            findings=[],
            project_root=actor_root,
            state_dir=tmp_path,
        )


def test_attestation_is_append_only(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    _report_path, report = _fake_clean_run(checker, manifest, monkeypatch, tmp_path)
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_ATTEST_SESSION)

    with pytest.raises(checker.ManifestError, match="execution receipt already exists"):
        checker.attest_clean_run(
            manifest,
            run_id=report["run_id"],
            project_root=tmp_path / "actor-root",
            state_dir=tmp_path,
        )


def test_clean_run_id_collision_fails_closed(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    fixed = datetime.now(UTC)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed if tz is not None else fixed.replace(tzinfo=None)

    monkeypatch.setattr(checker, "datetime", FrozenDateTime)
    monkeypatch.setattr(checker.uuid, "uuid4", lambda: type("FixedUUID", (), {"hex": "A" * 32})())
    _fake_clean_run(checker, manifest, monkeypatch, tmp_path)

    with pytest.raises(checker.ManifestError, match="clean acceptance run ID collision"):
        _fake_clean_run(checker, manifest, monkeypatch, tmp_path)


@pytest.mark.parametrize(
    "findings, message",
    [
        ([{"id": "F-1", "severity": "p1", "status": "closed"}], "invalid severity"),
        ([{"id": "F-1", "severity": "P1", "status": "closed"}], "resolution must be a non-empty string"),
        (
            [
                {"id": "F-1", "severity": "P3", "status": "deferred"},
                {"id": "F-1", "severity": "P3", "status": "backlogged"},
            ],
            "duplicate finding id",
        ),
    ],
)
def test_audit_rejects_malformed_finding_taxonomy(checker, monkeypatch, tmp_path, findings, message):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    assert len(reports) == 2
    _write_actor_envelope(
        tmp_path / "actor-root",
        session_id=LO_AUDIT_SESSION,
        harness_id="B",
        harness_name="claude",
        role="loyal-opposition",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", LO_AUDIT_SESSION)

    with pytest.raises(checker.ManifestError, match=message):
        checker.issue_independent_audit(
            manifest,
            findings=findings,
            project_root=tmp_path / "actor-root",
            state_dir=tmp_path,
        )


def test_audit_must_postdate_clean_runs_and_attestations(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_completion_evidence(checker, manifest, monkeypatch, tmp_path, reports)
    audit_path = tmp_path / "audits" / "000001.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit["issued_at"] = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    audit["audit_sha256"] = checker._record_digest(audit, "audit_sha256")
    _write_json(audit_path, audit)

    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert "independent modernization audit predates its clean-run or attestation evidence" in status["blockers"]


def test_status_rejects_historical_twice_passing_head(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    reports = [_fake_clean_run(checker, manifest, monkeypatch, tmp_path)[1] for _ in range(2)]
    _write_completion_evidence(checker, manifest, monkeypatch, tmp_path, reports)

    def advanced_git(_root: Path, *args: str) -> str:
        if args and args[0] == "status":
            return ""
        if args == ("rev-parse", "HEAD"):
            return "b" * 40
        raise AssertionError(args)

    monkeypatch.setattr(checker, "_git_output", advanced_git)
    status = checker.evaluate_status(manifest, project_root=REPO_ROOT, state_dir=tmp_path)

    assert status["ready"] is False
    assert status["current_git_head"] == "b" * 40
    assert status["qualifying_clean_passes"] == 0


def test_clean_runner_checks_git_state_around_each_command(checker, monkeypatch, tmp_path):
    manifest = checker.load_manifest(MANIFEST_PATH)
    monkeypatch.setattr(checker, "validate_manifest", lambda *args, **kwargs: [])
    status_calls = 0

    def changing_git(_root: Path, *args: str) -> str:
        nonlocal status_calls
        if args and args[0] == "status":
            status_calls += 1
            return " M changed.py" if status_calls == 3 else ""
        if args == ("rev-parse", "HEAD"):
            return "a" * 40
        raise AssertionError(args)

    monkeypatch.setattr(checker, "_git_output", changing_git)
    monkeypatch.setattr(
        checker.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, stdout="PASS\n"),
    )
    _write_actor_envelope(
        tmp_path,
        session_id=PB_SESSION,
        harness_id="A",
        harness_name="codex",
        role="prime-builder",
    )
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", PB_SESSION)

    with pytest.raises(checker.ManifestError, match="did not finish at the clean candidate Git HEAD"):
        checker.run_clean_acceptance(
            manifest,
            project_root=tmp_path,
            state_dir=tmp_path / "state",
        )


def test_cli_rejects_noncanonical_manifest_and_state_paths(checker, tmp_path, capsys):
    assert checker.main(["--manifest", str(tmp_path / "manifest.json"), "digest"]) == 1
    assert "canonical in-root modernization contract" in capsys.readouterr().err

    assert checker.main(["--state-dir", str(tmp_path / "state"), "status"]) == 1
    assert "canonical in-root release-candidate state directory" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# WI-5567 / TEST-11619: validate --json machine-readable evidence contract
# ---------------------------------------------------------------------------


def test_validate_plain_output_remains_unchanged(checker, capsys):
    """The human-readable form is untouched by the --json addition."""
    assert checker.main(["validate"]) == 0
    assert capsys.readouterr().out.strip() == "PASS modernization acceptance manifest (8 capabilities, 94 handles)"


def test_validate_json_emits_frozen_scope_evidence(checker, capsys):
    """--json emits the frozen digest and the inventory counts just validated."""
    assert checker.main(["validate", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    manifest = checker.load_manifest(checker.DEFAULT_MANIFEST)

    assert payload == {
        "capability_count": len(manifest["capabilities"]),
        "handle_count": manifest["program"]["expected_handle_count"],
        "require_test_paths": False,
        "result": "PASS",
        "scope_digest": checker.scope_digest(manifest),
    }
    # The emitted digest must be the frozen contract digest, not a recomputation
    # that silently drifted away from it.
    assert payload["scope_digest"] == manifest["program"]["frozen_scope_digest_sha256"]


def test_validate_json_is_deterministic_across_runs(checker, capsys):
    """Repeated invocations emit byte-identical evidence (no clock, no receipt)."""
    assert checker.main(["validate", "--json"]) == 0
    first = capsys.readouterr().out
    assert checker.main(["validate", "--json"]) == 0
    second = capsys.readouterr().out

    assert first == second


def test_validate_json_records_require_test_paths_flag(checker, capsys, monkeypatch):
    """The payload states which validation strictness produced the result."""
    monkeypatch.setattr(checker, "validate_manifest", lambda *args, **kwargs: [])

    assert checker.main(["validate", "--json", "--require-test-paths"]) == 0
    assert json.loads(capsys.readouterr().out)["require_test_paths"] is True


def test_validate_json_never_emits_pass_for_invalid_manifest(checker, capsys, monkeypatch):
    """An invalid manifest fails closed in JSON mode instead of emitting PASS."""
    monkeypatch.setattr(
        checker,
        "validate_manifest",
        lambda *args, **kwargs: ["capability CAP-1 is missing"],
    )

    assert checker.main(["validate", "--json"]) == 1
    captured = capsys.readouterr()
    assert captured.out.strip() == ""
    assert "PASS" not in captured.out
    assert "capability CAP-1 is missing" in captured.err


def test_existing_release_gate_enforces_modernization_scope_paths(monkeypatch, capsys):
    import scripts.check_modernization_release_candidate as canonical_checker

    gate = _load_release_gate()
    manifest = {"capabilities": [{"id": "CAP"}], "program": {"expected_handle_count": 94}}
    observed: dict[str, object] = {}

    monkeypatch.setattr(canonical_checker, "load_manifest", lambda _path: manifest)

    def fake_validate(payload, *, project_root, require_test_paths):
        observed.update(
            payload=payload,
            project_root=project_root,
            require_test_paths=require_test_paths,
        )
        return []

    monkeypatch.setattr(canonical_checker, "validate_manifest", fake_validate)

    gate._check_modernization_scope()

    assert observed == {
        "payload": manifest,
        "project_root": gate.PROJECT_ROOT,
        "require_test_paths": True,
    }
    assert "PASS modernization acceptance scope (1 capabilities, 94 handles)" in capsys.readouterr().out


def test_existing_release_gate_fails_when_modernization_scope_is_incomplete(monkeypatch):
    import scripts.check_modernization_release_candidate as canonical_checker

    gate = _load_release_gate()
    monkeypatch.setattr(canonical_checker, "load_manifest", lambda _path: {})
    monkeypatch.setattr(
        canonical_checker,
        "validate_manifest",
        lambda *args, **kwargs: ["acceptance test path is missing: planned.py"],
    )

    with pytest.raises(gate.GateFailure, match="planned.py"):
        gate._check_modernization_scope()
