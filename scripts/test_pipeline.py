#!/usr/bin/env python3
"""Automated Test Pipeline — SPEC-1616 / PLAN-001.

Single-invocation, fully autonomous pipeline that executes ALL 16 phases of
the Master Test Plan (PLAN-001) without any human or Claude interaction.

Each phase maps 1:1 to a PLAN-001 phase (PHASE-001 through PHASE-016):

    Pre-check : Validate Environment (fail-fast)
    Phase  1  : Pre-flight Checks (live platform gates)
    Phase  2  : Unit & Integration Tests (thermal-safe, 5 batches)
    Phase  3  : Production Regression (live E2E Playwright)
    Phase  4  : External URL Reachability (ops spec tests)
    Phase  5  : Tenant Isolation (live cross-tenant verification)
    Phase  6  : API Security & Penetration (live adversarial requests)
    Phase  7  : Rate Limiting & DoS Resilience (live rate limit exhaustion)
    Phase  8  : Data Integrity & Backup (live consistency checks)
    Phase  9  : Resilience & Failover (live graceful degradation)
    Phase 10  : Load Testing (Locust headless)
    Phase 11  : Conversation Quality (evaluation metrics)
    Phase 12  : UI Regression (mocked E2E Playwright — ALL tests)
    Phase 13  : SPA Provisioning + Critical Path (live config pipeline)
    Phase 14  : Upgrade Verification (live multi-tenant assertions)
    Phase 15  : Manual Verification (automatable subset + SKIP for manual)
    Phase 16  : Widget Visual Regression (widget + visual source tests)
    Summary   : Print table, create DEFECTs, write log, update KB phases

Usage:
    python scripts/test_pipeline.py --env staging --version 1.66.0
    python scripts/test_pipeline.py --env staging --version 1.66.0 --phase local
    python scripts/test_pipeline.py --env staging --version 1.66.0 --phase live
    python scripts/test_pipeline.py --env staging --version 1.66.0 --phase security
    python scripts/test_pipeline.py --env staging --version 1.66.0 --stop-on-fail

Exit codes:
    0 = all PASS/WARN/SKIP
    1 = any FAIL

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
import time
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))

from scripts._subprocess_stream import stream_subprocess  # noqa: E402


# ---------------------------------------------------------------------------
# Phase result
# ---------------------------------------------------------------------------
class PhaseResult:
    """Result of a single pipeline phase."""

    def __init__(self, phase: int, name: str, status: str, duration: float,
                 detail: str = "", extra: str = ""):
        self.phase = phase
        self.name = name
        self.status = status  # PASS, FAIL, WARN, SKIP
        self.duration = duration
        self.detail = detail
        self.extra = extra

    @property
    def passed(self) -> bool:
        return self.status in ("PASS", "WARN", "SKIP")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_log_lines: list[str] = []


def log(level: str, msg: str) -> None:
    """Log a message with timestamp — appears in real time + captured for log file."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level:5s}] {msg}"
    _log_lines.append(line)
    try:
        print(line, flush=True)
    except (OSError, ValueError):
        pass  # stdout closed (background task) — still captured in _log_lines


def _setup_log_file(env: str) -> Path:
    """Create log directory and return log file path."""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return log_dir / f"test-pipeline-{env}-{ts}.log"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
LIVE_COOLDOWN_SECONDS = 65


def _cooldown(label: str) -> None:
    """Rate limit cooldown between live API phases."""
    log("INFO", f"  Rate limit cooldown: {LIVE_COOLDOWN_SECONDS}s before {label}...")
    time.sleep(LIVE_COOLDOWN_SECONDS)


def _run_pytest(test_path: str | list[str], *, timeout: int = 300,
                prefix: str = "  [pytest] ", extra_args: list[str] | None = None,
                xdist: bool = False) -> tuple[int, int, int, int, float, str]:
    """Run pytest and return (passed, failed, errors, xfailed, duration, stdout).

    Handles all output parsing consistently across phases.
    """
    if isinstance(test_path, str):
        test_path = [test_path]

    cmd = [sys.executable, "-m", "pytest", *test_path,
           "-v", "--timeout=60", "--tb=short", "--no-header"]
    if xdist:
        cmd.extend(["-n", "4"])
    if extra_args:
        cmd.extend(extra_args)

    t0 = time.time()
    r = stream_subprocess(cmd, cwd=PROJECT_ROOT, timeout=timeout, prefix=prefix)
    dt = time.time() - t0

    # Parse pytest summary — take LAST match (thermal-safe runner prints per-batch)
    all_passed = re.findall(r"(\d+)\s+passed", r.stdout)
    all_failed = re.findall(r"(\d+)\s+failed", r.stdout)
    all_errors = re.findall(r"(\d+)\s+error", r.stdout)
    all_xfailed = re.findall(r"(\d+)\s+xfailed", r.stdout)
    passed = int(all_passed[-1]) if all_passed else 0
    failed = int(all_failed[-1]) if all_failed else 0
    errors = int(all_errors[-1]) if all_errors else 0
    xfailed = int(all_xfailed[-1]) if all_xfailed else 0

    return passed, failed, errors, xfailed, dt, r.stdout


