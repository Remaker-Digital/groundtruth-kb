"""Focused tests for objective-level modernization scope traceability."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

import scripts.check_modernization_scope_semantics as checker
import scripts.collect_modernization_semantic_evidence as collector_module

HEAD = "a" * 40
PB_SESSION = "20260713T180000-prime-builder-A"
LO_SESSION = "20260713T180100-loyal-opposition-B"


def _manifest() -> dict:
    return checker.load_manifest()


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _seed_session(root: Path, *, session_id: str, harness_name: str, harness_id: str, role: str) -> Path:
    path = root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
    _write(
        path,
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
                "role_resolution_source": "test-canonical-session-envelope",
                "issued_at": "2026-07-13T18:00:00Z",
                "dispatch_run_id": session_id,
            },
        },
    )
    return path


def _collector(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    *,
    session_id: str = PB_SESSION,
    harness_name: str = "codex",
    harness_id: str = "A",
    role: str = "prime-builder",
) -> collector_module.Collector:
    _seed_session(root, session_id=session_id, harness_name=harness_name, harness_id=harness_id, role=role)
    monkeypatch.setattr(checker, "_git_head", lambda _root: HEAD)
    monkeypatch.setattr(collector_module, "_git_head", lambda _root: HEAD)
    return collector_module.Collector(
        project_root=root,
        manifest=_manifest(),
        evidence_dir=root / "semantic-evidence",
        environ={"GTKB_AUTHOR_SESSION_CONTEXT_ID": session_id},
    )


def test_all_94_handles_have_unique_exact_executable_semantic_assertions() -> None:
    manifest = _manifest()

    assert checker.validate_bindings(manifest) == []
    assert len(checker.PROOFS) == 94
    assertion_ids = [item["semantic_assertion_ids"][0] for item in manifest["scope_handles"]]
    assert len(set(assertion_ids)) == 94
    assert assertion_ids == [checker.assertion_id(item["id"]) for item in manifest["scope_handles"]]
    assert all(checker.PROOFS[item["id"]] for item in manifest["scope_handles"])
    assert "report:git:GIT-LIFECYCLE-A22" in checker.PROOFS["MOD-GL12"]
    assert "report:git:GIT-LIFECYCLE-A26" in checker.PROOFS["MOD-GL12"]


def test_clean_suite_defers_only_post_clean_proofs_and_final_keeps_all_94() -> None:
    manifest = _manifest()
    scope_test = next(item for item in manifest["acceptance_tests"] if item["id"] == "AT-SCOPE-SEMANTICS")
    expected_post_clean = {
        "MSA-MOD-P06",
        "MSA-MOD-AS08",
        "MSA-MOD-AS12",
        "MSA-MOD-AS14",
    }

    assert scope_test["command"][-2:] == ["--phase", "clean-suite"]
    assert expected_post_clean == checker.POST_CLEAN_ASSERTION_IDS
    assert len({checker.assertion_id(handle) for handle in checker.PROOFS} - checker.POST_CLEAN_ASSERTION_IDS) == 90


def test_missing_or_reused_binding_fails_closed() -> None:
    manifest = copy.deepcopy(_manifest())
    manifest["scope_handles"][1]["semantic_assertion_ids"] = manifest["scope_handles"][0]["semantic_assertion_ids"]

    errors = checker.validate_bindings(manifest)

    assert any("MOD-P02: semantic_assertion_ids" in error for error in errors)
    assert any("duplicate semantic assertion id" in error for error in errors)


def test_mod_ad09_proves_query_quarantine_and_no_historical_worker_dependency() -> None:
    result = checker.check_history_quarantine()

    assert result.status == "PASS", result.evidence
    assert result.evidence["historical_or_unresolved_worker_dependencies"] == []
    assert result.evidence["reports_absent_from_worker_dependencies"] is True
    assert set(result.evidence["explicit_query_payloads_present"]) == {
        "archival_state",
        "bridge_thread_chain",
        "deliberation_search_results",
        "history_state",
    }


def test_mod_ad09_fails_when_history_becomes_startup_payload(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config = tmp_path / "config" / "agent-control" / "activity-envelope-sharding.toml"
    config.parent.mkdir(parents=True)
    config.write_text(
        """
[classes.explicit_query]
load_policy = "session_start"
allowed_payloads = ["history_state", "bridge_thread_chain", "archival_state", "deliberation_search_results"]
[classes.never_startup]
load_policy = "forbidden_startup"
forbidden_payloads = ["raw_bridge_archival_json", "full_session_transcripts", "generated_runtime_cache_directories", "retired_aggregate_queue_artifacts"]
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        checker,
        "_artifact_report",
        lambda _root: {"status": "PASS", "audit": {"worker_references": []}},
    )

    result = checker.check_history_quarantine(tmp_path)

    assert result.status == "FAIL"


