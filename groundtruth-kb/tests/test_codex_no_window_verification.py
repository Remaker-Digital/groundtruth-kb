from __future__ import annotations

from copy import deepcopy
from typing import Any

import pytest

from groundtruth_kb.codex_no_window_verification import SCHEMA_VERSION, schema_failure_reason


def _valid_payload() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "dispatcher_wrapper_path": True,
        "wrapper_ok": True,
        "containment_mechanism": "windows_private_desktop",
        "requested_permissions_profile": ":workspace",
        "effective_profile_ok": True,
        "sentinel_lifecycle_ok": True,
        "runs": [
            {
                "requested_permissions_profile": ":workspace",
                "observed_effective_profile": "workspace-write",
                "effective_profile_ok": True,
                "sentinel_lifecycle_ok": True,
                "sentinel_residual_before_cleanup": False,
                "sentinel_residual_after_cleanup": False,
                "wrapper_returncode": 0,
                "command_steps": [
                    {
                        "marker": f"marker-{run}-{step}",
                        "returncode": 0,
                        "stdout_contains_marker": True,
                    }
                    for step in range(3)
                ],
            }
            for run in range(2)
        ],
    }


def _replace(payload: dict[str, Any], path: tuple[object, ...], value: object) -> None:
    target: Any = payload
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = value


def test_schema_failure_reason_accepts_complete_schema_v3_evidence() -> None:
    assert schema_failure_reason(_valid_payload()) is None


@pytest.mark.parametrize(
    ("path", "value", "reason"),
    [
        (("schema_version",), 2, "codex_no_window_verification_legacy_schema"),
        (("runs",), [], "codex_no_window_verification_insufficient_run_count"),
        (("dispatcher_wrapper_path",), False, "codex_no_window_verification_missing_dispatch_wrapper"),
        (("wrapper_ok",), False, "codex_no_window_verification_missing_dispatch_wrapper"),
        (("containment_mechanism",), "visible_console", "codex_no_window_verification_missing_private_desktop"),
        (("requested_permissions_profile",), ":read-only", "codex_no_window_verification_requested_profile_mismatch"),
        (("effective_profile_ok",), False, "codex_no_window_verification_effective_profile_mismatch"),
        (("sentinel_lifecycle_ok",), False, "codex_no_window_verification_incomplete_sentinel_lifecycle"),
        (("runs", 0, "command_steps"), [], "codex_no_window_verification_insufficient_command_count"),
        (("runs", 0, "command_steps", 0, "marker"), "", "codex_no_window_verification_missing_marker_chain"),
        (
            ("runs", 0, "requested_permissions_profile"),
            ":read-only",
            "codex_no_window_verification_requested_profile_mismatch",
        ),
        (
            ("runs", 0, "observed_effective_profile"),
            "read-only",
            "codex_no_window_verification_effective_profile_mismatch",
        ),
        (("runs", 0, "effective_profile_ok"), False, "codex_no_window_verification_effective_profile_mismatch"),
        (
            ("runs", 0, "sentinel_lifecycle_ok"),
            False,
            "codex_no_window_verification_incomplete_sentinel_lifecycle",
        ),
        (("runs", 0, "sentinel_residual_before_cleanup"), True, "codex_no_window_verification_sentinel_residue"),
        (("runs", 0, "sentinel_residual_after_cleanup"), True, "codex_no_window_verification_sentinel_residue"),
        (("runs", 0, "wrapper_returncode"), 1, "codex_no_window_verification_dispatch_wrapper_failed"),
    ],
)
def test_schema_failure_reason_rejects_each_required_structural_violation(
    path: tuple[object, ...],
    value: object,
    reason: str,
) -> None:
    payload = deepcopy(_valid_payload())
    _replace(payload, path, value)

    assert schema_failure_reason(payload) == reason
