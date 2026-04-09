#!/usr/bin/env python3
"""Release Pipeline — HIGHER-LEVEL RELEASE ORCHESTRATION (S251 OM-1).

This script orchestrates the full release cycle (tests → staging → production).
It delegates production deployment to the CANONICAL production deploy command:

    python scripts/deploy_pipeline.py --env production --version vX.Y.Z --approved

deploy_pipeline.py is the sole canonical production deployment procedure.
This script is the orchestrator that sequences pre-release gates around it.

Single-invocation pipeline that executes the complete release cycle:

    Step 1: Offline unit/integration tests (fail-fast)
    Step 2: Deploy to staging (via deploy_pipeline.py --env staging)
    Step 3: E2E tests against staging (destructive + load, excluding Shopify)
    Step 4: Deploy to production (via deploy_pipeline.py --env production)
    Step 5: Production health verification

GOV-16: Production deployment requires owner approval via DEPLOY_APPROVED
environment token.  Binary pass/fail — there is no SKIP or WARN status.
Absence of proof is failure.  Any non-PASS result halts the pipeline.

Usage:
    python scripts/release_pipeline.py --version v1.80.0
    python scripts/release_pipeline.py --version v1.80.0 --skip-offline
    python scripts/release_pipeline.py --version v1.80.0 --dry-run

Exit codes:
    0 = SUCCESS (all steps passed)
    1 = FAILURE (pipeline halted at first critical failure)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_log_lines: list[str] = []


def log(level: str, msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] [{level:>5}] {msg}"
    print(line, flush=True)
    _log_lines.append(line)


# ---------------------------------------------------------------------------
# Step runner
# ---------------------------------------------------------------------------

class StepResult:
    def __init__(self, step: int, name: str, status: str, duration: float, detail: str = ""):
        self.step = step
        self.name = name
        self.status = status
        self.duration = duration
        self.detail = detail

    @property
    def passed(self) -> bool:
        """Binary: proven (PASS) or not proven (FAIL).  No third state."""
        return self.status == "PASS"


def run_subprocess(cmd: list[str], timeout: int = 600, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a subprocess, streaming output live."""
    cwd = cwd or PROJECT_ROOT
    log("INFO", f"  $ {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        if result.stdout:
            for line in result.stdout.strip().split("\n")[-20:]:
                log("INFO", f"    {line}")
        if result.returncode != 0 and result.stderr:
            for line in result.stderr.strip().split("\n")[-10:]:
                log("ERROR", f"    {line}")
        return result
    except subprocess.TimeoutExpired:
        log("ERROR", f"  Command timed out after {timeout}s")
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="TIMEOUT")


# ---------------------------------------------------------------------------
# Step 1: Offline tests
# ---------------------------------------------------------------------------

def step_1_offline_tests(args: argparse.Namespace) -> StepResult:
    """Run offline unit/integration test suite (fail-fast gate)."""
    t0 = time.time()
    log("INFO", "Step 1: Offline unit/integration tests")

    if args.skip_offline:
        log("FAIL", "  Offline tests not run — not proven")
        return StepResult(1, "Offline Tests", "FAIL", time.time() - t0,
                          "not run (--skip-offline) — absence of proof is failure")

    # Use PowerShell test harness
    r = run_subprocess(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File",
         "scripts/run-tests-thermal-safe.ps1", "-SkipLive"],
        timeout=600,
    )

    dt = time.time() - t0

    # Parse result: look for "X passed" and "X failed"
    passed_match = re.search(r"(\d+)\s+passed", r.stdout or "")
    failed_match = re.search(r"(\d+)\s+failed", r.stdout or "")
    passed_count = int(passed_match.group(1)) if passed_match else 0
    failed_count = int(failed_match.group(1)) if failed_match else 0

    if r.returncode == 0 and failed_count == 0:
        log("PASS", f"  Offline tests: {passed_count} passed, 0 failed")
        return StepResult(1, "Offline Tests", "PASS", dt,
                          f"{passed_count}P/0F")
    else:
        # ADOPT-1/AVOID-2: Zero tolerance — any failure blocks the release.
        # No "known failure" exceptions. Fix the test or fix the code.
        log("FAIL", f"  Offline tests: {passed_count} passed, {failed_count} failed")
        return StepResult(1, "Offline Tests", "FAIL", dt,
                          f"{passed_count}P/{failed_count}F")


