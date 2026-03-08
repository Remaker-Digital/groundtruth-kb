#!/usr/bin/env python3
"""Automated Test Pipeline — SPEC-1616 / PLAN-001.

Single-invocation, fully autonomous pipeline that executes the Master Test
Plan (PLAN-001) without any human or Claude interaction.

SPEC-1649: ALL phases use only live external interfaces (HTTP, WebSocket,
rendered UI against real backend). No mocked APIs, stubs, or code inspection.

    Pre-check : Validate Environment (fail-fast)
    Phase  1  : Pre-flight Checks (live platform gates)
    Phase  2  : Data Seeding (populate staging with realistic test data)
    Phase  3  : Production Regression (live E2E Playwright)
    Phase  5  : Tenant Isolation (live cross-tenant verification)
    Phase  6  : API Security & Penetration (live adversarial requests)
    Phase  7  : Rate Limiting & DoS Resilience (live rate limit exhaustion)
    Phase  8  : Data Integrity & Backup (live consistency checks)
    Phase  9  : Resilience & Failover (live graceful degradation)
    Phase 10  : Load Testing (Locust headless against staging)
    Phase 11  : Conversation Quality (live widget API conversation flow)
    Phase 13  : SPA Provisioning + Critical Path (live config pipeline)
    Phase 14  : Upgrade Verification (live multi-tenant assertions)
    Phase 15  : External Verification (live URL reachability checks)
    Phase 16  : Widget Embed (live widget bundle/config/CORS checks)
    Summary   : Print table, create DEFECTs, write log, update KB phases

Removed phases (SPEC-1649 — mocked/inspection tests excluded from PLAN-001):
    Phase  4  : External URL Reachability (MOCKED_UNIT → consolidated into Phase 1)
    Phase 12  : UI Regression (MOCKED_UI → covered by Phase 3 live E2E)

Restored phases:
    Phase  2  : Data Seeding (was MOCKED_UNIT; now seeds realistic test data via REST API)

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


def _get_env_vars(args: argparse.Namespace) -> dict[str, str]:
    """Get environment-specific variables for subprocess invocations.

    S132 lesson: config pipeline tests read PROD_URL, SUPERADMIN_PREVIEW_API_KEY,
    and PREVIEW_WIDGET_KEY from env vars. Without explicit passthrough, a staging
    pipeline silently tests production.
    """
    try:
        from scripts.upgrade_verification import ENVIRONMENTS, TENANTS
        env_cfg = ENVIRONMENTS.get(args.env, {})
        fqdn = env_cfg.get("fqdn", "")
        superadmin_key = env_cfg.get("api_key", "")  # ENVIRONMENTS uses "api_key" key
        widget_key = env_cfg.get("widget_key", "")
        cosmos_db = env_cfg.get("cosmos_db_database", "")
        env_vars = {}
        if fqdn:
            env_vars["PROD_URL"] = f"https://{fqdn}"
        if superadmin_key:
            env_vars["SUPERADMIN_PREVIEW_API_KEY"] = superadmin_key
        if widget_key:
            env_vars["PREVIEW_WIDGET_KEY"] = widget_key
        if cosmos_db:
            env_vars["COSMOS_DB_DATABASE"] = cosmos_db

        # S134: Pass Tenant B credentials for multi-tenant isolation tests.
        # Multi-tenant tests (Phase 5, 7, 8) need a second tenant's credentials.
        # Look up the first non-primary tenant in TENANTS for this environment.
        for key, overlay in TENANTS.items():
            if key.startswith(f"{args.env}:"):
                env_vars["TENANT_B_API_KEY"] = overlay.get("api_key", "")
                env_vars["TENANT_B_WIDGET_KEY"] = overlay.get("widget_key", "")
                break
        return env_vars
    except Exception as e:
        log("WARN", f"  Could not load ENVIRONMENTS: {e}")
        return {}


def _run_pytest(test_path: str | list[str], *, timeout: int = 300,
                prefix: str = "  [pytest] ", extra_args: list[str] | None = None,
                xdist: bool = False,
                extra_env: dict[str, str] | None = None) -> tuple[int, int, int, int, float, str]:
    """Run pytest and return (passed, failed, errors, xfailed, duration, stdout).

    Handles all output parsing consistently across phases.
    """
    if isinstance(test_path, str):
        test_path = [test_path]

    # JUnit XML for test traceability (SPEC-1661)
    xml_dir = os.path.join(PROJECT_ROOT, "logs")
    os.makedirs(xml_dir, exist_ok=True)
    junit_xml = os.path.join(xml_dir, "test-results-pipeline.xml")
    cmd = [sys.executable, "-m", "pytest", *test_path,
           "-v", "--timeout=60", "--tb=short", "--no-header",
           f"--junitxml={junit_xml}"]
    if xdist:
        cmd.extend(["-n", "4"])
    if extra_args:
        cmd.extend(extra_args)

    # Merge extra_env into current environment for the subprocess
    env = None
    if extra_env:
        env = {**os.environ, **extra_env}

    t0 = time.time()
    r = stream_subprocess(cmd, cwd=PROJECT_ROOT, timeout=timeout, prefix=prefix,
                          env=env)
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

    # All phases are live (SPEC-1649) — always validate live prerequisites
    needs_live = True
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
# Phase 2 — Data Seeding (populate staging with realistic test data)
# ---------------------------------------------------------------------------
def phase_2_data_seeding(args: argparse.Namespace) -> PhaseResult:
    """Populate tenant with realistic data via REST API (seed_midflight.py).

    Runs immediately before live E2E tests (Phase 3) to ensure the tenant has
    the data that a real customer would have after weeks of active use:
    - Team members (admin, escalation agents, viewer)
    - Knowledge base articles (FAQ, policy, product, article)
    - Quick actions (5 widget buttons)
    - Conversations (5 widget-initiated via chat API)
    - Active configuration (brand, widget, escalation settings)

    Without this data, CRUD display tests (inbox, KB list, team table,
    dashboard stats) fail due to empty state.

    For staging: runs both cleanup (idempotent) and full seed.
    For production: SKIPPED — never mutate production data automatically.

    The initialization seed (seed_tenant.py) is a separate concern — it resets
    the tenant to first-use state via direct Cosmos writes and should be run
    manually after deployment when a full tenant reset is needed.
    """
    t0 = time.time()

    if args.env == "production":
        log("SKIP", "  Data seeding skipped — production environment")
        return PhaseResult(2, "Data Seeding", "SKIP", time.time() - t0,
                           "Skipped for production safety")

    try:
        # S158 fix: seed_midflight reads env vars directly (not subprocess).
        # Override os.environ so it picks up the correct staging credentials
        # instead of .env.local's production keys.
        env_vars = _get_env_vars(args)
        for k, v in env_vars.items():
            os.environ[k] = v

        from scripts.seed_midflight import run_seed
        ok = run_seed(
            env=args.env,
            skip_conversations=False,
            skip_cleanup=False,
        )
        dt = time.time() - t0

        if ok:
            log("PASS", "  Data seeding completed")
            return PhaseResult(2, "Data Seeding", "PASS", dt)
        else:
            log("WARN", "  Data seeding completed with warnings")
            return PhaseResult(2, "Data Seeding", "WARN", dt,
                               "Some seed operations failed")
    except Exception as e:
        dt = time.time() - t0
        detail = str(e)[:200]
        log("WARN", f"  Data seeding error: {detail}")
        return PhaseResult(2, "Data Seeding", "WARN", dt, detail)


# ---------------------------------------------------------------------------
# Phase 3 — Production Regression / Live E2E (PHASE-003)
# ---------------------------------------------------------------------------
def phase_3_live_e2e(args: argparse.Namespace) -> PhaseResult:
    """Run live E2E Playwright tests against the target environment."""
    t0 = time.time()
    env_vars = _get_env_vars(args)
    # S134: Playwright tests against live staging need longer per-test timeout.
    # Default --timeout=60 is insufficient: each test starts Vite dev server,
    # navigates SPA via proxy to staging, waits for real API responses.
    # Override to 120s per test, 900s total subprocess.
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/e2e_live/", timeout=900, prefix="  [live-e2e] ",
        extra_env=env_vars,
        extra_args=["--timeout=120"],
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
# Phase 4 — REMOVED (SPEC-1649: MOCKED_UNIT)
# tests/ops/ runs mocked script inspection. External URL reachability is
# covered by Phase 1 pre-flight checks (live HTTP to health endpoint).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Phase 5 — Tenant Isolation (PHASE-005)
# ---------------------------------------------------------------------------
def phase_5_tenant_isolation(args: argparse.Namespace) -> PhaseResult:
    """Run live tenant isolation verification."""
    t0 = time.time()
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_tenant_isolation_live.py",
        timeout=300, prefix="  [isolation] ",
        extra_env=env_vars,
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
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_live_penetration.py",
        timeout=300, prefix="  [security] ",
        extra_env=env_vars,
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
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_rate_limiting_live.py",
        timeout=300, prefix="  [rate-limit] ",
        extra_env=env_vars,
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
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_data_integrity_live.py",
        timeout=300, prefix="  [integrity] ",
        extra_env=env_vars,
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
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_resilience_live.py",
        timeout=300, prefix="  [resilience] ",
        extra_env=env_vars,
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
# Phase 11 — Conversation Quality (PHASE-011) — LIVE_API
# Replaces mocked evaluation framework with live widget API conversation flow.
# WI-1022: Tests real chat pipeline via external HTTP interface.
# ---------------------------------------------------------------------------
def phase_11_conversation_quality(args: argparse.Namespace) -> PhaseResult:
    """Run live conversation quality tests via widget API (SPEC-1649)."""
    t0 = time.time()
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/live_api/test_conversation_quality_live.py",
        timeout=300, prefix="  [conv-quality] ",
        extra_env=env_vars,
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
# Phase 12 — REMOVED (SPEC-1649: MOCKED_UI)
# tests/e2e/ uses Playwright with local Vite + route interception (mocked).
# Phase 3 runs live E2E via tests/e2e_live/.
# Future: WI-1023 will expand tests/e2e_live/ to cover all admin pages.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Phase 13 — SPA Provisioning + Critical Path (PHASE-013)
# ---------------------------------------------------------------------------
def phase_13_config_pipeline(args: argparse.Namespace) -> PhaseResult:
    """Run live config pipeline tests (SPEC-1649: live API only).

    SPEC-1649: KB assertion checks (SOURCE_INSPECTION) removed from PLAN-001.
    KB assertions remain a development-time tool (run via assertion-check.py hook).
    """
    t0 = time.time()

    # Pass environment-specific variables (S132 lesson: env-aware config tests)
    env_vars = _get_env_vars(args)

    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/security/test_config_pipeline_live.py",
        timeout=300, prefix="  [config] ",
        extra_env=env_vars,
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Config Pipeline: {passed} passed")
        return PhaseResult(13, "SPA Provisioning + Critical Path", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Config Pipeline: {detail}")
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
# Phase 15 — External Verification (PHASE-015) — LIVE_API
# Replaces source inspection with live HTTP reachability checks.
# WI-1025: Tests external URLs (docs site, public endpoints, admin SPAs).
# ---------------------------------------------------------------------------
def phase_15_external_verification(args: argparse.Namespace) -> PhaseResult:
    """Run live external URL verification tests (SPEC-1649)."""
    t0 = time.time()
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/live_api/test_external_urls_live.py",
        timeout=120, prefix="  [ext-verify] ",
        extra_env=env_vars,
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  External Verification: {passed} passed")
        return PhaseResult(15, "External Verification", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  External Verification: {detail}")
        return PhaseResult(15, "External Verification", "FAIL", dt, detail)


def phase_16_widget_embed(args: argparse.Namespace) -> PhaseResult:
    """Run live widget embed verification tests (SPEC-1649)."""
    t0 = time.time()
    env_vars = _get_env_vars(args)
    passed, failed, errors, xfailed, dt, _ = _run_pytest(
        "tests/live_api/test_widget_embed_live.py",
        timeout=120, prefix="  [widget-embed] ",
        extra_env=env_vars,
    )

    if failed == 0 and errors == 0 and passed > 0:
        log("PASS", f"  Widget Embed: {passed} passed")
        return PhaseResult(16, "Widget Embed", "PASS", dt,
                           extra=f"[{passed}]")
    else:
        detail = f"{passed} passed, {failed} failed, {errors} errors"
        log("FAIL", f"  Widget Embed: {detail}")
        return PhaseResult(16, "Widget Embed", "FAIL", dt, detail)


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
# Phase execution order: ALL phases are live (SPEC-1649).
# Phase 2 restored as data seeding (replaced removed mocked-unit phase).
# Security phases reordered so rate-limiting runs last to avoid exhausting windows.
# Phases 5 → 6 → 8 → 9 → 7 (rate limiting last among security).
# Removed phases: 4 (mocked ops), 12 (mocked UI)
# Restored phases: 2 (data seeding), 11 (conversation quality), 15 (external verify), 16 (widget embed)
PHASE_ORDER_ALL = [1, 2, 3, 5, 6, 8, 9, 7, 10, 11, 13, 14, 15, 16]

PHASE_GROUPS = {
    "live":     [1, 2, 3, 5, 6, 8, 9, 7, 10, 11, 13, 14, 15, 16],
    "security": [5, 6, 8, 9, 7],
    "all":      PHASE_ORDER_ALL,
}

# ALL remaining phases are live (SPEC-1649)
LIVE_PHASES = {1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16}

# Phases that MUST have a cooldown before them (heavy API consumers)
COOLDOWN_BEFORE = {3, 5, 6, 7, 8, 9, 11, 14}


def main():
    parser = argparse.ArgumentParser(
        description="Master Test Plan Runner — PLAN-001 (live-only, SPEC-1649)")
    parser.add_argument("--env", required=True, choices=["staging", "production"],
                        help="Target environment")
    parser.add_argument("--version", required=True,
                        help="Expected product version (e.g., 1.66.0)")
    parser.add_argument("--phase", default=None,
                        choices=["live", "security", "all"],
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

    # Phase dispatch table (SPEC-1649: live-only phases)
    phase_funcs: dict[int, callable] = {
        1:  lambda: phase_1_preflight(args),
        2:  lambda: phase_2_data_seeding(args),
        3:  lambda: phase_3_live_e2e(args),
        5:  lambda: phase_5_tenant_isolation(args),
        6:  lambda: phase_6_security_penetration(args),
        7:  lambda: phase_7_rate_limiting(args),
        8:  lambda: phase_8_data_integrity(args),
        9:  lambda: phase_9_resilience(args),
        10: lambda: phase_10_load_testing(args),
        11: lambda: phase_11_conversation_quality(args),
        13: lambda: phase_13_config_pipeline(args),
        14: lambda: phase_14_upgrade_verification(args),
        15: lambda: phase_15_external_verification(args),
        16: lambda: phase_16_widget_embed(args),
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
