"""Canonical structural contract for Codex no-window verification evidence."""

from __future__ import annotations

from typing import Any

SCHEMA_VERSION = 3
MIN_RUNS = 2
MIN_COMMAND_STEPS = 3
REQUIRED_PERMISSIONS_PROFILE = ":workspace"
REQUIRED_EFFECTIVE_PROFILE = "workspace-write"


def _run_steps(run: object) -> list[dict[str, Any]]:
    if not isinstance(run, dict):
        return []
    raw_steps = run.get("command_steps")
    if raw_steps is None:
        raw_steps = run.get("commands")
    if not isinstance(raw_steps, list):
        return []
    return [step for step in raw_steps if isinstance(step, dict)]


def _step_has_marker_proof(step: dict[str, Any]) -> bool:
    marker = str(step.get("marker") or step.get("expected_marker") or "").strip()
    if not marker or step.get("returncode") not in {0, "0"}:
        return False
    if step.get("stdout_contains_marker") is True:
        return True
    transcript = str(step.get("transcript_preview") or step.get("stdout_preview") or step.get("stdout") or "")
    return marker in transcript


def schema_failure_reason(payload: dict[str, Any]) -> str | None:
    """Return the stable fail-closed reason for malformed schema-v3 evidence."""
    if payload.get("schema_version") != SCHEMA_VERSION:
        return "codex_no_window_verification_legacy_schema"
    runs = payload.get("runs")
    if not isinstance(runs, list) or len(runs) < MIN_RUNS:
        return "codex_no_window_verification_insufficient_run_count"
    if payload.get("dispatcher_wrapper_path") is not True or payload.get("wrapper_ok") is not True:
        return "codex_no_window_verification_missing_dispatch_wrapper"
    if payload.get("containment_mechanism") != "windows_private_desktop":
        return "codex_no_window_verification_missing_private_desktop"
    if payload.get("requested_permissions_profile") != REQUIRED_PERMISSIONS_PROFILE:
        return "codex_no_window_verification_requested_profile_mismatch"
    if payload.get("effective_profile_ok") is not True:
        return "codex_no_window_verification_effective_profile_mismatch"
    if payload.get("sentinel_lifecycle_ok") is not True:
        return "codex_no_window_verification_incomplete_sentinel_lifecycle"
    for run in runs:
        steps = _run_steps(run)
        if len(steps) < MIN_COMMAND_STEPS:
            return "codex_no_window_verification_insufficient_command_count"
        if not all(_step_has_marker_proof(step) for step in steps):
            return "codex_no_window_verification_missing_marker_chain"
        if run.get("requested_permissions_profile") != REQUIRED_PERMISSIONS_PROFILE:
            return "codex_no_window_verification_requested_profile_mismatch"
        if run.get("observed_effective_profile") != REQUIRED_EFFECTIVE_PROFILE:
            return "codex_no_window_verification_effective_profile_mismatch"
        if run.get("effective_profile_ok") is not True:
            return "codex_no_window_verification_effective_profile_mismatch"
        if run.get("sentinel_lifecycle_ok") is not True:
            return "codex_no_window_verification_incomplete_sentinel_lifecycle"
        if run.get("sentinel_residual_before_cleanup") is not False:
            return "codex_no_window_verification_sentinel_residue"
        if run.get("sentinel_residual_after_cleanup") is not False:
            return "codex_no_window_verification_sentinel_residue"
        if run.get("wrapper_returncode") not in {0, "0"}:
            return "codex_no_window_verification_dispatch_wrapper_failed"
    return None
