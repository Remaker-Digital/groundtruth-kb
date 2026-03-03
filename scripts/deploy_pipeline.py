#!/usr/bin/env python3
"""Automated Build/Deploy Pipeline — SPEC-1615 (Two-Track).

Single-invocation pipeline that builds, deploys, and verifies a release
without any human or Claude interaction during execution.

Two tracks:
  Staging (comprehensive):  15 phases — build, deploy, version verify,
    upgrade verification, config pipeline, seed test tenant, verify
    Initialized state.
  Production (safe):  12 phases — build, deploy, version verify,
    upgrade verification + lightweight smoke. No tenant mutations.

Usage:
    python scripts/deploy_pipeline.py --env staging --version v1.66.0
    python scripts/deploy_pipeline.py --env production --version v1.66.0
    python scripts/deploy_pipeline.py --env staging --version v1.66.0 --dry-run

Exit codes:
    0 = SUCCESS (all phases passed)
    1 = FAILURE (one or more phases failed)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 stdout on Windows to avoid cp1252 encoding crashes
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))

from upgrade_verification import ENVIRONMENTS, TENANTS, api_call  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ACR_NAME = "acragentredeastus"
ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
IMAGE_REPO = "api-gateway"
RESOURCE_GROUP = "Agent-Red"

ADMIN_SPAS = [
    ("standalone", PROJECT_ROOT / "admin" / "standalone"),
    ("shopify", PROJECT_ROOT / "admin" / "shopify"),
    ("provider", PROJECT_ROOT / "admin" / "provider"),
]
WIDGET_DIR = PROJECT_ROOT / "widget"

DIST_ARTIFACTS = [
    PROJECT_ROOT / "admin" / "standalone" / "dist" / "index.html",
    PROJECT_ROOT / "admin" / "shopify" / "dist" / "index.html",
    PROJECT_ROOT / "admin" / "provider" / "dist" / "index.html",
    PROJECT_ROOT / "widget" / "dist" / "agent-red-widget.iife.js",
]

PROTECTED_BEHAVIORS = [
    ("PB-001", "injectWidget", "admin/standalone/layouts/StandaloneLayout.tsx", 1),
    ("PB-002", "icon-master.svg", "admin/standalone/index.html", 1),
    ("PB-003", "icon-master.svg", "admin/provider/index.html", 1),
    ("PB-010", "Save your configuration first", "src/multi_tenant/activation_service.py", 2),
    ("PB-011", "isProOrHigher", "admin/standalone/pages/MemoryPrivacy.tsx", 1),
    ("PB-020", "send_team_invite_alert", "src/multi_tenant/admin_team_api.py", 1),
    ("PB-021", "admin_url", "src/multi_tenant/alert_delivery.py", 2),
    ("PB-022", "resend-invite", "src/multi_tenant/admin_team_api.py", 1),
    ("PB-023a", "find_superadmin_email", "src/chat/pipeline/critic_escalation.py", 1),
    ("PB-023b", "recipient_emails", "src/multi_tenant/alert_delivery.py", 3),
    ("PB-030", "VITE_API_URL", "docs/operations/build-deploy-procedure.md", 1),
]

BUILD_CONTEXT_CRITICAL_FILES = [
    "src/main.py",
    "src/multi_tenant/cosmos_schema.py",
    "src/multi_tenant/auth.py",
    "src/multi_tenant/middleware.py",
    "src/chat/pipeline/__init__.py",
    "Dockerfile",
    "requirements.txt",
]

HEALTH_WAIT_SECONDS = 90
HEALTH_POLL_INTERVAL = 10


# ---------------------------------------------------------------------------
# Phase result tracking
# ---------------------------------------------------------------------------
class PhaseResult:
    """Result of a single pipeline phase."""

    def __init__(self, phase: int, name: str, status: str, duration: float,
                 detail: str = "", extra: str = ""):
        self.phase = phase
        self.name = name
        self.status = status  # PASS, FAIL, SKIP
        self.duration = duration
        self.detail = detail
        self.extra = extra  # e.g., "[70/70]"

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_log_lines: list[str] = []


def log(level: str, msg: str) -> None:
    """Print a timestamped log line and buffer for log file."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level:5s}] {msg}"
    _log_lines.append(line)
    try:
        print(line, flush=True)
    except (OSError, ValueError):
        pass  # stdout closed (background task) — still captured in _log_lines


def _write_log_file(env: str) -> Path:
    """Write buffered log lines to a file."""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = log_dir / f"deploy-pipeline-{env}-{ts}.log"
    log_path.write_text("\n".join(_log_lines) + "\n", encoding="utf-8")
    return log_path


# ---------------------------------------------------------------------------
# Subprocess helpers — real-time streaming (SPEC-1619)
# ---------------------------------------------------------------------------
from scripts._subprocess_stream import stream_subprocess as _stream


