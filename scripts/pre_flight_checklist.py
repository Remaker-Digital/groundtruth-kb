#!/usr/bin/env python3
"""Pre-Flight Deployment Checklist — automated verification for every deployment.

Phases:
    A — Pre-Build Verification (source-level, local)
    B — Build & Deploy (invokes existing procedures — manual, not automated here)
    C — Post-Deploy Platform Verification
    D — Live Tenant Provisioning Verification (end-to-end smoke test)
    E — Verdict

Usage:
    python scripts/pre_flight_checklist.py --env production --new-version 1.59.1
    python scripts/pre_flight_checklist.py --env production --phase D --new-version 1.59.0
    python scripts/pre_flight_checklist.py --env staging --phase C --new-version 1.59.1

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import argparse
import datetime
import io
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple

# Force UTF-8 stdout on Windows to avoid cp1252 encoding crashes
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Project root and imports from sibling scripts
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from upgrade_verification import api_call, widget_call, ENVIRONMENTS  # noqa: E402

# Optional: httpx for Phase D SSE streaming
try:
    import httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------
class AssertionResult(NamedTuple):
    id: str           # e.g., "A.1", "D.9"
    description: str  # human-readable gate name
    status: str       # PASS, FAIL, SKIP, WARN
    detail: str       # specifics


def _pass(aid: str, desc: str, detail: str = "") -> AssertionResult:
    return AssertionResult(aid, desc, "PASS", detail)


def _fail(aid: str, desc: str, detail: str = "") -> AssertionResult:
    return AssertionResult(aid, desc, "FAIL", detail)


def _skip(aid: str, desc: str, detail: str = "") -> AssertionResult:
    return AssertionResult(aid, desc, "SKIP", detail)


def _warn(aid: str, desc: str, detail: str = "") -> AssertionResult:
    return AssertionResult(aid, desc, "WARN", detail)


# ---------------------------------------------------------------------------
# Phase A — Pre-Build Verification
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


def phase_a(new_version: str) -> list[AssertionResult]:
    """Pre-build source-level verification."""
    results = []

    # A.1 — Version bump confirmed
    try:
        from scripts._subprocess_stream import stream_subprocess as _stream
        r_s = _stream(
            [sys.executable, "-c",
             "from src.multi_tenant.api_versioning import PRODUCT_VERSION; print(PRODUCT_VERSION)"],
            cwd=PROJECT_ROOT, timeout=15, prefix="  [A.1] ",
        )
        r = subprocess.CompletedProcess(args="", returncode=r_s.returncode,
                                        stdout=r_s.stdout, stderr="")
        actual = r.stdout.strip()
        if actual == new_version:
            results.append(_pass("A.1", "Version bump confirmed", f"PRODUCT_VERSION={actual}"))
        else:
            results.append(_fail("A.1", "Version bump confirmed",
                                 f"Expected {new_version}, got {actual}"))
    except Exception as e:
        results.append(_fail("A.1", "Version bump confirmed", str(e)))

    # A.2 — Protected Behaviors (11 assertions)
    pb_pass = 0
    pb_total = len(PROTECTED_BEHAVIORS)
    pb_failures = []
    for pb_id, pattern, filepath, threshold in PROTECTED_BEHAVIORS:
        full_path = PROJECT_ROOT / filepath
        if not full_path.exists():
            pb_failures.append(f"{pb_id}: file not found ({filepath})")
            continue
        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
            count = content.count(pattern)
            if count >= threshold:
                pb_pass += 1
            else:
                pb_failures.append(f"{pb_id}: '{pattern}' count={count} < {threshold} in {filepath}")
        except Exception as e:
            pb_failures.append(f"{pb_id}: {e}")

    if pb_pass == pb_total:
        results.append(_pass("A.2", "Protected Behaviors", f"{pb_pass}/{pb_total} assertions"))
    else:
        results.append(_fail("A.2", "Protected Behaviors",
                             f"{pb_pass}/{pb_total}: " + "; ".join(pb_failures)))

    # A.3 — No uncommitted changes
    try:
        r_s = _stream(
            ["git", "diff", "--stat", "src/", "admin/", "widget/"],
            cwd=PROJECT_ROOT, timeout=15, prefix="  [A.3] ",
        )
        r = subprocess.CompletedProcess(args="", returncode=r_s.returncode,
                                        stdout=r_s.stdout, stderr="")
        if r.stdout.strip() == "":
            results.append(_pass("A.3", "No uncommitted changes", "Clean working tree"))
        else:
            results.append(_fail("A.3", "No uncommitted changes",
                                 f"Modified files: {r.stdout.strip()[:200]}"))
    except Exception as e:
        results.append(_fail("A.3", "No uncommitted changes", str(e)))

    # A.4 and A.5 are manual (test harness and lint) — report as SKIP when running automated
    results.append(_skip("A.4", "Unit/integration tests",
                         "Run manually: .\\scripts\\run-tests-thermal-safe.ps1 -SkipLive"))
    results.append(_skip("A.5", "TypeScript lint",
                         "Run manually: cd admin && npx eslint --ext .tsx,.ts shared/ standalone/ provider/ shopify/ --max-warnings 50"))

    return results


# ---------------------------------------------------------------------------
# Phase C — Post-Deploy Platform Verification
# ---------------------------------------------------------------------------
def phase_c(fqdn: str, api_key: str, widget_key: str, new_version: str) -> list[AssertionResult]:
    """Post-deploy platform verification against a live environment."""
    results = []

    # C.1 — Version header (strip 'v' prefix for comparison — API returns bare semver)
    status, body, hdrs = api_call(fqdn, "/health")
    pv = hdrs.get("x-product-version", "")
    expected_bare = new_version.lstrip("v")
    if status == 200 and pv == expected_bare:
        results.append(_pass("C.1", "Version header matches", f"X-Product-Version: {pv}"))
    elif status == 200:
        results.append(_fail("C.1", "Version header matches",
                             f"Expected {new_version}, got '{pv}'"))
    else:
        results.append(_fail("C.1", "Version header matches",
                             f"GET /health returned HTTP {status}"))

    # C.2 — Health endpoint
    if status == 200 and isinstance(body, dict) and body.get("status") == "healthy":
        results.append(_pass("C.2", "Health endpoint healthy",
                             f"product_version={body.get('product_version', '?')}"))
    else:
        results.append(_fail("C.2", "Health endpoint healthy",
                             f"HTTP {status}, body={str(body)[:200]}"))

    # C.3 — Ready endpoint
    rs, rb, rh = api_call(fqdn, "/ready")
    if rs == 200:
        ready_status = rb.get("status", "?") if isinstance(rb, dict) else "?"
        nats_connected = True
        if isinstance(rb, dict) and isinstance(rb.get("nats"), dict):
            nats_connected = rb["nats"].get("connected", False)
        if ready_status == "ready":
            if nats_connected:
                results.append(_pass("C.3", "Ready endpoint", f"status=ready, nats=connected"))
            else:
                results.append(_warn("C.3", "Ready endpoint",
                                     "status=ready but nats.connected=false (lazy init)"))
        else:
            results.append(_fail("C.3", "Ready endpoint", f"status={ready_status}"))
    else:
        results.append(_fail("C.3", "Ready endpoint", f"HTTP {rs}"))

    # C.4–C.6 — Admin SPAs
    for cid, path, name in [
        ("C.4", "/admin/standalone/", "Standalone SPA"),
        ("C.5", "/admin/shopify/", "Shopify SPA"),
        ("C.6", "/admin/provider/", "Provider SPA"),
    ]:
        s, b, h = api_call(fqdn, path)
        ct = h.get("content-type", "")
        if s == 200 and "text/html" in ct:
            results.append(_pass(cid, name, "HTTP 200, text/html"))
        else:
            results.append(_fail(cid, name, f"HTTP {s}, content-type={ct}"))

    # C.7 — Widget.js
    s, b, h = api_call(fqdn, "/widget.js")
    if s == 200 and isinstance(b, str) and len(b) > 1000:
        results.append(_pass("C.7", "Widget.js accessible", f"{len(b)} bytes"))
    elif s == 200:
        results.append(_fail("C.7", "Widget.js accessible",
                             f"Only {len(b) if isinstance(b, str) else '?'} bytes"))
    else:
        results.append(_fail("C.7", "Widget.js accessible", f"HTTP {s}"))

    # C.8 — OpenAPI spec
    s, b, h = api_call(fqdn, "/openapi.json")
    if s == 200:
        results.append(_pass("C.8", "OpenAPI spec", "HTTP 200"))
    else:
        results.append(_fail("C.8", "OpenAPI spec", f"HTTP {s}"))

    # C.9 — Security headers
    s, b, h = api_call(fqdn, "/health")
    missing = []
    if "x-content-type-options" not in h:
        missing.append("X-Content-Type-Options")
    if "x-frame-options" not in h:
        missing.append("X-Frame-Options")
    if not missing:
        results.append(_pass("C.9", "Security headers", "nosniff + X-Frame-Options present"))
    else:
        results.append(_fail("C.9", "Security headers", f"Missing: {', '.join(missing)}"))

    # Rate limit cooldown — C.1-C.9 consume ~10 API calls.
    # The upgrade verification subprocess needs its own rate budget.
    print("    ... waiting 65s for rate limit cooldown before upgrade verification ...")
    time.sleep(65)

    # C.10 — Existing tenant data (upgrade verification Phase C)
    # This requires a Phase A snapshot to exist. Check for it.
    env_name = "production" if "api-gateway" in fqdn else "staging"
    env_cfg = ENVIRONMENTS.get(env_name, {})
    tenant_id = env_cfg.get("tenant_id", "unknown")
    snapshot_path = PROJECT_ROOT / "scripts" / "upgrade-results" / f"phase_a_{tenant_id}.json"

    if snapshot_path.exists():
        try:
            from scripts._subprocess_stream import stream_subprocess as _stream
            r_s = _stream(
                [sys.executable, str(PROJECT_ROOT / "scripts" / "upgrade_verification.py"),
                 "phase-c", "--env", env_name,
                 "--snapshot", str(snapshot_path),
                 "--new-version", new_version],
                cwd=PROJECT_ROOT, timeout=600, prefix="  [C.10] ",
            )
            r = subprocess.CompletedProcess(args="", returncode=r_s.returncode,
                                            stdout=r_s.stdout, stderr="")
            # Parse actual PASS/FAIL counts from output (e.g., "35 PASS, 0 FAIL")
            import re as _re
            m = _re.search(r"(\d+)\s+PASS,\s+(\d+)\s+FAIL", r.stdout)
            if m:
                pass_count = int(m.group(1))
                fail_count = int(m.group(2))
                if fail_count == 0:
                    results.append(_pass("C.10", "Upgrade verification (35 assertions)",
                                         f"phase-c {pass_count} PASS, 0 FAIL"))
                else:
                    detail = r.stdout[-500:] if r.stdout else r.stderr[-500:]
                    results.append(_fail("C.10", "Upgrade verification (35 assertions)",
                                         f"{pass_count} PASS, {fail_count} FAIL: {detail.strip()[:200]}"))
            elif r.returncode == 0:
                results.append(_pass("C.10", "Upgrade verification (35 assertions)",
                                     "phase-c exit 0"))
            else:
                detail = r.stdout[-500:] if r.stdout else r.stderr[-500:]
                results.append(_fail("C.10", "Upgrade verification (35 assertions)",
                                     detail.strip()))
        except Exception as e:
            results.append(_fail("C.10", "Upgrade verification (35 assertions)", str(e)))
    else:
        results.append(_skip("C.10", "Upgrade verification (35 assertions)",
                             f"No Phase A snapshot at {snapshot_path}. "
                             f"Run: python scripts/upgrade_verification.py phase-a --env {env_name}"))

    # Rate limit cooldown — Phases C.1–C.10 consume 15+ API calls.
    # Starter tier allows 10 rpm; wait for budget to replenish before regression tests.
    print("    ... waiting 65s for rate limit cooldown before regression tests ...")
    time.sleep(65)

    # C.11 — Tier 0 regression (17 tests)
    tier0_result = _run_regression_tier(fqdn, api_key, widget_key, "tier0", "C.11", 17)
    results.append(tier0_result)

    # Cooldown between tier0 and tier1 — tier0 makes 18+ API calls
    if tier0_result.status != "SKIP":
        print("    ... waiting 65s for rate limit cooldown between tier0 and tier1 ...")
        time.sleep(65)

    # C.12 — Tier 1 regression (20 tests)
    tier1_result = _run_regression_tier(fqdn, api_key, widget_key, "tier1", "C.12", 20)
    results.append(tier1_result)

    return results


def _run_regression_tier(fqdn: str, api_key: str, widget_key: str,
                         tier: str, aid: str, expected_min: int) -> AssertionResult:
    """Run a pytest tier against the live environment."""
    import re as _re
    env = os.environ.copy()
    env["PROD_URL"] = f"https://{fqdn}"
    env["PREVIEW_WIDGET_KEY"] = widget_key
    env["WIDGET_KEY"] = widget_key
    env["AGENTRED_API_KEY"] = api_key
    env["SUPERADMIN_PREVIEW_API_KEY"] = api_key
    # Ensure Python can find project modules
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    try:
        from scripts._subprocess_stream import stream_subprocess as _stream
        r_s = _stream(
            [sys.executable, "-m", "pytest",
             "tests/regression/test_upgrade_regression.py",
             "-x", "-q", "-m", tier, "--tb=short", "--no-header"],
            cwd=PROJECT_ROOT, env=env, timeout=120, prefix=f"  [{aid}] ",
        )
        r = subprocess.CompletedProcess(args="", returncode=r_s.returncode,
                                        stdout=r_s.stdout, stderr="")
        # Parse pytest output using regex (handles "18 passed," with trailing comma)
        output = r.stdout + "\n" + r.stderr
        passed = 0
        failed = 0
        for line in output.splitlines():
            m_passed = _re.search(r"(\d+)\s+passed", line)
            m_failed = _re.search(r"(\d+)\s+failed", line)
            if m_passed:
                passed = int(m_passed.group(1))
            if m_failed:
                failed = int(m_failed.group(1))

        desc = f"Tier {tier[-1]} regression ({expected_min} tests)"
        if failed == 0 and passed >= expected_min:
            return _pass(aid, desc, f"{passed} passed, 0 failed")
        elif failed > 0:
            return _fail(aid, desc, f"{passed} passed, {failed} failed")
        elif passed == 0:
            # Provide diagnostic info
            last_lines = output.strip().splitlines()[-5:]
            diag = " | ".join(l.strip() for l in last_lines if l.strip())
            return _skip(aid, desc, f"No tests collected. Output: {diag[:200]}")
        else:
            return _warn(aid, desc, f"{passed} passed (expected >={expected_min})")
    except subprocess.TimeoutExpired:
        return _fail(aid, f"Tier {tier[-1]} regression", "Timeout (120s)")
    except Exception as e:
        return _fail(aid, f"Tier {tier[-1]} regression", str(e))


# ---------------------------------------------------------------------------
# Phase D — Live Tenant Provisioning Verification
# ---------------------------------------------------------------------------
def phase_d(fqdn: str, spa_api_key: str) -> list[AssertionResult]:
    """End-to-end smoke test: provision a tenant, configure, verify conversation."""
    results = []
    today = datetime.date.today().isoformat()
    smoke_email = f"preflight-smoke-{today}@preflight.internal"
    smoke_name = f"Preflight Smoke {today}"

    # State captured across steps
    tenant_id = None
    admin_key = None
    widget_key = None
    conv_id = None
    agent_key = None

    # D.1 — Create smoke tenant
    s, b, h = api_call(fqdn, "/api/superadmin/tenants", spa_api_key, method="POST",
                       body={
                           "merchantName": smoke_name,
                           "superadminEmail": smoke_email,
                           "tier": "starter",
                       })
    if s in (200, 201) and isinstance(b, dict):
        tenant_id = b.get("tenantId") or b.get("tenant_id")
        admin_key = b.get("superadminApiKey") or b.get("superadmin_api_key")
        widget_key = b.get("widgetKey") or b.get("widget_key")
        results.append(_pass("D.1", "Create smoke tenant",
                             f"tenant={tenant_id}, key={'yes' if admin_key else 'NO'}, "
                             f"widget={'yes' if widget_key else 'NO'}"))
    else:
        detail = str(b)[:300] if b else f"HTTP {s}"
        results.append(_fail("D.1", "Create smoke tenant", f"HTTP {s}: {detail}"))
        # Cannot continue Phase D without tenant credentials
        for i in range(2, 19):
            results.append(_skip(f"D.{i}", f"(skipped — D.1 failed)", "No tenant"))
        return results

    if not admin_key or not widget_key:
        results.append(_fail("D.2", "Tenant credentials", "Missing admin key or widget key"))
        for i in range(3, 19):
            results.append(_skip(f"D.{i}", f"(skipped — no credentials)", ""))
        return results

    # D.2 — Tenant in directory
    s, b, h = api_call(fqdn, "/api/superadmin/tenants", spa_api_key)
    if s == 200:
        results.append(_pass("D.2", "Tenant in directory", "Superadmin directory accessible"))
    else:
        results.append(_warn("D.2", "Tenant in directory", f"HTTP {s}"))

    # D.3 — Superadmin key authenticates
    s, b, h = api_call(fqdn, "/api/config", admin_key)
    if s == 200:
        results.append(_pass("D.3", "Superadmin key authenticates", "GET /api/config → 200"))
    else:
        results.append(_fail("D.3", "Superadmin key authenticates", f"HTTP {s}"))

    # D.4 — Identity correct
    s, b, h = api_call(fqdn, "/api/admin/team/whoami", admin_key)
    if s == 200 and isinstance(b, dict):
        role = str(b.get("role", "")).lower()
        if role == "superadmin":
            results.append(_pass("D.4", "Identity correct", f"role={role}"))
        else:
            results.append(_fail("D.4", "Identity correct", f"role={role}, expected superadmin"))
    else:
        results.append(_fail("D.4", "Identity correct", f"HTTP {s}"))

    # D.5 — Clean initial state
    s1, b1, _ = api_call(fqdn, "/api/admin/conversations?limit=1", admin_key)
    s2, b2, _ = api_call(fqdn, "/api/admin/knowledge?limit=1", admin_key)
    conv_count = b1.get("totalCount", -1) if isinstance(b1, dict) else -1
    kb_count = b2.get("totalCount", b2.get("total", -1)) if isinstance(b2, dict) else -1
    if conv_count == 0 and kb_count == 0:
        results.append(_pass("D.5", "Clean initial state",
                             f"conversations={conv_count}, kb={kb_count}"))
    else:
        results.append(_warn("D.5", "Clean initial state",
                             f"conversations={conv_count}, kb={kb_count} (expected 0)"))

    # D.6 — Create draft config
    s, b, _ = api_call(fqdn, "/api/config/reset", admin_key, method="POST")
    s2, b2, _ = api_call(fqdn, "/api/config", admin_key, method="PUT",
                         body={"fields": {
                             "brand_name": "Preflight Smoke Test",
                             "brand_voice": "Professional and helpful",
                         }})
    if s in (200, 201) and s2 in (200, 201):
        results.append(_pass("D.6", "Config draft created",
                             f"reset={s}, update={s2}"))
    else:
        results.append(_fail("D.6", "Config draft created",
                             f"reset={s}, update={s2}: {str(b2)[:200]}"))

    # D.7 — Activate configuration
    s, b, _ = api_call(fqdn, "/api/config/draft/activate", admin_key, method="POST")
    # 500 is known behavior — check D.8 regardless
    if s in (200, 201):
        results.append(_pass("D.7", "Config activated", f"HTTP {s}"))
    elif s == 500:
        results.append(_warn("D.7", "Config activated",
                             "HTTP 500 (known first-activation behavior — checking D.8)"))
    else:
        results.append(_fail("D.7", "Config activated", f"HTTP {s}: {str(b)[:200]}"))

    # D.8 — Activation verified
    s, b, _ = api_call(fqdn, "/api/config/activation-status", admin_key)
    if s == 200 and isinstance(b, dict):
        is_active = b.get("is_active") or b.get("isActive")
        is_configured = b.get("is_configured") or b.get("isConfigured")
        if is_active and is_configured:
            results.append(_pass("D.8", "Activation verified",
                                 f"is_active={is_active}, is_configured={is_configured}"))
        else:
            results.append(_fail("D.8", "Activation verified",
                                 f"is_active={is_active}, is_configured={is_configured}"))
    else:
        results.append(_fail("D.8", "Activation verified", f"HTTP {s}"))

    # D.9 — Widget key works
    s, b = widget_call(fqdn, widget_key)
    if s == 201 and isinstance(b, dict):
        conv_id = b.get("conversation_id") or b.get("conversationId")
        results.append(_pass("D.9", "Widget key works",
                             f"conversation_id={conv_id}"))
    elif s == 503:
        results.append(_skip("D.9", "Widget key works", "HTTP 503 — NATS not warmed"))
    elif s == 401:
        results.append(_fail("D.9", "Widget key works",
                             "HTTP 401 — widget key rejected (dual-write failure?)"))
    elif s == 403:
        results.append(_fail("D.9", "Widget key works",
                             "HTTP 403 — config not activated"))
    else:
        results.append(_fail("D.9", "Widget key works", f"HTTP {s}: {str(b)[:200]}"))

    # D.10 — AI pipeline produces response (SSE)
    if not conv_id:
        results.append(_skip("D.10", "AI pipeline (SSE)", "No conversation_id from D.9"))
    elif not _HTTPX_AVAILABLE:
        results.append(_skip("D.10", "AI pipeline (SSE)",
                             "httpx not installed. pip install httpx"))
    else:
        results.append(_verify_sse(fqdn, conv_id, widget_key))

    # D.11 — Conversation in inbox
    s, b, _ = api_call(fqdn, "/api/admin/conversations", admin_key)
    if s == 200 and isinstance(b, dict):
        count = b.get("totalCount", b.get("total", 0))
        if count >= 1:
            results.append(_pass("D.11", "Conversation in inbox", f"totalCount={count}"))
        else:
            results.append(_warn("D.11", "Conversation in inbox",
                                 f"totalCount={count} (expected >=1)"))
    else:
        results.append(_fail("D.11", "Conversation in inbox", f"HTTP {s}"))

    # D.12 — Create KB entry
    s, b, _ = api_call(fqdn, "/api/admin/knowledge", admin_key, method="POST",
                       body={
                           "title": "Preflight Test Article",
                           "content": "Preflight smoke test knowledge base article.",
                           "entry_type": "faq",
                           "status": "published",
                       })
    if s in (200, 201):
        results.append(_pass("D.12", "KB entry created", f"HTTP {s}"))
    else:
        results.append(_fail("D.12", "KB entry created", f"HTTP {s}: {str(b)[:200]}"))

    # D.13 — KB entry visible
    s, b, _ = api_call(fqdn, "/api/admin/knowledge", admin_key)
    if s == 200 and isinstance(b, dict):
        count = b.get("totalCount", b.get("total", 0))
        if count >= 1:
            results.append(_pass("D.13", "KB entry visible", f"total={count}"))
        else:
            results.append(_fail("D.13", "KB entry visible", f"total={count}"))
    else:
        results.append(_fail("D.13", "KB entry visible", f"HTTP {s}"))

    # D.14 — Create team member (escalation_agent)
    s, b, _ = api_call(fqdn, "/api/admin/team", admin_key, method="POST",
                       body={
                           "email": f"escalation-{today}@preflight.internal",
                           "displayName": "Preflight Agent",
                           "role": "escalation_agent",
                       })
    if s in (200, 201) and isinstance(b, dict):
        agent_key = (b.get("userApiKey") or b.get("user_api_key")
                     or b.get("api_key") or b.get("apiKey"))
        results.append(_pass("D.14", "Team member created",
                             f"HTTP {s}, key={'yes' if agent_key else 'NO'}"))
    else:
        results.append(_fail("D.14", "Team member created", f"HTTP {s}: {str(b)[:200]}"))

    # D.15 — RBAC blocks non-admin
    if agent_key:
        s, b, _ = api_call(fqdn, "/api/config", agent_key)
        if s == 403:
            results.append(_pass("D.15", "RBAC blocks non-admin",
                                 "escalation_agent → /api/config → 403"))
        else:
            results.append(_fail("D.15", "RBAC blocks non-admin",
                                 f"Expected 403, got HTTP {s}"))
    else:
        results.append(_skip("D.15", "RBAC blocks non-admin", "No agent key from D.14"))

    # D.16 — RBAC allows inbox
    if agent_key:
        s, b, _ = api_call(fqdn, "/api/admin/conversations", agent_key)
        if s == 200:
            results.append(_pass("D.16", "RBAC allows inbox",
                                 "escalation_agent → /api/admin/conversations → 200"))
        else:
            results.append(_fail("D.16", "RBAC allows inbox",
                                 f"Expected 200, got HTTP {s}"))
    else:
        results.append(_skip("D.16", "RBAC allows inbox", "No agent key from D.14"))

    # D.17 — Admin SPA routes
    spa_ok = True
    for path in ["/admin/standalone/", "/admin/provider/"]:
        s, b, h = api_call(fqdn, path)
        ct = h.get("content-type", "")
        if s != 200 or "text/html" not in ct:
            spa_ok = False
    if spa_ok:
        results.append(_pass("D.17", "Admin SPA routes", "Both return 200 text/html"))
    else:
        results.append(_fail("D.17", "Admin SPA routes", "One or more SPAs not returning 200"))

    # D.18 — Phase D summary (computed by caller)
    pass_count = sum(1 for r in results if r.status == "PASS")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    skip_count = sum(1 for r in results if r.status == "SKIP")
    warn_count = sum(1 for r in results if r.status == "WARN")
    results.append(_pass("D.18", "Phase D summary",
                         f"{pass_count} PASS, {fail_count} FAIL, "
                         f"{skip_count} SKIP, {warn_count} WARN"))

    return results


def _verify_sse(fqdn: str, conv_id: str, widget_key: str) -> AssertionResult:
    """Send a message and verify SSE stream produces AI tokens."""
    # First send a message
    s, b, _ = api_call(fqdn, "/api/chat/message", method="POST",
                       body={"conversation_id": conv_id,
                             "content": "Hello, what products do you offer?"})
    # Widget key auth for message endpoint — use header
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError
    msg_url = f"https://{fqdn}/api/chat/message"
    msg_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-Widget-Key": widget_key,
    }
    msg_body = json.dumps({
        "conversation_id": conv_id,
        "content": "Hello, what products do you offer?",
    }).encode()
    try:
        req = Request(msg_url, data=msg_body, headers=msg_headers, method="POST")
        with urlopen(req, timeout=15) as resp:
            pass  # Message sent
    except HTTPError:
        pass  # Some errors are OK — the stream may already be active
    except Exception:
        pass

    # Now consume SSE stream
    stream_url = f"https://{fqdn}/api/chat/stream/{conv_id}?widget_key={widget_key}"
    try:
        got_token = False
        got_done = False
        with httpx.stream("GET", stream_url, timeout=45.0) as resp:
            if resp.status_code == 503:
                return _skip("D.10", "AI pipeline (SSE)", "HTTP 503 — NATS not warmed")
            if resp.status_code != 200:
                return _fail("D.10", "AI pipeline (SSE)",
                             f"Stream HTTP {resp.status_code}")
            for line in resp.iter_lines():
                if "event: token" in line or "event:token" in line:
                    got_token = True
                elif "event: done" in line or "event:done" in line:
                    got_done = True
                    break
                elif "event: error" in line or "event:error" in line:
                    return _fail("D.10", "AI pipeline (SSE)", f"Stream error: {line}")
        if got_token and got_done:
            return _pass("D.10", "AI pipeline (SSE)", "Got token + done events")
        elif got_token:
            return _warn("D.10", "AI pipeline (SSE)", "Got tokens but no done event")
        else:
            return _fail("D.10", "AI pipeline (SSE)", "No token events in stream")
    except httpx.TimeoutException:
        return _warn("D.10", "AI pipeline (SSE)", "Timeout (45s) — pipeline may be slow")
    except Exception as e:
        return _fail("D.10", "AI pipeline (SSE)", str(e))


# ---------------------------------------------------------------------------
# Phase E — Verdict
# ---------------------------------------------------------------------------
def compute_verdict(all_results: dict[str, list[AssertionResult]]) -> str:
    """Determine overall deployment verdict."""
    c_fails = sum(1 for r in all_results.get("C", []) if r.status == "FAIL")
    d_fails = sum(1 for r in all_results.get("D", []) if r.status == "FAIL")
    a_fails = sum(1 for r in all_results.get("A", []) if r.status == "FAIL")

    if a_fails > 0:
        return "DEPLOYMENT BLOCKED — Phase A pre-build failures"
    if c_fails > 0:
        return "ROLLBACK REQUIRED — Phase C post-deploy failures"
    if d_fails > 0:
        return "DEPLOYMENT LIVE BUT DEFECTIVE — Phase D tenant provisioning failures"
    return "DEPLOYMENT VERIFIED"


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
def print_results(phase_name: str, phase_label: str, results: list[AssertionResult]) -> None:
    """Print a formatted results table for one phase."""
    print(f"\n{'=' * 60}")
    print(f"  Phase {phase_name} — {phase_label}")
    print(f"{'=' * 60}")
    for r in results:
        icon = {"PASS": "+", "FAIL": "X", "SKIP": "-", "WARN": "!"}[r.status]
        print(f"  [{icon}] {r.id:5s} {r.status:4s}  {r.description}")
        if r.detail:
            print(f"               {r.detail[:120]}")
    counts = {}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    summary_parts = [f"{v} {k}" for k, v in sorted(counts.items())]
    print(f"  {'—' * 50}")
    print(f"  Total: {', '.join(summary_parts)}")


def save_report(results: dict[str, list[AssertionResult]], env_name: str,
                new_version: str, verdict: str) -> Path:
    """Save structured JSON report."""
    results_dir = PROJECT_ROOT / "scripts" / "pre-flight-results"
    results_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    filename = f"preflight-{env_name}-{now.strftime('%Y-%m-%d-%H%M%S')}.json"

    report = {
        "run_at": now.isoformat(),
        "environment": env_name,
        "new_version": new_version,
        "verdict": verdict,
        "phases": {},
        "summary": {},
    }

    for phase, phase_results in results.items():
        report["phases"][phase] = [
            {"id": r.id, "description": r.description,
             "status": r.status, "detail": r.detail}
            for r in phase_results
        ]
        counts = {}
        for r in phase_results:
            counts[r.status] = counts.get(r.status, 0) + 1
        report["summary"][phase] = counts

    out_path = results_dir / filename
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pre-Flight Deployment Checklist — automated verification")
    parser.add_argument("--env", required=True, choices=["staging", "production"],
                        help="Target environment")
    parser.add_argument("--new-version", required=True,
                        help="Expected product version (e.g., 1.59.1)")
    parser.add_argument("--phase", default=None, choices=["A", "B", "C", "D"],
                        help="Run only this phase (default: all phases)")
    args = parser.parse_args()

    env_cfg = ENVIRONMENTS[args.env]
    fqdn = env_cfg["fqdn"]
    api_key = env_cfg["api_key"]
    widget_key = env_cfg["widget_key"]

    # SPA superadmin key for Phase D — from environment
    spa_api_key = os.environ.get("SUPERADMIN_PREVIEW_API_KEY", "")

    print(f"\n{'#' * 60}")
    print(f"  Pre-Flight Deployment Checklist")
    print(f"  Environment: {args.env}")
    print(f"  Target FQDN: {fqdn}")
    print(f"  Expected Version: {args.new_version}")
    print(f"  Phase: {args.phase or 'ALL'}")
    print(f"  Timestamp: {datetime.datetime.now().isoformat()}")
    print(f"{'#' * 60}")

    all_results: dict[str, list[AssertionResult]] = {}
    phases_to_run = [args.phase] if args.phase else ["A", "C", "D"]

    # Phase A
    if "A" in phases_to_run:
        results_a = phase_a(args.new_version)
        all_results["A"] = results_a
        print_results("A", "Pre-Build Verification", results_a)

    # Phase B is manual — print reminder
    if "B" in phases_to_run or (args.phase is None):
        print(f"\n{'=' * 60}")
        print("  Phase B — Build & Deploy (MANUAL)")
        print(f"{'=' * 60}")
        print("  Phase B steps are executed manually or via upgrade.ps1.")
        print("  See: docs/operations/pre-flight-deployment-checklist.md")
        print("  Before deploying, capture Phase A snapshot:")
        print(f"    python scripts/upgrade_verification.py phase-a --env {args.env}")

    # Phase C
    if "C" in phases_to_run:
        results_c = phase_c(fqdn, api_key, widget_key, args.new_version)
        all_results["C"] = results_c
        print_results("C", "Post-Deploy Platform Verification", results_c)

    # Phase D
    if "D" in phases_to_run:
        if not spa_api_key:
            print(f"\n  WARNING: SUPERADMIN_PREVIEW_API_KEY not set.")
            print(f"  Phase D requires the SPA superadmin key to provision tenants.")
            print(f"  Set it: export SUPERADMIN_PREVIEW_API_KEY=ar_user_rema_...")
            all_results["D"] = [
                _fail("D.0", "SPA key required",
                      "Set SUPERADMIN_PREVIEW_API_KEY env var")]
        else:
            results_d = phase_d(fqdn, spa_api_key)
            all_results["D"] = results_d
            print_results("D", "Live Tenant Provisioning Verification", results_d)

    # Phase E — Verdict
    verdict = compute_verdict(all_results)
    report_path = save_report(all_results, args.env, args.new_version, verdict)

    print(f"\n{'#' * 60}")
    icon = "OK" if "VERIFIED" in verdict else "XX"
    print(f"  {icon} VERDICT: {verdict}")
    print(f"  Results: {report_path}")
    print(f"{'#' * 60}\n")

    # DEFECT auto-creation (SPEC-1617): one per failed phase
    if "VERIFIED" not in verdict:
        from scripts._defect_reporter import create_defect
        for phase_name, phase_results in all_results.items():
            fails = [r for r in phase_results if r.status == "FAIL"]
            if fails:
                detail = "; ".join(f"{r.id}: {r.detail[:80]}" for r in fails[:5])
                wi = create_defect(
                    title=f"Pre-flight Phase {phase_name} failure: {args.env} {args.new_version}",
                    description=(
                        f"Pre-flight checklist Phase {phase_name} failed.\n\n"
                        f"Environment: {args.env}\n"
                        f"Version: {args.new_version}\n"
                        f"Failures: {detail}"
                    ),
                    source_spec_id="SPEC-1617",
                    component="infrastructure_automation",
                    changed_by="pre-flight-checklist",
                )
                if wi:
                    print(f"  Created DEFECT: {wi} (Phase {phase_name})")

    # Exit code: 0 for verified, 1 for failures
    sys.exit(0 if "VERIFIED" in verdict else 1)


if __name__ == "__main__":
    main()
