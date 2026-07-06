# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Spec-derived tests for the service/SoT watchdog restoration policy (WI-5045)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.bridge.disposition import STATUS_ADVISORY  # noqa: E402
from groundtruth_kb.project.sot_registry import SoTArtifact  # noqa: E402
from groundtruth_kb.watchdog import service_sot  # noqa: E402
from groundtruth_kb.watchdog.restore_policy import (  # noqa: E402
    AutoRestoreAction,
    EscalateAction,
    NoRestoreAction,
    decide_artifact_restoration,
    decide_restore_action,
    restore_action_tier,
)


def _artifact(artifact_id: str, restore_action: str) -> SoTArtifact:
    return SoTArtifact(
        id=artifact_id,
        domain="runtime_state",
        lifecycle="active",
        storage_path=f".gtkb-state/{artifact_id}.json",
        authority_spec_id="ADR-PLATFORM-SERVICE-SOT-WATCHDOG-001",
        mutation_api="test",
        versioning_policy="overwrite_single_writer",
        backup_policy="regenerable_from_source",
        health_check_function="_check_test",
        owner_role="automated_only",
        restore_action=restore_action,
    )


def test_policy_auto_restores_safe_idempotent_action_after_fresh_failure_probe() -> None:
    decision = decide_restore_action(
        artifact_id="bridge-dispatch-state",
        restore_action="ensure_alive",
        probe_status="FAIL",
        fresh_probe=True,
        retry_attempts=1,
        max_attempts=3,
    )

    assert isinstance(decision, AutoRestoreAction)
    assert decision.restore_action == "ensure_alive"
    assert decision.reason_code == "safe_auto_restore"
    assert decision.to_json_dict()["kind"] == "auto_restore"


def test_policy_escalates_canonical_restore_instead_of_auto_mutating() -> None:
    decision = decide_restore_action(
        artifact_id="membase-specifications",
        restore_action="membase_export_restore",
        probe_status="FAIL",
        fresh_probe=True,
    )

    assert isinstance(decision, EscalateAction)
    assert decision.reason_code == "canonical_restore_forbidden"
    assert decision.advisory_required is True
    assert decision.escalation_status == STATUS_ADVISORY


def test_policy_honors_visibility_only_override_before_auto_restore() -> None:
    decision = decide_restore_action(
        artifact_id="owner-local-env",
        restore_action="ensure_alive",
        probe_status="FAIL",
        fresh_probe=True,
        visibility_only_artifact_ids={"owner-local-env"},
    )

    assert isinstance(decision, NoRestoreAction)
    assert decision.reason_code == "visibility_only"
    assert decision.flagged_state_required is True


def test_policy_escalates_retry_exhaustion_for_safe_action() -> None:
    decision = decide_restore_action(
        artifact_id="bridge-dispatch-state",
        restore_action="ensure_alive",
        probe_status="FAIL",
        fresh_probe=True,
        retry_attempts=3,
        max_attempts=3,
    )

    assert isinstance(decision, EscalateAction)
    assert decision.reason_code == "retry_exhausted"
    assert decision.retry_exhausted is True
    assert decision.escalation_status == STATUS_ADVISORY


def test_policy_requires_fresh_probe_before_restore() -> None:
    decision = decide_restore_action(
        artifact_id="bridge-dispatch-state",
        restore_action="ensure_alive",
        probe_status="FAIL",
        fresh_probe=False,
    )

    assert isinstance(decision, NoRestoreAction)
    assert decision.reason_code == "stale_probe"
    assert decision.flagged_state_required is True


def test_policy_consumes_sot_artifact_restore_action_metadata() -> None:
    artifact = _artifact("runtime-index", "regenerate_from_source")

    decision = decide_artifact_restoration(artifact, {"status": "FAIL", "detail": "index missing"})

    assert isinstance(decision, AutoRestoreAction)
    assert decision.artifact_id == "runtime-index"
    assert decision.restore_action == "regenerate_from_source"


def test_artifact_probe_carries_restore_action_metadata(monkeypatch) -> None:
    artifact = _artifact("runtime-index", "regenerate_from_source")
    monkeypatch.setattr(
        service_sot,
        "_invoke_health_check",
        lambda function_name, project_root: {
            "name": function_name,
            "status": "FAIL",
            "detail": "index missing",
            "found": False,
            "required": True,
        },
    )

    probe = service_sot._artifact_probe(artifact, _REPO_ROOT)

    assert probe["artifact_id"] == "runtime-index"
    assert probe["restore_action"] == "regenerate_from_source"
    assert probe["status"] == "FAIL"


def test_restore_action_tiers_classify_safe_canonical_and_no_restore_actions() -> None:
    assert restore_action_tier("ensure_alive") == "safe"
    assert restore_action_tier("regenerate-from-source") == "safe"
    assert restore_action_tier("git_restore") == "canonical"
    assert restore_action_tier("membase_export_restore") == "canonical"
    assert restore_action_tier("visibility_only") == "visibility_only"
    assert restore_action_tier("noop") == "noop"
