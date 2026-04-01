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
    "agent-escalation-handler": "agent-red-escalation-handler",
    "agent-analytics-collector": "agent-red-analytics-collector",
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


def verify_container_health(app_name: str) -> dict:
    """Query the latest revision health for a container app.

    Returns dict with image, healthState, runningState for evidence.
    """
    cmd = (
        f"az containerapp revision list --name {app_name} "
        f"--resource-group {RESOURCE_GROUP} "
        f'--query "sort_by(@, &name) | [-1].{{image:properties.template.containers[0].image, '
        f'health:properties.healthState, running:properties.runningState, '
        f'name:name}}" -o json'
    )
    code, output = _run(cmd, timeout=30)
    if code == 0 and output:
        try:
            import json as _json
            return _json.loads(output.strip())
        except Exception:
            pass
    return {"image": None, "health": "Unknown", "running": "Unknown", "name": None}


def verify_all_containers(tag: str) -> bool:
    """Verify image, health, and running state for all deployed containers.

    Returns True if all containers are healthy with the expected tag.
    """
    all_ok = True
    expected_suffix = f":{tag}"

    containers = {
        **{f"api-gateway ({app})": app for app in [CONTAINER_APPS.get("staging", "")]},
        **{f"agent ({ca})": ca for ca in AGENT_CONTAINER_APPS.values()},
        **{f"infra ({ca})": ca for ca in INFRA_CONTAINER_APPS.values()},
    }

    log("Per-container verification:")
    for label, ca_name in containers.items():
        if not ca_name:
            continue
        info = verify_container_health(ca_name)
        image = info.get("image", "")
        health = info.get("health", "Unknown")
        running = info.get("running", "Unknown")
        tag_ok = expected_suffix in (image or "")
        health_ok = health == "Healthy"

        icon = "PASS" if (tag_ok and health_ok) else "FAIL"
        log(f"  [{icon}] {label}: {health}/{running} image={image}")

        if not (tag_ok and health_ok):
            all_ok = False

    return all_ok