def _run(cmd: list[str], cwd: str | Path | None = None,
         timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a subprocess with real-time output streaming.

    Returns a CompletedProcess-compatible object so all existing call sites
    continue to work.  Output appears on the terminal line-by-line as the
    subprocess executes (SPEC-1619: SHOW EVERYTHING).
    """
    r = _stream(cmd, cwd=cwd, timeout=timeout, prefix="  ")
    return subprocess.CompletedProcess(
        args=cmd, returncode=r.returncode,
        stdout=r.stdout, stderr="",
    )


def _run_shell(cmd: str, cwd: str | Path | None = None,
               timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a shell command with real-time output streaming."""
    r = _stream(cmd, cwd=cwd, timeout=timeout, prefix="  ")
    return subprocess.CompletedProcess(
        args=cmd, returncode=r.returncode,
        stdout=r.stdout, stderr="",
    )


# ---------------------------------------------------------------------------
# Phase implementations
# ---------------------------------------------------------------------------
def phase_0_validate_environment(args: argparse.Namespace) -> PhaseResult:
    """Validate all prerequisites before any build step (fail-fast)."""
    t0 = time.time()
    failures = []

    # 1. Azure CLI authenticated
    r = _run(["az", "account", "show"])
    if r.returncode != 0:
        failures.append("Azure CLI not authenticated (run: az login)")

    # 2. ACR accessible
    r = _run(["az", "acr", "show", "--name", ACR_NAME])
    if r.returncode != 0:
        failures.append(f"ACR '{ACR_NAME}' not accessible")

    # 3. Node.js
    r = _run(["node", "--version"])
    if r.returncode != 0:
        failures.append("Node.js not available")
    else:
        ver = r.stdout.strip()
        log("INFO", f"  Node.js: {ver}")

    # 4. npm
    r = _run(["npm", "--version"])
    if r.returncode != 0:
        failures.append("npm not available")

    # 5. Python version check (we're already running Python)
    log("INFO", f"  Python: {sys.version.split()[0]}")

    # 6. Version matches PRODUCT_VERSION
    r = _run([sys.executable, "-c",
              "from src.multi_tenant.api_versioning import PRODUCT_VERSION; print(PRODUCT_VERSION)"],
             cwd=PROJECT_ROOT)
    if r.returncode != 0:
        failures.append(f"Cannot read PRODUCT_VERSION: {r.stderr.strip()[:200]}")
    else:
        product_version = r.stdout.strip()
        expected = args.version.lstrip("v")
        if product_version != expected:
            failures.append(
                f"PRODUCT_VERSION mismatch: code has '{product_version}', "
                f"pipeline version is '{expected}'"
            )
        else:
            log("INFO", f"  PRODUCT_VERSION: {product_version} (matches)")

    # 7. Project root sanity check
    if not (PROJECT_ROOT / "Dockerfile").exists():
        failures.append("Not in project root (Dockerfile not found)")
    if not (PROJECT_ROOT / "CLAUDE.md").exists():
        failures.append("Not in project root (CLAUDE.md not found)")

    # 8. Target environment valid
    if args.env not in ENVIRONMENTS:
        failures.append(f"Unknown environment '{args.env}' (valid: {list(ENVIRONMENTS.keys())})")

    dt = time.time() - t0
    if failures:
        detail = "; ".join(failures)
        log("FAIL", f"  Environment validation failed: {detail}")
        return PhaseResult(0, "Validate Environment", "FAIL", dt, detail)

    log("PASS", "  All environment checks passed")
    return PhaseResult(0, "Validate Environment", "PASS", dt)


def phase_1_protected_behaviors(args: argparse.Namespace) -> PhaseResult:
    """Verify protected behaviors exist in codebase (regression gate)."""
    t0 = time.time()
    passed = 0
    total = len(PROTECTED_BEHAVIORS)
    failures = []

    for pb_id, pattern, filepath, threshold in PROTECTED_BEHAVIORS:
        full_path = PROJECT_ROOT / filepath
        if not full_path.exists():
            failures.append(f"{pb_id}: file not found ({filepath})")
            continue
        content = full_path.read_text(encoding="utf-8", errors="replace")
        count = content.count(pattern)
        if count >= threshold:
            passed += 1
        else:
            failures.append(f"{pb_id}: '{pattern}' count={count} < {threshold} in {filepath}")

    dt = time.time() - t0
    if passed == total:
        log("PASS", f"  Protected Behaviors: {passed}/{total}")
        return PhaseResult(1, "Protected Behaviors", "PASS", dt)
    else:
        detail = "; ".join(failures)
        log("FAIL", f"  Protected Behaviors: {passed}/{total} — {detail}")
        return PhaseResult(1, "Protected Behaviors", "FAIL", dt, detail)


def phase_2_clear_vite_api_url(args: argparse.Namespace) -> PhaseResult:
    """Write empty VITE_API_URL to admin SPA .env.local files for production builds."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would clear VITE_API_URL in 3 admin .env.local files")
        return PhaseResult(2, "Clear VITE_API_URL", "PASS", time.time() - t0, "dry-run")

    for name, spa_dir in ADMIN_SPAS:
        env_file = spa_dir / ".env.local"
        env_file.write_text("VITE_API_URL=\n", encoding="utf-8")
        log("INFO", f"  Cleared VITE_API_URL in {name}/.env.local")

    dt = time.time() - t0
    return PhaseResult(2, "Clear VITE_API_URL", "PASS", dt)


def phase_3_build_artifacts(args: argparse.Namespace) -> PhaseResult:
    """Build all 4 admin dists + widget bundle."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would build 3 admin SPAs + widget")
        return PhaseResult(3, "Build Artifacts", "PASS", time.time() - t0, "dry-run")

    # Build 3 admin SPAs using npx tsc && npx vite build (bypasses sync-env prebuild hook)
    for name, spa_dir in ADMIN_SPAS:
        log("INFO", f"  Building {name}...")
        # Run tsc first
        r = _run_shell("npx tsc", cwd=spa_dir, timeout=120)
        if r.returncode != 0:
            detail = f"TypeScript compilation failed for {name}: {r.stderr.strip()[:300]}"
            log("FAIL", f"  {detail}")
            return PhaseResult(3, "Build Artifacts", "FAIL", time.time() - t0, detail)

        # Then vite build
        r = _run_shell("npx vite build", cwd=spa_dir, timeout=120)
        if r.returncode != 0:
            detail = f"Vite build failed for {name}: {r.stderr.strip()[:300]}"
            log("FAIL", f"  {detail}")
            return PhaseResult(3, "Build Artifacts", "FAIL", time.time() - t0, detail)

        log("PASS", f"  {name} built")

    # Build widget
    log("INFO", "  Building widget...")
    r = _run_shell("npm run build", cwd=WIDGET_DIR, timeout=120)
    if r.returncode != 0:
        detail = f"Widget build failed: {r.stderr.strip()[:300]}"
        log("FAIL", f"  {detail}")
        return PhaseResult(3, "Build Artifacts", "FAIL", time.time() - t0, detail)
    log("PASS", "  widget built")

    dt = time.time() - t0
    return PhaseResult(3, "Build Artifacts", "PASS", dt)


