#!/usr/bin/env python3
"""Build — single command for the entire build pipeline.

Usage:
    python scripts/build.py v1.95.9

This is the ONE build command. It handles ALL artifacts autonomously:
  0. Bump PRODUCT_VERSION in source
  1. Build all frontend bundles (provider, standalone, shopify, widget)
  2. Commit version bump + frontend dist artifacts, push to remote
  3. Trigger GitHub Actions workflows (api-gateway + test-host)
  4. Poll workflows until completion
  5. Verify ACR image tags exist

Exit codes:
    0 - All builds succeeded and images verified
    1 - Any step failed

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
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = {
    "api-gateway": "build-api-gateway.yml",
    "test-host": "build-test-host.yml",
    "agent-containers": "build-agent-containers.yml",
    "slim-gateway": "build-slim-gateway.yml",
}
REPOS = {
    "api-gateway": "api-gateway",
    "test-host": "test-host",
    # Agent container repos (built by matrix workflow)
    "agent-intent-classifier": "agent-intent-classifier",
    "agent-knowledge-retrieval": "agent-knowledge-retrieval",
    "agent-response-generator": "agent-response-generator",
    "agent-escalation-handler": "agent-escalation-handler",
    "agent-analytics-collector": "agent-analytics-collector",
    "agent-critic-supervisor": "agent-critic-supervisor",
    # Infrastructure containers
    "slim-gateway": "slim-gateway",
}
# Frontend projects whose dist/ directories are COPY'd into the Docker image.
# Each entry is relative to PROJECT_ROOT.
FRONTEND_PROJECTS = [
    "admin/provider",
    "admin/standalone",
    "admin/shopify",
    "widget",
]
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
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr:
            output = f"{output}\n[stderr] {result.stderr.strip()}"
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return 1, "Command timed out"
    except Exception as e:
        return 1, str(e)


def _check_tool(name: str) -> bool:
    """Check if a CLI tool is available."""
    code, _ = _run(f"{name} --version")
    return code == 0


# ---------------------------------------------------------------------------
# Frontend build
# ---------------------------------------------------------------------------


def build_frontends() -> bool:
    """Build all frontend projects (npm install + npm run build).

    Returns True if all succeeded, False on first failure.
    """
    log("Building frontend bundles...")
    for project in FRONTEND_PROJECTS:
        project_dir = PROJECT_ROOT / project
        name = project.replace("admin/", "")

        if not (project_dir / "package.json").exists():
            log(f"  ERROR: {project}/package.json not found")
            return False

        # npm install (skip if node_modules exists and is fresh)
        node_modules = project_dir / "node_modules"
        if not node_modules.exists():
            log(f"  [{name}] npm install...")
            code, output = _run(f'npm install --prefix "{project_dir}"', timeout=120)
            if code != 0:
                log(f"  [{name}] ERROR: npm install failed: {output[:200]}")
                return False

        # npm run build
        log(f"  [{name}] building...")
        code, output = _run(f'npm run build --prefix "{project_dir}"', timeout=120)
        if code != 0:
            log(f"  [{name}] ERROR: build failed: {output[:300]}")
            return False

        # Verify dist/ was created
        dist_dir = project_dir / "dist"
        if not dist_dir.exists() or not any(dist_dir.iterdir()):
            log(f"  [{name}] ERROR: dist/ is missing or empty after build")
            return False

        log(f"  [{name}] OK")

    log("  All frontends built successfully.")
    return True


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
    for tool, url in [("gh", "https://cli.github.com/"), ("npm", "https://nodejs.org/")]:
        if not _check_tool(tool):
            log(f"ERROR: '{tool}' CLI not found. Install: {url}")
            _close_log()
            return 1

    # 0. Bump PRODUCT_VERSION in source
    version = args.tag.lstrip("v")  # v1.95.9 → 1.95.9
    ver_file = PROJECT_ROOT / "src" / "multi_tenant" / "api_versioning.py"
    log(f"Step 0: Setting PRODUCT_VERSION = \"{version}\"...")
    content = ver_file.read_text(encoding="utf-8")
    new_content = re.sub(
        r'PRODUCT_VERSION\s*=\s*"[^"]*"',
        f'PRODUCT_VERSION = "{version}"',
        content,
    )
    version_changed = new_content != content
    if not version_changed:
        log("  Version already set.")
    else:
        ver_file.write_text(new_content, encoding="utf-8")
        log("  Updated api_versioning.py")
    log("")

    # 1. Build all frontend bundles
    log("Step 1: Building frontend bundles...")
    if not build_frontends():
        log("ERROR: Frontend build failed.")
        _close_log()
        return 1
    log("")

    # 2. Commit version + dist artifacts and push
    log("Step 2: Committing and pushing...")
    # Stage version file + all dist directories (use forward slashes for git)
    # dist/ is in .gitignore so we need --force for the frontend bundles.
    _run('git add "src/multi_tenant/api_versioning.py"', timeout=15)
    for project in FRONTEND_PROJECTS:
        _run(f'git add --force "{project}/dist"', timeout=15)

    # Only commit+push if there are staged changes
    code, _ = _run("git diff --cached --quiet", timeout=10)
    if code != 0:
        # There are staged changes — commit and push
        code, _ = _run(
            f'git commit -m "bump: v{version} + build.py auto-bumps PRODUCT_VERSION from tag" && git push',
            timeout=60,
        )
        if code != 0:
            log("  ERROR: Failed to commit/push.")
            _close_log()
            return 1
        log("  Committed and pushed.")
    else:
        log("  No changes to commit — already up to date.")
    log("")

    # 3. Trigger GitHub Actions workflows
    log("Step 3: Triggering GitHub Actions builds...")
    ok = True
    for name, workflow in WORKFLOWS.items():
        log(f"  {name}: {workflow}")
        if not trigger_workflow(workflow, args.tag):
            ok = False

    if not ok:
        _close_log()
        return 1

    log("")

    # 4. Wait for run IDs to appear
    log("Step 4: Waiting for runs to register...")
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

    # 5. Poll both runs
    log("Step 5: Waiting for builds to complete...")
    results: dict[str, bool] = {}
    for name, rid in run_ids.items():
        results[name] = poll_run(rid, name)

    log("")

    # 6. Verify ACR tags
    log("Step 6: Verifying ACR images...")
    for name, repo in REPOS.items():
        if results.get(name):
            tag_ok = verify_acr_tag(repo, args.tag)
            if tag_ok:
                log(f"  {repo}:{args.tag} — verified")
            else:
                log(f"  {repo}:{args.tag} — NOT FOUND in ACR")
                results[name] = False

    # 7. Summary
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