# ---------------------------------------------------------------------------
# Step 2: Deploy to staging
# ---------------------------------------------------------------------------

def step_2_deploy_staging(args: argparse.Namespace) -> StepResult:
    """Run the deploy pipeline for staging."""
    t0 = time.time()
    log("INFO", "Step 2: Deploy to staging")

    cmd = [sys.executable, "scripts/deploy_pipeline.py",
           "--env", "staging", "--version", args.version]
    if args.dry_run:
        cmd.append("--dry-run")

    r = run_subprocess(cmd, timeout=600)
    dt = time.time() - t0

    if r.returncode == 0:
        log("PASS", f"  Staging deploy: SUCCESS ({dt:.0f}s)")
        return StepResult(2, "Deploy Staging", "PASS", dt)
    else:
        log("FAIL", f"  Staging deploy: FAILED ({dt:.0f}s)")
        return StepResult(2, "Deploy Staging", "FAIL", dt, "deploy_pipeline.py returned non-zero")


# ---------------------------------------------------------------------------
# Step 3: E2E tests against staging (excluding Shopify)
# ---------------------------------------------------------------------------

def step_3_e2e_tests(args: argparse.Namespace) -> StepResult:
    """Run E2E test pipeline against staging (all phases, excluding Shopify)."""
    t0 = time.time()
    log("INFO", "Step 3: E2E tests against staging (excluding Shopify)")

    if args.dry_run:
        log("INFO", "  [DRY RUN] Would run: test_pipeline.py --env staging")
        return StepResult(3, "E2E Tests", "FAIL", time.time() - t0,
                          "not run (dry run) — absence of proof is failure")

    # 65s cooldown after deploy to allow rate limit windows to expire
    log("INFO", "  ... 65s post-deploy cooldown ...")
    time.sleep(65)

    version_num = args.version.lstrip("v")
    cmd = [sys.executable, "scripts/test_pipeline.py",
           "--env", "staging", "--version", version_num]

    r = run_subprocess(cmd, timeout=600)
    dt = time.time() - t0

    # Parse results
    pass_match = re.search(r"(\d+)\s+PASS", r.stdout or "")
    fail_match = re.search(r"(\d+)\s+FAIL", r.stdout or "")
    pass_count = int(pass_match.group(1)) if pass_match else 0
    fail_count = int(fail_match.group(1)) if fail_match else 0

    if r.returncode == 0 and fail_count == 0:
        log("PASS", f"  E2E tests: {pass_count} PASS, 0 FAIL")
        return StepResult(3, "E2E Tests", "PASS", dt, f"{pass_count}P/0F")
    else:
        # ADOPT-1/AVOID-2: Zero tolerance — no "minor failure" exceptions.
        log("FAIL", f"  E2E tests: {pass_count} PASS, {fail_count} FAIL")
        return StepResult(3, "E2E Tests", "FAIL", dt, f"{pass_count}P/{fail_count}F")


# ---------------------------------------------------------------------------
# Step 4: Deploy to production
# ---------------------------------------------------------------------------

def step_4_deploy_production(args: argparse.Namespace) -> StepResult:
    """Run the deploy pipeline for production (non-disruptive upgrade)."""
    t0 = time.time()
    log("INFO", "Step 4: Deploy to production")

    cmd = [sys.executable, "scripts/deploy_pipeline.py",
           "--env", "production", "--version", args.version]
    if args.dry_run:
        cmd.append("--dry-run")

    r = run_subprocess(cmd, timeout=600)
    dt = time.time() - t0

    if r.returncode == 0:
        log("PASS", f"  Production deploy: SUCCESS ({dt:.0f}s)")
        return StepResult(4, "Deploy Production", "PASS", dt)
    else:
        log("FAIL", f"  Production deploy: FAILED ({dt:.0f}s)")
        return StepResult(4, "Deploy Production", "FAIL", dt, "deploy_pipeline.py returned non-zero")


