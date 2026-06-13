"""Spec-derived tests for the TAFE stuck-flow detector (WI-4505).

Covers:
- SPEC-TAFE-R3: each stuck reason is detected (expired-lease, stalled-pending,
  owner-gate-stalled, failed-unrecovered) and a self-diagnosis is produced.
- SPEC-TAFE-R6: the failed-unrecovered facet + diagnosis consume the
  ``outcome`` / ``failure_class`` / ``cleanup_result`` / ``recovery_actions``
  telemetry recorded by WI-4504.
- SPEC-TAFE-R2: expired-lease detection reads lease state and never mutates it.
- SPEC-TAFE-R5: the detector returns a structured report a future tick can
  consume while initiating nothing.
- The non-mutating invariant (``mutated=False`` + a real-DB row-count guard) and
  a structural guard asserting no recovery-actuation surface in the module.

The ``FakeFlowService`` gives precise control over stage/flow/lease/telemetry
shapes and a deterministic ``now``; the CliRunner tests exercise the real
production interface (``TypedArtifactFlowService`` + ``gt flow stuck``) against
the real schema, validating the read assumptions end-to-end.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_stuck_flow import (
    REASON_EXPIRED_LEASE,
    REASON_FAILED_UNRECOVERED,
    REASON_OWNER_GATE_STALLED,
    REASON_STALLED_PENDING,
    StuckThresholds,
    detect_stuck_flows,
    diagnose_stuck_flow,
)
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

NOW = "2026-06-13T12:00:00Z"
TWO_HOURS_AGO = "2026-06-13T10:00:00Z"  # 7200s before NOW
TWO_DAYS_AGO = "2026-06-11T12:00:00Z"  # 172800s before NOW
ONE_HOUR_HENCE = "2026-06-13T13:00:00Z"  # lease not yet expired


# ---------------------------------------------------------------------------
# Fake injected service + record builders
# ---------------------------------------------------------------------------


class FakeFlowService:
    """Minimal in-memory stand-in for the read slice the detector depends on."""

    def __init__(
        self,
        *,
        flows: list[dict[str, Any]] | None = None,
        stages: list[dict[str, Any]] | None = None,
        leases: list[dict[str, Any]] | None = None,
        telemetry: list[dict[str, Any]] | None = None,
    ) -> None:
        self._flows = list(flows or [])
        self._stages = list(stages or [])
        self._leases = list(leases or [])
        self._telemetry = list(telemetry or [])

    def list_flow_instances(
        self,
        *,
        flow_definition_id: str | None = None,
        flow_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._flows
        if status is not None:
            rows = [f for f in rows if f.get("status") == status]
        return [dict(f) for f in rows]

    def list_stage_instances(
        self, *, flow_instance_id: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        rows = self._stages
        if flow_instance_id is not None:
            rows = [s for s in rows if s.get("flow_instance_id") == flow_instance_id]
        if status is not None:
            rows = [s for s in rows if s.get("status") == status]
        return [dict(s) for s in rows]

    def list_stage_leases(
        self,
        *,
        stage_instance_id: str | None = None,
        lease_status: str | None = None,
        holder_harness_id: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._leases
        if stage_instance_id is not None:
            rows = [le for le in rows if le.get("stage_instance_id") == stage_instance_id]
        if lease_status is not None:
            rows = [le for le in rows if le.get("lease_status") == lease_status]
        if holder_harness_id is not None:
            rows = [le for le in rows if le.get("holder_harness_id") == holder_harness_id]
        return [dict(le) for le in rows]

    def list_stage_attempt_telemetry(
        self,
        *,
        flow_instance_id: str | None = None,
        stage_instance_id: str | None = None,
        outcome: str | None = None,
        failure_class: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._telemetry
        if flow_instance_id is not None:
            rows = [t for t in rows if t.get("flow_instance_id") == flow_instance_id]
        if stage_instance_id is not None:
            rows = [t for t in rows if t.get("stage_instance_id") == stage_instance_id]
        if outcome is not None:
            rows = [t for t in rows if t.get("outcome") == outcome]
        if failure_class is not None:
            rows = [t for t in rows if t.get("failure_class") == failure_class]
        return [dict(t) for t in rows]


def _flow(**overrides: Any) -> dict[str, Any]:
    base = {"id": "FLOWINST-1", "subject_type": "gtkb-platform", "subject_id": "x", "status": "running"}
    base.update(overrides)
    return base


def _stage(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "STAGEINST-1",
        "stage_id": "review",
        "flow_instance_id": "FLOWINST-1",
        "required_role": "loyal-opposition",
        "status": "pending",
        "claim_status": "unclaimed",
        "changed_at": TWO_HOURS_AGO,
        "started_at": None,
        "metadata": {},
    }
    base.update(overrides)
    return base


def _lease(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "LEASE-1",
        "stage_instance_id": "STAGEINST-1",
        "lease_status": "active",
        "holder_harness_id": "B",
        "expires_at": TWO_HOURS_AGO,
        "changed_at": TWO_HOURS_AGO,
    }
    base.update(overrides)
    return base


def _telem(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "TELEM-1",
        "flow_instance_id": "FLOWINST-1",
        "stage_instance_id": "STAGEINST-1",
        "attempt_number": 1,
        "outcome": "failure",
        "failure_class": "timeout",
        "cleanup_result": "partial",
        "recovery_actions_parsed": [],
        "changed_at": TWO_HOURS_AGO,
    }
    base.update(overrides)
    return base


def _detect(service: FakeFlowService, **kwargs: Any):
    kwargs.setdefault("now", NOW)
    return detect_stuck_flows(service, **kwargs)


# ---------------------------------------------------------------------------
# SPEC-TAFE-R3: each stuck reason is detected
# ---------------------------------------------------------------------------


def test_expired_lease_detected_read_only() -> None:
    """SPEC-TAFE-R3/R2: a held lease past expiry is flagged; lease state is read."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],
        leases=[_lease(expires_at=TWO_HOURS_AGO)],
    )
    report = _detect(service)
    assert report.mutated is False
    assert report.counts_by_reason == {REASON_EXPIRED_LEASE: 1}
    finding = report.findings[0]
    assert finding.reason == REASON_EXPIRED_LEASE
    assert finding.lease_id == "LEASE-1"
    assert finding.age_seconds == 7200
    assert "WI-4494" in finding.diagnosis  # advisory: recovery is not actuated here


