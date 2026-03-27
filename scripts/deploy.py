#!/usr/bin/env python3
"""Deploy a tagged container image to staging or production.

Usage:
    python scripts/deploy.py staging v1.95.6
    python scripts/deploy.py production v1.95.6 --confirm

For staging, also deploys the test host container (same tag by default).
Use --test-host-tag to specify a different test host tag.

Exit codes:
    0 - Deployment succeeded and version verified
    1 - Deployment failed or verification failed

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ACR_LOGIN_SERVER = "acragentredeastus.azurecr.io"
ACR_NAME = "acragentredeastus"
RESOURCE_GROUP = "Agent-Red"

CONTAINER_APPS = {
    "staging": "agent-red-staging",
    "production": "agent-red-api-gateway",
}
TEST_HOST_APPS = {
    "staging": "agent-red-test-host",
    "production": "agent-red-test-host-prod",
}

# ADR-002: Per-agent containers. Deployed alongside the gateway.
# Maps ACR repo name → Azure Container App name.
AGENT_CONTAINER_APPS: dict[str, str] = {
    "agent-intent-classifier": "agent-red-intent-classifier",
    "agent-knowledge-retrieval": "agent-red-knowledge-retrieval",
    "agent-response-generator": "agent-red-response-generator",
    "agent-escalation-handler": "agent-red-escalation",
    "agent-analytics-collector": "agent-red-analytics",
    "agent-critic-supervisor": "agent-red-critic-supervisor",
}

# Infrastructure containers (non-agent services supporting transport)
INFRA_CONTAINER_APPS: dict[str, str] = {
    "slim-gateway": "agent-red-slim",
    # NATS uses public image, managed by Terraform, not deploy.py
}

FQDNS = {
    "staging": "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    "production": "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
}

HEALTH_TIMEOUT_S = 120
HEALTH_POLL_S = 10

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_log_file = None


def _init_log() -> None:
    global _log_file
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    _log_file = open(log_dir / f"deploy-{ts}.log", "w", encoding="utf-8")


def _safe_print(msg: str) -> None:
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


def _run(cmd: str, timeout: int = 120) -> tuple[int, str]:
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


# ---------------------------------------------------------------------------
# Deployment functions
# ---------------------------------------------------------------------------


def verify_acr_tag(repo: str, tag: str) -> bool:
    """Check that an image tag exists in ACR before deploying."""
    cmd = (
        f'az acr repository show-tags --name {ACR_NAME} '
        f'--repository {repo} --query "[?@==\'{tag}\']" -o tsv'
    )
    code, output = _run(cmd, timeout=30)
    if code != 0:
        log(f"  WARNING: Could not verify ACR tag (az CLI issue)")
        return True  # proceed anyway — deploy will fail if image missing
    return tag in output


def deploy_container(app_name: str, image: str) -> bool:
    """Deploy a container image to Azure Container Apps."""
    cmd = (
        f"az containerapp update "
        f"--name {app_name} "
        f"--resource-group {RESOURCE_GROUP} "
        f"--image {image} "
        f"--output none"
    )
    log(f"  Deploying {image} → {app_name}...")
    code, output = _run(cmd, timeout=180)
    if code != 0:
        log(f"  ERROR: Deploy failed: {output}")
        return False
    log(f"  Deploy command completed.")
    return True


def wait_for_healthy(fqdn: str) -> bool:
    """Wait until the /ready endpoint returns 200."""
    url = f"https://{fqdn}/ready"
    start = time.time()

    log(f"  Waiting for healthy response from {fqdn}...")
    while True:
        elapsed = int(time.time() - start)
        if elapsed > HEALTH_TIMEOUT_S:
            log(f"  TIMEOUT: No healthy response after {elapsed}s")
            return False

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    log(f"  Healthy after {elapsed}s")
                    return True
        except Exception:
            pass

        time.sleep(HEALTH_POLL_S)


def verify_version(fqdn: str, expected: str, api_key: str | None = None) -> str | None:
    """Check X-Product-Version header. Returns actual version or None on error."""
    url = f"https://{fqdn}/ready"
    try:
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.headers.get("x-product-version")
    except Exception as e:
        log(f"  ERROR checking version: {e}")
        return None


def get_deployed_image(app_name: str) -> str | None:
    """Query the currently deployed image for a container app."""
    cmd = (
        f"az containerapp show --name {app_name} "
        f"--resource-group {RESOURCE_GROUP} "
        f'--query "properties.template.containers[0].image" -o tsv'
    )
    code, output = _run(cmd, timeout=30)
    if code == 0 and output:
        return output.strip()
    return None


def record_deployment_event(
    fqdn: str,
    environment: str,
    version: str,
    image: str,
    success: bool,
    duration_s: float,
) -> None:
    """POST a deployment audit event to the API (best-effort).

    Requires SPA_PLATFORM_ADMIN_KEY env var. Silently skips if not set.
    """
    api_key = os.environ.get("SPA_PLATFORM_ADMIN_KEY", "")
    if not api_key:
        log("  Skipping deployment event recording (SPA_PLATFORM_ADMIN_KEY not set)")
        return

    payload = {
        "event_type": "model.deployed",
        "environment": environment,
        "version": version,
        "image": image,
        "previous_image": "",
        "revision_name": "",
        "status": "succeeded" if success else "failed",
        "duration_s": round(duration_s, 1),
        "verification_pass": 1 if success else 0,
        "verification_fail": 0 if success else 1,
        "dry_run": False,
    }

    try:
        url = f"https://{fqdn}/api/superadmin/deployments/record"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            log(f"  Deployment event recorded ({resp.status})")
    except Exception as exc:
        log(f"  WARNING: Failed to record deployment event (non-fatal): {exc}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy container images.")
    parser.add_argument(
        "environment",
        choices=["staging", "production"],
        help="Target environment",
    )
    parser.add_argument("tag", help="Image tag to deploy (e.g., v1.95.6)")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required for production deployments",
    )
    parser.add_argument(
        "--test-host-tag",
        help="Test host image tag (staging only, defaults to same as tag)",
    )
    args = parser.parse_args()

    if not re.match(r"^v\d+\.\d+\.\d+$", args.tag):
        print(f"ERROR: Invalid tag format '{args.tag}'. Expected: v1.95.6")
        return 1

    # Production safety gate
    if args.environment == "production" and not args.confirm:
        print("ERROR: Production deployment requires --confirm flag.")
        print(f"  python scripts/deploy.py production {args.tag} --confirm")
        return 1

    _init_log()
    deploy_start = time.monotonic()

    log("Agent Red Deployment")
    log(f"  Environment: {args.environment}")
    log(f"  Tag: {args.tag}")
    log("")

    app_name = CONTAINER_APPS[args.environment]
    fqdn = FQDNS[args.environment]
    gw_image = f"{ACR_LOGIN_SERVER}/api-gateway:{args.tag}"
    expected_version = args.tag.lstrip("v")  # v1.95.6 → 1.95.6

    # 1. Verify image exists in ACR
    log("Verifying images in ACR...")
    if not verify_acr_tag("api-gateway", args.tag):
        log(f"  ERROR: api-gateway:{args.tag} not found in ACR.")
        log(f"  Run: python scripts/build.py {args.tag}")
        _close_log()
        return 1
    log(f"  api-gateway:{args.tag} — found")

    th_tag = args.test_host_tag or args.tag
    if not verify_acr_tag("test-host", th_tag):
        log(f"  WARNING: test-host:{th_tag} not found — skipping test host deploy")
    else:
        log(f"  test-host:{th_tag} — found")

    log("")

    # 2. Deploy API gateway
    log("Deploying API gateway...")
    if not deploy_container(app_name, gw_image):
        _close_log()
        return 1

    # 3. Deploy test host (both environments)
    th_app = TEST_HOST_APPS.get(args.environment)
    if th_app:
        th_tag = args.test_host_tag or args.tag
        th_image = f"{ACR_LOGIN_SERVER}/test-host:{th_tag}"
        log("")
        log(f"Deploying test host ({th_app})...")
        if not deploy_container(th_app, th_image):
            log("  WARNING: Test host deploy failed (non-fatal)")

    # 3b. Deploy agent containers (ADR-002: per-agent containers)
    log("")
    log("Deploying agent containers...")
    agent_failures = 0
    for repo, ca_name in AGENT_CONTAINER_APPS.items():
        agent_image = f"{ACR_LOGIN_SERVER}/{repo}:{args.tag}"
        if verify_acr_tag(repo, args.tag):
            if not deploy_container(ca_name, agent_image):
                log(f"  WARNING: {ca_name} deploy failed (non-fatal)")
                agent_failures += 1
        else:
            log(f"  SKIP: {repo}:{args.tag} not in ACR — build with: python scripts/build.py {args.tag}")
    if agent_failures:
        log(f"  {agent_failures} agent container(s) failed to deploy")
    else:
        log(f"  All {len(AGENT_CONTAINER_APPS)} agent containers deployed or skipped")

    # 3c. Deploy infrastructure containers (SLIM)
    for repo, ca_name in INFRA_CONTAINER_APPS.items():
        infra_image = f"{ACR_LOGIN_SERVER}/{repo}:{args.tag}"
        if verify_acr_tag(repo, args.tag):
            if not deploy_container(ca_name, infra_image):
                log(f"  WARNING: {ca_name} deploy failed (non-fatal)")
        else:
            log(f"  SKIP: {repo}:{args.tag} not in ACR")

    log("")

    # 4. Wait for healthy
    if not wait_for_healthy(fqdn):
        log("WARNING: Health check timed out — continuing with verification...")

    # 5. Verify version
    log("")
    log("Verifying deployment...")

    # Wait for new revision to take traffic (production rollout can take 60-90s)
    for attempt in range(6):
        wait = 15 if attempt == 0 else 20
        time.sleep(wait)
        actual = verify_version(fqdn, expected_version)
        if actual == expected_version:
            log(f"  X-Product-Version: {actual} ✅")
            break
        elapsed_wait = 15 + attempt * 20
        log(f"  X-Product-Version: {actual} (expected {expected_version}) — retry {attempt + 1}/6 [{elapsed_wait}s]")

    # 6. Show deployed image
    deployed = get_deployed_image(app_name)
    if deployed:
        log(f"  Deployed image: {deployed}")

    # 7. Record deployment event
    version_ok = actual == expected_version
    duration = time.monotonic() - deploy_start
    record_deployment_event(
        fqdn=fqdn,
        environment=args.environment,
        version=args.tag,
        image=gw_image,
        success=version_ok,
        duration_s=duration,
    )

    # Summary
    log("")
    log("=" * 50)
    icon = "✅" if version_ok else "⚠️"
    log(f"  {icon} {args.environment}: {actual or 'unknown'}")
    log(f"  URL: https://{fqdn}")
    log("=" * 50)

    _close_log()
    return 0 if version_ok else 1


if __name__ == "__main__":
    sys.exit(main())
