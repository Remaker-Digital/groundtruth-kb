"""Tests for groundtruth_kb.tafe_dispatch_runtime (WI-4499).

Covers SPEC-TAFE-R5 need evaluation, R2 unclaimed-only candidacy, R4 policy-engine
invocation, R6 decision-evidence output, the non-mutating invariant, the documented
metadata-key mapping assumptions, and the read-only ``gt flow dispatch`` CLI.

The ``FakeFlowService`` gives precise control over stage/flow/snapshot dict shapes
for mapping coverage; the CliRunner tests exercise the real production interface
(``TypedArtifactFlowService`` + the ``gt flow dispatch`` commands) against the real
schema to validate the mapping assumptions end-to-end.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from click.testing import CliRunner

from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.tafe_dispatch_runtime import (
    evaluate_dispatch_health,
    evaluate_dispatch_tick,
    health_report_to_payload,
    tick_report_to_payload,
)
from groundtruth_kb.typed_artifact_flow import TypedArtifactFlowService

# ---------------------------------------------------------------------------
# Fake injected service + record builders
# ---------------------------------------------------------------------------


class FakeFlowService:
    """Minimal in-memory stand-in for the read slice the runtime depends on."""

    def __init__(
        self,
        *,
        stages: list[dict[str, Any]] | None = None,
        flows: list[dict[str, Any]] | None = None,
        snapshots: list[dict[str, Any]] | None = None,
    ) -> None:
        self._stages = list(stages or [])
        self._flows = {flow["id"]: flow for flow in (flows or [])}
        self._snapshots = list(snapshots or [])

    def list_stage_instances(
        self, *, flow_instance_id: str | None = None, status: str | None = None
    ) -> list[dict[str, Any]]:
        rows = self._stages
        if flow_instance_id is not None:
            rows = [s for s in rows if s.get("flow_instance_id") == flow_instance_id]
        if status is not None:
            rows = [s for s in rows if s.get("status") == status]
        return [dict(s) for s in rows]

    def get_flow_instance(self, flow_instance_id: str) -> dict[str, Any] | None:
        flow = self._flows.get(flow_instance_id)
        return dict(flow) if flow else None

    def list_capability_snapshots(
        self,
        *,
        harness_id: str | None = None,
        health_status: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._snapshots
        if status is not None:
            rows = [s for s in rows if s.get("status") == status]
        if health_status is not None:
            rows = [s for s in rows if s.get("health_status") == health_status]
        if harness_id is not None:
            rows = [s for s in rows if s.get("harness_id") == harness_id]
        return [dict(s) for s in rows]


def _meta(**extra: Any) -> dict[str, Any]:
    # A stage needs an artifact_author_session_id for the review-independence gate to
    # pass; without it the policy engine fails closed and no candidate is eligible.
    base: dict[str, Any] = {"artifact_author_session_id": "session-author"}
    base.update(extra)
    return base


def _stage(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "STAGEINST-1",
        "stage_id": "review",
        "flow_instance_id": "FLOWINST-1",
        "required_role": "loyal-opposition",
        "status": "pending",
        "claim_status": "unclaimed",
        "metadata": _meta(),
    }
    if isinstance(overrides.get("metadata"), dict):
        overrides["metadata"] = _meta(**overrides["metadata"])
    base.update(overrides)
    return base


def _flow(**overrides: Any) -> dict[str, Any]:
    base = {"id": "FLOWINST-1", "subject_type": "gtkb-platform", "subject_id": "x"}
    base.update(overrides)
    return base


def _snapshot(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "SNAP-1",
        "harness_id": "A",
        "role": "loyal-opposition",
        "subject_scope": "gtkb-platform",
        "health_status": "active",
        "reviewer_precedence": 1,
        "workspace_availability": "available",
        "model_identifier": "model-a",
        "capabilities": {},
        "status": "active",
        "metadata": {"active_session_id": "session-reviewer"},
    }
    base.update(overrides)
    return base


def _eligible_service(**stage_overrides: Any) -> FakeFlowService:
    return FakeFlowService(
        stages=[_stage(**stage_overrides)],
        flows=[_flow()],
        snapshots=[_snapshot()],
    )


# ---------------------------------------------------------------------------
# tick: selection, candidacy filtering (R2, R4, R5)
# ---------------------------------------------------------------------------


def test_tick_selects_eligible_candidate_for_pending_stage() -> None:
    report = evaluate_dispatch_tick(_eligible_service())
    assert report.mutated is False
    assert report.pending_stage_count == 1
    decision = report.decisions[0]
    assert decision.selected_harness_id == "A"
    assert decision.eligible_candidate_count == 1
    assert decision.ranked_harness_ids == ("A",)


def test_tick_excludes_claimed_stage() -> None:
    report = evaluate_dispatch_tick(_eligible_service(claim_status="claimed"))
    assert report.pending_stage_count == 0
    assert report.decisions == ()


def test_tick_excludes_terminal_stage() -> None:
    report = evaluate_dispatch_tick(_eligible_service(status="completed"))
    assert report.pending_stage_count == 0


def test_tick_reports_no_eligible_candidate_when_role_mismatches() -> None:
    service = FakeFlowService(
        stages=[_stage(required_role="prime-builder")],
        flows=[_flow()],
        snapshots=[_snapshot(role="loyal-opposition")],
    )
    report = evaluate_dispatch_tick(service)
    decision = report.decisions[0]
    assert decision.selected_harness_id is None
    assert decision.eligible_candidate_count == 0


def test_tick_subject_scope_filter_restricts_to_matching_flow() -> None:
    service = FakeFlowService(
        stages=[
            _stage(id="STAGE-PLATFORM", flow_instance_id="FLOW-PLATFORM"),
            _stage(id="STAGE-AGENTRED", flow_instance_id="FLOW-AGENTRED"),
        ],
        flows=[
            _flow(id="FLOW-PLATFORM", subject_type="gtkb-platform"),
            _flow(id="FLOW-AGENTRED", subject_type="agent-red"),
        ],
        snapshots=[_snapshot()],
    )
    report = evaluate_dispatch_tick(service, subject_scope="gtkb-platform")
    assert report.pending_stage_count == 1
    assert report.decisions[0].stage_instance_id == "STAGE-PLATFORM"
    assert report.decisions[0].subject_scope == "gtkb-platform"


# ---------------------------------------------------------------------------
# documented metadata-key mapping assumptions
# ---------------------------------------------------------------------------


def test_tick_required_capabilities_sourced_from_stage_metadata() -> None:
    needs_cap = _eligible_service(metadata=_meta(required_capabilities=["bridge-review"]))
    # Candidate lacks the capability -> ineligible.
    assert evaluate_dispatch_tick(needs_cap).decisions[0].selected_harness_id is None

    has_cap = FakeFlowService(
        stages=[_stage(metadata=_meta(required_capabilities=["bridge-review"]))],
        flows=[_flow()],
        snapshots=[_snapshot(capabilities={"bridge-review": True})],
    )
    assert evaluate_dispatch_tick(has_cap).decisions[0].selected_harness_id == "A"


def test_tick_owner_gate_blocked_from_stage_metadata_blocks_selection() -> None:
    service = _eligible_service(metadata={"owner_gate_blocked": True})
    decision = evaluate_dispatch_tick(service).decisions[0]
    assert decision.owner_gate_blocked is True
    assert decision.selected_harness_id is None


def test_tick_metadata_accepts_json_string() -> None:
    service = _eligible_service(metadata=json.dumps({"owner_gate_blocked": True}))
    assert evaluate_dispatch_tick(service).decisions[0].owner_gate_blocked is True


def test_candidate_without_active_session_is_ineligible() -> None:
    service = FakeFlowService(
        stages=[_stage()],
        flows=[_flow()],
        snapshots=[_snapshot(metadata={})],  # no active_session_id
    )
    assert evaluate_dispatch_tick(service).decisions[0].selected_harness_id is None


def test_candidate_workspace_unavailable_is_ineligible() -> None:
    service = FakeFlowService(
        stages=[_stage()],
        flows=[_flow()],
        snapshots=[_snapshot(workspace_availability="unavailable")],
    )
    assert evaluate_dispatch_tick(service).decisions[0].selected_harness_id is None


def test_candidate_capabilities_json_string_parsed() -> None:
    service = FakeFlowService(
        stages=[_stage(metadata={"required_capabilities": ["bridge-review"]})],
        flows=[_flow()],
        snapshots=[_snapshot(capabilities=json.dumps({"bridge-review": True}))],
    )
    assert evaluate_dispatch_tick(service).decisions[0].selected_harness_id == "A"


# ---------------------------------------------------------------------------
# health aggregation
# ---------------------------------------------------------------------------


def test_health_aggregates_readiness_counts() -> None:
    service = FakeFlowService(
        stages=[
            _stage(id="S1", flow_instance_id="FLOWINST-1"),
            _stage(id="S2", flow_instance_id="FLOWINST-1", required_role="prime-builder"),
            _stage(id="S3", flow_instance_id="FLOWINST-1", claim_status="claimed"),
        ],
        flows=[_flow()],
        snapshots=[
            _snapshot(id="SNAP-A", harness_id="A", role="loyal-opposition"),
            _snapshot(id="SNAP-B", harness_id="B", role="prime-builder", metadata={}),
        ],
    )
    report = evaluate_dispatch_health(service)
    assert report.mutated is False
    assert report.pending_unclaimed_stage_count == 2  # claimed S3 excluded
    assert report.active_candidate_count == 2
    assert report.candidates_by_role == {"loyal-opposition": 1, "prime-builder": 1}
    # S1 has an eligible LO candidate; S2 (prime-builder) candidate has no active session -> not eligible.
    assert report.no_eligible_candidate_stage_count == 1


def test_health_counts_owner_gated_stages() -> None:
    service = FakeFlowService(
        stages=[_stage(metadata={"owner_gate_blocked": True})],
        flows=[_flow()],
        snapshots=[_snapshot()],
    )
    report = evaluate_dispatch_health(service)
    assert report.owner_gated_stage_count == 1


# ---------------------------------------------------------------------------
# payload rendering + non-mutating invariant
# ---------------------------------------------------------------------------


def test_tick_payload_shape_is_json_compatible_and_non_mutating() -> None:
    payload = tick_report_to_payload(evaluate_dispatch_tick(_eligible_service()))
    assert payload["command"] == "flow dispatch tick"
    assert payload["status"] == "phase1_evaluate_only"
    assert payload["mutated"] is False
    assert payload["pending_stage_count"] == 1
    assert payload["decisions"][0]["selected_harness_id"] == "A"
    json.dumps(payload)  # must be serializable


def test_health_payload_shape_is_json_compatible() -> None:
    payload = health_report_to_payload(evaluate_dispatch_health(_eligible_service()))
    assert payload["command"] == "flow dispatch health"
    assert payload["status"] == "phase1_evaluate_only"
    assert payload["mutated"] is False
    json.dumps(payload)


def test_runtime_module_has_no_live_dispatch_surface() -> None:
    """The runtime is read/compute/report only: no spawn/subprocess/index-write."""
    import groundtruth_kb.tafe_dispatch_runtime as runtime

    source = Path(runtime.__file__).read_text(encoding="utf-8")
    for forbidden in ("subprocess", "Popen", "os.system", "claim_stage_lease", "INDEX.md"):
        assert forbidden not in source, f"unexpected live-dispatch surface: {forbidden}"


# ---------------------------------------------------------------------------
# Real production interface: gt flow dispatch CLI (validates schema assumptions)
# ---------------------------------------------------------------------------


def _config_args(project_dir: Path) -> list[str]:
    return ["--config", str(project_dir / "groundtruth.toml")]


def _json_output(result: Any) -> dict[str, Any]:
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_cli_dispatch_tick_empty_db_is_clean_and_non_mutating(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "dispatch", "tick", "--json"])
    payload = _json_output(result)
    assert payload["command"] == "flow dispatch tick"
    assert payload["status"] == "phase1_evaluate_only"
    assert payload["mutated"] is False
    assert payload["pending_stage_count"] == 0


def test_cli_dispatch_health_empty_db_is_clean(runner: CliRunner, project_dir: Path) -> None:
    result = runner.invoke(main, [*_config_args(project_dir), "flow", "dispatch", "health", "--json"])
    payload = _json_output(result)
    assert payload["command"] == "flow dispatch health"
    assert payload["status"] == "phase1_evaluate_only"
    assert payload["mutated"] is False
    assert payload["pending_unclaimed_stage_count"] == 0


def test_cli_dispatch_tick_reports_real_unclaimed_stage(runner: CliRunner, project_dir: Path) -> None:
    db = KnowledgeDB(project_dir / "groundtruth.db")
    try:
        service = TypedArtifactFlowService(db)
        definition = service.create_flow_definition(
            id="FLOW-DISP-TICK",
            flow_type="implementation",
            name="dispatch tick flow",
            stages=["review"],
            required_roles={"review": "loyal-opposition"},
            changed_by="test",
            change_reason="seed dispatch tick flow",
            source_spec_ids=["SPEC-TAFE-R2"],
        )
        flow = service.create_flow_instance(
            id="FLOWINST-DISP-TICK",
            flow_definition_id=definition["id"],
            subject_type="gtkb-platform",
            subject_id="dispatch-tick",
            changed_by="test",
            change_reason="seed dispatch tick instance",
        )
        service.create_stage_instance(
            id="STAGEINST-DISP-TICK",
            flow_instance_id=flow["id"],
            stage_id="review",
            stage_index=0,
            required_role="loyal-opposition",
            metadata={"artifact_author_session_id": "session-author"},
            changed_by="test",
            change_reason="seed dispatch tick stage",
        )
        service.record_capability_snapshot(
            id="SNAP-DISP-TICK",
            harness_id="A",
            role="loyal-opposition",
            subject_scope="gtkb-platform",
            health_status="active",
            reviewer_precedence=1,
            workspace_availability="available",
            model_identifier="model-a",
            capabilities={},
            metadata={"active_session_id": "session-reviewer"},
            changed_by="test",
            change_reason="seed dispatch tick candidate",
        )
    finally:
        db.close()

    result = runner.invoke(main, [*_config_args(project_dir), "flow", "dispatch", "tick", "--json"])
    payload = _json_output(result)
    assert payload["mutated"] is False
    assert payload["pending_stage_count"] >= 1
    decision = next(d for d in payload["decisions"] if d["stage_instance_id"] == "STAGEINST-DISP-TICK")
    assert decision["required_role"] == "loyal-opposition"
    assert decision["subject_scope"] == "gtkb-platform"
    assert decision["selected_harness_id"] == "A"