def test_active_unexpired_lease_is_not_flagged() -> None:
    """A lease whose expiry is in the future is not stuck."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],
        leases=[_lease(expires_at=ONE_HOUR_HENCE)],
    )
    assert _detect(service).findings == ()


def test_stalled_pending_detected() -> None:
    """SPEC-TAFE-R3: an unclaimed non-terminal stage past the stall threshold."""
    service = FakeFlowService(flows=[_flow()], stages=[_stage(changed_at=TWO_HOURS_AGO)])
    report = _detect(service, thresholds=StuckThresholds(stalled_seconds=3600))
    assert report.counts_by_reason == {REASON_STALLED_PENDING: 1}
    assert report.findings[0].age_seconds == 7200
    assert report.findings[0].last_activity_at == TWO_HOURS_AGO


def test_stalled_pending_not_flagged_under_threshold() -> None:
    service = FakeFlowService(flows=[_flow()], stages=[_stage(changed_at=TWO_HOURS_AGO)])
    # 7200s old, threshold 1 day -> not stalled yet.
    assert _detect(service, thresholds=StuckThresholds(stalled_seconds=86400)).findings == ()


def test_owner_gate_stalled_detected_and_takes_precedence_over_stalled_pending() -> None:
    """SPEC-TAFE-R3: an owner-gate-blocked stage past its gate threshold."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(changed_at=TWO_DAYS_AGO, metadata={"owner_gate_blocked": True})],
    )
    report = _detect(
        service,
        thresholds=StuckThresholds(stalled_seconds=3600, owner_gate_stalled_seconds=86400),
    )
    # Owner-gate facet wins; not double-counted as stalled_pending.
    assert report.counts_by_reason == {REASON_OWNER_GATE_STALLED: 1}
    assert report.findings[0].age_seconds == 172800


