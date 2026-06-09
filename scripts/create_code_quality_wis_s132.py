#!/usr/bin/env python3
"""Create KB artifacts for code quality review findings (S132).

External code quality review dated 2026-03-02 identified 7 findings.
This script creates specs, work items, tests, and assigns to PLAN-001.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
import db  # noqa: E402

kdb = db.KnowledgeDB()
BY = "S132"
REASON = "Code quality review findings — external audit 2026-03-02"

# ============================================================
# 1. SPECIFICATIONS (SPEC-1621..1627)
# ============================================================

specs = [
    dict(
        id="SPEC-1621",
        title="PreAuth rate limiter must record auth failures",
        description=(
            "When TenantAuthMiddleware catches an AuthenticationError, it MUST call "
            "get_pre_auth_limiter().record_failure(client_ip) before returning the error response. "
            "Without this wiring, the PreAuthRateLimitMiddleware is_blocked() check is inert. "
            "Source: external code quality review 2026-03-02, Section 5.1."
        ),
        status="specified",
        priority="P0",
        section="SECURITY",
        scope="src/multi_tenant/middleware.py",
        assertions=[
            dict(
                description="AuthenticationError handler calls record_failure(client_ip)",
                type="grep",
                pattern="record_failure",
                target="src/multi_tenant/middleware.py",
            )
        ],
    ),
    dict(
        id="SPEC-1622",
        title="SMTP sends must not block the async event loop",
        description=(
            "All smtplib.SMTP / SMTP_SSL usage in async code paths MUST be offloaded via "
            "asyncio.to_thread() or replaced with aiosmtplib. Currently 11 modules use blocking "
            "SMTP directly. Affected: standalone_auth, magic_link_auth, trial_expiry_email, "
            "access_expiry_email, admin_apikey_api, admin_contact_api, widget_otp_verification, "
            "email_verification, welcome_email, alert_delivery (SMTP path). "
            "Source: external code quality review 2026-03-02, Sections 2.1 and 7.4."
        ),
        status="specified",
        priority="P1",
        section="INFRASTRUCTURE",
        scope="src/multi_tenant/, src/app/standalone_auth.py",
    ),
    dict(
        id="SPEC-1623",
        title="PreAuth tracker must schedule periodic cleanup",
        description=(
            "PreAuthRateLimiter.cleanup() exists but is never called. The _trackers dict grows "
            "unbounded with each unique failing IP. A background task or periodic timer must call "
            "cleanup() to remove expired entries. "
            "Source: external code quality review 2026-03-02, Section 4.2."
        ),
        status="specified",
        priority="P3",
        section="SECURITY",
        scope="src/multi_tenant/security_hardening.py",
        assertions=[
            dict(
                description="cleanup() is called from a background task or startup handler",
                type="grep",
                pattern=r"cleanup\(\)",
                target="src/",
            )
        ],
    ),
    dict(
        id="SPEC-1624",
        title="Migrate on_event() to FastAPI lifespan context manager",
        description=(
            "FastAPI app.on_event() is deprecated. The codebase has 57 registrations across "
            "lifecycle.py, background.py, agent_app.py, nats_isolation.py, otel_tracing.py. "
            "Migrate to the lifespan context manager pattern. "
            "Source: external code quality review 2026-03-02, Section 12.2."
        ),
        status="specified",
        priority="P3",
        section="INFRASTRUCTURE",
        scope="src/app/lifecycle.py, src/app/background.py",
    ),
    dict(
        id="SPEC-1625",
        title="TenantGate acquire() should use asyncio.Lock for queue check",
        description=(
            "_TenantGate.acquire() checks _semaphore.locked() and _waiting >= _queue_depth then "
            "increments _waiting without a lock. Not exploitable in cooperative asyncio but "
            "wrapping in asyncio.Lock is defensive best practice. "
            "Source: external code quality review 2026-03-02, Section 6.2. "
            "Priority downgraded from P2 to P4."
        ),
        status="specified",
        priority="P4",
        section="INFRASTRUCTURE",
        scope="src/multi_tenant/pipeline_resilience.py",
    ),
    dict(
        id="SPEC-1626",
        title="Rate limiting should support distributed backends for horizontal scaling",
        description=(
            "In-memory rate limiting (middleware sliding window, pre-auth tracker, tenant "
            "concurrency gates) is per-process only. For horizontal scaling beyond 2 replicas, "
            "these should be backed by Redis or Cosmos atomic counters. Current single-replica "
            "handles 680 tenants. "
            "Source: external code quality review 2026-03-02, Sections 10.1-10.3."
        ),
        status="specified",
        priority="P4",
        section="INFRASTRUCTURE",
        scope="src/multi_tenant/middleware.py, security_hardening.py, pipeline_resilience.py",
    ),
    dict(
        id="SPEC-1627",
        title="Repository module naming should use consistent plural convention",
        description=(
            "repository.py (singular, TenantRepository) vs repositories/ (plural, "
            "TenantScopedRepository) is inconsistent. Consolidate naming. "
            "Source: external code quality review 2026-03-02, Section 2.3."
        ),
        status="specified",
        priority="P4",
        section="INFRASTRUCTURE",
        scope="src/multi_tenant/repository.py, src/multi_tenant/repositories/",
    ),
]

print("Creating specifications...")
for s in specs:
    kdb.insert_spec(
        id=s["id"],
        title=s["title"],
        status=s["status"],
        changed_by=BY,
        change_reason=REASON,
        description=s["description"],
        priority=s.get("priority"),
        scope=s.get("scope"),
        section=s.get("section"),
        assertions=s.get("assertions"),
    )
    print(f"  {s['id']}: {s['title']}")

print(f"\n  7 specs created (SPEC-1621..1627)\n")

# ============================================================
# 2. WORK ITEMS (WI-0980..0986)
# ============================================================

wis = [
    dict(
        id="WI-0980",
        title="Wire PreAuth record_failure() on auth failure",
        origin="defect",
        component="infrastructure_automation",
        priority="P0",
        source_spec_id="SPEC-1621",
        failure_description=(
            "PreAuthRateLimitMiddleware checks is_blocked() but record_failure() is never called "
            "when TenantAuthMiddleware catches AuthenticationError. Brute-force protection is inert."
        ),
        description=(
            "In middleware.py dispatch(), add get_pre_auth_limiter().record_failure(client_ip) "
            "in both the AuthenticationError and generic Exception handlers. "
            "Also add record_success() on successful auth to reset counters."
        ),
    ),
    dict(
        id="WI-0981",
        title="Offload all SMTP sends to asyncio.to_thread()",
        origin="defect",
        component="external_integration",
        priority="P1",
        source_spec_id="SPEC-1622",
        failure_description=(
            "11 modules use blocking smtplib in async code paths, blocking the event loop for 1-10s per send."
        ),
        description=(
            "Wrap each smtplib send block in asyncio.to_thread(). Affected: standalone_auth, "
            "magic_link_auth, trial_expiry_email, access_expiry_email, admin_apikey_api, "
            "admin_contact_api, widget_otp_verification, email_verification, welcome_email, "
            "alert_delivery SMTP path."
        ),
    ),
    dict(
        id="WI-0982",
        title="Schedule periodic PreAuth tracker cleanup",
        origin="defect",
        component="infrastructure_automation",
        priority="P3",
        source_spec_id="SPEC-1623",
        failure_description=("PreAuthRateLimiter.cleanup() exists but is never called. Memory grows unbounded."),
        description=(
            "Add a background task in lifecycle.py startup that calls "
            "get_pre_auth_limiter().cleanup() periodically (every 5-10 minutes)."
        ),
    ),
    dict(
        id="WI-0983",
        title="Migrate on_event() handlers to FastAPI lifespan",
        origin="hygiene",
        component="infrastructure_automation",
        priority="P3",
        source_spec_id="SPEC-1624",
        description=(
            "Replace 57 app.on_event() registrations with a single async lifespan context "
            "manager. Affects lifecycle.py, background.py, agent_app.py, nats_isolation.py, "
            "otel_tracing.py."
        ),
    ),
    dict(
        id="WI-0984",
        title="Add asyncio.Lock to TenantGate acquire() queue check",
        origin="hygiene",
        component="infrastructure_automation",
        priority="P4",
        source_spec_id="SPEC-1625",
        description=(
            "Wrap the semaphore.locked() check and _waiting increment in an asyncio.Lock for defensive robustness."
        ),
    ),
    dict(
        id="WI-0985",
        title="Design distributed rate limiting for horizontal scaling",
        origin="new",
        component="infrastructure_automation",
        priority="P4",
        source_spec_id="SPEC-1626",
        description=(
            "Replace in-memory rate limiting with Redis or Cosmos-backed distributed "
            "alternatives. Required when scaling beyond 2 replicas."
        ),
    ),
    dict(
        id="WI-0986",
        title="Consolidate repository module naming convention",
        origin="hygiene",
        component="infrastructure_automation",
        priority="P4",
        source_spec_id="SPEC-1627",
        description=(
            "Rename repository.py to repositories/tenant.py or consolidate all into repositories/. Update all imports."
        ),
    ),
]

print("Creating work items...")
for w in wis:
    kdb.insert_work_item(
        id=w["id"],
        title=w["title"],
        origin=w["origin"],
        component=w["component"],
        resolution_status="open",
        changed_by=BY,
        change_reason=REASON,
        description=w.get("description"),
        source_spec_id=w.get("source_spec_id"),
        failure_description=w.get("failure_description"),
        priority=w.get("priority"),
        stage="created",
    )
    print(f"  {w['id']}: {w['title']}")

print(f"\n  7 work items created (WI-0980..0986)\n")

# ============================================================
# 3. TEST ARTIFACTS (TEST-2948..2954) — GOV-12
# ============================================================

tests = [
    dict(
        id="TEST-2948",
        title="Auth failure calls PreAuth record_failure()",
        spec_id="SPEC-1621",
        test_type="unit",
        expected_outcome=(
            "When TenantAuthMiddleware catches AuthenticationError, "
            "get_pre_auth_limiter().record_failure(client_ip) is called. "
            "Verify via mock: pre_auth_limiter.record_failure.assert_called_with(ip)."
        ),
    ),
    dict(
        id="TEST-2949",
        title="SMTP sends are wrapped in asyncio.to_thread()",
        spec_id="SPEC-1622",
        test_type="assertion",
        expected_outcome=(
            "No direct smtplib.SMTP/SMTP_SSL usage outside asyncio.to_thread() in async "
            "functions. Source grep: all smtplib calls are inside to_thread() wrappers."
        ),
    ),
    dict(
        id="TEST-2950",
        title="PreAuth cleanup() is periodically invoked",
        spec_id="SPEC-1623",
        test_type="unit",
        expected_outcome=(
            "A background task or periodic timer calls PreAuthRateLimiter.cleanup(). "
            "Verify via grep: cleanup() call site exists in startup/background code."
        ),
    ),
    dict(
        id="TEST-2951",
        title="No deprecated on_event() registrations remain",
        spec_id="SPEC-1624",
        test_type="assertion",
        expected_outcome=(
            "Zero occurrences of app.on_event() in src/. All startup/shutdown logic uses the lifespan context manager."
        ),
    ),
    dict(
        id="TEST-2952",
        title="TenantGate acquire() uses asyncio.Lock for queue check",
        spec_id="SPEC-1625",
        test_type="assertion",
        expected_outcome=(
            "_TenantGate.acquire() wraps the semaphore check and _waiting increment "
            "in an asyncio.Lock. Source inspection confirms Lock usage."
        ),
    ),
    dict(
        id="TEST-2953",
        title="Rate limiting supports distributed backend",
        spec_id="SPEC-1626",
        test_type="integration",
        expected_outcome=(
            "Rate limiting state is persisted in a shared backend (Redis/Cosmos). "
            "Two concurrent processes share rate limit counters."
        ),
    ),
    dict(
        id="TEST-2954",
        title="Repository modules follow consistent naming convention",
        spec_id="SPEC-1627",
        test_type="assertion",
        expected_outcome=(
            "All repository modules use consistent plural naming (repositories/). "
            "No singular repository.py exists at module level."
        ),
    ),
]

print("Creating test artifacts...")
for t in tests:
    kdb.insert_test(
        id=t["id"],
        title=t["title"],
        spec_id=t["spec_id"],
        test_type=t["test_type"],
        expected_outcome=t["expected_outcome"],
        changed_by=BY,
        change_reason=REASON,
    )
    print(f"  {t['id']}: {t['title']}")

print(f"\n  7 tests created (TEST-2948..2954)\n")

# ============================================================
# 4. ASSIGN TO PLAN PHASES — GOV-13
# ============================================================

print("Assigning tests to PHASE-002...")
phase = kdb.get_test_plan_phase("PHASE-002")
existing_ids = json.loads(phase["test_ids"]) if phase and phase["test_ids"] else []
new_test_ids = [f"TEST-{n}" for n in range(2948, 2955)]
updated_ids = existing_ids + new_test_ids

kdb.update_test_plan_phase(
    "PHASE-002",
    changed_by=BY,
    change_reason="Add 7 code quality review test artifacts (TEST-2948..2954)",
    test_ids=updated_ids,
)
print(f"  PHASE-002: {len(existing_ids)} -> {len(updated_ids)} test IDs\n")

print("DONE: 7 specs, 7 WIs, 7 tests, phase assignment complete.")
