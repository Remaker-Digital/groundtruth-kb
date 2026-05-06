#!/usr/bin/env python3
"""Non-deploying release-candidate gate for Agent Red.

This script runs the local checks that must pass before a build can be treated
as a serious production-release candidate. It intentionally does not deploy,
push images, call live services, or mutate external infrastructure.
"""

from __future__ import annotations

import argparse
import json
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


def _check_secret_gate_present() -> None:
    pre_commit_path = PROJECT_ROOT / ".githooks" / "pre-commit"
    if not pre_commit_path.is_file():
        raise GateFailure("Tracked pre-commit hook is missing: .githooks/pre-commit")
    pre_commit_text = pre_commit_path.read_text(encoding="utf-8", errors="replace")
    if (
        "secrets scan" not in pre_commit_text
        or "--staged" not in pre_commit_text
        or "--redacted" not in pre_commit_text
    ):
        raise GateFailure("Tracked pre-commit hook does not invoke the staged secret scan")

    pre_push_path = PROJECT_ROOT / ".githooks" / "pre-push"
    if not pre_push_path.is_file():
        raise GateFailure("Tracked pre-push hook is missing: .githooks/pre-push")
    pre_push_text = pre_push_path.read_text(encoding="utf-8", errors="replace")
    if "secrets scan" not in pre_push_text or "--range" not in pre_push_text or "--redacted" not in pre_push_text:
        raise GateFailure("Tracked pre-push hook does not invoke the redacted range secret scan")

    setup_path = PROJECT_ROOT / ".githooks" / "setup-hooks.sh"
    if not setup_path.is_file():
        raise GateFailure("Hook setup script is missing: .githooks/setup-hooks.sh")
    setup_text = setup_path.read_text(encoding="utf-8", errors="replace")
    if "core.hooksPath .githooks" not in setup_text or "pre-push" not in setup_text or "pre-commit" not in setup_text:
        raise GateFailure("Hook setup script does not activate both tracked secret gates")

    hooks_path = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if hooks_path.stdout.strip() != ".githooks":
        raise GateFailure("git core.hooksPath must be .githooks for the tracked secret gate")

    help_result = subprocess.run(
        [sys.executable, "-m", "groundtruth_kb", "secrets", "scan", "--help"],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    if help_result.returncode != 0:
        raise GateFailure("gt secrets scan CLI is not callable")
    required_help_tokens = ("--staged", "--range", "--paths", "--tracked", "--all-refs")
    missing_help_tokens = [token for token in required_help_tokens if token not in help_result.stdout]
    if missing_help_tokens:
        raise GateFailure("gt secrets scan help is missing options: " + ", ".join(missing_help_tokens))
    print("PASS local secret gate presence")


def _check_secret_ci_workflow_present() -> None:
    workflow_path = PROJECT_ROOT / ".github" / "workflows" / "gtkb-secrets-scan.yml"
    if not workflow_path.is_file():
        raise GateFailure("Broad GT-KB secret-scan workflow is missing: .github/workflows/gtkb-secrets-scan.yml")
    workflow_text = workflow_path.read_text(encoding="utf-8", errors="replace")
    required_tokens = (
        "pull_request",
        "push",
        "workflow_dispatch",
        "python -m groundtruth_kb secrets scan",
        "--tracked",
        "--redacted",
        "--report-json .quality/gtkb-secrets.json",
        "--fail-on verified-provider",
        "actions/upload-artifact",
    )
    missing_tokens = [token for token in required_tokens if token not in workflow_text]
    if missing_tokens:
        raise GateFailure("Broad GT-KB secret-scan workflow is incomplete: " + ", ".join(missing_tokens))
    if "paths:" in workflow_text:
        raise GateFailure("Broad GT-KB secret-scan workflow must not be constrained by path filters")
    print("PASS broad GT-KB secret-scan workflow presence")


def _dev_inventory_helpers():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.collect_dev_environment_inventory import (  # noqa: PLC0415
        DEFAULT_MAX_AGE_HOURS,
        PUBLIC_JSON_RELATIVE_PATH,
        validate_public_inventory_payload,
    )

    return DEFAULT_MAX_AGE_HOURS, PUBLIC_JSON_RELATIVE_PATH, validate_public_inventory_payload


def _check_dev_environment_inventory(max_age_hours: int | None = None) -> None:
    default_max_age, relative_path, validate_payload = _dev_inventory_helpers()
    effective_max_age = default_max_age if max_age_hours is None else max_age_hours
    inventory_path = PROJECT_ROOT / relative_path
    if not inventory_path.is_file():
        raise GateFailure(f"Development environment inventory is missing: {relative_path.as_posix()}")
    try:
        payload = json.loads(inventory_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateFailure(f"Development environment inventory is malformed JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise GateFailure("Development environment inventory JSON root must be an object")
    errors = validate_payload(payload, project_root=PROJECT_ROOT, max_age_hours=effective_max_age)
    if errors:
        raise GateFailure("Development environment inventory is invalid: " + "; ".join(errors))
    generated_at = payload.get("generated_at")
    redaction_status = (payload.get("redaction") or {}).get("status")
    print(
        f"PASS development environment inventory ({relative_path.as_posix()}, generated {generated_at}, redaction {redaction_status})"
    )


def _dev_inventory_drift_helpers():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.check_dev_environment_inventory_drift import evaluate_drift  # noqa: PLC0415

    return evaluate_drift


def _check_dev_environment_inventory_drift() -> None:
    evaluate_drift = _dev_inventory_drift_helpers()
    result = evaluate_drift(PROJECT_ROOT)
    if result.get("status") != "pass":
        reasons = []
        for item in result.get("blocking", []):
            if item.get("path"):
                reasons.append(f"{item.get('path')} requires {item.get('route')}")
            else:
                reasons.append(str(item.get("message") or item.get("reason")))
        raise GateFailure("Development environment inventory drift: " + "; ".join(reasons))
    print(f"PASS development environment inventory drift ({result.get('outcome')})")


def _project_resource_helpers():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.resolve_project_resource import (  # noqa: PLC0415
        check_git_remote_drift,
        load_registry,
        validate_registry,
    )

    return load_registry, validate_registry, check_git_remote_drift


def _check_project_resource_registry() -> None:
    load_registry, validate_registry, check_git_remote_drift = _project_resource_helpers()
    registry_path = PROJECT_ROOT / "config" / "agent-control" / "project-resource-aliases.toml"
    if not registry_path.is_file():
        raise GateFailure(f"Project resource registry is missing: {registry_path.relative_to(PROJECT_ROOT)}")
    try:
        registry = load_registry(registry_path)
    except (OSError, ValueError) as exc:
        raise GateFailure(f"Project resource registry is unreadable: {exc}") from exc
    errors = validate_registry(registry)
    if errors:
        raise GateFailure("Project resource registry is invalid: " + "; ".join(errors))
    drift = check_git_remote_drift(registry, repo_root=PROJECT_ROOT)
    if drift.get("status") != "pass":
        raise GateFailure(f"Project GitHub remote identity drift: {drift.get('message')}")
    print(
        "PASS project resource registry "
        f"({registry_path.relative_to(PROJECT_ROOT).as_posix()}, origin={drift.get('origin')})"
    )


def _python_gates() -> None:
    _run([sys.executable, "-m", "ruff", "check", "src/", "tests/", "--select", "E,F"], timeout=120)
    _run([sys.executable, "scripts/detect_import_cycles.py", "src"], timeout=120)
    _run([sys.executable, "-m", "bandit", "-r", "src/", "-ll", "-c", "pyproject.toml"], timeout=180)
    _run([sys.executable, "-m", "pip_audit", "-r", "requirements.txt"], timeout=180)
    _run([sys.executable, "scripts/check_codex_hook_parity.py"], timeout=60)
    _run([sys.executable, "scripts/generate_codex_skill_adapters.py", "--update-registry", "--check"], timeout=30)
    _run([sys.executable, "scripts/check_harness_parity.py", "--all", "--markdown"], timeout=30)
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
            "tests/scripts/test_collect_dev_environment_inventory.py",
            "tests/scripts/test_check_dev_environment_inventory_drift.py",
            "tests/scripts/test_gtkb_scoped_client.py",
            "tests/scripts/test_gtkb_dashboard_control_plane.py",
            "tests/scripts/test_gtkb_overlay.py",
            "tests/scripts/test_session_self_initialization.py",
            "tests/scripts/test_groundtruth_governance_adoption.py",
            "tests/scripts/test_codex_hook_parity.py",
            "tests/scripts/test_run_spec_derived_tests.py",
            "tests/scripts/test_memory_md_ceiling.py",
            "tests/scripts/test_command_registry_tracking.py",
            "tests/scripts/test_wrap_capture_transcript.py",
            "tests/scripts/test_wrap_scan_hygiene.py",
            "tests/scripts/test_wrap_scan_consistency.py",
            "tests/scripts/test_gitignore_session_snapshots.py",
            "tests/scripts/test_wrap_scan_hygiene_skip_dirs.py",
            "tests/scripts/test_wrap_scan_consistency_allowlist.py",
            "tests/scripts/test_rehearse_isolation.py",
            "tests/scripts/test_standing_backlog_harvest.py",
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

    # Per Slice A of GTKB-MEMBASE-EFFECTIVE-USE-RECOVERY (bridge -006 GO):
    # spec-event-surfacer hook + supporting upstream tests for managed-artifact
    # registry, scaffold, upgrade, and doctor coverage of the new hook entries.
    # Run in a separate pytest invocation with --rootdir so the upstream
    # `groundtruth-kb/tests/conftest.py` doesn't collide with `tests/conftest.py`,
    # and so the project-root pyproject.toml `testpaths=["tests"]` doesn't
    # exclude these paths from collection.
    upstream_root = PROJECT_ROOT / "groundtruth-kb"
    _run(
        [
            sys.executable,
            "-m",
            "pytest",
            f"--rootdir={upstream_root}",
            "--override-ini=testpaths=tests",
            str(upstream_root / "tests" / "test_spec_event_surfacer.py"),
            str(upstream_root / "tests" / "test_managed_registry.py"),
            str(upstream_root / "tests" / "test_scaffold_settings.py"),
            str(upstream_root / "tests" / "test_scaffold_project.py"),
            str(upstream_root / "tests" / "test_upgrade.py"),
            str(upstream_root / "tests" / "test_settings_merge_drift.py"),
            str(upstream_root / "tests" / "test_doctor.py"),
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
    parser.add_argument(
        "--skip-dev-inventory", action="store_true", help="Skip the GT-KB dev-environment inventory gate."
    )
    parser.add_argument(
        "--skip-dev-inventory-drift",
        action="store_true",
        help="Skip protected-artifact drift control for the GT-KB dev-environment inventory.",
    )
    parser.add_argument(
        "--dev-inventory-max-age-hours",
        type=int,
        default=None,
        help="Maximum allowed age for docs/release/dev-environment-inventory.json.",
    )
    args = parser.parse_args()

    try:
        _check_python_version(args.require_python or None)
        _check_secret_manifest_removed()
        _check_secret_gate_present()
        _check_secret_ci_workflow_present()
        _check_project_resource_registry()
        if not args.skip_dev_inventory:
            _check_dev_environment_inventory(args.dev_inventory_max_age_hours)
        if not args.skip_dev_inventory_drift:
            _check_dev_environment_inventory_drift()
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
