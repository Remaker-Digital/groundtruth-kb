"""S133 Group B: Record test artifacts and update KB phases for live API tests.

GOV-12: Work item creation triggers test creation.
GOV-13: Tests assigned to PLAN-001 phases at creation.

New test artifacts:
  TEST-2974..2982  — 9 conversation quality tests (SPEC-1649, WI-1022)
  TEST-2983..2991  — 9 external verification tests (SPEC-1649, WI-1025)

Phase updates:
  PHASE-011 — Restored with live conversation quality tests (was REMOVED)
  PHASE-015 — Restored with live external verification tests (was REMOVED)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import json

sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()

# -------------------------------------------------------------------------
# Test artifacts for WI-1022: Conversation Quality (SPEC-1649)
# -------------------------------------------------------------------------
conv_tests = [
    (
        "TEST-2974",
        "SPEC-1649",
        "CQ-LIVE-01",
        "Widget.js accessible via GET /widget.js with 200 status",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestWidgetAPIAccessibility",
        "test_cq_live_01_widget_js_accessible",
    ),
    (
        "TEST-2975",
        "SPEC-1649",
        "CQ-LIVE-02",
        "Health endpoint returns healthy status",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestWidgetAPIAccessibility",
        "test_cq_live_02_health_endpoint_healthy",
    ),
    (
        "TEST-2976",
        "SPEC-1649",
        "CQ-LIVE-03",
        "POST /api/chat/conversations with valid widget key returns 201",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestConversationLifecycle",
        "test_cq_live_03_start_conversation",
    ),
    (
        "TEST-2977",
        "SPEC-1649",
        "CQ-LIVE-04",
        "Starting a conversation yields an AI-generated response",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestConversationLifecycle",
        "test_cq_live_04_conversation_returns_ai_response",
    ),
    (
        "TEST-2978",
        "SPEC-1649",
        "CQ-LIVE-05",
        "AI response has meaningful content (>=20 chars, no error markers)",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestConversationLifecycle",
        "test_cq_live_05_response_quality_non_trivial",
    ),
    (
        "TEST-2979",
        "SPEC-1649",
        "CQ-LIVE-06",
        "Invalid widget key is rejected with 401/403",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestConversationLifecycle",
        "test_cq_live_06_invalid_widget_key_rejected",
    ),
    (
        "TEST-2980",
        "SPEC-1649",
        "CQ-LIVE-07",
        "Missing widget key is rejected with 401/403",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestConversationLifecycle",
        "test_cq_live_07_missing_widget_key_rejected",
    ),
    (
        "TEST-2981",
        "SPEC-1649",
        "CQ-LIVE-08",
        "AI response is valid UTF-8 text with real words",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestResponseContentQuality",
        "test_cq_live_08_response_is_utf8_text",
    ),
    (
        "TEST-2982",
        "SPEC-1649",
        "CQ-LIVE-09",
        "Conversation ID is a valid format (UUID or similar)",
        "requirement",
        "tests/live_api/test_conversation_quality_live.py",
        "TestResponseContentQuality",
        "test_cq_live_09_conversation_id_format",
    ),
]

# -------------------------------------------------------------------------
# Test artifacts for WI-1025: External Verification (SPEC-1649)
# -------------------------------------------------------------------------
ext_tests = [
    (
        "TEST-2983",
        "SPEC-1649",
        "EV-LIVE-01",
        "Documentation site (agentredcx.com) returns HTTP 200",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestDocumentationSite",
        "test_ev_live_01_docs_site_reachable",
    ),
    (
        "TEST-2984",
        "SPEC-1649",
        "EV-LIVE-02",
        "Docs site serves HTML content > 500 bytes",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestDocumentationSite",
        "test_ev_live_02_docs_site_has_content",
    ),
    (
        "TEST-2985",
        "SPEC-1649",
        "EV-LIVE-03",
        "Docs site references Agent Red brand",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestDocumentationSite",
        "test_ev_live_03_docs_site_contains_brand",
    ),
    (
        "TEST-2986",
        "SPEC-1649",
        "EV-LIVE-04",
        "Health endpoint returns JSON with status and version fields",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestPlatformPublicEndpoints",
        "test_ev_live_04_health_structure",
    ),
    (
        "TEST-2987",
        "SPEC-1649",
        "EV-LIVE-05",
        "Ready endpoint returns JSON with status field",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestPlatformPublicEndpoints",
        "test_ev_live_05_ready_endpoint_structure",
    ),
    (
        "TEST-2988",
        "SPEC-1649",
        "EV-LIVE-06",
        "OpenAPI spec accessible and returns valid JSON",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestPlatformPublicEndpoints",
        "test_ev_live_06_openapi_spec_accessible",
    ),
    (
        "TEST-2989",
        "SPEC-1649",
        "EV-LIVE-07",
        "Widget.js accessible without authentication",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestPlatformPublicEndpoints",
        "test_ev_live_07_widget_js_public",
    ),
    (
        "TEST-2990",
        "SPEC-1649",
        "EV-LIVE-08",
        "Admin SPAs serve HTML content (standalone, shopify, provider)",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestAdminSPAAccessibility",
        "test_ev_live_08_admin_spa_serves_html",
    ),
    (
        "TEST-2991",
        "SPEC-1649",
        "EV-LIVE-09",
        "Security headers (nosniff, X-Frame-Options) present",
        "requirement",
        "tests/live_api/test_external_urls_live.py",
        "TestSecurityHeaders",
        "test_ev_live_09_security_headers_present",
    ),
]

# -------------------------------------------------------------------------
# Insert all test artifacts
# -------------------------------------------------------------------------
all_tests = conv_tests + ext_tests
for test_id, spec_id, assertion_id, description, test_type, test_file, test_class, test_function in all_tests:
    kdb.insert_test(
        id=test_id,
        title=description,
        spec_id=spec_id,
        test_type=test_type,
        expected_outcome=f"{assertion_id}: PASS when verified against live staging/production API",
        changed_by="S133",
        change_reason=f"GOV-12: test creation for live API replacement ({spec_id}, WI-1022/WI-1025)",
        description=f"Assertion {assertion_id} from {spec_id}. {description}",
        test_file=test_file,
        test_class=test_class,
        test_function=test_function,
    )
    print(f"{test_id} created ({assertion_id})")

print(f"\n{len(all_tests)} test artifacts created (TEST-2974..TEST-2991)")

# -------------------------------------------------------------------------
# Update PHASE-011: Restore with live conversation quality tests
# -------------------------------------------------------------------------
conv_test_ids = [t[0] for t in conv_tests]
kdb.update_test_plan_phase(
    id="PHASE-011",
    changed_by="S133",
    change_reason="SPEC-1649/WI-1022: Restore Phase 11 with live conversation quality tests (replaces MOCKED_UNIT)",
    description="Live conversation quality tests — widget API conversation flow (9 tests via test_conversation_quality_live.py). Replaces mocked evaluation framework.",
    test_ids=conv_test_ids,  # Raw Python list — KB method calls json.dumps() internally
    last_result="PENDING",
)
print(f"\nPHASE-011: restored with {len(conv_test_ids)} live tests")

# -------------------------------------------------------------------------
# Update PHASE-015: Restore with live external verification tests
# -------------------------------------------------------------------------
ext_test_ids = [t[0] for t in ext_tests]
kdb.update_test_plan_phase(
    id="PHASE-015",
    changed_by="S133",
    change_reason="SPEC-1649/WI-1025: Restore Phase 15 with live external verification tests (replaces SOURCE_INSPECTION)",
    description="Live external verification tests — URL reachability, public endpoints, security headers (9 tests via test_external_urls_live.py). Replaces source inspection.",
    test_ids=ext_test_ids,  # Raw Python list
    last_result="PENDING",
)
print(f"PHASE-015: restored with {len(ext_test_ids)} live tests")

# -------------------------------------------------------------------------
# Resolve WI-1022 and WI-1025
# -------------------------------------------------------------------------
for wi_id, desc in [
    (
        "WI-1022",
        "Resolved: Live conversation quality tests created (9 tests in tests/live_api/test_conversation_quality_live.py). Phase 11 restored in pipeline.",
    ),
    (
        "WI-1025",
        "Resolved: Live external verification tests created (9 tests in tests/live_api/test_external_urls_live.py). Phase 15 restored in pipeline.",
    ),
]:
    try:
        kdb.update_work_item(
            id=wi_id,
            changed_by="S133",
            change_reason=desc,
            resolution_status="resolved",
            stage="resolved",
        )
        print(f"{wi_id}: resolved")
    except Exception as e:
        print(f"{wi_id}: update failed: {e}")

# -------------------------------------------------------------------------
# Verify final state
# -------------------------------------------------------------------------
print("\n--- PLAN-001 Phase Summary (post-Group B) ---")
phases = kdb.list_test_plan_phases("PLAN-001")
for p in phases:
    tids = json.loads(p["test_ids"]) if p["test_ids"] else []
    status = "ACTIVE" if tids else "REMOVED"
    print(f"  {p['id']:10s} | {p['title']:45s} | {len(tids):4d} tests | {status}")

active_phases = [p for p in phases if (json.loads(p["test_ids"]) if p["test_ids"] else [])]
removed_phases = [p for p in phases if not (json.loads(p["test_ids"]) if p["test_ids"] else [])]
print(f"\nActive: {len(active_phases)} phases")
print(f"Removed: {len(removed_phases)} phases")
