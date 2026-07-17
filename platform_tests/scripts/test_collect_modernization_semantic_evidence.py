"""Focused tests for observed modernization semantic evidence collection."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.check_modernization_scope_semantics as semantic_checker
import scripts.collect_modernization_semantic_evidence as collector_module

HEAD = "a" * 40
SESSION = "019f5ce7-b9f0-7d32-9920-687e057013b8"


def _write(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _seed_harness_state(root: Path, *, names: tuple[str, ...] = ("codex",)) -> None:
    ids = {name: chr(ord("A") + index) for index, name in enumerate(names)}
    _write(
        root / "harness-state" / "harness-identities.json",
        {
            "schema_version": 1,
            "harnesses": {name: {"id": harness_id} for name, harness_id in ids.items()},
        },
    )
    _write(
        root / "harness-state" / "harness-registry.json",
        {
            "schema_version": 1,
            "harnesses": [
                {
                    "id": harness_id,
                    "harness_name": name,
                    "status": "active",
                    "role": ["prime-builder" if name == "codex" else "loyal-opposition"],
                    "version": 1,
                }
                for name, harness_id in ids.items()
            ],
        },
    )


def _seed_session(
    root: Path,
    *,
    session_id: str = SESSION,
    harness_name: str = "codex",
    harness_id: str = "A",
    role: str = "prime-builder",
) -> Path:
    return _write(
        root / "harness-state" / harness_name / "session-envelopes" / f"{session_id}.json",
        {
            "envelope_schema_version": 1,
            "status": "open",
            "session_id": session_id,
            "harness_id": harness_id,
            "harness_name": harness_name,
            "role": role,
            "role_resolved": role,
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


@pytest.fixture
def collector(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> collector_module.Collector:
    _seed_harness_state(tmp_path)
    _seed_session(tmp_path)
    monkeypatch.setattr(collector_module, "_git_head", lambda _root: HEAD)
    monkeypatch.setattr(semantic_checker, "_git_head", lambda _root: HEAD)
    return collector_module.Collector(
        project_root=tmp_path,
        manifest=semantic_checker.load_manifest(),
        evidence_dir=tmp_path / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence",
        environ={
            "GTKB_AUTHOR_SESSION_CONTEXT_ID": SESSION,
            "GTKB_HARNESS_NAME": "forged-harness-is-ignored",
            "GTKB_ROLE": "loyal-opposition",
        },
    )


def _command_plan(*, return_code: int = 0) -> collector_module.Plan:
    return collector_module.Plan(
        "MOD-AS05",
        "six-activity-behavior-matrix",
        "assurance",
        "pytest",
        "focused-observation",
        (
            "{python}",
            "-c",
            f"import sys; print('observed objective execution'); sys.exit({return_code})",
        ),
        30,
    )


def test_exactly_26_checker_receipts_have_one_collector_plan() -> None:
    assert collector_module.validate_plan_coverage() == []
    assert len(collector_module.PLANS) == 26
    assert set(collector_module.GROUPS) == {"assurance", "final", "foundations", "harness-live", "repository"}


def test_successful_executable_measurement_binds_output_scope_head_and_runtime_provenance(
    collector: collector_module.Collector,
) -> None:
    plan = _command_plan()

    result = collector.collect(plan)

    assert result.status == "COLLECTED", result.reason
    receipt_path = collector.project_root / str(result.receipt_path)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    measurement_path = collector.project_root / receipt["measurement"]["path"]
    measurement = json.loads(measurement_path.read_text(encoding="utf-8"))
    assert receipt["scope_digest_sha256"] == semantic_checker.scope_digest(collector.manifest)
    assert receipt["git_head"] == HEAD
    assert receipt["issuer"]["service_id"] == semantic_checker.COLLECTOR_SERVICE_ID
    assert receipt["issuer"]["session"]["harness_id"] == "A"
    assert receipt["issuer"]["session"]["harness_name"] == "codex"
    assert receipt["issuer"]["session"]["role"] == "prime-builder"
    assert receipt["issuer"]["session"]["session_id"] == SESSION
    envelope_ref = receipt["issuer"]["session_envelope"]
    snapshot_path = collector.project_root / envelope_ref["snapshot_path"]
    assert Path(collector_module._native_io_path(snapshot_path)).is_file()
    assert collector_module._sha256(snapshot_path) == envelope_ref["sha256"]
    assert receipt["issue_id"] == collector.invocation_id
    assert (receipt_path.parent / "issuance.json").is_file()
    assert measurement["observed"]["command"]["return_code"] == 0
    assert collector.validate_receipt(plan) == []

    live_path = collector.project_root / envelope_ref["path"]
    closed = json.loads(live_path.read_text(encoding="utf-8"))
    closed["status"] = "closed"
    _write(live_path, closed)
    assert collector.validate_receipt(plan) == []


def test_failed_measurement_never_mints_a_pass_receipt(collector: collector_module.Collector) -> None:
    plan = _command_plan(return_code=9)

    result = collector.collect(plan)

    assert result.status == "FAIL"
    assert "exited 9" in result.reason
    assert "focused-observation" not in collector._command_cache
    assert not collector._issue_dir(plan).exists()
    assert collector._command_log_path("focused-observation").is_file()


def test_pytest_temp_path_uses_forward_slashes_in_subprocess_environment(
    collector: collector_module.Collector,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def fake_run(*_args, **kwargs):
        captured.update(kwargs["env"])
        return SimpleNamespace(returncode=0, stdout="observed\n", stderr="")

    monkeypatch.setattr(collector_module.subprocess, "run", fake_run)

    collector._run_command("portable-pytest-temp", ("{python}", "-c", "print('ok')"), 30)

    basetemp = captured["PYTEST_ADDOPTS"].split("--basetemp=", 1)[1]
    assert "\\" not in basetemp
    assert basetemp.startswith(collector.project_root.as_posix())
    assert len(Path(basetemp).parent.name) == 8
    assert (collector.project_root / ".gtkb-state" / "mrc-pytest").is_dir()


def test_live_program_reconciliation_is_executable_and_duplicate_free() -> None:
    collector = collector_module.Collector()

    predecessor = collector._program_reconciliation(collector_module.PLAN_BY_NAME["predecessor-reconciliation"])
    deduplication = collector._program_reconciliation(collector_module.PLAN_BY_NAME["work-item-advisory-deduplication"])

    assert predecessor["project_count"] == 8
    assert predecessor["active_membership_count"] >= 8
    assert predecessor["duplicate_memberships"] == {}
    assert len(predecessor["selected_source_advisories"]) == 1
    assert deduplication["work_item_assignments"] == predecessor["work_item_assignments"]


def test_pre_modernization_baseline_binds_historical_observations_and_explicit_gaps() -> None:
    collector = collector_module.Collector()

    baseline = collector._pre_baseline()

    assert baseline["measurement_kind"] == "pre_modernization_historical_baseline"
    assert baseline["cutoff"] == "2026-07-10T00:00:00+00:00"
    assert baseline["source_commit"] == "e43dc79e296d126c306468dd3af92639ce8e01dc"
    assert baseline["dimensions"]["payloads"]["harnesses"] == ["antigravity", "claude", "codex"]
    assert baseline["dimensions"]["latency"]["status"] == "OBSERVED"
    assert baseline["dimensions"]["failures"]["record_count"] == 2443
    assert baseline["dimensions"]["regressions"] == {
        "status": "OBSERVED_PROTOCOL_SMOKE",
        "passed": 6,
        "total": 6,
    }
    assert baseline["dimensions"]["tokens"]["status"] == "NOT_OBSERVED_REAL"
    assert baseline["dimensions"]["first_tool_behavior"]["status"] == "NOT_OBSERVED"
    assert baseline["dimensions"]["transcripts"]["status"] == "COMPACT_ONLY"
    for source in ("benchmark", "corpus_manifest", "token_advisory", "dispatch_advisory"):
        evidence = baseline["historical_sources"][source]
        assert len(evidence["sha256"]) == 64
        assert (collector.project_root / evidence["path"]).is_file()


def test_pre_modernization_baseline_does_not_relabel_current_telemetry_as_history(
    collector: collector_module.Collector,
) -> None:
    with pytest.raises(collector_module.MeasurementBlocked, match="historical benchmark is absent"):
        collector._pre_baseline()


def test_nested_raw_output_tampering_invalidates_an_existing_receipt(
    collector: collector_module.Collector,
) -> None:
    plan = _command_plan()
    assert collector.collect(plan).status == "COLLECTED"
    log_path = collector._command_log_path("focused-observation")
    log_path.write_text("tampered\n", encoding="utf-8")

    errors = collector.validate_receipt(plan)

    assert any("evidence path/hash mismatch" in error for error in errors)
    status = collector.status((plan,))
    assert status["counts"] == {"INVALID": 1}


def test_live_harness_requires_matching_successful_invocation_and_canonical_envelope(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _seed_harness_state(tmp_path)
    _seed_session(tmp_path)
    monkeypatch.setattr(collector_module, "_git_head", lambda _root: HEAD)
    monkeypatch.setattr(semantic_checker, "_git_head", lambda _root: HEAD)
    collector = collector_module.Collector(
        project_root=tmp_path,
        manifest=semantic_checker.load_manifest(),
        evidence_dir=tmp_path / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence",
        environ={"GTKB_AUTHOR_SESSION_CONTEXT_ID": SESSION, "GTKB_HARNESS_NAME": "codex"},
    )
    plan = collector_module.Plan(
        "MOD-HP04",
        "harness-codex-live",
        "harness-live",
        "live-harness",
        harnesses=("codex",),
    )
    invocation_session = "2026-07-13T18-00-00Z-prime-builder-A-observed"
    envelope_path = _seed_session(tmp_path, session_id=invocation_session)

    without_invocation = collector.collect(plan)
    assert without_invocation.status == "BLOCKED"
    assert not collector._issue_dir(plan).exists()

    relative_envelope = envelope_path.relative_to(tmp_path).as_posix()
    _write(
        tmp_path / ".gtkb-state" / "bridge-poller" / "dispatch-runs" / f"{invocation_session}.telemetry.json",
        {
            "schema_id": "gtkb.shim_dispatch_telemetry.v1",
            "schema_version": 1,
            "correlation": {"session_context_id": invocation_session},
            "outcome": {"exit_code": 0, "exit_status": "succeeded"},
            "worker": {
                "harness_id": "A",
                "harness_name": "codex",
                "role": "prime-builder",
                "role_source_document_id": relative_envelope,
            },
        },
    )

    def passing_parity(command_id: str, _argv: tuple[str, ...], _timeout: int) -> dict:
        log = collector._command_log_path(command_id)
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("2 passed\n", encoding="utf-8")
        return {
            "command_id": command_id,
            "argv": [sys.executable, "-m", "pytest"],
            "return_code": 0,
            "timed_out": False,
            "git_head_before": HEAD,
            "git_head_after": HEAD,
            "output": {
                "path": log.relative_to(tmp_path).as_posix(),
                "sha256": collector_module._sha256(log),
                "byte_count": log.stat().st_size,
            },
        }

    monkeypatch.setattr(collector, "_run_command", passing_parity)
    result = collector.collect(plan)

    assert result.status == "COLLECTED", result.reason
    measurement = json.loads((collector.project_root / str(result.measurement_path)).read_text(encoding="utf-8"))
    observed = measurement["observed"]["harnesses"]["codex"]
    assert observed["session_context_id"] == invocation_session
    assert observed["invocation"]["exit_status"] == "succeeded"
    assert observed["session_authority"]["session_envelope"]["path"] == relative_envelope
    snapshot_path = collector.project_root / observed["session_authority"]["session_envelope"]["snapshot_path"]
    assert Path(collector_module._native_io_path(snapshot_path)).is_file()


def test_live_harness_parity_failure_is_blocked_without_minting_a_receipt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _seed_harness_state(tmp_path)
    _seed_session(tmp_path)
    monkeypatch.setattr(collector_module, "_git_head", lambda _root: HEAD)
    monkeypatch.setattr(semantic_checker, "_git_head", lambda _root: HEAD)
    collector = collector_module.Collector(
        project_root=tmp_path,
        manifest=semantic_checker.load_manifest(),
        evidence_dir=tmp_path / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence",
        environ={"GTKB_AUTHOR_SESSION_CONTEXT_ID": SESSION, "GTKB_HARNESS_NAME": "codex"},
    )
    plan = collector_module.Plan(
        "MOD-HP04",
        "harness-codex-live",
        "harness-live",
        "live-harness",
        harnesses=("codex",),
    )
    invocation_session = "2026-07-13T18-00-00Z-prime-builder-A-parity"
    envelope_path = _seed_session(tmp_path, session_id=invocation_session)
    _write(
        tmp_path / ".gtkb-state" / "bridge-poller" / "dispatch-runs" / f"{invocation_session}.telemetry.json",
        {
            "schema_id": "gtkb.shim_dispatch_telemetry.v1",
            "correlation": {"session_context_id": invocation_session},
            "outcome": {"exit_code": 0, "exit_status": "succeeded"},
            "worker": {
                "harness_name": "codex",
                "role": "prime-builder",
                "role_source_document_id": envelope_path.relative_to(tmp_path).as_posix(),
            },
        },
    )

    def blocked_parity(*_args, **_kwargs):
        raise collector_module.MeasurementFailed("H expectation mismatch")

    monkeypatch.setattr(collector, "_run_command", blocked_parity)

    result = collector.collect(plan)

    assert result.status == "BLOCKED"
    assert "harness-parity prerequisite is blocked" in result.reason
    assert "H expectation mismatch" in result.reason
    assert not collector._issue_dir(plan).exists()


def test_program_closure_stays_blocked_until_release_status_is_ready(
    collector: collector_module.Collector,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        collector_module.release_checker,
        "evaluate_status",
        lambda *_args, **_kwargs: {"ready": False, "blockers": ["need two clean runs"]},
    )
    plan = collector_module.PLAN_BY_NAME["program-closure"]

    result = collector.collect(plan)

    assert result.status == "BLOCKED"
    assert "need two clean runs" in result.reason
    assert not collector._issue_dir(plan).exists()


def test_program_closure_uses_versioned_audit_and_leaves_owner_acceptance_external(
    collector: collector_module.Collector,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    audit_path = _write(
        collector.project_root / ".gtkb-state" / "modernization-release-candidate" / "audits" / "000001.json",
        {"schema_version": 5, "status": "PASS"},
    )
    monkeypatch.setattr(
        collector_module.release_checker,
        "evaluate_status",
        lambda *_args, **_kwargs: {"engineering_ready": True, "blockers": []},
    )
    monkeypatch.setattr(
        collector_module.release_checker,
        "_audit_records",
        lambda _state_dir: [{"_path": str(audit_path)}],
    )
    monkeypatch.setattr(
        collector,
        "_valid_receipt",
        lambda _name: {"measurement": {"path": "semantic-evidence/independent.json", "sha256": "A" * 64}},
    )

    observed = collector._program_closure()

    assert observed["independent_audit"]["path"].endswith("audits/000001.json")
    assert observed["owner_acceptance"] == "required_external_owner_decision_after_engineering_closure"
    assert not (collector.project_root / ".gtkb-state/modernization-release-candidate/owner-acceptance.json").exists()


def test_stale_git_head_invalidates_an_append_only_issue(
    collector: collector_module.Collector,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = _command_plan()
    assert collector.collect(plan).status == "COLLECTED"

    monkeypatch.setattr(semantic_checker, "_git_head", lambda _root: "b" * 40)

    errors = collector.validate_receipt(plan)
    assert any("git_head mismatch" in error for error in errors)


@pytest.mark.parametrize(
    ("field", "forged_value"),
    [
        ("session_id", "019f5ce7-b9f0-7d32-9920-687e05709999"),
        ("harness_name", "cursor"),
        ("role", "loyal-opposition"),
    ],
)
def test_forged_session_harness_or_role_is_rejected_even_when_hashes_are_rebound(
    collector: collector_module.Collector,
    field: str,
    forged_value: str,
) -> None:
    plan = _command_plan()
    result = collector.collect(plan)
    assert result.status == "COLLECTED"
    issue_dir = (collector.project_root / str(result.receipt_path)).parent
    receipt_path = issue_dir / "receipt.json"
    measurement_path = issue_dir / "measurement.json"
    issuance_path = issue_dir / "issuance.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    measurement = json.loads(measurement_path.read_text(encoding="utf-8"))
    issuance = json.loads(issuance_path.read_text(encoding="utf-8"))
    forged_issuer = json.loads(json.dumps(receipt["issuer"]))
    forged_issuer["session"][field] = forged_value
    measurement["issuer"] = forged_issuer
    _write(measurement_path, measurement)
    measurement_ref = {
        "path": measurement_path.relative_to(collector.project_root).as_posix(),
        "sha256": collector_module._sha256(measurement_path),
    }
    receipt["issuer"] = forged_issuer
    receipt["measurement"] = measurement_ref
    receipt["evidence"] = [measurement_ref]
    _write(receipt_path, receipt)
    issuance["issuer"] = forged_issuer
    issuance["measurement"] = measurement_ref
    issuance["receipt"] = {
        "path": receipt_path.relative_to(collector.project_root).as_posix(),
        "sha256": collector_module._sha256(receipt_path),
    }
    _write(issuance_path, issuance)

    errors = collector.validate_receipt(plan)

    assert any("canonical" in error or "session provenance" in error for error in errors)


def test_tampered_session_envelope_snapshot_invalidates_existing_receipt(
    collector: collector_module.Collector,
) -> None:
    plan = _command_plan()
    result = collector.collect(plan)
    assert result.status == "COLLECTED"
    receipt = json.loads((collector.project_root / str(result.receipt_path)).read_text(encoding="utf-8"))
    snapshot_path = collector.project_root / receipt["issuer"]["session_envelope"]["snapshot_path"]
    with open(collector_module._native_io_path(snapshot_path), "w", encoding="utf-8", newline="\n") as stream:
        stream.write('{"status":"tampered"}\n')

    errors = collector.validate_receipt(plan)

    assert any("snapshot path/hash mismatch" in error for error in errors)


def test_content_addressed_session_snapshot_rejects_conflicting_existing_bytes(
    collector: collector_module.Collector,
) -> None:
    authority = collector_module.resolve_session_authority(
        collector.project_root,
        SESSION,
        evidence_dir=collector.evidence_dir,
    )
    snapshot_path = collector.project_root / authority["session_envelope"]["snapshot_path"]
    with open(collector_module._native_io_path(snapshot_path), "w", encoding="utf-8", newline="\n") as stream:
        stream.write('{"conflict":true}\n')

    with pytest.raises(collector_module.CollectionError, match="conflicting bytes"):
        collector_module.resolve_session_authority(
            collector.project_root,
            SESSION,
            evidence_dir=collector.evidence_dir,
        )


def test_append_only_issue_path_refuses_overwrite(collector: collector_module.Collector) -> None:
    plan = _command_plan()
    first = collector.collect(plan)
    assert first.status == "COLLECTED"
    issue_dir = (collector.project_root / str(first.receipt_path)).parent
    before = {path.name: collector_module._sha256(path) for path in issue_dir.iterdir() if path.is_file()}

    second = collector.collect(plan)

    assert second.status == "FAIL"
    assert "append-only issue path already exists" in second.reason
    after = {path.name: collector_module._sha256(path) for path in issue_dir.iterdir() if path.is_file()}
    assert after == before


def test_missing_canonical_runtime_envelope_blocks_before_measurement(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _seed_harness_state(tmp_path)
    monkeypatch.setattr(collector_module, "_git_head", lambda _root: HEAD)
    collector = collector_module.Collector(
        project_root=tmp_path,
        manifest=semantic_checker.load_manifest(),
        evidence_dir=tmp_path / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence",
        environ={"GTKB_AUTHOR_SESSION_CONTEXT_ID": SESSION, "GTKB_ROLE": "prime-builder"},
    )
    plan = _command_plan()

    result = collector.collect(plan)

    assert result.status == "BLOCKED"
    assert "canonical runtime session provenance is unavailable" in result.reason
    assert not collector._command_log_path("focused-observation").exists()


def test_collector_cli_rejects_alternate_manifest_or_evidence_locations(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        collector_module.main(["--manifest", str(tmp_path / "alternate.json"), "status"])
    with pytest.raises(SystemExit):
        collector_module.main(["--evidence-dir", str(tmp_path / "alternate-evidence"), "status"])