def test_failed_unrecovered_detected_with_diagnosis_from_telemetry() -> None:
    """SPEC-TAFE-R3/R6: latest failed attempt with a failure_class and no recovery."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],  # claimed -> no stall facet, isolates telemetry facet
        telemetry=[_telem(outcome="failure", failure_class="timeout", recovery_actions_parsed=[])],
    )
    report = _detect(service)
    assert report.counts_by_reason == {REASON_FAILED_UNRECOVERED: 1}
    finding = report.findings[0]
    assert finding.failure_class == "timeout"
    assert finding.last_outcome == "failure"
    assert finding.cleanup_result == "partial"
    assert "timeout" in finding.diagnosis  # diagnosis maps the telemetry failure_class


def test_failed_with_recovery_actions_is_not_unrecovered() -> None:
    """SPEC-TAFE-R6: a recorded recovery_action means recovery was attempted."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],
        telemetry=[_telem(outcome="failure", failure_class="timeout", recovery_actions_parsed=["retry"])],
    )
    assert _detect(service).findings == ()


def test_latest_telemetry_attempt_supersedes_earlier_failure() -> None:
    """SPEC-TAFE-R6: a later successful attempt clears the failed-unrecovered facet."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],
        telemetry=[
            _telem(id="T1", attempt_number=1, outcome="failure", failure_class="timeout"),
            _telem(id="T2", attempt_number=2, outcome="success", failure_class=None),
        ],
    )
    assert _detect(service).findings == ()


def test_recovery_actions_json_string_is_parsed() -> None:
    """Telemetry recovery_actions provided as a JSON string round-trips."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],
        telemetry=[
            {
                "id": "TELEM-1",
                "flow_instance_id": "FLOWINST-1",
                "stage_instance_id": "STAGEINST-1",
                "attempt_number": 1,
                "outcome": "failure",
                "failure_class": "timeout",
                "recovery_actions": json.dumps(["retry"]),
                "changed_at": TWO_HOURS_AGO,
            }
        ],
    )
    assert _detect(service).findings == ()


# ---------------------------------------------------------------------------
# Negative / scoping / co-occurrence
# ---------------------------------------------------------------------------


def test_healthy_flow_produces_no_findings() -> None:
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed", changed_at=NOW)],
        telemetry=[_telem(outcome="success", failure_class=None)],
    )
    report = _detect(service)
    assert report.findings == ()
    assert report.counts_by_reason == {}
    assert report.active_flow_count == 1


def test_terminal_flow_and_terminal_stage_are_skipped() -> None:
    service = FakeFlowService(
        flows=[_flow(id="DONE", status="completed"), _flow(id="LIVE", status="running")],
        stages=[
            _stage(id="S-DONE", flow_instance_id="DONE", changed_at=TWO_DAYS_AGO),
            _stage(id="S-SKIP", flow_instance_id="LIVE", status="completed", changed_at=TWO_DAYS_AGO),
        ],
    )
    report = _detect(service, thresholds=StuckThresholds(stalled_seconds=1))
    assert report.active_flow_count == 1  # only LIVE
    assert report.findings == ()  # its only stage is terminal


def test_subject_scope_filters_active_flows() -> None:
    service = FakeFlowService(
        flows=[
            _flow(id="F-PLAT", subject_type="gtkb-platform"),
            _flow(id="F-AR", subject_type="agent-red"),
        ],
        stages=[
            _stage(id="S-PLAT", flow_instance_id="F-PLAT", changed_at=TWO_HOURS_AGO),
            _stage(id="S-AR", flow_instance_id="F-AR", changed_at=TWO_HOURS_AGO),
        ],
    )
    report = _detect(service, thresholds=StuckThresholds(stalled_seconds=1), subject_scope="agent-red")
    assert report.active_flow_count == 1
    assert {f.stage_instance_id for f in report.findings} == {"S-AR"}


