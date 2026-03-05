"""
Record S140 Billing & Usage live E2E test artifacts in KB.
35 tests covering all 34 inventoried elements (EL-billing-001..034).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys
sys.path.insert(0, "tools/knowledge-db")
import db

d = db.KnowledgeDB()

# Mapping: TEST-ID, title, spec_id, class, function, expected_outcome, last_result
TESTS = [
    # TestPageHeader (2 tests)
    ("TEST-3119", "BU page title visible", "SPEC-1652",
     "TestPageHeader", "test_page_title_visible",
     "Page title 'Billing & usage' is visible", "pass"),
    ("TEST-3120", "BU page subtitle visible", "SPEC-1652",
     "TestPageHeader", "test_page_subtitle_visible",
     "Subtitle about managing subscription is visible", "pass"),

    # TestPlanCard (7 tests)
    ("TEST-3121", "BU current plan card visible", "SPEC-1652",
     "TestPlanCard", "test_current_plan_card_visible",
     "Current plan card is visible", "pass"),
    ("TEST-3122", "BU tier badge visible", "SPEC-1652",
     "TestPlanCard", "test_tier_badge_visible",
     "Tier badge (Trial/Starter/Professional/Enterprise) is visible", "pass"),
    ("TEST-3123", "BU subscription status badge", "SPEC-1652",
     "TestPlanCard", "test_subscription_status_badge",
     "Subscription status badge (Active/Suspended/etc.) is visible", "pass"),
    ("TEST-3124", "BU included conversations display", "SPEC-1652",
     "TestPlanCard", "test_included_conversations_display",
     "Included conversations count is shown", "pass"),
    ("TEST-3125", "BU used this period display", "SPEC-1652",
     "TestPlanCard", "test_used_this_period_display",
     "Used this period count is shown", "pass"),
    ("TEST-3126", "BU remaining display", "SPEC-1652",
     "TestPlanCard", "test_remaining_display",
     "Remaining conversations count is shown", "pass"),
    ("TEST-3127", "BU manage subscription button", "SPEC-1652",
     "TestPlanCard", "test_manage_subscription_button",
     "Manage subscription button visible for Stripe tenants", "skip"),

    # TestUsageStats (5 tests)
    ("TEST-3128", "BU conversations used card", "SPEC-1652",
     "TestUsageStats", "test_conversations_used_card",
     "Conversations used stat card with progress ring is visible", "pass"),
    ("TEST-3129", "BU pack balance card", "SPEC-1652",
     "TestUsageStats", "test_pack_balance_card",
     "Pack balance stat card is visible", "pass"),
    ("TEST-3130", "BU current overage card", "SPEC-1652",
     "TestUsageStats", "test_current_overage_card",
     "Current overage stat card is visible", "pass"),
    ("TEST-3131", "BU estimated overage cost card", "SPEC-1652",
     "TestUsageStats", "test_estimated_overage_cost_card",
     "Estimated overage cost stat card is visible", "pass"),
    ("TEST-3132", "BU usage percent shown", "SPEC-1652",
     "TestUsageStats", "test_usage_percent_shown",
     "Usage percentage shown as subtext", "pass"),

    # TestUsageChart (3 tests)
    ("TEST-3133", "BU chart section visible", "SPEC-1652",
     "TestUsageChart", "test_chart_section_visible",
     "Daily usage chart section header is visible", "pass"),
    ("TEST-3134", "BU chart or empty state", "SPEC-1652",
     "TestUsageChart", "test_chart_or_empty_state",
     "Either the chart renders or empty state message is shown", "pass"),
    ("TEST-3135", "BU chart legend", "SPEC-1652",
     "TestUsageChart", "test_chart_legend",
     "Chart legend with Total and Billable labels", "skip"),

    # TestUsageAlerts (1 test)
    ("TEST-3136", "BU alert banner or absence", "SPEC-1652",
     "TestUsageAlerts", "test_alert_banner_or_absence",
     "Alert banner shown when usage thresholds met, else absent", "pass"),

    # TestConversationPacks (6 tests)
    ("TEST-3137", "BU packs section visible", "SPEC-1652",
     "TestConversationPacks", "test_packs_section_visible",
     "Conversation packs section header is visible", "pass"),
    ("TEST-3138", "BU pack 1000 card", "SPEC-1652",
     "TestConversationPacks", "test_pack_1000_card",
     "1,000 conversation pack card is visible", "pass"),
    ("TEST-3139", "BU pack 5000 card", "SPEC-1652",
     "TestConversationPacks", "test_pack_5000_card",
     "5,000 conversation pack card is visible", "pass"),
    ("TEST-3140", "BU pack 20000 card", "SPEC-1652",
     "TestConversationPacks", "test_pack_20000_card",
     "20,000 conversation pack card is visible", "pass"),
    ("TEST-3141", "BU pack purchase buttons", "SPEC-1652",
     "TestConversationPacks", "test_pack_purchase_buttons",
     "Each pack card has a Purchase button", "pass"),
    ("TEST-3142", "BU pack prices shown", "SPEC-1652",
     "TestConversationPacks", "test_pack_prices_shown",
     "Pack prices ($29, $99, $249) displayed", "pass"),

    # TestAddOnModules (5 tests)
    ("TEST-3143", "BU addons section visible", "SPEC-1652",
     "TestAddOnModules", "test_addons_section_visible",
     "Add-on modules section header visible", "pass"),
    ("TEST-3144", "BU addon cards rendered", "SPEC-1652",
     "TestAddOnModules", "test_addon_cards_rendered",
     "At least 5 add-on module cards rendered", "pass"),
    ("TEST-3145", "BU addon tier badges", "SPEC-1652",
     "TestAddOnModules", "test_addon_tier_badges",
     "Add-on cards show tier requirement badges", "pass"),
    ("TEST-3146", "BU addon subscribe buttons", "SPEC-1652",
     "TestAddOnModules", "test_addon_subscribe_buttons",
     "Subscribe or Requires tier buttons on add-on cards", "pass"),
    ("TEST-3147", "BU addon prices shown", "SPEC-1652",
     "TestAddOnModules", "test_addon_prices_shown",
     "Add-on prices with /mo suffix displayed", "pass"),

    # TestTierComparison (1 test)
    ("TEST-3148", "BU tier section or absence", "SPEC-1652",
     "TestTierComparison", "test_tier_section_or_absence",
     "Tier comparison section exists or page is functional", "skip"),

    # TestManageBilling (2 tests)
    ("TEST-3149", "BU manage billing section", "SPEC-1652",
     "TestManageBilling", "test_manage_billing_section",
     "Invoices and payment methods section visible", "skip"),
    ("TEST-3150", "BU manage billing button", "SPEC-1652",
     "TestManageBilling", "test_manage_billing_button",
     "Manage billing button exists for Stripe tenants", "skip"),

    # TestLoadStates (2 tests)
    ("TEST-3151", "BU loading state not stuck", "SPEC-1652",
     "TestLoadStates", "test_loading_state_not_stuck",
     "Loading spinner not stuck after page load", "pass"),
    ("TEST-3152", "BU error state or clean load", "SPEC-1652",
     "TestLoadStates", "test_error_state_or_clean_load",
     "No error alert on clean load", "pass"),

    # TestHelpTooltips (1 test)
    ("TEST-3153", "BU help tooltips exist", "SPEC-1652",
     "TestHelpTooltips", "test_help_tooltips_exist",
     "Multiple help tooltip ? badges exist on the page", "pass"),
]

TEST_FILE = "tests/e2e_live/test_billing_live.py"

print(f"Recording {len(TESTS)} test artifacts (TEST-3119..TEST-3153)...")

for test_id, title, spec_id, test_class, test_func, expected, result in TESTS:
    d.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type="e2e",
        expected_outcome=expected,
        changed_by="S140",
        change_reason="Billing & Usage comprehensive live E2E tests",
        test_file=TEST_FILE,
        test_class=test_class,
        test_function=test_func,
        last_result=result,
        last_executed_at="2026-03-04",
    )
    print(f"  {test_id}: {title} [{result}]")

# Assign all to PLAN-001 Phase 3 (live E2E)
conn = d._conn
phase = conn.execute(
    "SELECT rowid, id, test_ids, version FROM test_plan_phases WHERE plan_id='PLAN-001' AND phase_order=3 ORDER BY version DESC LIMIT 1"
).fetchone()
if phase:
    existing_ids = phase["test_ids"] or ""
    new_ids = ",".join(t[0] for t in TESTS)
    updated = f"{existing_ids},{new_ids}" if existing_ids else new_ids
    new_version = phase["version"] + 1
    conn.execute(
        """INSERT INTO test_plan_phases (id, plan_id, phase_order, title, description, test_ids, gate_criteria, version, changed_by, changed_at, change_reason)
           SELECT id, plan_id, phase_order, title, description, ?, gate_criteria, ?,
                  'S140', datetime('now'), 'Add 35 Billing live E2E tests'
           FROM test_plan_phases WHERE rowid=?""",
        (updated, new_version, phase["rowid"])
    )
    conn.commit()
    print(f"\nPLAN-001 Phase 3 updated to v{new_version}: +35 tests")

# Summary
summary = d.get_summary()
print(f"\nKB Summary after recording:")
for k, v in summary.items():
    if v and v != "N/A":
        print(f"  {k}: {v}")

print("\nDone.")