def phase_4_freshness_gate(args: argparse.Namespace) -> PhaseResult:
    """Verify all dist artifacts exist and are less than 5 minutes old."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would verify dist freshness")
        return PhaseResult(4, "Build Freshness Gate", "PASS", time.time() - t0, "dry-run")

    stale = []
    now = time.time()
    for artifact in DIST_ARTIFACTS:
        if not artifact.exists():
            stale.append(f"MISSING: {artifact.relative_to(PROJECT_ROOT)}")
            continue
        age_min = (now - artifact.stat().st_mtime) / 60
        if age_min > 5:
            stale.append(f"STALE: {artifact.relative_to(PROJECT_ROOT)} ({age_min:.0f} min old)")
        else:
            log("INFO", f"  FRESH: {artifact.relative_to(PROJECT_ROOT)} ({age_min:.1f} min)")

    dt = time.time() - t0
    if stale:
        detail = "; ".join(stale)
        log("FAIL", f"  Freshness gate failed: {detail}")
        return PhaseResult(4, "Build Freshness Gate", "FAIL", dt, detail)

    return PhaseResult(4, "Build Freshness Gate", "PASS", dt)


def phase_5_restore_env_local(args: argparse.Namespace) -> PhaseResult:
    """Restore .env.local files by running sync-admin-env.ps1."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would restore .env.local files")
        return PhaseResult(5, "Restore .env.local", "PASS", time.time() - t0, "dry-run")

    script = PROJECT_ROOT / "scripts" / "sync-admin-env.ps1"
    if script.exists():
        r = _run(["powershell", "-File", str(script)], cwd=PROJECT_ROOT, timeout=30)
        if r.returncode != 0:
            log("WARN", f"  sync-admin-env.ps1 returned {r.returncode}: {r.stderr.strip()[:200]}")
        else:
            log("INFO", "  .env.local files restored via sync-admin-env.ps1")
    else:
        log("WARN", "  sync-admin-env.ps1 not found — skipping restore")

    dt = time.time() - t0
    return PhaseResult(5, "Restore .env.local", "PASS", dt)


def phase_6_create_build_context(args: argparse.Namespace) -> tuple[PhaseResult, str]:
    """Create minimal build context directory for ACR build."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would create build context")
        return PhaseResult(6, "Create Build Context", "PASS", time.time() - t0, "dry-run"), ""

    ctx = tempfile.mkdtemp(prefix="agentred-build-")
    log("INFO", f"  Build context: {ctx}")

    try:
        # Copy Dockerfile and requirements.txt
        shutil.copy2(PROJECT_ROOT / "Dockerfile", ctx)
        shutil.copy2(PROJECT_ROOT / "requirements.txt", ctx)

        # Copy src/ and config/
        shutil.copytree(PROJECT_ROOT / "src", Path(ctx) / "src")
        shutil.copytree(PROJECT_ROOT / "config", Path(ctx) / "config")

        # Copy admin dist directories
        for name, spa_dir in ADMIN_SPAS:
            dist_src = spa_dir / "dist"
            dist_dst = Path(ctx) / "admin" / name / "dist"
            if dist_src.exists():
                shutil.copytree(dist_src, dist_dst)
                log("INFO", f"  Copied admin/{name}/dist")
            else:
                detail = f"admin/{name}/dist missing — cannot proceed"
                log("FAIL", f"  {detail}")
                shutil.rmtree(ctx, ignore_errors=True)
                return PhaseResult(6, "Create Build Context", "FAIL", time.time() - t0, detail), ""

        # Copy widget dist
        widget_dist = WIDGET_DIR / "dist"
        if widget_dist.exists():
            widget_dst = Path(ctx) / "widget" / "dist"
            widget_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(widget_dist, widget_dst)
            log("INFO", "  Copied widget/dist")
        else:
            detail = "widget/dist missing — cannot proceed"
            log("FAIL", f"  {detail}")
            shutil.rmtree(ctx, ignore_errors=True)
            return PhaseResult(6, "Create Build Context", "FAIL", time.time() - t0, detail), ""

        # Verify critical files
        missing = []
        for f in BUILD_CONTEXT_CRITICAL_FILES:
            if not (Path(ctx) / f).exists():
                missing.append(f)
        if missing:
            detail = f"Critical files missing from build context: {', '.join(missing)}"
            log("FAIL", f"  {detail}")
            shutil.rmtree(ctx, ignore_errors=True)
            return PhaseResult(6, "Create Build Context", "FAIL", time.time() - t0, detail), ""

        # Calculate context size
        total_size = sum(f.stat().st_size for f in Path(ctx).rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)
        log("INFO", f"  Build context: {size_mb:.1f} MB, {len(BUILD_CONTEXT_CRITICAL_FILES)} critical files verified")

    except Exception as e:
        detail = f"Build context creation failed: {e}"
        log("FAIL", f"  {detail}")
        shutil.rmtree(ctx, ignore_errors=True)
        return PhaseResult(6, "Create Build Context", "FAIL", time.time() - t0, detail), ""

    dt = time.time() - t0
    return PhaseResult(6, "Create Build Context", "PASS", dt), ctx


def phase_7_acr_build(args: argparse.Namespace, build_context: str) -> PhaseResult:
    """Build Docker image on ACR."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", f"  [DRY RUN] Would build {IMAGE_REPO}:{args.version} on ACR")
        return PhaseResult(7, "ACR Docker Build", "PASS", time.time() - t0, "dry-run")

    version = args.version
    log("INFO", f"  Building {IMAGE_REPO}:{version} on ACR (--no-logs)...")

    r = _run([
        "az", "acr", "build",
        "--registry", ACR_NAME,
        "--image", f"{IMAGE_REPO}:{version}",
        "--build-arg", f"BUILD_VERSION={version}",
        "--file", str(Path(build_context) / "Dockerfile"),
        "--no-logs",
        build_context,
    ], timeout=600)

    # Note: on Windows, az acr build may crash with UnicodeEncodeError
    # even when the build succeeds. Check ACR run status instead.
    log("INFO", "  Verifying ACR build status...")
    r2 = _run([
        "az", "acr", "task", "list-runs",
        "--registry", ACR_NAME,
        "--top", "1",
        "--query", "[0].status",
        "-o", "tsv",
    ])
    build_status = r2.stdout.strip()
    if build_status != "Succeeded":
        detail = f"ACR build status: {build_status} (expected 'Succeeded')"
        log("FAIL", f"  {detail}")
        return PhaseResult(7, "ACR Docker Build", "FAIL", time.time() - t0, detail)

    # Verify tag exists in registry
    log("INFO", "  Verifying image tag in ACR...")
    r3 = _run([
        "az", "acr", "repository", "show-tags",
        "--name", ACR_NAME,
        "--repository", IMAGE_REPO,
        "--query", f"[?@=='{version}']",
        "-o", "tsv",
    ])
    if r3.stdout.strip() != version:
        detail = f"Image tag {version} not found in ACR after build"
        log("FAIL", f"  {detail}")
        return PhaseResult(7, "ACR Docker Build", "FAIL", time.time() - t0, detail)

    # Get build ID for logging
    r4 = _run([
        "az", "acr", "task", "list-runs",
        "--registry", ACR_NAME,
        "--top", "1",
        "--query", "[0].runId",
        "-o", "tsv",
    ])
    build_id = r4.stdout.strip()
    log("PASS", f"  Image {IMAGE_REPO}:{version} built (run: {build_id})")

    dt = time.time() - t0
    return PhaseResult(7, "ACR Docker Build", "PASS", dt, f"run={build_id}")