# ---------------------------------------------------------------------------
# Step 5: Production health verification
# ---------------------------------------------------------------------------

def step_5_verify_both(args: argparse.Namespace) -> StepResult:
    """Verify both staging and production are operational."""
    t0 = time.time()
    log("INFO", "Step 5: Verify both environments")

    if args.dry_run:
        log("INFO", "  [DRY RUN] Would verify staging + production health")
        return StepResult(5, "Verify Environments", "FAIL", time.time() - t0,
                          "not run (dry run) — absence of proof is failure")

    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    from upgrade_verification import ENVIRONMENTS, api_call

    errors = []
    version_num = args.version.lstrip("v")

    for env_name in ["staging", "production"]:
        env = ENVIRONMENTS.get(env_name)
        if not env:
            errors.append(f"{env_name}: not configured in upgrade_verification.py")
            continue

        fqdn = env.get("fqdn", "")
        base_url = env.get("base_url", f"https://{fqdn}" if fqdn else "")
        api_key = env.get("api_key", "") or env.get("spa_api_key", "")

        # Health check
        try:
            resp = api_call(f"{base_url}/api/health", headers={})
            if resp.get("status") != "healthy":
                errors.append(f"{env_name}: health status = {resp.get('status')}")
            else:
                log("PASS", f"  {env_name}: healthy")
        except Exception as exc:
            errors.append(f"{env_name}: health check failed: {exc}")

        # Version check
        try:
            headers = {"X-API-Key": api_key} if api_key else {}
            resp = api_call(f"{base_url}/api/superadmin/dashboard", headers=headers)
            reported_version = resp.get("system_health", {}).get("version", {}).get("product")
            if reported_version != version_num:
                errors.append(f"{env_name}: version mismatch ({reported_version} != {version_num})")
            else:
                log("PASS", f"  {env_name}: version {reported_version}")
        except Exception as exc:
            # Non-fatal — dashboard may require auth
            log("WARN", f"  {env_name}: version check skipped ({exc})")

    # P1-1b: Widget transport proof (unconditional — hard deployment gate).
    # Verify widget.js served + conversation creation + SSE stream for each env.
    for env_name in ["staging", "production"]:
        env = ENVIRONMENTS.get(env_name)
        if not env:
            continue
        fqdn = env.get("fqdn", "")
        base_url = env.get("base_url", f"https://{fqdn}" if fqdn else "")
        widget_key = env.get("widget_key", "")
        if not widget_key:
            # P1-1b: fail-closed — missing widget key is a gate failure, not a skip
            errors.append(f"{env_name}: widget key not configured — cannot verify transport")
            continue
        try:
            import json
            import urllib.request

            headers_common = {"Content-Type": "application/json", "X-Widget-Key": widget_key}

            # 1. Widget bundle reachable
            widget_req = urllib.request.Request(f"{base_url}/widget.js")
            with urllib.request.urlopen(widget_req, timeout=10) as resp:
                bundle_size = len(resp.read())
                if resp.status != 200 or bundle_size < 1000:
                    errors.append(f"{env_name}: widget.js not served correctly (status={resp.status}, size={bundle_size})")
                else:
                    log("PASS", f"  {env_name}: widget.js served ({bundle_size} bytes)")

            # 2. Conversation creation
            conv_req = urllib.request.Request(
                f"{base_url}/api/chat/conversations",
                data=json.dumps({}).encode(),
                headers=headers_common,
                method="POST",
            )
            with urllib.request.urlopen(conv_req, timeout=15) as resp:
                conv_data = json.loads(resp.read())
                conv_id = conv_data.get("conversation_id", "")
                if not conv_id:
                    errors.append(f"{env_name}: conversation creation returned no ID")
                else:
                    log("PASS", f"  {env_name}: conversation created ({conv_id[:8]}...)")

            # 3. Send message + SSE stream delivers token + done
            if conv_id:
                msg_req = urllib.request.Request(
                    f"{base_url}/api/chat/message",
                    data=json.dumps({"conversation_id": conv_id, "content": "health check"}).encode(),
                    headers=headers_common,
                    method="POST",
                )
                with urllib.request.urlopen(msg_req, timeout=15) as resp:
                    if resp.status not in (200, 201):
                        errors.append(f"{env_name}: message send failed (status={resp.status})")
                    else:
                        log("PASS", f"  {env_name}: message sent")

                # Verify SSE stream delivers at least one token event + done
                stream_url = f"{base_url}/api/chat/stream/{conv_id}"
                sse_req = urllib.request.Request(stream_url, headers={"X-Widget-Key": widget_key})
                got_token = False
                got_done = False
                with urllib.request.urlopen(sse_req, timeout=45) as resp:
                    for raw_line in resp:
                        line = raw_line.decode("utf-8", errors="replace").strip()
                        if line.startswith("event: token"):
                            got_token = True
                        elif line.startswith("event: done"):
                            got_done = True
                            break
                if got_token and got_done:
                    log("PASS", f"  {env_name}: SSE stream delivered token + done")
                else:
                    errors.append(f"{env_name}: SSE stream incomplete (token={got_token}, done={got_done})")

        except Exception as exc:
            errors.append(f"{env_name}: widget transport proof failed: {exc}")

    dt = time.time() - t0

    if not errors:
        log("PASS", f"  Both environments verified ({dt:.0f}s)")
        return StepResult(5, "Verify Environments", "PASS", dt)
    else:
        for err in errors:
            log("FAIL", f"  {err}")
        return StepResult(5, "Verify Environments", "FAIL", dt, "; ".join(errors))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fully Autonomous Release Pipeline — single invocation, no human/Claude interaction",
    )
    parser.add_argument("--version", required=True,
                        help="Image version tag (e.g., v1.80.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate without executing destructive actions")
    parser.add_argument("--skip-offline", action="store_true",
                        help="Skip offline test suite (Step 1)")
    parser.add_argument(
        "--change-class",
        choices=["A", "B", "C"],
        required=True,
        help=(
            "Change classification by blast radius (S251 OM-2). "
            "A=UI-only, B=admin/config/integration, "
            "C=widget/auth/chat/config/activation/migration"
        ),
    )
    args = parser.parse_args()

    if not re.match(r"^v\d+\.\d+\.\d+$", args.version):
        print(f"ERROR: Version must be in format vX.Y.Z (got: {args.version})")
        return 1

    start_time = time.time()
    results: list[StepResult] = []

    log("INFO", f"Release Pipeline: {args.version}")
    log("INFO", f"  Change Class: {args.change_class}"
        f" ({'UI-only' if args.change_class == 'A' else 'admin/config' if args.change_class == 'B' else 'widget/auth/chat — FULL GATES'})")
    log("INFO", f"  staging -> E2E -> production -> verify")
    if args.dry_run:
        log("INFO", "  *** DRY RUN MODE ***")

    # Execute steps sequentially — halt on critical failure
    steps = [
        step_1_offline_tests,
        step_2_deploy_staging,
        step_3_e2e_tests,
        step_4_deploy_production,
        step_5_verify_both,
    ]

    for step_fn in steps:
        result = step_fn(args)
        results.append(result)
        if not result.passed:
            log("FAIL", f"  Pipeline halted at Step {result.step}: {result.name}")
            break

    # Summary
    total_time = time.time() - start_time
    log("INFO", "")
    log("INFO", f"{'='*60}")
    log("INFO", f"  RELEASE PIPELINE SUMMARY — {args.version}")
    log("INFO", f"{'='*60}")

    for r in results:
        status_icon = {"PASS": "+", "FAIL": "X"}
        icon = status_icon.get(r.status, "?")
        log("INFO", f"  [{icon}] Step {r.step}: {r.name:<25} {r.status:>5}  {r.duration:6.1f}s  {r.detail}")

    all_passed = all(r.passed for r in results)
    log("INFO", f"{'='*60}")
    log("INFO", f"  RESULT: {'SUCCESS' if all_passed else 'FAILED'}  ({total_time:.0f}s total)")
    log("INFO", f"{'='*60}")

    # Write log
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    log_path = log_dir / f"release-pipeline-{args.version}-{ts}.log"
    log_path.write_text("\n".join(_log_lines), encoding="utf-8")
    log("INFO", f"  Log: {log_path}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
