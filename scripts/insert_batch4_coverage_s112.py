"""Insert test_coverage mappings for Batch 4 (66 ADMIN_UI specs): page elements, input fields, buttons, toggles.

Session S112 — Phase C coverage insertion.

Includes both:
  - Mappings for existing E2E tests that already cover ADMIN_UI specs
  - Mappings for new E2E tests created in this batch

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

db = KnowledgeDB()
c = db._get_conn()

CREATED_BY = "S112-batch4-coverage"
MAPPINGS: list[tuple[str, str, str, str, str, str]] = [
    # (spec_id, test_file, test_class, test_function, confidence, match_reason)

    # ── ALREADY-COVERED SPECS (existing tests, new mappings) ────────────────

    # Dashboard
    ("SPEC-0873", "tests/e2e/test_dashboard_page.py", "TestDashboardStructure", "test_period_selector_options", "high", "Analytics merged into Dashboard — period SegmentedControl"),
    ("SPEC-0895", "tests/e2e/test_dashboard_page.py", "TestDashboardStructure", "test_page_title", "high", "Dashboard page title"),
    ("SPEC-0896", "tests/e2e/test_dashboard_page.py", "TestDashboardStructure", "test_period_selector_options", "high", "Dashboard SegmentedControl options"),

    # Configuration
    ("SPEC-0882", "tests/e2e/test_configuration_page.py", "TestDropdowns", "test_formality_selector_exists", "high", "Formality selector"),
    ("SPEC-0894", "tests/e2e/test_configuration_page.py", "TestConfigPageStructure", "test_page_heading_visible", "high", "Configuration page title"),

    # Knowledge Base
    ("SPEC-0911", "tests/e2e/test_knowledge_base_page.py", "TestKnowledgeBaseStructure", "test_page_heading_visible", "high", "KB page title"),
    ("SPEC-0912", "tests/e2e/test_knowledge_base_page.py", "TestKnowledgeBaseStructure", "test_page_heading_visible", "high", "KB page title (duplicate spec)"),

    # Memory & Privacy
    ("SPEC-0921", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyStructure", "test_page_heading_visible", "high", "Memory & Privacy page title"),
    ("SPEC-0922", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyStructure", "test_page_heading_visible", "high", "Memory & Privacy page title (duplicate spec)"),

    # Team
    ("SPEC-0933", "tests/e2e/test_team_page.py", "TestTeamPageStructure", "test_page_title_visible", "high", "Team page title"),

    # Widget
    ("SPEC-0935", "tests/e2e/test_widget_page.py", "TestWidgetAppearance", "test_launcher_icon_label", "high", "Launcher icon input"),
    ("SPEC-0938", "tests/e2e/test_widget_page.py", "TestWidgetBehavior", "test_greeting_message_switch", "high", "Greeting message switch"),
    ("SPEC-0940", "tests/e2e/test_widget_page.py", "TestWidgetContent", "test_header_subtitle_label", "high", "Header subtitle label"),
    ("SPEC-0947", "tests/e2e/test_widget_page.py", "TestWidgetActions", "test_reset_button_text", "high", "Reset to defaults button"),
    ("SPEC-0948", "tests/e2e/test_widget_page.py", "TestWidgetActions", "test_save_button_text", "high", "Save draft inputs button"),
    ("SPEC-0950", "tests/e2e/test_widget_page.py", "TestWidgetPageStructure", "test_page_heading_text", "high", "Widget page title"),
    ("SPEC-0951", "tests/e2e/test_widget_page.py", "TestWidgetBehavior", "test_greeting_mode_options", "high", "Static/AI-generated SegmentedControl"),

    # WI specs (existing coverage)
    ("226", "tests/e2e/test_dashboard_page.py", "TestDashboardHelpTooltips", "test_total_conversations_has_tooltip", "medium", "Admin contextual tooltips"),
    ("248", "tests/e2e/test_dashboard_page.py", "TestDashboardTestModeAlert", "test_alert_visible_when_test_mode_enabled", "medium", "Test mode E2E validation"),

    # ── NEW TESTS: Configuration input fields ───────────────────────────────

    ("SPEC-0879", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_configuration_name_input", "high", "Configuration name input field"),
    ("SPEC-0881", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_brand_voice_input", "high", "Brand voice input field"),
    ("SPEC-0884", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_return_window_input", "high", "Return window input field"),
    ("SPEC-0885", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_refund_policy_input", "high", "Refund policy input field"),
    ("SPEC-0886", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_shipping_policy_input", "high", "Shipping policy input field"),
    ("SPEC-0887", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_notification_email_input", "high", "Notification email input field"),
    ("SPEC-0888", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_idle_timeout_input", "high", "Idle timeout input field"),
    ("SPEC-0889", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_max_turns_input", "high", "Max turns input field"),
    ("SPEC-0890", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_primary_language_input", "high", "Primary language input field"),
    ("SPEC-0891", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_retry_button", "high", "Retry button"),
    ("SPEC-0892", "tests/e2e/test_configuration_page.py", "TestConfigInputFields", "test_cancel_button", "high", "Cancel button (save modal)"),

    # ── NEW TESTS: Knowledge Base form fields ───────────────────────────────

    ("SPEC-0902", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_title_input", "high", "KB article Title input"),
    ("SPEC-0903", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_category_input", "high", "KB article Category input"),
    ("SPEC-0904", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_content_input", "high", "KB article Content input"),
    ("SPEC-0905", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_status_input", "high", "KB article Status input"),
    ("SPEC-0907", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_retry_button", "high", "KB Retry button"),
    ("SPEC-0908", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_cancel_button", "high", "KB Cancel button"),
    ("SPEC-0909", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_import_button", "high", "KB Import button"),
    ("SPEC-0910", "tests/e2e/test_knowledge_base_page.py", "TestArticleFormFields", "test_close_button", "high", "KB Close button"),
    ("SPEC-0913", "tests/e2e/test_knowledge_base_page.py", "TestKBImportAndTabs", "test_import_successful_title", "medium", "Import modal"),
    ("SPEC-0914", "tests/e2e/test_knowledge_base_page.py", "TestKBImportAndTabs", "test_file_tab", "high", "KB file tab"),
    ("SPEC-0915", "tests/e2e/test_knowledge_base_page.py", "TestKBImportAndTabs", "test_url_tab", "high", "KB url tab"),

    # ── NEW TESTS: Memory & Privacy fields ──────────────────────────────────

    ("SPEC-0916", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyFields", "test_data_retention_period_input", "high", "Data retention period input"),
    ("SPEC-0917", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyFields", "test_pii_scrubbing_toggle", "high", "PII scrubbing toggle"),
    ("SPEC-0918", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyFields", "test_consent_required_toggle", "high", "Consent required toggle"),
    ("SPEC-0919", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyFields", "test_automatic_deletion_toggle", "high", "Automatic deletion toggle"),
    ("SPEC-0920", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyFields", "test_save_draft_inputs_button", "high", "Save draft inputs button"),
    ("SPEC-0923", "tests/e2e/test_memory_privacy_page.py", "TestMemoryPrivacyFields", "test_identification_mode_segmented_control", "high", "Identification mode SegmentedControl"),

    # ── NEW TESTS: Billing page ─────────────────────────────────────────────

    ("SPEC-0875", "tests/e2e/test_billing_page.py", "TestBillingPageStructure", "test_manage_subscription_button", "high", "Manage subscription button"),
    ("SPEC-0876", "tests/e2e/test_billing_page.py", "TestBillingPageStructure", "test_manage_billing_button", "high", "Manage billing button"),
    ("SPEC-0878", "tests/e2e/test_billing_page.py", "TestBillingPageStructure", "test_page_title", "high", "Billing page title"),

    # ── NEW TESTS: Inbox page ───────────────────────────────────────────────

    ("SPEC-0897", "tests/e2e/test_inbox_page.py", "TestInboxPageStructure", "test_category_input", "high", "Inbox Category input"),
    ("SPEC-0898", "tests/e2e/test_inbox_page.py", "TestInboxPageStructure", "test_assign_to_agent_input", "high", "Inbox Assign to agent input"),
    ("SPEC-0899", "tests/e2e/test_inbox_page.py", "TestInboxPageStructure", "test_cancel_button", "high", "Inbox Cancel button"),
    ("SPEC-0900", "tests/e2e/test_inbox_page.py", "TestInboxPageStructure", "test_status_segmented_control", "high", "Inbox status SegmentedControl"),

    # ── NEW TESTS: Quick Actions page ───────────────────────────────────────

    ("SPEC-0924", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsFields", "test_button_label_input", "high", "QA Button label input"),
    ("SPEC-0925", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsFields", "test_prompt_template_input", "high", "QA Prompt template input"),
    ("SPEC-0926", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsFields", "test_icon_input", "high", "QA Icon input"),
    ("SPEC-0927", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsFields", "test_active_toggle", "high", "QA Active toggle"),
    ("SPEC-0928", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsFields", "test_cancel_button", "high", "QA Cancel button"),
    ("SPEC-0929", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsPageStructure", "test_page_title", "high", "QA page title"),
    ("SPEC-0930", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsPageStructure", "test_page_title", "high", "QA page title (duplicate spec)"),
    ("SPEC-0931", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsTabs", "test_prompts_tab", "high", "QA prompts tab"),
    ("SPEC-0932", "tests/e2e/test_quick_actions_page.py", "TestQuickActionsTabs", "test_assignments_tab", "high", "QA assignments tab"),

    # ── NEW TESTS: Integrations page ────────────────────────────────────────

    ("SPEC-0901", "tests/e2e/test_integrations_page.py", "TestIntegrationsPageStructure", "test_page_title", "high", "Integrations page title"),

    # ── WI specs needing new mappings ───────────────────────────────────────

    ("246", "tests/e2e/test_navigation.py", "TestPageNavigation", "test_configuration_loads", "medium", "Onboarding wizard replaced — config page loads"),
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

    total_coverage = c.execute(
        "SELECT COUNT(DISTINCT spec_id) FROM test_coverage"
    ).fetchone()[0]
    total_specs = c.execute(
        "SELECT COUNT(DISTINCT id) FROM specifications WHERE status != 'retired'"
    ).fetchone()[0]

    print(f"Inserted: {inserted}, Skipped (already exist): {skipped}")
    print(f"Total coverage: {total_coverage}/{total_specs} specs ({100*total_coverage/total_specs:.1f}%)")


if __name__ == "__main__":
    main()
