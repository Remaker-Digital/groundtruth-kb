#!/usr/bin/env python3
"""Validate and execute objective-level assertions for the frozen modernization scope.

Family-level test success is not semantic traceability.  This checker binds each
frozen scope handle to a unique assertion and to concrete machine assertions,
pytest nodes, or observed-event receipts.  A missing observed event is a failed
assertion, not permission to substitute a simulation or a file-existence check.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = PROJECT_ROOT / "config" / "governance" / "modernization-release-candidate.json"
DEFAULT_EVIDENCE_DIR = PROJECT_ROOT / ".gtkb-state" / "modernization-release-candidate" / "semantic-evidence"
PACKAGE_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from groundtruth_kb.session.envelope import (  # noqa: E402
    EnvelopeError,
    _validate_worker_role_provenance,
    worker_session_envelope_path,
)

_SHA256_RE = re.compile(r"^[0-9A-F]{64}$")
_GIT_HEAD_RE = re.compile(r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
_ISSUE_ID_RE = re.compile(r"^[0-9]{14}-[0-9a-f]{12}$")
_PR_URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/pull/[1-9][0-9]*$")
COLLECTOR_SERVICE_ID = "gtkb.modernization-semantic-evidence.collector.v1"
ISSUER_SCHEMA_VERSION = 2
RECEIPT_SCHEMA_VERSION = 2
MEASUREMENT_SCHEMA_VERSION = 2
ISSUANCE_SCHEMA_VERSION = 1
_PILOT_OPERATIONS = {
    "branch_create",
    "scoped_commit",
    "work_item_merge",
    "project_pull_request",
    "develop_stage_promotion",
    "quiescence_lease",
    "recovery_replay",
}
_REPORT_ASSERTION_IDS = {
    "context": {f"CTX-MANIFEST-A{index}" for index in range(1, 9)},
    "artifact": {f"MOD-AD-{index:02d}" for index in range(1, 13)},
    "git": {f"GIT-LIFECYCLE-A{index}" for index in range(1, 27)},
}
_BUILTIN_NAMES = {
    "program-hierarchy",
    "umbrella-bridge-proposal",
    "traceability-contract",
    "history-quarantine",
    "git-modernization-pilot",
}
POST_CLEAN_ASSERTION_IDS = {
    "MSA-MOD-P06",
    "MSA-MOD-AS08",
    "MSA-MOD-AS12",
    "MSA-MOD-AS14",
}


@dataclass(frozen=True)
class CheckResult:
    status: str
    evidence: Any


def _r(source: str, *assertion_ids: str) -> tuple[str, ...]:
    return tuple(f"report:{source}:{assertion_id}" for assertion_id in assertion_ids)


def _t(*nodeids: str) -> tuple[str, ...]:
    return tuple(f"pytest:{nodeid}" for nodeid in nodeids)


def _b(*names: str) -> tuple[str, ...]:
    return tuple(f"builtin:{name}" for name in names)


# This is deliberately literal.  Shared family commands are insufficient: each
# handle has an exact proof selection that can be reviewed against its objective.
PROOFS: dict[str, tuple[str, ...]] = {
    "MOD-P01": _b("program-hierarchy"),
    "MOD-P02": _r("artifact", "MOD-AD-12") + _b("receipt:predecessor-reconciliation"),
    "MOD-P03": _b("program-hierarchy")
    + _t(
        "platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once"
    ),
    "MOD-P04": _b("umbrella-bridge-proposal"),
    "MOD-P05": _b("traceability-contract"),
    "MOD-P06": _b("receipt:program-closure"),
    "MOD-AF01": _t(
        "platform_tests/scripts/test_modernization_authority_foundations.py::test_frozen_authority_carriers_are_current_stated_and_uniquely_asserted"
    )
    + _b("receipt:authority-carrier-classification"),
    "MOD-AF02": _t(
        "platform_tests/scripts/test_modernization_nonimpairment.py::test_complete_nonimpairing_evidence_passes"
    ),
    "MOD-AF03": _r("context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A5"),
    "MOD-AF04": _t(
        "platform_tests/scripts/test_modernization_authority_foundations.py::test_authority_enforcement_sources_are_live_root_bound_files"
    ),
    "MOD-AF05": _r("artifact", "MOD-AD-05", "MOD-AD-10"),
    "MOD-AF06": _t(
        "platform_tests/scripts/test_modernization_nonimpairment.py::test_missing_hard_invariant_blocks_verification_promotion_and_closure"
    ),
    "MOD-AF07": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_role_resolution_orders_marker_then_envelope_then_durable_fallback"
    ),
    "MOD-AF08": _t(
        "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py::test_bounded_envelope_produces_machine_readable_allow",
        "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py::test_unknown_operation_fails_closed",
    )
    + _r("git", "GIT-LIFECYCLE-A23"),
    "MOD-AF09": _t(
        "platform_tests/scripts/test_modernization_authority_foundations.py::test_every_frozen_authority_carrier_is_fully_evaluable"
    ),
    "MOD-CM01": _r("context", "CTX-MANIFEST-A3"),
    "MOD-CM02": _r("context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A6"),
    "MOD-CM03": _r("context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A3"),
    "MOD-CM04": _r("context", "CTX-MANIFEST-A3", "CTX-MANIFEST-A4"),
    "MOD-CM05": _r("context", "CTX-MANIFEST-A2", "CTX-MANIFEST-A6"),
    "MOD-CM06": _r("context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A8"),
    "MOD-CM07": _r("context", "CTX-MANIFEST-A4", "CTX-MANIFEST-A7"),
    "MOD-CM08": _r("context", "CTX-MANIFEST-A7", "CTX-MANIFEST-A8")
    + _t(
        "platform_tests/scripts/test_modernization_fresh_worker.py::test_project_context_override_cannot_fall_back_to_packaged_assets"
    ),
    "MOD-CM09": _r("context", "CTX-MANIFEST-A2", "CTX-MANIFEST-A3"),
    "MOD-CM10": _r(
        "context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A2", "CTX-MANIFEST-A3", "CTX-MANIFEST-A7", "CTX-MANIFEST-A8"
    ),
    "MOD-AD01": _r("artifact", "MOD-AD-01", "MOD-AD-11"),
    "MOD-AD02": _r("artifact", "MOD-AD-02", "MOD-AD-03", "MOD-AD-04"),
    "MOD-AD03": _r("artifact", "MOD-AD-04", "MOD-AD-09"),
    "MOD-AD04": _r("artifact", "MOD-AD-05", "MOD-AD-06", "MOD-AD-07", "MOD-AD-10"),
    "MOD-AD05": _r("artifact", "MOD-AD-12") + _b("receipt:artifact-cleanup-batches"),
    "MOD-AD06": _r("artifact", "MOD-AD-05", "MOD-AD-12") + _b("receipt:semantic-guidance-cleanup"),
    "MOD-AD07": _r("artifact", "MOD-AD-05", "MOD-AD-08"),
    "MOD-AD08": _r("artifact", "MOD-AD-04", "MOD-AD-12") + _b("receipt:lifecycle-state-reconciliation"),
    "MOD-AD09": _b("history-quarantine"),
    "MOD-AD10": _b("receipt:work-item-advisory-deduplication"),
    "MOD-AD11": _r("artifact", "MOD-AD-11", "MOD-AD-12")
    + _t(
        "platform_tests/scripts/test_modernization_artifact_decontamination.py::test_mod_ad_12_live_repository_contract_passes"
    ),
    "MOD-AD12": _r("artifact", "MOD-AD-09", "MOD-AD-12"),
    "MOD-RI01": _b("receipt:runtime-interface-inventory")
    + _t(
        "platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once"
    ),
    "MOD-RI02": _r("context", "CTX-MANIFEST-A5"),
    "MOD-RI03": _r("context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A6")
    + _t(
        "platform_tests/scripts/test_modernization_fresh_worker.py::test_fresh_worker_bootstraps_from_only_copied_product_assets"
    ),
    "MOD-RI04": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_role_resolution_orders_marker_then_envelope_then_durable_fallback",
        "platform_tests/scripts/test_session_role_resolution_table.py::test_assertion4_compaction_resume_falls_back_to_durable",
    ),
    "MOD-RI05": _t(
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_observation_exposes_recovery_state_and_ordered_events"
    ),
    "MOD-RI06": _r("context", "CTX-MANIFEST-A4", "CTX-MANIFEST-A7"),
    "MOD-RI07": _t(
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_retry_budget_is_bounded_and_exhaustion_quarantines",
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_nonretryable_failure_quarantines_immediately",
    ),
    "MOD-RI08": _t(
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_observation_exposes_recovery_state_and_ordered_events"
    ),
    "MOD-RI09": _r("context", "CTX-MANIFEST-A6") + _b("activity:all"),
    "MOD-RI10": _b("activity:ops"),
    "MOD-RI11": _b("activity:deliberation"),
    "MOD-RI12": _b("activity:build")
    + _t(
        "platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once"
    ),
    "MOD-RI13": _b("activity:test")
    + _t(
        "platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once"
    ),
    "MOD-RI14": _b("activity:spec")
    + _t(
        "platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once"
    ),
    "MOD-RI15": _b("activity:project")
    + _t(
        "platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once"
    ),
    "MOD-RI16": _r("context", "CTX-MANIFEST-A1", "CTX-MANIFEST-A5", "CTX-MANIFEST-A6", "CTX-MANIFEST-A7")
    + _t(
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_interrupted_attempt_resumes_from_durable_checkpoint"
    ),
    "MOD-HP01": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity"
    ),
    "MOD-HP02": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_explicit_roles_context_and_routes_are_equivalent_across_harnesses"
    ),
    "MOD-HP03": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity"
    )
    + _b("receipt:harness-claude-live"),
    "MOD-HP04": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity"
    )
    + _b("receipt:harness-codex-live"),
    "MOD-HP05": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity"
    )
    + _b("receipt:harness-cursor-live"),
    "MOD-HP06": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity"
    )
    + _b("receipt:harness-antigravity-optimized-startup"),
    "MOD-HP07": _t(
        "platform_tests/scripts/test_cross_harness_protocol_parity.py::test_durable_harness_identity_and_role_surfaces_cover_expected_harnesses"
    )
    + _b("receipt:headless-provider-conformance"),
    "MOD-HP08": _t(
        "platform_tests/scripts/test_cross_harness_protocol_parity.py::test_harness_parity_skill_separates_catalog_operational_and_hook_scope"
    ),
    "MOD-HP09": _t(
        "platform_tests/scripts/test_cross_harness_protocol_parity.py::test_capability_registry_tracks_shared_skill_and_low_cost_harness_floors",
        "platform_tests/scripts/test_cross_harness_protocol_parity.py::test_hook_fallback_surfaces_distinguish_event_sources_from_dispatch_targets",
    ),
    "MOD-HP10": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_headless_worker_authority_is_isolated_by_session_and_harness",
        "platform_tests/scripts/test_session_role_resolution_table.py::test_assertion4_compaction_resume_falls_back_to_durable",
    ),
    "MOD-HP11": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_role_resolution_orders_marker_then_envelope_then_durable_fallback",
        "platform_tests/scripts/test_session_role_resolution_table.py::test_assertion2_marker_with_matching_session_id_overrides_durable",
    ),
    "MOD-HP12": _b("receipt:cross-harness-confusion-corpus"),
    "MOD-HP13": _t(
        "platform_tests/scripts/test_modernization_fresh_worker.py::test_project_context_override_cannot_fall_back_to_packaged_assets",
        "platform_tests/scripts/test_session_role_resolution_table.py::test_malformed_marker_json_treated_as_absent",
    ),
    "MOD-HP14": _t(
        "platform_tests/scripts/test_modernization_harness_parity.py::test_active_harnesses_have_required_production_parity",
        "platform_tests/scripts/test_modernization_harness_parity.py::test_explicit_roles_context_and_routes_are_equivalent_across_harnesses",
        "platform_tests/scripts/test_modernization_harness_parity.py::test_headless_worker_authority_is_isolated_by_session_and_harness",
    ),
    "MOD-AS01": _b("receipt:pre-modernization-baseline"),
    "MOD-AS02": _t(
        "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_stale_or_retired_authority",
        "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_an_unauthorized_protected_operation",
        "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_ambiguous_worker_role_authority",
        "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_incomplete_or_expired_context",
    ),
    "MOD-AS03": _t(
        "platform_tests/scripts/test_modernization_fresh_worker.py::test_fresh_worker_bootstraps_from_only_copied_product_assets",
        "platform_tests/scripts/test_modernization_fresh_worker.py::test_built_wheel_assembles_context_without_source_tree_or_root_config",
    ),
    "MOD-AS04": _b("receipt:seven-category-scenario-matrix")
    + _t(
        "platform_tests/scripts/test_modernization_hard_invariants.py::test_hard_invariant_rejects_incomplete_or_expired_context"
    ),
    "MOD-AS05": _b("activity:all", "receipt:six-activity-behavior-matrix"),
    "MOD-AS06": _b("receipt:role-harness-session-branch-scenarios")
    + _t(
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_concurrent_attempts_have_exactly_one_owner",
        "platform_tests/scripts/test_modernization_runtime_recovery.py::test_interrupted_attempt_resumes_from_durable_checkpoint",
    ),
    "MOD-AS07": _b("receipt:confusion-regression-fixtures"),
    "MOD-AS08": _b("receipt:nonimpairment-orchestrator")
    + _t("platform_tests/scripts/test_modernization_nonimpairment.py::test_complete_nonimpairing_evidence_passes"),
    "MOD-AS09": _b("receipt:modernization-measurements"),
    "MOD-AS10": _b("receipt:shadow-six-activities-primary-harnesses"),
    "MOD-AS11": _b("receipt:activation-thresholds")
    + _t(
        "platform_tests/scripts/test_modernization_nonimpairment.py::test_missing_hard_invariant_blocks_verification_promotion_and_closure"
    ),
    "MOD-AS12": _b("receipt:reversible-activation-slices")
    + _t("platform_tests/scripts/test_modernization_nonimpairment.py::test_untested_rollback_blocks_activation"),
    "MOD-AS13": _b("receipt:operational-observation")
    + _r("git", "GIT-LIFECYCLE-A8", "GIT-LIFECYCLE-A17", "GIT-LIFECYCLE-A24"),
    "MOD-AS14": _b("receipt:independent-verification"),
    "MOD-GL01": _r(
        "git", "GIT-LIFECYCLE-A2", "GIT-LIFECYCLE-A5", "GIT-LIFECYCLE-A6", "GIT-LIFECYCLE-A16", "GIT-LIFECYCLE-A23"
    ),
    "MOD-GL02": _r(
        "git", "GIT-LIFECYCLE-A1", "GIT-LIFECYCLE-A4", "GIT-LIFECYCLE-A7", "GIT-LIFECYCLE-A16", "GIT-LIFECYCLE-A23"
    ),
    "MOD-GL03": _r("git", "GIT-LIFECYCLE-A1", "GIT-LIFECYCLE-A3"),
    "MOD-GL04": _r("git", "GIT-LIFECYCLE-A14"),
    "MOD-GL05": _r("git", "GIT-LIFECYCLE-A2", "GIT-LIFECYCLE-A3"),
    "MOD-GL06": _r("git", "GIT-LIFECYCLE-A4", "GIT-LIFECYCLE-A5", "GIT-LIFECYCLE-A12"),
    "MOD-GL07": _r("git", "GIT-LIFECYCLE-A9", "GIT-LIFECYCLE-A10", "GIT-LIFECYCLE-A11", "GIT-LIFECYCLE-A26"),
    "MOD-GL08": _r("git", "GIT-LIFECYCLE-A15", "GIT-LIFECYCLE-A18", "GIT-LIFECYCLE-A19"),
    "MOD-GL09": _r("git", "GIT-LIFECYCLE-A15", "GIT-LIFECYCLE-A19"),
    "MOD-GL10": _r(
        "git",
        "GIT-LIFECYCLE-A6",
        "GIT-LIFECYCLE-A7",
        "GIT-LIFECYCLE-A8",
        "GIT-LIFECYCLE-A17",
        "GIT-LIFECYCLE-A24",
        "GIT-LIFECYCLE-A25",
    ),
    "MOD-GL11": _r(
        "git",
        "GIT-LIFECYCLE-A7",
        "GIT-LIFECYCLE-A17",
        "GIT-LIFECYCLE-A21",
        "GIT-LIFECYCLE-A23",
        "GIT-LIFECYCLE-A24",
        "GIT-LIFECYCLE-A25",
    ),
    "MOD-GL12": _r(
        "git",
        "GIT-LIFECYCLE-A3",
        "GIT-LIFECYCLE-A4",
        "GIT-LIFECYCLE-A8",
        "GIT-LIFECYCLE-A12",
        "GIT-LIFECYCLE-A13",
        "GIT-LIFECYCLE-A16",
        "GIT-LIFECYCLE-A18",
        "GIT-LIFECYCLE-A20",
        "GIT-LIFECYCLE-A21",
        "GIT-LIFECYCLE-A22",
        "GIT-LIFECYCLE-A23",
        "GIT-LIFECYCLE-A24",
        "GIT-LIFECYCLE-A25",
        "GIT-LIFECYCLE-A26",
    ),
    "MOD-GL13": _b("git-modernization-pilot"),
}


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest root must be an object")
    return payload


def scope_digest(manifest: dict[str, Any]) -> str:
    payload = copy.deepcopy(manifest)
    payload["program"].pop("frozen_scope_digest_sha256", None)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest().upper()


def assertion_id(handle_id: str) -> str:
    return f"MSA-{handle_id}"


def _validate_proof_reference(proof: str) -> str | None:
    if proof.startswith("report:"):
        parts = proof.split(":", 2)
        if len(parts) != 3 or parts[1] not in _REPORT_ASSERTION_IDS:
            return f"unknown report proof: {proof}"
        if parts[2] not in _REPORT_ASSERTION_IDS[parts[1]]:
            return f"unknown {parts[1]} report assertion: {parts[2]}"
        return None
    if proof.startswith("pytest:"):
        nodeid = proof.removeprefix("pytest:")
        if "::" not in nodeid:
            return f"pytest proof must name an exact test node: {nodeid}"
        raw_path, symbol = nodeid.split("::", 1)
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            return f"pytest proof path is unsafe: {raw_path}"
        path = PROJECT_ROOT / relative
        if not path.is_file():
            return f"pytest proof path does not exist: {raw_path}"
        function_name = symbol.split("[", 1)[0]
        pattern = re.compile(rf"^def\s+{re.escape(function_name)}\s*\(", re.MULTILINE)
        if pattern.search(path.read_text(encoding="utf-8")) is None:
            return f"pytest proof function does not exist: {nodeid}"
        return None
    if proof.startswith("builtin:"):
        name = proof.removeprefix("builtin:")
        if name in _BUILTIN_NAMES:
            return None
        if name.startswith("receipt:") and name.removeprefix("receipt:"):
            return None
        if name.startswith("activity:") and name.removeprefix("activity:") in {
            "all",
            "ops",
            "deliberation",
            "build",
            "test",
            "spec",
            "project",
        }:
            return None
        return f"unknown builtin proof: {name}"
    return f"unsupported semantic proof: {proof}"


def validate_bindings(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    handles = manifest.get("scope_handles")
    if not isinstance(handles, list):
        return ["scope_handles must be an array"]
    ids = [item.get("id") for item in handles if isinstance(item, dict)]
    if len(ids) != 94 or len(set(ids)) != 94:
        errors.append("semantic contract requires exactly 94 unique scope handles")
    if set(ids) != set(PROOFS):
        errors.append(
            "semantic proof coverage mismatch: "
            f"missing={sorted(set(ids) - set(PROOFS))}, extra={sorted(set(PROOFS) - set(ids))}"
        )
    seen_assertions: set[str] = set()
    for index, handle in enumerate(handles):
        if not isinstance(handle, dict):
            errors.append(f"scope_handles[{index}] must be an object")
            continue
        handle_id = handle.get("id")
        expected = assertion_id(handle_id) if isinstance(handle_id, str) else ""
        bound = handle.get("semantic_assertion_ids")
        if bound != [expected]:
            errors.append(f"{handle_id}: semantic_assertion_ids must be exactly [{expected!r}]")
        for bound_id in bound if isinstance(bound, list) else []:
            if not isinstance(bound_id, str):
                continue
            if bound_id in seen_assertions:
                errors.append(f"duplicate semantic assertion id: {bound_id}")
            seen_assertions.add(bound_id)
        if not isinstance(handle.get("objective"), str) or not handle["objective"].strip():
            errors.append(f"{handle_id}: objective must be non-empty")
        proofs = PROOFS.get(handle_id, ())
        if not proofs:
            errors.append(f"{handle_id}: semantic assertion has no executable proof")
        for proof in proofs:
            proof_error = _validate_proof_reference(proof)
            if proof_error:
                errors.append(f"{handle_id}: {proof_error}")
    return errors


def _artifact_report(project_root: Path) -> dict[str, Any]:
    from scripts.check_artifact_decontamination import audit_repository

    return audit_repository(project_root)


def _context_report() -> dict[str, Any]:
    from scripts.check_context_manifests import run_contract

    return run_contract()


def _git_report() -> dict[str, Any]:
    from scripts.check_modernization_git_lifecycle import run_acceptance

    return run_acceptance()


def _git_head(project_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    head = result.stdout.strip()
    return head if result.returncode == 0 and _GIT_HEAD_RE.fullmatch(head) else ""


def _safe_evidence_error(project_root: Path, evidence: object) -> str | None:
    if not isinstance(evidence, dict) or not {"path", "sha256"} <= set(evidence):
        return "evidence reference must contain path and sha256"
    raw_path = evidence.get("path")
    expected = evidence.get("sha256")
    if not isinstance(raw_path, str) or not raw_path or not isinstance(expected, str):
        return "evidence reference path and sha256 must be non-empty strings"
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts or _SHA256_RE.fullmatch(expected) is None:
        return "evidence reference is not a safe project-relative path with an uppercase SHA-256"
    root = project_root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return "evidence reference escapes the project root"
    if not path.is_file():
        return f"evidence file does not exist: {raw_path}"
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if actual != expected:
        return f"evidence path/hash mismatch: {raw_path}"
    byte_count = evidence.get("byte_count")
    if byte_count is not None and byte_count != path.stat().st_size:
        return f"evidence byte-count mismatch: {raw_path}"
    return None


def _safe_evidence_file(project_root: Path, evidence: object) -> bool:
    return _safe_evidence_error(project_root, evidence) is None


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object")
    return payload


def _project_ref(project_root: Path, path: Path) -> dict[str, str]:
    relative = path.resolve().relative_to(project_root.resolve()).as_posix()
    return {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}


def _native_io_path(path: Path) -> str:
    resolved = str(path.resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    if resolved.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved[2:]
    return "\\\\?\\" + resolved


def _canonical_session_authority_errors(
    project_root: Path,
    authority: object,
    *,
    evidence_dir: Path,
) -> list[str]:
    if not isinstance(authority, dict):
        return ["session authority must be an object"]
    session = authority.get("session")
    envelope_ref = authority.get("session_envelope")
    if not isinstance(session, dict):
        return ["session authority lacks resolved provenance"]
    session_id = session.get("session_id")
    harness_name = session.get("harness_name")
    if not isinstance(session_id, str) or not isinstance(harness_name, str):
        return ["session authority lacks session_id or harness_name"]
    if harness_name in {".", ".."} or Path(harness_name).name != harness_name:
        return ["session authority harness_name is not a safe path component"]
    try:
        envelope_path = worker_session_envelope_path(project_root, harness_name, session_id)
    except EnvelopeError as exc:
        return [f"canonical session provenance is invalid: {exc}"]
    errors: list[str] = []
    if not isinstance(envelope_ref, dict):
        return ["session authority lacks a session-envelope reference"]
    source_path = envelope_ref.get("path")
    snapshot_path = envelope_ref.get("snapshot_path")
    expected_sha256 = envelope_ref.get("sha256")
    try:
        canonical_source = envelope_path.resolve().relative_to(project_root.resolve()).as_posix()
        resolved_evidence_dir = evidence_dir.resolve()
        resolved_evidence_dir.relative_to(project_root.resolve())
    except ValueError as exc:
        return [f"canonical session authority path escapes the project root: {exc}"]
    if source_path != canonical_source:
        errors.append("session envelope canonical source path mismatch")
    if not isinstance(expected_sha256, str) or _SHA256_RE.fullmatch(expected_sha256) is None:
        errors.append("session envelope captured SHA-256 is missing or malformed")
        return errors
    expected_snapshot = (
        resolved_evidence_dir / "session-envelope-snapshots" / harness_name / session_id / f"{expected_sha256}.json"
    )
    expected_snapshot_ref = expected_snapshot.resolve().relative_to(project_root.resolve()).as_posix()
    if snapshot_path != expected_snapshot_ref:
        errors.append("session envelope snapshot path is not the exact content-addressed authority path")
        return errors
    try:
        with open(_native_io_path(expected_snapshot), "rb") as stream:
            snapshot_bytes = stream.read()
    except OSError as exc:
        errors.append(f"session envelope snapshot is missing or unreadable: {exc}")
        return errors
    actual_sha256 = hashlib.sha256(snapshot_bytes).hexdigest().upper()
    if actual_sha256 != expected_sha256:
        errors.append("session envelope snapshot path/hash mismatch")
        return errors
    try:
        snapshot = json.loads(snapshot_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"session envelope snapshot is not valid UTF-8 JSON: {exc}")
        return errors
    if not isinstance(snapshot, dict):
        errors.append("session envelope snapshot must contain a JSON object")
        return errors
    try:
        resolved = _validate_worker_role_provenance(
            snapshot,
            current_session_id=session_id,
            expected_harness_name=harness_name,
        )
    except EnvelopeError as exc:
        errors.append(f"session envelope snapshot provenance is invalid: {exc}")
        return errors
    if session != resolved:
        errors.append("stored session provenance differs from the captured snapshot authority")
    return errors


def _canonical_issuer_errors(project_root: Path, issuer: object, *, evidence_dir: Path) -> list[str]:
    if not isinstance(issuer, dict):
        return ["collector issuer must be an object"]
    errors: list[str] = []
    if issuer.get("schema_version") != ISSUER_SCHEMA_VERSION:
        errors.append("collector issuer schema version mismatch")
    if issuer.get("service_id") != COLLECTOR_SERVICE_ID:
        errors.append("receipt was not issued by the canonical collector service")
    errors.extend(_canonical_session_authority_errors(project_root, issuer, evidence_dir=evidence_dir))
    return errors


def _nested_measurement_errors(
    project_root: Path,
    value: object,
    current_head: str,
    *,
    evidence_dir: Path,
) -> list[str]:
    errors: list[str] = []

    def visit(item: object) -> None:
        if isinstance(item, dict):
            if {"session", "session_envelope"} <= set(item):
                errors.extend(
                    _canonical_session_authority_errors(
                        project_root,
                        item,
                        evidence_dir=evidence_dir,
                    )
                )
                return
            if "sha256" in item:
                if error := _safe_evidence_error(project_root, item):
                    errors.append(error)
            if {"command_id", "output", "return_code"} <= set(item):
                if item.get("return_code") != 0 or item.get("timed_out") is not False:
                    errors.append(f"measurement command did not pass: {item.get('command_id')}")
                if item.get("git_head_before") != current_head or item.get("git_head_after") != current_head:
                    errors.append(f"measurement command Git HEAD mismatch: {item.get('command_id')}")
            for nested in item.values():
                visit(nested)
        elif isinstance(item, list):
            for nested in item:
                visit(nested)

    visit(value)
    return errors


def _validate_receipt_issue(
    issue_dir: Path,
    *,
    name: str,
    semantic_assertion_id: str,
    manifest: dict[str, Any],
    project_root: Path,
    evidence_dir: Path,
) -> tuple[list[str], dict[str, Any] | None]:
    receipt_path = issue_dir / "receipt.json"
    measurement_path = issue_dir / "measurement.json"
    issuance_path = issue_dir / "issuance.json"
    try:
        issuance = _read_json_object(issuance_path)
        receipt = _read_json_object(receipt_path)
        measurement = _read_json_object(measurement_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"invalid append-only issue {issue_dir}: {exc}"], None

    current_head = _git_head(project_root)
    expected_scope = scope_digest(manifest)
    issue_id = issue_dir.name
    errors: list[str] = []
    if _GIT_HEAD_RE.fullmatch(current_head) is None:
        errors.append("current full Git HEAD is unavailable")
    if _ISSUE_ID_RE.fullmatch(issue_id) is None:
        errors.append("issue id is malformed")
    expected_common = {
        "semantic_assertion_id": semantic_assertion_id,
        "scope_digest_sha256": expected_scope,
        "git_head": current_head,
    }
    for key, expected in expected_common.items():
        if receipt.get(key) != expected:
            errors.append(f"receipt {key} mismatch")
        if measurement.get(key) != expected:
            errors.append(f"measurement {key} mismatch")
        if issuance.get(key) != expected:
            errors.append(f"issuance {key} mismatch")
    receipt_expected = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "issue_id": issue_id,
        "status": "PASS",
    }
    measurement_expected = {
        "schema_version": MEASUREMENT_SCHEMA_VERSION,
        "issue_id": issue_id,
        "receipt_name": name,
        "status": "PASS",
    }
    issuance_expected = {
        "schema_version": ISSUANCE_SCHEMA_VERSION,
        "issue_id": issue_id,
        "receipt_name": name,
        "service_id": COLLECTOR_SERVICE_ID,
        "status": "ISSUED",
    }
    for key, expected in receipt_expected.items():
        if receipt.get(key) != expected:
            errors.append(f"receipt {key} mismatch")
    for key, expected in measurement_expected.items():
        if measurement.get(key) != expected:
            errors.append(f"measurement {key} mismatch")
    for key, expected in issuance_expected.items():
        if issuance.get(key) != expected:
            errors.append(f"issuance {key} mismatch")

    try:
        measurement_ref = _project_ref(project_root, measurement_path)
        receipt_ref = _project_ref(project_root, receipt_path)
    except (OSError, ValueError) as exc:
        return errors + [f"issue artifact path is outside the project root or unreadable: {exc}"], receipt
    if receipt.get("measurement") != measurement_ref or receipt.get("evidence") != [measurement_ref]:
        errors.append("receipt does not bind the exact issued measurement path/hash")
    if issuance.get("measurement") != measurement_ref or issuance.get("receipt") != receipt_ref:
        errors.append("issuance manifest does not bind the exact receipt and measurement hashes")
    issuer = receipt.get("issuer")
    if measurement.get("issuer") != issuer or issuance.get("issuer") != issuer:
        errors.append("receipt, measurement, and issuance issuer provenance differ")
    errors.extend(_canonical_issuer_errors(project_root, issuer, evidence_dir=evidence_dir))
    errors.extend(
        _nested_measurement_errors(
            project_root,
            measurement.get("observed"),
            current_head,
            evidence_dir=evidence_dir,
        )
    )

    if name == "independent-verification":
        session = issuer.get("session", {}) if isinstance(issuer, dict) else {}
        observed = measurement.get("observed", {})
        producer_ids = receipt.get("producer_session_context_ids")
        verifier_id = receipt.get("verifier_session_context_id")
        authorities = observed.get("producer_authorities", []) if isinstance(observed, dict) else []
        if (
            session.get("role") != "loyal-opposition"
            or verifier_id != session.get("session_id")
            or receipt.get("verifier_role") != "loyal-opposition"
        ):
            errors.append("independent verification was not issued by its canonical Loyal Opposition verifier")
        if (
            not isinstance(producer_ids, list)
            or not producer_ids
            or verifier_id in producer_ids
            or not isinstance(authorities, list)
            or len(authorities) != len(producer_ids)
        ):
            errors.append("independent verification lacks distinct canonical producer sessions")
        else:
            authority_ids: list[str] = []
            for authority in authorities:
                errors.extend(
                    _canonical_session_authority_errors(
                        project_root,
                        authority,
                        evidence_dir=evidence_dir,
                    )
                )
                authority_session = authority.get("session", {}) if isinstance(authority, dict) else {}
                authority_ids.append(str(authority_session.get("session_id", "")))
                if authority_session.get("role") != "prime-builder":
                    errors.append("independent verification producer is not canonically Prime Builder")
            if authority_ids != producer_ids:
                errors.append("independent verification producer authority order or identity mismatch")

    return errors, receipt


def _check_receipt(
    name: str,
    *,
    semantic_assertion_id: str,
    manifest: dict[str, Any],
    project_root: Path,
    evidence_dir: Path,
) -> CheckResult:
    issue_root = evidence_dir / "issues" / name
    issuance_paths = sorted(issue_root.glob("*/issuance.json"), reverse=True)
    if not issuance_paths:
        return CheckResult("FAIL", f"no canonical append-only collector issue exists for {name}")
    failures: list[dict[str, Any]] = []
    for issuance_path in issuance_paths:
        issue_dir = issuance_path.parent
        errors, receipt = _validate_receipt_issue(
            issue_dir,
            name=name,
            semantic_assertion_id=semantic_assertion_id,
            manifest=manifest,
            project_root=project_root,
            evidence_dir=evidence_dir,
        )
        if not errors:
            return CheckResult(
                "PASS",
                {
                    "issue_id": issue_dir.name,
                    "receipt": str(issue_dir / "receipt.json"),
                    "measurement": str(issue_dir / "measurement.json"),
                },
            )
        failures.append({"issue_id": issue_dir.name, "errors": errors, "receipt": receipt})
    return CheckResult("FAIL", {"receipt": name, "issues_checked": len(failures), "failures": failures})


def check_history_quarantine(project_root: Path = PROJECT_ROOT) -> CheckResult:
    """Prove historical payloads are query-only and absent from live worker dependencies."""

    report = _artifact_report(project_root)
    worker_rows = report.get("audit", {}).get("worker_references", [])
    artifact_assertions = {
        row.get("id"): row.get("status") for row in report.get("assertions", []) if isinstance(row, dict)
    }
    required_artifact_assertions = {"MOD-AD-05", "MOD-AD-06", "MOD-AD-07", "MOD-AD-10"}
    contaminated = [row for row in worker_rows if row.get("resolution") in {"historical", "conflict", "unknown"}]
    config_path = project_root / "config" / "agent-control" / "activity-envelope-sharding.toml"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return CheckResult("FAIL", f"cannot load quarantine taxonomy: {exc}")
    classes = config.get("classes", {})
    explicit = classes.get("explicit_query", {})
    never = classes.get("never_startup", {})
    explicit_payloads = set(explicit.get("allowed_payloads", []))
    forbidden_payloads = set(never.get("forbidden_payloads", []))
    required_explicit = {"history_state", "bridge_thread_chain", "archival_state", "deliberation_search_results"}
    required_forbidden = {
        "raw_bridge_archival_json",
        "full_session_transcripts",
        "generated_runtime_cache_directories",
        "retired_aggregate_queue_artifacts",
    }
    reports_are_not_loaded = all(
        not str(row.get("path", "")).startswith("independent-progress-assessments/") for row in worker_rows
    )
    passed = (
        not contaminated
        and all(artifact_assertions.get(assertion_id) == "PASS" for assertion_id in required_artifact_assertions)
        and explicit.get("load_policy") == "on_demand_query"
        and never.get("load_policy") == "forbidden_startup"
        and required_explicit <= explicit_payloads
        and required_forbidden <= forbidden_payloads
        and reports_are_not_loaded
    )
    return CheckResult(
        "PASS" if passed else "FAIL",
        {
            "artifact_report_status": report.get("status"),
            "required_artifact_assertions": {
                assertion_id: artifact_assertions.get(assertion_id)
                for assertion_id in sorted(required_artifact_assertions)
            },
            "historical_or_unresolved_worker_dependencies": contaminated,
            "explicit_query_payloads_present": sorted(required_explicit & explicit_payloads),
            "never_startup_payloads_present": sorted(required_forbidden & forbidden_payloads),
            "reports_absent_from_worker_dependencies": reports_are_not_loaded,
        },
    )


def check_git_modernization_pilot(
    *,
    manifest: dict[str, Any],
    project_root: Path = PROJECT_ROOT,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> CheckResult:
    """Require a real modernization pilot and a distinct-session LO verification."""

    path = evidence_dir / "git-lifecycle-modernization-pilot.json"
    try:
        receipt = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult("FAIL", f"missing or invalid real-pilot receipt {path}: {exc}")
    expected_head = _git_head(project_root)
    urls = receipt.get("github_pull_request_urls")
    author = receipt.get("author_session_context_id")
    verifier = receipt.get("verifier_session_context_id")
    checks = {
        "schema_version": receipt.get("schema_version") == 1,
        "semantic_assertion_id": receipt.get("semantic_assertion_id") == "MSA-MOD-GL13",
        "scope_digest": receipt.get("scope_digest_sha256") == scope_digest(manifest),
        "status": receipt.get("status") == "VERIFIED",
        "real_not_offline": receipt.get("offline") is False,
        "modernization_project": receipt.get("project_id") == "PROJECT-GTKB-PLATFORM-MODERNIZATION",
        "current_candidate_head": bool(expected_head)
        and _GIT_HEAD_RE.fullmatch(expected_head) is not None
        and receipt.get("candidate_head_sha") == expected_head,
        "complete_operations": set(receipt.get("operations", [])) == _PILOT_OPERATIONS,
        "real_pull_requests": isinstance(urls, list)
        and len(urls) >= 2
        and all(isinstance(url, str) and _PR_URL_RE.fullmatch(url) for url in urls),
        "independent_verifier": bool(author)
        and bool(verifier)
        and author != verifier
        and receipt.get("verifier_role") == "loyal-opposition",
        "verification_artifact": _safe_evidence_file(project_root, receipt.get("verification_artifact")),
    }
    return CheckResult("PASS" if all(checks.values()) else "FAIL", checks)


def _check_activity(name: str) -> CheckResult:
    from groundtruth_kb.activity.profiles import CANONICAL_ACTIVITY_ORDER, load_activity_profiles

    profiles = load_activity_profiles()
    selected = list(CANONICAL_ACTIVITY_ORDER) if name == "all" else [name]
    valid = all(
        activity in profiles
        and profiles[activity].version >= 1
        and profiles[activity].skills
        and profiles[activity].terminology
        and profiles[activity].direction
        and set(profiles[activity].classification) == {"skills", "terminology", "history_state", "direction"}
        for activity in selected
    )
    return CheckResult("PASS" if valid else "FAIL", {activity: activity in profiles for activity in selected})


def _expected_program_dependencies(project_by_family: dict[str, str]) -> set[tuple[str, str]]:
    return {
        (project_by_family["CONTEXT_MANIFESTS"], project_by_family["AUTHORITY_FOUNDATIONS"]),
        (project_by_family["ARTIFACT_DECONTAMINATION"], project_by_family["AUTHORITY_FOUNDATIONS"]),
        (project_by_family["RUNTIME_INTERFACES"], project_by_family["AUTHORITY_FOUNDATIONS"]),
        (project_by_family["RUNTIME_INTERFACES"], project_by_family["CONTEXT_MANIFESTS"]),
        (project_by_family["RUNTIME_INTERFACES"], project_by_family["ARTIFACT_DECONTAMINATION"]),
        (project_by_family["HARNESS_PARITY"], project_by_family["RUNTIME_INTERFACES"]),
        (project_by_family["GIT_LIFECYCLE"], project_by_family["AUTHORITY_FOUNDATIONS"]),
        (project_by_family["GIT_LIFECYCLE"], project_by_family["RUNTIME_INTERFACES"]),
        (project_by_family["ASSURANCE"], project_by_family["CONTEXT_MANIFESTS"]),
        (project_by_family["ASSURANCE"], project_by_family["ARTIFACT_DECONTAMINATION"]),
        (project_by_family["ASSURANCE"], project_by_family["RUNTIME_INTERFACES"]),
        (project_by_family["ASSURANCE"], project_by_family["HARNESS_PARITY"]),
        (project_by_family["ASSURANCE"], project_by_family["GIT_LIFECYCLE"]),
    }


def _check_program_hierarchy(manifest: dict[str, Any], project_root: Path) -> CheckResult:
    project_by_family = {
        str(family.get("id")): str(family.get("project_id")) for family in manifest.get("scope_families", [])
    }
    projects = list(project_by_family.values())
    expected_root = str(manifest.get("program", {}).get("project_id"))
    expected_dependencies = _expected_program_dependencies(project_by_family)
    database_path = project_root / "groundtruth.db"
    try:
        connection = sqlite3.connect(f"file:{database_path.as_posix()}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in projects)
        project_rows = connection.execute(
            f"SELECT id, status, parent_project_id FROM current_projects WHERE id IN ({placeholders})",
            projects,
        ).fetchall()
        membership_rows = connection.execute(
            "SELECT project_id, COUNT(*) AS membership_count "
            f"FROM current_project_work_item_memberships WHERE project_id IN ({placeholders}) "
            "AND status = 'active' GROUP BY project_id",
            projects,
        ).fetchall()
        dependency_rows = connection.execute(
            "SELECT from_project_id, to_project_id FROM current_project_dependencies "
            f"WHERE status = 'active' AND from_project_id IN ({placeholders}) AND to_project_id IN ({placeholders})",
            [*projects, *projects],
        ).fetchall()
    except sqlite3.Error as exc:
        return CheckResult("FAIL", {"database": str(database_path), "error": str(exc)})
    finally:
        if "connection" in locals():
            connection.close()

    project_records = {str(row["id"]): dict(row) for row in project_rows}
    membership_counts = {str(row["project_id"]): int(row["membership_count"]) for row in membership_rows}
    actual_dependencies = {(str(row["from_project_id"]), str(row["to_project_id"])) for row in dependency_rows}
    root_record = project_records.get(expected_root)
    child_ids = set(projects) - {expected_root}
    checks = {
        "manifest_has_exact_eight_projects": len(projects) == 8 and len(set(projects)) == 8,
        "all_projects_exist_and_are_active": len(project_records) == 8
        and all(record["status"] == "active" for record in project_records.values()),
        "root_project_is_unparented": root_record is not None and root_record["parent_project_id"] is None,
        "seven_children_bind_the_root": all(
            project_records.get(project_id, {}).get("parent_project_id") == expected_root for project_id in child_ids
        ),
        "every_project_has_active_work_items": set(membership_counts) == set(projects)
        and all(count > 0 for count in membership_counts.values()),
        "dependency_dag_is_exact": actual_dependencies == expected_dependencies,
    }
    return CheckResult(
        "PASS" if all(checks.values()) else "FAIL",
        {
            "checks": checks,
            "project_ids": projects,
            "membership_counts": membership_counts,
            "dependencies": sorted([list(edge) for edge in actual_dependencies]),
            "expected_dependencies": sorted([list(edge) for edge in expected_dependencies]),
        },
    )


def _check_traceability_contract(manifest: dict[str, Any], project_root: Path) -> CheckResult:
    binding_errors = validate_bindings(manifest)
    hierarchy = _check_program_hierarchy(manifest, project_root)
    handles = manifest.get("scope_handles", [])
    families = {str(item.get("id")): str(item.get("project_id")) for item in manifest.get("scope_families", [])}
    handle_checks = [
        isinstance(handle, dict)
        and handle.get("scope_family") in families
        and bool(handle.get("objective"))
        and bool(handle.get("implementation_evidence_paths"))
        and bool(handle.get("acceptance_test_ids"))
        and bool(handle.get("semantic_assertion_ids"))
        for handle in handles
    ]
    passed = not binding_errors and hierarchy.status == "PASS" and len(handle_checks) == 94 and all(handle_checks)
    return CheckResult(
        "PASS" if passed else "FAIL",
        {
            "binding_errors": binding_errors,
            "hierarchy": hierarchy.evidence,
            "handle_count": len(handle_checks),
            "handles_with_complete_traceability": sum(handle_checks),
        },
    )


def _check_umbrella_bridge(project_root: Path) -> CheckResult:
    path = project_root / "bridge" / "gtkb-modernization-gate-1-25-execution-design-001.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return CheckResult("FAIL", str(exc))
    required = (
        "Project: PROJECT-GTKB-PLATFORM-MODERNIZATION",
        "bridge_kind: governance_advisory",
        "target_paths: []",
        "## Claim",
    )
    passed = all(token in text for token in required)
    return CheckResult("PASS" if passed else "FAIL", {token: token in text for token in required})


class SemanticRunner:
    def __init__(
        self,
        *,
        manifest: dict[str, Any],
        project_root: Path = PROJECT_ROOT,
        evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
    ) -> None:
        self.manifest = manifest
        self.project_root = project_root
        self.evidence_dir = evidence_dir
        self.cache: dict[str, CheckResult] = {}
        self.report_cache: dict[str, dict[str, Any]] = {}

    def run_proof(self, proof: str, semantic_assertion_id: str) -> CheckResult:
        cache_key = f"{semantic_assertion_id}:{proof}" if "receipt:" in proof else proof
        if cache_key in self.cache:
            return self.cache[cache_key]
        if proof.startswith("report:"):
            _, source, expected_id = proof.split(":", 2)
            if source not in self.report_cache:
                loader: dict[str, Callable[[], dict[str, Any]]] = {
                    "artifact": lambda: _artifact_report(self.project_root),
                    "context": _context_report,
                    "git": _git_report,
                }
                self.report_cache[source] = loader[source]()
            rows = self.report_cache[source].get("assertions", [])
            row = next((item for item in rows if item.get("id") == expected_id), None)
            result = CheckResult("PASS" if row and row.get("status") == "PASS" else "FAIL", row)
        elif proof.startswith("pytest:"):
            nodeid = proof.removeprefix("pytest:")
            completed = subprocess.run(
                [sys.executable, "-m", "pytest", nodeid, "-q", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            result = CheckResult(
                "PASS" if completed.returncode == 0 else "FAIL",
                {
                    "nodeid": nodeid,
                    "returncode": completed.returncode,
                    "output_tail": (completed.stdout + completed.stderr)[-2000:],
                },
            )
        else:
            name = proof.removeprefix("builtin:")
            if name == "program-hierarchy":
                result = _check_program_hierarchy(self.manifest, self.project_root)
            elif name == "umbrella-bridge-proposal":
                result = _check_umbrella_bridge(self.project_root)
            elif name == "traceability-contract":
                result = _check_traceability_contract(self.manifest, self.project_root)
            elif name == "history-quarantine":
                result = check_history_quarantine(self.project_root)
            elif name == "git-modernization-pilot":
                result = check_git_modernization_pilot(
                    manifest=self.manifest,
                    project_root=self.project_root,
                    evidence_dir=self.evidence_dir,
                )
            elif name.startswith("activity:"):
                result = _check_activity(name.split(":", 1)[1])
            elif name.startswith("receipt:"):
                result = _check_receipt(
                    name.split(":", 1)[1],
                    semantic_assertion_id=semantic_assertion_id,
                    manifest=self.manifest,
                    project_root=self.project_root,
                    evidence_dir=self.evidence_dir,
                )
            else:
                result = CheckResult("FAIL", f"unknown builtin proof: {name}")
        self.cache[cache_key] = result
        return result


def run_assertions(
    manifest: dict[str, Any],
    *,
    selected_assertion_ids: set[str] | None = None,
    project_root: Path = PROJECT_ROOT,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
) -> dict[str, Any]:
    binding_errors = validate_bindings(manifest)
    if binding_errors:
        return {"schema_version": 1, "status": "FAIL", "binding_errors": binding_errors, "assertions": []}
    runner = SemanticRunner(manifest=manifest, project_root=project_root, evidence_dir=evidence_dir)
    rows: list[dict[str, Any]] = []
    handles = {item["id"]: item for item in manifest["scope_handles"]}
    for handle_id, proofs in PROOFS.items():
        current_assertion_id = assertion_id(handle_id)
        if selected_assertion_ids is not None and current_assertion_id not in selected_assertion_ids:
            continue
        proof_results = [runner.run_proof(proof, current_assertion_id) for proof in proofs]
        rows.append(
            {
                "id": current_assertion_id,
                "handle_id": handle_id,
                "objective": handles[handle_id]["objective"],
                "status": "PASS" if all(result.status == "PASS" for result in proof_results) else "FAIL",
                "proofs": [
                    {"id": proof, "status": result.status, "evidence": result.evidence}
                    for proof, result in zip(proofs, proof_results, strict=True)
                ],
            }
        )
    return {
        "schema_version": 1,
        "scope_digest_sha256": scope_digest(manifest),
        "status": "PASS" if rows and all(row["status"] == "PASS" for row in rows) else "FAIL",
        "binding_errors": [],
        "assertions": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate exact 94-handle semantic bindings")
    validate_parser.add_argument("--json", action="store_true", dest="as_json")
    run_parser = subparsers.add_parser("run", help="execute semantic assertions")
    run_parser.add_argument("--assertion", action="append", default=[])
    run_parser.add_argument("--phase", choices=("clean-suite", "final"), default="final")
    run_parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    manifest = load_manifest(DEFAULT_MANIFEST)
    if args.command == "validate":
        errors = validate_bindings(manifest)
        payload = {"status": "PASS" if not errors else "FAIL", "handle_count": len(PROOFS), "errors": errors}
    else:
        selected = set(args.assertion) or None
        unknown = sorted((selected or set()) - {assertion_id(handle) for handle in PROOFS})
        if unknown:
            payload = {"status": "FAIL", "errors": [f"unknown assertion ids: {unknown}"]}
        else:
            if args.phase == "clean-suite":
                clean_suite_ids = {assertion_id(handle) for handle in PROOFS} - POST_CLEAN_ASSERTION_IDS
                selected = clean_suite_ids if selected is None else selected & clean_suite_ids
            payload = run_assertions(manifest, selected_assertion_ids=selected, evidence_dir=DEFAULT_EVIDENCE_DIR)
            payload["phase"] = args.phase
    if args.as_json:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print(f"MODERNIZATION SCOPE SEMANTICS: {payload['status']}")
        for error in payload.get("errors", payload.get("binding_errors", [])):
            print(f"- {error}")
        for row in payload.get("assertions", []):
            print(f"- {row['id']}: {row['status']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