def verify_chat_conversation(fqdn: str, environment: str) -> bool:
    """Post-deploy smoke test: send a real chat message and verify pipeline completion.

    Creates a conversation via the widget key, consumes the SSE stream, and
    checks that IC, KR, RG, and Critic stages all complete without errors.
    This catches issues that health checks miss: CriticPolicy not wired,
    Critic timeouts, NameErrors in post-Critic code paths, etc.

    Returns True if the pipeline completes successfully.
    """
    import json as _json

    # Need a widget key for the target environment
    widget_key = os.environ.get("DEPLOY_SMOKE_WIDGET_KEY", "")
    if not widget_key:
        # Try environment-specific keys
        if environment == "staging":
            widget_key = os.environ.get("STAGING_REMAKER_WIDGET_KEY", "")
        elif environment == "production":
            widget_key = os.environ.get("PRODUCTION_WIDGET_KEY", "")

    if not widget_key:
        log("  [FAIL] Chat smoke test: no widget key configured")
        log("    Set DEPLOY_SMOKE_WIDGET_KEY or STAGING_REMAKER_WIDGET_KEY env var")
        log("    To deploy without widget verification, pass --skip-widget-check")
        return False

    log("Chat conversation smoke test...")

    try:
        import httpx

        base = f"https://{fqdn}"
        headers = {
            "X-Widget-Key": widget_key,
            "Content-Type": "application/json",
            "X-Widget-Origin": "https://deploy-smoke-test.internal",
        }

        # 1. Create conversation
        resp = httpx.post(
            f"{base}/api/chat/conversations",
            headers=headers,
            json={"initial_message": "Hello"},
            timeout=30.0,
        )
        if resp.status_code != 201:
            log(f"  [FAIL] Conversation creation: {resp.status_code} {resp.text[:100]}")
            return False

        conv = resp.json()
        conv_id = conv["conversation_id"]
        stream_url = conv.get("stream_url", f"/api/chat/stream/{conv_id}")

        # 2. Consume SSE stream
        stream = httpx.get(
            f"{base}{stream_url}",
            headers={**headers, "Accept": "text/event-stream"},
            timeout=60.0,
        )
        if stream.status_code != 200:
            log(f"  [FAIL] Stream: {stream.status_code}")
            return False

        # 3. Parse events and check pipeline stages
        stages_completed = []
        has_tokens = False
        has_error = False
        has_done = False
        error_detail = ""

        for line in stream.text.split("\n"):
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload:
                continue
            try:
                evt = _json.loads(payload)
                if evt.get("stage") and evt.get("status") == "completed":
                    stages_completed.append(evt["stage"])
                elif "text" in evt and "sequence" in evt:
                    has_tokens = True
                elif evt.get("code"):
                    has_error = True
                    error_detail = f'{evt["code"]}: {evt.get("message", "")[:80]}'
                elif "conversation_id" in evt and "turn_count" in evt:
                    has_done = True
            except _json.JSONDecodeError:
                pass

        # 4. Verify pipeline completion
        required_stages = ["intent-classifier", "knowledge-retrieval",
                           "response-generator", "critic-supervisor"]
        missing = [s for s in required_stages if s not in stages_completed]

        if has_error:
            log(f"  [FAIL] Pipeline error: {error_detail}")
            return False

        if missing:
            log(f"  [FAIL] Missing stages: {missing}")
            log(f"    Completed: {stages_completed}")
            return False

        if not has_tokens:
            log("  [FAIL] No response tokens received")
            return False

        if not has_done:
            log("  [FAIL] Stream did not complete (no done event)")
            return False

        log(f"  [PASS] Pipeline: {' → '.join(stages_completed)}")
        log(f"    Tokens: yes, Done: yes, Errors: none")
        return True

    except Exception as exc:
        log(f"  [FAIL] Chat smoke test exception: {type(exc).__name__}: {exc}")
        return False


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
    parser.add_argument(
        "--skip-widget-check",
        action="store_true",
        help="Skip widget chat smoke test (requires explicit owner approval)",
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

    # 6b. Per-container health verification (Codex P2.1 remediation)
    log("")
    containers_ok = verify_all_containers(args.tag)
    if not containers_ok:
        log("WARNING: Not all containers are healthy with expected tag")

    # 7. Chat conversation smoke test (post-deploy readiness)
    #    Proves the pipeline works end-to-end, not just that containers are up.
    #    This is a STRICT GATE: deployment fails if the widget is non-functional.
    #    Only exception: --skip-widget-check with explicit owner approval.
    if args.skip_widget_check:
        log("")
        log("⚠️  Widget chat smoke test SKIPPED (--skip-widget-check)")
        log("    Deployment proceeding WITHOUT widget verification.")
        log("    This requires explicit owner approval.")
        chat_ok = True  # Explicit skip — owner responsibility
    else:
        chat_ok = verify_chat_conversation(fqdn, args.environment)

    # 8. Record deployment event
    version_ok = actual == expected_version
    all_ok = version_ok and chat_ok
    duration = time.monotonic() - deploy_start
    record_deployment_event(
        fqdn=fqdn,
        environment=args.environment,
        version=args.tag,
        image=gw_image,
        success=all_ok,
        duration_s=duration,
    )

    # Summary
    log("")
    log("=" * 50)
    icon = "✅" if all_ok else "❌"
    log(f"  {icon} {args.environment}: {actual or 'unknown'}")
    log(f"  URL: https://{fqdn}")
    if not version_ok:
        log(f"  ❌ Version mismatch: expected {expected_version}, got {actual}")
    if not chat_ok:
        log(f"  ❌ Widget chat smoke test FAILED — deployment is NOT verified")
    if args.skip_widget_check:
        log(f"  ⚠️  Widget check was SKIPPED (--skip-widget-check)")
    log("=" * 50)

    _close_log()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