def phase_8_deploy(args: argparse.Namespace) -> PhaseResult:
    """Deploy new image to target environment."""
    t0 = time.time()
    env_config = ENVIRONMENTS[args.env]
    container_app = env_config["container_app"]
    new_image = f"{ACR_LOGIN_SERVER}/{IMAGE_REPO}:{args.version}"

    if args.dry_run:
        log("INFO", f"  [DRY RUN] Would deploy {new_image} to {container_app}")
        return PhaseResult(9, "Deploy to Target", "PASS", time.time() - t0, "dry-run")

    log("INFO", f"  Deploying {new_image} to {container_app}...")
    r = _run([
        "az", "containerapp", "update",
        "--name", container_app,
        "--resource-group", RESOURCE_GROUP,
        "--image", new_image,
    ], timeout=120)

    if r.returncode != 0:
        detail = f"Container app update failed: {r.stderr.strip()[:300]}"
        log("FAIL", f"  {detail}")
        return PhaseResult(9, "Deploy to Target", "FAIL", time.time() - t0, detail)

    # Verify the deployed image
    r2 = _run([
        "az", "containerapp", "show",
        "--name", container_app,
        "--resource-group", RESOURCE_GROUP,
        "--query", "properties.template.containers[0].image",
        "-o", "tsv",
    ])
    deployed_image = r2.stdout.strip()
    if deployed_image != new_image:
        log("WARN", f"  Expected {new_image}, got {deployed_image} — may still be transitioning")

    log("PASS", f"  Deployed to {container_app}")
    dt = time.time() - t0
    return PhaseResult(9, "Deploy to Target", "PASS", dt)


def phase_10_startup_and_version(args: argparse.Namespace) -> PhaseResult:
    """Wait for healthy startup AND verify product_version matches deployed version."""
    t0 = time.time()
    env_config = ENVIRONMENTS[args.env]
    fqdn = env_config["fqdn"]
    expected_version = args.version.lstrip("v")

    if args.dry_run:
        log("INFO", f"  [DRY RUN] Would wait for https://{fqdn}/health (version={expected_version})")
        return PhaseResult(10, "Startup + Version Verify", "PASS", time.time() - t0, "dry-run")

    log("INFO", f"  Waiting up to {HEALTH_WAIT_SECONDS}s for /health (version={expected_version})...")
    elapsed = 0
    last_status = 0
    last_version = "?"

    while elapsed < HEALTH_WAIT_SECONDS:
        time.sleep(HEALTH_POLL_INTERVAL)
        elapsed += HEALTH_POLL_INTERVAL
        status, body, _ = api_call(fqdn, "/health", timeout=10)
        last_status = status
        if status == 200 and isinstance(body, dict):
            actual_version = body.get("product_version", "?")
            last_version = actual_version
            if actual_version == expected_version:
                log("PASS", f"  /health 200, product_version={actual_version} (matched after {elapsed}s)")
                return PhaseResult(10, "Startup + Version Verify", "PASS", time.time() - t0)
            else:
                log("INFO", f"  Waiting... [{elapsed}s] (200 but version={actual_version}, want {expected_version})")
        else:
            log("INFO", f"  Waiting... [{elapsed}s / {HEALTH_WAIT_SECONDS}s] (status={status})")

    # Final attempt
    status, body, _ = api_call(fqdn, "/health", timeout=10)
    if status == 200 and isinstance(body, dict):
        actual_version = body.get("product_version", "?")
        if actual_version == expected_version:
            return PhaseResult(10, "Startup + Version Verify", "PASS", time.time() - t0)
        detail = (f"Health 200 but product_version={actual_version}, expected={expected_version} "
                  f"-- old revision still active")
    else:
        detail = f"Not healthy after {HEALTH_WAIT_SECONDS}s (last status={last_status})"

    log("FAIL", f"  {detail}")
    return PhaseResult(10, "Startup + Version Verify", "FAIL", time.time() - t0, detail)


def phase_10a_pre_deploy_snapshot(args: argparse.Namespace) -> PhaseResult:
    """Capture pre-deploy snapshots for upgrade verification.

    Must run BEFORE deployment (Phase 8) to record pre-upgrade state.
    """
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would capture pre-deploy snapshots")
        return PhaseResult(8, "Pre-Deploy Snapshot", "PASS", time.time() - t0, "dry-run")

    script = PROJECT_ROOT / "scripts" / "upgrade_verification.py"
    env = args.env
    phase_name = "multi-a" if env == "staging" else "phase-a"

    log("INFO", f"  Capturing {phase_name} snapshots...")
    try:
        r = _run(
            [sys.executable, str(script), phase_name, "--env", env],
            cwd=PROJECT_ROOT,
            timeout=600,  # 10 min — rate limiting may slow this down
        )
    except subprocess.TimeoutExpired:
        detail = f"{phase_name} timed out after 600s"
        log("FAIL", f"  {detail}")
        return PhaseResult(8, "Pre-Deploy Snapshot", "FAIL", time.time() - t0, detail)

    if r.returncode != 0:
        detail = f"{phase_name} failed (exit={r.returncode}): {r.stderr.strip()[:200]}"
        log("FAIL", f"  {detail}")
        return PhaseResult(8, "Pre-Deploy Snapshot", "FAIL", time.time() - t0, detail)

    # Verify snapshot files were created
    results_dir = PROJECT_ROOT / "scripts" / "upgrade-results"
    if env == "staging":
        expected_files = [results_dir / "phase_a_staging-001.json",
                          results_dir / "phase_a_staging-002.json"]
    else:
        expected_files = [results_dir / "phase_a_remaker-digital-001.json"]

    missing = [str(f.name) for f in expected_files if not f.exists()]
    if missing:
        detail = f"Snapshot files not created: {', '.join(missing)}"
        log("FAIL", f"  {detail}")
        return PhaseResult(8, "Pre-Deploy Snapshot", "FAIL", time.time() - t0, detail)

    log("PASS", f"  {phase_name} snapshots saved ({len(expected_files)} tenants)")
    dt = time.time() - t0
    return PhaseResult(8, "Pre-Deploy Snapshot", "PASS", dt)


