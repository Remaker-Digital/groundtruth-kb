"""Subprocess wrapper for CPD-009 / CPD-010 protocol-shaped CLI tests.

Runs deploy_pipeline.main() with all external calls mocked so that the test
suite can invoke this script as a real subprocess and verify exit-code behaviour
without touching Azure, ACR, or live HTTP endpoints.

DEPLOY_MOCK_MODE is taken from argv[1]:
  success        All phases mocked to PASS → main() exits 0   (CPD-009, Phase C case 4)
  smoke_failure  Phases 0-10 mocked to PASS; phase_11 api_call
                 returns 503 → main() exits 1, rollback logged (CPD-010, Phase C case 5)

Usage (from project root):
    python tests/unit/helpers/run_mocked_pipeline.py <mode> [-- pipeline-args...]

All argv after the mode token are forwarded verbatim to deploy_pipeline's argparse.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import importlib.util
import sys
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Bootstrap path so scripts.* and tools.knowledge-db imports resolve
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
for _p in [str(PROJECT_ROOT), str(PROJECT_ROOT / "scripts"),
           str(PROJECT_ROOT / "tools" / "knowledge-db")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Consume mode from argv before argparse inside main() reads sys.argv
# ---------------------------------------------------------------------------
if len(sys.argv) < 2:
    print("Usage: run_mocked_pipeline.py <success|smoke_failure> [pipeline-args...]",
          file=sys.stderr)
    sys.exit(2)

MODE = sys.argv[1]
# Strip mode so deploy_pipeline's argparse sees only pipeline args
sys.argv = [sys.argv[0]] + sys.argv[2:]

# ---------------------------------------------------------------------------
# Load deploy_pipeline with platform patch to suppress Windows stdout fix
# ---------------------------------------------------------------------------
with patch.object(sys, "platform", "linux"):
    _spec = importlib.util.spec_from_file_location(
        "deploy_pipeline_mocked",
        PROJECT_ROOT / "scripts" / "deploy_pipeline.py",
    )
    dp = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(dp)

PR = dp.PhaseResult


def _pass(n: int, name: str) -> PR:
    return PR(n, name, "PASS", 0.0)


def _mock_snapshot_phase(args):
    """Side-effect for phase_10a: returns PASS and seeds args._snapshot_files."""
    args._snapshot_files = ["/tmp/mock_snapshot.json"]
    return _pass(8, "Pre-Deploy Snapshot")


def _api_call_503(fqdn, path, api_key=None, timeout=10):
    """Stub api_call that always returns a 503 smoke failure."""
    return (503, {}, {})


# ---------------------------------------------------------------------------
# CPD-009: All phases mocked to PASS — pipeline must exit 0
# ---------------------------------------------------------------------------
if MODE == "success":
    with ExitStack() as stack:
        stack.enter_context(patch.object(dp, "phase_0_validate_environment",
                                         return_value=_pass(0, "Validate Environment")))
        stack.enter_context(patch.object(dp, "phase_1_protected_behaviors",
                                         return_value=_pass(1, "Protected Behaviors")))
        stack.enter_context(patch.object(dp, "phase_2_clear_vite_api_url",
                                         return_value=_pass(2, "Clear Vite API URL")))
        stack.enter_context(patch.object(dp, "phase_3_build_artifacts",
                                         return_value=_pass(3, "Build Artifacts")))
        stack.enter_context(patch.object(dp, "phase_4_freshness_gate",
                                         return_value=_pass(4, "Build Freshness Gate")))
        stack.enter_context(patch.object(dp, "phase_5_restore_env_local",
                                         return_value=_pass(5, "Restore .env.local")))
        stack.enter_context(patch.object(dp, "phase_6_create_build_context",
                                         return_value=(_pass(6, "Create Build Context"), "/tmp/ctx")))
        stack.enter_context(patch.object(dp, "phase_7_acr_build",
                                         return_value=_pass(7, "ACR Build")))
        stack.enter_context(patch.object(dp, "phase_10a_pre_deploy_snapshot",
                                         side_effect=_mock_snapshot_phase))
        stack.enter_context(patch.object(dp, "phase_8_deploy",
                                         return_value=_pass(9, "Deploy")))
        stack.enter_context(patch.object(dp, "phase_10_startup_and_version",
                                         return_value=_pass(10, "Startup & Version")))
        # Staging-track post-deploy phases
        stack.enter_context(patch.object(dp, "phase_13_upgrade_verification",
                                         return_value=_pass(11, "Upgrade Verification")))
        stack.enter_context(patch.object(dp, "phase_14_config_pipeline",
                                         return_value=_pass(12, "Config Pipeline")))
        stack.enter_context(patch.object(dp, "phase_13_seed_test_tenant",
                                         return_value=_pass(13, "Seed Test Tenant")))
        stack.enter_context(patch.object(dp, "phase_14_verify_initialized_state",
                                         return_value=_pass(14, "Verify Initialized State")))
        # Skip real sleeps (65-second rate-limit cooldowns in main())
        mock_time = stack.enter_context(patch.object(dp, "time"))
        mock_time.time.side_effect = __import__("time").time
        mock_time.sleep.return_value = None
        # Suppress KB write on failure (should not trigger, but guard anyway)
        stack.enter_context(patch.object(dp, "_create_defect_work_item",
                                         return_value=None))
        sys.exit(dp.main())

# ---------------------------------------------------------------------------
# CPD-010: Shared/deploy phases PASS; phase_11 api_call returns 503 → exit 1
# ---------------------------------------------------------------------------
elif MODE == "smoke_failure":
    with ExitStack() as stack:
        stack.enter_context(patch.object(dp, "phase_0_validate_environment",
                                         return_value=_pass(0, "Validate Environment")))
        stack.enter_context(patch.object(dp, "phase_1_protected_behaviors",
                                         return_value=_pass(1, "Protected Behaviors")))
        stack.enter_context(patch.object(dp, "phase_2_clear_vite_api_url",
                                         return_value=_pass(2, "Clear Vite API URL")))
        stack.enter_context(patch.object(dp, "phase_3_build_artifacts",
                                         return_value=_pass(3, "Build Artifacts")))
        stack.enter_context(patch.object(dp, "phase_4_freshness_gate",
                                         return_value=_pass(4, "Build Freshness Gate")))
        stack.enter_context(patch.object(dp, "phase_5_restore_env_local",
                                         return_value=_pass(5, "Restore .env.local")))
        stack.enter_context(patch.object(dp, "phase_6_create_build_context",
                                         return_value=(_pass(6, "Create Build Context"), "/tmp/ctx")))
        stack.enter_context(patch.object(dp, "phase_7_acr_build",
                                         return_value=_pass(7, "ACR Build")))
        stack.enter_context(patch.object(dp, "phase_10a_pre_deploy_snapshot",
                                         side_effect=_mock_snapshot_phase))
        stack.enter_context(patch.object(dp, "phase_8_deploy",
                                         return_value=_pass(9, "Deploy")))
        stack.enter_context(patch.object(dp, "phase_10_startup_and_version",
                                         return_value=_pass(10, "Startup & Version")))
        # phase_11_production_verification is NOT mocked — it runs with mocked api_call
        stack.enter_context(patch.object(dp, "api_call", side_effect=_api_call_503))
        # _stream backs the upgrade_verification subprocess call inside phase_11
        stack.enter_context(patch.object(
            dp, "_stream",
            return_value=MagicMock(returncode=0, stdout="(41 pass, 0 fail)"),
        ))
        # get_current_image is imported inside main() — patch at source module level.
        # Use a synthetic previous-version tag (the "current" image being replaced).
        stack.enter_context(patch(
            "scripts.deploy_config.get_current_image",
            return_value="acragentredeastus.azurecr.io/api-gateway:v1.98.0-mock-prev",
        ))
        stack.enter_context(patch(
            "scripts.deploy_config.rollback_to_image",
            return_value=True,
        ))
        # Skip sleeps (65s cooldown in phase_11, 15s post-rollback wait)
        mock_time = stack.enter_context(patch.object(dp, "time"))
        mock_time.time.side_effect = __import__("time").time
        mock_time.sleep.return_value = None
        # Suppress KB write for the expected failure
        stack.enter_context(patch.object(dp, "_create_defect_work_item",
                                         return_value=None))
        sys.exit(dp.main())

else:
    print(f"Unknown mode: {MODE!r}. Use 'success' or 'smoke_failure'.", file=sys.stderr)
    sys.exit(2)
