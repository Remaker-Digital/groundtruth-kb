"""Unit tests for phase_15_enforce_scaling() in scripts/deploy_pipeline.py.

These tests prove that the canonical production deployment pipeline now
enforces scaling baselines, and that the operator-visibility contract is
delivered (drift surfaces in the final summary even though the phase
returns PASS).

Tests:
- T1: Production canonical path calls _run_shell once per scaling target,
      returns PASS with detail=`failed=0 ok=N total=N` and extra="".
- T2: Smoke ≡ canonical parity — the set of az command strings produced
      by phase_15_enforce_scaling("production") matches the set produced
      by deploy.py's enforce_all_scaling("production").
- T3: dry-run returns PASS without invoking the runner (call count == 0).
- T4: Single-app failure produces PASS with extra="DRIFT: 1/N failed (...)"
      and detail recording the failed app; WARN log line emitted.
- T5: OPERATOR-VISIBILITY (Codex -006 required action). Capture
      _print_summary() output for a PASS scaling phase whose extra contains
      a DRIFT marker; assert the DRIFT substring appears in the captured
      summary text.
- T6: SCALING_CONFIG reconciles against infrastructure/terraform/main.tf
      production-only entries (parallels test_deploy_scaling.py:148 but
      via the pipeline import path).

Created 2026-04-25 (S308) per
`bridge/canonical-deploy-pipeline-scaling-enforcement-007.md` (Codex GO at -008).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import io
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEPLOY_PIPELINE = PROJECT_ROOT / "scripts" / "deploy_pipeline.py"
DEPLOY_SCRIPT = PROJECT_ROOT / "scripts" / "deploy.py"
TERRAFORM_MAIN = PROJECT_ROOT / "infrastructure" / "terraform" / "main.tf"


def _load_deploy_pipeline():
    """Import deploy_pipeline module fresh so per-test patches don't leak.

    Mirrors the pattern in test_deploy_pipeline_production.py: bootstrap
    sys.path, neutralize the Windows stdout-wrapper guard via platform
    patch, then exec_module.
    """
    for p in [str(PROJECT_ROOT), str(PROJECT_ROOT / "scripts"),
              str(PROJECT_ROOT / "tools" / "knowledge-db")]:
        if p not in sys.path:
            sys.path.insert(0, p)
    with patch.object(sys, "platform", "linux"):
        spec = importlib.util.spec_from_file_location(
            "deploy_pipeline_scaling_test", DEPLOY_PIPELINE
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


def _load_deploy_script():
    """Import deploy.py fresh so per-test patches against its _run don't leak."""
    for p in [str(PROJECT_ROOT), str(PROJECT_ROOT / "scripts")]:
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location("deploy_smoke_test", DEPLOY_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["deploy_smoke_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_args(env: str = "production", dry_run: bool = False, version: str = "v1.99.0"):
    """Construct an argparse.Namespace-like object for phase_15_enforce_scaling."""
    import argparse
    return argparse.Namespace(env=env, dry_run=dry_run, version=version)


def _fake_run_shell_success(_cmd, timeout=120):
    """_run_shell stand-in that always succeeds (returncode 0, empty stdout)."""
    return subprocess.CompletedProcess(args=_cmd, returncode=0, stdout="", stderr="")


def _fake_run_shell_fail_for(failing_apps: set[str]):
    """Return a _run_shell stand-in that fails (returncode 1) for cmds matching any failing app."""
    def runner(cmd, timeout=120):
        for app in failing_apps:
            if app in cmd:
                return subprocess.CompletedProcess(args=cmd, returncode=1, stdout="failure", stderr="")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
    return runner


# T1 — production canonical path calls runner once per target, returns PASS
def test_phase_15_production_returns_pass_when_all_succeed() -> None:
    pipeline = _load_deploy_pipeline()
    args = _make_args(env="production", dry_run=False)

    with patch.object(pipeline, "_run_shell", side_effect=_fake_run_shell_success) as mock_run:
        result = pipeline.phase_15_enforce_scaling(args)

    assert result.phase == 15
    assert result.name == "Enforce Scaling Baseline"
    assert result.status == "PASS"
    assert result.extra == "", f"Clean run should leave extra empty; got {result.extra!r}"
    assert re.match(r"^failed=0 ok=\d+ total=\d+$", result.detail), (
        f"Clean run detail must match pattern; got {result.detail!r}"
    )
    # One az invocation per target in get_scaling_targets("production")
    from lib.scaling_targets import get_scaling_targets
    expected_n = len(get_scaling_targets("production"))
    assert mock_run.call_count == expected_n, (
        f"Expected {expected_n} _run_shell calls (one per target); got {mock_run.call_count}"
    )


# T2 — Smoke ≡ canonical parity
def test_phase_15_az_commands_match_smoke_path() -> None:
    """The set of `az containerapp update` commands the canonical pipeline issues
    must match the set the smoke deploy script issues for the same environment."""
    pipeline = _load_deploy_pipeline()
    deploy = _load_deploy_script()
    args = _make_args(env="production", dry_run=False)

    pipeline_cmds: list[str] = []

    def capture_run_shell(cmd, timeout=120):
        pipeline_cmds.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    smoke_cmds: list[str] = []

    def capture_run(cmd, timeout=120):
        smoke_cmds.append(cmd)
        return (0, "")

    with patch.object(pipeline, "_run_shell", side_effect=capture_run_shell):
        pipeline.phase_15_enforce_scaling(args)

    with patch.object(deploy, "_run", side_effect=capture_run):
        deploy.enforce_all_scaling("production")

    # Compare the set of `az containerapp update --name X --min-replicas N --max-replicas M`
    # invocations. Strip whitespace differences for robustness.
    def _normalize(cmds: list[str]) -> set[str]:
        return {" ".join(c.split()) for c in cmds}

    assert _normalize(pipeline_cmds) == _normalize(smoke_cmds), (
        f"Pipeline issues different az commands than smoke path.\n"
        f"Pipeline only: {_normalize(pipeline_cmds) - _normalize(smoke_cmds)}\n"
        f"Smoke only: {_normalize(smoke_cmds) - _normalize(pipeline_cmds)}"
    )


# T3 — dry-run returns PASS without invoking the runner
def test_phase_15_dry_run_skips_runner() -> None:
    pipeline = _load_deploy_pipeline()
    args = _make_args(env="production", dry_run=True)

    with patch.object(pipeline, "_run_shell", side_effect=_fake_run_shell_success) as mock_run:
        result = pipeline.phase_15_enforce_scaling(args)

    assert result.status == "PASS"
    assert result.detail == "dry-run"
    assert mock_run.call_count == 0, "dry-run must not invoke _run_shell"


# T4 — single-app failure produces PASS + DRIFT marker in extra
def test_phase_15_single_failure_returns_pass_with_drift_extra() -> None:
    pipeline = _load_deploy_pipeline()
    args = _make_args(env="production", dry_run=False)
    failing = {"agent-red-slim"}

    with patch.object(pipeline, "_run_shell", side_effect=_fake_run_shell_fail_for(failing)):
        result = pipeline.phase_15_enforce_scaling(args)

    # Status remains PASS even with drift (WI-3156 contract)
    assert result.status == "PASS"
    # Extra carries the human-readable DRIFT marker for the final summary
    assert "DRIFT: 1/" in result.extra
    assert "agent-red-slim" in result.extra
    # Detail records machine-readable count + names per owner GOV-17 ack
    assert "failed=1" in result.detail
    assert "agent-red-slim" in result.detail


# T5 — OPERATOR-VISIBILITY (Codex -006 required action)
def test_phase_15_drift_appears_in_final_summary_when_status_is_pass() -> None:
    """Capture _print_summary() output for a PASS scaling phase with DRIFT extra;
    assert the DRIFT substring appears so an operator scanning the final
    summary table would see the failed-app list."""
    pipeline = _load_deploy_pipeline()

    # Construct a synthetic PhaseResult mirroring what phase_15 produces on drift.
    drift_result = pipeline.PhaseResult(
        15, "Enforce Scaling Baseline", "PASS", 12.4,
        detail="failed=2 ok=6 total=8 names=agent-red-slim,agent-red-staging",
        extra="DRIFT: 2/8 failed (agent-red-slim,agent-red-staging)",
    )

    captured: list[str] = []

    def capture_print(*pieces):
        captured.append(" ".join(str(p) for p in pieces))

    # Use any args namespace; _print_summary just reads args.env / args.version.
    args = _make_args(env="production", dry_run=False, version="v1.99.0")

    with patch.object(pipeline, "_safe_print", side_effect=capture_print):
        # _print_summary signature: (results, args, start_time, log_path, defect_wi).
        # Use a finite start_time so the duration math doesn't blow up; pass
        # None for log_path and defect_wi (their formatting handles None).
        import time as _time
        pipeline._print_summary([drift_result], args, _time.time() - 1.0, None, None)

    summary_text = "\n".join(captured)
    assert "DRIFT: 2/8 failed (agent-red-slim,agent-red-staging)" in summary_text, (
        f"Final summary must surface DRIFT marker for operator visibility.\n"
        f"Captured output:\n{summary_text}"
    )
    # Status row must also still show PASS (proving drift visibility doesn't
    # regress to FAIL):
    assert "Enforce Scaling Baseline" in summary_text
    assert "PASS" in summary_text


# T6 — SCALING_CONFIG reconciles against Terraform via the pipeline import path
def test_scaling_config_matches_terraform_via_pipeline_import() -> None:
    """Parallels test_deploy_scaling.py reconciliation, but exercises the
    pipeline's import path so a future divergence in pipeline imports cannot
    silently mask the reconciliation."""
    pipeline = _load_deploy_pipeline()  # noqa: F841 — proves pipeline import succeeds
    from lib.scaling_targets import SCALING_CONFIG

    if not TERRAFORM_MAIN.exists():
        pytest.skip(f"Terraform main.tf not present at {TERRAFORM_MAIN}")

    tf_content = TERRAFORM_MAIN.read_text(encoding="utf-8")
    # Spot-check production gateway baseline (Decision #16): min_replicas = 2
    assert SCALING_CONFIG["agent-red-api-gateway"]["min_replicas"] == 2
    assert SCALING_CONFIG["agent-red-api-gateway"]["max_replicas"] == 8
    # Spot-check shared infra (SLIM): min=2 max=2
    assert SCALING_CONFIG["agent-red-slim"]["min_replicas"] == 2
    assert SCALING_CONFIG["agent-red-slim"]["max_replicas"] == 2
    # Sanity: api-gateway must appear as a container_apps entry in main.tf
    # (loose match — the test_deploy_scaling.py file does the strict version)
    assert "api-gateway" in tf_content