def phase_13_upgrade_verification(args: argparse.Namespace) -> PhaseResult:
    """Run post-deploy upgrade verification against snapshots from Phase 10.

    Compares current state to pre-deploy snapshots to verify no data loss.
    """
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would run upgrade verification")
        return PhaseResult(11, "Upgrade Verification", "PASS", time.time() - t0, "dry-run")

    script = PROJECT_ROOT / "scripts" / "upgrade_verification.py"
    env = args.env
    version_stripped = args.version.lstrip("v")
    phase_name = "multi-c" if env == "staging" else "phase-c"
    total_expected = 70 if env == "staging" else 35

    log("INFO", f"  Running {phase_name} --new-version {version_stripped}...")
    try:
        r = _run(
            [sys.executable, str(script), phase_name,
             "--env", env, "--new-version", version_stripped],
            cwd=PROJECT_ROOT,
            timeout=600,  # 10 min — rate limiting at 10 rpm means 70 calls ≈ 7 min
        )
    except subprocess.TimeoutExpired:
        detail = f"{phase_name} timed out after 600s (rate limiting may be too aggressive)"
        log("FAIL", f"  {detail}")
        return PhaseResult(11, "Upgrade Verification", "FAIL", time.time() - t0, detail)
    output = r.stdout + r.stderr

    # Parse PASS/FAIL counts from multi-tenant summary output
    # Format: "  staging-001              PASS  (35 pass, 0 fail)"
    total_pass = 0
    total_fail = 0
    for m in re.finditer(r"\((\d+)\s+pass,\s*(\d+)\s+fail\)", output):
        total_pass += int(m.group(1))
        total_fail += int(m.group(2))

    # Fallback: try uppercase format from individual assertions
    if total_pass == 0 and total_fail == 0:
        pass_matches = re.findall(r"(\d+)\s+PASS", output)
        fail_matches = re.findall(r"(\d+)\s+FAIL", output)
        if pass_matches:
            total_pass = sum(int(x) for x in pass_matches)
        if fail_matches:
            total_fail = sum(int(x) for x in fail_matches)

    dt = time.time() - t0
    extra = f"[{total_pass}/{total_expected}]"

    if r.returncode != 0 or total_fail > 0:
        detail = f"{total_pass} PASS, {total_fail} FAIL (expected {total_expected})"
        if r.returncode != 0 and total_pass == 0 and total_fail == 0:
            detail += f" — script exited {r.returncode}: {r.stderr.strip()[:200]}"
        log("FAIL", f"  Upgrade verification: {detail}")
        return PhaseResult(11, "Upgrade Verification", "FAIL", dt, detail, extra)

    log("PASS", f"  Upgrade verification: {total_pass}/{total_expected}")
    return PhaseResult(11, "Upgrade Verification", "PASS", dt, extra=extra)


