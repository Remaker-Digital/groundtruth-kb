"""Unit tests for DORA-001b Track 1 manifest writer enhancement.

Tests the writer side: does scripts/deploy_pipeline.py populate the
`_deploy_evidence` accumulator correctly during phase 8 / 10 / 15, and
does the manifest write site inject the block under the right conditions
(non-empty phase_timings only, excluding dry-run mode)?

Created 2026-04-28 (S319) per
`bridge/gtkb-dora-001b-track1-implementation-006.md` Codex GO.
Implementation contract: `bridge/gtkb-dora-001b-track1-implementation-005.md`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import deploy_pipeline  # noqa: E402


class _Result:
    """Minimal CompletedProcess stand-in for mocking _run."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _build_args(
    env: str = "production", version: str = "v1.99.0", dry_run: bool = False, with_evidence: bool = True
) -> argparse.Namespace:
    """Build an args namespace shaped like deploy_pipeline.main() would produce."""
    args = argparse.Namespace(
        env=env,
        version=version,
        dry_run=dry_run,
        approved=True,
    )
    if with_evidence:
        args._deploy_evidence = {"phase_timings": {}}
    return args


# ---------------------------------------------------------------------------
# Phase 8 tests (T2-T8)
# ---------------------------------------------------------------------------


def test_phase_8_populates_image_and_tag() -> None:
    """T2: phase_8 sets image, image_tag, target_container_app on entry."""
    args = _build_args()
    with patch.object(deploy_pipeline, "_run") as mock_run:
        # az update success, az show returns matching image, az revision returns name
        mock_run.side_effect = [
            _Result(0, "", ""),
            _Result(0, f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0", ""),
            _Result(0, "rev-abc123\n", ""),
        ]
        result = deploy_pipeline.phase_8_deploy(args)

    assert result.passed
    assert args._deploy_evidence["image"] == f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
    assert args._deploy_evidence["image_tag"] == "v1.99.0"
    assert args._deploy_evidence["target_container_app"] == deploy_pipeline.ENVIRONMENTS["production"]["container_app"]


def test_phase_8_populates_target_update_attempted_after_az_update() -> None:
    """T3: az returncode 0 → target_update_attempted=True, target_update_succeeded=True."""
    args = _build_args()
    image = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
    with patch.object(deploy_pipeline, "_run") as mock_run:
        mock_run.side_effect = [
            _Result(0, "", ""),
            _Result(0, image, ""),
            _Result(0, "rev-abc\n", ""),
        ]
        deploy_pipeline.phase_8_deploy(args)

    assert args._deploy_evidence["target_update_attempted"] is True
    assert args._deploy_evidence["target_update_succeeded"] is True


def test_phase_8_target_update_succeeded_false_when_az_returncode_nonzero() -> None:
    """T4: az returncode != 0 → target_update_succeeded=False; phase returns FAIL."""
    args = _build_args()
    with patch.object(deploy_pipeline, "_run") as mock_run:
        mock_run.return_value = _Result(1, "", "az auth failed")
        result = deploy_pipeline.phase_8_deploy(args)

    assert not result.passed
    assert args._deploy_evidence["target_update_attempted"] is True
    assert args._deploy_evidence["target_update_succeeded"] is False
    # Phase timing recorded on failure path (Codex GO -006 condition 2)
    assert "phase_9_deploy" in args._deploy_evidence["phase_timings"]


def test_phase_8_target_update_succeeded_downgraded_on_image_mismatch() -> None:
    """T5: az update succeeds but verify-image returns different image → False."""
    args = _build_args()
    actual = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.98.92"
    with patch.object(deploy_pipeline, "_run") as mock_run:
        mock_run.side_effect = [
            _Result(0, "", ""),
            _Result(0, actual, ""),
            _Result(0, "rev-old\n", ""),
        ]
        result = deploy_pipeline.phase_8_deploy(args)

    assert result.passed  # mismatch is just a WARN, not a FAIL
    assert args._deploy_evidence["target_update_attempted"] is True
    assert args._deploy_evidence["target_update_succeeded"] is False  # downgraded


def test_phase_8_revision_name_captured_when_az_query_succeeds() -> None:
    """T6: az revision-list returns name → revision_name populated."""
    args = _build_args()
    image = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
    with patch.object(deploy_pipeline, "_run") as mock_run:
        mock_run.side_effect = [
            _Result(0, "", ""),
            _Result(0, image, ""),
            _Result(0, "agent-red--rev-xyz789\n", ""),
        ]
        deploy_pipeline.phase_8_deploy(args)

    assert args._deploy_evidence["revision_name"] == "agent-red--rev-xyz789"
    assert "target_verified_at" in args._deploy_evidence


def test_phase_8_revision_name_failure_does_not_fail_phase() -> None:
    """T7: revision-list returns nonzero → revision_name not set, phase still PASS."""
    args = _build_args()
    image = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
    with patch.object(deploy_pipeline, "_run") as mock_run:
        mock_run.side_effect = [
            _Result(0, "", ""),
            _Result(0, image, ""),
            _Result(1, "", "rate limited"),  # revision list fails
        ]
        result = deploy_pipeline.phase_8_deploy(args)

    assert result.passed
    assert "revision_name" not in args._deploy_evidence
    # Other fields still populated
    assert args._deploy_evidence["target_update_succeeded"] is True
    assert "target_verified_at" in args._deploy_evidence


def test_phase_8_phase_timings_captured() -> None:
    """T8: phase_timings.phase_9_deploy contains started_at/completed_at/duration_seconds."""
    args = _build_args()
    image = f"{deploy_pipeline.ACR_LOGIN_SERVER}/{deploy_pipeline.IMAGE_REPO}:v1.99.0"
    with patch.object(deploy_pipeline, "_run") as mock_run:
        mock_run.side_effect = [
            _Result(0, "", ""),
            _Result(0, image, ""),
            _Result(0, "rev-abc\n", ""),
        ]
        deploy_pipeline.phase_8_deploy(args)

    timings = args._deploy_evidence["phase_timings"]["phase_9_deploy"]
    assert "started_at" in timings
    assert "completed_at" in timings
    assert "duration_seconds" in timings
    assert isinstance(timings["duration_seconds"], (int, float))


# ---------------------------------------------------------------------------
# Phase 10 tests (T9-T10)
# ---------------------------------------------------------------------------


def test_phase_10_records_deployed_at_on_version_match() -> None:
    """T9: phase_10 sets deployed_at + phase timing when version matches."""
    args = _build_args(version="v1.99.0")
    with patch.object(deploy_pipeline, "api_call") as mock_api, patch.object(deploy_pipeline, "time") as mock_time:
        mock_time.time.side_effect = [1000.0, 1000.0, 1001.0]
        mock_time.sleep = lambda _x: None
        mock_api.return_value = (200, {"product_version": "1.99.0"}, "")
        result = deploy_pipeline.phase_10_startup_and_version(args)

    assert result.passed
    assert "deployed_at" in args._deploy_evidence
    assert "phase_10_startup_and_version" in args._deploy_evidence["phase_timings"]


def test_phase_10_does_not_record_deployed_at_on_version_mismatch() -> None:
    """T10: phase_10 does NOT set deployed_at when version never matches."""
    args = _build_args(version="v1.99.0")
    # Use HEALTH_WAIT_SECONDS=0 by stubbing at module level so the loop terminates.
    with (
        patch.object(deploy_pipeline, "api_call") as mock_api,
        patch.object(deploy_pipeline, "HEALTH_WAIT_SECONDS", 0),
        patch.object(deploy_pipeline, "HEALTH_POLL_INTERVAL", 1),
        patch.object(deploy_pipeline.time, "sleep", lambda _x: None),
    ):
        # Always return mismatch
        mock_api.return_value = (200, {"product_version": "1.98.92"}, "")
        result = deploy_pipeline.phase_10_startup_and_version(args)

    assert not result.passed
    assert "deployed_at" not in args._deploy_evidence
    assert "phase_10_startup_and_version" not in args._deploy_evidence["phase_timings"]


# ---------------------------------------------------------------------------
# Phase 15 tests (T11)
# ---------------------------------------------------------------------------


def test_phase_15_records_phase_timing() -> None:
    """T11: phase_15 records phase_timings.phase_15_enforce_scaling on success."""
    args = _build_args()
    fake_results = {"app-a": True, "app-b": True}

    # Patch the lazy imports to skip the real scaling-enforcement library.
    with patch.dict(
        sys.modules,
        {
            "lib.scaling_enforcement": type(sys)("lib.scaling_enforcement"),
            "lib.scaling_targets": type(sys)("lib.scaling_targets"),
        },
    ):
        sys.modules["lib.scaling_enforcement"].enforce_all_scaling = lambda **_kw: fake_results
        sys.modules["lib.scaling_targets"].get_scaling_targets = lambda _env: []
        sys.modules["lib.scaling_targets"].SCALING_CONFIG = {}
        sys.modules["lib.scaling_targets"].RESOURCE_GROUP = "Agent-Red"
        result = deploy_pipeline.phase_15_enforce_scaling(args)

    assert result.passed
    timings = args._deploy_evidence["phase_timings"]["phase_15_enforce_scaling"]
    assert "started_at" in timings
    assert "completed_at" in timings
    assert "duration_seconds" in timings


# ---------------------------------------------------------------------------
# Main() and dry-run tests (T1, T12, T13)
# ---------------------------------------------------------------------------


def test_evidence_dict_initialized_in_main() -> None:
    """T1: main() initializes args._deploy_evidence early with empty phase_timings.

    Verified by a sentinel phase_0 that captures args after main()'s init code
    runs but before any other phase. By the time phase_0 is called, args has
    been parsed, validated, and `_deploy_evidence` initialized.
    """
    captured: dict[str, Any] = {}

    def _capture_phase(args: argparse.Namespace) -> deploy_pipeline.PhaseResult:
        captured["args"] = args
        raise SystemExit(0)

    fake_args = argparse.Namespace(env="staging", version="v1.99.0", dry_run=True, approved=False)
    with (
        patch.object(deploy_pipeline.argparse.ArgumentParser, "parse_args", return_value=fake_args),
        patch.object(deploy_pipeline, "phase_0_validate_environment", _capture_phase),
    ):
        try:
            deploy_pipeline.main()
        except SystemExit:
            pass

    assert "args" in captured, "phase_0 was never called — main() exited earlier"
    assert hasattr(captured["args"], "_deploy_evidence")
    assert captured["args"]._deploy_evidence == {"phase_timings": {}}


def _patch_main_pipeline_phases(
    stack: contextlib.ExitStack,
    fake_args: argparse.Namespace,
    phase_8_impl: Any,
    other_phase_impl: Any,
    tmp_path: Path,
) -> Any:
    """Stack-based phase patching to avoid Python's nested-with limit (~20).

    Returns the subprocess.run mock so callers can configure return_value.
    """
    other_phases = [
        "phase_0_validate_environment",
        "phase_1_protected_behaviors",
        "phase_2_clear_vite_api_url",
        "phase_3_build_artifacts",
        "phase_4_freshness_gate",
        "phase_5_restore_env_local",
        "phase_7_acr_build",
        "phase_10_startup_and_version",
        "phase_15_enforce_scaling",
        "phase_10a_pre_deploy_snapshot",
        "phase_11_production_verification",
        "phase_13_seed_test_tenant",
        "phase_13_upgrade_verification",
        "phase_14_verify_initialized_state",
        "phase_14_config_pipeline",
    ]

    stack.enter_context(patch.object(deploy_pipeline.argparse.ArgumentParser, "parse_args", return_value=fake_args))
    for name in other_phases:
        stack.enter_context(patch.object(deploy_pipeline, name, other_phase_impl))
    stack.enter_context(patch.object(deploy_pipeline, "phase_8_deploy", phase_8_impl))
    stack.enter_context(
        patch.object(deploy_pipeline, "phase_6_create_build_context", lambda _a: (other_phase_impl(_a), ""))
    )
    stack.enter_context(patch.object(deploy_pipeline, "_print_summary", lambda *_a, **_kw: None))
    stack.enter_context(patch.object(deploy_pipeline, "_write_log_file", lambda _e: None))
    stack.enter_context(patch.object(deploy_pipeline, "PROJECT_ROOT", tmp_path))
    stack.enter_context(patch.object(deploy_pipeline.time, "sleep", lambda _x: None))
    mock_sp_run = stack.enter_context(patch.object(deploy_pipeline.subprocess, "run"))
    mock_sp_run.return_value = type("R", (), {"returncode": 0, "stdout": "abc123def456\n", "stderr": ""})()
    return mock_sp_run


def test_main_emits_manifest_with_deploy_evidence_block(tmp_path: Path) -> None:
    """T12: main() with successful phases produces manifest containing deploy_evidence."""
    fake_args = argparse.Namespace(env="staging", version="v1.99.0", dry_run=False, approved=True)

    def _phase_pass(*args_: Any, **_kw: Any) -> deploy_pipeline.PhaseResult:
        # Synthesize meaningful evidence so the gate passes.
        args = args_[0]
        args._deploy_evidence["image"] = "fake/image:v1.99.0"
        args._deploy_evidence["target_update_attempted"] = True
        args._deploy_evidence["target_update_succeeded"] = True
        args._deploy_evidence["phase_timings"]["phase_9_deploy"] = {
            "started_at": "2026-04-28T00:00:00",
            "completed_at": "2026-04-28T00:01:00",
            "duration_seconds": 60.0,
        }
        return deploy_pipeline.PhaseResult(9, "fake", "PASS", 0.1)

    def _phase_other(*_a: Any, **_kw: Any) -> deploy_pipeline.PhaseResult:
        return deploy_pipeline.PhaseResult(0, "stub", "PASS", 0.0)

    with contextlib.ExitStack() as stack:
        _patch_main_pipeline_phases(stack, fake_args, _phase_pass, _phase_other, tmp_path)
        deploy_pipeline.main()

    manifests = list((tmp_path / "logs").glob("deploy-result-staging-*.json"))
    assert len(manifests) == 1, f"Expected 1 manifest, found {len(manifests)}"
    body = json.loads(manifests[0].read_text())
    assert "deploy_evidence" in body
    assert body["deploy_evidence"]["image"] == "fake/image:v1.99.0"
    assert body["deploy_evidence"]["target_update_succeeded"] is True


def test_dry_run_does_not_populate_evidence(tmp_path: Path) -> None:
    """T13: dry-run mode produces a manifest WITHOUT deploy_evidence block.

    Codex GO -006 condition 1: dry runs must not emit meaningful
    deploy_evidence just because `args._deploy_evidence` is truthy.
    """
    fake_args = argparse.Namespace(env="staging", version="v1.99.0", dry_run=True, approved=False)

    def _phase_pass(*_a: Any, **_kw: Any) -> deploy_pipeline.PhaseResult:
        return deploy_pipeline.PhaseResult(0, "stub", "PASS", 0.0)

    with contextlib.ExitStack() as stack:
        _patch_main_pipeline_phases(stack, fake_args, _phase_pass, _phase_pass, tmp_path)
        deploy_pipeline.main()

    manifests = list((tmp_path / "logs").glob("deploy-result-staging-*.json"))
    assert len(manifests) == 1
    body = json.loads(manifests[0].read_text())
    # Per Codex condition 1: dry-run produces manifest without deploy_evidence
    assert "deploy_evidence" not in body
    assert body["dry_run"] is True
