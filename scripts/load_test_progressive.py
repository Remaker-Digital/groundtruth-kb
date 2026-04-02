"""Progressive load test runner — finds infrastructure inflection points.

Runs Locust with stepped user counts against staging (or any target) and
produces a summary table of response-time percentiles, error rates, and
throughput at each load level.

Usage:
    # Full progressive test (health → mixed traffic, 10 → 200 users):
    python scripts/load_test_progressive.py --env staging

    # Quick smoke test (health only, 10 users):
    python scripts/load_test_progressive.py --env staging --quick

    # Custom host:
    python scripts/load_test_progressive.py --host http://localhost:8000

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

STAGING_HOST = os.environ.get("STAGING_URL", "")  # SPEC-0058: No hardcoded FQDNs

# Staging credentials from environment (SPEC-1845: no hardcoded keys)
STAGING_API_KEY = os.environ.get("STAGING_REMAKER_USER_KEY", "")
STAGING_WIDGET_KEY = os.environ.get("STAGING_REMAKER_WIDGET_KEY", "")

LOCUSTFILE = "tests/performance/locustfile.py"
OUTPUT_DIR = Path("tests/performance/progressive-results")


@dataclass
class RoundConfig:
    """Configuration for a single load test round."""

    name: str
    users: int
    spawn_rate: int
    duration: str  # e.g. "1m", "2m"
    user_classes: list[str] | None = None  # e.g. ["HealthProbeUser"]
    description: str = ""


@dataclass
class RoundResult:
    """Results from a single load test round."""

    name: str
    users: int
    total_requests: int = 0
    total_failures: int = 0
    error_rate_pct: float = 0.0
    avg_response_time: float = 0.0
    p50: float = 0.0
    p75: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    max_response_time: float = 0.0
    rps: float = 0.0
    status_429_count: int = 0
    status_5xx_count: int = 0
    raw_csv: str = ""


# ---------------------------------------------------------------------------
# Progressive test plans
# ---------------------------------------------------------------------------

FULL_PLAN: list[RoundConfig] = [
    # Phase 1: Infrastructure baseline (health endpoints only — no auth, no rate limit)
    RoundConfig(
        name="health-10u",
        users=10,
        spawn_rate=5,
        duration="1m",
        user_classes=["HealthProbeUser"],
        description="Health probes only — 10 users, infrastructure baseline",
    ),
    RoundConfig(
        name="health-50u",
        users=50,
        spawn_rate=10,
        duration="1m",
        user_classes=["HealthProbeUser"],
        description="Health probes only — 50 users, infrastructure stress",
    ),
    RoundConfig(
        name="health-100u",
        users=100,
        spawn_rate=20,
        duration="1m",
        user_classes=["HealthProbeUser"],
        description="Health probes only — 100 users, infrastructure peak",
    ),
    # Phase 2: Admin-only (Cosmos read throughput, hits rate limit)
    RoundConfig(
        name="admin-10u",
        users=10,
        spawn_rate=5,
        duration="2m",
        user_classes=["AdminUser"],
        description="Admin endpoints only — 10 users (Cosmos reads)",
    ),
    RoundConfig(
        name="admin-25u",
        users=25,
        spawn_rate=5,
        duration="2m",
        user_classes=["AdminUser"],
        description="Admin endpoints only — 25 users (moderate load)",
    ),
    # Phase 3: Full traffic mix with increasing load
    RoundConfig(
        name="mixed-10u",
        users=10,
        spawn_rate=5,
        duration="2m",
        description="Full traffic mix — 10 users (baseline)",
    ),
    RoundConfig(
        name="mixed-25u",
        users=25,
        spawn_rate=5,
        duration="2m",
        description="Full traffic mix — 25 users (moderate)",
    ),
    RoundConfig(
        name="mixed-50u",
        users=50,
        spawn_rate=10,
        duration="2m",
        description="Full traffic mix — 50 users (designed capacity)",
    ),
    RoundConfig(
        name="mixed-100u",
        users=100,
        spawn_rate=20,
        duration="2m",
        description="Full traffic mix — 100 users (stress)",
    ),
]

QUICK_PLAN: list[RoundConfig] = [
    RoundConfig(
        name="health-10u",
        users=10,
        spawn_rate=5,
        duration="1m",
        user_classes=["HealthProbeUser"],
        description="Health probes only — 10 users",
    ),
    RoundConfig(
        name="mixed-10u",
        users=10,
        spawn_rate=5,
        duration="1m",
        description="Full traffic mix — 10 users",
    ),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def _run_round(
    cfg: RoundConfig,
    host: str,
    output_dir: Path,
    project_root: Path,
) -> RoundResult:
    """Execute a single Locust round and parse results."""
    csv_prefix = str(output_dir / cfg.name)
    html_report = str(output_dir / f"{cfg.name}-report.html")

    cmd = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        LOCUSTFILE,
        "--host",
        host,
        "--headless",
        "-u",
        str(cfg.users),
        "-r",
        str(cfg.spawn_rate),
        "--run-time",
        cfg.duration,
        "--csv",
        csv_prefix,
        "--html",
        html_report,
        "--only-summary",
        "--loglevel",
        "WARNING",
    ]

    # Append specific user class names to run only those classes
    if cfg.user_classes:
        cmd.extend(cfg.user_classes)

    env = os.environ.copy()
    env["LOAD_TEST_API_KEY"] = STAGING_API_KEY
    env["LOAD_TEST_WIDGET_KEY"] = STAGING_WIDGET_KEY

    print(f"\n{'=' * 70}")
    print(f"  Round: {cfg.name}")
    print(f"  {cfg.description}")
    print(f"  Users: {cfg.users}, Spawn: {cfg.spawn_rate}/s, Duration: {cfg.duration}")
    print(f"{'=' * 70}")

    start_time = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(project_root),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,  # 10 min max per round
    )
    elapsed = time.time() - start_time

    print(f"  Completed in {elapsed:.1f}s (exit code {proc.returncode})")

    if proc.stderr:
        # Print warnings/errors but filter out noise
        for line in proc.stderr.strip().split("\n"):
            if line.strip() and "WARNING" not in line:
                print(f"  stderr: {line.strip()}")

    # Parse the CSV stats file
    result = RoundResult(name=cfg.name, users=cfg.users)
    stats_csv = f"{csv_prefix}_stats.csv"

    if os.path.exists(stats_csv):
        with open(stats_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Name") == "Aggregated":
                    result.total_requests = int(row.get("Request Count", 0))
                    result.total_failures = int(row.get("Failure Count", 0))
                    result.avg_response_time = float(
                        row.get("Average Response Time", 0)
                    )
                    result.p50 = float(row.get("50%", 0))
                    result.p75 = float(row.get("75%", 0))
                    result.p90 = float(row.get("90%", 0))
                    result.p95 = float(row.get("95%", 0))
                    result.p99 = float(row.get("99%", 0))
                    result.max_response_time = float(
                        row.get("Max Response Time", 0)
                    )
                    result.rps = float(
                        row.get("Requests/s", 0)
                    )

                    total = result.total_requests
                    if total > 0:
                        result.error_rate_pct = (
                            result.total_failures / total * 100
                        )
                    break

        result.raw_csv = stats_csv
    else:
        print(f"  [WARN] No stats CSV found at {stats_csv}")

    # Parse failures CSV for status code breakdown
    failures_csv = f"{csv_prefix}_failures.csv"
    if os.path.exists(failures_csv):
        with open(failures_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                error_msg = row.get("Error", "")
                occurrences = int(row.get("Occurrences", 0))
                if "429" in error_msg:
                    result.status_429_count += occurrences
                elif any(
                    str(code) in error_msg
                    for code in [500, 502, 503, 504]
                ):
                    result.status_5xx_count += occurrences

    _print_round_summary(result)
    return result


def _print_round_summary(r: RoundResult) -> None:
    """Print a compact summary of one round."""
    print(f"\n  --- Results: {r.name} ({r.users} users) ---")
    print(f"  Requests:  {r.total_requests:,}")
    print(f"  Failures:  {r.total_failures:,} ({r.error_rate_pct:.1f}%)")
    print(f"  RPS:       {r.rps:.1f}")
    print(f"  Avg:       {r.avg_response_time:.0f}ms")
    print(f"  P50:       {r.p50:.0f}ms")
    print(f"  P95:       {r.p95:.0f}ms")
    print(f"  P99:       {r.p99:.0f}ms")
    print(f"  Max:       {r.max_response_time:.0f}ms")
    if r.status_429_count:
        print(f"  429s:      {r.status_429_count:,}")
    if r.status_5xx_count:
        print(f"  5xx:       {r.status_5xx_count:,}")


def _print_summary_table(results: list[RoundResult]) -> str:
    """Print and return a formatted summary table of all rounds."""
    lines = []
    header = (
        f"{'Round':<16} {'Users':>5} {'Reqs':>7} {'Fail%':>6} "
        f"{'RPS':>7} {'Avg':>7} {'P50':>7} {'P95':>7} "
        f"{'P99':>7} {'Max':>8} {'429s':>6} {'5xx':>5}"
    )
    separator = "-" * len(header)

    lines.append("")
    lines.append("=" * 80)
    lines.append("  PROGRESSIVE LOAD TEST RESULTS — SUMMARY TABLE")
    lines.append("=" * 80)
    lines.append("")
    lines.append(header)
    lines.append(separator)

    for r in results:
        line = (
            f"{r.name:<16} {r.users:>5} {r.total_requests:>7,} "
            f"{r.error_rate_pct:>5.1f}% {r.rps:>7.1f} "
            f"{r.avg_response_time:>6.0f}ms {r.p50:>6.0f}ms "
            f"{r.p95:>6.0f}ms {r.p99:>6.0f}ms "
            f"{r.max_response_time:>7.0f}ms {r.status_429_count:>6} "
            f"{r.status_5xx_count:>5}"
        )
        lines.append(line)

    lines.append(separator)
    lines.append("")

    # Inflection point analysis
    lines.append("  INFLECTION POINT ANALYSIS")
    lines.append("  " + "-" * 40)

    # Find where P95 exceeds SLA thresholds
    for r in results:
        if r.p95 > 2000:
            lines.append(
                f"  [!] P95 SLA violation at {r.users} users "
                f"({r.name}): {r.p95:.0f}ms > 2,000ms"
            )
        if r.p99 > 5000:
            lines.append(
                f"  [!] P99 SLA violation at {r.users} users "
                f"({r.name}): {r.p99:.0f}ms > 5,000ms"
            )
        if r.error_rate_pct > 5:
            lines.append(
                f"  [!] Error rate > 5% at {r.users} users "
                f"({r.name}): {r.error_rate_pct:.1f}%"
            )
        if r.status_429_count > 0:
            pct_429 = (
                r.status_429_count / max(r.total_requests, 1) * 100
            )
            lines.append(
                f"  [R] Rate-limited at {r.users} users "
                f"({r.name}): {r.status_429_count} / "
                f"{r.total_requests} = {pct_429:.1f}%"
            )

    # Peak throughput
    if results:
        peak = max(results, key=lambda r: r.rps)
        lines.append(
            f"\n  Peak throughput: {peak.rps:.1f} RPS at {peak.users} "
            f"users ({peak.name})"
        )

        # Find inflection point (where error rate first exceeds 1%)
        for r in results:
            if r.error_rate_pct > 1.0 and r.total_requests > 10:
                lines.append(
                    f"  Error inflection: {r.users} users ({r.name}) — "
                    f"{r.error_rate_pct:.1f}% error rate"
                )
                break

        # Find latency inflection (where P95 doubles from baseline)
        baseline_p95 = None
        for r in results:
            if baseline_p95 is None and r.total_requests > 10:
                baseline_p95 = r.p95
            elif (
                baseline_p95
                and r.p95 > baseline_p95 * 2
                and r.total_requests > 10
            ):
                lines.append(
                    f"  Latency inflection: {r.users} users ({r.name}) — "
                    f"P95 {r.p95:.0f}ms (2x baseline {baseline_p95:.0f}ms)"
                )
                break

    lines.append("")
    lines.append("=" * 80)

    output = "\n".join(lines)
    print(output)
    return output


def main() -> None:
    """Run progressive load tests."""
    parser = argparse.ArgumentParser(
        description="Progressive load test runner for Agent Red"
    )
    parser.add_argument(
        "--env",
        choices=["staging", "local"],
        default="staging",
        help="Target environment (default: staging)",
    )
    parser.add_argument(
        "--host",
        help="Custom host URL (overrides --env)",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick smoke test (health + 10 users only)",
    )
    args = parser.parse_args()

    # Determine host
    if args.host:
        host = args.host
    elif args.env == "staging":
        host = STAGING_HOST
    else:
        host = "http://localhost:8000"

    plan = QUICK_PLAN if args.quick else FULL_PLAN
    project_root = Path(__file__).resolve().parent.parent

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = OUTPUT_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'#' * 70}")
    print(f"  PROGRESSIVE LOAD TEST")
    print(f"  Host:    {host}")
    print(f"  Plan:    {'quick' if args.quick else 'full'} ({len(plan)} rounds)")
    print(f"  Output:  {run_dir}")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"{'#' * 70}")

    # Run each round
    results: list[RoundResult] = []
    for i, cfg in enumerate(plan, 1):
        print(f"\n  [{i}/{len(plan)}] Starting round: {cfg.name}")

        # Brief pause between rounds to let the system recover
        if i > 1:
            print("  Cooling down (10s)...")
            time.sleep(10)

        try:
            result = _run_round(cfg, host, run_dir, project_root)
            results.append(result)
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] Round {cfg.name} exceeded 10 minute limit")
            results.append(RoundResult(name=cfg.name, users=cfg.users))
        except Exception as exc:
            print(f"  [ERROR] Round {cfg.name} failed: {exc}")
            results.append(RoundResult(name=cfg.name, users=cfg.users))

    # Print and save summary
    summary = _print_summary_table(results)

    summary_file = run_dir / "SUMMARY.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"Progressive Load Test Results\n")
        f.write(f"Host: {host}\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Rounds: {len(plan)}\n\n")
        f.write(summary)

    # Save results as JSON for programmatic analysis
    json_file = run_dir / "results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(
            [
                {
                    "name": r.name,
                    "users": r.users,
                    "total_requests": r.total_requests,
                    "total_failures": r.total_failures,
                    "error_rate_pct": r.error_rate_pct,
                    "avg_response_time": r.avg_response_time,
                    "p50": r.p50,
                    "p75": r.p75,
                    "p90": r.p90,
                    "p95": r.p95,
                    "p99": r.p99,
                    "max_response_time": r.max_response_time,
                    "rps": r.rps,
                    "status_429_count": r.status_429_count,
                    "status_5xx_count": r.status_5xx_count,
                }
                for r in results
            ],
            f,
            indent=2,
        )

    print(f"\n  Summary saved to: {summary_file}")
    print(f"  JSON results:     {json_file}")
    print(f"  HTML reports:     {run_dir}/*-report.html")


if __name__ == "__main__":
    main()