def phase_14_config_pipeline(args: argparse.Namespace) -> PhaseResult:
    """Run config pipeline live E2E tests."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would run config pipeline tests")
        return PhaseResult(12, "Config Pipeline", "PASS", time.time() - t0, "dry-run")

    test_file = PROJECT_ROOT / "tests" / "security" / "test_config_pipeline_live.py"
    if not test_file.exists():
        log("WARN", "  Config pipeline test file not found — skipping")
        return PhaseResult(12, "Config Pipeline", "SKIP", time.time() - t0)

    log("INFO", "  Running config pipeline live tests...")
    env_vars = os.environ.copy()
    env_vars["DEPLOY_TARGET_ENV"] = args.env

    r = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-x", "-q", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=300,
        env=env_vars,
        errors="replace",
    )
    output = r.stdout + r.stderr

    # Parse results
    pass_match = re.search(r"(\d+)\s+passed", output)
    fail_match = re.search(r"(\d+)\s+failed", output)
    p = int(pass_match.group(1)) if pass_match else 0
    f = int(fail_match.group(1)) if fail_match else 0

    dt = time.time() - t0
    extra = f"[{p}/{p + f}]" if (p + f) > 0 else ""

    if r.returncode != 0 or f > 0:
        detail = f"{p} passed, {f} failed"
        log("FAIL", f"  Config pipeline: {detail}")
        return PhaseResult(12, "Config Pipeline", "FAIL", dt, detail, extra)

    log("PASS", f"  Config pipeline: {p} passed")
    return PhaseResult(12, "Config Pipeline", "PASS", dt, extra=extra)


# ---------------------------------------------------------------------------
# Helpers for two-track pipeline
# ---------------------------------------------------------------------------
_seed_credentials: dict[str, str] = {}


def _parse_seed_credentials(output: str) -> None:
    """Extract credentials from seed_tenant.py stdout."""
    # Widget key: "  Widget Key:        pk_live_..."
    m = re.search(r"Widget Key:\s+(pk_live_\S+)", output)
    if m:
        _seed_credentials["widget_key"] = m.group(1)
    # User API key: appears after "User API Keys:" block
    m = re.search(r"(ar_user_\S+)", output)
    if m:
        _seed_credentials["user_api_key"] = m.group(1)


def _parse_upgrade_output(output: str) -> tuple[int, int]:
    """Parse PASS/FAIL counts from upgrade_verification.py output.

    Returns (total_pass, total_fail).
    """
    total_pass = 0
    total_fail = 0
    # Multi-tenant summary: "  staging-001              PASS  (35 pass, 0 fail)"
    for m in re.finditer(r"\((\d+)\s+pass,\s*(\d+)\s+fail\)", output):
        total_pass += int(m.group(1))
        total_fail += int(m.group(2))
    # Fallback: uppercase format from individual assertions
    if total_pass == 0 and total_fail == 0:
        pass_matches = re.findall(r"(\d+)\s+PASS", output)
        fail_matches = re.findall(r"(\d+)\s+FAIL", output)
        if pass_matches:
            total_pass = sum(int(x) for x in pass_matches)
        if fail_matches:
            total_fail = sum(int(x) for x in fail_matches)
    return total_pass, total_fail


# ---------------------------------------------------------------------------
# Staging-only phases
# ---------------------------------------------------------------------------
def phase_13_seed_test_tenant(args: argparse.Namespace) -> PhaseResult:
    """Reset/create remaker-digital-001 on staging via seed_tenant.py."""
    t0 = time.time()
    if args.env != "staging":
        return PhaseResult(13, "Seed Test Tenant", "SKIP", time.time() - t0, "staging-only")
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would run seed_tenant.py --execute against staging")
        return PhaseResult(13, "Seed Test Tenant", "PASS", time.time() - t0, "dry-run")

    env_config = ENVIRONMENTS["staging"]
    seed_env = os.environ.copy()
    seed_env["SEED_TENANT_ID"] = "remaker-digital-001"
    seed_env["SEED_SHOP_DOMAIN"] = "blanco-9939.myshopify.com"
    seed_env["SEED_CUSTOMER_EMAIL"] = "mike@remakerdigital.com"
    seed_env["SEED_TIER"] = "professional"
    seed_env["SEED_BILLING_CHANNEL"] = "shopify"
    seed_env["SEED_FQDN"] = env_config["fqdn"]
    # Critical: staging uses a separate Cosmos database (agentred-staging)
    if "cosmos_db_database" in env_config:
        seed_env["COSMOS_DB_DATABASE"] = env_config["cosmos_db_database"]

    script = PROJECT_ROOT / "scripts" / "seed_tenant.py"
    log("INFO", "  Running seed_tenant.py --execute (creates/resets remaker-digital-001)...")

    r = _stream(
        [sys.executable, str(script), "--execute"],
        cwd=PROJECT_ROOT, timeout=300, env=seed_env,
        prefix="  [seed] ",
    )

    dt = time.time() - t0
    if r.returncode != 0:
        detail = f"seed_tenant.py exited {r.returncode}"
        log("FAIL", f"  {detail}")
        return PhaseResult(13, "Seed Test Tenant", "FAIL", dt, detail)

    # Parse credentials from seed output for Phase 14
    _parse_seed_credentials(r.stdout)
    if "user_api_key" not in _seed_credentials:
        detail = "No API key found in seed output -- credential parsing failed"
        log("FAIL", f"  {detail}")
        return PhaseResult(13, "Seed Test Tenant", "FAIL", dt, detail)

    log("PASS", f"  remaker-digital-001 seeded on staging (key={_seed_credentials['user_api_key'][:20]}...)")
    return PhaseResult(13, "Seed Test Tenant", "PASS", dt)


def phase_14_verify_initialized_state(args: argparse.Namespace) -> PhaseResult:
    """Verify remaker-digital-001 is in Initialized (draft) state after seed."""
    t0 = time.time()
    if args.env != "staging":
        return PhaseResult(14, "Verify Initialized State", "SKIP", time.time() - t0, "staging-only")
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would verify 6 Initialized-state assertions")
        return PhaseResult(14, "Verify Initialized State", "PASS", time.time() - t0, "dry-run")

    fqdn = ENVIRONMENTS["staging"]["fqdn"]
    api_key = _seed_credentials.get("user_api_key")
    if not api_key:
        detail = "No API key from seed output -- cannot verify"
        log("FAIL", f"  {detail}")
        return PhaseResult(14, "Verify Initialized State", "FAIL", time.time() - t0, detail)

    # Brief delay for Cosmos consistency
    log("INFO", "  Waiting 5s for Cosmos consistency...")
    time.sleep(5)

    failures = []
    passed = 0
    total = 6

    # I.1 -- Tenant lookup
    status, body, _ = api_call(fqdn, "/api/tenants/lookup", api_key)
    if status == 200 and isinstance(body, dict) and body.get("found"):
        log("PASS", "  I.1 Tenant lookup: found=true")
        passed += 1
    else:
        msg = f"I.1: lookup HTTP {status}"
        failures.append(msg)
        log("FAIL", f"  {msg}")

    # I.2 + I.3 + I.4 -- Activation status (single API call)
    # Replaces separate /api/admin/preferences (which doesn't exist) with
    # the activation-status endpoint that fully describes Initialized state.
    status, body, _ = api_call(fqdn, "/api/config/activation-status", api_key)
    if status == 200 and isinstance(body, dict):
        # I.2: Not yet configured (mandatory fields incomplete)
        is_configured = body.get("isConfigured", body.get("is_configured"))
        if not is_configured:
            log("PASS", "  I.2 Not configured: isConfigured=false")
            passed += 1
        else:
            msg = f"I.2: isConfigured={is_configured}, expected false"
            failures.append(msg)
            log("FAIL", f"  {msg}")

        # I.3: Never activated (active_version == 0)
        active_ver = body.get("activeVersion", body.get("active_version", -1))
        if active_ver == 0:
            log("PASS", "  I.3 Never activated: activeVersion=0")
            passed += 1
        else:
            msg = f"I.3: activeVersion={active_ver}, expected 0"
            failures.append(msg)
            log("FAIL", f"  {msg}")

        # I.4: Not active
        is_active = body.get("isActive", body.get("is_active"))
        if not is_active:
            log("PASS", "  I.4 Not activated: isActive=false")
            passed += 1
        else:
            msg = f"I.4: isActive={is_active}, expected false"
            failures.append(msg)
            log("FAIL", f"  {msg}")
    else:
        failures.append(f"I.2: activation-status HTTP {status}")
        failures.append("I.3: skipped (I.2 failed)")
        failures.append("I.4: skipped (I.2 failed)")
        log("FAIL", f"  I.2/I.3/I.4: activation-status HTTP {status}")

    # I.5 -- Exactly 1 superadmin
    status, body, _ = api_call(fqdn, "/api/admin/team", api_key)
    if status == 200:
        members = body if isinstance(body, list) else (body.get("members", []) if isinstance(body, dict) else [])
        superadmins = [m for m in members if m.get("role") == "superadmin"]
        if len(members) == 1 and len(superadmins) == 1:
            log("PASS", "  I.5 Team: 1 superadmin")
            passed += 1
        else:
            msg = f"I.5: {len(members)} members, {len(superadmins)} superadmins"
            failures.append(msg)
            log("FAIL", f"  {msg}")
    else:
        msg = f"I.5: GET /api/admin/team HTTP {status}"
        failures.append(msg)
        log("FAIL", f"  {msg}")

    # I.6 -- Zero conversations
    status, body, _ = api_call(fqdn, "/api/admin/conversations?limit=1", api_key)
    if status == 200 and isinstance(body, dict):
        total_count = body.get("totalCount", body.get("total_count", -1))
        if total_count == 0:
            log("PASS", "  I.6 Conversations: 0")
            passed += 1
        else:
            msg = f"I.6: totalCount={total_count}, expected 0"
            failures.append(msg)
            log("FAIL", f"  {msg}")
    else:
        msg = f"I.6: GET /api/admin/conversations HTTP {status}"
        failures.append(msg)
        log("FAIL", f"  {msg}")

    dt = time.time() - t0
    extra = f"[{passed}/{total}]"
    if failures:
        detail = "; ".join(failures)
        log("FAIL", f"  Initialized state: {len(failures)} failure(s)")
        return PhaseResult(14, "Verify Initialized State", "FAIL", dt, detail, extra)

    log("PASS", f"  All {total} Initialized state assertions passed")
    return PhaseResult(14, "Verify Initialized State", "PASS", dt, extra=extra)


# ---------------------------------------------------------------------------
# Production-only phases
# ---------------------------------------------------------------------------
def phase_11_production_verification(args: argparse.Namespace) -> PhaseResult:
    """Production: upgrade verification + lightweight smoke (no mutations)."""
    t0 = time.time()
    if args.dry_run:
        log("INFO", "  [DRY RUN] Would run production verification (phase-c + smoke)")
        return PhaseResult(11, "Production Verification", "PASS", time.time() - t0, "dry-run")

    env_config = ENVIRONMENTS["production"]
    fqdn = env_config["fqdn"]
    api_key = env_config["api_key"]
    expected_version = args.version.lstrip("v")
    failures = []

    # Part 1: Upgrade verification (phase-c, 35 assertions)
    script = PROJECT_ROOT / "scripts" / "upgrade_verification.py"
    log("INFO", "  Running phase-c upgrade verification...")
    try:
        r = _stream(
            [sys.executable, str(script), "phase-c",
             "--env", "production", "--new-version", expected_version],
            cwd=PROJECT_ROOT, timeout=600, prefix="  [phase-c] ",
        )
    except Exception as e:
        failures.append(f"phase-c exception: {e}")
        r = None

    total_pass, total_fail = (0, 0)
    if r is not None:
        total_pass, total_fail = _parse_upgrade_output(r.stdout)
        if r.returncode != 0 or total_fail > 0:
            failures.append(f"phase-c: {total_pass} PASS, {total_fail} FAIL")

    # 65s rate limit cooldown
    log("INFO", "  ... 65s rate limit cooldown before smoke test ...")
    time.sleep(65)

    # Part 2: Lightweight smoke (read-only, NO mutations)
    log("INFO", "  Running lightweight smoke test...")

    # Smoke 1: /health + correct version
    status, body, hdrs = api_call(fqdn, "/health", timeout=10)
    pv = body.get("product_version", "?") if isinstance(body, dict) else "?"
    if status == 200 and pv == expected_version:
        log("PASS", f"  Smoke: /health 200, product_version={pv}")
    else:
        msg = f"smoke-health: HTTP {status}, product_version={pv}"
        failures.append(msg)
        log("FAIL", f"  {msg}")

    # Smoke 2: X-Product-Version header
    xpv = hdrs.get("x-product-version", "?") if isinstance(hdrs, dict) else "?"
    if xpv == expected_version:
        log("PASS", f"  Smoke: X-Product-Version header={xpv}")
    else:
        msg = f"smoke-header: X-Product-Version={xpv}, expected {expected_version}"
        failures.append(msg)
        log("FAIL", f"  {msg}")

    # Smoke 3: Tenant lookup (read-only)
    status, body, _ = api_call(fqdn, "/api/tenants/lookup", api_key)
    if status == 200 and isinstance(body, dict) and body.get("found"):
        log("PASS", "  Smoke: /api/tenants/lookup found=true")
    else:
        msg = f"smoke-lookup: HTTP {status}"
        failures.append(msg)
        log("FAIL", f"  {msg}")

    dt = time.time() - t0
    if failures:
        detail = "; ".join(failures)
        log("FAIL", f"  Production verification failed: {detail}")
        # Include rollback instructions
        log("WARN", "")
        log("WARN", "  PRODUCTION DEPLOYMENT VERIFICATION FAILED -- Manual action may be required:")
        log("WARN", f"  1. Check if failure is transient (rate limiting, cold start)")
        log("WARN", f"  2. If persistent, rollback:")
        log("WARN", f"     az containerapp update --name {env_config.get('container_app', '?')} "
                     f"--resource-group {RESOURCE_GROUP} --image <previous-image-tag>")
        log("WARN", "")
        return PhaseResult(11, "Production Verification", "FAIL", dt, detail, f"[{total_pass}/35]")

    log("PASS", f"  Production verification: {total_pass}/35 upgrade + 3/3 smoke")
    return PhaseResult(11, "Production Verification", "PASS", dt, extra=f"[{total_pass}/35]")


# ---------------------------------------------------------------------------
# DEFECT work item creation on failure
# ---------------------------------------------------------------------------
def _create_defect_work_item(results: list[PhaseResult], args: argparse.Namespace) -> str | None:
    """Create a DEFECT work item in the KB for the first failed phase.

    Delegates to the shared _defect_reporter module (SPEC-1617).
    """
    from scripts._defect_reporter import create_defect

    failed = [r for r in results if r.status == "FAIL"]
    if not failed:
        return None

    first_fail = failed[0]
    all_failures = "; ".join(f"Phase {r.phase} ({r.name}): {r.detail}" for r in failed)

    wi_id = create_defect(
        title=f"Deploy pipeline failure: Phase {first_fail.phase} ({first_fail.name})",
        description=(
            f"Automated deploy pipeline (SPEC-1615) failed during execution.\n\n"
            f"Environment: {args.env}\n"
            f"Version: {args.version}\n"
            f"Failed phases: {all_failures}\n\n"
            f"First failure: Phase {first_fail.phase} ({first_fail.name}): "
            f"{first_fail.detail}"
        ),
        source_spec_id="SPEC-1615",
        component="infrastructure_automation",
        changed_by="deploy-pipeline",
    )
    if wi_id:
        log("INFO", f"  Created DEFECT work item: {wi_id}")
    return wi_id


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------
def _safe_print(*args_p, **kwargs_p) -> None:
    """Print that silently ignores closed stdout (background tasks)."""
    try:
        print(*args_p, **kwargs_p)
    except (OSError, ValueError):
        pass


def _print_summary(results: list[PhaseResult], args: argparse.Namespace,
                   start_time: float, log_path: Path | None, defect_wi: str | None) -> None:
    """Print final summary report."""
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    all_passed = all(r.passed or r.status == "SKIP" for r in results)
    verdict = "SUCCESS" if all_passed else "FAILURE"

    _safe_print()
    _safe_print("=" * 55)
    _safe_print(f"  DEPLOY PIPELINE — {args.env} {args.version}")
    _safe_print(f"  Started: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    _safe_print("=" * 55)
    _safe_print()

    for r in results:
        dots = "." * (35 - len(r.name))
        extra = f"  {r.extra}" if r.extra else ""
        _safe_print(f"Phase {r.phase:2d}: {r.name} {dots} {r.status} ({r.duration:.1f}s){extra}")

    _safe_print()
    _safe_print("=" * 55)
    _safe_print(f"  RESULT: {verdict}")
    _safe_print(f"  Duration: {minutes}m {seconds}s")
    _safe_print(f"  Image: {ACR_LOGIN_SERVER}/{IMAGE_REPO}:{args.version}")
    env_config = ENVIRONMENTS.get(args.env, {})
    _safe_print(f"  Environment: {args.env} ({env_config.get('container_app', '?')})")
    if defect_wi:
        _safe_print(f"  Defect: {defect_wi}")
    if log_path:
        _safe_print(f"  Log: {log_path}")
    _safe_print("=" * 55)
    _safe_print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Automated Build/Deploy Pipeline (SPEC-1615) — Two-Track",
    )
    parser.add_argument("--env", required=True, choices=["staging", "production"],
                        help="Target environment (staging=comprehensive, production=safe)")
    parser.add_argument("--version", required=True,
                        help="Image version tag (e.g., v1.66.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate without executing destructive actions")
    args = parser.parse_args()

    # Validate version format
    if not re.match(r"^v\d+\.\d+\.\d+$", args.version):
        print(f"ERROR: Version must be in format vX.Y.Z (got: {args.version})")
        return 1

    start_time = time.time()
    results: list[PhaseResult] = []
    build_context = ""

    track = "STAGING (comprehensive)" if args.env == "staging" else "PRODUCTION (safe)"
    log("INFO", f"Deploy Pipeline starting: {args.env} {args.version} [{track}]")
    if args.dry_run:
        log("INFO", "*** DRY RUN MODE -- no destructive actions ***")

    # -----------------------------------------------------------------------
    # Shared build phases (0-7) — identical for both tracks, stop on failure
    # -----------------------------------------------------------------------
    build_phases = [
        phase_0_validate_environment,
        phase_1_protected_behaviors,
        phase_2_clear_vite_api_url,
        phase_3_build_artifacts,
        phase_4_freshness_gate,
        phase_5_restore_env_local,
    ]

    for phase_fn in build_phases:
        result = phase_fn(args)
        results.append(result)
        if not result.passed and result.status != "SKIP":
            break

    all_ok = all(r.passed for r in results)

    if all_ok:
        result, build_context = phase_6_create_build_context(args)
        results.append(result)
        all_ok = result.passed

    if all_ok:
        result = phase_7_acr_build(args, build_context)
        results.append(result)
        all_ok = result.passed
        if build_context and not args.dry_run:
            shutil.rmtree(build_context, ignore_errors=True)
            log("INFO", "  Build context cleaned up")

    # -----------------------------------------------------------------------
    # Deploy phases (8-10) — identical for both tracks, stop on failure
    # -----------------------------------------------------------------------
    if all_ok:
        # Phase 8: Pre-deploy snapshot
        result = phase_10a_pre_deploy_snapshot(args)
        results.append(result)
        all_ok = result.passed or result.status == "SKIP"

    if all_ok:
        # Phase 9: Deploy
        result = phase_8_deploy(args)
        results.append(result)
        all_ok = result.passed

    if all_ok:
        # Phase 10: Startup + version verification (MUST match deployed version)
        result = phase_10_startup_and_version(args)
        results.append(result)
        all_ok = result.passed

    # -----------------------------------------------------------------------
    # Post-deploy verification — DIVERGES by environment
    # -----------------------------------------------------------------------
    if all_ok and args.env == "staging":
        # STAGING TRACK: comprehensive verification
        # Phases 11-12 stop on failure; phases 13-14 continue to gather data

        # Phase 11: Upgrade verification (multi-c for staging-001, staging-002)
        result = phase_13_upgrade_verification(args)
        results.append(result)
        all_ok = result.passed or result.status == "SKIP"

        if all_ok:
            # Phase 12: Config pipeline tests
            result = phase_14_config_pipeline(args)
            results.append(result)
            # Continue even if config pipeline fails — gather seed data

        # 65s rate limit cooldown before seeding
        if not args.dry_run:
            log("INFO", "  ... 65s rate limit cooldown before seed ...")
            time.sleep(65)

        # Phase 13: Seed test tenant (remaker-digital-001)
        result = phase_13_seed_test_tenant(args)
        results.append(result)
        seed_ok = result.passed

        # Phase 14: Verify Initialized state
        if seed_ok:
            result = phase_14_verify_initialized_state(args)
            results.append(result)
        else:
            # Seed failed — skip initialized verification
            results.append(PhaseResult(14, "Verify Initialized State", "SKIP",
                                       0, "seed failed"))

    elif all_ok and args.env == "production":
        # PRODUCTION TRACK: safe verification (no mutations)

        # Phase 11: Combined upgrade verification + lightweight smoke
        result = phase_11_production_verification(args)
        results.append(result)

    # -----------------------------------------------------------------------
    # Create DEFECT work item if any phase failed
    # -----------------------------------------------------------------------
    defect_wi = None
    any_failed = any(r.status == "FAIL" for r in results)
    if any_failed:
        defect_wi = _create_defect_work_item(results, args)

    # Write log file
    log_path = _write_log_file(args.env)

    # Print summary
    _print_summary(results, args, start_time, log_path, defect_wi)

    return 0 if not any_failed else 1


if __name__ == "__main__":
    sys.exit(main())
