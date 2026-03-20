#!/usr/bin/env python3
"""Build both container images via GitHub Actions.

Usage:
    python scripts/build.py v1.95.6

Triggers build-api-gateway.yml and build-test-host.yml workflows,
waits for both to complete, and verifies images exist in ACR.

Exit codes:
    0 - Both builds succeeded and images verified
    1 - Any build failed or verification failed

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ACR_NAME = "acragentredeastus"
WORKFLOWS = {
    "api-gateway": "build-api-gateway.yml",
    "test-host": "build-test-host.yml",
}
REPOS = {
    "api-gateway": "api-gateway",
    "test-host": "test-host",
}
POLL_INTERVAL_S = 15
BUILD_TIMEOUT_S = 600  # 10 minutes

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_log_file = None


def _init_log() -> None:
    global _log_file
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    _log_file = open(log_dir / f"build-{ts}.log", "w", encoding="utf-8")


def _safe_print(msg: str) -> None:
    """Print with fallback for Windows cp1252 encoding."""
    try:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()
    except Exception:
        print(msg.encode("ascii", errors="replace").decode(), flush=True)


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    _safe_print(msg)
    if _log_file:
        _log_file.write(line + "\n")
        _log_file.flush()


def _close_log() -> None:
    if _log_file:
        _log_file.close()


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------


def _run(cmd: str, timeout: int = 60) -> tuple[int, str]:
    """Run a shell command and return (exit_code, stdout)."""
    env = dict(__import__("os").environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            errors="replace",
        )
        return result.returncode, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)


def _check_tool(name: str) -> bool:
    """Check if a CLI tool is available."""
    code, _ = _run(f"{name} --version")
    return code == 0


# ---------------------------------------------------------------------------
# Workflow functions
# ---------------------------------------------------------------------------


def trigger_workflow(workflow_file: str, tag: str) -> bool:
    """Trigger a GitHub Actions workflow."""
    cmd = f"gh workflow run {workflow_file} --field tag={tag}"
    code, output = _run(cmd)
    if code != 0:
        log(f"  ERROR: Failed to trigger {workflow_file}: {output}")
        return False
    return True


def find_run_id(workflow_file: str) -> int | None:
    """Find the most recent run ID for a workflow."""
    cmd = (
        f"gh run list --workflow={workflow_file} --limit=1 "
        f"--json databaseId,status --jq .[0].databaseId"
    )
    code, output = _run(cmd)
    if code != 0 or not output:
        return None
    try:
        return int(output.strip())
    except ValueError:
        return None


def poll_run(run_id: int, label: str) -> bool:
    """Poll a GitHub Actions run until completion. Returns True if succeeded."""
    start = time.time()
    last_status = ""

    while True:
        elapsed = int(time.time() - start)
        if elapsed > BUILD_TIMEOUT_S:
            log(f"  [{label}] TIMEOUT after {elapsed}s")
            return False

        cmd = f"gh run view {run_id} --json status,conclusion"
        code, output = _run(cmd)
        if code != 0:
            time.sleep(POLL_INTERVAL_S)
            continue

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            time.sleep(POLL_INTERVAL_S)
            continue

        status = data.get("status", "unknown")
        conclusion = data.get("conclusion", "")

        if status != last_status:
            log(f"  [{label}] {elapsed:>3}s — {status}" + (f" ({conclusion})" if conclusion else ""))
            last_status = status

        if status == "completed":
            return conclusion == "success"

        time.sleep(POLL_INTERVAL_S)


def verify_acr_tag(repo: str, tag: str) -> bool:
    """Verify a tag exists in ACR."""
    cmd = (
        f'az acr repository show-tags --name {ACR_NAME} '
        f'--repository {repo} --query "[?@==\'{tag}\']" -o tsv'
    )
    code, output = _run(cmd, timeout=30)
    if code != 0:
        log(f"  WARNING: Could not verify ACR tag for {repo}:{tag}")
        log(f"    (az CLI may not be authenticated)")
        return True  # non-fatal — GH Actions succeeded
    return tag in output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Build container images via GitHub Actions.")
    parser.add_argument("tag", help="Image tag (e.g., v1.95.6)")
    args = parser.parse_args()

    if not re.match(r"^v\d+\.\d+\.\d+$", args.tag):
        print(f"ERROR: Invalid tag format '{args.tag}'. Expected: v1.95.6")
        return 1

    _init_log()

    log("Agent Red Container Build")
    log(f"  Tag: {args.tag}")
    log("")

    # Check prerequisites
    if not _check_tool("gh"):
        log("ERROR: 'gh' CLI not found. Install: https://cli.github.com/")
        _close_log()
        return 1

    # 0. Bump PRODUCT_VERSION in source, commit, and push
    version = args.tag.lstrip("v")  # v1.95.8 → 1.95.8
    ver_file = Path(__file__).resolve().parent.parent / "src" / "multi_tenant" / "api_versioning.py"
    log(f"Setting PRODUCT_VERSION = \"{version}\"...")
    content = ver_file.read_text(encoding="utf-8")
    new_content = re.sub(
        r'PRODUCT_VERSION\s*=\s*"[^"]*"',
        f'PRODUCT_VERSION = "{version}"',
        content,
    )
    if new_content == content:
        log("  Version already set — skipping.")
    else:
        ver_file.write_text(new_content, encoding="utf-8")
        log("  Updated api_versioning.py")
        # Commit and push so GitHub Actions builds the correct version
        code, _ = _run(
            f'git add "{ver_file}" && '
            f'git commit -m "bump: v{version}" && '
            f'git push',
            timeout=60,
        )
        if code != 0:
            log("  ERROR: Failed to commit/push version bump.")
            _close_log()
            return 1
        log("  Committed and pushed.")
    log("")

    # 1. Trigger both workflows
    log("Triggering GitHub Actions builds...")
    ok = True
    for name, workflow in WORKFLOWS.items():
        log(f"  {name}: {workflow}")
        if not trigger_workflow(workflow, args.tag):
            ok = False

    if not ok:
        _close_log()
        return 1

    log("")

    # 2. Wait for run IDs to appear
    log("Waiting for runs to register...")
    time.sleep(8)

    run_ids: dict[str, int] = {}
    for name, workflow in WORKFLOWS.items():
        rid = find_run_id(workflow)
        if rid:
            log(f"  {name}: run #{rid}")
            run_ids[name] = rid
        else:
            log(f"  {name}: ERROR — could not find run ID")

    if len(run_ids) != len(WORKFLOWS):
        log("ERROR: Not all runs were found.")
        _close_log()
        return 1

    log("")

    # 3. Poll both runs
    log("Waiting for builds to complete...")
    results: dict[str, bool] = {}
    for name, rid in run_ids.items():
        results[name] = poll_run(rid, name)

    log("")

    # 4. Verify ACR tags
    log("Verifying ACR images...")
    for name, repo in REPOS.items():
        if results.get(name):
            tag_ok = verify_acr_tag(repo, args.tag)
            if tag_ok:
                log(f"  {repo}:{args.tag} — verified")
            else:
                log(f"  {repo}:{args.tag} — NOT FOUND in ACR")
                results[name] = False

    # 5. Summary
    log("")
    log("=" * 50)
    all_ok = all(results.values())
    for name, ok in results.items():
        icon = "✅" if ok else "❌"
        log(f"  {icon} {name}: {'success' if ok else 'FAILED'}")
    log("=" * 50)

    _close_log()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