def _record_phase_result(phase_num: int, result: str, detail: str) -> None:
    """Update the PLAN-001 phase record in the Knowledge Database."""
    try:
        from db import KnowledgeDB
        kdb = KnowledgeDB()
        try:
            phase_id = f"PHASE-{phase_num:03d}"
            kdb.update_test_plan_phase(
                id=phase_id,
                changed_by="test-pipeline",
                change_reason=f"Automated execution: {detail[:200]}",
                last_result=result,
                last_executed_at=datetime.now(timezone.utc).isoformat(),
            )
        finally:
            kdb.close()
    except Exception as e:
        log("WARN", f"  KB phase update failed: {e}")


# ---------------------------------------------------------------------------
# Pre-check — Validate Environment (not a numbered phase)
# ---------------------------------------------------------------------------
def precheck_validate_environment(args: argparse.Namespace) -> PhaseResult:
    """Fail-fast validation of all prerequisites."""
    t0 = time.time()
    failures = []

    # Python version >= 3.12
    if sys.version_info < (3, 12):
        failures.append(f"Python {sys.version} < 3.12")
    else:
        log("INFO", f"  Python: {sys.version.split()[0]}")

    # pytest available
    try:
        import pytest  # noqa: F401
        log("INFO", f"  pytest: {pytest.__version__}")
    except ImportError:
        failures.append("pytest not installed")

    # pytest-xdist
    try:
        import xdist  # noqa: F401
        log("INFO", "  pytest-xdist: available")
    except ImportError:
        failures.append("pytest-xdist not installed")

    # pytest-timeout
    try:
        import pytest_timeout  # noqa: F401
        log("INFO", "  pytest-timeout: available")
    except ImportError:
        failures.append("pytest-timeout not installed")

    # Playwright
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        log("INFO", "  Playwright: available")
    except ImportError:
        failures.append("playwright not installed")

    # Node.js (use subprocess.run — stream_subprocess hangs on .cmd wrappers)
    try:
        r = subprocess.run(["node", "--version"], capture_output=True, text=True,
                           timeout=10, shell=(sys.platform == "win32"))
        if r.returncode == 0:
            log("INFO", f"  Node.js: {r.stdout.strip()}")
        else:
            failures.append("Node.js not found")
    except Exception:
        failures.append("Node.js not found")

    # npm
    try:
        r = subprocess.run(["npm", "--version"], capture_output=True, text=True,
                           timeout=10, shell=(sys.platform == "win32"))
        if r.returncode == 0:
            log("INFO", f"  npm: {r.stdout.strip()}")
        else:
            failures.append("npm not found")
    except Exception:
        failures.append("npm not found")

    # admin/standalone/node_modules
    nm = PROJECT_ROOT / "admin" / "standalone" / "node_modules"
    if nm.exists():
        log("INFO", "  admin/standalone/node_modules: present")
    else:
        failures.append("admin/standalone/node_modules not found — run npm install")

    # Locust (optional — SKIP not FAIL)
    if shutil.which("locust"):
        log("INFO", "  Locust: available")
    else:
        log("WARN", "  Locust: not installed (Phase 10 will SKIP)")

    # Live-phase prerequisites (only when running live phases)
    needs_live = args.phase in ("live", "security", "all", None)
    if needs_live:
        # .env.local credentials
        try:
            from scripts._env import load_env_local
            load_env_local()
            log("INFO", "  .env.local: loaded")
        except Exception as e:
            failures.append(f".env.local load failed: {e}")

        # ENVIRONMENTS dict
        try:
            from scripts.upgrade_verification import ENVIRONMENTS
            if args.env in ENVIRONMENTS:
                log("INFO", f"  ENVIRONMENTS[{args.env}]: present")
            else:
                failures.append(f"ENVIRONMENTS dict missing '{args.env}'")
        except Exception as e:
            failures.append(f"Cannot import ENVIRONMENTS: {e}")

        # Health endpoint reachable
        try:
            from scripts.upgrade_verification import ENVIRONMENTS as _ENV
            env_cfg = _ENV.get(args.env, {})
            fqdn = env_cfg.get("fqdn", "")
            if fqdn:
                import httpx
                with httpx.Client(timeout=10.0) as c:
                    resp = c.get(f"https://{fqdn}/health")
                    if resp.status_code == 200:
                        body = resp.json()
                        log("INFO", f"  /health: 200 (v{body.get('product_version', '?')})")
                    else:
                        failures.append(f"/health returned HTTP {resp.status_code}")
            else:
                failures.append(f"No FQDN for env '{args.env}'")
        except Exception as e:
            failures.append(f"/health check failed: {e}")

    dt = time.time() - t0
    if failures:
        detail = "; ".join(failures)
        log("FAIL", f"  Environment validation: {len(failures)} failures")
        for f in failures:
            log("FAIL", f"    - {f}")
        return PhaseResult(0, "Pre-check: Environment", "FAIL", dt, detail)

    log("PASS", "  All environment checks passed")
    return PhaseResult(0, "Pre-check: Environment", "PASS", dt)