def _pilot_receipt(manifest: dict, project_root: Path, verification: Path) -> dict:
    return {
        "schema_version": 1,
        "semantic_assertion_id": "MSA-MOD-GL13",
        "scope_digest_sha256": checker.scope_digest(manifest),
        "status": "VERIFIED",
        "offline": False,
        "project_id": "PROJECT-GTKB-PLATFORM-MODERNIZATION",
        "candidate_head_sha": "a" * 40,
        "operations": sorted(checker._PILOT_OPERATIONS),
        "github_pull_request_urls": [
            "https://github.com/example/gtkb/pull/101",
            "https://github.com/example/gtkb/pull/102",
        ],
        "author_session_context_id": "pb-session",
        "verifier_session_context_id": "lo-session",
        "verifier_role": "loyal-opposition",
        "verification_artifact": {
            "path": verification.relative_to(project_root).as_posix(),
            "sha256": hashlib.sha256(verification.read_bytes()).hexdigest().upper(),
        },
    }


def test_mod_gl13_rejects_offline_simulation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    manifest = _manifest()
    verification = tmp_path / "evidence" / "verification.json"
    verification.parent.mkdir()
    verification.write_text("{}\n", encoding="utf-8")
    evidence_dir = tmp_path / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence"
    receipt = _pilot_receipt(manifest, tmp_path, verification)
    receipt["offline"] = True
    _write(evidence_dir / "git-lifecycle-modernization-pilot.json", receipt)
    monkeypatch.setattr(checker, "_git_head", lambda _root: "a" * 40)

    result = checker.check_git_modernization_pilot(
        manifest=manifest,
        project_root=tmp_path,
        evidence_dir=evidence_dir,
    )

    assert result.status == "FAIL"
    assert result.evidence["real_not_offline"] is False


