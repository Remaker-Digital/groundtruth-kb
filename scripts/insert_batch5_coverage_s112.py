"""Insert test_coverage mappings for Batch 5 (46 numbered UI specs): tooltips, renames, features, setup.

Session S112 — Phase C coverage insertion.

Includes:
  - Mappings for existing E2E tests that already cover numbered UI specs
  - Mappings for new E2E tests created in this batch
  - Mappings for new Python unit tests (WI 115, 201, 204, 297)
  - 3 deferred widget-runtime specs (253, 255, 256) NOT included — Batch 6

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()
c = db._get_conn()

CREATED_BY = "S112-batch5-coverage"
MAPPINGS: list[tuple[str, str, str, str, str, str]] = [
    # (spec_id, test_file, test_class, test_function, confidence, match_reason)
    # ── MAPPING-ONLY: Existing tests that already cover specs ─────────────
    # Dashboard
    (
        "258",
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardStructure",
        "test_store_name_from_config",
        "high",
        "Storefront name displayed on Dashboard",
    ),
    (
        "259",
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardHelpTooltips",
        "test_total_conversations_has_tooltip",
        "high",
        "Dashboard metric help tooltips",
    ),
    (
        "283",
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardStructure",
        "test_period_selector_options",
        "high",
        "Analytics merged into Dashboard — period selector present",
    ),
    (
        "288",
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardSetupChecklist",
        "test_checklist_visible_for_inactive_tenant",
        "high",
        "Go live setup completion checklist",
    ),
    (
        "289",
        "tests/e2e/test_dashboard_page.py",
        "TestDashboardTestModeAlert",
        "test_alert_visible_when_test_mode_enabled",
        "high",
        "Go live test mode diff checklist",
    ),
    # Configuration
    (
        "262",
        "tests/e2e/test_configuration_page.py",
        "TestConfigPageStructure",
        "test_page_heading_visible",
        "high",
        "Rename Configuration to Agent configuration — heading check",
    ),
    (
        "265",
        "tests/e2e/test_configuration_page.py",
        "TestConfigInputFields",
        "test_configuration_name_input",
        "high",
        "Named configuration save/restore — named configs present",
    ),
    # Widget Config
    (
        "240",
        "tests/e2e/test_widget_page.py",
        "TestWidgetDataLoading",
        "test_primary_color_from_api",
        "medium",
        "Widget applies saved color configuration — color from API",
    ),
    (
        "241",
        "tests/e2e/test_widget_page.py",
        "TestWidgetBehavior",
        "test_greeting_textarea_visible",
        "medium",
        "Widget displays custom greeting message — textarea present",
    ),
    (
        "249",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_panel_shadow_label",
        "high",
        "Widget drop-shadow control — shadow config present",
    ),
    (
        "252",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_panel_width_label",
        "medium",
        "Chat UI resizable width — panel width config present",
    ),
    (
        "257",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_horizontal_offset_label",
        "high",
        "Launcher position offset controls X/Y",
    ),
    (
        "268",
        "tests/e2e/test_widget_page.py",
        "TestWidgetPageStructure",
        "test_page_heading_text",
        "high",
        "Rename Widget to Widget configuration — heading check",
    ),
    (
        "269",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_header_left_color_label",
        "high",
        "Rename color fields: Header left/right color",
    ),
    (
        "270",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_gradient_switch_label",
        "high",
        "Gradient enable/disable toggle — switch label present",
    ),
    (
        "271",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAppearance",
        "test_color_inputs_present",
        "high",
        "Side-by-side color pickers for header colors",
    ),
    (
        "296",
        "tests/e2e/test_widget_page.py",
        "TestWidgetBehavior",
        "test_greeting_mode_options",
        "high",
        "AI-generated greeting option — Static/AI SegmentedControl",
    ),
    # Team
    (
        "275",
        "tests/e2e/test_team_page.py",
        "TestRoleManagement",
        "test_agent_role_selector_visible",
        "high",
        "Role selector replaces textual role badges",
    ),
    (
        "279",
        "tests/e2e/test_team_page.py",
        "TestEscalationCategories",
        "test_category_chips_visible_for_agent",
        "high",
        "Escalation category assignment per team member",
    ),
    (
        "280",
        "tests/e2e/test_team_page.py",
        "TestEscalationCategories",
        "test_category_toggle_sends_put",
        "medium",
        "Enable/disable toggle — category toggle mechanism",
    ),
    # Navigation
    (
        "284",
        "tests/e2e/test_navigation.py",
        "TestSidebarStructure",
        "test_sidebar_has_all_nav_links",
        "high",
        "Reorder sidebar navigation — all links present",
    ),
    # ── NEW E2E TESTS: Configuration page ─────────────────────────────────
    (
        "263",
        "tests/e2e/test_configuration_page.py",
        "TestConfigTooltips",
        "test_section_help_tooltips_present",
        "high",
        "Configuration section help tooltips",
    ),
    (
        "266",
        "tests/e2e/test_configuration_page.py",
        "TestNamedConfigManagement",
        "test_delete_config_button",
        "high",
        "Delete saved configurations",
    ),
    (
        "267",
        "tests/e2e/test_configuration_page.py",
        "TestNamedConfigManagement",
        "test_config_timestamp_visible",
        "high",
        "Saved configuration date-stamp",
    ),
    # ── NEW E2E TESTS: Knowledge Base page ────────────────────────────────
    (
        "260",
        "tests/e2e/test_knowledge_base_page.py",
        "TestKBTooltips",
        "test_toolbar_help_tooltips",
        "high",
        "KB toolbar buttons help tooltips",
    ),
    # ── NEW E2E TESTS: Widget Config page ─────────────────────────────────
    (
        "272",
        "tests/e2e/test_widget_page.py",
        "TestWidgetTooltips",
        "test_section_help_tooltips_present",
        "high",
        "Widget page section help tooltips",
    ),
    (
        "254",
        "tests/e2e/test_widget_page.py",
        "TestWidgetAutoOpen",
        "test_auto_open_config_field",
        "high",
        "Auto-open per page config field",
    ),
    # ── NEW E2E TESTS: Quick Actions page ─────────────────────────────────
    (
        "242",
        "tests/e2e/test_quick_actions_page.py",
        "TestQuickActionsFeatures",
        "test_starter_examples_on_first_visit",
        "high",
        "Quick actions starter examples",
    ),
    (
        "243",
        "tests/e2e/test_quick_actions_page.py",
        "TestQuickActionsFeatures",
        "test_icon_field_guidance",
        "high",
        "Quick action Icon field guidance",
    ),
    (
        "244",
        "tests/e2e/test_quick_actions_page.py",
        "TestQuickActionsFeatures",
        "test_sort_order_field_removed",
        "high",
        "Quick action Sort order field redundancy",
    ),
    (
        "245",
        "tests/e2e/test_quick_actions_page.py",
        "TestQuickActionsFeatures",
        "test_widget_preview_available",
        "medium",
        "Quick actions previewable in admin widget",
    ),
    (
        "273",
        "tests/e2e/test_quick_actions_page.py",
        "TestQuickActionsFeatures",
        "test_page_assignments_list",
        "high",
        "Page assignments single-column list",
    ),
    (
        "274",
        "tests/e2e/test_quick_actions_page.py",
        "TestQuickActionsFeatures",
        "test_template_variables_inline",
        "high",
        "Template variables inline below prompt",
    ),
    # ── NEW E2E TESTS: Team page ──────────────────────────────────────────
    (
        "276",
        "tests/e2e/test_team_page.py",
        "TestTeamPageRenames",
        "test_team_member_column_header",
        "high",
        "Rename Member column to Team member",
    ),
    (
        "277",
        "tests/e2e/test_team_page.py",
        "TestTeamPageRenames",
        "test_role_column_tooltip",
        "high",
        "Roles & permissions tooltip on Role column",
    ),
    # ── NEW E2E TESTS: Billing page ───────────────────────────────────────
    (
        "281",
        "tests/e2e/test_billing_page.py",
        "TestBillingFeatures",
        "test_metric_cards_help_tooltips",
        "high",
        "Billing metric cards help tooltips",
    ),
    (
        "282",
        "tests/e2e/test_billing_page.py",
        "TestBillingFeatures",
        "test_purchase_button_exists",
        "high",
        "Purchase button hover color consistency",
    ),
    # ── NEW E2E TESTS: Navigation ─────────────────────────────────────────
    (
        "291",
        "tests/e2e/test_navigation.py",
        "TestSystemStateIndicator",
        "test_activation_status_in_navbar",
        "high",
        "Inactive system state indicator in nav bar",
    ),
    # ── NEW E2E TESTS: Dashboard / Setup Wizard ───────────────────────────
    (
        "286",
        "tests/e2e/test_dashboard_page.py",
        "TestSetupWizardFeatures",
        "test_no_redundant_wizard_steps",
        "high",
        "Remove redundant wizard steps",
    ),
    (
        "287",
        "tests/e2e/test_dashboard_page.py",
        "TestSetupWizardFeatures",
        "test_wizard_steps_align_with_sidebar",
        "high",
        "Wizard steps mirror sidebar pages",
    ),
    (
        "292",
        "tests/e2e/test_dashboard_page.py",
        "TestSetupWizardFeatures",
        "test_welcome_message_for_new_merchants",
        "high",
        "Welcome message popup for new merchants",
    ),
    (
        "293",
        "tests/e2e/test_dashboard_page.py",
        "TestSetupWizardFeatures",
        "test_custom_ai_instructions_label",
        "high",
        "Rename Review and launch to Custom AI instructions",
    ),
    # ── NEW PYTHON UNIT TESTS ─────────────────────────────────────────────
    (
        "115",
        "tests/unit/test_batch5_misc_specs.py",
        "TestCustomerProfileUI",
        "test_customer_profile_api_module_exists",
        "high",
        "Customer profile viewer UI — API module exists",
    ),
    (
        "201",
        "tests/unit/test_batch5_misc_specs.py",
        "TestSeedKnowledgeBase",
        "test_seed_script_has_kb_phase",
        "high",
        "Seed knowledge base — KB phase in seed script",
    ),
    (
        "204",
        "tests/unit/test_batch5_misc_specs.py",
        "TestFavicon",
        "test_admin_has_favicon_files",
        "high",
        "Favicon and app icons from icon-master.png",
    ),
    (
        "297",
        "tests/unit/test_batch5_misc_specs.py",
        "TestMaxTurnsMin",
        "test_max_turns_min_value_is_at_least_one",
        "high",
        "Enforce min=1 for max_turns on server",
    ),
]


def main() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    inserted = 0
    skipped = 0

    for spec_id, test_file, test_class, test_func, confidence, reason in MAPPINGS:
        existing = c.execute(
            "SELECT 1 FROM test_coverage WHERE spec_id = ? AND test_function = ?",
            (spec_id, test_func),
        ).fetchone()
        if existing:
            skipped += 1
            continue

        c.execute(
            """INSERT INTO test_coverage
               (spec_id, test_file, test_class, test_function, confidence, match_reason, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (spec_id, test_file, test_class, test_func, confidence, reason, now, CREATED_BY),
        )
        inserted += 1

    c.commit()

    total_coverage = c.execute("SELECT COUNT(DISTINCT spec_id) FROM test_coverage").fetchone()[0]
    total_specs = c.execute("SELECT COUNT(DISTINCT id) FROM specifications WHERE status != 'retired'").fetchone()[0]

    print(f"Inserted: {inserted}, Skipped (already exist): {skipped}")
    print(f"Total coverage: {total_coverage}/{total_specs} specs ({100 * total_coverage / total_specs:.1f}%)")


if __name__ == "__main__":
    main()