# ---------------------------------------------------------------------------
# Phase 1 — Pre-flight Checks (PHASE-001)
# ---------------------------------------------------------------------------
def phase_1_preflight(args: argparse.Namespace) -> PhaseResult:
    """Run pre-flight checklist Phase C (live platform gates)."""
    t0 = time.time()

    r = stream_subprocess(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "pre_flight_checklist.py"),
         "--phase", "C", "--env", args.env, "--new-version", args.version],
        cwd=PROJECT_ROOT, timeout=300, prefix="  [preflight] ",
    )

    # Parse "NN PASS, NN WARN, NN FAIL" or "NN PASS"
    m_pass = re.search(r"(\d+)\s+PASS", r.stdout)
    m_fail = re.search(r"(\d+)\s+FAIL", r.stdout)
    m_warn = re.search(r"(\d+)\s+WARN", r.stdout)
    passed = int(m_pass.group(1)) if m_pass else 0
    failed = int(m_fail.group(1)) if m_fail else 0
    warned = int(m_warn.group(1)) if m_warn else 0

    dt = time.time() - t0
    if failed == 0 and passed > 0:
        status = "WARN" if warned > 0 else "PASS"
        log(status, f"  Pre-flight: {passed} PASS, {warned} WARN")
        return PhaseResult(1, "Pre-flight Checks", status, dt,
                           extra=f"[{passed} PASS, {warned} WARN]")
    else:
        detail = f"{passed} PASS, {failed} FAIL, {warned} WARN"
        log("FAIL", f"  Pre-flight: {detail}")
        return PhaseResult(1, "Pre-flight Checks", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 2 — Unit & Integration Tests (PHASE-002)
# ---------------------------------------------------------------------------
def phase_2_local_pytest(args: argparse.Namespace) -> PhaseResult:
    """Run the full local pytest suite via thermal-safe PowerShell runner.

    Uses subprocess.run instead of stream_subprocess because PowerShell with
    CREATE_NEW_PROCESS_GROUP on Windows hangs after child pytest processes
    exit — the pipe never closes.  The thermal-safe runner manages its own
    child timeouts, so we don't need the process-group kill path.
    """
    t0 = time.time()

    cmd_str = subprocess.list2cmdline([
        "powershell", "-ExecutionPolicy", "Bypass", "-File",
        str(PROJECT_ROOT / "scripts" / "run-tests-thermal-safe.ps1"),
        "-SkipLive",
    ])

    log("INFO", "  Launching thermal-safe test runner (up to 20 min)...")
    try:
        proc = subprocess.run(
            cmd_str,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=1200,
            shell=True,
            encoding="utf-8",
            errors="replace",
        )
        stdout = proc.stdout or ""
        returncode = proc.returncode
        timed_out = False
    except subprocess.TimeoutExpired as e:
        stdout = (e.stdout or b"").decode("utf-8", errors="replace")
        returncode = -1
        timed_out = True

    dt = time.time() - t0

    # Print captured output (replay for real-time log file)
    for line in stdout.splitlines():
        log("INFO", f"  [pytest] {line}")

    # Parse output — take LAST match (thermal-safe prints per-batch before summary)
    all_passed = re.findall(r"(\d+)\s+passed", stdout)
    all_failed = re.findall(r"(\d+)\s+failed", stdout)
    passed = int(all_passed[-1]) if all_passed else 0
    failed = int(all_failed[-1]) if all_failed else 0

    if returncode == 0 and failed == 0 and passed > 0:
        log("PASS", f"  Local pytest: {passed} passed, 0 failed")
        return PhaseResult(2, "Unit & Integration Tests", "PASS", dt,
                           extra=f"[{passed}/{passed}]")
    elif timed_out:
        log("FAIL", "  Local pytest: TIMEOUT (20 min)")
        return PhaseResult(2, "Unit & Integration Tests", "FAIL", dt, "Timeout")
    else:
        detail = f"{passed} passed, {failed} failed"
        log("FAIL", f"  Local pytest: {detail}")
        return PhaseResult(2, "Unit & Integration Tests", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 3 — Production Regression / Live E2E (PHASE-003)
# ---------------------------------------------------------------------------
def phase_3_live_e2e(args: argparse.Namespace) -> PhaseResult:
    """Run live E2E Playwright tests against the target environment."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/e2e_live/", timeout=600, prefix="  [live-e2e] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        extra_parts = [f"{passed} passed"]
        if xfailed:
            extra_parts.append(f"{xfailed} xfailed")
        log("PASS", f"  Live E2E: {', '.join(extra_parts)}")
        return PhaseResult(3, "Production Regression", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Live E2E: {detail}")
        return PhaseResult(3, "Production Regression", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 4 — External URL Reachability (PHASE-004)
# ---------------------------------------------------------------------------
def phase_4_url_reachability() -> PhaseResult:
    """Run ops spec tests — pre-flight specs, seed specs, hooks, upgrade specs."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/ops/", timeout=300, prefix="  [ops] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  URL Reachability / Ops: {passed} passed")
        return PhaseResult(4, "External URL Reachability", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  URL Reachability / Ops: {detail}")
        return PhaseResult(4, "External URL Reachability", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 5 — Tenant Isolation (PHASE-005)
# ---------------------------------------------------------------------------
def phase_5_tenant_isolation(args: argparse.Namespace) -> PhaseResult:
    """Run live tenant isolation verification."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_tenant_isolation_live.py",
        timeout=300, prefix="  [isolation] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Tenant Isolation: {passed} passed")
        return PhaseResult(5, "Tenant Isolation", "PASS", dt, extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Tenant Isolation: {detail}")
        return PhaseResult(5, "Tenant Isolation", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 6 — API Security & Penetration (PHASE-006)
# ---------------------------------------------------------------------------
def phase_6_security_penetration(args: argparse.Namespace) -> PhaseResult:
    """Run live API security and penetration tests."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_live_penetration.py",
        timeout=300, prefix="  [security] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  API Security: {passed} passed")
        return PhaseResult(6, "API Security & Penetration", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  API Security: {detail}")
        return PhaseResult(6, "API Security & Penetration", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 7 — Rate Limiting & DoS Resilience (PHASE-007)
# WARNING: This phase intentionally exhausts rate limits. Run LAST among
# security phases, and always cool down afterward.
# ---------------------------------------------------------------------------
def phase_7_rate_limiting(args: argparse.Namespace) -> PhaseResult:
    """Run live rate limiting tests (intentionally exhausts rate windows)."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_rate_limiting_live.py",
        timeout=300, prefix="  [rate-limit] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Rate Limiting: {passed} passed")
        return PhaseResult(7, "Rate Limiting & DoS", "PASS", dt, extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Rate Limiting: {detail}")
        return PhaseResult(7, "Rate Limiting & DoS", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 8 — Data Integrity & Backup (PHASE-008)
# ---------------------------------------------------------------------------
def phase_8_data_integrity(args: argparse.Namespace) -> PhaseResult:
    """Run live data integrity and consistency checks."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_data_integrity_live.py",
        timeout=300, prefix="  [integrity] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Data Integrity: {passed} passed")
        return PhaseResult(8, "Data Integrity & Backup", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Data Integrity: {detail}")
        return PhaseResult(8, "Data Integrity & Backup", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 9 — Resilience & Failover (PHASE-009)
# ---------------------------------------------------------------------------
def phase_9_resilience(args: argparse.Namespace) -> PhaseResult:
    """Run live resilience and graceful degradation tests."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_resilience_live.py",
        timeout=300, prefix="  [resilience] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        extra_parts = [f"{passed} passed"]
        if xfailed:
            extra_parts.append(f"{xfailed} xfailed")
        log("PASS", f"  Resilience: {', '.join(extra_parts)}")
        return PhaseResult(9, "Resilience & Failover", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Resilience: {detail}")
        return PhaseResult(9, "Resilience & Failover", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 10 — Load Testing (PHASE-010)
# ---------------------------------------------------------------------------
def phase_10_load_testing(args: argparse.Namespace) -> PhaseResult:
    """Run Locust headless load test against the target environment."""
    t0 = time.time()

    if not shutil.which("locust"):
        dt = time.time() - t0
        log("SKIP", "  Load Testing: locust not installed")
        return PhaseResult(10, "Load Testing", "SKIP", dt,
                           "locust not installed — pip install locust")

    conf_file = f"tests/performance/locust-{args.env}.conf"
    conf_path = PROJECT_ROOT / conf_file
    if not conf_path.exists():
        conf_file = "tests/performance/locust.conf"
        conf_path = PROJECT_ROOT / conf_file
        if not conf_path.exists():
            dt = time.time() - t0
            log("SKIP", f"  Load Testing: no config file for {args.env}")
            return PhaseResult(10, "Load Testing", "SKIP", dt, "No locust config")

    r = stream_subprocess(
        ["locust", "-f", "tests/performance/locustfile.py",
         "--config", conf_file, "--headless"],
        cwd=PROJECT_ROOT, timeout=300, prefix="  [locust] ",
    )

    dt = time.time() - t0

    # Parse Locust summary for failure count and response times
    # Locust prints: "Aggregated ... | NN  | NN  | NN | NN | ..."
    # and "X% (N) ... Aggregated" for failure percentage
    fail_match = re.search(r"(\d+)\s+failures?", r.stdout, re.IGNORECASE)
    req_match = re.search(r"Aggregated\s+\d+\s+(\d+)", r.stdout)
    fail_count = int(fail_match.group(1)) if fail_match else 0

    # Check for SLA violations in output
    p95_match = re.search(r"95%.*?(\d+)", r.stdout)
    p95 = int(p95_match.group(1)) if p95_match else 0

    if r.returncode == 0 and fail_count == 0:
        log("PASS", f"  Load Testing: 0 failures, P95={p95}ms")
        return PhaseResult(10, "Load Testing", "PASS", dt,
                           extra=f"[P95={p95}ms]")
    elif r.returncode == 0:
        # Locust succeeded but had some failures — WARN
        log("WARN", f"  Load Testing: {fail_count} failures, P95={p95}ms")
        return PhaseResult(10, "Load Testing", "WARN", dt,
                           f"{fail_count} failures, P95={p95}ms")
    else:
        detail = f"exit {r.returncode}, {fail_count} failures"
        log("FAIL", f"  Load Testing: {detail}")
        return PhaseResult(10, "Load Testing", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 11 — Conversation Quality (PHASE-011)
# ---------------------------------------------------------------------------
def phase_11_conversation_quality() -> PhaseResult:
    """Run conversation quality evaluation tests."""
    t0 = time.time()
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/evaluation/", timeout=300, prefix="  [quality] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Conversation Quality: {passed} passed")
        return PhaseResult(11, "Conversation Quality", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Conversation Quality: {detail}")
        return PhaseResult(11, "Conversation Quality", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 12 — UI Regression (PHASE-012)
# ---------------------------------------------------------------------------
def phase_12_ui_regression() -> PhaseResult:
    """Run ALL mocked E2E Playwright tests — including display_values.

    The Vite dev server is managed by conftest.py's session-scoped
    ``admin_vite_server`` fixture.
    """
    t0 = time.time()

    # Collect ALL E2E test files (no exclusions)
    e2e_dir = PROJECT_ROOT / "tests" / "e2e"
    test_files = sorted(
        str(f.relative_to(PROJECT_ROOT))
        for f in e2e_dir.glob("test_*.py")
    )

    log("INFO", f"  Running {len(test_files)} E2E test files (all, including display_values)...")

    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        test_files, timeout=1500, prefix="  [e2e] ",
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  UI Regression: {passed} passed, 0 failed")
        return PhaseResult(12, "UI Regression", "PASS", dt, extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  UI Regression: {detail}")
        return PhaseResult(12, "UI Regression", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 13 — SPA Provisioning + Critical Path (PHASE-013)
# ---------------------------------------------------------------------------
def phase_13_config_pipeline(args: argparse.Namespace) -> PhaseResult:
    """Run live config pipeline tests + KB assertion check."""
    t0 = time.time()

    # Part A: Config pipeline live tests (26 tests)
    passed_a, failed_a, errors_a, _, _, _ = _run_pytest(
        "tests/security/test_config_pipeline_live.py",
        timeout=300, prefix="  [config] ",
    )

    # Part B: KB Assertion Check (in-process)
    kb_passed = 0
    kb_failed = 0
    kb_regressions: list[str] = []
    try:
        from db import KnowledgeDB
        from assertions import run_all_assertions

        kdb = KnowledgeDB()
        try:
            summary = run_all_assertions(kdb, triggered_by="test-pipeline")
        finally:
            kdb.close()

        kb_passed = summary.get("passed", 0)
        kb_failed = summary.get("failed", 0)

        # Only count machine-checkable regressions in implemented/verified specs
        _MACHINE_TYPES = {"grep", "glob", "grep_absent"}
        failures = [d for d in summary.get("details", [])
                    if not d.get("skipped") and not d["overall_passed"]]
        if failures:
            kdb2 = KnowledgeDB()
            try:
                for f in failures:
                    spec = kdb2.get_spec(f["spec_id"])
                    status = spec["status"] if spec else "unknown"
                    if status not in ("implemented", "verified"):
                        continue
                    has_machine_fail = any(
                        not r["passed"]
                        and r.get("type", "") in _MACHINE_TYPES
                        and "Invalid assertion type" not in r.get("detail", "")
                        for r in f.get("results", [])
                    )
                    if has_machine_fail:
                        kb_regressions.append(f["spec_id"])
            finally:
                kdb2.close()

        log("INFO", f"  KB Assertions: {kb_passed}/{summary.get('specs_with_assertions', 0)} PASS")
    except Exception as e:
        log("WARN", f"  KB Assertions error: {e}")

    dt = time.time() - t0
    total_failed = failed_a + errors_a + len(kb_regressions)

    if total_failed == 0 and passed_a > 0:
        log("PASS", f"  SPA + Critical Path: {passed_a} config + {kb_passed} KB assertions")
        return PhaseResult(13, "SPA Provisioning + Critical Path", "PASS", dt,
                           extra=f"[{passed_a}+{kb_passed}]")
    else:
        parts = []
        if failed_a or errors_a:
            parts.append(f"config: {failed_a} failed, {errors_a} errors")
        if kb_regressions:
            parts.append(f"KB regressions: {', '.join(kb_regressions[:5])}")
        detail = "; ".join(parts)
        log("FAIL", f"  SPA + Critical Path: {detail}")
        return PhaseResult(13, "SPA Provisioning + Critical Path", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Phase 14 — Upgrade Verification (PHASE-014)
# ---------------------------------------------------------------------------
def phase_14_upgrade_verification(args: argparse.Namespace) -> PhaseResult:
    """Run upgrade verification multi-c against target environment."""
    t0 = time.time()

    r = stream_subprocess(
        [sys.executable, str(PROJECT_ROOT / "scripts" / "upgrade_verification.py"),
         "multi-c", "--env", args.env, "--new-version", args.version],
        cwd=PROJECT_ROOT, timeout=900, prefix="  [upgrade] ",
    )

    m = re.search(r"(\d+)\s+PASS,\s+(\d+)\s+FAIL", r.stdout)
    dt = time.time() - t0

    if m:
        pass_count = int(m.group(1))
        fail_count = int(m.group(2))
        if fail_count == 0 and pass_count > 0:
            log("PASS", f"  Upgrade verification: {pass_count}/{pass_count}")
            return PhaseResult(14, "Upgrade Verification", "PASS", dt,
                               extra=f"[{pass_count}/{pass_count}]")
        else:
            detail = f"{pass_count} PASS, {fail_count} FAIL"
            log("FAIL", f"  Upgrade verification: {detail}")
            return PhaseResult(14, "Upgrade Verification", "FAIL", dt, detail)
    elif r.returncode == 0:
        log("PASS", "  Upgrade verification: exit 0")
        return PhaseResult(14, "Upgrade Verification", "PASS", dt)
    else:
        detail = r.stdout[-300:].strip() if r.stdout else "No output"
        log("FAIL", f"  Upgrade verification: exit {r.returncode}")
        return PhaseResult(14, "Upgrade Verification", "FAIL", dt, detail[:200])


# ---------------------------------------------------------------------------
# Phase 15 — Manual Verification (PHASE-015)
# Runs automatable subset: protected behaviors + governance checks.
# Reports SKIP for inherently manual items.
# ---------------------------------------------------------------------------
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


def phase_15_manual_verification(args: argparse.Namespace) -> PhaseResult:
    """Run automatable subset of manual verification."""
    t0 = time.time()
    warnings = []

    # Part A: Protected behaviors
    pb_pass = 0
    pb_total = len(PROTECTED_BEHAVIORS)
    pb_failures = []

    for pb_id, pattern, filepath, threshold in PROTECTED_BEHAVIORS:
        full_path = PROJECT_ROOT / filepath
        if not full_path.exists():
            pb_failures.append(f"{pb_id}: file not found ({filepath})")
            continue
        content = full_path.read_text(encoding="utf-8", errors="replace")
        count = content.count(pattern)
        if count >= threshold:
            pb_pass += 1
        else:
            pb_failures.append(f"{pb_id}: '{pattern}' count={count} < {threshold}")

    if pb_failures:
        for f in pb_failures:
            log("FAIL", f"    - {f}")
    else:
        log("PASS", f"  Protected Behaviors: {pb_pass}/{pb_total}")

    # Part B: Governance checks (GOV-14/15/16 via git analysis)
    try:
        r_ui = stream_subprocess(
            ["git", "diff", "--name-only", "HEAD~5"],
            cwd=PROJECT_ROOT, timeout=15, prefix="  [gov-14] ",
        )
        ui_files = [f for f in r_ui.stdout.splitlines()
                    if f.startswith("admin/") and f.endswith(".tsx")]
        test_files = [f for f in r_ui.stdout.splitlines()
                      if f.startswith("tests/e2e")]
        if ui_files and not test_files:
            warnings.append(f"GOV-14: {len(ui_files)} UI files changed, 0 E2E test changes")
            log("WARN", f"  GOV-14: {len(ui_files)} UI changes, no E2E test changes")
        else:
            log("INFO", f"  GOV-14: OK ({len(ui_files)} UI, {len(test_files)} test)")
    except Exception as e:
        warnings.append(f"GOV-14 error: {e}")

    try:
        r_tests = stream_subprocess(
            ["git", "log", "--oneline", "HEAD~5..HEAD", "--", "tests/"],
            cwd=PROJECT_ROOT, timeout=15, prefix="  [gov-15] ",
        )
        test_commits = r_tests.stdout.strip().splitlines()
        unapproved = [c for c in test_commits
                      if "approved" not in c.lower() and "drift" not in c.lower()
                      and c.strip()]
        if unapproved:
            warnings.append(f"GOV-15: {len(unapproved)} test commits without approval marker")
        else:
            log("INFO", f"  GOV-15: OK ({len(test_commits)} test commits)")
    except Exception as e:
        warnings.append(f"GOV-15 error: {e}")

    try:
        r_auto = stream_subprocess(
            ["git", "log", "--oneline", "HEAD~5..HEAD", "--",
             "scripts/deploy_pipeline.py", "scripts/test_pipeline.py",
             "scripts/pre_flight_checklist.py"],
            cwd=PROJECT_ROOT, timeout=15, prefix="  [gov-16] ",
        )
        auto_commits = r_auto.stdout.strip().splitlines()
        unapproved = [c for c in auto_commits
                      if "approved" not in c.lower() and c.strip()]
        if unapproved:
            warnings.append(f"GOV-16: {len(unapproved)} automation commits without approval")
        else:
            log("INFO", f"  GOV-16: OK ({len(auto_commits)} automation commits)")
    except Exception as e:
        warnings.append(f"GOV-16 error: {e}")

    # Part C: Manual items — always SKIP
    log("SKIP", "  3 manual test artifacts require human verification (see KB)")

    dt = time.time() - t0

    if pb_failures:
        detail = f"Protected behaviors: {'; '.join(pb_failures[:3])}"
        return PhaseResult(15, "Manual Verification", "FAIL", dt, detail)

    if warnings:
        detail = "; ".join(warnings)
        log("WARN", f"  Governance: {len(warnings)} warnings")
        return PhaseResult(15, "Manual Verification", "WARN", dt, detail)

    log("PASS", "  Manual Verification: automatable subset PASS")
    return PhaseResult(15, "Manual Verification", "WARN", dt,
                       "3 manual items SKIP — see KB")


# ---------------------------------------------------------------------------
# Phase 16 — Widget Visual Regression (PHASE-016)
# ---------------------------------------------------------------------------
def phase_16_widget_visual(args: argparse.Namespace) -> PhaseResult:
    """Run widget source inspection + visual regression tests."""
    t0 = time.time()

    # Combine tests/widget/ (753 tests) + tests/visual/ (38 tests)
    test_dirs = ["tests/widget/", "tests/visual/"]
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        test_dirs, timeout=600, prefix="  [widget] ", xdist=True,
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Widget Visual: {passed} passed")
        return PhaseResult(16, "Widget Visual Regression", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Widget Visual: {detail}")
        return PhaseResult(16, "Widget Visual Regression", "FAIL", dt, detail)


# ---------------------------------------------------------------------------
# Summary — create DEFECTs, write log, update KB
# ---------------------------------------------------------------------------
def run_summary(results: list[PhaseResult], args: argparse.Namespace,
                start_time: float, log_path: Path) -> PhaseResult:
    """Print summary, create DEFECT WIs, write log file, update KB phases."""
    t0 = time.time()

    # Create DEFECT WIs for failed phases (SPEC-1617)
    from scripts._defect_reporter import create_defect
    defect_wis = []
    for r in results:
        if r.status == "FAIL" and r.phase > 0:  # Skip pre-check (phase 0)
            wi_id = create_defect(
                title=f"Test pipeline failure: Phase {r.phase} ({r.name})",
                description=(
                    f"Automated test pipeline (PLAN-001) failed.\n\n"
                    f"Environment: {args.env}\n"
                    f"Version: {args.version}\n"
                    f"Phase {r.phase} ({r.name}): {r.detail}"
                ),
                source_spec_id="SPEC-1616",
                component="infrastructure_automation",
                changed_by="test-pipeline",
            )
            if wi_id:
                defect_wis.append(wi_id)
                log("INFO", f"  Created DEFECT: {wi_id} (Phase {r.phase})")

    # Update KB phase records
    for r in results:
        if r.phase > 0:  # Only numbered phases (not pre-check)
            _record_phase_result(r.phase, r.status,
                                f"{r.name}: {r.detail}" if r.detail else r.name)

    # Write log file
    try:
        log_path.write_text("\n".join(_log_lines), encoding="utf-8")
    except Exception:
        pass

    # Print summary table
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)

    def _sp(*a, **kw):
        try:
            print(*a, flush=True, **kw)
        except (OSError, ValueError):
            pass

    _sp(f"\n{'=' * 70}")
    _sp(f"  MASTER TEST PLAN (PLAN-001) — {args.env} v{args.version}")
    _sp(f"  Started: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    _sp(f"{'=' * 70}")

    for r in results:
        if r.phase == 0:
            label = f"Pre-check: {r.name.replace('Pre-check: ', '')}"
        else:
            label = f"Phase {r.phase:2d}: {r.name}"
        extra = f"  {r.extra}" if r.extra else ""
        pad = 45 - len(label)
        dots = "." * max(pad, 2)
        _sp(f"  {label} {dots} {r.status:4s} ({r.duration:.1f}s){extra}")

    passed_count = sum(1 for r in results if r.status == "PASS")
    failed_count = sum(1 for r in results if r.status == "FAIL")
    warn_count = sum(1 for r in results if r.status == "WARN")
    skip_count = sum(1 for r in results if r.status == "SKIP")

    all_pass = all(r.passed for r in results)
    result_str = "SUCCESS" if all_pass else "FAILURE"

    _sp(f"\n{'=' * 70}")
    _sp(f"  RESULT: {result_str}")
    _sp(f"  Phases: {passed_count} PASS, {failed_count} FAIL, "
        f"{warn_count} WARN, {skip_count} SKIP")
    _sp(f"  Duration: {minutes}m {seconds}s")
    _sp(f"  Environment: {args.env}")
    _sp(f"  Version: {args.version}")
    if defect_wis:
        _sp(f"  DEFECTs created: {', '.join(defect_wis)}")
    _sp(f"  Log: {log_path}")
    _sp(f"{'=' * 70}\n")

    dt = time.time() - t0
    return PhaseResult(99, "Summary", "PASS" if all_pass else "FAIL", dt)


# ---------------------------------------------------------------------------
# CLI + orchestrator
# ---------------------------------------------------------------------------
# Phase execution order: local phases first, then live phases (with security
# reordered so rate-limiting runs last to avoid exhausting windows).
# Phases 5 → 6 → 8 → 9 → 7 (rate limiting last among security).
PHASE_ORDER_ALL = [1, 2, 3, 4, 5, 6, 8, 9, 7, 10, 11, 12, 13, 14, 15, 16]

PHASE_GROUPS = {
    "local":    [2, 4, 11, 12, 15, 16],
    "live":     [1, 3, 5, 6, 8, 9, 7, 10, 13, 14],
    "security": [5, 6, 8, 9, 7],
    "all":      PHASE_ORDER_ALL,
}

# Phases that require live API access (need cooldowns between them)
LIVE_PHASES = {1, 3, 5, 6, 7, 8, 9, 10, 13, 14}

# Phases that MUST have a cooldown before them (heavy API consumers)
COOLDOWN_BEFORE = {5, 6, 7, 8, 9, 14}


def main():
    parser = argparse.ArgumentParser(
        description="Master Test Plan Runner — PLAN-001 (16 phases)")
    parser.add_argument("--env", required=True, choices=["staging", "production"],
                        help="Target environment")
    parser.add_argument("--version", required=True,
                        help="Expected product version (e.g., 1.66.0)")
    parser.add_argument("--phase", default=None,
                        choices=["local", "live", "security", "all"],
                        help="Phase group to run (default: all)")
    parser.add_argument("--stop-on-fail", action="store_true",
                        help="Stop after first FAIL")
    args = parser.parse_args()

    phase_group = args.phase or "all"
    phases_to_run = PHASE_GROUPS[phase_group]

    start_time = time.time()
    log_path = _setup_log_file(args.env)

    log("INFO", f"Master Test Plan (PLAN-001) starting: {args.env} v{args.version}")
    log("INFO", f"  Phase group: {phase_group} ({phases_to_run})")
    log("INFO", f"  Stop on fail: {args.stop_on_fail}")
    log("INFO", f"  Log file: {log_path}")

    results: list[PhaseResult] = []

    # Pre-check: environment validation (always runs)
    log("INFO", "--- Pre-check: Environment ---")
    precheck = precheck_validate_environment(args)
    results.append(precheck)
    if not precheck.passed:
        log("FAIL", "Pre-check failed — aborting pipeline")
        run_summary(results, args, start_time, log_path)
        sys.exit(1)

    # Phase dispatch table
    phase_funcs: dict[int, callable] = {
        1:  lambda: phase_1_preflight(args),
        2:  lambda: phase_2_local_pytest(args),
        3:  lambda: phase_3_live_e2e(args),
        4:  lambda: phase_4_url_reachability(),
        5:  lambda: phase_5_tenant_isolation(args),
        6:  lambda: phase_6_security_penetration(args),
        7:  lambda: phase_7_rate_limiting(args),
        8:  lambda: phase_8_data_integrity(args),
        9:  lambda: phase_9_resilience(args),
        10: lambda: phase_10_load_testing(args),
        11: lambda: phase_11_conversation_quality(),
        12: lambda: phase_12_ui_regression(),
        13: lambda: phase_13_config_pipeline(args),
        14: lambda: phase_14_upgrade_verification(args),
        15: lambda: phase_15_manual_verification(args),
        16: lambda: phase_16_widget_visual(args),
    }

    prev_was_live = False

    for phase_num in phases_to_run:
        is_live = phase_num in LIVE_PHASES
        needs_cooldown = phase_num in COOLDOWN_BEFORE and prev_was_live

        if needs_cooldown:
            _cooldown(f"Phase {phase_num}")

        log("INFO", f"--- Phase {phase_num}: {phase_funcs[phase_num].__name__ if hasattr(phase_funcs[phase_num], '__name__') else '?'} ---")

        result = phase_funcs[phase_num]()
        results.append(result)

        prev_was_live = is_live

        if not result.passed and args.stop_on_fail:
            log("INFO", f"  Stopping on fail (Phase {phase_num})")
            break

    # Summary always runs
    run_summary(results, args, start_time, log_path)

    # Exit code
    all_pass = all(r.passed for r in results)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
