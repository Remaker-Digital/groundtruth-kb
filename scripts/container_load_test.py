"""Container agent load test & resilience runner.

Exercises the containerized agent pipeline (IC→KR→RG via HTTP Tier 2)
with progressive load while monitoring container health, replica counts,
and routing distribution.

Phases:
    1. Baseline     — 1 replica per container, progressive load
    2. Multi-replica — scale to 2 replicas, verify distribution
    3. Resilience    — kill a container under load, observe recovery

Usage:
    # Full test (all phases):
    python scripts/container_load_test.py --env staging

    # Single phase:
    python scripts/container_load_test.py --env staging --phase baseline
    python scripts/container_load_test.py --env staging --phase multi-replica
    python scripts/container_load_test.py --env staging --phase resilience

    # Quick smoke (5 users, 1 min):
    python scripts/container_load_test.py --env staging --quick

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STAGING_HOST = (
    "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"
)
STAGING_FQDN = (
    "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io"
)

RESOURCE_GROUP = "Agent-Red"

AGENT_CONTAINERS = [
    "agent-red-intent-classifier",
    "agent-red-knowledge-retrieval",
    "agent-red-response-generator",
    "agent-red-escalation-handler",
    "agent-red-analytics-collector",
    "agent-red-critic-supervisor",
    "agent-red-co-pilot",
]

# Pipeline-critical containers (IC→KR→RG) — these get extra scrutiny
PIPELINE_CONTAINERS = [
    "agent-red-intent-classifier",
    "agent-red-knowledge-retrieval",
    "agent-red-response-generator",
]

LOCUSTFILE = "tests/performance/locustfile.py"
OUTPUT_DIR = Path("tests/performance/container-load-results")

# Self-provisioning for fresh keys
SELF_PROVISION_ENDPOINT = "/api/superadmin/test/provision-tenant"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ContainerStatus:
    """Health status snapshot of a single container."""
    name: str
    replicas: int = 0
    ready_replicas: int = 0
    running: bool = False
    health_status: str = "unknown"


@dataclass
class PhaseResult:
    """Results from a single load test phase."""
    name: str
    description: str
    duration_s: float = 0.0
    total_requests: int = 0
    total_failures: int = 0
    error_rate_pct: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    max_response_time: float = 0.0
    rps: float = 0.0
    status_429_count: int = 0
    status_5xx_count: int = 0
    container_health: list[ContainerStatus] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Azure CLI helpers
# ---------------------------------------------------------------------------

def _az(cmd: list[str], timeout: int = 60) -> dict | list | str:
    """Run an Azure CLI command and return parsed JSON output."""
    full_cmd = ["az"] + cmd + ["-o", "json"]
    try:
        result = subprocess.run(
            full_cmd, capture_output=True, text=True, timeout=timeout,
            shell=True,  # Required on Windows — az is az.cmd
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        if not result.stdout.strip():
            return {}
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except json.JSONDecodeError:
        return result.stdout.strip()


def _get_container_replicas(container_name: str) -> int:
    """Get the current replica count for a container app."""
    result = _az([
        "containerapp", "show",
        "--name", container_name,
        "--resource-group", RESOURCE_GROUP,
        "--query", "properties.runningStatus.replicas",
    ])
    if isinstance(result, int):
        return result
    # Fallback: check template
    result = _az([
        "containerapp", "show",
        "--name", container_name,
        "--resource-group", RESOURCE_GROUP,
        "--query", "properties.template.scale",
    ])
    if isinstance(result, dict) and "minReplicas" in result:
        return result.get("minReplicas", 0)
    return 0


def _scale_container(container_name: str, min_replicas: int, max_replicas: int) -> bool:
    """Scale a container app to the specified replica range."""
    print(f"    Scaling {container_name}: min={min_replicas}, max={max_replicas}")
    result = _az([
        "containerapp", "update",
        "--name", container_name,
        "--resource-group", RESOURCE_GROUP,
        "--min-replicas", str(min_replicas),
        "--max-replicas", str(max_replicas),
    ], timeout=120)
    if isinstance(result, dict) and "error" in result:
        print(f"    [ERROR] Scale failed: {result['error'][:200]}")
        return False
    return True


def _get_container_logs(container_name: str, lines: int = 50) -> list[str]:
    """Get recent logs from a container app."""
    result = _az([
        "containerapp", "logs", "show",
        "--name", container_name,
        "--resource-group", RESOURCE_GROUP,
        "--tail", str(lines),
        "--type", "console",
    ], timeout=30)
    if isinstance(result, list):
        return [
            entry.get("Log", "")
            for entry in result
            if isinstance(entry, dict) and entry.get("Log")
        ]
    if isinstance(result, str):
        return result.strip().split("\n")
    return []


def _get_all_container_status() -> list[ContainerStatus]:
    """Get health status of all agent containers."""
    statuses = []
    for name in AGENT_CONTAINERS:
        status = ContainerStatus(name=name)
        show = _az([
            "containerapp", "show",
            "--name", name,
            "--resource-group", RESOURCE_GROUP,
        ])
        if isinstance(show, dict) and "error" not in show:
            props = show.get("properties", {}) or {}
            running_status = props.get("runningStatus", "")
            scale = (props.get("template", {}) or {}).get("scale", {}) or {}
            # runningStatus can be a string "Running" or a dict with replicas
            if isinstance(running_status, str):
                status.running = running_status.lower() == "running"
                status.replicas = scale.get("minReplicas", 0) if status.running else 0
            else:
                rs = running_status or {}
                status.replicas = rs.get("replicas", scale.get("minReplicas", 0))
                status.ready_replicas = rs.get("readyReplicas", 0)
                status.running = status.replicas > 0
            status.health_status = "healthy" if status.running else "stopped"
        statuses.append(status)
    return statuses


# ---------------------------------------------------------------------------
# Gateway health helpers
# ---------------------------------------------------------------------------

def _check_gateway_health(host: str) -> dict:
    """Check gateway /health and /ready endpoints."""
    import urllib.request
    import urllib.error
    result = {}
    for endpoint in ["/health", "/ready"]:
        try:
            req = urllib.request.Request(f"{host}{endpoint}", method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                result[endpoint] = {
                    "status_code": resp.status,
                    "body": json.loads(resp.read().decode()),
                }
        except urllib.error.HTTPError as e:
            result[endpoint] = {
                "status_code": e.code,
                "body": json.loads(e.read().decode()) if e.readable() else {},
            }
        except Exception as e:
            result[endpoint] = {"status_code": 0, "error": str(e)}
    return result


def _self_provision(host: str, spa_key: str) -> dict | None:
    """Create an ephemeral test tenant via self-provisioning."""
    import urllib.request
    import urllib.error
    url = f"{host}{SELF_PROVISION_ENDPOINT}"
    payload = json.dumps({
        "merchantName": "LoadTest Container",
        "superadminEmail": f"loadtest-{int(time.time())}@test.agentredcx.com",
        "tier": "professional",
    }).encode()
    req = urllib.request.Request(
        url, data=payload, method="POST",
        headers={"X-API-Key": spa_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  [ERROR] Self-provision failed: {e.code} {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"  [ERROR] Self-provision failed: {e}")
        return None


def _expire_tenant(host: str, spa_key: str, tenant_id: str) -> None:
    """Expire an ephemeral test tenant via expiry patch."""
    import urllib.request
    import urllib.error
    from datetime import timezone
    now_iso = datetime.now(timezone.utc).isoformat()
    url = f"{host}/api/superadmin/tenants/{tenant_id}/expiry"
    payload = json.dumps({"expiresAt": now_iso}).encode()
    req = urllib.request.Request(
        url, data=payload, method="PATCH",
        headers={"X-API-Key": spa_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"  Expired: {tenant_id}")
    except Exception as e:
        print(f"  [WARN] Cleanup failed for {tenant_id}: {e}")


# ---------------------------------------------------------------------------
# Locust runner
# ---------------------------------------------------------------------------

def _run_locust(
    host: str,
    users: int,
    spawn_rate: int,
    duration: str,
    output_dir: Path,
    round_name: str,
    project_root: Path,
    api_key: str,
    widget_key: str,
    user_classes: list[str] | None = None,
) -> dict:
    """Run a Locust test round and return parsed results."""
    csv_prefix = str(output_dir / round_name)
    html_report = str(output_dir / f"{round_name}-report.html")

    cmd = [
        sys.executable, "-m", "locust",
        "-f", LOCUSTFILE,
        "--host", host,
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--run-time", duration,
        "--csv", csv_prefix,
        "--html", html_report,
        "--only-summary",
        "--loglevel", "WARNING",
    ]
    if user_classes:
        cmd.extend(user_classes)

    env = os.environ.copy()
    env["LOAD_TEST_API_KEY"] = api_key
    env["LOAD_TEST_WIDGET_KEY"] = widget_key

    start = time.time()
    proc = subprocess.run(
        cmd, cwd=str(project_root), env=env,
        capture_output=True, text=True, timeout=600,
    )
    elapsed = time.time() - start

    result = {
        "exit_code": proc.returncode,
        "duration_s": elapsed,
        "total_requests": 0,
        "total_failures": 0,
        "error_rate_pct": 0.0,
        "p50": 0.0, "p75": 0.0, "p90": 0.0,
        "p95": 0.0, "p99": 0.0,
        "max_response_time": 0.0,
        "rps": 0.0,
        "status_429_count": 0,
        "status_5xx_count": 0,
    }

    # Parse stats CSV
    stats_csv = f"{csv_prefix}_stats.csv"
    if os.path.exists(stats_csv):
        with open(stats_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("Name") == "Aggregated":
                    result["total_requests"] = int(row.get("Request Count", 0))
                    result["total_failures"] = int(row.get("Failure Count", 0))
                    result["p50"] = float(row.get("50%", 0))
                    result["p75"] = float(row.get("75%", 0))
                    result["p90"] = float(row.get("90%", 0))
                    result["p95"] = float(row.get("95%", 0))
                    result["p99"] = float(row.get("99%", 0))
                    result["max_response_time"] = float(row.get("Max Response Time", 0))
                    result["rps"] = float(row.get("Requests/s", 0))
                    total = result["total_requests"]
                    if total > 0:
                        result["error_rate_pct"] = result["total_failures"] / total * 100
                    break

    # Parse failures CSV
    failures_csv = f"{csv_prefix}_failures.csv"
    if os.path.exists(failures_csv):
        with open(failures_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                error = row.get("Error", "")
                count = int(row.get("Occurrences", 0))
                if "429" in error:
                    result["status_429_count"] += count
                elif any(str(c) in error for c in [500, 502, 503, 504]):
                    result["status_5xx_count"] += count

    return result


# ---------------------------------------------------------------------------
# Phase implementations
# ---------------------------------------------------------------------------

def phase_baseline(
    host: str, output_dir: Path, project_root: Path,
    api_key: str, widget_key: str, quick: bool = False,
) -> PhaseResult:
    """Phase 1: Baseline load test with 1 replica per container."""
    phase = PhaseResult(
        name="baseline",
        description="Progressive load with 1 replica per container (HTTP Tier 2)",
    )
    start = time.time()

    # Check container status
    print("\n  Checking container health...")
    phase.container_health = _get_all_container_status()
    for cs in phase.container_health:
        status_icon = "OK" if cs.running else "DOWN"
        print(f"    [{status_icon}] {cs.name}: {cs.replicas} replica(s)")

    # Run progressive rounds
    if quick:
        rounds = [("chat-5u", 5, 2, "1m")]
    else:
        rounds = [
            ("chat-10u", 10, 5, "2m"),
            ("chat-25u", 25, 5, "2m"),
            ("chat-50u", 50, 10, "2m"),
        ]

    all_results = []
    for round_name, users, spawn_rate, duration in rounds:
        print(f"\n  --- Round: {round_name} ({users} users, {duration}) ---")
        r = _run_locust(
            host, users, spawn_rate, duration, output_dir, f"baseline-{round_name}",
            project_root, api_key, widget_key,
        )
        all_results.append((round_name, r))
        _print_round(round_name, r)

        # Brief cooldown between rounds
        if round_name != rounds[-1][0]:
            print("  Cooling down (15s)...")
            time.sleep(15)

    # Aggregate last round as phase result
    if all_results:
        last = all_results[-1][1]
        phase.total_requests = sum(r["total_requests"] for _, r in all_results)
        phase.total_failures = sum(r["total_failures"] for _, r in all_results)
        phase.p50 = last["p50"]
        phase.p95 = last["p95"]
        phase.p99 = last["p99"]
        phase.max_response_time = last["max_response_time"]
        phase.rps = last["rps"]
        phase.status_429_count = sum(r["status_429_count"] for _, r in all_results)
        phase.status_5xx_count = sum(r["status_5xx_count"] for _, r in all_results)
        if phase.total_requests > 0:
            phase.error_rate_pct = phase.total_failures / phase.total_requests * 100

    # Observations
    for round_name, r in all_results:
        if r["p95"] > 2000:
            phase.observations.append(f"P95 SLA violation at {round_name}: {r['p95']:.0f}ms")
        if r["status_5xx_count"] > 0:
            phase.observations.append(f"5xx errors at {round_name}: {r['status_5xx_count']}")

    if not phase.observations:
        phase.observations.append("No SLA violations or errors detected")

    phase.duration_s = time.time() - start
    return phase


def phase_multi_replica(
    host: str, output_dir: Path, project_root: Path,
    api_key: str, widget_key: str, quick: bool = False,
) -> PhaseResult:
    """Phase 2: Scale to 2 replicas, run load test, verify distribution."""
    phase = PhaseResult(
        name="multi-replica",
        description="Scale pipeline containers to 2 replicas, verify load distribution",
    )
    start = time.time()

    # Scale pipeline containers to 2 replicas
    print("\n  Scaling pipeline containers to 2 replicas...")
    for container in PIPELINE_CONTAINERS:
        _scale_container(container, min_replicas=2, max_replicas=3)

    # Wait for replicas to become ready
    print("  Waiting 60s for replicas to warm up...")
    time.sleep(60)

    # Verify replica counts
    print("  Verifying replica counts...")
    phase.container_health = _get_all_container_status()
    for cs in phase.container_health:
        if cs.name in PIPELINE_CONTAINERS:
            print(f"    {cs.name}: {cs.replicas} replica(s) (target: 2)")
            if cs.replicas < 2:
                phase.observations.append(f"{cs.name} only has {cs.replicas} replica(s), expected 2")

    # Run load test with elevated traffic
    if quick:
        rounds = [("multi-10u", 10, 5, "1m")]
    else:
        rounds = [
            ("multi-25u", 25, 5, "2m"),
            ("multi-50u", 50, 10, "3m"),
        ]

    all_results = []
    for round_name, users, spawn_rate, duration in rounds:
        print(f"\n  --- Round: {round_name} ({users} users, {duration}) ---")
        r = _run_locust(
            host, users, spawn_rate, duration, output_dir, f"multi-{round_name}",
            project_root, api_key, widget_key,
        )
        all_results.append((round_name, r))
        _print_round(round_name, r)

        if round_name != rounds[-1][0]:
            print("  Cooling down (15s)...")
            time.sleep(15)

    # Check container logs for routing distribution
    print("\n  Checking container logs for routing distribution...")
    for container in PIPELINE_CONTAINERS:
        short_name = container.replace("agent-red-", "")

        # Use system logs which include replica names
        sys_logs = _az([
            "containerapp", "logs", "show",
            "--name", container,
            "--resource-group", RESOURCE_GROUP,
            "--tail", "200",
            "--type", "system",
        ], timeout=30)

        replica_names: set[str] = set()
        if isinstance(sys_logs, list):
            for entry in sys_logs:
                if isinstance(entry, dict):
                    # System logs include ContainerAppReplica_s field
                    replica = entry.get("ContainerAppReplica_s", "")
                    if replica:
                        replica_names.add(replica)

        # Also check console logs for request counts
        console_logs = _get_container_logs(container, lines=200)
        request_lines = sum(1 for l in console_logs if "POST" in l or "GET" in l or "INFO" in l)

        if replica_names:
            phase.observations.append(
                f"{short_name}: {len(replica_names)} replicas seen ({', '.join(sorted(replica_names)[:4])}), "
                f"{request_lines} log lines"
            )
            print(f"    {short_name}: {len(replica_names)} replicas — {sorted(replica_names)[:4]}")
        else:
            phase.observations.append(
                f"{short_name}: {request_lines} log lines (replica names unavailable via API)"
            )
            print(f"    {short_name}: {request_lines} log lines")

    # Aggregate results
    if all_results:
        last = all_results[-1][1]
        phase.total_requests = sum(r["total_requests"] for _, r in all_results)
        phase.total_failures = sum(r["total_failures"] for _, r in all_results)
        phase.p50 = last["p50"]
        phase.p95 = last["p95"]
        phase.p99 = last["p99"]
        phase.max_response_time = last["max_response_time"]
        phase.rps = last["rps"]
        phase.status_5xx_count = sum(r["status_5xx_count"] for _, r in all_results)
        if phase.total_requests > 0:
            phase.error_rate_pct = phase.total_failures / phase.total_requests * 100

    # Scale back to 1 replica
    print("\n  Scaling pipeline containers back to 1 replica...")
    for container in PIPELINE_CONTAINERS:
        _scale_container(container, min_replicas=1, max_replicas=3)

    phase.duration_s = time.time() - start
    return phase


def phase_resilience(
    host: str, output_dir: Path, project_root: Path,
    api_key: str, widget_key: str, quick: bool = False,
) -> PhaseResult:
    """Phase 3: Kill a container under load, observe recovery.

    Strategy:
      1. Start load test in background
      2. After 30s, scale intent-classifier to 0 replicas (simulates crash)
      3. Observe 503 errors accumulate
      4. After 30s, scale back to 1 replica
      5. Observe recovery — errors should stop
      6. Record timeline of failure/recovery
    """
    phase = PhaseResult(
        name="resilience",
        description="Kill intent-classifier during load, observe failure and recovery",
    )
    start = time.time()

    # Target container for failure injection
    target = "agent-red-intent-classifier"
    target_short = "intent-classifier"

    # Pre-check: verify target is running
    print(f"\n  Pre-check: verifying {target_short} is running...")
    statuses = _get_all_container_status()
    phase.container_health = statuses
    target_status = next((s for s in statuses if s.name == target), None)
    if target_status and not target_status.running:
        print(f"  [WARN] {target_short} is NOT running — scaling to 1 first")
        _scale_container(target, min_replicas=1, max_replicas=3)
        print("  Waiting 30s for container to start...")
        time.sleep(30)

    # Start Locust in background (longer duration to span failure + recovery)
    duration = "2m" if quick else "4m"
    users = 10 if quick else 25
    print(f"\n  Starting load test: {users} users, {duration}")
    print("  Load test runs in background while we inject failure...")

    csv_prefix = str(output_dir / "resilience")
    html_report = str(output_dir / "resilience-report.html")

    env = os.environ.copy()
    env["LOAD_TEST_API_KEY"] = api_key
    env["LOAD_TEST_WIDGET_KEY"] = widget_key

    locust_cmd = [
        sys.executable, "-m", "locust",
        "-f", LOCUSTFILE,
        "--host", host,
        "--headless",
        "-u", str(users),
        "-r", "5",
        "--run-time", duration,
        "--csv", csv_prefix,
        "--html", html_report,
        "--only-summary",
        "--loglevel", "WARNING",
    ]

    locust_proc = subprocess.Popen(
        locust_cmd, cwd=str(project_root), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    timeline = []

    # Phase 3a: Let traffic stabilize (30s)
    print("  [T+0s]   Traffic stabilizing...")
    time.sleep(30)
    timeline.append(("T+30s", "Traffic stabilized"))

    # Phase 3b: Kill the container by deactivating its revision
    print(f"  [T+30s]  KILLING {target_short} (deactivate revision)...")
    # Get current active revision
    rev = _az([
        "containerapp", "revision", "list",
        "--name", target,
        "--resource-group", RESOURCE_GROUP,
        "--query", "[?properties.active].name | [0]",
    ])
    if isinstance(rev, str) and rev:
        _az([
            "containerapp", "revision", "deactivate",
            "--name", target,
            "--resource-group", RESOURCE_GROUP,
            "--revision", rev,
        ], timeout=120)
        timeline.append(("T+30s", f"Deactivated revision {rev}"))
    else:
        # Fallback: scale min=0/max=1 — container may stay at 1 but at least tests the path
        _scale_container(target, min_replicas=0, max_replicas=1)
        rev = None
        timeline.append(("T+30s", f"Scaled {target_short} to min=0, max=1"))

    # Phase 3c: Observe failure (30-60s depending on quick mode)
    failure_window = 30 if quick else 45
    print(f"  [T+30s]  Observing failure for {failure_window}s...")

    # Sample gateway health during failure
    for i in range(0, failure_window, 10):
        time.sleep(10)
        health = _check_gateway_health(host)
        ready_code = health.get("/ready", {}).get("status_code", 0)
        health_code = health.get("/health", {}).get("status_code", 0)
        t = 30 + i + 10
        state = f"health={health_code}, ready={ready_code}"
        print(f"  [T+{t}s]  Gateway: {state}")
        timeline.append((f"T+{t}s", f"Gateway: {state}"))

    # Phase 3d: Restore the container
    restore_time = 30 + failure_window
    print(f"  [T+{restore_time}s] RESTORING {target_short}...")
    if rev:
        _az([
            "containerapp", "revision", "activate",
            "--name", target,
            "--resource-group", RESOURCE_GROUP,
            "--revision", rev,
        ], timeout=120)
        timeline.append((f"T+{restore_time}s", f"Reactivated revision {rev}"))
    _scale_container(target, min_replicas=1, max_replicas=3)
    timeline.append((f"T+{restore_time}s", f"Scaled {target_short} to min=1, max=3"))

    # Phase 3e: Wait for recovery and observe
    recovery_window = 30 if quick else 60
    print(f"  [T+{restore_time}s] Waiting {recovery_window}s for recovery...")

    for i in range(0, recovery_window, 15):
        time.sleep(15)
        health = _check_gateway_health(host)
        ready_code = health.get("/ready", {}).get("status_code", 0)
        health_code = health.get("/health", {}).get("status_code", 0)
        t = restore_time + i + 15
        state = f"health={health_code}, ready={ready_code}"
        print(f"  [T+{t}s]  Gateway: {state}")
        timeline.append((f"T+{t}s", f"Gateway: {state}"))

    # Wait for Locust to finish
    print("\n  Waiting for load test to complete...")
    try:
        locust_proc.wait(timeout=180)
    except subprocess.TimeoutExpired:
        locust_proc.kill()

    # Parse results
    stats_csv = f"{csv_prefix}_stats.csv"
    if os.path.exists(stats_csv):
        with open(stats_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("Name") == "Aggregated":
                    phase.total_requests = int(row.get("Request Count", 0))
                    phase.total_failures = int(row.get("Failure Count", 0))
                    phase.p50 = float(row.get("50%", 0))
                    phase.p95 = float(row.get("95%", 0))
                    phase.p99 = float(row.get("99%", 0))
                    phase.max_response_time = float(row.get("Max Response Time", 0))
                    phase.rps = float(row.get("Requests/s", 0))
                    if phase.total_requests > 0:
                        phase.error_rate_pct = (
                            phase.total_failures / phase.total_requests * 100
                        )
                    break

    failures_csv = f"{csv_prefix}_failures.csv"
    if os.path.exists(failures_csv):
        with open(failures_csv, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                error = row.get("Error", "")
                count = int(row.get("Occurrences", 0))
                if "429" in error:
                    phase.status_429_count += count
                elif any(str(c) in error for c in [500, 502, 503, 504]):
                    phase.status_5xx_count += count

    # Record timeline as observations
    for ts, event in timeline:
        phase.observations.append(f"[{ts}] {event}")

    # Final health check
    final_statuses = _get_all_container_status()
    target_final = next((s for s in final_statuses if s.name == target), None)
    if target_final and target_final.running:
        phase.observations.append(f"RECOVERY: {target_short} is running ({target_final.replicas} replicas)")
    else:
        phase.observations.append(f"RECOVERY INCOMPLETE: {target_short} may still be starting")

    phase.duration_s = time.time() - start
    return phase


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _print_round(name: str, r: dict) -> None:
    """Print compact round summary."""
    print(f"    Requests: {r['total_requests']:,}  "
          f"Failures: {r['total_failures']:,} ({r['error_rate_pct']:.1f}%)  "
          f"RPS: {r['rps']:.1f}")
    print(f"    P50: {r['p50']:.0f}ms  P95: {r['p95']:.0f}ms  "
          f"P99: {r['p99']:.0f}ms  Max: {r['max_response_time']:.0f}ms")
    if r["status_429_count"]:
        print(f"    429s: {r['status_429_count']}")
    if r["status_5xx_count"]:
        print(f"    5xx:  {r['status_5xx_count']}")


def _print_final_report(phases: list[PhaseResult]) -> str:
    """Print and return the final report."""
    lines = []
    lines.append("")
    lines.append("=" * 80)
    lines.append("  CONTAINER AGENT LOAD TEST — FINAL REPORT")
    lines.append("=" * 80)

    for phase in phases:
        lines.append("")
        lines.append(f"  Phase: {phase.name}")
        lines.append(f"  {phase.description}")
        lines.append(f"  Duration: {phase.duration_s:.0f}s")
        lines.append(f"  Requests: {phase.total_requests:,}  "
                     f"Failures: {phase.total_failures:,} ({phase.error_rate_pct:.1f}%)")
        lines.append(f"  P50: {phase.p50:.0f}ms  P95: {phase.p95:.0f}ms  "
                     f"P99: {phase.p99:.0f}ms  Max: {phase.max_response_time:.0f}ms")
        lines.append(f"  RPS: {phase.rps:.1f}  "
                     f"429s: {phase.status_429_count}  5xx: {phase.status_5xx_count}")

        if phase.container_health:
            lines.append("  Containers:")
            for cs in phase.container_health:
                icon = "OK" if cs.running else "DOWN"
                lines.append(f"    [{icon}] {cs.name}: {cs.replicas} replica(s)")

        if phase.observations:
            lines.append("  Observations:")
            for obs in phase.observations:
                lines.append(f"    - {obs}")

        lines.append("  " + "-" * 76)

    # Verdict
    lines.append("")
    total_5xx = sum(p.status_5xx_count for p in phases if p.name != "resilience")
    max_p95 = max((p.p95 for p in phases), default=0)
    verdict = "PASS" if total_5xx == 0 and max_p95 < 2000 else "REVIEW"
    lines.append(f"  VERDICT: {verdict}")
    if total_5xx > 0:
        lines.append(f"  [!] {total_5xx} 5xx errors outside resilience phase")
    if max_p95 > 2000:
        lines.append(f"  [!] P95 SLA violation: {max_p95:.0f}ms > 2,000ms")

    lines.append("=" * 80)

    output = "\n".join(lines)
    print(output)
    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run container agent load tests."""
    parser = argparse.ArgumentParser(
        description="Container agent load test & resilience runner"
    )
    parser.add_argument(
        "--env", choices=["staging"], default="staging",
        help="Target environment (default: staging)",
    )
    parser.add_argument(
        "--phase", choices=["baseline", "multi-replica", "resilience", "all"],
        default="all", help="Which phase to run (default: all)",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick smoke test (reduced users and duration)",
    )
    parser.add_argument(
        "--spa-key", help="SPA platform admin key for self-provisioning",
    )
    args = parser.parse_args()

    host = STAGING_HOST
    project_root = Path(__file__).resolve().parent.parent

    # Load .env.local for SPA key
    env_local = project_root / ".env.local"
    if env_local.exists():
        with open(env_local, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())

    spa_key = (
        args.spa_key
        or os.environ.get("STAGING_SPA_KEY")
        or os.environ.get("SPA_PLATFORM_ADMIN_KEY")
        or "ar_spa_plat_ukgY1GK594QUxICKJfIXFWiNrWxnkhvB"  # staging default
    )

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = OUTPUT_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'#' * 70}")
    print(f"  CONTAINER AGENT LOAD TEST")
    print(f"  Host:    {host}")
    print(f"  Phase:   {args.phase}")
    print(f"  Quick:   {args.quick}")
    print(f"  Output:  {run_dir}")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"{'#' * 70}")

    # Pre-check: gateway health
    print("\n  Pre-check: gateway health...")
    health = _check_gateway_health(host)
    h_code = health.get("/health", {}).get("status_code", 0)
    r_code = health.get("/ready", {}).get("status_code", 0)
    print(f"  /health: {h_code}  /ready: {r_code}")
    if h_code != 200:
        print("  [FATAL] Gateway not healthy. Aborting.")
        sys.exit(1)

    # Self-provision a test tenant
    print("\n  Self-provisioning ephemeral test tenant...")
    tenant = _self_provision(host, spa_key)
    if tenant:
        api_key = tenant.get("userApiKey", "") or tenant.get("user_api_key", "")
        widget_key = tenant.get("widgetKey", "") or tenant.get("widget_key", "")
        tenant_id = tenant.get("tenantId", "") or tenant.get("tenant_id", "")
        print(f"  Tenant: {tenant_id}")
        print(f"  API key: {api_key[:20]}...")
        print(f"  Widget key: {widget_key[:20]}...")
    else:
        # Fall back to staging credentials
        print("  [WARN] Self-provisioning failed, using staging credentials")
        api_key = os.environ.get(
            "STAGING_REMAKER_USER_KEY",
            "ar_user_rema_TwjRWmhZhjo3sX1sROYKcTHGVKfks9cu",
        )
        widget_key = os.environ.get(
            "STAGING_REMAKER_WIDGET_KEY",
            "pk_live_c79a2bd0b3d4_96f287f39e6a217f10dc76709297c169",
        )
        tenant_id = ""

    # Run phases
    phases: list[PhaseResult] = []
    phase_map = {
        "baseline": phase_baseline,
        "multi-replica": phase_multi_replica,
        "resilience": phase_resilience,
    }

    if args.phase == "all":
        phase_order = ["baseline", "multi-replica", "resilience"]
    else:
        phase_order = [args.phase]

    for phase_name in phase_order:
        print(f"\n{'=' * 70}")
        print(f"  PHASE: {phase_name.upper()}")
        print(f"{'=' * 70}")

        fn = phase_map[phase_name]
        try:
            result = fn(host, run_dir, project_root, api_key, widget_key, args.quick)
            phases.append(result)
        except Exception as e:
            print(f"\n  [ERROR] Phase {phase_name} failed: {e}")
            phases.append(PhaseResult(
                name=phase_name, description=f"FAILED: {e}",
                observations=[f"Exception: {e}"],
            ))

        # Cooldown between phases
        if phase_name != phase_order[-1]:
            print("\n  Phase cooldown (30s)...")
            time.sleep(30)

    # Final report
    report = _print_final_report(phases)

    # Save report
    report_file = run_dir / "REPORT.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"Container Agent Load Test Report\n")
        f.write(f"Host: {host}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Quick: {args.quick}\n\n")
        f.write(report)

    # Save structured results
    json_file = run_dir / "results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(
            [{
                "name": p.name,
                "description": p.description,
                "duration_s": p.duration_s,
                "total_requests": p.total_requests,
                "total_failures": p.total_failures,
                "error_rate_pct": p.error_rate_pct,
                "p50": p.p50, "p95": p.p95, "p99": p.p99,
                "max_response_time": p.max_response_time,
                "rps": p.rps,
                "status_429_count": p.status_429_count,
                "status_5xx_count": p.status_5xx_count,
                "observations": p.observations,
                "container_health": [
                    {"name": c.name, "replicas": c.replicas, "running": c.running}
                    for c in p.container_health
                ],
            } for p in phases],
            f, indent=2,
        )

    # Cleanup: expire ephemeral tenant
    if tenant_id:
        print(f"\n  Cleaning up ephemeral tenant {tenant_id}...")
        _expire_tenant(host, spa_key, tenant_id)

    print(f"\n  Report: {report_file}")
    print(f"  JSON:   {json_file}")
    print(f"  HTML:   {run_dir}/*-report.html")


if __name__ == "__main__":
    main()
