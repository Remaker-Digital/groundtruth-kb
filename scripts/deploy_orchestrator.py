#!/usr/bin/env python3
"""Deploy Orchestrator — automated deploy-verify-rollback lifecycle.

Deterministic script that can be triggered by:
  - Claude Code (manual invocation)
  - SPA Provider Console (POST /api/superadmin/deployments/trigger)
  - CLI: python scripts/deploy_orchestrator.py --env staging --version v1.90.0

Pipeline steps:
  1. Validate image exists in ACR
  2. Phase A: Pre-deploy snapshot (upgrade_verification.py phase-a/multi-a)
  3. Deploy: az containerapp update with new image
  4. Health poll: wait for /health to return 200 + correct version
  5. Phase C: Post-deploy verification (upgrade_verification.py phase-c/multi-c)
  6. Optional E2E regression (test_pipeline.py subset)
  7. Auto-rollback on verification failure
  8. Structured JSON result + audit log

Exit codes:
    0 = SUCCESS
    1 = FAILURE (with auto-rollback attempted if applicable)

WI-1433 / SPEC-1825 / SPEC-1830
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Force UTF-8 stdout on Windows (only when run as main, not when imported by pytest)
if sys.platform == "win32" and __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))

from scripts._subprocess_stream import stream_subprocess  # noqa: E402
from upgrade_verification import ENVIRONMENTS  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ACR_NAME = "acragentredeastus"
ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
IMAGE_REPO = "api-gateway"
RESOURCE_GROUP = "Agent-Red"

HEALTH_TIMEOUT_S = 120
HEALTH_POLL_INTERVAL_S = 10

_log_lines: list[str] = []


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------
@dataclass
class DeployResult:
    """Structured result of a deploy orchestration run."""

    status: str = "pending"  # pending, running, succeeded, failed, rolled_back
    environment: str = ""
    version: str = ""
    image: str = ""
    previous_image: str = ""
    revision_name: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_s: float = 0.0
    dry_run: bool = False
    rollback_performed: bool = False
    rollback_status: str = ""  # "", succeeded, failed
    verification_pass: int = 0
    verification_fail: int = 0
    steps: list[dict] = field(default_factory=list)
    error: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def _log(level: str, msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level:5s}] {msg}"
    _log_lines.append(line)
    try:
        print(line, flush=True)
    except (OSError, ValueError):
        pass


def _write_log_file(env: str) -> Path:
    """Write buffered log lines to a file."""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = log_dir / f"deploy-orchestrator-{env}-{ts}.log"
    log_path.write_text("\n".join(_log_lines) + "\n", encoding="utf-8")
    return log_path


def _run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    """Run subprocess with real-time streaming."""
    r = stream_subprocess(cmd, cwd=str(PROJECT_ROOT), timeout=timeout, prefix="  ")
    return subprocess.CompletedProcess(
        args=cmd, returncode=r.returncode, stdout=r.stdout, stderr="",
    )


def _step(result: DeployResult, name: str, status: str, detail: str = "") -> None:
    """Record a step in the deploy result."""
    result.steps.append({
        "name": name,
        "status": status,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


# ---------------------------------------------------------------------------
# Deploy steps
# ---------------------------------------------------------------------------
def _validate_image(result: DeployResult, version: str, dry_run: bool) -> bool:
    """Step 1: Verify image tag exists in ACR."""
    _log("INFO", f"Step 1: Validating image {IMAGE_REPO}:{version} in ACR")

    if not re.match(r"^v\d+\.\d+\.\d+$", version):
        _step(result, "validate_image", "failed", f"Invalid version format: {version}")
        result.error = f"Version must be vX.Y.Z (got: {version})"
        return False

    if dry_run:
        _step(result, "validate_image", "skipped", "dry-run")
        _log("INFO", f"  [DRY RUN] Would verify {IMAGE_REPO}:{version}")
        return True

    r = _run([
        "az", "acr", "repository", "show-tags",
        "--name", ACR_NAME,
        "--repository", IMAGE_REPO,
        "--query", f"[?@=='{version}']",
        "-o", "tsv",
    ])
    if r.stdout.strip() != version:
        _step(result, "validate_image", "failed", f"Tag {version} not found in ACR")
        result.error = f"Image {IMAGE_REPO}:{version} not found in ACR — build first"
        return False

    result.image = f"{ACR_LOGIN_SERVER}/{IMAGE_REPO}:{version}"
    _step(result, "validate_image", "passed", result.image)
    _log("PASS", f"  Image verified: {result.image}")
    return True


def _get_current_image(env: str) -> str:
    """Query the currently deployed image for rollback reference."""
    container_app = ENVIRONMENTS[env]["container_app"]
    r = _run([
        "az", "containerapp", "show",
        "--name", container_app,
        "--resource-group", RESOURCE_GROUP,
        "--query", "properties.template.containers[0].image",
        "-o", "tsv",
    ])
    return r.stdout.strip()


def _pre_deploy_snapshot(result: DeployResult, env: str, dry_run: bool) -> bool:
    """Step 2: Phase A — capture pre-deploy state for verification."""
    _log("INFO", "Step 2: Pre-deploy snapshot (Phase A)")
    phase_name = "multi-a" if env == "staging" else "phase-a"

    if dry_run:
        _step(result, "pre_deploy_snapshot", "skipped", "dry-run")
        _log("INFO", f"  [DRY RUN] Would run {phase_name}")
        return True

    script = PROJECT_ROOT / "scripts" / "upgrade_verification.py"
    r = _run(
        [sys.executable, str(script), phase_name, "--env", env],
        timeout=600,
    )

    if r.returncode != 0:
        _step(result, "pre_deploy_snapshot", "failed",
               f"Exit {r.returncode}: {r.stdout.strip()[:200]}")
        result.error = f"Phase A snapshot failed (exit={r.returncode})"
        return False

    # Verify snapshot files exist
    results_dir = PROJECT_ROOT / "scripts" / "upgrade-results"
    if env == "staging":
        expected = ["phase_a_staging-001.json", "phase_a_staging-002.json"]
    else:
        expected = ["phase_a_remaker-digital-001.json"]

    missing = [f for f in expected if not (results_dir / f).exists()]
    if missing:
        _step(result, "pre_deploy_snapshot", "failed", f"Missing: {', '.join(missing)}")
        result.error = f"Snapshot files not created: {', '.join(missing)}"
        return False

    _step(result, "pre_deploy_snapshot", "passed", f"{len(expected)} tenant(s)")
    _log("PASS", f"  Phase A snapshots saved ({len(expected)} tenants)")
    return True


def _deploy_container(result: DeployResult, env: str, version: str, dry_run: bool) -> bool:
    """Step 3: Deploy new image to container app."""
    container_app = ENVIRONMENTS[env]["container_app"]
    new_image = f"{ACR_LOGIN_SERVER}/{IMAGE_REPO}:{version}"
    _log("INFO", f"Step 3: Deploying {new_image} to {container_app}")

    if dry_run:
        _step(result, "deploy", "skipped", "dry-run")
        _log("INFO", f"  [DRY RUN] Would deploy to {container_app}")
        return True

    # Record previous image for rollback
    result.previous_image = _get_current_image(env)
    _log("INFO", f"  Previous image: {result.previous_image}")

    r = _run([
        "az", "containerapp", "update",
        "--name", container_app,
        "--resource-group", RESOURCE_GROUP,
        "--image", new_image,
    ], timeout=120)

    if r.returncode != 0:
        _step(result, "deploy", "failed", f"Container update failed: {r.stdout.strip()[:200]}")
        result.error = f"Container app update failed for {container_app}"
        return False

    _step(result, "deploy", "passed", f"{container_app} → {new_image}")
    _log("PASS", f"  Deployed to {container_app}")
    return True


def _health_poll(result: DeployResult, env: str, version: str, dry_run: bool) -> bool:
    """Step 4: Wait for healthy startup + version match."""
    fqdn = ENVIRONMENTS[env]["fqdn"]
    expected_version = version.lstrip("v")
    _log("INFO", f"Step 4: Health poll — waiting for /health (version={expected_version})")

    if dry_run:
        _step(result, "health_poll", "skipped", "dry-run")
        return True

    elapsed = 0
    last_status = 0
    while elapsed < HEALTH_TIMEOUT_S:
        try:
            req = Request(f"https://{fqdn}/health", method="GET")
            with urlopen(req, timeout=10) as resp:
                last_status = resp.status
                body = json.loads(resp.read().decode())
                live_version = body.get("product_version", "")
                if live_version == expected_version:
                    _step(result, "health_poll", "passed",
                          f"Healthy in {elapsed}s (version={live_version})")
                    _log("PASS", f"  Healthy in {elapsed}s (version={live_version})")
                    return True
                _log("INFO", f"  {elapsed}s: version={live_version} (waiting for {expected_version})")
        except (HTTPError, URLError, OSError) as e:
            _log("INFO", f"  {elapsed}s: {type(e).__name__} (waiting...)")
        except Exception:
            pass

        time.sleep(HEALTH_POLL_INTERVAL_S)
        elapsed += HEALTH_POLL_INTERVAL_S

    _step(result, "health_poll", "failed",
          f"Timeout after {HEALTH_TIMEOUT_S}s (last HTTP {last_status})")
    result.error = f"Health check timeout after {HEALTH_TIMEOUT_S}s"
    return False


def _post_deploy_verification(result: DeployResult, env: str, version: str,
                               dry_run: bool) -> bool:
    """Step 5: Phase C — post-deploy verification against Phase A snapshots."""
    _log("INFO", "Step 5: Post-deploy verification (Phase C)")
    phase_name = "multi-c" if env == "staging" else "phase-c"
    version_stripped = version.lstrip("v")
    total_expected = 70 if env == "staging" else 35

    if dry_run:
        _step(result, "post_deploy_verification", "skipped", "dry-run")
        return True

    script = PROJECT_ROOT / "scripts" / "upgrade_verification.py"
    r = _run(
        [sys.executable, str(script), phase_name,
         "--env", env, "--new-version", version_stripped],
        timeout=600,
    )
    output = r.stdout

    # Parse PASS/FAIL counts
    total_pass = 0
    total_fail = 0
    for m in re.finditer(r"\((\d+)\s+pass,\s*(\d+)\s+fail\)", output):
        total_pass += int(m.group(1))
        total_fail += int(m.group(2))

    # Fallback: try uppercase format
    if total_pass == 0 and total_fail == 0:
        pass_matches = re.findall(r"(\d+)\s+PASS", output)
        fail_matches = re.findall(r"(\d+)\s+FAIL", output)
        if pass_matches:
            total_pass = sum(int(x) for x in pass_matches)
        if fail_matches:
            total_fail = sum(int(x) for x in fail_matches)

    result.verification_pass = total_pass
    result.verification_fail = total_fail

    if r.returncode != 0 or total_fail > 0:
        detail = f"{total_pass} pass, {total_fail} fail (expected {total_expected})"
        _step(result, "post_deploy_verification", "failed", detail)
        result.error = f"Phase C verification failed: {detail}"
        return False

    _step(result, "post_deploy_verification", "passed",
          f"{total_pass}/{total_expected} assertions passed")
    _log("PASS", f"  Phase C: {total_pass}/{total_expected} passed")
    return True


def _optional_e2e_regression(result: DeployResult, env: str, dry_run: bool,
                              run_e2e: bool) -> bool:
    """Step 6: Optional E2E regression (test_pipeline.py)."""
    if not run_e2e:
        _step(result, "e2e_regression", "skipped", "not requested")
        _log("INFO", "Step 6: E2E regression — skipped (not requested)")
        return True

    _log("INFO", "Step 6: E2E regression (test_pipeline.py)")

    if dry_run:
        _step(result, "e2e_regression", "skipped", "dry-run")
        return True

    script = PROJECT_ROOT / "scripts" / "test_pipeline.py"
    if not script.exists():
        _step(result, "e2e_regression", "skipped", "test_pipeline.py not found")
        _log("WARN", "  test_pipeline.py not found — skipping E2E")
        return True

    r = _run(
        [sys.executable, str(script), "--env", env],
        timeout=900,  # 15 min for full E2E
    )

    if r.returncode != 0:
        _step(result, "e2e_regression", "failed", f"Exit {r.returncode}")
        # E2E failure is logged but does NOT trigger rollback — only Phase C does
        _log("WARN", f"  E2E regression exited {r.returncode}")
        return True  # Non-fatal: E2E is informational

    _step(result, "e2e_regression", "passed")
    _log("PASS", "  E2E regression passed")
    return True


def _rollback(result: DeployResult, env: str) -> None:
    """Step 7: Auto-rollback to previous image on verification failure."""
    if not result.previous_image:
        _log("WARN", "  Cannot rollback — no previous image recorded")
        result.rollback_status = "failed"
        _step(result, "rollback", "failed", "No previous image")
        return

    container_app = ENVIRONMENTS[env]["container_app"]
    _log("INFO", f"Step 7: Rolling back {container_app} to {result.previous_image}")

    r = _run([
        "az", "containerapp", "update",
        "--name", container_app,
        "--resource-group", RESOURCE_GROUP,
        "--image", result.previous_image,
    ], timeout=120)

    if r.returncode != 0:
        _log("FAIL", f"  Rollback FAILED: {r.stdout.strip()[:200]}")
        result.rollback_status = "failed"
        _step(result, "rollback", "failed", r.stdout.strip()[:200])
    else:
        _log("PASS", f"  Rolled back to {result.previous_image}")
        result.rollback_status = "succeeded"
        result.rollback_performed = True
        _step(result, "rollback", "passed", result.previous_image)

    # Create DEFECT work item for the rollback
    try:
        from scripts._defect_reporter import create_defect
        create_defect(
            title=f"Deploy rollback: {env} {result.version} → {result.previous_image}",
            description=(
                f"Deploy of {result.version} to {env} failed verification. "
                f"Auto-rollback to {result.previous_image}. "
                f"Verification: {result.verification_pass} pass, "
                f"{result.verification_fail} fail. Error: {result.error}"
            ),
            source_spec_id="SPEC-1825",
            component="infrastructure_automation",
            changed_by="deploy-orchestrator",
        )
    except Exception as e:
        _log("WARN", f"  Could not create DEFECT WI: {e}")


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------
def run_deploy(
    env: str,
    version: str,
    *,
    dry_run: bool = False,
    run_e2e: bool = False,
    skip_snapshot: bool = False,
) -> DeployResult:
    """Execute the full deploy orchestration pipeline.

    This is the primary programmatic entry point — called by the superadmin
    API and by the CLI.  Returns a structured DeployResult.
    """
    result = DeployResult(
        status="running",
        environment=env,
        version=version,
        dry_run=dry_run,
        started_at=datetime.now(timezone.utc).isoformat(),
    )

    _log("INFO", f"Deploy Orchestrator starting: {env} {version}"
         + (" [DRY RUN]" if dry_run else ""))

    # --- Pre-deploy steps (abort on failure, no rollback needed) ---
    if not _validate_image(result, version, dry_run):
        result.status = "failed"
        _finalize(result, env)
        return result

    if not skip_snapshot and not _pre_deploy_snapshot(result, env, dry_run):
        result.status = "failed"
        _finalize(result, env)
        return result

    # --- Deploy (failure here = no rollback, image didn't change) ---
    if not _deploy_container(result, env, version, dry_run):
        result.status = "failed"
        _finalize(result, env)
        return result

    # --- Post-deploy steps (failure triggers rollback) ---
    if not _health_poll(result, env, version, dry_run):
        if not dry_run:
            _rollback(result, env)
        result.status = "rolled_back" if result.rollback_performed else "failed"
        _finalize(result, env)
        return result

    if not _post_deploy_verification(result, env, version, dry_run):
        if not dry_run:
            _rollback(result, env)
        result.status = "rolled_back" if result.rollback_performed else "failed"
        _finalize(result, env)
        return result

    # --- Optional E2E (informational, no rollback on failure) ---
    _optional_e2e_regression(result, env, dry_run, run_e2e)

    result.status = "succeeded"
    _finalize(result, env)
    return result


def _record_deployment_event(result: DeployResult, env: str) -> None:
    """POST a MODEL_DEPLOYED or MODEL_ROLLED_BACK audit event to the API (WI-1285).

    Best-effort — failures are logged but do not change the deploy result.
    Requires SPA_PLATFORM_ADMIN_KEY env var to authenticate.
    """
    env_config = ENVIRONMENTS.get(env, {})
    fqdn = env_config.get("fqdn", "")
    api_key = os.environ.get("SPA_PLATFORM_ADMIN_KEY", "")

    if not fqdn or not api_key:
        _log("INFO", "Skipping deployment event recording (no FQDN or API key)")
        return

    event_type = "model.rolled_back" if result.rollback_performed else "model.deployed"
    payload = {
        "event_type": event_type,
        "environment": env,
        "version": result.version,
        "image": result.image,
        "previous_image": result.previous_image,
        "revision_name": result.revision_name,
        "status": result.status,
        "duration_s": result.duration_s,
        "verification_pass": result.verification_pass,
        "verification_fail": result.verification_fail,
        "dry_run": result.dry_run,
    }

    try:
        url = f"https://{fqdn}/api/superadmin/deployments/record"
        body = json.dumps(payload).encode("utf-8")
        req = Request(url, data=body, method="POST", headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        })
        with urlopen(req, timeout=10) as resp:
            _log("PASS", f"  Deployment event recorded: {event_type} ({resp.status})")
    except Exception as exc:
        _log("WARN", f"  Failed to record deployment event (non-fatal): {exc}")


def _finalize(result: DeployResult, env: str) -> None:
    """Compute duration and write log file."""
    result.completed_at = datetime.now(timezone.utc).isoformat()
    result.duration_s = round(
        (datetime.fromisoformat(result.completed_at)
         - datetime.fromisoformat(result.started_at)).total_seconds(), 1
    )

    level = "PASS" if result.status == "succeeded" else "FAIL"
    _log(level, f"Deploy Orchestrator {result.status} in {result.duration_s}s")

    # Record deployment audit event (WI-1285)
    _record_deployment_event(result, env)

    log_path = _write_log_file(env)
    _log("INFO", f"Log written to {log_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy Orchestrator — deploy-verify-rollback (SPEC-1825)",
    )
    parser.add_argument("--env", required=True, choices=["staging", "production"],
                        help="Target environment")
    parser.add_argument("--version", required=True,
                        help="Image version tag (e.g., v1.90.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate without executing deployment")
    parser.add_argument("--e2e", action="store_true",
                        help="Run optional E2E regression after verification")
    parser.add_argument("--skip-snapshot", action="store_true",
                        help="Skip Phase A snapshot (use existing snapshots)")
    parser.add_argument("--json", action="store_true",
                        help="Output result as JSON (for SPA integration)")
    args = parser.parse_args()

    result = run_deploy(
        args.env, args.version,
        dry_run=args.dry_run,
        run_e2e=args.e2e,
        skip_snapshot=args.skip_snapshot,
    )

    if args.json:
        print(result.to_json())

    return 0 if result.status == "succeeded" else 1


if __name__ == "__main__":
    sys.exit(main())
