#!/usr/bin/env python3
"""Build Orchestrator — validates, builds, and tags ACR images.

Deterministic script that can be triggered by:
  - Claude Code (push hook or manual invocation)
  - SPA Provider Console (POST /api/superadmin/deployments/trigger → build phase)
  - CLI: python scripts/build_orchestrator.py --version v1.90.0 [--dry-run]

Steps:
  1. Validate Dockerfile exists and version format is correct
  2. Verify Azure CLI + ACR login
  3. Run az acr build (--no-logs for Windows safety)
  4. Verify image tag exists in registry
  5. Tag with git SHA (if available)
  6. Return structured JSON result

Exit codes:
    0 = SUCCESS
    1 = FAILURE

WI-1437 / SPEC-1825 / SPEC-1830
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ACR_NAME = "acragentredeastus"
ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
IMAGE_REPO = "api-gateway"
RESOURCE_GROUP = "Agent-Red"
DOCKERFILE = PROJECT_ROOT / "Dockerfile"

_log_lines: list[str] = []


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------
@dataclass
class BuildResult:
    """Structured result of a build orchestration run."""

    status: str = "pending"  # pending, running, succeeded, failed
    version: str = ""
    image: str = ""
    acr_run_id: str = ""
    git_sha: str = ""
    started_at: str = ""
    completed_at: str = ""
    duration_s: float = 0.0
    dry_run: bool = False
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


def _run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    """Run subprocess with real-time streaming."""
    r = stream_subprocess(cmd, cwd=str(PROJECT_ROOT), timeout=timeout, prefix="  ")
    return subprocess.CompletedProcess(
        args=cmd,
        returncode=r.returncode,
        stdout=r.stdout,
        stderr="",
    )


def _step(result: BuildResult, name: str, status: str, detail: str = "") -> None:
    """Record a step in the build result."""
    result.steps.append(
        {
            "name": name,
            "status": status,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )


# ---------------------------------------------------------------------------
# Build steps
# ---------------------------------------------------------------------------
def _get_git_sha() -> str:
    """Get current git short SHA, or empty string if unavailable."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short=8", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(PROJECT_ROOT),
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _validate_prerequisites(result: BuildResult, version: str, dry_run: bool) -> bool:
    """Step 1: Validate Dockerfile and version format."""
    _log("INFO", "Step 1: Validating prerequisites")

    if not re.match(r"^v\d+\.\d+\.\d+$", version):
        _step(result, "validate_version", "failed", f"Invalid format: {version}")
        result.error = f"Version must be vX.Y.Z (got: {version})"
        return False
    _step(result, "validate_version", "passed", version)

    if not DOCKERFILE.is_file():
        _step(result, "validate_dockerfile", "failed", "Dockerfile not found")
        result.error = "Dockerfile not found at project root"
        return False
    _step(result, "validate_dockerfile", "passed", str(DOCKERFILE))

    _log("PASS", "  Prerequisites validated")
    return True


def _verify_acr_access(result: BuildResult, dry_run: bool) -> bool:
    """Step 2: Verify Azure CLI and ACR access."""
    _log("INFO", "Step 2: Verifying ACR access")

    if dry_run:
        _step(result, "acr_access", "skipped", "dry-run")
        _log("INFO", "  [DRY RUN] Skipping ACR access check")
        return True

    r = _run(["az", "acr", "show", "--name", ACR_NAME, "--query", "name", "-o", "tsv"])
    if r.returncode != 0 or r.stdout.strip() != ACR_NAME:
        _step(result, "acr_access", "failed", f"Cannot access ACR: {r.stdout.strip()}")
        result.error = f"ACR access failed — ensure 'az login' is current"
        return False

    _step(result, "acr_access", "passed", ACR_NAME)
    _log("PASS", f"  ACR access verified: {ACR_NAME}")
    return True


def _acr_build(result: BuildResult, version: str, dry_run: bool) -> bool:
    """Step 3: Build Docker image on ACR."""
    _log("INFO", f"Step 3: Building {IMAGE_REPO}:{version} on ACR")
    full_image = f"{ACR_LOGIN_SERVER}/{IMAGE_REPO}:{version}"
    result.image = full_image

    if dry_run:
        _step(result, "acr_build", "skipped", "dry-run")
        _log("INFO", f"  [DRY RUN] Would build {full_image}")
        return True

    r = _run(
        [
            "az",
            "acr",
            "build",
            "--registry",
            ACR_NAME,
            "--image",
            f"{IMAGE_REPO}:{version}",
            "--build-arg",
            f"BUILD_VERSION={version}",
            "--file",
            "Dockerfile",
            "--no-logs",
            ".",
        ],
        timeout=600,
    )

    # az acr build may crash with encoding errors on Windows even on success.
    # Verify via ACR run status instead of exit code alone.
    _log("INFO", "  Verifying ACR build status...")
    r2 = _run(
        [
            "az",
            "acr",
            "task",
            "list-runs",
            "--registry",
            ACR_NAME,
            "--top",
            "1",
            "--query",
            "[0].status",
            "-o",
            "tsv",
        ]
    )
    build_status = r2.stdout.strip()
    if build_status != "Succeeded":
        _step(result, "acr_build", "failed", f"ACR status: {build_status}")
        result.error = f"ACR build status: {build_status} (expected 'Succeeded')"
        return False

    # Get run ID
    r3 = _run(
        [
            "az",
            "acr",
            "task",
            "list-runs",
            "--registry",
            ACR_NAME,
            "--top",
            "1",
            "--query",
            "[0].runId",
            "-o",
            "tsv",
        ]
    )
    result.acr_run_id = r3.stdout.strip()

    _step(result, "acr_build", "passed", f"run={result.acr_run_id}")
    _log("PASS", f"  Image built (run: {result.acr_run_id})")
    return True


