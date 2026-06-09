"""
Insert E2E test → Phase 1 spec coverage mappings.
Session S112 — cross-referencing S107/S108 E2E tests against uncovered Phase 1 specs.

Usage: python scripts/insert_e2e_phase1_coverage_s112.py
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()
c = db._get_conn()

# All new E2E → Phase 1 mappings
MAPPINGS = [
    # Navigation tests
    (
        "tests/e2e/test_navigation.py",
        "TestSidebarStructure",
        "test_sidebar_has_all_nav_links",
        "SPEC-0696",
        "high",
        "Checks 'Team members' nav label — verifies rename from 'Team'",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestSidebarStructure",
        "test_sidebar_has_all_nav_links",
        "SPEC-0697",
        "medium",
        "Checks config nav links present — partially verifies grouping",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestSidebarStructure",
        "test_dark_mode_toggle_exists",
        "SPEC-0015",
        "medium",
        "Dark mode toggle exists — partially verifies dark mode default",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestSidebarStructure",
        "test_dark_mode_toggle_exists",
        "SPEC-0086",
        "medium",
        "Dark mode toggle present in admin UI",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestPageNavigation",
        "test_dashboard_loads",
        "SPEC-0007",
        "high",
        "Dashboard renders — Analytics merged into Dashboard",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestPageNavigation",
        "test_dashboard_loads",
        "SPEC-0008",
        "high",
        "Dashboard loads, Analytics nav item removed",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestNoConsoleErrors",
        "test_no_js_errors_on_page_load",
        "SPEC-0578",
        "high",
        "Zero JS errors on page load",
    ),
    (
        "tests/e2e/test_navigation.py",
        "TestSidebarStructure",
        "test_logout_button_exists",
        "SPEC-0584",
        "medium",
        "Sign out button confirms session management",
    ),
    # Dashboard tests
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardStructure",
        "test_store_name_from_config",
        "SPEC-0119",
        "high",
        "Brand name displayed on Dashboard",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardStructure",
        "test_period_selector_options",
        "SPEC-0155",
        "high",
        "4 period options (7d/14d/30d/90d) present",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardPeriodFilter",
        "test_switch_to_7d",
        "SPEC-0155",
        "high",
        "Chart label changes to 'Last 7 days'",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardPeriodFilter",
        "test_switch_to_14d",
        "SPEC-0155",
        "high",
        "Chart label changes to 'Last 14 days'",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardPeriodFilter",
        "test_switch_to_90d",
        "SPEC-0155",
        "high",
        "Chart label changes to 'Last 90 days'",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardStructure",
        "test_detailed_analytics_divider",
        "SPEC-0234",
        "high",
        "Intents renamed to 'Detailed analytics'",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardTopicBreakdownTable",
        "test_table_heading",
        "SPEC-0234",
        "high",
        "Topic breakdown heading visible",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardHelpTooltips",
        "test_total_conversations_has_tooltip",
        "SPEC-0094",
        "medium",
        "Tooltip present on Total conversations",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardHelpTooltips",
        "test_conversation_volume_has_tooltip",
        "SPEC-0094",
        "medium",
        "Tooltip present on Conversation volume",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardHelpTooltips",
        "test_knowledge_gaps_has_tooltip",
        "SPEC-0094",
        "medium",
        "Tooltip present on Knowledge gaps",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardConversationChart",
        "test_chart_period_label",
        "SPEC-0155",
        "high",
        "Chart shows 'Last 30 days' by default",
    ),
    (
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardConversationChart",
        "test_chart_container_renders",
        "SPEC-0093",
        "medium",
        "Chart SVG renders — actual data not synthetic",
    ),
    # Widget page tests
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_gradient_switch_label",
        "SPEC-0126",
        "high",
        "Gradient toggle present",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_gradient_switch_description",
        "SPEC-0126",
        "high",
        "Gradient toggle description shown",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_gradient_right_color_dimmed_when_off",
        "SPEC-0127",
        "high",
        "Right color dimmed when gradient off",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_horizontal_offset_label",
        "SPEC-0118",
        "high",
        "Horizontal offset control present",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_vertical_offset_label",
        "SPEC-0118",
        "high",
        "Vertical offset control present",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_position_options",
        "SPEC-0118",
        "medium",
        "Position options Bottom right/left",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetActions",
        "test_save_button_text",
        "SPEC-0055",
        "high",
        "Save draft inputs button on Widget page",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetActions",
        "test_save_button_text",
        "SPEC-0056",
        "medium",
        "Widget page follows save workflow",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetPageStructure",
        "test_page_heading_text",
        "SPEC-0627",
        "high",
        "Heading reads 'Widget configuration'",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetInstallation",
        "test_widget_key_read_only",
        "SPEC-0685",
        "high",
        "Widget key input is readonly",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetKeyRotation",
        "test_rotate_opens_modal",
        "SPEC-0686",
        "high",
        "Rotate key opens confirmation modal",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetKeyRotation",
        "test_rotation_modal_warning",
        "SPEC-0686",
        "high",
        "Modal warns about immediate invalidation",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetBehavior",
        "test_greeting_textarea_visible",
        "SPEC-0103",
        "medium",
        "Greeting textarea present in static mode",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetInteractions",
        "test_ai_generated_mode_hides_textarea",
        "SPEC-0112",
        "high",
        "AI-generated hides textarea",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetBehavior",
        "test_greeting_mode_options",
        "SPEC-0112",
        "high",
        "Static and AI-generated options visible",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_color_mode_options",
        "SPEC-0246",
        "high",
        "Light/Dark/Auto color mode options",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetInteractions",
        "test_pre_chat_fields_shown_on_enable",
        "SPEC-0747",
        "high",
        "Pre-chat form shows fields on enable",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetInteractions",
        "test_pre_chat_fields_shown_on_enable",
        "SPEC-0769",
        "high",
        "Pre-chat disabled by default",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_color_inputs_present",
        "SPEC-0102",
        "medium",
        "Color input controls exist",
    ),
    (
        "tests/e2e/test_widget_page.py",
        "TestWidgetInstallation",
        "test_shopify_helper_text",
        "SPEC-0345",
        "medium",
        "Shopify helper text in standalone admin",
    ),
    # Configuration page tests
    (
        "tests/e2e/test_configuration_page.py",
        "TestConfigPageStructure",
        "test_save_button_visible",
        "SPEC-0055",
        "medium",
        "Save button on Agent config page",
    ),
    (
        "tests/e2e/test_configuration_page.py",
        "TestConfigPageStructure",
        "test_save_button_visible",
        "SPEC-0056",
        "medium",
        "Agent config follows save workflow",
    ),
    (
        "tests/e2e/test_configuration_page.py",
        "TestConfigPageStructure",
        "test_page_heading_visible",
        "SPEC-0574",
        "high",
        "Config page heading renders",
    ),
    (
        "tests/e2e/test_configuration_page.py",
        "TestSaveDraft",
        "test_save_draft_sends_api_call",
        "SPEC-0574",
        "high",
        "Config page saves changes",
    ),
    (
        "tests/e2e/test_configuration_page.py",
        "TestSaveDraft",
        "test_save_draft_sends_api_call",
        "SPEC-0402",
        "high",
        "Save persists without activating",
    ),
    # Team page tests
    (
        "tests/e2e/test_team_page.py",
        "TestTeamPageStructure",
        "test_page_title_visible",
        "SPEC-0696",
        "high",
        "Team members heading visible",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestTeamPageStructure",
        "test_table_headers_visible",
        "SPEC-0311",
        "medium",
        "Table columns incl Role/Joined/Escalations",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestRoleManagement",
        "test_agent_role_selector_visible",
        "SPEC-0752",
        "high",
        "Role column uses select menus",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestRoleManagement",
        "test_superadmin_role_not_editable",
        "SPEC-0758",
        "high",
        "Superadmin role not changeable",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestTeamPageStructure",
        "test_superadmin_no_remove_button",
        "SPEC-0758",
        "high",
        "Superadmin cannot be deleted",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestEscalationCategories",
        "test_category_chips_visible_for_agent",
        "SPEC-0754",
        "high",
        "Agent has category chips",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestEscalationCategories",
        "test_category_chips_hidden_for_viewer",
        "SPEC-0754",
        "high",
        "Viewer has no category chips",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestEscalationCategories",
        "test_category_toggle_sends_put",
        "SPEC-0754",
        "high",
        "Category toggle persists via PUT",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestTeamPageStructure",
        "test_invite_button_visible",
        "SPEC-0558",
        "medium",
        "Invite member button present",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestRemoveMember",
        "test_confirm_remove_sends_delete",
        "SPEC-0475",
        "high",
        "Hard delete sends DELETE request",
    ),
    (
        "tests/e2e/test_team_page.py",
        "TestTeamPageStructure",
        "test_agent_escalation_count",
        "SPEC-0359",
        "medium",
        "Escalation count visible per agent",
    ),
    # Knowledge base page tests
    (
        "tests/e2e/test_knowledge_base_page.py",
        "TestSearch",
        "test_search_filters_articles",
        "SPEC-0095",
        "high",
        "Search returns matching results",
    ),
    (
        "tests/e2e/test_knowledge_base_page.py",
        "TestKnowledgeBaseStructure",
        "test_search_input_visible",
        "SPEC-0095",
        "medium",
        "Search input present",
    ),
    (
        "tests/e2e/test_knowledge_base_page.py",
        "TestKnowledgeBaseStructure",
        "test_article_list_rendered",
        "SPEC-0641",
        "medium",
        "Articles rendered in list",
    ),
    (
        "tests/e2e/test_knowledge_base_page.py",
        "TestArticleCRUD",
        "test_add_article_opens_modal",
        "SPEC-0641",
        "high",
        "Add article modal opens",
    ),
    # Memory & Privacy page tests
    (
        "tests/e2e/test_memory_privacy_page.py",
        "TestTierGating",
        "test_professional_tier_shows_all_fields",
        "SPEC-0170",
        "high",
        "Professional tier shows all toggles",
    ),
    (
        "tests/e2e/test_memory_privacy_page.py",
        "TestToggleInteractions",
        "test_toggle_click_changes_state",
        "SPEC-0698",
        "high",
        "Toggle switches change state on click",
    ),
]

# Check existing to avoid duplicates
existing = set()
for row in c.execute("SELECT spec_id, test_file, test_function FROM test_coverage").fetchall():
    existing.add((row[0], row[1], row[2]))

inserted = 0
skipped_dup = 0
skipped_unresolved = 0

for test_file, test_class, test_function, spec_id, confidence, match_reason in MAPPINGS:
    # Verify spec exists
    row = c.execute("SELECT id FROM current_specifications WHERE id = ? AND status != 'retired'", (spec_id,)).fetchone()
    if row is None:
        skipped_unresolved += 1
        print(f"  WARN: {spec_id} not found in KB")
        continue

    test_file_norm = test_file.replace("\\", "/")
    if (spec_id, test_file_norm, test_function) in existing:
        skipped_dup += 1
        continue

    c.execute(
        """INSERT INTO test_coverage
           (spec_id, test_file, test_class, test_function, confidence, match_reason, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 'S112-e2e-phase1-mapping')""",
        (spec_id, test_file_norm, test_class, test_function, confidence, match_reason),
    )
    existing.add((spec_id, test_file_norm, test_function))
    inserted += 1

c.execute("COMMIT")

# Final stats
total_mappings = c.execute("SELECT COUNT(*) FROM test_coverage").fetchone()[0]
unique_files = len(set(r[0] for r in c.execute("SELECT DISTINCT test_file FROM test_coverage").fetchall()))
unique_specs = len(set(r[0] for r in c.execute("SELECT DISTINCT spec_id FROM test_coverage").fetchall()))
high = c.execute("SELECT COUNT(*) FROM test_coverage WHERE confidence = 'high'").fetchone()[0]
medium = c.execute("SELECT COUNT(*) FROM test_coverage WHERE confidence = 'medium'").fetchone()[0]

print(f"\nInserted: {inserted}")
print(f"Skipped (duplicate): {skipped_dup}")
print(f"Skipped (unresolved): {skipped_unresolved}")
print(f"\nFinal totals:")
print(f"  Total mappings: {total_mappings}")
print(f"  Unique test files: {unique_files}")
print(f"  Unique specs covered: {unique_specs}")
print(f"  High confidence: {high}")
print(f"  Medium confidence: {medium}")

# Coverage percentage
total_active = c.execute("SELECT COUNT(DISTINCT id) FROM current_specifications WHERE status != 'retired'").fetchone()[
    0
]
print(f"\nCoverage: {unique_specs}/{total_active} = {unique_specs / total_active * 100:.1f}%")
