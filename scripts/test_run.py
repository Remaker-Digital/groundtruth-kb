#!/usr/bin/env python3
"""Trigger a test suite and wait for results.

Usage:
    python scripts/test_run.py staging pipeline
    python scripts/test_run.py production pipeline
    python scripts/test_run.py staging unit

Environment variables:
    STAGING_SPA_KEY     - SPA platform admin key for staging
    PRODUCTION_SPA_KEY  - SPA platform admin key for production

Exit codes:
    0 - All tests passed
    1 - Failures or errors occurred

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FQDNS = {
    "staging": "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    "production": "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
}

KEY_ENV_VARS = {
    "staging": "STAGING_SPA_KEY",
    "production": "PRODUCTION_SPA_KEY",
}

POLL_INTERVAL_S = 10
MAX_POLL_S = 5400  # 90 minutes — matches _STALE_RUN_TIMEOUT_S
TERMINAL_STATUSES = {"passed", "failed", "cancelled", "error"}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_log_file = None


def _init_log() -> None:
    global _log_file
    log_dir = Path(__file__).resolve().parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    _log_file = open(log_dir / f"test-{ts}.log", "w", encoding="utf-8")


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
# HTTP helpers
# ---------------------------------------------------------------------------


def _api_request(
    url: str,
    api_key: str,
    method: str = "GET",
    body: dict | None = None,
    timeout: int = 60,
) -> tuple[int, dict]:
    """Make an HTTP request and return (status_code, json_body)."""
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read())
        except Exception:
            err_body = {"error": str(e)}
        return e.code, err_body
    except urllib.error.URLError as e:
        return 0, {"error": f"Connection failed: {e.reason}"}


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------


def resolve_api_key(env: str) -> str | None:
    """Read API key from environment variable."""
    var = KEY_ENV_VARS[env]
    key = os.environ.get(var)
    if not key:
        log(f"ERROR: {var} environment variable not set.")
        log(f"  Set it with: export {var}=ar_spa_plat_...")
        return None
    return key


def trigger_run(base_url: str, api_key: str, suite: str, env: str) -> str | None:
    """POST /api/superadmin/tests/run and return the run ID."""
    url = f"https://{base_url}/api/superadmin/tests/run"
    body = {"suite": suite, "environment": env}

    log(f"Triggering '{suite}' suite on {env}...")
    status, data = _api_request(url, api_key, method="POST", body=body)

    if status == 200 or status == 202:
        run_id = data.get("runId")
        log(f"  Run queued: {run_id}")
        return run_id
    elif status == 409:
        log(f"  ERROR: A test run is already in progress.")
        log(f"  {data}")
        return None
    elif status == 0:
        log(f"  ERROR: {data.get('error')}")
        return None
    else:
        log(f"  ERROR: HTTP {status} — {data}")
        return None


def poll_until_complete(
    base_url: str, api_key: str, run_id: str
) -> dict:
    """Poll /api/superadmin/tests/{run_id}/status until terminal state."""
    url = f"https://{base_url}/api/superadmin/tests/{run_id}/status"
    start = time.time()
    last_completed = -1
    retries = 0

    while True:
        elapsed = int(time.time() - start)

        if elapsed > MAX_POLL_S:
            log(f"  TIMEOUT after {elapsed}s — giving up.")
            return {"status": "timeout", "passed": 0, "failed": 0}

        status_code, data = _api_request(url, api_key, timeout=60)

        if status_code == 0:
            retries += 1
            if retries > 3:
                log(f"  ERROR: 3 consecutive connection failures. Aborting.")
                return {"status": "connection_error", "passed": 0, "failed": 0}
            log(f"  Connection error (retry {retries}/3)...")
            time.sleep(POLL_INTERVAL_S)
            continue

        retries = 0  # reset on success
        run_status = data.get("status", "unknown")
        passed = data.get("passed", 0)
        failed = data.get("failed", 0)
        errored = data.get("errored", 0)
        completed = data.get("completed", 0)
        phase = data.get("currentPhase", "")
        phases_done = data.get("phasesRun", [])

        # Print progress only when something changes
        if completed != last_completed:
            phase_str = f", phase: {phase}" if phase else ""
            phases_str = f" [{len(phases_done)} phases done]" if phases_done else ""
            log(
                f"  [{elapsed:>4}s] {run_status} — "
                f"{passed}P/{failed}F/{errored}E "
                f"({completed} completed){phase_str}{phases_str}"
            )
            last_completed = completed

        if run_status in TERMINAL_STATUSES:
            data["_elapsed"] = elapsed
            return data

        time.sleep(POLL_INTERVAL_S)


def print_summary(data: dict) -> None:
    """Print the final test run summary."""
    status = data.get("status", "unknown")
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    errored = data.get("errored", 0)
    skipped = data.get("skipped", 0)
    duration = data.get("durationS")
    phases = data.get("phasesRun", [])
    elapsed = data.get("_elapsed", 0)
    failures = data.get("failures", [])

    log("")
    log("=" * 60)
    status_icon = "✅" if status == "passed" else "❌"
    log(f"  {status_icon} Status: {status.upper()}")
    log(f"  Passed: {passed}  Failed: {failed}  Errored: {errored}  Skipped: {skipped}")
    if duration:
        log(f"  Duration: {duration:.1f}s")
    log(f"  Wall time: {elapsed}s")
    log(f"  Phases: {', '.join(phases) if phases else 'none'}")
    log("=" * 60)

    if failures:
        log(f"\nFailures ({len(failures)}):")
        for f in failures:
            cat = f.get("category", "?")
            name = f.get("name", "unknown")
            detail = f.get("detail", "")
            # Print first 2 lines of detail
            detail_lines = detail.strip().split("\n")[:2]
            log(f"  [{cat}] {name}")
            for dl in detail_lines:
                log(f"    {dl}")
        log("")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Trigger a test suite and wait for results."
    )
    parser.add_argument(
        "environment",
        choices=["staging", "production"],
        help="Target environment",
    )
    parser.add_argument(
        "suite",
        nargs="?",
        default="pipeline",
        help="Test suite name (default: pipeline)",
    )
    args = parser.parse_args()

    _init_log()

    log(f"Agent Red Test Runner")
    log(f"  Environment: {args.environment}")
    log(f"  Suite: {args.suite}")
    log("")

    # 1. Resolve API key
    api_key = resolve_api_key(args.environment)
    if not api_key:
        _close_log()
        return 1

    base_url = FQDNS[args.environment]

    # 2. Trigger the run
    run_id = trigger_run(base_url, api_key, args.suite, args.environment)
    if not run_id:
        _close_log()
        return 1

    # 3. Poll until complete
    log("")
    log("Polling for results...")
    data = poll_until_complete(base_url, api_key, run_id)

    # 4. Print summary
    print_summary(data)

    _close_log()

    return 0 if data.get("status") == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
