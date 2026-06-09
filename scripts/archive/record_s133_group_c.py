"""S133 Group C: Record KB artifacts for live E2E expansion + widget embed tests.

Creates TEST-2992..3016 (25 test artifacts):
  - 4 Knowledge Base page tests (KB-LIVE-01..04)
  - 3 Quick Actions page tests (QA-LIVE-01..03)
  - 3 Integrations page tests (INT-LIVE-01..03)
  - 3 Memory & Privacy page tests (MEM-LIVE-01..03)
  - 4 Billing page tests (BILL-LIVE-01..04)
  - 8 Widget Embed tests (WE-LIVE-01..08)

Phase updates:
  - PHASE-003: Add 17 new e2e_live tests to existing 58
  - PHASE-016: Restore with 8 live widget embed tests (un-REMOVE)

WI resolution:
  - WI-1023: Resolve (expand e2e_live to cover all admin pages)
  - WI-1026: Resolve (live widget E2E against staging)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import json

sys.path.insert(0, "tools/knowledge-db")
import db

kdb = db.KnowledgeDB()

# ─────────────────────────────────────────────────────────────
# 1. Record test artifacts: e2e_live Playwright tests (17)
# ─────────────────────────────────────────────────────────────

e2e_live_tests = [
    # Knowledge Base page (test_knowledge_base_live.py)
    (
        "TEST-2992",
        "SPEC-1649",
        "KB-LIVE-01: Knowledge base page shows heading",
        "Verify the Knowledge Base admin page renders with correct heading via live Playwright.",
        "e2e",
        "tests/e2e_live/test_knowledge_base_live.py::TestKBPageStructure::test_kb_live_01_page_heading",
    ),
    (
        "TEST-2993",
        "SPEC-1649",
        "KB-LIVE-02: Knowledge base page shows article list",
        "Verify KB page displays articles or empty state message.",
        "e2e",
        "tests/e2e_live/test_knowledge_base_live.py::TestKBPageStructure::test_kb_live_02_article_list_present",
    ),
    (
        "TEST-2994",
        "SPEC-1649",
        "KB-LIVE-03: Knowledge base page has add button",
        "Verify KB page has an Add/Create/New article button.",
        "e2e",
        "tests/e2e_live/test_knowledge_base_live.py::TestKBPageStructure::test_kb_live_03_add_button_visible",
    ),
    (
        "TEST-2995",
        "SPEC-1649",
        "KB-LIVE-04: Knowledge base page has search input",
        "Verify KB page has a search/filter input field.",
        "e2e",
        "tests/e2e_live/test_knowledge_base_live.py::TestKBPageStructure::test_kb_live_04_search_input_present",
    ),
    # Quick Actions page (test_quick_actions_live.py)
    (
        "TEST-2996",
        "SPEC-1649",
        "QA-LIVE-01: Quick actions page shows heading",
        "Verify Quick Actions admin page renders with correct heading.",
        "e2e",
        "tests/e2e_live/test_quick_actions_live.py::TestQuickActionsPageStructure::test_qa_live_01_page_heading",
    ),
    (
        "TEST-2997",
        "SPEC-1649",
        "QA-LIVE-02: Quick actions list or empty state",
        "Verify Quick Actions page shows action items or empty state.",
        "e2e",
        "tests/e2e_live/test_quick_actions_live.py::TestQuickActionsPageStructure::test_qa_live_02_action_list_or_empty",
    ),
    (
        "TEST-2998",
        "SPEC-1649",
        "QA-LIVE-03: Quick actions add button present",
        "Verify Quick Actions page has Add/Create button.",
        "e2e",
        "tests/e2e_live/test_quick_actions_live.py::TestQuickActionsPageStructure::test_qa_live_03_add_action_button",
    ),
    # Integrations page (test_integrations_live.py)
    (
        "TEST-2999",
        "SPEC-1649",
        "INT-LIVE-01: Integrations page loads",
        "Verify Integrations admin page loads with heading or main content.",
        "e2e",
        "tests/e2e_live/test_integrations_live.py::TestIntegrationsPageStructure::test_int_live_01_page_loads",
    ),
    (
        "TEST-3000",
        "SPEC-1649",
        "INT-LIVE-02: Integrations page has items",
        "Verify Integrations page displays integration options or cards.",
        "e2e",
        "tests/e2e_live/test_integrations_live.py::TestIntegrationsPageStructure::test_int_live_02_has_integration_items",
    ),
    (
        "TEST-3001",
        "SPEC-1649",
        "INT-LIVE-03: Integrations page no error state",
        "Verify Integrations page has no error message banner.",
        "e2e",
        "tests/e2e_live/test_integrations_live.py::TestIntegrationsPageStructure::test_int_live_03_no_error_state",
    ),
    # Memory & Privacy page (test_memory_live.py)
    (
        "TEST-3002",
        "SPEC-1649",
        "MEM-LIVE-01: Memory page shows heading",
        "Verify Memory & Privacy admin page renders with correct heading.",
        "e2e",
        "tests/e2e_live/test_memory_live.py::TestMemoryPageStructure::test_mem_live_01_page_heading",
    ),
    (
        "TEST-3003",
        "SPEC-1649",
        "MEM-LIVE-02: Memory page has settings sections",
        "Verify Memory page displays settings content (privacy, retention, etc.).",
        "e2e",
        "tests/e2e_live/test_memory_live.py::TestMemoryPageStructure::test_mem_live_02_has_settings",
    ),
    (
        "TEST-3004",
        "SPEC-1649",
        "MEM-LIVE-03: Memory page has toggle or input controls",
        "Verify Memory page has interactive controls (toggles, checkboxes, inputs).",
        "e2e",
        "tests/e2e_live/test_memory_live.py::TestMemoryPageStructure::test_mem_live_03_has_toggle_or_input",
    ),
    # Billing page (test_billing_live.py)
    (
        "TEST-3005",
        "SPEC-1649",
        "BILL-LIVE-01: Billing page shows heading",
        "Verify Billing admin page renders with heading.",
        "e2e",
        "tests/e2e_live/test_billing_live.py::TestBillingPageStructure::test_bill_live_01_page_heading",
    ),
    (
        "TEST-3006",
        "SPEC-1649",
        "BILL-LIVE-02: Billing page shows plan info",
        "Verify Billing page displays plan tier or subscription information.",
        "e2e",
        "tests/e2e_live/test_billing_live.py::TestBillingPageStructure::test_bill_live_02_plan_info_displayed",
    ),
    (
        "TEST-3007",
        "SPEC-1649",
        "BILL-LIVE-03: Billing page shows usage metrics",
        "Verify Billing page displays usage metrics or conversation stats.",
        "e2e",
        "tests/e2e_live/test_billing_live.py::TestBillingPageStructure::test_bill_live_03_usage_metrics_present",
    ),
    (
        "TEST-3008",
        "SPEC-1649",
        "BILL-LIVE-04: Billing page has manage buttons",
        "Verify Billing page has management action buttons (Manage, Upgrade, etc.).",
        "e2e",
        "tests/e2e_live/test_billing_live.py::TestBillingPageStructure::test_bill_live_04_manage_buttons_present",
    ),
]

# ─────────────────────────────────────────────────────────────
# 2. Record test artifacts: Widget embed live tests (8)
# ─────────────────────────────────────────────────────────────

widget_embed_tests = [
    (
        "TEST-3009",
        "SPEC-1649",
        "WE-LIVE-01: Widget.js serves JavaScript content-type",
        "Verify /widget.js returns HTTP 200 with JavaScript content-type.",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetBundleIntegrity::test_we_live_01_widget_js_serves_javascript",
    ),
    (
        "TEST-3010",
        "SPEC-1649",
        "WE-LIVE-02: Widget bundle has runtime markers",
        "Verify widget.js contains expected runtime code (shadowRoot, AgentRed, createElement).",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetBundleIntegrity::test_we_live_02_widget_bundle_has_runtime",
    ),
    (
        "TEST-3011",
        "SPEC-1649",
        "WE-LIVE-03: Widget bundle minimum size",
        "Verify widget.js is between 5KB and 500KB (not empty/corrupt).",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetBundleIntegrity::test_we_live_03_widget_bundle_minimum_size",
    ),
    (
        "TEST-3012",
        "SPEC-1649",
        "WE-LIVE-04: Widget config accessible via widget key",
        "Verify /api/tenants/lookup responds 200 to valid widget key.",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetConfigEndpoint::test_we_live_04_widget_config_accessible",
    ),
    (
        "TEST-3013",
        "SPEC-1649",
        "WE-LIVE-05: Widget config has appearance settings",
        "Verify widget config contains appearance fields (color, position, gradient, etc.).",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetConfigEndpoint::test_we_live_05_widget_config_has_appearance",
    ),
    (
        "TEST-3014",
        "SPEC-1649",
        "WE-LIVE-06: Invalid widget key rejected",
        "Verify /api/tenants/lookup rejects invalid widget key with 401/403/404.",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetConfigEndpoint::test_we_live_06_invalid_widget_key_rejected",
    ),
    (
        "TEST-3015",
        "SPEC-1649",
        "WE-LIVE-07: Widget.js responds with CORS headers",
        "Verify /widget.js CORS support for cross-origin embedding.",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetCORSHeaders::test_we_live_07_widget_js_cors",
    ),
    (
        "TEST-3016",
        "SPEC-1649",
        "WE-LIVE-08: Chat API responds to OPTIONS preflight",
        "Verify /api/chat/conversations responds to OPTIONS preflight requests.",
        "integration",
        "tests/live_api/test_widget_embed_live.py::TestWidgetCORSHeaders::test_we_live_08_chat_api_cors",
    ),
]

# ─────────────────────────────────────────────────────────────
# 3. Insert all test artifacts
# ─────────────────────────────────────────────────────────────

all_tests = e2e_live_tests + widget_embed_tests
for test_id, spec_id, title, desc, test_type, node_id in all_tests:
    # Decompose pytest node ID: file::class::function
    parts = node_id.split("::")
    t_file = parts[0] if len(parts) >= 1 else None
    t_class = parts[1] if len(parts) >= 2 else None
    t_func = parts[2] if len(parts) >= 3 else None
    kdb.insert_test(
        id=test_id,
        spec_id=spec_id,
        title=title,
        description=desc,
        test_type=test_type,
        expected_outcome="PASS",
        test_file=t_file,
        test_class=t_class,
        test_function=t_func,
        changed_by="S133",
        change_reason="SPEC-1649: Live E2E expansion (Group C).",
    )
    print(f"  {test_id}: {title[:60]}")

print(f"\nInserted {len(all_tests)} test artifacts (TEST-2992..3016)")

# ─────────────────────────────────────────────────────────────
# 4. Update PHASE-003: Add 17 e2e_live tests to existing list
# ─────────────────────────────────────────────────────────────

# Get current Phase 3 test_ids
conn = kdb._get_conn()
row = conn.execute("SELECT test_ids FROM current_test_plan_phases WHERE id='PHASE-003'").fetchone()
current_phase3_ids = json.loads(row["test_ids"]) if row and row["test_ids"] else []

new_e2e_ids = [t[0] for t in e2e_live_tests]  # TEST-2992..3008
updated_phase3_ids = current_phase3_ids + new_e2e_ids

kdb.update_test_plan_phase(
    id="PHASE-003",
    changed_by="S133",
    change_reason="SPEC-1649 Group C: Add 17 live E2E tests for uncovered admin pages (KB, Quick Actions, Integrations, Memory, Billing).",
    test_ids=updated_phase3_ids,  # Raw Python list
)
print(f"\nPHASE-003: {len(current_phase3_ids)} -> {len(updated_phase3_ids)} tests (+{len(new_e2e_ids)})")

# ─────────────────────────────────────────────────────────────
# 5. Restore PHASE-016 with live widget embed tests
# ─────────────────────────────────────────────────────────────

widget_test_ids = [t[0] for t in widget_embed_tests]  # TEST-3009..3016

kdb.update_test_plan_phase(
    id="PHASE-016",
    changed_by="S133",
    change_reason="SPEC-1649 Group C: Restore Phase 16 with live widget embed tests (replacing removed SOURCE_INSPECTION + VISUAL_WIDGET).",
    description="Live widget embed verification (8 tests via test_widget_embed_live.py). Verifies widget.js bundle, config endpoint, CORS headers.",
    test_ids=widget_test_ids,  # Raw Python list
    last_result="PENDING",
)
print(f"PHASE-016: RESTORED with {len(widget_test_ids)} live widget embed tests")

# ─────────────────────────────────────────────────────────────
# 6. Resolve WIs
# ─────────────────────────────────────────────────────────────

# WI-1023: transition created -> tested -> backlogged -> implementing -> resolved
for wi_id, title_suffix in [("WI-1023", "e2e_live expansion"), ("WI-1026", "widget embed E2E")]:
    try:
        kdb.update_work_item(
            id=wi_id,
            changed_by="S133",
            change_reason=f"SPEC-1649: Tests created for {title_suffix}.",
            stage="tested",
        )
        kdb.update_work_item(
            id=wi_id,
            changed_by="S133",
            change_reason=f"SPEC-1649: Added to backlog for implementation.",
            stage="backlogged",
        )
        kdb.update_work_item(
            id=wi_id,
            changed_by="S133",
            change_reason=f"SPEC-1649: Implementing {title_suffix}.",
            stage="implementing",
        )
        kdb.update_work_item(
            id=wi_id,
            changed_by="S133",
            change_reason=f"SPEC-1649: {title_suffix} complete — tests created + phase updated.",
            stage="resolved",
            resolution_status="done",
            owner_approved=True,  # GOV-15: owner approved all Group C work
        )
        print(f"{wi_id}: resolved (created -> tested -> backlogged -> implementing -> resolved)")
    except Exception as e:
        print(f"{wi_id}: ERROR — {e}")

# ─────────────────────────────────────────────────────────────
# 7. Summary
# ─────────────────────────────────────────────────────────────

print("\n--- Group C Summary ---")
phases = kdb.list_test_plan_phases("PLAN-001")
active = 0
removed = 0
for p in phases:
    tids = json.loads(p["test_ids"]) if p["test_ids"] else []
    status = "ACTIVE" if tids else "REMOVED"
    if tids:
        active += 1
    else:
        removed += 1
    print(f"  {p['id']:10s} | {len(tids):4d} tests | {status}")
print(f"\nActive: {active} phases, Removed: {removed} phases")