def test_expired_lease_and_failed_unrecovered_co_occur() -> None:
    """Structural and telemetry facets are orthogonal and can both fire."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(claim_status="claimed")],
        leases=[_lease(expires_at=TWO_HOURS_AGO)],
        telemetry=[_telem(outcome="failure", failure_class="timeout", recovery_actions_parsed=[])],
    )
    reasons = sorted(f.reason for f in _detect(service).findings)
    assert reasons == [REASON_EXPIRED_LEASE, REASON_FAILED_UNRECOVERED]


def test_unparseable_timestamp_fails_open_no_false_positive() -> None:
    """A stage whose activity timestamp cannot be parsed is not flagged stalled."""
    service = FakeFlowService(
        flows=[_flow()],
        stages=[_stage(changed_at="not-a-timestamp", started_at=None)],
    )
    assert _detect(service, thresholds=StuckThresholds(stalled_seconds=0)).findings == ()


def test_diagnose_stuck_flow_is_pure_and_advisory() -> None:
    """diagnose_stuck_flow derives advisory text from a finding without actuation."""
    from groundtruth_kb.tafe_stuck_flow import StuckFlowFinding

    finding = StuckFlowFinding(
        flow_instance_id="F",
        stage_instance_id="S",
        stage_id="review",
        required_role="loyal-opposition",
        reason=REASON_FAILED_UNRECOVERED,
        failure_class="oom",
        last_outcome="failure",
        cleanup_result="none",
    )
    text = diagnose_stuck_flow(finding, [{"attempt_number": 3}])
    assert "oom" in text
    assert "#3" in text
    assert "not actuated" in text


# ---------------------------------------------------------------------------
# Non-mutating invariant + structural guard
# ---------------------------------------------------------------------------


def _table_counts(db: KnowledgeDB) -> dict[str, int]:
    conn = db._get_conn()
    counts = {}
    for table in ("flow_instances", "stage_instances", "stage_leases", "stage_attempt_telemetry"):
        counts[table] = conn.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
    return counts


def test_detect_is_non_mutating_against_real_db(tmp_path: Path) -> None:
    """SPEC-TAFE-R2/R3: detection writes no rows to any TAFE table."""
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        definition = service.create_flow_definition(
            id="FLOW-STUCK",
            flow_type="implementation",
            name="stuck flow",
            stages=["review"],
            required_roles={"review": "loyal-opposition"},
            changed_by="test",
            change_reason="seed stuck flow",
            source_spec_ids=["SPEC-TAFE-R3"],
        )
        flow = service.create_flow_instance(
            id="FLOWINST-STUCK",
            flow_definition_id=definition["id"],
            subject_type="gtkb-platform",
            subject_id="stuck",
            changed_by="test",
            change_reason="seed instance",
        )
        service.create_stage_instance(
            id="STAGEINST-STUCK",
            flow_instance_id=flow["id"],
            stage_id="review",
            stage_index=0,
            required_role="loyal-opposition",
            changed_by="test",
            change_reason="seed stage",
        )
        before = _table_counts(db)
        report = detect_stuck_flows(service, now=NOW, thresholds=StuckThresholds(stalled_seconds=0))
        after = _table_counts(db)
    finally:
        db.close()

    assert report.mutated is False
    assert before == after  # no rows added by detection


def test_module_has_no_recovery_actuation_surface() -> None:
    """WI-4505 bounding: read/compute/report only -- no actuation surface.

    Scans the module's CODE with docstrings and comments stripped, so a
    forbidden token that appears only in prose documenting the no-actuation
    bound (e.g. ``subprocess`` in the module docstring's "no ... subprocess"
    sentence) is not a false positive. Real usage -- a ``subprocess`` import, a
    ``Popen`` / ``os.system`` call, a mutation method name, an ``insert_`` write,
    an ``INDEX.md`` string, or a ``.commit(`` -- survives docstring stripping and
    is still flagged, because ``ast.unparse`` emits only executable code
    (comments are absent from the AST).
    """
    import ast

    import groundtruth_kb.tafe_stuck_flow as module

    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                stripped = body[1:]
                if not stripped and not isinstance(node, ast.Module):
                    stripped = [ast.Pass()]
                node.body = stripped
    code = ast.unparse(ast.fix_missing_locations(tree))
    forbidden = (
        "subprocess",
        "Popen",
        "os.system",
        "claim_stage_lease",
        "release_stage_lease",
        "recover_expired_stage_leases",
        "record_stage_attempt_telemetry",
        "record_capability_snapshot",
        "insert_",
        "INDEX.md",
        ".commit(",
    )
    for token in forbidden:
        assert token not in code, f"unexpected actuation/mutation surface: {token}"


# ---------------------------------------------------------------------------
# Real production interface: gt flow stuck CLI (validates schema assumptions)
# ---------------------------------------------------------------------------


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def _json_output(result: Any) -> dict[str, Any]:
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_cli_stuck_empty_db_is_clean_and_non_mutating(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "stuck", "--json"])
    payload = _json_output(result)
    assert payload["command"] == "flow stuck"
    assert payload["status"] == "phase1_detect_only"
    assert payload["mutated"] is False
    assert payload["active_flow_count"] == 0
    assert payload["findings"] == []


def test_cli_stuck_reports_real_unclaimed_stalled_stage(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        definition = service.create_flow_definition(
            id="FLOW-CLI-STUCK",
            flow_type="implementation",
            name="cli stuck flow",
            stages=["review"],
            required_roles={"review": "loyal-opposition"},
            changed_by="test",
            change_reason="seed cli stuck flow",
            source_spec_ids=["SPEC-TAFE-R3"],
        )
        flow = service.create_flow_instance(
            id="FLOWINST-CLI-STUCK",
            flow_definition_id=definition["id"],
            subject_type="gtkb-platform",
            subject_id="cli-stuck",
            changed_by="test",
            change_reason="seed cli instance",
        )
        service.create_stage_instance(
            id="STAGEINST-CLI-STUCK",
            flow_instance_id=flow["id"],
            stage_id="review",
            stage_index=0,
            required_role="loyal-opposition",
            changed_by="test",
            change_reason="seed cli stage",
        )
    finally:
        db.close()

    # --stalled-seconds 0: any unclaimed non-terminal stage with parseable activity is stalled.
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "stuck", "--stalled-seconds", "0", "--json"])
    payload = _json_output(result)
    assert payload["mutated"] is False
    finding = next(f for f in payload["findings"] if f["stage_instance_id"] == "STAGEINST-CLI-STUCK")
    assert finding["reason"] == REASON_STALLED_PENDING
    assert finding["required_role"] == "loyal-opposition"


def test_cli_stuck_consumes_real_wi4504_telemetry(runner: CliRunner, project_dir: Path) -> None:
    """End-to-end: failed-unrecovered reads the real WI-4504 telemetry surface."""
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        definition = service.create_flow_definition(
            id="FLOW-CLI-TELEM",
            flow_type="implementation",
            name="cli telem flow",
            stages=["review"],
            required_roles={"review": "loyal-opposition"},
            changed_by="test",
            change_reason="seed cli telem flow",
            source_spec_ids=["SPEC-TAFE-R6"],
        )
        flow = service.create_flow_instance(
            id="FLOWINST-CLI-TELEM",
            flow_definition_id=definition["id"],
            subject_type="gtkb-platform",
            subject_id="cli-telem",
            changed_by="test",
            change_reason="seed cli telem instance",
        )
        stage = service.create_stage_instance(
            id="STAGEINST-CLI-TELEM",
            flow_instance_id=flow["id"],
            stage_id="review",
            stage_index=0,
            required_role="loyal-opposition",
            claim_status="claimed",  # claimed -> isolate the telemetry facet from stall
            changed_by="test",
            change_reason="seed cli telem stage",
        )
        service.record_stage_attempt_telemetry(
            id="TELEM-CLI-1",
            flow_instance_id=flow["id"],
            stage_instance_id=stage["id"],
            changed_by="test",
            change_reason="record failed attempt",
            attempt_number=1,
            outcome="failure",
            failure_class="dispatch_timeout",
            cleanup_result="partial",
        )
    finally:
        db.close()

    # Large stall threshold so only the failed-unrecovered telemetry facet fires.
    result = runner.invoke(
        main, [*_config_args(project_dir), "flow", "stuck", "--stalled-seconds", "999999999", "--json"]
    )
    payload = _json_output(result)
    finding = next(f for f in payload["findings"] if f["stage_instance_id"] == "STAGEINST-CLI-TELEM")
    assert finding["reason"] == REASON_FAILED_UNRECOVERED
    assert finding["failure_class"] == "dispatch_timeout"
    assert "dispatch_timeout" in finding["diagnosis"]