def test_mod_gl13_requires_current_hash_bound_distinct_session_verification(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    manifest = _manifest()
    verification = tmp_path / "evidence" / "verification.json"
    verification.parent.mkdir()
    verification.write_text('{"status":"VERIFIED"}\n', encoding="utf-8")
    evidence_dir = tmp_path / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence"
    _write(
        evidence_dir / "git-lifecycle-modernization-pilot.json",
        _pilot_receipt(manifest, tmp_path, verification),
    )
    monkeypatch.setattr(checker, "_git_head", lambda _root: "a" * 40)

    result = checker.check_git_modernization_pilot(
        manifest=manifest,
        project_root=tmp_path,
        evidence_dir=evidence_dir,
    )

    assert result.status == "PASS", result.evidence
    assert all(result.evidence.values())


def test_collector_issued_observed_event_binds_current_head_session_and_nested_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    manifest = _manifest()
    collector = _collector(monkeypatch, tmp_path)
    plan = collector_module.Plan(
        "MOD-AS01",
        "pre-modernization-baseline",
        "assurance",
        "pytest",
        "baseline-observation",
        ("{python}", "-c", "print('measured baseline')"),
        30,
    )
    collected = collector.collect(plan)
    assert collected.status == "COLLECTED", collected.reason

    result = checker._check_receipt(
        "pre-modernization-baseline",
        semantic_assertion_id="MSA-MOD-AS01",
        manifest=manifest,
        project_root=tmp_path,
        evidence_dir=collector.evidence_dir,
    )

    assert result.status == "PASS", result.evidence
    measurement = json.loads((tmp_path / str(collected.measurement_path)).read_text(encoding="utf-8"))
    live_path = tmp_path / collector.issuer["session_envelope"]["path"]
    closed = json.loads(live_path.read_text(encoding="utf-8"))
    closed["status"] = "closed"
    _write(live_path, closed)
    assert (
        checker._check_receipt(
            "pre-modernization-baseline",
            semantic_assertion_id="MSA-MOD-AS01",
            manifest=manifest,
            project_root=tmp_path,
            evidence_dir=collector.evidence_dir,
        ).status
        == "PASS"
    )
    output_path = tmp_path / measurement["observed"]["command"]["output"]["path"]
    output_path.write_text("tampered\n", encoding="utf-8")
    assert (
        checker._check_receipt(
            "pre-modernization-baseline",
            semantic_assertion_id="MSA-MOD-AS01",
            manifest=manifest,
            project_root=tmp_path,
            evidence_dir=collector.evidence_dir,
        ).status
        == "FAIL"
    )


def test_direct_hand_authored_receipt_json_never_qualifies(tmp_path: Path) -> None:
    manifest = _manifest()
    evidence_dir = tmp_path / "semantic-evidence"
    artifact = tmp_path / "evidence" / "baseline.json"
    artifact.parent.mkdir()
    artifact.write_text('{"measurements":[]}\n', encoding="utf-8")
    _write(
        evidence_dir / "issues" / "pre-modernization-baseline" / "20260713180000-deadbeefcafe" / "receipt.json",
        {
            "schema_version": checker.RECEIPT_SCHEMA_VERSION,
            "semantic_assertion_id": "MSA-MOD-AS01",
            "scope_digest_sha256": checker.scope_digest(manifest),
            "git_head": HEAD,
            "status": "PASS",
            "issuer": {"role": "prime-builder", "session_id": PB_SESSION},
            "evidence": [
                {
                    "path": artifact.relative_to(tmp_path).as_posix(),
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest().upper(),
                }
            ],
        },
    )

    result = checker._check_receipt(
        "pre-modernization-baseline",
        semantic_assertion_id="MSA-MOD-AS01",
        manifest=manifest,
        project_root=tmp_path,
        evidence_dir=evidence_dir,
    )

    assert result.status == "FAIL"
    assert "no canonical append-only collector issue" in result.evidence


def test_production_cli_rejects_alternate_manifest_and_evidence_locations(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        checker.main(["--manifest", str(tmp_path / "alternate.json"), "validate"])
    with pytest.raises(SystemExit):
        checker.main(["run", "--evidence-dir", str(tmp_path / "alternate-evidence")])


def test_independent_verification_requires_distinct_canonical_loyal_opposition_issuer(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _seed_session(
        tmp_path,
        session_id=PB_SESSION,
        harness_name="codex",
        harness_id="A",
        role="prime-builder",
    )
    collector = _collector(
        monkeypatch,
        tmp_path,
        session_id=LO_SESSION,
        harness_name="claude",
        harness_id="B",
        role="loyal-opposition",
    )
    producer = collector_module.resolve_session_authority(
        tmp_path,
        PB_SESSION,
        evidence_dir=collector.evidence_dir,
    )
    observed = {
        "measurement_kind": "independent_audit_and_clean_run_reconciliation",
        "producer_session_context_ids": [PB_SESSION],
        "producer_authorities": [producer],
        "verifier_session_context_id": LO_SESSION,
        "verifier_role": "loyal-opposition",
    }
    monkeypatch.setattr(collector, "_measure", lambda _plan: observed)
    plan = collector_module.Plan("MOD-AS14", "independent-verification", "final", "independent-verification")

    result = collector.collect(plan)

    assert result.status == "COLLECTED", result.reason

    def receipt_check() -> checker.CheckResult:
        return checker._check_receipt(
            "independent-verification",
            semantic_assertion_id="MSA-MOD-AS14",
            manifest=_manifest(),
            project_root=tmp_path,
            evidence_dir=collector.evidence_dir,
        )

    assert receipt_check().status == "PASS"

    for session_id, harness_name in ((PB_SESSION, "codex"), (LO_SESSION, "claude")):
        live_path = tmp_path / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json"
        closed = json.loads(live_path.read_text(encoding="utf-8"))
        closed["status"] = "closed"
        _write(live_path, closed)
    assert receipt_check().status == "PASS"

    producer_snapshot = tmp_path / producer["session_envelope"]["snapshot_path"]
    with open(checker._native_io_path(producer_snapshot), "w", encoding="utf-8", newline="\n") as stream:
        stream.write('{"status":"tampered"}\n')
    assert receipt_check().status == "FAIL"

    non_independent = _collector(
        monkeypatch,
        tmp_path,
        session_id=LO_SESSION,
        harness_name="claude",
        harness_id="B",
        role="loyal-opposition",
    )
    lo_authority = collector_module.resolve_session_authority(
        tmp_path,
        LO_SESSION,
        evidence_dir=non_independent.evidence_dir,
    )
    same_session_observation = {
        **observed,
        "producer_session_context_ids": [LO_SESSION],
        "producer_authorities": [lo_authority],
    }
    monkeypatch.setattr(non_independent, "_measure", lambda _plan: same_session_observation)

    rejected = non_independent.collect(plan)

    assert rejected.status == "FAIL"
    assert "distinct canonical producer sessions" in rejected.reason


@pytest.mark.parametrize(
    "snapshot_path",
    [
        "../outside.json",
        "semantic-evidence/session-envelope-snapshots/codex/wrong-session/" + "A" * 64 + ".json",
    ],
)
def test_session_authority_rejects_noncanonical_snapshot_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    snapshot_path: str,
) -> None:
    collector = _collector(monkeypatch, tmp_path)
    authority = copy.deepcopy(collector.issuer)
    authority["session_envelope"]["snapshot_path"] = snapshot_path

    errors = checker._canonical_session_authority_errors(
        tmp_path,
        authority,
        evidence_dir=collector.evidence_dir,
    )

    assert "session envelope snapshot path is not the exact content-addressed authority path" in errors


def test_session_authority_rejects_missing_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    collector = _collector(monkeypatch, tmp_path)
    authority = copy.deepcopy(collector.issuer)
    snapshot_path = tmp_path / authority["session_envelope"]["snapshot_path"]
    Path(checker._native_io_path(snapshot_path)).unlink()

    errors = checker._canonical_session_authority_errors(
        tmp_path,
        authority,
        evidence_dir=collector.evidence_dir,
    )

    assert any("snapshot is missing or unreadable" in error for error in errors)


def test_session_authority_rejects_unsafe_harness_path_component(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    collector = _collector(monkeypatch, tmp_path)
    authority = copy.deepcopy(collector.issuer)
    authority["session"]["harness_name"] = "../codex"

    errors = checker._canonical_session_authority_errors(
        tmp_path,
        authority,
        evidence_dir=collector.evidence_dir,
    )

    assert errors == ["session authority harness_name is not a safe path component"]
