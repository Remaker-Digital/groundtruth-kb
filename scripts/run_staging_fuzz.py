"""
Run Schemathesis API fuzzing against live staging (SPEC-1839 / WI-1497).

Exercises the staging API gateway with generated test cases from the OpenAPI
schema. Verifies no 500 errors, schema compliance, and stateful link testing.

Environment variables:
    STAGING_URL     — Staging API base URL (required, no default)
    STAGING_API_KEY — SPA platform admin API key for authenticated endpoints
    FUZZ_MAX_CASES  — Max test cases per endpoint (default: 50)

Usage:
    python scripts/run_staging_fuzz.py [--dry-run] [--report report.json]

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_STAGING_URL = ""  # SPEC-0058: No hardcoded FQDNs — set STAGING_URL env var


def run_fuzz(
    staging_url: str,
    api_key: str | None,
    max_cases: int = 50,
    dry_run: bool = False,
    report_path: str | None = None,
) -> dict:
    """Run Schemathesis against staging."""
    openapi_url = f"{staging_url}/openapi.json"

    cmd = [
        sys.executable,
        "-m",
        "schemathesis",
        "run",
        openapi_url,
        "--checks=all",
        "--stateful=links",
        f"--hypothesis-max-examples={max_cases}",
        "--hypothesis-deadline=10000",
        "--request-timeout=15000",
        "--base-url",
        staging_url,
    ]

    if api_key:
        cmd.extend(["--header", f"X-API-Key:{api_key}"])

    if report_path:
        cmd.extend(["--cassette-path", report_path])

    cmd_str = " ".join(cmd)

    if dry_run:
        logger.info("[DRY RUN] Would execute:\n  %s", cmd_str)
        return {"status": "dry_run", "command": cmd_str}

    logger.info("Running Schemathesis against staging: %s", staging_url)
    logger.info("Max cases per endpoint: %d", max_cases)
    logger.info("Command: %s", cmd_str)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "staging_url": staging_url,
        "max_cases": max_cases,
        "exit_code": result.returncode,
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-1000:] if result.stderr else "",
        "status": "pass" if result.returncode == 0 else "fail",
    }

    if result.returncode == 0:
        logger.info("Schemathesis PASSED — no failures detected")
    else:
        logger.warning("Schemathesis FAILED (exit code %d)", result.returncode)
        logger.warning("Output:\n%s", result.stdout[-500:])

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Schemathesis API fuzzing against staging (SPEC-1839)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", help="Save cassette report to this path")
    parser.add_argument("--max-cases", type=int, default=50)
    args = parser.parse_args()

    staging_url = os.environ.get("STAGING_URL", DEFAULT_STAGING_URL)
    api_key = os.environ.get("STAGING_API_KEY")

    if not api_key and not args.dry_run:
        logger.warning("STAGING_API_KEY not set — only public endpoints will be tested")

    result = run_fuzz(
        staging_url=staging_url,
        api_key=api_key,
        max_cases=args.max_cases,
        dry_run=args.dry_run,
        report_path=args.report,
    )

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("status") in ("pass", "dry_run") else 1)


if __name__ == "__main__":
    main()
