#!/usr/bin/env python3
"""Non-deploying release-candidate gate for Agent Red.

This script runs the local checks that must pass before a build can be treated
as a serious production-release candidate. It intentionally does not deploy,
push images, call live services, or mutate external infrastructure.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class GateFailure(RuntimeError):
    """Raised when one or more release gates fail."""


def _run(command: list[str], *, timeout: int = 300, env: dict[str, str] | None = None) -> None:
    started = time.time()
    print(f"\n$ {' '.join(command)}", flush=True)
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=env,
    )
    elapsed = time.time() - started
    if result.returncode != 0:
        raise GateFailure(f"Command failed after {elapsed:.1f}s: {' '.join(command)}")
    print(f"PASS ({elapsed:.1f}s)")


def _check_python_version(required: str | None) -> None:
    if not required:
        return
    actual = f"{sys.version_info.major}.{sys.version_info.minor}"
    if actual != required:
        raise GateFailure(f"Python {required} required for release gate; running {actual}")
    print(f"PASS Python version: {actual}")


def _check_secret_manifest_removed() -> None:
    unsafe_path = PROJECT_ROOT / "scripts" / "deploy" / "production-gateway-generated.yaml"
    if unsafe_path.exists():
        raise GateFailure(f"Unsafe generated production manifest still exists: {unsafe_path}")

    result = subprocess.run(
        ["git", "ls-files", "scripts/deploy/production-gateway-generated.yaml"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if result.stdout.strip():
        status = subprocess.run(
            ["git", "status", "--short", "--", "scripts/deploy/production-gateway-generated.yaml"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        if not status.stdout.lstrip().startswith("D"):
            raise GateFailure("Unsafe generated production manifest is still tracked by git")
        print("PASS secret manifest containment (pending git deletion)")
        return
    print("PASS secret manifest containment")


def _python_gates() -> None:
    _run([sys.executable, "-m", "ruff", "check", "src/", "tests/", "--select", "E,F"], timeout=120)
    _run([sys.executable, "scripts/detect_import_cycles.py", "src"], timeout=120)
    _run([sys.executable, "-m", "bandit", "-r", "src/", "-ll", "-c", "pyproject.toml"], timeout=180)
    _run([sys.executable, "-m", "pip_audit", "-r", "requirements.txt"], timeout=180)
    _run([sys.executable, "scripts/check_codex_hook_parity.py"], timeout=60)
    _run([sys.executable, "scripts/check_pending_owner_decisions_parity.py"], timeout=30)
    _run([sys.executable, "scripts/check_environment_isolation.py"], timeout=60)
    _run([sys.executable, "scripts/check_session_overlay_policy.py"], timeout=60)
    _run([sys.executable, "scripts/check_scoped_service_boundary.py"], timeout=60)
    _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/security/test_production_config_guard.py",
            "tests/security/test_standalone_admin_hardening.py",
            "tests/multi_tenant/test_magic_link_auth.py",
            "tests/multi_tenant/test_mfa_totp.py",
            "tests/unit/test_widget_otp_verification.py",
            "tests/unit/test_deploy_scaling.py",
            "tests/unit/test_lib_scaling_enforcement.py",
            "tests/unit/test_deploy_pipeline_scaling.py",
            "tests/scripts/test_dora_001b_track2_ingest.py",
            "tests/scripts/test_check_environment_isolation.py",
            "tests/scripts/test_release_candidate_gate.py",
            "tests/scripts/test_gtkb_scoped_client.py",
            "tests/scripts/test_gtkb_dashboard_control_plane.py",
            "tests/scripts/test_gtkb_overlay.py",
            "tests/scripts/test_session_self_initialization.py",
            "tests/scripts/test_groundtruth_governance_adoption.py",
            "tests/scripts/test_codex_hook_parity.py",
            "tests/scripts/test_memory_md_ceiling.py",
            "tests/scripts/test_standing_backlog_harvest.py",
            "tests/integrations/test_commercial_state_store.py",
            "tests/integrations/test_cosmos_schema_extensions.py",
            "tests/integrations/test_action_executor.py",
            "tests/integrations/test_admin_integration_framework_api.py",
            "tests/integrations/test_usage_consumption.py",
            "tests/integrations/test_shopify_billing.py",
            "tests/unit/test_stripe_webhooks.py",
            "tests/hooks/test_formal_artifact_approval_gate.py",
            "tests/hooks/test_owner_decision_tracker.py",
            "tests/hooks/test_workstream_focus.py",
            "-q",
            "--tb=short",
        ],
        timeout=180,
    )


def _frontend_gates() -> None:
    npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm") or shutil.which("npm")
    if not npm:
        raise GateFailure("npm executable not found on PATH")
    powershell = shutil.which("powershell.exe") or shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise GateFailure("PowerShell executable not found on PATH")
    frontend_projects = [
        "widget",
        os.path.join("admin", "standalone"),
        os.path.join("admin", "provider"),
        os.path.join("admin", "shopify"),
    ]
    _run([npm, "--prefix", "widget", "test"], timeout=180)
    for project in frontend_projects:
        if project.startswith("admin"):
            break
        _run([npm, "--prefix", project, "run", "build"], timeout=240)

    _run([powershell, "-ExecutionPolicy", "Bypass", "-File", "scripts/sync-admin-env.ps1"], timeout=60)
    admin_build_env = os.environ.copy()
    admin_build_env["npm_config_ignore_scripts"] = "true"
    for project in frontend_projects:
        if not project.startswith("admin"):
            continue
        _run([npm, "--prefix", project, "run", "build"], timeout=240, env=admin_build_env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run non-deploying release-candidate gates.")
    parser.add_argument("--require-python", default="", help="Require a specific Python major.minor, for example 3.12.")
    parser.add_argument("--skip-python", action="store_true", help="Skip Python/security gates.")
    parser.add_argument("--skip-frontend", action="store_true", help="Skip frontend widget/admin gates.")
    parser.add_argument("--include-frontend", action="store_true", help="Run frontend widget/admin gates.")
    args = parser.parse_args()

    try:
        _check_python_version(args.require_python or None)
        _check_secret_manifest_removed()
        if not args.skip_python:
            _python_gates()
        if args.include_frontend and not args.skip_frontend:
            _frontend_gates()
    except (GateFailure, subprocess.TimeoutExpired) as exc:
        print(f"\nRELEASE GATE: FAIL - {exc}", file=sys.stderr)
        return 1

    print("\nRELEASE GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
