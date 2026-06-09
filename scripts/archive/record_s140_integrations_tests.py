"""
Record S140 Integrations live E2E test artifacts in KB.
22 tests covering all 20 inventoried elements (EL-integrations-001..020).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db

d = db.KnowledgeDB()

# Mapping: TEST-ID, title, spec_id, class, function, expected_outcome, last_result
TESTS = [
    # TestPageHeader (2 tests)
    (
        "TEST-3194",
        "INT page title visible",
        "SPEC-1652",
        "TestPageHeader",
        "test_page_title_visible",
        "Page title 'Integrations' is visible",
        "pass",
    ),
    (
        "TEST-3195",
        "INT page subtitle visible",
        "SPEC-1652",
        "TestPageHeader",
        "test_page_subtitle_visible",
        "Subtitle about connecting services is visible",
        "pass",
    ),
    # TestIntegrationCards (4 tests)
    (
        "TEST-3196",
        "INT at least 4 cards",
        "SPEC-1652",
        "TestIntegrationCards",
        "test_at_least_4_cards",
        "At least 4 integration cards rendered",
        "pass",
    ),
    (
        "TEST-3197",
        "INT card has logo or icon",
        "SPEC-1652",
        "TestIntegrationCards",
        "test_card_has_logo_or_icon",
        "Integration cards have logo images or SVG icons",
        "pass",
    ),
    (
        "TEST-3198",
        "INT card has name and description",
        "SPEC-1652",
        "TestIntegrationCards",
        "test_card_has_name_and_description",
        "Each card shows name and description",
        "pass",
    ),
    (
        "TEST-3199",
        "INT help tooltips on cards",
        "SPEC-1652",
        "TestIntegrationCards",
        "test_help_tooltips_on_cards",
        "Integration names have help tooltips",
        "pass",
    ),
    # TestStatusBadges (3 tests)
    (
        "TEST-3200",
        "INT connection status badges",
        "SPEC-1652",
        "TestStatusBadges",
        "test_connection_status_badges",
        "At least one status badge (Connected/Not Connected)",
        "pass",
    ),
    (
        "TEST-3201",
        "INT Coming Soon badge",
        "SPEC-1652",
        "TestStatusBadges",
        "test_coming_soon_badge",
        "Coming Soon badge on unavailable integrations",
        "pass",
    ),
    (
        "TEST-3202",
        "INT tier gate badge",
        "SPEC-1652",
        "TestStatusBadges",
        "test_tier_gate_badge",
        "Tier gate badge on restricted integrations",
        "skip",
    ),
    # TestActionButtons (3 tests)
    (
        "TEST-3203",
        "INT activate button exists",
        "SPEC-1652",
        "TestActionButtons",
        "test_activate_button_exists",
        "Activate button shown for disconnected integrations",
        "pass",
    ),
    (
        "TEST-3204",
        "INT deactivate button or absent",
        "SPEC-1652",
        "TestActionButtons",
        "test_deactivate_button_or_absent",
        "Deactivate button for connected integrations",
        "pass",
    ),
    (
        "TEST-3205",
        "INT disconnect button or absent",
        "SPEC-1652",
        "TestActionButtons",
        "test_disconnect_button_or_absent",
        "Disconnect button for connected integrations",
        "pass",
    ),
    # TestSpecificIntegrations (5 tests)
    (
        "TEST-3206",
        "INT Shopify card",
        "SPEC-1652",
        "TestSpecificIntegrations",
        "test_shopify_card",
        "Shopify integration card visible",
        "pass",
    ),
    (
        "TEST-3207",
        "INT Zendesk card",
        "SPEC-1652",
        "TestSpecificIntegrations",
        "test_zendesk_card",
        "Zendesk integration card visible",
        "pass",
    ),
    (
        "TEST-3208",
        "INT Mailchimp card",
        "SPEC-1652",
        "TestSpecificIntegrations",
        "test_mailchimp_card",
        "Mailchimp integration card visible",
        "pass",
    ),
    (
        "TEST-3209",
        "INT Google Analytics card",
        "SPEC-1652",
        "TestSpecificIntegrations",
        "test_google_analytics_card",
        "Google Analytics integration card visible",
        "pass",
    ),
    (
        "TEST-3210",
        "INT Stripe card",
        "SPEC-1652",
        "TestSpecificIntegrations",
        "test_stripe_card",
        "Stripe integration card visible",
        "pass",
    ),
    # TestActiveCount (1 test)
    (
        "TEST-3211",
        "INT active count footer",
        "SPEC-1652",
        "TestActiveCount",
        "test_active_count_footer",
        "X of Y integrations active footer text",
        "pass",
    ),
    # TestMutations (1 test)
    (
        "TEST-3212",
        "INT activate Shopify",
        "SPEC-1652",
        "TestMutations",
        "test_activate_shopify",
        "Activate Shopify integration via button click",
        "pass",
    ),
    # TestDisconnectConfirmation (1 test)
    (
        "TEST-3213",
        "INT disconnect confirmation",
        "SPEC-1652",
        "TestDisconnectConfirmation",
        "test_disconnect_shows_confirmation",
        "Clicking Disconnect shows confirmation inline",
        "pass",
    ),
    # TestLoadStates (2 tests)
    (
        "TEST-3214",
        "INT loading not stuck",
        "SPEC-1652",
        "TestLoadStates",
        "test_loading_not_stuck",
        "Loading spinner not stuck after page load",
        "pass",
    ),
    (
        "TEST-3215",
        "INT no error on clean load",
        "SPEC-1652",
        "TestLoadStates",
        "test_no_error_on_clean_load",
        "No error alert on fresh page load",
        "pass",
    ),
]

TEST_FILE = "tests/e2e_live/test_integrations_live.py"

print(f"Recording {len(TESTS)} test artifacts (TEST-3194..TEST-3215)...")

for test_id, title, spec_id, test_class, test_func, expected, result in TESTS:
    d.insert_test(
        id=test_id,
        title=title,
        spec_id=spec_id,
        test_type="e2e",
        expected_outcome=expected,
        changed_by="S140",
        change_reason="Integrations comprehensive live E2E tests",
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
    "SELECT rowid, id, test_ids, gate_criteria, version FROM test_plan_phases WHERE plan_id='PLAN-001' AND phase_order=3 ORDER BY version DESC LIMIT 1"
).fetchone()
if phase:
    existing_ids = phase["test_ids"] or ""
    new_ids = ",".join(t[0] for t in TESTS)
    updated = f"{existing_ids},{new_ids}" if existing_ids else new_ids
    new_version = phase["version"] + 1
    conn.execute(
        """INSERT INTO test_plan_phases (id, plan_id, phase_order, title, description, test_ids, gate_criteria, version, changed_by, changed_at, change_reason)
           SELECT id, plan_id, phase_order, title, description, ?, gate_criteria, ?,
                  'S140', datetime('now'), 'Add 22 Integrations live E2E tests'
           FROM test_plan_phases WHERE rowid=?""",
        (updated, new_version, phase["rowid"]),
    )
    conn.commit()
    print(f"\nPLAN-001 Phase 3 updated to v{new_version}: +22 tests")

# Summary
summary = d.get_summary()
print(f"\nKB Summary after recording:")
for k, v in summary.items():
    if v and v != "N/A":
        print(f"  {k}: {v}")

print("\nDone.")