def _verify_image_tag(result: BuildResult, version: str, dry_run: bool) -> bool:
    """Step 4: Verify the image tag exists in ACR.

    ACR tag propagation can lag a few seconds after ``az acr build``
    completes (especially when ``--no-logs`` suppresses streaming).
    We retry up to 3 times with a 5-second delay to handle this
    eventual-consistency window (WI-1439).
    """
    _log("INFO", f"Step 4: Verifying image tag {version} in ACR")

    if dry_run:
        _step(result, "verify_tag", "skipped", "dry-run")
        return True

    import time

    max_attempts = 3
    delay_seconds = 5

    for attempt in range(1, max_attempts + 1):
        r = _run(
            [
                "az",
                "acr",
                "repository",
                "show-tags",
                "--name",
                ACR_NAME,
                "--repository",
                IMAGE_REPO,
                "--query",
                f"[?@=='{version}']",
                "-o",
                "tsv",
            ]
        )
        if r.stdout.strip() == version:
            _step(result, "verify_tag", "passed", f"{version} (attempt {attempt})")
            _log("PASS", f"  Tag {version} verified in ACR (attempt {attempt}/{max_attempts})")
            return True

        if attempt < max_attempts:
            _log("INFO", f"  Tag not yet visible (attempt {attempt}/{max_attempts}), retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)

    _step(result, "verify_tag", "failed", f"Tag {version} not found after {max_attempts} attempts")
    result.error = (
        f"Image tag {version} not found in ACR after {max_attempts} attempts "
        f"(total wait: {(max_attempts - 1) * delay_seconds}s)"
    )
    return False


def _tag_with_sha(result: BuildResult, version: str, dry_run: bool) -> bool:
    """Step 5: Tag image with git SHA (best-effort, non-fatal)."""
    sha = _get_git_sha()
    if not sha:
        _log("INFO", "Step 5: No git SHA available, skipping SHA tag")
        _step(result, "sha_tag", "skipped", "no git SHA")
        return True

    result.git_sha = sha
    _log("INFO", f"Step 5: Tagging with git SHA {sha}")

    if dry_run:
        _step(result, "sha_tag", "skipped", f"dry-run (sha={sha})")
        return True

    # Import the manifest to create an alias tag
    r = _run(
        [
            "az",
            "acr",
            "import",
            "--name",
            ACR_NAME,
            "--source",
            f"{ACR_LOGIN_SERVER}/{IMAGE_REPO}:{version}",
            "--image",
            f"{IMAGE_REPO}:{sha}",
            "--force",
        ]
    )
    if r.returncode != 0:
        _log("WARN", f"  SHA tag failed (non-fatal): {r.stdout.strip()[:200]}")
        _step(result, "sha_tag", "warning", f"Tag failed: {r.stdout.strip()[:100]}")
    else:
        _step(result, "sha_tag", "passed", sha)
        _log("PASS", f"  Tagged {IMAGE_REPO}:{sha}")

    return True  # Always non-fatal


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------
def run_build(version: str, *, dry_run: bool = False) -> BuildResult:
    """Execute the full build orchestration pipeline.

    This is the primary programmatic entry point — called by the superadmin
    API and by the CLI.  Returns a structured BuildResult.
    """
    result = BuildResult(
        status="running",
        version=version,
        dry_run=dry_run,
        started_at=datetime.now(timezone.utc).isoformat(),
    )

    _log("INFO", f"Build Orchestrator starting: {IMAGE_REPO}:{version}" + (" [DRY RUN]" if dry_run else ""))

    steps = [
        lambda: _validate_prerequisites(result, version, dry_run),
        lambda: _verify_acr_access(result, dry_run),
        lambda: _acr_build(result, version, dry_run),
        lambda: _verify_image_tag(result, version, dry_run),
        lambda: _tag_with_sha(result, version, dry_run),
    ]

    for step_fn in steps:
        if not step_fn():
            result.status = "failed"
            break
    else:
        result.status = "succeeded"

    result.completed_at = datetime.now(timezone.utc).isoformat()
    result.duration_s = round(
        (datetime.fromisoformat(result.completed_at) - datetime.fromisoformat(result.started_at)).total_seconds(), 1
    )

    level = "PASS" if result.status == "succeeded" else "FAIL"
    _log(level, f"Build Orchestrator {result.status} in {result.duration_s}s")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Orchestrator — ACR build + tag + verify (SPEC-1825)",
    )
    parser.add_argument("--version", required=True, help="Image version tag (e.g., v1.90.0)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without executing builds")
    parser.add_argument("--json", action="store_true", help="Output result as JSON (for SPA integration)")
    args = parser.parse_args()

    result = run_build(args.version, dry_run=args.dry_run)

    if args.json:
        print(result.to_json())

    return 0 if result.status == "succeeded" else 1


if __name__ == "__main__":
    sys.exit(main())
